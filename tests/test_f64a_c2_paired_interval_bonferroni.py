"""The marginal-normal bound is finite and preserves matched-pair counts."""

import numpy as np
import pytest

from src.analysis.f64a_c2_paired_interval_bonferroni import (
    DEFAULT_CONFIG, load_config, paired_bonferroni_interval,
)


def test_frozen_spec_and_bound() -> None:
    cfg, base, digest = load_config(DEFAULT_CONFIG)
    assert len(digest) == 64 and cfg["normal_model_only"]
    assert base["within_pair_correlations"] == [0.6, -0.6]
    rng = np.random.default_rng(5)
    b = rng.normal(size=33)
    h = .6 * b + rng.normal(size=33)
    lower, upper = paired_bonferroni_interval(b, h, coverage=.95)
    point = np.std(h, ddof=1) - np.std(b, ddof=1)
    assert lower < point < upper


def test_rejects_incomplete_or_nonfinite_pairs() -> None:
    with pytest.raises(ValueError, match="too few complete"):
        paired_bonferroni_interval(np.ones(4), np.ones(4), coverage=.95)
    h = np.arange(10, dtype=float)
    h[0] = np.nan
    with pytest.raises(ValueError, match="nonfinite"):
        paired_bonferroni_interval(np.arange(10), h, coverage=.95)
