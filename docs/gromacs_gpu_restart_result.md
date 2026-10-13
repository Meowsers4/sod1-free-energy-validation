# Stage R reported result — 2026-09-28

**Reviewed outcome: Stage R passed for graceful four-rank restart on one L40S.
Scheduler completion/accounting evidence has been received.** Acceptance is
based on the user-supplied runtime report, restart details, permutations and
qacct, not an independent download of the binary checkpoints/trajectories.

User-supplied job-log output for job **7763081**, package
`gmx-gpu-restart-20260927-v1` (manifest SHA-256
`195331e4357bf28347b85b4a4d735d10307fd4ea348c2d8e8bba1fba67d59a11`):

```json
{
  "technical_status": "pass_pending_review_and_accounting",
  "stage": "R",
  "production_authorized": false,
  "job_id": "7763081",
  "accounting": "pending_qacct",
  "failure": null,
  "restart_verified": true,
  "mps_cleanup_confirmed": true,
  "mps_four_clients_observed": true,
  "wall_seconds": 14.486157707986422,
  "allocated_gpu_hours_observed": 0.004023932696662895
}
```

Retained scratch: `/scratch/gmx-smoke-A-7763081.10mnahsl` (the inherited scratch
prefix does not change the reported stage R). SCC package:
`/projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-restart-20260927-v1`.

According to the sealed runtime's pass conditions, all four replicas stopped
normally at step 500 with matching time/part and correct lambda-state indices,
their checkpoints and outputs were sealed before restart, and a new MPI process
set appended to step 1,000 with part-2 checkpoints. The validator checked the
preserved archive, unchanged earlier energy/DHDL rows, unique checkpoint-time
output, nine combined exchange rounds, matching earlier permutations and an
accepted post-restart exchange. Four-client MPS overlap was required in both
phases; MPS cleanup was confirmed.

The subsequent supplied restart review, permutations and qacct have now been
checked as detailed below. The original runtime status above remains verbatim;
its pending fields predate this review. Retain all raw outputs and hashes.
The 14.49 seconds is wrapper elapsed time, and its derived GPU-hour field is
not billed SU or scheduler allocation duration. qacct reports 18 seconds of
scheduler wall time; it does not supply billed SU.

Scope remains graceful four-rank restart on one allocated L40S, with the same
private MPS service between launches. It does not qualify arbitrary crash
recovery, cross-allocation restart, larger ladders or protein performance.
No rerun is needed for this completed milestone.

## Evidence review

Source: attachment `5663d4ca-aab6-49de-9938-4a9f8af929c4/Pasted text.txt`.
Verbatim retained copy: `docs/review/gromacs_restart_7763081_user_transcript.txt`;
SHA-256 `58500cf2b1221627f235d0dcc234e6eaab14c736f233b571203e13006215f8a3`.

Independently parsed and checked the supplied records:

- All four state-indexed checkpoints advance from step 500/time 0.5 ps/part 1
  to step 1,000/time 1.0 ps/part 2, retaining the correct lambda-state indices.
- The first launch's PIDs 293424–293427 and second launch's PIDs 293937–293940
  form distinct four-process sets. Each set exactly matches its MPS client list.
  Both phases use server 293361 and GPU
  `GPU-baba41da-924a-885e-18d6-82cfaef802fd`, as planned.
- Nine ordered exchange rounds cover steps 100–900, with step 500 appearing
  exactly once. Reconstructed every permutation from 14 accepted neighbor swaps,
  including eight in the resumed phase (step 500 onward). Pair parity and
  non-overlap within each round are correct.
- The runtime review reports preserved pre-checkpoint data and unique boundary
  output. Binary/raw numerical output files have not been independently reread.
- qacct confirms job 7763081, owner bodeb, rise-batteries, l40s, omp/four slots,
  host `scc-512.scc.bu.edu`, `failed 0`, `exit_status 0`, 18 wall-clock seconds.
  Submission/start/end are 00:48:42/00:50:15/00:50:33 on September 28 in the
  scheduler's unspecified timezone: queue wait 93 seconds.

MPS cleanup is confirmed by the runtime status. This closes review of the
bounded synthetic restart attempt; larger-ladder and protein qualification
remain separate work, and no further job was submitted during review.
