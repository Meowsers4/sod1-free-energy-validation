# F64A C2 scout execution release candidate

Prepared locally after the [queue and storage preflight](f64a_c2_scout_execution_preflight.md).
The SCC SU balance query remained unavailable. This is a **sealed, inactive
execution candidate**. It contains the actual SGE and submission scripts so
they can be reviewed, but its contract has `execution_authorized=false` and
`selected_technical_arms=[]`. The `permit`, `job`, `rank` and `probe` paths
reject before an attempt or GPU access. No job has been submitted.

The current package is
`packages/f64a-c2-scout-execution-release-candidate-20260929-v3` with 20
manifest entries and `SHA256SUMS` SHA-256
`abb0439e1f39c210edd8cd5f3c3eedd66688a433052f6027629fffef2705861e`.
It embeds the accepted v4 candidate identity
`71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df`,
rechecks its copied runtime/validator/input metadata, and does not alter the
accepted CPU tree or r6 image. A first local draft v1 was superseded before
transfer when its permit path was changed to reject an inactive contract
before attempting SCC source checks. Local v2 was superseded before transfer
to prevent Python bytecode files from appearing in the sealed package during
review and jobs. Preserve both local drafts and use v3.

The exact SGE request in both arm scripts is one `l40s` L40S, `omp16`/16
slots, `h_rt=02:00:00`, no rescheduling. Each submission wrapper rehashes the
package, reviews SCC inputs and image, checks the arm's execution permission,
then atomically creates its one-attempt submission directory, validates the
request with `qsub -w v`, and only then calls `qsub -terse`. The baseline arm
must complete technical validation and zero-failure/exit accounting before
the HREX wrapper passes its gate. There is no automatic HREX launch or retry.
The runner's 100-ps, storage, timing, MPS, output and accounting contract is
unchanged from the [reviewed guarded candidate](f64a_c2_scout_gpu_runtime_candidate.md).

Local package review, shell syntax checks and the inactive permit rejection
passed. The release-specific tests and earlier candidate tests passed (9
tests together); the wider 15-test C2 set also passed. These checks do not
establish a compute-node runtime result. An authorized release must be
regenerated in a **new path** with the user's explicit baseline/HREX technical
selection, the preflight evidence, and either a verified SU balance or a
documented user decision to accept that uncertainty. The v3 package must
never be edited in place or used to submit.

## Read-only SCC review

From a local Mac terminal in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-scout-execution-release-candidate-20260929-v3 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then in the user's `scc-i01` terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-release-candidate-20260929-v3
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh
bash REVIEW_ON_SCC.sh
```

Do not run either `SUBMIT_*` script from this inactive package. The expected
review marker is `C2_SCOUT_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`.

## SCC read-only review result — 2026-09-29

The user supplied `scc-i01` output from the v3 package. Its remote
`SHA256SUMS` SHA-256 was
`abb0439e1f39c210edd8cd5f3c3eedd66688a433052f6027629fffef2705861e`,
matching the local seal. Both `REVIEW_PACKAGE.sh` and `REVIEW_ON_SCC.sh`
verified all 20 listed files. The latter reported
`C2_SCOUT_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`. Accept this package/source
review. It is not a compute-node rehearsal or scout result. Preserve v3
unchanged; no rerun of its read-only review is needed.

The remaining gate is the [explicit scout selection](f64a_c2_scout_execution_selection.md),
including disposition of the unavailable SU balance. A fresh, separately
sealed selected release must be built after that decision.

The user subsequently selected the bounded pair with balance unknown. The
[new selected release](f64a_c2_scout_execution_selected_release.md) was built
at a different path; this inactive v3 remains immutable and must not be
submitted.
