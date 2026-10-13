"""Review and stage the paired C2 timing-scout runtime candidate (Python 3.8+).

This revision deliberately has no scheduler submission or GPU execution entry
point. A selected successor must add those after the CPU import and audit are
reviewed. All SCC operations exposed here are read-only or CPU file copies.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

import yaml


SPEC = Path("docs/f64a_c2_scout_runtime_v1.yaml")
RESULT = Path("docs/f64a_c2_scout_cpu_result.md")
MANIFEST_HASH = "cffefe198d66e670ebc7db2960039e2cfc159e64bb238af7d5c3fe13c7f64487"
SPEC_HASH = "50d2964cfef6ca95091ae05c390e3f7626dc66028d0599bdb28f05c11520cb60"
IMAGE_HASH = "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee"
PACKAGE_MARKER = "F64A_C2_SCOUT_RUNTIME_CANDIDATE_CPU_ONLY"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def manifest(directory):
    directory = Path(directory)
    rows = ["{}  {}\n".format(sha(p), p.relative_to(directory))
            for p in sorted(directory.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("".join(rows))
    return len(rows)


def verify_manifest(directory, expected_hash=None, expected_count=None):
    directory = Path(directory)
    path = directory / "SHA256SUMS"
    require(path.is_file() and not path.is_symlink(), "manifest absent")
    if expected_hash:
        require(sha(path) == expected_hash, "manifest hash mismatch")
    rows = path.read_text().splitlines()
    if expected_count is not None:
        require(len(rows) == expected_count, "manifest count mismatch")
    seen = set()
    for row in rows:
        digest, sep, name = row.partition("  ")
        rel = Path(name)
        require(sep and re.fullmatch("[0-9a-f]{64}", digest) and name not in seen and
                not rel.is_absolute() and ".." not in rel.parts, "invalid manifest row")
        seen.add(name)
        p = directory / rel
        require(p.is_file() and not p.is_symlink() and sha(p) == digest,
                "file hash mismatch: " + name)
    return len(rows)


def accepted_hashes(result):
    rows = re.findall(r"^\| (\d+) \| `([0-9a-f]{64})` \|$", result, re.M)
    require([int(number) for number, _ in rows] == list(range(20)),
            "accepted TPR table is incomplete")
    return [value for _, value in rows]


def validate_contract(spec):
    require(spec["schema_version"] == 1 and
            spec["scope"] == "f64a_folded_apo_2sh_r0_paired_timing_scout_runtime_candidate" and
            spec["execution_authorized"] is False and
            spec["production_authorized"] is False, "execution scope changed")
    source = spec["prepared_source"]
    require(source["manifest_sha256"] == MANIFEST_HASH and
            source["manifest_entries"] == 381 and
            source["source_spec_sha256"] == SPEC_HASH, "CPU input identity changed")
    require(spec["image"]["sha256"] == IMAGE_HASH, "image identity changed")
    s = spec["scheduler"]
    require((s["project"], s["queue"], s["pe"], s["slots"], s["gpus"],
             s["gpu_type"], s["ranks"], s["threads"]) ==
            ("rise-batteries", "l40s", "omp16", 16, 1, "L40S", 20, 1),
            "allocation geometry changed")
    require((s["walltime_seconds_per_arm"], s["work_deadline_seconds_per_arm"],
             s["attempts_per_arm"], s["stop_bytes_per_location"],
             s["cap_bytes_per_location"], s["minimum_free_bytes_per_location"]) ==
            (7200, 6300, 1, 805306368, 1073741824, 3221225472),
            "time or storage bounds changed")
    require(spec["sharing"] == {"mode": "private_MPS", "cpu_affinity_count": 16,
                                "mpi_yield_when_idle": 1}, "sharing mode changed")
    f = spec["scout"]
    require(f == {"nsteps": 50000, "dt_ps": 0.002, "output_stride": 500,
                  "coordinate_stride": 25000, "log_stride": 5000,
                  "checkpoint_minutes": 15, "baseline_replex": 0,
                  "hrex_replex": 500, "hrex_seed": 20260929,
                  "arm_order": ["baseline", "hrex"], "no_planned_restart": True,
                  "no_automatic_retry": True}, "scout schedule changed")
    hashes = spec["accepted_tpr_sha256"]
    require(len(hashes) == 20 and all(re.fullmatch("[0-9a-f]{64}", x) for x in hashes),
            "invalid TPR hash list")


def launch_plan(spec, arm):
    """Make reviewable argv, not a callable scheduler submission."""
    require(arm in ("baseline", "hrex"), "unknown arm")
    s, f = spec["scheduler"], spec["scout"]
    mpi = [spec["image"]["mpirun"], "--mca", "plm", "isolated", "--host",
           "localhost:16", "--np", "20", "--bind-to", "none", "--oversubscribe",
           "--mca", "mpi_yield_when_idle", "1"]
    # The per-rank adapter must create a rank/device record and exec gmx_mpi.
    # These are the exact mdrun arguments it is to use after validation.
    mdrun = [spec["image"]["gmx"], "mdrun", "-multidir"] + [
        "state{:02d}".format(i) for i in range(20)] + [
        "-s", "topol.tpr", "-deffnm", "scout", "-nb", "gpu", "-pme", "cpu",
        "-bonded", "cpu", "-update", "cpu", "-ntomp", "1", "-gpu_id", "0",
        "-pin", "off", "-dlb", "no", "-notunepme", "-cpt", "15",
        "-replex", str(f["baseline_replex"] if arm == "baseline" else f["hrex_replex"])]
    if arm == "hrex":
        mdrun += ["-reseed", str(f["hrex_seed"])]
    return {"arm": arm, "mpi_prefix": mpi, "mdrun_per_rank": mdrun,
            "scheduler_request": {"project": s["project"], "queue": s["queue"],
                                  "pe": s["pe"], "slots": s["slots"],
                                  "gpu_type": s["gpu_type"], "gpus": s["gpus"],
                                  "h_rt": "02:00:00", "restartable": False},
            "limits": {"work_deadline_seconds": s["work_deadline_seconds_per_arm"],
                       "storage_stop_bytes_each": s["stop_bytes_per_location"],
                       "storage_cap_bytes_each": s["cap_bytes_per_location"]}}


def package(destination, spec_path=SPEC, result_path=RESULT):
    destination = Path(destination).resolve()
    require(not destination.exists(), "refusing to overwrite package")
    spec = yaml.safe_load(Path(spec_path).read_text())
    spec["accepted_tpr_sha256"] = accepted_hashes(Path(result_path).read_text())
    validate_contract(spec)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "package"
        root.mkdir()
        shutil.copy2(Path(__file__), root / "builder.py")
        shutil.copy2(spec_path, root / "source-spec.yaml")
        (root / "contract.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        for arm in ("baseline", "hrex"):
            (root / ("plan-" + arm + ".json")).write_text(
                json.dumps(launch_plan(spec, arm), indent=2, sort_keys=True) + "\n")
        (root / "README.txt").write_text(
            "F64A C2 paired timing-scout runtime candidate, CPU review only.\n"
            "Run REVIEW_PACKAGE.sh, then IMPORT_ON_SCC.sh once on scc-i01.\n"
            "REVIEW_IMPORTED.sh verifies the full source and imported hash set.\n"
            "There is no qsub, SGE job script, mdrun entry point or GPU authorization.\n"
            "See docs/f64a_c2_scout_runtime_candidate.md in the repository.\n")
        scripts = {
            "REVIEW_PACKAGE.sh": "review-package",
            "IMPORT_ON_SCC.sh": "import",
            "REVIEW_IMPORTED.sh": "review-imported",
        }
        for name, command in scripts.items():
            (root / name).write_text(
                '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
                'exec python builder.py ' + command + ' --package "$PWD"\n')
            (root / name).chmod(0o755)
        manifest(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(root, destination)
    print(PACKAGE_MARKER + "_CREATED; no job submitted")


def review_package(root):
    root = Path(root).resolve()
    verify_manifest(root)
    spec = json.loads((root / "contract.json").read_text())
    validate_contract(spec)
    require(sha(root / "builder.py") == sha(__file__), "wrong builder code")
    source_spec = yaml.safe_load((root / "source-spec.yaml").read_text())
    require({k: v for k, v in spec.items() if k != "accepted_tpr_sha256"} ==
            source_spec, "package spec mismatch")
    for arm in ("baseline", "hrex"):
        require(json.loads((root / ("plan-" + arm + ".json")).read_text()) ==
                launch_plan(spec, arm), "launch plan mismatch: " + arm)
    require(not any((root / name).exists() for name in
                    ("SUBMIT_ON_SCC.sh", "stage_baseline.sge", "stage_hrex.sge")),
            "candidate unexpectedly has a submission path")
    return spec


def review_source(spec):
    source = Path(spec["prepared_source"]["path"])
    verify_manifest(source, MANIFEST_HASH, 381)
    record = json.loads((source / "PREPARED.json").read_text())
    require(record["status"] == "cpu_inputs_prepared_pending_review" and
            record["execution_authorized"] is False and
            record["production_authorized"] is False and
            record["package_spec_sha256"] == SPEC_HASH and
            record["sif_sha256"] == IMAGE_HASH and len(record["states"]) == 20,
            "CPU source metadata changed")
    for i, digest in enumerate(spec["accepted_tpr_sha256"]):
        name = "state{:02d}".format(i)
        require(record["states"][i]["state"] == i and
                record["states"][i]["tpr_sha256"] == digest, "TPR record mismatch")
        for rel in ("common/states/{}/topol.tpr".format(name),
                    "arms/baseline/states/{}/topol.tpr".format(name),
                    "arms/hrex/states/{}/topol.tpr".format(name)):
            require(sha(source / rel) == digest, "accepted TPR mismatch: " + rel)
    return source


def import_prepared(root):
    root = Path(root).resolve()
    require(not os.environ.get("JOB_ID"), "CPU import must be outside an SGE job")
    spec = review_package(root)
    source = review_source(spec)
    target = root / "prepared"
    require(not target.exists(), "refusing to overwrite import or retry")
    shutil.copytree(source, target, symlinks=False)
    provenance = {"source": str(source), "source_manifest_sha256": MANIFEST_HASH,
                  "source_record_sha256": sha(source / "PREPARED.json"),
                  "package_manifest_sha256": sha(root / "SHA256SUMS"),
                  "execution_authorized": False, "gpu_executed": False}
    (root / "IMPORT.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    review_imported(root)
    print(PACKAGE_MARKER + "_IMPORTED; no job submitted")


def review_imported(root):
    root = Path(root).resolve()
    spec = review_package(root)
    source = review_source(spec)
    target = root / "prepared"
    verify_manifest(target, MANIFEST_HASH, 381)
    record = json.loads((root / "IMPORT.json").read_text())
    require(record == {"source": str(source), "source_manifest_sha256": MANIFEST_HASH,
                       "source_record_sha256": sha(source / "PREPARED.json"),
                       "package_manifest_sha256": sha(root / "SHA256SUMS"),
                       "execution_authorized": False, "gpu_executed": False},
            "import provenance mismatch")
    for i, digest in enumerate(spec["accepted_tpr_sha256"]):
        for arm in ("baseline", "hrex"):
            require(sha(target / "arms" / arm / "states" /
                        "state{:02d}".format(i) / "topol.tpr") == digest,
                    "imported paired TPR mismatch")
    print(PACKAGE_MARKER + "_REVIEW_PASS states=20 manifest_entries=381 execution_authorized=False")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("package")
    create.add_argument("--destination", type=Path, required=True)
    create.add_argument("--spec", type=Path, default=SPEC)
    create.add_argument("--result", type=Path, default=RESULT)
    for command in ("review-package", "import", "review-imported", "job"):
        p = sub.add_parser(command)
        p.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "package":
        package(args.destination, args.spec, args.result)
    elif args.command == "review-package":
        review_package(args.package)
        print(PACKAGE_MARKER + "_VERIFIED; no job submitted")
    elif args.command == "import":
        import_prepared(args.package)
    elif args.command == "review-imported":
        review_imported(args.package)
    elif args.command == "job":
        raise ValueError("GPU execution is not authorized by this candidate")


if __name__ == "__main__":
    main()
