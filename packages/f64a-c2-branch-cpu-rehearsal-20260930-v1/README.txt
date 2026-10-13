F64A C2 branch CPU rehearsal from accepted Stage P checkpoints.

No mdrun, GPU passthrough, MPI launch, scheduler command, job submission,
or production authorization is present. Stage P had exchange, so this
rehearsal checks continuation preprocessing and the checker format only.
The 1000/500 retained steps are technical probes, not C2 run targets.

REVIEW_PACKAGE.sh verifies all transferred files.
PREPARE_ON_SCC.sh checks accepted Stage P saved file hashes and the r6
image, then creates a new prepared/ tree. It invokes only gmx_mpi dump
and gmx_mpi grompp through CPU-only Singularity. If it fails, preserve
the partial prepared/ tree and logs; do not rerun in place.
REVIEW_PREPARED.sh verifies the resulting manifest and the 20-state
paired-input checker. No GPU execution is implied by a pass.
