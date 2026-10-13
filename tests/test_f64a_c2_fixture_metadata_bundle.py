"""Fixture subset checks preserve all 20 branch checkpoint ancestries."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from src.analysis.f64a_c2_fixture_metadata_bundle import (
    CONTRACT, FILES, STATES, review,
)


def _write(root: Path, name: str, value: dict) -> str:
    file = root / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(value, sort_keys=True) + "\n")
    return sha256(file.read_bytes()).hexdigest()


def _make_bundle(root: Path) -> str:
    contract = json.loads(CONTRACT.read_text())
    checkpoint = {name: sha256(name.encode()).hexdigest() for name in STATES}
    common = {f"{name}/final.cpt": checkpoint[name] for name in STATES}
    common.update({f"other/{i:03d}": "0" * 64 for i in range(310)})
    branch = {f"{place}/{name}/start.cpt": checkpoint[name]
              for place in ("common", "arms/baseline", "arms/hrex")
              for name in STATES}
    branch.update({f"other/{i:03d}": "0" * 64 for i in range(301)})
    plan = {"state_count": 20, "atom_count": contract["expected_atom_count"],
            "image_sha256": contract["image_sha256"],
            "lambda_vector": contract["expected_lambdas"],
            "prep_step": 1100, "branch_simulation_part": 2,
            "retained_steps": {"baseline": 2000, "hrex": 1500},
            "production_authorized": False, "checkpoint_sha256": checkpoint}
    _write(root, "common-seal.json", common)
    _write(root, "branch-input-seal.json", branch)
    _write(root, "branch-inputs/plan.json", plan)
    _write(root, "status.json", {
        "job_id": "7865574", "technical_status": "pass_pending_accounting_and_review",
        "production_authorized": False, "failure": None})
    _write(root, "accounting.json", {
        "job_id": "7865574", "exit_status": 0, "failed": 0,
        "reviewed": True, "wall_seconds": 306})
    history = []
    for parity, step in enumerate((1500, 2000, 2500)):
        history.append({"step": step, "attempted_pairs": [
            [i, i + 1] for i in range(parity % 2, 19, 2)],
            "accepted_pairs": [], "state_to_walker": list(range(20))})
    for phase, step, part, records in (("common", 1100, 1, 12),
                                       ("baseline", 3100, 2, 21),
                                       ("hrex", 2600, 2, 16)):
        exchange = ({"rounds": 3, "attempted_exchanges": 29,
                     "accepted_exchanges": 0, "final_state_to_walker": list(range(20)),
                     "history": history}
                    if phase == "hrex" else {"rounds": 0, "accepted": 0})
        review_doc = {"checkpoints": {name: {
            "step": step, "part": part, "fep_state": i,
            "time_ps": step * 0.002} for i, name in enumerate(STATES)},
            "dhdl": {name: {"records": records} for name in STATES},
            "energy": {name: {"records": records} for name in STATES},
            "xtc": {name: [] for name in STATES}, "exchange": exchange}
        _write(root, f"{phase}-review.json", review_doc)
    original = {name: sha256((root / name).read_bytes()).hexdigest()
                for name in FILES if name not in ("accounting.json", "output-hashes.json")}
    original.update({f"common/{name}/final.cpt": checkpoint[name] for name in STATES})
    original.update({f"branch-inputs/{place}/{name}/start.cpt": checkpoint[name]
                     for place in ("common", "arms/baseline", "arms/hrex")
                     for name in STATES})
    original.update({f"untransferred/{i:04d}": "0" * 64
                     for i in range(1608 - len(original))})
    _write(root, "output-hashes.json", original)
    post = dict(original)
    post.update({"accounting.json": sha256((root / "accounting.json").read_bytes()).hexdigest(),
                 "output-hashes.json": sha256((root / "output-hashes.json").read_bytes()).hexdigest(),
                 "qacct.log": "0" * 64})
    return _write(root, "output-hashes-after-accounting.json", post)


def test_metadata_subset_links_branch_checkpoints(tmp_path: Path) -> None:
    digest = _make_bundle(tmp_path)
    result = review(tmp_path, post_manifest_sha256=digest)
    assert result["common_checkpoint_hashes_linked_to_both_arms"] == 20
    assert result["hrex_exchange"]["attempted"] == 29
    assert result["full_attempt_files_rehashed_locally"] is False
    with (tmp_path / "branch-input-seal.json").open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="checksum mismatch"):
        review(tmp_path, post_manifest_sha256=digest)


def test_metadata_subset_requires_original_manifest_pin(tmp_path: Path) -> None:
    _make_bundle(tmp_path)
    with pytest.raises(ValueError, match="manifest SHA-256 mismatch"):
        review(tmp_path, post_manifest_sha256="0" * 64)


def test_metadata_subset_rejects_changed_pre_accounting_hash(tmp_path: Path) -> None:
    _make_bundle(tmp_path)
    post = json.loads((tmp_path / "output-hashes-after-accounting.json").read_text())
    post["common/state00/final.cpt"] = "f" * 64
    digest = _write(tmp_path, "output-hashes-after-accounting.json", post)
    with pytest.raises(ValueError, match="did not preserve original"):
        review(tmp_path, post_manifest_sha256=digest)
