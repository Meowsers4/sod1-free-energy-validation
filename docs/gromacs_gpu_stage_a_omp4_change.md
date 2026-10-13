# Stage A CPU reservation change — 2026-09-27

Current status: user reported successful guarded replacement submission as job
`7758910`. Its scheduler state and execution result have not yet been reported.
The earlier preparation/transition steps below are history; do not repeat them.
Monitor v3 `submission-A/job.log` and retain `qacct -j 7758910` after completion.

The user requested a CPU configuration change after job 7726162 remained queued.
The replacement candidate uses `-pe omp 4` instead of `-pe mpi32 32`. The test
already launches four MPI ranks with one OpenMP thread each inside one container.
The scheduler PE name does not change that launcher into an OpenMP program.
Four CPU slots cover the four computational threads; CPU binding remains off.

All four L40S GPUs, one-host placement, seeds, synthetic inputs, SIF, exchange
interval, one-attempt limit and ten-minute walltime are preserved. Maximum CPU
reservation falls from 16/3 to 2/3 slot-hours. GPU reservation stays at 2/3 GPU-hour.
The old package and queued job have not been changed. No replacement was submitted.

This is a placement improvement candidate, not a proven fix. The September 26
snapshot had four eligible-model hosts with four GPUs and 32 CPU slots apparently
free, so CPU count alone did not explain that snapshot. Queue eligibility,
reservations, quota and scheduler policy remain unresolved. Earlier site evidence
listed `omp` in `l40s`'s `pe_list`.

Follow-up attachment `0fa45a30-60c1-457a-ae22-e7fd49ea955d/Pasted text.txt`
confirms `omp` uses `allocation_rule $pe_slots`, no start/stop hooks, no PE user
restrictions, and `job_is_first_task TRUE`. This supports a four-slot single-host
allocation with the container-local launcher. Job 7726162 is still `qw`. All ten
`l40s` queue instances show blank state flags; five report zero used CPU slots.
The complete quota output contains host CPU/GPU caps and unrelated `linga` rules;
it does not identify a user/project quota blocking this job. These observations
do not prove why the 32-slot job is waiting or guarantee dispatch of the candidate.
The scheduling checks and subsequent CPU preparation have now been supplied.
User reports `INPUTS_PREPARED` and `PACKAGE_AND_PREPARED_INPUTS_VERIFIED` for v3.
No remote files were independently downloaded, and no replacement job ID is yet
reported. No SIF rebuild or preparation repeat is needed.

The guarded transition is `scripts/replace_queued_gmx_stage_a.sh`, supplied as a
pasteable SCC block. It rechecks the pinned manifest and preparation, requires
the old job still pending, holds it and requires `hqw`, confirms no old attempt,
deletes that held job, confirms disappearance, and performs exactly one qsub.
It keeps transition logs under v3 `submission-A/`; any error stops and preserves
that guard. Do not rerun/clear it after an ambiguous result. This implements the
requested CPU reduction within the single unexecuted Stage A attempt, not an
additional attempt. GPU allocation and dynamics still require actual SCC execution.

## Next SCC checks

```bash
qstat -u bodeb
qconf -sp omp
qstat -f -explain a -q l40s
qquota -u bodeb
```

These are read-only. Do not use `qalter -pe omp 4` on 7726162: its immutable v2
contract requires `mpi32` and 32 slots and would abort. Do not run a second job
alongside it. If it has started or completed, inspect its evidence before deciding
on a replacement; that would no longer be a substitution of an unused attempt.

## Fresh candidate preparation

Package: `results/gpu_smoke_packages/gmx-gpu-stage-a-20260927-v3-omp4`.
Package manifest SHA-256:
`ead0eac31e97a63f96484fb3da87ae24d50618090887fba65f251f3ca87632ef`.
Specification: `docs/gromacs_gpu_stage_a_omp4_v1.yaml`.
The original specification remains the generator default. The explicit Snakemake
config option `gpu_smoke_spec` selects the new specification for this package only.

After the scheduling checks, transfer the fresh directory from a local Mac terminal:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/gmx-gpu-stage-a-20260927-v3-omp4 bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

On SCC, CPU-only preparation in the fresh directory:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-stage-a-20260927-v3-omp4
sha256sum --check --strict SHA256SUMS
bash PREPARE_ON_SCC.sh
bash REVIEW_ON_SCC.sh
```

This regenerates only the tiny toy TPR inputs and records them against the new
package identity; it does not compile GROMACS, build a SIF, submit a job or use a
GPU. Existing v2 prepared inputs and logs remain untouched. Return the preparation
result and current old-job status before transitioning submissions. Cancellation
and confirmation that the old job never executed must precede a replacement
submission; the available authorization does not cover an additional GPU attempt.

## Local verification

Focused tests: 18 passed, one optional CPU dynamics rehearsal skipped. Tests cover
the four-slot single-host allocation, rejection of wrong allocations and unreviewed
resource changes, and identical image/fixture/state/input bytes across configurations.
No dynamics code changed. Snakemake dry-run and execution each selected one
`gpu=0` packaging job. Both manifests verified; v2 retained manifest SHA-256
`59fc0d8e1e5a0e881f6f73d1060646ac5a2b568fd31cd6b6b81555a284c678c9`.
Released v2/v3 runtime and input files are byte-identical; their contracts differ
only in scheduler PE and slot count.
SCC `omp` configuration is now inspected; actual job integration and GPU execution
remain untested.

References: [BU single-node allocations](https://www.bu.edu/tech/support/research/system-usage/running-jobs/parallel-batch/)
and the recorded [site preflight](gromacs_gpu_preflight_2026-09-24.md).
