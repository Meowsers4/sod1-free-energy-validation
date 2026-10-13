"""Entry point for a separately sealed C2 scout execution release (Python 3.6+)."""

import json
from pathlib import Path
import sys

import core_runtime as core
import smoke_runtime as smoke


def require(ok, message):
    if not ok:
        raise ValueError(message)


def review(root, spec):
    root = Path(root)
    smoke.verify_package(root)
    require(spec.get("scope") == "f64a_folded_apo_2sh_r0_paired_100ps_timing_scout_release" and
            spec.get("production_authorized") is False and
            spec.get("release_source_candidate_sha256") ==
            "71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df",
            "wrong C2 scout release lineage")
    selected = spec.get("execution_authorized") is True
    require(spec.get("execution_authorized") is False or selected,
            "invalid execution flag")
    require(spec.get("selected_technical_arms") ==
            (["baseline", "hrex"] if selected else []) and
            (isinstance(spec.get("selection_record"), dict) if selected else
             spec.get("selection_record") is None),
            "selection record/arm gate mismatch")
    core.source_review(root, spec)
    require(smoke.sha(spec["image"]["path"]) == spec["image"]["sha256"],
            "r6 SIF hash mismatch")
    print("C2_SCOUT_EXECUTION_RELEASE_REVIEW_PASS states=20 execution_authorized={}; no job submitted".format(selected))


def permit(root, spec, arm):
    review(root, spec)
    core.execution_guard(spec, arm)
    if arm == "hrex":
        core.preflight_baseline_gate(root, arm)
        prior = core.work_path(root, "baseline")
        smoke.verify_files(prior, json.loads((prior / "output-hashes-after-accounting.json").read_text()))
    print("C2_SCOUT_{}_SUBMISSION_GUARD_PASS; no job submitted".format(arm.upper()))


def main():
    root = Path(__file__).resolve().parent
    require(len(sys.argv) >= 2, "command required")
    command = sys.argv[1]
    spec = core.spec_at(root)
    if command == "review":
        review(root, spec)
    elif command == "permit":
        require(len(sys.argv) == 3, "arm required")
        permit(root, spec, sys.argv[2])
    elif command in ("job", "rank", "probe"):
        require(len(sys.argv) == 3, "arm required")
        core.execution_guard(spec, sys.argv[2])
        if command == "job":
            core.job(root, spec, sys.argv[2])
        elif command == "rank":
            core.rank_main(root, spec, sys.argv[2])
        else:
            smoke.write_json(core.work_path(root, sys.argv[2]) / "device-map.json",
                             smoke.cuda_probe())
    elif command == "check-tmp":
        require(len(sys.argv) == 3, "token required")
        smoke.check_tmp_inside(sys.argv[2])
    elif command == "accounting":
        require(len(sys.argv) == 3, "arm required")
        core.accounting_review(root, sys.argv[2])
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    main()
