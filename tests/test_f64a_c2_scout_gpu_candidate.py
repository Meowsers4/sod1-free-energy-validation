"""Technical checks for the guarded paired-scout GPU candidate."""

import json
from pathlib import Path
import struct
import sys

import pytest

from src.analysis import f64a_c2_scout_gpu_checks as checks
from src.analysis import f64a_c2_scout_gpu_runtime as runtime
from src.analysis import f64a_c2_scout_gpu_package as package
from src.analysis import gromacs_gpu_smoke_runtime as smoke


ROOT = Path(__file__).resolve().parents[1]


def xtc_frame(atoms, step, time_ps, payload=b"abcd"):
    header = struct.pack(">iiif9f", 1995, atoms, step, time_ps,
                         7.0, 0.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 7.0)
    compressed = struct.pack(">if7i", atoms, 1000.0, 0, 0, 0, 1, 1, 1, 8)
    return header + compressed + struct.pack(">i", len(payload)) + payload


def test_xtc_envelope_and_gmx_decoder_report(tmp_path):
    path = tmp_path / "scout.xtc"
    path.write_bytes(b"".join(xtc_frame(38414, step, step * .002)
                              for step in (0, 25000, 50000)))
    frames = checks.xtc_envelopes(path, 38414)
    assert [frame["time_ps"] for frame in frames] == [0.0, 50.0, 100.0]
    report = ("Reading frame       0 time    0.000\n# Atoms  38414\n"
              "Precision 0.001 (nm)\nLast frame          2 time  100.000\n"
              "Item        #frames Timestep (ps)\nStep             3   50\n"
              "Time             3   50\nLambda           0\n"
              "Coords           3   50\nVelocities       0\n"
              "Forces           0\nBox              3   50\n")
    assert checks.gmx_check_summary(report, 38414)["frames"] == 3
    stage_p_report = ("Reading frame       0 time    0.000\n# Atoms  38414\n"
                      "Precision 0.001 (nm)\nLast frame         10 time    4.000\n"
                      "Item        #frames Timestep (ps)\nStep            11    0.4\n"
                      "Time            11    0.4\nLambda           0\n"
                      "Coords          11    0.4\nVelocities       0\n"
                      "Forces           0\nBox             11    0.4\n")
    assert checks.gmx_check_summary(stage_p_report, 38414, frames=11,
                                    last_ps=4.0, stride_ps=0.4)["frames"] == 11
    with pytest.raises(ValueError, match="atom count"):
        checks.gmx_check_summary(report, 38415)
    path.write_bytes(path.read_bytes()[:-1])
    with pytest.raises(ValueError, match="truncated"):
        checks.xtc_envelopes(path, 38414)


def test_energy_and_checkpoint_grids_fail_closed():
    times = [i for i in range(101)]
    energy = ('@ s0 legend "Potential"\n@ s1 legend "Temperature"\n' +
              ''.join(f'{t} -12.0 298.15\n' for t in times))
    assert checks.energy_summary(energy)["records"] == 101
    with pytest.raises(ValueError, match="grid"):
        checks.energy_summary(energy.replace("50 -12.0", "49 -12.0"))
    checkpoint = "step = 50000\nt = 100\nsimulation part # = 1\nfep_state[0] = 7\n"
    assert checks.checkpoint_summary(checkpoint, 7)["part"] == 1
    with pytest.raises(ValueError, match="mismatch"):
        checks.checkpoint_summary(checkpoint, 8)
    lambdas = [round(i / 19, 4) for i in range(20)]
    legends = ''.join('@ s{} legend "energy to {:.4f}"\n'.format(i, value)
                      for i, value in enumerate(lambdas))
    dhdl = ('# state 7:\n' + legends +
            ''.join(str(t) + ' ' + ' '.join(['1.0'] * 20) + '\n'
                    for t in times))
    assert checks.dhdl_summary(dhdl, 7, lambdas)["foreign_states"] == 20
    with pytest.raises(ValueError, match="foreign-state"):
        checks.dhdl_summary(dhdl.replace('energy to 1.0000', 'energy to 0.9000'),
                            7, lambdas)


def test_real_gromacs_dhdl_legend_layout_with_auxiliary_columns():
    lambdas = [0.0000, 0.0588, 0.1176, 0.1765, 0.2353, 0.2941, 0.3529,
               0.4118, 0.4706, 0.5294, 0.5882, 0.6471, 0.7059, 0.7647,
               0.8235, 0.8824, 0.9200, 0.9500, 0.9750, 1.0000]
    lines = ['@ subtitle "T = 298.15 (K) \\xl\\f{} state 0: fep-lambda = 0.0000"',
             '@ s0 legend "Total Energy (kJ/mol)"',
             '@ s1 legend "dH/d\\xl\\f{} fep-lambda = 0.0000"']
    lines += ['@ s{} legend "\\xD\\f{{}}H \\xl\\f{{}} to {:.4f}"'.format(i + 2, value)
              for i, value in enumerate(lambdas)]
    lines.append('@ s22 legend "pV (kJ/mol)"')
    lines += ['{:.4f} {}'.format(i * 0.2, ' '.join(['1.0'] * 23))
              for i in range(21)]
    text = '\n'.join(lines) + '\n'
    assert checks.dhdl_summary(text, 0, lambdas, nsteps=2000,
                               stride=100)['records'] == 21
    with pytest.raises(ValueError, match="foreign-state"):
        checks.dhdl_summary(text.replace('to 1.0000', 'to 0.9999'), 0,
                            lambdas, nsteps=2000, stride=100)


def test_gro_atom_order_is_checked(tmp_path):
    source = tmp_path / "source.gro"
    final = tmp_path / "final.gro"
    source.write_text("start\n2\n    1ALA      N    1   0.0   0.0   0.0\n"
                      "    1ALA     CA    2   0.1   0.0   0.0\n1 1 1\n")
    final.write_text(source.read_text().replace("start", "final"))
    assert checks.gro_identity(source) == checks.gro_identity(final)
    final.write_text(final.read_text().replace("CA", "CB"))
    assert checks.gro_identity(source) != checks.gro_identity(final)


def test_baseline_and_hrex_exchange_separation():
    no_exchange = ["Finished mdrun\n" for _ in range(20)]
    baseline = checks.exchange_summary(no_exchange, "baseline")
    assert baseline["rounds"] == 0
    with pytest.raises(ValueError, match="exchange activity"):
        checks.exchange_summary([no_exchange[0] + "Repl ex  0 1\n"] +
                                no_exchange[1:], "baseline")
    # A zero-acceptance protein scout is technically valid if all attempts and
    # permutations are present. Acceptance is descriptive, not a pass gate.
    log = "".join("Replica exchange at step {} time {}\nRepl ex  {}\n".format(
        step, step * .002, " ".join(str(i) for i in range(20)))
        for step in range(500, 50000, 500)) + "Finished mdrun\n"
    summary = checks.exchange_summary([log] * 20, "hrex")
    assert summary["rounds"] == 99
    assert summary["accepted_exchanges"] == 0
    assert summary["all_neighbor_links_attempted"]


def test_qacct_and_storage_bounds(tmp_path):
    qacct = """qname l40s
hostname scc-504.scc.bu.edu
project rise-batteries
jobnumber 7791102
granted_pe omp16
slots 16
failed 0
exit_status 0
ru_wallclock 146
"""
    assert checks.qacct_summary(qacct, "7791102")["allocated_cpu_slot_hours"] == 146*16/3600
    with pytest.raises(ValueError, match="exit mismatch"):
        checks.qacct_summary(qacct.replace("exit_status 0", "exit_status 1"), "7791102")
    work, scratch = tmp_path / "work", tmp_path / "scratch"
    work.mkdir()
    scratch.mkdir()
    runner = runtime.BoundedRunner(work, scratch, float("inf"), 10, 20)
    runner.limits()
    (work / "big").write_bytes(b"x" * 10)
    with pytest.raises(ValueError, match="per-location storage stop"):
        runner.limits()
    (work / "big").unlink()
    runner = runtime.BoundedRunner(work, scratch, float("inf"), 1024*1024, 2*1024*1024)
    text = runner.capture([sys.executable, "-c", "print('checkpoint metadata')"],
                          work / "capture-summary.log")
    assert "checkpoint metadata" in text
    assert not list(scratch.glob("capture-*"))


def test_package_is_sealed_and_job_is_inert(tmp_path):
    target = tmp_path / "candidate"
    package.package(target, root=ROOT)
    package.review_package(target)
    spec = json.loads((target / "contract.json").read_text())
    assert spec["execution_authorized"] is False
    assert len(spec["states"]) == 20
    assert spec["states"][0]["tpr_sha256"] == \
        "f31aef6118cad78fbe9313944fe3d5a60c849603bab055131e32fa19795d3e45"
    base = runtime.mdrun_arguments(spec, "baseline")
    hrex = runtime.mdrun_arguments(spec, "hrex")
    assert base[:-2] == hrex[:-4]
    assert base[-2:] == ["-replex", "0"]
    assert hrex[-4:] == ["-replex", "500", "-reseed", "20260929"]
    assert not list(target.glob("*.sge"))
    with pytest.raises(ValueError, match="not authorized"):
        runtime.job(target, spec, "baseline")
    assert not (target / "attempts").exists()
    with pytest.raises(ValueError, match="baseline technical/accounting gate"):
        runtime.preflight_baseline_gate(target, "hrex")
    (target / "contract.json").write_text((target / "contract.json").read_text().replace(
        '"execution_authorized": false', '"execution_authorized": true'))
    with pytest.raises(ValueError, match="package file changed"):
        package.review_package(target)


def test_source_review_checks_all_paired_tpr_copies(tmp_path):
    candidate = tmp_path / "candidate"
    package.package(candidate, root=ROOT)
    parent = tmp_path / "cpu-import"
    source = parent / "prepared"
    source.mkdir(parents=True)
    (parent / "SHA256SUMS").write_text("sealed source package marker\n")
    spec = json.loads((candidate / "contract.json").read_text())
    spec["states"] = spec["states"][:2]
    spec["prepared_source"]["path"] = str(source)
    spec["prepared_source"]["package_manifest_sha256"] = smoke.sha(parent / "SHA256SUMS")
    rows = []
    for index, state in enumerate(spec["states"]):
        name = state["directory"]
        content = ("test TPR " + name).encode()
        for branch in ("common", "arms/baseline", "arms/hrex"):
            path = source / branch / "states" / name / "topol.tpr"
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
        state["tpr_sha256"] = smoke.sha(source / "common" / "states" / name / "topol.tpr")
        rows.append({"state": index, "tpr_sha256": state["tpr_sha256"]})
    (source / "PREPARED.json").write_text(json.dumps({
        "status": "cpu_inputs_prepared_pending_review", "execution_authorized": False,
        "production_authorized": False, "sif_sha256": spec["image"]["sha256"],
        "states": rows}))
    package.manifest(source)
    spec["prepared_source"]["prepared_manifest_sha256"] = smoke.sha(source / "SHA256SUMS")
    spec["prepared_source"]["prepared_manifest_entries"] = len(
        (source / "SHA256SUMS").read_text().splitlines())
    (parent / "IMPORT.json").write_text(json.dumps({
        "source_manifest_sha256": spec["prepared_source"]["prepared_manifest_sha256"],
        "execution_authorized": False, "gpu_executed": False}))
    assert runtime.source_review(parent, spec) == source
    (source / "arms/hrex/states/state01/topol.tpr").write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum mismatch"):
        runtime.source_review(parent, spec)
