# Stage A one-GPU MPS result — 2026-09-27

**Reviewed outcome: Stage A passed for the synthetic four-rank/one-L40S
configuration. Scheduler completion/accounting evidence is now received.**
This acceptance is based on the user-supplied runtime, overlap, permutation and
qacct records; it is not an independent download/reanalysis of all raw outputs.

User-supplied job-log output reports a technical pass for job **7762792**,
package `gmx-gpu-stage-a-20260927-v4-mps`, manifest SHA-256
`6557fcd03adad353d60b65f6f2d1d57547d50f127c116dddd139b8f3e3421904`.

```json
{
  "technical_status": "pass_pending_review_and_accounting",
  "stage": "A",
  "production_authorized": false,
  "job_id": "7762792",
  "accounting": "pending_qacct",
  "failure": null,
  "mps_cleanup_confirmed": true,
  "mps_four_clients_observed": true,
  "wall_seconds": 8.91108157596318,
  "allocated_gpu_hours_observed": 0.0024753004377675502
}
```

Retained scratch: `/scratch/gmx-smoke-A-7762792.tpam9sla`.
SCC package root:
`/projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-stage-a-20260927-v4-mps`.

The runtime reaches this status only after verifying container/device mapping,
observing all four rank PIDs simultaneously attached to the private MPS server,
successful MPI mdrun completion, and MPS shutdown. Its result validator requires
GPU work in each state, nine exchange rounds at steps 100–900 with at least one
accepted exchange, consistent walker permutations, finite complete DHDL/energy
outputs, and final step-1000 checkpoints in all four states.

These are conclusions from the supplied status and the sealed runtime's checks;
raw SCC output files have not been independently retrieved. The subsequent
transcript supplies the job-log status, MPS overlap, permutations and qacct.
The original status above is preserved verbatim; its pending fields describe
the runtime's state before this review. Preserve prepared inputs, output hashes
and raw files on SCC.

The 8.91 seconds is runtime-wrapper elapsed time, including its checks and
postprocessing, not scheduler allocation duration or a throughput benchmark.
The GPU-hour field is that elapsed time multiplied by one GPU, not measured
GPU utilization or billed service units. The received qacct record reports
14 scheduler wall-clock seconds; it does not report billed service units.

This result is confined to the synthetic four-rank/one-L40S layout. Restart,
20-rank scaling, the original four-GPU layout, protein dynamics and scientific
sampling performance remain unqualified. No rerun or further GPU stage is
needed for this completed Stage A milestone.

## Evidence review

Source attachment: `820ba058-cbd6-4de4-9177-d7a4d00186f3/Pasted text.txt`.
Verbatim copy retained at
`docs/review/gromacs_stage_a_7762792_user_transcript.txt`, SHA-256
`328ed22c7e2b87367f313b2e18055d75d302e8370031d4cb14ef36a6d779d337`.

Independently parsed the supplied JSON and reconstructed all walker permutations:

- One MPS server, PID 649761, lists exactly the four rank PIDs
  649823, 649824, 649825 and 649826.
- Assigned shared GPU UUID: `GPU-48f8c4f9-3f7d-4979-a18d-0916a5aa435c`.
- Nine ordered exchange rounds at steps 100 through 900, with 14 accepted
  neighbor swaps. Every swap has the expected alternating parity, pairs do not
  overlap within a round, and every recorded state-to-walker permutation matches.
- qacct matches job 7762792, owner bodeb, project rise-batteries, queue l40s,
  omp/four slots, host `scc-502.scc.bu.edu`, `failed 0` and `exit_status 0`.
- Submitted 23:37:48, started 23:39:30, ended 23:39:44 on September 27 in the
  scheduler's unspecified timezone: 102 seconds queued and 14 seconds running.

The smoke job used a different GPU/node from the earlier metadata/MPS probe;
that is expected because each allocation resolves its own assigned UUID.
The earlier interactive probe connection closed before the replacement was
submitted from scc-i01. No further job submission or runtime mutation was made
as part of this review. Restart and larger-ladder qualification remain separate
next milestones; this tiny test does not establish protein sampling performance.
