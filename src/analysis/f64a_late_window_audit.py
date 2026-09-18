"""Report-only, post-result CPU audit; no MBAR refits or GPU dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_late_window_audit.yaml"


def sha256(path: Path) -> str:
    """Hash an artifact without changing it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float) -> None:
    """Check arithmetic reconciliation, not scientific convergence."""
    if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f"arithmetic mismatch: {actual} != {expected}")


def validate_report(report: dict, design: dict, windows: int, repeats: int) -> None:
    """Refuse missing fits, malformed selection and inconsistent summaries."""

    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite report value")
        if isinstance(value, dict):
            for child in value.values():
                finite(child)
        elif isinstance(value, list):
            for child in value:
                finite(child)

    finite(report)
    if report["design"] != design or report["v1_reproduction_passed"] is not True:
        raise ValueError("unregistered design or failed v1 reproduction")
    expected = {
        (p["label"], b["label"], r)
        for p in design["policies"]
        for b in design["blocks"]
        for r in range(repeats)
    }
    expected |= {
        ("adaptive", b["label"], r)
        for b in design["cumulative"]
        for r in range(repeats)
    }
    records = report["records"]
    if (
        len(records) != len(expected)
        or {(r["policy"], r["block"], r["replicate"]) for r in records} != expected
    ):
        raise ValueError("missing or duplicate fit")
    slices = {b["label"]: b for b in design["blocks"] + design["cumulative"]}
    for record in records:
        block = slices[record["block"]]
        start, stop = block["start"], block["stop"]
        if (record["raw_column_start"], record["raw_column_stop"]) != (start, stop):
            raise ValueError("fit slice mismatch")
        ds, edges = record["window_diagnostics"], record["adjacent_diagnostics"]
        if len(ds) != windows or {d["window"] for d in ds} != set(range(windows)):
            raise ValueError("incomplete selection diagnostics")
        if len(edges) != windows - 1 or {
            (e["lower_window"], e["upper_window"]) for e in edges
        } != {(w, w + 1) for w in range(windows - 1)}:
            raise ValueError("incomplete adjacent diagnostics")
        for d in ds:
            cut, first, last = (
                d[k]
                for k in (
                    "trim_start_column",
                    "first_selected_column",
                    "last_selected_column",
                )
            )
            if not (
                d["n_raw"] == stop - start
                and 0 <= cut <= first <= last < stop - start
                and d["n_after_trim"] == stop - start - cut
                and 0 < d["n_retained"] <= d["n_after_trim"]
                and d["subsample_g"] >= 1
            ):
                raise ValueError("invalid selection bounds/counts")
            for key in (
                "trim_start_column",
                "first_selected_column",
                "last_selected_column",
            ):
                if d[key + "_global"] != start + d[key]:
                    raise ValueError("incorrect global selection index")
        if record["n_raw"] != (stop - start) * windows or record["n_retained"] != sum(
            d["n_retained"] for d in ds
        ):
            raise ValueError("aggregate counts mismatch")
        matrix = record["overlap_matrix"]
        if len(matrix) != windows or any(len(row) != windows for row in matrix):
            raise ValueError("overlap matrix shape mismatch")
        for e in edges:
            a, b = e["lower_window"], e["upper_window"]
            close(
                e["signed_discrepancy_kcal"],
                e["forward_dg_kcal"] - e["reverse_dg_kcal"],
            )
            close(e["overlap_lower_to_upper"], matrix[a][b])
            close(e["overlap_upper_to_lower"], matrix[b][a])
        local = [e["signed_discrepancy_kcal"] for e in edges]
        close(record["net_hysteresis_kcal"], abs(sum(local)))
        close(record["sum_absolute_hysteresis_kcal"], sum(abs(v) for v in local))
        close(record["max_absolute_hysteresis_kcal"], max(abs(v) for v in local))
    expected_summaries = {
        (p["label"], b["label"]) for p in design["policies"] for b in design["blocks"]
    }
    expected_summaries |= {("adaptive", b["label"]) for b in design["cumulative"]}
    summaries = report["summaries"] + report["cumulative_summaries"]
    if (
        len(summaries) != len(expected_summaries)
        or {(s.get("policy", "adaptive"), s["block"]) for s in summaries}
        != expected_summaries
    ):
        raise ValueError("missing or duplicate summary")
    for summary in summaries:
        group = [
            r
            for r in records
            if r["block"] == summary["block"]
            and r["policy"] == summary.get("policy", "adaptive")
        ]
        xs = [r["dg_kcal"] for r in group]
        close(summary["mean_dg_kcal"], statistics.mean(xs))
        close(summary["replicate_range_kcal"], max(xs) - min(xs))
        close(summary["replicate_sem_kcal"], statistics.stdev(xs) / math.sqrt(repeats))
        propagated = math.sqrt(sum(r["mbar_error_kcal"] ** 2 for r in group)) / repeats
        close(summary["propagated_mbar_error_kcal"], propagated)
        close(
            summary["uncertainty_kcal"], max(propagated, summary["replicate_sem_kcal"])
        )
    by_key = {(r["policy"], r["block"], r["replicate"]): r for r in records}
    expected_contrasts = {
        (p["label"], c["label"], r)
        for p in design["policies"]
        for c in design["contrasts"]
        for r in range(repeats)
    }
    cs = report["contrasts"]
    if (
        len(cs) != len(expected_contrasts)
        or {(c["policy"], c["label"], c["replicate"]) for c in cs} != expected_contrasts
    ):
        raise ValueError("missing or duplicate contrast")
    for c in cs:
        a, b = (by_key[c["policy"], c[k], c["replicate"]] for k in ("earlier", "later"))
        close(c["signed_movement_kcal"], b["dg_kcal"] - a["dg_kcal"])
    expected_movements = {
        (p["label"], c["label"])
        for p in design["policies"]
        for c in design["contrasts"]
    }
    if (
        len(report["contrast_summaries"]) != len(expected_movements)
        or {(c["policy"], c["label"]) for c in report["contrast_summaries"]}
        != expected_movements
    ):
        raise ValueError("missing or duplicate movement summary")
    for c in report["contrast_summaries"]:
        xs = [
            r["signed_movement_kcal"]
            for r in cs
            if r["policy"] == c["policy"] and r["label"] == c["label"]
        ]
        close(c["mean_signed_movement_kcal"], statistics.mean(xs))
        close(c["paired_movement_sem_kcal"], statistics.stdev(xs) / math.sqrt(repeats))
        close(c["max_absolute_movement_kcal"], max(abs(v) for v in xs))
    expected_changes = {
        (p, label, r, w)
        for p, label, r in expected_contrasts
        for w in range(windows - 1)
    }
    changes = report["local_changes"]
    if (
        len(changes) != len(expected_changes)
        or {
            (c["policy"], c["contrast"], c["replicate"], c["lower_window"])
            for c in changes
        }
        != expected_changes
    ):
        raise ValueError("missing or duplicate local change")
    definitions = {c["label"]: c for c in design["contrasts"]}
    for c in changes:
        definition = definitions[c["contrast"]]
        a, b = (
            by_key[c["policy"], definition[k], c["replicate"]]
            for k in ("earlier", "later")
        )
        w = c["lower_window"]
        u, v = (
            [e for e in r["adjacent_diagnostics"] if e["lower_window"] == w][0]
            for r in (a, b)
        )
        if c["upper_window"] != w + 1:
            raise ValueError("local change pair mismatch")
        for key in ("forward_dg_kcal", "reverse_dg_kcal", "signed_discrepancy_kcal"):
            close(c[key + "_change"], v[key] - u[key])


def summarize(report: dict, focus: list[str], heavy: float) -> dict:
    """Join selection to local diagnostics without attributing endpoint causality."""
    selections, edges, fits = [], [], []
    for r in report["records"]:
        key = {k: r[k] for k in ("policy", "block", "replicate")}
        by_window = {d["window"]: d for d in r["window_diagnostics"]}
        for d in by_window.values():
            selections.append(
                {
                    **key,
                    **d,
                    "trim_fraction_observed": d["trim_start_column"] / d["n_raw"],
                }
            )
        for e in r["adjacent_diagnostics"]:
            edges.append(
                {
                    **key,
                    **e,
                    "minimum_directional_overlap": min(
                        e["overlap_lower_to_upper"], e["overlap_upper_to_lower"]
                    ),
                    "lower_n_retained": by_window[e["lower_window"]]["n_retained"],
                    "upper_n_retained": by_window[e["upper_window"]]["n_retained"],
                    "lower_trim_fraction": by_window[e["lower_window"]][
                        "trim_start_column"
                    ]
                    / by_window[e["lower_window"]]["n_raw"],
                    "upper_trim_fraction": by_window[e["upper_window"]][
                        "trim_start_column"
                    ]
                    / by_window[e["upper_window"]]["n_raw"],
                }
            )
        ds = r["window_diagnostics"]
        fits.append(
            {
                **key,
                **{
                    k: r[k]
                    for k in (
                        "dg_kcal",
                        "mbar_error_kcal",
                        "net_hysteresis_kcal",
                        "sum_absolute_hysteresis_kcal",
                        "min_adjacent_overlap",
                        "solver_notes",
                    )
                },
                "heavy_trim_windows": [
                    d["window"]
                    for d in ds
                    if d["trim_start_column"] / d["n_raw"] >= heavy
                ],
                "minimum_retained_count": min(d["n_retained"] for d in ds),
                "median_retained_count": statistics.median(d["n_retained"] for d in ds),
                "largest_trim_fraction": max(
                    d["trim_start_column"] / d["n_raw"] for d in ds
                ),
                "largest_subsample_g": max(d["subsample_g"] for d in ds),
                "cancellation_fraction": 1
                - r["net_hysteresis_kcal"] / r["sum_absolute_hysteresis_kcal"]
                if r["sum_absolute_hysteresis_kcal"]
                else None,
            }
        )
    paired = []
    for policy in report["design"]["policies"]:
        for block in focus:
            group = [
                e
                for e in edges
                if e["policy"] == policy["label"] and e["block"] == block
            ]
            for w in sorted({e["lower_window"] for e in group}):
                es = [e for e in group if e["lower_window"] == w]
                paired.append(
                    {
                        "policy": policy["label"],
                        "block": block,
                        "lower_window": w,
                        "upper_window": w + 1,
                        "mean_absolute_hysteresis_kcal": statistics.mean(
                            abs(e["signed_discrepancy_kcal"]) for e in es
                        ),
                        "minimum_directional_overlap": min(
                            e["minimum_directional_overlap"] for e in es
                        ),
                    }
                )
    return {
        "fit_summaries": fits,
        "window_selection": selections,
        "adjacent_pairs": edges,
        "focus_pair_summaries": paired,
        "focus_heavy_trim_windows": [
            d
            for d in selections
            if d["block"] in focus and d["trim_fraction_observed"] >= heavy
        ],
        "registered_primary_comparison": [
            c
            for c in report["contrast_summaries"]
            if c["label"] == "primary_new_blocks"
        ],
    }


def audit(config: Path = DEFAULT_CONFIG) -> Path:
    """Preserve source identity and atomically write a new descriptive report."""
    spec = yaml.safe_load(config.read_text())
    source = ROOT / spec["input"]
    digest = sha256(source)
    if digest != spec["input_sha256"]:
        raise ValueError("supplied report hash mismatch")
    design = yaml.safe_load((ROOT / spec["registered_design"]).read_text())
    pilot = yaml.safe_load((ROOT / spec["pilot_config"]).read_text())
    report = json.loads(source.read_text())
    validate_report(report, design, pilot["lambda_windows"], pilot["replicates"])
    if not 0 <= spec["heavy_trim_fraction"] <= 1 or not set(spec["focus_blocks"]) <= {
        b["label"] for b in design["blocks"]
    }:
        raise ValueError("invalid audit reporting configuration")
    value = {
        "audit_id": "f64a_late_window_report_audit_2026_09_18",
        "exploratory_post_result": True,
        "source_sha256": digest,
        "source_analysis_identity": report["analysis_identity"],
        "audit_source_sha256": sha256(Path(__file__)),
        "audit_config_sha256": sha256(config),
        "reporting_config": spec,
        "all_fit_and_summary_checks_passed": True,
        "limitations": [
            "Report-only audit: no independent NPZ/XVG or MBAR reproduction.",
            "No refitting, dropping windows, policy selection, new pass threshold or GPU work.",
            "Local discrepancies are not additive MBAR endpoint contributions or structural mechanisms.",
            "Thinned counts and uncertainties do not establish stationarity or basin coverage.",
        ],
        **summarize(report, spec["focus_blocks"], spec["heavy_trim_fraction"]),
    }
    if sha256(source) != digest:
        raise ValueError("source report changed during audit")
    output = ROOT / spec["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=output.parent, prefix=".f64a-audit-")
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, allow_nan=False)
            handle.write("\n")
        os.link(name, output)  # Exclusive, atomic publication; never overwrite.
    finally:
        os.unlink(name)
    print(f"Wrote {output}; audited {len(report['records'])} fits")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    audit(parser.parse_args().config)


if __name__ == "__main__":
    main()
