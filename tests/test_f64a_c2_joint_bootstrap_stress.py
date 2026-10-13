"""Focused checks of the joint time-row resampling contract."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis.f64a_c2_joint_bootstrap_stress import (
    load_config, stationary_bootstrap_indices,
)
from src.analysis.f64a_c2_joint_bootstrap_stress import DEFAULT_CONFIG


def test_frozen_spec_has_disjoint_seeds_and_required_regimes() -> None:
    cfg, digest = load_config(DEFAULT_CONFIG)
    assert len(digest) == 64
    assert set(cfg["development_seeds"]).isdisjoint(cfg["heldout_seeds"])
    assert set(cfg["regimes"]) == {
        "iid", "correlated_synchronized", "long_correlation", "drifting"}


def test_stationary_bootstrap_keeps_contiguous_runs_and_shared_rows() -> None:
    rng = np.random.default_rng(123)
    index = stationary_bootstrap_indices(256, 32, rng)
    assert index.shape == (256,)
    assert np.all((index >= 0) & (index < 256))
    assert np.count_nonzero(index[1:] == (index[:-1] + 1) % 256) > 220
    rows = np.column_stack((np.arange(256), np.arange(256) + 1000))
    resampled = rows[index]
    assert np.all(resampled[:, 1] - resampled[:, 0] == 1000)


def test_invalid_bootstrap_length_fails() -> None:
    with pytest.raises(ValueError, match="invalid bootstrap length"):
        stationary_bootstrap_indices(20, 20, np.random.default_rng(1))
