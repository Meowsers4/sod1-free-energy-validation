"""Pure CPU helpers for the prospective F64A C2 analysis contract.

These functions validate a registered time grid and bound the possible
noise correction for squared early-to-late movement. They do not fit MBAR,
estimate standard errors, read protein outputs, or authorize a simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True)
class RetainedBlocks:
    """Positions of the optional boundary and disjoint retained blocks."""

    boundary_index: int | None
    early_indices: tuple[int, ...]
    late_indices: tuple[int, ...]


@dataclass(frozen=True)
class NoiseCorrectionBounds:
    """Cauchy–Schwarz bounds when cross-block covariance is unknown."""

    variance_lower: float
    variance_upper: float
    adjusted_square_lower: float
    adjusted_square_upper: float


@dataclass(frozen=True)
class StateReducedPotentials:
    """One sampled state's all-state, dimensionless reduced potentials."""

    times_ps: Sequence[float]
    lambda_values: Sequence[float]
    rows: Sequence[Sequence[float]]


def split_retained_grid(
    times_ps: Sequence[float], *, duration_ps: float, stride_ps: float,
    tolerance_ps: float,
) -> RetainedBlocks:
    """Require an exact even retained grid, allowing one excluded t=0 record.

    The caller supplies every scientific and numerical parameter from its
    reviewed contract. Returned indices address the original sequence; the
    boundary, if present, cannot enter either estimation block.
    """
    if (not all(isfinite(x) for x in (duration_ps, stride_ps, tolerance_ps))
            or duration_ps <= 0 or stride_ps <= 0
            or tolerance_ps < 0 or tolerance_ps >= stride_ps / 2):
        raise ValueError("invalid retained-grid parameters")
    count_float = duration_ps / stride_ps
    count = round(count_float)
    if (count < 2 or count % 2 or
            abs(count_float - count) * stride_ps > tolerance_ps):
        raise ValueError("duration must contain an even integer number of samples")

    times = tuple(float(t) for t in times_ps)
    if not times or not all(isfinite(t) for t in times):
        raise ValueError("empty or nonfinite time grid")
    boundary = 0 if abs(times[0]) <= tolerance_ps else None
    if len(times) != count + (boundary is not None):
        raise ValueError("missing, extra or duplicate retained time")
    offset = 1 if boundary is not None else 0
    for sample in range(1, count + 1):
        if abs(times[offset + sample - 1] - sample * stride_ps) > tolerance_ps:
            raise ValueError(f"retained time {sample} does not match registered grid")
    half = count // 2
    return RetainedBlocks(
        boundary_index=boundary,
        early_indices=tuple(range(offset, offset + half)),
        late_indices=tuple(range(offset + half, offset + count)),
    )


def validate_reduced_potential_ladder(
    states: Mapping[int, StateReducedPotentials], *,
    expected_lambdas: Sequence[float], duration_ps: float, stride_ps: float,
    tolerance_ps: float, lambda_tolerance: float,
) -> dict[int, RetainedBlocks]:
    """Check a complete ladder's labels, energy shape and frozen time grid.

    This validates already parsed reduced potentials. It does not establish
    file provenance, convert GROMACS energies or estimate free energies.
    """
    lambdas = tuple(float(value) for value in expected_lambdas)
    n_states = len(lambdas)
    if (n_states < 2 or not all(isfinite(value) for value in lambdas)
            or any(right <= left for left, right in zip(lambdas, lambdas[1:]))
            or not isfinite(lambda_tolerance) or lambda_tolerance < 0):
        raise ValueError("invalid registered lambda ladder")
    if set(states) != set(range(n_states)):
        raise ValueError("missing or unexpected sampled state")

    blocks = {}
    for state in range(n_states):
        data = states[state]
        labels = tuple(float(value) for value in data.lambda_values)
        if (len(labels) != n_states or not all(isfinite(value) for value in labels)
                or any(abs(a - b) > lambda_tolerance
                       for a, b in zip(labels, lambdas))):
            raise ValueError(f"state {state} has wrong energy lambda labels")
        block = split_retained_grid(
            data.times_ps, duration_ps=duration_ps, stride_ps=stride_ps,
            tolerance_ps=tolerance_ps,
        )
        if len(data.rows) != len(data.times_ps):
            raise ValueError(f"state {state} has wrong energy row count")
        for row in data.rows:
            if len(row) != n_states or not all(isfinite(value) for value in row):
                raise ValueError(f"state {state} has incomplete or nonfinite energies")
        blocks[state] = block
    if len({block.boundary_index for block in blocks.values()}) != 1:
        raise ValueError("states disagree about the branch-boundary record")
    return blocks


def noise_correction_bounds(
    movement: float, *, early_se: float, late_se: float,
) -> NoiseCorrectionBounds:
    """Bound ``movement² - Var(late - early)`` without assuming covariance.

    These are covariance sensitivity bounds, not confidence limits. The
    supplied block SEs must be separately validated for the sampling method.
    """
    if (not all(isfinite(x) for x in (movement, early_se, late_se))
            or early_se < 0 or late_se < 0):
        raise ValueError("movement and block errors must be finite; errors nonnegative")
    lower_delta = late_se - early_se
    upper_sum = late_se + early_se
    lower_variance = lower_delta * lower_delta
    upper_variance = upper_sum * upper_sum
    square = movement * movement
    if not all(isfinite(value) for value in
               (lower_variance, upper_variance, square)):
        raise ValueError("movement or error square overflows")
    adjusted_lower = square - upper_variance
    adjusted_upper = square - lower_variance
    if not all(isfinite(value) for value in
               (adjusted_lower, adjusted_upper)):
        raise ValueError("adjusted movement square overflows")
    return NoiseCorrectionBounds(
        variance_lower=lower_variance,
        variance_upper=upper_variance,
        adjusted_square_lower=adjusted_lower,
        adjusted_square_upper=adjusted_upper,
    )


def noise_corrected_square(
    movement: float, *, early_se: float, late_se: float,
    difference_variance: float, tolerance: float,
) -> float:
    """Compute point correction only when joint variance obeys SE bounds.

    This checks arithmetic consistency, not calibration of the joint
    variance estimator. A scientifically reported point value still needs
    the separate CPU qualification in the analysis contract.
    """
    if not isfinite(tolerance) or tolerance < 0:
        raise ValueError("invalid variance tolerance")
    bounds = noise_correction_bounds(
        movement, early_se=early_se, late_se=late_se,
    )
    if (not isfinite(difference_variance)
            or difference_variance < bounds.variance_lower - tolerance
            or difference_variance > bounds.variance_upper + tolerance):
        raise ValueError("joint difference variance violates block-SE bounds")
    return movement ** 2 - difference_variance
