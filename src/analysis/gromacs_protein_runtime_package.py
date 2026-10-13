"""Build a sealed, non-submitting Stage P protein runtime candidate."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import yaml


SPEC = Path("docs/gromacs_protein_runtime_v1.yaml")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_spec(spec):
    require(spec["schema_version"] == 1 and spec["stage"] == "P" and
            spec["scope"] == "f64a_folded_apo_2sh_r0_twenty_state_technical_restart_only",
            "wrong Stage P runtime scope")
    require(spec["execution_authorized"] is False and
            spec["production_authorized"] is False,
            "candidate package cannot grant execution authorization")
    source = spec["prepared_source"]
    require(source["manifest_sha256"] ==
            "858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9" and
            source["source_spec_sha256"] ==
            "155a24a60191334c0c06a3e02d3c21ecf51cea0902f5ebe5e53370b3c6c322cf",
            "Stage P input identity changed")
    require(spec["image"]["sha256"] ==
            "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee",
            "r6 SIF identity changed")
    s = spec["scheduler"]
    require((s["project"], s["queue"], s["pe"], s["slots"], s["gpus"],
             s["gpu_type"], s["ranks"], s["threads"], s["walltime_seconds"],
             s["work_deadline_seconds"], s["attempts"]) ==
            ("rise-batteries", "l40s", "omp16", 16, 1, "L40S", 20, 1, 1800, 1560, 1),
            "unreviewed Stage P scheduler scope")
    require((s["stop_bytes"], s["cap_bytes"], s["min_free_bytes"]) ==
            (1610612736, 2147483648, 3221225472), "unreviewed storage bounds")
    require(spec["cpu_sharing"] == {"mode": "explicit_oversubscription",
            "affinity_cpus": 16, "mpi_yield_when_idle": 1}, "wrong CPU sharing")
    require(spec["sharing"]["mode"] == "private_MPS", "private MPS required")
    f = spec["fixture"]
    require(f["lambda_indices"] == list(range(20)) and f["nsteps"] == 2000 and
            float(f["dt_ps"]) == 0.002 and f["replex"] == 100 and
            f["output_stride"] == 100 and f["coordinate_stride"] == 200 and
            isinstance(f["exchange_seed"], int) and f["exchange_seed"] > 0,
            "protein TPR schedule changed")
    r = spec["restart"]
    require(r["first_stop_step"] == 1000 and r["final_step"] == 2000 and
            (r["first_checkpoint_part"], r["final_checkpoint_part"]) == (1, 2) and
            r["checkpoint"] == "smoke.cpt" and r["append"] is True and
            r["abrupt_failure_injection"] is False and
            r["phase1_expected_exchange_steps"] == list(range(100, 1000, 100)) and
            r["combined_expected_exchange_steps"] == list(range(100, 2000, 100)),
            "unreviewed protein restart schedule")


def create_package(destination, root=Path("."), spec_path=SPEC):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    require(not destination.exists(), "refusing to overwrite runtime package")
    spec_path = root / spec_path
    spec = yaml.safe_load(spec_path.read_text())
    validate_spec(spec)
    pipeline = root / spec["fixture"]["lambda_source"]
    vector = [float(value) for value in yaml.safe_load(pipeline.read_text())["fep"]["lambda_vector"]]
    require(len(vector) == 20 and all(a < b for a, b in zip(vector, vector[1:])),
            "historical lambda vector changed")
    spec["states"] = [{"directory": "state{:02d}".format(i), "local_index": i,
                       "source_index": i, "lambda_value": vector[i]} for i in range(20)]
    spec["pipeline_sha256"] = digest(pipeline)
    require(spec["pipeline_sha256"] ==
            "af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29",
            "historical pipeline changed")
    with tempfile.TemporaryDirectory() as temporary:
        package = Path(temporary) / "package"
        package.mkdir()
        (package / "contract.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        sources = {
            spec_path: "source-spec.yaml",
            pipeline: "historical-pipeline.yaml",
            root / "src/analysis/gromacs_gpu_smoke_runtime.py": "smoke_runtime.py",
            root / "src/analysis/gromacs_protein_runtime.py": "runtime.py",
            root / "src/analysis/gromacs_protein_runtime_checks.py": "protein_checks.py",
            root / "src/analysis/gromacs_protein_restart.py": "restart.py",
            root / "src/analysis/gromacs_gpu_mps.py": "mps.py",
            root / "docs/gromacs_protein_runtime_package.md": "README.md",
        }
        for source, name in sources.items():
            shutil.copy2(source, package / name)
        for command, filename in (("import-protein-prepared", "IMPORT_ON_SCC.sh"),
                                  ("review", "REVIEW_ON_SCC.sh")):
            (package / filename).write_text(
                '#!/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\n'
                'exec /usr/libexec/platform-python runtime.py ' + command + '\n')
        (package / "VALIDATE_QUEUE_ON_SCC.sh").write_text('''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS > queue-package-check.log
log=$(mktemp "$PWD/queue-validation.XXXXXXXX.log")
qsub -clear -hard -P rise-batteries -q l40s -pe omp16 16 \\
  -l gpus=1,gpu_type=L40S,h_rt=00:30:00 -r n -N gmx-protein-P \\
  -S /bin/bash -cwd -j y -w v stage_P.sge > "$log" 2>&1 || { cat "$log"; exit 1; }
cat "$log"
grep -Fq 'verification: found suitable queue(s)' "$log"
echo 'PROTEIN_RESOURCE_REQUEST_VALIDATED; no job submitted.'
''')
        (package / "stage_P.sge").write_text('''#!/bin/bash -l
#$ -N gmx-protein-P
#$ -P rise-batteries
#$ -q l40s
#$ -pe omp16 16
#$ -l gpus=1,gpu_type=L40S
#$ -l h_rt=00:30:00
#$ -r n
#$ -j y
#$ -cwd
set -euo pipefail
exec /usr/libexec/platform-python runtime.py job
''')
        (package / "SUBMIT_ON_SCC.sh").write_text('''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
trap 'echo "Stopped: preserve submission-P and return the output; do not rerun." >&2' ERR
sha256sum -c SHA256SUMS > package-check-before-submit.log
bash REVIEW_ON_SCC.sh
test ! -e attempt
mkdir submission-P
request=(-clear -hard -P rise-batteries -q l40s -pe omp16 16
         -l gpus=1,gpu_type=L40S,h_rt=00:30:00 -r n -N gmx-protein-P
         -S /bin/bash -cwd -j y -o "$PWD/submission-P/job.log")
qsub "${request[@]}" -w v stage_P.sge > submission-P/validation.log 2>&1
cat submission-P/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-P/validation.log
qsub "${request[@]}" -terse stage_P.sge > submission-P/qsub.log 2>&1
cat submission-P/qsub.log
echo 'One bounded protein technical job submitted; retain this job ID.'
''')
        manifest = "".join("{}  {}\n".format(digest(path), path.relative_to(package))
                           for path in sorted(package.rglob("*")) if path.is_file())
        (package / "SHA256SUMS").write_text(manifest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    create_package(args.package_dir, spec_path=args.spec)
    print("Created protein technical candidate; no import, GPU job or submission")


if __name__ == "__main__":
    main()
