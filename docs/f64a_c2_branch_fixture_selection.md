# F64A C2 live branch fixture: selected one technical attempt

The [inactive execution release](f64a_c2_branch_fixture_execution_release_candidate.md)
passed the user-run SCC static review with `review_exit=0` and
`execution_authorized=False; no job submitted`. The earlier CPU branch
rehearsal and no-job queue/storage preflight also passed. The reviewed
package remains sealed and inactive. No live common checkpoint or branch
trajectory exists yet.

## Proposed one-attempt scope

| Item | Exact bound |
| --- | --- |
| Purpose | Technical qualification of a new shared no-exchange common preparation and two isolated continuations; no free-energy estimate |
| Inputs | Accepted 344-entry Stage P **initial-input** tree and exact-r6 image; no Stage P terminal checkpoints |
| Schedule | Common to step 1,100; copy/seal 20 checkpoints; preprocess/check 40 arm TPRs; baseline to step 3,100 without exchange; HREX to step 2,600 with expected exchange at 1,500/2,000/2,500 |
| Allocation | One `l40s` L40S GPU, `omp16`/16 slots, 20 one-thread ranks, one host; phases sequential in one job |
| Attempt ceiling | One 30-minute allocation, no reschedule or automatic retry; at most 0.5 allocated GPU-hours and 8 requested CPU-slot-hours |
| Storage | `/project` outputs and private `/scratch`; 1.5-GiB stop, 2-GiB cap and 3-GiB free-space floor at each location |
| Stop/acceptance | Stop and retain evidence on any failed checkpoint, branch input, output, MPS, storage or accounting check; review `qacct` after completion |

The preflight recorded about 26.04 GB of `/project` quota headroom and
33.33 GB filesystem free on 2026-10-02. The selected job would recheck
those resources at start. Its 30-minute limit bounds allocated time,
**not** billed SCC SUs. The current `rise-batteries` SU balance and the
actual charge rate have not been reported. The user's earlier instruction
to proceed with an unknown balance applied to the completed paired scouts;
it does not select this fixture.

**Decision status: selected, 2026-10-03 America/Chicago.** Asked whether to
select this exact one-job fixture or wait for an SU-balance check, the user
replied: **“continue. SU balance is 15k, which is more than enough.”** The
machine-readable [selection record](f64a_c2_branch_fixture_selection.json)
records 15,000 SUs as user reported. The agent has not independently checked
the balance or the SU charge rate, so no precise billed cost is claimed.
This selection is for the bounded technical fixture only. The
[new selected package](f64a_c2_branch_fixture_selected_release.md) is in
a different path, manifest sealed, and awaits static SCC review before its
one-attempt submission guard is used. The reviewed inactive package remains
unchanged. No production protocol, longer F64A sampling, retry, or further
GPU job follows from this decision.
