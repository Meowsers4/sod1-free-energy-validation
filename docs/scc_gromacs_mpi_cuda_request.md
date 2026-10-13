# Draft SCC software request — combined MPI+CUDA GROMACS 2025.3

Prepared 2026-09-21 from the completed read-only SCC inventory. This is a draft for the
official [RCS SCC Application Request Form](https://www.bu.edu/tech/support/research/software-and-programming/software-and-applications/request-software/).
It has not been submitted.

## Form fields

| Field | Proposed entry |
|---|---|
| BU Login Name | `bodeb` |
| Name | **User must fill** |
| Email | **User must fill** |
| SCC Project | `rise-batteries` |
| SCC Lead Project Investigator | **User must fill/verify** |
| Application Name | GROMACS — combined external-MPI and CUDA build |
| Version | 2025.3 |
| Source/Homepage | `https://manual.gromacs.org/documentation/2025.3/download.html` |
| Level of interest | Required for research |

## Justification text to paste

> I need a GROMACS 2025.3 executable that combines external MPI support and the CUDA
> backend for a controlled Hamiltonian replica-exchange free-energy study on the SCC L40S
> queue. Replica exchange uses GROMACS multi-simulation communication (`gmx_mpi mdrun
> -multidir ... -replex ...`), so external MPI and GPU support must be enabled in the same
> executable.
>
> The current `gromacs/2025.3` installation exposes these capabilities in separate builds:
>
> - `/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx` reports `MPI library: none` and
>   `GPU support: CUDA` (CUDA 12.8).
> - `/share/pkg.8/gromacs/2025.3/install_mpi_avx2/bin/gmx_mpi` reports OpenMPI 4.1.5 and
>   `GPU support: disabled`.
> - `/share/pkg.8/gromacs/2025.3/install_mpi/bin/gmx_mpi` also reports OpenMPI 4.1.5 and
>   `GPU support: disabled`.
>
> Could RCS provide or recommend a supported GROMACS 2025.3 build configured with external
> MPI (`GMX_MPI=ON`) and CUDA (`GMX_GPU=CUDA`), preferably compatible with the installed
> GCC 12.2.0, OpenMPI 4.1.5, CUDA 12.8, and L40S nodes? A separate module/build suffix is
> fine; preserving the existing builds is preferred.
>
> The immediate technical qualification uses one 20-state ladder (at least 20 MPI ranks)
> and will initially benchmark compact layouts that may share four or eight GPUs among
> ranks. No production study will start until a bounded technical smoke test passes.

## Additional scheduler question

Paste this after the justification if the form provides sufficient space; otherwise use
the form's additional-information field or ask in the resulting ticket:

> The `l40s` queue lists `mpi8`, `mpi16`, `mpi28`, and `mpi32` parallel environments.
> The `gpus` complex is a requestable integer `JOB` consumable. For one multi-host MPI job,
> what request syntax does RCS recommend to reserve GPUs on every allocated host and map
> ranks to scheduler-assigned devices? For example, is a 20-rank layout using `mpi8` or
> `mpi16` with four GPUs per host supported, and how should per-host GPU visibility be
> interpreted? We will not hard-code device IDs.

## Acceptance evidence requested from RCS

The installed executable should produce one internally consistent version report containing:

```text
GROMACS version: 2025.3
MPI library: MPI
MPI library version: Open MPI ...
GPU support: CUDA
```

It should also expose `mdrun` options `-multidir`, `-replex`, `-reseed`, `-gputasks`,
`-cpi`, and `-cpo`. This establishes build capability only; the project will separately
validate a short non-production ladder, rank/device mapping, synchronized restart and
output/state-history handling.

## Evidence available if RCS asks

- [Completed local inventory summary](scc_exchange_inventory_2026-09-19.md)
- Raw capture `c1_scc_inventory_login.txt`, SHA-256
  `fc1f83b89841a1ab12a0d83e44598926590c09b90ebef427d31a8f2621dd5ac9`
- Queue: `l40s`, ten 32-slot/four-L40S hosts, hard wall time 48 hours
- Existing module: `gromacs/2025.3`

Do not attach unrelated project data, credentials, simulation structures, or historical
production outputs to the request.

## If RCS declines or recommends a user build

Do not improvise an installation in SCC home. The home quota is 10 GB and this project's
software/data must use a separately declared project path and storage allowance. Before a
project-local build, freeze:

1. installation prefix under `/projectnb/rise-batteries`;
2. exact source archive and checksum;
3. compiler, OpenMPI, CUDA, CMake and FFT dependencies;
4. configure flags including external MPI and CUDA;
5. build/regression-test commands and retained logs;
6. binary/library hashes and a dedicated environment helper; and
7. cleanup size, rollback path, and the same build acceptance checks above.

A local installation and GPU/MPI smoke test require separate authorization; this draft does
not authorize either.
