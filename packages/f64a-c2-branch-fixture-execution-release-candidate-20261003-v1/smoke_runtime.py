"""Reviewed helper-only subset of the accepted one-GPU runtime.

No job, rank, preparation, main, or submission entry point is included.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
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



def device_for_rank(mapping, rank, spec):
    require(0 <= rank < spec["scheduler"]["ranks"], "invalid MPI rank")
    sharing = spec.get("sharing", {}).get("mode") == "private_MPS"
    require(len(mapping["devices"]) == spec["scheduler"]["gpus"], "wrong visible GPU count")
    if sharing:
        require(len(mapping["devices"]) == 1 and mapping["devices"][0]["ordinal"] == 0,
                "MPS requires exactly one visible CUDA device")
    return mapping["devices"][0 if sharing else rank]
