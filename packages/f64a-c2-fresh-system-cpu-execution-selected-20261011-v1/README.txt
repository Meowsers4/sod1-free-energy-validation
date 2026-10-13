F64A C2 isolated r3 CPU system-build selected release, 2026-10-11.

The user selected one technical CPU-only rehearsal after the inactive
release passed SCC static review. selection.json pins one job, omp/8,
01:00:00, no GPU resource, no reschedule or automatic retry, and no
production authority. The source candidate and inactive release manifests
are archived in this package and checked by REVIEW_PACKAGE.sh.

First transfer and run REVIEW_PACKAGE.sh and REVIEW_ON_SCC.sh on SCC.
REVIEW_ON_SCC.sh rechecks sources, quota, free space and queue eligibility;
it submits no job. Save its full output to review.log. The submission
guard requires the passing review marker in that file.

After the selected static review passes, run SUBMIT_ON_SCC.sh once to
validate the request and submit one CPU job. The script creates a unique
submission directory before qsub; it refuses an in-place second attempt.
Retain the job ID and output. Do not run qsub directly.

The job writes only in its own package-local prepared.incomplete directory
on /project, then seals and renames it to prepared after the chemistry and
source checks pass. Any failure leaves the incomplete tree and command
logs for diagnosis. REVIEW_PREPARED.sh checks the completed manifest and
system chemistry without submitting another job. No FEP window dynamics,
lambda-aware starts, GPU job, or production inference is authorized.
