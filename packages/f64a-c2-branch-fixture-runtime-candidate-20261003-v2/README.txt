F64A C2 live no-exchange common checkpoint branch: inactive runtime candidate v2.

The sealed contract has execution_authorized=false. There is no SGE job file,
submission command or selected-release script in this package. A direct
runtime.py job/rank/probe request stops at the authorization guard before
creating an attempt or touching the GPU. This candidate is for code and SCC
source review, not execution.

This revision narrows core_runtime.py and smoke_runtime.py to the helpers
called by this fixture. It removes the older callable preparation/job
routines copied into v1. The reviewed v1 package must be preserved as
historical evidence; this v2 package has a new manifest and needs its own
static review on SCC.

REVIEW_PACKAGE.sh verifies all package files. REVIEW_ON_SCC.sh also verifies
the accepted preflight.json, all 344 original prepared-source files, per-state
TPRs, MDPs, source atom order and the exact r6 SIF. It never submits a job.

A future separately sealed selected release would run one no-exchange common
phase to step 1100, seal all 20 checkpoints, preprocess and review 40 branch
TPRs from copied checkpoints, and then run baseline and HREX sequentially in
separate output trees. It would validate per-phase GPU/MPS, checkpoint,
energy, trajectory and exchange evidence. Local helper and guard checks
pass. SCC static review, actual dynamics, cost/SU decision and selection
remain separate.
