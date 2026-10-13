"""Unit/synthetic checks for the work-package B constructed model."""

from copy import deepcopy

import numpy as np
import pytest

from src.analysis import known_answer_model as model


def test_spec_is_complete_and_seeds_are_held_out():
    spec = model.load_spec()
    assert spec["lambda_vector"][0] == 0
    assert spec["lambda_vector"][-1] == 1
    assert not (
        set(spec["sampling"]["development_seeds"])
        & set(spec["sampling"]["heldout_seeds"])
    )
    assert spec["sampling"]["methods"] == [
        "independent_windows",
        "neighbor_replica_exchange",
    ]


def test_potential_vectorization_matches_scalar_evaluation():
    spec = model.load_spec()
    regime = spec["regimes"]["metastable"]
    x = np.array([-1.2, 0.1, 1.4])
    y = np.array([-0.9, 0.2, 1.1])
    lam = np.array([0.0, 0.5, 1.0])
    vector = model.reduced_potential(x, y, lam, spec["potential"], regime)
    scalar = np.array(
        [
            model.reduced_potential(a, b, c, spec["potential"], regime)
            for a, b, c in zip(x, y, lam)
        ]
    )
    assert np.allclose(vector, scalar, rtol=0, atol=1e-14)


@pytest.mark.parametrize("regime", ["easy", "metastable"])
def test_reference_refines_stably(regime):
    spec = model.load_spec()
    low = np.asarray(
        model.gauss_legendre_free_energies(spec, 96, spec["regimes"][regime])
    )
    high = np.asarray(
        model.gauss_legendre_free_energies(spec, 192, spec["regimes"][regime])
    )
    low -= low[0]
    high -= high[0]
    assert np.max(abs(low - high)) < 1e-8


def test_equal_cost_simulators_respect_budget_and_return_all_states():
    spec = deepcopy(model.load_spec())
    spec["sampling"]["potential_evaluation_budget"] = 4000
    spec["sampling"]["snapshot_stride_sweeps"] = 5
    outputs = {}
    for method in spec["sampling"]["methods"]:
        xs, ys, summary = model.simulate(
            spec, spec["regimes"]["easy"], method, seed=17
        )
        assert len(xs) == len(ys) == len(spec["lambda_vector"])
        assert len({len(values) for values in xs}) == 1
        assert summary["potential_evaluations"] <= 4000
        assert summary["unused_evaluation_budget"] < 2 * len(spec["lambda_vector"])
        outputs[method] = summary
    assert outputs["independent_windows"]["exchange_attempts"] == 0
    assert outputs["independent_windows"]["exchange_acceptance"] is None
    assert outputs["neighbor_replica_exchange"]["exchange_attempts"] > 0


def test_hysteresis_local_terms_reconstruct_net():
    spec = deepcopy(model.load_spec())
    spec["sampling"]["potential_evaluation_budget"] = 8000
    spec["sampling"]["snapshot_stride_sweeps"] = 5
    xs, ys, _ = model.simulate(
        spec, spec["regimes"]["easy"], "independent_windows", seed=19
    )
    result = model.solve_samples(xs, ys, spec, spec["regimes"]["easy"])
    local = result["signed_local_discrepancies_kT"]
    assert result["net_hysteresis_kT"] == pytest.approx(abs(sum(local)))
    assert result["sum_absolute_hysteresis_kT"] == pytest.approx(sum(map(abs, local)))
    assert result["max_absolute_hysteresis_kT"] == pytest.approx(max(map(abs, local)))
