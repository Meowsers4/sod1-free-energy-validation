# F64A C2 CPU-only checkpoint-branch input checker

Status: **implemented and passed the archived Stage P CPU rehearsal,
2026-09-30; selected no-exchange branch inputs do not yet exist**.
This implements the CPU input-review portion of the
[checkpoint-branch contract](f64a_c2_checkpoint_branch_review.md).
It does not create checkpoints or TPRs, run GROMACS, contact SCC, submit
a job, or authorize the bounded branch fixture or production.

The [transferable checker](../packages/f64a-c2-branch-input-checker-20260930-v1)
contains a standalone Python 3 script and two review wrappers. Its
source is [`src/analysis/f64a_c2_branch_input_checks.py`](../src/analysis/f64a_c2_branch_input_checks.py).
The four-entry package manifest has SHA-256
`20ab60faf698286fa0365998ce11f3f00e9ba88975e5ed68e392001616fe1369`.
It consumes **saved outputs** from a separately reviewed CPU-only
`grompp -t`/`gmx dump` preparation. The
[archived Stage P rehearsal](f64a_c2_branch_cpu_rehearsal_package.md)
passed the checker on SCC with a 363-file prepared manifest. Those Stage P
checkpoints followed exchange and are only a mechanics rehearsal; the
required common no-exchange checkpoints do not currently exist.

## Required plan

A JSON plan accompanies one independent realization. It has exactly the
following required fields (additional metadata may be stored separately):

| Field | Meaning |
| --- | --- |
| `schema_version=1`, `scope="f64a_c2_shared_checkpoint_branch_cpu_input_review"` | Checker identity. |
| `execution_authorized=false`, `production_authorized=false` | This input review cannot select a run. |
| `image_path`, `image_sha256` | Absolute r6 SIF path and its accepted SHA-256 `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`; the checker hashes the file. |
| `state_count=20`, `atom_count` | Exact state and atom dimensions. |
| `prep_step`, `prep_time_ps`, `prep_checkpoint_part`, `branch_simulation_part`, `dt_ps` | Registered common boundary and continuation metadata. The branch part must not precede the checkpoint part. |
| `retained_steps` | Object with positive integer `baseline` and `hrex` targets; these remain unselected today. |
| `lambda_vector` | The registered ordered 20-state FEP vector. |
| `output_strides` | Positive `nstdhdl`, `nstenergy`, `nstxout-compressed` values; these remain subject to final registration. |
| `checkpoint_sha256` | Exact map from `state00` through `state19` to the independently sealed common checkpoint hashes. |

The plan must be derived from a verified common-preparation record. This
checker verifies its declared files and arm copies, but cannot establish
that an as-yet-unrun common preparation is scientifically adequate or
that a self-declared plan has been independently approved.

## Saved input layout

For each `stateXX`, the root passed to the checker must contain:

```text
common/stateXX/start.cpt
common/stateXX/start.cpt.dump
arms/baseline/stateXX/start.cpt
arms/baseline/stateXX/start.cpt.dump
arms/baseline/stateXX/topol.tpr
arms/baseline/stateXX/topol.tpr.dump
arms/baseline/stateXX/mdout.mdp
arms/baseline/stateXX/grompp.log
arms/baseline/stateXX/grompp-result.json
arms/hrex/stateXX/          (same seven file names as baseline)
```

`*.dump` files are saved text output from exact-r6 `gmx_mpi dump -cp`
or `dump -s`. Each `grompp-result.json` must contain `exit_status: 0` and
the full `argv` list, including `grompp -t` for that state's copied
`start.cpt`, `-f`, `-c`, `-p`, and `-o`; `-maxwarn` is rejected. Existing
simulation outputs in the arm directories are rejected. The CPU rehearsal
collector saves the required metadata lines and records the SHA-256 and
byte count of each full dump in `dump-provenance.json`; do not hand-edit
those extracts.

The checker verifies all 20 source checkpoint hashes and metadata,
both copied checkpoint hashes and metadata, exact r6 image, zero-warning
`grompp`, 40 TPRs and dumps, effective continuation and velocity settings,
registered step/time and output strides, atom and lambda dimensions,
and the complete effective-MDP comparison. For a given state, only
`nsteps` may differ between arms. Across states, only the lambda-state
index and state-specific `gen-seed`/`ld-seed` may differ. Any extra
physical or output setting in one arm fails the review.

This is a **read-only artifact check**. It cannot prove that `mdrun -cpi`
will resume from the copies or that the first exchange occurs strictly
after the branch. The [bounded branch fixture](f64a_c2_checkpoint_branch_review.md)
must still test those behaviors before a production design can be selected.

## Later user-run review

Once a separate CPU preparation has produced and sealed the layout and
plan for the selected no-exchange common phase, the user can run these
commands in their SCC terminal. The archived Stage P rehearsal has its
own accepted tree; it is not a selected scientific branch plan.

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-input-checker-20260930-v1
cd "$PKG" || exit
bash REVIEW_PACKAGE.sh
bash REVIEW_INPUTS.sh /absolute/path/to/branch-inputs /absolute/path/to/branch-plan.json
```

A successful review prints the plan hash, all 40 TPR hashes/final steps,
and `C2_BRANCH_CPU_INPUT_REVIEW_PASS states=20 arms=2; no job submitted`.
Retain the input tree, plan, dumps, `grompp` logs and package manifest
for independent review. No submission command is included.

Local verification: seven targeted tests cover a complete 20-state
synthetic input, missing checkpoint, wrong checkpoint state, changed
arm physics, velocity regeneration, missing TPR/warning, and old output
in an arm tree. They test the checker, not GROMACS or SCC behavior.
