"""Reproducible CPU review of the user-transferred Stage P XVG subset."""

from __future__ import annotations

import argparse
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
import tarfile
import tempfile

import numpy as np
from alchemlyb.parsing.gmx import extract_u_nk

from src.analysis.f64a_c2_gromacs_inputs import (
    parse_gromacs_dhdl, relative_reduced_potentials,
)
from src.analysis.f64a_c2_stage_p_bundle import LAMBDAS, review_bundle
from src.fep.analyze import solve_leg_mbar


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "docs/f64a_c2_stage_p_full_review_v1.json"


def load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    cfg = json.loads(raw)
    if (cfg["analysis_id"] != "f64a_c2_stage_p_full_ladder_cpu_review_v1"
            or cfg["expected_archive_files"] != 22
            or cfg["expected_source_manifest_entries"] != 614
            or cfg["fit_blocks"] != {"early": [1, 11], "late": [11, 21],
                                     "all_retained": [1, 21]}
            or any(cfg[key] <= 0 for key in (
                "endpoint_agreement_tolerance_kT",
                "conditional_se_agreement_tolerance_kT",
                "overlap_agreement_tolerance"))):
        raise ValueError("invalid Stage P CPU review specification")
    return cfg, sha256(raw).hexdigest()


def _extract_exact_archive(archive: Path, root: Path, count: int) -> None:
    expected = {"output-hashes.json", "status.json"} | {
        f"state{i:02d}/smoke.xvg" for i in range(20)}
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        names = [member.name for member in members]
        if (len(members) != count or set(names) != expected
                or not all(member.isfile() and member.size <= 10_000_000
                           for member in members)):
            raise ValueError("archive member identity/type/size mismatch")
        for member in members:
            target = root / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())


def _fit_rows(matrices: list[np.ndarray], start: int, stop: int) -> dict:
    sample_count = stop - start
    u_kn = np.concatenate([matrix[start:stop].T for matrix in matrices], axis=1)
    if u_kn.shape != (20, 20 * sample_count) or not np.isfinite(u_kn).all():
        raise ValueError("invalid stacked all-state MBAR matrix")
    fit = solve_leg_mbar(u_kn, np.full(20, sample_count, dtype=int))
    return {"samples_per_state": sample_count,
            "max_abs_reduced_potential_kT": float(np.max(np.abs(u_kn))),
            "endpoint_kT": fit["dg_kT"],
            "conditional_se_kT": fit["ddg_kT"],
            "minimum_adjacent_overlap": fit["min_adjacent"],
            "solver_notes": fit["solver_notes"]}


def run(config_path: Path) -> dict:
    cfg, digest = load_config(config_path)
    archive = ROOT / cfg["archive"]
    if sha256(archive.read_bytes()).hexdigest() != cfg["archive_sha256_scc"]:
        raise ValueError("transferred archive differs from SCC SHA-256")
    with tempfile.TemporaryDirectory(prefix="f64a-stage-p-review-") as tmp:
        root = Path(tmp)
        _extract_exact_archive(archive, root, cfg["expected_archive_files"])
        admission = review_bundle(
            root, manifest_sha256=cfg["source_manifest_sha256_scc"],
            compare_independent=True)
        if len(admission["states"]) != 20:
            raise ValueError("incomplete admitted state ladder")
        ours, independent = [], []
        for state in range(20):
            file = root / f"state{state:02d}/smoke.xvg"
            parsed = parse_gromacs_dhdl(
                file.read_text(), sampled_state=state, expected_lambdas=LAMBDAS,
                expected_temperature_K=298.15, origin_ps=0.0,
                duration_ps=4.0, stride_ps=0.2, tolerance_ps=1e-5,
                lambda_tolerance=1e-4, temperature_tolerance_K=0.01,
                self_energy_tolerance_kj_mol=1e-3)
            ours.append(np.asarray(relative_reduced_potentials(parsed).rows))
            reference = np.asarray(extract_u_nk(str(file), T=298.15, filter=False).values)
            reference -= reference[:, [state]]
            independent.append(reference)
        fits = {}
        for name, (start, stop) in cfg["fit_blocks"].items():
            left = _fit_rows(ours, start, stop)
            right = _fit_rows(independent, start, stop)
            difference = {"endpoint_kT": abs(left["endpoint_kT"] - right["endpoint_kT"]),
                          "conditional_se_kT": abs(left["conditional_se_kT"] - right["conditional_se_kT"]),
                          "minimum_adjacent_overlap": abs(left["minimum_adjacent_overlap"] - right["minimum_adjacent_overlap"])}
            if (difference["endpoint_kT"] > cfg["endpoint_agreement_tolerance_kT"]
                    or difference["conditional_se_kT"] > cfg["conditional_se_agreement_tolerance_kT"]
                    or difference["minimum_adjacent_overlap"] > cfg["overlap_agreement_tolerance"]):
                raise ValueError(f"independent MBAR calculation differs for {name}")
            fits[name] = {"local_parser": left, "independent_parser": right,
                          "absolute_differences": difference}
    return {"analysis_id": cfg["analysis_id"], "scope": cfg["scope"],
            "config_sha256": digest,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "archive_sha256": cfg["archive_sha256_scc"],
            "source_manifest_sha256": cfg["source_manifest_sha256_scc"],
            "runtime": {"python": sys.version.split()[0],
                        "alchemlyb": version("alchemlyb"),
                        "pymbar": version("pymbar")},
            "admission": admission, "fits": fits,
            "limitations": [
                "Only 21 copied files were rehashed against the 614-entry original seal locally.",
                "Stage P is a 4-ps technical HREX run, not C2 production sampling.",
                "Both fits use PyMBAR; parser independence does not imply independent estimator software.",
                "Conditional MBAR standard errors ignore unresolved correlated-walker uncertainty."]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cfg, _ = load_config(args.config)
    output = args.output or ROOT / cfg["report"]
    if output.exists():
        raise FileExistsError("refusing to overwrite saved Stage P review")
    report = run(args.config)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_STAGE_P_FULL_LADDER_CPU_REVIEW_PASS {output}")


if __name__ == "__main__":
    main()
