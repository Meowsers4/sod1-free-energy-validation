"""Self-contained Stage A runner/validator; Python 3.6+ standard library only.

Copied into the transfer package. Preparation never submits; job mode requires
an existing SGE allocation. Optional private MPS is restricted to the separately
specified one-GPU package. No retries, Stage B or protein work is provided.
"""
import ctypes
import hashlib
import json
import math
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
import uuid


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with open(str(path), "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def inventory(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}


def verify_files(root, files):
    for name, digest in files.items():
        path = root / name
        require(not Path(name).is_absolute() and ".." not in Path(name).parts,
                "unsafe manifest path")
        require(path.is_file() and not path.is_symlink(), "missing file: " + name)
        require(sha(path) == digest, "checksum mismatch: " + name)


def verify_package(root):
    entries = [line.split("  ", 1) for line in (root / "SHA256SUMS").read_text().splitlines()]
    require(len({name for _, name in entries}) == len(entries), "duplicate manifest path")
    verify_files(root, {name: digest for digest, name in entries})


def container_env(gpu=False):
    # Prevent host conda/MPI and caller-supplied container overrides from leaking in.
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SINGULARITY", "APPTAINER", "OMPI_", "GMX_", "CUDA_"))}
    for k in ("LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONPATH", "PYTHONHOME"):
        env.pop(k, None)
    values = {"TMPDIR": "/tmp", "OMP_NUM_THREADS": "1", "OMPI_MCA_plm": "isolated",
              "OMPI_MCA_orte_tmpdir_base": "/tmp", "GMX_MAXBACKUP": "-1"}
    if gpu:
        values["CUDA_VISIBLE_DEVICES"] = os.environ["CUDA_VISIBLE_DEVICES"]
        if "CUDA_DEVICE_ORDER" in os.environ:
            values["CUDA_DEVICE_ORDER"] = os.environ["CUDA_DEVICE_ORDER"]
    for k, v in values.items():
        env["SINGULARITYENV_" + k] = v
    return env


def container_command(root, spec, scratch, cwd="/smoke", gpu=False):
    command = ["singularity", "exec", "--cleanenv", "--contain",
               "--no-mount", "bind-paths,hostfs,cwd,tmp",
               "--bind", str(root) + ":/smoke", "--bind", str(scratch) + ":/tmp",
               "--pwd", cwd]
    if gpu:
        command.append("--nv")
        if spec.get("sharing", {}).get("mode") == "private_MPS":
            # MPS UNIX sockets must have the same absolute path on both sides.
            command += ["--bind", str(scratch) + ":" + str(scratch)]
    return command + [spec["image"]["path"]]


def check_preparation_warnings(log):
    """Keep warning rejection, but report the actual warning and its log path."""
    warnings = re.findall(r"^\s*WARNING[^\n]*", Path(log).read_text(), re.M)
    if warnings:
        kind = "GROMACS input" if any(re.match(r"\s*WARNING\s+\d+\b", w) for w in warnings) else "container/runtime or unclassified"
        raise ValueError("{} warning requires review in {}:\n{}".format(
            kind, log, "\n".join(w.strip() for w in warnings)))


def check_tmp_inside(token):
    """Verify that /tmp is the caller's private writable directory, not session tmpfs."""
    scratch = Path("/tmp")
    source = scratch / ".sod1-smoke-mount-token"
    require(source.is_file() and source.read_text() == token,
            "container /tmp does not expose the intended private scratch")
    (scratch / ".sod1-smoke-mount-return").write_text(token)
    print("PRIVATE_TMP_BIND_VERIFIED")


def verify_tmp_bind(root, spec, scratch, runner, log, gpu=False):
    token = uuid.uuid4().hex
    (scratch / ".sod1-smoke-mount-token").write_text(token)
    command = container_command(root, spec, scratch, gpu=gpu)
    runner.run(command + [spec["image"]["python"], "/smoke/runtime.py", "check-tmp", token],
               log, env=container_env(gpu))
    check_preparation_warnings(log)
    returned = scratch / ".sod1-smoke-mount-return"
    require(returned.is_file() and returned.read_text() == token,
            "container /tmp write did not reach private host scratch")


class Runner:
    def __init__(self, root, seconds, max_bytes):
        self.root = root
        self.extra_storage = []
        self.end = time.monotonic() + seconds
        self.max_bytes = max_bytes

    def run(self, args, log, env=None, cwd=None, timeout=None, stdin=None, mps=None):
        """Capture argv and all output; enforce shared deadline and storage stop."""
        end = min(self.end, time.monotonic() + timeout) if timeout else self.end
        require(time.monotonic() < end, "work deadline already reached")
        write_json(Path(str(log) + ".command.json"), args)
        with open(str(log), "w") as output:
            proc = subprocess.Popen(args, cwd=str(cwd or self.root), env=env,
                                    stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            if stdin is not None:
                proc.stdin.write(stdin.encode())
                proc.stdin.close()
            try:
                while proc.poll() is None:
                    if mps is not None:
                        mps.observe()
                    require(time.monotonic() < end, "work deadline reached")
                    size = sum(p.stat().st_size for base in [self.root] + self.extra_storage
                               for p in base.rglob("*") if p.is_file())
                    require(size < self.max_bytes, "storage stop threshold reached")
                    time.sleep(0.05 if mps is not None else 0.2)
                if proc.returncode != 0:
                    tail = "\n".join(Path(log).read_text(errors="replace").splitlines()[-30:])
                    raise ValueError("command failed ({}); see {}:\n{}".format(proc.returncode, log, tail))
            except BaseException:
                if mps is not None:
                    # Quiesce GPU work before any forceful process-group teardown.
                    mps.abort(proc)
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=5)
                raise


def validate_tpr_dump(text, state, spec):
    f = spec["fixture"]
    for key, expected in (("init-lambda-state", state["local_index"]),
                          ("nsteps", f["nsteps"]), ("init-step", 0),
                          ("natoms", f["grid_side"] ** 3),
                          ("n-lambdas", len(spec["states"])), ("calc-lambda-neighbors", -1)):
        match = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*(-?\d+)\s*$", text, re.M)
        require(match and int(match.group(1)) == expected, "TPR mismatch: " + key)
    block = text.split("all-lambdas:", 1)[1]
    match = re.search(r"^\s*fep-lambdas\s*=([^\n]+)", block, re.M)
    actual = [float(x) for x in match.group(1).split()] if match else []
    require(len(actual) == len(spec["states"]) and all(
        abs(a - s["lambda_value"]) < 1e-6 for a, s in zip(actual, spec["states"])),
        "TPR lambda array mismatch")


def prepare(root, spec):
    require(not os.environ.get("JOB_ID"), "prepare outside a GPU allocation")
    verify_package(root)
    require(sha(spec["image"]["path"]) == spec["image"]["sha256"], "SIF hash mismatch")
    work = root / "prepared"
    work.mkdir()  # Never silently replace partial or previously prepared evidence.
    scratch = Path(tempfile.mkdtemp(prefix="gmx-smoke-prepare.", dir="/scratch"))
    write_json(work / "location.json", {"scratch": str(scratch), "host": socket.gethostname()})
    runner = Runner(root, spec["preparation"]["total_timeout_seconds"], spec["scheduler"]["stop_bytes"])
    runner.extra_storage = [scratch]
    try:
        # Check both the exact container Python and a round-trip through the /tmp bind.
        verify_tmp_bind(root, spec, scratch, runner, work / "python-and-mount.log")
        for state in spec["states"]:
            name = state["directory"]
            target = work / name
            target.mkdir()
            base = container_command(root, spec, scratch, "/smoke/prepared/" + name)
            gmx = base + [spec["image"]["gmx"]]
            runner.run(gmx + ["grompp", "-f", "/smoke/inputs/" + name + ".mdp",
                             "-c", "/smoke/inputs/conf.gro", "-p", "/smoke/inputs/topol.top",
                             "-o", "topol.tpr", "-po", "mdout.mdp", "-pp", "processed.top"],
                       target / "grompp.log", env=container_env(),
                       timeout=spec["preparation"]["command_timeout_seconds"])
            check_preparation_warnings(target / "grompp.log")
            runner.run(gmx + ["dump", "-s", "topol.tpr"], target / "tpr.dump",
                       env=container_env(), timeout=spec["preparation"]["command_timeout_seconds"])
            validate_tpr_dump((target / "tpr.dump").read_text(), state, spec)
        write_json(work / "PREPARED.json", {"sif_sha256": spec["image"]["sha256"],
                   "package_manifest_sha256": sha(root / "SHA256SUMS"),
                   "files": inventory(work), "gpu_executed": False})
        print("INPUTS_PREPARED: " + str(work / "PREPARED.json"))
        print("No job submitted. Return this log for package review before qsub.")
    finally:
        # Only this process's fresh temporary directory; no build evidence is removed.
        shutil.rmtree(str(scratch))


def verify_prepared(root, spec):
    record = json.loads((root / "prepared/PREPARED.json").read_text())
    require(record["sif_sha256"] == spec["image"]["sha256"], "prepared SIF mismatch")
    require(record["package_manifest_sha256"] == sha(root / "SHA256SUMS"), "package changed after preparation")
    verify_files(root / "prepared", record["files"])
    for state in spec["states"]:
        rel = state["directory"] + "/topol.tpr"
        require(rel in record["files"], "missing sealed TPR")
        validate_tpr_dump((root / "prepared" / state["directory"] / "tpr.dump").read_text(), state, spec)


def import_prepared(root, spec):
    """Reuse verified exact-SIF TPRs without running grompp again."""
    require(not os.environ.get("JOB_ID"), "import prepared files outside an allocation")
    verify_package(root)
    source = Path(spec["prepared_source"]["path"])
    require(sha(source / "SHA256SUMS") == spec["prepared_source"]["manifest_sha256"], "source manifest mismatch")
    verify_package(source)
    old_spec = json.loads((source / "contract.json").read_text())
    verify_prepared(source, old_spec)
    for key in ("fixture", "states", "image", "pipeline_sha256"):
        require(spec[key] == old_spec[key], "prepared source mismatch: " + key)
    require(inventory(root / "inputs") == inventory(source / "inputs"), "fixture input bytes changed")
    require(sha(spec["image"]["path"]) == spec["image"]["sha256"], "SIF hash mismatch")
    record = json.loads((source / "prepared/PREPARED.json").read_text())
    provenance = {"source": str(source), "source_manifest_sha256": sha(source / "SHA256SUMS"),
                  "source_prepared_record_sha256": sha(source / "prepared/PREPARED.json")}
    target = root / "prepared"
    target.mkdir()  # Preserve partial import on failure; never overwrite.
    for name in record["files"]:
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(source / "prepared" / name), str(dest))
    record["import_provenance"] = provenance
    record["package_manifest_sha256"] = sha(root / "SHA256SUMS")
    write_json(target / "PREPARED.json", record)
    verify_prepared(root, spec)
    print("EXISTING_TPRS_IMPORTED_AND_VERIFIED; no grompp or GPU job run")


def validate_allocation(env, hostfile, hostname, spec):
    s = spec["scheduler"]
    require(env.get("JOB_ID", "").isdigit(), "not in an SGE job")
    require(env.get("PE") == s["pe"] and int(env.get("NSLOTS", "0")) == s["slots"], "wrong PE/slots")
    require(env.get("SGE_TASK_ID", "undefined") in ("undefined", ""), "arrays forbidden")
    rows = [line.split() for line in hostfile.splitlines() if line.strip()]
    require(rows and all(len(row) >= 2 for row in rows), "invalid PE_HOSTFILE")
    require({r[0].split('.')[0] for r in rows} == {hostname.split('.')[0]}, "multi-host or wrong-host allocation")
    require(sum(int(r[1]) for r in rows) == s["slots"], "PE_HOSTFILE slot mismatch")
    cvd = env.get("CUDA_VISIBLE_DEVICES", "").split(",")
    require(len(cvd) == s["gpus"] and len(set(cvd)) == len(cvd) and all(cvd), "wrong assigned GPU count")
    require(not env.get("CUDA_MPS_PIPE_DIRECTORY"), "Stage A must not inherit an MPS service")


def configure_cpu_sharing(root, spec):
    """Limit this job and its children to NSLOTS inherited Linux CPU IDs."""
    if not spec.get("cpu_sharing"):
        return
    count = spec["scheduler"]["slots"]
    require(count == spec["cpu_sharing"]["affinity_cpus"], "CPU affinity/slot mismatch")
    original = sorted(os.sched_getaffinity(0))
    require(len(original) >= count, "inherited CPU affinity smaller than reservation")
    selected = original[:count]
    os.sched_setaffinity(0, set(selected))
    require(set(os.sched_getaffinity(0)) == set(selected), "CPU affinity restriction failed")
    write_json(root / "attempt/cpu-affinity.json", {
        "inherited_cpu_ids": original, "selected_cpu_ids": selected,
        "allocated_slots": count, "mpi_ranks": spec["scheduler"]["ranks"],
        "mode": spec["cpu_sharing"]["mode"]})


def rank_cpu_affinity(root, spec):
    """Reject a rank that escaped the common job CPU affinity mask."""
    if not spec.get("cpu_sharing"):
        return None
    selected = json.loads((root / "attempt/cpu-affinity.json").read_text())["selected_cpu_ids"]
    actual = sorted(os.sched_getaffinity(0))
    require(len(selected) == spec["scheduler"]["slots"] and actual == selected,
            "rank CPU affinity differs from bounded job mask")
    return actual


def mpi_arguments(spec):
    """Report real available slots to MPI, enabling only registered oversubscription."""
    s = spec["scheduler"]
    sharing = spec.get("cpu_sharing")
    slots = s["slots"] if sharing else s["ranks"]
    require(s["ranks"] <= s["slots"] or sharing, "unregistered MPI oversubscription")
    args = [spec["image"]["mpirun"], "--mca", "plm", "isolated",
            "--host", "localhost:" + str(slots), "--np", str(s["ranks"]), "--bind-to", "none"]
    if sharing:
        args += ["--oversubscribe", "--mca", "mpi_yield_when_idle", str(sharing["mpi_yield_when_idle"])]
    return args


def assigned_uuids(cvd, smi, expected_type):
    rows = [[item.strip() for item in line.split(",")] for line in smi.splitlines() if line.strip()]
    selected = []
    for token in cvd.split(","):
        matches = [r for r in rows if len(r) >= 4 and (r[0] == token or r[1] == token)]
        require(len(matches) == 1, "unresolved scheduler GPU token: " + token)
        require(expected_type in matches[0][2], "wrong GPU model")
        selected.append(matches[0][1])
    require(len(set(selected)) == len(selected), "duplicate assigned UUID")
    return selected


def cuda_probe():
    """Enumerate CUDA-visible UUIDs without creating competing GPU contexts."""
    lib = ctypes.CDLL("libcuda.so.1")
    def call(name, *args):
        rc = getattr(lib, name)(*args)
        require(rc == 0, "CUDA {} failed: {}".format(name, rc))
    call("cuInit", 0)
    count = ctypes.c_int()
    call("cuDeviceGetCount", ctypes.byref(count))
    devices = []
    for ordinal in range(count.value):
        device = ctypes.c_int()
        call("cuDeviceGet", ctypes.byref(device), ordinal)
        raw = (ctypes.c_ubyte * 16)()
        call("cuDeviceGetUuid", ctypes.byref(raw), device)
        name = ctypes.create_string_buffer(256)
        call("cuDeviceGetName", name, len(name), device)
        devices.append({"ordinal": ordinal, "uuid": "GPU-" + str(uuid.UUID(bytes=bytes(raw))),
                        "name": name.value.decode()})
    return {"devices": devices, "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES")}


def rank_main(root, spec, phase=None):
    cpu_affinity = rank_cpu_affinity(root, spec)
    rank = int(os.environ["OMPI_COMM_WORLD_RANK"])
    require(int(os.environ["OMPI_COMM_WORLD_SIZE"]) == len(spec["states"]), "wrong MPI world size")
    require(int(os.environ["OMPI_COMM_WORLD_LOCAL_SIZE"]) == len(spec["states"]), "MPI spans hosts")
    mapping = json.loads((root / "attempt/device-map.json").read_text())
    require(os.environ.get("CUDA_VISIBLE_DEVICES") == mapping["CUDA_VISIBLE_DEVICES"], "rank visibility changed")
    chosen = device_for_rank(mapping, rank, spec)
    if spec.get("sharing"):
        mps_record = json.loads((root / "attempt/mps.json").read_text())
        require(os.environ.get("CUDA_MPS_PIPE_DIRECTORY") == mps_record["pipe"], "rank lost private MPS pipe")
    record = {"rank": rank, "pid": os.getpid(), "host": socket.gethostname(),
              "state": spec["states"][rank]["directory"], "gpu": chosen,
              "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"]}
    if cpu_affinity is not None:
        record["cpu_affinity"] = cpu_affinity
    write_json(root / "attempt" / ("rank-{}.json".format(rank)), record)
    f = spec["fixture"]
    args = [spec["image"]["gmx"], "mdrun", "-multidir"] + [s["directory"] for s in spec["states"]]
    args += ["-s", "topol.tpr", "-deffnm", "smoke", "-nb", "gpu", "-pme", "cpu",
             "-bonded", "cpu", "-update", "cpu", "-ntomp", str(spec["scheduler"]["threads"]),
             "-gpu_id", str(chosen["ordinal"]), "-pin", "off", "-dlb", "no", "-notunepme",
             "-replex", str(f["replex"]), "-reseed", str(f["exchange_seed"])]
    if spec.get("restart"):
        from restart import restart_arguments, verify_checkpoint_inputs
        if phase == "resume":
            verify_checkpoint_inputs(root, spec)
        args += restart_arguments(spec, phase)
        record["phase"] = phase
        write_json(root / "attempt" / ("rank-{}.json".format(rank)), record)
    write_json(root / "attempt" / ("rank-{}.argv.json".format(rank)), args)
    os.environ["OMP_NUM_THREADS"] = str(spec["scheduler"]["threads"])
    os.execv(args[0], args)


def device_for_rank(mapping, rank, spec):
    require(0 <= rank < spec["scheduler"]["ranks"], "invalid MPI rank")
    sharing = spec.get("sharing", {}).get("mode") == "private_MPS"
    require(len(mapping["devices"]) == spec["scheduler"]["gpus"], "wrong visible GPU count")
    if sharing:
        require(len(mapping["devices"]) == 1 and mapping["devices"][0]["ordinal"] == 0,
                "MPS requires exactly one visible CUDA device")
    return mapping["devices"][0 if sharing else rank]


def parse_exchange(text, count, interval, nsteps):
    """Reconstruct nearest-neighbor walker permutations, rejecting malformed logs."""
    headers = list(re.finditer(r"^Replica exchange at step (\d+) time [^\n]+$", text, re.M))
    require(headers, "no exchange records")
    steps = [int(m.group(1)) for m in headers]
    # GROMACS does not exchange on the last dynamics step.
    require(steps == list(range(interval, nsteps, interval)), "missing/duplicated exchange rounds")
    walkers = list(range(count))
    history, accepted = [], 0
    for idx, header in enumerate(headers):
        section = text[header.end():headers[idx+1].start() if idx+1 < len(headers) else len(text)]
        lines = re.findall(r"^Repl\s+ex\s+(.+)$", section, re.M)
        require(len(lines) == 1, "missing or duplicate exchange outcome")
        tokens = lines[0].split()
        require([int(t) for t in tokens if t.isdigit()] == list(range(count)), "invalid state order")
        require(all(t.isdigit() or t == "x" for t in tokens), "invalid exchange token")
        swaps = []
        for j, token in enumerate(tokens):
            if token == "x":
                require(0 < j < len(tokens)-1 and tokens[j-1].isdigit() and tokens[j+1].isdigit(), "invalid swap")
                a, b = int(tokens[j-1]), int(tokens[j+1])
                require(b == a+1 and b % 2 == (steps[idx] // interval) % 2, "invalid neighbor parity")
                swaps.append((a, b))
        require(len({v for pair in swaps for v in pair}) == 2*len(swaps), "overlapping swaps")
        for a, b in swaps:
            walkers[a], walkers[b] = walkers[b], walkers[a]
        accepted += len(swaps)
        history.append({"step": steps[idx], "accepted_pairs": swaps, "state_to_walker": walkers[:]})
    require(accepted > 0, "no accepted exchange; incomplete demonstration")
    return history


def validate_dhdl(text, state, spec):
    require("state {}:".format(state["local_index"]) in text, "DHDL state label mismatch")
    legends = re.findall(r'^@\s+s\d+\s+legend "(.+)"$', text, re.M)
    foreign = [float(m.group(1)) for line in legends for m in [re.search(r" to ([0-9.]+)$", line)] if m]
    require(foreign == [s["lambda_value"] for s in spec["states"]], "foreign-energy labels mismatch")
    rows = [[float(v) for v in line.split()] for line in text.splitlines()
            if line.strip() and not line.startswith(("#", "@"))]
    require(rows and all(len(row) == len(legends)+1 for row in rows), "wrong DHDL column count")
    require(all(math.isfinite(v) for row in rows for v in row), "nonfinite DHDL")
    f = spec["fixture"]
    expected = [step*f["dt_ps"] for step in range(0, f["nsteps"]+1, f["output_stride"])]
    require(len(rows) == len(expected) and all(abs(r[0]-t) < 1e-5 for r, t in zip(rows, expected)), "DHDL times incomplete")


def validate_results(root, spec):
    work = root / "attempt"
    mapping = json.loads((work / "device-map.json").read_text())
    common_history = None
    for rank, state in enumerate(spec["states"]):
        p = work / state["directory"]
        record = json.loads((work / ("rank-{}.json".format(rank))).read_text())
        if spec.get("cpu_sharing"):
            selected = json.loads((work / "cpu-affinity.json").read_text())["selected_cpu_ids"]
            require(len(selected) == spec["scheduler"]["slots"] and record.get("cpu_affinity") == selected,
                    "recorded rank CPU affinity mismatch")
        chosen = device_for_rank(mapping, rank, spec)
        require(record["rank"] == rank and record["state"] == state["directory"]
                and record["gpu"] == chosen, "rank/device/state mismatch")
        text = (p / "smoke.log").read_text()
        require("Finished mdrun" in text, "mdrun did not finish")
        require(re.search(r"PP:" + str(chosen["ordinal"]) + r"(?:\D|$)", text), "GROMACS GPU map mismatch")
        require(re.search(r"PP tasks will do[^\n]+GPU", text), "GPU work not recorded")
        history = parse_exchange(text, len(spec["states"]), spec["fixture"]["replex"], spec["fixture"]["nsteps"])
        if common_history is None:
            common_history = history
        require(history == common_history, "inconsistent exchange logs between states")
        validate_dhdl((p / "smoke.xvg").read_text(), state, spec)
        energy = (p / "energy.xvg").read_text()
        require('legend "Potential"' in energy and 'legend "Temperature"' in energy,
                "EDR extraction missing requested terms")
        rows = [[float(x) for x in line.split()] for line in energy.splitlines()
                if line.strip() and not line.startswith(("#", "@"))]
        require(rows and all(len(row) == 3 and all(math.isfinite(v) for v in row) for row in rows),
                "invalid EDR energy/temperature")
        f = spec["fixture"]
        expected_times = [step*f["dt_ps"] for step in range(0, f["nsteps"]+1, f["output_stride"])]
        require(len(rows) == len(expected_times) and all(abs(row[0]-t) < 1e-5 for row, t in zip(rows, expected_times)),
                "EDR output times incomplete")
        checkpoint = (p / "checkpoint.dump").read_text()
        match = re.search(r"^\s*step\s*=\s*(\d+)\s*$", checkpoint, re.M)
        require(match and int(match.group(1)) == spec["fixture"]["nsteps"], "wrong final checkpoint step")
        for filename in ("smoke.edr", "smoke.xtc", "smoke.gro", "smoke.cpt"):
            require((p / filename).stat().st_size > 0, "missing output " + filename)
    return common_history


def check_quota(text, spec):
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == "/projectnb/" + spec["scheduler"]["project"]:
            require(len(fields) == 5, "unexpected pquota format")
            # Conservative decimal GB conversion against byte-valued requirement.
            require((float(fields[1])-float(fields[3]))*10**9 >= spec["scheduler"]["min_free_bytes"], "insufficient project quota")
            require(int(fields[4]) < int(fields[2]), "project file quota exhausted")
            return
    raise ValueError("project quota row missing")


def extract_outputs(root, spec, scratch, runner):
    """Read checkpoints and energies with CPU-only container commands."""
    work = root / "attempt"
    for state in spec["states"]:
        name = state["directory"]
        gmx = container_command(root, spec, scratch, "/smoke/attempt/" + name) + [spec["image"]["gmx"]]
        runner.run(gmx + ["dump", "-cp", "smoke.cpt"], work / name / "checkpoint.dump", env=container_env())
        runner.run(gmx + ["energy", "-f", "smoke.edr", "-o", "energy.xvg"],
                   work / name / "energy-extraction.log", env=container_env(),
                   stdin="Potential\nTemperature\n0\n")


def ladder_summary(history, spec):
    """Require accepted exchange across every link of this weakly perturbed toy."""
    count = len(spec["states"])
    pairs = {(i, i+1): 0 for i in range(count-1)}
    for row in history:
        for pair in row["accepted_pairs"]:
            key = tuple(pair)
            require(key in pairs, "non-neighbor ladder exchange")
            pairs[key] += 1
    require(all(pairs.values()), "larger ladder has an unexercised neighbor link")
    return {"states": count, "exchange_rounds": len(history),
            "accepted_exchanges": sum(pairs.values()),
            "accepted_by_neighbor": [{"pair": list(pair), "count": n}
                                     for pair, n in sorted(pairs.items())],
            "all_neighbor_links_exercised": True,
            "scope": spec["scope"]}


def job(root, spec):
    started = time.monotonic()
    require(os.environ.get("JOB_ID", "").isdigit(), "job mode requires an SGE allocation")
    work = root / "attempt"
    work.mkdir()  # One attempt/package, including failures. Never remove this marker.
    runner = Runner(root, spec["scheduler"]["work_deadline_seconds"], spec["scheduler"]["stop_bytes"])
    scratch = None
    mps = None
    status = {"technical_status": "failed", "stage": spec.get("stage", "R" if spec.get("restart") else "A"), "production_authorized": False,
              "job_id": os.environ["JOB_ID"], "accounting": "pending_qacct", "failure": None}
    try:
        verify_package(root)
        verify_prepared(root, spec)
        require(sha(spec["image"]["path"]) == spec["image"]["sha256"], "SIF hash mismatch")
        hostfile = Path(os.environ["PE_HOSTFILE"]).read_text()
        (work / "PE_HOSTFILE").write_text(hostfile)
        keys = ("JOB_ID", "PE", "NSLOTS", "QUEUE", "SGE_TASK_ID", "CUDA_VISIBLE_DEVICES", "CUDA_DEVICE_ORDER")
        write_json(work / "allocation.json", {k: os.environ.get(k) for k in keys})
        validate_allocation(os.environ, hostfile, socket.gethostname(), spec)
        configure_cpu_sharing(root, spec)
        status["allocated_cpu_slots"] = spec["scheduler"]["slots"]
        status["mpi_ranks"] = spec["scheduler"]["ranks"]
        status["cpu_oversubscribed"] = bool(spec.get("cpu_sharing"))
        runner.run(["pquota", spec["scheduler"]["project"]], work / "quota.log", timeout=30)
        check_quota((work / "quota.log").read_text(), spec)
        for filesystem in (root, Path("/scratch")):
            require(shutil.disk_usage(str(filesystem)).free >= spec["scheduler"]["min_free_bytes"], "insufficient free space")
        scratch = Path(tempfile.mkdtemp(prefix="gmx-smoke-" + status["stage"] + "-" + os.environ["JOB_ID"] + ".", dir="/scratch"))
        runner.extra_storage = [scratch]
        write_json(work / "scratch.json", {"path": str(scratch)})
        verify_tmp_bind(root, spec, scratch, runner, work / "mount.log", gpu=True)
        runner.run(["nvidia-smi", "--query-gpu=index,uuid,name,compute_mode", "--format=csv,noheader"],
                   work / "gpus.csv", timeout=20)
        assigned = assigned_uuids(os.environ["CUDA_VISIBLE_DEVICES"], (work / "gpus.csv").read_text(), spec["scheduler"]["gpu_type"])
        gpu_env = container_env(True)
        if spec.get("sharing", {}).get("mode") == "private_MPS":
            from mps import PrivateMPS
            require(len(assigned) == 1, "MPS requires one assigned GPU")
            mps = PrivateMPS(work, scratch, assigned[0], spec)
            mps.start()
            gpu_env = mps.container_environment(gpu_env)
        base = container_command(root, spec, scratch, "/smoke/attempt", gpu=True)
        runner.run(base + [spec["image"]["python"], "/smoke/runtime.py", "probe"], work / "probe.log", env=gpu_env)
        mapping = json.loads((work / "device-map.json").read_text())
        require(mapping["CUDA_VISIBLE_DEVICES"] == gpu_env["SINGULARITYENV_CUDA_VISIBLE_DEVICES"], "container dropped scheduler device assignment")
        require(len(mapping["devices"]) == len(assigned) and {d["uuid"] for d in mapping["devices"]} == set(assigned), "container UUIDs differ from allocation")
        for state in spec["states"]:
            p = work / state["directory"]
            p.mkdir()
            shutil.copyfile(str(root / "prepared" / state["directory"] / "topol.tpr"), str(p / "topol.tpr"))
        launch = base + mpi_arguments(spec) + [spec["image"]["python"], "/smoke/runtime.py", "rank"]
        if spec.get("restart"):
            from restart import run_phases
            run_phases(root, spec, scratch, runner, launch, gpu_env, mps)
        else:
            runner.run(launch, work / "mpi.log", env=gpu_env, mps=mps)
        if mps is not None:
            mps.close()
            require(mps.observed_all, "All expected simultaneous GROMACS MPS clients not observed; incomplete demonstration")
        # Validation uses CPU reads only, with the remaining walltime reserved for evidence.
        runner.end = started + spec["scheduler"]["walltime_seconds"] - 30
        extract_outputs(root, spec, scratch, runner)
        history = validate_results(root, spec)
        if spec.get("restart"):
            from restart import validate_restart
            validate_restart(root, spec, history)
            status["restart_verified"] = True
        write_json(work / "permutations.json", history)
        if spec.get("stage") == "L":
            write_json(work / "ladder-review.json", ladder_summary(history, spec))
            status["larger_ladder_verified"] = True
        status["technical_status"] = "pass_pending_review_and_accounting"
    except Exception as exc:
        status["failure"] = str(exc)
        raise
    finally:
        if mps is not None:
            try:
                mps.close()
            except Exception as exc:
                status["technical_status"] = "failed"
                status["failure"] = str(status["failure"] or "") + "; MPS cleanup: " + str(exc)
            status["mps_cleanup_confirmed"] = mps.closed
            status["mps_expected_clients"] = spec["scheduler"]["ranks"]
            status["mps_all_clients_observed"] = mps.observed_all
            if spec["scheduler"]["ranks"] == 4:
                status["mps_four_clients_observed"] = mps.observed_all
        status["wall_seconds"] = time.monotonic() - started
        status["allocated_gpu_hours_observed"] = status["wall_seconds"] * spec["scheduler"]["gpus"] / 3600
        write_json(work / "status.json", status)
        write_json(work / "output-hashes.json", inventory(work))
        print(json.dumps(status, indent=2))
        if scratch is not None:
            # Keep scratch on failure for inspection; report it explicitly.
            print("Private scratch retained: " + str(scratch))
        require(status["technical_status"] == "pass_pending_review_and_accounting", status["failure"] or "smoke test incomplete")


def main():
    root = Path(__file__).resolve().parent
    spec = json.loads((root / "contract.json").read_text())
    command = sys.argv[1]
    if command == "prepare":
        prepare(root, spec)
    elif command == "import-prepared":
        import_prepared(root, spec)
    elif command == "job":
        def interrupted(signum, frame):
            raise RuntimeError("job interrupted by signal {}".format(signum))
        signal.signal(signal.SIGTERM, interrupted)
        job(root, spec)
    elif command == "probe":
        write_json(root / "attempt/device-map.json", cuda_probe())
    elif command == "check-tmp":
        check_tmp_inside(sys.argv[2])
    elif command == "rank":
        rank_main(root, spec, sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == "review":
        verify_package(root)
        verify_prepared(root, spec)
        print("PACKAGE_AND_PREPARED_INPUTS_VERIFIED; submission remains a separate decision")
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    main()
