"""Read-only identity and seed plan for a fresh C2 folded-leg system."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import yaml

from src.seeds import stable_seed


EXPECTED_CONFIG_SHA256 = "af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29"
EXPECTED_WT_SHA256 = "394776d7388e79c8de7ecd46b96b16c1eaf3aaa3a7e4a4a1a2173db397bc6f29"
HISTORICAL_ION_SEEDS = (331504349, 313761282, 1063212952)
EXPECTED_LAMBDAS = (
    0.0000, 0.0588, 0.1176, 0.1765, 0.2353, 0.2941, 0.3529, 0.4118,
    0.4706, 0.5294, 0.5882, 0.6471, 0.7059, 0.7647, 0.8235, 0.8824,
    0.9200, 0.9500, 0.9750, 1.0000,
)


def seed_map(repeat: int) -> dict:
    if repeat < 3:
        raise ValueError("fresh technical repeat must not reuse archived r0-r2")
    prior_system_seeds = [stable_seed("F64A", "folded", r, "system")
                          for r in range(repeat + 1)]
    if tuple(prior_system_seeds[:3]) != HISTORICAL_ION_SEEDS:
        raise ValueError("historical ion seed derivation changed")
    if len(set(prior_system_seeds)) != len(prior_system_seeds):
        raise ValueError("system seed collision")
    sampling = [stable_seed("F64A", "folded", i, repeat, "sampling") or 1
                for i in range(20)]
    exchange = stable_seed("F64A", "folded", repeat, "hrex", "exchange") or 1
    if len(set(sampling + [exchange, prior_system_seeds[-1]])) != 22:
        raise ValueError("sampling/exchange/system seed collision")
    return {"ion_placement_seed": prior_system_seeds[-1],
            "sampling_seed_by_state": {f"state{i:02d}": seed for i, seed in enumerate(sampling)},
            "candidate_hrex_exchange_seed": exchange,
            "archived_ion_seeds_reproduced": list(prior_system_seeds[:3])}


def plan(config: Path, prepared_wt: Path, repeat: int) -> dict:
    config_hash = sha256(config.read_bytes()).hexdigest()
    wt_hash = sha256(prepared_wt.read_bytes()).hexdigest()
    if config_hash != EXPECTED_CONFIG_SHA256 or wt_hash != EXPECTED_WT_SHA256:
        raise ValueError("source or historical config hash mismatch")
    cfg = yaml.safe_load(config.read_text())
    fep = cfg["fep"]
    if (not fep["independent_replicate_systems"]
            or int(fep["lambda_windows"]) != 20
            or tuple(float(x) for x in fep["lambda_vector"]) != EXPECTED_LAMBDAS
            or fep["keep_disulfide_reduced"] is not True
            or float(fep["timestep_fs"]) != 2.0):
        raise ValueError("fresh-system source protocol mismatch")
    return {"status": "local_source_and_seed_plan_only",
            "variant": "F64A", "leg": "folded", "technical_repeat": repeat,
            "config_sha256": config_hash, "prepared_wt_sha256": wt_hash,
            "protein_start_family": "single_vetted_prepared_WT_family",
            "independent_replicate_systems": True,
            "expected_states": 20,
            "historical_builder_system_key": "stable_seed('F64A','folded',repeat,'system')",
            "historical_builder_sampling_key": "stable_seed('F64A','folded',state,repeat,'sampling')",
            "proposed_hrex_exchange_key": "stable_seed('F64A','folded',repeat,'hrex','exchange')",
            "seeds": seed_map(repeat),
            "branch_initial_velocities": "shared_via_common_checkpoint",
            "execution_authorized": False, "production_authorized": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prepared-wt", type=Path, required=True)
    parser.add_argument("--repeat", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("refusing to overwrite source plan")
    result = plan(args.config, args.prepared_wt, args.repeat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"F64A_C2_SOURCE_PREFLIGHT_RECORDED {args.output}")


if __name__ == "__main__":
    main()
