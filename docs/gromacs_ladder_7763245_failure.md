# Stage L v2 allocation guard failure — job 7763245

Source: user-pasted qstat and submission-L/job.log in this conversation,
2026-09-28. No remote files independently downloaded. Package:
`gmx-gpu-ladder-20260928-v2-omp16`, manifest
`f49e471b32d222986145fb4665edaa44b464ca3aaad80c97b89b369ee5ccfb07`.

The submitted request was `-pe omp 16`. User qstat reports:

```
submission_time: Mon Sep 28 01:59:47 2026
hard resource_list: gpus=1,h_rt=1200,nvlink=FALSE,gpu_type=L40S
parallel environment: omp16 range: 16
project: rise-batteries
```

Scheduler timezone was not supplied. Runtime reported:

```
"technical_status": "failed",
"stage": "L",
"production_authorized": false,
"job_id": "7763245",
"accounting": "pending_qacct",
"failure": "wrong PE/slots",
"wall_seconds": 2.5483192420215346,
"allocated_gpu_hours_observed": 0.0007078664561170929
```

The failing guard requires PE to equal the contract's literal `omp` and NSLOTS
16; qstat's effective PE is `omp16`. The name mismatch is sufficient to reject
this otherwise intended allocation shape. The original allocation.json and
PE_HOSTFILE should be retained to confirm the runtime environment independently.
The traceback points to validate_allocation before configure_cpu_sharing, scratch
creation, private MPS startup and MPI execution. No GPU dynamics were started.
Wrapper elapsed is not scheduler wallclock or billed SU; qacct remains pending.
This is a failed allocated v2 attempt, not a successful qualification or permission
to clear its guard and rerun it.

Correction: new v3 contract requests and requires `omp16` exactly. Strict checks
for 16 slots and a single local host remain. Reuse all 20 verified v2 TPRs through
hash/fixture-validated import. No scientific input, MPI rank count, CPU-sharing
mode, GPU resource, duration or acceptance criterion changes. No SIF rebuild.
A new candidate is prepared for review; it does not automatically retry v2.

## Follow-up accounting and allocation received — 2026-09-28

User supplied allocation.json: JOB_ID 7763245, PE omp16, NSLOTS 16,
QUEUE l40s, CUDA_VISIBLE_DEVICES 0, SGE_TASK_ID undefined, CUDA_DEVICE_ORDER null.
This directly confirms that the runtime environment PE differed from v2's omp
contract; the slot count was correct. Device index 0 is historical only.

qacct: host scc-502.scc.bu.edu, granted_pe omp16, slots 16, failed 0,
exit_status 1, ru_wallclock 4 seconds. Scheduler timestamps (timezone unspecified):
submitted September 28 01:59:47, started 02:01:34, ended 02:01:38; queue wait 107 s.
failed 0 indicates no scheduler-level failure; exit_status 1 confirms application
failure. It is not a passing simulation. No billed SU was supplied. The job has
ended and its failed allocated attempt/accounting are preserved.

The user also supplied RESOURCE_REQUEST_VALIDATED, EXISTING_TPRS_IMPORTED_AND_VERIFIED
and PACKAGE_AND_PREPARED_INPUTS_VERIFIED for v3. New input preparation is complete
on the reported checks; no grompp or GPU job ran during import. No v3 job ID or
execution result is yet supplied. Agent has not downloaded remote raw inputs.
