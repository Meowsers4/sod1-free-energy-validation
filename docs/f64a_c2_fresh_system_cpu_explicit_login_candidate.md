# F64A r3 CPU system build: explicit-login correction candidate

Status 2026-10-12: **inactive; user-run SCC static review passed.** The [first login-shell candidate](f64a_c2_fresh_system_cpu_login_candidate.md) passed static review and submitted no job. Its batch file has `#!/bin/bash -l`, but its SGE request also specifies `-S /bin/bash`. [Grid Engine's configuration reference](https://gridscheduler.sourceforge.net/htmlman/htmlman5/sge_conf.html) says some shell startup modes feed the job script to the `-S` interpreter and ignore interpreter lines; SCC's exact compute-node setting is unverified. [BU's batch examples](https://www.bu.edu/tech/support/research/system-usage/running-jobs/batch-script-examples/) use the login Bash shebang. To remove the SGE interpretation ambiguity, the new wrapper explicitly executes `/bin/bash -l` on a separate sealed body script and checks `login_shell` before environment setup.

The [new candidate package](../packages/f64a-c2-fresh-system-cpu-explicit-login-candidate-20261012-v2) is sealed with 18 manifest entries; `SHA256SUMS` SHA-256 is `6f9d041ff165d2a6169442f4e0dde9b3f8766ca5e7eb0b4c9c97c6891c7ff9cd`. It archives manifests from the source candidate, inactive release, failed selected package and first login candidate. The scientific source, F64A folded r3 seed `2072077476`, builder, no-GPU scope, eight slots and one-hour limit are unchanged. Both execution and production authorization remain false. No new job is submitted by the static review.

Local checks: all 18 package hashes matched, `REVIEW_PACKAGE.sh` passed, shell syntax passed, and a focused test confirmed that the package rejects submission and detects body-script tampering. The explicit login process has **not** run on an SCC compute node; passing static review cannot establish that `MODULEPATH`, conda or GROMACS work there.

## User-run SCC static review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-explicit-login-candidate-20261012-v2 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-explicit-login-candidate-20261012-v2
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 6f9d041ff165d2a6169442f4e0dde9b3f8766ca5e7eb0b4c9c97c6891c7ff9cd | sha256sum -c - || exit
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 38 review.log
```

Expected final marker: `C2_R3_CPU_SYSTEM_EXPLICIT_LOGIN_CANDIDATE_REVIEW_PASS execution_authorized=False; no job submitted`. Preserve both prior packages, job 8032575's log/accounting, and this candidate's `review.log`. Do not run `SUBMIT_ON_SCC.sh`: its guard rejects the inactive candidate. A new scheduled attempt requires a separate selection and new sealed package.

## User-run SCC result

The user supplied the expected final marker. The same pasted output reports the pinned config/WT hashes, r3 ion seed `2072077476`, pmx force-field root, host GROMACS path, and `historical_output_tree_unchanged=true`. `/project/rise-batteries` used 24.75/50 GB and 214,930 files; `/project` had 31 GB free. SGE reported a suitable queue. The excerpt did not include the standalone `SHA256SUMS: OK` or `review_exit=0` lines, so their exact values are not independently recorded here. The final marker shows that the review script reached its end after the internal package check. No job was submitted. A compute-node run and its accounting are still required to establish whether the corrected startup works.
