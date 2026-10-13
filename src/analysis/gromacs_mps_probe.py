"""Bounded, job-private MPS diagnostic. Runtime uses Python 3.6 stdlib in r6 SIF."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess as sp
import sys
import tempfile
import time
import uuid


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with open(str(path), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_env(source):
    """Remove inherited container overrides and CUDA/MPS selection."""
    prefixes = ("SINGULARITY", "APPTAINER", "CUDA_", "OMPI_", "GMX_")
    return {k: v for k, v in source.items()
            if not k.startswith(prefixes) and k not in
            ("LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH", "PYTHONHOME")}


def assigned_device(value):
    """Reject multi-device or ambiguous scheduler assignments."""
    require(bool(re.fullmatch(r"(?:[0-9]+|GPU-[0-9a-fA-F-]+)", value)),
            "Expected exactly one scheduler-assigned GPU")
    return value


def run(args, env=None, text=None, timeout=15):
    result = sp.run(args, env=env, input=text, stdout=sp.PIPE, stderr=sp.STDOUT,
                    universal_newlines=True, timeout=timeout)
    print("COMMAND", json.dumps(args), "\n" + result.stdout, flush=True)
    require(result.returncode == 0, "Command failed: " + str(args))
    return result.stdout


def numbers(text):
    """Accept only the documented one-PID-per-line control response."""
    values = text.split()
    require(all(x.isdigit() for x in values), "Unexpected MPS control response")
    return {int(x) for x in values}


def client(root, scratch, expected, index):
    """Hold a synchronized CUDA context until host releases all four clients."""
    spec = json.loads((root / "contract.json").read_text())
    lib = C.CDLL("libcuda.so.1")

    def call(name, types, *args):
        fn = getattr(lib, name)
        fn.argtypes, fn.restype = types, C.c_int
        code = fn(*args)
        require(code == 0, "{} returned CUDA error {}".format(name, code))

    call("cuInit", [C.c_uint], 0)
    count = C.c_int()
    call("cuDeviceGetCount", [C.POINTER(C.c_int)], C.byref(count))
    require(count.value == 1, "Client must see exactly the allocated GPU")
    device = C.c_int()
    call("cuDeviceGet", [C.POINTER(C.c_int), C.c_int], C.byref(device), 0)
    raw = (C.c_ubyte * 16)()
    call("cuDeviceGetUuid", [C.c_void_p, C.c_int], C.byref(raw), device)
    found = "GPU-" + str(uuid.UUID(bytes=bytes(raw)))
    require(found == expected, "CUDA UUID does not match scheduler assignment")
    ctx, ptr = C.c_void_p(), C.c_uint64()
    try:
        call("cuCtxCreate_v2", [C.POINTER(C.c_void_p), C.c_uint, C.c_int],
             C.byref(ctx), 0, device)
        size = spec["bytes_per_client"]
        call("cuMemAlloc_v2", [C.POINTER(C.c_uint64), C.c_size_t], C.byref(ptr), size)
        call("cuMemsetD8_v2", [C.c_uint64, C.c_ubyte, C.c_size_t], ptr, index + 1, size)
        data = (C.c_ubyte * size)()
        call("cuMemcpyDtoH_v2", [C.c_void_p, C.c_uint64, C.c_size_t], data, ptr, size)
        call("cuCtxSynchronize", [])
        require(all(x == index + 1 for x in data), "Device memory round trip failed")
        record = {"pid": os.getpid(), "uuid": found, "bytes_verified": size}
        ready = scratch / ("ready-{}.json".format(index))
        temporary = ready.with_suffix(".tmp")
        temporary.write_text(json.dumps(record))
        temporary.rename(ready)
        deadline = time.monotonic() + spec["client_hold_seconds"]
        while not (scratch / "release").exists():
            require(time.monotonic() < deadline, "Host release timed out")
            time.sleep(0.1)
    finally:
        if ctx.value:
            call("cuCtxSynchronize", [])
            if ptr.value:
                call("cuMemFree_v2", [C.c_uint64], ptr)
            call("cuCtxDestroy_v2", [C.c_void_p], ctx)
    print("CLIENT_PASS", json.dumps(record), flush=True)


def verify(root):
    for line in (root / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        require(sha(root / name) == digest, "Package checksum mismatch: " + name)


def host(root):
    """Run once inside the explicit one-GPU/four-slot scheduler allocation."""
    verify(root)
    spec = json.loads((root / "contract.json").read_text())
    require(os.environ.get("JOB_ID", "").isdigit(), "Not in a scheduler allocation")
    require(os.environ.get("NSLOTS") == "4" and os.environ.get("PE") == "omp",
            "Requires omp/4 allocation")
    hosts = Path(os.environ["PE_HOSTFILE"]).read_text().splitlines()
    require(len(hosts) == 1 and hosts[0].split()[1] == "4", "Requires one host/four slots")
    require(os.environ.get("QUEUE", "").split("@")[0] == "l40s", "Requires l40s queue")
    require(not os.environ.get("CUDA_MPS_PIPE_DIRECTORY"), "Existing MPS environment; stop for review")
    selection = assigned_device(os.environ.get("CUDA_VISIBLE_DEVICES", ""))
    env = clean_env(os.environ)
    env["TMPDIR"] = "/tmp"
    info = run(["nvidia-smi", "-i", selection,
                "--query-gpu=name,uuid,compute_mode", "--format=csv,noheader"], env).strip().split(",")
    require(len(info) == 3 and info[0].strip() == "NVIDIA L40S"
            and info[2].strip() == "Exclusive_Process", "Unexpected GPU/model/mode")
    gpu = info[1].strip()
    require(re.fullmatch(r"GPU-[0-9a-f-]{36}", gpu), "Invalid GPU UUID")
    active = run(["nvidia-smi", "-i", gpu, "--query-compute-apps=pid", "--format=csv,noheader"], env)
    require(not active.strip(), "Assigned GPU already has compute processes; stop")
    processes = run(["ps", "-eo", "args="], env)
    require(not any(re.match(r"(?:\S*/)?nvidia-cuda-mps-(?:control|server)(?:\s|$)", x.strip())
                    for x in processes.splitlines()), "Existing MPS service on node; stop for review")
    require(sha(spec["sif"]) == spec["sif_sha256"], "SIF checksum mismatch")
    evidence = root / "attempt"
    evidence.mkdir(mode=0o700)  # one attempt; never overwrite or automatically retry
    scratch = Path(tempfile.mkdtemp(prefix="mps-{}-".format(os.environ["JOB_ID"]), dir="/scratch"))
    for name in ("pipe", "log", "tmp"):
        (scratch / name).mkdir(mode=0o700)
    (evidence / "allocation.json").write_text(json.dumps({
        "job_id": os.environ["JOB_ID"], "host": socket.gethostname(),
        "gpu": gpu, "scratch": str(scratch), "spec": spec}, indent=2))
    print("Evidence:", evidence, "Scratch:", scratch, flush=True)
    env.update(CUDA_VISIBLE_DEVICES=gpu, CUDA_MPS_PIPE_DIRECTORY=str(scratch / "pipe"),
               CUDA_MPS_LOG_DIRECTORY=str(scratch / "log"))
    control = shutil.which("nvidia-cuda-mps-control", path=env["PATH"])
    require(control, "MPS executable missing")
    children, streams = [], []
    daemon_started = False
    passed = False

    def ctl(command):
        return run([control], env, command + "\n")

    def interrupted(signum, frame):
        raise RuntimeError("Interrupted by signal {}".format(signum))

    previous_handlers = {sig: signal.signal(sig, interrupted)
                         for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        # Mark before launch so a partially successful start still gets cleanup.
        daemon_started = True
        run([control, "-d"], env)
        ctl("get_server_list")
        container_env = clean_env(env)
        # UUIDs avoid MPS ordinal remapping and restrict fallback visibility too.
        for key, value in {"CUDA_VISIBLE_DEVICES": gpu,
                           "CUDA_MPS_PIPE_DIRECTORY": str(scratch / "pipe"),
                           "CUDA_MPS_LOG_DIRECTORY": str(scratch / "log"),
                           "TMPDIR": "/tmp"}.items():
            container_env["SINGULARITYENV_" + key] = value
        for index in range(spec["clients"]):
            output = open(str(evidence / ("client-{}.log".format(index))), "w")
            streams.append(output)
            command = ["singularity", "exec", "--nv", "--cleanenv", "--contain",
                       "--no-mount", "bind-paths,hostfs,cwd,tmp",
                       "--bind", str(root) + ":/probe:ro", "--bind", str(scratch) + ":" + str(scratch),
                       "--bind", str(scratch / "tmp") + ":/tmp", "--pwd", "/",
                       spec["sif"], "/usr/libexec/platform-python", "/probe/probe.py",
                       "client", str(scratch), gpu, str(index)]
            children.append(sp.Popen(command, env=container_env, stdout=output, stderr=sp.STDOUT))
        deadline = time.monotonic() + spec["ready_timeout_seconds"]
        while len(list(scratch.glob("ready-*.json"))) != spec["clients"]:
            require(all(p.poll() is None for p in children), "A CUDA client failed; inspect client logs")
            require(time.monotonic() < deadline, "CUDA client startup timed out")
            time.sleep(0.2)
        records = [json.loads(p.read_text()) for p in sorted(scratch.glob("ready-*.json"))]
        servers = numbers(ctl("get_server_list"))
        require(len(servers) == 1, "Expected exactly one private MPS server")
        clients = numbers(ctl("get_client_list {}".format(next(iter(servers)))))
        require(len(clients) == spec["clients"] and clients == {r["pid"] for r in records},
                "Four live CUDA clients were not all attached to our MPS server")
        require(all(p.poll() is None for p in children), "A client exited before overlap check")
        (evidence / "overlap.json").write_text(json.dumps({"servers": sorted(servers), "clients": records}, indent=2))
        passed = True
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        (scratch / "release").touch()
        cleanup_ok = True
        wait_deadline = time.monotonic() + 105
        for process in children:
            try:
                process.wait(timeout=max(0.1, wait_deadline - time.monotonic()))
                passed = passed and process.returncode == 0
            except sp.TimeoutExpired:
                cleanup_ok = False
        # Never abruptly kill CUDA clients or shut down a server with live clients.
        if daemon_started and cleanup_ok:
            try:
                ctl("quit")
                pid_file = scratch / "pipe" / "nvidia-cuda-mps-control.pid"
                deadline = time.monotonic() + 10
                while pid_file.exists() and time.monotonic() < deadline:
                    time.sleep(0.1)
                cleanup_ok = not pid_file.exists()
            except Exception as exc:
                cleanup_ok = False
                print("MPS cleanup failed:", exc, flush=True)
        for stream in streams:
            stream.close()
        shutil.copytree(str(scratch / "log"), str(evidence / "mps-logs"))
        (evidence / "result.json").write_text(json.dumps({
            "sharing_passed": passed and cleanup_ok, "cleanup_confirmed": cleanup_ok,
            "gpu_uuid": gpu, "mpi_tested": False, "dynamics_tested": False}, indent=2))
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        require(cleanup_ok, "Cleanup unconfirmed; retain allocation/scratch and report log")
    require(passed, "CUDA sharing check failed; inspect retained evidence")
    print("FOUR_CUDA_CLIENTS_SHARED_ONE_GPU; MPS_CLEANUP_CONFIRMED", flush=True)


def package(destination):
    """Create an immutable transfer package; never submit or use a GPU."""
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, str(destination / "probe.py"))
    shutil.copyfile("docs/gromacs_mps_probe_v1.json", str(destination / "contract.json"))
    shutil.copyfile("docs/gromacs_mps_probe.md", str(destination / "README.md"))
    launch = '''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
test ! -e attempt || { echo 'Existing attempt: stop for review'; exit 1; }
exec /usr/libexec/platform-python -u probe.py host
'''
    (destination / "RUN_ON_COMPUTE.sh").write_text(launch)
    rows = [sha(p) + "  " + p.name for p in sorted(destination.iterdir())]
    (destination / "SHA256SUMS").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1]
    root = Path(__file__).resolve().parent
    if mode == "package":
        package(Path(sys.argv[2]))
    elif mode == "host":
        host(root)
    elif mode == "client":
        client(root, Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    else:
        raise ValueError("Unknown mode")
