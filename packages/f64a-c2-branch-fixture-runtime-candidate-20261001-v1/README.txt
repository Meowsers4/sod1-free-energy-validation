F64A C2 live no-exchange common checkpoint branch: inactive runtime candidate.

The sealed contract has execution_authorized=false. There is no SGE job file,
submission command or selected-release script in this package. A direct
runtime.py job/rank/probe request stops at the authorization guard before
creating an attempt or touching the GPU. This candidate is for code and SCC
source review, not execution.

REVIEW_PACKAGE.sh verifies all package files. REVIEW_ON_SCC.sh also verifies
the accepted preflight.json, all 344 original prepared-source files, per-state
TPRs, MDPs, source atom order and the exact r6 SIF. It never submits a job.

A future separately sealed selected release would run one no-exchange common
phase to step 1100, seal all 20 checkpoints, preprocess and review 40 branch
TPRs from copied checkpoints, and then run baseline and HREX sequentially in
separate output trees. It would validate per-phase GPU/MPS, checkpoint,
energy, trajectory and exchange evidence. This code is a candidate pending
local tests, SCC review, explicit cost/SU decision and selection.
