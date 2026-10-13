# F64A C2 paired technical scout: selected with unknown SU balance

This is the concrete decision record for the next **technical** GPU attempt.
The [CPU scout inputs](f64a_c2_scout_cpu_result.md),
[guarded GPU runtime](f64a_c2_scout_gpu_runtime_candidate.md),
[resource preflight](f64a_c2_scout_execution_preflight.md), and
[inactive execution package](f64a_c2_scout_execution_release_candidate.md)
have passed their respective user-supplied SCC reviews. No C2 scout job has
been submitted. The original stopped F64A FEP campaign remains stopped at
15 ns; this timing scout will not produce a free-energy estimate.

## Proposed selected scope

| Item | Exact limit or condition |
| --- | --- |
| Question | Measure runtime and stored bytes for identical 20-state F64A folded apo-2SH `r0` baseline and HREX technical runs, each targeting 100 ps/state. No convergence or effect claim. |
| Inputs | Accepted 381-entry CPU prepared tree, all 20 paired TPR hashes, exact r6 SIF. Baseline and HREX receive byte-identical TPRs. |
| Order | One baseline attempt first. Review all 20 technical outputs, MPS cleanup, file hashes and `qacct` (`failed=0`, `exit_status=0`) before considering one HREX attempt. HREX is never automatic. |
| Exchange | Baseline `-replex 0`; HREX `-replex 500 -reseed 20260929`, with 99 complete exchange rounds required for a completed 100-ps HREX run. |
| Allocation | Each arm: one L40S, `omp16`/16 slots, 20 one-thread ranks, private MPS, one host, hard walltime 2 hours, no reschedule. Pair maximum: two attempts, 4 allocated GPU-hours and 64 requested CPU-slot-hours. No automatic retry. |
| Early bounds | 105-minute work deadline and GROMACS `-maxh 1.7`; persistent and scratch each stop at 768 MiB per arm below the 1-GiB cap. A stopped or incomplete arm is censored and cannot supply a paired rate. |
| Storage | Persistent outputs under `/project/rise-batteries`; exact-r6 image stays on `/projectnb`; compute-node scratch is checked at job start. The 2026-09-30 UTC preflight saw `/project` 23.63/50 GB quota usage and 32G filesystem free. |
| Accounting | Preserve job IDs, scheduler walltime, requested slot-hours, post-job `qacct`, output byte totals and separate setup-inclusive and dynamics-only rates. Actual billed SU remains unverified. |
| Scientific boundary | No production protocol, extension of the historical 15-ns pilot, MBAR ΔΔG, variant prediction or wider protein arm follows from this selection. |

`qsub -w v` found a suitable queue for the exact per-arm two-hour request.
The remote inactive v3 package manifest matched its local seal and its SCC
review passed with `execution_authorized=False`. Its submission scripts are
present for review but remain closed. The remaining accounting uncertainty is
the current `rise-batteries` SU balance: `acctool` returned command not found
on `scc-i01`, and no current balance was supplied from BU's RCS User
Information page. BU says charges depend on requested CPU-slot walltime and
the node's SU rate; therefore 64 requested CPU-slot-hours is an upper bound
on slot-time if both jobs exhaust their limits, **not** a verified SU cost.

**Selection status: selected, 2026-09-29 America/Chicago.** After reviewing
the exact bounded pair and SU uncertainty, the user replied **“proceed with
balance unknown.”** The machine-readable decision is in
[`f64a_c2_scout_execution_selection.json`](f64a_c2_scout_execution_selection.json).
This accepts uncertainty in the current project balance for this limited
technical pair; it does not establish an SU tariff or authorize any larger
run. Keep the reviewed inactive v3 package unchanged. Build and review a
new manifest-sealed selected release on SCC before submitting baseline.
Review baseline technical evidence and accounting before the separate HREX
submission. No automatic retry or production work is selected.
