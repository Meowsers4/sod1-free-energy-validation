"""CPU-only source, image, queue and storage preflight; never submits a job.

Python 3.6+ for the SCC system interpreter. The package remains inactive:
there is no mdrun, GPU passthrough, MPI launch or submission entry point.
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
from datetime import datetime, timezone


FILES = {"README.txt", "REVIEW_PACKAGE.sh", "PREFLIGHT_ON_SCC.sh",
         "config.json", "preflight.py"}
EXPECTED_SCOPE = "f64a_c2_live_branch_fixture_preflight"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_file(root, relative):
    name = Path(relative)
    require(not name.is_absolute() and name.parts and ".." not in name.parts,
            "invalid manifest path: " + relative)
    current = root
    for part in name.parts:
        current = current / part
        require(not current.is_symlink(), "symlink in manifest path: " + relative)
    require(current.is_file(), "manifest file missing: " + relative)
    return current


def verify_manifest(root, expected_digest=None, expected_count=None, exact_names=None):
    root = Path(root)
    manifest = root / "SHA256SUMS"
    require(manifest.is_file() and not manifest.is_symlink(), "manifest missing")
    digest = sha(manifest)
    if expected_digest is not None:
        require(digest == expected_digest, "manifest SHA-256 mismatch")
    rows = manifest.read_text().splitlines()
    if expected_count is not None:
        require(len(rows) == expected_count, "manifest entry count mismatch")
    names = set()
    for row in rows:
        recorded, separator, name = row.partition("  ")
        require(separator and re.fullmatch(r"[0-9a-f]{64}", recorded) and
                name not in names, "invalid/duplicate manifest row")
        names.add(name)
        require(sha(safe_file(root, name)) == recorded,
                "manifest content changed: " + name)
    if exact_names is not None:
        require(names == exact_names, "package file set mismatch")
    return digest, len(rows)


def config_at(root):
    cfg = json.loads((Path(root) / "config.json").read_text())
    require(cfg.get("schema_version") == 1 and
            cfg.get("scope") == EXPECTED_SCOPE and
            cfg.get("execution_authorized") is False and
            cfg.get("production_authorized") is False and
            cfg.get("source_manifest_sha256") ==
            "858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9" and
            cfg.get("image_sha256") ==
            "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee" and
            cfg.get("source_manifest_entries") == 344 and
            cfg.get("expected_source_nsteps") == 2000 and
            cfg.get("expected_dt_ps") == 0.002 and
            cfg.get("expected_atom_count") == 38414 and
            len(cfg.get("expected_lambdas", [])) == 20 and
            cfg.get("project") == "rise-batteries" and
            cfg.get("queue") == "l40s" and
            cfg.get("pe") == "omp16" and cfg.get("slots") == 16 and
            cfg.get("gpus") == 1 and cfg.get("gpu_type") == "L40S" and
            cfg.get("ranks") == 20 and cfg.get("walltime") == "00:30:00" and
            cfg.get("min_project_quota_free_bytes") == 3221225472 and
            cfg.get("min_filesystem_free_bytes") == 3221225472,
            "preflight scope/resources changed")
    for key in ("source_prepared", "image_path", "persistent_root"):
        require(Path(cfg[key]).is_absolute(), "absolute path required: " + key)
    require(cfg["persistent_root"].startswith("/project/rise-batteries/"),
            "persistent root must be on /project")
    return cfg


def mdp_values(path):
    values = {}
    for line in Path(path).read_text().splitlines():
        body = line.split(";", 1)[0]
        if "=" not in body:
            continue
        key, value = body.split("=", 1)
        key = key.strip().lower().replace("_", "-")
        require(key and key not in values, "duplicate/empty MDP field")
        values[key] = value.strip()
    return values


def source_review(cfg):
    source = Path(cfg["source_prepared"])
    require(source.is_dir() and not source.is_symlink(), "source prepared tree missing")
    digest, count = verify_manifest(
        source, cfg["source_manifest_sha256"], cfg["source_manifest_entries"])
    require(sha(source / "source-spec.yaml") == cfg["source_spec_sha256"],
            "source spec changed")
    record = json.loads((source / "PREPARED.json").read_text())
    require(record.get("status") == "cpu_inputs_prepared_pending_review" and
            record.get("execution_authorized") is False and
            record.get("production_authorized") is False and
            record.get("sif_sha256") == cfg["image_sha256"] and
            record.get("source_spec_sha256") == cfg["source_spec_sha256"] and
            len(record.get("states", [])) == 20,
            "source record/status mismatch")
    identities = []
    for state in range(20):
        name = "state{:02d}".format(state)
        row = record["states"][state]
        tpr = source / "states" / name / "topol.tpr"
        mdp = source / "inputs" / "states" / name / "technical.mdp"
        gro = source / "inputs" / "states" / name / "start.gro"
        require(row.get("state") == state and row.get("tpr_sha256") == sha(tpr),
                "TPR provenance mismatch: " + name)
        values = mdp_values(mdp)
        require(int(values["init-lambda-state"]) == state and
                int(values["nsteps"]) == cfg["expected_source_nsteps"] and
                float(values["dt"]) == cfg["expected_dt_ps"] and
                values["free-energy"].lower() == "yes" and
                int(values["calc-lambda-neighbors"]) == -1 and
                [float(x) for x in values["fep-lambdas"].split()] ==
                cfg["expected_lambdas"], "source MDP mismatch: " + name)
        with gro.open() as stream:
            stream.readline()
            require(int(stream.readline().strip()) == cfg["expected_atom_count"],
                    "source atom count mismatch: " + name)
            identities.append(tuple(line[:20] for line in
                                    (stream.readline() for _ in
                                     range(cfg["expected_atom_count"]))))
        print("state={} initial_tpr_sha256={}".format(state, row["tpr_sha256"]),
              flush=True)
    require(all(item == identities[0] for item in identities),
            "source atom identity/order differs across states")
    image = Path(cfg["image_path"])
    require(image.is_file() and not image.is_symlink() and
            sha(image) == cfg["image_sha256"], "exact-r6 image mismatch")
    return {"source_manifest_sha256": digest, "source_manifest_entries": count,
            "image_sha256": cfg["image_sha256"], "states": 20,
            "atom_count": cfg["expected_atom_count"]}


def quota_summary(text, cfg):
    target = "/project/" + cfg["project"]
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == target:
            require(len(fields) == 5, "unexpected project quota format")
            quota_gb, quota_files, usage_gb, usage_files = (
                float(fields[1]), int(fields[2]), float(fields[3]), int(fields[4]))
            free = int((quota_gb - usage_gb) * 10**9)
            require(free >= cfg["min_project_quota_free_bytes"] and
                    usage_files < quota_files,
                    "insufficient /project quota or file allowance")
            return {"quota_gb": quota_gb, "usage_gb": usage_gb,
                    "quota_files": quota_files, "usage_files": usage_files,
                    "free_quota_bytes_estimated": free}
    raise ValueError("/project quota row missing")


def queue_validation(cfg):
    descriptor, probe = tempfile.mkstemp(prefix="c2-branch-queue.", dir="/tmp")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write("#!/bin/bash\nexit 0\n")
        command = ["qsub", "-clear", "-hard", "-P", cfg["project"],
                   "-q", cfg["queue"], "-pe", cfg["pe"], str(cfg["slots"]),
                   "-l", "gpus=1,gpu_type=L40S,h_rt=" + cfg["walltime"],
                   "-r", "n", "-N", "c2-branch-preflight", "-S", "/bin/bash",
                   "-cwd", "-j", "y", "-w", "v", probe]
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, universal_newlines=True,
                                timeout=60)
        require(result.returncode == 0 and
                "verification: found suitable queue(s)" in result.stdout,
                "exact-request queue verification failed: " + result.stdout)
        return {"command": command, "output": result.stdout.strip(),
                "validation_only": True}
    finally:
        os.unlink(probe)


def run(root, cfg):
    require(not os.environ.get("JOB_ID"), "preflight must run on login node")
    output = root / "preflight.json"
    require(not output.exists(), "preserve existing preflight evidence")
    source = source_review(cfg)
    queue = queue_validation(cfg)
    quota = subprocess.run(["pquota", cfg["project"]],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True, timeout=30)
    require(quota.returncode == 0, "pquota failed: " + quota.stdout)
    project_root = Path("/project") / cfg["project"]
    require(os.access(str(project_root), os.W_OK) and
            os.access(cfg["persistent_root"], os.W_OK),
            "project output root not writable")
    free_fs = shutil.disk_usage(str(project_root)).free
    require(free_fs >= cfg["min_filesystem_free_bytes"],
            "insufficient /project filesystem free space")
    record = {"status": "preflight_pass_pending_fixture_selection",
              "execution_authorized": False, "production_authorized": False,
              "utc": datetime.now(timezone.utc).isoformat(),
              "package_manifest_sha256": sha(root / "SHA256SUMS"),
              "source": source, "queue": queue,
              "project_quota": quota_summary(quota.stdout, cfg),
              "project_filesystem_free_bytes": free_fs,
              "persistent_root_writable": True,
              "su_balance": "unknown_not_waived_for_this_fixture"}
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("queue_validation=pass; one_L40S_omp16_16_slots_00:30:00; no_job_submitted")
    print("project_usage_gb={:.2f} project_quota_gb={:.0f}".format(
        record["project_quota"]["usage_gb"],
        record["project_quota"]["quota_gb"]))
    print("project_filesystem_free_bytes={}".format(free_fs))
    print("C2_BRANCH_FIXTURE_PREFLIGHT_PASS_PENDING_SELECTION; no job submitted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify-package", "run"))
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    root = args.package.resolve()
    cfg = config_at(root)
    verify_manifest(root, exact_names=FILES)
    if args.command == "run":
        run(root, cfg)
    else:
        print("C2_BRANCH_FIXTURE_PREFLIGHT_PACKAGE_VERIFIED; no job submitted")


if __name__ == "__main__":
    main()
