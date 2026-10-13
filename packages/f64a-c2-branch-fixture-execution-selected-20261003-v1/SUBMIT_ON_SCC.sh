#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONDONTWRITEBYTECODE=1
/usr/libexec/platform-python runtime.py permit
test ! -e attempt
mkdir submission
request=(-clear -hard -P rise-batteries -q l40s -pe omp16 16
         -l gpus=1,gpu_type=L40S,h_rt=00:30:00 -r n -N c2-branch-fixture
         -S /bin/bash -cwd -j y -o "$PWD/submission/job.log")
qsub "${request[@]}" -w v fixture.sge > submission/validation.log 2>&1
cat submission/validation.log
grep -Fq 'verification: found suitable queue(s)' submission/validation.log
qsub "${request[@]}" -terse fixture.sge > submission/qsub.log 2>&1
cat submission/qsub.log
echo 'One bounded live branch technical fixture submitted; retain this job ID.'
