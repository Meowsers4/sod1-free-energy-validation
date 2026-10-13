"""CPU calibration of paired C2 movement and late-spread intervals."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import erf, exp, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_paired_interval_stress_v1.json"


def folded_normal_mean(mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return sigma * sqrt(2 / pi) * exp(-mu * mu / (2 * sigma * sigma)) + mu * erf(mu / (sqrt(2) * sigma))


def load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    if (cfg["analysis_id"] != "f64a_c2_paired_interval_stress_v1"
            or cfg["attempted_pair_counts"] != [10, 33]
            or cfg["trials_per_scenario"] < 500
            or cfg["bootstrap_replicates"] < 199
            or cfg["minimum_complete_pairs_for_interval"] < 3
            or set(cfg["missingness_regimes"]) != {
                "complete", "mcar", "mnar_hrex_high_movement"}
            or cfg["within_pair_correlations"] != [0.6, -0.6]
            or not cfg["mnar_is_failure_probe_only"]):
        raise ValueError("invalid paired interval specification")
    return cfg, sha256(raw).hexdigest()


def draw_attempts(cfg: dict, n: int, rho: float, missingness: str,
                  rng: np.random.Generator) -> dict:
    """Each row is one independent paired start; missing arms remain attempts."""
    z = rng.normal(size=(4, n))
    direction = sqrt(1 - rho * rho)
    signed_b = cfg["baseline_signed_movement_mean"] + cfg["baseline_signed_movement_sd"] * z[0]
    signed_h = cfg["hrex_signed_movement_mean"] + cfg["hrex_signed_movement_sd"] * (rho * z[0] + direction * z[1])
    late_b = cfg["baseline_late_sd"] * z[2]
    late_h = cfg["hrex_late_sd"] * (rho * z[2] + direction * z[3])
    # These early values make D = G_late - G_early exactly.
    early_b = late_b - signed_b
    early_h = late_h - signed_h
    observed_b = np.ones(n, dtype=bool)
    observed_h = np.ones(n, dtype=bool)
    if missingness == "mcar":
        row = cfg["missingness_regimes"]["mcar"]
        observed_b = rng.random(n) >= row["baseline_missing_probability"]
        observed_h = rng.random(n) >= row["hrex_missing_probability"]
    elif missingness == "mnar_hrex_high_movement":
        threshold = np.quantile(abs(signed_h), 0.75)
        p = cfg["missingness_regimes"][missingness]["hrex_missing_if_top_quartile_probability"]
        observed_h = ~((abs(signed_h) >= threshold) & (rng.random(n) < p))
    elif missingness != "complete":
        raise ValueError("unknown missingness")
    return {"early_baseline": early_b, "early_hrex": early_h,
            "late_baseline": late_b, "late_hrex": late_h,
            "signed_baseline": signed_b, "signed_hrex": signed_h,
            "observed_baseline": observed_b, "observed_hrex": observed_h}


def paired_intervals(attempts: dict, cfg: dict,
                     rng: np.random.Generator) -> dict:
    observed_b = attempts["observed_baseline"]
    observed_h = attempts["observed_hrex"]
    complete = observed_b & observed_h
    n = int(complete.sum())
    out = {"attempted_pairs": len(complete),
           "complete_pairs": n,
           "missing_baseline": int((~observed_b).sum()),
           "missing_hrex": int((~observed_h).sum()),
           "status": "unavailable"}
    if n < cfg["minimum_complete_pairs_for_interval"]:
        return out
    d_b = (attempts["late_baseline"] - attempts["early_baseline"])[complete]
    d_h = (attempts["late_hrex"] - attempts["early_hrex"])[complete]
    paired_movement = abs(d_h) - abs(d_b)
    alpha = 1 - cfg["nominal_coverage"]
    mean = float(np.mean(paired_movement))
    halfwidth = float(t.ppf(1 - alpha / 2, n - 1) * np.std(paired_movement, ddof=1) / sqrt(n))
    b = attempts["late_baseline"][complete]
    h = attempts["late_hrex"][complete]
    point_spread = float(np.std(h, ddof=1) - np.std(b, ddof=1))
    index = rng.integers(n, size=(cfg["bootstrap_replicates"], n))
    spread_star = np.std(h[index], axis=1, ddof=1) - np.std(b[index], axis=1, ddof=1)
    lower, upper = np.quantile(spread_star, [alpha / 2, 1 - alpha / 2])
    out.update({"status": "complete", "movement_point": mean,
                "movement_interval": [mean - halfwidth, mean + halfwidth],
                "spread_point": point_spread,
                "spread_interval": [float(lower), float(upper)]})
    return out


def run(config_path: Path) -> dict:
    cfg, digest = load_config(config_path)
    truth_m = (folded_normal_mean(cfg["hrex_signed_movement_mean"], cfg["hrex_signed_movement_sd"])
               - folded_normal_mean(cfg["baseline_signed_movement_mean"], cfg["baseline_signed_movement_sd"]))
    truth_s = cfg["hrex_late_sd"] - cfg["baseline_late_sd"]
    summaries = []
    rng = np.random.default_rng(cfg["seed"])
    for n in cfg["attempted_pair_counts"]:
        for rho in cfg["within_pair_correlations"]:
            for missingness in cfg["missingness_regimes"]:
                records = []
                for _ in range(cfg["trials_per_scenario"]):
                    attempts = draw_attempts(cfg, n, rho, missingness, rng)
                    records.append(paired_intervals(attempts, cfg, rng))
                complete = [row for row in records if row["status"] == "complete"]
                movement_covered = sum(row["movement_interval"][0] <= truth_m <= row["movement_interval"][1]
                                       for row in complete)
                spread_covered = sum(row["spread_interval"][0] <= truth_s <= row["spread_interval"][1]
                                     for row in complete)
                summaries.append({"attempted_pairs_per_trial": n, "within_pair_correlation": rho,
                                  "missingness": missingness,
                                  "attempted_trials": len(records), "interval_available_trials": len(complete),
                                  "mean_complete_pairs": float(np.mean([r["complete_pairs"] for r in records])),
                                  "movement_truth_covered": movement_covered,
                                  "spread_truth_covered": spread_covered,
                                  "movement_conditional_coverage": movement_covered / len(complete) if complete else None,
                                  "spread_conditional_coverage": spread_covered / len(complete) if complete else None,
                                  "both_interval_methods_pass": bool(
                                      missingness != "mnar_hrex_high_movement" and complete
                                      and movement_covered / len(complete) >= cfg["minimum_acceptable_conditional_coverage"]
                                      and spread_covered / len(complete) >= cfg["minimum_acceptable_conditional_coverage"])
                                      if missingness != "mnar_hrex_high_movement" else None})
    return {"analysis_id": cfg["analysis_id"], "config_sha256": digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "truth_movement_contrast": truth_m, "truth_spread_contrast": truth_s,
            "limitations": ["Constructed normal paired starts, not protein FEP.",
                            "MCAR is independent of outcomes; MNAR probe is deliberately biased.",
                            "Conditional coverage excludes unavailable trials but availability is reported separately.",
                            "No useful-effect threshold or production pair count is selected."],
            "summaries": summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite interval report")
    report = run(args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_PAIRED_INTERVAL_STRESS_RECORDED {args.output}")


if __name__ == "__main__":
    main()
