F64A C2 isolated r3 CPU system-build ion-warning selected attempt,
2026-10-13. User selected exactly one fresh technical CPU job after the
inactive candidate passed user-run SCC static review.

This package pins the old job 8059683 saved ion grompp command hash and
requires the command to have exited 0 with exactly the reviewed pre-ion
charge -5 Ewald warning. This one warning is allowed only for the exact
ions.mdp command before genion -neutral. A nonzero command exit, any
additional or changed warning, or a warning in a later grompp remains fatal.

The output is a fresh isolated F64A folded r3 system, never a continuation
of prepared.incomplete. The pinned WT/config, seed 2072077476, force
field, eight CPU slots, one-hour limit, no GPU, explicit login-shell
startup, complete output audit, and historical-tree isolation remain.
No FEP windows or production work are authorized. No automatic retry.

The user must transfer this new package and run its static SCC review.
Only after exact manifest verification, review_exit=0, and the selected
review marker should SUBMIT_ON_SCC.sh be run once. It creates submission/
before queue validation and submission. Jobs 8032575 and 8059683, their
packages, logs and guards must be preserved. Do not submit old packages.
