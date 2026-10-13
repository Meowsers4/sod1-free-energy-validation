"""Separate CPU calibration of paired BCa spread intervals."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

from src.analysis.f64a_c2_paired_interval_stress import (
    draw_attempts, folded_normal_mean, load_config as load_base_config,
    paired_intervals,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_paired_interval_bca_v1.json"


def load_config(path: Path) -> tuple[dict, dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    base_path = ROOT / cfg["base_spec"]
    base, base_digest = load_base_config(base_path)
    runner = ROOT / "src/analysis/f64a_c2_paired_interval_stress.py"
    if (cfg["analysis_id"] != "f64a_c2_paired_interval_bca_v1"
            or base_digest != cfg["base_spec_sha256"]
            or sha256(runner.read_bytes()).hexdigest() != cfg["base_runner_sha256"]
            or cfg["development_trials_per_scenario"] < 100
            or cfg["heldout_trials_per_scenario"] < 500
            or cfg["development_seed"] == cfg["heldout_seed"]
            or cfg["bootstrap_replicates"] < 399
            or cfg["spread_interval"] != "paired_BCa_bootstrap_on_HREX_minus_baseline_late_SD"
            or cfg["movement_interval"] != "paired_Student_t_unchanged"
            or cfg["failure"] != "unavailable_interval_retained_in_attempted_trial_denominator"
            or not cfg["mnar_is_failure_probe_only"]):
        raise ValueError("invalid frozen BCa specification or base identity")
    base["bootstrap_replicates"] = cfg["bootstrap_replicates"]
    return cfg, base, sha256(raw).hexdigest()


def spread_difference(b: np.ndarray, h: np.ndarray) -> float:
    return float(np.std(h, ddof=1) - np.std(b, ddof=1))


def paired_bca_interval(b: np.ndarray, h: np.ndarray, *, replicates: int,
                        coverage: float, rng: np.random.Generator) -> tuple[float, float]:
    """BCa resamples pair rows together and jackknifes the same paired rows."""
    if len(b) != len(h) or len(b) < 5:
        raise ValueError("too few matched pairs for BCa")
    n = len(b)
    point = spread_difference(b, h)
    index = rng.integers(n, size=(replicates, n))
    star = np.std(h[index], axis=1, ddof=1) - np.std(b[index], axis=1, ddof=1)
    if not np.isfinite(star).all():
        raise FloatingPointError("nonfinite bootstrap spread")
    p_less = (np.count_nonzero(star < point) + 0.5 * np.count_nonzero(star == point)) / replicates
    p_less = np.clip(p_less, 0.5 / replicates, 1 - 0.5 / replicates)
    z0 = norm.ppf(p_less)
    jack = np.array([spread_difference(np.delete(b, i), np.delete(h, i))
                     for i in range(n)])
    centered = np.mean(jack) - jack
    denominator = 6 * np.sum(centered ** 2) ** 1.5
    if denominator == 0:
        raise ValueError("degenerate paired jackknife")
    acceleration = np.sum(centered ** 3) / denominator
    alpha = (1 - coverage) / 2
    z = norm.ppf([alpha, 1 - alpha])
    divisor = 1 - acceleration * (z0 + z)
    if np.any(divisor <= 0):
        raise ValueError("BCa adjusted quantile is undefined")
    adjusted = norm.cdf(z0 + (z0 + z) / divisor)
    if not np.all((adjusted > 0) & (adjusted < 1)):
        raise ValueError("BCa adjusted quantile is outside sample support")
    lower, upper = np.quantile(star, adjusted)
    return float(lower), float(upper)


def run(config_path: Path, cohort: str) -> dict:
    cfg, base, digest = load_config(config_path)
    if cohort not in ("development", "heldout"):
        raise ValueError("invalid cohort")
    trials = cfg[f"{cohort}_trials_per_scenario"]
    rng = np.random.default_rng(cfg[f"{cohort}_seed"])
    truth_m = (folded_normal_mean(base["hrex_signed_movement_mean"], base["hrex_signed_movement_sd"])
               - folded_normal_mean(base["baseline_signed_movement_mean"], base["baseline_signed_movement_sd"]))
    truth_s = base["hrex_late_sd"] - base["baseline_late_sd"]
    summaries = []
    for n in base["attempted_pair_counts"]:
        for rho in base["within_pair_correlations"]:
            for missingness in base["missingness_regimes"]:
                complete_count = movement_covered = spread_covered = 0
                sum_complete = 0
                failure_counts = {}
                for _ in range(trials):
                    attempts = draw_attempts(base, n, rho, missingness, rng)
                    row = paired_intervals(attempts, base, rng)
                    sum_complete += row["complete_pairs"]
                    if row["status"] != "complete":
                        failure_counts["too_few_complete_pairs"] = failure_counts.get("too_few_complete_pairs", 0) + 1
                        continue
                    mask = attempts["observed_baseline"] & attempts["observed_hrex"]
                    try:
                        interval = paired_bca_interval(
                            attempts["late_baseline"][mask], attempts["late_hrex"][mask],
                            replicates=cfg["bootstrap_replicates"],
                            coverage=base["nominal_coverage"], rng=rng)
                    except (ValueError, FloatingPointError) as exc:
                        key = type(exc).__name__ + ": " + str(exc)
                        failure_counts[key] = failure_counts.get(key, 0) + 1
                        continue
                    complete_count += 1
                    movement_covered += row["movement_interval"][0] <= truth_m <= row["movement_interval"][1]
                    spread_covered += interval[0] <= truth_s <= interval[1]
                movement_rate = movement_covered / complete_count if complete_count else None
                spread_rate = spread_covered / complete_count if complete_count else None
                summaries.append({"attempted_pairs_per_trial": n, "within_pair_correlation": rho,
                                  "missingness": missingness, "attempted_trials": trials,
                                  "both_intervals_available_trials": complete_count,
                                  "mean_complete_pairs": sum_complete / trials,
                                  "unavailable_reasons": failure_counts,
                                  "movement_truth_covered": movement_covered,
                                  "spread_truth_covered": spread_covered,
                                  "movement_conditional_coverage": movement_rate,
                                  "spread_conditional_coverage": spread_rate,
                                  "both_interval_methods_pass": bool(
                                      movement_rate is not None and spread_rate is not None
                                      and movement_rate >= cfg["minimum_acceptable_conditional_coverage"]
                                      and spread_rate >= cfg["minimum_acceptable_conditional_coverage"])
                                      if missingness != "mnar_hrex_high_movement" else None})
    return {"analysis_id": cfg["analysis_id"], "cohort": cohort,
            "config_sha256": digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "base_spec_sha256": cfg["base_spec_sha256"],
            "truth_movement_contrast": truth_m, "truth_spread_contrast": truth_s,
            "limitations": ["Constructed paired normal data, not C2 protein output.",
                            "BCa can be undefined with few or degenerate complete pairs.",
                            "MNAR is a failure probe; complete-case intervals may be biased.",
                            "A synthetic pass does not select a pair count or production rule."],
            "summaries": summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cohort", choices=("development", "heldout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite BCa report")
    report = run(args.config, args.cohort)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_BCA_INTERVAL_STRESS_RECORDED {args.output}")


if __name__ == "__main__":
    main()
