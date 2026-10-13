# F64A C2 live branch fixture: selected technical release

Status: **selected package reviewed; job 7865574 completed and technical fixture accepted,
2026-10-03**. See the [accepted result](f64a_c2_branch_fixture_result.md).
The user selected exactly one bounded technical fixture and
reported a 15,000-SU balance. The agent has not independently verified that
balance or the SU charge rate. The agent has not
accessed SCC.

The [21-entry selected package](../packages/f64a-c2-branch-fixture-execution-selected-20261003-v1)
has `SHA256SUMS` SHA-256
`a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`.
It archives the SCC-reviewed [inactive execution candidate](f64a_c2_branch_fixture_execution_release_candidate.md)
manifest, README, contract and runtime, checks all 17 archived file hashes,
and preserves the reviewed runtime-v2 provenance. Its selected contract
and [decision record](f64a_c2_branch_fixture_selection.json) fix one
L40S, `omp16`/16 slots, 20 ranks, a 30-minute hard walltime, 26-minute
work deadline, one attempt, no reschedule and no production. The
allocation ceiling remains **0.5 GPU-hours and 8 requested CPU-slot-hours**.
The actual SCC SU charge remains unquantified.

The package review, shell syntax, selected guard, provenance rejection,
simulated static review and 25 focused tests passed locally. The user-run SCC
review and bounded job subsequently passed. Saved checkpoint, exchange,
seal, output and accounting summaries support technical acceptance.

## User-run SCC static review

From a local Mac terminal in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-branch-fixture-execution-selected-20261003-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from your SCC terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-execution-selected-20261003-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 28 review.log
```

Expected manifest digest:
`a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`.
Expected final marker:
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20 execution_authorized=True; no job submitted`.
The review checks the sealed package, archived candidate provenance,
accepted source/preflight and exact-r6 image. It does not submit a job.
Preserve this package and `review.log`. After the selected review is
confirmed, the existing one-attempt authorization permits the separate
`SUBMIT_ON_SCC.sh` step; retain its job ID and review saved output plus
`qacct` before any technical acceptance. Do not run the submission script
from the inactive package.

## SCC static review and execution result

The user ran `REVIEW_PACKAGE.sh` and `REVIEW_ON_SCC.sh` on `scc-i01` and
supplied `review_exit=0`, all 20 registered initial TPR SHA-256 values,
the selected-package verification marker, and
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=True; no job submitted`. Accept the selected static
review and preserve its log. The standalone remote `sha256sum SHA256SUMS`
line appeared in the later full transcript and matched the local seal.
No preflight or review rerun is needed.

The already selected one-attempt submission may now be run from **this
selected package only**, using `bash SUBMIT_ON_SCC.sh`. The script rechecks
the full permit, claims a unique submission directory, validates the exact
request with `qsub -w v`, then submits one job. Record the returned job ID.
The user ran the submission script once: it exited 0, rechecked the permit,
found a suitable queue with `qsub -w v` and returned **job 7865574**.
The user supplied saved status, phase reviews and scheduler accounting;
the [accepted result](f64a_c2_branch_fixture_result.md) records their
assessment. Do not run the submission script again or remove its guards.
