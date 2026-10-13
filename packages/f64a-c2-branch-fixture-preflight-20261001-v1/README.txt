F64A C2 live checkpoint-branch fixture: non-submitting SCC preflight.

This package checks the original Stage P initial inputs and exact r6 image,
validates the one-L40S/omp16/16-slot/30-minute queue request with qsub -w v,
and checks current /project quota and write access. It does not create new
checkpoints or TPRs, launch MPI/GROMACS dynamics, allocate a GPU, or submit a job.
The qsub validation mode creates no job ID. There is no submission script.

REVIEW_PACKAGE.sh checks the transferred five-file package against SHA256SUMS.
PREFLIGHT_ON_SCC.sh performs the read-only source/resource preflight and saves
preflight.json. Run once and preserve its output and log. The current SU balance
is unknown and has not been waived for this proposed fixture. A successful
preflight still requires a complete runtime release and explicit selection.
