F64A C2 live checkpoint branch fixture: selected one-attempt technical release.

The user selected this one bounded fixture and reported a 15,000-SU project
balance. The agent has not independently checked that balance or the actual
SU charge rate. The selection authorizes one technical job only, subject to
SCC review of this newly sealed package. It does not authorize production,
another attempt, or a longer F64A simulation.

This release archives the reviewed inactive release manifest, README,
contract and runtime, and rechecks the unchanged files against that source.
The exact single-job request is one l40s L40S GPU, omp16/16 CPU slots,
20 one-thread MPI ranks, 00:30:00 hard walltime and no reschedule. The
maximum is 0.5 allocated GPU-hours and 8 requested CPU-slot-hours.

First run REVIEW_PACKAGE.sh and REVIEW_ON_SCC.sh. They are read-only. The
separate SUBMIT_ON_SCC.sh rechecks the selection, source, image, quota and
request, then atomically claims one submission directory, validates the
queue with qsub -w v and submits at most one job. Retain the returned ID.
The job starts with fresh /project and scratch checks, and stops at the
registered time and storage limits. Review all technical output and qacct
after completion before calling the fixture qualified.
