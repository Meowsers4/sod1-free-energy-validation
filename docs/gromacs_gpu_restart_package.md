# Four-rank, one-GPU checkpoint/restart qualification

Preparation requested on 2026-09-27 after Stage A job 7762792 passed. This is a
new bounded synthetic restart test, not the 20-rank Stage B or a repeat of the
completed Stage A job. Preparation does not authorize or submit GPU execution.

Use the same r6 SIF, four lambda states, toy system, TPRs, seeds and device
mapping. Resources: one L40S, one host, omp/four slots, four MPI ranks and one
thread per rank, ten minutes maximum (at most 1/6 allocated GPU-hour), one
attempt. The seven-minute shared work deadline includes both dynamics phases
and intermediate validation. Quota/storage guards and private MPS failure
handling are inherited from the passing Stage A package.

1. Verify/import the sealed v4 TPRs on SCC without grompp or rebuilding.
2. Launch all four replicas with the original 1,000-step TPRs and `-nsteps 500`.
   This is a planned normal stop, not signal/crash injection.
3. Require successful first-phase GPU dynamics, four-client MPS overlap, four
   exchange rounds (100–400), finite outputs, and all four checkpoints at step
   500/time 0.5 ps, simulation part 1 and the correct lambda-state indices.
4. Copy all first-phase outputs, commands, rank/device records, MPS overlap and
   permutations into `attempt/before-restart/`. Seal hashes and make copied files
   read-only. Verify current checkpoint/TPR/output hashes before launching again.
5. Start a new four-rank MPI process set using unchanged TPRs, `-cpi smoke.cpt
   -append`, and no `-nsteps` override. Every checkpoint must exist with the sealed
   hash; missing checkpoints cannot silently start fresh simulations. The private
   MPS service remains idle between MPI launches and stops after the second.
6. Require new four-client MPS overlap and final checkpoints at step 1,000/time
   1.0 ps/part 2. Validate complete finite output times with the 0.5 ps boundary
   present exactly once. DHDL/energy rows strictly before the checkpoint must
   remain unchanged. Validate all nine exchange rounds 100–900, preserving the
   first four permutations and requiring accepted exchanges after restart.
   The sealed first-phase archive must still match its hashes.

GROMACS 2025.3 skips exchange on the last step of a run; its MD loop permits
exchange at the initial continuation step. Thus step 500 is expected once,
in the continuation, and is not silently discarded or double-counted. A
different observed boundary schedule fails review; no adaptive parser relaxation.
Checkpoint-aware append can remove the old log's final performance summary, so
whole-log byte-prefix identity is deliberately not an acceptance criterion.
The checkpoint row itself may be recomputed; earlier numerical output is
preserved and the boundary time must remain unique.

Sources: [GROMACS 2025.3 mdrun options](https://manual.gromacs.org/2025.3/onlinehelp/gmx-mdrun.html),
[append behavior](https://manual.gromacs.org/2025.3/user-guide/managing-simulations.html),
[version-pinned MD loop](https://github.com/gromacs/gromacs/blob/v2025.3/src/gromacs/mdrun/md.cpp).

This checks graceful whole-ladder restart on a single allocation/device. It does
not test cross-node or cross-allocation restart, daemon restart, arbitrary failure,
20-rank scaling, a protein model, or bitwise agreement with an uninterrupted run.

## Transfer and prepare only

On the laptop:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/gmx-gpu-restart-20260927-v1 \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

In the SCC login shell:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-restart-20260927-v1 &&
sha256sum -c SHA256SUMS &&
bash PREPARE_ON_SCC.sh &&
bash REVIEW_ON_SCC.sh
```

This imports verified inputs from `gmx-gpu-stage-a-20260927-v4-mps`, checks the
existing SIF and records ancestry. It does not read/modify the completed Stage A
dynamics outputs, submit a job, or delete any old job/package. Do not rerun after
a partial preparation failure; retain the output for review.

## Separately selected execution

The reviewable job is `stage_R.sge`; `SUBMIT_ON_SCC.sh` validates resources and
submits once, with a `submission-R` guard and no automatic retry. Run it only
after execution of this new ten-minute attempt is selected. There is no old
queued job to replace. After submission, monitor the returned ID and
`submission-R/job.log`. Required evidence is `attempt/status.json`,
`attempt/restart-review.json`, `attempt/permutations.json`, both MPI logs,
`attempt/before-restart/`, output hashes and `qacct -j JOB_ID`.
Success remains pending evidence review and accounting. Keep checkpoint copies
and all files referenced by their checksums; do not clean up the append targets.
