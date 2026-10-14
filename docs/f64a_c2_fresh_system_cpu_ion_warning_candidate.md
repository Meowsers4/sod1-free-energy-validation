# F64A r3 CPU system build: inactive ion-warning correction

Status 2026-10-13: **inactive correction package passed user-run SCC static review; no job selected.** The spent job [8059683](f64a_c2_fresh_system_cpu_8059683_warning_failure.md) confirmed login Bash and Python 3.11, then stopped because its wrapper rejected one `grompp` warning while creating the pre-ion `ions.tpr`. The user supplied the warning: the solvated system has net charge −5 and GROMACS warns about Ewald electrostatics on a charged system. The historical source builder calls that command with `-maxwarn 2`, then `gmx genion -neutral` before minimization. [GROMACS 2025.3 documents `genion -neutral`](https://manual.gromacs.org/2025.3/onlinehelp/gmx-genion.html) as adding ions to neutralize the system, while its [`grompp` documentation](https://manual.gromacs.org/2025.3/onlinehelp/gmx-grompp.html) cautions that warnings require interpretation before using `-maxwarn`.

The [new package](../packages/f64a-c2-fresh-system-cpu-ion-warning-candidate-20261013-v1) contains 22 sealed files; `SHA256SUMS` SHA-256 is `9235ba3ac4820e417f6a60bcca2222d5b207625217607a926944a755ab081a5f`. Its only runtime policy change is a narrow exception for **one exact warning** from the exact `ions.mdp` command, with charge −5 and a one-warning summary. A nonzero `grompp` exit still fails. An extra or changed warning, another `grompp` step, or a different charge still fails. The post-ion minimization `grompp` continues to reject warnings. The system audit still requires the expected 41 NA and 36 CL ions, 38,414 atoms, reduced cysteines, no metals, distinct ion placement, complete system files and a sealed output tree.

The selected job's saved command JSON has not been copied locally or independently hashed. `REVIEW_ON_SCC.sh` therefore verifies that old selected package's pinned manifest and reads its retained `prepared.incomplete/build-logs/command-*.json`. It requires exactly one matching ion `grompp`, the exact command and warning, `returncode=0`, and prints the saved command's SHA-256. This is read-only; it does not use or modify the incomplete system as a starting point. The candidate is a fresh package whose builder would start from the pinned WT, config and seed, in its own output tree if separately selected later.

The pinned source, F64A folded r3 seed `2072077476`, explicit login-shell startup, eight-slot/one-hour CPU request, and no-GPU scope remain unchanged. `execution_authorized=false` and `production_authorized=false`. The old job/package/guard are preserved. Local package review, all 22 manifest hashes, shell syntax and focused warning-policy tests passed. No SCC access or new job occurred during preparation.

## User-run SCC static review

From the local Mac terminal:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-ion-warning-candidate-20261013-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-ion-warning-candidate-20261013-v1
cd "$PKG" || exit
printf '%s  SHA256SUMS\n' 9235ba3ac4820e417f6a60bcca2222d5b207625217607a926944a755ab081a5f | sha256sum -c - || exit
bash REVIEW_PACKAGE.sh || exit
bash REVIEW_ON_SCC.sh > review.log 2>&1
review_rc=$?
printf 'review_exit=%s\n' "$review_rc"
tail -n 70 review.log
```

The user ran this review on SCC and reported `review_exit=0`. It identified `command-07.json` from job 8059683, with SHA-256 `e1ba44209ac4b849c5e731446a99fcf51624e22819284f9b174c55eedaee5418`, `returncode=0`, pre-ion charge −5, and exactly one matching warning. The output reported 24.76/50 GB project quota use, 31 GB free on `/project`, a suitable CPU queue, and `C2_R3_CPU_SYSTEM_ION_WARNING_CANDIDATE_REVIEW_PASS execution_authorized=False; no job submitted`. These are user-supplied SCC results; the standalone outer manifest check was not pasted, although the package reviewer passed. Preserve the full review log and both spent jobs' evidence. Do **not** run this candidate's `SUBMIT_ON_SCC.sh`; its guard rejects submission. A fresh selected package and separate one-attempt decision are required for further CPU work.
