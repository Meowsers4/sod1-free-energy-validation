"""Guard the technical MDP against changes to the protein Hamiltonian."""

from pathlib import Path

import yaml

from src.analysis.gromacs_protein_technical_inputs import mdp_values, technical_mdp
from src.fep.pmx_engine import production_mdp


def test_short_input_changes_only_registered_timing_and_output():
    root = Path(__file__).resolve().parents[1]
    cfg = yaml.safe_load((root / "config/pipeline.yaml").read_text())
    spec = yaml.safe_load((root / "docs/gromacs_protein_technical_inputs_v1.yaml").read_text())
    original = production_mdp(cfg, 19, 10971, leg="folded")
    changes = {k: v for k, v in spec["technical_mdp"].items()
               if k not in ("first_stop_step", "replex")}
    short = technical_mdp(original, changes)
    old, new = mdp_values(original), mdp_values(short)
    assert old["init-lambda-state"] == new["init-lambda-state"] == "19"
    assert old["fep-lambdas"] == new["fep-lambdas"]
    assert old["sc-coul"] == new["sc-coul"] == "yes"
    assert {k: v for k, v in old.items() if k not in changes} == {
        k: v for k, v in new.items() if k not in changes}
    assert all(new[k] == str(v) for k, v in changes.items())
    assert "historical analysis-discard schedule does not apply" in short


def test_missing_output_key_fails_closed():
    try:
        technical_mdp("nsteps = 100\n", {"nsteps": 20, "nstdhdl": 10})
    except ValueError as exc:
        assert "technical key absent" in str(exc)
    else:
        raise AssertionError("missing technical key accepted")
