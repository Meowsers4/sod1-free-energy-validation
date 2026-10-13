#!/bin/bash
# SCC only. One guarded replacement of the still-unexecuted four-GPU attempt.
set -euo pipefail
trap 'echo "Stopped. Retain submission-A and return this output; do not rerun." >&2' ERR
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
bash REVIEW_ON_SCC.sh
test ! -e attempt

# Read identities from the sealed contract rather than guessing which job to delete.
IFS=$'\t' read -r old_job old_package job_owner < <(/usr/libexec/platform-python - <<'PY'
import json
c = json.load(open('contract.json'))
assert c['sharing']['mode'] == 'private_MPS'
assert c['scheduler']['gpus'] == 1
print('\t'.join([c['replacement']['old_job_id'], c['prepared_source']['path'], c['replacement']['owner']]))
PY
)
test -n "$old_job" && test -n "$old_package" && test -n "$job_owner"
test "$(id -un)" = "$job_owner"
test ! -e "$old_package/attempt"
mkdir submission-A

# All resources explicit: do not inherit a different GPU/CPU request from defaults.
request=(-clear -hard -P rise-batteries -q l40s -pe omp 4
         -l gpus=1,gpu_type=L40S,h_rt=00:10:00 -r n -N gmx-smoke-A-MPS
         -S /bin/bash -cwd -j y -o "$PWD/submission-A/job.log")
qsub "${request[@]}" -w v stage_A.sge > submission-A/validation.log 2>&1
cat submission-A/validation.log
grep -Fq 'verification: found suitable queue(s)' submission-A/validation.log
qstat -u "$job_owner" > submission-A/before.txt
test "$(awk -v j="$old_job" '$1 == j {print $5}' submission-A/before.txt)" = qw
qstat -j "$old_job" > submission-A/old-job.txt
/usr/libexec/platform-python - "$old_package" "$job_owner" <<'PY'
import sys
fields = {}
for line in open('submission-A/old-job.txt'):
    if ':' in line:
        k, v = line.split(':', 1)
        fields[k.strip()] = v.strip()
assert fields.get('owner') == sys.argv[2], 'Unexpected old job owner'
assert fields.get('cwd') == sys.argv[1], 'Unexpected old package directory'
assert fields.get('script_file') == 'stage_A.sge', 'Unexpected old job script'
PY
qhold "$old_job" > submission-A/hold.log 2>&1
qstat -u "$job_owner" > submission-A/held.txt
test "$(awk -v j="$old_job" '$1 == j {print $5}' submission-A/held.txt)" = hqw
test ! -e "$old_package/attempt"
qdel "$old_job" > submission-A/delete.log 2>&1
for check in {1..10}; do
    qstat -u "$job_owner" > submission-A/after-delete.txt
    old_state=$(awk -v j="$old_job" '$1 == j {print $5}' submission-A/after-delete.txt)
    [ -n "$old_state" ] || break
    sleep 1
done
test -z "$old_state"
test ! -e "$old_package/attempt"
test ! -e attempt
qsub "${request[@]}" -terse stage_A.sge > submission-A/qsub.log 2>&1
cat submission-A/qsub.log
echo 'One-GPU replacement submitted. Preserve the new job ID and logs.'
