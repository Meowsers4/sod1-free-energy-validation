"""Stage A packaging, rejection paths and optional real local CPU rehearsal."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from src.analysis.gromacs_gpu_smoke import create_package
from src.analysis import gromacs_gpu_smoke_runtime as runtime


@pytest.fixture
def package(tmp_path):
    root = tmp_path / "package"
    create_package(root)
    return root, json.loads((root / "contract.json").read_text())


def test_package_refuses_replacement_and_detects_changed_input(package):
    root, spec = package
    runtime.verify_package(root)
    with pytest.raises(FileExistsError):
        create_package(root)
    with (root / "inputs/state00.mdp").open("a") as stream:
        stream.write("nsteps = 500000\n")
    with pytest.raises(ValueError, match="checksum"):
        runtime.verify_package(root)


def test_scripts_are_non_submitting_and_syntax_valid(package):
    root, spec = package
    for name in ("PREPARE_ON_SCC.sh", "REVIEW_ON_SCC.sh", "stage_A.sge"):
        subprocess.run(["bash", "-n", str(root / name)], check=True)
    text = (root / "stage_A.sge").read_text()
    assert "#$ -r n" in text and "#$ -l h_rt=00:10:00" in text
    assert "#$ -t " not in text
    with pytest.raises(ValueError, match="SGE allocation"):
        runtime.job(root, spec)
    assert not (root / "attempt").exists()


def test_allocation_rejects_wrong_slots_hosts_and_devices(package):
    _, spec = package
    env = dict(JOB_ID="123", PE="mpi32", NSLOTS="32", CUDA_VISIBLE_DEVICES="3,0,2,1")
    runtime.validate_allocation(env, "scc-501 32 l40s UNDEFINED\n", "scc-501", spec)
    for key, value in (("PE", "omp"), ("NSLOTS", "4"), ("CUDA_VISIBLE_DEVICES", "0,0,1,2"),
                       ("SGE_TASK_ID", "1"), ("CUDA_MPS_PIPE_DIRECTORY", "/tmp/mps")):
        bad = dict(env, **{key: value})
        with pytest.raises(ValueError):
            runtime.validate_allocation(bad, "scc-501 32 q x", "scc-501", spec)
    with pytest.raises(ValueError, match="multi-host"):
        runtime.validate_allocation(env, "scc-501 16 q x\nscc-502 16 q x", "scc-501", spec)


def test_omp4_package_preserves_fixture_and_requires_single_host(package, tmp_path):
    original, old_spec = package
    root = tmp_path / "omp4"
    create_package(root, spec_path=Path("docs/gromacs_gpu_stage_a_omp4_v1.yaml"))
    runtime.verify_package(root)
    spec = json.loads((root / "contract.json").read_text())
    assert spec["image"] == old_spec["image"]
    assert spec["fixture"] == old_spec["fixture"]
    assert spec["states"] == old_spec["states"]
    assert {k for k in spec["scheduler"] if spec["scheduler"][k] != old_spec["scheduler"][k]} == {"pe", "slots"}
    for source in (original / "inputs").iterdir():
        assert source.read_bytes() == (root / "inputs" / source.name).read_bytes()
    assert "#$ -pe omp 4\n" in (root / "stage_A.sge").read_text()
    subprocess.run(["bash", "-n", str(root / "stage_A.sge")], check=True)
    env = dict(JOB_ID="123", PE="omp", NSLOTS="4", CUDA_VISIBLE_DEVICES="3,0,2,1")
    runtime.validate_allocation(env, "scc-501 4 l40s UNDEFINED\n", "scc-501", spec)
    with pytest.raises(ValueError, match="multi-host"):
        runtime.validate_allocation(env, "scc-501 2 q x\nscc-502 2 q x", "scc-501", spec)
    with pytest.raises(ValueError, match="wrong PE/slots"):
        runtime.validate_allocation(dict(env, PE="mpi32", NSLOTS="32"), "scc-501 32 q x", "scc-501", spec)


@pytest.mark.parametrize("change", [{"threads": 2}, {"slots": 2}, {"pe": "mpi32"}, {"gpus": 2}])
def test_omp4_package_rejects_unreviewed_resource_changes(tmp_path, change):
    spec = yaml.safe_load(Path("docs/gromacs_gpu_stage_a_omp4_v1.yaml").read_text())
    spec["scheduler"].update(change)
    source = tmp_path / "bad.yaml"
    source.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError, match="scope changed"):
        create_package(tmp_path / "package", spec_path=source)


def test_device_mapping_uses_assignment_not_physical_zero():
    smi = "7, GPU-a, NVIDIA L40S, Exclusive_Process\n3, GPU-b, NVIDIA L40S, Default\n"
    assert runtime.assigned_uuids("3,7", smi, "L40S") == ["GPU-b", "GPU-a"]
    with pytest.raises(ValueError, match="unresolved"):
        runtime.assigned_uuids("0", smi, "L40S")
    with pytest.raises(ValueError, match="duplicate"):
        runtime.assigned_uuids("3,GPU-b", smi, "L40S")


def test_container_environment_preserves_cvd_but_removes_host_overrides(monkeypatch):
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "3,1,7,2")
    monkeypatch.setenv("SINGULARITYENV_CUDA_VISIBLE_DEVICES", "0")
    monkeypatch.setenv("SINGULARITY_BINDPATH", "/usr/local")
    monkeypatch.setenv("LD_LIBRARY_PATH", "/host/mpi/lib")
    env = runtime.container_env(True)
    assert env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"] == "3,1,7,2"
    assert "SINGULARITY_BINDPATH" not in env and "LD_LIBRARY_PATH" not in env


def test_container_disables_automatic_tmp_mount_before_explicit_bind(package, tmp_path):
    root, spec = package
    for gpu in (False, True):
        args = runtime.container_command(root, spec, tmp_path, gpu=gpu)
        assert "tmp" in args[args.index("--no-mount")+1].split(",")
        assert str(tmp_path) + ":/tmp" in args
        assert ("--nv" in args) == gpu


def test_warning_reports_origin_and_offending_line(tmp_path):
    log = tmp_path / "grompp.log"
    mount_warning = "WARNING: path /overlay-lowerdir/tmp is already overridden, replacing with session/tmp"
    log.write_text(mount_warning + "\nGROMACS - gmx grompp, 2025.3\n")
    with pytest.raises(ValueError, match="container/runtime") as error:
        runtime.check_preparation_warnings(log)
    assert mount_warning in str(error.value) and str(log) in str(error.value)
    log.write_text("WARNING 1 [file state00.mdp]:\nInvalid input\n")
    with pytest.raises(ValueError, match="GROMACS input"):
        runtime.check_preparation_warnings(log)
    # Known non-GPU-host MPI message is retained; it is not an input warning.
    log.write_text("CUDA-aware support is disabled.\nlibcuda.so.1: cannot open shared object file\n")
    runtime.check_preparation_warnings(log)


def test_private_tmp_roundtrip_rejects_overridden_mount(package, tmp_path):
    root, spec = package
    class FakeRunner:
        def run(self, args, log, **kwargs):
            Path(log).write_text("PRIVATE_TMP_BIND_VERIFIED\n")
            # Simulate a container writing into session tmp instead of the host bind.
    with pytest.raises(ValueError, match="write did not reach"):
        runtime.verify_tmp_bind(root, spec, tmp_path, FakeRunner(), tmp_path / "mount.log")
    class RoundTripRunner:
        def run(self, args, log, **kwargs):
            (tmp_path / ".sod1-smoke-mount-return").write_text(args[-1])
            Path(log).write_text("PRIVATE_TMP_BIND_VERIFIED\n")
    runtime.verify_tmp_bind(root, spec, tmp_path, RoundTripRunner(), tmp_path / "mount.log")


def test_failed_command_includes_diagnostic_output(tmp_path):
    runner = runtime.Runner(tmp_path, 10, 1024**2)
    with pytest.raises(ValueError, match="specific error from subprocess"):
        runner.run([sys.executable, "-c", "print('specific error from subprocess'); raise SystemExit(2)"],
                   tmp_path / "failed.log")


def exchange_fixture():
    return ("Replica exchange at step 100 time 0.10000\nRepl ex  0 x  1    2 x  3\n"
            "Replica exchange at step 200 time 0.20000\nRepl ex  0    1 x  2    3\n")


def test_exchange_reconstructs_walkers_and_rejects_missing_duplicate_or_wrong_parity():
    text = exchange_fixture()
    history = runtime.parse_exchange(text, 4, 100, 300)
    assert history[0]["state_to_walker"] == [1, 0, 3, 2]
    assert history[1]["state_to_walker"] == [1, 3, 0, 2]
    for bad in (text + text, text.split("Replica exchange at step 200")[0],
                text.replace("0    1 x  2    3", "0 x  1    2 x  3"),
                text.replace(" x ", "   ")):
        with pytest.raises(ValueError):
            runtime.parse_exchange(bad, 4, 100, 300)


def test_quota_uses_project_headroom_not_filesystem_free(package):
    _, spec = package
    runtime.check_quota("/projectnb/rise-batteries 50 1638400 42.97 434105", spec)
    with pytest.raises(ValueError, match="quota"):
        runtime.check_quota("/projectnb/rise-batteries 50 1638400 49.97 434105", spec)


def test_deadline_terminates_command(tmp_path):
    runner = runtime.Runner(tmp_path, 0.2, 1024**2)
    with pytest.raises(ValueError, match="deadline"):
        runner.run([sys.executable, "-c", "import time; time.sleep(30)"], tmp_path / "wait.log")


def test_missing_or_changed_prepared_tpr_fails(package):
    root, spec = package
    p = root / "prepared"
    p.mkdir()
    record = {"sif_sha256": spec["image"]["sha256"],
              "package_manifest_sha256": runtime.sha(root / "SHA256SUMS"),
              "files": {"state00/topol.tpr": "0"*64}}
    runtime.write_json(p / "PREPARED.json", record)
    with pytest.raises(ValueError, match="missing file"):
        runtime.verify_prepared(root, spec)
    (p / "state00").mkdir()
    (p / "state00/topol.tpr").write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        runtime.verify_prepared(root, spec)


@pytest.mark.skipif(not os.environ.get("GROMACS_SMOKE_LOCAL_GMX"), reason="requires explicit local CPU GROMACS binary")
def test_real_gromacs_input_and_finite_dynamics_rehearsal(package):
    root, spec = package
    gmx = os.environ["GROMACS_SMOKE_LOCAL_GMX"]
    for state in spec["states"]:
        p = root / state["directory"]
        p.mkdir()
        def run(args, filename, stdin=None):
            result = subprocess.run([gmx] + args, cwd=p, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=60, input=stdin)
            (p / filename).write_text(result.stdout)
            assert result.returncode == 0, result.stdout
            return result.stdout
        out = run(["grompp", "-f", str(root / "inputs" / (state["directory"] + ".mdp")),
                   "-c", str(root / "inputs/conf.gro"), "-p", str(root / "inputs/topol.top"),
                   "-o", "topol.tpr", "-po", "mdout.mdp"], "grompp.log")
        assert "WARNING" not in out
        dump = run(["dump", "-s", "topol.tpr"], "tpr.dump")
        runtime.validate_tpr_dump(dump, state, spec)
        with pytest.raises(ValueError, match="init-lambda-state"):
            runtime.validate_tpr_dump(dump, dict(state, local_index=99), spec)
        run(["mdrun", "-s", "topol.tpr", "-deffnm", "smoke", "-ntmpi", "1", "-ntomp", "1",
             "-nb", "cpu", "-update", "cpu"], "mdrun.out")
        xvg = (p / "smoke.xvg").read_text()
        runtime.validate_dhdl(xvg, state, spec)
        with pytest.raises(ValueError, match="nonfinite"):
            runtime.validate_dhdl(xvg + "1.1 nan 0 0 0 0 0\n", state, spec)
        run(["dump", "-cp", "smoke.cpt"], "checkpoint.dump")
        run(["energy", "-f", "smoke.edr", "-o", "energy.xvg"], "energy-extraction.log",
            "Potential\nTemperature\n0\n")
        assert 'legend "Temperature"' in (p / "energy.xvg").read_text()
