"""Read-only admission of a small export from accepted Stage P job 7791102.

The source attempt's 614-file seal was already checked on SCC. A subset
bundle can recheck only its copied files, so this module states that limit.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from src.analysis.f64a_c2_gromacs_inputs import (
    compare_with_alchemlyb, parse_gromacs_dhdl,
)


_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
STAGE_P_ROOT = Path("/projectnb/rise-batteries/bode/container-build-packages/") / (
    "f64a-protein-technical-runtime-20260928-v1/attempt")
LAMBDAS = (0.0, 0.0588, 0.1176, 0.1765, 0.2353, 0.2941, 0.3529,
           0.4118, 0.4706, 0.5294, 0.5882, 0.6471, 0.7059, 0.7647,
           0.8235, 0.8824, 0.92, 0.95, 0.975, 1.0)


def _unique_pairs(pairs: list[tuple[str, str]]) -> dict[str, str]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest entry")
        result[key] = value
    return result


def _file(root: Path, name: str) -> Path:
    parts = PurePosixPath(name).parts
    if (not name or "\\" in name or PurePosixPath(name).is_absolute()
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("unsafe bundle path")
    path = root.joinpath(*parts)
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("bundle contains symlink")
        current = current.parent
    if not path.is_file():
        raise ValueError(f"missing bundle file: {name}")
    return path


def verify_subset(root: Path, *, manifest_sha256: str,
                  required_paths: tuple[str, ...],
                  expected_manifest_entries: int) -> dict[str, str]:
    """Pin the original full seal and rehash only copied subset files."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir() or not _DIGEST.fullmatch(manifest_sha256):
        raise ValueError("invalid bundle root or pinned digest")
    raw = _file(root, "output-hashes.json").read_bytes()
    if sha256(raw).hexdigest() != manifest_sha256:
        raise ValueError("original manifest SHA-256 mismatch")
    manifest = json.loads(raw, object_pairs_hook=_unique_pairs)
    if not isinstance(manifest, dict) or len(manifest) != expected_manifest_entries:
        raise ValueError("original manifest entry count mismatch")
    if len(set(required_paths)) != len(required_paths):
        raise ValueError("duplicate required bundle file")
    for name in required_paths:
        digest = manifest.get(name)
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise ValueError(f"required path absent from original manifest: {name}")
        if sha256(_file(root, name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"bundle file SHA-256 mismatch: {name}")
    return manifest


def review_bundle(root: Path, *, manifest_sha256: str,
                  compare_independent: bool = False) -> dict:
    """Validate the 20 copied Stage P XVGs without writing any analysis output."""
    root = Path(root)
    names = tuple(f"state{i:02d}/smoke.xvg" for i in range(20))
    manifest = verify_subset(
        root, manifest_sha256=manifest_sha256,
        required_paths=("status.json",) + names,
        expected_manifest_entries=614)
    status = json.loads(_file(root, "status.json").read_text())
    if (status.get("stage") != "P" or status.get("job_id") != "7791102"
            or status.get("technical_status") != "pass_pending_review_and_accounting"
            or status.get("production_authorized") is not False
            or status.get("restart_verified") is not True):
        raise ValueError("Stage P status identity mismatch")
    rows = []
    for state, name in enumerate(names):
        file = _file(root, name)
        parsed = parse_gromacs_dhdl(
            file.read_text(), sampled_state=state,
            expected_lambdas=LAMBDAS, expected_temperature_K=298.15,
            origin_ps=0.0, duration_ps=4.0, stride_ps=0.2,
            tolerance_ps=1e-5, lambda_tolerance=1e-4,
            temperature_tolerance_K=0.01,
            self_energy_tolerance_kj_mol=1e-3)
        row = {"state": state, "file": name,
               "records": len(parsed.times_ps),
               "retained_records": len(parsed.blocks.early_indices)
                                   + len(parsed.blocks.late_indices),
               "sha256": manifest[name]}
        if compare_independent:
            row["independent_comparison"] = compare_with_alchemlyb(
                file, parsed=parsed, origin_ps=0.0,
                time_tolerance_ps=1e-5, lambda_tolerance=1e-4,
                reduced_tolerance=1e-7, relative_tolerance=2e-15)
        rows.append(row)
    return {"status": "stage_p_subset_review_pass", "job_id": "7791102",
            "full_source_manifest_sha256": manifest_sha256,
            "full_source_manifest_entries": len(manifest),
            "copied_and_rehashed_files": len(names) + 1,
            "all_614_original_files_rechecked_locally": False,
            "independent_alchemlyb_comparison": compare_independent,
            "states": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--compare-alchemlyb", action="store_true")
    args = parser.parse_args()
    print(json.dumps(review_bundle(args.root, manifest_sha256=args.manifest_sha256,
                                   compare_independent=args.compare_alchemlyb),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
