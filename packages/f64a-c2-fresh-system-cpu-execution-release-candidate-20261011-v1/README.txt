F64A C2 isolated r3 CPU system-build execution release candidate, 2026-10-11.

Execution is disabled. REVIEW_PACKAGE.sh, PREFLIGHT_ON_SCC.sh and
REVIEW_ON_SCC.sh are read-only. They check package, historical source, code, three older ion
placements, seed derivation, host GROMACS 2025.3 and the pmx force field.
They do not create a system or submit a job. REVIEW_ON_SCC.sh also validates
the requested CPU queue with qsub -w v, which does not submit.

The included cpu-system.sge, SUBMIT_ON_SCC.sh and builder.py prepare are
reviewable candidate code. The submission guard rejects execution while
source-spec.json says execution_authorized=false. Do not qsub this candidate.
A separately sealed selected package is needed for one scheduled 8-slot,
1-hour CPU rehearsal, with no reschedule or automatic retry.

The rehearsal design would copy the pinned prepared WT, config and panel
CSV into a new package-local workspace. It would call the existing pmx
builder with only its ROOT redirected to that workspace. The historical
rise-project/results tree must remain untouched. Its build would use no GPU
allocation or FEP window dynamics. The audit requires a reduced, apo 38414-
atom system, 41 NA and 36 CL, a distinct r3 ion coordinate hash, saved full
command logs including failures and a final SHA-256 manifest. Lambda-aware state starts are a
later separate step. No protein production or scientific inference is
authorized by this candidate.
