# F64A r3 CPU system build: selected ion-warning correction

Status 2026-10-13: **one fresh CPU-only technical attempt selected; user-run SCC static review pending; no job submitted.** The user selected this after the [inactive ion-warning candidate](f64a_c2_fresh_system_cpu_ion_warning_candidate.md) passed SCC review. Jobs 8032575 and 8059683 each spent their one attempt and remain preserved. This package starts from the pinned WT/config and seed in a new isolated output tree; it never resumes `prepared.incomplete/` from job 8059683.

The [selected package](../packages/f64a-c2-fresh-system-cpu-ion-warning-selected-20261013-v1) has 25 sealed files. `SHA256SUMS` SHA-256 is `836d869a293034fa275af079cba508e261b34cd0fd255ed02b21cebc48cf8316`. It archives the reviewed inactive candidate's manifest and pins saved job 8059683 `command-07.json` to SHA-256 `e1ba44209ac4b849c5e731446a99fcf51624e22819284f9b174c55eedaee5418`. The SCC review and compute-node builder both require that exact saved command hash, successful command exit, charge −5, one exact pre-ion Ewald warning, and the old package's intact seal. Only that warning in the exact `ions.mdp` step is allowed before `genion -neutral`; other warnings or nonzero exits stop the build.

The selected scope is F64A folded r3 system preparation, eight CPU slots, one-hour wall limit, no GPU, one job, no automatic retry, and no production work. It preserves ion seed `2072077476`, explicit login Bash startup, historical source hashes, force field and GROMACS version checks, and the post-build system audit. The submission guard requires the new package's passing SCC review marker and an absent `submission/` and output tree. It creates `submission/` before queue validation and refuses a second call. The old packages and their guards are untouched.

Local verification passed: `REVIEW_PACKAGE.sh`, all 25 SHA-256 entries, shell syntax, five focused warning and selection tests, and `git diff --check`. The agent has not accessed SCC.

## User-run transfer and static review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-ion-warning-selected-20261013-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-ion-warning-selected-20261013-v1
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 836d869a293034fa275af079cba508e261b34cd0fd255ed02b21cebc48cf8316 | sha256sum -c - || exit
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 45 review.log
```

The required result is `review_exit=0` and `C2_R3_CPU_SYSTEM_ION_WARNING_SELECTED_REVIEW_PASS execution_authorized=True; no job submitted`. The review also prints the saved warning hash, source preflight, storage and queue checks. Preserve `review.log`. If any check fails, stop and retain the output.

Once the exact manifest check and SCC review pass, this selected package may submit its one bounded job with `bash SUBMIT_ON_SCC.sh`. Retain its job ID and later inspect `submission/job.log`, `prepared/` or `prepared.incomplete/`, and `qacct`. A successful build still needs `REVIEW_PREPARED.sh` plus scheduler accounting before technical acceptance. It does not authorize FEP windows, a GPU job or production inference.
