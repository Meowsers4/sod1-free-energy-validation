# Stage A replacement: four MPI ranks sharing one L40S

Prepared at the user's request on 2026-09-27 after the private MPS probe passed
on scc-505. This package substitutes for the unexecuted four-GPU Stage A attempt;
it is not a second dynamics attempt. No image rebuild or toy-input change.

Resources: one L40S on one host, omp/four CPU slots, four MPI ranks, one thread
per rank, ten minutes maximum, one attempt, no rescheduling or automatic retries.
Allocation ceiling: 1/6 GPU-hour, plus the completed separate MPS probe. The
existing 1,000-step/four-state synthetic fixture, exchange every 100 steps,
output limits, quota checks, SIF pin and acceptance checks remain in force.
This qualifies a one-GPU layout only; it does not validate the original four-GPU
layout, 20-rank Stage B, restart, performance, or protein production.

`PREPARE_ON_SCC.sh` verifies and imports the exact-SIF TPRs from the previously
sealed v3-omp4 package. It compares image/fixture/state identities and input
bytes, verifies every prepared file, and records source manifest/record hashes.
It does not run grompp, allocate GPUs, submit jobs, or modify the source package.

The job resolves its sole scheduler-assigned GPU to a UUID. A private unprivileged
MPS service uses that UUID and a unique 0700 scratch pipe directory, bound into
the container at the identical path. It refuses a busy assigned device or an
existing MPS service. All four ranks select visible CUDA ordinal zero, which is
verified against the assigned UUID. During dynamics, all four rank PIDs must be
observed simultaneously in the private MPS server. A missed observation produces
an incomplete/failed result, not an inferred pass. MPS is closed before CPU
postprocessing. GPU use, nine exchange rounds, at least one accepted exchange,
consistent walker permutations, finite complete energy/DHDL output, and final
step-1000 checkpoints are checked for all four states.

The simulation work deadline is seven minutes. On timeout, storage limit, signal,
or command failure, ranks first receive SIGTERM for graceful checkpoint/exit.
If clients persist, NVIDIA's `terminate_client` cancels their GPU work before
process-group termination is allowed. A failed control operation prevents that
forced teardown and records a cleanup failure; scheduler hard termination may
still occur. Normal shutdown requires no attached clients and disappearance of
the private control PID file. This is failure containment, not qualification of
arbitrary crashes or checkpoint recovery. Retain all scratch/logs after failure.

Implementation references:
[NVIDIA MPS controls and UUID mapping](https://docs.nvidia.com/deploy/mps/appendix-tools-and-interface-reference.html),
[GROMACS 2025.3 GPU assignment](https://manual.gromacs.org/2025.3/user-guide/mdrun-performance.html).

## Transfer, prepare, replace

Laptop:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/gmx-gpu-stage-a-20260927-v4-mps \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

SCC login shell, after exiting the completed interactive probe allocation:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-stage-a-20260927-v4-mps
sha256sum -c SHA256SUMS && bash PREPARE_ON_SCC.sh && bash REVIEW_ON_SCC.sh
```

Preparation success prints `EXISTING_TPRS_IMPORTED_AND_VERIFIED`, then review
prints `PACKAGE_AND_PREPARED_INPUTS_VERIFIED`. The source v3 package must remain
at its pinned path. If anything fails, preserve the output and stop for review.

After successful preparation, the concrete replacement is:

```bash
bash REPLACE_AND_SUBMIT_ON_SCC.sh
```

This first verifies scheduler feasibility. It then requires job 7758910 to be
owned by bodeb, refer to the expected old package/script, remain `qw`, and have
no attempt directory. It holds the job, confirms `hqw` and no execution, then
deletes it and submits the sealed one-GPU package exactly once. If the old job
is running/completed/absent or otherwise changed, it stops without submitting.
It does not cancel a running job. A partial transition is retained in
`submission-A/`; do not rerun or remove this guard. Validation-only job numbers
are not submissions; the actual new job ID is written to `submission-A/qsub.log`.

Check the submitted ID with `qstat -j ID`. Once started, follow
`tail -n 60 -F submission-A/job.log`; Ctrl-C stops the tail, not the job.
After completion, return `attempt/status.json`, `attempt/mps-overlap.json`, and
the job log, then retain `qacct -j ID` when available. Successful execution is
`pass_pending_review_and_accounting`; accounting and scientific interpretation
are not inferred from a zero exit status.
