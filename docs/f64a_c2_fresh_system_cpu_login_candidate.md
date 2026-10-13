# F64A r3 CPU system build: inactive login-shell correction

Status 2026-10-12: the [failed job 8032575](f64a_c2_fresh_system_cpu_8032575_failure.md) stopped before system construction because its batch shell lacked `MODULEPATH`, module and conda loads failed, and the fallback Python was too old to parse the builder. The original selected package and submission guard are preserved. The [fresh correction candidate](../packages/f64a-c2-fresh-system-cpu-login-candidate-20261012-v1) is **inactive**: `execution_authorized=false` and `production_authorized=false`. Its user-run SCC static review passed; no corrected batch job has run.

Its 16-file `SHA256SUMS` has SHA-256 `1c926cf2349aeb43602c3e39a93453b7c38324a487dbd6fe652f6729065b8a28`. The package archives the source candidate, inactive release, and failed selected-package manifests, plus the user-supplied failure summary. The pinned prepared WT, historical config, source code hashes, F64A r3 seed `2072077476`, CPU request (`omp`/8, one hour), and build/audit code are unchanged.

The proposed job script now starts with `#!/bin/bash -l`, as prior working SCC scripts do. If `MODULEPATH` is still empty, it tries `/etc/profile`; if it remains empty, the script stops with an explicit error. After `scripts/scc_env.sh`, it requires the `sod1-fep` conda environment and Python 3.11+ with `pmx` and `yaml` before invoking the builder. It clears `CUDA_VISIBLE_DEVICES` and still requests no GPU. These changes target the observed startup failure but have **not** been tested inside a scheduled CPU shell. The selected package cannot be edited or rerun in place; any new scheduled attempt requires a fresh explicit selection and new sealed package.

## User-run static SCC review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-login-candidate-20261012-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-login-candidate-20261012-v1
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 1c926cf2349aeb43602c3e39a93453b7c38324a487dbd6fe652f6729065b8a28 | sha256sum -c - || exit
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 38 review.log
```

Expected final marker: `C2_R3_CPU_SYSTEM_LOGIN_CANDIDATE_REVIEW_PASS execution_authorized=False; no job submitted`. This static review rechecks source identity, quota, filesystem space and CPU queue eligibility without requesting an allocation. Preserve the original failed job evidence and the new `review.log`. Do not run `SUBMIT_ON_SCC.sh` from this inactive candidate.

Local verification: sealed package review, inactive submission guard, archived failure provenance, `bash -n` on all shell files, and nine focused fresh-system package tests. The agent did not access SCC. A passing static review would allow a **separate** choice of a bounded batch-environment probe or corrected build attempt; it would not itself prove compute-node startup.

## User-run SCC static review result

The user supplied the expected `C2_R3_CPU_SYSTEM_LOGIN_CANDIDATE_REVIEW_PASS execution_authorized=False; no job submitted` marker. The same output shows the pinned config and WT hashes, r3 ion seed `2072077476`, pmx force-field root, host GROMACS path and `historical_output_tree_unchanged=true`. `/project/rise-batteries` used 24.75 of 50 GB and 214,911 files; `/project` reported 31 GB free. SGE returned `verification: found suitable queue(s)`. The pasted excerpt does not include a standalone `review_exit` or SHA-256 check, though the final marker means the review script reached its end after its package check. No job was submitted, and the compute-node module environment remains unverified. The earlier one-attempt authorization was consumed by failed job 8032575. Any new scheduled attempt needs a fresh selection and a new sealed package; do not change this inactive candidate in place.

After this review, a source check identified a remaining startup ambiguity: SGE's `-S /bin/bash` can interpret the job script without applying its login shebang, depending on site configuration. This is a risk, **not** an observed failure of this inactive candidate. The [explicit-login v2 candidate](f64a_c2_fresh_system_cpu_explicit_login_candidate.md) instead execs `/bin/bash -l` from the wrapper. Use v2 for any future selection after its own static SCC review; preserve this v1 package and its pass log.
