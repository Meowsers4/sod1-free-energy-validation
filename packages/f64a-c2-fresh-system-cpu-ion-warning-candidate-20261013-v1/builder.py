"""Isolated CPU-only F64A r3 system-build rehearsal; never runs FEP windows."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import yaml


PACKAGE_FILES = (
    "README.txt", "REVIEW_PACKAGE.sh", "PREFLIGHT_ON_SCC.sh",
    "REVIEW_PREPARED.sh", "REVIEW_ON_SCC.sh", "SUBMIT_ON_SCC.sh",
    "candidate-SHA256SUMS", "release-candidate-SHA256SUMS",
    "failed-selected-SHA256SUMS", "login-candidate-SHA256SUMS",
    "explicit-login-candidate-SHA256SUMS", "spent-selected-SHA256SUMS",
    "spent-selection.json", "warning-evidence.json",
    "failure-evidence.json", "cpu-system.sge", "run-system-login.sh", "builder.py",
    "source-spec.json", "historical-pipeline.yaml", "variants.csv",
    "prepared-wt.pdb",
)
PACKAGE_NAME = "f64a-c2-fresh-system-cpu-ion-warning-candidate-20261013-v1"
SOURCE_MANIFEST_SHA256 = "3d81f4c8c077e736919da9e54b7d60bcdcc432748cccf6d21548b76c4b02559d"
RELEASE_MANIFEST_SHA256 = "015b32ea7a038ac069dfd36557da7795d7f65d0677bcc2fcbd6bdc941974451d"
FAILED_SELECTED_MANIFEST_SHA256 = "2df16c4e9930a89a2a141438386677bae225c13041891c4a0765c63c85d17a2c"
LOGIN_CANDIDATE_MANIFEST_SHA256 = "1c926cf2349aeb43602c3e39a93453b7c38324a487dbd6fe652f6729065b8a28"
EXPLICIT_LOGIN_CANDIDATE_MANIFEST_SHA256 = "6f9d041ff165d2a6169442f4e0dde9b3f8766ca5e7eb0b4c9c97c6891c7ff9cd"
SPENT_SELECTED_MANIFEST_SHA256 = "364ba3704c2c9067fb9d1ad633d51a9415ae7d03388bb10fe765392796196a07"
SPENT_SELECTION_SHA256 = "37876acca063e9bb48a30d8968b2268fb579829180681bec78acdbc491ea90c7"
REVIEW_MARKER = "C2_R3_CPU_SYSTEM_ION_WARNING_CANDIDATE_REVIEW_PASS execution_authorized=False; no job submitted"
REQUIRED_SYSTEM_FILES = (
    "SYSTEM_READY", "wt.pdb", "wt_gmx.pdb", "hybrid.pdb", "conf.gro",
    "hybrid.top", "posre.itp", "box.gro", "solv.gro", "ions.gro",
    "em.gro", "em.tpr", "em.mdp",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def verify_package(package: Path) -> dict:
    require(package.name == PACKAGE_NAME and package.is_dir(), "wrong package directory")
    manifest = package / "SHA256SUMS"
    require(manifest.is_file(), "missing package manifest")
    rows = []
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        require(match is not None, "malformed package manifest")
        rows.append((match.group(2), match.group(1)))
    require([name for name, _ in rows] == sorted(PACKAGE_FILES), "package file set mismatch")
    for name, expected in rows:
        target = package / name
        require(target.is_file() and not target.is_symlink(), f"missing/symlinked package file: {name}")
        require(digest(target) == expected, f"package checksum mismatch: {name}")
    spec = json.loads((package / "source-spec.json").read_text())
    require(spec["scope"] == "isolated_cpu_only_f64a_folded_r3_system_build_rehearsal"
            and spec["variant"] == "F64A" and spec["leg"] == "folded"
            and spec["repeat"] == 3 and spec["gpu_requested"] is False
            and spec["execution_authorized"] is False
            and spec["production_authorized"] is False
            and spec["lambda_aware_state_starts_in_scope"] is False
            and spec["requested_cpu_slots"] == 8
            and spec["scheduler_walltime"] == "01:00:00"
            and spec["candidate_manifest_sha256"] == SOURCE_MANIFEST_SHA256
            and spec["release_candidate_manifest_sha256"] == RELEASE_MANIFEST_SHA256
            and spec["failed_selected_manifest_sha256"] == FAILED_SELECTED_MANIFEST_SHA256
            and spec["login_candidate_manifest_sha256"] == LOGIN_CANDIDATE_MANIFEST_SHA256
            and spec["explicit_login_candidate_manifest_sha256"] == EXPLICIT_LOGIN_CANDIDATE_MANIFEST_SHA256
            and spec["spent_selected_manifest_sha256"] == SPENT_SELECTED_MANIFEST_SHA256
            and spec["allowed_preion_warning"] == "one_ewald_warning_for_charge_minus_5_before_genion_neutral",
            "package scope mismatch")
    require(digest(package / "candidate-SHA256SUMS") == SOURCE_MANIFEST_SHA256,
            "source candidate manifest mismatch")
    require(digest(package / "release-candidate-SHA256SUMS") == RELEASE_MANIFEST_SHA256,
            "release candidate manifest mismatch")
    require(digest(package / "failed-selected-SHA256SUMS") == FAILED_SELECTED_MANIFEST_SHA256,
            "failed selected manifest mismatch")
    require(digest(package / "login-candidate-SHA256SUMS") == LOGIN_CANDIDATE_MANIFEST_SHA256,
            "login candidate manifest mismatch")
    require(digest(package / "explicit-login-candidate-SHA256SUMS") == EXPLICIT_LOGIN_CANDIDATE_MANIFEST_SHA256,
            "explicit login candidate manifest mismatch")
    require(digest(package / "spent-selected-SHA256SUMS") == SPENT_SELECTED_MANIFEST_SHA256,
            "spent selected manifest mismatch")
    selection = json.loads((package / "spent-selection.json").read_text())
    require(selection.get("decision") == "one_corrected_isolated_r3_cpu_system_build"
            and selection.get("selection_date") == "2026-10-12"
            and selection.get("authorization_source") == "user selection after explicit-login v2 static review"
            and selection.get("failed_job_id") == "8032575"
            and selection.get("repeat") == 3
            and selection.get("max_jobs") == 1
            and selection.get("cpu_slots") == 8
            and selection.get("walltime") == "01:00:00"
            and selection.get("gpu_requested") is False
            and selection.get("automatic_retry") is False
            and selection.get("production_authorized") is False
            and selection.get("explicit_login_candidate_manifest_sha256") == EXPLICIT_LOGIN_CANDIDATE_MANIFEST_SHA256,
            "selection record mismatch")
    require(digest(package / "spent-selection.json") == SPENT_SELECTION_SHA256,
            "spent selection hash mismatch")
    warning = json.loads((package / "warning-evidence.json").read_text())
    require(warning.get("job_id") == "8059683"
            and warning.get("exit_status") == 1
            and warning.get("saved_grompp_step") == "ions.mdp"
            and warning.get("pre_ion_charge") == -5
            and warning.get("warning_count") == 1
            and warning.get("warning_class") == "Ewald electrostatics on charged solvated system before genion -neutral"
            and warning.get("prepared_exists") is False
            and warning.get("prepared_incomplete_exists") is True
            and warning.get("spent_selected_manifest_sha256") == SPENT_SELECTED_MANIFEST_SHA256
            and warning.get("saved_command_metadata") == "to be verified read-only by REVIEW_ON_SCC.sh",
            "warning attempt provenance mismatch")
    failure = json.loads((package / "failure-evidence.json").read_text())
    require(failure.get("job_id") == "8032575"
            and failure.get("exit_status") == 1
            and failure.get("prepared_exists") is False
            and failure.get("prepared_incomplete_exists") is False
            and failure.get("selected_manifest_sha256") == FAILED_SELECTED_MANIFEST_SHA256,
            "failed attempt provenance mismatch")
    for name, key in (("historical-pipeline.yaml", "source_config_sha256"),
                      ("variants.csv", "panel_csv_sha256"),
                      ("prepared-wt.pdb", "source_wt_sha256")):
        require(digest(package / name) == spec[key], f"pinned package input mismatch: {name}")
    return spec


def permit(package: Path) -> dict:
    spec = verify_package(package)
    require(spec["execution_authorized"] is True,
            "CPU system build not selected; no job may be submitted")
    review = package / "review.log"
    require(review.is_file() and not review.is_symlink()
            and REVIEW_MARKER in review.read_text(),
            "selected package needs a passing SCC static review log")
    require(not (package / "submission").exists()
            and not (package / "prepared").exists()
            and not (package / "prepared.incomplete").exists(),
            "existing submission or output; no second attempt")
    return spec


def remote_preflight(package: Path) -> dict:
    spec = verify_package(package)
    repo = Path(spec["source_repo"])
    require(repo.is_dir(), "SCC source repo unavailable")
    checks = {
        spec["source_config_relative"]: spec["source_config_sha256"],
        spec["source_wt_relative"]: spec["source_wt_sha256"],
        "data/variants.csv": spec["panel_csv_sha256"],
        **spec["source_code_sha256"],
    }
    for relative, expected in checks.items():
        target = repo / relative
        require(target.is_file() and digest(target) == expected,
                f"SCC source identity mismatch: {relative}")
    sys.path.insert(0, str(repo))
    from src.seeds import stable_seed
    from src.fep import pmx_engine

    require(Path(pmx_engine.__file__).resolve() == (repo / "src/fep/pmx_engine.py").resolve(),
            "wrong pmx engine imported")
    cfg = yaml.safe_load((package / "historical-pipeline.yaml").read_text())
    require(cfg["fep"]["independent_replicate_systems"] is True
            and cfg["fep"]["keep_disulfide_reduced"] is True
            and cfg["fep"]["lambda_windows"] == 20,
            "historical C2 source settings changed")
    folded = repo / "results/fep/F64A/folded"
    for r, (seed, ion_hash) in enumerate(zip(spec["historical_ion_seeds"],
                                              spec["historical_ions_gro_sha256"])):
        marker = folded / f"system_r{r}/SYSTEM_READY"
        ions = folded / f"system_r{r}/ions.gro"
        require(marker.is_file() and f"seed={seed}" in marker.read_text().split(),
                f"historical system marker mismatch: r{r}")
        require(ions.is_file() and digest(ions) == ion_hash,
                f"historical ion coordinates mismatch: r{r}")
        require(stable_seed("F64A", "folded", r, "system") == seed,
                f"historical seed derivation mismatch: r{r}")
    require(stable_seed("F64A", "folded", 3, "system") == spec["expected_r3_ion_seed"],
            "r3 ion seed derivation mismatch")
    require(not (folded / "system_r3").exists()
            and not list(folded.glob("w*_r3")),
            "r3 already exists in historical SCC source tree")
    forcefield = pmx_engine.pmx_ff_dir(cfg)
    require((forcefield / (cfg["fep"]["pmx_forcefield"] + ".ff") / "forcefield.itp").is_file(),
            "pmx mutation force field unavailable")
    gmx = Path(cfg["cluster"]["gmx_binary"])
    require(gmx.is_file() and os.access(gmx, os.X_OK), "historical host GROMACS unavailable")
    version = subprocess.run([str(gmx), "--version"], text=True, capture_output=True,
                             timeout=30, check=True)
    require("GROMACS version:    2025.3" in version.stdout
            or re.search(r"GROMACS version:\s+2025\.3", version.stdout),
            "wrong host GROMACS version")
    return {"status": "cpu_system_source_preflight_pass",
            "repeat": 3, "source_wt_sha256": spec["source_wt_sha256"],
            "config_sha256": spec["source_config_sha256"],
            "ion_placement_seed": spec["expected_r3_ion_seed"],
            "pmx_forcefield_root": str(forcefield),
            "gromacs_binary": str(gmx),
            "historical_output_tree_unchanged": True,
            "execution_authorized": spec["execution_authorized"]}


def gro_atoms(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    require(len(lines) >= 4 and len(lines[2:-1]) == int(lines[1].strip()),
            f"malformed GRO atom count: {path.name}")
    return lines[2:-1]


def audit_system(package: Path, prepared: Path, spec: dict) -> dict:
    repo = Path(spec["source_repo"])
    sys.path.insert(0, str(repo))
    from src.fep import pmx_engine

    system = prepared / "results/fep/F64A/folded/system_r3"
    require(system.is_dir(), "missing isolated r3 system")
    for name in REQUIRED_SYSTEM_FILES:
        require((system / name).is_file(), f"missing r3 system file: {name}")
    marker = (system / "SYSTEM_READY").read_text().split()
    for token in ("variant=F64A", "leg=folded", "rep=3",
                  f"seed={spec['expected_r3_ion_seed']}"):
        require(token in marker, f"r3 completion marker mismatch: {token}")
    require(digest(system / "wt.pdb") == spec["source_wt_sha256"],
            "r3 WT source checksum mismatch")
    for name in ("conf.gro", "em.gro"):
        atoms = gro_atoms(system / name)
        require(not any(line[5:10].strip().upper().startswith(("CU", "ZN"))
                        for line in atoms), f"metal in {name}")
        pmx_engine.assert_topology_disulfide_free(system / "hybrid.top", system / name)
    ions = gro_atoms(system / "ions.gro")
    em = gro_atoms(system / "em.gro")
    require(len(ions) == len(em) == spec["expected_atom_count"],
            "r3 atom count differs from technical protein source")
    ion_counts = {name: sum(line[5:10].strip() == name for line in ions)
                  for name in ("NA", "CL")}
    require(ion_counts == spec["expected_ion_counts"], "r3 ion count mismatch")
    ion_hash = digest(system / "ions.gro")
    require(ion_hash not in spec["historical_ions_gro_sha256"],
            "r3 ion coordinates repeat an archived system")
    return {"status": "isolated_r3_cpu_system_prepared_pending_review",
            "repeat": 3, "seed": spec["expected_r3_ion_seed"],
            "atom_count": len(em), "ion_counts": ion_counts,
            "wt_pdb_sha256": digest(system / "wt.pdb"),
            "conf_gro_sha256": digest(system / "conf.gro"),
            "hybrid_top_sha256": digest(system / "hybrid.top"),
            "ions_gro_sha256": ion_hash,
            "em_gro_sha256": digest(system / "em.gro"),
            "production_authorized": False,
            "lambda_aware_state_starts_prepared": False}


def seal(prepared: Path) -> int:
    paths = sorted(p for p in prepared.rglob("*") if p.is_file()
                   and p.name != "SHA256SUMS")
    lines = [f"{digest(path)}  {path.relative_to(prepared).as_posix()}" for path in paths]
    (prepared / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    return len(paths)


def check_grompp_warning(cmd: list[str], output: str) -> None:
    """Allow only the reviewed charged-solvent warning before genion -neutral."""
    headers = re.findall(r"(?m)^\s*WARNING\s+\d+\s+\[[^\n]+\]:", output)
    if not headers:
        require(not re.search(r"(?m)^There (?:was|were) \d+ WARNINGS?\s*$", output),
                "GROMACS warning summary without warning block")
        return
    ions_argv = ["grompp", "-f", "ions.mdp", "-c", "solv.gro", "-p", "hybrid.top",
                 "-o", "ions.tpr", "-maxwarn", "2"]
    require(cmd[1:] == ions_argv and len(headers) == 1,
            "unexpected GROMACS grompp warning in CPU system build")
    match = re.search(
        r"(?m)^WARNING 1 \[file hybrid\.top, line \d+\]:\n((?:[ \t]+[^\n]*\n)+)",
        output,
    )
    expected = (
        "You are using Ewald electrostatics in a system with net charge. "
        "This can lead to severe artifacts, such as ions moving into regions "
        "with low dielectric, due to the uniform background charge. We suggest "
        "to neutralize your system with counter ions, possibly in combination "
        "with a physiological salt concentration."
    )
    require(match is not None and " ".join(match.group(1).split()) == expected
            and re.search(r"(?m)^\s*System has non-zero total charge:\s+-5\.000000\s*$", output)
            and re.search(r"(?m)^There was 1 WARNING\s*$", output),
            "ion grompp warning differs from reviewed pre-neutralization charge warning")


def review_saved_warning(package: Path, old: Path | None = None) -> dict:
    """Read the spent job's sealed package and exact saved grompp record."""
    verify_package(package)
    if old is None:
        old = Path("/project/rise-batteries/bode/container-build-packages"
                   "/f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1")
    require(old.is_dir() and digest(old / "SHA256SUMS") == SPENT_SELECTED_MANIFEST_SHA256,
            "spent selected package manifest missing or changed")
    for line in (old / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        require(match is not None, "malformed spent selected manifest")
        target = old / match.group(2)
        require(target.is_file() and not target.is_symlink()
                and digest(target) == match.group(1),
                f"spent selected package file changed: {match.group(2)}")
    require(not (old / "prepared").exists() and (old / "prepared.incomplete").is_dir(),
            "spent job output tree differs from supplied evidence")
    log_root = old / "prepared.incomplete/build-logs"
    found = []
    for path in sorted(log_root.glob("command-*.json")):
        require(path.is_file() and not path.is_symlink(), "unsafe saved command log")
        row = json.loads(path.read_text())
        argv = row.get("argv", [])
        if "grompp" in argv and "ions.mdp" in argv:
            found.append((path, row))
    require(len(found) == 1, "expected exactly one saved ion grompp command")
    path, row = found[0]
    require(row.get("returncode") == 0, "saved ion grompp did not exit successfully")
    require(row.get("argv", [None])[0] == "/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx",
            "saved ion grompp binary mismatch")
    system = old / "prepared.incomplete/results/fep/F64A/folded/system_r3"
    require(row.get("cwd") == str(system) and (system / "ions.tpr").is_file(),
            "saved ion grompp working directory or TPR missing")
    check_grompp_warning(row["argv"], row["output"])
    return {"status": "saved_preion_warning_review_pass",
            "job_id": "8059683", "command_log": path.name,
            "command_log_sha256": digest(path),
            "returncode": row["returncode"],
            "warning_count": 1, "pre_ion_charge": -5,
            "production_authorized": False}


def prepare(package: Path) -> dict:
    spec = verify_package(package)
    require(spec["execution_authorized"] is True,
            "CPU system build not selected; candidate package cannot execute")
    require(os.environ.get("JOB_ID", "").isdigit()
            and int(os.environ.get("NSLOTS", "0")) == spec["requested_cpu_slots"],
            "CPU scheduler allocation required")
    require(not os.environ.get("CUDA_VISIBLE_DEVICES"), "GPU exposure forbidden")
    source = remote_preflight(package)
    unfinished = package / "prepared.incomplete"
    finished = package / spec["output_root"]
    require(not unfinished.exists() and not finished.exists(),
            "prepared tree already exists; never overwrite or rerun in place")
    unfinished.mkdir()
    inputs = unfinished / "results/fep/F64A/inputs"
    inputs.mkdir(parents=True)
    shutil.copy2(package / "prepared-wt.pdb", inputs / "wt_apo.pdb")
    (unfinished / "config").mkdir()
    (unfinished / "data").mkdir()
    shutil.copy2(package / "historical-pipeline.yaml", unfinished / "config/pipeline.yaml")
    shutil.copy2(package / "variants.csv", unfinished / "data/variants.csv")
    repo = Path(spec["source_repo"])
    sys.path.insert(0, str(repo))
    from src.fep import pmx_engine

    cfg = yaml.safe_load((package / "historical-pipeline.yaml").read_text())
    original_root = pmx_engine.ROOT
    original_run = pmx_engine._run
    pmx_engine.ROOT = unfinished
    log_root = unfinished / "build-logs"
    log_root.mkdir()
    counter = 0

    def logged_run(cmd, cwd, stdin=None, dry_run=False, env=None):
        nonlocal counter
        require(not dry_run, "unexpected dry-run in system build")
        joined = " ".join(cmd)
        require("-nb gpu" not in joined and "-pme gpu" not in joined,
                "GPU command forbidden in CPU build")
        counter += 1
        process = subprocess.run(cmd, cwd=cwd, input=stdin, text=True,
                                 capture_output=True, env={**os.environ, **(env or {})})
        output = (process.stdout or "") + (process.stderr or "")
        (log_root / f"command-{counter:02d}.json").write_text(
            json.dumps({"argv": cmd, "cwd": str(cwd),
                        "returncode": process.returncode, "output": output},
                       indent=2, sort_keys=True) + "\n")
        require(process.returncode == 0,
                f"external command {counter} failed (exit {process.returncode}); see saved command log")
        if "grompp" in cmd:
            check_grompp_warning(cmd, output)
        return output

    pmx_engine._run = logged_run
    try:
        pmx_engine.build_system(cfg, "F64A", "folded", rep=3)
    finally:
        pmx_engine._run = original_run
        pmx_engine.ROOT = original_root
    result = audit_system(package, unfinished, spec)
    result["source_preflight"] = source
    result["commands_recorded"] = counter
    (unfinished / "PREPARED.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["manifest_entries"] = seal(unfinished)
    unfinished.rename(finished)
    return result


def review_prepared(package: Path) -> dict:
    spec = verify_package(package)
    prepared = package / spec["output_root"]
    require(prepared.is_dir() and not prepared.is_symlink(), "prepared output missing")
    manifest = prepared / "SHA256SUMS"
    require(manifest.is_file(), "prepared manifest missing")
    names = []
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        require(match is not None, "malformed prepared manifest")
        name = match.group(2)
        target = prepared / name
        require(target.is_file() and not target.is_symlink()
                and target.resolve().is_relative_to(prepared.resolve()),
                f"unsafe/missing prepared path: {name}")
        require(digest(target) == match.group(1), f"prepared hash mismatch: {name}")
        names.append(name)
    require(len(names) == len(set(names)) and len(names) >= 20,
            "incomplete/duplicate prepared manifest")
    recorded = json.loads((prepared / "PREPARED.json").read_text())
    audited = audit_system(package, prepared, spec)
    for key, value in audited.items():
        require(recorded.get(key) == value, f"prepared inventory mismatch: {key}")
    require(recorded.get("commands_recorded", 0) >= 10,
            "incomplete system-build command record")
    return {"status": "isolated_r3_cpu_system_review_pass",
            "manifest_entries": len(names),
            "ion_placement_seed": spec["expected_r3_ion_seed"],
            "atom_count": audited["atom_count"],
            "production_authorized": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("verify-package", "preflight", "review-saved-warning",
                                           "permit", "prepare", "review-prepared"))
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    if args.action == "verify-package":
        result = {"status": "cpu_system_ion_warning_candidate_package_verified",
                  "scope": verify_package(package)["scope"],
                  "execution_authorized": False}
    elif args.action == "preflight":
        result = remote_preflight(package)
    elif args.action == "review-saved-warning":
        result = review_saved_warning(package)
    elif args.action == "permit":
        result = {"status": "cpu_system_one_job_submission_guard_pass",
                  "execution_authorized": permit(package)["execution_authorized"]}
    elif args.action == "prepare":
        result = prepare(package)
    else:
        result = review_prepared(package)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
