# F64A C2 bounded technical scout: selected release

The user explicitly selected the [registered bounded pair](f64a_c2_scout_execution_selection.md)
on 2026-09-29 America/Chicago by replying “proceed with balance unknown.”
This selects one 100-ps baseline technical attempt, then one 100-ps HREX
attempt only if baseline output and `qacct` review pass. The current SCC SU
balance and applicable tariff remain unknown; this uncertainty is recorded
in the sealed contract. No production or free-energy arm is selected.

The new package is
`packages/f64a-c2-scout-execution-selected-20260929-v1`, separate from the
accepted inactive v3 review package. Its 20-entry `SHA256SUMS` SHA-256 is
`a4d353e5571beaae97fbbeddb413796fa10d0a97894018e2ba9d25f0f539a587`.
`contract.json` has `execution_authorized=true`,
`selected_technical_arms=[baseline,hrex]`, and
`production_authorized=false`. Its selection record embeds the user's
decision, accepted queue/storage preflight, reviewed inactive package hash,
SU disposition, and the two-attempt resource ceilings. The accepted 381-entry
CPU tree, all 20 TPR hashes and exact r6 SIF remain the sources.

Both SGE scripts request one L40S in `l40s`, `omp16`/16 CPU slots,
`h_rt=02:00:00`, and `-r n`. Each submission wrapper verifies the package,
source and SIF, checks its arm gate, creates a one-use submission directory,
tests the exact request with `qsub -w v`, then submits with `qsub -terse`.
The HREX wrapper requires baseline technical completion, private MPS cleanup,
verified output hashes and post-job accounting with `failed=0` and
`exit_status=0`. There is no automatic HREX launch or retry. Each job
checks current quota and compute-node scratch before GPU dynamics and
enforces the registered time and storage stops.

Local manifest review and shell syntax checks passed; the selected contract
was checked for two arms, SU uncertainty and production denial. The combined
release/candidate/CPU tests passed (**19 tests**, including the later
actual-format DHDL regression). This is local evidence,
not SCC execution. The selected release has not yet been transferred,
reviewed on SCC or submitted.

## SCC review before the first submission

From a local Mac terminal in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-scout-execution-selected-20260929-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then from the user's `scc-i01` terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh
bash REVIEW_ON_SCC.sh
```

One final read-only parser check uses the already accepted Stage P state logs
and DHDL header. The selected runtime expects a GPU task marker and
performance line in each state log, plus all 20 foreign-energy legends.
Run this on `scc-i01` after the package review:

```bash
python - <<'PY'
from pathlib import Path
import re
root = Path('/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-runtime-20260928-v1/attempt')
for i in range(20):
    path = root / ('state%02d' % i) / 'smoke.log'
    log = path.read_text(errors='replace')
    print('state=%d pp0=%s gpu_task=%s performance=%s finished=%s' % (
        i,
        bool(re.search(r'PP:0(?:\D|$)', log)),
        bool(re.search(r'PP tasks will do[^\n]+GPU', log)),
        bool(re.search(r'^\s*Performance:\s+([0-9.]+)', log, re.M)),
        'Finished mdrun' in log))
xvg = (root / 'state00' / 'smoke.xvg').read_text(errors='replace')
print('state0_dhdl_label=%s foreign_energy_legends=%d' % (
    'state 0:' in xvg,
    len(re.findall(r'^@\s+s\d+\s+legend "energy to ([0-9.]+)"$', xvg, re.M))))
PY
```

Return the review and parser-check output. These checks read existing Stage P
evidence and submit nothing. Do not use the inactive v3 package for
submission. Preserve the selected package and its future attempt directory;
never edit its contract or remove one-attempt guards. Baseline submission is
the next separate SCC command after the selected package's review is
accepted. HREX remains conditional on baseline result and accounting.

## SCC review and Stage P parser check — 2026-09-29

The user supplied `scc-i01` output for this selected v1 package. The remote
`SHA256SUMS` SHA-256 matched the local
`a4d353e5571beaae97fbbeddb413796fa10d0a97894018e2ba9d25f0f539a587`.
Both package and SCC source/image reviews passed all 20 manifest entries;
the final marker was `C2_SCOUT_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=True; no job submitted`. Accept this read-only review.
The same user output showed all 20 accepted Stage P state logs match the
selected scout's `PP:0`, GPU-task, `Performance:` and `Finished mdrun`
patterns. No rerun of these checks is needed.

The Stage P state-0 DHDL file contains the expected `state 0:` label, but
the quick probe for the literal spelling `energy to <lambda>` returned zero
matches. The user then supplied its first 80 lines (pasted-text SHA-256
`d673edb307e9d2feb32f2a1d83c2d086999229d1fde5c5c03a6fd4e8564e9c81`).
The actual GROMACS legend spelling is `\xD\f{}H \xl\f{} to <lambda>`;
the sealed validator matches the numeric `to <lambda>` suffix and therefore
does not depend on the quick probe's mistaken wording. Running the unmodified
validator on the pasted Stage P XVG passed: 20 foreign lambda legends,
23 total legends (including total energy, dH/dlambda and pV), 21 finite
data rows on the 0–4 ps / 0.2-ps grid, and 24 columns. A regression test
using this actual legend layout also passed. The parser hold is resolved;
the selected package remains unchanged, with no new release needed. No
scout job has yet been submitted.

## Baseline submission after accepted review

The user's selection already covers one bounded baseline attempt. On
`scc-i01`, from the selected v1 package only:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
cd "$PKG" || exit
bash SUBMIT_BASELINE_ON_SCC.sh
```

The wrapper repeats package/source review, checks its one-attempt guard,
validates the exact queue request and submits once. Preserve its job ID,
`submission-baseline/` and all resulting logs. If it exits without a job ID,
return the complete output and do not rerun or remove the guard. HREX remains
conditional on baseline technical evidence and `qacct`.

## Baseline submission result — 2026-09-30

The user ran `SUBMIT_BASELINE_ON_SCC.sh` from selected v1 on `scc-i01`.
Package/SCC source reviews and the baseline arm guard passed. The exact
two-hour L40S/`omp16` request returned `verification: found suitable
queue(s)`, and `qsub -terse` returned **job 7796136**. The wrapper reported
one bounded baseline technical scout submitted and the user recorded
`baseline_submit_exit=0`. This is evidence of successful submission, not
execution or technical completion. Preserve the job ID and
`submission-baseline/`; do not submit baseline again. HREX remains gated on
baseline technical output and `qacct` review.

## Read-only baseline status check

From `scc-i01`, run this while monitoring job 7796136, then again after it
leaves `qstat` if accounting is initially pending:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
qstat -j 7796136 2>&1 | tail -n 12
if [ -f "$PKG/attempts/baseline/status.json" ]; then
  cat "$PKG/attempts/baseline/status.json"
fi
if [ -f "$PKG/submission-baseline/job.log" ]; then
  tail -n 80 "$PKG/submission-baseline/job.log"
fi
qacct -j 7796136 2>&1 | tail -n 45
```

The status, job log and `qacct` must be reviewed before running the separate
`runtime.py accounting baseline` command. A missing `qacct` record while the
job is running is expected. Do not start HREX on a provisional technical
status or a job ID alone.

## HREX submission after accepted baseline

The [baseline result](f64a_c2_scout_baseline_result.md) passed the selected
technical and accounting gate on user-supplied evidence. The original user
selection covers one conditional HREX attempt. From `scc-i01`, use only the
selected release:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
cd "$PKG" || exit
bash SUBMIT_HREX_ON_SCC.sh
submit_rc=$?
printf 'hrex_submit_exit=%s\n' "$submit_rc"
```

The wrapper rechecks the baseline's 365-file post-accounting inventory and
then validates and submits one HREX job. Retain its output and job ID. If
it fails before returning a job ID, preserve `submission-hrex/` and send
the error; do not rerun or clear its one-attempt guard.
