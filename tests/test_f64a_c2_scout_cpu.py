"""Check the paired scout's sealed CPU inputs and fail-closed review."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from src.analysis import f64a_c2_scout_cpu as scout
from src.fep.pmx_engine import production_mdp


ROOT = Path(__file__).resolve().parents[1]


def test_scout_mdp_preserves_physical_settings_and_lambdas():
    cfg = yaml.safe_load((ROOT / "config/pipeline.yaml").read_text())
    for state in (0, 19):
        source = production_mdp(cfg, state, 10971, leg="folded")
        before = scout.mdp_values(source)
        after = scout.mdp_values(scout.scout_mdp(source))
        assert set(before) == set(after)
        assert all(after[k] == v for k, v in before.items() if k not in scout.CHANGES)
        assert all(after[k] == str(v) for k, v in scout.CHANGES.items())
        assert after["init-lambda-state"] == str(state)
        assert after["calc-lambda-neighbors"] == "-1"


def test_cpu_spec_rejects_execution_or_unreviewed_stride():
    spec = yaml.safe_load((ROOT / "docs/f64a_c2_scout_cpu_v1.yaml").read_text())
    scout.validate_spec(spec)
    changed = copy.deepcopy(spec)
    changed["scout_candidate"]["gpu_jobs_authorized"] = 1
    with pytest.raises(ValueError, match="executable scope"):
        scout.validate_spec(changed)
    changed = copy.deepcopy(spec)
    changed["mdp_changes"]["nstxout-compressed"] = 200
    with pytest.raises(ValueError, match="unreviewed MDP"):
        scout.validate_spec(changed)


def _fake_prepared(package):
    prepared = package / "prepared"
    prepared.mkdir()
    (prepared / "historical-pipeline.yaml").write_bytes(
        (ROOT / "config/pipeline.yaml").read_bytes())
    spec = yaml.safe_load((package / "source-spec.yaml").read_text())
    cfg = yaml.safe_load((prepared / "historical-pipeline.yaml").read_text())
    rows = []
    for state in range(20):
        name = "state{:02d}".format(state)
        inputs = prepared / "inputs" / "states" / name
        inputs.mkdir(parents=True)
        source_mdp = production_mdp(cfg, state, 10971, leg="folded")
        (inputs / "source.mdp").write_text(source_mdp)
        (inputs / "scout.mdp").write_text(scout.scout_mdp(source_mdp))
        (inputs / "start.gro").write_text("fixture\n")
        common = prepared / "common" / "states" / name
        common.mkdir(parents=True)
        effective = scout.scout_mdp(source_mdp)
        effective += ("compressed-x-grps = \n"
                      "compressed-x-precision = 1000\n"
                      "nstxout = 0\nnstvout = 0\nnstfout = 0\n")
        (common / "mdout.mdp").write_text(effective)
        (common / "topol.tpr").write_bytes(("fake-TPR-%02d" % state).encode())
        for arm in ("baseline", "hrex"):
            target = prepared / "arms" / arm / "states" / name
            target.mkdir(parents=True)
            (target / "topol.tpr").write_bytes((common / "topol.tpr").read_bytes())
        rows.append({"state": state,
                     "tpr_sha256": scout.digest(common / "topol.tpr"),
                     "mdout_sha256": scout.digest(common / "mdout.mdp")})
    record = {"status": "cpu_inputs_prepared_pending_review", "scope": spec["scope"],
              "execution_authorized": False, "production_authorized": False,
              "package_spec_sha256": scout.digest(package / "source-spec.yaml"),
              "source_manifest_sha256": scout.SOURCE_MANIFEST,
              "source_inventory_sha256": scout.SOURCE_INVENTORY,
              "sif_sha256": scout.IMAGE, "states": rows}
    (prepared / "PREPARED.json").write_text(json.dumps(record))
    scout.manifest(prepared)
    return prepared


def test_sealed_package_and_pair_review(tmp_path):
    package = tmp_path / "candidate"
    scout.package(package, ROOT / "docs/f64a_c2_scout_cpu_v1.yaml")
    scout.check_package(package)
    assert not any("SUBMIT" in p.name or p.suffix == ".sge"
                   for p in package.iterdir())
    prepared = _fake_prepared(package)
    scout.review(package)

    altered = prepared / "arms" / "hrex" / "states" / "state07" / "topol.tpr"
    altered.write_bytes(b"different TPR")
    scout.manifest(prepared)  # Even a re-sealed divergent pair must fail.
    with pytest.raises(ValueError, match="paired TPR mismatch"):
        scout.review(package)


def test_non_system_coordinate_group_rejected():
    cfg = yaml.safe_load((ROOT / "config/pipeline.yaml").read_text())
    vector = [float(v) for v in cfg["fep"]["lambda_vector"]]
    spec = yaml.safe_load((ROOT / "docs/f64a_c2_scout_cpu_v1.yaml").read_text())
    values = scout.mdp_values(scout.scout_mdp(
        production_mdp(cfg, 0, 10971, leg="folded")))
    values.update({"compressed-x-grps": "System", "compressed-x-precision": "1000",
                   "nstxout": "0", "nstvout": "0", "nstfout": "0"})
    scout.effective_checks(values, 0, vector, spec)
    values["compressed-x-grps"] = "Protein"
    with pytest.raises(ValueError, match="compressed-x-grps mismatch"):
        scout.effective_checks(values, 0, vector, spec)


def test_cpu_preparation_rehearsal_has_no_gpu_or_scheduler_call(tmp_path, monkeypatch):
    package = tmp_path / "candidate"
    scout.package(package, ROOT / "docs/f64a_c2_scout_cpu_v1.yaml")
    source = tmp_path / "accepted-source"
    system = source / "inputs" / "system"
    system.mkdir(parents=True)
    (system / "hybrid.top").write_text("[ system ]\nfixture\n")
    (system / "posre.itp").write_text("; fixture\n")
    ff = source / "forcefield" / "amber99sb-star-ildn-mut.ff"
    ff.mkdir(parents=True)
    (ff / "forcefield.itp").write_text("; fixture\n")
    (source / "historical-pipeline.yaml").write_bytes(
        (ROOT / "config/pipeline.yaml").read_bytes())
    cfg = yaml.safe_load((source / "historical-pipeline.yaml").read_text())
    vector = [float(v) for v in cfg["fep"]["lambda_vector"]]
    for state in range(20):
        target = source / "inputs" / "states" / "state{:02d}".format(state)
        target.mkdir(parents=True)
        (target / "start.gro").write_text("fixture\n")
        (target / "source.mdp").write_text(
            production_mdp(cfg, state, 10971, leg="folded"))
    monkeypatch.setattr(scout, "source_checks", lambda spec: (source, "/fake/ffroot", vector))
    real_digest = scout.digest
    image_path = yaml.safe_load((package / "source-spec.yaml").read_text())["image"]["path"]
    monkeypatch.setattr(scout, "digest", lambda path: scout.IMAGE
                        if str(path) == image_path else real_digest(path))
    calls = []

    def fake_grompp(command, **kwargs):
        calls.append(command)
        assert command[0:2] == ["singularity", "exec"]
        assert "--nv" not in command and "grompp" in command
        assert not any(item in command for item in ("mdrun", "qsub", "mpirun"))
        assert kwargs["env"]["SINGULARITYENV_GMXLIB"] == "/fake/ffroot"
        bindings = [command[i + 1] for i, value in enumerate(command) if value == "--bind"]
        output = Path(bindings[-1].split(":/tmp")[0])
        name = Path(command[command.index("-f") + 1]).parent.name
        state = int(name.replace("state", ""))
        input_mdp = package / "prepared" / "inputs" / "states" / name / "scout.mdp"
        (output / "topol.tpr").write_bytes(("fake-TPR-%02d" % state).encode())
        (output / "mdout.mdp").write_text(
            input_mdp.read_text() + "compressed-x-grps = \n"
            "compressed-x-precision = 1000\n"
            "nstxout = 0\nnstvout = 0\nnstfout = 0\n")
        return SimpleNamespace(returncode=0, stdout="GROMACS grompp fixture\n")

    monkeypatch.setattr(scout.subprocess, "run", fake_grompp)
    scout.prepare(package)
    scout.review(package)
    assert len(calls) == 20
    assert all("--cleanenv" in call and "--contain" in call for call in calls)
