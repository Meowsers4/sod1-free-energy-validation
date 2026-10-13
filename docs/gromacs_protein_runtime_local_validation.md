# F64A protein runtime candidate — local package validation

Date: 2026-09-28. Candidate package:
`results/gpu_smoke_packages/f64a-protein-technical-runtime-20260928-v1`.
Its `SHA256SUMS` SHA-256 is
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`.
`sha256sum -c SHA256SUMS` passed locally, and all generated shell/SGE scripts
passed `bash -n`. The source spec, runtime adapter, protein checks, restart
validator, MPS code, existing wrapper and scheduler scripts are sealed.

Ten targeted local tests passed across CPU Stage P input preparation, protein
exchange parsing, runtime package generation and a mocked 20-state CPU import.
The mock exercised manifest and source ancestry checks, copied all 20 TPRs,
ran metadata validation through a fake `singularity` command and confirmed no
job/attempt directory was created. A separate test exercised 20-state
checkpoint/archive validation through a 1,000→2,000-step restart with **zero
accepted swaps**, which is valid when every scheduled attempt and state
permutation is accounted for. These tests are implementation checks, not
actual GROMACS/SCC protein execution.

The SCC source manifest, r6 SIF and Stage P TPRs are not available locally.
The next read-only/CPU step is transfer, `qsub -w v` queue validation and one
fresh import under SCC, following [the package guide](gromacs_protein_runtime_package.md).
The import performs exact-r6 `gmx dump -s` on all 20 TPRs and checks their
atom count, state index, lambda vector, timestep and step count. It retains
compact dump metadata rather than full protein dumps to protect project quota.
No GPU job was submitted. The candidate 30-minute ceiling is at most 0.5
allocated GPU-hour and 8 allocated CPU-slot-hours if fully used; billable SU
depends on SCC accounting and is not estimated here.

## SCC CPU import reported

The user reported `import_exit=0` on `scc-i01`, 20 `imported_tpr_sha256`
lines matching the accepted Stage P short TPR hashes, and
`PROTEIN_TPRS_IMPORTED_AND_REVIEWED_CPU_ONLY; no job submitted`. The importer
reaches that marker only after its source manifest, TPR and exact-r6 metadata
checks and fresh target seal pass. This is a successful CPU import on
user-supplied output; no rerun is needed.

## SCC package and queue review accepted — 2026-09-29

The user then reported the runtime package `SHA256SUMS` SHA-256 as
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`,
matching the local candidate. `REVIEW_ON_SCC.sh` returned
`PACKAGE_AND_PREPARED_INPUTS_VERIFIED` and `review_exit=0`. The saved
`queue-validation.iXRbyNjL.log` says `verification: found suitable queue(s)`
for the sealed one-L40S/`omp16`/16-slot/30-minute request. Thus the CPU-imported
runtime package and scheduler request are accepted for a **separate explicit
one-attempt GPU decision**. Queue suitability does not guarantee immediate
dispatch. Agent-side SSH is unavailable; all remote evidence is user-supplied.

The reviewed attempt is 20 protein ranks, private MPS, two MPI launches with
the whole ladder stopped at step 1,000 then appended to step 2,000 (4 ps), one
L40S, 30 minutes hard walltime, one attempt, no retry, 1.5 GiB early storage
stop, 2 GiB cap and 3 GiB free-space guard. Maximum allocation is 0.5
GPU-hour and 8 CPU-slot-hours; billed SU remains unknown. The package's
`execution_authorized: false` records preparation-time status. No protein GPU
job was submitted or authorized by this review; a separate explicit user
selection is the remaining admission step under `CLAUDE.md` rule 6.

## Bounded Stage P submission — 2026-09-29

The user explicitly selected the registered technical attempt by running the
guarded `SUBMIT_ON_SCC.sh` on SCC. It repeated the package/input review and
suitable-queue check, returned **job 7791102**, and printed its single-job
submission marker. The agent did not log in or submit remotely. This is a
submission record only: queue/running/completed state, runtime status, all
protein exchange/restart/energy results, MPS cleanup and `qacct` are pending.
Preserve `submission-P/` and any `attempt/`; do not rerun the script, remove
guards, or submit a second protein attempt automatically.

## Provisional Stage P runtime result and accounting — 2026-09-29

User-supplied `submission-P/job.log` and `attempt/status.json` agree on
`pass_pending_review_and_accounting`, no reported failure, 20 ranks on 16 CPU
slots, restart verified, both 20-client MPS observations and MPS cleanup.
Wrapper elapsed time was 141.026 s, or 0.039174 observed allocated GPU-hour.
Private scratch was retained at `/scratch/gmx-smoke-P-7791102.fsx6uj_5`.
`qacct -j 7791102` reports `l40s` on scc-504, `omp16`/16, `failed 0`,
`exit_status 0`, and 146 s scheduler wallclock (about 0.0406 allocated
GPU-hour). Billed SU has not been supplied. Scheduler `maxvmem=120.739G` is
virtual memory, not a GPU-memory observation. `qstat` not finding the job is
consistent with its completed state.

The saved detailed attempt files still need review: complete exchange schedule
and walker permutations, per-state 1,000→2,000 checkpoint transition, archived
pre-checkpoint data, phase-specific MPS rank/client PID sets, CPU affinity and
output hashes. Do not treat the short technical pass as production validation.
No repeat or production/C2 job is selected.

## Stage P evidence review accepted — 2026-09-29

The user ran the read-only independent saved-evidence check on SCC. It reported
19 rounds, 181 scheduled neighbor attempts, 113 accepted swaps, all 19 links
covered, and matching walker permutations. All 20 first/final checkpoint
transitions, preserved pre-checkpoint data, unique boundary, both matching
20-client MPS sets, 20 rank affinities within the 16-CPU mask, and 614 saved
output hashes checked successfully. Together with `qacct` exit status 0, this
accepts the selected short protein technical qualification. See the
[Stage P result](gromacs_protein_runtime_result.md) for provenance and limits.
No rerun is needed; production remains a separate decision.
