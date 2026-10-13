"""CPU-only exact-r6 grompp/dump rehearsal from accepted Stage P checkpoints.

This creates two short, unexecuted continuation TPR sets. It never invokes
mdrun, a scheduler, MPI launch, MPS, or GPU passthrough. Stage P checkpoints
had exchange; this rehearses branch mechanics, not the selected ancestry.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

try:
    import branch_input_checker as checks
except ImportError:
    from src.analysis import f64a_c2_branch_input_checks as checks


SOURCE_MANIFEST = "858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9"
SOURCE_ENTRIES = 344
PACKAGE_SCOPE = "f64a_c2_stage_p_checkpoint_branch_cpu_rehearsal"
SOURCE_PREPARED = "/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1/prepared"
SOURCE_ATTEMPT = "/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-runtime-20260928-v1/attempt"
IMAGE_PATH = "/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gromacs-2025.3-mpi-cuda-l40s.sif"
FORCEFIELD_ROOT = "/projectnb/rise-batteries/bode/.conda/envs/sod1-fep/lib/python3.11/site-packages/pmx/data/mutff"
LAMBDAS = [0.0, 0.0588, 0.1176, 0.1765, 0.2353, 0.2941, 0.3529,
           0.4118, 0.4706, 0.5294, 0.5882, 0.6471, 0.7059, 0.7647,
           0.8235, 0.8824, 0.92, 0.95, 0.975, 1.0]
TPR_LINES = re.compile(r"^\s*(?:natoms|nsteps|init-step|init-lambda-state|"
                       r"n-lambdas|calc-lambda-neighbors|dt|fep-lambdas)\s*=|"
                       r"^\s*all-lambdas:")
CHECKPOINT_LINES = re.compile(r"^\s*(?:step|t|simulation part #|fep_state\[0\])\s*=")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return checks.sha256(Path(path))


def hashlib_sha_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def verify_manifest(root, expected, count):
    manifest = root / "SHA256SUMS"
    require(manifest.is_file() and sha(manifest) == expected,
            "accepted prepared manifest identity mismatch")
    rows = manifest.read_text().splitlines()
    require(len(rows) == count, "prepared manifest entry count mismatch")
    seen = set()
    for row in rows:
        digest, sep, name = row.partition("  ")
        require(sep and re.fullmatch(r"[0-9a-f]{64}", digest) and name not in seen,
                "invalid prepared manifest row")
        seen.add(name)
        require(sha(checks.file_under(root, name)) == digest,
                "prepared source file changed: " + name)


def verify_package(root, cfg):
    require(cfg == json.loads((root / "config.json").read_text()), "package config changed")
    records = (root / "SHA256SUMS").read_text().splitlines()
    require(len(records) == 7, "package manifest count mismatch")
    seen = set()
    for row in records:
        digest, sep, name = row.partition("  ")
        require(sep and re.fullmatch(r"[0-9a-f]{64}", digest) and
                name not in seen and
                sha(checks.file_under(root, name)) == digest,
                "package manifest mismatch: " + name)
        seen.add(name)
    require(seen == {"PREPARE_ON_SCC.sh", "README.txt", "REVIEW_PACKAGE.sh",
                     "REVIEW_PREPARED.sh", "branch_input_checker.py", "builder.py",
                     "config.json"}, "package file set mismatch")
    require(cfg["schema_version"] == 1 and cfg["scope"] == PACKAGE_SCOPE and
            cfg["execution_authorized"] is False and
            cfg["production_authorized"] is False and
            cfg["image_sha256"] == checks.IMAGE_SHA256 and
            cfg["source_manifest_sha256"] == SOURCE_MANIFEST and
            cfg["source_manifest_entries"] == SOURCE_ENTRIES and
            cfg["job_id"] == "7791102" and
            cfg["checkpoint_step"] == 2000 and cfg["checkpoint_time_ps"] == 4.0 and
            cfg["checkpoint_part"] == 2 and cfg["branch_part"] == 3 and
            cfg["dt_ps"] == 0.002 and cfg["atom_count"] == 38414 and
            cfg["retained_steps"] == {"baseline": 1000, "hrex": 500} and
            cfg["output_strides"] == {"nstdhdl": 100, "nstenergy": 100,
                                      "nstxout-compressed": 200} and
            cfg["lambda_vector"] == LAMBDAS and
            cfg["source_prepared"] == SOURCE_PREPARED and
            cfg["source_attempt"] == SOURCE_ATTEMPT and
            cfg["image_path"] == IMAGE_PATH and
            cfg["forcefield_root"] == FORCEFIELD_ROOT and
            cfg["command_timeout_seconds"] == 180 and
            cfg["total_timeout_seconds"] == 1800,
            "CPU rehearsal scope changed")
    for key in ("source_prepared", "source_attempt", "image_path", "forcefield_root"):
        require(Path(cfg[key]).is_absolute(), "absolute source path required: " + key)


def write_prepared_manifest(output):
    rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            rows.append("{}  {}\n".format(sha(path), path.relative_to(output)))
    (output / "SHA256SUMS").write_text("".join(rows))
    return len(rows)


def verify_prepared_manifest(output):
    rows = (output / "SHA256SUMS").read_text().splitlines()
    recorded = set()
    for row in rows:
        digest, sep, name = row.partition("  ")
        require(sep and re.fullmatch(r"[0-9a-f]{64}", digest) and
                name not in recorded and sha(checks.file_under(output, name)) == digest,
                "prepared manifest mismatch: " + name)
        recorded.add(name)
    actual = {str(path.relative_to(output)) for path in output.rglob("*")
              if path.is_file() and path.name != "SHA256SUMS"}
    require(recorded == actual, "prepared file set changed")
    return len(rows)


def source_checks(cfg):
    source = Path(cfg["source_prepared"])
    attempt = Path(cfg["source_attempt"])
    verify_manifest(source, SOURCE_MANIFEST, SOURCE_ENTRIES)
    require(sha(cfg["image_path"]) == checks.IMAGE_SHA256, "r6 image hash mismatch")
    status = json.loads((attempt / "status.json").read_text())
    require(status.get("job_id") == cfg["job_id"] and
            status.get("technical_status") == "pass_pending_review_and_accounting" and
            status.get("restart_verified") is True and
            status.get("mps_cleanup_confirmed") is True and
            status.get("production_authorized") is False and
            status.get("failure") is None,
            "accepted Stage P attempt status mismatch")
    inventory = json.loads((attempt / "output-hashes.json").read_text())
    require(isinstance(inventory, dict), "Stage P output hash inventory missing")
    for state, name in enumerate(checks.STATE_NAMES):
        for filename in ("smoke.cpt", "checkpoint.dump"):
            relative = name + "/" + filename
            path = checks.file_under(attempt, relative)
            require(inventory.get(relative) == sha(path),
                    "Stage P saved output hash mismatch: " + relative)
        checks.checkpoint_metadata(
            (attempt / name / "checkpoint.dump").read_text(), state,
            {"prep_step": cfg["checkpoint_step"],
             "prep_time_ps": cfg["checkpoint_time_ps"],
             "prep_checkpoint_part": cfg["checkpoint_part"]})
        origin = source / "inputs" / "states" / name
        mdp = checks.mdp_values((origin / "technical.mdp").read_text())
        require(int(mdp["init-lambda-state"]) == state and
                int(mdp["nsteps"]) == cfg["checkpoint_step"] and
                [float(x) for x in mdp["fep-lambdas"].split()] ==
                cfg["lambda_vector"], "Stage P state MDP mismatch: " + name)
        with (origin / "start.gro").open() as stream:
            stream.readline()
            require(int(stream.readline().strip()) == cfg["atom_count"],
                    "Stage P atom count mismatch: " + name)
    require((source / "forcefield" / "amber99sb-star-ildn-mut.ff" /
             "forcefield.itp").is_file(), "accepted force-field snapshot missing")
    return source, attempt


def continuation_mdp(original, cfg, arm):
    """Change only continuation bookkeeping and the technical arm length."""
    before = checks.mdp_values(original)
    require(int(before["nsteps"]) == cfg["checkpoint_step"],
            "original TPR schedule drift")
    changes = {"nsteps": str(cfg["retained_steps"][arm]),
               "init-step": str(cfg["checkpoint_step"]),
               "tinit": "0", "simulation-part": str(cfg["branch_part"]),
               "gen-vel": "no", "continuation": "yes"}
    output = ["; Stage P checkpoint branch CPU rehearsal; never execute this TPR"]
    replaced = set()
    for line in original.splitlines():
        body, sep, comment = line.partition(";")
        if "=" in body:
            key, _ = body.split("=", 1)
            normalized = key.strip().lower().replace("_", "-")
            if normalized in changes:
                line = key + "= " + changes[normalized]
                if sep:
                    line += ";" + comment
                replaced.add(normalized)
        output.append(line)
    for key in changes:
        if key not in replaced:
            output.append(key + " = " + changes[key])
    rendered = "\n".join(output) + "\n"
    after = checks.mdp_values(rendered)
    require(set(after) == set(before) | set(changes) and all(
        after[key] == (changes[key] if key in changes else value)
        for key, value in before.items()), "unregistered source MDP change")
    return rendered


def container_env(cfg):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SINGULARITY", "APPTAINER", "OMPI_", "GMX_", "CUDA_"))}
    for key in ("LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    env["SINGULARITYENV_GMXLIB"] = cfg["forcefield_root"]
    env["SINGULARITYENV_OMPI_MCA_orte_tmpdir_base"] = "/tmp"
    env["SINGULARITYENV_GMX_MAXBACKUP"] = "-1"
    env["SINGULARITYENV_OMP_NUM_THREADS"] = "1"
    return env


def container_base(cfg, source, output, private_tmp):
    return ["singularity", "exec", "--cleanenv", "--contain", "--no-mount",
            "bind-paths,hostfs,cwd,tmp", "--bind", str(source) + ":/protein:ro",
            "--bind", str(source / "forcefield") + ":" + cfg["forcefield_root"] + ":ro",
            "--bind", str(output / "arms") + ":/branches",
            "--bind", str(output / "mdps") + ":/branch-mdp:ro",
            "--bind", str(private_tmp) + ":/tmp", "--pwd", "/tmp", cfg["image_path"],
            "/opt/gromacs/2025.3/bin/gmx_mpi"]


def run_cpu(argv, cfg, started):
    remaining = cfg["total_timeout_seconds"] - (time.monotonic() - started)
    require(remaining > 0, "CPU rehearsal deadline expired")
    try:
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True, env=container_env(cfg),
                                timeout=min(remaining, cfg["command_timeout_seconds"]))
    except subprocess.TimeoutExpired as exc:
        raise ValueError("GROMACS CPU command timed out") from exc
    return result


def selected_dump(text, pattern):
    return "\n".join(line for line in text.splitlines() if pattern.match(line)) + "\n"


def prepare(root, cfg):
    root = Path(root).resolve()
    verify_package(root, cfg)
    require(not os.environ.get("JOB_ID"), "CPU rehearsal must run outside an SGE job")
    output = root / "prepared"
    require(not output.exists(), "preserve existing prepared evidence")
    source, attempt = source_checks(cfg)
    output.mkdir()
    (output / "arms").mkdir()
    (output / "mdps").mkdir()
    (output / "common").mkdir()
    started = time.monotonic()
    hashes = {}
    dump_records = {}
    with tempfile.TemporaryDirectory(prefix="c2-cpu-branch.", dir="/tmp") as tmp:
        private_tmp = Path(tmp)
        base = container_base(cfg, source, output, private_tmp)
        for state, name in enumerate(checks.STATE_NAMES):
            common = output / "common" / name
            common.mkdir()
            shutil.copy2(attempt / name / "smoke.cpt", common / "start.cpt")
            hashes[name] = sha(common / "start.cpt")
            # Dump the copied binary with the exact image, not only the saved Stage P text.
            command = base + ["dump", "-cp", "/branches/baseline/" + name + "/start.cpt"]
            baseline = output / "arms" / "baseline" / name
            hrex = output / "arms" / "hrex" / name
            baseline.mkdir(parents=True)
            hrex.mkdir(parents=True)
            for arm_dir in (baseline, hrex):
                shutil.copy2(common / "start.cpt", arm_dir / "start.cpt")
            result = run_cpu(command, cfg, started)
            require(result.returncode == 0 and
                    not re.search(r"^\s*WARNING", result.stdout, re.M),
                    "checkpoint dump failed/warned: " + name)
            selected = selected_dump(result.stdout, CHECKPOINT_LINES)
            checks.checkpoint_metadata(selected, state, {
                "prep_step": cfg["checkpoint_step"],
                "prep_time_ps": cfg["checkpoint_time_ps"],
                "prep_checkpoint_part": cfg["checkpoint_part"]})
            (common / "start.cpt.dump").write_text(selected)
            dump_records[name + "/checkpoint"] = {
                "full_output_sha256": hashlib_sha_text(result.stdout),
                "full_output_bytes": len(result.stdout.encode()),
                "selected_sha256": hashlib_sha_text(selected),
                "argv": command}
            for arm_dir in (baseline, hrex):
                (arm_dir / "start.cpt.dump").write_text(selected)
            for arm in checks.ARMS:
                arm_dir = output / "arms" / arm / name
                mdp_dir = output / "mdps" / arm
                mdp_dir.mkdir(exist_ok=True)
                (mdp_dir / (name + ".mdp")).write_text(continuation_mdp(
                    (source / "inputs" / "states" / name / "technical.mdp").read_text(),
                    cfg, arm))
                command = base + ["grompp", "-f", "/branch-mdp/" + arm + "/" + name + ".mdp",
                                  "-c", "/protein/inputs/states/" + name + "/start.gro",
                                  "-p", "/protein/inputs/system/hybrid.top",
                                  "-t", "/branches/" + arm + "/" + name + "/start.cpt",
                                  "-o", "/branches/" + arm + "/" + name + "/topol.tpr",
                                  "-po", "/branches/" + arm + "/" + name + "/mdout.mdp"]
                result = run_cpu(command, cfg, started)
                (arm_dir / "grompp.log").write_text(result.stdout)
                save_json(arm_dir / "grompp-result.json", {
                    "argv": command, "exit_status": result.returncode})
                require(result.returncode == 0 and
                        not re.search(r"^\s*WARNING", result.stdout, re.M),
                        "grompp failed/warned: {} {}".format(arm, name))
                require((arm_dir / "topol.tpr").is_file() and
                        (arm_dir / "mdout.mdp").is_file(),
                        "grompp output missing: {} {}".format(arm, name))
                dump = run_cpu(base + ["dump", "-s", "/branches/" + arm + "/" +
                                       name + "/topol.tpr"], cfg, started)
                require(dump.returncode == 0 and
                        not re.search(r"^\s*WARNING", dump.stdout, re.M),
                        "TPR dump failed/warned: {} {}".format(arm, name))
                (arm_dir / "topol.tpr.dump").write_text(
                    selected_dump(dump.stdout, TPR_LINES))
                dump_records[arm + "/" + name + "/tpr"] = {
                    "full_output_sha256": hashlib_sha_text(dump.stdout),
                    "full_output_bytes": len(dump.stdout.encode()),
                    "selected_sha256": sha(arm_dir / "topol.tpr.dump"),
                    "argv": base + ["dump", "-s", "/branches/" + arm + "/" +
                                    name + "/topol.tpr"]}
            print("state={} checkpoint_sha256={}".format(state, hashes[name]), flush=True)
    plan = {"schema_version": 1, "scope": checks.SCOPE,
            "execution_authorized": False, "production_authorized": False,
            "image_path": cfg["image_path"], "image_sha256": cfg["image_sha256"],
            "state_count": 20, "atom_count": cfg["atom_count"],
            "prep_step": cfg["checkpoint_step"],
            "prep_time_ps": cfg["checkpoint_time_ps"],
            "prep_checkpoint_part": cfg["checkpoint_part"],
            "branch_simulation_part": cfg["branch_part"], "dt_ps": cfg["dt_ps"],
            "retained_steps": cfg["retained_steps"],
            "lambda_vector": cfg["lambda_vector"],
            "output_strides": cfg["output_strides"],
            "checkpoint_sha256": hashes}
    save_json(output / "plan.json", plan)
    save_json(output / "dump-provenance.json", dump_records)
    checks.review(output, plan)
    save_json(output / "REHEARSAL.json", {
        "status": "cpu_rehearsal_prepared_pending_independent_review",
        "stage_p_job_id": cfg["job_id"],
        "source_manifest_sha256": SOURCE_MANIFEST,
        "stage_p_output_hashes_sha256": sha(attempt / "output-hashes.json"),
        "image_sha256": cfg["image_sha256"],
        "execution_authorized": False, "production_authorized": False,
        "elapsed_seconds": time.monotonic() - started})
    count = write_prepared_manifest(output)
    print("prepared_manifest_entries={}".format(count))
    print("C2_STAGE_P_CHECKPOINT_CPU_REHEARSAL_PREPARED; no job submitted")


def review(root, cfg):
    root = Path(root).resolve()
    verify_package(root, cfg)
    _, attempt = source_checks(cfg)
    output = root / "prepared"
    count = verify_prepared_manifest(output)
    record = json.loads((output / "REHEARSAL.json").read_text())
    require(record["status"] == "cpu_rehearsal_prepared_pending_independent_review" and
            record["stage_p_job_id"] == cfg["job_id"] and
            record["source_manifest_sha256"] == SOURCE_MANIFEST and
            record["stage_p_output_hashes_sha256"] == sha(attempt / "output-hashes.json") and
            record["image_sha256"] == cfg["image_sha256"] and
            record["execution_authorized"] is False and
            record["production_authorized"] is False,
            "rehearsal record mismatch")
    plan = json.loads((output / "plan.json").read_text())
    dumps = json.loads((output / "dump-provenance.json").read_text())
    expected_dump_keys = {name + "/checkpoint" for name in checks.STATE_NAMES} | {
        arm + "/" + name + "/tpr" for arm in checks.ARMS
        for name in checks.STATE_NAMES}
    require(set(dumps) == expected_dump_keys, "dump provenance coverage mismatch")
    for state, name in enumerate(checks.STATE_NAMES):
        entry = dumps[name + "/checkpoint"]
        require(entry["selected_sha256"] == sha(output / "common" / name /
                                                 "start.cpt.dump"),
                "checkpoint dump provenance mismatch")
        for arm in checks.ARMS:
            entry = dumps[arm + "/" + name + "/tpr"]
            require(entry["selected_sha256"] == sha(output / "arms" / arm / name /
                                                     "topol.tpr.dump"),
                    "TPR dump provenance mismatch")
    checks.review(output, plan)
    print("C2_STAGE_P_CHECKPOINT_CPU_REHEARSAL_REVIEW_PASS manifest_entries={}; no job submitted".format(count))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify-package", "prepare", "review"))
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    root = args.package.resolve()
    cfg = json.loads((root / "config.json").read_text())
    if args.command == "verify-package":
        verify_package(root, cfg)
        print("C2_STAGE_P_CPU_REHEARSAL_PACKAGE_VERIFIED; no job submitted")
    elif args.command == "prepare":
        prepare(root, cfg)
    else:
        review(root, cfg)


if __name__ == "__main__":
    main()
