"""Synthetic/unit tests for the exploratory lambda/comparator analysis."""

import numpy as np
import pytest

from src.analysis import f64a_lambda_comparator as comparator


def _summary(value: float) -> dict:
    return {
        "second_half_minus_first_half_mean_kT": value,
        "linear_slope_kT_per_ns": value / 2,
        "std_kT": 2.0,
    }


def test_neighbor_records_include_explicit_endpoint_slots():
    lambdas = [0.0, 0.5, 1.0]
    blocks = [{"label": "b", "start": 0, "stop": 4}]
    series = []
    for rep in range(2):
        for window in range(3):
            for direction, neighbor in (
                ("previous_minus_sampled_u", window - 1),
                ("next_minus_sampled_u", window + 1),
            ):
                if 0 <= neighbor < 3:
                    series.append(
                        {
                            "block": "b",
                            "replicate": rep,
                            "window": window,
                            "observable": direction,
                            "full_block": _summary(window + rep + 1),
                            "policy_raw_suffixes": [
                                {
                                    "policy": "adaptive",
                                    "raw_suffix": {"n_raw": 3},
                                }
                            ],
                        }
                    )
    records = []
    for rep in range(2):
        records.append(
            {
                "policy": "adaptive",
                "block": "b",
                "replicate": rep,
                "window_diagnostics": [
                    {"window": w, "n_retained": 2, "trim_start_column": 1}
                    for w in range(3)
                ],
                "adjacent_diagnostics": [
                    {
                        "lower_window": w,
                        "upper_window": w + 1,
                        "overlap_lower_to_upper": 0.1 + w,
                        "overlap_upper_to_lower": 0.2 + w,
                    }
                    for w in range(2)
                ],
            }
        )
    actual = comparator.neighbor_records(
        {"series_records": series},
        {"records": records},
        blocks,
        lambdas,
        2,
        "adaptive",
    )
    assert len(actual) == 12
    assert sum(row["available"] for row in actual) == 8
    assert sum(not row["available"] for row in actual) == 4
    previous = next(
        row for row in actual
        if row["replicate"] == 0 and row["window"] == 1
        and row["direction"] == "previous_minus_sampled_u"
    )
    assert previous["directional_overlap"] == pytest.approx(0.2)
    assert previous["signed_half_drift_kT"] == pytest.approx(2.0)
    assert previous["absolute_half_drift_over_std"] == pytest.approx(1.0)


def test_fixed_pair_observables_use_same_states_on_every_path():
    # State offsets make u[2]-u[0] exactly 20 on every sampled path.
    matrices = {
        (sampled, 0): np.vstack(
            [np.arange(8) + 100 * sampled + 10 * state for state in range(3)]
        )
        for sampled in range(3)
    }
    rows = comparator.fixed_pair_records(
        matrices,
        [{"label": "b", "start": 0, "stop": 8}],
        [0.0, 0.5, 1.0],
        [[0, 2]],
        1.0,
        [1],
        [0.5],
    )
    assert len(rows) == 3
    assert {row["full_block"]["mean_kT"] for row in rows} == {20.0}
    assert {row["signed_half_drift_kT"] for row in rows} == {0.0}


def test_neighbor_summary_distinguishes_pooled_and_window_denominators():
    rows = []
    for window, count in enumerate((1, 2, 1)):
        for index in range(count):
            rows.append(
                {
                    "available": True,
                    "window": window,
                    **{metric: float(window + index) for metric in comparator.FULL_METRICS},
                }
            )
    rows.append(
        {
            "available": False,
            "window": 0,
            **{metric: None for metric in comparator.FULL_METRICS},
        }
    )
    summary = comparator.summarize_neighbors(rows, [0.0, 0.5, 1.0])
    assert summary["planned_directional_slots"] == 5
    assert summary["available_neighbor_records"] == 4
    assert summary["explicit_missing_endpoint_slots"] == 1
    metric = summary["metric_summaries"]["absolute_half_drift_kT"]
    assert metric["pooled_record_n"] == 4
    assert metric["window_count"] == 3
    assert metric["pooled_record_median"] == pytest.approx(1.5)


def test_duplicate_source_record_is_fatal():
    with pytest.raises(ValueError, match="expected one record"):
        comparator._require_unique([{"window": 0}, {"window": 0}], window=0)
