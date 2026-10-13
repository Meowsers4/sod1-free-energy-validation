# F64A C2 r3 CPU system build: inactive execution release

Status 2026-10-11: **user-run SCC static review passed.** The [13-file release candidate](../packages/f64a-c2-fresh-system-cpu-execution-release-candidate-20261011-v1) has `SHA256SUMS` SHA-256 `015b32ea7a038ac069dfd36557da7795d7f65d0677bcc2fcbd6bdc941974451d`, matched by the user on `scc-i01`. Its embedded `candidate-SHA256SUMS` pins the earlier [SCC-reviewed source candidate](f64a_c2_fresh_system_cpu_candidate.md). The release still has `execution_authorized=false` and `production_authorized=false`. Its submit guard fails before creating a submission directory or calling `qsub`.

The proposed technical rehearsal would construct **only** folded F64A r3 from the pinned prepared WT, historical config and panel. The builder would write to its own `/project` package directory; it must leave `/projectnb/.../rise-project/results` untouched. It requires seed `2072077476`, reduced cysteines, no Cu/Zn, 38,414 atoms, 41 NA, 36 CL, distinct ion coordinates from r0–r2, saved output from every external command, and a final file manifest. Lambda-state starts, retained FEP dynamics, GPU allocation and production are outside this step.

The scheduler draft requests one **CPU-only** `omp` eight-slot job with `h_rt=01:00:00`, `-r n`, and no GPU resource. The allocation ceiling is eight CPU-slot-hours, with no automatic retry. Billed SU is not inferred from the slot-hours. A selected release would be a separate sealed package after an explicit one-job decision.

## SCC static review result

The user supplied the matching manifest SHA-256, `REVIEW_PACKAGE.sh` success, and `review_exit=0`. The saved output repeated the pinned config and prepared WT hashes, seed `2072077476`, pmx force-field root, host GROMACS binary, and `historical_output_tree_unchanged=true`. The scheduler returned `verification: found suitable queue(s)` for the CPU request. `/project/rise-batteries` quota was 24.75 of 50 GB used with 214,873 of 1,638,400 files; the `/project` filesystem reported 31 GB available. The final marker was `C2_R3_CPU_SYSTEM_RELEASE_REVIEW_PASS execution_authorized=False; no job submitted`. These are user-supplied SCC results; the agent did not access SCC. Preserve the package and `review.log`; no static-review rerun is needed.

The next decision is whether to select **one** isolated technical CPU build within these bounds. Selection would create a new sealed, execution-enabled package for user-run review and submission. It would not authorize lambda-state starts, C2 production, a GPU job, or a second attempt.

## User-run static SCC review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-execution-release-candidate-20261011-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-execution-release-candidate-20261011-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 35 review.log
```

Expected manifest digest: `015b32ea7a038ac069dfd36557da7795d7f65d0677bcc2fcbd6bdc941974451d`. The review checks source identity again, reports project quota and filesystem space, and asks SGE to **validate only** the eight-slot request with `qsub -w v`. It does not submit a job. The final marker is `C2_R3_CPU_SYSTEM_RELEASE_REVIEW_PASS execution_authorized=False; no job submitted`. Preserve the complete `review.log` and paste the digest, exit status and log tail. Do not run `SUBMIT_ON_SCC.sh` from this inactive package.

Local checks passed: sealed package review, inactive permit rejection, provenance-tamper rejection, shell syntax, and seven focused tests across the source and release packages. The actual build remains untested. The agent did not access SCC.
