# SCC exchange inventory — completed 2026-09-19

## Provenance

- Initial non-login capture: `c1_scc_inventory.txt`, SHA-256
  `9cedb6bf8ed30ba5017610e4ee77bac39c7d09eadf0af5b5f2c803ea71552e6b`
- Complete login-shell capture: `c1_scc_inventory_login.txt`, SHA-256
  `fc1f83b89841a1ab12a0d83e44598926590c09b90ebef427d31a8f2621dd5ac9`
- Host: `scc1.bu.edu`
- Complete-capture UTC time: `2026-09-19T23:35:23Z`
- Both captures were read-only; no job or allocation was requested.

## Build result

The executable search below `/share/pkg.8/gromacs/2025.3` found exactly three GROMACS
front ends:

1. `install_gpu/bin/gmx`: GROMACS 2025.3, `MPI library: none`, `GPU support: CUDA`,
   CUDA 12.8, AVX2.
2. `install_mpi_avx2/bin/gmx_mpi`: GROMACS 2025.3, OpenMPI 4.1.5,
   `GPU support: disabled`, AVX2.
3. `install_mpi/bin/gmx_mpi`: GROMACS 2025.3, OpenMPI 4.1.5,
   `GPU support: disabled`, AVX.

No `gmx_mpi` exists in the CUDA install and no CUDA-linked `gmx_mpi` was found elsewhere
in this GROMACS version tree. The installed 2025.3 package therefore separates the CUDA
and external-MPI capabilities required together for the proposed HREX design. C1's
`build.combined_mpi_cuda` gate is now **fail**, rather than unresolved.

The MPI binaries expose `-multidir`, `-replex`, `-reseed`, checkpoint and GPU-mapping
options, confirming the software interface. They cannot provide GPU HREX because GPU
support is disabled in those binaries. The SCC module description likewise selects `gmx`
on GPU nodes and `gmx_mpi` on CPU-only nodes; it does not expose a combined executable.

## Scheduler result

The `l40s` queue contains ten hosts (`scc-501` through `scc-506` and `scc-510` through
`scc-513`), each with 32 CPU slots and four L40S GPUs. It permits the `mpi8`, `mpi16`,
`mpi28`, and `mpi32` parallel environments and has a 48-hour hard wall-time limit. The
parallel-environment definitions use the SCC MPI start/stop integration and fixed per-host
allocation rules. C1's `scheduler.parallel_environment` gate is therefore **pass**.

The GPU complexes are requestable, and `gpus` is an integer `JOB` consumable. The ten queue
hosts reported 21 available GPU units in this point-in-time snapshot, but this is shared,
dynamic capacity—not an entitlement or proof that a coupled request will be placed. The
read-only configuration does not fully establish how a multi-host PE job's job-level GPU
request is distributed across hosts or how ranks receive device visibility. The
`scheduler.coupled_gpu_placement` gate remains **unresolved** pending SCC confirmation or a
separately authorized scheduler/runtime smoke test.

## C1 consequence

No further read-only inventory is required. The next decision is the build route:

1. Prefer an SCC-supported GROMACS 2025.3 build combining external MPI and CUDA, using the
   installed GCC 12.2.0, OpenMPI 4.1.5 and CUDA 12.8 stack; or
2. Separately authorize a project-local pinned build and its storage/test plan.

After a combined build exists, a bounded non-production technical package must still prove
the exact PE/GPU request, rank/device mapping, 20-directory HREX launch, state-history
export, synchronized checkpoint restart, cost, and storage. None of those runtime gates is
passed by this inventory.

## Initial capture limitation (resolved)

The command was streamed into `bash -s`, which did not initialize the full SCC login
environment. `MODULEPATH` and `SGE_ROOT` were unset. Consequently:

- `module spider/avail` could not inspect alternate installed modules;
- the binaries could not load MKL/compiler runtime libraries to print authoritative
  `--version` metadata; and
- `qconf`/`qhost` could not report parallel environments, GPU complexes, queues, or
  placement capacity.

The login-shell rerun resolved all three environment failures. It ended with
`All read-only inventory sections completed.`
