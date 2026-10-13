"""CPU branch rehearsal tests; GROMACS calls are simulated locally."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.analysis import f64a_c2_branch_cpu_rehearsal as rehearsal
from src.analysis import f64a_c2_branch_input_checks as checks


def config(image):
    return {
        "schema_version": 1, "scope": rehearsal.PACKAGE_SCOPE,
        "execution_authorized": False, "production_authorized": False,
        "source_prepared": rehearsal.SOURCE_PREPARED,
        "source_manifest_sha256": rehearsal.SOURCE_MANIFEST,
        "source_manifest_entries": 344,
        "source_attempt": rehearsal.SOURCE_ATTEMPT, "job_id": "7791102",
        "image_path": str(image), "image_sha256": checks.IMAGE_SHA256,
        "forcefield_root": rehearsal.FORCEFIELD_ROOT,
        "checkpoint_step": 2000, "checkpoint_time_ps": 4.0,
        "checkpoint_part": 2, "branch_part": 3, "dt_ps": 0.002,
        "atom_count": 38414,
        "retained_steps": {"baseline": 1000, "hrex": 500},
        "output_strides": {"nstdhdl": 100, "nstenergy": 100,
                           "nstxout-compressed": 200},
        "lambda_vector": rehearsal.LAMBDAS,
        "command_timeout_seconds": 180, "total_timeout_seconds": 1800,
    }


def technical_mdp(state):
    return ("nsteps = 2000\ndt = 0.002\ninit-lambda-state = {}\n"
            "fep-lambdas = {}\nfree-energy = yes\n"
            "calc-lambda-neighbors = -1\n"
            "gen-vel = yes\ncontinuation = no\n"
            "nstdhdl = 100\nnstenergy = 100\n"
            "nstxout-compressed = 200\n"
            "gen-seed = {}\n".format(
                state, " ".join(map(str, rehearsal.LAMBDAS)), state + 50))


def test_continuation_mdp_changes_only_registered_keys(tmp_path):
    cfg = config(tmp_path / "r6.sif")
    original = technical_mdp(4) + "pcoupl = C-rescale\n"
    base = rehearsal.continuation_mdp(original, cfg, "baseline")
    hrex = rehearsal.continuation_mdp(original, cfg, "hrex")
    b, h = checks.mdp_values(base), checks.mdp_values(hrex)
    assert b["nsteps"] == "1000" and h["nsteps"] == "500"
    assert b["init-step"] == "2000" and b["simulation-part"] == "3"
    assert b["gen-vel"] == "no" and b["continuation"] == "yes"
    assert b["pcoupl"] == "C-rescale"
    assert {k: v for k, v in b.items() if k != "nsteps"} == {
        k: v for k, v in h.items() if k != "nsteps"}


def test_mocked_twenty_state_cpu_preparation_and_review(tmp_path, monkeypatch):
    package = tmp_path / "package"
    package.mkdir()
    image = tmp_path / "r6.sif"
    image.write_text("mock exact image")
    monkeypatch.setattr(checks, "IMAGE_SHA256", checks.sha256(image))
    cfg = config(image)
    cfg["image_sha256"] = checks.IMAGE_SHA256
    source = tmp_path / "source"
    attempt = tmp_path / "attempt"
    for state, name in enumerate(checks.STATE_NAMES):
        p = source / "inputs" / "states" / name
        p.mkdir(parents=True)
        (p / "technical.mdp").write_text(technical_mdp(state))
        q = attempt / name
        q.mkdir(parents=True)
        (q / "smoke.cpt").write_text("checkpoint {}".format(state))
    (attempt / "output-hashes.json").write_text("{}\n")
    monkeypatch.setattr(rehearsal, "verify_package", lambda *_: None)
    monkeypatch.setattr(rehearsal, "source_checks", lambda *_: (source, attempt))
    calls = []

    def fake_cpu(argv, _cfg, _started):
        calls.append(argv)
        assert "mdrun" not in argv and "qsub" not in argv and "--nv" not in argv
        if argv[-2:] and argv[-2] == "-cp":
            name = Path(argv[-1]).parent.name
            state = int(name[-2:])
            return SimpleNamespace(returncode=0, stdout=(
                "step = 2000\nt = 4\nsimulation part # = 2\n"
                "fep_state[0] = {}\n".format(state)))
        if "grompp" in argv:
            out = argv[argv.index("-o") + 1].split("/branches/", 1)[1]
            arm, name, _ = out.split("/")
            p = package / "prepared" / "arms" / arm / name
            (p / "topol.tpr").write_text("mock TPR {} {}".format(arm, name))
            mdp = package / "prepared" / "mdps" / arm / (name + ".mdp")
            (p / "mdout.mdp").write_text(mdp.read_text())
            return SimpleNamespace(returncode=0, stdout="grompp completed\n")
        assert argv[-2] == "-s"
        path = argv[-1].split("/branches/", 1)[1]
        arm, name, _ = path.split("/")
        state = int(name[-2:])
        return SimpleNamespace(returncode=0, stdout=(
            "natoms = 38414\nnsteps = {}\ninit-step = 2000\n"
            "init-lambda-state = {}\nn-lambdas = 20\n"
            "calc-lambda-neighbors = -1\ndt = 0.002\n"
            "all-lambdas:\nfep-lambdas = {}\n".format(
                cfg["retained_steps"][arm], state,
                " ".join(map(str, rehearsal.LAMBDAS)))))

    monkeypatch.setattr(rehearsal, "run_cpu", fake_cpu)
    rehearsal.prepare(package, cfg)
    rehearsal.review(package, cfg)
    assert len(calls) == 100  # 20 checkpoint dumps, 40 grompp, 40 TPR dumps
    assert checks.review(package / "prepared",
                         json.loads((package / "prepared/plan.json").read_text()))["states"] == 20


def test_no_in_place_rerun(tmp_path, monkeypatch):
    package = tmp_path / "package"
    (package / "prepared").mkdir(parents=True)
    monkeypatch.setattr(rehearsal, "verify_package", lambda *_: None)
    with pytest.raises(ValueError, match="preserve existing prepared evidence"):
        rehearsal.prepare(package, config(tmp_path / "r6.sif"))
