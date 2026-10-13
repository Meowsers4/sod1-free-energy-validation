#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONDONTWRITEBYTECODE=1
bash REVIEW_ON_SCC.sh
/usr/libexec/platform-python runtime.py permit hrex
test ! -e attempts/hrex
mkdir submission-hrex
request=(-clear -hard -P rise-batteries -q l40s -pe omp16 16
         -l gpus=1,gpu_type=L40S,h_rt=02:00:00 -r n -N c2-scout-hrex
         -S /bin/bash -cwd -j y -o "$PWD/submission-hrex/job.log")
qsub "${request[@]}" -w v hrex.sge > submission-hrex/validation.log 2>&1
cat submission-hrex/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-hrex/validation.log
qsub "${request[@]}" -terse hrex.sge > submission-hrex/qsub.log 2>&1
cat submission-hrex/qsub.log
echo 'One bounded hrex technical scout submitted; retain this job ID.'
