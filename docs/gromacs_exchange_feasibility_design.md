# C1 GROMACS Hamiltonian-exchange feasibility — 2026-09-18

## Current status — 2026-09-24

The combined MPI/CUDA image has now been built and its identity/dependencies
verified: see the [r6 evidence record](gromacs_hrex_sif_r6_verification.md).
No new build is needed. The next step is the
[bounded GPU smoke-test draft](gromacs_gpu_smoke_plan.md), requested for planning
only: separate four-rank and 20-rank synthetic tests, with sharing admission before
the latter. No GPU execution or protein arm is authorized.

The decision, table and sequence below preserve the September 18–21 assessment.
Their unbuilt-image statements are historical and superseded by the r6 record;
the graceful restart scope and resource limits for the next proposed step are in
the new smoke plan. The frozen v1 qualification YAML/results remain unchanged and
must not be presented as a current runtime qualification.

## Historical decision — September 18–21

**Conditionally feasible, new build required; not executable now.** GROMACS 2025.3
supports Hamiltonian replica exchange (HREX), but the SCC CUDA binary selected by this
repository is explicitly a serial build: `GMX_MPI=off`, `GMX_THREAD_MPI=off`, and
`MPI library: none`. The historical one-window-per-array-task contract therefore cannot
acquire exchange by adding an MDP option.

This is not a finding that HREX is impossible on SCC. The authenticated 2026-09-19
read-only inventory found a serial CUDA executable and two separate external-MPI CPU
executables, but no combined MPI+CUDA executable below the installed GROMACS 2025.3 tree.
The corrected login-shell inventory then confirmed the build metadata and found no
alternate combined executable. It also confirmed MPI parallel environments on the L40S
queue. A new supported or project-local combined build is therefore required.

**Route selected 2026-09-21:** prepare a project-owned Singularity image with GROMACS
2025.3, OpenMPI 4.1.5, and CUDA 12.8, initially restricted to one 32-slot/four-L40S
host. The pinned definition and SCC build procedure are in
[`gromacs_hrex_singularity_plan.md`](gromacs_hrex_singularity_plan.md). Keeping all 20
ranks and the MPI launcher inside one container on one host avoids cross-host
host/container MPI interoperability. The definition is ready to build but no SIF or
runtime evidence exists yet; this selection does not change `eligible_now: false`.

The machine-readable qualification is
[`gromacs_exchange_qualification_v1.yaml`](gromacs_exchange_qualification_v1.yaml).
Its CPU-only evaluator writes
`results/cpu_qualification/gromacs_exchange_c1_v1/qualification.json` and cannot invoke
GROMACS, MPI, SGE, or a GPU.

The revised publication plan prioritizes a fresh folded-leg F64A baseline/HREX development
comparison, followed by an initially four-mutation SOD1 panel with five independent ladders
per method. Those counts remain planning choices pending precision and resource admission;
they are not an executable arm. No production duration, exchange interval, or GPU submission
is authorized. The historical F64A stop at 15 ns and array contract remain unchanged.

## Why the standing build fails

GROMACS defines Hamiltonians through the free-energy lambda pathway and exchanges complete
states between lambda values. The 2025.3 manual states that replica exchange only works
with MPI. Multi-simulations are launched with ordered state directories through
`gmx_mpi mdrun -multidir ...`; `-replex N` attempts exchanges every `N` steps. A cluster
build is enabled with `-DGMX_MPI=on`; CUDA-aware MPI can improve direct GPU communication,
but correctness and performance still have to be demonstrated on SCC.

Primary documentation:

- [GROMACS 2025.3 replica exchange](https://manual.gromacs.org/2025.3/reference-manual/algorithms/replica-exchange.html)
- [GROMACS 2025.3 `gmx mdrun`](https://manual.gromacs.org/2025.3/onlinehelp/gmx-mdrun.html)
- [GROMACS 2025.3 installation / MPI support](https://manual.gromacs.org/2025.3/install-guide/index.html)

The standing repository contract instead selects
`/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx`, has an empty `mdrun_launcher`, and
dispatches one independent `(variant, leg, window, replicate)` per SGE array task. The
CPU `gmx_mpi` mentioned in the project history has GPU support disabled and is not a
substitute for the required combined build.

## Controlled unit and scheduler shape

One exchange ensemble is exactly one **independently initialized folded-leg realization**:
20 ordered lambda states derived from the same pmx hybrid topology, atom ordering, box,
and ion placement. The core comparison creates no new unfolded legs, so it estimates the
folded-leg mutation free energy rather than folding ΔΔG. Independently initialized
realizations remain separate; walkers are not statistical repeats, and exchange across
realizations is forbidden.

Each ladder requires at least 20 external-MPI ranks—one per state. GROMACS permits more
ranks if the total is a multiple of the number of simulations, but that is not assumed to
be efficient here. The selected first candidate is one `mpi32` L40S host, 20 local ranks,
and four GPUs, with five simulations sharing each GPU if mapping and performance checks
admit it. This is a prospective layout, not an established entitlement: the SCC wrapper
still has to expose all four scheduler-assigned devices inside the container, and the
layout must be benchmarked. The slowest state controls each synchronization interval, so
load imbalance remains part of the resource model.

For the eventual scientific contrast, both fresh arms must use the same admitted build,
MPI layout, directory order, lambda vector, starts, seed policy, checkpoint cadence,
output cadence, and allocated GPU-hour cap. The baseline should use the same coupled
multi-simulation launch with exchange disabled; the intended factor is exchange, not a
different executable or scheduler architecture. Historical F64A continuations are context,
not a matched baseline.

## Admission gates

| Area | Required evidence | Current state |
|---|---|---|
| Build | `gmx_mpi --version`: 2025.3, external MPI, CUDA enabled; exact binary and library identities | Pinned single-node Singularity definition prepared; SIF not built or verified |
| Scheduler | SGE PE definition, slot and GPU consumable semantics, compact placement, maximum request | One-host `mpi32`/four-L40S candidate selected; container GPU exposure unresolved |
| Launch | 20 numerically ordered directories; rank count divisible by 20; `-multidir` and `-replex` complete | Unresolved |
| GPU mapping | Host/rank/`CUDA_VISIBLE_DEVICES` mapping captured; no hard-coded device IDs | Unresolved |
| Physical identity | One hybrid topology and coordinate atom order per ladder; same lambda vector and endpoints; only `init-lambda-state` differs | Design passes; runtime hashes required |
| Energies | `calc-lambda-neighbors=-1`, DHDL/EDR exports, sample counts and state labels reconcile | Design passes; runtime fixture required |
| Exchange history | Attempted/accepted neighbor swaps and assignment history parse from preserved build-specific output | Unresolved |
| Coordinates | Analysis declares state-space versus walker-space and reconstructs permutations for mixing/round-trip metrics | Unresolved |
| Restart | Forced interruption resumes the whole ladder from one synchronized checkpoint boundary; no single-directory repair | Unresolved |
| Accounting | Baseline/HREX use equal allocated GPU-hours, counting synchronization idle time and failed first light | Unresolved |
| Storage | TPR/MDP/topology, logs, checkpoints, energy/DHDL, exchange history, and admitted coordinate cadence fit a frozen cap | Unresolved |

All required gates must be `pass` or `design_pass`. Any `fail` or `unresolved` value keeps
`eligible_now: false`. Passing C1 would authorize only a proposal for the next scoped step;
it would not silently authorize a protein run.

## Read-only SCC inventory completed

The first capture is preserved locally as `c1_scc_inventory.txt` (SHA-256
`9cedb6bf8ed30ba5017610e4ee77bac39c7d09eadf0af5b5f2c803ea71552e6b`). It found
the executables but could not query SGE because the streamed shell was not a login shell.
The completed login-shell capture is `c1_scc_inventory_login.txt` (SHA-256
`fc1f83b89841a1ab12a0d83e44598926590c09b90ebef427d31a8f2621dd5ac9`). The repository
packages the reproducible checks in the read-only
[`capture_scc_exchange_inventory.sh`](../scripts/capture_scc_exchange_inventory.sh)
script. It writes only to standard output and can be streamed from a local clone into an
SCC login shell without copying a file to SCC:

```bash
ssh scc1.bu.edu 'bash -l -s' < scripts/capture_scc_exchange_inventory.sh
```

Its core queries are:

```bash
hostname
module spider gromacs
module avail gromacs
qconf -spl
qconf -sc
/share/pkg.8/gromacs/2025.3/install_gpu/bin/gmx --version
command -v gmx_mpi
gmx_mpi --version
```

For each plausible MPI parallel environment returned by `qconf -spl`, also capture
`qconf -sp <name>`. If a different CUDA-enabled `gmx_mpi` is found, capture its resolved
path, `--version`, linked MPI/CUDA libraries, and `gmx_mpi mdrun -h` lines containing
`multidir`, `replex`, `gputasks`, and checkpoint options. This inventory is read-only and
does not establish runtime correctness.

No combined build exists in the installed 2025.3 tree. The user selected the project-local
Singularity route on 2026-09-21 because native installation and sending the prepared SCC
request were not practical. The versioned
[`container contract`](gromacs_hrex_container_v1.yaml),
[`definition`](../containers/gromacs-2025.3-mpi-cuda-l40s.def), and
[`build procedure`](gromacs_hrex_singularity_plan.md) are now prepared. The local static
validator does not pull images, build software, request an allocation, or run GROMACS.
The SIF must still be built on an SCC build host and its identity evidence preserved.

The earlier [`SCC-supported build request`](scc_gromacs_mpi_cuda_request.md) remains an
unsent fallback, not the active route. No scheduler script or GPU smoke test has been
created or authorized.

## Qualification sequence

1. **Build check — selected, not yet executed:** build the pinned single-node Singularity
   image and record its source/version, configuration, compiler, MPI, CUDA, regression
   tests, and SIF hash.
2. **Non-production launch smoke:** run a very short 20-directory synthetic/free-energy
   ladder solely to prove MPI grouping, ordered state identity, GPU mapping, and exchange
   records. This is not F64A and produces no scientific estimate.
3. **Failure injection:** stop the coupled job after a synchronized checkpoint and prove
   whole-ladder append/restart plus output checksums.
4. **Layout benchmark:** compare compact GPU layouts at fixed steps and report allocated
   GPU-hours, wall time, imbalance, exchange overhead, and storage growth.
5. **Freeze analysis contract:** validate energy-to-state alignment and permutation-aware
   mixing diagnostics on the retained fixture before proposing a protein comparator.

Only after those steps pass should C2 register fresh matched baseline/HREX folded-leg arms.
