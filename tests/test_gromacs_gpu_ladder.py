"""Full-ladder resource, exchange, checkpoint and twenty-client failure guards."""
import ast
import copy
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from src.analysis.gromacs_gpu_smoke import create_package
from src.analysis import gromacs_gpu_smoke_runtime as rt
from src.analysis import gromacs_gpu_restart as restart
from src.analysis.gromacs_gpu_mps import PrivateMPS


@pytest.fixture(params=["docs/gromacs_gpu_ladder_v1.yaml", "docs/gromacs_gpu_ladder_omp16_v2.yaml"])
def package(tmp_path, request):
    root = tmp_path / "ladder"
    create_package(root, spec_path=Path(request.param))
    return root, json.loads((root / "contract.json").read_text())


def exchange_text(count=20, final=2000):
    lines = []
    for step in range(100, final, 100):
        tokens = []
        for i in range(count):
            tokens.append(str(i))
            if i < count-1 and i % 2 == (step//100+1) % 2:
                tokens.append("x")
        lines.append("Replica exchange at step {} time {}\nRepl ex {}\n".format(step, step*.001, " ".join(tokens)))
    return "".join(lines)


def test_full_ladder_package_and_bounded_scripts(package):
    root, spec = package
    rt.verify_package(root)
    assert [s["source_index"] for s in spec["states"]] == list(range(20))
    assert [s["lambda_value"] for s in spec["states"]] == yaml.safe_load(Path("config/pipeline.yaml").read_text())["fep"]["lambda_vector"]
    assert "import-prepared" not in (root / "PREPARE_ON_SCC.sh").read_text()
    assert "runtime.py prepare" in (root / "PREPARE_ON_SCC.sh").read_text()
    for name in ("runtime.py", "restart.py", "mps.py"):
        ast.parse((root / name).read_text(), feature_version=(3, 6))
    for script in list(root.glob("*.sh")) + list(root.glob("*.sge")):
        subprocess.run(["bash", "-n", str(script)], check=True)
    job = (root / "stage_L.sge").read_text()
    assert "#$ -pe omp {}".format(spec["scheduler"]["slots"]) in job and "#$ -l h_rt=00:20:00" in job
    assert "#$ -l gpus=1,gpu_type=L40S" in job
    assert "-w v" in (root / "VALIDATE_QUEUE_ON_SCC.sh").read_text()
    assert "-terse" not in (root / "VALIDATE_QUEUE_ON_SCC.sh").read_text()
    submit = (root / "SUBMIT_ON_SCC.sh").read_text()
    assert "mkdir submission-L" in submit and "test ! -e attempt" in submit
    assert "h_rt=00:20:00" in submit and "-pe omp {}".format(spec["scheduler"]["slots"]) in submit
    assert "qdel" not in submit
    args = rt.mpi_arguments(spec)
    assert ("--oversubscribe" in args) == bool(spec.get("cpu_sharing"))
    assert args[args.index("--host")+1] == "localhost:" + str(spec["scheduler"]["slots"])
    assert args[args.index("--np")+1] == "20"


@pytest.mark.parametrize("change", ["slots", "gpus", "deadline", "indices", "import", "duration"])
def test_resource_or_ladder_scope_cannot_silently_change(tmp_path, change):
    spec = yaml.safe_load(Path("docs/gromacs_gpu_ladder_v1.yaml").read_text())
    if change in ("slots", "gpus"):
        spec["scheduler"][change] = 4
    elif change == "deadline":
        spec["scheduler"]["work_deadline_seconds"] = 1199
    elif change == "indices":
        spec["fixture"]["lambda_indices"] = [0, 6, 13, 19]
    elif change == "import":
        spec["prepared_source"] = {"path": "old-four-state"}
    else:
        spec["fixture"]["nsteps"] = 4000
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError):
        create_package(tmp_path / "bad-package", spec_path=path)


def test_allocation_and_mps_require_twenty_matching_clients(package, tmp_path, monkeypatch):
    root, spec = package
    count = spec["scheduler"]["slots"]
    env = dict(JOB_ID="123", PE="omp", NSLOTS=str(count), CUDA_VISIBLE_DEVICES="3")
    rt.validate_allocation(env, "scc-505 {} l40s UNDEFINED".format(count), "scc-505", spec)
    for slots in (4, 19):
        with pytest.raises(ValueError):
            rt.validate_allocation(dict(env, NSLOTS=str(slots)), "scc-505 {} l40s UNDEFINED".format(slots), "scc-505", spec)
    with pytest.raises(ValueError):
        rt.validate_allocation(env, "scc-505 {0} l40s UNDEFINED\nscc-506 {0} l40s UNDEFINED".format(count//2), "scc-505", spec)
    work, scratch = root / "attempt", tmp_path / "scratch"
    work.mkdir(); scratch.mkdir()
    service = PrivateMPS(work, scratch, "GPU-7ab63c30-8edc-e49c-e306-922c040486e6", spec)
    service.started = True
    for i in range(20):
        rt.write_json(work / "rank-{}.json".format(i), {"rank": i, "pid": 100+i, "gpu": {"uuid": service.gpu}})
    for clients in (set(range(100,104)), set(range(100,119)), set(range(100,119)) | {999}):
        monkeypatch.setattr(service, "clients", lambda: {50: clients})
        service.observe()
        assert not service.observed_all
    monkeypatch.setattr(service, "clients", lambda: {50: set(range(100,120))})
    service.observe()
    assert service.observed_all
    mapping = {"devices": [{"ordinal": 0, "uuid": service.gpu, "name": "NVIDIA L40S"}]}
    assert [rt.device_for_rank(mapping, i, spec)["ordinal"] for i in range(20)] == [0]*20


def test_exchange_covers_upper_states_and_every_neighbor(package):
    _, spec = package
    history = rt.parse_exchange(exchange_text(), 20, 100, 2000)
    summary = rt.ladder_summary(history, spec)
    assert len(history) == 19 and sum(h["step"] == 1000 for h in history) == 1
    assert summary["accepted_exchanges"] == 181
    assert summary["accepted_by_neighbor"][-1] == {"pair": [18, 19], "count": 10}
    bad = copy.deepcopy(history)
    for h in bad:
        h["accepted_pairs"] = [p for p in h["accepted_pairs"] if tuple(p) != (18,19)]
    with pytest.raises(ValueError, match="unexercised"):
        rt.ladder_summary(bad, spec)
    with pytest.raises(ValueError):
        rt.parse_exchange(exchange_text().replace(" 19\n", " 18\n", 1), 20, 100, 2000)


def test_last_state_checkpoint_cannot_be_missing_on_resume(package):
    root, spec = package
    work = root / "attempt"
    work.mkdir()
    files = {}
    for state in spec["states"]:
        p = work / state["directory"]
        p.mkdir()
        for name in ("smoke.cpt", "topol.tpr"):
            (p / name).write_bytes(str(state["local_index"]).encode())
            files[state["directory"] + "/" + name] = rt.sha(p / name)
    rt.write_json(work / "RESTART_READY.json", {"files": files,
                  "sif_sha256": spec["image"]["sha256"], "package_manifest_sha256": rt.sha(root / "SHA256SUMS")})
    restart.verify_checkpoint_inputs(root, spec)
    (work / "state19/smoke.cpt").unlink()
    with pytest.raises(ValueError, match="missing file"):
        restart.verify_checkpoint_inputs(root, spec)


def test_omp16_inputs_unchanged_and_oversubscription_explicit(tmp_path):
    root = tmp_path / "omp16"
    create_package(root, spec_path=Path("docs/gromacs_gpu_ladder_omp16_v2.yaml"))
    spec = json.loads((root / "contract.json").read_text())
    old = Path("results/gpu_smoke_packages/gmx-gpu-ladder-20260928-v1")
    # Compare generated inputs to the frozen candidate when present, otherwise regenerate.
    if not old.exists():
        old = tmp_path / "old"
        create_package(old, spec_path=Path("docs/gromacs_gpu_ladder_v1.yaml"))
    assert rt.inventory(root / "inputs") == rt.inventory(old / "inputs")
    args = rt.mpi_arguments(spec)
    assert args[args.index("--host")+1] == "localhost:16"
    assert args[args.index("--np")+1] == "20"
    assert "--oversubscribe" in args and args[-3:] == ["--mca", "mpi_yield_when_idle", "1"]
    spec.pop("cpu_sharing")
    with pytest.raises(ValueError, match="unregistered"):
        rt.mpi_arguments(spec)


def test_cpu_affinity_limits_parent_and_rejects_escaped_rank(tmp_path, monkeypatch):
    root = tmp_path / "cpu-mask"
    create_package(root, spec_path=Path("docs/gromacs_gpu_ladder_omp16_v2.yaml"))
    spec = json.loads((root / "contract.json").read_text())
    (root / "attempt").mkdir()
    mask = set(range(8,40))  # Inherited permission need not start at CPU zero.
    def getmask(pid):
        assert pid == 0
        return mask.copy()
    def setmask(pid, selected):
        assert pid == 0 and selected <= mask
        mask.clear()
        mask.update(selected)
    monkeypatch.setattr(rt.os, "sched_getaffinity", getmask, raising=False)
    monkeypatch.setattr(rt.os, "sched_setaffinity", setmask, raising=False)
    rt.configure_cpu_sharing(root, spec)
    assert mask == set(range(8,24))
    assert rt.rank_cpu_affinity(root, spec) == list(range(8,24))
    record = json.loads((root / "attempt/cpu-affinity.json").read_text())
    assert record["allocated_slots"] == 16 and record["mpi_ranks"] == 20
    mask.add(24)
    with pytest.raises(ValueError, match="rank CPU affinity"):
        rt.rank_cpu_affinity(root, spec)
    mask.clear(); mask.update(range(15))
    with pytest.raises(ValueError, match="smaller than reservation"):
        rt.configure_cpu_sharing(root, spec)


@pytest.mark.parametrize("change", ["no_mode", "extra_slots", "extra_affinity", "aggressive_mpi"])
def test_unregistered_cpu_oversubscription_rejected(tmp_path, change):
    spec = yaml.safe_load(Path("docs/gromacs_gpu_ladder_omp16_v2.yaml").read_text())
    if change == "no_mode":
        spec.pop("cpu_sharing")
    elif change == "extra_slots":
        spec["scheduler"]["slots"] = 20
    elif change == "extra_affinity":
        spec["cpu_sharing"]["affinity_cpus"] = 20
    else:
        spec["cpu_sharing"]["mpi_yield_when_idle"] = 0
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError):
        create_package(tmp_path / "bad-package", spec_path=path)


def test_canonical_scc_pe_is_explicit_and_allocation_guard_remains_strict(tmp_path):
    root = tmp_path / "canonical"
    create_package(root, spec_path=Path("docs/gromacs_gpu_ladder_pe_omp16_v3.yaml"))
    spec = json.loads((root / "contract.json").read_text())
    rt.verify_package(root)
    for name in ("stage_L.sge", "VALIDATE_QUEUE_ON_SCC.sh", "SUBMIT_ON_SCC.sh"):
        assert "-pe omp16 16" in (root / name).read_text()
        subprocess.run(["bash", "-n", str(root / name)], check=True)
    assert "import-prepared" in (root / "PREPARE_ON_SCC.sh").read_text()
    env = dict(JOB_ID="7763245", PE="omp16", NSLOTS="16", CUDA_VISIBLE_DEVICES="3")
    rt.validate_allocation(env, "scc-505 16 l40s UNDEFINED", "scc-505", spec)
    for pe, slots in (("omp", "16"), ("mpi16", "16"), ("omp16", "20"), ("omp16", "8")):
        with pytest.raises(ValueError, match="wrong PE/slots"):
            rt.validate_allocation(dict(env, PE=pe, NSLOTS=slots), "scc-505 16 l40s UNDEFINED", "scc-505", spec)
    with pytest.raises(ValueError, match="multi-host"):
        rt.validate_allocation(env, "scc-505 8 l40s UNDEFINED\nscc-506 8 l40s UNDEFINED", "scc-505", spec)
    old = yaml.safe_load(Path("docs/gromacs_gpu_ladder_omp16_v2.yaml").read_text())
    with pytest.raises(ValueError, match="wrong PE/slots"):
        rt.validate_allocation(env, "scc-505 16 l40s UNDEFINED", "scc-505", old)


@pytest.mark.parametrize("corrupt", [False, True])
def test_full_ladder_import_checks_state19_and_preserves_ancestry(tmp_path, monkeypatch, corrupt):
    source = tmp_path / "source"
    create_package(source, spec_path=Path("docs/gromacs_gpu_ladder_omp16_v2.yaml"))
    old = json.loads((source / "contract.json").read_text())
    for state in old["states"]:
        d = source / "prepared" / state["directory"]
        d.mkdir(parents=True)
        (d / "topol.tpr").write_bytes(b"test TPR " + str(state["local_index"]).encode())
        (d / "tpr.dump").write_text(
            "init-lambda-state = {}\nnsteps = 2000\ninit-step = 0\nnatoms = 512\n"
            "n-lambdas = 20\ncalc-lambda-neighbors = -1\nall-lambdas:\nfep-lambdas = {}\n".format(
                state["local_index"], " ".join(str(s["lambda_value"]) for s in old["states"])))
    rt.write_json(source / "prepared/PREPARED.json", {"files": rt.inventory(source / "prepared"),
                  "gpu_executed": False, "sif_sha256": old["image"]["sha256"],
                  "package_manifest_sha256": rt.sha(source / "SHA256SUMS")})
    data = yaml.safe_load(Path("docs/gromacs_gpu_ladder_pe_omp16_v3.yaml").read_text())
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
        (source / "prepared/state19/topol.tpr").write_bytes(b"tampered")
        with pytest.raises(ValueError, match="checksum"):
            rt.import_prepared(root, spec)
        assert not (root / "prepared").exists()
    else:
        rt.import_prepared(root, spec)
        rt.verify_prepared(root, spec)
        record = json.loads((root / "prepared/PREPARED.json").read_text())
        assert record["import_provenance"]["source_prepared_record_sha256"] == rt.sha(source / "prepared/PREPARED.json")
        assert len(list((root / "prepared").glob("state*/topol.tpr"))) == 20
        assert not (root / "attempt").exists()
