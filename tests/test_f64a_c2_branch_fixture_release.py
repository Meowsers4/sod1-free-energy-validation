"""The branch fixture release package stays inert until a separate selection."""

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = (Path(__file__).resolve().parents[1] / "packages" /
        "f64a-c2-branch-fixture-execution-release-candidate-20261003-v1")


def runtime_module(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    import runtime
    return runtime


def test_inactive_permit_rejects_before_any_attempt_or_submission():
    proc = subprocess.run([sys.executable, str(ROOT / "runtime.py"), "permit"],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode != 0
    assert "live GPU fixture not selected by this package" in proc.stderr
    assert not (ROOT / "attempt").exists()
    assert not (ROOT / "submission").exists()
    script = (ROOT / "SUBMIT_ON_SCC.sh").read_text()
    assert script.index("runtime.py permit") < script.index("mkdir submission")
    assert script.index("mkdir submission") < script.index("qsub ")


def test_release_review_checks_provenance_and_exact_bounds(tmp_path, monkeypatch):
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
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps(record))
    spec["preflight"]["path"] = str(preflight)
    monkeypatch.setattr(runtime.preflight, "source_review", lambda _: {"states": 20})
    runtime.review(ROOT, spec)
    altered = copy.deepcopy(spec)
    altered["scheduler"]["walltime_seconds"] = 3600
    with pytest.raises(ValueError, match="candidate resources"):
        runtime.review(ROOT, altered)
    selected = copy.deepcopy(spec)
    selected["execution_authorized"] = True
    with pytest.raises(ValueError, match="not selected"):
        runtime.guard(selected)
    selected["reviewed_release_candidate_sha256"] = "a" * 64
    selected["selection_record"] = {
        "decision": "one_bounded_technical_live_branch_fixture",
        "reviewed_release_candidate_sha256": "a" * 64,
        "su_balance_decision": "proceed_with_balance_unknown",
        "max_allocated_gpu_hours": 0.5,
        "max_requested_cpu_slot_hours": 8,
        "no_retry": True,
        "production_authorized": False,
    }
    runtime.guard(selected)
    selected["scheduler"]["walltime_seconds"] = 3600
    with pytest.raises(ValueError, match="not selected"):
        runtime.guard(selected)


def test_storage_summary_counts_phase_and_type_for_partial_attempt(tmp_path, monkeypatch):
    runtime = runtime_module(monkeypatch)
    (tmp_path / "common").mkdir()
    (tmp_path / "common" / "run.cpt").write_bytes(b"123")
    (tmp_path / "baseline").mkdir()
    (tmp_path / "baseline" / "run.log").write_bytes(b"12")
    (tmp_path / "status.json").write_bytes(b"1")
    summary = runtime.storage_summary(tmp_path)
    assert summary["total_bytes"] == 6
    assert summary["by_phase"]["common"] == {"files": 1, "bytes": 3}
    assert summary["by_phase"]["baseline"] == {"files": 1, "bytes": 2}
    assert summary["by_phase"]["metadata"] == {"files": 1, "bytes": 1}
    assert summary["by_type"][".cpt"] == {"files": 1, "bytes": 3}
