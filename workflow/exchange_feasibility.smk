# Work-package C1 technical qualification. This target is CPU-only and cannot submit.

from pathlib import Path


def require_fresh_container_package(wildcards):
    """Protect an existing package before Snakemake can delete its outputs."""
    path = Path("results/container_build_packages") / wildcards.package_id
    if path.exists():
        raise FileExistsError(f"Refusing to replace {path}; choose a fresh package_id")
    return []


def require_fresh_container_report(wildcards):
    """Preserve the earlier static evidence; new packages carry fresh reports."""
    path = Path("results/cpu_qualification/gromacs_exchange_c1_v1/container_spec.json")
    if path.exists():
        raise FileExistsError(f"Refusing to replace {path}; create a fresh container package")
    return []


def require_fresh_runtime_probe_package(wildcards):
    path = Path("results/container_runtime_probe_packages") / wildcards.probe_id
    if path.exists():
        raise FileExistsError(f"Refusing to replace {path}; choose a fresh probe_id")
    return []

rule gromacs_exchange_feasibility:
    input:
        spec="docs/gromacs_exchange_qualification_v1.yaml",
        pipeline="config/pipeline.yaml",
        code="src/analysis/gromacs_exchange_feasibility.py",
    output:
        "results/cpu_qualification/gromacs_exchange_c1_v1/qualification.json",
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_exchange_feasibility "
        "--spec {input.spec:q} --pipeline {input.pipeline:q} --output {output:q}"


# Static validation only: this target never pulls an image, invokes Singularity,
# starts MPI, requests an allocation, or runs GROMACS.
rule gromacs_hrex_container_spec:
    input:
        fresh=require_fresh_container_report,
        spec="docs/gromacs_hrex_container_v1.yaml",
        definition="containers/gromacs-2025.3-mpi-cuda-l40s.def",
        code="src/analysis/gromacs_container_spec.py",
        design="docs/gromacs_hrex_singularity_plan.md",
    output:
        "results/cpu_qualification/gromacs_exchange_c1_v1/container_spec.json",
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_container_spec "
        "--spec {input.spec:q} --output {output:q}"


# Fresh transfer package only; does not connect to SCC or build the image.
rule gromacs_hrex_container_package:
    input:
        require_fresh_container_package,
        "containers/gromacs-2025.3-mpi-cuda-l40s.def",
        "docs/gromacs_hrex_container_v1.yaml",
        "docs/gromacs_hrex_singularity_plan.md",
        "src/__init__.py",
        "src/analysis/__init__.py",
        "src/analysis/gromacs_container_spec.py",
        "tests/test_gromacs_container_spec.py",
        "workflow/exchange_feasibility.smk",
    output:
        directory("results/container_build_packages/{package_id}"),
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_container_spec --package-dir {output:q}"


# Local packaging only: SCC execution is explicit and never recompiles software.
rule gromacs_hrex_runtime_probe_package:
    input:
        require_fresh_runtime_probe_package,
        "containers/gromacs-runtime-probe.def",
        "containers/run_gromacs_runtime_probe.sh",
        "docs/gromacs_runtime_probe.md",
        "src/analysis/gromacs_container_spec.py",
    output:
        directory("results/container_runtime_probe_packages/{probe_id}"),
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_container_spec --runtime-probe-package-dir {output:q}"


def require_fresh_gpu_smoke_package(wildcards):
    path = Path("results/gpu_smoke_packages") / wildcards.package_id
    if path.exists():
        raise FileExistsError(f"Refusing to replace {path}; choose a fresh package_id")
    return []


# Generate inputs and launch/validation tools only. Never invokes qsub or a GPU.
rule gromacs_gpu_stage_a_package:
    input:
        require_fresh_gpu_smoke_package,
        "docs/gromacs_gpu_stage_a_package.md",
        "config/pipeline.yaml",
        "src/analysis/gromacs_gpu_smoke.py",
        "src/analysis/gromacs_gpu_smoke_runtime.py",
        "src/analysis/gromacs_gpu_mps.py",
        "src/analysis/gromacs_gpu_restart.py",
        "scripts/replace_queued_gmx_stage_a_mps.sh",
        "docs/gromacs_gpu_stage_a_mps_package.md",
        "docs/gromacs_gpu_restart_package.md",
        "docs/gromacs_gpu_ladder_package.md",
        "docs/gromacs_gpu_ladder_omp16_package.md",
        "docs/gromacs_gpu_ladder_pe_omp16_package.md",
        "workflow/exchange_feasibility.smk",
        spec=config.get("gpu_smoke_spec", "docs/gromacs_gpu_stage_a_v1.yaml"),
    output:
        directory("results/gpu_smoke_packages/{package_id}"),
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_gpu_smoke --spec {input.spec:q} --package-dir {output:q}"


def require_fresh_mps_probe_package(wildcards):
    path = Path("results/gpu_sharing_probe_packages") / wildcards.package_id
    if path.exists():
        raise FileExistsError(f"Refusing to replace {path}; choose a fresh package_id")
    return []


rule gromacs_mps_probe_package:
    input:
        require_fresh_mps_probe_package,
        "src/analysis/gromacs_mps_probe.py",
        "docs/gromacs_mps_probe_v1.json",
        "docs/gromacs_mps_probe.md",
    output:
        directory("results/gpu_sharing_probe_packages/{package_id}"),
    resources:
        gpu=0,
    shell:
        "python -m src.analysis.gromacs_mps_probe package {output:q}"
