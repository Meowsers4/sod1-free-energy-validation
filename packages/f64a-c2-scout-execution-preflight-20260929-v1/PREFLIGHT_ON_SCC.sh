#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
bash REVIEW_PACKAGE.sh
printf 'preflight_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# A throwaway, inert SGE script is needed by qsub verification mode. The
# exact proposed request is passed on the command line. -w v verifies only;
# it does not create an allocation or a job ID.
probe=$(mktemp /tmp/f64a-c2-scout-queue.XXXXXXXX) || exit 1
trap 'rm -f -- "$probe"' EXIT
printf '#!/bin/bash\nexit 0\n' > "$probe"
queue_output=$(qsub -clear -hard -P rise-batteries -q l40s -pe omp16 16 \
  -l gpus=1,gpu_type=L40S,h_rt=02:00:00 -r n -N c2-scout-preflight \
  -S /bin/bash -cwd -j y -w v "$probe" 2>&1) || {
    printf '%s\n' "$queue_output"
    exit 1
  }
printf '%s\n' "$queue_output"
grep -Fq 'verification: found suitable queue(s)' <<< "$queue_output"
echo 'queue_validation=pass; request=one_L40S_omp16_16_slots_02:00:00; no_job_submitted'

echo 'project_quota:'
pquota rise-batteries
echo 'project_filesystems:'
df -h /project/rise-batteries /projectnb/rise-batteries
if test -w /project/rise-batteries; then
  echo 'project_writable=yes'
else
  echo 'project_writable=no'
  exit 1
fi

echo 'project_SU_balance_query:'
acctool -project rise-batteries -detail -1 -balance 09/01/26 yesterday
echo 'C2_SCOUT_EXECUTION_PREFLIGHT_QUERY_COMPLETE; no job submitted'
