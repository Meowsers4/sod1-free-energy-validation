"""Job-private MPS lifecycle for the bounded one-GPU smoke package (Python 3.6+)."""
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pid_set(text):
    values = text.split()
    require(all(v.isdigit() and int(v) > 0 for v in values), "Unrecognized MPS PID response")
    return {int(v) for v in values}


class PrivateMPS:
    """Own only this job's pipe; never attach to or control another service."""

    def __init__(self, work, scratch, gpu, spec):
        self.work, self.scratch, self.gpu, self.spec = work, scratch, gpu, spec
        self.pipe, self.logs = scratch / "mps-pipe", scratch / "mps-log"
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("CUDA_", "SINGULARITY", "APPTAINER", "OMPI_", "GMX_"))
                    and k not in ("LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONPATH", "PYTHONHOME")}
        self.env.update(CUDA_VISIBLE_DEVICES=gpu, CUDA_MPS_PIPE_DIRECTORY=str(self.pipe),
                        CUDA_MPS_LOG_DIRECTORY=str(self.logs), TMPDIR="/tmp")
        self.control = shutil.which("nvidia-cuda-mps-control", path=self.env["PATH"])
        self.started = self.closed = self.observed_all = False

    def command(self, args, text=None):
        result = subprocess.run(args, env=self.env, input=text, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True,
                                timeout=self.spec["sharing"]["control_timeout_seconds"])
        with (self.work / "mps-control.log").open("a") as stream:
            stream.write(json.dumps({"argv": args, "stdin": text, "exit": result.returncode}) + "\n" + result.stdout + "\n")
        require(result.returncode == 0, "MPS command failed; see mps-control.log")
        return result.stdout

    def ctl(self, command):
        require(self.started and not self.closed, "MPS service is not owned/live")
        return self.command([self.control], command + "\n")

    def start(self):
        require(self.control, "MPS control executable missing")
        require(re.fullmatch(r"GPU-[0-9a-f-]{36}", self.gpu), "Invalid assigned GPU UUID")
        info = self.command(["nvidia-smi", "-i", self.gpu,
                             "--query-gpu=uuid,name,compute_mode", "--format=csv,noheader"])
        fields = [x.strip() for x in info.strip().split(",")]
        require(fields == [self.gpu, "NVIDIA L40S", "Exclusive_Process"], "Unexpected assigned GPU/mode")
        active = self.command(["nvidia-smi", "-i", self.gpu,
                               "--query-compute-apps=pid", "--format=csv,noheader"])
        require(not active.strip(), "Assigned GPU already has a compute process")
        processes = self.command(["ps", "-eo", "args="])
        require(not any(re.match(r"(?:\S*/)?nvidia-cuda-mps-(?:control|server)(?:\s|$)", x.strip())
                        for x in processes.splitlines()), "Existing MPS service; stop for review")
        self.pipe.mkdir(mode=0o700)
        self.logs.mkdir(mode=0o700)
        (self.work / "mps.json").write_text(json.dumps({
            "gpu_uuid": self.gpu, "pipe": str(self.pipe), "logs": str(self.logs),
            "uid": os.getuid()}, indent=2))
        self.started = True  # Includes partial startup failures in cleanup.
        self.command([self.control, "-d"])
        self.ctl("get_server_list")

    def container_environment(self, base):
        env = dict(base)
        for key in ("CUDA_VISIBLE_DEVICES", "CUDA_MPS_PIPE_DIRECTORY", "CUDA_MPS_LOG_DIRECTORY"):
            env["SINGULARITYENV_" + key] = self.env[key]
        env.pop("SINGULARITYENV_CUDA_DEVICE_ORDER", None)
        return env

    def clients(self):
        result = {}
        for server in pid_set(self.ctl("get_server_list")):
            result[server] = pid_set(self.ctl("get_client_list {}".format(server)))
        require(len(result) <= 1, "Unexpected multiple servers in private MPS service")
        return result

    def ranks(self):
        try:
            records = [json.loads((self.work / ("rank-{}.json".format(i))).read_text())
                       for i in range(self.spec["scheduler"]["ranks"])]
        except (FileNotFoundError, ValueError):
            return set()  # Rank startup may still be writing its record.
        require(all(r["rank"] == i and r["gpu"]["uuid"] == self.gpu for i, r in enumerate(records)),
                "Rank record mismatch during MPS observation")
        pids = {r["pid"] for r in records}
        require(len(pids) == self.spec["scheduler"]["ranks"] and all(p > 0 for p in pids), "Invalid rank PIDs")
        return pids

    def observe(self):
        if self.observed_all:
            return
        ranks = self.ranks()
        if not ranks:
            return
        clients = self.clients()
        if len(clients) == 1 and next(iter(clients.values())) == ranks:
            self.observed_all = True
            (self.work / "mps-overlap.json").write_text(json.dumps({
                "gpu_uuid": self.gpu, "servers": {str(k): sorted(v) for k, v in clients.items()},
                "rank_pids": sorted(ranks)}, indent=2))

    def abort(self, process):
        """Ask ranks to finish; cancel outstanding MPS work before forced teardown."""
        for pid in self.ranks():
            try:
                os.kill(pid, signal.SIGTERM)  # GROMACS catches this and checkpoints.
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + self.spec["sharing"]["graceful_stop_seconds"]
        while process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        clients = self.clients()
        for server, pids in clients.items():
            # This is our unique 0700 pipe. Never operate on a shared/global service.
            for pid in sorted(pids):
                response = self.ctl("terminate_client {} {}".format(server, pid))
                require(response.strip() == "0", "MPS did not confirm CUDA_SUCCESS; forced teardown forbidden")
        (self.work / "mps-abort.json").write_text(json.dumps({
            "terminated_gpu_clients": {str(k): sorted(v) for k, v in clients.items()},
            "forced_process_teardown_permitted": True}, indent=2))
        # If any control operation failed, this method raised and Runner must NOT kill.

    def close(self):
        if self.closed:
            return
        if not self.started:
            self.closed = True  # Nothing was started by this object.
            return
        try:
            deadline = time.monotonic() + self.spec["sharing"]["shutdown_timeout_seconds"]
            while True:
                require(time.monotonic() < deadline, "MPS clients still live; cleanup unconfirmed")
                if not any(self.clients().values()):
                    break
                time.sleep(0.2)
            self.ctl("quit")
            pid_file = self.pipe / "nvidia-cuda-mps-control.pid"
            deadline = time.monotonic() + self.spec["sharing"]["shutdown_timeout_seconds"]
            while pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.1)
            require(not pid_file.exists(), "MPS control PID file remains; cleanup unconfirmed")
            self.closed = True
        finally:
            # Preserve logs even on failed shutdown; do not erase diagnostic scratch.
            if self.logs.exists():
                target = self.work / "mps-logs"
                target.mkdir(exist_ok=True)
                for path in self.logs.iterdir():
                    if path.is_file():
                        shutil.copyfile(str(path), str(target / path.name))
