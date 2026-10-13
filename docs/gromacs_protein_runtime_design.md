# F64A protein technical runtime design — admission pending

Date: 2026-09-28. This design follows the [accepted CPU short-input package](gromacs_protein_technical_inputs_result.md)
and the [accepted synthetic Stage L run](gromacs_gpu_ladder_result.md). It does
not authorize or submit a protein GPU job.

## Frozen input ancestry

- Stage P source package: `/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1/prepared`.
- Stage P `SHA256SUMS` SHA-256:
  `858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
- Exact r6 SIF SHA-256:
  `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
- Twenty per-state short TPR hashes are recorded in the Stage P result. Import
  must verify the 344-entry source manifest, all 20 TPR hashes, matching
  per-state atom identity and `gmx dump` MDP/state/lambda fields. No `grompp`
  repetition or historical 1,750,000-step TPR use.

## Proposed bounded technical test

Use one `l40s` host, one L40S, `omp16`/16 CPU slots, 20 one-thread MPI ranks
with the verified explicit 16-CPU affinity mask and private MPS. Use the 20
already prepared 2,000-step protein TPRs (2 fs; 4 ps). Perform two normal MPI
launches in one allocation: stop all states at step 1,000, seal all first-phase
checkpoints and outputs, then append all states to step 2,000. Exchange interval
is 100 steps. Use a fresh fixed exchange seed in the runtime contract.

The user-supplied size survey found 89 MB prepared inputs, 28 MB total TPRs
and `grompp` estimates of roughly 5 Mb/state, or about 100 MB across the 20
states. A **candidate** 2 GiB package/output cap, 1.5 GiB early stop and 3 GiB
free-space requirement leave room for logs, extracted energies and the sealed
first-phase copy. `df -h` showed 9.3 GB available on `/projectnb`. Subsequent
`pquota rise-batteries` showed 50 GB quota and 45.79 GB usage on
`/projectnb/rise-batteries`, leaving about 4.21 decimal GB before import;
the earlier 4 GiB guard would have rejected that quota snapshot. The package
checks current project quota and compute-node scratch at runtime. The 2 GiB
cap remains a conservative hard limit, not a target. A candidate 30-minute scheduler ceiling
with an earlier work deadline is conservative for a technical test, not a
throughput estimate. Actual protein GPU memory and speed remain unknown.

## Acceptance checks specific to protein

The runtime package must reuse Stage L's scheduler, GPU UUID, private MPS,
CPU-affinity, storage stop, timeout, whole-ladder checkpoint sealing and
cleanup checks. The protein validator must additionally confirm:

1. Every imported TPR has the same atom count/order and 20-value lambda vector,
   the intended local `init-lambda-state`, 2,000 steps, 2 fs, all-state energy
   request and the sealed source hash.
2. All 20 ranks finish both phases on the assigned GPU, with matching MPS
   clients in each launch and correct rank/state/CPU mapping.
3. Every scheduled exchange round and every neighboring-pair **attempt** is
   recorded, and the resulting walker permutations agree across state logs.
   A protein link may have zero accepted swaps; acceptance is descriptive,
   never a technical pass threshold.
4. All 20 checkpoints move from step 1,000/2 ps/part 1 to step 2,000/4 ps/part
   2 with correct state identities. First-phase archives remain unchanged;
   energy/DHDL prefix rows survive append and the 2 ps boundary occurs once.
5. DHDL labels include all 20 foreign lambda states, numeric energy and
   temperature records are finite at the prescribed times, final coordinates
   and compressed trajectories exist, and no output cap is breached.
6. MPS cleanup is confirmed and `qacct` shows `failed 0`, `exit_status 0`.

The user will review a sealed executable package, its measured resource checks
and one-attempt bound before any submission. A technical pass would qualify the
protein runtime mechanics only. It would not validate production sampling, a
folding free energy, speedup, or the prospective matched-cost comparison.
