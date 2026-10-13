"""Guarded one-GPU F64A timing-scout runner (Python 3.8+).

This is copied into a non-submitting candidate. The candidate contract denies
``job`` before an attempt directory, GPU probe or scheduler action is made.
An authorized successor requires a new sealed contract and separate selection.
"""

import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

try:
    import smoke_runtime as base
    import mps
    import scout_checks as checks
except ImportError:
    from src.analysis import gromacs_gpu_smoke_runtime as base
    from src.analysis import gromacs_gpu_mps as mps
    from src.analysis import f64a_c2_scout_gpu_checks as checks


def require(ok, message):
    if not ok:
        raise ValueError(message)


def root_path():
    return Path(__file__).resolve().parent


def spec_at(root):
    return json.loads((Path(root) / "contract.json").read_text())


def work_path(root, arm):
    require(arm in ("baseline", "hrex"), "unknown scout arm")
    return Path(root) / "attempts" / arm


def source_review(root, spec):
    source = Path(spec["prepared_source"]["path"])
    require(source.is_dir() and
            base.sha(source / "SHA256SUMS") ==
            spec["prepared_source"]["prepared_manifest_sha256"],
            "accepted CPU prepared manifest changed")
    require(base.sha(source.parent / "SHA256SUMS") ==
            spec["prepared_source"]["package_manifest_sha256"],
            "accepted CPU import package changed")
    base.verify_package(source)
    rows = (source / "SHA256SUMS").read_text().splitlines()
    require(len(rows) == spec["prepared_source"]["prepared_manifest_entries"],
            "prepared manifest count changed")
    record = json.loads((source / "PREPARED.json").read_text())
    require(record["status"] == "cpu_inputs_prepared_pending_review" and
            record["execution_authorized"] is False and
            record["production_authorized"] is False and
            record["sif_sha256"] == spec["image"]["sha256"] and
            len(record["states"]) == len(spec["states"]),
            "prepared source record changed")
    for i, state in enumerate(spec["states"]):
        name = state["directory"]
        digest = state["tpr_sha256"]
        require(record["states"][i]["state"] == i and
                record["states"][i]["tpr_sha256"] == digest,
                "source TPR record mismatch: " + name)
        for branch in ("common", "arms/baseline", "arms/hrex"):
            path = source / branch / "states" / name / "topol.tpr"
            require(base.sha(path) == digest, "paired TPR changed: " + name)
    import_record = json.loads((source.parent / "IMPORT.json").read_text())
    require(import_record["source_manifest_sha256"] ==
            spec["prepared_source"]["prepared_manifest_sha256"] and
            import_record["execution_authorized"] is False and
            import_record["gpu_executed"] is False,
            "accepted CPU import provenance changed")
    return source


def review(root, spec):
    root = Path(root)
    base.verify_package(root)
    require(spec["execution_authorized"] is False and
            spec["production_authorized"] is False,
            "this candidate cannot authorize GPU execution")
    require(not any((root / name).exists() for name in
                    ("SUBMIT_ON_SCC.sh", "baseline.sge", "hrex.sge")),
            "candidate has a submission script")
    source_review(root, spec)
    require(base.sha(spec["image"]["path"]) == spec["image"]["sha256"],
            "r6 SIF hash mismatch")
    print("C2_SCOUT_GPU_RUNTIME_CANDIDATE_REVIEW_PASS states=20 execution_authorized=False; no job submitted")


def size_bytes(directory):
    directory = Path(directory)
    return sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())


class BoundedRunner:
    def __init__(self, work, scratch, deadline, stop_bytes, cap_bytes):
        self.work, self.scratch = Path(work), Path(scratch)
        self.deadline = deadline
        self.stop_bytes, self.cap_bytes = stop_bytes, cap_bytes
        self.max_work = self.max_scratch = 0

    def limits(self):
        work = size_bytes(self.work)
        scratch = size_bytes(self.scratch)
        self.max_work = max(self.max_work, work)
        self.max_scratch = max(self.max_scratch, scratch)
        require(work < self.stop_bytes and scratch < self.stop_bytes,
                "per-location storage stop threshold reached")
        require(work < self.cap_bytes and scratch < self.cap_bytes,
                "per-location storage cap reached")
        require(time.monotonic() < self.deadline, "work deadline reached")

    def run(self, args, log, env=None, cwd=None, timeout=None, stdin=None, mps_service=None):
        self.limits()
        end = min(self.deadline, time.monotonic() + timeout) if timeout else self.deadline
        base.write_json(Path(str(log) + ".command.json"), args)
        with Path(log).open("w") as output:
            proc = subprocess.Popen(args, cwd=str(cwd or self.work), env=env,
                                    stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            if stdin is not None:
                proc.stdin.write(stdin.encode())
                proc.stdin.close()
            try:
                while proc.poll() is None:
                    if mps_service is not None:
                        mps_service.observe()
                    self.limits()
                    require(time.monotonic() < end, "command deadline reached")
                    time.sleep(0.2)
                self.limits()
                require(proc.returncode == 0,
                        "command failed ({}): {}".format(proc.returncode, log))
            except BaseException:
                if mps_service is not None:
                    # PrivateMPS confirms all clients are terminated before
                    # process-group forceful teardown is permitted.
                    mps_service.abort(proc)
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=5)
                raise

    def capture(self, args, log, env=None, cwd=None, timeout=120):
        self.limits()
        remain = min(timeout, self.deadline - time.monotonic())
        require(remain > 0, "no CPU validation time remaining")
        base.write_json(Path(str(log) + ".command.json"), args)
        result = subprocess.run(args, cwd=str(cwd or self.work), env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=remain)
        require(len(result.stdout) < 32 * 1024 * 1024,
                "validation text unexpectedly large")
        text = result.stdout.decode(errors="replace")
        # Keep a small summary of exact command and outcome; do not archive
        # the multi-MB checkpoint text dump.
        Path(log).write_text("exit={} captured_bytes={}\n".format(
            result.returncode, len(result.stdout)))
        self.limits()
        require(result.returncode == 0, "CPU validation command failed: " + str(log))
        return text


def quota_check(text, spec):
    target = "/project/" + spec["scheduler"]["project"]
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == target:
            require(len(fields) == 5 and
                    (float(fields[1]) - float(fields[3])) * 10**9 >=
                    spec["scheduler"]["minimum_free_bytes_each"] and
                    int(fields[4]) < int(fields[2]),
                    "insufficient /project quota or file count")
            return
    raise ValueError("/project quota row missing")


def configure_affinity(work, spec):
    count = spec["scheduler"]["slots"]
    selected = sorted(os.sched_getaffinity(0))[:count]
    require(len(selected) == count and count == spec["cpu_sharing"]["affinity_cpus"],
            "inherited CPU set smaller than allocation")
    os.sched_setaffinity(0, set(selected))
    require(sorted(os.sched_getaffinity(0)) == selected,
            "CPU affinity restriction failed")
    base.write_json(work / "cpu-affinity.json", {"selected_cpu_ids": selected,
                    "allocated_slots": count, "mpi_ranks": spec["scheduler"]["ranks"]})


def rank_main(root, spec, arm):
    work = work_path(root, arm)
    rank = int(os.environ["OMPI_COMM_WORLD_RANK"])
    require(int(os.environ["OMPI_COMM_WORLD_SIZE"]) == 20 and
            int(os.environ["OMPI_COMM_WORLD_LOCAL_SIZE"]) == 20 and
            0 <= rank < 20, "wrong MPI rank layout")
    selected = json.loads((work / "cpu-affinity.json").read_text())["selected_cpu_ids"]
    require(sorted(os.sched_getaffinity(0)) == selected, "rank escaped CPU mask")
    mapping = json.loads((work / "device-map.json").read_text())
    require(os.environ.get("CUDA_VISIBLE_DEVICES") ==
            mapping["CUDA_VISIBLE_DEVICES"], "rank device visibility changed")
    gpu = base.device_for_rank(mapping, rank, spec)
    mps_record = json.loads((work / "mps.json").read_text())
    require(os.environ.get("CUDA_MPS_PIPE_DIRECTORY") == mps_record["pipe"],
            "rank lost private MPS pipe")
    record = {"rank": rank, "pid": os.getpid(), "host": socket.gethostname(),
              "state": spec["states"][rank]["directory"], "gpu": gpu,
              "cpu_affinity": selected,
              "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"]}
    base.write_json(work / ("rank-{}.json".format(rank)), record)
    f = spec["scout"]
    argv = [spec["image"]["gmx"], "mdrun", "-multidir"] + [
        state["directory"] for state in spec["states"]] + [
        "-s", "topol.tpr", "-deffnm", "scout", "-nb", "gpu", "-pme", "cpu",
        "-bonded", "cpu", "-update", "cpu", "-ntomp", "1", "-gpu_id", "0",
        "-pin", "off", "-dlb", "no", "-notunepme", "-cpt",
        str(f["checkpoint_minutes"]), "-maxh", str(f["maxh_hours"]),
        "-replex", str(f["baseline_replex"] if arm == "baseline" else f["hrex_replex"])]
    if arm == "hrex":
        argv += ["-reseed", str(f["hrex_seed"])]
    base.write_json(work / ("rank-{}.argv.json".format(rank)), argv)
    os.environ["OMP_NUM_THREADS"] = "1"
    os.execv(argv[0], argv)


def preflight_baseline_gate(root, arm):
    if arm == "hrex":
        prior = work_path(root, "baseline")
        status = json.loads((prior / "status.json").read_text())
        accounting = json.loads((prior / "accounting.json").read_text())
        require(status["technical_status"] == "pass_pending_accounting_and_review" and
                status["mps_cleanup_confirmed"] is True and
                accounting["failed"] == 0 and accounting["exit_status"] == 0 and
                accounting["reviewed"] is True,
                "baseline technical/accounting gate not passed")


def validate_outputs(work, spec, arm, runner, scratch):
    f = spec["scout"]
    lambdas = [s["lambda_value"] for s in spec["states"]]
    logs, checkpoints, xtc = [], {}, {}
    energy = {}
    for state in spec["states"]:
        name = state["directory"]
        path = work / name
        require(base.sha(path / "topol.tpr") == state["tpr_sha256"],
                "run TPR changed: " + name)
        for filename in ("scout.log", "scout.xvg", "scout.edr",
                         "scout.xtc", "scout.gro", "scout.cpt"):
            require((path / filename).is_file() and (path / filename).stat().st_size > 0,
                    "missing state output: " + name + "/" + filename)
        log = (path / "scout.log").read_text()
        require(re.search(r"PP:0(?:\D|$)", log) and
                re.search(r"PP tasks will do[^\n]+GPU", log),
                "GROMACS GPU execution not established: " + name)
        logs.append(log)
        checks.dhdl_summary((path / "scout.xvg").read_text(),
                            state["local_index"], lambdas)
        gmx = base.container_command(root_path(), spec, scratch,
                                     "/smoke/attempts/{}/{}".format(arm, name)) + [
                                     spec["image"]["gmx"]]
        runner.run(gmx + ["energy", "-f", "scout.edr", "-o", "energy.xvg"],
                   path / "energy-extraction.log", env=base.container_env(),
                   stdin="Potential\nTemperature\n0\n")
        energy[name] = checks.energy_summary((path / "energy.xvg").read_text())
        dump = runner.capture(gmx + ["dump", "-cp", "scout.cpt"],
                              path / "checkpoint-extraction.log",
                              env=base.container_env())
        checkpoints[name] = checks.checkpoint_summary(dump, state["local_index"])
        # An XTC envelope scan checks frame/atom/box metadata; gmx check
        # independently decompresses every coordinate payload.
        gro = (Path(spec["prepared_source"]["path"]) / "inputs" /
               "states" / name / "start.gro")
        atoms = int(gro.read_text().splitlines()[1].strip())
        xtc[name] = checks.xtc_envelopes(path / "scout.xtc", atoms)
        report = runner.capture(gmx + ["check", "-f", "scout.xtc"],
                                path / "xtc-check.log", env=base.container_env())
        checks.gmx_check_summary(report, atoms)
        (path / "xtc-check-summary.txt").write_text(report[-5000:])
    exchange = checks.exchange_summary(logs, arm)
    return {"checkpoints": checkpoints, "xtc": xtc, "energy": energy,
            "exchange": exchange}


def job(root, spec, arm):
    # The candidate is deliberately inert. The selected successor must have a
    # different sealed contract and an explicit scope/arm authorization.
    require(spec["execution_authorized"] is True and
            spec["production_authorized"] is False and
            arm in spec.get("selected_technical_arms", []),
            "GPU execution is not authorized by this candidate")
    require(os.environ.get("JOB_ID", "").isdigit(), "job requires SGE allocation")
    preflight_baseline_gate(root, arm)
    started = time.monotonic()
    work = work_path(root, arm)
    work.mkdir(parents=True)  # One attempt per arm, even after failure.
    scratch = None
    service = None
    runner = None
    status = {"technical_status": "failed", "arm": arm,
              "job_id": os.environ["JOB_ID"], "production_authorized": False,
              "accounting": "pending_qacct", "failure": None}
    try:
        base.verify_package(root)
        source = source_review(root, spec)
        require(base.sha(spec["image"]["path"]) == spec["image"]["sha256"],
                "r6 SIF hash mismatch")
        hostfile = Path(os.environ["PE_HOSTFILE"]).read_text()
        (work / "PE_HOSTFILE").write_text(hostfile)
        base.validate_allocation(os.environ, hostfile, socket.gethostname(), spec)
        base.write_json(work / "allocation.json", {
            k: os.environ.get(k) for k in
            ("JOB_ID", "PE", "NSLOTS", "QUEUE", "CUDA_VISIBLE_DEVICES", "SGE_TASK_ID")})
        configure_affinity(work, spec)
        quota = subprocess.run(["pquota", spec["scheduler"]["project"]],
                               capture_output=True, text=True, timeout=30)
        (work / "quota.log").write_text(quota.stdout + quota.stderr)
        require(quota.returncode == 0, "pquota failed")
        quota_check(quota.stdout, spec)
        min_free = spec["scheduler"]["minimum_free_bytes_each"]
        require(shutil.disk_usage(root).free >= min_free and
                shutil.disk_usage("/scratch").free >= min_free,
                "insufficient /project or scratch free space")
        scratch = Path(tempfile.mkdtemp(prefix="gmx-c2-{}-{}-".format(
            arm, os.environ["JOB_ID"]), dir="/scratch"))
        base.write_json(work / "scratch.json", {"path": str(scratch)})
        runner = BoundedRunner(work, scratch,
                               started + spec["scheduler"]["work_deadline_seconds"],
                               spec["scheduler"]["storage_stop_bytes_each"],
                               spec["scheduler"]["storage_cap_bytes_each"])
        base.verify_tmp_bind(root, spec, scratch, runner, work / "mount.log", gpu=True)
        runner.run(["nvidia-smi", "--query-gpu=index,uuid,name,compute_mode",
                    "--format=csv,noheader"], work / "gpus.csv", timeout=20)
        assigned = base.assigned_uuids(os.environ["CUDA_VISIBLE_DEVICES"],
                                       (work / "gpus.csv").read_text(),
                                       spec["scheduler"]["gpu_type"])
        require(len(assigned) == 1, "private MPS requires one assigned GPU")
        service = mps.PrivateMPS(work, scratch, assigned[0], spec)
        service.start()
        gpu_env = service.container_environment(base.container_env(True))
        probe = base.container_command(root, spec, scratch,
                                       "/smoke/attempts/" + arm, gpu=True)
        runner.run(probe + [spec["image"]["python"], "/smoke/runtime.py",
                            "probe", arm], work / "probe.log", env=gpu_env)
        mapping = json.loads((work / "device-map.json").read_text())
        require(mapping["CUDA_VISIBLE_DEVICES"] ==
                gpu_env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"] and
                len(mapping["devices"]) == 1 and
                mapping["devices"][0]["uuid"] == assigned[0],
                "container GPU differs from allocation")
        for state in spec["states"]:
            name = state["directory"]
            target = work / name
            target.mkdir()
            shutil.copyfile(source / "arms" / arm / "states" / name / "topol.tpr",
                            target / "topol.tpr")
            require(base.sha(target / "topol.tpr") == state["tpr_sha256"],
                    "run TPR copy changed")
        status["startup_seconds"] = time.monotonic() - started
        launch = probe + base.mpi_arguments(spec) + [
            spec["image"]["python"], "/smoke/runtime.py", "rank", arm]
        dynamics_start = time.monotonic()
        runner.run(launch, work / "mpi.log", env=gpu_env, mps_service=service)
        status["dynamics_seconds"] = time.monotonic() - dynamics_start
        service.close()
        require(service.observed_all, "20 simultaneous MPS clients not observed")
        runner.deadline = started + spec["scheduler"]["walltime_seconds"] - 30
        result = validate_outputs(work, spec, arm, runner, scratch)
        base.write_json(work / "output-review.json", result)
        status["technical_status"] = "pass_pending_accounting_and_review"
    except BaseException as exc:
        status["failure"] = str(exc)
        raise
    finally:
        if service is not None:
            try:
                service.close()
            except Exception as exc:
                status["technical_status"] = "failed"
                status["failure"] = (status["failure"] or "") + "; MPS cleanup: " + str(exc)
            status["mps_cleanup_confirmed"] = service.closed
            status["mps_all_clients_observed"] = service.observed_all
            status["mps_expected_clients"] = 20
        status["wall_seconds"] = time.monotonic() - started
        status["allocated_gpu_hours_observed"] = status["wall_seconds"] / 3600
        if runner is not None:
            status["max_persistent_bytes"] = runner.max_work
            status["max_scratch_bytes"] = runner.max_scratch
        base.write_json(work / "status.json", status)
        base.write_json(work / "output-hashes.json", base.inventory(work))
        print(json.dumps(status, indent=2, sort_keys=True))
        if scratch is not None:
            print("Private scratch retained: " + str(scratch))
        require(status["technical_status"] == "pass_pending_accounting_and_review" and
                status.get("mps_cleanup_confirmed") is True,
                status["failure"] or "scout incomplete")


def accounting_review(root, arm):
    work = work_path(root, arm)
    status = json.loads((work / "status.json").read_text())
    require(status["technical_status"] == "pass_pending_accounting_and_review",
            "technical result incomplete")
    require(not (work / "accounting.json").exists(), "accounting already recorded")
    job_id = status["job_id"]
    proc = subprocess.run(["qacct", "-j", job_id], capture_output=True,
                          text=True, timeout=30)
    (work / "qacct.log").write_text(proc.stdout + proc.stderr)
    require(proc.returncode == 0, "qacct missing or failed")
    summary = checks.qacct_summary(proc.stdout, job_id)
    summary["reviewed"] = True
    summary["scc_su_charge"] = None  # qacct does not report the project SU tariff.
    base.write_json(work / "accounting.json", summary)
    base.write_json(work / "output-hashes-after-accounting.json", base.inventory(work))
    print("C2_SCOUT_{}_ACCOUNTING_REVIEW_PASS job_id={} gpu_hours={:.6f}".format(
        arm.upper(), job_id, summary["allocated_gpu_hours"]))


def main():
    root = root_path()
    require(len(sys.argv) >= 2, "command required")
    command = sys.argv[1]
    spec = spec_at(root)
    if command == "review":
        review(root, spec)
    elif command == "job":
        require(len(sys.argv) == 3, "arm required")
        job(root, spec, sys.argv[2])
    elif command == "rank":
        require(len(sys.argv) == 3, "arm required")
        rank_main(root, spec, sys.argv[2])
    elif command == "probe":
        require(len(sys.argv) == 3, "arm required")
        base.write_json(work_path(root, sys.argv[2]) / "device-map.json",
                        base.cuda_probe())
    elif command == "check-tmp":
        base.check_tmp_inside(sys.argv[2])
    elif command == "accounting":
        require(len(sys.argv) == 3, "arm required")
        accounting_review(root, sys.argv[2])
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    main()
