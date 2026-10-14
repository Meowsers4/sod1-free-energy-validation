#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONDONTWRITEBYTECODE=1
python builder.py permit --package "$PWD"
mkdir submission
request=(-clear -hard -P rise-batteries -pe omp 8 -l h_rt=01:00:00
         -r n -N c2-r3-cpu-system -S /bin/bash -cwd -j y
         -o "$PWD/submission/job.log")
qsub "${request[@]}" -w v cpu-system.sge > submission/validation.log 2>&1
cat submission/validation.log
grep -Fq 'verification: found suitable queue(s)' submission/validation.log
qsub "${request[@]}" -terse cpu-system.sge > submission/qsub.log 2>&1
cat submission/qsub.log
printf '%s\n' 'One bounded CPU system rehearsal submitted; retain this job ID.'
