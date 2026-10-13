"""Known-answer two-coordinate calibration for work package B."""

from __future__ import annotations

import argparse
import contextlib
import importlib.metadata
import io
import json
import math
import os
import platform
import tempfile
from pathlib import Path

import numpy as np
import yaml
from scipy.special import logsumexp

from src.analysis.f64a_late_window_audit import ROOT, sha256

DEFAULT_CONFIG = ROOT / "docs/known_answer_model_v2.yaml"


def load_spec(path: Path = DEFAULT_CONFIG) -> dict:
    """Validate every scientific and execution choice; supply no silent defaults."""
    spec = yaml.safe_load(path.read_text())
    lambdas = spec["lambda_vector"]
    domain = spec["domain"]
    sampling = spec["sampling"]
    reference = spec["reference"]
    evaluation = spec["evaluation"]
    analysis = spec["analysis"]
    potential_keys = {
        "x_force_constant",
        "x_lambda_shift",
        "x_y_coupling",
        "base_y_tilt",
        "lambda_y_tilt",
        "lambda_offset",
    }
    if (
        set(spec["potential"]) != potential_keys
        or len(lambdas) < 3
        or lambdas[0] != 0
        or lambdas[-1] != 1
        or any(not math.isfinite(value) for value in lambdas)
        or any(b <= a for a, b in zip(lambdas, lambdas[1:]))
        or set(domain) != {"x", "y"}
        or any(
            len(bounds) != 2
            or not all(math.isfinite(value) for value in bounds)
            or bounds[0] >= bounds[1]
            for bounds in domain.values()
        )
        or set(spec["regimes"]) != {"easy", "metastable"}
        or any(
            set(regime) != {"barrier_height", "barrier_relief"}
            or regime["barrier_height"] <= 0
            or not 0 <= regime["barrier_relief"] < 1
            for regime in spec["regimes"].values()
        )
        or reference["gauss_legendre_orders"]
        != sorted(set(reference["gauss_legendre_orders"]))
        or any(order < 16 for order in reference["gauss_legendre_orders"])
        or any(
            reference[key] <= 0
            for key in (
                "relative_free_energy_tolerance_kT",
                "independent_absolute_tolerance",
                "independent_relative_tolerance",
                "independent_agreement_tolerance_kT",
            )
        )
        or sampling["methods"]
        != ["independent_windows", "neighbor_replica_exchange"]
        or type(sampling["potential_evaluation_budget"]) is not int
        or sampling["potential_evaluation_budget"] <= len(lambdas)
        or type(sampling["snapshot_stride_sweeps"]) is not int
        or sampling["snapshot_stride_sweeps"] <= 0
        or not 0 < sampling["burn_fraction"] < 1
        or type(sampling["exchange_interval_sweeps"]) is not int
        or sampling["exchange_interval_sweeps"] <= 0
        or sampling["proposal_sigma_x"] <= 0
        or sampling["proposal_sigma_y"] <= 0
        or not sampling["development_seeds"]
        or not sampling["heldout_seeds"]
        or set(sampling["development_seeds"]) & set(sampling["heldout_seeds"])
        or len(set(sampling["development_seeds"] + sampling["heldout_seeds"]))
        != len(sampling["development_seeds"] + sampling["heldout_seeds"])
        or analysis
        != {
            "fixed_burn_only": True,
            "correlation_treatment": "max_statistical_inefficiency_of_y_and_sampled_state_energy",
            "fit_each_block_independently": True,
        }
        or evaluation["nominal_interval_z"] <= 0
        or evaluation["error_tolerance_kT"] <= 0
        or evaluation["reassuring_net_hysteresis_max_kT"] <= 0
        or not 0 < evaluation["reassuring_min_overlap_min"] < 1
        or evaluation["reassuring_interval_halfwidth_max_kT"] <= 0
        or type(evaluation["minimum_samples_per_state"]) is not int
        or evaluation["minimum_samples_per_state"] <= 0
        or spec["figures"]["dpi"] <= 0
    ):
        raise ValueError("invalid known-answer model specification")
    return spec


def reduced_potential(
    x: np.ndarray | float,
    y: np.ndarray | float,
    lam: np.ndarray | float,
    potential: dict,
    regime: dict,
) -> np.ndarray:
    """Evaluate the dimensionless two-coordinate potential u_lambda(x,y)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    lam = np.asarray(lam, dtype=float)
    center = (
        potential["x_lambda_shift"] * (2 * lam - 1)
        + potential["x_y_coupling"] * y
    )
    barrier = regime["barrier_height"] * (
        1 - regime["barrier_relief"] * 4 * lam * (1 - lam)
    )
    return (
        0.5 * potential["x_force_constant"] * (x - center) ** 2
        + barrier * (y**2 - 1) ** 2
        + (
            potential["base_y_tilt"]
            + potential["lambda_y_tilt"] * (lam - 0.5)
        )
        * y
        + potential["lambda_offset"] * lam
    )


def gauss_legendre_free_energies(spec: dict, order: int, regime: dict) -> list[float]:
    """Compute all lambda free energies by tensor Gauss-Legendre quadrature."""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    (x0, x1), (y0, y1) = spec["domain"]["x"], spec["domain"]["y"]
    x = x0 + (nodes + 1) * (x1 - x0) / 2
    y = y0 + (nodes + 1) * (y1 - y0) / 2
    log_weights = (
        np.log(weights[:, None])
        + np.log(weights[None, :])
        + math.log((x1 - x0) * (y1 - y0) / 4)
    )
    values = []
    for lam in spec["lambda_vector"]:
        u = reduced_potential(
            x[:, None], y[None, :], lam, spec["potential"], regime
        )
        values.append(float(-logsumexp(-u + log_weights)))
    return values


def build_reference(config: Path = DEFAULT_CONFIG) -> Path:
    """Refine primary quadrature until the frozen tolerance is satisfied."""
    spec = load_spec(config)
    output = ROOT / spec["output_dir"] / "reference.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    records = {}
    for label, regime in spec["regimes"].items():
        history = []
        previous = None
        converged = None
        for order in spec["reference"]["gauss_legendre_orders"]:
            absolute = gauss_legendre_free_energies(spec, order, regime)
            relative = [value - absolute[0] for value in absolute]
            difference = (
                None
                if previous is None
                else float(np.max(np.abs(np.asarray(relative) - previous)))
            )
            history.append(
                {
                    "order": order,
                    "absolute_free_energies_kT": absolute,
                    "relative_free_energies_kT": relative,
                    "max_change_from_previous_kT": difference,
                }
            )
            if (
                difference is not None
                and difference
                <= spec["reference"]["relative_free_energy_tolerance_kT"]
            ):
                converged = history[-1]
                break
            previous = np.asarray(relative)
        if converged is None:
            raise ValueError(f"quadrature did not converge for {label}")
        records[label] = {
            "refinement": history,
            "selected_order": converged["order"],
            "absolute_free_energies_kT": converged["absolute_free_energies_kT"],
            "relative_free_energies_kT": converged["relative_free_energies_kT"],
            "endpoint_delta_f_kT": converged["relative_free_energies_kT"][-1],
            "refinement_error_bound_kT": converged["max_change_from_previous_kT"],
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "analysis_id": spec["analysis_id"],
        "implementation": "tensor Gauss-Legendre quadrature",
        "config_sha256": sha256(config),
        "config": spec,
        "regimes": records,
    }
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    os.link(temporary, output)
    temporary.unlink()
    print(f"Wrote {output}")
    return output


def _initial_state(spec: dict, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    lambdas = np.asarray(spec["lambda_vector"])
    sampling = spec["sampling"]
    y = sampling["initial_y"] + rng.normal(
        0, sampling["initial_sigma_y"], len(lambdas)
    )
    center = (
        spec["potential"]["x_lambda_shift"] * (2 * lambdas - 1)
        + spec["potential"]["x_y_coupling"] * y
    )
    x = center + rng.normal(0, sampling["initial_sigma_x"], len(lambdas))
    return x, y


def simulate(
    spec: dict, regime: dict, method: str, seed: int
) -> tuple[list[np.ndarray], list[np.ndarray], dict]:
    """Run one equal-potential-evaluation baseline or exchange experiment."""
    rng = np.random.default_rng(seed)
    lambdas = np.asarray(spec["lambda_vector"])
    sampling = spec["sampling"]
    budget = sampling["potential_evaluation_budget"]
    x, y = _initial_state(spec, rng)
    current = reduced_potential(x, y, lambdas, spec["potential"], regime)
    evaluations = len(lambdas)
    sweeps = 0
    local_attempts = local_accepts = 0
    exchange_attempts = exchange_accepts = 0
    parity = 0
    walkers = np.arange(len(lambdas))
    walker_positions = [np.arange(len(lambdas)).tolist()]
    snapshots_x, snapshots_y, snapshot_sweeps = [], [], []
    while evaluations + len(lambdas) <= budget:
        proposal_x = x + rng.normal(0, sampling["proposal_sigma_x"], len(lambdas))
        proposal_y = y + rng.normal(0, sampling["proposal_sigma_y"], len(lambdas))
        proposed = reduced_potential(
            proposal_x, proposal_y, lambdas, spec["potential"], regime
        )
        accept = np.log(rng.random(len(lambdas))) < -(proposed - current)
        x[accept], y[accept], current[accept] = (
            proposal_x[accept],
            proposal_y[accept],
            proposed[accept],
        )
        evaluations += len(lambdas)
        local_attempts += len(lambdas)
        local_accepts += int(accept.sum())
        sweeps += 1
        if (
            method == "neighbor_replica_exchange"
            and sweeps % sampling["exchange_interval_sweeps"] == 0
        ):
            pairs = list(zip(range(parity, len(lambdas) - 1, 2), range(parity + 1, len(lambdas), 2)))
            needed = 2 * len(pairs)
            if evaluations + needed <= budget:
                for lower, upper in pairs:
                    cross_lower = float(
                        reduced_potential(
                            x[upper], y[upper], lambdas[lower], spec["potential"], regime
                        )
                    )
                    cross_upper = float(
                        reduced_potential(
                            x[lower], y[lower], lambdas[upper], spec["potential"], regime
                        )
                    )
                    log_acceptance = -(
                        cross_lower + cross_upper - current[lower] - current[upper]
                    )
                    exchange_attempts += 1
                    if math.log(rng.random()) < log_acceptance:
                        x[lower], x[upper] = x[upper], x[lower]
                        y[lower], y[upper] = y[upper], y[lower]
                        walkers[lower], walkers[upper] = walkers[upper], walkers[lower]
                        current[lower], current[upper] = cross_lower, cross_upper
                        exchange_accepts += 1
                evaluations += needed
                parity = 1 - parity
                positions = np.empty(len(lambdas), dtype=int)
                positions[walkers] = np.arange(len(lambdas))
                walker_positions.append(positions.tolist())
        if sweeps % sampling["snapshot_stride_sweeps"] == 0:
            snapshots_x.append(x.copy())
            snapshots_y.append(y.copy())
            snapshot_sweeps.append(sweeps)
    burn_sweep = math.ceil(sampling["burn_fraction"] * sweeps)
    retained = [i for i, sweep in enumerate(snapshot_sweeps) if sweep >= burn_sweep]
    if not retained:
        raise ValueError("sampling produced no retained snapshots")
    xs = np.asarray(snapshots_x)[retained]
    ys = np.asarray(snapshots_y)[retained]
    per_state_x = [xs[:, state].copy() for state in range(len(lambdas))]
    per_state_y = [ys[:, state].copy() for state in range(len(lambdas))]
    transitions = [
        int(np.count_nonzero(np.diff(np.signbit(values)))) for values in per_state_y
    ]
    summary = {
        "potential_evaluations": evaluations,
        "unused_evaluation_budget": budget - evaluations,
        "sweeps": sweeps,
        "burn_sweep": burn_sweep,
        "samples_per_state": len(retained),
        "local_attempts": local_attempts,
        "local_acceptance": local_accepts / local_attempts,
        "exchange_attempts": exchange_attempts,
        "exchange_acceptance": exchange_accepts / exchange_attempts
        if exchange_attempts
        else None,
        "y_sign_transitions_by_state": transitions,
        "walkers_visiting_both_endpoints": sum(
            1
            for walker in range(len(lambdas))
            if {0, len(lambdas) - 1}.issubset(
                {positions[walker] for positions in walker_positions}
            )
        ),
    }
    return per_state_x, per_state_y, summary


def _mbar_inputs(
    xs: list[np.ndarray], ys: list[np.ndarray], spec: dict, regime: dict
) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    lambdas = np.asarray(spec["lambda_vector"])
    counts = np.asarray([len(values) for values in xs], dtype=int)
    all_x = np.concatenate(xs)
    all_y = np.concatenate(ys)
    u_kn = np.vstack(
        [
            reduced_potential(all_x, all_y, lam, spec["potential"], regime)
            for lam in lambdas
        ]
    )
    per_window = []
    start = 0
    for count in counts:
        per_window.append(u_kn[:, start : start + count])
        start += count
    return u_kn, counts, per_window


def decorrelate_samples(
    xs: list[np.ndarray], ys: list[np.ndarray], spec: dict, regime: dict
) -> tuple[list[np.ndarray], list[np.ndarray], list[dict]]:
    """Thin each state using the larger g from y and sampled-state energy."""
    from pymbar import timeseries

    selected_x, selected_y, diagnostics = [], [], []
    for state, (x, y, lam) in enumerate(zip(xs, ys, spec["lambda_vector"])):
        sampled_u = reduced_potential(x, y, lam, spec["potential"], regime)
        g_y = float(timeseries.statistical_inefficiency(y))
        g_u = float(timeseries.statistical_inefficiency(sampled_u))
        g = max(g_y, g_u)
        indices = np.asarray(timeseries.subsample_correlated_data(y, g=g), dtype=int)
        if not len(indices):
            raise ValueError("correlation treatment selected no samples")
        selected_x.append(x[indices])
        selected_y.append(y[indices])
        diagnostics.append(
            {
                "state": state,
                "n_raw_after_fixed_burn": len(x),
                "g_y": g_y,
                "g_sampled_state_energy": g_u,
                "g_used": g,
                "n_selected": len(indices),
                "first_selected_index": int(indices[0]),
                "last_selected_index": int(indices[-1]),
            }
        )
    return selected_x, selected_y, diagnostics


def solve_samples(
    xs: list[np.ndarray], ys: list[np.ndarray], spec: dict, regime: dict
) -> dict:
    """Compute MBAR estimate, uncertainty, overlap and local discrepancies."""
    from pymbar import MBAR

    xs, ys, selection = decorrelate_samples(xs, ys, spec, regime)
    u_kn, counts, per_window = _mbar_inputs(xs, ys, spec, regime)
    chatter = io.StringIO()
    with contextlib.redirect_stdout(chatter), contextlib.redirect_stderr(chatter):
        mbar = MBAR(u_kn, counts)
        free = mbar.compute_free_energy_differences()
        overlap = np.asarray(mbar.compute_overlap()["matrix"], dtype=float)
    estimate = float(free["Delta_f"][0, -1])
    error = float(free["dDelta_f"][0, -1])
    discrepancies = []
    for state in range(len(counts) - 1):
        lower = per_window[state]
        upper = per_window[state + 1]
        d_forward = lower[state + 1] - lower[state]
        d_reverse = upper[state + 1] - upper[state]
        forward = float(-logsumexp(-d_forward) + math.log(len(d_forward)))
        reverse = float(logsumexp(d_reverse) - math.log(len(d_reverse)))
        discrepancies.append(forward - reverse)
    if not all(math.isfinite(value) for value in [estimate, error, *discrepancies]):
        raise FloatingPointError("nonfinite estimator result")
    return {
        "estimate_delta_f_kT": estimate,
        "conditional_mbar_error_kT": error,
        "net_hysteresis_kT": abs(sum(discrepancies)),
        "sum_absolute_hysteresis_kT": sum(abs(value) for value in discrepancies),
        "max_absolute_hysteresis_kT": max(abs(value) for value in discrepancies),
        "min_adjacent_overlap": min(
            float(overlap[state, state + 1]) for state in range(len(counts) - 1)
        ),
        "signed_local_discrepancies_kT": discrepancies,
        "selection_diagnostics": selection,
        "minimum_selected_samples": int(counts.min()),
        "median_selected_samples": float(np.median(counts)),
        "solver_notes": [
            line.strip()
            for line in chatter.getvalue().splitlines()
            if line.strip() and not set(line.strip()) <= {"*"}
        ],
    }


def analyze_experiment(
    spec: dict,
    regime_label: str,
    method: str,
    seed: int,
    cohort: str,
    truth: float,
) -> dict:
    """Run and analyze one experiment, including a disjoint half comparison."""
    regime = spec["regimes"][regime_label]
    xs, ys, simulation = simulate(spec, regime, method, seed)
    full = solve_samples(xs, ys, spec, regime)
    split = len(xs[0]) // 2
    early = solve_samples([values[:split] for values in xs], [values[:split] for values in ys], spec, regime)
    late = solve_samples([values[split:] for values in xs], [values[split:] for values in ys], spec, regime)
    minimum = spec["evaluation"]["minimum_samples_per_state"]
    selected_minimum = min(
        full["minimum_selected_samples"],
        early["minimum_selected_samples"],
        late["minimum_selected_samples"],
    )
    if selected_minimum < minimum:
        return {
            "status": "insufficient_decorrelated_samples",
            "failure_reason": (
                f"minimum selected count {selected_minimum} is below frozen minimum {minimum}"
            ),
            "cohort": cohort,
            "regime": regime_label,
            "method": method,
            "seed": seed,
            "truth_delta_f_kT": truth,
            "minimum_selected_samples": {
                "full": full["minimum_selected_samples"],
                "early": early["minimum_selected_samples"],
                "late": late["minimum_selected_samples"],
            },
            "simulation": simulation,
        }
    error = full["estimate_delta_f_kT"] - truth
    z = spec["evaluation"]["nominal_interval_z"]
    halfwidth = z * full["conditional_mbar_error_kT"]
    tolerance = spec["evaluation"]["error_tolerance_kT"]
    rules = {
        "net_hysteresis": full["net_hysteresis_kT"]
        <= spec["evaluation"]["reassuring_net_hysteresis_max_kT"],
        "minimum_overlap": full["min_adjacent_overlap"]
        >= spec["evaluation"]["reassuring_min_overlap_min"],
        "conditional_interval_width": halfwidth
        <= spec["evaluation"]["reassuring_interval_halfwidth_max_kT"],
    }
    return {
        "status": "complete",
        "cohort": cohort,
        "regime": regime_label,
        "method": method,
        "seed": seed,
        "truth_delta_f_kT": truth,
        "signed_error_kT": error,
        "absolute_error_kT": abs(error),
        "nominal_interval_halfwidth_kT": halfwidth,
        "nominal_interval_covers_truth": abs(error) <= halfwidth,
        "within_declared_error_tolerance": abs(error) <= tolerance,
        "reassuring_rules": rules,
        "false_reassurance": {
            name: passed and abs(error) > tolerance for name, passed in rules.items()
        }
        | {"all_three": all(rules.values()) and abs(error) > tolerance},
        "early_estimate_delta_f_kT": early["estimate_delta_f_kT"],
        "late_estimate_delta_f_kT": late["estimate_delta_f_kT"],
        "signed_late_minus_early_kT": late["estimate_delta_f_kT"]
        - early["estimate_delta_f_kT"],
        "absolute_late_minus_early_kT": abs(
            late["estimate_delta_f_kT"] - early["estimate_delta_f_kT"]
        ),
        "simulation": simulation,
        "diagnostics": full,
    }


def summarize_evaluation(records: list[dict], spec: dict) -> list[dict]:
    """Summarize held-out experiments by regime and method without pooling regimes."""
    summaries = []
    for regime in spec["regimes"]:
        for method in spec["sampling"]["methods"]:
            all_rows = [
                row
                for row in records
                if row["cohort"] == "heldout"
                and row["regime"] == regime
                and row["method"] == method
            ]
            rows = [row for row in all_rows if row["status"] == "complete"]
            if not rows:
                summaries.append(
                    {
                        "regime": regime,
                        "method": method,
                        "n_experiments": len(all_rows),
                        "n_complete": 0,
                        "n_insufficient_decorrelated_samples": len(all_rows),
                        "complete_case_metrics": None,
                        "potential_evaluation_budget": spec["sampling"]["potential_evaluation_budget"],
                    }
                )
                continue
            errors = np.asarray([row["signed_error_kT"] for row in rows])
            summaries.append(
                {
                    "regime": regime,
                    "method": method,
                    "n_experiments": len(all_rows),
                    "n_complete": len(rows),
                    "n_insufficient_decorrelated_samples": len(all_rows) - len(rows),
                    "bias_kT": float(errors.mean()),
                    "rmse_kT": float(np.sqrt(np.mean(errors**2))),
                    "median_absolute_error_kT": float(np.median(abs(errors))),
                    "nominal_interval_coverage": float(
                        np.mean([row["nominal_interval_covers_truth"] for row in rows])
                    ),
                    "within_tolerance_fraction": float(
                        np.mean([row["within_declared_error_tolerance"] for row in rows])
                    ),
                    "mean_conditional_mbar_error_kT": float(
                        np.mean(
                            [
                                row["diagnostics"]["conditional_mbar_error_kT"]
                                for row in rows
                            ]
                        )
                    ),
                    "median_absolute_late_minus_early_kT": float(
                        np.median([row["absolute_late_minus_early_kT"] for row in rows])
                    ),
                    "false_reassurance_fraction": {
                        rule: float(np.mean([row["false_reassurance"][rule] for row in rows]))
                        for rule in (
                            "net_hysteresis",
                            "minimum_overlap",
                            "conditional_interval_width",
                            "all_three",
                        )
                    },
                    "mean_local_acceptance": float(
                        np.mean([row["simulation"]["local_acceptance"] for row in rows])
                    ),
                    "mean_exchange_acceptance": float(
                        np.mean(
                            [
                                row["simulation"]["exchange_acceptance"]
                                for row in rows
                                if row["simulation"]["exchange_acceptance"] is not None
                            ]
                        )
                    )
                    if method == "neighbor_replica_exchange"
                    else None,
                    "mean_y_sign_transitions": float(
                        np.mean(
                            [sum(row["simulation"]["y_sign_transitions_by_state"]) for row in rows]
                        )
                    ),
                    "mean_walkers_visiting_both_endpoints": float(
                        np.mean(
                            [row["simulation"]["walkers_visiting_both_endpoints"] for row in rows]
                        )
                    ),
                    "potential_evaluation_budget": spec["sampling"]["potential_evaluation_budget"],
                }
            )
    return summaries


def _plot_results(report: dict, directory: Path, dpi: int) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = []
    reference = report["reference"]["regimes"]
    lambdas = report["config"]["lambda_vector"]
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    for label, record in reference.items():
        ax.plot(lambdas, record["relative_free_energies_kT"], marker="o", label=label)
    ax.set(xlabel="lambda", ylabel="F(lambda) - F(0) (kT)", title="Quadrature reference profiles")
    ax.grid(alpha=0.2)
    ax.legend()
    name = "reference_profiles.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    names.append(name)

    heldout_all = [
        row for row in report["experiments"] if row["cohort"] == "heldout"
    ]
    heldout = [
        row
        for row in heldout_all
        if row["status"] == "complete"
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    colors = {"independent_windows": "#2166ac", "neighbor_replica_exchange": "#b2182b"}
    for ax, regime in zip(axes, report["config"]["regimes"]):
        regime_complete = [row for row in heldout if row["regime"] == regime]
        tolerance = report["config"]["evaluation"]["error_tolerance_kT"]
        error_values = [row["signed_error_kT"] for row in regime_complete]
        lower = min([-tolerance, *error_values])
        upper = max([tolerance, *error_values])
        span = upper - lower or 1.0
        failure_y = lower - 0.10 * span
        for offset, method in enumerate(report["config"]["sampling"]["methods"]):
            all_rows = [
                row
                for row in heldout_all
                if row["regime"] == regime and row["method"] == method
            ]
            complete_positions = [
                index for index, row in enumerate(all_rows) if row["status"] == "complete"
            ]
            rows = [row for row in all_rows if row["status"] == "complete"]
            x = np.asarray(complete_positions) + (offset - 0.5) * 0.15
            ax.scatter(x, [r["signed_error_kT"] for r in rows], s=24,
                       color=colors[method], alpha=0.8, label=method.replace("_", " "))
            failed_positions = [
                index for index, row in enumerate(all_rows) if row["status"] != "complete"
            ]
            if failed_positions:
                ax.scatter(
                    np.asarray(failed_positions) + (offset - 0.5) * 0.15,
                    [failure_y] * len(failed_positions),
                    marker="x",
                    s=34,
                    linewidths=1.2,
                    color=colors[method],
                    label="insufficient decorrelated samples",
                )
        ax.axhspan(-tolerance, tolerance, color="grey", alpha=0.12)
        ax.axhline(0, color="black", linewidth=0.7)
        ax.set_ylim(failure_y - 0.05 * span, upper + 0.05 * span)
        ax.set(title=regime, xlabel="Held-out seed index", ylabel="MBAR error (kT)")
        ax.grid(alpha=0.15)
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8, loc="lower right")
    name = "heldout_errors.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    names.append(name)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    metrics = [
        ("net_hysteresis_kT", "Net hysteresis (kT)"),
        ("min_adjacent_overlap", "Minimum adjacent overlap"),
        ("conditional_mbar_error_kT", "Conditional MBAR error (kT)"),
    ]
    for ax, (metric, label) in zip(axes, metrics):
        for method in report["config"]["sampling"]["methods"]:
            rows = [r for r in heldout if r["method"] == method]
            ax.scatter(
                [r["diagnostics"][metric] for r in rows],
                [r["absolute_error_kT"] for r in rows],
                c=colors[method], alpha=0.65, s=25,
                label=method.replace("_", " "),
            )
        ax.set(xlabel=label, ylabel="Absolute error (kT)")
        ax.grid(alpha=0.15)
    axes[0].legend(fontsize=8)
    name = "diagnostics_vs_error.png"
    fig.savefig(directory / name, dpi=dpi)
    plt.close(fig)
    names.append(name)
    return names


def evaluate(config: Path = DEFAULT_CONFIG) -> Path:
    """Compare equal-cost methods after both reference implementations agree."""
    spec = load_spec(config)
    directory = ROOT / spec["output_dir"]
    output = directory / "calibration.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    primary_path = directory / "reference.json"
    independent_path = directory / "independent_reference.json"
    if not primary_path.is_file() or not independent_path.is_file():
        raise FileNotFoundError("both primary and independent references are required")
    primary = json.loads(primary_path.read_text())
    independent = json.loads(independent_path.read_text())
    config_hash = sha256(config)
    if primary["config_sha256"] != config_hash or independent["config_sha256"] != config_hash:
        raise ValueError("reference/config identity mismatch")
    agreement = {}
    for regime in spec["regimes"]:
        a = primary["regimes"][regime]["relative_free_energies_kT"]
        b = independent["regimes"][regime]["relative_free_energies_kT"]
        maximum = float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        agreement[regime] = maximum
        if maximum > spec["reference"]["independent_agreement_tolerance_kT"]:
            raise ValueError(f"independent reference disagreement for {regime}: {maximum}")
    records = []
    for cohort, seed_key in (
        ("development", "development_seeds"),
        ("heldout", "heldout_seeds"),
    ):
        for regime in spec["regimes"]:
            truth = primary["regimes"][regime]["endpoint_delta_f_kT"]
            for method in spec["sampling"]["methods"]:
                for seed in spec["sampling"][seed_key]:
                    print(f"Running {cohort} {regime} {method} seed {seed}", flush=True)
                    records.append(
                        analyze_experiment(spec, regime, method, seed, cohort, truth)
                    )
    summaries = summarize_evaluation(records, spec)
    dependencies = [config, Path(__file__), primary_path, independent_path]
    identities = {str(path.resolve()): sha256(path) for path in dependencies}
    runtime = {
        "python": platform.python_version(),
        "packages": {
            package: importlib.metadata.version(package)
            for package in ("numpy", "scipy", "pymbar", "matplotlib", "PyYAML")
        },
    }
    with tempfile.TemporaryDirectory(dir=directory, prefix=".known-answer-") as temp:
        staging = Path(temp)
        partial = {
            "schema_version": 1,
            "analysis_id": spec["analysis_id"],
            "scope": (
                "constructed-model calibration only; no protein mechanism, universal "
                "threshold, or GPU intervention authorization"
            ),
            "config": spec,
            "config_sha256": config_hash,
            "reference": primary,
            "independent_reference_sha256": sha256(independent_path),
            "independent_reference_max_disagreement_kT": agreement,
            "runtime": runtime,
            "dependency_sha256": identities,
            "experiments": records,
            "heldout_summaries": summaries,
            "limitations": [
                "The constructed slow mode was chosen deliberately and is not a protein mechanism.",
                "Held-out seeds test stochastic repetitions within two fixed regimes, not new model families.",
                "Conditional MBAR intervals assume admitted samples adequately represent each state.",
                "Diagnostic thresholds apply only to this frozen model and cost budget.",
                "Exchange success here cannot establish feasibility or benefit in GROMACS/SOD1.",
            ],
        }
        figures = _plot_results(partial, staging, spec["figures"]["dpi"])
        partial["figures"] = figures
        partial["figure_traceability"] = {
            "reference_profiles.png": "reference.regimes[*].relative_free_energies_kT",
            "heldout_errors.png": "experiments[cohort=heldout].signed_error_kT",
            "diagnostics_vs_error.png": "experiments[cohort=heldout].diagnostics and absolute_error_kT",
        }
        (staging / "calibration.json").write_text(
            json.dumps(partial, indent=2, allow_nan=False) + "\n"
        )
        if any(sha256(Path(path)) != digest for path, digest in identities.items()):
            raise ValueError("known-answer input changed during evaluation")
        for name in figures + ["calibration.json"]:
            os.link(staging / name, directory / name)
    print(f"Wrote {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("reference")
    subparsers.add_parser("evaluate")
    args = parser.parse_args()
    if args.command == "reference":
        build_reference(args.config)
    else:
        evaluate(args.config)


if __name__ == "__main__":
    main()
