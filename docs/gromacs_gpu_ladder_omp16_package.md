# Stage L v2: twenty states, sixteen CPU slots, one L40S

Selected for preparation on 2026-09-28 after accepted four-rank exchange (7762792)
and graceful restart (7763081). This extends the proven private-MPS launch path
using the unchanged, verified r6 SIF. No image rebuild is required.

## Scheduler correction

The supplied validation matrix accepted one L40S with omp/4, /8 and /16 slots,
and rejected /20, /28 and /32. It does not identify the underlying restriction;
we do not infer a cluster-wide maximum. V1 never reached CPU preparation in the
chained commands and was not submitted. Preserve it as rejected preflight evidence.

V2 retains all 20 MPI ranks/states on **16 reserved CPU slots**. The MPI launcher
reports `localhost:16`, uses `--np 20 --oversubscribe --bind-to none`, and sets
`mpi_yield_when_idle=1` to yield during MPI waits. It never advertises 20 CPU slots.
The job restricts its Linux CPU affinity to 16 IDs from its inherited permitted
mask before starting MPS or MPI. Children inherit this common mask; each rank
verifies and records the same 16-ID mask before exec. If fewer than 16 IDs are
available or a rank's mask changes, the job fails. This does not assert exclusive
ownership of physical cores. GROMACS CPU pinning is disabled and OMP threads=1.

Thus 20 processes time-share at most 16 allowed logical CPUs. This is a bounded
functional qualification, not a throughput comparison. GPU count, full lambda
vector, toy physics, seeds, exchange/restart criteria, duration, storage cap and
one-attempt limit are unchanged. Original one-thread-per-rank behavior is retained;
CPU oversubscription is now explicit, instead of quietly shrinking the allocation.
Open MPI documents the need to report the actual slot count and its yielding
mode for oversubscribed launches in its
[v4-and-earlier MPI launch FAQ](https://www.open-mpi.org/faq/?category=running#oversubscribing).
GPU/runtime qualification of this combination remains pending on SCC.

## Registered scope

- One node, one assigned L40S, **20 MPI ranks, omp/16 CPU slots**, one thread/rank.
  Every rank uses container device 0, verified against the assigned GPU UUID.
  All 20 rank PIDs must match simultaneous MPS client PIDs in **each** launch.
- Same 512-atom neutral LJ toy, now using **all 20 historical lambda values** in
  order. All foreign-state energies are recorded. Physics and seeds remain from
  the previous toy; no protein input is used or altered.
- 2,000 steps per state at 0.001 ps: first stop normally at 1,000, seal all
  checkpoints/outputs, then resume unchanged TPRs with `-cpi smoke.cpt -append`.
  This is two MPI launches in one allocation, with one private MPS service.
- **One attempt, 20 minutes maximum**, at most 1/3 allocated GPU-hour. One shared
  17-minute work deadline covers startup, both dynamics phases and intermediate
  checks. The remainder accommodates cleanup/evidence; no automatic retry.
- Stop at 1.5 GiB recorded storage; declared cap 2 GiB, require 4 GiB free/quota
  headroom at execution. Existing safe MPS termination and cleanup guards apply.

A four-state TPR cannot represent this full ladder. PREPARE generates 20 new TPRs
with CPU-only grompp inside the same SIF, validates their complete lambda arrays,
state indices, atom counts and duration, and seals the input hashes. It never
uses `-maxwarn`. This is necessary input preparation, not repetition of the
completed four-rank qualification or a container build.

## Required evidence

Require all 20 states' finite DHDL/energy data, all 20 GPU task mappings, consistent
exchange histories and walker permutations, and at least one accepted exchange
across **each of the 19 neighbor links**. The weak toy perturbation makes link
coverage an appropriate technical check; this is not a protein acceptance target.
Expected first-phase rounds: steps 100–900 (nine); combined: 100–1900 (19).
The step-1000 exchange must appear exactly once on continuation. The final step
2000 is not an exchange step. Require accepted exchanges after the boundary.

All 20 checkpoints must advance 1000/1.0 ps/part 1 → 2000/2.0 ps/part 2 with the
correct state indices. Every checkpoint/TPR is hash checked before continuation;
all first-part outputs are archived read-only. Earlier DHDL/energy rows must be
preserved; times 0–2.0 ps at 0.1 ps intervals and the 1.0 ps boundary must occur
exactly once. Require both sets of 20 MPS clients, successful daemon cleanup,
unchanged archive hashes, and subsequent qacct `failed 0`/`exit_status 0`.

This qualifies the complete synthetic ladder on one GPU. It does not establish
protein stability, convergence, sampling efficiency, round trips, arbitrary-crash
recovery or multi-GPU scaling. The original four-GPU Stage B remains a separate
layout, and the historical scientific gate remains closed.

Technical references: [GROMACS 2025.3 mdrun](https://manual.gromacs.org/2025.3/onlinehelp/gmx-mdrun.html),
[checkpoint append](https://manual.gromacs.org/2025.3/user-guide/managing-simulations.html),
[version-pinned exchange loop](https://github.com/gromacs/gromacs/blob/v2025.3/src/gromacs/mdrun/md.cpp),
[NVIDIA MPS](https://docs.nvidia.com/deploy/mps/when-to-use-mps.html).
The installed driver’s 20-client behavior is what this job tests; four-client
success alone is not proof that the larger launch works.

## Transfer and prepare

On the laptop:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/gmx-gpu-ladder-20260928-v2-omp16 \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

On SCC, in the login shell (outside the container and outside a GPU allocation):

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-ladder-20260928-v2-omp16 &&
bash VALIDATE_QUEUE_ON_SCC.sh &&
bash PREPARE_ON_SCC.sh &&
bash REVIEW_ON_SCC.sh
```

The first script runs **validation only** (`qsub -w v`); it cannot submit. This
checks the 16-slot request before input generation. Suitable queues do not
promise immediate placement. If any command fails, keep the log and stop;
do not change resources or remove preparation guards to retry. Return the
preparation/review output. No job has been submitted by these commands.

## Submission and review

The concrete job is `stage_L.sge`. Once prepared inputs are reviewed, the
user-operated `bash SUBMIT_ON_SCC.sh` verifies inputs again, validates resources,
creates the `submission-L` guard, and submits once. It does not cancel any job.
No old A/R job should be repeated or replaced. Preserve the returned job ID.

```bash
qstat -u bodeb
tail -n 80 -F submission-L/job.log
```

The job log appears when the job starts. Ctrl-C exits tail, not the job. After
completion, retain `attempt/status.json`, `attempt/ladder-review.json`,
`attempt/restart-review.json`, `attempt/permutations.json`, `attempt/cpu-affinity.json`, both MPI logs,
`attempt/before-restart`, all output hashes and `qacct -j JOB_ID`. Runtime
`pass_pending_review_and_accounting` is provisional until that evidence is
reviewed. Wrapper elapsed GPU-hours are not billed service units.
