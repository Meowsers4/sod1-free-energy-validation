"""One-GPU mapping, prepared-input ancestry, and safe MPS shutdown paths."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from src.analysis.gromacs_gpu_smoke import create_package
from src.analysis import gromacs_gpu_smoke_runtime as rt
from src.analysis.gromacs_gpu_mps import PrivateMPS


@pytest.fixture
def mps_package(tmp_path):
    root = tmp_path / "mps"
    create_package(root, spec_path=Path("docs/gromacs_gpu_stage_a_mps_v1.yaml"))
    return root, json.loads((root / "contract.json").read_text())


def test_mapping_and_package(mps_package, tmp_path):
    root, spec = mps_package
    old = tmp_path / "old"
    create_package(old, spec_path=Path("docs/gromacs_gpu_stage_a_omp4_v1.yaml"))
    assert rt.inventory(root / "inputs") == rt.inventory(old / "inputs")
    rt.verify_package(root)
    for name in ("runtime.py", "mps.py"):
        ast.parse((root / name).read_text(), feature_version=(3, 6))
    for script in list(root.glob("*.sh")) + list(root.glob("*.sge")):
        subprocess.run(["bash", "-n", str(script)], check=True)
    assert "#$ -l gpus=1,gpu_type=L40S" in (root / "stage_A.sge").read_text()
    mapping = {"devices": [{"ordinal": 0, "uuid": "GPU-assigned", "name": "NVIDIA L40S"}]}
    assert [rt.device_for_rank(mapping, r, spec)["ordinal"] for r in range(4)] == [0]*4
    with pytest.raises(ValueError):
        rt.device_for_rank({"devices": mapping["devices"] * 4}, 0, spec)
    with pytest.raises(ValueError):
        rt.device_for_rank(mapping, 4, spec)
    env = dict(JOB_ID="123", PE="omp", NSLOTS="4", CUDA_VISIBLE_DEVICES="3")
    rt.validate_allocation(env, "scc-505 4 l40s UNDEFINED", "scc-505", spec)
    with pytest.raises(ValueError, match="GPU count"):
        rt.validate_allocation(dict(env, CUDA_VISIBLE_DEVICES="0,1,2,3"), "scc-505 4 l40s UNDEFINED", "scc-505", spec)


def test_four_state_result_validation_uses_same_gpu_for_every_rank(mps_package):
    root, spec = mps_package
    work = root / "attempt"
    work.mkdir()
    gpu = {"ordinal": 0, "uuid": "GPU-assigned", "name": "NVIDIA L40S"}
    rt.write_json(work / "device-map.json", {"devices": [gpu]})
    exchanges = "".join("Replica exchange at step {} time 0.10000\nRepl ex {}\n".format(
        step, "0 x 1 2 x 3" if (step//100) % 2 else "0 1 x 2 3") for step in range(100, 1000, 100))
    for rank, state in enumerate(spec["states"]):
        p = work / state["directory"]
        p.mkdir()
        rt.write_json(work / ("rank-{}.json".format(rank)), {"rank": rank, "state": state["directory"], "gpu": gpu})
        (p / "smoke.log").write_text("PP:0\nPP tasks will do work on GPU\n" + exchanges + "Finished mdrun\n")
        legends = "@ subtitle \"state {}:\"\n".format(rank)
        legends += "".join('@ s{} legend "to {}"\n'.format(i, s["lambda_value"]) for i, s in enumerate(spec["states"]))
        # The parser looks for the foreign-energy label suffix ' to <lambda>'.
        legends = legends.replace('legend "to ', 'legend "energy to ')
        (p / "smoke.xvg").write_text(legends + "".join("{} 1 2 3 4\n".format(i/10) for i in range(11)))
        (p / "energy.xvg").write_text('@ s0 legend "Potential"\n@ s1 legend "Temperature"\n'
                                      + "".join("{} -10 120\n".format(i/10) for i in range(11)))
        (p / "checkpoint.dump").write_text("step = 1000\n")
        for filename in ("smoke.edr", "smoke.xtc", "smoke.gro", "smoke.cpt"):
            (p / filename).write_bytes(b"test data")
    assert len(rt.validate_results(root, spec)) == 9
    bad = work / "state03/smoke.log"
    bad.write_text(bad.read_text().replace("PP:0", "PP:3"))
    with pytest.raises(ValueError, match="GPU map mismatch"):
        rt.validate_results(root, spec)


@pytest.mark.parametrize("corrupt", [False, True])
def test_prepared_import_preserves_tprs_and_checks_ancestry(tmp_path, monkeypatch, corrupt):
    source = tmp_path / "source"
    create_package(source, spec_path=Path("docs/gromacs_gpu_stage_a_omp4_v1.yaml"))
    old = json.loads((source / "contract.json").read_text())
    prepared = source / "prepared"
    prepared.mkdir()
    for state in old["states"]:
        d = prepared / state["directory"]
        d.mkdir()
        (d / "topol.tpr").write_bytes(b"sealed test TPR " + str(state["local_index"]).encode())
        (d / "tpr.dump").write_text(
            "init-lambda-state = {}\nnsteps = 1000\ninit-step = 0\nnatoms = 512\n"
            "n-lambdas = 4\ncalc-lambda-neighbors = -1\nall-lambdas:\nfep-lambdas = {}\n".format(
                state["local_index"], " ".join(str(s["lambda_value"]) for s in old["states"])))
    rt.write_json(prepared / "PREPARED.json", {"files": rt.inventory(prepared), "gpu_executed": False,
                  "sif_sha256": old["image"]["sha256"], "package_manifest_sha256": rt.sha(source / "SHA256SUMS")})
    data = yaml.safe_load(Path("docs/gromacs_gpu_stage_a_mps_v1.yaml").read_text())
    data["prepared_source"] = {"path": str(source), "manifest_sha256": rt.sha(source / "SHA256SUMS")}
    path = tmp_path / "spec.yaml"
    path.write_text(yaml.safe_dump(data))
    root = tmp_path / "new"
    create_package(root, spec_path=path)
    spec = json.loads((root / "contract.json").read_text())
    original_sha = rt.sha
    monkeypatch.setattr(rt, "sha", lambda p: spec["image"]["sha256"] if str(p) == spec["image"]["path"] else original_sha(p))
    monkeypatch.delenv("JOB_ID", raising=False)
    if corrupt:
        (prepared / "state00/topol.tpr").write_bytes(b"tampered")
        with pytest.raises(ValueError, match="checksum"):
            rt.import_prepared(root, spec)
        assert not (root / "prepared").exists()
    else:
        rt.import_prepared(root, spec)
        rt.verify_prepared(root, spec)
        record = json.loads((root / "prepared/PREPARED.json").read_text())
        assert record["import_provenance"]["source_prepared_record_sha256"] == rt.sha(prepared / "PREPARED.json")
        assert record["files"] == json.loads((prepared / "PREPARED.json").read_text())["files"]
        with pytest.raises(FileExistsError):
            rt.import_prepared(root, spec)


def fake_service(tmp_path, spec):
    work, scratch = tmp_path / "attempt", tmp_path / "scratch"
    work.mkdir()
    scratch.mkdir()
    service = PrivateMPS(work, scratch, "GPU-7ab63c30-8edc-e49c-e306-922c040486e6", spec)
    service.started = True
    return service


def test_mps_membership_and_container_isolation(mps_package, tmp_path, monkeypatch):
    _, spec = mps_package
    service = fake_service(tmp_path, spec)
    for i in range(4):
        rt.write_json(service.work / ("rank-{}.json".format(i)),
                      {"rank": i, "pid": 100+i, "gpu": {"uuid": service.gpu}})
    monkeypatch.setattr(service, "clients", lambda: {50: {100, 101, 102}})
    service.observe()
    assert not service.observed_all
    monkeypatch.setattr(service, "clients", lambda: {50: {100, 101, 102, 103}})
    service.observe()
    assert service.observed_all
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "3")
    env = service.container_environment(rt.container_env(True))
    assert env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"] == service.gpu
    assert env["SINGULARITYENV_CUDA_MPS_PIPE_DIRECTORY"] == str(service.pipe)
    cmd = rt.container_command(tmp_path, spec, service.scratch, gpu=True)
    assert str(service.scratch) + ":" + str(service.scratch) in cmd


def test_abort_quiesces_gpu_before_runner_may_kill(mps_package, tmp_path, monkeypatch):
    _, spec = mps_package
    service = fake_service(tmp_path, spec)
    monkeypatch.setattr(service, "ranks", lambda: set())
    monkeypatch.setattr(service, "clients", lambda: {50: {100, 101}})
    commands = []
    monkeypatch.setattr(service, "ctl", lambda text: commands.append(text) or "0\n")
    class Process:
        def poll(self):
            return 1
    service.abort(Process())
    assert commands == ["terminate_client 50 100", "terminate_client 50 101"]
    assert (service.work / "mps-abort.json").exists()
    (service.work / "mps-abort.json").unlink()
    def failure(command):
        raise ValueError("control failed")
    monkeypatch.setattr(service, "ctl", failure)
    with pytest.raises(ValueError, match="control failed"):
        service.abort(Process())
    assert not (service.work / "mps-abort.json").exists()
    monkeypatch.setattr(service, "ctl", lambda text: "999\n")
    with pytest.raises(ValueError, match="CUDA_SUCCESS"):
        service.abort(Process())
    assert not (service.work / "mps-abort.json").exists()


def test_close_refuses_live_clients_and_is_idempotent(mps_package, tmp_path, monkeypatch):
    _, spec = mps_package
    service = fake_service(tmp_path, spec)
    spec["sharing"]["shutdown_timeout_seconds"] = 0.01
    monkeypatch.setattr(service, "clients", lambda: {50: {100}})
    commands = []
    monkeypatch.setattr(service, "ctl", lambda text: commands.append(text))
    with pytest.raises(ValueError, match="still live"):
        service.close()
    assert commands == [] and not service.closed
    monkeypatch.setattr(service, "clients", lambda: {50: set()})
    service.close()
    service.close()
    assert commands == ["quit"] and service.closed


@pytest.mark.parametrize("state", ["qw", "r", "absent", "hqw", "race"])
def test_replacement_guard_never_deletes_started_or_missing_job(tmp_path, state):
    root, old, commands = tmp_path / "new", tmp_path / "old", tmp_path / "bin"
    for p in (root, old, commands):
        p.mkdir()
    (root / "REVIEW_ON_SCC.sh").write_text("#!/bin/bash\nexit 0\n")
    (root / "contract.json").write_text(json.dumps({"sharing": {"mode": "private_MPS"},
        "scheduler": {"gpus": 1}, "replacement": {"old_job_id": "7758910", "owner": "bodeb"},
        "prepared_source": {"path": str(old)}}))
    # Mock only cluster commands and the absent local Rocky interpreter path.
    script = Path("scripts/replace_queued_gmx_stage_a_mps.sh").read_text().replace(
        "/usr/libexec/platform-python", sys.executable)
    (root / "replace.sh").write_text(script)
    fake = commands / "fake"
    fake.write_text("#!" + sys.executable + '''
import os, sys
from pathlib import Path
cmd = Path(sys.argv[0]).name
args = sys.argv[1:]
base = Path(os.environ['FAKE_ROOT'])
with (base/'events').open('a') as f:
    f.write(cmd + ' ' + ' '.join(args) + '\\n')
if cmd == 'id':
    print('bodeb')
elif cmd == 'qsub':
    if '-w' in args:
        print('verification: found suitable queue(s)')
    else:
        assert (base/'deleted').exists()
        print('8000000')
elif cmd == 'qstat':
    if '-j' in args:
        print('owner: bodeb\\ncwd: ' + os.environ['FAKE_OLD'] + '\\nscript_file: stage_A.sge')
    elif not (base/'deleted').exists():
        state = os.environ['FAKE_STATE']
        if (base/'held').exists():
            state = 'hr' if state == 'race' else 'hqw'
        elif state == 'race':
            state = 'qw'
        if state != 'absent':
            print('7758910 0.4 gmx-smoke-A bodeb ' + state + ' date 4')
elif cmd == 'qhold':
    (base/'held').touch()
elif cmd == 'qdel':
    assert (base/'held').exists()
    (base/'deleted').touch()
''')
    fake.chmod(0o755)
    for name in ("id", "sha256sum", "qsub", "qstat", "qhold", "qdel"):
        (commands / name).symlink_to(fake)
    env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ["PATH"],
               FAKE_ROOT=str(root), FAKE_OLD=str(old), FAKE_STATE=state)
    result = subprocess.run(["bash", str(root / "replace.sh")], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    events = (root / "events").read_text()
    if state == "qw":
        assert result.returncode == 0, result.stdout
        assert "qdel 7758910" in events
        assert (root / "submission-A/qsub.log").read_text().strip() == "8000000"
    else:
        assert result.returncode != 0
        assert "qdel " not in events
        assert not (root / "submission-A/qsub.log").exists()
