F64A C2 isolated r3 CPU system-build explicit-login candidate, 2026-10-12.
This package is INACTIVE: execution_authorized=false.

Selected job 8032575 failed before system construction when MODULEPATH and
conda were unavailable in its batch shell. A first inactive correction
added #!/bin/bash -l and passed user-run SCC static review. That script
also used SGE -S /bin/bash; depending on SGE shell_start_mode, the shebang
may not control how the job script is interpreted. The login environment
therefore remains unverified. Preserve both earlier packages and logs.

This candidate makes the startup explicit: the SGE-interpreted script
execs /bin/bash -l on a separate sealed body script. The body checks it
is running in a login shell, then checks MODULEPATH, sod1-fep, Python
3.11+, pmx and yaml before calling the unchanged builder. The pinned
source, seed, CPU request (eight slots, one hour) and no-GPU scope are
unchanged. The package archives manifests for the source candidate,
inactive release, failed selected package and first login candidate.

REVIEW_PACKAGE.sh and REVIEW_ON_SCC.sh are read-only static checks. They
do not prove compute-node startup. The builder and submission guard reject
execution while this package is inactive. A fresh selected package and
separate one-attempt decision are required for any scheduled work. No
automatic retry, FEP windows, GPU job or production inference is authorized.
