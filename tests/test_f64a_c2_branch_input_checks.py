"""Contract tests for the read-only common-checkpoint branch reviewer."""

import hashlib
import json

import pytest

from src.analysis import f64a_c2_branch_input_checks as checks


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def fixture(tmp_path, monkeypatch):
    image = write(tmp_path / "r6.sif", "test image")
    monkeypatch.setattr(checks, "IMAGE_SHA256", checks.sha256(image))
    vector = [round(i / 19, 6) for i in range(20)]
    plan = {
        "schema_version": 1, "scope": checks.SCOPE,
        "execution_authorized": False, "production_authorized": False,
        "image_path": str(image), "image_sha256": checks.IMAGE_SHA256,
        "state_count": 20, "atom_count": 38414, "prep_step": 1000,
        "prep_time_ps": 2.0, "prep_checkpoint_part": 1,
        "branch_simulation_part": 2, "dt_ps": 0.002,
        "retained_steps": {"baseline": 4000, "hrex": 2000},
        "lambda_vector": vector,
        "output_strides": {"nstdhdl": 500, "nstenergy": 500,
                           "nstxout-compressed": 1000},
        "checkpoint_sha256": {},
    }
    root = tmp_path / "inputs"
    for state, name in enumerate(checks.STATE_NAMES):
        cpt = "checkpoint {}".format(state)
        plan["checkpoint_sha256"][name] = hashlib.sha256(cpt.encode()).hexdigest()
        dump = ("step = 1000\nt = 2\nsimulation part # = 1\n"
                "fep_state[0] = {}\n".format(state))
        write(root / "common" / name / "start.cpt", cpt)
        write(root / "common" / name / "start.cpt.dump", dump)
        for arm in checks.ARMS:
            p = root / "arms" / arm / name
            write(p / "start.cpt", cpt)
            write(p / "start.cpt.dump", dump)
            write(p / "topol.tpr", "tpr {} {}".format(arm, state))
            nsteps = plan["retained_steps"][arm]
            mdp = ("nsteps = {}\ninit-step = 1000\ntinit = 0\n"
                   "simulation-part = 2\ndt = 0.002\n"
                   "gen-vel = no\ncontinuation = yes\n"
                   "init-lambda-state = {}\nfep-lambdas = {}\n"
                   "free-energy = yes\ncalc-lambda-neighbors = -1\n"
                   "nstdhdl = 500\nnstenergy = 500\n"
                   "nstxout-compressed = 1000\n"
                   "gen-seed = {}\n".format(
                       nsteps, state, " ".join(map(str, vector)), state + 10))
            write(p / "mdout.mdp", mdp)
            tpr_dump = ("natoms = 38414\nnsteps = {}\ninit-step = 1000\n"
                        "init-lambda-state = {}\nn-lambdas = 20\n"
                        "calc-lambda-neighbors = -1\ndt = 0.002\n"
                        "all-lambdas:\nfep-lambdas = {}\n".format(
                            nsteps, state, " ".join(map(str, vector))))
            write(p / "topol.tpr.dump", tpr_dump)
            write(p / "grompp.log", "GROMACS grompp completed\n")
            write(p / "grompp-result.json", json.dumps({
                "exit_status": 0,
                "argv": ["gmx_mpi", "grompp", "-t", "/branch/{}/start.cpt".format(name),
                         "-f", "branch.mdp", "-p", "hybrid.top", "-c", "start.gro",
                         "-o", "topol.tpr"],
            }))
    return root, plan


def test_complete_paired_branch_passes(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    result = checks.review(root, plan)
    assert result["states"] == 20
    assert len(result["rows"]) == 40
    assert {row["final_step"] for row in result["rows"]} == {3000, 5000}


def test_missing_checkpoint_fails_closed(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    (root / "arms/hrex/state09/start.cpt").unlink()
    with pytest.raises(ValueError, match="unexpected or missing branch input file"):
        checks.review(root, plan)


def test_changed_arm_physics_rejected(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    path = root / "arms/hrex/state05/mdout.mdp"
    path.write_text(path.read_text() + "pcoupl = no\n")
    with pytest.raises(ValueError, match="unregistered arm MDP difference"):
        checks.review(root, plan)


def test_wrong_checkpoint_state_rejected(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    path = root / "common/state03/start.cpt.dump"
    path.write_text(path.read_text().replace("fep_state[0] = 3", "fep_state[0] = 4"))
    with pytest.raises(ValueError, match="checkpoint step/time/part/FEP-state mismatch"):
        checks.review(root, plan)


def test_velocity_regeneration_rejected(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    path = root / "arms/baseline/state00/mdout.mdp"
    path.write_text(path.read_text().replace("gen-vel = no", "gen-vel = yes"))
    with pytest.raises(ValueError, match="continuation/free-energy"):
        checks.review(root, plan)


def test_missing_tpr_and_warning_rejected(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    (root / "arms/hrex/state19/topol.tpr").unlink()
    with pytest.raises(ValueError, match="unexpected or missing branch input file"):
        checks.review(root, plan)
    write(root / "arms/hrex/state19/topol.tpr", "restored")
    write(root / "arms/hrex/state19/grompp.log", "WARNING 1\n")
    with pytest.raises(ValueError, match="grompp warning"):
        checks.review(root, plan)


def test_preexisting_output_in_branch_rejected(tmp_path, monkeypatch):
    root, plan = fixture(tmp_path, monkeypatch)
    write(root / "arms/baseline/state01/scout.xvg", "old output")
    with pytest.raises(ValueError, match="unexpected or missing branch input file"):
        checks.review(root, plan)
