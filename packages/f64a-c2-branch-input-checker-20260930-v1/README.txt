F64A C2 shared-checkpoint branch: CPU input checker v1

This package is read-only. It contains no grompp invocation, mdrun,
Singularity invocation, scheduler script, or job-submission command.
It cannot prepare or authorize production inputs. Do not run it yet:
the selected common no-exchange preparation checkpoints do not exist.

After a separately reviewed CPU preparation has saved its 20 checkpoint
copies, GROMACS checkpoint/TPR dumps, effective MDPs, and grompp records,
run REVIEW_PACKAGE.sh and REVIEW_INPUTS.sh ROOT PLAN. The latter prints
one pass marker only if all 40 arm inputs meet the plan. A pass covers
file-level branch-input consistency, not live restart or scientific
adequacy. The bounded fan-out runtime fixture remains separate.

See docs/f64a_c2_branch_input_checker.md in the repository for the
JSON plan schema and exact artifact layout.
