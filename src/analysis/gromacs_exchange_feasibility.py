"""Fail-closed C1 qualification for a future GROMACS HREX comparison.

This module evaluates design and environment evidence only. It never invokes GROMACS,
MPI, a scheduler, or a GPU and therefore cannot submit or start a simulation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from src.fep.pmx_engine import lambda_ladder
from src.prep.build import load_config


DEFAULT_SPEC = Path("docs/gromacs_exchange_qualification_v1.yaml")
DEFAULT_PIPELINE = Path("config/pipeline.yaml")
DEFAULT_OUTPUT = Path(
    "results/cpu_qualification/gromacs_exchange_c1_v1/qualification.json"
)
ALLOWED_STATUSES = {"pass", "design_pass", "fail", "unresolved"}


def load_qualification(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    """Load and structurally validate the frozen C1 qualification record."""
    spec = yaml.safe_load(path.read_text())
    if spec.get("schema_version") != 1:
        raise ValueError("C1 qualification schema_version must be 1")
    if spec.get("production_authorized") is not False:
        raise ValueError("C1 is technical feasibility only; production_authorized must be false")

    gates = spec.get("gates", [])
    ids = [gate.get("id") for gate in gates]
    if not gates or len(ids) != len(set(ids)):
        raise ValueError("C1 gates must be non-empty and have unique ids")
    for gate in gates:
        if gate.get("status") not in ALLOWED_STATUSES:
            raise ValueError(f"invalid status for {gate.get('id')}: {gate.get('status')}")
        if gate.get("required") is not True or not gate.get("evidence"):
            raise ValueError(f"gate {gate.get('id')} must be required and carry evidence")
    return spec


def evaluate(
    spec: dict[str, Any], pipeline: dict[str, Any]
) -> dict[str, Any]:
    """Reconcile the frozen qualification against the current pipeline contract."""
    ladder = lambda_ladder(pipeline)
    controlled = spec["controlled_unit"]
    prospective = spec["prospective_design"]
    standing = spec["standing_contract"]
    cluster = pipeline["cluster"]
    fep = pipeline["fep"]

    checks = {
        "lambda_state_count_matches": len(ladder) == controlled["lambda_states"],
        "lambda_endpoints_preserved": ladder[0] == 0.0 and ladder[-1] == 1.0,
        "lambda_vector_strictly_ascending": all(
            right > left for left, right in zip(ladder, ladder[1:])
        ),
        "historical_pipeline_contains_folded_leg": "folded" in fep["legs"],
        "prospective_scope_is_folded_only": (
            controlled["leg"] == "folded"
            and controlled["unfolded_leg_in_core_comparison"] is False
        ),
        "one_directory_per_lambda_state": (
            controlled["state_directories_per_ladder"] == len(ladder)
        ),
        "historical_replicate_systems_are_independent": (
            fep["independent_replicate_systems"] is True
        ),
        "prospective_baseline_disables_exchange": (
            prospective["baseline_exchange_disabled"] is True
        ),
        "prospective_counts_remain_planning_choices": (
            prospective["counts_are_planning_choices"] is True
            and prospective["final_counts_require_precision_and_resource_admission"] is True
        ),
        "standing_binary_matches": cluster["gmx_binary"] == standing["binary"],
        "standing_launcher_is_empty": cluster["mdrun_launcher"] == "",
        "standing_array_unit_matches": cluster["array_unit"] == standing["array_unit"],
        "production_is_not_authorized": spec["production_authorized"] is False,
        "admission_is_closed": spec["admission"]["eligible_now"] is False,
    }
    if not all(checks.values()):
        failed = ", ".join(key for key, value in checks.items() if not value)
        raise ValueError(f"C1 qualification no longer matches pipeline: {failed}")

    admitted = set(spec["admission"]["all_required_statuses"])
    blockers = [
        {"id": gate["id"], "status": gate["status"], "evidence": gate["evidence"]}
        for gate in spec["gates"]
        if gate["required"] and gate["status"] not in admitted
    ]
    return {
        "schema_version": 1,
        "qualification_id": spec["qualification_id"],
        "frozen_at": str(spec["frozen_at"]),
        "scope": spec["scope"],
        "decision": spec["decision"],
        "decision_meaning": spec["decision_meaning"],
        "production_authorized": False,
        "eligible_now": not blockers and spec["admission"]["eligible_now"],
        "controlled_unit": controlled,
        "prospective_design": prospective,
        "evidence_snapshots": spec["evidence_snapshots"],
        "method_contract": spec["method_contract"],
        "pipeline_checks": checks,
        "gate_counts": {
            status: sum(gate["status"] == status for gate in spec["gates"])
            for status in sorted(ALLOWED_STATUSES)
        },
        "blockers": blockers,
        "next_evidence": spec["admission"]["next_evidence"],
        "prohibited_until_admitted": spec["admission"]["prohibited_until_admitted"],
        "sources": spec["sources"],
    }


def write_report(report: dict[str, Any], output: Path = DEFAULT_OUTPUT) -> None:
    """Write a deterministic JSON qualification report."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--pipeline", type=Path, default=DEFAULT_PIPELINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = evaluate(load_qualification(args.spec), load_config(args.pipeline))
    write_report(report, args.output)
    print(
        f"{report['decision']}: {len(report['blockers'])} required gates block admission; "
        f"production_authorized={report['production_authorized']}"
    )


if __name__ == "__main__":
    main()
