# F64A C2 live branch fixture: inactive runtime candidate

Status: **v1 and v2 SCC static review pass markers supplied, 2026-10-03**.
This is the next reversible step after the user-run
[preflight](f64a_c2_branch_fixture_preflight_package.md). No GPU attempt,
new common checkpoint or branch TPR has been made. The package's sealed
contract has `execution_authorized=false` and
`production_authorized=false`; it contains no SGE job file or submission
script. The agent has not accessed SCC.

## Accepted preflight evidence

The user ran the five-file preflight package on `scc-i01` and supplied
`preflight_exit=0`, all five manifest entries `OK`, 20 initial TPR hashes
matching the accepted Stage P source, and
`C2_BRANCH_FIXTURE_PREFLIGHT_PASS_PENDING_SELECTION`. The exact
one-L40S, `omp16`/16-slot, 30-minute `qsub -w v` request found a suitable
queue and submitted no job. `preflight.json` records the correct package
manifest SHA-256
`66ecf45d671fca74909d897ae356dec3bd515197dfbcf0851225744773e3389e`,
344 source entries, exact-r6 SIF SHA-256, 20 states and 38,414 atoms.
At 2026-10-02 02:05:39 UTC, `/project` quota had approximately
26,040,000,000 bytes remaining and filesystem free space was
33,327,939,584 bytes; its proposed output root was writable. The SU
balance remains unknown **and has not been waived for this fixture**.
This preflight is accepted as source and resource admission evidence,
subject to fresh checks at job start; it does not select execution.

## Candidate package and workflow

The original [12-file runtime candidate](../packages/f64a-c2-branch-fixture-runtime-candidate-20261001-v1)
has `SHA256SUMS` SHA-256
`fcf880535ba54aae1e0efc779fd8907b7d49ae549b81519a894afcbdb30ccd3b`.
It imports the accepted 20-state CPU branch input checker and previously
used one-GPU MPS/allocation/trajectory helpers. A direct `runtime.py job` or `probe` returns
`live GPU fixture not selected by this package` before creating an
attempt directory or touching the GPU.

The user ran `REVIEW_ON_SCC.sh` for v1 and supplied all 20 matching initial
TPR hashes and
`C2_BRANCH_FIXTURE_RUNTIME_CANDIDATE_REVIEW_PASS states=20 execution_authorized=False; no job submitted`.
Accept that static source/image/package review. It did not run dynamics.
Independent local code review then found that v1 copied older helper modules
with callable job/preparation routines outside the new fixture guard. The
normal v1 commands were inactive, but this was unnecessary executable code.
Preserve the reviewed v1 unchanged.

The revised [inactive v2 package](../packages/f64a-c2-branch-fixture-runtime-candidate-20261003-v2)
has `SHA256SUMS` SHA-256
`27e712a4dfc1e43d8e1d1eb3a8544224d86be95b4e758a33a27f327eb5de92d3`.
Its `core_runtime.py` and `smoke_runtime.py` contain only helpers used by
this fixture, including the retained storage and private `/tmp` guards.
The contract still has `execution_authorized=false` and no selection
record, job script or submission script. Local manifest verification,
inactive entry-point rejection before an attempt directory, storage-limit
exercise, and 19 targeted checker/MPS tests pass. The user subsequently
supplied the SCC tail with the registered initial TPR hashes through state 19
and `C2_BRANCH_FIXTURE_RUNTIME_CANDIDATE_REVIEW_PASS states=20
execution_authorized=False; no job submitted` for v2. This is evidence that
the runtime review completed. The separate manifest-hash and shell-exit lines
were not included in the pasted excerpt and are requested for exact transfer
provenance. No GPU attempt occurred.

In a future **separately selected release**, one job would do the following
in order, stopping and retaining evidence on any failure:

1. Reverify the original 344-file source, SIF, TPR hashes, scheduler
   allocation, quota, filesystem space, CPU affinity and private MPS.
2. Run 20 states without exchange from the initial TPRs to step 1,100;
   verify output and checkpoint identity, then seal the common tree.
3. Copy all 20 checkpoints into isolated arm input trees and build 40
   changed-MDP TPRs with exact-r6 `grompp -t`. Run the CPU branch input
   checker before either arm starts.
4. Run baseline without exchange to absolute step 3,100, then HREX with
   500-step exchange to step 2,600. Each phase has its own private MPS
   service and isolated output tree. Preserve copies of arm input
   checkpoints with distinct checkpoint output names and `-noappend`.
5. Check finite complete energy/DHDL grids, XTC decode, checkpoint
   step/time/part/state, GPU logs, MPS client overlap and cleanup, no
   common/baseline exchange, three HREX rounds and all neighboring
   attempts. Rehash common and branch inputs after both arms. Record
   status and output hashes. Review `qacct` separately before acceptance.

The technical step counts are the
[bounded fixture candidate](f64a_c2_branch_fixture_design.md), not a
production sampling choice or equal-cost comparison. A runtime pass would
qualify fan-out mechanics only.

## Completed user-run SCC review commands

From a **local Mac terminal** at the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-branch-fixture-runtime-candidate-20261003-v2 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from **your SCC terminal**:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-runtime-candidate-20261003-v2
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 28 review.log
```

Expected `SHA256SUMS` SHA-256 is
`27e712a4dfc1e43d8e1d1eb3a8544224d86be95b4e758a33a27f327eb5de92d3`.
The v2 review pass marker has been supplied. The commands are retained here
for provenance; do not repeat the review merely to obtain the omitted
manifest-hash or exit-status lines. Do not
run `runtime.py job`; this candidate deliberately rejects it. Return the
manifest SHA-256 and review exit status from the existing terminal output if
available. Passing SCC review establishes static source/image/package
compatibility only. Before a
job could be selected, the executable release and its validator still
need independent review, including the actual cost/SU decision. The
accepted v1 source preflight need not be rerun; v2 review reads its record.

For v1, local checks passed: Python compilation, 12-file package manifest
verification, authorization-guard rejection before side effects,
common/HREX argument construction, post-branch exchange timing and
neighbor coverage, continuation MDP changes, XVG grid rejection of a
missing record, and `git diff --check`. No exact-r6 branch run was
available locally; runtime output naming and dynamics remain unproven.
