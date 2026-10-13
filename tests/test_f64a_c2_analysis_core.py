"""Contract checks for the CPU-only C2 analysis primitives."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis.f64a_c2_analysis_core import (
    StateReducedPotentials,
    noise_corrected_square,
    noise_correction_bounds,
    split_retained_grid,
    validate_reduced_potential_ladder,
)


def test_grid_keeps_optional_boundary_out_of_disjoint_blocks() -> None:
    with_boundary = split_retained_grid(
        [0, 1, 2, 3, 4], duration_ps=4, stride_ps=1, tolerance_ps=1e-9,
    )
    assert with_boundary.boundary_index == 0
    assert with_boundary.early_indices == (1, 2)
    assert with_boundary.late_indices == (3, 4)

    without_boundary = split_retained_grid(
        [1, 2, 3, 4], duration_ps=4, stride_ps=1, tolerance_ps=1e-9,
    )
    assert without_boundary.boundary_index is None
    assert without_boundary.early_indices == (0, 1)
    assert without_boundary.late_indices == (2, 3)


@pytest.mark.parametrize("times", [
    [0, 0, 1, 2, 3, 4],  # duplicate branch-boundary record
    [0, 1, 3, 4],        # missing sample
    [0, 1, 2, 3, 3],     # duplicate retained sample
    [0, 1, 2, 3, 5],     # shifted endpoint
    [0, 1, 2, np.nan, 4],
])
def test_grid_rejects_broken_cadence(times: list[float]) -> None:
    with pytest.raises(ValueError):
        split_retained_grid(
            times, duration_ps=4, stride_ps=1, tolerance_ps=1e-9,
        )


def test_grid_requires_even_registered_sample_count() -> None:
    with pytest.raises(ValueError, match="even integer"):
        split_retained_grid(
            [1, 2, 3], duration_ps=3, stride_ps=1, tolerance_ps=1e-9,
        )


def test_complete_reduced_potential_ladder_and_fault_rejection() -> None:
    def sampled_state() -> StateReducedPotentials:
        return StateReducedPotentials(
            times_ps=[0, 1, 2, 3, 4],
            lambda_values=[0.0, 0.5, 1.0],
            rows=[[0.0, 1.0, 2.0] for _ in range(5)],
        )

    states = {state: sampled_state() for state in range(3)}
    kwargs = dict(expected_lambdas=[0.0, 0.5, 1.0], duration_ps=4,
                  stride_ps=1, tolerance_ps=1e-9, lambda_tolerance=1e-9)
    blocks = validate_reduced_potential_ladder(states, **kwargs)
    assert set(blocks) == {0, 1, 2}
    assert all(block.early_indices == (1, 2) for block in blocks.values())

    with pytest.raises(ValueError, match="sampled state"):
        validate_reduced_potential_ladder({0: states[0], 1: states[1]}, **kwargs)
    bad_labels = dict(states)
    bad_labels[1] = StateReducedPotentials(
        times_ps=[0, 1, 2, 3, 4], lambda_values=[0.0, 0.6, 1.0],
        rows=states[1].rows,
    )
    with pytest.raises(ValueError, match="lambda labels"):
        validate_reduced_potential_ladder(bad_labels, **kwargs)
    bad_energy = dict(states)
    bad_energy[2] = StateReducedPotentials(
        times_ps=[0, 1, 2, 3, 4], lambda_values=[0.0, 0.5, 1.0],
        rows=[[0.0, np.nan, 2.0], *states[2].rows[1:]],
    )
    with pytest.raises(ValueError, match="nonfinite energies"):
        validate_reduced_potential_ladder(bad_energy, **kwargs)


def test_ladder_rejects_mismatched_boundary_shape() -> None:
    common = StateReducedPotentials(
        times_ps=[0, 1, 2, 3, 4], lambda_values=[0, 1],
        rows=[[0.0, 1.0] for _ in range(5)],
    )
    no_boundary = StateReducedPotentials(
        times_ps=[1, 2, 3, 4], lambda_values=[0, 1],
        rows=[[0.0, 1.0] for _ in range(4)],
    )
    with pytest.raises(ValueError, match="boundary"):
        validate_reduced_potential_ladder(
            {0: common, 1: no_boundary}, expected_lambdas=[0, 1],
            duration_ps=4, stride_ps=1, tolerance_ps=1e-9,
            lambda_tolerance=0,
        )


def test_covariance_bounds_and_point_consistency() -> None:
    # With SEs 2 and 3, all admissible difference variances lie in [1, 25].
    bounds = noise_correction_bounds(4, early_se=2, late_se=3)
    assert bounds.variance_lower == 1
    assert bounds.variance_upper == 25
    assert bounds.adjusted_square_lower == -9
    assert bounds.adjusted_square_upper == 15
    assert noise_corrected_square(
        4, early_se=2, late_se=3, difference_variance=13, tolerance=0,
    ) == 3
    with pytest.raises(ValueError, match="violates"):
        noise_corrected_square(
            4, early_se=2, late_se=3, difference_variance=26, tolerance=0,
        )
    with pytest.raises(ValueError, match="overflows"):
        noise_correction_bounds(1e308, early_se=1, late_se=1)


def test_stationary_noise_correction_retains_negative_values() -> None:
    rng = np.random.default_rng(20261003)
    early = rng.normal(0, 1, 100_000)
    late = rng.normal(0, 2, 100_000)
    movement = late - early
    corrected = movement**2 - 5  # independent errors: Var(late - early) = 1 + 4
    assert abs(float(corrected.mean())) < 0.08
    assert int((corrected < 0).sum()) > 0
    # Individual negative corrections are scientifically meaningful and
    # must not be clipped to zero.
    assert noise_corrected_square(
        1, early_se=1, late_se=2, difference_variance=5, tolerance=0,
    ) == -4
