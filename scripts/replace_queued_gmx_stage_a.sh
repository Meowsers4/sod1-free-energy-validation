#!/bin/bash
# Run on SCC only, after v3-omp4 preparation. Never retries a submission.
set -euo pipefail
trap 'echo "Stopped. Return this output; do not rerun or remove submission-A." >&2' ERR

packages=/projectnb/rise-batteries/bode/container-build-packages
cd "$packages/gmx-gpu-stage-a-20260927-v3-omp4"
printf '%s  SHA256SUMS\n' ead0eac31e97a63f96484fb3da87ae24d50618090887fba65f251f3ca87632ef | sha256sum -c -
bash REVIEW_ON_SCC.sh
test ! -e attempt
test ! -e "$packages/gmx-gpu-stage-a-20260924-v2/attempt"
mkdir submission-A

qstat -u bodeb > submission-A/before.txt
old_state=$(awk '$1 == 7726162 {print $5}' submission-A/before.txt)
test "$old_state" = qw
qhold 7726162 2>&1 | tee submission-A/hold.log
qstat -u bodeb > submission-A/held.txt
old_state=$(awk '$1 == 7726162 {print $5}' submission-A/held.txt)
test "$old_state" = hqw
test ! -e "$packages/gmx-gpu-stage-a-20260924-v2/attempt"
qdel 7726162 2>&1 | tee submission-A/delete.log

for check in {1..10}; do
    qstat -u bodeb > submission-A/after-delete.txt
    old_state=$(awk '$1 == 7726162 {print $5}' submission-A/after-delete.txt)
    [ -n "$old_state" ] || break
    sleep 1
done
test -z "$old_state"
test ! -e "$packages/gmx-gpu-stage-a-20260924-v2/attempt"
test ! -e attempt
qsub -terse -o "$PWD/submission-A/job.log" stage_A.sge 2>&1 | tee submission-A/qsub.log
echo 'Replacement submitted. Return the new job ID above.'
