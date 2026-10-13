"""CPU-only synchronized stationary-bootstrap stress for joint early/late MBAR.

The resampling unit is one complete 20-state time row. This preserves within-
block cross-state correlations, but the constructed data have no HREX walkers.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys

import numpy as np

from src.analysis.f64a_c2_uncertainty_stress import fit_fixed_block, stationary_ladder


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_joint_bootstrap_stress_v1.json"


def load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    seeds = cfg["development_seeds"] + cfg["heldout_seeds"]
    selection = cfg["selection"]
    if (cfg["analysis_id"] != "f64a_c2_joint_bootstrap_stress_v1"
            or cfg["state_count"] != 20
            or cfg["samples_per_block"] != 128
            or cfg["bootstrap_replicates"] < 20
            or not 1 < cfg["mean_bootstrap_block_length"] < 128
            or len(seeds) != len(set(seeds))
            or set(cfg["regimes"]) != {
                "iid", "correlated_synchronized", "long_correlation", "drifting"}
            or not all(selection[key] for key in (
                "time_rows_resampled_jointly_across_all_states",
                "whole_series_stationary_bootstrap",
                "fixed_early_late_split_after_resampling"))
            or selection["additional_equilibration_trim"] != 0
            or selection["failure"] != "retain_in_attempted_denominator"
            or selection["minimum_successful_bootstraps"] > cfg["bootstrap_replicates"]):
        raise ValueError("invalid frozen joint-bootstrap specification")
    return cfg, sha256(raw).hexdigest()


def stationary_bootstrap_indices(n: int, mean_length: int,
                                 rng: np.random.Generator) -> np.ndarray:
    """Politis–Romano random-length circular blocks across the whole series."""
    if n < 2 or not 1 < mean_length < n:
        raise ValueError("invalid bootstrap length")
    out = np.empty(n, dtype=int)
    out[0] = rng.integers(n)
    new_block = rng.random(n - 1) < 1 / mean_length
    starts = rng.integers(n, size=n - 1)
    for t in range(1, n):
        out[t] = starts[t - 1] if new_block[t - 1] else (out[t - 1] + 1) % n
    return out


def joint_difference(samples: np.ndarray, centers: np.ndarray) -> tuple[float, float, float]:
    n = len(samples) // 2
    early = fit_fixed_block(samples[:n], centers, thin=False, minimum_selected=1)
    late = fit_fixed_block(samples[n:], centers, thin=False, minimum_selected=1)
    return (float(late["estimate_kT"] - early["estimate_kT"]),
            float(early["estimate_kT"]), float(late["estimate_kT"]))


def experiment(cfg: dict, *, regime: str, seed: int, cohort: str) -> dict:
    n = cfg["samples_per_block"]
    centers = np.linspace(cfg["center_min"], cfg["center_max"], cfg["state_count"])
    model = cfg["regimes"][regime]
    samples = stationary_ladder(
        centers, samples_per_block=n, phi=model["ar1_phi"],
        shared_fraction=model["cross_state_innovation_fraction"], seed=seed)
    if model["linear_shift"]:
        samples += np.linspace(0, model["linear_shift"], 2 * n)[:, None]
    record = {"regime": regime, "cohort": cohort, "seed": seed,
              "bootstrap_attempted": cfg["bootstrap_replicates"],
              "bootstrap_successful": 0, "status": "failed"}
    try:
        observed, early, late = joint_difference(samples, centers)
        record.update({"observed_difference_kT": observed,
                       "early_estimate_kT": early, "late_estimate_kT": late})
        rng = np.random.default_rng(seed + 10_000_000)
        differences = []
        for _ in range(cfg["bootstrap_replicates"]):
            index = stationary_bootstrap_indices(
                2 * n, cfg["mean_bootstrap_block_length"], rng)
            try:
                difference, _, _ = joint_difference(samples[index], centers)
                if np.isfinite(difference):
                    differences.append(difference)
            except (ValueError, FloatingPointError, RuntimeError):
                pass
        record["bootstrap_successful"] = len(differences)
        if len(differences) < cfg["selection"]["minimum_successful_bootstraps"]:
            record["failure"] = "too_few_successful_bootstrap_fits"
            return record
        variance = float(np.var(differences, ddof=1))
        if not np.isfinite(variance) or variance <= 0:
            record["failure"] = "nonpositive_or_nonfinite_variance"
            return record
        record.update({"status": "complete", "joint_variance_kT2": variance,
                       "joint_se_kT": float(np.sqrt(variance)),
                       "bootstrap_mean_difference_kT": float(np.mean(differences)),
                       "nominal95_stationary_zero_covered": bool(
                           abs(observed) <= 1.96 * np.sqrt(variance))
                           if model["linear_shift"] == 0 else None})
    except (ValueError, FloatingPointError, RuntimeError) as exc:
        record["failure"] = f"{type(exc).__name__}: {exc}"
    return record


def summarize(records: list[dict], cfg: dict, *, regime: str, cohort: str) -> dict:
    subset = [r for r in records if r["regime"] == regime and r["cohort"] == cohort]
    complete = [r for r in subset if r["status"] == "complete"]
    out = {"regime": regime, "cohort": cohort, "attempted": len(subset),
           "complete": len(complete),
           "failed_seeds": [r["seed"] for r in subset if r["status"] != "complete"]}
    if len(complete) < 2:
        return out
    differences = np.array([r["observed_difference_kT"] for r in complete])
    empirical = float(np.var(differences, ddof=1))
    mean_estimated = float(np.mean([r["joint_variance_kT2"] for r in complete]))
    out.update({"empirical_difference_mean_kT": float(np.mean(differences)),
                "empirical_difference_variance_kT2": empirical,
                "mean_joint_variance_kT2": mean_estimated,
                "mean_variance_to_empirical_variance": mean_estimated / empirical,
                "mean_bootstrap_successful": float(np.mean(
                    [r["bootstrap_successful"] for r in complete]))})
    if cfg["regimes"][regime]["linear_shift"] == 0:
        covered = sum(r["nominal95_stationary_zero_covered"] for r in complete)
        out["nominal95_stationary_zero_coverage_count"] = covered
        out["nominal95_stationary_zero_coverage_fraction"] = covered / len(complete)
        rules = cfg["diagnostic_acceptance"]
        out["diagnostic_pass"] = bool(
            cohort == "heldout"
            and len(complete) >= rules["minimum_complete_heldout_seeds"]
            and covered >= rules["minimum_nominal95_difference_coverage_count"]
            and rules["mean_variance_to_empirical_variance_lower"] <=
                out["mean_variance_to_empirical_variance"] <=
                rules["mean_variance_to_empirical_variance_upper"])
    else:
        out["diagnostic_pass"] = None
        out["note"] = "nonstationary failure probe; stationary-bootstrap coverage is undefined"
    return out


def run(config_path: Path, *, cohort: str) -> dict:
    cfg, digest = load_config(config_path)
    if cohort not in ("development", "heldout"):
        raise ValueError("cohort must be development or heldout")
    records = []
    for regime in cfg["regimes"]:
        for seed in cfg[f"{cohort}_seeds"]:
            records.append(experiment(cfg, regime=regime, seed=seed, cohort=cohort))
    summaries = [summarize(records, cfg, regime=regime, cohort=cohort)
                 for regime in cfg["regimes"]]
    return {"analysis_id": cfg["analysis_id"], "scope": cfg["scope"],
            "cohort": cohort, "config_sha256": digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "runtime": {"python": sys.version.split()[0],
                        "pymbar": version("pymbar"), "numpy": version("numpy"),
                        "scipy": version("scipy")},
            "method_limitations": [
                "No actual replica-exchange walkers or protein potential energies.",
                "Stationary bootstrap assumes time stationarity and may fail under drift.",
                "Fixed block length and finite 128-record blocks may not capture long memory.",
                "A diagnostic pass does not qualify protein C2 uncertainty or Q."],
            "experiments": records, "summaries": summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cohort", choices=("development", "heldout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("calibration output exists; refusing overwrite")
    report = run(args.config, cohort=args.cohort)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_JOINT_BOOTSTRAP_STRESS_RECORDED {args.output}")


if __name__ == "__main__":
    main()
