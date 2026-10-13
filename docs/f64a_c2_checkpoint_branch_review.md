# F64A C2 shared-checkpoint branch review

**Subsequent result, 2026-10-03:** The [live branch fixture](f64a_c2_branch_fixture_result.md)
passed its bounded technical acceptance checks, including a new no-exchange
common checkpoint set, isolated baseline/HREX continuations, exchange history,
saved output hashes and scheduler accounting. The text below is the earlier
pre-fixture review. Technical qualification does not select C2 production;
the [post-fixture design review](f64a_c2_post_fixture_production_design.md)
records the remaining scientific decisions.

Status: **CPU-only design and static code review, updated 2026-09-30**. The user
selected one common no-exchange preparation followed by isolated baseline
and HREX retained runs. This review specifies the admission contract for
that branch. It does **not** qualify a branch execution, select a duration,
or authorize another cluster job or production MD.

## Verdict and evidence boundary

The branch is feasible in the GROMACS 2025.3 interface, but **is not yet
technically qualified** in this project. A checkpoint contains full-precision
coordinates, velocities, and coupling state. GROMACS documents both
continuation from a checkpoint and creating a changed-MDP TPR from it.
It also documents separate `.partXXXX` outputs with `-noappend`.
([Managing long simulations](https://manual.gromacs.org/documentation/2025.3/user-guide/managing-simulations.html),
[grompp 2025.3](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-grompp.html))

The accepted Stage P restart uses `-cpi ... -append` with the same TPR and
output tree (`src/analysis/gromacs_protein_restart.py`). It proves a
20-checkpoint restart, but it does not prove fan-out from one checkpoint
set into two isolated output trees. The accepted C2 scouts use distinct
fresh starts (`packages/f64a-c2-scout-execution-selected-20260929-v1/core_runtime.py`)
and have no `-cpi` branch. Their fixed 50,000-step validator assumes
unparted output names and cannot validate a branched retained run as is.
No local GROMACS executable or SCC checkpoint was available for a dynamic
branch test during this review. These are evidence limits, not failures
of the accepted runs.

## Contract to implement before any branch run

| Boundary | Required invariant and evidence |
| --- | --- |
| Common preparation | For each independent realization, freeze one system and 20 state starts. Exchange is off for the entire common phase. Verify all 20 terminal checkpoint hashes and `gmx dump` step, time, simulation part, and FEP state. Seal the common outputs and record the exact image, topology/includes, TPRs, MDPs, seed, and source ancestry. |
| Fan-out | Copy each state checkpoint into two new, isolated arm trees. Verify every copy against the sealed original before launch. Preserve the common outputs unchanged. Do not carry common output files into the arm trees or append to them. |
| Arm inputs | Build and review both 20-TPR sets with the exact r6 image. If preparation and retained-phase output settings differ, use `grompp -t` with the checkpoint and a registered retained MDP; supply the checkpoint again to `mdrun -cpi`. Set `gen-vel = no` and `continuation = yes`; do not draw new velocities. Inspect `mdout.mdp`, TPR contents, `init-step`, `tinit`, `simulation-part`, total step target, state labels, and lambda vector. Freeze the effective physical/output-field allowlist before execution. Different `nsteps` are expected if equal-cost arm durations differ. |
| Launch | Require all 20 input checkpoints to exist and match hashes immediately before `mdrun`. Use a copied input checkpoint as `-cpi`, a distinct output checkpoint name with `-cpo`, and `-noappend` in each arm. Baseline exchange remains off; HREX uses its frozen post-branch interval and seed. Record each rank's arguments and source checkpoint hash. |
| Results | Validate absolute and retained-relative step/time grids, 20 state outputs and checkpoint states, unique post-branch boundary records, complete energy/DHDL labels, final step, and part-numbered files. Confirm zero baseline exchange; in HREX validate common round history, all neighbor attempts, and the final permutation. Verify source-checkpoint and common-tree hashes after both arms. |
| Cost | Account for common preparation once per realization and allocate half to each arm in the equal-cost ledger. Record arm-specific setup, failed attempts, resumes, GPU time, storage, and final retained exposure separately. |

GROMACS may **start from the TPR's first step if the `-cpi` file is absent**;
therefore a missing checkpoint must fail in our wrapper before GROMACS runs.
The default append behavior checks old output-file checksums, while
`-noappend` writes separate part files. A distinct `-cpo` prevents the
retained run from overwriting the copied input checkpoint.
([mdrun 2025.3](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-mdrun.html))
`grompp -t` and `mdrun -cpi` are both needed when changing the MDP while
preserving a continuous restart; GROMACS recommends inspecting `mdout.mdp`
and comparing TPRs, and warns against bypassing warnings with `-maxwarn`.
([grompp 2025.3](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-grompp.html))

## Narrow qualification sequence

1. **CPU input review:** The
   [read-only checker](f64a_c2_branch_input_checker.md) is implemented
   locally. Once common checkpoints exist, a separate CPU preparation
   must preprocess and dump both 20-state branch TPR sets with exact r6;
   the checker then compares saved evidence with a registered plan and
   rejects warnings, changed physics, wrong checkpoint ancestry, or
   ambiguous final steps. The
   [archived Stage P CPU rehearsal](f64a_c2_branch_cpu_rehearsal_package.md)
   has now passed for all 20 states, but those exchange-enabled checkpoints
   are not the selected common no-exchange ancestry. The new common
   checkpoint set still needs its own input review.
2. **Bounded branch fixture:** With an explicitly selected small execution
   scope, run one short no-exchange common phase, fan out all 20 checkpoints,
   then run both branches. Validate actual part-file naming, preserved
   input checkpoints, step/time continuity, first HREX exchange timing,
   20-rank exchange permutation, baseline nonexchange, and MPS cleanup.
   Stage P cannot substitute for this fan-out test. This fixture remains
   **unselected**; the
   [bounded fixture candidate](f64a_c2_branch_fixture_design.md)
   now specifies the short schedule and pass gates, but no command should
   submit it yet.
3. **Production design review:** Only after the fixture passes, freeze
   common-preparation duration, arm targets, repeats, exchange interval,
   storage and cost caps, and scientific analysis. Independent review of
   those frozen inputs is required before a production selection.

The candidate 2-ns common preparation is not selected. The accepted scouts
do not determine its equilibration adequacy, long-run rate, or the absolute
`init-step`/part behavior of a changed-MDP branch. The dynamic fixture
must resolve those mechanics before the branch is treated as ready.
