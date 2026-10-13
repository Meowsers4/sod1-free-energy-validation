"""Protein whole-ladder restart; exchange acceptance is descriptive. Python 3.6+."""
import copy
import json
import math
from pathlib import Path
import re
import shutil
import time

try:  # Standalone transfer package, or repository tests.
    import runtime as rt
except ImportError:
    from src.analysis import gromacs_gpu_smoke_runtime as rt


def restart_arguments(spec, phase):
    """Never pass a first-part step override to the continuation."""
    if phase == "first":
        return ["-nsteps", str(spec["restart"]["first_stop_step"])]
    rt.require(phase == "resume", "unknown restart phase")
    rt.require(spec["restart"]["append"], "restart requires explicit append")
    return ["-cpi", spec["restart"]["checkpoint"], "-append"]


def checkpoint_metadata(text, state, spec, final=False):
    """Reject wrong step/time/part or a checkpoint from a different lambda state."""
    def field(pattern, convert):
        matches = re.findall(pattern, text, re.M)
        rt.require(len(matches) == 1, "checkpoint metadata missing/ambiguous: " + pattern)
        return convert(matches[0])
    step = field(r"^\s*step\s*=\s*(\d+)\s*$", int)
    t = field(r"^\s*t\s*=\s*(\S+)\s*$", float)
    part = field(r"^\s*simulation part #\s*=\s*(\d+)\s*$", int)
    fep = field(r"^\s*fep_state\[0\]\s*=\s*(\d+)\s*$", int)
    r = spec["restart"]
    expected_step = r["final_step"] if final else r["first_stop_step"]
    expected_part = r["final_checkpoint_part"] if final else r["first_checkpoint_part"]
    rt.require(step == expected_step and part == expected_part, "checkpoint step/part mismatch")
    rt.require(math.isfinite(t) and abs(t - step*spec["fixture"]["dt_ps"]) < 1e-6,
               "checkpoint time mismatch")
    rt.require(fep == state["local_index"], "checkpoint lambda-state mismatch")
    return {"step": step, "time_ps": t, "part": part, "fep_state": fep}


def seal_first_part(root, spec, first_history):
    """Preserve every first-part file before any output is appended."""
    work = root / "attempt"
    archive = work / "before-restart"
    archive.mkdir()
    checkpoints, files = {}, {}
    for state in spec["states"]:
        name = state["directory"]
        p = work / name
        checkpoints[name] = checkpoint_metadata((p / "checkpoint.dump").read_text(), state, spec)
        rt.require(rt.sha(p / "topol.tpr") == rt.sha(root / "prepared" / name / "topol.tpr"),
                   "TPR changed during first part")
        rt.require((p / spec["restart"]["checkpoint"]).is_file(), "missing checkpoint")
        shutil.copytree(str(p), str(archive / name))
        for rel, digest in rt.inventory(p).items():
            files[name + "/" + rel] = digest
    for p in list(work.glob("rank-*.json")) + [work / "mps-overlap.json", work / "mpi-first.log",
                                                  work / "device-map.json", work / "protein-ladder-review-first.json"]:
        shutil.copyfile(str(p), str(archive / p.name))
    if spec.get("cpu_sharing"):
        shutil.copyfile(str(work / "cpu-affinity.json"), str(archive / "cpu-affinity.json"))
    rt.write_json(archive / "permutations.json", first_history)
    proof = {"files": files, "archive_files": rt.inventory(archive), "checkpoints": checkpoints,
             "sif_sha256": spec["image"]["sha256"], "package_manifest_sha256": rt.sha(root / "SHA256SUMS")}
    rt.write_json(work / "RESTART_READY.json", proof)
    for p in archive.rglob("*"):
        if p.is_file():
            p.chmod(0o444)
    return proof


def verify_checkpoint_inputs(root, spec):
    """Fail before MPI startup if even one checkpoint or TPR is absent/changed."""
    work = root / "attempt"
    proof = json.loads((work / "RESTART_READY.json").read_text())
    rt.require(proof["sif_sha256"] == spec["image"]["sha256"] and
               proof["package_manifest_sha256"] == rt.sha(root / "SHA256SUMS"), "restart identity mismatch")
    selected = {}
    for state in spec["states"]:
        for filename in (spec["restart"]["checkpoint"], "topol.tpr"):
            rel = state["directory"] + "/" + filename
            rt.require(rel in proof["files"], "checkpoint/TPR not sealed")
            selected[rel] = proof["files"][rel]
    rt.verify_files(work, selected)
    return proof


def run_phases(root, spec, scratch, runner, launch, env, mps):
    """Two MPI launches in one bounded allocation; MPS stays idle between them."""
    rt.require(mps is not None, "restart test requires private MPS")
    work = root / "attempt"
    runner.run(launch + ["first"], work / "mpi-first.log", env=env, mps=mps)
    rt.require(mps.observed_all, "first-part all-rank client MPS overlap not observed")
    deadline = time.monotonic() + spec["sharing"]["shutdown_timeout_seconds"]
    while any(mps.clients().values()):
        rt.require(time.monotonic() < deadline, "first-part MPS clients did not exit")
        time.sleep(0.1)
    rt.extract_outputs(root, spec, scratch, runner)
    first = copy.deepcopy(spec)
    first["fixture"]["nsteps"] = spec["restart"]["first_stop_step"]
    history = rt.validate_results(root, first)
    rt.require([h["step"] for h in history] == spec["restart"]["phase1_expected_exchange_steps"],
               "first-part exchange schedule mismatch")
    proof = seal_first_part(root, spec, history)
    # Check raw outputs as well as checkpoints before append; never relax hashes.
    rt.verify_files(work, proof["files"])
    rt.verify_files(work / "before-restart", proof["archive_files"])
    verify_checkpoint_inputs(root, spec)
    mps.observed_all = False
    # Old PID records are sealed above; require a complete new set for observation.
    for p in work.glob("rank-*.json"):
        p.unlink()
    runner.run(launch + ["resume"], work / "mpi-resume.log", env=env, mps=mps)
    rt.require(mps.observed_all, "resumed all-rank client MPS overlap not observed")


def data_rows(text):
    return [line.split() for line in text.splitlines() if line.strip() and not line.startswith(("#", "@"))]


def validate_restart(root, spec, history):
    """Check preserved prefix, unique boundary outputs, part advance, and exchanges."""
    work = root / "attempt"
    archive = work / "before-restart"
    proof = json.loads((work / "RESTART_READY.json").read_text())
    history = json.loads(json.dumps(history))  # Parser pairs are tuples; sealed JSON uses lists.
    rt.verify_files(archive, proof["archive_files"])
    first_history = json.loads((archive / "permutations.json").read_text())
    rt.require(history[:len(first_history)] == first_history, "pre-restart exchange history changed")
    rt.require([h["step"] for h in history] == spec["restart"]["combined_expected_exchange_steps"],
               "missing/duplicated restart-boundary exchange")
    boundary = spec["restart"]["first_stop_step"] * spec["fixture"]["dt_ps"]
    final = {}
    for state in spec["states"]:
        name = state["directory"]
        p = work / name
        final[name] = checkpoint_metadata((p / "checkpoint.dump").read_text(), state, spec, final=True)
        rt.require(rt.sha(p / "topol.tpr") == proof["files"][name + "/topol.tpr"], "TPR changed across restart")
        for filename in ("smoke.xvg", "energy.xvg"):
            previous = data_rows((archive / name / filename).read_text())
            current = data_rows((p / filename).read_text())
            old_prefix = [row for row in previous if float(row[0]) < boundary - 1e-6]
            new_prefix = [row for row in current if float(row[0]) < boundary - 1e-6]
            rt.require(new_prefix == old_prefix, "appended output changed pre-checkpoint data: " + name + "/" + filename)
            rt.require(sum(abs(float(row[0])-boundary) < 1e-6 for row in current) == 1,
                       "missing/duplicated checkpoint-time output")
        rt.require(not list(p.glob("*.part[0-9]*")), "non-appended part outputs found")
    rt.write_json(work / "restart-review.json", {"restart_verified": True,
                  "first_checkpoints": proof["checkpoints"], "final_checkpoints": final,
                  "phase1_exchange_rounds": len(first_history), "combined_exchange_rounds": len(history),
                  "pre_checkpoint_data_preserved": True, "boundary_output_unique": True,
                  "phase1_mps_overlap": json.loads((archive / "mps-overlap.json").read_text()),
                  "phase2_mps_overlap": json.loads((work / "mps-overlap.json").read_text())})
