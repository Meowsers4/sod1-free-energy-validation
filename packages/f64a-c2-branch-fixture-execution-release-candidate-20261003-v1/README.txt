F64A C2 live checkpoint branch fixture: inactive execution release candidate.

The sealed contract has execution_authorized=false and no selection record.
SUBMIT_ON_SCC.sh contains the exact one-job request for review, but its first
operation is runtime.py permit, which rejects this inactive contract before
creating a submission directory, touching the GPU or calling qsub. Do not
submit this candidate. REVIEW_ON_SCC.sh is read-only and has no job effect.

This package copies the reviewed inactive runtime v2 helpers unchanged and
archives its original manifest, contract and runtime for provenance. The
release runtime adds a selected-fixture permit requiring a separate reviewed
candidate digest and an explicit decision about the SU balance. A future
selected release must be sealed in a new directory after that decision.

The single candidate allocation is one l40s L40S GPU, omp16/16 CPU slots,
20 one-thread MPI ranks, 00:30:00 hard walltime and no reschedule. The
maximum is 0.5 allocated GPU-hours and 8 requested CPU-slot-hours. Its
fresh job-start checks retain the 1.5-GiB storage stop, 2-GiB cap and
3-GiB free-space floor at both persistent output and scratch locations.
The actual billed SCC SU rate and current balance are unknown and unwaived
for this fixture. Production remains unauthorized.
