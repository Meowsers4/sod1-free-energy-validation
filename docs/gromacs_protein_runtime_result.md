# Stage P accepted — F64A folded-protein technical run, job 7791102

Reviewed 2026-09-29. The selected, bounded 20-state F64A folded apo-2SH
technical qualification passed on the user-supplied SCC evidence. One L40S,
private MPS, 20 one-thread MPI ranks on 16 CPU slots, exchange, all-state
energy output and a graceful whole-ladder checkpoint/append restart ran with
the exact r6 SIF and the accepted 2,000-step short TPRs. **No rerun is needed.**

Package: `f64a-protein-technical-runtime-20260928-v1` at
`/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-runtime-20260928-v1`.
Package `SHA256SUMS` SHA-256:
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`.
Prepared 344-entry source manifest SHA-256:
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
SIF SHA-256: `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
Registered runtime: [gromacs_protein_runtime_v1.yaml](gromacs_protein_runtime_v1.yaml).
Private scratch was retained at `/scratch/gmx-smoke-P-7791102.fsx6uj_5`.

## Reviewed execution evidence

The user supplied `submission-P/job.log` and `attempt/status.json`. Both
reported `pass_pending_review_and_accounting`, no failure, restart verified,
20 MPS clients observed, cleanup confirmed, 20 MPI ranks and 16 allocated CPU
slots. The wrapper elapsed time was 141.02632453897968 seconds. Its derived
0.039173979038605464 allocated GPU-hour is distinct from scheduler accounting.
The historical `status.json` still says `pending_qacct`; accounting was reviewed
afterward and is recorded here without modifying the sealed attempt.

The user then ran a read-only Python evidence check on SCC, separately from
the runtime validator, and supplied `STAGE_P_SAVED_EVIDENCE_CHECK_PASS`. The
reported output is preserved in
[the review transcript](review/gromacs_protein_7791102_saved_evidence_user_output.txt),
SHA-256 `e11f4fb4b03d86f7255c32ad3149a847af94c46d7cc9370210598c5f0deb7496`.
The check read `protein-ladder-review.json`, `permutations.json`,
`restart-review.json`, both phases' 20 rank records, `cpu-affinity.json`,
`device-map.json`, and `output-hashes.json`. It confirmed:

- Exactly 19 exchange rounds at steps 100–1900, with the step-1000 boundary
  appearing once. The registered alternating-neighbor schedule made 181
  attempts across all 19 links; 113 swaps were accepted. Applying every
  accepted swap reproduced each saved state-to-walker permutation. Acceptance
  is descriptive, not a pass threshold for the protein.
- All 20 checkpoints advanced from step 1000, 2 ps, part 1 to step 2000,
  4 ps, part 2, each with its correct lambda-state index. The restart review
  reports nine pre-restart rounds, 19 combined rounds, preserved pre-checkpoint
  data and a unique boundary output.
- Each phase had exactly 20 rank PIDs matching exactly 20 MPS clients on
  server PID 826770. Both phases used
  `GPU-9dab95cd-93b6-8551-58e3-71a474c82587`. All 20 rank records matched
  the selected 16-CPU affinity mask.
- SHA-256 rechecking of all 614 files listed in `output-hashes.json` passed.
  This checks the saved attempt against its runtime-created inventory; it is
  not an independent scientific assessment of each raw trajectory.

Per-neighbor attempted/accepted counts, from links 0–1 through 18–19:

| Pair | Attempted | Accepted | Pair | Attempted | Accepted |
|---|---:|---:|---|---:|---:|
| 0–1 | 10 | 6 | 1–2 | 9 | 7 |
| 2–3 | 10 | 8 | 3–4 | 9 | 5 |
| 4–5 | 10 | 7 | 5–6 | 9 | 6 |
| 6–7 | 10 | 6 | 7–8 | 9 | 5 |
| 8–9 | 10 | 6 | 9–10 | 9 | 5 |
| 10–11 | 10 | 6 | 11–12 | 9 | 5 |
| 12–13 | 10 | 4 | 13–14 | 9 | 2 |
| 14–15 | 10 | 7 | 15–16 | 9 | 5 |
| 16–17 | 10 | 9 | 17–18 | 9 | 8 |
| 18–19 | 10 | 6 | | | |

The runtime validator additionally requires finished `mdrun` logs and GPU task
mapping for every state, consistent exchange logs across ranks, finite and
complete all-state DHDL and EDR energy/temperature rows, unchanged TPRs and
first-phase archive hashes, and clean MPS teardown. The user-supplied pass
status supports those checks; the agent did not download raw SCC binaries.

## Scheduler accounting

`qacct -j 7791102` reports queue `l40s` on `scc-504.scc.bu.edu`, project
`rise-batteries`, PE `omp16`/16 slots, `failed 0`, `exit_status 0`, and 146
seconds scheduler wallclock. It started September 29 at 19:02:29 and ended
at 19:04:55 (scheduler timezone not independently supplied). One GPU for
146 seconds is about 0.0406 allocated GPU-hour; 16 slots for that duration
are about 0.649 allocated CPU-slot-hour. These are resource-time calculations,
not billed SU. The `qacct` `maxvmem=120.739G` field is virtual memory, not a
GPU-memory measurement. The completed job no longer appearing in `qstat`
does not indicate a failure.

## Scope and next decision

Stage P qualifies this one real, solvated protein system and short exchange/
restart execution on the selected one-GPU layout. It establishes neither
equilibration nor converged free energy, speedup, sampling efficiency, a
matched-cost method advantage, multi-start reliability or GPU-memory margin.
It does not reopen the failed historical validation gate. Production/C2 remains
unselected and unauthorized. Preserve the sealed package, 614-file attempt,
first-phase archive, scratch, logs and `qacct`; no technical repeat is needed.
The next project decision is a separately designed and preregistered protein
sampling comparison with a scientific endpoint, resources and stop rules.
