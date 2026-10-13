# Stage L accepted — job 7763284, reviewed 2026-09-28

The full synthetic 20-state ladder passed technical and scheduler review on the
user-supplied evidence. Qualified layout: one SCC host, one L40S, private MPS,
20 one-thread MPI ranks time-sharing 16 CPU slots with explicit oversubscription
and a shared 16-CPU affinity mask. Graceful whole-ladder checkpoint/append restart
succeeded in the same allocation. No rerun is needed.

Package: `gmx-gpu-ladder-20260928-v3-pe-omp16`; manifest SHA-256
`4faa2d6c66a896d21420fb4c08cd8520870d4a6f9be02d5cbc4742a5f5ae28a8`.
Spec: `docs/gromacs_gpu_ladder_pe_omp16_v3.yaml`.
SIF SHA-256: `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
SCC package directory:
`/projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-ladder-20260928-v3-pe-omp16`.
Retained private scratch: `/scratch/gmx-smoke-L-7763284.cvq4nam4`.

## Evidence and verification

The user first supplied status.json through the job log: technical pass pending
review/accounting, no failure, restart and larger ladder verified, all 20 MPS
clients observed, and cleanup confirmed. They then supplied ladder-review.json,
restart-review.json, permutations.json, cpu-affinity.json and qacct.
The latter transcript is preserved verbatim in
`docs/review/gromacs_ladder_7763284_user_transcript.txt`, SHA-256
`ae0590d27c186c35c78a4db71d359b3d0dec711c794db4e9e744dc50d8a1c35a`.

Independent parsing/checks of that supplied transcript confirmed:

- Every state00–state19 checkpoint advances from step 1000/time 1.0 ps/part 1 to
  step 2000/time 2.0 ps/part 2, with the correct lambda-state index throughout.
- Exactly 19 exchange rounds, steps 100–1900 at interval 100. Step 1000 appears
  once. Nine rounds precede restart; ten occur in the resumed phase.
- Reconstructed every state-to-walker permutation by applying the accepted swaps
  in order; all match the supplied arrays. All swaps are adjacent, have the
  correct alternating parity, and do not overlap within a round.
- 181 accepted neighbor swaps overall: each even-start pair exchanges ten times,
  each odd-start pair nine times. All 19 links are exercised. There are 95 swaps
  in the resumed phase including nine at step 1000 (86 strictly after it).
- Phase 1 rank PIDs 278233–278252 and phase 2 PIDs 280385–280404 are distinct sets
  of 20. Each set exactly matches its recorded MPS clients. Both use server
  278175 and GPU UUID `GPU-39197a5d-b0c7-dff4-e40b-c6a5ddfebe7a`.
- CPU record reports 20 ranks, 16 allocated slots, inherited IDs 0–31 and selected
  IDs 0–15. The selected set contains exactly 16 allowed IDs. Per-rank enforcement
  is supported by the successful runtime checks, not an independent download of
  every rank record.

Runtime validators additionally report preserved pre-checkpoint data, unique
boundary output, finite complete DHDL/energy records and foreign-lambda labels,
correct GPU task mapping, unchanged sealed first-phase archives/TPRs and cleanup.
Raw TPRs, checkpoints, energy files, logs and output-hash inventories have not been
independently downloaded or recomputed locally. Acceptance is explicitly based
on the reported runtime validation plus the independently checked supplied review
records and accounting. Historical status.json pending fields remain unchanged;
this document records the completed review separately.

## Scheduler accounting

qacct identifies job 7763284 on **scc-503.scc.bu.edu**, queue l40s, project
rise-batteries, granted PE **omp16**, 16 slots, **failed 0 / exit_status 0**.
Scheduler timestamps: September 28 02:17:25 submitted, 02:19:37 started,
02:20:29 ended (timezone not supplied). Queue wait was **132 seconds** and
scheduler wallclock **52 seconds**. Runtime wrapper elapsed was
48.21217385798809 seconds; its derived GPU-hour value 0.013392270516107804
is not billed SU. Actual billed service units were not supplied.

Preserve the failed v2 attempt 7763245 separately: four seconds scheduler wallclock,
exit status 1 from the omp/omp16 name mismatch, before MPS/dynamics. Its accounting
was reviewed in `docs/gromacs_ladder_7763245_failure.md`; it is not silently removed
from qualification history or counted as a pass.

## Scope of the completed milestone

This completes the selected synthetic full-ladder technical qualification on
one GPU with 20 ranks and graceful restart. Earlier four-state Stage A and Stage R
are also accepted. It does not qualify the original four-GPU Stage B layout,
protein topology/PME/constraints, crash or cross-allocation recovery, convergence,
free-energy accuracy, speedup, or sampling efficiency. The weakly perturbed toy's
high exchange acceptance is not a protein acceptance target. No production or
new GPU simulation is selected by this result; the historical scientific gate
and completed-pilot stopping decisions remain unchanged.

Keep the sealed package, imported prepared inputs, both phases' logs and MPS
records, before-restart archive, CPU-affinity evidence, output hashes and qacct.
The next scientific implementation would need its own concrete protein-system
qualification design; this completed toy should not be rerun as a prerequisite.
