"""BCa interval preserves pair rows and rejects insufficient inputs."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis.f64a_c2_paired_interval_bca import (
    DEFAULT_CONFIG, load_config, paired_bca_interval,
)


def test_bca_frozen_base_and_finite_interval() -> None:
    _, base, digest = load_config(DEFAULT_CONFIG)
    assert len(digest) == 64
    assert base["bootstrap_replicates"] == 799
    rng = np.random.default_rng(81)
    b = rng.normal(0, 1.0, 33)
    h = rng.normal(0, 0.75, 33)
    lower, upper = paired_bca_interval(
        b, h, replicates=799, coverage=0.95, rng=rng)
    assert np.isfinite(lower) and np.isfinite(upper) and lower < upper


def test_bca_requires_complete_matched_rows() -> None:
    with pytest.raises(ValueError, match="too few matched pairs"):
        paired_bca_interval(np.ones(4), np.ones(4),
                            replicates=399, coverage=0.95,
                            rng=np.random.default_rng(1))
