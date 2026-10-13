"""Restart guards plus a real optional GROMACS 2025.3 CPU append rehearsal."""
import copy
import json
import os
import sys
from pathlib import Path
import subprocess

import pytest

from src.analysis.gromacs_gpu_smoke import create_package
from src.analysis import gromacs_gpu_smoke_runtime as rt
from src.analysis import gromacs_gpu_restart as restart


@pytest.fixture
def package(tmp_path):
    root = tmp_path / "restart"
    create_package(root, spec_path=Path("docs/gromacs_gpu_restart_v1.yaml"))
    return root, json.loads((root / "contract.json").read_text())


def test_packaged_restart_does_not_replace_completed_stage_A(package):
    root, spec = package
    rt.verify_package(root)
    assert not (root / "REPLACE_AND_SUBMIT_ON_SCC.sh").exists()
    for path in list(root.glob("*.sh")) + list(root.glob("*.sge")):
        subprocess.run(["bash", "-n", str(path)], check=True)
    assert "import-prepared" in (root / "PREPARE_ON_SCC.sh").read_text()
    assert "qsub" not in (root / "PREPARE_ON_SCC.sh").read_text()
    assert "qdel" not in (root / "SUBMIT_ON_SCC.sh").read_text()
    assert "#$ -l gpus=1,gpu_type=L40S" in (root / "stage_R.sge").read_text()
    assert restart.restart_arguments(spec, "first") == ["-nsteps", "500"]
    assert restart.restart_arguments(spec, "resume") == ["-cpi", "smoke.cpt", "-append"]
    with pytest.raises(ValueError):
        restart.restart_arguments(spec, None)


def checkpoint(state, step=500, part=1):
    return "step = {}\nt = {}\nsimulation part # = {}\nfep_state[0]={}\n".format(step, step*.001, part, state)


def history(nsteps):
    text = "".join("Replica exchange at step {} time 0.10000\nRepl ex {}\n".format(
        step, "0 x 1 2 x 3" if step//100 % 2 else "0 1 x 2 3") for step in range(100, nsteps, 100))
    return rt.parse_exchange(text, 4, 100, nsteps)


def sealed_first_part(root, spec):
    work = root / "attempt"
    work.mkdir()
    for state in spec["states"]:
        name, index = state["directory"], state["local_index"]
        p = work / name
        p.mkdir()
        prepared = root / "prepared" / name
        prepared.mkdir(parents=True)
        (prepared / "topol.tpr").write_bytes(b"test TPR")
        (p / "topol.tpr").write_bytes(b"test TPR")
        (p / "smoke.cpt").write_bytes(b"test checkpoint " + str(index).encode())
        (p / "checkpoint.dump").write_text(checkpoint(index))
        for filename in ("smoke.xvg", "energy.xvg"):
            (p / filename).write_text("".join("{} 10 20\n".format(i/10) for i in range(6)))
    for name in ("mps-overlap.json", "device-map.json"):
        rt.write_json(work / name, {"test": True})
    (work / "mpi-first.log").write_text("test log")
    return restart.seal_first_part(root, spec, history(500))


@pytest.mark.parametrize("change", ["missing", "altered", "tpr", "wrong_part", "wrong_time", "wrong_state"])
def test_checkpoint_failures_rejected_before_continuation(package, change):
    root, spec = package
    if change.startswith("wrong"):
        text = checkpoint(0)
        text = {"wrong_part": text.replace("# = 1", "# = 2"),
                "wrong_time": text.replace("t = 0.5", "t = 0.6"),
                "wrong_state": text.replace("[0]=0", "[0]=1")}[change]
        with pytest.raises(ValueError):
            restart.checkpoint_metadata(text, spec["states"][0], spec)
        return
    sealed_first_part(root, spec)
    restart.verify_checkpoint_inputs(root, spec)
    p = root / "attempt/state02" / ("topol.tpr" if change == "tpr" else "smoke.cpt")
    if change == "missing":
        p.unlink()
    else:
        p.write_bytes(b"tampered")
    with pytest.raises(ValueError):
        restart.verify_checkpoint_inputs(root, spec)


def test_restart_validator_checks_prefix_boundary_parts_and_archive(package):
    root, spec = package
    sealed_first_part(root, spec)
    for state in spec["states"]:
        p = root / "attempt" / state["directory"]
        (p / "checkpoint.dump").write_text(checkpoint(state["local_index"], 1000, 2))
        for filename in ("smoke.xvg", "energy.xvg"):
            (p / filename).write_text("".join("{} 10 20\n".format(i/10) for i in range(11)))
    restart.validate_restart(root, spec, history(1000))
    bad_history = history(1000)
    bad_history.pop(4)  # Missing the step-500 boundary exchange must fail.
    with pytest.raises(ValueError, match="boundary exchange"):
        restart.validate_restart(root, spec, bad_history)
    p = root / "attempt/state03/smoke.xvg"
    original = p.read_text()
    p.write_text(original.replace("0.2 10 20", "0.2 11 20"))
    with pytest.raises(ValueError, match="pre-checkpoint data"):
        restart.validate_restart(root, spec, history(1000))
    p.write_text(original + "0.5 10 20\n")
    with pytest.raises(ValueError, match="checkpoint-time"):
        restart.validate_restart(root, spec, history(1000))
    p.write_text(original)
    archive = root / "attempt/before-restart/state00/smoke.cpt"
    archive.chmod(0o644)
    archive.write_bytes(b"tampered archive")
    with pytest.raises(ValueError, match="checksum"):
        restart.validate_restart(root, spec, history(1000))


def test_rank_launches_resume_from_checkpoints_without_step_override(package, monkeypatch):
    root, spec = package
    sealed_first_part(root, spec)
    gpu = {"ordinal": 0, "uuid": "GPU-assigned", "name": "NVIDIA L40S"}
    rt.write_json(root / "attempt/device-map.json", {"devices": [gpu], "CUDA_VISIBLE_DEVICES": "GPU-assigned"})
    rt.write_json(root / "attempt/mps.json", {"pipe": "/private-job-pipe"})
    monkeypatch.setitem(sys.modules, "restart", restart)
    for key, value in {"OMPI_COMM_WORLD_SIZE": "4", "OMPI_COMM_WORLD_LOCAL_SIZE": "4",
                       "CUDA_VISIBLE_DEVICES": "GPU-assigned", "CUDA_MPS_PIPE_DIRECTORY": "/private-job-pipe"}.items():
        monkeypatch.setenv(key, value)
    calls = []
    monkeypatch.setattr(rt.os, "execv", lambda binary, args: calls.append(args))
    for phase in ("first", "resume"):
        for rank in range(4):
            monkeypatch.setenv("OMPI_COMM_WORLD_RANK", str(rank))
            rt.rank_main(root, spec, phase)
            argv = calls[-1]
            assert argv[argv.index("-gpu_id")+1] == "0"
            if phase == "first":
                assert argv[-2:] == ["-nsteps", "500"] and "-cpi" not in argv
            else:
                assert argv[-3:] == ["-cpi", "smoke.cpt", "-append"] and "-nsteps" not in argv
    (root / "attempt/state02/smoke.cpt").unlink()
    with pytest.raises(ValueError, match="missing file"):
        rt.rank_main(root, spec, "resume")
    assert len(calls) == 8


@pytest.mark.skipif(not os.environ.get("GROMACS_RESTART_LOCAL_GMX"), reason="requires explicit local CPU GROMACS")
@pytest.mark.parametrize("spec_path", ["docs/gromacs_gpu_restart_v1.yaml", "docs/gromacs_gpu_ladder_v1.yaml"])
def test_real_cpu_checkpoint_and_append_all_states(tmp_path, spec_path):
    """CPU-only, independent states: validates restart mechanics, not MPI/exchange."""
    root = tmp_path / "cpu-rehearsal"
    create_package(root, spec_path=Path(spec_path))
    spec = json.loads((root / "contract.json").read_text())
    first_step = spec["restart"]["first_stop_step"]
    boundary = first_step * spec["fixture"]["dt_ps"]
    stride = spec["fixture"]["output_stride"]
    gmx = os.environ["GROMACS_RESTART_LOCAL_GMX"]
    env = dict(os.environ, OMP_NUM_THREADS="1", GMX_MAXBACKUP="-1")
    for state in spec["states"]:
        p = root / state["directory"]
        p.mkdir()
        def run(args, name, stdin=None):
            result = subprocess.run([gmx] + args, cwd=p, env=env, input=stdin, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            (p / name).write_text(result.stdout)
            assert result.returncode == 0, result.stdout
            return result.stdout
        run(["grompp", "-f", str(root / "inputs" / (state["directory"] + ".mdp")),
             "-c", str(root / "inputs/conf.gro"), "-p", str(root / "inputs/topol.top"), "-o", "topol.tpr"], "grompp.log")
        rt.validate_tpr_dump(run(["dump", "-s", "topol.tpr"], "tpr.dump"), state, spec)
        rt.check_preparation_warnings(p / "grompp.log")
        args = ["mdrun", "-s", "topol.tpr", "-deffnm", "smoke", "-ntmpi", "1", "-ntomp", "1", "-nb", "cpu", "-update", "cpu"]
        run(args + restart.restart_arguments(spec, "first"), "first.log")
        text = run(["dump", "-cp", "smoke.cpt"], "first.dump")
        restart.checkpoint_metadata(text, state, spec)
        first_spec = copy.deepcopy(spec)
        first_spec["fixture"]["nsteps"] = first_step
        before = (p / "smoke.xvg").read_text()
        rt.validate_dhdl(before, state, first_spec)
        run(["energy", "-f", "smoke.edr", "-o", "first-energy.xvg"], "first-energy.log", "Potential\nTemperature\n0\n")
        old_energy = (p / "first-energy.xvg").read_text()
        out = run(args + restart.restart_arguments(spec, "resume"), "resume.log")
        assert "continuing from step {}".format(first_step) in out
        restart.checkpoint_metadata(run(["dump", "-cp", "smoke.cpt"], "final.dump"), state, spec, final=True)
        after = (p / "smoke.xvg").read_text()
        rt.validate_dhdl(after, state, spec)
        run(["energy", "-f", "smoke.edr", "-o", "final-energy.xvg"], "final-energy.log", "Potential\nTemperature\n0\n")
        for first, final in ((before, after), (old_energy, (p / "final-energy.xvg").read_text())):
            a, b = restart.data_rows(first), restart.data_rows(final)
            assert [r for r in a if float(r[0]) < boundary] == [r for r in b if float(r[0]) < boundary]
            assert [float(r[0]) for r in b] == pytest.approx(
                [i * spec["fixture"]["dt_ps"] for i in range(0, spec["fixture"]["nsteps"]+1, stride)], abs=1e-6)
