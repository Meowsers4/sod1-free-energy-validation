"""CPU-only held-out stress diagnostic for conditional C2 block MBAR errors.

This stationary Gaussian harmonic construction is deliberately simpler than
protein HREX. It tests a failure mode; it cannot qualify a production SE.
"""

from __future__ import annotations

import argparse
import contextlib
from hashlib import sha256
from importlib.metadata import version
import io
import json
from math import ceil, isfinite, sqrt
from pathlib import Path
import sys

import numpy as np

from src.fep.analyze import solve_leg_mbar


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_uncertainty_stress_v1.json"


def load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    seeds = cfg["development_seeds"] + cfg["heldout_seeds"]
    if (cfg["analysis_id"] != "f64a_c2_uncertainty_stress_v1"
            or cfg["state_count"] != 20
            or cfg["samples_per_block"] < 16
            or cfg["minimum_thinned_samples_per_state"] < 2
            or cfg["center_max"] <= cfg["center_min"]
            or len(seeds) != len(set(seeds))
            or set(cfg["regimes"]) != {"iid", "correlated_synchronized"}
            or any(not 0 <= row["ar1_phi"] < 1
                   or not 0 <= row["cross_state_innovation_fraction"] < 1
                   for row in cfg["regimes"].values())
            or cfg["selection"] != {
                "fixed_early_late_blocks": True,
                "additional_equilibration_trim": 0,
                "proxy": "nearest_neighbor_reduced_energy_difference",
                "stride": "ceil(pymbar_statistical_inefficiency_within_each_block)",
                "failure": "retain_in_attempted_denominator",
            }):
        raise ValueError("invalid frozen CPU stress specification")
    return cfg, sha256(raw).hexdigest()


def stationary_ladder(
    centers: np.ndarray, *, samples_per_block: int, phi: float,
    shared_fraction: float, seed: int,
) -> np.ndarray:
    """Return two fixed blocks of samples; equal harmonic Z gives true Δf=0."""
    rng = np.random.default_rng(seed)
    n_times = 2 * samples_per_block
    n_states = len(centers)
    shared = rng.normal(size=(n_times, 1))
    local = rng.normal(size=(n_times, n_states))
    innovations = sqrt(shared_fraction) * shared + sqrt(1 - shared_fraction) * local
    deviations = np.empty_like(innovations)
    deviations[0] = innovations[0]
    for t in range(1, n_times):
        deviations[t] = phi * deviations[t - 1] + sqrt(1 - phi * phi) * innovations[t]
    return deviations + centers[None, :]


def fit_fixed_block(
    samples: np.ndarray, centers: np.ndarray, *, thin: bool,
    minimum_selected: int,
) -> dict:
    """Fit one pre-split block; never sees samples from the other block."""
    from pymbar import timeseries

    n_times, n_states = samples.shape
    selected = []
    gs = []
    for state in range(n_states):
        x = samples[:, state]
        neighbor = state + 1 if state + 1 < n_states else state - 1
        difference = (0.5 * (x - centers[neighbor]) ** 2
                      - 0.5 * (x - centers[state]) ** 2)
        g = float(timeseries.statistical_inefficiency(difference)) if thin else 1.0
        if not isfinite(g) or g < 1:
            raise ValueError("invalid within-block inefficiency")
        indices = np.arange(0, n_times, ceil(g), dtype=int)
        if len(indices) < minimum_selected:
            raise ValueError("too few selected samples in a fixed block")
        selected.append(x[indices])
        gs.append(g)
    counts = np.asarray([len(x) for x in selected], dtype=int)
    all_x = np.concatenate(selected)
    u_kn = 0.5 * (all_x[None, :] - centers[:, None]) ** 2
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        fit = solve_leg_mbar(u_kn, counts)
    return {
        "estimate_kT": fit["dg_kT"],
        "conditional_se_kT": fit["ddg_kT"],
        "minimum_selected": int(counts.min()),
        "median_selected": float(np.median(counts)),
        "maximum_g": max(gs),
        "minimum_adjacent_overlap": fit["min_adjacent"],
        "solver_notes": fit["solver_notes"],
    }


def experiment(cfg: dict, *, regime: str, seed: int, cohort: str) -> dict:
    centers = np.linspace(cfg["center_min"], cfg["center_max"],
                          cfg["state_count"])
    n = cfg["samples_per_block"]
    model = cfg["regimes"][regime]
    samples = stationary_ladder(
        centers, samples_per_block=n, phi=model["ar1_phi"],
        shared_fraction=model["cross_state_innovation_fraction"], seed=seed,
    )
    record = {"cohort": cohort, "regime": regime, "seed": seed,
              "truth_delta_f_kT": 0.0, "status": "complete", "fits": {}}
    for treatment in ("raw", "thinned"):
        try:
            early = fit_fixed_block(
                samples[:n], centers, thin=treatment == "thinned",
                minimum_selected=cfg["minimum_thinned_samples_per_state"],
            )
            late = fit_fixed_block(
                samples[n:], centers, thin=treatment == "thinned",
                minimum_selected=cfg["minimum_thinned_samples_per_state"],
            )
            difference = late["estimate_kT"] - early["estimate_kT"]
            naive_variance = (early["conditional_se_kT"] ** 2
                              + late["conditional_se_kT"] ** 2)
            record["fits"][treatment] = {
                "status": "complete", "early": early, "late": late,
                "difference_kT": difference,
                "naive_zero_covariance_difference_variance_kT2": naive_variance,
                "naive_noise_corrected_square_kT2": difference ** 2 - naive_variance,
            }
        except (ValueError, FloatingPointError, RuntimeError) as exc:
            record["fits"][treatment] = {
                "status": "failed", "reason": f"{type(exc).__name__}: {exc}",
            }
    record["status"] = ("complete" if all(
        fit["status"] == "complete" for fit in record["fits"].values())
        else "partial_or_failed")
    return record


def summarize(records: list[dict], *, regime: str, cohort: str,
              treatment: str) -> dict:
    subset = [row for row in records
              if row["regime"] == regime and row["cohort"] == cohort]
    complete = [row["fits"][treatment] for row in subset
                if row["fits"][treatment]["status"] == "complete"]
    result = {"regime": regime, "cohort": cohort, "treatment": treatment,
              "attempted": len(subset), "complete": len(complete),
              "failed_seeds": [row["seed"] for row in subset
                               if row["fits"][treatment]["status"] != "complete"]}
    if len(complete) < 2:
        return result
    differences = np.asarray([row["difference_kT"] for row in complete])
    naive = np.asarray([
        row["naive_zero_covariance_difference_variance_kT2"]
        for row in complete])
    result.update({
        "early_nominal95_truth_coverage": float(np.mean([
            abs(row["early"]["estimate_kT"]) <=
            1.96 * row["early"]["conditional_se_kT"] for row in complete])),
        "late_nominal95_truth_coverage": float(np.mean([
            abs(row["late"]["estimate_kT"]) <=
            1.96 * row["late"]["conditional_se_kT"] for row in complete])),
        "empirical_difference_variance_kT2": float(np.var(differences, ddof=1)),
        "mean_naive_zero_covariance_variance_kT2": float(np.mean(naive)),
        "mean_naive_noise_corrected_square_kT2": float(np.mean(
            differences ** 2 - naive)),
        "mean_absolute_movement_kT": float(np.mean(abs(differences))),
    })
    return result


def run(config_path: Path) -> dict:
    cfg, config_digest = load_config(config_path)
    records = []
    for regime in cfg["regimes"]:
        for cohort, key in (("development", "development_seeds"),
                            ("heldout", "heldout_seeds")):
            for seed in cfg[key]:
                records.append(experiment(cfg, regime=regime, seed=seed,
                                          cohort=cohort))
    summaries = [summarize(records, regime=regime, cohort=cohort,
                           treatment=treatment)
                 for regime in cfg["regimes"]
                 for cohort in ("development", "heldout")
                 for treatment in ("raw", "thinned")]
    return {"analysis_id": cfg["analysis_id"], "scope": cfg["scope"],
            "config_sha256": config_digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "runtime": {"python": sys.version.split()[0],
                        "pymbar": version("pymbar"),
                        "numpy": version("numpy"),
                        "scipy": version("scipy")},
            "truth_endpoint_delta_f_kT": 0.0,
            "limitations": [
                "Stationary Gaussian harmonic ladder, not GROMACS protein dynamics.",
                "Cross-state shared innovations are not actual HREX swaps.",
                "Conditional PyMBAR SE and zero-covariance difference variance are diagnostics only.",
                "No point noise-corrected C2 endpoint or production uncertainty is qualified.",
            ],
            "experiments": records, "summaries": summaries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cfg, _ = load_config(args.config)
    output = args.output or ROOT / cfg["report"]
    if output.exists():
        raise ValueError("calibration output already exists; refusing overwrite")
    report = run(args.config)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_CPU_UNCERTAINTY_STRESS_RECORDED {output}")


if __name__ == "__main__":
    main()
