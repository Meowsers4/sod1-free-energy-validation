"""Seal a CPU-only, paired F64A timing-scout input candidate.

Package mode runs locally without SCC files. Prepare/review run on SCC, but only
invoke exact-r6 ``gmx_mpi grompp`` through Singularity without GPU passthrough.
There is no mdrun, scheduler operation, GPU allocation or submission command.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

import yaml


SPEC = Path("docs/f64a_c2_scout_cpu_v1.yaml")
SOURCE_MANIFEST = "858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9"
SOURCE_SPEC = "155a24a60191334c0c06a3e02d3c21ecf51cea0902f5ebe5e53370b3c6c322cf"
SOURCE_INVENTORY = "c908e1c1695e0ebe8bd02dce2fece5bdbc83332d617528ca81495bd826c51fe2"
PIPELINE = "af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29"
IMAGE = "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee"
CHANGES = {"nsteps": 50000, "nstcalcenergy": 500, "nstenergy": 500,
           "nstdhdl": 500, "nstlog": 5000, "nstxout-compressed": 25000}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mdp_values(body):
    values = {}
    for line in body.splitlines():
        physical = line.split(";", 1)[0]
        if "=" not in physical:
            continue
        key, value = physical.split("=", 1)
        key = key.strip().lower().replace("_", "-")
        require(key not in values, "duplicate MDP key: " + key)
        values[key] = value.strip()
    return values


def scout_mdp(original, changes=CHANGES):
    """Change only registered timing/output keys; preserve every other key."""
    before = mdp_values(original)
    require(set(changes) <= set(before), "source MDP missing registered key")
    lines = ["; F64A C2 paired timing scout; no scientific estimate"]
    for line in original.splitlines():
        body, separator, comment = line.partition(";")
        if "=" in body:
            key, _ = body.split("=", 1)
            normalized = key.strip().lower().replace("_", "-")
            if normalized in changes:
                line = key + "= " + str(changes[normalized])
                if separator:
                    line += ";" + comment
        if line.lstrip().startswith("; equilibration steps discarded downstream:"):
            line = "; historical analysis-discard schedule does not apply to scout"
        lines.append(line)
    result = "\n".join(lines) + "\n"
    after = mdp_values(result)
    require(set(after) == set(before), "MDP key set changed")
    require(all(after[k] == (str(changes[k]) if k in changes else v)
                for k, v in before.items()), "unregistered MDP value changed")
    return result


def validate_spec(spec):
    require(spec["schema_version"] == 1 and
            spec["scope"] == "f64a_folded_apo_2sh_r0_paired_timing_scout_inputs_only" and
            spec["execution_authorized"] is False and
            spec["production_authorized"] is False, "wrong CPU-only scope")
    source = spec["source"]
    require(source["manifest_sha256"] == SOURCE_MANIFEST and
            source["manifest_entries"] == 344 and
            source["source_spec_sha256"] == SOURCE_SPEC and
            source["source_inventory_sha256"] == SOURCE_INVENTORY and
            source["pipeline_sha256"] == PIPELINE,
            "accepted Stage P source identity changed")
    require(spec["image"]["sha256"] == IMAGE and
            spec["image"]["gmx"] == "/opt/gromacs/2025.3/bin/gmx_mpi",
            "exact-r6 image identity changed")
    require(spec["mdp_changes"] == CHANGES, "unreviewed MDP change")
    require(spec["expected_effective_mdp"] == {"dt_ps": 0.002,
            "calc-lambda-neighbors": -1, "compressed-x-grps": "System",
            "compressed-x-precision": 1000, "nstxout": 0,
            "nstvout": 0, "nstfout": 0}, "effective output contract changed")
    candidate = spec["scout_candidate"]
    require(candidate == {"baseline_replex": 0, "hrex_replex": 500,
            "target_steps": 50000, "target_ps_per_state": 100,
            "checkpoint_minutes": 15, "gpu_jobs_authorized": 0,
            "attempts_per_arm": None}, "executable scope introduced")
    prep = spec["preparation"]
    require(prep == {"command_timeout_seconds": 180,
                     "total_timeout_seconds": 900}, "preparation cap changed")


def manifest(directory):
    directory = Path(directory)
    lines = ["{}  {}\n".format(digest(path), path.relative_to(directory))
             for path in sorted(directory.rglob("*"))
             if path.is_file() and path.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("".join(lines))
    return len(lines)


def verify_manifest(directory, expected_hash=None, expected_count=None):
    directory = Path(directory)
    sums = directory / "SHA256SUMS"
    require(sums.is_file(), "SHA256SUMS absent")
    if expected_hash:
        require(digest(sums) == expected_hash, "manifest identity changed")
    records = sums.read_text().splitlines()
    if expected_count is not None:
        require(len(records) == expected_count, "manifest entry count changed")
    seen = set()
    for record in records:
        digest_text, separator, name = record.partition("  ")
        relative = Path(name)
        require(separator and re.fullmatch(r"[0-9a-f]{64}", digest_text) and
                name and not relative.is_absolute() and ".." not in relative.parts and
                name not in seen, "malformed manifest entry")
        seen.add(name)
        path = directory / relative
        require(path.is_file() and not path.is_symlink() and
                digest(path) == digest_text, "manifest file mismatch: " + name)
    return len(records)


def package(destination, spec_path=SPEC):
    destination = Path(destination).resolve()
    require(not destination.exists(), "refusing to overwrite package")
    spec_path = Path(spec_path).resolve()
    spec = yaml.safe_load(spec_path.read_text())
    validate_spec(spec)
    with tempfile.TemporaryDirectory() as temp:
        staging = Path(temp) / "package"
        staging.mkdir()
        shutil.copy2(Path(__file__), staging / "builder.py")
        shutil.copy2(spec_path, staging / "source-spec.yaml")
        (staging / "README.txt").write_text(
            "CPU-only F64A C2 timing-scout input candidate.\n"
            "No scheduler script, mdrun command, GPU job or submission authorization.\n"
            "Run REVIEW_PACKAGE.sh, then PREPARE_ON_SCC.sh once on scc-i01.\n"
            "The preparation wrapper writes prepared/ and never submits a job.\n")
        (staging / "REVIEW_PACKAGE.sh").write_text(
            '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
            'sha256sum -c SHA256SUMS\n'
            'python builder.py verify-package --package "$PWD"\n')
        (staging / "PREPARE_ON_SCC.sh").write_text(
            '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
            'bash REVIEW_PACKAGE.sh\n'
            'python builder.py prepare --package "$PWD"\n')
        (staging / "REVIEW_PREPARED.sh").write_text(
            '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
            'python builder.py review --package "$PWD"\n')
        for name in ("REVIEW_PACKAGE.sh", "PREPARE_ON_SCC.sh", "REVIEW_PREPARED.sh"):
            (staging / name).chmod(0o755)
        manifest(staging)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, destination)
    print("CPU_ONLY_PACKAGE_CREATED; no SCC operation or GPU job")


def check_package(root):
    root = Path(root).resolve()
    verify_manifest(root)
    spec = yaml.safe_load((root / "source-spec.yaml").read_text())
    validate_spec(spec)
    require(digest(root / "builder.py") == digest(__file__),
            "running a different builder from packaged builder.py")
    return spec


def source_checks(spec):
    source = Path(spec["source"]["prepared"])
    require(source.is_dir(), "accepted Stage P prepared source absent")
    verify_manifest(source, SOURCE_MANIFEST, 344)
    record = json.loads((source / "PREPARED.json").read_text())
    require(record["status"] == "cpu_inputs_prepared_pending_review" and
            record["execution_authorized"] is False and
            record["production_authorized"] is False and
            record["source_inventory_sha256"] == SOURCE_INVENTORY and
            record["source_spec_sha256"] == SOURCE_SPEC and
            record["sif_sha256"] == IMAGE and
            len(record["states"]) == 20, "accepted Stage P metadata changed")
    require(digest(source / "historical-pipeline.yaml") == PIPELINE and
            digest(source / "source-spec.yaml") == SOURCE_SPEC,
            "accepted Stage P recipe changed")
    old_spec = yaml.safe_load((source / "source-spec.yaml").read_text())
    ffroot = old_spec["source"]["pmx_forcefield_root"]
    require(Path(ffroot).is_absolute() and
            (source / "forcefield" / "amber99sb-star-ildn-mut.ff" / "forcefield.itp").is_file(),
            "force-field snapshot or bind root absent")
    cfg = yaml.safe_load((source / "historical-pipeline.yaml").read_text())
    vector = [float(v) for v in cfg["fep"]["lambda_vector"]]
    require(len(vector) == 20 and all(a < b for a, b in zip(vector, vector[1:])),
            "source lambda vector changed")
    common = None
    for index in range(20):
        p = source / "inputs" / "states" / "state{:02d}".format(index)
        require((p / "start.gro").is_file() and (p / "source.mdp").is_file(),
                "source state incomplete")
        values = mdp_values((p / "source.mdp").read_text())
        require(values["init-lambda-state"] == str(index) and
                [float(v) for v in values["fep-lambdas"].split()] == vector and
                values["free-energy"].lower() == "yes" and
                values["calc-lambda-neighbors"] == "-1" and
                float(values["dt"]) == 0.002,
                "source state/physics mismatch")
        comparable = {k: v for k, v in values.items()
                      if k not in ("init-lambda-state", "gen-seed", "ld-seed")}
        if common is None:
            common = comparable
        require(comparable == common, "source state MDPs diverge")
    return source, ffroot, vector


def effective_checks(values, state, vector, spec):
    changes = spec["mdp_changes"]
    require(all(int(values[key]) == value for key, value in changes.items()),
            "effective output/timing MDP mismatch")
    expected = spec["expected_effective_mdp"]
    require(float(values["dt"]) == expected["dt_ps"] and
            values["calc-lambda-neighbors"] == str(expected["calc-lambda-neighbors"]) and
            values["compressed-x-grps"].strip().lower() == "system" and
            float(values["compressed-x-precision"]) == expected["compressed-x-precision"] and
            all(int(values[key]) == 0 for key in ("nstxout", "nstvout", "nstfout")) and
            values["init-lambda-state"] == str(state) and
            [float(v) for v in values["fep-lambdas"].split()] == vector,
            "effective physical/output MDP mismatch")


def container_environment(ffroot):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SINGULARITY", "APPTAINER", "OMPI_", "GMX_", "CUDA_"))}
    for key in ("LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    env["SINGULARITYENV_GMXLIB"] = str(ffroot)
    env["SINGULARITYENV_GMX_MAXBACKUP"] = "-1"
    return env


def run_grompp(root, spec, ffroot, state, started):
    target = root / "prepared" / "common" / "states" / "state{:02d}".format(state)
    inputs = root / "prepared" / "inputs"
    forcefield = root / "prepared" / "forcefield"
    timeout = min(spec["preparation"]["command_timeout_seconds"],
                  spec["preparation"]["total_timeout_seconds"] - (time.monotonic() - started))
    require(timeout > 0, "total CPU preparation deadline expired")
    command = ["singularity", "exec", "--cleanenv", "--contain", "--no-mount",
               "bind-paths,hostfs,cwd,tmp", "--bind", str(inputs) + ":/protein:ro",
               "--bind", str(forcefield) + ":" + ffroot + ":ro",
               "--bind", str(target) + ":/tmp", "--pwd", "/tmp",
               spec["image"]["path"], spec["image"]["gmx"], "grompp",
               "-f", "/protein/states/state{:02d}/scout.mdp".format(state),
               "-c", "/protein/states/state{:02d}/start.gro".format(state),
               "-p", "/protein/system/hybrid.top", "-o", "/tmp/topol.tpr"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=timeout, env=container_environment(ffroot))
    except subprocess.TimeoutExpired as exc:
        (target / "grompp.log").write_text(str(exc) + "\n")
        raise RuntimeError("grompp timeout at state {}".format(state))
    (target / "grompp.log").write_text(result.stdout)
    require(result.returncode == 0 and not re.search(r"^\s*WARNING", result.stdout, re.M),
            "grompp failed/warned at state {}".format(state))
    require((target / "topol.tpr").is_file() and (target / "mdout.mdp").is_file(),
            "grompp outputs absent at state {}".format(state))
    effective_checks(mdp_values((target / "mdout.mdp").read_text()), state,
                     spec["_vector"], spec)
    return {"state": state, "tpr_sha256": digest(target / "topol.tpr"),
            "mdout_sha256": digest(target / "mdout.mdp"),
            "grompp_notes": len(re.findall(r"^NOTE\s+\d+", result.stdout, re.M))}


def prepare(root):
    root = Path(root).resolve()
    spec = check_package(root)
    require(not (root / "prepared").exists(), "refusing to overwrite prepared inputs")
    source, ffroot, vector = source_checks(spec)
    require(digest(spec["image"]["path"]) == IMAGE, "r6 SIF hash mismatch")
    started = time.monotonic()
    prepared = root / "prepared"
    prepared.mkdir()
    shutil.copy2(source / "historical-pipeline.yaml", prepared / "historical-pipeline.yaml")
    inputs = prepared / "inputs"
    (inputs / "system").mkdir(parents=True)
    for name in ("hybrid.top", "posre.itp"):
        shutil.copy2(source / "inputs" / "system" / name, inputs / "system" / name)
    shutil.copytree(source / "forcefield", prepared / "forcefield")
    for state in range(20):
        original = source / "inputs" / "states" / "state{:02d}".format(state)
        target = inputs / "states" / "state{:02d}".format(state)
        target.mkdir(parents=True)
        shutil.copy2(original / "start.gro", target / "start.gro")
        shutil.copy2(original / "source.mdp", target / "source.mdp")
        (target / "scout.mdp").write_text(scout_mdp((target / "source.mdp").read_text()))
    spec["_vector"] = vector
    rows = []
    for state in range(20):
        target = prepared / "common" / "states" / "state{:02d}".format(state)
        target.mkdir(parents=True)
        row = run_grompp(root, spec, ffroot, state, started)
        rows.append(row)
        for arm in ("baseline", "hrex"):
            copy = prepared / "arms" / arm / "states" / "state{:02d}".format(state)
            copy.mkdir(parents=True)
            shutil.copy2(target / "topol.tpr", copy / "topol.tpr")
            require(digest(copy / "topol.tpr") == row["tpr_sha256"],
                    "paired TPR copy mismatch")
        print("state={} scout_tpr_sha256={}".format(state, row["tpr_sha256"]), flush=True)
    record = {"status": "cpu_inputs_prepared_pending_review", "scope": spec["scope"],
              "execution_authorized": False, "production_authorized": False,
              "package_spec_sha256": digest(root / "source-spec.yaml"),
              "source_manifest_sha256": SOURCE_MANIFEST,
              "source_inventory_sha256": SOURCE_INVENTORY,
              "sif_sha256": IMAGE, "states": rows,
              "elapsed_seconds": time.monotonic() - started}
    (prepared / "PREPARED.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    count = manifest(prepared)
    print("prepared_manifest_entries={}".format(count), flush=True)
    print("F64A_C2_PAIRED_SCOUT_TPRS_CPU_PREPARED_PENDING_REVIEW; no job submitted", flush=True)


def review(root):
    root = Path(root).resolve()
    spec = check_package(root)
    prepared = root / "prepared"
    require(prepared.is_dir(), "prepared inputs absent")
    count = verify_manifest(prepared)
    record = json.loads((prepared / "PREPARED.json").read_text())
    require(record["status"] == "cpu_inputs_prepared_pending_review" and
            record["scope"] == spec["scope"] and
            record["execution_authorized"] is False and
            record["production_authorized"] is False and
            record["package_spec_sha256"] == digest(root / "source-spec.yaml") and
            record["source_manifest_sha256"] == SOURCE_MANIFEST and
            record["source_inventory_sha256"] == SOURCE_INVENTORY and
            record["sif_sha256"] == IMAGE and len(record["states"]) == 20,
            "prepared record mismatch")
    pipeline = prepared / "historical-pipeline.yaml"
    require(digest(pipeline) == PIPELINE, "prepared pipeline identity mismatch")
    vector = [float(v) for v in yaml.safe_load(pipeline.read_text())["fep"]["lambda_vector"]]
    for state, row in enumerate(record["states"]):
        require(row["state"] == state, "state order mismatch")
        name = "state{:02d}".format(state)
        inputs = prepared / "inputs" / "states" / name
        require((inputs / "start.gro").is_file() and
                (inputs / "scout.mdp").read_text() ==
                scout_mdp((inputs / "source.mdp").read_text()),
                "scout input changed from sealed source")
        common = prepared / "common" / "states" / name
        require(digest(common / "topol.tpr") == row["tpr_sha256"] and
                digest(common / "mdout.mdp") == row["mdout_sha256"],
                "common TPR/MDOUT identity mismatch")
        effective_checks(mdp_values((common / "mdout.mdp").read_text()), state, vector, spec)
        for arm in ("baseline", "hrex"):
            require(digest(prepared / "arms" / arm / "states" / name / "topol.tpr") ==
                    row["tpr_sha256"], "paired TPR mismatch")
    print("F64A_C2_PAIRED_SCOUT_CPU_REVIEW_PASS states=20 manifest_entries={} execution_authorized=False".format(count))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("package")
    create.add_argument("--destination", type=Path, required=True)
    create.add_argument("--spec", type=Path, default=SPEC)
    for name in ("verify-package", "prepare", "review"):
        p = sub.add_parser(name)
        p.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "package":
        package(args.destination, args.spec)
    elif args.command == "verify-package":
        check_package(args.package)
        print("CPU_ONLY_PACKAGE_VERIFIED; no job submitted")
    elif args.command == "prepare":
        prepare(args.package)
    else:
        review(args.package)


if __name__ == "__main__":
    main()
