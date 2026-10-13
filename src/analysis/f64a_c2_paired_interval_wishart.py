"""CPU-only normal-model calibration of a paired late-SD contrast interval."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path

import numpy as np
from scipy.stats import t

from src.analysis.f64a_c2_paired_interval_stress import (
    draw_attempts, folded_normal_mean, load_config as load_base_config,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_paired_interval_wishart_v1.json"


def load_config(path: Path) -> tuple[dict, dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    base, base_digest = load_base_config(ROOT / cfg["base_spec"])
    runner = ROOT / "src/analysis/f64a_c2_paired_interval_stress.py"
    if (cfg["analysis_id"] != "f64a_c2_paired_interval_wishart_v1"
            or base_digest != cfg["base_spec_sha256"]
            or sha256(runner.read_bytes()).hexdigest() != cfg["base_runner_sha256"]
            or cfg["development_trials_per_scenario"] < 100
            or cfg["heldout_trials_per_scenario"] < 500
            or cfg["development_seed"] == cfg["heldout_seed"]
            or cfg["pivot_draws"] < 999
            or cfg["minimum_complete_pairs_for_interval"] != 5
            or not cfg["normal_model_only"]
            or not cfg["mnar_is_failure_probe_only"]):
        raise ValueError("invalid frozen Wishart specification or base identity")
    return cfg, base, sha256(raw).hexdigest()


def paired_wishart_interval(b: np.ndarray, h: np.ndarray, *, draws: int,
                            coverage: float, rng: np.random.Generator) -> tuple[float, float]:
    """Resample the paired covariance through an inverse Wishart pivot.

    This is a normal-model confidence-distribution candidate. Its empirical
    frequentist coverage is screened separately; it makes no distribution-free
    claim for protein repeats.
    """
    b = np.asarray(b, dtype=float)
    h = np.asarray(h, dtype=float)
    if b.ndim != 1 or h.shape != b.shape or len(b) < 5:
        raise ValueError("too few complete matched pairs")
    if not np.isfinite(b).all() or not np.isfinite(h).all():
        raise ValueError("nonfinite paired values")
    if draws < 999 or not 0 < coverage < 1:
        raise ValueError("invalid pivot settings")
    df = len(b) - 1
    sample_covariance = np.cov(np.column_stack((b, h)), rowvar=False, ddof=1)
    try:
        cholesky = np.linalg.cholesky(sample_covariance)
    except np.linalg.LinAlgError as exc:
        raise ValueError("degenerate paired covariance") from exc
    z = rng.normal(size=(draws, df, 2))
    w = np.einsum("rni,rnj->rij", z, z)
    inverse_w = np.linalg.inv(w)
    candidate = df * (cholesky @ inverse_w @ cholesky.T)
    difference = np.sqrt(candidate[:, 1, 1]) - np.sqrt(candidate[:, 0, 0])
    lower, upper = np.quantile(difference, [(1 - coverage) / 2, (1 + coverage) / 2])
    return float(lower), float(upper)


def run(config_path: Path, cohort: str) -> dict:
    cfg, base, config_digest = load_config(config_path)
    if cohort not in ("development", "heldout"):
        raise ValueError("invalid cohort")
    rng = np.random.default_rng(cfg[f"{cohort}_seed"])
    trials = cfg[f"{cohort}_trials_per_scenario"]
    truth_m = (folded_normal_mean(base["hrex_signed_movement_mean"], base["hrex_signed_movement_sd"])
               - folded_normal_mean(base["baseline_signed_movement_mean"], base["baseline_signed_movement_sd"]))
    truth_s = base["hrex_late_sd"] - base["baseline_late_sd"]
    summaries = []
    for attempted in base["attempted_pair_counts"]:
        for correlation in base["within_pair_correlations"]:
            for missingness in base["missingness_regimes"]:
                movement_covered = spread_covered = available = complete_total = 0
                failures: dict[str, int] = {}
                for _ in range(trials):
                    data = draw_attempts(base, attempted, correlation, missingness, rng)
                    mask = data["observed_baseline"] & data["observed_hrex"]
                    n = int(np.sum(mask))
                    complete_total += n
                    if n < cfg["minimum_complete_pairs_for_interval"]:
                        failures["too_few_complete_pairs"] = failures.get("too_few_complete_pairs", 0) + 1
                        continue
                    b, h = data["late_baseline"][mask], data["late_hrex"][mask]
                    try:
                        spread_interval = paired_wishart_interval(
                            b, h, draws=cfg["pivot_draws"], coverage=base["nominal_coverage"], rng=rng)
                    except (ValueError, np.linalg.LinAlgError) as exc:
                        key = type(exc).__name__ + ": " + str(exc)
                        failures[key] = failures.get(key, 0) + 1
                        continue
                    difference = abs(data["signed_hrex"][mask]) - abs(data["signed_baseline"][mask])
                    point = float(np.mean(difference))
                    halfwidth = float(t.ppf((1 + base["nominal_coverage"]) / 2, n - 1)
                                      * np.std(difference, ddof=1) / sqrt(n))
                    available += 1
                    movement_covered += point - halfwidth <= truth_m <= point + halfwidth
                    spread_covered += spread_interval[0] <= truth_s <= spread_interval[1]
                movement_rate = movement_covered / available if available else None
                spread_rate = spread_covered / available if available else None
                summaries.append({
                    "attempted_pairs_per_trial": attempted,
                    "within_pair_correlation": correlation,
                    "missingness": missingness,
                    "attempted_trials": trials,
                    "both_intervals_available_trials": available,
                    "mean_complete_pairs": complete_total / trials,
                    "unavailable_reasons": failures,
                    "movement_truth_covered": movement_covered,
                    "spread_truth_covered": spread_covered,
                    "movement_conditional_coverage": movement_rate,
                    "spread_conditional_coverage": spread_rate,
                    "both_interval_methods_pass": (
                        movement_rate >= cfg["minimum_acceptable_conditional_coverage"]
                        and spread_rate >= cfg["minimum_acceptable_conditional_coverage"])
                        if missingness != "mnar_hrex_high_movement" and available else None,
                })
    return {"analysis_id": cfg["analysis_id"], "cohort": cohort,
            "config_sha256": config_digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "base_spec_sha256": cfg["base_spec_sha256"],
            "truth_movement_contrast": truth_m,
            "truth_spread_contrast": truth_s,
            "normal_model_only": True,
            "summaries": summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cohort", choices=("development", "heldout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Wishart report")
    report = run(args.config, args.cohort)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_WISHART_INTERVAL_STRESS_RECORDED {args.output}")


if __name__ == "__main__":
    main()
