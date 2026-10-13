#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
bash REVIEW_ON_SCC.sh
/usr/libexec/platform-python runtime.py permit baseline
test ! -e attempts/baseline
mkdir submission-baseline
request=(-clear -hard -P rise-batteries -q l40s -pe omp16 16
         -l gpus=1,gpu_type=L40S,h_rt=02:00:00 -r n -N c2-scout-baseline
         -S /bin/bash -cwd -j y -o "$PWD/submission-baseline/job.log")
qsub "${request[@]}" -w v baseline.sge > submission-baseline/validation.log 2>&1
cat submission-baseline/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-baseline/validation.log
qsub "${request[@]}" -terse baseline.sge > submission-baseline/qsub.log 2>&1
cat submission-baseline/qsub.log
echo 'One bounded baseline technical scout submitted; retain this job ID.'
