# F64A C2 live branch fixture: inactive execution release candidate

Status: **SCC static review passed; fixture unselected, 2026-10-03**. The user
supplied the inactive runtime v2 SCC review pass marker, following the
accepted CPU rehearsal and no-job resource preflight. No common checkpoint,
branch TPR or live fixture GPU job has been made. The agent has not accessed
SCC.

The [17-entry release package](../packages/f64a-c2-branch-fixture-execution-release-candidate-20261003-v1)
has `SHA256SUMS` SHA-256
`951d9f722fe693935fb3c7d2788bc4d503125e3dae6746551d854dbf5896268f`.
It archives the [reviewed inactive runtime v2](f64a_c2_branch_fixture_runtime_candidate.md)
manifest, contract and runtime, and verifies the unchanged helper files
against that source. It adds `fixture.sge`, `SUBMIT_ON_SCC.sh`, and a permit
gate. Its sealed contract still has `execution_authorized=false` and no
selection record. Calling `runtime.py permit` fails before creating an
attempt or submission directory, touching the GPU, or calling `qsub`.
**Do not run `SUBMIT_ON_SCC.sh` from this inactive package.**

## Exact candidate ceiling

| Item | Limit |
| --- | --- |
| Allocation | One `l40s` L40S GPU, `omp16`/16 slots, 20 one-thread MPI ranks, one host |
| Attempt | One job, no reschedule or automatic retry |
| Time | `h_rt=00:30:00`; 26-minute work deadline |
| Allocated time ceiling | 0.5 GPU-hours; 8 requested CPU-slot-hours |
| Storage | `/project` persistent output and private `/scratch`; 1.5 GiB stop and 2 GiB cap at each, with at least 3 GiB filesystem free |
| SU | Current balance and actual SCC SU rate unknown; the earlier scout waiver does not apply |

The 2026-10-02 preflight measured about 26.04 GB of `/project` quota
headroom and 33.33 GB filesystem free; job start rechecks quota and free
space. The known 0.5 GPU-hour and 8 slot-hour ceilings are allocation
bounds, **not** a verified SU charge. A later explicit fixture selection
must either verify the current SU balance or specifically accept the
unknown balance for this one bounded attempt. It would require a fresh,
separately sealed release path and SCC review before submission. It would
not authorize production or change the stopped 15-ns F64A campaign.

## Local review

Local manifest verification and shell syntax checks pass. The inactive
`permit` path rejects before side effects; a simulated external-evidence
review exercises package provenance, the exact scheduler request and the
resource guard. A partial-attempt test checks stored-byte totals by phase
and extension. The CPU branch checker and private-MPS tests also pass:
22 targeted tests total. Exact-r6 dynamics and actual scheduler execution
remain untested for this live branch fixture.

## User-run SCC static review

From a local Mac terminal in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-branch-fixture-execution-release-candidate-20261003-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from your SCC terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-execution-release-candidate-20261003-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 28 review.log
```

Expected manifest digest:
`951d9f722fe693935fb3c7d2788bc4d503125e3dae6746551d854dbf5896268f`.
Expected final marker:
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20 execution_authorized=False; no job submitted`.
The review reads the accepted preflight/source and rechecks the exact r6
image; it does not request a GPU or call `qsub`. Preserve this package and
its log. Do not rerun the accepted preflight or v2 runtime review.

## SCC static review result

The user ran the package and SCC reviews on `scc-i01`. The supplied tail
reported `review_exit=0`, all 20 registered initial TPR SHA-256 values,
all shown package entries `OK`, and
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`. Accept the static
source/image/package review; preserve the candidate and `review.log`.
The standalone `sha256sum SHA256SUMS` line was not in the pasted excerpt,
so the remote digest is not independently reported here. The review's
manifest entry check succeeded. This evidence does not show runtime GPU
behavior, an SU balance, or a selected technical fixture.

The concrete [selection decision](f64a_c2_branch_fixture_selection.md)
is now the next gate. The earlier unknown-balance decision covered the
completed paired scouts only.
