"""Independent distribution check for the C2 constructed stress model."""

from __future__ import annotations

import numpy as np

from src.analysis.f64a_c2_uncertainty_stress import stationary_ladder


def test_stationary_model_has_registered_marginal_and_correlations() -> None:
    centers = np.array([0.0, 1.0, 2.0])
    samples = stationary_ladder(
        centers, samples_per_block=20_000, phi=0.9,
        shared_fraction=0.5, seed=7391,
    )
    centered = samples - centers
    assert abs(float(np.mean(centered[:, 0]))) < 0.08
    assert abs(float(np.var(centered[:, 0])) - 1.0) < 0.08
    assert abs(float(np.corrcoef(centered[:-1, 0], centered[1:, 0])[0, 1])
               - 0.9) < 0.03
    assert abs(float(np.corrcoef(centered[:, 0], centered[:, 1])[0, 1])
               - 0.5) < 0.05
