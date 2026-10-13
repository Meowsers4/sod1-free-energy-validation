"""Build/review a separate F64A C2 scout execution release without submitting."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile


CANDIDATE = Path("packages/f64a-c2-scout-gpu-runtime-candidate-20260929-v4")
CANDIDATE_MANIFEST_SHA256 = "71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df"
SCOPE = "f64a_folded_apo_2sh_r0_paired_100ps_timing_scout_release"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_manifest(path):
    rows = {}
    for line in Path(path).read_text().splitlines():
        digest, sep, name = line.partition("  ")
        part = Path(name)
        require(sep and re.fullmatch("[0-9a-f]{64}", digest) and
                name not in rows and not part.is_absolute() and
                ".." not in part.parts, "invalid manifest row")
        rows[name] = digest
    return rows


def manifest(directory):
    rows = ["{}  {}\n".format(sha(p), p.relative_to(directory))
            for p in sorted(directory.rglob("*"))
            if p.is_file() and p.name != "SHA256SUMS"]
    (directory / "SHA256SUMS").write_text("".join(rows))
    return len(rows)


def contract_from_candidate(candidate, selection=None):
    source = (candidate / "candidate-contract.json") if (
        candidate / "candidate-contract.json").exists() else candidate / "contract.json"
    base = json.loads(source.read_text())
    require(base["execution_authorized"] is False and
            base["production_authorized"] is False and
            len(base["states"]) == 20,
            "accepted candidate is not inert/complete")
    require(selection is None or
            (selection.get("arms") == ["baseline", "hrex"] and
             selection.get("su_disposition") in ("verified", "explicitly_waived") and
             isinstance(selection.get("user_selection"), str) and
             isinstance(selection.get("preflight_evidence"), str) and
             all(selection.get(x) for x in
                 ("user_selection", "preflight_evidence"))),
            "selected release requires both arms, SU disposition, preflight and user decision")
    base["scope"] = SCOPE
    base["execution_authorized"] = selection is not None
    base["selected_technical_arms"] = ["baseline", "hrex"] if selection else []
    base["selection_record"] = selection
    base["release_source_candidate_sha256"] = CANDIDATE_MANIFEST_SHA256
    return base


def sge_script(arm):
    return ("#!/bin/bash -l\n"
            "#$ -N c2-scout-{arm}\n"
            "#$ -P rise-batteries\n"
            "#$ -q l40s\n"
            "#$ -pe omp16 16\n"
            "#$ -l gpus=1,gpu_type=L40S\n"
            "#$ -l h_rt=02:00:00\n"
            "#$ -r n\n"
            "#$ -j y\n"
            "#$ -cwd\n"
            "set -euo pipefail\n"
            "export PYTHONDONTWRITEBYTECODE=1\n"
            "exec /usr/libexec/platform-python runtime.py job {arm}\n").format(arm=arm)


def submit_script(arm):
    return ('''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONDONTWRITEBYTECODE=1
bash REVIEW_ON_SCC.sh
/usr/libexec/platform-python runtime.py permit {arm}
test ! -e attempts/{arm}
mkdir submission-{arm}
request=(-clear -hard -P rise-batteries -q l40s -pe omp16 16
         -l gpus=1,gpu_type=L40S,h_rt=02:00:00 -r n -N c2-scout-{arm}
         -S /bin/bash -cwd -j y -o "$PWD/submission-{arm}/job.log")
qsub "${{request[@]}}" -w v {arm}.sge > submission-{arm}/validation.log 2>&1
cat submission-{arm}/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-{arm}/validation.log
qsub "${{request[@]}}" -terse {arm}.sge > submission-{arm}/qsub.log 2>&1
cat submission-{arm}/qsub.log
echo 'One bounded {arm} technical scout submitted; retain this job ID.'
''').format(arm=arm)


def package(destination, root=Path("."), selection=None):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    require(not destination.exists(), "refusing to overwrite sealed release")
    candidate = root / CANDIDATE
    require(sha(candidate / "SHA256SUMS") == CANDIDATE_MANIFEST_SHA256,
            "accepted candidate manifest changed")
    for name, digest in read_manifest(candidate / "SHA256SUMS").items():
        require(sha(candidate / name) == digest, "candidate file changed: " + name)
    spec = contract_from_candidate(candidate, selection)
    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp) / "release"
        stage.mkdir()
        (stage / "contract.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        mapping = {
            "runtime.py": "core_runtime.py", "smoke_runtime.py": "smoke_runtime.py",
            "mps.py": "mps.py", "scout_checks.py": "scout_checks.py",
            "protein_checks.py": "protein_checks.py",
            "accepted-cpu-contract.json": "accepted-cpu-contract.json",
            "historical-pipeline.yaml": "historical-pipeline.yaml",
            "source-spec.yaml": "candidate-source-spec.yaml",
            "contract.json": "candidate-contract.json",
            "SHA256SUMS": "candidate-SHA256SUMS",
        }
        for source, target in mapping.items():
            shutil.copy2(candidate / source, stage / target)
        shutil.copy2(root / "src/analysis/f64a_c2_scout_gpu_release_runtime.py",
                     stage / "runtime.py")
        shutil.copy2(root / "src/analysis/f64a_c2_scout_gpu_release_package.py",
                     stage / "builder.py")
        (stage / "README.txt").write_text(
            "F64A C2 paired technical execution release.\n"
            "Review contract.json before any submission. An inactive contract denies all jobs.\n"
            "Baseline must pass technical and qacct review before HREX submission.\n"
            "Each arm has one attempt, one L40S, 16 slots, two hours, no reschedule.\n"
            "No production or free-energy inference is authorized.\n")
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
        for arm in ("baseline", "hrex"):
            (stage / (arm + ".sge")).write_text(sge_script(arm))
            (stage / ("SUBMIT_" + arm.upper() + "_ON_SCC.sh")).write_text(
                submit_script(arm))
        for name in ("REVIEW_PACKAGE.sh", "REVIEW_ON_SCC.sh",
                     "SUBMIT_BASELINE_ON_SCC.sh", "SUBMIT_HREX_ON_SCC.sh"):
            (stage / name).chmod(0o755)
        manifest(stage)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)
    print("C2_SCOUT_EXECUTION_RELEASE_CREATED; execution_authorized={}; no job submitted".format(
        selection is not None))


def review_package(directory):
    directory = Path(directory).resolve()
    rows = read_manifest(directory / "SHA256SUMS")
    for name, digest in rows.items():
        require((directory / name).is_file() and
                not (directory / name).is_symlink() and
                sha(directory / name) == digest,
                "release package file changed: " + name)
    require(sha(directory / "candidate-SHA256SUMS") == CANDIDATE_MANIFEST_SHA256,
            "candidate identity changed")
    candidate_rows = read_manifest(directory / "candidate-SHA256SUMS")
    mapping = {"runtime.py": "core_runtime.py", "smoke_runtime.py": "smoke_runtime.py",
               "mps.py": "mps.py", "scout_checks.py": "scout_checks.py",
               "protein_checks.py": "protein_checks.py",
               "accepted-cpu-contract.json": "accepted-cpu-contract.json",
               "historical-pipeline.yaml": "historical-pipeline.yaml",
               "source-spec.yaml": "candidate-source-spec.yaml",
               "contract.json": "candidate-contract.json"}
    for source, target in mapping.items():
        require(sha(directory / target) == candidate_rows[source],
                "accepted candidate source changed: " + source)
    spec = json.loads((directory / "contract.json").read_text())
    candidate = json.loads((directory / "candidate-contract.json").read_text())
    expected = contract_from_candidate(directory, spec.get("selection_record"))
    require(spec == expected and candidate["execution_authorized"] is False and
            candidate["production_authorized"] is False,
            "release contract changed")
    for arm in ("baseline", "hrex"):
        require((directory / (arm + ".sge")).read_text() == sge_script(arm) and
                (directory / ("SUBMIT_" + arm.upper() + "_ON_SCC.sh")).read_text() ==
                submit_script(arm), "SGE request or submission guard changed")
    print("C2_SCOUT_EXECUTION_RELEASE_PACKAGE_VERIFIED; execution_authorized={}".format(
        spec["execution_authorized"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("package")
    build.add_argument("--destination", type=Path, required=True)
    build.add_argument("--selection-file", type=Path)
    review = sub.add_parser("review-package")
    review.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "package":
        selection = json.loads(args.selection_file.read_text()) if args.selection_file else None
        package(args.destination, selection=selection)
    else:
        review_package(args.package)


if __name__ == "__main__":
    main()
