"""Admission checks for a copied subset of the accepted Stage P seal."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from src.analysis.f64a_c2_stage_p_bundle import LAMBDAS, review_bundle


FIXTURE = Path(__file__).parent / "fixtures/f64a_stage_p_state0_dhdl_excerpt.xvg"


def _synthetic_bundle(root: Path) -> str:
    """Generate parser-shaped data, never presented as real state trajectories."""
    original = FIXTURE.read_text()
    manifest = {}
    status = {"stage": "P", "job_id": "7791102",
              "technical_status": "pass_pending_review_and_accounting",
              "production_authorized": False, "restart_verified": True}
    status_bytes = (json.dumps(status) + "\n").encode()
    (root / "status.json").write_bytes(status_bytes)
    manifest["status.json"] = sha256(status_bytes).hexdigest()
    for state, lam in enumerate(LAMBDAS):
        path = root / f"state{state:02d}/smoke.xvg"
        path.parent.mkdir()
        text = original.replace(
            "state 0: fep-lambda = 0.0000",
            f"state {state}: fep-lambda = {lam:.4f}")
        lines = []
        for line in text.splitlines():
            if not line or line.startswith(("#", "@")):
                lines.append(line)
                continue
            values = [float(value) for value in line.split()]
            foreign = values[3:-1]
            offset = foreign[state]
            values[3:-1] = [value - offset for value in foreign]
            lines.append(" ".join(f"{value:.9f}" for value in values))
        raw = ("\n".join(lines) + "\n").encode()
        path.write_bytes(raw)
        manifest[str(path.relative_to(root))] = sha256(raw).hexdigest()
    for i in range(614 - len(manifest)):
        manifest[f"untransferred/{i:03d}.log"] = "0" * 64
    raw = (json.dumps(manifest, sort_keys=True) + "\n").encode()
    (root / "output-hashes.json").write_bytes(raw)
    return sha256(raw).hexdigest()


def test_complete_copied_subset_and_tamper_detection(tmp_path: Path) -> None:
    digest = _synthetic_bundle(tmp_path)
    result = review_bundle(tmp_path, manifest_sha256=digest)
    assert len(result["states"]) == 20
    assert {row["records"] for row in result["states"]} == {21}
    assert {row["retained_records"] for row in result["states"]} == {20}
    assert result["all_614_original_files_rechecked_locally"] is False
    with (tmp_path / "state19/smoke.xvg").open("a") as stream:
        stream.write("# altered\n")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        review_bundle(tmp_path, manifest_sha256=digest)


def test_manifest_pin_must_match(tmp_path: Path) -> None:
    _synthetic_bundle(tmp_path)
    with pytest.raises(ValueError, match="manifest SHA-256 mismatch"):
        review_bundle(tmp_path, manifest_sha256="0" * 64)
