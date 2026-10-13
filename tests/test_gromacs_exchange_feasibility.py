"""Checks for the fail-closed C1 GROMACS exchange qualification."""

from copy import deepcopy

import pytest

from src.analysis import gromacs_exchange_feasibility as feasibility
from src.prep.build import load_config


def test_current_contract_is_blocked_and_never_authorizes_production():
    report = feasibility.evaluate(
        feasibility.load_qualification(), load_config("config/pipeline.yaml")
    )
    assert report["decision"] == "conditionally_feasible_new_build_required"
    assert report["production_authorized"] is False
    assert report["eligible_now"] is False
    assert report["controlled_unit"]["lambda_states"] == 20
    assert report["controlled_unit"]["leg"] == "folded"
    assert report["controlled_unit"]["state_directories_per_ladder"] == 20
    assert report["prospective_design"]["initial_realizations_per_method"] == 5
    assert report["prospective_design"]["counts_are_planning_choices"] is True


def test_standing_external_mpi_failure_and_scheduler_unknown_are_explicit():
    report = feasibility.evaluate(
        feasibility.load_qualification(), load_config("config/pipeline.yaml")
    )
    blockers = {item["id"]: item["status"] for item in report["blockers"]}
    assert blockers["build.external_mpi"] == "fail"
    assert blockers["build.combined_mpi_cuda"] == "fail"
    assert "scheduler.parallel_environment" not in blockers
    assert blockers["restart.whole_ladder"] == "unresolved"


def test_design_requires_separate_folded_ladders_for_realizations():
    controlled = feasibility.load_qualification()["controlled_unit"]
    assert controlled["cross_realization_exchange_forbidden"] is True
    assert controlled["unfolded_leg_in_core_comparison"] is False
    assert controlled["exchange_boundary"] == (
        "one independently initialized folded-leg realization"
    )


def test_pipeline_drift_fails_closed():
    pipeline = deepcopy(load_config("config/pipeline.yaml"))
    pipeline["cluster"]["mdrun_launcher"] = "mpirun"
    with pytest.raises(ValueError, match="standing_launcher_is_empty"):
        feasibility.evaluate(feasibility.load_qualification(), pipeline)


def test_qualification_rejects_authorization(tmp_path):
    spec = feasibility.load_qualification()
    spec["production_authorized"] = True
    path = tmp_path / "bad.yaml"
    import yaml

    path.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError, match="production_authorized"):
        feasibility.load_qualification(path)
