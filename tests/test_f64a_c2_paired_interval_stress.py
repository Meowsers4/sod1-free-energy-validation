"""Focused tests for paired outcomes and missing-attempt bookkeeping."""

from __future__ import annotations

import numpy as np

from src.analysis.f64a_c2_paired_interval_stress import (
    DEFAULT_CONFIG, draw_attempts, folded_normal_mean, load_config,
    paired_intervals,
)


def test_folded_normal_known_center() -> None:
    assert abs(folded_normal_mean(0, 1) - np.sqrt(2 / np.pi)) < 1e-12


def test_pairing_and_denominators_are_preserved() -> None:
    cfg, _ = load_config(DEFAULT_CONFIG)
    rng = np.random.default_rng(18)
    attempts = draw_attempts(cfg, 33, 0.6, "complete", rng)
    assert np.allclose(attempts["late_baseline"] - attempts["early_baseline"],
                       attempts["signed_baseline"])
    assert np.allclose(attempts["late_hrex"] - attempts["early_hrex"],
                       attempts["signed_hrex"])
    attempts["observed_baseline"][0] = False
    attempts["observed_hrex"][1] = False
    row = paired_intervals(attempts, cfg, rng)
    assert row["attempted_pairs"] == 33
    assert row["complete_pairs"] == 31
    assert row["missing_baseline"] == 1
    assert row["missing_hrex"] == 1
    assert row["status"] == "complete"


def test_too_few_complete_pairs_stays_unavailable() -> None:
    cfg, _ = load_config(DEFAULT_CONFIG)
    rng = np.random.default_rng(19)
    attempts = draw_attempts(cfg, 10, -0.6, "complete", rng)
    attempts["observed_hrex"][4:] = False
    row = paired_intervals(attempts, cfg, rng)
    assert row["status"] == "unavailable"
    assert row["attempted_pairs"] == 10
    assert row["complete_pairs"] == 4
