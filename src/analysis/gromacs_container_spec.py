"""Validate the pinned, non-production GROMACS Singularity build specification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


DEFAULT_SPEC = Path("docs/gromacs_hrex_container_v1.yaml")
DEFAULT_OUTPUT = Path(
    "results/cpu_qualification/gromacs_exchange_c1_v1/container_spec.json"
)
PACKAGE_FILES = (
    DEFAULT_SPEC,
    Path("containers/gromacs-2025.3-mpi-cuda-l40s.def"),
    Path("docs/gromacs_hrex_singularity_plan.md"),
    Path("src/__init__.py"),
    Path("src/analysis/__init__.py"),
    Path("src/analysis/gromacs_container_spec.py"),
    Path("tests/test_gromacs_container_spec.py"),
    Path("workflow/exchange_feasibility.smk"),
)


def _check_pins(spec: dict[str, Any], definition: str) -> None:
    """Match active assignments, source versions, build flags and image identities."""
    toolchain = spec["toolchain"]
    archives = {
        "gromacs": ("GROMACS", "gromacs-{version}.tar.gz", "md5"),
        "regressiontests": ("REGRESSION", "regressiontests-{version}.tar.gz", "md5"),
        "openmpi": ("OPENMPI", "openmpi-{version}.tar.gz", "sha256"),
        "cmake": ("CMAKE", "cmake-{version}-linux-x86_64.tar.gz", "sha256"),
        "fftw": ("FFTW", "fftw-{version}.tar.gz", "sha256"),
    }
    for name, (prefix, archive, algorithm) in archives.items():
        pin = toolchain[name]
        version = pin["version"]
        digest = pin[algorithm]
        length = 32 if algorithm == "md5" else 64
        if not re.fullmatch(rf"[0-9a-f]{{{length}}}", digest):
            raise ValueError(f"invalid {name} {algorithm}")
        if Path(urlparse(pin["url"]).path).name != archive.format(version=version):
            raise ValueError(f"{name} version disagrees with archive URL")
        for suffix, value in (("URL", pin["url"]), (algorithm.upper(), digest)):
            actual = re.findall(rf"^\s*{prefix}_{suffix}=(\S+)\s*$", definition, re.M)
            if actual != [value]:
                raise ValueError(f"{name} {suffix} disagrees with definition")
        manifest = f"'{name.upper()}={version} {algorithm}={digest}'"
        if manifest not in definition:
            raise ValueError(f"{name} manifest disagrees with contract")

    artifact = spec["artifact"]
    if re.findall(r"^Bootstrap: (\S+)$", definition, re.M) != [artifact["bootstrap"]] * 2:
        raise ValueError("bootstrap disagrees with definition")
    if re.findall(r"^From: (\S+)$", definition, re.M) != [
        artifact["build_image"], artifact["runtime_image"]
    ]:
        raise ValueError("base images disagree with definition")
    for key, flavor in (("build_image", "devel"), ("runtime_image", "runtime")):
        if artifact[key] != f"nvidia/cuda:{toolchain['cuda']}-{flavor}-rockylinux8":
            raise ValueError("CUDA version disagrees with base image")
    if f". /opt/rh/{toolchain['compiler']}/enable" not in definition:
        raise ValueError("compiler disagrees with definition")

    contract = spec["build_contract"]
    options = {
        "GMX_MPI": "ON" if contract["gromacs_mpi"] else "OFF",
        "GMX_THREAD_MPI": "ON" if contract["gromacs_thread_mpi"] else "OFF",
        "GMX_GPU": contract["gromacs_gpu"],
        "GMX_CUDA_TARGET_SM": contract["cuda_target_sm"],
        "GMX_CUDA_TARGET_COMPUTE": contract["cuda_target_compute"],
        "GMX_SIMD": contract["simd"],
    }
    for key, value in options.items():
        actual = re.findall(rf"^\s*-D{key}=(\S+)", definition, re.M)
        if actual != [value]:
            raise ValueError(f"{key} disagrees with definition")
    actual_hash = hashlib.sha256(definition.encode()).hexdigest()
    if actual_hash != artifact["definition_sha256"]:
        raise ValueError("definition SHA-256 disagrees with contract")
    plm = spec["runtime_contract"]["openmpi_plm"]
    # Build, runtime environment, and final self-test must all select local launch.
    sections = (
        definition.split("\n%post\n", 1)[1].split("\nBootstrap:", 1)[0],
        definition.split("\n%environment\n", 1)[1].split("\n%runscript\n", 1)[0],
        definition.split("\n%test\n", 1)[1],
    )
    if plm != "isolated" or any(
        re.findall(r"^\s*export OMPI_MCA_plm=(\S+)", section, re.M) != [plm]
        for section in sections
    ):
        raise ValueError("single-node OpenMPI launcher disagrees with contract")
    session_tmpdir = spec["runtime_contract"]["openmpi_session_tmpdir"]
    if session_tmpdir != "/tmp" or any(
        re.findall(r"^\s*export OMPI_MCA_orte_tmpdir_base=(\S+)", section, re.M) != [session_tmpdir]
        or "unset OMPI_MCA_orte_local_tmpdir_base OMPI_MCA_orte_remote_tmpdir_base" not in section
        for section in sections
    ):
        raise ValueError("OpenMPI session directory disagrees with contract")
    final_post = definition.rsplit("\n%post\n", 1)[1].split("\n%environment\n", 1)[0]
    installs = re.findall(r"^\s*dnf install -y ([^\n]+)$", final_post, re.M)
    if len(installs) != 1 or installs[0].split() != spec["build_contract"]["runtime_packages"]:
        raise ValueError("final runtime packages disagree with contract")


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    """Load and fail-closed validate the container contract."""
    spec = yaml.safe_load(path.read_text())
    if spec.get("schema_version") != 1:
        raise ValueError("container schema_version must be 1")
    if spec.get("production_authorized") is not False:
        raise ValueError("container specification cannot authorize production")
    if spec.get("build_executed") is not False:
        raise ValueError("build_executed must remain false until SCC evidence is captured")
    if spec.get("gpu_smoke_executed") is not False:
        raise ValueError("gpu_smoke_executed must remain false until SCC evidence is captured")
    if spec["runtime_contract"].get("deployment_scope") != "single_node_only":
        raise ValueError("v1 container is restricted to single-node deployment")
    if spec["runtime_contract"].get("host_container_mpi_interoperation_required") is not False:
        raise ValueError("v1 must not depend on host/container MPI interoperability")
    return spec


def evaluate(spec: dict[str, Any], repository_root: Path = Path(".")) -> dict[str, Any]:
    """Reconcile the definition against the machine-readable pinned contract."""
    definition_path = repository_root / spec["artifact"]["definition"]
    definition = definition_path.read_text()
    required = spec["build_contract"]["required_fragments"]
    forbidden = spec["build_contract"]["forbidden_fragments"]
    missing = [fragment for fragment in required if fragment not in definition]
    present_forbidden = [fragment for fragment in forbidden if fragment in definition]
    if missing:
        raise ValueError(f"container definition is missing required fragments: {missing}")
    if present_forbidden:
        raise ValueError(
            f"container definition contains prohibited runtime/submission fragments: {present_forbidden}"
        )

    _check_pins(spec, definition)

    runtime = spec["runtime_contract"]
    checks = {
        "toolchain_and_definition_pins_match": True,
        "one_rank_per_lambda_state": (
            runtime["mpi_ranks"] == runtime["lambda_states"]
            and runtime["ranks_per_state"] == 1
        ),
        "one_host_only": runtime["candidate_host_count"] == 1,
        "internal_mpi_only": (
            runtime["launcher"] == "container_internal_openmpi"
            and runtime["host_container_mpi_interoperation_required"] is False
        ),
        "scheduler_controls_gpu_visibility": (
            runtime["gpu_visibility_source"] == "scheduler_cuda_visible_devices"
        ),
        "production_not_authorized": spec["production_authorized"] is False,
        "runtime_not_yet_qualified": spec["admission"]["eligible_now"] is False,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"container contract checks failed: {failed}")

    return {
        "schema_version": 1,
        "container_id": spec["container_id"],
        "selected_at": str(spec["selected_at"]),
        "scope": spec["scope"],
        "production_authorized": False,
        "build_executed": False,
        "gpu_smoke_executed": False,
        "eligible_now": False,
        "ready_to_build": spec["admission"]["ready_to_build"],
        "definition": str(spec["artifact"]["definition"]),
        "definition_sha256": hashlib.sha256(definition.encode()).hexdigest(),
        "toolchain": spec["toolchain"],
        "runtime_contract": runtime,
        "checks": checks,
        "blockers": spec["admission"]["blockers"],
        "prohibited": spec["admission"]["prohibited"],
        "sources": spec["sources"],
    }


def write_report(report: dict[str, Any], output: Path = DEFAULT_OUTPUT) -> None:
    """Write a deterministic JSON validation report."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")


def create_package(destination: Path, repository_root: Path = Path(".")) -> None:
    """Create a new isolated transfer package, validating the copied bytes first."""
    if destination.exists():
        raise FileExistsError(f"refusing to replace package: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as staging:
        package = Path(staging) / "package"
        package.mkdir()
        for relative in PACKAGE_FILES:
            target = package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repository_root / relative, target)
        report = evaluate(load_spec(package / DEFAULT_SPEC), package)
        write_report(report, package / "container_spec.json")
        plan = (package / "docs/gromacs_hrex_singularity_plan.md").read_text()
        build_script = plan.split("```bash\nbash <<'BUILD'\n", 1)[1].split("\nBUILD\n```", 1)[0]
        (package / "BUILD_ON_SCC.sh").write_text(
            "#!/bin/bash\n# Generated from the reviewed build block in docs/gromacs_hrex_singularity_plan.md.\n"
            + build_script + "\n"
        )
        files = sorted(path for path in package.rglob("*") if path.is_file())
        manifest = "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(package)}\n"
            for path in files
        )
        (package / "SHA256SUMS").write_text(manifest)
        # mkdir is the no-clobber reservation, including against a concurrent writer.
        destination.mkdir()
        try:
            shutil.copytree(package, destination, dirs_exist_ok=True)
        except BaseException:
            shutil.rmtree(destination)
            raise


def create_runtime_probe_package(destination: Path, repository_root: Path = Path(".")) -> None:
    """Package a diagnostic that copies retained binaries; never compile or connect."""
    if destination.exists():
        raise FileExistsError(f"refusing to replace package: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as staging:
        package = Path(staging) / "package"
        package.mkdir()
        for source, name in (
            ("containers/gromacs-runtime-probe.def", "gromacs-runtime-probe.def"),
            ("containers/run_gromacs_runtime_probe.sh", "RUN_PROBE_ON_SCC.sh"),
            ("docs/gromacs_runtime_probe.md", "README.md"),
        ):
            shutil.copyfile(repository_root / source, package / name)
        manifest = "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in sorted(package.iterdir())
        )
        (package / "SHA256SUMS").write_text(manifest)
        destination.mkdir()
        try:
            shutil.copytree(package, destination, dirs_exist_ok=True)
        except BaseException:
            shutil.rmtree(destination)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    packages = parser.add_mutually_exclusive_group()
    packages.add_argument("--package-dir", type=Path)
    packages.add_argument("--runtime-probe-package-dir", type=Path)
    args = parser.parse_args()
    if args.runtime_probe_package_dir is not None:
        create_runtime_probe_package(args.runtime_probe_package_dir, args.repository_root)
        print(f"Created runtime diagnostic package: {args.runtime_probe_package_dir}")
        return
    if args.package_dir is not None:
        create_package(args.package_dir, args.repository_root)
        print(f"Created verified build package: {args.package_dir}")
        return
    report = evaluate(load_spec(args.spec), args.repository_root)
    write_report(report, args.output)
    print(
        f"{report['container_id']}: definition validated; "
        f"ready_to_build={report['ready_to_build']}; eligible_now={report['eligible_now']}"
    )


if __name__ == "__main__":
    main()
