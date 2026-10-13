# F64A C2 r3 CPU system build: selected technical release

Status 2026-10-12: **job 8032575 failed before system construction; environment cause identified.** The user selected one isolated CPU-only technical system build after the [inactive release](f64a_c2_fresh_system_cpu_release_candidate.md) passed SCC static review. The [selected package](../packages/f64a-c2-fresh-system-cpu-execution-selected-20261011-v1) is sealed locally; its `SHA256SUMS` SHA-256 is `2df16c4e9930a89a2a141438386677bae225c13041891c4a0765c63c85d17a2c`. It includes the reviewed candidate and inactive-release manifests and a sealed `selection.json`.

The selected scope is folded F64A repeat r3, using the pinned prepared WT and ion seed `2072077476`. One CPU job may request `omp`/8 slots for at most one hour, or **eight allocated CPU-slot-hours**. It requests no GPU, rescheduling or automatic retry. It writes only beneath this new package on `/project`. A failed or partial attempt is retained for diagnosis; the same package refuses a second submission. No lambda-aware state starts, FEP window dynamics, C2 production, or new GPU work is authorized.

The builder checks source, force field, older ion placements and chemistry again at job start. It records each external command's full combined output and exit status, requires a reduced 38,414-atom apo system with 41 NA and 36 CL, and seals the completed tree. These build checks have not been exercised on SCC for r3.

## Selected SCC static review result

The user supplied `REVIEW_PACKAGE.sh` success, `review_exit=0`, the expected config/WT hashes and seed `2072077476`, the pmx force-field root and host GROMACS binary, and `historical_output_tree_unchanged=true`. `/project/rise-batteries` used 24.75 of 50 GB and 214,889 of 1,638,400 files; the `/project` filesystem reported 31 GB available. SGE returned `verification: found suitable queue(s)` and the final marker was `C2_R3_CPU_SYSTEM_RELEASE_REVIEW_PASS execution_authorized=True; no job submitted`. The standalone `sha256sum SHA256SUMS` line was omitted from the pasted review output, but the user subsequently checked the exact expected manifest digest with `sha256sum -c -` and reported `SHA256SUMS: OK`. The package's internal manifest check also passed. Preserve `review.log`; no static-review rerun is needed.

## User-run transfer and static review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-execution-selected-20261011-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-execution-selected-20261011-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 35 review.log
```

Expected manifest digest: `2df16c4e9930a89a2a141438386677bae225c13041891c4a0765c63c85d17a2c`. Expected final marker: `C2_R3_CPU_SYSTEM_RELEASE_REVIEW_PASS execution_authorized=True; no job submitted`. The static review checks the exact package, source identity, quota, free space, and queue eligibility with `qsub -w v`; it does not submit. Paste the checksum, exit status and log tail for review. Preserve `review.log`, because the submission guard requires its passing marker.

The user ran `SUBMIT_ON_SCC.sh` once. It printed `cpu_system_one_job_submission_guard_pass`, verified a suitable queue again, returned **job ID 8032575**, and reported one bounded CPU system rehearsal submitted. This is evidence of accepted submission, not execution or technical success. Retain `submission/`, the job log, any incomplete tree, and eventual `qacct`. Do not call `qsub` directly or rerun the script. A separate `REVIEW_PREPARED.sh` must pass before accepting any completed system.

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-execution-selected-20261011-v1
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 2df16c4e9930a89a2a141438386677bae225c13041891c4a0765c63c85d17a2c | sha256sum -c - || exit
bash SUBMIT_ON_SCC.sh
```

The user-supplied `qacct` excerpt reports start `2026-10-12 00:16:49`, end `00:16:50`, PE `omp8`, eight slots, `failed 0`, and **`exit_status 1`**. The scheduler ran the job, but it failed before technical completion. The subsequent [failure review](f64a_c2_fresh_system_cpu_8032575_failure.md) found `MODULEPATH` unset in the non-login batch shell, failed module/conda initialization, and an old fallback Python that raised a syntax error before the builder began. Both `prepared/` and `prepared.incomplete/` were absent. Preserve the one-attempt submission guard and failed evidence; do not resubmit this package.

Local verification: sealed manifest, source/release provenance, selection record, shell syntax, a simulated passing-review permit and second-attempt rejection, plus nine focused tests across the source, inactive and selected packages. The agent did not access SCC or submit the job; remote results are user-supplied.
