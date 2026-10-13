"""The proposed fresh repeat keeps the archived seed lineage distinct."""

from pathlib import Path

import pytest

from src.analysis.f64a_c2_source_preflight import seed_map, plan


def test_r3_seed_map_reproduces_archived_ion_seeds() -> None:
    result = seed_map(3)
    assert result["archived_ion_seeds_reproduced"] == [331504349, 313761282, 1063212952]
    assert result["ion_placement_seed"] == 2072077476
    assert len(set(result["sampling_seed_by_state"].values())) == 20
    assert result["candidate_hrex_exchange_seed"] == 634884696


def test_rejects_historical_repeat_and_unpinned_source(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not reuse"):
        seed_map(2)
    config = tmp_path / "config.yaml"
    source = tmp_path / "wt.pdb"
    config.write_text("fep: {}\n")
    source.write_text("wrong source\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        plan(config, source, 3)
