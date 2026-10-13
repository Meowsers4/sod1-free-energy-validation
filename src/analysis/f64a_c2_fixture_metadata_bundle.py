"""Read-only local review of a small C2 fixture metadata subset.

This checks identities and seal relationships. It does not rehash the large
untransferred checkpoint, TPR, trajectory or coordinate files.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from src.analysis.f64a_c2_stage_p_bundle import _file, _unique_pairs


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "packages/f64a-c2-branch-fixture-execution-selected-20261003-v1/contract.json"
CONTRACT_SHA256 = "05165bda5d4bf6867e36f4e1fc52c0a8926dcddb7ca53738ac96ed5a88d8ea4d"
FILES = (
    "output-hashes.json", "status.json", "accounting.json",
    "common-seal.json", "branch-input-seal.json",
    "common-review.json", "baseline-review.json", "hrex-review.json",
    "branch-inputs/plan.json",
)
STATES = tuple(f"state{i:02d}" for i in range(20))


def _read_json(root: Path, name: str) -> dict:
    result = json.loads(_file(root, name).read_text(), object_pairs_hook=_unique_pairs)
    if not isinstance(result, dict):
        raise ValueError(f"invalid JSON object: {name}")
    return result


def _sealed_manifest(root: Path, name: str, digest: str, count: int) -> dict[str, str]:
    raw = _file(root, name).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"manifest SHA-256 mismatch: {name}")
    manifest = _read_json(root, name)
    if len(manifest) != count:
        raise ValueError(f"manifest entry count mismatch: {name}")
    return manifest


def _verify_copied(root: Path, manifest: dict[str, str], names: tuple[str, ...]) -> None:
    for name in names:
        expected = manifest.get(name)
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"missing copied path in seal: {name}")
        if sha256(_file(root, name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"copied metadata checksum mismatch: {name}")


def _review_history(exchange: dict) -> dict:
    history = exchange.get("history")
    if not isinstance(history, list) or len(history) != 3:
        raise ValueError("wrong HREX history length")
    mapping = list(range(20))
    attempts = accepts = 0
    links = set()
    for expected_step, round_ in zip((1500, 2000, 2500), history):
        if round_.get("step") != expected_step:
            raise ValueError("wrong HREX exchange step")
        attempted = [tuple(pair) for pair in round_["attempted_pairs"]]
        accepted = [tuple(pair) for pair in round_["accepted_pairs"]]
        parity = ((expected_step - 1500) // 500) % 2
        expected_pairs = [(i, i + 1) for i in range(parity, 19, 2)]
        if attempted != expected_pairs or not set(accepted).issubset(attempted):
            raise ValueError("wrong HREX exchange pair schedule")
        for left, right in accepted:
            mapping[left], mapping[right] = mapping[right], mapping[left]
        if round_["state_to_walker"] != mapping:
            raise ValueError("HREX walker permutation mismatch")
        attempts += len(attempted)
        accepts += len(accepted)
        links.update(attempted)
    if (exchange.get("rounds") != 3
            or exchange.get("attempted_exchanges") != attempts
            or exchange.get("accepted_exchanges") != accepts
            or exchange.get("final_state_to_walker") != mapping
            or len(links) != 19):
        raise ValueError("HREX exchange summary mismatch")
    return {"rounds": 3, "attempted": attempts, "accepted": accepts,
            "all_neighbor_links_attempted": True,
            "final_state_to_walker": mapping}


def review(root: Path, *, post_manifest_sha256: str) -> dict:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("missing or symlinked bundle root")
    if sha256(CONTRACT.read_bytes()).hexdigest() != CONTRACT_SHA256:
        raise ValueError("local selected contract changed")
    contract = json.loads(CONTRACT.read_text())
    post = _sealed_manifest(root, "output-hashes-after-accounting.json",
                            post_manifest_sha256, 1611)
    _verify_copied(root, post, FILES)
    original = _read_json(root, "output-hashes.json")
    if len(original) != 1608:
        raise ValueError("original output seal entry count mismatch")
    if (set(post) - set(original) != {"accounting.json", "output-hashes.json", "qacct.log"}
            or any(post.get(name) != digest for name, digest in original.items())):
        raise ValueError("post-accounting seal did not preserve original output hashes")
    status = _read_json(root, "status.json")
    accounting = _read_json(root, "accounting.json")
    if (status.get("job_id") != "7865574"
            or status.get("technical_status") != "pass_pending_accounting_and_review"
            or status.get("production_authorized") is not False
            or status.get("failure") is not None
            or str(accounting.get("job_id")) != "7865574"
            or accounting.get("exit_status") != 0
            or accounting.get("failed") != 0
            or accounting.get("reviewed") is not True):
        raise ValueError("fixture status/accounting identity mismatch")
    common_seal = _read_json(root, "common-seal.json")
    branch_seal = _read_json(root, "branch-input-seal.json")
    plan = _read_json(root, "branch-inputs/plan.json")
    if (len(common_seal) != 330 or len(branch_seal) != 361
            or plan.get("state_count") != 20
            or plan.get("atom_count") != contract["expected_atom_count"]
            or plan.get("image_sha256") != contract["image_sha256"]
            or plan.get("lambda_vector") != contract["expected_lambdas"]
            or plan.get("prep_step") != 1100
            or plan.get("branch_simulation_part") != 2
            or plan.get("retained_steps") != {"baseline": 2000, "hrex": 1500}
            or plan.get("production_authorized") is not False):
        raise ValueError("fixture plan/source/seal mismatch")
    checkpoint_hashes = plan.get("checkpoint_sha256")
    if not isinstance(checkpoint_hashes, dict) or set(checkpoint_hashes) != set(STATES):
        raise ValueError("common checkpoint hash map incomplete")
    for name in STATES:
        digest = checkpoint_hashes[name]
        if (common_seal.get(f"{name}/final.cpt") != digest
                or branch_seal.get(f"common/{name}/start.cpt") != digest
                or branch_seal.get(f"arms/baseline/{name}/start.cpt") != digest
                or branch_seal.get(f"arms/hrex/{name}/start.cpt") != digest
                or original.get(f"common/{name}/final.cpt") != digest
                or original.get(f"branch-inputs/common/{name}/start.cpt") != digest
                or original.get(f"branch-inputs/arms/baseline/{name}/start.cpt") != digest
                or original.get(f"branch-inputs/arms/hrex/{name}/start.cpt") != digest):
            raise ValueError(f"branch checkpoint ancestry mismatch: {name}")
    phases = {}
    for phase, step, part, records in (("common", 1100, 1, 12),
                                       ("baseline", 3100, 2, 21),
                                       ("hrex", 2600, 2, 16)):
        phase_review = _read_json(root, f"{phase}-review.json")
        if any(set(phase_review.get(key, {})) != set(STATES)
               for key in ("checkpoints", "dhdl", "energy", "xtc")):
            raise ValueError(f"incomplete phase review: {phase}")
        for index, name in enumerate(STATES):
            cp = phase_review["checkpoints"][name]
            if (cp.get("step") != step or cp.get("part") != part
                    or cp.get("fep_state") != index
                    or abs(cp.get("time_ps", float("inf")) - step * 0.002) > 1e-5
                    or phase_review["dhdl"][name].get("records") != records
                    or phase_review["energy"][name].get("records") != records):
                raise ValueError(f"phase checkpoint/grid mismatch: {phase}/{name}")
        if phase == "hrex":
            exchange = _review_history(phase_review["exchange"])
        elif phase_review.get("exchange") != {"rounds": 0, "accepted": 0}:
            raise ValueError("exchange in no-exchange phase")
        phases[phase] = {"states": 20, "checkpoint_step": step,
                         "simulation_part": part, "energy_records_per_state": records}
    return {"status": "fixture_metadata_subset_review_pass",
            "job_id": "7865574", "selected_contract_sha256": CONTRACT_SHA256,
            "post_accounting_manifest_sha256": post_manifest_sha256,
            "post_accounting_manifest_entries": len(post),
            "copied_files_rehashed": len(FILES),
            "full_attempt_files_rehashed_locally": False,
            "common_seal_entries": len(common_seal),
            "branch_input_seal_entries": len(branch_seal),
            "common_checkpoint_hashes_linked_to_both_arms": 20,
            "accounting": {"exit_status": accounting["exit_status"],
                           "failed": accounting["failed"],
                           "wall_seconds": accounting.get("wall_seconds")},
            "phases": phases, "hrex_exchange": exchange}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--post-manifest-sha256", required=True)
    args = parser.parse_args()
    print(json.dumps(review(args.root, post_manifest_sha256=args.post_manifest_sha256),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
