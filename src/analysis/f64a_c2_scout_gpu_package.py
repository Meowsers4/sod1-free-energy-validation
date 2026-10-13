"""Seal the guarded, non-submitting F64A C2 GPU runtime candidate."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

import yaml


SPEC = Path("docs/f64a_c2_scout_gpu_candidate_v1.yaml")
CPU_CONTRACT = Path("packages/f64a-c2-scout-runtime-cpu-20260929-v1/contract.json")
PIPELINE = Path("config/pipeline.yaml")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_spec(spec):
    require(spec["schema_version"] == 1 and
            spec["scope"] == "f64a_folded_apo_2sh_r0_paired_100ps_timing_scout_candidate" and
            spec["execution_authorized"] is False and
            spec["production_authorized"] is False,
            "GPU scout candidate cannot grant execution")
    require(spec["prepared_source"] == {
        "path": "/project/rise-batteries/bode/container-build-packages/"
                "f64a-c2-scout-runtime-cpu-20260929-v1/prepared",
        "package_manifest_sha256": "8d8919e005da81b44e8dbd973a5935eda406f4e23c9c1f8b3d8abd59f4a288af",
        "prepared_manifest_sha256": "cffefe198d66e670ebc7db2960039e2cfc159e64bb238af7d5c3fe13c7f64487",
        "prepared_manifest_entries": 381}, "accepted CPU source changed")
    require(spec["image"] == {
        "path": "/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/"
                "gromacs-2025.3-mpi-cuda-l40s.sif",
        "sha256": "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee",
        "gmx": "/opt/gromacs/2025.3/bin/gmx_mpi",
        "mpirun": "/opt/openmpi/4.1.5/bin/mpirun",
        "python": "/usr/libexec/platform-python"}, "r6 image changed")
    require(spec["scheduler"] == {
        "project": "rise-batteries", "queue": "l40s", "pe": "omp16",
        "slots": 16, "gpus": 1, "gpu_type": "L40S", "ranks": 20,
        "threads": 1, "walltime_seconds": 7200,
        "work_deadline_seconds": 6300, "attempts_per_arm": 1,
        "storage_stop_bytes_each": 805306368,
        "storage_cap_bytes_each": 1073741824,
        "minimum_free_bytes_each": 3221225472},
        "scheduler or cost bound changed")
    require(spec["cpu_sharing"] == {
        "mode": "explicit_oversubscription", "affinity_cpus": 16,
        "mpi_yield_when_idle": 1}, "CPU sharing changed")
    require(spec["sharing"] == {
        "mode": "private_MPS", "control_timeout_seconds": 5,
        "graceful_stop_seconds": 40, "shutdown_timeout_seconds": 10},
        "MPS bound changed")
    require(spec["scout"] == {
        "nsteps": 50000, "dt_ps": 0.002, "energy_stride": 500,
        "coordinate_stride": 25000, "log_stride": 5000,
        "checkpoint_minutes": 15, "maxh_hours": 1.7,
        "baseline_replex": 0, "hrex_replex": 500,
        "hrex_seed": 20260929, "arm_order": ["baseline", "hrex"],
        "no_planned_restart": True, "no_automatic_retry": True},
        "scientific/technical scout schedule changed")


def add_states(spec, cpu_contract, pipeline):
    require(cpu_contract["prepared_source"]["manifest_sha256"] ==
            spec["prepared_source"]["prepared_manifest_sha256"] and
            cpu_contract["execution_authorized"] is False,
            "CPU runtime contract changed")
    hashes = cpu_contract["accepted_tpr_sha256"]
    require(len(hashes) == 20 and all(re.fullmatch("[0-9a-f]{64}", x) for x in hashes),
            "accepted TPR hash table incomplete")
    require(sha(pipeline) ==
            "af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29",
            "historical lambda config changed")
    lambdas = [float(x) for x in yaml.safe_load(pipeline.read_text())["fep"]["lambda_vector"]]
    require(len(lambdas) == 20 and all(a < b for a, b in zip(lambdas, lambdas[1:])),
            "historical lambda vector changed")
    spec["states"] = [{"directory": "state{:02d}".format(i),
                       "local_index": i, "lambda_value": lambdas[i],
                       "tpr_sha256": hashes[i]} for i in range(20)]
    spec["pipeline_sha256"] = sha(pipeline)


def manifest(directory):
    lines = ["{}  {}\n".format(sha(p), p.relative_to(directory))
             for p in sorted(directory.rglob("*"))
             if p.is_file() and p.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("".join(lines))
    return len(lines)


def package(destination, root=Path("."), spec_path=SPEC):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    require(not destination.exists(), "refusing to overwrite sealed candidate")
    spec_file = root / spec_path
    spec = yaml.safe_load(spec_file.read_text())
    validate_spec(spec)
    add_states(spec, json.loads((root / CPU_CONTRACT).read_text()), root / PIPELINE)
    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp) / "package"
        stage.mkdir()
        (stage / "contract.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        sources = {
            spec_file: "source-spec.yaml",
            root / PIPELINE: "historical-pipeline.yaml",
            root / "src/analysis/f64a_c2_scout_gpu_package.py": "builder.py",
            root / "src/analysis/f64a_c2_scout_gpu_runtime.py": "runtime.py",
            root / "src/analysis/f64a_c2_scout_gpu_checks.py": "scout_checks.py",
            root / "src/analysis/gromacs_gpu_smoke_runtime.py": "smoke_runtime.py",
            root / "src/analysis/gromacs_gpu_mps.py": "mps.py",
            root / "src/analysis/gromacs_protein_runtime_checks.py": "protein_checks.py",
            root / CPU_CONTRACT: "accepted-cpu-contract.json",
        }
        for source, filename in sources.items():
            shutil.copy2(source, stage / filename)
        (stage / "README.txt").write_text(
            "F64A C2 100-ps paired technical GPU runtime candidate.\n"
            "The contract denies job execution; no submission script is present.\n"
            "REVIEW_PACKAGE.sh checks local identities without SCC.\n"
            "REVIEW_ON_SCC.sh verifies the accepted 381-entry CPU inputs and r6 image.\n"
            "Do not run job or accounting modes before a separately selected release.\n")
        (stage / "REVIEW_PACKAGE.sh").write_text(
            '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
            'export PYTHONDONTWRITEBYTECODE=1\n'
            'sha256sum -c SHA256SUMS\n'
            'python builder.py review-package --package "$PWD"\n')
        (stage / "REVIEW_ON_SCC.sh").write_text(
            '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
            'export PYTHONDONTWRITEBYTECODE=1\n'
            'bash REVIEW_PACKAGE.sh\n'
            'exec /usr/libexec/platform-python runtime.py review\n')
        for name in ("REVIEW_PACKAGE.sh", "REVIEW_ON_SCC.sh"):
            (stage / name).chmod(0o755)
        manifest(stage)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)
    print("C2_SCOUT_GPU_RUNTIME_CANDIDATE_CREATED; no GPU job or submission")


def review_package(directory):
    directory = Path(directory).resolve()
    rows = (directory / "SHA256SUMS").read_text().splitlines()
    seen = set()
    for row in rows:
        digest, separator, name = row.partition("  ")
        rel = Path(name)
        require(separator and re.fullmatch("[0-9a-f]{64}", digest) and
                not rel.is_absolute() and ".." not in rel.parts and name not in seen,
                "invalid package manifest row")
        seen.add(name)
        path = directory / rel
        require(path.is_file() and not path.is_symlink() and sha(path) == digest,
                "package file changed: " + name)
    spec = json.loads((directory / "contract.json").read_text())
    source_spec = yaml.safe_load((directory / "source-spec.yaml").read_text())
    validate_spec(source_spec)
    validate_spec({key: value for key, value in spec.items()
                   if key not in ("states", "pipeline_sha256")})
    require(sha(directory / "historical-pipeline.yaml") == spec["pipeline_sha256"],
            "pipeline copy changed")
    add_states(source_spec, json.loads((directory /
                                        "accepted-cpu-contract.json").read_text()),
               directory / "historical-pipeline.yaml")
    require(spec == source_spec, "candidate contract or TPR hash set changed")
    require(not any((directory / x).exists() for x in
                    ("SUBMIT_ON_SCC.sh", "baseline.sge", "hrex.sge")),
            "candidate includes a submission script")
    print("C2_SCOUT_GPU_RUNTIME_PACKAGE_VERIFIED; execution_authorized=False")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("package")
    create.add_argument("--destination", type=Path, required=True)
    create.add_argument("--spec", type=Path, default=SPEC)
    review = sub.add_parser("review-package")
    review.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "package":
        package(args.destination, spec_path=args.spec)
    else:
        review_package(args.package)


if __name__ == "__main__":
    main()
