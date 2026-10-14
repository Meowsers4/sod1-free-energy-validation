#!/bin/bash
set -eo pipefail
cd -- "$(dirname -- "$0")"
package_dir=$PWD
export PYTHONDONTWRITEBYTECODE=1
python builder.py verify-package --package "$package_dir"
cd /projectnb/rise-batteries/bode/rise-project
source scripts/scc_env.sh
cd "$package_dir"
python builder.py preflight --package "$package_dir"
python builder.py review-saved-warning --package "$package_dir"
pquota rise-batteries
df -h /project/rise-batteries
qsub -clear -hard -P rise-batteries -pe omp 8 -l h_rt=01:00:00 \
  -r n -N c2-r3-cpu-system -S /bin/bash -cwd -j y \
  -w v cpu-system.sge
printf '%s\n' 'C2_R3_CPU_SYSTEM_ION_WARNING_SELECTED_REVIEW_PASS execution_authorized=True; no job submitted'
