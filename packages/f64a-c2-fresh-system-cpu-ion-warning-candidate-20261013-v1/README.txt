F64A C2 isolated r3 CPU system-build ion-warning correction candidate,
2026-10-13. This package is INACTIVE: execution_authorized=false.

Selected job 8059683 passed explicit login-shell and Python checks, then
stopped when its wrapper rejected a grompp warning while making ions.tpr.
The warning reports net charge -5 before the next genion -neutral step.
The historical builder calls this grompp with -maxwarn 2. This candidate
permits exactly one reviewed Ewald/net-charge warning for that one exact
ions.mdp command and charge -5; every other warning remains fatal.
The warning exemption does not allow a nonzero command exit. The later
post-ion minimization grompp still rejects every warning.

REVIEW_ON_SCC.sh is read-only. It verifies the old selected package's
manifest and saved ion grompp command JSON, requires returncode 0, and
prints the saved command hash before doing storage and queue checks. It
submits no job. The output of this static review is needed before any
separate selection. The previously selected jobs 8032575 and 8059683,
their packages, logs and one-attempt guards must be preserved.

The pinned WT/config, seed 2072077476, force field, CPU request (eight
slots, one hour), no-GPU scope and explicit login-shell startup are
unchanged. Both execution and production remain unauthorized. No FEP
windows, GPU work, automatic retry or production inference is selected.
