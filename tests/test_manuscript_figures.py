"""Guards for the manuscript figure assembly (src/analysis/manuscript_figures.py)."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from src.analysis import manuscript_figures as mf

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/manuscript_figures_v1.yaml"
COMPARATOR = ROOT / "results/cpu_audits/f64a_lambda_comparator_v1/lambda_comparator.json"


def _spec() -> dict:
    return mf.load_spec(SPEC_PATH)


def _hashed_reports_only(spec: dict) -> dict:
    """Spec restricted to the committed reports (the comparator lives in results/)."""
    spec = copy.deepcopy(spec)
    del spec["inputs"]["lambda_comparator"]
    return spec


def test_committed_reports_reproduce_every_quoted_outline_value():
    spec = _hashed_reports_only(_spec())
    data = mf.temporal_data(spec, mf.load_verified_reports(spec))
    observed = mf.check_quoted_values(spec, data)
    assert observed["r1_early_net_hysteresis"] == pytest.approx(0.022705, abs=1e-6)
    assert observed["adaptive_primary_mean"] == pytest.approx(-0.049510, abs=1e-6)
    assert len(data["blocks"]) == 5
    assert all(len(values) == 20 for values in data["suffix"].values())


def test_quoted_value_mismatch_is_fatal():
    spec = _hashed_reports_only(_spec())
    data = mf.temporal_data(spec, mf.load_verified_reports(spec))
    spec["temporal"]["quoted"]["adaptive_primary_mean"] = 0.0
    with pytest.raises(ValueError, match="adaptive_primary_mean"):
        mf.check_quoted_values(spec, data)


def test_report_hash_mismatch_is_fatal():
    spec = _hashed_reports_only(_spec())
    spec["inputs"]["blocks_v1"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="does not match registered"):
        mf.load_verified_reports(spec)


def test_lambda_axis_comes_from_pipeline_config():
    config = yaml.safe_load((ROOT / "config/pipeline.yaml").read_text())
    assert mf.lambda_vector(_spec()) == [float(v) for v in config["fep"]["lambda_vector"]]


def test_existing_output_directory_is_never_overwritten(tmp_path):
    (tmp_path / "existing.png").write_bytes(b"prior output")
    with pytest.raises(FileExistsError):
        mf.build(SPEC_PATH, output_dir=tmp_path)
    assert (tmp_path / "existing.png").read_bytes() == b"prior output"


@pytest.mark.parametrize("force_args", [[], ["--forceall"]])
def test_snakemake_preserves_existing_directory_on_failed_rebuild(tmp_path, force_args):
    """Exercise scheduler cleanup as well as the Python guard on disposable files."""
    pytest.importorskip("snakemake")
    for relative in ("docs/manuscript_figures_v1.yaml", "src/analysis/manuscript_figures.py"):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    output = tmp_path / _spec()["output_dir"]
    output.mkdir(parents=True)
    sentinel = output / "existing.png"
    sentinel.write_bytes(b"immutable prior output")
    result = subprocess.run(
        [sys.executable, "-m", "snakemake", "--snakefile",
         str(ROOT / "workflow/manuscript_figures.smk"), "--cores", "1",
         "--runtime-source-cache-path", str(tmp_path / "source-cache"),
         *force_args, "manuscript_figures_v1"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode != 0
    assert "FileExistsError" in result.stdout + result.stderr
    assert sentinel.read_bytes() == b"immutable prior output"


def test_changed_supplement_is_rejected_despite_unchanged_report(tmp_path):
    spec = _spec()
    source_dir = tmp_path / Path(spec["inputs"]["lambda_comparator"]["path"]).parent
    source_dir.mkdir(parents=True)
    for item in spec["supplement"]:
        shutil.copyfile(ROOT / "docs/manuscript/figures_v1" / item["output"],
                        source_dir / item["source"])
    report = {"lambda_comparator": {"figures": [x["source"] for x in spec["supplement"]]}}
    mf.verify_supplement_sources(spec, report, root=tmp_path)
    (source_dir / spec["supplement"][0]["source"]).write_bytes(b"replaced image")
    with pytest.raises(ValueError, match="does not match registered"):
        mf.verify_supplement_sources(spec, report, root=tmp_path)


@pytest.mark.skipif(not COMPARATOR.exists(), reason="lambda comparator outputs not present locally")
def test_full_build_copies_supplement_byte_identically(tmp_path):
    out = mf.build(SPEC_PATH, output_dir=tmp_path / "figures")
    trace = json.loads((out / "fig6_f64a_temporal.json").read_text())
    assert set(trace["outputs"]) == {"fig6_f64a_temporal.png", "fig6_f64a_temporal.pdf"}
    source_dir = COMPARATOR.parent
    for item in _spec()["supplement"]:
        copied = (out / item["output"]).read_bytes()
        assert copied == (source_dir / item["source"]).read_bytes()
        assert trace["supplement"][item["output"]]["sha256"] == hashlib.sha256(copied).hexdigest()
