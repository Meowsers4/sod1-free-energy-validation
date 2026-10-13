# Stage L v3: use SCC's actual omp16 PE

Job 7763245 from v2 failed at the allocation guard: it requested `omp 16`, but
SCC's job report names the effective parallel environment `omp16`, range 16.
The runtime required the literal name `omp`. This was a wrapper contract mismatch.
The trace places the failure before CPU-affinity setup, MPS startup, or MPI/GPU
dynamics. Runtime elapsed was 2.548319 seconds; allocation accounting is pending.
The failed allocation counts as the v2 attempt even though dynamics never started.
Preserve its package, attempt/status.json, allocation.json, PE_HOSTFILE, logs and
qacct. Never delete its attempt/submission guards or rerun it.

V3 requests **`-pe omp16 16`** explicitly in validation and submission and requires
`PE=omp16`, `NSLOTS=16`, and exactly one local host totaling 16 slots at runtime.
It does not accept arbitrary PE names or remove allocation checks. All other
resources and dynamics remain unchanged: one L40S, 20 MPI ranks, 20 states,
private MPS, shared 16-ID CPU mask verified by each rank, explicit oversubscription
with localhost:16 and MPI idle yielding, normal stop at 1000 then append to 2000,
20-minute maximum, 17-minute work deadline, storage guards and one attempt.
This is a fresh candidate; it does not automatically retry the failed job.

All 20 existing TPRs are imported from the sealed v2 package. Import verifies
source package SHA-256 `f49e471b32d222986145fb4665edaa44b464ca3aaad80c97b89b369ee5ccfb07`,
the source PREPARED.json and its files, exact SIF hash, full fixture/state vector
and input-byte equality, and records ancestry. It copies only the prepared inputs,
not the failed attempt directory. No grompp, image rebuild or GPU work is needed.

## Acceptance

Keep the v2 criteria: all 20 ranks must share the assigned GPU through MPS in both
launches; all 20 checkpoint transitions must be 1000/1.0 ps/part 1 to
2000/2.0 ps/part 2 with correct state indices. Require nine first-phase exchange
rounds and 19 combined rounds, step 1000 exactly once, consistent permutations,
at least one accepted swap over each of 19 neighbor links and accepted swaps
post-restart. All foreign-lambda energy labels and finite output times must match.
Require sealed unchanged first-phase archives/TPRs, preserved earlier DHDL/energy
rows and a unique restart boundary, rank CPU masks, MPS cleanup and qacct review.
This demonstrates synthetic technical operation only, not performance or protein
sampling validity. Production remains unauthorized.

## Transfer, import and review

On the laptop:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/gmx-gpu-ladder-20260928-v3-pe-omp16 \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

On SCC, in the login shell outside an allocation/container:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-ladder-20260928-v3-pe-omp16 &&
bash VALIDATE_QUEUE_ON_SCC.sh &&
bash PREPARE_ON_SCC.sh &&
bash REVIEW_ON_SCC.sh
```

This validates the explicit omp16 request, imports the verified TPRs and checks
the new package. Nothing is submitted. Return the final output; preserve any
failure without clearing guards. Also collect the failed job's accounting:

```bash
qacct -j 7763245
```

After input review and selection of this new bounded attempt, the packaged
`bash SUBMIT_ON_SCC.sh` rechecks everything and submits once using a new
submission-L guard. No old job is deleted or resubmitted. Retain the returned
new job ID and use `tail -n 80 -F submission-L/job.log` to monitor. Preserve
status.json, ladder-review.json, restart-review.json, permutations.json,
cpu-affinity.json, both MPS overlap records, all archived first-phase files,
output hashes and qacct for the new job. A runtime technical pass remains
pending evidence/accounting review.
