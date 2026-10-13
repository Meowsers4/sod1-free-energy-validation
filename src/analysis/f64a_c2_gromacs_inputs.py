"""Read-only, CPU-only admission of sealed GROMACS dH/dlambda input files.

The foreign-state columns are GROMACS energy differences in kJ/mol, not
dimensionless MBAR inputs. This module does not fit or authorize simulations.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
import json
from math import isfinite
from pathlib import Path, PurePosixPath
import re
from typing import Mapping

from src.analysis.f64a_c2_analysis_core import (
    RetainedBlocks, StateReducedPotentials, split_retained_grid,
)


_FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"
_SUBTITLE = re.compile(
    rf'^@\s+subtitle "T = ({_FLOAT}) \(K\).*?state (\d+): '
    rf'fep-lambda = ({_FLOAT})"$', re.M,
)
_LEGEND = re.compile(r'^@\s+s(\d+)\s+legend "(.+)"$', re.M)
_FOREIGN = re.compile(rf" to ({_FLOAT})$")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_GAS_CONSTANT_KJ_MOL_K = 0.00831446261815324


@dataclass(frozen=True)
class ParsedDhdl:
    sampled_state: int
    temperature_K: float
    lambda_values: tuple[float, ...]
    times_ps: tuple[float, ...]
    foreign_dh_kj_mol: tuple[tuple[float, ...], ...]
    blocks: RetainedBlocks


def relative_reduced_potentials(parsed: ParsedDhdl) -> StateReducedPotentials:
    """Convert same-temperature foreign Hamiltonian differences to kT units.

    Every row is centered on its sampled state. MBAR is invariant to a
    per-configuration constant shared across all evaluated states, so total
    energy and pV are unnecessary for this same-temperature contrast.
    An independent alchemlyb comparison is still required before protein use.
    """
    beta = 1.0 / (_GAS_CONSTANT_KJ_MOL_K * parsed.temperature_K)
    rows = tuple(tuple(value * beta for value in row)
                 for row in parsed.foreign_dh_kj_mol)
    if not all(isfinite(value) for row in rows for value in row):
        raise ValueError("reduced-potential conversion overflows")
    return StateReducedPotentials(
        times_ps=parsed.times_ps, lambda_values=parsed.lambda_values,
        rows=rows,
    )


def compare_with_alchemlyb(
    xvg: Path, *, parsed: ParsedDhdl, origin_ps: float,
    time_tolerance_ps: float, lambda_tolerance: float,
    reduced_tolerance: float, relative_tolerance: float = 0.0,
) -> dict[str, float | int | str]:
    """Compare centered kT rows against alchemlyb's independent XVG parser.

    Requires an environment with alchemlyb. This check is deliberately
    separate from the standard-library input-admission path.
    """
    import numpy as np
    from alchemlyb.parsing.gmx import extract_u_nk

    if (not all(isfinite(x) for x in
                (origin_ps, time_tolerance_ps, lambda_tolerance,
                 reduced_tolerance, relative_tolerance))
            or min(time_tolerance_ps, lambda_tolerance, reduced_tolerance,
                   relative_tolerance) < 0):
        raise ValueError("invalid parser-comparison tolerances")
    reference = extract_u_nk(str(xvg), T=parsed.temperature_K, filter=False)
    observed = np.asarray(reference.values, dtype=float)
    ours = np.asarray(relative_reduced_potentials(parsed).rows, dtype=float)
    n_rows, n_states = ours.shape
    if observed.shape != (n_rows, n_states) or not np.isfinite(observed).all():
        raise ValueError("independent parser produced wrong energy shape")
    try:
        reference_labels = tuple(float(column[0] if isinstance(column, tuple)
                                       and len(column) == 1 else column)
                                 for column in reference.columns)
    except (TypeError, ValueError) as exc:
        raise ValueError("independent parser lambda labels are ambiguous") from exc
    if (len(reference_labels) != n_states
            or any(abs(a - b) > lambda_tolerance for a, b in
                   zip(reference_labels, parsed.lambda_values))):
        raise ValueError("independent parser lambda labels differ")
    reference_times = np.asarray(reference.index.get_level_values(0), dtype=float)
    expected_times = np.asarray(parsed.times_ps) + origin_ps
    if (reference_times.shape != (n_rows,)
            or not np.isfinite(reference_times).all()
            or np.max(np.abs(reference_times - expected_times)) > time_tolerance_ps):
        raise ValueError("independent parser time grid differs")
    # GROMACS may include a configuration-wise total-energy/pV offset.
    centered_reference = observed - observed[:, [parsed.sampled_state]]
    difference = np.abs(centered_reference - ours)
    max_difference = float(np.max(difference))
    # Very large foreign-state penalties can lose a few floating-point bits
    # when alchemlyb subtracts the sampled-state total-energy offset. Keep
    # the absolute check near zero and permit only a roundoff-scale relative
    # allowance for huge values.
    allowance = (reduced_tolerance + relative_tolerance *
                 np.maximum(np.abs(centered_reference), np.abs(ours)))
    if np.any(difference > allowance):
        raise ValueError("independent reduced potentials differ")
    return {"alchemlyb_version": version("alchemlyb"),
            "records": n_rows, "states": n_states,
            "max_abs_difference_kT": max_difference,
            "max_abs_reference_kT": float(np.max(np.abs(centered_reference))),
            "max_fraction_of_allowed_difference": float(np.max(
                np.divide(difference, allowance,
                          out=np.zeros_like(difference), where=allowance > 0)))}


def parse_gromacs_dhdl(
    text: str, *, sampled_state: int, expected_lambdas: tuple[float, ...],
    expected_temperature_K: float, origin_ps: float, duration_ps: float,
    stride_ps: float, tolerance_ps: float, lambda_tolerance: float,
    temperature_tolerance_K: float, self_energy_tolerance_kj_mol: float,
) -> ParsedDhdl:
    """Validate one GROMACS XVG with the observed total/dH/foreign/pV layout."""
    n_states = len(expected_lambdas)
    if (n_states < 2 or sampled_state not in range(n_states)
            or not all(isfinite(x) for x in expected_lambdas)
            or any(right <= left for left, right in
                   zip(expected_lambdas, expected_lambdas[1:]))
            or not all(isfinite(x) for x in
                       (expected_temperature_K, origin_ps, lambda_tolerance,
                        temperature_tolerance_K, self_energy_tolerance_kj_mol))
            or expected_temperature_K <= 0
            or min(lambda_tolerance, temperature_tolerance_K,
                   self_energy_tolerance_kj_mol) < 0):
        raise ValueError("invalid registered XVG parameters")

    subtitles = _SUBTITLE.findall(text)
    if len(subtitles) != 1:
        raise ValueError("missing or ambiguous XVG temperature/state subtitle")
    temperature, state, state_lambda = (
        float(subtitles[0][0]), int(subtitles[0][1]), float(subtitles[0][2]))
    if (not isfinite(temperature) or not isfinite(state_lambda)
            or abs(temperature - expected_temperature_K) > temperature_tolerance_K
            or state != sampled_state
            or abs(state_lambda - expected_lambdas[state]) > lambda_tolerance):
        raise ValueError("XVG temperature or sampled-state label mismatch")

    legends = [(int(index), label) for index, label in _LEGEND.findall(text)]
    if (len(legends) != n_states + 3
            or [index for index, _ in legends] != list(range(len(legends)))
            or legends[0][1] != "Total Energy (kJ/mol)"
            or not legends[1][1].startswith("dH/d")
            or legends[-1][1] != "pV (kJ/mol)"):
        raise ValueError("XVG energy-column layout mismatch")
    foreign = []
    for _, label in legends[2:-1]:
        match = _FOREIGN.search(label)
        if match is None:
            raise ValueError("XVG foreign-energy legend missing")
        foreign.append(float(match.group(1)))
    if (not all(isfinite(value) for value in foreign)
            or any(abs(a - b) > lambda_tolerance
                   for a, b in zip(foreign, expected_lambdas))):
        raise ValueError("XVG foreign-state lambda labels mismatch")

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "@")):
            continue
        try:
            row = tuple(float(token) for token in line.split())
        except ValueError as exc:
            raise ValueError("nonnumeric XVG data row") from exc
        if len(row) != n_states + 4 or not all(isfinite(x) for x in row):
            raise ValueError("incomplete or nonfinite XVG data row")
        rows.append(row)
    if not rows:
        raise ValueError("XVG has no data rows")
    relative_times = tuple(row[0] - origin_ps for row in rows)
    blocks = split_retained_grid(
        relative_times, duration_ps=duration_ps, stride_ps=stride_ps,
        tolerance_ps=tolerance_ps,
    )
    energy = tuple(tuple(row[3:-1]) for row in rows)
    if any(abs(row[sampled_state]) > self_energy_tolerance_kj_mol
           for row in energy):
        raise ValueError("XVG energy to sampled state is nonzero")
    return ParsedDhdl(
        sampled_state=sampled_state, temperature_K=temperature,
        lambda_values=tuple(foreign), times_ps=relative_times,
        foreign_dh_kj_mol=energy, blocks=blocks,
    )


def _safe_path(root: Path, name: str) -> Path:
    if (not name or "\\" in name or "//" in name
            or PurePosixPath(name).is_absolute()
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("unsafe manifest or input path")
    path = root.joinpath(*name.split("/"))
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("symlink in manifest or input path")
        current = current.parent
    return path


def _no_duplicate_keys(pairs: list[tuple[str, str]]) -> dict[str, str]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest key")
        result[key] = value
    return result


def verify_pinned_json_manifest(
    root: Path, *, manifest_name: str, manifest_sha256: str,
) -> dict[str, str]:
    """Verify a pinned JSON seal and every named regular file without writes."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("input root missing or symlinked")
    if not _DIGEST.fullmatch(manifest_sha256):
        raise ValueError("invalid pinned manifest SHA-256")
    manifest_path = _safe_path(root, manifest_name)
    raw = manifest_path.read_bytes()
    if sha256(raw).hexdigest() != manifest_sha256:
        raise ValueError("manifest SHA-256 mismatch")
    manifest = json.loads(raw, object_pairs_hook=_no_duplicate_keys)
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("empty or invalid hash manifest")
    for name, digest in manifest.items():
        if not isinstance(name, str) or not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise ValueError("invalid hash manifest entry")
        file = _safe_path(root, name)
        if not file.is_file() or sha256(file.read_bytes()).hexdigest() != digest:
            raise ValueError(f"file missing or SHA-256 mismatch: {name}")
    return manifest


def load_sealed_dhdl_ladder(
    root: Path, *, manifest_name: str, manifest_sha256: str,
    files_by_state: Mapping[int, str], expected_lambdas: tuple[float, ...],
    expected_temperature_K: float, origin_ps: float, duration_ps: float,
    stride_ps: float, tolerance_ps: float, lambda_tolerance: float,
    temperature_tolerance_K: float, self_energy_tolerance_kj_mol: float,
) -> dict[int, ParsedDhdl]:
    """Admit explicitly named state XVGs after verifying the full saved seal."""
    root = Path(root)
    if (set(files_by_state) != set(range(len(expected_lambdas)))
            or len(set(files_by_state.values())) != len(files_by_state)):
        raise ValueError("missing state or duplicate XVG path")
    manifest = verify_pinned_json_manifest(
        root, manifest_name=manifest_name, manifest_sha256=manifest_sha256,
    )
    result = {}
    for state in range(len(expected_lambdas)):
        name = files_by_state[state]
        if name not in manifest:
            raise ValueError(f"XVG absent from pinned manifest: {name}")
        file = _safe_path(root, name)
        raw = file.read_bytes()
        if sha256(raw).hexdigest() != manifest[name]:
            raise ValueError(f"XVG changed after seal verification: {name}")
        result[state] = parse_gromacs_dhdl(
            raw.decode("utf-8"), sampled_state=state,
            expected_lambdas=expected_lambdas,
            expected_temperature_K=expected_temperature_K,
            origin_ps=origin_ps, duration_ps=duration_ps,
            stride_ps=stride_ps, tolerance_ps=tolerance_ps,
            lambda_tolerance=lambda_tolerance,
            temperature_tolerance_K=temperature_tolerance_K,
            self_energy_tolerance_kj_mol=self_energy_tolerance_kj_mol,
        )
    if len({item.blocks.boundary_index for item in result.values()}) != 1:
        raise ValueError("states disagree about branch-boundary record")
    return result
