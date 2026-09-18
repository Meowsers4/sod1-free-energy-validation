"""Checks for the report-only audit; never invoke fits or GPU producers."""

import copy
import json
from pathlib import Path

import pytest
import yaml

from src.analysis.f64a_late_window_audit import ROOT, audit, summarize, validate_report


@pytest.fixture
def evidence():
    report = json.loads(
        (ROOT / "docs/f64a_extension_review/f64a_continuation_v2.json").read_text()
    )
    design = yaml.safe_load(
        (ROOT / "pilots/f64a_sampling_extension_v2/analysis.yaml").read_text()
    )
    return report, design


def test_complete_report(evidence):
    report, design = evidence
    validate_report(report, design, 20, 3)
    output = summarize(report, ["block_9_12_ns", "block_12_15_ns"], 0.9)
    assert len(output["window_selection"]) == 1080
    assert len(output["adjacent_pairs"]) == 1026
    assert len(output["focus_pair_summaries"]) == 114
    (observed,) = [
        r
        for r in output["focus_heavy_trim_windows"]
        if r["block"] == "block_12_15_ns" and r["replicate"] == 2 and r["window"] == 17
    ]
    assert observed["n_retained"] == 7
    assert observed["trim_fraction_observed"] == pytest.approx(2968 / 3000)


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "duplicate",
        "nan",
        "count",
        "bounds",
        "global",
        "overlap",
        "hysteresis",
        "summary",
        "contrast",
        "design",
        "missing_summary",
        "missing_movement",
        "missing_local_change",
        "local_change",
    ],
)
def test_rejects_inconsistent_report(evidence, change):
    report, design = copy.deepcopy(evidence)
    r = report["records"][0]
    d = r["window_diagnostics"][0]
    if change == "missing":
        report["records"].pop()
    elif change == "duplicate":
        report["records"][-1] = copy.deepcopy(r)
    elif change == "nan":
        r["dg_kcal"] = float("nan")
    elif change == "count":
        d["n_retained"] += 1
    elif change == "bounds":
        d["trim_start_column"] = d["n_raw"]
    elif change == "global":
        d["first_selected_column_global"] += 1
    elif change == "overlap":
        r["adjacent_diagnostics"][0]["overlap_lower_to_upper"] += 0.1
    elif change == "hysteresis":
        r["net_hysteresis_kcal"] += 0.1
    elif change == "summary":
        report["summaries"][0]["uncertainty_kcal"] = 0
    elif change == "contrast":
        report["contrasts"][0]["signed_movement_kcal"] += 1
    elif change == "design":
        report["design"]["blocks"][0]["start"] += 1
    elif change == "missing_summary":
        report["summaries"].pop()
    elif change == "missing_movement":
        report["contrast_summaries"].pop()
    elif change == "missing_local_change":
        report["local_changes"].pop()
    elif change == "local_change":
        report["local_changes"][0]["forward_dg_kcal_change"] += 1
    with pytest.raises(ValueError):
        validate_report(report, design, 20, 3)


def test_hash_mismatch_never_writes(tmp_path):
    spec = yaml.safe_load((ROOT / "docs/f64a_late_window_audit.yaml").read_text())
    spec["input_sha256"] = "0" * 64
    spec["output"] = str(tmp_path / "must-not-exist.json")
    config = tmp_path / "audit.yaml"
    config.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError, match="hash mismatch"):
        audit(config)
    assert not Path(spec["output"]).exists()


def test_exclusive_atomic_publication(tmp_path):
    spec = yaml.safe_load((ROOT / "docs/f64a_late_window_audit.yaml").read_text())
    spec["output"] = str(tmp_path / "audit.json")
    config = tmp_path / "audit.yaml"
    config.write_text(yaml.safe_dump(spec))
    output = audit(config)
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        audit(config)
    assert output.read_bytes() == original
    assert not list(tmp_path.glob(".f64a-audit-*"))
