# C2 branch CPU rehearsal from archived Stage P checkpoints

Status: **CPU rehearsal accepted on user-supplied SCC preparation and
independent review, 2026-09-30**.
This is the next reversible check in the
[branch design](f64a_c2_checkpoint_branch_review.md). The agent has not
logged into SCC or used a cluster connector. This package contains no
`mdrun`, GPU passthrough, MPS, MPI launch, scheduler call, or submission
script.

The [package](../packages/f64a-c2-branch-cpu-rehearsal-20260930-v1)
has a seven-entry `SHA256SUMS` whose SHA-256 is
`f6a935f50612b920eb143be187dcb4963d5bb894705868473e284038eac79b7a`.
It
uses the accepted Stage P job **7791102** checkpoints from step 2,000,
4 ps, simulation part 2. Stage P ran exchange, so these checkpoints
test **preprocessing and input-review mechanics only**. They are not the
selected common no-exchange preparation and cannot establish its
scientific ancestry. The CPU rehearsal sets technical continuation lengths
of 1,000 baseline and 500 HREX steps solely to exercise unequal arm TPRs;
neither is a C2 duration selection.

The builder checks the 344-entry accepted Stage P source manifest, the
saved attempt checkpoint and dump hashes in `output-hashes.json`, all 20
checkpoint step/time/part/FEP labels, original atom and lambda settings,
and the exact r6 image SHA-256. It copies each checkpoint into two isolated
trees. Through CPU-only Singularity, it runs `gmx_mpi dump -cp` on a copy,
`gmx_mpi grompp -t` for both arms, and `gmx_mpi dump -s` on all 40 new
TPRs. The changed MDP keys are only `nsteps`, `init-step`, `tinit`,
`simulation-part`, `gen-vel`, and `continuation`; the underlying Stage P
physical settings remain. `gen-vel=no` and `continuation=yes` preserve
the checkpoint state in a changed-MDP restart as described by the
[GROMACS 2025.3 restart guide](https://manual.gromacs.org/documentation/2025.3/user-guide/managing-simulations.html).

The builder saves grompp logs and argument/exit records, the selected
checkpoint/TPR dump fields, hashes and byte counts of the full dump
stdout, generated MDPs, a branch plan, and a prepared-file manifest.
It invokes the [20-state input checker](f64a_c2_branch_input_checker.md)
before marking preparation complete. The independent review wrapper
rechecks the package, prepared manifest, dump provenance and checker.
Any failure leaves `prepared/` in place for inspection; the builder
refuses to reuse it. A pass does not prove that `mdrun -cpi` or post-branch
exchange works. That remains the bounded runtime fixture.

## User-run transfer and CPU check

From a **local Mac terminal** at the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-branch-cpu-rehearsal-20260930-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then, from **your SCC terminal** in a Python environment with Singularity
available:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-cpu-rehearsal-20260930-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash PREPARE_ON_SCC.sh > prepare.log 2>&1
prep_rc=$?
printf 'prepare_exit=%s\n' "$prep_rc"
tail -n 35 prepare.log
```

If `prepare_exit` is nonzero, stop and preserve the directory. If it is
zero, run:

```bash
bash REVIEW_PREPARED.sh
printf 'review_exit=%s\n' "$?"
sha256sum prepared/SHA256SUMS
```

Return the package manifest SHA-256, `prepare_exit`, final preparation
marker and log tail, `review_exit`, and prepared-manifest SHA-256. The
package should be run once; do not delete `prepared/` or rerun into it.

## Reported SCC preparation evidence

The user pasted the package review pass followed by 20 lines of distinct,
well-formed `checkpoint_sha256` values for states 0–19, then
`prepared_manifest_entries=363` and
`C2_STAGE_P_CHECKPOINT_CPU_REHEARSAL_PREPARED; no job submitted`.
The count agrees with the expected layout: 40 common checkpoint files,
280 arm files, 40 generated MDPs and three records. Reaching this marker
means the builder completed its exact-r6 `dump`/`grompp` collection and
ran its 20-state checker. The separately run `REVIEW_PREPARED.sh` returned
`review_exit=0` and
`C2_STAGE_P_CHECKPOINT_CPU_REHEARSAL_REVIEW_PASS manifest_entries=363`.
The package manifest SHA-256 was
`f6a935f50612b920eb143be187dcb4963d5bb894705868473e284038eac79b7a`,
matching the local sealed package; the prepared manifest SHA-256 was
`2ed9a0f0166bf0db6a1962a8a854a4e978f4a08d85d11abe1e1efbbb14375a04`.
Accept this **CPU preprocessing/input-checker rehearsal**. The shell's
`prepare_exit` was not separately pasted, but the builder reached its
final marker and the later independent review passed. Preserve the
363-file prepared tree and logs; do not repeat preparation. This does
not qualify a live branch or production.

Local verification: the mocked 20-state CPU collection/review passed,
along with the seven branch-checker tests and a one-time-directory guard.
The remaining technical gap is an explicitly selected bounded run that
branches one no-exchange checkpoint set into two isolated retained arms.
