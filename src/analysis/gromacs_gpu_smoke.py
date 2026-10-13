"""Prepare an immutable, non-submitting GPU qualification package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import yaml


SPEC = Path("docs/gromacs_gpu_stage_a_v1.yaml")
RUNTIME = Path("src/analysis/gromacs_gpu_smoke_runtime.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(spec: dict, lambdas: list[float], output: Path) -> None:
    """Generate a neutral LJ toy; all numeric physics comes from the new spec."""
    f = spec["fixture"]
    side = f["grid_side"]
    count = side**3
    spacing = f["box_nm"] / side
    if spacing <= f["sigma_nm"] or 2 * f["cutoff_nm"] >= f["box_nm"]:
        raise ValueError("overlapping lattice or invalid cutoff/box")
    lines = ["Nonprotein alchemical GPU smoke fixture", str(count)]
    for atom in range(count):
        x, rem = divmod(atom, side * side)
        y, z = divmod(rem, side)
        xyz = [(v + 0.5) * spacing for v in (x, y, z)]
        lines.append(f"{atom+1:5d}{'LJ':<5}{'LJ':>5}{atom+1:5d}"
                     + "".join(f"{v:8.3f}" for v in xyz))
    lines.append(" ".join([str(f["box_nm"])] * 3))
    (output / "conf.gro").write_text("\n".join(lines) + "\n")
    top = ["[ defaults ]", "1 2 no 1.0 1.0", "[ atomtypes ]"]
    for name, eps in (("LJA", f["epsilon_A_kj_mol"]), ("LJB", f["epsilon_B_kj_mol"])):
        top.append(f"{name} {f['mass_u']} 0 A {f['sigma_nm']} {eps}")
    if f["tagged_atom"] != 1:
        raise ValueError("fixture requires the first atom to be the tagged particle")
    for molecule, btype in (("TAG", "LJB"), ("BATH", "LJA")):
        top += ["[ moleculetype ]", f"{molecule} 0", "[ atoms ]",
                f"1 LJA 1 LJ LJ 1 0 {f['mass_u']} {btype} 0 {f['mass_u']}"]
    top += ["[ system ]", "Synthetic neutral LJ alchemy", "[ molecules ]", "TAG 1", f"BATH {count-1}"]
    (output / "topol.top").write_text("\n".join(top) + "\n")
    for state in range(len(lambdas)):
        mdp = {
            "integrator": "sd", "dt": f["dt_ps"], "nsteps": f["nsteps"],
            "cutoff-scheme": "Verlet", "nstlist": f["nstlist"], "pbc": "xyz",
            "coulombtype": "Cut-off", "rcoulomb": f["cutoff_nm"],
            "vdwtype": "Cut-off", "rvdw": f["cutoff_nm"], "vdw-modifier": "Potential-shift",
            "verlet-buffer-tolerance": f["verlet_buffer_tolerance"],
            "DispCorr": "no", "constraints": "none", "pcoupl": "no",
            "tc-grps": "System", "tau-t": f["tau_t_ps"], "ref-t": f["temperature_K"],
            "gen-vel": "yes", "gen-temp": f["temperature_K"],
            "gen-seed": f["gen_seed_base"] + state, "ld-seed": f["ld_seed_base"] + state,
            "comm-mode": "None", "free-energy": "yes", "delta-lambda": 0,
            "init-lambda-state": state, "fep-lambdas": " ".join(map(str, lambdas)),
            "calc-lambda-neighbors": -1, "sc-alpha": 0,
            "nstdhdl": f["output_stride"], "dhdl-derivatives": "yes",
            "dhdl-print-energy": "potential", "separate-dhdl-file": "yes",
            "nstcalcenergy": f["nstcalcenergy"], "nstenergy": f["output_stride"],
            "nstlog": f["output_stride"], "nstxout-compressed": f["coordinate_stride"],
            "nstxout": 0, "nstvout": 0, "nstfout": 0,
        }
        (output / f"state{state:02d}.mdp").write_text(
            "\n".join(f"{k} = {v}" for k, v in mdp.items()) + "\n")


def create_package(destination: Path, root: Path = Path("."), spec_path: Path = SPEC) -> None:
    """Package sources and generated inputs without launching GROMACS or SGE."""
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    spec = yaml.safe_load((root / spec_path).read_text())
    if spec["execution_authorized"] or spec["production_authorized"]:
        raise ValueError("package preparation cannot authorize execution")
    s = spec["scheduler"]
    mps = spec.get("sharing", {}).get("mode") == "private_MPS"
    restart = spec.get("restart")
    ladder = spec.get("stage") == "L"
    stage = "L" if ladder else ("R" if restart else "A")
    ranks, walltime, first_stop, final_step = (20, 1200, 1000, 2000) if ladder else (4, 600, 500, 1000)
    cpu_sharing = spec.get("cpu_sharing")
    if cpu_sharing and (not ladder or cpu_sharing != {
            "mode": "explicit_oversubscription", "affinity_cpus": 16, "mpi_yield_when_idle": 1}):
        raise ValueError("unreviewed CPU sharing scope")
    slots = 16 if cpu_sharing else ranks
    allowed_pes = (("omp", 16), ("omp16", 16)) if cpu_sharing else (
        (("omp", slots),) if mps else (("mpi32", 32), ("omp", 4)))
    expected_gpus = 1 if mps else 4
    if ((s["ranks"], s["gpus"], s["threads"], s["walltime_seconds"], s["attempts"]) != (ranks, expected_gpus, 1, walltime, 1)
            or (s["pe"], s["slots"]) not in allowed_pes
            or (spec.get("sharing") and not mps)):
        raise ValueError("qualification resource scope changed; review a new implementation")
    if ladder and (not mps or not restart or
                   ("prepared_source" in spec and not (cpu_sharing and s["pe"] == "omp16")) or
                   spec["scope"] != "synthetic_twenty_rank_one_gpu_graceful_restart_only" or
                   spec["fixture"]["lambda_indices"] != list(range(20)) or
                   s["work_deadline_seconds"] != 1020):
        raise ValueError("larger-ladder scope changed; full-ladder preparation or verified import required")
    if restart and (not mps or restart["first_stop_step"] != first_stop or
                    restart["final_step"] != spec["fixture"]["nsteps"] or restart["final_step"] != final_step or
                    spec["fixture"]["replex"] != 100 or
                    not restart["append"] or restart["abrupt_failure_injection"] or
                    restart["checkpoint"] != "smoke.cpt" or
                    (restart["first_checkpoint_part"], restart["final_checkpoint_part"]) != (1, 2) or
                    restart["phase1_expected_exchange_steps"] != list(range(100, first_stop, 100)) or
                    restart["combined_expected_exchange_steps"] != list(range(100, final_step, 100))):
        raise ValueError("restart scope changed; review a new implementation")
    walltime_text = f"{walltime // 3600:02d}:{walltime % 3600 // 60:02d}:{walltime % 60:02d}"
    pipeline = root / spec["fixture"]["lambda_source"]
    all_lambdas = yaml.safe_load(pipeline.read_text())["fep"]["lambda_vector"]
    indices = spec["fixture"]["lambda_indices"]
    if len(all_lambdas) != 20 or indices != sorted(set(indices)) or len(indices) != s["ranks"]:
        raise ValueError("invalid source lambda selection")
    lambdas = [all_lambdas[i] for i in indices]
    if lambdas != sorted(set(lambdas)):
        raise ValueError("lambda values must be strictly increasing")
    spec["states"] = [dict(directory=f"state{i:02d}", local_index=i,
                           source_index=j, lambda_value=all_lambdas[j]) for i, j in enumerate(indices)]
    spec["pipeline_sha256"] = digest(pipeline)
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / "package"
        package.mkdir()
        (package / "inputs").mkdir()
        fixture(spec, lambdas, package / "inputs")
        (package / "contract.json").write_text(json.dumps(spec, indent=2) + "\n")
        shutil.copyfile(root / spec_path, package / "source-spec.yaml")
        shutil.copyfile(pipeline, package / "historical-pipeline.yaml")
        shutil.copyfile(root / RUNTIME, package / "runtime.py")
        shutil.copyfile(root / "src/analysis/gromacs_gpu_smoke.py", package / "generator.py")
        shutil.copyfile(root / "workflow/exchange_feasibility.smk", package / "workflow-source.smk")
        readme = "docs/gromacs_gpu_stage_a_mps_package.md" if mps else "docs/gromacs_gpu_stage_a_package.md"
        if restart:
            readme = "docs/gromacs_gpu_ladder_package.md" if ladder else "docs/gromacs_gpu_restart_package.md"
            if cpu_sharing:
                readme = ("docs/gromacs_gpu_ladder_pe_omp16_package.md" if s["pe"] == "omp16"
                          else "docs/gromacs_gpu_ladder_omp16_package.md")
            shutil.copyfile(root / "src/analysis/gromacs_gpu_restart.py", package / "restart.py")
        shutil.copyfile(root / readme, package / "README.md")
        if mps:
            shutil.copyfile(root / "src/analysis/gromacs_gpu_mps.py", package / "mps.py")
            if not restart:
                shutil.copyfile(root / "scripts/replace_queued_gmx_stage_a_mps.sh", package / "REPLACE_AND_SUBMIT_ON_SCC.sh")
        for command, filename in (("prepare", "PREPARE_ON_SCC.sh"), ("review", "REVIEW_ON_SCC.sh")):
            if "prepared_source" in spec and command == "prepare":
                command = "import-prepared"
            (package / filename).write_text(
                '#!/bin/bash\nset -euo pipefail\ncd "$(dirname "$0")"\n'
                f'exec /usr/libexec/platform-python runtime.py {command}\n')
        job = f'''#!/bin/bash -l
#$ -N gmx-smoke-{stage}
#$ -P {s['project']}
#$ -q {s['queue']}
#$ -pe {s['pe']} {s['slots']}
#$ -l gpus={s['gpus']},gpu_type={s['gpu_type']}
#$ -l h_rt={walltime_text}
#$ -r n
#$ -j y
#$ -cwd
set -euo pipefail
# Must be submitted from the verified package directory after separate review.
exec /usr/libexec/platform-python runtime.py job
'''
        (package / f"stage_{stage}.sge").write_text(job)
        if restart:
            (package / "SUBMIT_ON_SCC.sh").write_text(f'''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
trap 'echo "Stopped: preserve submission-{stage} and return the output; do not rerun." >&2' ERR
sha256sum -c SHA256SUMS
bash REVIEW_ON_SCC.sh
test ! -e attempt
mkdir submission-{stage}
request=(-clear -hard -P {s['project']} -q {s['queue']} -pe {s['pe']} {s['slots']}
         -l gpus={s['gpus']},gpu_type={s['gpu_type']},h_rt={walltime_text} -r n -N gmx-smoke-{stage}
         -S /bin/bash -cwd -j y -o "$PWD/submission-{stage}/job.log")
qsub "${{request[@]}}" -w v stage_{stage}.sge > submission-{stage}/validation.log 2>&1
cat submission-{stage}/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-{stage}/validation.log
qsub "${{request[@]}}" -terse stage_{stage}.sge > submission-{stage}/qsub.log 2>&1
cat submission-{stage}/qsub.log
echo 'One bounded Stage {stage} job submitted; retain this job ID.'
''')
        if ladder:
            (package / "VALIDATE_QUEUE_ON_SCC.sh").write_text(f'''#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
log=$(mktemp "$PWD/queue-validation.XXXXXXXX.log")
qsub -clear -hard -P {s['project']} -q {s['queue']} -pe {s['pe']} {s['slots']} \
  -l gpus={s['gpus']},gpu_type={s['gpu_type']},h_rt={walltime_text} -r n -N gmx-smoke-{stage} \
  -S /bin/bash -cwd -j y -w v stage_{stage}.sge > "$log" 2>&1 || {{ cat "$log"; exit 1; }}
cat "$log"
grep -Fq 'verification: found suitable queue(s)' "$log"
echo 'RESOURCE_REQUEST_VALIDATED; no job submitted; immediate availability is not guaranteed.'
''')
        manifest = "".join(f"{digest(p)}  {p.relative_to(package)}\n"
                           for p in sorted(package.rglob("*")) if p.is_file())
        (package / "SHA256SUMS").write_text(manifest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", required=True, type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    create_package(args.package_dir, spec_path=args.spec)
    print(f"Created GPU qualification package: {args.package_dir}; no job submitted")


if __name__ == "__main__":
    main()
