# F64A r3 CPU system build: explicit-login selected attempt

Status 2026-10-13: **job 8059683 stopped at ion-preparation `grompp`; no completed r3 system.** After the inactive [explicit-login v2 candidate](f64a_c2_fresh_system_cpu_explicit_login_candidate.md) passed user-run SCC static review, the user directed preparation of one fresh selected attempt. The previous job 8032575 and its one-attempt guard remain untouched. The agent has not accessed SCC. See the [failure record](f64a_c2_fresh_system_cpu_8059683_warning_failure.md).

The [selected package](../packages/f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1) has 20 sealed files. Its `SHA256SUMS` SHA-256 is `364ba3704c2c9067fb9d1ad633d51a9415ae7d03388bb10fe765392796196a07`. It archives the source candidate, inactive release, failed selected, first login correction and reviewed explicit-login candidate manifests. `selection.json` pins F64A folded repeat r3, one job, eight CPU slots, one-hour wall limit, no GPU, no automatic retry and no production authority. The WT/config hashes, ion seed `2072077476`, scientific builder and isolated `/project` output destination are unchanged.

The SGE wrapper explicitly execs `/bin/bash -l` on a separate sealed body. The body records `batch_login_shell=yes` and `batch_modulepath_present=yes` if those checks pass, then requires `sod1-fep`, Python 3.11+, `pmx` and `yaml` before invoking the builder. These are startup checks, not evidence that the job has yet run successfully. The builder requires `JOB_ID` and eight allocated slots, rechecks the pinned source and refuses an existing output tree.

Local verification: all 20 manifest entries matched; `REVIEW_PACKAGE.sh` and shell syntax passed; four focused candidate/selected tests passed. The selected package's `SUBMIT_ON_SCC.sh` requires a review log containing the selected-package marker, creates a `submission` directory before `qsub`, and rejects a second attempt. No SCC command was run by the agent.

## User-run transfer and static review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-explicit-login-selected-20261012-v1
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 364ba3704c2c9067fb9d1ad633d51a9415ae7d03388bb10fe765392796196a07 | sha256sum -c - || exit
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 38 review.log
```

Expected final marker: `C2_R3_CPU_SYSTEM_EXPLICIT_LOGIN_SELECTED_REVIEW_PASS execution_authorized=True; no job submitted`. This review verifies package/source identity, storage and a suitable CPU queue without allocating compute. Retain the full `review.log`. Once the exact manifest check returns `SHA256SUMS: OK`, `review_exit=0`, and the expected final marker appears, the already selected one-attempt guard may be run once from this new package:

```bash
bash SUBMIT_ON_SCC.sh
```

This command validates queue eligibility again and submits one CPU job. Retain the returned job ID. Do not call `qsub` directly or submit the old packages. If the scheduled job fails, retain its log/accounting and stop. A finished system requires `REVIEW_PREPARED.sh` and successful scheduler accounting before technical acceptance; no FEP windows or production work follow automatically.

## User-run selected static-review result

The user supplied `review_exit=0` and the expected selected-package final marker. The review reported the pinned config/WT hashes, r3 seed `2072077476`, pmx force-field root, host GROMACS path, and `historical_output_tree_unchanged=true`. `/project/rise-batteries` used 24.75/50 GB and 215,053 files; `/project` reported 31 GB available. SGE found a suitable queue. The pasted excerpt omitted the standalone `SHA256SUMS: OK` line; the final marker shows that the review script completed its internal package check. The subsequent submission excerpt also omitted the separate exact-check output. The login-shell repair remains untested on a compute node.

## User-run submission

The user ran the selected package's `SUBMIT_ON_SCC.sh` once. It printed `cpu_system_one_job_submission_guard_pass`, SGE reported a suitable queue, and `qsub` returned **8059683**. The later job log confirms login Bash, `MODULEPATH`, and Python 3.11.15, then shows a wrapper exception on a warning from ion-preparation `grompp`. `prepared.incomplete/` exists; `prepared/` does not. `qacct` reports `failed 0`, `exit_status 1`, 8 slots and 77 seconds wallclock. The warning's exact contents remain to be reviewed from the saved command JSON. Preserve `submission/`, `prepared.incomplete/`, and accounting. Do not resubmit this package or launch another r3 build.
