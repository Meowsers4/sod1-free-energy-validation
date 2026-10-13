# F64A C2 live branch fixture: non-submitting SCC preflight

Status: **SCC preflight accepted on user-supplied evidence, 2026-10-01**.
The [live fan-out fixture](f64a_c2_branch_fixture_design.md) remains a
design candidate. This package performs CPU-only source, image, queue and
storage checks. It has no `mdrun`, MPI launch, GPU passthrough, job script
or submission entry point. It cannot create the new common checkpoints or
the 40 arm TPRs; those require a separately reviewed runtime release.
The agent has not accessed SCC.

The user supplied a fresh SCC snapshot: `/project/rise-batteries` uses
**23.96/50 GB**, with 206,368 files, and `/projectnb/rise-batteries`
uses **46.32/50 GB**. `df` reported 32G free on `/project` and 8.7G
on `/projectnb`; `/project/rise-batteries` was writable. This supports
placing new persistent outputs under `/project`, subject to another
check at runtime. It says nothing about current SU balance or exact
30-minute queue eligibility.

The [five-file package](../packages/f64a-c2-branch-fixture-preflight-20261001-v1)
has a `SHA256SUMS` SHA-256 of
`66ecf45d671fca74909d897ae356dec3bd515197dfbcf0851225744773e3389e`.
It verifies all 344 files in the accepted Stage P **initial prepared**
manifest, the `PREPARED.json` identity, 20 per-state TPR hashes,
2,000-step/2-fs state MDPs, lambda values, atom labels/order, and the
exact-r6 image hash. It does not read Stage P terminal exchange
checkpoints. A temporary inert script is passed to `qsub -w v` with
the candidate one-L40S, `omp16`/16-slot, 30-minute request. Validation
mode does not submit a job. Finally it checks `/project` quota, free
space and write access. On success, it writes `preflight.json` with
`execution_authorized=false` and status
`preflight_pass_pending_fixture_selection`.

## User-run transfer and preflight

From a **local Mac terminal** in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-branch-fixture-preflight-20261001-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then, from **your SCC terminal**:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-preflight-20261001-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash PREFLIGHT_ON_SCC.sh > preflight.log 2>&1
preflight_rc=$?
printf 'preflight_exit=%s\n' "$preflight_rc"
tail -n 30 preflight.log
if [ "$preflight_rc" -eq 0 ]; then
  cat preflight.json
fi
```

If `preflight_exit` is nonzero, preserve the package and complete log;
do not rerun into a partial `preflight.json`. Return the package manifest
SHA, exit status, log tail, and JSON if present. Passing this preflight
does not select a GPU attempt or waive unknown SU balance. The guarded
[runtime candidate](f64a_c2_branch_fixture_runtime_candidate.md) is now
locally prepared for a separate static SCC review; a one-attempt
selection remains later.

The user-run result was `preflight_exit=0`. All five package files checked
`OK`, all 20 initial TPR hashes matched the accepted Stage P record,
the exact queue request was eligible, and the final marker was
`C2_BRANCH_FIXTURE_PREFLIGHT_PASS_PENDING_SELECTION`. `preflight.json`
reports 26,040,000,000 bytes of estimated project quota remaining,
33,327,939,584 bytes of filesystem free space, and a writable output
root. The SU balance remains unknown and unwaived. Preserve the result;
no rerun is needed. The next package is the
[inactive runtime candidate](f64a_c2_branch_fixture_runtime_candidate.md).

Local checks: package self-review, Python compilation, quota parser
against the user's snapshot and low-headroom case, tampered-manifest
rejection, and `git diff --check` passed. No SCC command was run locally.
