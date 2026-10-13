"""Exercise MPS isolation/cleanup without CUDA or an SCC allocation."""
import ast
import json
from pathlib import Path
import subprocess

import pytest

from src.analysis import gromacs_mps_probe as probe


def test_package_integrity_and_old_python(tmp_path):
    root = tmp_path / "probe"
    probe.package(root)
    probe.verify(root)
    ast.parse((root / "probe.py").read_text(), feature_version=(3, 6))
    subprocess.run(["bash", "-n", str(root / "RUN_ON_COMPUTE.sh")], check=True)
    with pytest.raises(FileExistsError):
        probe.package(root)
    (root / "contract.json").write_text("{}")
    with pytest.raises(RuntimeError, match="checksum"):
        probe.verify(root)


def test_selection_and_environment_isolation():
    for value in ("", "0,1", "-1", "3 4", "all"):
        with pytest.raises(RuntimeError):
            probe.assigned_device(value)
    assert probe.assigned_device("3") == "3"
    assert probe.clean_env({"PATH": "/usr/bin", "CUDA_VISIBLE_DEVICES": "3",
                            "CUDA_MPS_PIPE_DIRECTORY": "/other/job",
                            "APPTAINERENV_LD_PRELOAD": "bad",
                            "SINGULARITY_BINDPATH": "/foreign", "LD_PRELOAD": "bad"}) == {"PATH": "/usr/bin"}


@pytest.mark.parametrize("scenario", ["pass", "client_failed", "wrong_mps_pids", "busy", "existing_service"])
def test_host_isolation_overlap_and_cleanup(tmp_path, monkeypatch, scenario):
    root = tmp_path / "package"
    probe.package(root)
    spec = json.loads((root / "contract.json").read_text())
    gpu = "GPU-d1609426-3406-79b2-051a-0a57dffc5956"
    hostfile = tmp_path / "hosts"
    hostfile.write_text("scc-test 4 l40s UNDEFINED\n")
    for key, value in dict(JOB_ID="123", PE="omp", NSLOTS="4", QUEUE="l40s",
                           PE_HOSTFILE=str(hostfile), CUDA_VISIBLE_DEVICES="3").items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("CUDA_MPS_PIPE_DIRECTORY", raising=False)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(probe.tempfile, "mkdtemp", lambda **kw: str(scratch))
    original_sha = probe.sha
    monkeypatch.setattr(probe, "sha", lambda p: spec["sif_sha256"] if str(p) == spec["sif"] else original_sha(p))
    monkeypatch.setattr(probe.shutil, "which", lambda *a, **kw: "/usr/bin/nvidia-cuda-mps-control")
    commands, processes = [], []

    def fake_run(args, env=None, text=None, timeout=15):
        commands.append((args, dict(env or {}), text))
        if "--query-gpu=name,uuid,compute_mode" in args:
            return "NVIDIA L40S, {}, Exclusive_Process\n".format(gpu)
        if "--query-compute-apps=pid" in args:
            return "999\n" if scenario == "busy" else ""
        if args[0] == "ps":
            return "/usr/bin/nvidia-cuda-mps-control -d\n" if scenario == "existing_service" else "bash\n"
        assert env["CUDA_VISIBLE_DEVICES"] == gpu
        assert env["CUDA_MPS_PIPE_DIRECTORY"] == str(scratch / "pipe")
        if text == "get_server_list\n":
            return "500\n" if processes else ""
        if text and text.startswith("get_client_list"):
            return "999\n" if scenario == "wrong_mps_pids" else "101\n102\n103\n104\n"
        if text == "quit\n":
            assert (scratch / "release").exists()
            assert all(p.waited for p in processes)
        return ""

    class FakeClient:
        def __init__(self, command, env, stdout, stderr):
            index = int(command[-1])
            assert "--nv" in command and "--cleanenv" in command
            assert str(scratch) + ":" + str(scratch) in command
            assert env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"] == gpu
            assert env["SINGULARITYENV_CUDA_MPS_PIPE_DIRECTORY"] == str(scratch / "pipe")
            assert "CUDA_VISIBLE_DEVICES" not in env
            self.returncode = None
            self.waited = False
            if scenario != "client_failed":
                (scratch / ("ready-{}.json".format(index))).write_text(json.dumps({"pid": 101 + index, "uuid": gpu}))
            processes.append(self)

        def poll(self):
            return 1 if scenario == "client_failed" else None

        def wait(self, timeout):
            assert (scratch / "release").exists()
            self.returncode = 1 if scenario == "client_failed" else 0
            self.waited = True

    monkeypatch.setattr(probe, "run", fake_run)
    monkeypatch.setattr(probe.sp, "Popen", FakeClient)
    if scenario == "pass":
        probe.host(root)
        result = json.loads((root / "attempt/result.json").read_text())
        assert result["sharing_passed"] and result["cleanup_confirmed"]
        assert not result["mpi_tested"] and not result["dynamics_tested"]
    else:
        with pytest.raises(RuntimeError):
            probe.host(root)
    if scenario in ("busy", "existing_service"):
        assert not processes
        assert not any("nvidia-cuda-mps-control" in x[0][0] for x in commands)
        assert not (root / "attempt").exists()
    else:
        assert commands[-1][2] == "quit\n"
        assert json.loads((root / "attempt/result.json").read_text())["sharing_passed"] == (scenario == "pass")
