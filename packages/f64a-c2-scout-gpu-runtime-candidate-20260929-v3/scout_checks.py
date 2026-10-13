"""Fail-closed checks for the paired F64A 100-ps timing scout.

Pure Python 3.8+; the selected runner also asks exact-r6 ``gmx check`` to
decompress every XTC. This module only scans the portable XTC frame envelope.
"""

import math
from pathlib import Path
import re
import struct

try:
    import protein_checks
except ImportError:
    from src.analysis import gromacs_protein_runtime_checks as protein_checks


def require(ok, message):
    if not ok:
        raise ValueError(message)


def _read_exact(stream, n):
    data = stream.read(n)
    require(len(data) == n, "truncated XTC frame")
    return data


def gro_identity(path):
    lines = Path(path).read_text().splitlines()
    require(len(lines) >= 3, "GRO truncated")
    try:
        atoms = int(lines[1].strip())
    except ValueError as exc:
        raise ValueError("GRO atom count invalid") from exc
    require(atoms > 0 and len(lines) == atoms + 3, "GRO length mismatch")
    labels = tuple(line[:20] for line in lines[2:2 + atoms])
    require(all(len(label) == 20 for label in labels), "GRO atom label truncated")
    for line in lines[2:2 + atoms]:
        values = line[20:].split()
        require(len(values) >= 3 and
                all(math.isfinite(float(v)) for v in values[:3]),
                "GRO coordinate invalid")
    box = [float(x) for x in lines[-1].split()]
    require(len(box) in (3, 9) and all(math.isfinite(v) for v in box) and
            all(box[i] > 0 for i in range(3)), "GRO box invalid")
    return atoms, labels


def xtc_envelopes(path, expected_atoms, expected_steps=(0, 25000, 50000), dt_ps=0.002):
    """Check XDR frame boundaries, full-system count, time and finite box.

    XTC1995 has a 52-byte main header, 4-byte repeated atom count, 32-byte
    compressed-coordinate header, a 4-byte payload length and padded payload.
    This scanner does not decompress coordinates; exact-r6 ``gmx check`` must
    separately read the entire trajectory without error.
    """
    path = Path(path)
    require(path.is_file() and path.stat().st_size > 0, "XTC absent or empty")
    frames = []
    with path.open("rb") as stream:
        while stream.tell() < path.stat().st_size:
            header = _read_exact(stream, 52)
            magic, atoms, step, t = struct.unpack(">iiif", header[:16])
            require(magic == 1995 and atoms == expected_atoms and atoms > 9,
                    "XTC magic or full-system atom count mismatch")
            box = struct.unpack(">9f", header[16:])
            require(all(math.isfinite(v) for v in box) and
                    all(box[i] > 0 for i in (0, 4, 8)), "XTC box invalid")
            repeated = struct.unpack(">i", _read_exact(stream, 4))[0]
            require(repeated == atoms, "XTC repeated atom count mismatch")
            compressed = _read_exact(stream, 32)
            precision = struct.unpack(">f", compressed[:4])[0]
            require(math.isfinite(precision) and precision > 0,
                    "XTC coordinate precision invalid")
            nbytes = struct.unpack(">i", _read_exact(stream, 4))[0]
            require(nbytes > 0, "XTC coordinate payload length invalid")
            pad = (-nbytes) % 4
            require(nbytes + pad <= path.stat().st_size - stream.tell(),
                    "truncated XTC coordinate payload")
            _read_exact(stream, nbytes + pad)
            frames.append({"step": step, "time_ps": t, "atoms": atoms,
                           "box_nm": list(box), "precision": precision})
            require(len(frames) <= len(expected_steps), "extra XTC frame")
        require(stream.tell() == path.stat().st_size, "XTC trailing bytes")
    require([f["step"] for f in frames] == list(expected_steps),
            "XTC frame-step grid mismatch")
    require(all(abs(f["time_ps"] - f["step"] * dt_ps) < 2e-4 for f in frames),
            "XTC frame-time grid mismatch")
    return frames


def gmx_check_summary(text, atoms, frames=3, last_ps=100.0, stride_ps=50.0):
    """Check the exact-r6 CPU decoder's trajectory inventory.

    The format was confirmed against user-supplied GROMACS 2025.3 output for
    the accepted Stage P protein trajectory; the candidate run is still
    independently checked for its own atom count and three-frame grid.
    """
    atom_rows = re.findall(r"^# Atoms\s+(\d+)\s*$", text, re.M)
    last_rows = re.findall(r"^Last frame\s+(\d+) time\s+([0-9.]+)", text, re.M)
    require(len(atom_rows) == len(last_rows) == 1 and
            int(atom_rows[0]) == atoms and int(last_rows[0][0]) == frames - 1 and
            abs(float(last_rows[0][1]) - last_ps) < 1e-4,
            "gmx check atom count or last frame mismatch")
    for item in ("Step", "Time", "Coords", "Box"):
        rows = re.findall(r"^" + item + r"\s+(\d+)\s+([0-9.]+)\s*$", text, re.M)
        require(len(rows) == 1 and int(rows[0][0]) == frames and
                abs(float(rows[0][1]) - stride_ps) < 1e-4,
                "gmx check {} frame grid mismatch".format(item))
    return {"atoms": atoms, "frames": frames, "last_ps": last_ps,
            "stride_ps": stride_ps}


def xvg_rows(text, expected_times, columns=None, labels=None):
    legends = re.findall(r'^@\s+s\d+\s+legend "(.+)"$', text, re.M)
    if labels is not None:
        require(all(any(label in legend for legend in legends) for label in labels),
                "XVG required legend absent")
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith(("#", "@")):
            continue
        try:
            row = [float(x) for x in line.split()]
        except ValueError as exc:
            raise ValueError("invalid XVG numeric row") from exc
        require(all(math.isfinite(x) for x in row), "nonfinite XVG value")
        if columns is not None:
            require(len(row) == columns, "XVG column count mismatch")
        rows.append(row)
    require(len(rows) == len(expected_times) and
            all(abs(row[0] - t) < 1e-5 for row, t in zip(rows, expected_times)),
            "XVG time grid incomplete or duplicated")
    return legends, rows


def dhdl_summary(text, state, lambdas, nsteps=50000, stride=500, dt_ps=0.002):
    require("state {}:".format(state) in text, "DHDL state label mismatch")
    legends = re.findall(r'^@\s+s\d+\s+legend "(.+)"$', text, re.M)
    foreign = [float(match.group(1)) for line in legends
               for match in [re.search(r" to ([0-9.]+)$", line)] if match]
    require(len(foreign) == len(lambdas) and
            all(abs(a-b) < 1e-5 for a, b in zip(foreign, lambdas)),
            "DHDL foreign-state labels mismatch")
    times = [i * dt_ps for i in range(0, nsteps + 1, stride)]
    xvg_rows(text, times, columns=len(legends) + 1)
    return {"records": len(times), "foreign_states": len(foreign),
            "first_ps": times[0], "last_ps": times[-1]}


def energy_summary(text, nsteps=50000, stride=500, dt_ps=0.002):
    times = [i * dt_ps for i in range(0, nsteps + 1, stride)]
    _, rows = xvg_rows(text, times, columns=3,
                       labels=('Potential', 'Temperature'))
    return {"records": len(rows), "first_ps": rows[0][0],
            "last_ps": rows[-1][0]}


def checkpoint_summary(text, state, nsteps=50000, dt_ps=0.002):
    fields = {}
    for key, pattern in {
            "step": r"^\s*step\s*=\s*(\d+)\s*$",
            "part": r"^\s*simulation part #\s*=\s*(\d+)\s*$",
            "fep_state": r"^\s*fep_state\[0\]\s*=\s*(\d+)\s*$",
            "time_ps": r"^\s*t\s*=\s*(\S+)\s*$"}.items():
        values = re.findall(pattern, text, re.M)
        require(len(values) == 1, "checkpoint field missing/ambiguous: " + key)
        fields[key] = float(values[0]) if key == "time_ps" else int(values[0])
    require(fields["step"] == nsteps and fields["part"] == 1 and
            fields["fep_state"] == state and math.isfinite(fields["time_ps"]) and
            abs(fields["time_ps"] - nsteps * dt_ps) < 1e-5,
            "checkpoint step/time/part/state mismatch")
    return fields


def exchange_summary(logs, arm, states=20, nsteps=50000, interval=500):
    require(len(logs) == states, "missing rank log")
    require(all("Finished mdrun" in log for log in logs), "mdrun incomplete")
    if arm == "baseline":
        require(all(not re.search(r"^Replica exchange at step |^Repl\s+ex\s+",
                                  log, re.M) for log in logs),
                "baseline contains exchange activity")
        return {"arm": arm, "rounds": 0, "attempted_exchanges": 0,
                "accepted_exchanges": 0,
                "final_state_to_walker": list(range(states))}
    require(arm == "hrex", "unknown arm")
    history, summary = protein_checks.compare_exchange_logs(
        logs, states, interval, nsteps)
    return {"arm": arm, **summary,
            "final_state_to_walker": history[-1]["state_to_walker"],
            "history": history}


def qacct_summary(text, job_id, expected_slots=16):
    values = {}
    for line in text.splitlines():
        match = re.match(r"^(\w+)\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2)
    require(values.get("jobnumber") == str(job_id) and
            values.get("project") == "rise-batteries" and
            values.get("qname") == "l40s" and
            values.get("granted_pe") == "omp16" and
            int(values.get("slots", "-1")) == expected_slots and
            values.get("failed") == "0" and values.get("exit_status") == "0",
            "qacct identity or exit mismatch")
    wall = int(values["ru_wallclock"])
    require(0 < wall <= 7200, "qacct allocation exceeded selected walltime")
    return {"job_id": str(job_id), "hostname": values["hostname"],
            "wall_seconds": wall, "allocated_gpu_hours": wall / 3600,
            "allocated_cpu_slot_hours": wall * expected_slots / 3600,
            "failed": 0, "exit_status": 0}
