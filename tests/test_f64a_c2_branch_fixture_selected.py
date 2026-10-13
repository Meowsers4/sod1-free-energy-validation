"""The selected technical release binds to the reviewed inactive package."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil

import pytest


ROOT = (Path(__file__).resolve().parents[1] / "packages" /
        "f64a-c2-branch-fixture-execution-selected-20261003-v1")


def runtime_module(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    info = importlib.util.spec_from_file_location("selected_branch_fixture_runtime",
                                                   ROOT / "runtime.py")
    module = importlib.util.module_from_spec(info)
    info.loader.exec_module(module)
    return module


def test_selected_release_guard_and_provenance(tmp_path, monkeypatch):
    runtime = runtime_module(monkeypatch)
    spec = json.loads((ROOT / "contract.json").read_text())
    assert spec["execution_authorized"] is True
    assert spec["production_authorized"] is False
    assert spec["selection_record"]["su_balance_su_reported"] == 15000
    assert spec["selection_record"]["su_balance_agent_verified"] is False
    runtime.guard(spec)
    runtime.verify_package(ROOT)
    runtime.review_selected_provenance(ROOT, spec)
    assert not (ROOT / "attempt").exists()
    assert not (ROOT / "submission").exists()

    widened = copy.deepcopy(spec)
    widened["scheduler"]["walltime_seconds"] = 3600
    with pytest.raises(ValueError, match="not selected"):
        runtime.guard(widened)
    altered_balance = copy.deepcopy(spec)
    altered_balance["selection_record"]["su_balance_su_reported"] = 14000
    with pytest.raises(ValueError, match="not selected"):
        runtime.guard(altered_balance)

    copied = tmp_path / "selected"
    shutil.copytree(ROOT, copied)
    (copied / "release-candidate-runtime.py").write_text("changed\n")
    with pytest.raises(ValueError, match="reviewed release source differs"):
        runtime.review_selected_provenance(copied, spec)


def test_selected_submit_script_retains_one_attempt_order():
    script = (ROOT / "SUBMIT_ON_SCC.sh").read_text()
    assert script.index("runtime.py permit") < script.index("mkdir submission")
    assert script.index("mkdir submission") < script.index("qsub ")
    assert "-pe omp16 16" in script
    assert "gpus=1,gpu_type=L40S,h_rt=00:30:00" in script
    assert "-r n" in script


def test_selected_static_review_with_saved_external_evidence(tmp_path, monkeypatch):
    runtime = runtime_module(monkeypatch)
    spec = copy.deepcopy(runtime.spec_at(ROOT))
    source = tmp_path / "source"
    source.mkdir()
    (source / "PREPARED.json").write_text(json.dumps({
        "states": [{"tpr_sha256": row["tpr_sha256"]} for row in spec["states"]]}))
    spec["source_prepared"] = str(source)
    record = {
        "status": "preflight_pass_pending_fixture_selection",
        "execution_authorized": False, "production_authorized": False,
        "package_manifest_sha256": spec["preflight"]["package_manifest_sha256"],
        "source": {"source_manifest_sha256": spec["source_manifest_sha256"],
                   "image_sha256": spec["image_sha256"]},
        "su_balance": "unknown_not_waived_for_this_fixture",
        "queue": {"validation_only": True,
                  "output": "verification: found suitable queue(s)",
                  "command": ["qsub", "-w", "v", "-pe", "omp16", "16",
                              "-l", "gpus=1,gpu_type=L40S,h_rt=00:30:00"]},
        "project_quota": {"free_quota_bytes_estimated": 26040000000},
        "project_filesystem_free_bytes": 33327939584,
        "persistent_root_writable": True,
    }
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(record))
    spec["preflight"]["path"] = str(path)
    monkeypatch.setattr(runtime.preflight, "source_review", lambda _: {"states": 20})
    runtime.review(ROOT, spec)
