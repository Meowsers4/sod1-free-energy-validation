F64A C2 isolated r3 CPU system-build explicit-login selected release,
2026-10-12. The user selected one corrected CPU-only technical attempt
after the inactive explicit-login candidate passed user-run SCC static
review. The earlier selected job 8032575 failed before system construction;
preserve that job, package, log and accounting.

selection.json pins one job, eight CPU slots, a one-hour wall limit,
no GPU, no reschedule, no automatic retry and no production authority.
The source, seed and build code are unchanged. This package archives the
source candidate, inactive release, failed selected, first login candidate
and explicit-login candidate manifests.

The batch wrapper explicitly execs /bin/bash -l on a separate sealed body
script. The body verifies login Bash, MODULEPATH, sod1-fep, Python 3.11+,
pmx and yaml before invoking the system builder. Its success on an SCC
compute node is not established by the prior static review.

First run REVIEW_PACKAGE.sh and REVIEW_ON_SCC.sh. They recheck package and
source identity, project storage and scheduler eligibility without
submitting. Save their complete output in review.log. After selected static
review passes, SUBMIT_ON_SCC.sh validates and submits exactly one attempt.
Its guard requires the passing review marker and rejects any existing
submission or output tree. Do not call qsub directly or clear the guard.

Retain the job ID, job log, any incomplete tree and qacct. If the build
finishes, REVIEW_PREPARED.sh must validate the sealed system before any
technical acceptance. FEP window dynamics, lambda-aware starts, GPU work
and production inference remain outside this selection.
