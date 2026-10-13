"""Bounded runner, quota and affinity helpers only; no job entry point."""
import os
from pathlib import Path
import signal
import shutil
import subprocess
import tempfile
import time
import smoke_runtime as base

def require(ok, message):
    if not ok:
        raise ValueError(message)


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
        with tempfile.NamedTemporaryFile(prefix="capture-", dir=self.scratch,
                                         delete=False) as stream:
            temporary = Path(stream.name)
        command_record = Path(str(temporary) + ".command.json")
        try:
            # The temporary output is counted against scratch during the
            # command, then discarded after compact metadata extraction.
            self.run(args, temporary, env=env, cwd=cwd, timeout=timeout)
            require(temporary.stat().st_size < 32 * 1024 * 1024,
                    "validation text unexpectedly large")
            text = temporary.read_text(errors="replace")
            base.write_json(Path(str(log) + ".command.json"), args)
            Path(log).write_text("exit=0 captured_bytes={}\n".format(
                temporary.stat().st_size))
            return text
        finally:
            for path in (temporary, command_record):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass



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
