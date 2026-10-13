"""The normal-model spread candidate preserves complete paired rows."""

import numpy as np
import pytest

from src.analysis.f64a_c2_paired_interval_wishart import (
    DEFAULT_CONFIG, load_config, paired_wishart_interval,
)


def test_frozen_spec_and_paired_spread_interval() -> None:
    cfg, base, digest = load_config(DEFAULT_CONFIG)
    assert len(digest) == 64 and cfg["pivot_draws"] == 1999
    assert base["within_pair_correlations"] == [0.6, -0.6]
    rng = np.random.default_rng(14)
    b = rng.normal(0, 1, 33)
    h = 0.6 * b + 0.6 * rng.normal(size=33)
    one = paired_wishart_interval(b, h, draws=1999, coverage=.95,
                                  rng=np.random.default_rng(19))
    two = paired_wishart_interval(b, h, draws=1999, coverage=.95,
                                  rng=np.random.default_rng(19))
    assert one == two
    assert one[0] < np.std(h, ddof=1) - np.std(b, ddof=1) < one[1]


def test_rejects_missing_or_degenerate_pairs() -> None:
    with pytest.raises(ValueError, match="too few complete"):
        paired_wishart_interval(np.ones(4), np.ones(4), draws=1999,
                                coverage=.95, rng=np.random.default_rng(1))
    with pytest.raises(ValueError, match="degenerate"):
        paired_wishart_interval(np.ones(10), np.arange(10), draws=1999,
                                coverage=.95, rng=np.random.default_rng(1))
