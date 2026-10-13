"""Constructed walker-lineage CPU stress of synchronized MBAR resampling."""

from __future__ import annotations

import argparse
import contextlib
from hashlib import sha256
import io
import json
from math import sqrt
from pathlib import Path

import numpy as np

from src.analysis.f64a_c2_joint_bootstrap_stress import stationary_bootstrap_indices


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_walker_stress_v1.json"


def load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    seeds = cfg["development_seeds"] + cfg["heldout_seeds"]
    if (cfg["analysis_id"] != "f64a_c2_walker_stress_v1"
            or cfg["state_count"] != 20
            or cfg["samples_per_block"] < 256
            or cfg["bootstrap_replicates"] < 20
            or cfg["minimum_successful_bootstraps"] > cfg["bootstrap_replicates"]
            or not 1 < cfg["primary_mean_block_length"] < cfg["samples_per_block"]
            or any(not 1 < x < cfg["samples_per_block"]
                   for x in cfg["development_sensitivity_mean_block_lengths"])
            or cfg["exchange_interval_records"] < 1
            or len(seeds) != len(set(seeds))
            or set(cfg["regimes"]) != {"iid", "walker_correlated",
                                         "walker_long_correlation", "walker_drift"}
            or any(not 0 <= row["ar1_phi"] < 1
                   or not 0 <= row["shared_fraction"] < 1
                   or not 0 <= row["swap_probability"] <= 1
                   for row in cfg["regimes"].values())
            or cfg["resampling"] !=
                "synchronized_all_state_rows_with_original_walker_map_contiguous_inside_stationary_blocks"
            or cfg["failure"] != "retain_all_attempted_seeds_and_bootstrap_failures"):
        raise ValueError("invalid frozen walker stress specification")
    return cfg, sha256(raw).hexdigest()


def simulate_walker_ladder(cfg: dict, regime: str, seed: int) -> tuple[np.ndarray, np.ndarray, dict]:
    """Exchangeable OU walkers with identity-preserving adjacent swaps.

    Swap decisions are coordinate-independent: this preserves the known
    harmonic marginal but is not a Metropolis HREX model.
    """
    rng = np.random.default_rng(seed)
    model = cfg["regimes"][regime]
    k = cfg["state_count"]
    n = 2 * cfg["samples_per_block"]
    centers = np.linspace(cfg["center_min"], cfg["center_max"], k)
    walker_by_state = np.empty((n, k), dtype=int)
    samples = np.empty((n, k), dtype=float)
    mapping = np.arange(k)
    walker_residual = rng.normal(size=k)
    phi = model["ar1_phi"]
    shared_fraction = model["shared_fraction"]
    proposed = accepted = rounds = 0
    for t in range(n):
        if t:
            innovation = (sqrt(shared_fraction) * rng.normal()
                          + sqrt(1 - shared_fraction) * rng.normal(size=k))
            walker_residual = phi * walker_residual + sqrt(1 - phi * phi) * innovation
        if t and t % cfg["exchange_interval_records"] == 0:
            parity = rounds % 2
            for state in range(parity, k - 1, 2):
                proposed += 1
                if rng.random() < model["swap_probability"]:
                    mapping[state], mapping[state + 1] = mapping[state + 1], mapping[state]
                    accepted += 1
            rounds += 1
        walker_by_state[t] = mapping
        samples[t] = centers + walker_residual[mapping]
    if model["linear_shift"]:
        samples += np.linspace(0, model["linear_shift"], n)[:, None]
    validate_walker_history(walker_by_state, cfg["exchange_interval_records"])
    return samples, walker_by_state, {
        "exchange_rounds": rounds, "proposed_swaps": proposed,
        "accepted_swaps": accepted,
        "final_state_to_walker": mapping.tolist()}


def validate_walker_history(mapping: np.ndarray, interval: int) -> None:
    """Require a permutation at every time and changes only at exchange times."""
    if mapping.ndim != 2 or mapping.shape[1] < 2 or interval < 1:
        raise ValueError("invalid walker history shape")
    k = mapping.shape[1]
    expected = np.arange(k)
    if not np.array_equal(mapping[0], expected):
        raise ValueError("initial walker mapping is not identity")
    for t, row in enumerate(mapping):
        if not np.array_equal(np.sort(row), expected):
            raise ValueError(f"walker mapping is not a permutation at {t}")
        if not t:
            continue
        previous = mapping[t - 1]
        if t % interval:
            if not np.array_equal(row, previous):
                raise ValueError(f"walker mapping changed outside exchange at {t}")
            continue
        parity = ((t // interval) - 1) % 2
        allowed = previous.copy()
        for state in range(parity, k - 1, 2):
            pair = row[state:state + 2]
            if np.array_equal(pair, previous[state:state + 2]):
                continue
            if np.array_equal(pair, previous[state:state + 2][::-1]):
                allowed[state:state + 2] = pair
            else:
                raise ValueError(f"invalid adjacent exchange at {t}")
        if not np.array_equal(row, allowed):
            raise ValueError(f"walker mapping changed outside exchange parity at {t}")


def endpoint_mbar(samples: np.ndarray, centers: np.ndarray) -> float:
    """Only the MBAR point estimate; avoid repeated overlap/error calculations."""
    from pymbar import MBAR

    n, k = samples.shape
    if n < 2 or len(centers) != k or not np.isfinite(samples).all():
        raise ValueError("invalid MBAR samples")
    x = np.concatenate([samples[:, state] for state in range(k)])
    u_kn = 0.5 * (x[None, :] - centers[:, None]) ** 2
    counts = np.full(k, n, dtype=int)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        fit = MBAR(u_kn, counts)
    endpoint = float(fit.f_k[-1] - fit.f_k[0])
    if not np.isfinite(endpoint):
        raise FloatingPointError("nonfinite MBAR endpoint")
    return endpoint


def difference(samples: np.ndarray, centers: np.ndarray) -> float:
    n = len(samples) // 2
    return endpoint_mbar(samples[n:], centers) - endpoint_mbar(samples[:n], centers)


def experiment(cfg: dict, *, regime: str, seed: int, cohort: str,
               block_length: int) -> dict:
    samples, mapping, exchange = simulate_walker_ladder(cfg, regime, seed)
    centers = np.linspace(cfg["center_min"], cfg["center_max"], cfg["state_count"])
    row = {"cohort": cohort, "regime": regime, "seed": seed,
           "mean_block_length": block_length, "status": "failed",
           "exchange": exchange, "bootstrap_attempted": cfg["bootstrap_replicates"],
           "bootstrap_successful": 0,
           "all_walker_rows_are_permutations": True,
           "walker_mapping_sha256": sha256(mapping.tobytes()).hexdigest()}
    try:
        observed = difference(samples, centers)
        row["observed_difference_kT"] = observed
        rng = np.random.default_rng(seed + 10_000_000 + block_length * 100_000)
        boot = []
        for _ in range(cfg["bootstrap_replicates"]):
            index = stationary_bootstrap_indices(len(samples), block_length, rng)
            try:
                boot.append(difference(samples[index], centers))
            except (ValueError, FloatingPointError, RuntimeError):
                pass
        row["bootstrap_successful"] = len(boot)
        if len(boot) < cfg["minimum_successful_bootstraps"]:
            row["failure"] = "too_few_successful_bootstrap_fits"
            return row
        variance = float(np.var(boot, ddof=1))
        if not np.isfinite(variance) or variance <= 0:
            row["failure"] = "nonpositive_or_nonfinite_joint_variance"
            return row
        row.update({"status": "complete", "joint_variance_kT2": variance,
                    "bootstrap_mean_difference_kT": float(np.mean(boot)),
                    "nominal95_zero_covered": bool(abs(observed) <= 1.96 * sqrt(variance))
                    if cfg["regimes"][regime]["linear_shift"] == 0 else None})
    except (ValueError, FloatingPointError, RuntimeError) as exc:
        row["failure"] = f"{type(exc).__name__}: {exc}"
    return row


def summarize(records: list[dict], cfg: dict, regime: str,
              cohort: str, block_length: int) -> dict:
    subset = [r for r in records if r["regime"] == regime
              and r["mean_block_length"] == block_length]
    complete = [r for r in subset if r["status"] == "complete"]
    out = {"regime": regime, "cohort": cohort, "mean_block_length": block_length,
           "attempted": len(subset), "complete": len(complete),
           "failed_seeds": [r["seed"] for r in subset if r["status"] != "complete"]}
    if len(complete) < 2:
        return out
    d = np.asarray([r["observed_difference_kT"] for r in complete])
    empirical = float(np.var(d, ddof=1))
    estimated = float(np.mean([r["joint_variance_kT2"] for r in complete]))
    out.update({"empirical_mean_difference_kT": float(np.mean(d)),
                "empirical_difference_variance_kT2": empirical,
                "mean_estimated_joint_variance_kT2": estimated,
                "estimated_to_empirical_variance_ratio": estimated / empirical})
    if cfg["regimes"][regime]["linear_shift"] == 0:
        covered = sum(r["nominal95_zero_covered"] for r in complete)
        out["nominal95_zero_coverage_count"] = covered
        rules = cfg["diagnostic_acceptance"]
        out["diagnostic_pass"] = bool(
            cohort == "heldout" and block_length == cfg["primary_mean_block_length"]
            and len(complete) >= rules["minimum_complete_heldout_seeds"]
            and covered >= rules["minimum_nominal95_difference_coverage_count"]
            and rules["mean_variance_to_empirical_variance_lower"] <=
                out["estimated_to_empirical_variance_ratio"] <=
                rules["mean_variance_to_empirical_variance_upper"])
    else:
        out["diagnostic_pass"] = None
        out["note"] = "drift violates stationary bootstrap assumptions"
    return out


def run(config_path: Path, cohort: str) -> dict:
    cfg, digest = load_config(config_path)
    if cohort not in ("development", "heldout"):
        raise ValueError("invalid cohort")
    lengths = [cfg["primary_mean_block_length"]]
    if cohort == "development":
        lengths += cfg["development_sensitivity_mean_block_lengths"]
    records = [experiment(cfg, regime=regime, seed=seed, cohort=cohort,
                          block_length=length)
               for regime in cfg["regimes"]
               for seed in cfg[f"{cohort}_seeds"]
               for length in lengths]
    return {"analysis_id": cfg["analysis_id"], "cohort": cohort,
            "config_sha256": digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "limitations": [
                "Coordinate-independent swaps preserve a known harmonic marginal but are not Metropolis HREX.",
                "Stationary blocks preserve contiguous walker lineage internally, not across block joins.",
                "No physical protein, experimental effect, or production uncertainty is qualified."],
            "experiments": records,
            "summaries": [summarize(records, cfg, regime, cohort, length)
                          for regime in cfg["regimes"] for length in lengths]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cohort", choices=("development", "heldout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite stress report")
    report = run(args.config, args.cohort)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_WALKER_STRESS_RECORDED {args.output}")


if __name__ == "__main__":
    main()
