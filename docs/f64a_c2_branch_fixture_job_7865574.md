# F64A C2 live branch fixture: job 7865574 accepted

Status: **bounded technical fixture accepted** after review of the saved
phase summaries and scheduler accounting. See the [accepted result](f64a_c2_branch_fixture_result.md).
The user ran the selected release on `scc-i01`; the agent did not access SCC.

The selected 21-entry package's remote `SHA256SUMS` SHA-256 was
`a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`,
matching the local seal. `REVIEW_PACKAGE.sh` checked every listed file,
and `REVIEW_ON_SCC.sh` exited 0 after matching all 20 initial TPR hashes.
The submission wrapper re-ran its permit/source checks, reported
`C2_BRANCH_FIXTURE_ONE_JOB_SUBMISSION_GUARD_PASS`, and `qsub -w v` found
suitable queues. `SUBMIT_ON_SCC.sh` exited 0 and returned **job 7865574**.
Its scope is one L40S/omp16/16-slot/20-rank/30-minute technical attempt,
no reschedule or retry. The user reported a 15,000-SU balance; actual SU
charge remains unknown.

The user subsequently supplied `attempt/status.json` and the job log.
They report `technical_status=pass_pending_accounting_and_review`,
`failure=null`, 300.07 seconds wrapper walltime and 0.08335 observed
allocated GPU-hours. Common, baseline and HREX dynamics took 26.34,
39.33 and 52.10 seconds, respectively; each phase reports 20 matching
MPS clients and cleanup. The log includes
`C2_BRANCH_INPUTS_FROM_NO_EXCHANGE_COMMON_REVIEW_PASS`. Peak recorded
persistent and scratch bytes were 524,885,081 and 142,801,721, below
their 1.5-GiB stop thresholds. These are runtime reports, not a separate
review of the saved output records.

The supplied `qacct -j 7865574` reports `l40s` on `scc-504.scc.bu.edu`,
`omp16`/16 slots, `failed=0`, `exit_status=0` and `ru_wallclock=306`
seconds. This is **0.085 allocated GPU-hours** and **1.36 requested
CPU-slot-hours**, below the 0.5/8 ceilings. The scheduler result is
consistent with the runtime report. The actual SU charge is not supplied.

The user then ran `runtime.py accounting`. Its **first call exited 0** and
reported `C2_BRANCH_FIXTURE_ACCOUNTING_REVIEW_PASS job_id=7865574
gpu_hours=0.085000`. That routine verifies all files in the runtime's
`output-hashes.json` before recording `qacct` and a post-accounting hash
manifest. The user invoked the same command a second time; it exited 1
with `ValueError: accounting already recorded`, as the one-time guard
requires. Source review of the code confirms that this guard returns
before writing any attempt file. The second shell redirection replaced
the top-level `accounting-run.log`, but the first success marker is in
the supplied transcript and the attempt's accounting record remains.
Do not invoke `runtime.py accounting` again.

The user supplied the saved common, baseline and HREX review summaries,
seals, output-hash counts and storage summary. All 20 states reached the
planned checkpoints; HREX recorded three rounds, 29 attempted and 23
accepted neighboring swaps, with every neighboring link attempted and
a consistent final permutation. The [result record](f64a_c2_branch_fixture_result.md)
gives the evidence and limits. Preserve the selected package,
`submit.log`, job log and complete attempt. Do not run the submission
wrapper again or clear guards.

## Completed read-only saved-evidence summary on SCC

From the user's SCC terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-execution-selected-20261003-v1
cd "$PKG" || exit
python - <<'PY'
import json
from pathlib import Path
p = Path('attempt')
load = lambda name: json.loads((p / name).read_text())
status, account = load('status.json'), load('accounting.json')
print('status=', status['technical_status'], 'job_id=', status['job_id'])
print('accounting=', account)
for phase, final, part in (('common', 1100, 1), ('baseline', 3100, 2), ('hrex', 2600, 2)):
    review = load(phase + '-review.json')
    checkpoints = review['checkpoints']
    print('phase=', phase, 'states=', len(checkpoints),
          'steps=', sorted(set(row['step'] for row in checkpoints.values())),
          'parts=', sorted(set(row['part'] for row in checkpoints.values())),
          'dhdl_records=', sorted(set(row['records'] for row in review['dhdl'].values())),
          'energy_records=', sorted(set(row['records'] for row in review['energy'].values())),
          'xtc_frames=', sorted(set(len(row) for row in review['xtc'].values())),
          'exchange=', review['exchange'])
for name in ('common-seal.json', 'branch-input-seal.json',
             'output-hashes.json', 'output-hashes-after-accounting.json'):
    print('manifest=', name, 'entries=', len(load(name)))
print('storage=', load('storage-summary.json'))
PY
```

The user ran this read-only summary and supplied its output. It touched
neither the GPU nor accounting; no further command is needed for this
bounded technical qualification.
