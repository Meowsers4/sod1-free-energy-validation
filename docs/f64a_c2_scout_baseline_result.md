# F64A C2 100-ps baseline scout — accepted technical result

Job **7796136** is the single selected baseline technical attempt from
`f64a-c2-scout-execution-selected-20260929-v1`. The user supplied its
`status.json`, job-log tail and `qacct` output from `scc-i01`. This is
user-supplied evidence; the remote output files have not been downloaded or
independently rehashed locally. HREX was submitted later, as recorded below.

The runner reported `technical_status=pass_pending_accounting_and_review`,
`failure=null`, 20 observed MPS clients and confirmed MPS cleanup. Its
wall time was 689.950 s, including 8.051 s startup, 651.975 s dynamics and
29.841 s validation. Peak observed persistent and scratch use were
111,144,766 and 142,742,154 bytes, respectively, both below the selected
768-MiB stop threshold. The retained private scratch path is
`/scratch/gmx-c2-baseline-7796136-114e2le0`; preserve it until the review
is complete.

SGE `qacct -j 7796136` reports `l40s` on `scc-513.scc.bu.edu`, project
`rise-batteries`, `omp16`/16 slots, `failed=0`, `exit_status=0`, and
`ru_wallclock=693` s. This is 0.1925 allocated GPU-hours and 3.08
requested CPU-slot-hours for the job. The SU charge remains unverified;
`qacct cpu` is process time, not billed SU. The scheduler record identifies
the job as `c2-scout-baseline`, started 2026-09-30 08:56:01 and ended
09:07:34 in the SCC log's timezone.

These values support a **provisional** technical pass. The package's
`runtime.py accounting baseline` mode must now verify its sealed output
hashes against the original post-job inventory and re-query/validate
`qacct`, writing `accounting.json` once. Review the compact per-state
checkpoint, energy, trajectory and no-exchange summary afterward. HREX
remains blocked until that accounting and evidence review passes; do not
rerun the baseline attempt.

On `scc-i01`, from the selected release, complete the one-time accounting
check and print a compact review summary:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-selected-20260929-v1
cd "$PKG" || exit
/usr/libexec/platform-python runtime.py accounting baseline
accounting_rc=$?
printf 'baseline_accounting_exit=%s\n' "$accounting_rc"
if [ "$accounting_rc" -eq 0 ]; then
  python - <<'PY'
import json
from pathlib import Path
p = Path('attempts/baseline')
status = json.loads((p/'status.json').read_text())
review = json.loads((p/'output-review.json').read_text())
accounting = json.loads((p/'accounting.json').read_text())
hashes = json.loads((p/'output-hashes-after-accounting.json').read_text())
print('technical_status=', status['technical_status'])
print('reviewed_states=', len(review['checkpoints']))
print('checkpoint_steps=', sorted(set(v['step'] for v in review['checkpoints'].values())))
print('energy_records=', sorted(set(v['records'] for v in review['energy'].values())))
print('xtc_frames=', sorted(set(len(v) for v in review['xtc'].values())))
print('exchange=', review['exchange'])
print('performance_states=', len(review['gromacs_performance_ns_per_day']))
print('post_accounting_hashed_files=', len(hashes))
print('accounting=', accounting)
PY
fi
```

Return the command output for independent review. If the accounting checker
fails, preserve its files and error output; do not submit HREX or alter the
baseline attempt to force a pass.

## Accounting and output review accepted — 2026-09-30

The user ran the selected package's `runtime.py accounting baseline` mode.
It returned `C2_SCOUT_BASELINE_ACCOUNTING_REVIEW_PASS
job_id=7796136 gpu_hours=0.192500` with exit 0. Per the sealed checker, this
reverified the original post-job output hashes before recording a validated
`qacct` result. The new post-accounting inventory lists **365 files**.

The user-supplied compact output review reports 20 state checkpoints all at
step **50,000** (100 ps), **101** energy records and **three** XTC frames per
state, 20 GROMACS performance records, and zero baseline exchange rounds,
attempts or accepts. The state-to-walker mapping stayed the identity. The
accounting record has `reviewed=true`, `failed=0`, `exit_status=0`, 693 s,
0.1925 allocated GPU-hours and 3.08 requested CPU-slot-hours. The
setup-inclusive rate is 519.48 ps per allocated GPU-hour; dynamics-only is
552.17 ps per GPU-hour. These are timings for this one technical baseline,
not a production FEP performance or convergence claim. Billed SU is still
unknown.

Accept baseline 7796136 for the **registered conditional HREX gate** on the
user-supplied evidence. The selected HREX wrapper independently rehashes
the 365-file post-accounting baseline inventory before its one-time queue
validation and submission. Preserve all baseline outputs and scratch; do
not rerun baseline. The HREX outcome is still unknown.

The user subsequently ran the guarded HREX submission as **job 7799011**;
the [HREX record](f64a_c2_scout_hrex_result.md) now accepts the second
technical arm and the paired scout on user-supplied execution, accounting,
and compact output-review evidence.
