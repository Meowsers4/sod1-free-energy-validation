"""CPU checks of synthetic walker ancestry and the fast MBAR endpoint."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis.f64a_c2_uncertainty_stress import fit_fixed_block
from src.analysis.f64a_c2_walker_stress import (
    DEFAULT_CONFIG, endpoint_mbar, load_config, simulate_walker_ladder,
    validate_walker_history,
)


def test_walker_rows_are_permutations_with_adjacent_changes_only() -> None:
    cfg, _ = load_config(DEFAULT_CONFIG)
    samples, mapping, exchanges = simulate_walker_ladder(
        cfg, "walker_correlated", 6201)
    assert samples.shape == (512, 20)
    assert mapping.shape == samples.shape
    assert exchanges["accepted_swaps"] > 0
    validate_walker_history(mapping, cfg["exchange_interval_records"])
    broken = mapping.copy()
    broken[1, :2] = broken[1, :2][::-1]
    with pytest.raises(ValueError, match="outside exchange"):
        validate_walker_history(broken, cfg["exchange_interval_records"])
    broken = mapping.copy()
    broken[5, [0, 2]] = broken[5, [2, 0]]
    with pytest.raises(ValueError, match="invalid adjacent exchange|outside exchange parity"):
        validate_walker_history(broken, cfg["exchange_interval_records"])


def test_fast_endpoint_agrees_with_full_existing_mbar_fit() -> None:
    cfg, _ = load_config(DEFAULT_CONFIG)
    samples, _, _ = simulate_walker_ladder(cfg, "iid", 6202)
    centers = np.linspace(cfg["center_min"], cfg["center_max"], 20)
    quick = endpoint_mbar(samples[:256], centers)
    full = fit_fixed_block(samples[:256], centers, thin=False, minimum_selected=1)
    assert abs(quick - full["estimate_kT"]) < 1e-9


def test_exchangeable_walker_model_has_known_marginal() -> None:
    cfg, _ = load_config(DEFAULT_CONFIG)
    cfg = dict(cfg, samples_per_block=20_000)
    samples, _, _ = simulate_walker_ladder(cfg, "walker_correlated", 6203)
    centers = np.linspace(cfg["center_min"], cfg["center_max"], 20)
    residual = samples - centers
    assert abs(float(np.mean(residual[:, 0]))) < 0.1
    assert abs(float(np.var(residual[:, 0])) - 1.0) < 0.1
