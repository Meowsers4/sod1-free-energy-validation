"""Inactive F64A C2 live-branch runtime candidate (Python 3.6+).

The transferred contract has execution_authorized=false. Review and CPU-only
preflight are callable; job/rank/probe fail before side effects. A separately
sealed selected release would be needed to run the technical fixture.
"""

import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import branch_input_checker as branch
import core_runtime as core
import mps
import preflight
import scout_checks as scout
import smoke_runtime as base


def require(ok, message):
    if not ok:
        raise ValueError(message)


def root_path():
    return Path(__file__).resolve().parent


def spec_at(root):
    return json.loads((root / "contract.json").read_text())


def guard(spec):
    selection = spec.get("selection_record")
    schedule = spec.get("scheduler", {})
    require(spec.get("execution_authorized") is True and
            spec.get("production_authorized") is False and
            spec.get("scope") == "f64a_c2_live_branch_fixture_runtime" and
            spec.get("release_source_candidate_sha256") ==
            "27e712a4dfc1e43d8e1d1eb3a8544224d86be95b4e758a33a27f327eb5de92d3" and
            isinstance(selection, dict) and
            selection.get("decision") == "one_bounded_technical_live_branch_fixture" and
            selection.get("reviewed_release_candidate_sha256") ==
            spec.get("reviewed_release_candidate_sha256") and
            spec.get("reviewed_release_candidate_sha256") ==
            "951d9f722fe693935fb3c7d2788bc4d503125e3dae6746551d854dbf5896268f" and
            selection.get("su_balance_decision") == "user_reported_balance" and
            selection.get("su_balance_reported_by") == "user" and
            selection.get("su_balance_su_reported") == 15000 and
            selection.get("su_balance_agent_verified") is False and
            selection.get("su_charge_rate_known") is False and
            selection.get("max_allocated_gpu_hours") == 0.5 and
            selection.get("max_requested_cpu_slot_hours") == 8 and
            selection.get("no_retry") is True and
            selection.get("production_authorized") is False and
            schedule.get("project") == "rise-batteries" and
            schedule.get("queue") == "l40s" and
            schedule.get("pe") == "omp16" and
            schedule.get("slots") == 16 and
            schedule.get("ranks") == 20 and
            schedule.get("gpus") == 1 and
            schedule.get("gpu_type") == "L40S" and
            schedule.get("walltime_seconds") == 1800 and
            schedule.get("work_deadline_seconds") == 1560 and
            schedule.get("storage_stop_bytes_each") == 1610612736 and
            schedule.get("storage_cap_bytes_each") == 2147483648 and
            schedule.get("minimum_free_bytes_each") == 3221225472,
            "live GPU fixture not selected by this package")


def verify_package(root):
    root = Path(root)
    base.verify_package(root)
    require(spec_at(root).get("scope") == "f64a_c2_live_branch_fixture_runtime",
            "wrong fixture scope")


def review_selected_provenance(root, spec):
    require(spec.get("reviewed_release_candidate_sha256") ==
            "951d9f722fe693935fb3c7d2788bc4d503125e3dae6746551d854dbf5896268f",
            "wrong reviewed release candidate")
    saved_manifest = root / "release-candidate-SHA256SUMS"
    require(saved_manifest.is_file() and not saved_manifest.is_symlink() and
            base.sha(saved_manifest) == spec["reviewed_release_candidate_sha256"],
            "reviewed release manifest changed")
    rows = [line.split("  ", 1) for line in saved_manifest.read_text().splitlines()]
    require(len(rows) == 17 and len({name for _, name in rows}) == 17,
            "reviewed release file set changed")
    saved = {"SHA256SUMS": "release-candidate-SHA256SUMS",
             "README.txt": "release-candidate-README.txt",
             "contract.json": "release-candidate-contract.json",
             "runtime.py": "release-candidate-runtime.py"}
    for digest, name in rows:
        file = root / saved.get(name, name)
        require(file.is_file() and not file.is_symlink() and
                base.sha(file) == digest,
                "reviewed release source differs: " + name)


def review(root, spec):
    verify_package(root)
    review_selected_provenance(root, spec)
    require(spec.get("release_source_candidate_sha256") ==
            "27e712a4dfc1e43d8e1d1eb3a8544224d86be95b4e758a33a27f327eb5de92d3" and
            spec.get("production_authorized") is False,
            "wrong release source or production scope")
    require(base.sha(root / "candidate-SHA256SUMS") ==
            spec["release_source_candidate_sha256"],
            "reviewed inactive runtime provenance changed")
    source_rows = [line.split("  ", 1) for line in
                   (root / "candidate-SHA256SUMS").read_text().splitlines()]
    require(len(source_rows) == 12 and
            len({name for _, name in source_rows}) == 12,
            "inactive runtime provenance manifest changed")
    for digest, name in source_rows:
        saved = {"runtime.py": "candidate-runtime.py",
                 "contract.json": "candidate-contract.json"}.get(name, name)
        if name not in ("README.txt", "REVIEW_ON_SCC.sh", "REVIEW_PACKAGE.sh"):
            require(base.sha(root / saved) == digest,
                    "inactive runtime source differs: " + name)
    require((root / "fixture.sge").is_file() and
            (root / "SUBMIT_ON_SCC.sh").is_file(),
            "release submission scripts missing")
    sge = (root / "fixture.sge").read_text()
    submission = (root / "SUBMIT_ON_SCC.sh").read_text()
    require(all(line in sge.splitlines() for line in
                ("#$ -P rise-batteries", "#$ -q l40s", "#$ -pe omp16 16",
                 "#$ -l gpus=1,gpu_type=L40S", "#$ -l h_rt=00:30:00",
                 "#$ -r n")) and
            "runtime.py job" in sge and
            submission.index("runtime.py permit") <
            submission.index("mkdir submission") <
            submission.index("qsub \"${request[@]}\" -w v") <
            submission.index("qsub \"${request[@]}\" -terse") and
            "gpus=1,gpu_type=L40S,h_rt=00:30:00" in submission and
            "-pe omp16 16" in submission and
            "-r n" in submission,
            "submission script or one-job request changed")
    if spec.get("execution_authorized") is True:
        guard(spec)
    else:
        require(spec.get("execution_authorized") is False and
                spec.get("selection_record") is None and
                spec.get("reviewed_release_candidate_sha256") is None,
                "candidate authorization changed")
    prior = Path(spec["preflight"]["path"])
    require(prior.is_file() and not prior.is_symlink(), "accepted preflight record missing")
    record = json.loads(prior.read_text())
    require(record.get("status") == "preflight_pass_pending_fixture_selection" and
            record.get("execution_authorized") is False and
            record.get("production_authorized") is False and
            record.get("package_manifest_sha256") ==
            spec["preflight"]["package_manifest_sha256"] and
            record.get("source", {}).get("source_manifest_sha256") ==
            spec["source_manifest_sha256"] and
            record.get("source", {}).get("image_sha256") ==
            spec["image_sha256"] and
            record.get("queue", {}).get("validation_only") is True and
            "verification: found suitable queue(s)" in
            record.get("queue", {}).get("output", "") and
            record.get("su_balance") == "unknown_not_waived_for_this_fixture",
            "preflight record/selection mismatch")
    queue = record["queue"]["command"]
    require(queue[0] == "qsub" and
            queue[queue.index("-w") + 1] == "v" and
            queue[queue.index("-pe") + 1:queue.index("-pe") + 3] ==
            ["omp16", "16"] and
            "gpus=1,gpu_type=L40S,h_rt=00:30:00" in queue and
            record["project_quota"]["free_quota_bytes_estimated"] >=
            spec["min_project_quota_free_bytes"] and
            record["project_filesystem_free_bytes"] >=
            spec["min_filesystem_free_bytes"] and
            record["persistent_root_writable"] is True,
            "preflight queue/storage evidence mismatch")
    source = preflight.source_review(spec)
    require(source["states"] == 20, "wrong source state count")
    prepared = json.loads((Path(spec["source_prepared"]) / "PREPARED.json").read_text())
    require(all(prepared["states"][i]["tpr_sha256"] ==
                spec["states"][i]["tpr_sha256"] for i in range(20)),
            "candidate initial TPR hash differs from source")
    require(spec["scheduler"]["walltime_seconds"] == 1800 and
            spec["scheduler"]["slots"] == 16 and
            spec["scheduler"]["ranks"] == 20 and
            spec["scheduler"]["gpus"] == 1 and
            spec["scheduler"]["pe"] == "omp16" and
            spec["scheduler"]["queue"] == "l40s" and
            spec["scheduler"]["project"] == "rise-batteries" and
            spec["fixture"]["common_step"] == 1100 and
            spec["fixture"]["retained_steps"] ==
            {"baseline": 2000, "hrex": 1500} and
            spec["fixture"]["hrex_replex"] == 500 and
            len(spec["states"]) == 20 and
            all(s["local_index"] == i and
                s["directory"] == "state{:02d}".format(i) and
                s["lambda_value"] == spec["expected_lambdas"][i]
                for i, s in enumerate(spec["states"])),
            "candidate resources/fixture schedule changed")
    print("C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20 execution_authorized={}; no job submitted".format(
          str(spec["execution_authorized"])) )


def container(root, spec, scratch, cwd="/smoke", gpu=False):
    source = Path(spec["source_prepared"])
    ff = source / "forcefield"
    args = ["singularity", "exec", "--cleanenv", "--contain", "--no-mount",
            "bind-paths,hostfs,cwd,tmp", "--bind", str(root) + ":/smoke",
            "--bind", str(source) + ":/protein:ro",
            "--bind", str(ff) + ":" + spec["forcefield_root"] + ":ro",
            "--bind", str(scratch) + ":/tmp", "--pwd", cwd]
    if gpu:
        args.extend(("--nv", "--bind", str(scratch) + ":" + str(scratch)))
    return args + [spec["image"]["path"]]


def environment(spec, gpu=False):
    result = base.container_env(gpu)
    result["SINGULARITYENV_GMXLIB"] = spec["forcefield_root"]
    return result


class MonitoredRunner(core.BoundedRunner):
    """Apply the byte stop plus live free-space guards to both locations."""

    def __init__(self, work, scratch, deadline, stop_bytes, cap_bytes,
                 min_free_bytes):
        super().__init__(work, scratch, deadline, stop_bytes, cap_bytes)
        self.min_free_bytes = min_free_bytes

    def limits(self):
        super().limits()
        require(shutil.disk_usage(str(self.work)).free >= self.min_free_bytes and
                shutil.disk_usage(str(self.scratch)).free >= self.min_free_bytes,
                "persistent or scratch free-space floor reached")


def selected(text, pattern):
    return "\n".join(line for line in text.splitlines() if pattern.match(line)) + "\n"


CP_LINES = re.compile(r"^\s*(?:step|t|simulation part #|fep_state\[0\])\s*=")
TPR_LINES = re.compile(r"^\s*(?:natoms|nsteps|init-step|init-lambda-state|"
                       r"n-lambdas|calc-lambda-neighbors|dt|fep-lambdas)\s*=|"
                       r"^\s*all-lambdas:")


def continuation_mdp(original, spec, arm):
    before = branch.mdp_values(original)
    require(int(before["nsteps"]) == 2000, "source TPR duration changed")
    changes = {"nsteps": str(spec["fixture"]["retained_steps"][arm]),
               "init-step": "1100", "tinit": "0", "simulation-part": "2",
               "gen-vel": "no", "continuation": "yes"}
    lines, replaced = [], set()
    for line in original.splitlines():
        body, sep, comment = line.partition(";")
        if "=" in body:
            key = body.split("=", 1)[0]
            normalized = key.strip().lower().replace("_", "-")
            if normalized in changes:
                line = key + "= " + changes[normalized]
                if sep:
                    line += ";" + comment
                replaced.add(normalized)
        lines.append(line)
    for key in changes:
        if key not in replaced:
            lines.append(key + " = " + changes[key])
    result = "\n".join(lines) + "\n"
    after = branch.mdp_values(result)
    require(set(after) == set(before) | set(changes) and
            all(after[key] == (changes[key] if key in changes else value)
                for key, value in before.items()),
            "unregistered branch MDP change")
    return result


def cpu_capture(runner, root, spec, scratch, command, log):
    full = runner.capture(container(root, spec, scratch) + [spec["image"]["gmx"]] +
                          command, log, env=environment(spec), timeout=120)
    require(not re.search(r"^\s*WARNING", full, re.M),
            "GROMACS CPU warning: " + str(log))
    return full


def phase_args(spec, phase):
    require(phase in ("common", "baseline", "hrex"), "unknown phase")
    f = spec["fixture"]
    argv = [spec["image"]["gmx"], "mdrun", "-multidir"] + [
        state["directory"] for state in spec["states"]] + [
        "-s", "topol.tpr", "-deffnm", "run", "-cpo", "final.cpt",
        "-nb", "gpu", "-pme", "cpu", "-bonded", "cpu", "-update", "cpu",
        "-ntomp", "1", "-gpu_id", "0", "-pin", "off", "-dlb", "no",
        "-notunepme", "-cpt", "1", "-maxh", "0.4"]
    if phase == "common":
        argv += ["-nsteps", str(f["common_step"]), "-replex", "0"]
    else:
        argv += ["-cpi", "start.cpt", "-noappend", "-replex",
                 str(0 if phase == "baseline" else f["hrex_replex"])]
        if phase == "hrex":
            argv += ["-reseed", str(f["hrex_seed"])]
    return argv


def rank_main(root, spec, phase):
    guard(spec)
    rank = int(os.environ["OMPI_COMM_WORLD_RANK"])
    require(int(os.environ["OMPI_COMM_WORLD_SIZE"]) == 20 and
            int(os.environ["OMPI_COMM_WORLD_LOCAL_SIZE"]) == 20 and
            0 <= rank < 20, "wrong MPI rank layout")
    work = root / "attempt" / phase
    selected_cpus = json.loads((root / "attempt/cpu-affinity.json").read_text())[
        "selected_cpu_ids"]
    require(sorted(os.sched_getaffinity(0)) == selected_cpus,
            "rank escaped CPU affinity mask")
    mapping = json.loads((work / "device-map.json").read_text())
    require(os.environ.get("CUDA_VISIBLE_DEVICES") ==
            mapping["CUDA_VISIBLE_DEVICES"], "rank GPU visibility changed")
    gpu = base.device_for_rank(mapping, rank, spec)
    service = json.loads((work / "mps.json").read_text())
    require(os.environ.get("CUDA_MPS_PIPE_DIRECTORY") == service["pipe"],
            "rank lost private MPS pipe")
    if phase != "common":
        source = (root / "attempt/branch-inputs/arms" / phase /
                  ("state{:02d}".format(rank)) / "start.cpt")
        require(base.sha(source) == base.sha(work / ("state{:02d}".format(rank)) /
                                             "start.cpt"),
                "rank checkpoint copy changed")
    base.write_json(work / ("rank-{}.json".format(rank)), {
        "rank": rank, "pid": os.getpid(), "host": socket.gethostname(),
        "state": "state{:02d}".format(rank), "gpu": gpu,
        "cpu_affinity": selected_cpus,
        "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"]})
    argv = phase_args(spec, phase)
    base.write_json(work / ("rank-{}.argv.json".format(rank)), argv)
    os.environ["OMP_NUM_THREADS"] = "1"
    os.execv(argv[0], argv)


def run_phase(root, spec, attempt, scratch, runner, phase, gpu_uuid):
    work = attempt / phase
    phase_scratch = scratch / phase
    phase_scratch.mkdir()
    service = mps.PrivateMPS(work, phase_scratch, gpu_uuid, spec)
    try:
        service.start()
        gpu_env = service.container_environment(environment(spec, True))
        command = container(root, spec, scratch, "/smoke/attempt/" + phase, True)
        runner.run(command + [spec["image"]["python"], "/smoke/runtime.py",
                              "probe", phase], work / "probe.log", env=gpu_env)
        mapping = json.loads((work / "device-map.json").read_text())
        require(mapping["CUDA_VISIBLE_DEVICES"] ==
                gpu_env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"] and
                len(mapping["devices"]) == 1 and
                mapping["devices"][0]["uuid"] == gpu_uuid,
                "container GPU differs from allocation")
        launch = command + base.mpi_arguments(spec) + [spec["image"]["python"],
                                                "/smoke/runtime.py", "rank", phase]
        started = time.monotonic()
        runner.run(launch, work / "mpi.log", env=gpu_env, mps_service=service)
        seconds = time.monotonic() - started
    finally:
        service.close()
    require(service.observed_all and service.closed,
            "20 matching MPS clients and cleanup not confirmed: " + phase)
    return {"dynamics_seconds": seconds, "mps_all_clients_observed": True,
            "mps_cleanup_confirmed": True}


def prepare_common(root, spec, attempt):
    source = Path(spec["source_prepared"])
    work = attempt / "common"
    work.mkdir()
    for state in spec["states"]:
        name = state["directory"]
        target = work / name
        target.mkdir()
        src = source / "states" / name / "topol.tpr"
        require(base.sha(src) == state["tpr_sha256"],
                "registered initial TPR changed: " + name)
        shutil.copyfile(str(src), str(target / "topol.tpr"))
        require(base.sha(src) == base.sha(target / "topol.tpr"),
                "initial TPR copy mismatch: " + name)


def seal_common(root, spec, attempt, scratch, runner):
    work = attempt / "common"
    inputs = attempt / "branch-inputs"
    inputs.mkdir()
    (inputs / "common").mkdir()
    (inputs / "arms").mkdir()
    (inputs / "mdps").mkdir()
    hashes = {}
    for index, name in enumerate(branch.STATE_NAMES):
        origin = work / name / "final.cpt"
        require(origin.is_file() and origin.stat().st_size > 0,
                "common checkpoint missing: " + name)
        dest = inputs / "common" / name
        dest.mkdir()
        shutil.copyfile(str(origin), str(dest / "start.cpt"))
        hashes[name] = base.sha(origin)
        require(base.sha(dest / "start.cpt") == hashes[name],
                "common checkpoint copy changed")
        full = cpu_capture(runner, root, spec, scratch,
                           ["dump", "-cp", "/smoke/attempt/branch-inputs/common/" +
                            name + "/start.cpt"], dest / "dump.log")
        text = selected(full, CP_LINES)
        (dest / "start.cpt.dump").write_text(text)
        branch.checkpoint_metadata(text, index, {
            "prep_step": 1100, "prep_time_ps": 2.2, "prep_checkpoint_part": 1})
        # The CPU checker requires precisely two common-state files.
        (dest / "dump.log").rename(attempt / ("common-dump-" + name + ".log"))
        (Path(str(dest / "dump.log") + ".command.json")).rename(
            attempt / ("common-dump-" + name + ".command.json"))
        log = (work / name / "run.log").read_text(errors="replace")
        require("Finished mdrun" in log and
                not re.search(r"^Replica exchange at step |^Repl\s+ex\s+",
                              log, re.M), "common run incomplete or exchanged")
    base.write_json(attempt / "common-checkpoints.json", hashes)
    base.write_json(attempt / "common-seal.json", base.inventory(work))
    return hashes


def prepare_branch_inputs(root, spec, attempt, scratch, runner, hashes):
    source = Path(spec["source_prepared"])
    inputs = attempt / "branch-inputs"
    for arm in branch.ARMS:
        (inputs / "arms" / arm).mkdir()
        (inputs / "mdps" / arm).mkdir()
    for index, name in enumerate(branch.STATE_NAMES):
        original = source / "inputs" / "states" / name / "technical.mdp"
        for arm in branch.ARMS:
            runner.limits()
            target = inputs / "arms" / arm / name
            target.mkdir()
            shutil.copyfile(str(inputs / "common" / name / "start.cpt"),
                            str(target / "start.cpt"))
            require(base.sha(target / "start.cpt") == hashes[name],
                    "branch checkpoint copy changed")
            shutil.copyfile(str(inputs / "common" / name / "start.cpt.dump"),
                            str(target / "start.cpt.dump"))
            mdp = inputs / "mdps" / arm / (name + ".mdp")
            mdp.write_text(continuation_mdp(original.read_text(), spec, arm))
            gmx = container(root, spec, scratch) + [spec["image"]["gmx"]]
            command = gmx + ["grompp", "-f", "/smoke/attempt/branch-inputs/mdps/" +
                             arm + "/" + name + ".mdp",
                             "-c", "/protein/inputs/states/" + name + "/start.gro",
                             "-p", "/protein/inputs/system/hybrid.top", "-t",
                             "/smoke/attempt/branch-inputs/arms/" + arm + "/" +
                             name + "/start.cpt", "-o",
                             "/smoke/attempt/branch-inputs/arms/" + arm + "/" +
                             name + "/topol.tpr", "-po",
                             "/smoke/attempt/branch-inputs/arms/" + arm + "/" +
                             name + "/mdout.mdp"]
            external_log = attempt / ("grompp-" + arm + "-" + name + ".log")
            runner.run(command, external_log, env=environment(spec), timeout=120)
            grompp_text = external_log.read_text(errors="replace")
            (target / "grompp.log").write_text(grompp_text)
            base.write_json(target / "grompp-result.json", {
                "argv": command, "exit_status": 0})
            require(not re.search(r"^\s*WARNING", grompp_text, re.M),
                    "grompp failed/warned: " + arm + "/" + name)
            runner.limits()
            full = cpu_capture(runner, root, spec, scratch,
                               ["dump", "-s", "/smoke/attempt/branch-inputs/arms/" +
                                arm + "/" + name + "/topol.tpr"],
                               attempt / ("tpr-dump-" + arm + "-" + name + ".log"))
            (target / "topol.tpr.dump").write_text(selected(full, TPR_LINES))
    plan = {"schema_version": 1, "scope": branch.SCOPE,
            "execution_authorized": False, "production_authorized": False,
            "image_path": spec["image"]["path"],
            "image_sha256": spec["image"]["sha256"],
            "state_count": 20, "atom_count": spec["expected_atom_count"],
            "prep_step": 1100, "prep_time_ps": 2.2,
            "prep_checkpoint_part": 1, "branch_simulation_part": 2,
            "dt_ps": 0.002,
            "retained_steps": spec["fixture"]["retained_steps"],
            "lambda_vector": spec["expected_lambdas"],
            "output_strides": spec["fixture"]["output_strides"],
            "checkpoint_sha256": hashes}
    base.write_json(inputs / "plan.json", plan)
    branch.review(inputs, plan)
    base.write_json(attempt / "branch-input-seal.json", base.inventory(inputs))
    print("C2_BRANCH_INPUTS_FROM_NO_EXCHANGE_COMMON_REVIEW_PASS", flush=True)


def prepare_arm_run(root, spec, attempt, arm, hashes):
    work = attempt / arm
    work.mkdir()
    for name in branch.STATE_NAMES:
        target = work / name
        target.mkdir()
        src = attempt / "branch-inputs/arms" / arm / name
        shutil.copyfile(str(src / "topol.tpr"), str(target / "topol.tpr"))
        shutil.copyfile(str(src / "start.cpt"), str(target / "start.cpt"))
        require(base.sha(target / "topol.tpr") == base.sha(src / "topol.tpr") and
                base.sha(target / "start.cpt") == hashes[name],
                "arm run input copy changed")


def parse_hrex(texts, spec):
    steps = spec["fixture"]["expected_exchange_steps"]
    histories = []
    for text in texts:
        headers = list(re.finditer(r"^Replica exchange at step (\d+) time [^\n]+$",
                                   text, re.M))
        actual = [int(m.group(1)) for m in headers]
        require(actual == steps, "HREX exchange round timing mismatch")
        walkers, history = list(range(20)), []
        for index, header in enumerate(headers):
            end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
            lines = re.findall(r"^Repl\s+ex\s+(.+)$", text[header.end():end], re.M)
            require(len(lines) == 1, "exchange outcome missing/duplicate")
            tokens = lines[0].split()
            require([int(x) for x in tokens if x.isdigit()] == list(range(20)) and
                    all(x.isdigit() or x == "x" for x in tokens),
                    "invalid exchange tokens")
            first = 0 if (actual[index] // 500) % 2 else 1
            attempted = [[left, left + 1] for left in range(first, 19, 2)]
            allowed = {tuple(x) for x in attempted}
            accepted = []
            for pos, token in enumerate(tokens):
                if token != "x":
                    continue
                require(0 < pos < len(tokens) - 1 and
                        tokens[pos - 1].isdigit() and tokens[pos + 1].isdigit(),
                        "invalid accepted swap marker")
                pair = (int(tokens[pos - 1]), int(tokens[pos + 1]))
                require(pair in allowed, "unattempted exchange accepted")
                accepted.append(list(pair))
            require(len({x for pair in accepted for x in pair}) ==
                    2 * len(accepted), "overlapping accepted swaps")
            for left, right in accepted:
                walkers[left], walkers[right] = walkers[right], walkers[left]
            history.append({"step": actual[index], "attempted_pairs": attempted,
                            "accepted_pairs": accepted,
                            "state_to_walker": walkers[:]})
        histories.append(history)
    require(len(histories) == 20 and all(h == histories[0] for h in histories),
            "exchange permutation differs across ranks")
    attempts = {(left, left + 1): 0 for left in range(19)}
    accepts = dict.fromkeys(attempts, 0)
    for row in histories[0]:
        for pair in row["attempted_pairs"]:
            attempts[tuple(pair)] += 1
        for pair in row["accepted_pairs"]:
            accepts[tuple(pair)] += 1
    require(all(attempts.values()), "HREX missed a neighboring pair")
    return {"history": histories[0], "rounds": len(steps),
            "attempted_exchanges": sum(attempts.values()),
            "accepted_exchanges": sum(accepts.values()),
            "by_neighbor": [{"pair": list(pair), "attempted": attempts[pair],
                             "accepted": accepts[pair]} for pair in sorted(attempts)],
            "final_state_to_walker": histories[0][-1]["state_to_walker"]}


def output_file(path, stem, suffix, part_required):
    matches = list(path.glob(stem + "*" + suffix))
    if part_required:
        matches = [m for m in matches if re.fullmatch(
            re.escape(stem) + r"\.part\d{4}" + re.escape(suffix), m.name)]
    else:
        matches = [m for m in matches if m.name == stem + suffix]
    require(len(matches) == 1 and matches[0].stat().st_size > 0,
            "missing/ambiguous output: " + str(path / (stem + suffix)))
    return matches[0]


def expected_grid(start, final, stride):
    first = ((start // stride) + 1) * stride
    return list(range(first, final + 1, stride))


def check_grid(text, start, final, stride, lambdas=None, state=None):
    legends = re.findall(r'^@\s+s\d+\s+legend "(.+)"$', text, re.M)
    if lambdas is not None:
        require("state {}:".format(state) in text, "DHDL state label mismatch")
        foreign = [float(m.group(1)) for line in legends
                   for m in [re.search(r" to ([0-9.]+)$", line)] if m]
        require(foreign == lambdas, "DHDL foreign-energy label mismatch")
    rows = []
    for line in text.splitlines():
        if not line or line.startswith(("#", "@")):
            continue
        row = [float(x) for x in line.split()]
        require(len(row) == len(legends) + 1 and
                all(math.isfinite(x) for x in row), "invalid/nonfinite XVG row")
        rows.append(row)
    steps = expected_grid(start, final, stride)
    times = [x * 0.002 for x in steps]
    observed = [r[0] for r in rows]
    if observed and abs(observed[0] - start * 0.002) < 1e-5:
        observed = observed[1:]  # Preserve but do not double-count boundary.
    require(len(observed) == len(times) and
            all(abs(a - b) < 1e-5 for a, b in zip(observed, times)),
            "output grid incomplete/duplicated")
    return {"records": len(rows), "boundary_present": len(rows) > len(times),
            "first_retained_ps": times[0], "last_ps": times[-1]}


def validate_phase(root, spec, attempt, scratch, runner, phase):
    start = 0 if phase == "common" else 1100
    final = {"common": 1100, "baseline": 3100, "hrex": 2600}[phase]
    work = attempt / phase
    logs, checkpoint, dhdl, energy, xtc = [], {}, {}, {}, {}
    parts = set()
    for state, name in enumerate(branch.STATE_NAMES):
        path = work / name
        suffix = phase != "common"
        log_path = output_file(path, "run", ".log", suffix)
        log = log_path.read_text(errors="replace")
        require("Finished mdrun" in log and
                re.search(r"PP:0(?:\D|$)", log) and
                re.search(r"PP tasks will do[^\n]+GPU", log),
                "GPU mdrun incomplete: " + phase + "/" + name)
        logs.append(log)
        for ext in (".log", ".xvg", ".edr", ".xtc", ".gro"):
            file = output_file(path, "run", ext, suffix)
            if suffix:
                parts.add(re.search(r"\.part(\d{4})\.", file.name).group(1))
        xvg_path = output_file(path, "run", ".xvg", suffix)
        dhdl[name] = check_grid(xvg_path.read_text(), start, final, 100,
                                spec["expected_lambdas"], state)
        edr = output_file(path, "run", ".edr", suffix)
        gmx = (container(root, spec, scratch,
                         "/smoke/attempt/{}/{}".format(phase, name)) +
               [spec["image"]["gmx"]])
        runner.run(gmx + ["energy", "-f", edr.name, "-o", "energy.xvg"],
                   path / "energy-extraction.log", env=environment(spec),
                   stdin="Potential\nTemperature\n0\n", timeout=120)
        energy[name] = check_grid((path / "energy.xvg").read_text(),
                                  start, final, 100)
        energy_text = (path / "energy.xvg").read_text()
        require('legend "Potential"' in energy_text and
                'legend "Temperature"' in energy_text,
                "energy extraction lacks Potential/Temperature")
        cpt = path / "final.cpt"
        if not cpt.is_file():
            cpt = output_file(path, "final", ".cpt", suffix)
        require(cpt.stat().st_size > 0, "empty final checkpoint")
        dump = cpu_capture(runner, root, spec, scratch,
                           ["dump", "-cp", "/smoke/attempt/{}/{}/{}".format(
                               phase, name, cpt.name)],
                           path / "checkpoint-extraction.log")
        checkpoint[name] = branch.checkpoint_metadata(selected(dump, CP_LINES), state,
            {"prep_step": final, "prep_time_ps": final * 0.002,
             "prep_checkpoint_part": 1 if phase == "common" else 2})
        source_gro = Path(spec["source_prepared"]) / "inputs/states" / name / "start.gro"
        atoms, source_labels = scout.gro_identity(source_gro)
        final_gro = output_file(path, "run", ".gro", suffix)
        final_atoms, final_labels = scout.gro_identity(final_gro)
        require(atoms == final_atoms and source_labels == final_labels,
                "final atom identity/order mismatch")
        xtc_path = output_file(path, "run", ".xtc", suffix)
        expected = ([0] if phase == "common" else []) + expected_grid(start, final, 200)
        candidates = [expected]
        if phase != "common":
            candidates.append([start] + expected)
        if final not in expected:
            candidates += [grid + [final] for grid in list(candidates)]
        accepted_frames = None
        for grid in candidates:
            try:
                accepted_frames = scout.xtc_envelopes(
                    xtc_path, atoms, expected_steps=grid)
                break
            except ValueError:
                pass
        require(accepted_frames is not None, "XTC grid is not a registered variant")
        xtc[name] = accepted_frames
        report = cpu_capture(runner, root, spec, scratch,
                             ["check", "-f", "/smoke/attempt/{}/{}/{}".format(
                                 phase, name, xtc_path.name)],
                             path / "xtc-check.log")
        atom_rows = re.findall(r"^# Atoms\s+(\d+)\s*$", report, re.M)
        last_rows = re.findall(r"^Last frame\s+(\d+) time\s+([0-9.]+)",
                               report, re.M)
        require(atom_rows == [str(atoms)] and len(last_rows) == 1 and
                int(last_rows[0][0]) == len(accepted_frames) - 1 and
                abs(float(last_rows[0][1]) - accepted_frames[-1]["time_ps"]) < 1e-4,
                "GROMACS XTC decode/count mismatch")
    require((not parts if phase == "common" else
             len(parts) == 1 and int(next(iter(parts))) >= 2),
            "post-branch part numbering inconsistent")
    if phase in ("common", "baseline"):
        require(all(not re.search(r"^Replica exchange at step |^Repl\s+ex\s+",
                                  log, re.M) for log in logs),
                "no-exchange phase contains exchange activity")
        exchange = {"rounds": 0, "accepted": 0}
    else:
        exchange = parse_hrex(logs, spec)
    return {"checkpoints": checkpoint, "dhdl": dhdl, "energy": energy,
            "xtc": xtc, "exchange": exchange, "part_numbers": sorted(parts)}


def storage_summary(attempt):
    """Count saved bytes by phase and file type, including a partial attempt."""
    by_phase, by_type = {}, {}
    for path in attempt.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(attempt)
        phase = relative.parts[0] if relative.parts[0] in (
            "common", "branch-inputs", "baseline", "hrex") else "metadata"
        kind = path.suffix or "(no extension)"
        size = path.stat().st_size
        for table, key in ((by_phase, phase), (by_type, kind)):
            row = table.setdefault(key, {"files": 0, "bytes": 0})
            row["files"] += 1
            row["bytes"] += size
    return {"by_phase": by_phase, "by_type": by_type,
            "total_bytes": sum(row["bytes"] for row in by_phase.values())}


def job(root, spec):
    guard(spec)  # Before creating an attempt, touching GPU, or calling scheduler.
    require(os.environ.get("JOB_ID", "").isdigit(), "SGE allocation required")
    started = time.monotonic()
    attempt = root / "attempt"
    attempt.mkdir()  # Never overwrite a failed or completed attempt.
    status = {"technical_status": "failed", "job_id": os.environ["JOB_ID"],
              "production_authorized": False, "accounting": "pending_qacct",
              "failure": None}
    scratch = None
    runner = None
    try:
        base.verify_package(root)
        preflight.source_review(spec)
        hostfile = Path(os.environ["PE_HOSTFILE"]).read_text()
        (attempt / "PE_HOSTFILE").write_text(hostfile)
        base.validate_allocation(os.environ, hostfile, socket.gethostname(), spec)
        base.write_json(attempt / "allocation.json", {key: os.environ.get(key)
            for key in ("JOB_ID", "PE", "NSLOTS", "QUEUE",
                        "CUDA_VISIBLE_DEVICES", "SGE_TASK_ID")})
        core.configure_affinity(attempt, spec)
        quota = subprocess.run(["pquota", spec["scheduler"]["project"]],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, timeout=30)
        (attempt / "quota.log").write_text(quota.stdout)
        require(quota.returncode == 0, "pquota failed")
        core.quota_check(quota.stdout, spec)
        require(shutil.disk_usage(str(root)).free >=
                spec["scheduler"]["minimum_free_bytes_each"] and
                shutil.disk_usage("/scratch").free >=
                spec["scheduler"]["minimum_free_bytes_each"],
                "insufficient persistent/scratch free space")
        scratch = Path(tempfile.mkdtemp(prefix="gmx-c2-branch-{}-".format(
            os.environ["JOB_ID"]), dir="/scratch"))
        base.write_json(attempt / "scratch.json", {"path": str(scratch)})
        runner = MonitoredRunner(attempt, scratch,
            started + spec["scheduler"]["work_deadline_seconds"],
            spec["scheduler"]["storage_stop_bytes_each"],
            spec["scheduler"]["storage_cap_bytes_each"],
            spec["scheduler"]["minimum_free_bytes_each"])
        base.verify_tmp_bind(root, spec, scratch, runner, attempt / "mount.log", gpu=True)
        runner.run(["nvidia-smi", "--query-gpu=index,uuid,name,compute_mode",
                    "--format=csv,noheader"], attempt / "gpus.csv", timeout=20)
        assigned = base.assigned_uuids(os.environ["CUDA_VISIBLE_DEVICES"],
                                       (attempt / "gpus.csv").read_text(), "L40S")
        require(len(assigned) == 1, "exactly one allocated GPU required")
        prepare_common(root, spec, attempt)
        status["phases"] = {}
        status["phases"]["common"] = run_phase(root, spec, attempt, scratch,
                                                runner, "common", assigned[0])
        common_review = validate_phase(root, spec, attempt, scratch, runner,
                                       "common")
        base.write_json(attempt / "common-review.json", common_review)
        hashes = seal_common(root, spec, attempt, scratch, runner)
        prepare_branch_inputs(root, spec, attempt, scratch, runner, hashes)
        for arm in ("baseline", "hrex"):
            base.verify_files(attempt / "common",
                              json.loads((attempt / "common-seal.json").read_text()))
            base.verify_files(attempt / "branch-inputs",
                              json.loads((attempt / "branch-input-seal.json").read_text()))
            prepare_arm_run(root, spec, attempt, arm, hashes)
            status["phases"][arm] = run_phase(root, spec, attempt, scratch,
                                               runner, arm, assigned[0])
            review = validate_phase(root, spec, attempt, scratch, runner, arm)
            base.write_json(attempt / (arm + "-review.json"), review)
        base.verify_files(attempt / "common",
                          json.loads((attempt / "common-seal.json").read_text()))
        base.verify_files(attempt / "branch-inputs",
                          json.loads((attempt / "branch-input-seal.json").read_text()))
        status["technical_status"] = "pass_pending_accounting_and_review"
    except BaseException as exc:
        status["failure"] = str(exc)
        raise
    finally:
        status["wall_seconds"] = time.monotonic() - started
        status["allocated_gpu_hours_observed"] = status["wall_seconds"] / 3600
        if runner is not None:
            status["max_persistent_bytes"] = runner.max_work
            status["max_scratch_bytes"] = runner.max_scratch
        base.write_json(attempt / "storage-summary.json", storage_summary(attempt))
        base.write_json(attempt / "status.json", status)
        base.write_json(attempt / "output-hashes.json", base.inventory(attempt))
        print(json.dumps(status, indent=2, sort_keys=True))
        if scratch is not None:
            print("Private scratch retained: " + str(scratch))


def accounting(root, spec):
    attempt = root / "attempt"
    status = json.loads((attempt / "status.json").read_text())
    require(status.get("technical_status") == "pass_pending_accounting_and_review",
            "technical fixture not complete")
    require(not (attempt / "accounting.json").exists(),
            "accounting already recorded")
    base.verify_files(attempt, json.loads((attempt / "output-hashes.json").read_text()))
    proc = subprocess.run(["qacct", "-j", status["job_id"]],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True, timeout=30)
    (attempt / "qacct.log").write_text(proc.stdout)
    require(proc.returncode == 0, "qacct still pending or failed")
    summary = scout.qacct_summary(proc.stdout, status["job_id"])
    require(summary["wall_seconds"] <= spec["scheduler"]["walltime_seconds"],
            "fixture exceeded selected walltime")
    summary["reviewed"] = True
    summary["scc_su_charge"] = None
    base.write_json(attempt / "accounting.json", summary)
    base.write_json(attempt / "output-hashes-after-accounting.json",
                    base.inventory(attempt))
    print("C2_BRANCH_FIXTURE_ACCOUNTING_REVIEW_PASS job_id={} gpu_hours={:.6f}".format(
        status["job_id"], summary["allocated_gpu_hours"]))


def main():
    root = root_path()
    require(len(sys.argv) >= 2, "command required")
    command = sys.argv[1]
    spec = spec_at(root)
    if command == "verify-package":
        verify_package(root)
        print("C2_BRANCH_FIXTURE_EXECUTION_RELEASE_PACKAGE_VERIFIED; execution_authorized={}".format(
            spec["execution_authorized"]))
    elif command == "review":
        review(root, spec)
    elif command == "permit":
        guard(spec)
        review(root, spec)
        print("C2_BRANCH_FIXTURE_ONE_JOB_SUBMISSION_GUARD_PASS; no job submitted")
    elif command == "job":
        job(root, spec)
    elif command == "rank":
        require(len(sys.argv) == 3, "phase required")
        rank_main(root, spec, sys.argv[2])
    elif command == "probe":
        guard(spec)
        require(len(sys.argv) == 3, "phase required")
        base.write_json(root / "attempt" / sys.argv[2] / "device-map.json",
                        base.cuda_probe())
    elif command == "check-tmp":
        guard(spec)
        require(len(sys.argv) == 3, "token required")
        base.check_tmp_inside(sys.argv[2])
    elif command == "accounting":
        accounting(root, spec)
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    main()
