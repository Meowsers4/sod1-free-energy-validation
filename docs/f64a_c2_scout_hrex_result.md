# F64A C2 100-ps HREX scout — accepted technical result

The user ran the selected release's `SUBMIT_HREX_ON_SCC.sh` on `scc-i01`
after the accepted [baseline 7796136 technical and accounting review](f64a_c2_scout_baseline_result.md).
The package and SCC source reviews passed, and the HREX submission guard
passed. That guard rechecked the baseline status/accounting gate and its
365-file post-accounting hash inventory before creating a new HREX
submission directory. The exact one-L40S, `omp16`/16-slot,
`h_rt=02:00:00` request returned `verification: found suitable queue(s)`.
`qsub -terse` returned **job 7799011**, and the user recorded
`hrex_submit_exit=0`.

This established one bounded HREX submission. Subsequent user-supplied
execution and scheduler evidence is recorded below. Preserve job 7799011,
`submission-hrex/`, any `attempts/hrex/` tree and private scratch. Do not
resubmit or clear its one-attempt guard. The selected pair allows no automatic
retry. Baseline outputs must remain intact for the paired timing comparison.

## Read-only status check

From `scc-i01`, run while monitoring the job, then again after it leaves
`qstat` if accounting is initially pending:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
qstat -j 7799011 2>&1 | tail -n 12
if [ -f "$PKG/attempts/hrex/status.json" ]; then
  cat "$PKG/attempts/hrex/status.json"
fi
if [ -f "$PKG/submission-hrex/job.log" ]; then
  tail -n 80 "$PKG/submission-hrex/job.log"
fi
qacct -j 7799011 2>&1 | tail -n 45
```

Review the job result and `qacct` before invoking the one-time
`runtime.py accounting hrex` checker. A missing `qacct` record while the
job is still running is expected. No further GPU work follows automatically.

## In-progress check — 2026-09-30

The user's first read-only check still found job 7799011 in `qstat -j`,
with the selected `l40s` queue, `omp16`/16 slots, project
`rise-batteries`, `hrex.sge` and the expected `submission-hrex/job.log`
path. The scheduler printed live usage, including `cpu=00:39:00`; this is
aggregate CPU usage, not elapsed walltime. Neither
`attempts/hrex/status.json` nor job-log text was yet available, and
`qacct -j 7799011` returned `job id ... not found`. Treat this as a job
still in progress or not yet accounted, not an execution pass or failure.
Wait for job completion and repeat only the read-only status check. Preserve
the one-attempt guard and do not submit another HREX job.

## Completed job and provisional technical result — 2026-09-30

The user then supplied `attempts/hrex/status.json`, the matching job-log
tail, and `qacct -j 7799011`. The runner reports
`technical_status=pass_pending_accounting_and_review`, `failure=null`, all
20 MPS clients observed, and MPS cleanup confirmed. Its measured wrapper
wall time is 1530.295 s, including 8.532 s startup, 1491.007 s dynamics,
and 30.659 s validation. Observed persistent and scratch maxima are
130,290,261 and 8,572,947 bytes. Private scratch is retained at
`/scratch/gmx-c2-hrex-7799011-cqwcrbnf`.

SGE reports job `c2-scout-hrex` on `l40s`, host `scc-510.scc.bu.edu`,
project `rise-batteries`, `omp16`/16 slots, `failed=0`,
`exit_status=0`, and `ru_wallclock=1540` s. This corresponds to
0.427778 allocated GPU-hours and 6.844444 requested CPU-slot-hours.
Combined with the accepted baseline, the pair used 0.620278 allocated
GPU-hours and 9.924444 requested CPU-slot-hours, within its selected
4/64-hour limits. These are allocation measures, not the SCC SU charge;
the tariff and remaining SU balance are still unknown.

This is a **provisional** HREX technical pass. The sealed accounting mode
must reverify the saved output hashes, validate `qacct`, and write its
post-accounting inventory. Then review the 20 checkpoints, energy records,
XTC frames, exchange summary, and performance records before accepting the
paired scout. No production or FEP conclusion follows from this job.

On `scc-i01`, run the one-time accounting review from the selected release:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
cd "$PKG" || exit
/usr/libexec/platform-python runtime.py accounting hrex
accounting_rc=$?
printf 'hrex_accounting_exit=%s\n' "$accounting_rc"
if [ "$accounting_rc" -eq 0 ]; then
  python - <<'PY'
import json
from pathlib import Path
p = Path('attempts/hrex')
review = json.loads((p / 'output-review.json').read_text())
accounting = json.loads((p / 'accounting.json').read_text())
hashes = json.loads((p / 'output-hashes-after-accounting.json').read_text())
exchange = review['exchange']
print('reviewed_states=', len(review['checkpoints']))
print('checkpoint_steps=', sorted({v['step'] for v in review['checkpoints'].values()}))
print('energy_records=', sorted({v['records'] for v in review['energy'].values()}))
print('xtc_frames=', sorted({len(v) for v in review['xtc'].values()}))
print('exchange_rounds=', exchange['rounds'])
print('exchange_attempted=', exchange['attempted_exchanges'])
print('exchange_accepted=', exchange['accepted_exchanges'])
print('all_neighbor_links_attempted=', exchange['all_neighbor_links_attempted'])
print('by_neighbor=', exchange['by_neighbor'])
print('final_state_to_walker=', exchange['final_state_to_walker'])
print('performance_states=', len(review['gromacs_performance_ns_per_day']))
print('post_accounting_hashed_files=', len(hashes))
print('accounting=', accounting)
PY
fi
```

If the checker fails, retain the attempt and its error output for review.
Do not rerun or resubmit HREX.

## Accounting and paired output review accepted — 2026-09-30

The user supplied the compact summary from the conditional review block
above. Because that block prints this summary only when the one-time
`runtime.py accounting hrex` command exits 0, it supports a successful
checker result, although the pass-marker line itself was not included in
the pasted output. The resulting `accounting.json` reports `reviewed=true`,
job 7799011, `failed=0`, `exit_status=0`, 1540 s, 0.427778 allocated
GPU-hours and 6.844444 requested CPU-slot-hours. The post-accounting
inventory lists **385 hashed files**. These are user-supplied SCC results;
the remote files have not been downloaded or independently hashed locally.

The sealed output review covered all **20** states. Each checkpoint is at
step **50,000** (100 ps); each state has **101** energy records and **three**
XTC frames. All 20 GROMACS performance records are present. The common
exchange history contains the registered **99 rounds**, **941 attempted**
and **629 accepted** neighbor swaps. The supplied per-neighbor counts sum
to those totals; all 19 links were attempted, and the final state-to-walker
vector is a permutation of 0–19. Acceptance is an observed technical
diagnostic, not a pass threshold or convergence finding.

The measured HREX rate is **233.77 ps per allocated GPU-hour** including
setup and validation, or **241.45 ps per GPU-hour** using dynamics time
alone. The accepted baseline measured 519.48 and 552.17, respectively.
For these two 100-ps technical jobs, HREX used **2.22 times** the allocated
GPU time for the same per-state duration; its setup-inclusive rate was
**45.0%** of baseline. The completed pair consumed **0.620278 allocated
GPU-hours** and **9.924444 requested CPU-slot-hours**. Billed SCC SU is
still unknown. These short-run rates include the exact scout outputs and
one-L40S/20-rank layout; they are measurements for resource design, not
long-duration speed guarantees or scientific FEP results.

Accept HREX 7799011 and the paired scout for the **registered technical
timing and output question**. Preserve both immutable attempt trees,
post-accounting inventories, scheduler records and private scratch pending
retention planning. No additional scout attempt or production run follows
automatically. The next work is CPU-only design: update the equal-cost and
storage sensitivity cases using these measured short-scout rates, then
choose scientific precision targets and a production protocol separately.

## Read-only output-size breakdown — 2026-09-30

The user subsequently read both `storage-by-extension.json` files on SCC
and summed each current attempt tree without altering it. The baseline
tree is **111,244,910 bytes** and HREX is **130,525,018 bytes** after
accounting. The by-extension snapshots, made during job validation before
the last accounting metadata, list `.xtc` at 8,430,480/8,429,380 bytes,
`.xvg` at 628,601/628,687 bytes, `.edr` at 530,480 bytes per arm,
`.tpr` at 29,061,760 bytes per arm and `.gro` at 53,012,440 bytes per
arm (baseline/HREX order). Baseline retained 20 `.cpt` files totaling
18,465,760 bytes; HREX retained 40 totaling 36,931,520 bytes. The extra
checkpoint copies account for most of the whole-tree size difference.
The two arms' 120 full-system XTC state-frames occupy 16,859,860 bytes,
or about 140,499 bytes per observed frame. The
[resource sensitivity draft](f64a_c2_precision_resource_draft.md) uses this
only for explicitly labeled XTC scale cases, not a complete storage
forecast. Both immutable attempt trees remain on SCC; the agent has not
downloaded or independently inventoried them.
