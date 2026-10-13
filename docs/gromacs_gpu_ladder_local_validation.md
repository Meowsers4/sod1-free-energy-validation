# Stage L local validation — 2026-09-28

Package: `results/gpu_smoke_packages/gmx-gpu-ladder-20260928-v1`.
Manifest SHA-256: `f3ab36b8fe46d8f768b826186edd462505b03b682bb8905e9d3b027dc72c44d8`.
No SCC connection, GPU allocation, job submission or image rebuild was performed.

## Checks performed

```bash
GROMACS_RESTART_LOCAL_GMX=/opt/anaconda3/envs/md/bin/gmx \
  /opt/anaconda3/envs/rise/bin/python -m pytest tests/ -q
```

**408 passed, one skipped in 49.17 seconds.** Captured output:
`docs/review/gromacs_ladder_20260928_pytest.txt`.
The skipped check is the separately enabled original smoke-only CPU rehearsal;
checkpoint/restart CPU rehearsals ran for both four-state and 20-state inputs.

For every one of the 20 states, actual local GROMACS 2025.3 CPU execution checked:
warning-free grompp, dumped TPR state/duration/atom count/full lambda vector,
normal stop at 1000 with correct 1.0 ps/part-1 checkpoint, successful append to
2000/2.0 ps/part 2, finite complete DHDL with all foreign-lambda labels, unchanged
pre-boundary DHDL/energy rows, and exactly 21 final output times including the
single 1.0 ps boundary. The CPU rehearsal runs states independently and does not
exercise external MPI, exchange, MPS, GPU dynamics or exact-SIF startup.

Additional tests reject insufficient or multi-host allocations, changed resource
scope, four-state input import, incomplete/foreign 20-client MPS PID sets,
malformed upper-state exchange logs, absent neighbor-link coverage, and a missing
state-19 checkpoint. General restart tests cover corrupt seals, wrong checkpoint
metadata, changed earlier rows and duplicated/missing restart-boundary records.
Runtime modules parse with Python 3.6 grammar; Bash checks pass for generated
shell/job scripts. The first extended CPU test run caught a test-only exact-float
comparison (0.7 versus 0.7000000000000001); numeric time comparison now uses an
explicit 1e-6 ps tolerance, and the complete suite above passed afterward.

Fresh-cache Snakemake dry-run and execution using the registered spec each
contained exactly one packaging job with gpu=0. Generated package checksums
were verified. The prior sealed Stage A v4 and Stage R package manifest hashes
still match their accepted records; neither package was rewritten.

Remote remaining evidence: queue eligibility for omp/20, fresh exact-SIF TPR
preparation, actual 20-rank exchange and restart, simultaneous 20-client MPS
observations in each launch, cleanup, and qacct. Local success does not substitute
for these checks or establish performance/scientific convergence.
