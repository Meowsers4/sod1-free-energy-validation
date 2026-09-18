"""Synthetic/unit-only tests; these arrays are not scientific result files."""

import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from src.analysis import f64a_raw_energy_audit as raw


def test_acf_matches_direct_definition_and_slope():
    x = np.arange(20, dtype=float)
    result = raw.describe_series(x, 1.0, [1, 4, 20], [0.05, 0.5, 0.95])
    centered = x - x.mean()
    assert result["acf_biased"]["4"] == pytest.approx(
        centered[:-4] @ centered[4:] / (centered @ centered)
    )
    assert result["acf_biased"]["20"] is None
    assert result["linear_slope_kT_per_ns"] == pytest.approx(1000)
    assert result["second_half_minus_first_half_mean_kT"] == pytest.approx(10)


def test_short_constant_series_are_explicitly_undefined():
    result = raw.describe_series(np.ones(1), 1.0, [1, 10], [0.5])
    assert result["acf_biased"] == {"1": None, "10": None}
    assert result["linear_slope_kT_per_ns"] is None
    assert result["second_half_minus_first_half_mean_kT"] is None


@pytest.mark.parametrize("series", [np.array([]), np.array([np.nan]), np.ones((2, 3))])
def test_rejects_bad_series(series):
    with pytest.raises(ValueError):
        raw.describe_series(series, 1.0, [1], [0.5])


def test_adjacent_observables_include_both_directions():
    u = np.array([[0, 1], [2, 3], [6, 7]], dtype=float)
    middle = raw.observables(u, 1)
    assert np.array_equal(middle["previous_minus_sampled_u"], [-2, -2])
    assert np.array_equal(middle["next_minus_sampled_u"], [4, 4])
    assert "previous_minus_sampled_u" not in raw.observables(u, 0)
    assert "next_minus_sampled_u" not in raw.observables(u, 2)


@pytest.fixture
def synthetic_bundle(tmp_path):
    """Tiny self-consistent fixture, deliberately labeled synthetic throughout."""
    pilot = {
        "pilot_id": "synthetic-test",
        "source_protocol": "synthetic-source",
        "lambda_windows": 3,
        "replicates": 2,
        "target_samples_per_window": 12,
        "energy_stride_ps": 1.0,
    }
    block = {"label": "synthetic-block", "start": 0, "stop": 12}
    design = {
        "blocks": [block],
        "cumulative": [],
        "contrasts": [],
        "policies": [{"label": "adaptive"}],
    }
    records = []
    for rep in range(2):
        selections = [
            {
                "window": w,
                "n_raw": 12,
                "n_after_trim": 12,
                "n_retained": 12,
                "trim_start_column": 0,
                "first_selected_column": 0,
                "last_selected_column": 11,
                "trim_start_column_global": 0,
                "first_selected_column_global": 0,
                "last_selected_column_global": 11,
                "subsample_g": 1.0,
            }
            for w in range(3)
        ]
        records.append(
            {
                "policy": "adaptive",
                "block": "synthetic-block",
                "replicate": rep,
                "raw_column_start": 0,
                "raw_column_stop": 12,
                "n_raw": 36,
                "n_retained": 36,
                "dg_kcal": float(rep),
                "mbar_error_kcal": 0.1,
                "net_hysteresis_kcal": 0.0,
                "sum_absolute_hysteresis_kcal": 0.0,
                "max_absolute_hysteresis_kcal": 0.0,
                "window_diagnostics": selections,
                "overlap_matrix": np.eye(3).tolist(),
                "adjacent_diagnostics": [
                    {
                        "lower_window": w,
                        "upper_window": w + 1,
                        "signed_discrepancy_kcal": 0.0,
                        "forward_dg_kcal": 0.0,
                        "reverse_dg_kcal": 0.0,
                        "overlap_lower_to_upper": 0.0,
                        "overlap_upper_to_lower": 0.0,
                    }
                    for w in range(2)
                ],
            }
        )
    report = {
        "design": design,
        "v1_reproduction_passed": True,
        "records": records,
        "simulation_protocol": "synthetic-protocol",
        "simulation_code_identity": {},
        "source_code_identity": {},
        "analysis_identity": {"synthetic_only": True},
        "input_sha256": {},
        "contrasts": [],
        "contrast_summaries": [],
        "local_changes": [],
        "cumulative_summaries": [],
        "summaries": [
            {
                "policy": "adaptive",
                "block": "synthetic-block",
                "mean_dg_kcal": 0.5,
                "replicate_range_kcal": 1.0,
                "replicate_sem_kcal": 0.5,
                "propagated_mbar_error_kcal": np.sqrt(0.02) / 2,
                "uncertainty_kcal": 0.5,
            }
        ],
    }
    folder = tmp_path / "npzs"
    folder.mkdir()
    for w in range(3):
        for rep in range(2):
            name = f"w{w}_r{rep}.npz"
            np.savez(
                folder / name,
                u_kn_window=np.arange(36, dtype=float).reshape(3, 12),
                pilot_id="synthetic-test",
                provenance="gromacs_pmx",
                lambda_index=w,
                replicate=rep,
                n_states=3,
                protocol="synthetic-protocol",
                source_protocol="synthetic-source",
                code_identity_json="{}",
                source_code_identity_json="{}",
            )
            report["input_sha256"]["/synthetic/production/fep/F64A/folded/" + name] = (
                raw.sha256(folder / name)
            )
    report_path, design_path, pilot_path = (
        tmp_path / name
        for name in ("synthetic-report.json", "design.yaml", "pilot.yaml")
    )
    report_path.write_text(json.dumps(report))
    design_path.write_text(yaml.safe_dump(design))
    pilot_path.write_text(yaml.safe_dump(pilot))
    evidence = {
        "input": str(report_path),
        "input_sha256": raw.sha256(report_path),
        "registered_design": str(design_path),
        "pilot_config": str(pilot_path),
    }
    evidence_path = tmp_path / "evidence.yaml"
    evidence_path.write_text(yaml.safe_dump(evidence))
    config = {
        "report_config": str(evidence_path),
        "npz_dir": str(folder),
        "output_dir": str(tmp_path / "output"),
        "blocks": ["synthetic-block"],
        "bin_samples": 4,
        "acf_lags_samples": [1, 4, 20],
        "quantiles": [0.05, 0.5, 0.95],
        "plot_color_percentile": 95,
        "plot_dpi": 40,
    }
    config_path = tmp_path / "audit.yaml"
    config_path.write_text(yaml.safe_dump(config))
    return config_path, folder, report, pilot, config


def test_complete_synthetic_pipeline_and_no_overwrite(synthetic_bundle):
    config, folder, report, pilot, spec = synthetic_bundle
    output = raw.audit(config)
    result = json.loads((output / "raw_energy_audit.json").read_text())
    assert result["raw_inputs_validated"] == 6
    assert len(result["series_records"]) == 14
    assert len(result["time_bins"]) == 42
    assert len(result["figures"]) == 3
    assert all((output / name).stat().st_size > 100 for name in result["figures"])
    assert not list(output.parent.glob(".f64a-raw-audit-*"))
    with pytest.raises(FileExistsError):
        raw.audit(config)


def test_raw_suffixes_use_saved_cutoff_not_thinned_points(synthetic_bundle):
    config, folder, report, pilot, spec = synthetic_bundle
    report["records"][0]["window_diagnostics"][1]["trim_start_column"] = 10
    u = np.arange(36, dtype=float).reshape(3, 12)
    rows, bins = raw.inspect_window(
        u, 1, 0, report, report["design"]["blocks"], pilot, spec
    )
    (own,) = [r for r in rows if r["observable"] == "sampled_state_u"]
    suffix = own["policy_raw_suffixes"][0]
    assert suffix["raw_suffix"]["n_raw"] == 2
    assert suffix["raw_suffix"]["mean_kT"] == pytest.approx(22.5)
    assert suffix["raw_suffix"]["acf_biased"]["4"] is None


@pytest.mark.parametrize(
    "problem", ["missing", "extra", "hash", "protocol", "shape", "nonfinite"]
)
def test_input_failure_never_publishes(synthetic_bundle, problem):
    config, folder, report, pilot, spec = synthetic_bundle
    path = folder / "w0_r0.npz"
    if problem == "missing":
        path.rename(folder / "preserved.npz")
    elif problem == "extra":
        (folder / "w99_r99.npz").write_bytes(b"not an input")
    else:
        with np.load(path) as data:
            contents = {k: data[k] for k in data.files}
        if problem == "protocol":
            contents["protocol"] = "wrong"
        elif problem == "shape":
            contents["u_kn_window"] = np.zeros((3, 11))
        elif problem == "nonfinite":
            contents["u_kn_window"][0, 0] = np.nan
        else:
            contents["u_kn_window"][0, 0] += 1
        np.savez(path, **contents)
        # For schema/metadata tests, update the synthetic hash so validation goes deeper.
        if problem != "hash":
            report["input_sha256"][
                "/synthetic/production/fep/F64A/folded/w0_r0.npz"
            ] = raw.sha256(path)
            evidence_path = Path(spec["report_config"])
            evidence = yaml.safe_load(evidence_path.read_text())
            Path(evidence["input"]).write_text(json.dumps(report))
            evidence["input_sha256"] = raw.sha256(Path(evidence["input"]))
            evidence_path.write_text(yaml.safe_dump(evidence))
    with pytest.raises((ValueError, FileNotFoundError)):
        raw.audit(config)
    assert not Path(spec["output_dir"]).exists()


def test_real_inputs_are_absent_and_no_gpu_is_scheduled(tmp_path):
    with pytest.raises(FileNotFoundError, match="no GPU producer"):
        raw.audit(npz_dir=tmp_path / "missing", output_dir=tmp_path / "unwritten")
    assert not (tmp_path / "unwritten").exists()


def test_changed_input_during_plotting_never_publishes(synthetic_bundle, monkeypatch):
    config, folder, report, pilot, spec = synthetic_bundle
    plot = raw.plot_bins

    def changed(*args):
        figures = plot(*args)
        path = folder / "w0_r0.npz"
        path.write_bytes(path.read_bytes() + b"synthetic alteration")
        return figures

    monkeypatch.setattr(raw, "plot_bins", changed)
    with pytest.raises(ValueError, match="changed during execution"):
        raw.audit(config)
    assert not Path(spec["output_dir"]).exists()
