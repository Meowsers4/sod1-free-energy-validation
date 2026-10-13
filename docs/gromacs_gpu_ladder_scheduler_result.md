# Stage L scheduler matrix — 2026-09-28

User-supplied SCC validation output is preserved verbatim in
`docs/review/gromacs_ladder_scheduler_20260928_user_transcript.txt`.
SHA-256: `f1bf4784ed9ab63d4488472df2bc6ce6e50a1752f088e1b669aa85666737cd65`.
Agent has not independently queried the scheduler.

All checks held project rise-batteries, hard queue l40s, one L40S GPU, 20-minute
wall limit and PE omp fixed; only CPU slots changed. Binary /bin/true was passed
with -b y and validation-only -w v, avoiding package script directives.

| CPU slots | Validation |
| --- | --- |
| 4 | found suitable queues |
| 8 | found suitable queues |
| 16 | found suitable queues |
| 20 | no suitable queues (7763184) |
| 28 | no suitable queues (7763185) |
| 32 | no suitable queues (7763186) |

The initial package /20 check (7763168) also failed. Numbers printed during
validation do not show submitted jobs. The many hard-queue-list exclusions are
expected from requesting l40s; they are not evidence of container errors or a
need for access to every other queue. The underlying restriction is not identified.
This supports eligibility of this one-GPU/omp16 request at the observed snapshot,
not immediate availability or a universal SCC 16-core limit.

The next candidate preserves the complete 20-state synthetic ladder while
reserving 16 CPU slots: explicit 20-on-16 MPI oversubscription, reported host slot
count 16, MPI yielding, and a shared 16-ID Linux CPU affinity mask verified by
every rank. See `docs/gromacs_gpu_ladder_omp16_package.md` and its registered spec.
This is preparation of a new immutable candidate; no allocation, submission or
GPU execution has been reported. Old v1 input preparation was not reached by the
failed && command chain. Preserve v1 and all successful A/R evidence.
