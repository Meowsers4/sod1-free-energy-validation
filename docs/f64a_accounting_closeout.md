# F64A v2 accounting closeout — pending SCC evidence

The registered requirement for a confirmed applicable SU/core-hour rate was waived
by explicit user direction before v2 GPU submission. 1 SU/core-hour is an assumption,
not a verified L40S tariff; 1040 SU is conditional. Approved limits were 130 total
GPU-hours and at most two attempts/task. Do not rewrite the preregistration or
infer actual billed SU from free energies, `qacct cpu`, or a shared-project balance
difference. Scientific evidence does not constitute billing evidence.

Preserve scheduler accounting promptly, before retention expires. On SCC, from
the repository root, use a **new** directory so existing records are not overwritten:

```bash
mkdir -p logs/f64a_continuation
mkdir logs/f64a_continuation/closeout_2026-09-18 \
&& qacct -j 7619903 > logs/f64a_continuation/closeout_2026-09-18/first_light_qacct.txt \
&& qacct -j 7620241 > logs/f64a_continuation/closeout_2026-09-18/production_qacct.txt \
&& acctool -project rise-batteries -detail -1 -balance 09/17/26 yesterday \
  > logs/f64a_continuation/closeout_2026-09-18/project_balance.txt
```

If this directory exists, choose a fresh date/suffix; do not overwrite or delete
earlier evidence. If qacct has no records yet, preserve its error and retry capture
later into a different file. Also retain v2 `admission.json`, first-light/production
submission records, attempt ledgers and logs. No new GPU submission is involved.

Review all attempts, including failures/reschedules; do not silently deduplicate
task IDs or count only successful outputs. GPU walltime is the sum of per-attempt
`ru_wallclock` for one-GPU jobs; requested core-wall hours sum walltime × `slots`.
The `cpu` field measures processor usage, not requested-core-wall billing or SU.
Compare recorded attempts/walltime against admission caps, reporting exceptions.

Actual billed SU requires the applicable billing record/tariff from SCC accounting
or support. A project balance is shared and may include other jobs/users. The
existing detailed `acctool` dump exposed no SU charge/rate field. Until direct
billing evidence is supplied, report measured wall/core-hours separately from
conditional SU calculations and leave **actual billed SU unreviewed**.

No direct authenticated cluster session is available to this local agent. The user
must supply these accounting records; this closeout is not claimed complete.
