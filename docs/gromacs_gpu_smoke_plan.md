# Bounded GROMACS GPU smoke test — draft 2026-09-24

## Completed selected qualification — 2026-09-28

**Stages A, R and L are accepted** for the synthetic one-GPU path. Full-ladder
job 7763284 completed with 20 ranks, 16 omp16 CPU slots, one L40S/private MPS and
graceful 1000→2000-step restart. Independent review of the user-supplied records
confirmed all 20 checkpoint transitions, 19 exchange rounds/181 swaps, both
20-client MPS overlaps and successful qacct (52 seconds, exit 0). See
[Stage L result](gromacs_gpu_ladder_result.md). No rerun or further GPU work is
selected. Earlier proposal/candidate sections below are history; the original
four-GPU Stage B and protein/scientific qualification are not passed by this result.

## Scheduler-supported revision — 2026-09-28

The user supplied a validation matrix: omp/4, /8 and /16 with one L40S pass;
/20, /28 and /32 fail. See [scheduler evidence](gromacs_gpu_ladder_scheduler_result.md).
The next candidate is [Stage L v2](gromacs_gpu_ladder_omp16_package.md): **20 MPI
ranks and states on 16 CPU slots**, with explicit oversubscription, truthful MPI
slot count, idle yielding and a shared 16-CPU affinity mask checked per rank.
One GPU, one attempt, 20-minute cap and all exchange/restart criteria are retained.
No performance claim follows from this functional test. The older /20 package
below remains immutable rejected-preflight evidence; no GPU attempt occurred.

## Current next milestone — 2026-09-28

The one-GPU/four-rank Stage A and graceful-restart Stage R have passed review,
including qacct. The user requested larger-ladder qualification. The current
package is **Stage L: 20 ranks, 20 omp CPU slots, one L40S, private MPS,
20 minutes maximum, one attempt**, with the full 20-state toy ladder stopped at
1,000 and appended to 2,000 steps. See [Stage L instructions](gromacs_gpu_ladder_package.md)
and [registered specification](gromacs_gpu_ladder_v1.yaml).
Validate scheduler eligibility before fresh exact-SIF input preparation; no
GPU execution is implied by packaging. Current Stage L GPU behavior and scheduler
placement are untested. A pass would qualify this single-GPU synthetic layout.
The original four-GPU Stage B below is preserved as the earlier draft and is
not the current submission layout. No protein arm is selected.

## Original September 24 draft

Status: planning requested; no allocation or execution authorized by this draft.
The companion [planning specification](gromacs_gpu_smoke_v1.yaml) records proposed
limits, not measured results or executable defaults. Submission readiness is false.

Stage A preparation is now implemented in the
[package guide](gromacs_gpu_stage_a_package.md) and its separate
[fixture specification](gromacs_gpu_stage_a_v1.yaml). The local package contains
generated topology/coordinates/MDPs and launch/validation tools. Exact-SIF TPR
generation has now [completed on SCC](gromacs_gpu_stage_a_scc_preparation.md),
with matching package/image identities reported by the user. Stage A is awaiting
its execution decision; Stage B is not implemented or submitted.

The [September 24 preflight](gromacs_gpu_preflight_2026-09-24.md) now records the
current PE/queue configuration, adequate project quota headroom at that snapshot,
and a successful login-host wrapper preview. `acctool` was unavailable on
`scc-i01`; current allocation balance and GPU-host behavior remain unresolved.

## Purpose and existing evidence

Reuse the [verified r6 SIF](gromacs_hrex_sif_r6_verification.md). No rebuild or
repeat of the completed CPU/startup qualification is needed. The next question is
whether this image can run short GPU dynamics, exchange configurations between
lambda states, and resume a coupled ladder on one SCC L40S host.

Use a synthetic, nonprotein alchemical fixture. Passing would establish these
technical operations for that fixture and layout. It would not validate protein
parameters, PME, constrained dynamics, sampling efficiency, a free-energy result,
or CUDA-aware device-to-device MPI transfers. The historical scientific gate and
15 ns F64A stop remain unchanged.

## Proposed resource envelope

Two separate jobs, reviewed between stages; no automatic dependency submission,
retry, rescheduling, or duration extension. Each job gets at most one attempt.
Queue failures and failed preflights consume the attempt and their actual allocation
time. Unused time is not permission for another attempt.

| Stage | Purpose | MPI ranks / GPUs | CPU slots | Walltime cap | Allocated GPU-hour cap |
| --- | --- | --- | --- | --- | --- |
| A | Device mapping and four-state exchange | 4 / 4, one rank per GPU | 32 | 10 min | 2/3 |
| B | Full ladder sharing and whole-ladder restart | 20 / 4, five ranks per GPU | 32 | 20 min | 4/3 |

Both together: **2 allocated GPU-hours and 16 CPU-slot-hours maximum**, including
startup, idle synchronization, failures and evidence collection. These are resource
bounds, not an SU-price estimate. Retain actual SGE accounting. All ranks and the
MPI launcher stay inside the container on one host, with one OpenMP thread/rank.

The candidate reservation is project `rise-batteries`, PE `mpi32` with 32 slots,
`gpus=4`, `gpu_type=L40S`, and the stage-specific `h_rt`. This is a request shape,
not a ready-to-submit script. The September 19 PE/queue snapshot supports this
candidate; refresh it before freezing the launcher. The historical protein array
script and its retry/reschedule behavior do not apply to these coupled jobs.

## Admission before any GPU submission

1. Refresh `qconf -sp mpi32`, the L40S queue configuration and GPU consumable
   definitions, project access, storage quotas and available allocation balance.
   Retain the output. Require a single-host reservation; do not infer it from the
   rank count. Review PE startup/accounting integration for container-local MPI.
2. The wrapper preview has been inspected. Stage A now uses direct
   `singularity exec --cleanenv --contain`, explicit package/tmp binds and `--nv`
   for GPU work, as specified in the package guide. It preserves the scheduler's
   device assignment and does not mount host `/usr/local`. CPU preparation first
   exercises the mounts; GPU-host UUID checks and command capture remain
   mandatory. No nested shell command string is used.
3. Generate, inspect and hash the toy topology, coordinates, resolved MDPs, TPRs,
   state manifest and launch scripts. Validate TPR state indices and common
   topology, atom ordering, masses, temperature and integration parameters.
   Preparation must reject unexplained `grompp` warnings; do not use `-maxwarn`
   to force acceptance. No GPU time is needed for input generation/inspection.
4. Implement package preparation and evidence validation through
   `workflow/exchange_feasibility.smk` and the existing analysis/package modules.
   Use a fresh package/result path. Add checks for meaningful failure cases such
   as missing checkpoints, a changed TPR, duplicated state indices and wrong
   GPU assignments. Freeze the command and manifest before submission review.
5. Confirm stage A's concrete package and allocation scope with the user before
   submitting. Stage B remains withheld until A's evidence and sharing admission
   below have been reviewed. No approval is requested by this planning document.

BU documents scheduler-assigned `CUDA_VISIBLE_DEVICES` and the wrapper's
`--scc-preview`/`--nolocal` options. Preserve the assigned device set; do not choose
physical IDs independently. See [BU GPU usage](https://www.bu.edu/tech/support/research/software-and-programming/gpu-computing/)
and [BU Singularity wrapper](https://www.bu.edu/tech/support/research/software-and-programming/containers/singularity/).

## Synthetic input proposal

Prepare a small periodic, neutral Lennard-Jones system, initially targeting 512
particles. Change one tagged particle's interaction modestly between A and B
states, retaining nonzero interactions at both endpoints. All atoms retain their
identity and mass. Use a fixed-volume, thermostatted trajectory, CPU updates and
no constraints or PME. Exact force-field, thermostat, timestep and seed values
are now declared for Stage A in its fixture specification before TPR generation;
they are not inherited from a protein protocol or silently supplied by code.

Read the 20 lambda values from `config/pipeline.yaml:fep.lambda_vector`; do not
copy and edit that historical configuration. Stage A uses source indices
`[0, 6, 13, 19]` and a four-entry TPR ladder, with local state indices 0–3.
Stage B uses all 20 entries with state indices 0–19. Record both local index and
source index in the manifest. Within each stage, every TPR has the same lambda
array. Differences between state inputs must be explicitly enumerated.

Proposed length: A completes 1,000 steps/state; B completes 2,000 steps/state,
with a planned stop at 1,000. Attempt neighbor exchange every 100 steps using a
recorded seed. Retain all-state foreign-lambda energies (`calc-lambda-neighbors=-1`),
DHDL and energy/log output every 100 steps, and sparse coordinates every 200
steps; no full-precision trajectory, velocities or forces. Cadences and their
compatibility must be validated during preparation. These lengths exercise code
paths; they are not equilibration or statistical sampling targets.

Require GPU short-range work explicitly (`-nb gpu`) and CPU updates
(`-update cpu`); use CPU bonded/PME selection, one OpenMP thread and disable
dynamic load balancing/PME tuning for this fixed layout. Exact argv is frozen by
the package. GROMACS 2025.3 excludes replica exchange from GPU-update support;
external MPI supplies the rank count, not `-ntmpi`.
[GROMACS performance guide](https://manual.gromacs.org/2025.3/user-guide/mdrun-performance.html).

## Stage A: four ranks, one GPU each

Inside the allocation, verify the SIF SHA-256 against the r6 record, host identity,
`PE_HOSTFILE`, `NSLOTS`, inherited device visibility, driver version and compute
mode. Require exactly one execution host, 32 reserved slots and four assigned
L40S devices. Record the CUDA-visible ordinal-to-UUID map inside the actual
container; `nvidia-smi` alone is not proof that CUDA sees only assigned devices.

Resolve per-rank selection from that verified map. Do not replace the scheduler's
device visibility or assume its physical IDs are `0,1,2,3`. Freeze one GROMACS
selection mechanism; do not combine `-gpu_id` and `-gputasks`. Capture rank, host,
PID, state directory, CUDA ordinal, UUID and GROMACS's own GPU task mapping.
The wrapper must preserve scheduler assignment and load the host driver into
the container. Missing `libcuda` on this GPU host is a failure, unlike the earlier
build-host warning.

Run four ordered state directories with one MPI rank/simulation. Verify finite
energies, completion at the planned step, actual short-range GPU work on all
four assigned devices, neighbor exchange attempts and at least one accepted
swap. Inspect all neighbor pairs across the alternating exchange rounds. No
accepted swap makes exchange demonstration incomplete; do not extend the run.
Preserve raw exchange logs and reconstruct a bijective state-to-walker mapping.
Do not require a round trip from such a short test.

Set an internal simulation deadline at seven allocation minutes, reserving three
minutes for shutdown and evidence. A failure stops A and leaves B unsubmitted.

## Stage B: sharing prerequisite, then 20 ranks and restart

Five processes per GPU require either a compatible compute mode or a supported
MPS arrangement. Earlier SCC evidence reported `Exclusive_Process`, so this
prerequisite is unresolved. The presence of `nvidia-cuda-mps-control` alone does
not establish a supported launch procedure. Stage A can qualify four-rank
operation while B remains blocked.

Do not change GPU compute mode, use someone else's MPS server, or start a global
daemon. If SCC supports per-job MPS, freeze its setup first: assigned devices only,
private writable pipe/log directories shared correctly into the container,
same-user clients, verified device remapping, and cleanup of this job's server
after clients exit. MPS may attribute GPU work to its server rather than showing
20 client PIDs in `nvidia-smi`; retain client and rank evidence as well.
NVIDIA explains the compute-mode restriction and MPS process behavior in
[When to use MPS](https://docs.nvidia.com/deploy/mps/when-to-use-mps.html).

With sharing admitted, repeat the allocation/device checks and launch exactly
20 ranks in ordered directories, five mapped to each assigned GPU. Do not use
oversubscription flags to hide an incorrect reservation. Run the first 1,000
steps with exchange, terminate normally, and preserve the full checkpoint set
and pre-restart evidence. Require all 20 checkpoints to exist and describe the
same step/time. Restart the entire ladder with unchanged mapping and original
2,000-step TPRs, explicitly reading every checkpoint and appending output.

The packaging implementation must verify the proposed first-part step override
against GROMACS 2025.3. A missing checkpoint must fail before launch: `-cpi` alone
can silently start a fresh run when its file is absent. Retain original output
paths and checkpoint checksum validation. Logs may legitimately lose their final
performance summary during append; compare the checkpoint-covered data, not an
assumption that every complete log remains a byte-for-byte prefix.
[GROMACS restart behavior](https://manual.gromacs.org/2025.3/onlinehelp/gmx-mdrun.html),
[Appending and checkpoints](https://manual.gromacs.org/2025.3/user-guide/managing-simulations.html).

Require all states to reach step 2,000, finite correctly labelled foreign-state
energies, exchange after restart and a continuous permutation history. Handle
restart boundary records explicitly so analysis does not count a step or swap
twice. GPU trajectories need not be bitwise identical to an uninterrupted run.
This tests a **planned, graceful whole-ladder restart**; arbitrary process death,
node failure and recovery from mismatched checkpoints remain unqualified.
In particular, do not introduce an abrupt client kill into this first MPS test.

Set the internal simulation deadline at 17 allocation minutes, with three
minutes left for shutdown/evidence. Sharing failure, CUDA error 46, CPU fallback,
MPI error, nonfinite output, checkpoint mismatch or a time/storage limit ends
the attempt. No automatic retry or fallback to a different rank count.

## Evidence, storage and decision

Budget at most 2 GiB of new smoke-test files in total, including working copies
and retained evidence; the existing SIF/recovery archive is referenced in place.
Require fresh quota/free-space checks with at least 4 GiB available in each
destination filesystem. Preparation estimates output size; the job monitors
growth and starts orderly termination at 1.5 GiB. The implementation must define
monitoring/retention behavior before it can claim to enforce this proposed cap.

Retain the package/config/TPR hashes, raw scheduler and wrapper evidence, complete
commands, rank/device map, logs, energy/DHDL, sparse coordinates, both checkpoint
sets for B, MPI/MPS diagnostics, return statuses, walltime and SGE accounting.
Hash an inventory of retained outputs. Keep pre-restart evidence immutable.

Report A and B separately as pass, fail or incomplete, with evidence paths.
Compilation metadata, a zero exit status or an accepted swap alone is insufficient.
Validate state labels and foreign-energy columns against the TPR manifest, and
exchange records against a permutation parser. An accounting record that has not
yet appeared stays pending; do not manufacture a billed SU value.

After both stages pass, the next decision is whether to design a separate
protein-representative qualification and matched-cost benchmark. No protein
sampling, production performance claim, or new scientific arm follows
automatically from this smoke test.
