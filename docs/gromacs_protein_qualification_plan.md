# Next C1 milestone: F64A folded-protein technical qualification

Status: **Stage P short protein technical qualification accepted,
2026-09-29**. Stage L job 7763284 is accepted; see
[its result](gromacs_gpu_ladder_result.md). The [Stage P input result](gromacs_protein_technical_inputs_result.md)
passed a 344-file integrity check; a separate
[runtime candidate](gromacs_protein_runtime_local_validation.md) passed SCC CPU
import, package review and queue validation. The user selected and submitted
the single bounded Stage P protein technical attempt as **job 7791102** on
2026-09-29. [The accepted result](gromacs_protein_runtime_result.md) records
19 rounds, 181 attempted/113 accepted exchanges, 20 correct checkpoint
transitions, both 20-client MPS sets, 614 verified saved hashes and `qacct`
`failed 0`/`exit_status 0` with 146 s on one L40S. Do not repeat A,
R, L, Stage P import or submission. No production arm or new FEP estimate is
selected by this plan.

## Purpose and boundary

Qualify one real, solvated **apo-2SH F64A folded-leg** hybrid system on the accepted
one-L40S/20-rank/private-MPS layout. Use all 20 lambda states of one independently
initialized realization. This is a short technical exercise for topology, PME,
constraints, GPU memory, exchange records, all-state energy export and graceful
whole-ladder restart. It cannot establish convergence, a folding ΔΔG, a method
advantage, or production throughput. Historical F64A continuation trajectories
are not a matched baseline for the future independent-window/HREX comparison.

The first candidate source is `r0` under
`/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded`, the SCC
tree previously validated against the frozen archive for the completed F64A pilot.
This path is a **candidate**, not a verified current input. Its old production TPRs
and checkpoints are evidence only; they must not be run under the r6 image or
altered in place. Local v2 pilot NPZs contain energies, not the topology and
coordinates needed for protein TPR preparation.

## Read-only source gate

Run the repository's [inventory script](../scripts/inventory_f64a_protein_source.py)
from the SCC repository clone in a login shell. It reads files and hashes them;
it does not invoke GROMACS or submit anything:

```bash
source scripts/scc_env.sh
python scripts/inventory_f64a_protein_source.py \
  --source /projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded \
  --config config/pipeline.yaml --repeat 0 > f64a_protein_source_inventory.json
```

Keep the JSON and command exit status, including a failed or incomplete inventory.
The script checks `system_r0/SYSTEM_READY`, `hybrid.top`, `em.gro`, `conf.gro`, and
each `w0_r0`–`w19_r0` window's lambda-minimized coordinates, MDP and TPR. It
reports SHA-256, size, the production MDP's physical keys, lambda-vector
agreement with the config, shared settings, state-index agreement and source
marker identity. The output is a provenance snapshot, not proof that an old TPR
is compatible with r6. Inspect the topology's recursive includes, force-field
availability and reduced-cysteine chemistry before copying
any source into a new isolated package. A missing/changed source fails this gate;
locate and verify another archived realization rather than reconstructing it
from NPZs or modifying historical files.

## Preparation and admission sequence

1. Preserve the inventory, path and hashes. Copy only the required source files
   into a new immutable qualification package. Keep the historical source and
   the A/R/L packages unchanged. Resolve and hash every topology include and
   parameter file. Confirm atom count/order, mutation F64A, neutral net-charge
   change, apo metal-free state and reduced Cys57/Cys146 with explicit checks.
2. In the **exact r6 SIF**, perform CPU-only `grompp` of all 20 states from the
   same source realization and per-state lambda-minimized coordinates. Use the
   historical 20-value vector and physical settings from
   `config/pipeline.yaml`, while recording any technical short-run output or
   restart settings separately. Do not use `-maxwarn`. Verify TPR/MDP identities,
   each `init-lambda-state`, common topology and atom order, full foreign-lambda
   energy labels and finite initial energies. If the r6 image lacks the needed
   pmx force field, stop at preparation and package the exact verified dependency
   before making TPRs; do not substitute another force field.
3. Register a fresh bounded GPU attempt only after preparation passes. The
   candidate layout is Stage L's proven **one L40S, `omp16`/16 slots, 20
   one-thread ranks explicitly oversubscribed on a shared 16-CPU mask, private
   MPS and one host**. Freeze its step count, exchange interval, walltime,
   storage cap, seeds, output cadence and restart boundary in its own YAML and
   immutable package. Stage L's toy timing and high exchange acceptance do not
   set protein acceptance thresholds. Validate scheduler eligibility before
   submission and retain a one-attempt guard.
4. Run two normal MPI launches in one allocation: synchronized stop, hash and
   archive all 20 first-phase checkpoints/outputs, then append all 20 together.
   Never resume a single state alone. Capture both MPS client sets, CPU affinity,
   GPU UUID and per-rank mapping. Record every exchange attempt, accepted swap
   and permutation. Validate state/walker mapping across restart, finite
   DHDL/EDR records and foreign-state labels, no duplicated boundary, unchanged
   first-phase archives, cleanup, and final `qacct` exit status. **Attempts need
   not be accepted on every protein neighbor link**: zero acceptance can be a
   valid physical outcome if attempts and accounting are complete.

## Exit and remaining design decisions

A technical pass requires all 20 protein states to complete and restart with
correct state identities, consistent exchange/permutation records, valid energy
exports, the assigned GPU and 20 matching MPS clients in each launch, cleaned
MPS, sealed outputs, and `qacct` `failed 0`/`exit_status 0`. Report failed or
timed-out attempts with their accounting. Do not call a short technical pass a
scientific result or infer speedup from it.

Before any GPU package is executable, freeze the short-run numerical settings
and resource cap after exact-SIF preparation and a storage/runtime estimate.
Protein-system qualification remains separate from C2's fresh, matched-cost
F64A independent-window/HREX development arms. C2 still needs its own registered
duration, repeats, analysis and resource admission; the historical 15 ns stop and
failed validation gate remain in force.
