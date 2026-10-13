"""Fresh-output lambda/comparator characterization for completed F64A v2 data."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
import platform
import tempfile
from pathlib import Path

import numpy as np
import yaml
from scipy.stats import spearmanr

from src.analysis.f64a_late_window_audit import ROOT, sha256, validate_report
from src.analysis.f64a_raw_energy_audit import (
    describe_series,
    load_matrix,
    production_hashes,
)

DEFAULT_CONFIG = ROOT / "docs/f64a_lambda_comparator.yaml"
NEIGHBOR_DIRECTIONS = ("previous_minus_sampled_u", "next_minus_sampled_u")
FULL_METRICS = (
    "signed_half_drift_kT",
    "absolute_half_drift_kT",
    "signed_slope_kT_per_ns",
    "absolute_slope_kT_per_ns",
    "std_kT",
    "absolute_half_drift_over_std",
)


def _require_unique(items: list[dict], **fields: object) -> dict:
    matches = [row for row in items if all(row.get(k) == v for k, v in fields.items())]
    if len(matches) != 1:
        raise ValueError(f"expected one record for {fields}, found {len(matches)}")
    return matches[0]


def load_inputs(config: Path) -> tuple[dict, dict, dict, dict, list[dict], Path]:
    """Load and cross-check the fixed specification and both frozen reports."""
    spec = yaml.safe_load(config.read_text())
    raw_path = ROOT / spec["raw_audit"]
    continuation_path = ROOT / spec["continuation_report"]
    pilot_path = ROOT / spec["pilot_config"]
    design_path = ROOT / spec["analysis_design"]
    for path, expected in (
        (raw_path, spec["raw_audit_sha256"]),
        (continuation_path, spec["continuation_report_sha256"]),
    ):
        if sha256(path) != expected:
            raise ValueError(f"frozen input hash mismatch: {path}")
    raw = json.loads(raw_path.read_text())
    continuation = json.loads(continuation_path.read_text())
    pilot = yaml.safe_load(pilot_path.read_text())
    design = yaml.safe_load(design_path.read_text())
    validate_report(
        continuation, design, pilot["lambda_windows"], pilot["replicates"]
    )
    lambdas = spec["lambda_vector"]
    states = spec["common_evaluation_states"]
    pairs = spec["fixed_pairs"]
    blocks = [b for b in design["blocks"] if b["label"] in spec["blocks"]]
    if (
        len(lambdas) != pilot["lambda_windows"]
        or not all(math.isfinite(x) for x in lambdas)
        or lambdas[0] != 0
        or lambdas[-1] != 1
        or any(b <= a for a, b in zip(lambdas, lambdas[1:]))
        or states != sorted(set(states))
        or any(type(i) is not int or not 0 <= i < len(lambdas) for i in states)
        or pairs != [list(pair) for pair in zip(states, states[1:])]
        or len(blocks) != len(spec["blocks"])
        or any(type(lag) is not int or lag <= 0 for lag in spec["acf_lags_samples"])
        or any(not math.isfinite(q) or not 0 <= q <= 1 for q in spec["quantiles"])
        or type(spec["plot_dpi"]) is not int
        or spec["plot_dpi"] <= 0
    ):
        raise ValueError("invalid lambda/comparator configuration")
    if (
        raw["audit_id"] != "f64a_raw_energy_v1"
        or raw["raw_inputs_validated"] != len(lambdas) * pilot["replicates"]
        or len(raw["series_records"]) != 348
        or len([r for r in raw["series_records"] if r["observable"] != "sampled_state_u"])
        != 228
        or raw["source_simulation_protocol"] != continuation["simulation_protocol"]
    ):
        raise ValueError("raw audit does not match the fixed v2 inventory")
    return spec, raw, continuation, pilot, blocks, ROOT / spec["npz_dir"]


def _full_metrics(summary: dict) -> dict:
    drift = summary["second_half_minus_first_half_mean_kT"]
    slope = summary["linear_slope_kT_per_ns"]
    std = summary["std_kT"]
    return {
        "signed_half_drift_kT": drift,
        "absolute_half_drift_kT": abs(drift),
        "signed_slope_kT_per_ns": slope,
        "absolute_slope_kT_per_ns": abs(slope),
        "std_kT": std,
        "absolute_half_drift_over_std": abs(drift) / std if std > 0 else None,
    }


def neighbor_records(
    raw: dict,
    continuation: dict,
    blocks: list[dict],
    lambdas: list[float],
    repeats: int,
    policy: str,
) -> list[dict]:
    """Build all planned path/direction slots, including explicit missing endpoints."""
    result = []
    series = [r for r in raw["series_records"] if r["observable"] != "sampled_state_u"]
    for block in blocks:
        for rep in range(repeats):
            fit = _require_unique(
                continuation["records"], policy=policy, block=block["label"], replicate=rep
            )
            for window, lam in enumerate(lambdas):
                selection = _require_unique(fit["window_diagnostics"], window=window)
                for direction in NEIGHBOR_DIRECTIONS:
                    neighbor = window - 1 if direction.startswith("previous") else window + 1
                    record_id = f"{block['label']}:r{rep}:w{window}:{direction}"
                    base = {
                        "record_id": record_id,
                        "block": block["label"],
                        "replicate": rep,
                        "window": window,
                        "lambda": lam,
                        "direction": direction,
                        "neighbor_window": neighbor if 0 <= neighbor < len(lambdas) else None,
                        "neighbor_lambda": lambdas[neighbor]
                        if 0 <= neighbor < len(lambdas)
                        else None,
                    }
                    if not 0 <= neighbor < len(lambdas):
                        result.append(
                            {
                                **base,
                                "available": False,
                                "missing_reason": "endpoint_has_no_neighbor_in_this_direction",
                                **{metric: None for metric in FULL_METRICS},
                                "directional_overlap": None,
                                "adaptive_raw_suffix_n": None,
                                "adaptive_selected_n": None,
                                "adaptive_trim_start_column": None,
                            }
                        )
                        continue
                    source = _require_unique(
                        series,
                        block=block["label"],
                        replicate=rep,
                        window=window,
                        observable=direction,
                    )
                    suffix = _require_unique(source["policy_raw_suffixes"], policy=policy)
                    lower, upper = sorted((window, neighbor))
                    adjacent = _require_unique(
                        fit["adjacent_diagnostics"],
                        lower_window=lower,
                        upper_window=upper,
                    )
                    overlap_key = (
                        "overlap_upper_to_lower"
                        if direction.startswith("previous")
                        else "overlap_lower_to_upper"
                    )
                    result.append(
                        {
                            **base,
                            "available": True,
                            "missing_reason": None,
                            **_full_metrics(source["full_block"]),
                            "directional_overlap": adjacent[overlap_key],
                            "adaptive_raw_suffix_n": suffix["raw_suffix"]["n_raw"],
                            "adaptive_selected_n": selection["n_retained"],
                            "adaptive_trim_start_column": selection["trim_start_column"],
                        }
                    )
    return result


def fixed_pair_records(
    matrices: dict[tuple[int, int], np.ndarray],
    blocks: list[dict],
    lambdas: list[float],
    pairs: list[list[int]],
    stride_ps: float,
    lags: list[int],
    quantiles: list[float],
) -> list[dict]:
    """Evaluate identical state-pair energy differences on every sampled path."""
    result = []
    for block in blocks:
        start, stop = block["start"], block["stop"]
        for (sampled_window, rep), u in sorted(matrices.items()):
            for lower, upper in pairs:
                summary = describe_series(
                    u[upper, start:stop] - u[lower, start:stop],
                    stride_ps,
                    lags,
                    quantiles,
                )
                result.append(
                    {
                        "record_id": (
                            f"{block['label']}:r{rep}:sampled_w{sampled_window}:"
                            f"pair_w{lower}_w{upper}"
                        ),
                        "block": block["label"],
                        "replicate": rep,
                        "sampled_window": sampled_window,
                        "sampled_lambda": lambdas[sampled_window],
                        "lower_state": lower,
                        "upper_state": upper,
                        "lower_lambda": lambdas[lower],
                        "upper_lambda": lambdas[upper],
                        "units": "reduced potential difference (kT), not free energy",
                        **_full_metrics(summary),
                        "full_block": summary,
                    }
                )
    return result


def summarize_neighbors(records: list[dict], lambdas: list[float]) -> dict:
    """Report pooled and window-median summaries with explicit denominators."""
    available = [r for r in records if r["available"]]
    window_rows = []
    for window, lam in enumerate(lambdas):
        rows = [r for r in available if r["window"] == window]
        window_rows.append(
            {
                "window": window,
                "lambda": lam,
                "n_available_neighbor_records": len(rows),
                **{
                    f"median_{metric}": float(np.median([r[metric] for r in rows]))
                    for metric in FULL_METRICS
                },
            }
        )
    metric_summaries = {}
    for metric in FULL_METRICS:
        medians = [row[f"median_{metric}"] for row in window_rows]
        metric_summaries[metric] = {
            "pooled_record_median": float(np.median([r[metric] for r in available])),
            "pooled_record_n": len(available),
            "window_median_of_medians": float(np.median(medians)),
            "window_count": len(window_rows),
            "spearman_vs_lambda": float(spearmanr(lambdas, medians).statistic),
        }
    return {
        "planned_directional_slots": len(records),
        "available_neighbor_records": len(available),
        "explicit_missing_endpoint_slots": len(records) - len(available),
        "dependence_note": (
            "The two neighbor directions share configurations and are not independent "
            "replications. Repeats share a protein start."
        ),
        "window_summaries": window_rows,
        "metric_summaries": metric_summaries,
    }


def _plot_lines(ax, rows: list[dict], metric: str, *, directions: bool = True) -> None:
    colors = ("#2166ac", "#b2182b", "#4d9221")
    styles = {
        "previous_minus_sampled_u": "--",
        "next_minus_sampled_u": "-",
    }
    for rep in sorted({r["replicate"] for r in rows}):
        groups = NEIGHBOR_DIRECTIONS if directions else (None,)
        for direction in groups:
            subset = [
                r
                for r in rows
                if r["replicate"] == rep
                and r["available"]
                and (direction is None or r["direction"] == direction)
            ]
            ax.plot(
                [r["lambda"] for r in subset],
                [r[metric] for r in subset],
                color=colors[rep],
                linestyle=styles.get(direction, "-"),
                marker="o",
                markersize=2.5,
                linewidth=0.9,
                alpha=0.85,
                label=(f"r{rep} " + ("prev" if direction and direction.startswith("previous") else "next"))
                if directions
                else f"r{rep}",
            )
    ax.axhline(0, color="black", linewidth=0.5, alpha=0.4)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(alpha=0.18)


def plot_neighbor_metrics(
    records: list[dict], blocks: list[dict], directory: Path, dpi: int
) -> str:
    """Plot signed and magnitude metrics for every repeat and direction."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [
        ("signed_half_drift_kT", "Signed half drift (kT)"),
        ("absolute_half_drift_kT", "|Half drift| (kT)"),
        ("signed_slope_kT_per_ns", "Signed slope (kT/ns)"),
        ("absolute_slope_kT_per_ns", "|Slope| (kT/ns)"),
        ("std_kT", "Raw-block SD (kT)"),
        ("absolute_half_drift_over_std", "|Drift| / raw-block SD"),
    ]
    fig, axes = plt.subplots(len(metrics), len(blocks), figsize=(13, 18), sharex=True)
    for col, block in enumerate(blocks):
        rows = [r for r in records if r["block"] == block["label"]]
        for row, (metric, label) in enumerate(metrics):
            ax = axes[row, col]
            _plot_lines(ax, rows, metric)
            ax.set_ylabel(label)
            if row == 0:
                ax.set_title(block["label"].replace("block_", "").replace("_", "–"))
            if row == len(metrics) - 1:
                ax.set_xlabel("Actual sampled lambda")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.975),
        ncol=6,
        fontsize=8,
    )
    fig.suptitle(
        "F64A v2 full-block neighbor-energy descriptions\n"
        "Both directions share configurations; lines are descriptive, not tests",
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    name = "neighbor_full_block_metrics.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    return name


def plot_selection_context(
    records: list[dict], blocks: list[dict], directory: Path, dpi: int
) -> str:
    """Place overlap and adaptive selection lengths beside the drift audit."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [
        ("directional_overlap", "Directional adjacent overlap"),
        ("adaptive_raw_suffix_n", "Adaptive raw suffix length"),
        ("adaptive_selected_n", "Adaptive thinned count"),
    ]
    fig, axes = plt.subplots(3, len(blocks), figsize=(13, 10), sharex=True)
    for col, block in enumerate(blocks):
        rows = [r for r in records if r["block"] == block["label"]]
        for row, (metric, label) in enumerate(metrics):
            ax = axes[row, col]
            # Suffix/count are path quantities duplicated across directions; show next
            # where available and previous only for the lambda=1 endpoint.
            if metric == "directional_overlap":
                plotted = rows
                directions = True
            else:
                plotted = [
                    r
                    for r in rows
                    if r["direction"] == "next_minus_sampled_u"
                    or (r["window"] == 19 and r["direction"] == "previous_minus_sampled_u")
                ]
                directions = False
            _plot_lines(ax, plotted, metric, directions=directions)
            ax.set_ylabel(label)
            if row == 0:
                ax.set_title(block["label"].replace("block_", "").replace("_", "–"))
            if row == 2:
                ax.set_xlabel("Actual sampled lambda")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.97),
        ncol=6,
        fontsize=8,
    )
    fig.suptitle("Overlap and saved adaptive-selection context", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    name = "selection_context.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    return name


def plot_fixed_pairs(
    records: list[dict], blocks: list[dict], directory: Path, dpi: int
) -> str:
    """Plot fixed state-pair observables against each path's actual sampled lambda."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, len(blocks), figsize=(13, 7), sharex=True)
    pair_keys = sorted({(r["lower_state"], r["upper_state"]) for r in records})
    colors = ("#1b9e77", "#d95f02", "#7570b3", "#e7298a")
    for col, block in enumerate(blocks):
        block_rows = [r for r in records if r["block"] == block["label"]]
        for row_index, (metric, label) in enumerate(
            (("signed_half_drift_kT", "Signed half drift (kT)"),
             ("absolute_half_drift_kT", "|Half drift| (kT)"))
        ):
            ax = axes[row_index, col]
            for pair_index, pair in enumerate(pair_keys):
                for rep in range(3):
                    subset = [
                        r for r in block_rows
                        if (r["lower_state"], r["upper_state"]) == pair
                        and r["replicate"] == rep
                    ]
                    label_text = None
                    if rep == 0:
                        first = subset[0]
                        label_text = f"lambda {first['lower_lambda']:.4f}–{first['upper_lambda']:.4f}"
                    ax.plot(
                        [r["sampled_lambda"] for r in subset],
                        [r[metric] for r in subset],
                        color=colors[pair_index],
                        alpha=0.35 + 0.25 * rep,
                        linewidth=0.8,
                        label=label_text,
                    )
            ax.axhline(0, color="black", linewidth=0.5, alpha=0.4)
            ax.set_ylabel(label)
            ax.grid(alpha=0.18)
            if row_index == 0:
                ax.set_title(block["label"].replace("block_", "").replace("_", "–"))
            else:
                ax.set_xlabel("Actual sampled lambda")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.925),
        ncol=4,
        fontsize=8,
    )
    fig.suptitle(
        "Fixed lambda-pair energy differences on every sampled path\n"
        "Three lines per color are repeats; observables are not free energies",
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    name = "fixed_pair_metrics.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    return name


def analyze(
    config: Path = DEFAULT_CONFIG,
    npz_dir: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Validate immutable inputs, compute A1 outputs, and refuse overwrite."""
    spec, raw, continuation, pilot, blocks, configured_npz = load_inputs(config)
    folder = (npz_dir or configured_npz).resolve()
    output = (output_dir or ROOT / spec["output_dir"]).resolve()
    if output.exists():
        raise FileExistsError(f"refusing existing lambda/comparator output: {output}")
    hashes = production_hashes(
        continuation, pilot["lambda_windows"], pilot["replicates"]
    )
    if hashes != raw["input_npz_sha256"]:
        raise ValueError("raw-audit and continuation NPZ inventories disagree")
    if {p.name for p in folder.glob("w*_r*.npz")} != set(hashes):
        raise FileNotFoundError(f"need exactly {len(hashes)} frozen production NPZs")
    dependencies = [
        config,
        ROOT / spec["raw_audit"],
        ROOT / spec["continuation_report"],
        ROOT / spec["pilot_config"],
        ROOT / spec["analysis_design"],
        Path(__file__),
        ROOT / "src/analysis/f64a_raw_energy_audit.py",
        ROOT / "src/analysis/f64a_late_window_audit.py",
    ]
    identities = {str(p.resolve()): sha256(p) for p in dependencies}
    matrices = {}
    for window in range(pilot["lambda_windows"]):
        for rep in range(pilot["replicates"]):
            name = f"w{window}_r{rep}.npz"
            matrices[(window, rep)] = load_matrix(
                folder / name, hashes[name], window, rep, pilot, continuation
            )
    neighbors = neighbor_records(
        raw,
        continuation,
        blocks,
        spec["lambda_vector"],
        pilot["replicates"],
        spec["policy"],
    )
    fixed = fixed_pair_records(
        matrices,
        blocks,
        spec["lambda_vector"],
        spec["fixed_pairs"],
        pilot["energy_stride_ps"],
        spec["acf_lags_samples"],
        spec["quantiles"],
    )
    summary = summarize_neighbors(neighbors, spec["lambda_vector"])
    if (len(neighbors), summary["available_neighbor_records"], len(fixed)) != (
        240,
        228,
        480,
    ):
        raise ValueError("unexpected A1 record denominator")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".f64a-lambda-") as temp:
        staging = Path(temp)
        figures = [
            plot_neighbor_metrics(neighbors, blocks, staging, spec["plot_dpi"]),
            plot_selection_context(neighbors, blocks, staging, spec["plot_dpi"]),
            plot_fixed_pairs(fixed, blocks, staging, spec["plot_dpi"]),
        ]
        if any(sha256(folder / name) != digest for name, digest in hashes.items()):
            raise ValueError("production NPZ changed during A1 analysis")
        if any(sha256(Path(path)) != digest for path, digest in identities.items()):
            raise ValueError("analysis dependency changed during A1 analysis")
        report = {
            "schema_version": 1,
            "analysis_id": spec["analysis_id"],
            "exploratory_post_result": True,
            "scope": (
                "F64A folded-only lambda/comparator characterization; no stationarity "
                "test, stopping rule, structural cause, MBAR refit, or GPU work"
            ),
            "configuration": spec,
            "source_raw_audit_sha256": spec["raw_audit_sha256"],
            "source_continuation_sha256": spec["continuation_report_sha256"],
            "input_npz_sha256": hashes,
            "dependency_sha256": identities,
            "runtime": {
                "python": platform.python_version(),
                "packages": {
                    package: importlib.metadata.version(package)
                    for package in ("numpy", "scipy", "matplotlib", "PyYAML")
                },
            },
            "neighbor_summary": summary,
            "neighbor_records": neighbors,
            "fixed_pair_summary": {
                "record_count": len(fixed),
                "sampled_paths_per_block": pilot["lambda_windows"]
                * pilot["replicates"],
                "blocks": len(blocks),
                "fixed_pairs": len(spec["fixed_pairs"]),
                "dependence_note": (
                    "Pairs evaluated on the same configurations are correlated. "
                    "Divide-by-lambda-spacing is intentionally not reported."
                ),
            },
            "fixed_pair_records": fixed,
            "figures": figures,
            "figure_traceability": {
                "neighbor_full_block_metrics.png": {
                    "records": "neighbor_records",
                    "metrics": list(FULL_METRICS),
                },
                "selection_context.png": {
                    "records": "neighbor_records",
                    "metrics": [
                        "directional_overlap",
                        "adaptive_raw_suffix_n",
                        "adaptive_selected_n",
                    ],
                },
                "fixed_pair_metrics.png": {
                    "records": "fixed_pair_records",
                    "metrics": ["signed_half_drift_kT", "absolute_half_drift_kT"],
                },
            },
            "limitations": [
                "Neighbor directions share configurations and are not independent replications.",
                "Repeats use independent boxes but share a protein start; distinct basins are not established.",
                "Normalized drift is descriptive, not a stationarity test or effective sample size.",
                "Overlap and fixed-pair energies do not provide per-window MBAR error contributions.",
                "Fixed-pair reduced-potential differences are not free energies and do not identify structural causes.",
            ],
        }
        report_name = "lambda_comparator.json"
        (staging / report_name).write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n"
        )
        output.mkdir()
        for name in figures + [report_name]:
            os.link(staging / name, output / name)
    print(f"Wrote {output / 'lambda_comparator.json'}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--npz-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    analyze(args.config, args.npz_dir, args.output_dir)


if __name__ == "__main__":
    main()
