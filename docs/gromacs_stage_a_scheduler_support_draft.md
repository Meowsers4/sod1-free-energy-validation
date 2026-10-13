# Scheduler support draft — not sent

To: help@scc.bu.edu
Subject: Job 7758910 remains queued on l40s; validation reports zero omp slots

Latest follow-up: validation with one L40S GPU and the same `omp 4`, project,
queue, walltime and soft preference reports `found suitable queue(s)`. Four GPUs
with four slots did not. A one-GPU/four-replica MPI design is therefore being
considered. Does SCC support per-job NVIDIA MPS on an assigned L40S GPU, and what
launch/cleanup procedure should be used? Earlier compute-mode evidence was
Exclusive_Process. We have not started MPS or changed GPU compute mode. One GPU
would need four simultaneous MPI processes to retain replica exchange.

Hello RCS,

Could you inspect why my job 7758910 (user bodeb, project rise-batteries) remains
queued? It requests four L40S GPUs on one host, `-pe omp 4`, and `h_rt=600`, with
hard queue `l40s`. `qstat -j` confirms these settings and the correct project;
it also shows the soft preference `buyin=TRUE`. This is a bounded synthetic
GROMACS container smoke test, and it has not started according to the supplied
queue output.

An earlier request, 7726162 with mpi32/32 slots, waited from September 24 and was
deleted while held pending before this replacement was submitted September 27
at 15:15:19 (scheduler-displayed time). Reducing the CPU request did not resolve
the wait. Both packages request four GPUs; no additional executed attempt is intended.

The September 27 `qstat -f -explain a -q l40s` output showed blank state flags
for all ten instances and zero used CPU slots on scc-501, 504, 505, 512 and 513.
Earlier GPU snapshots also showed whole idle L40S hosts. The queue lists omp
and mpi32; `qconf -sp omp` reports 99999 slots, `$pe_slots`, and no user ACL.
The supplied qquota output did not identify a user/project limit explaining it.

Both `qalter -w p 7758910` and `qalter -w v 7758910` end with:

    Job 7758910 cannot run in PE "omp" because it only offers 0 slots
    verification: no suitable queues

A validation-only trial `qalter -w v -hard -q '*' 7758910` also failed. Notably,
it prints `(no project)` for project-restricted queues, whereas `qstat -j`
immediately afterward still shows `project: rise-batteries` and `hard_queue_list:
l40s`. I have not applied that trial queue change. Scheduling explanations are
disabled. Could you check the actual dispatch restriction for this job and
whether the qalter validation is evaluating its full project/resource context?

Please advise the appropriate single-host GPU/PE request if a configuration
change is needed. Please do not start extra jobs or change the running program;
the existing request has a four-GPU/ten-minute bound.

A fresh, explicitly specified validation also failed:

```bash
qsub -clear -w v -P rise-batteries -hard -q l40s -pe omp 4 \
  -l gpus=4,gpu_type=L40S,h_rt=00:10:00 \
  -soft -l buyin=TRUE -hard -r n -cwd stage_A.sge
```

It printed `Job 7761829 cannot run in PE "omp" because it only offers 0 slots`,
`verification: no suitable queues`, and `Exiting.` This was validation mode,
not a second submitted job. Actual submitted job remains 7758910.

Thank you,
Bode

## Evidence retained locally

- `0fa45a30-60c1-457a-ae22-e7fd49ea955d/Pasted text.txt`: PE, queue states, quotas.
- `7f78e625-5ec0-46a8-954f-794edd3884ac/Pasted text.txt`: both validation modes,
  all-queue validation trial, and actual job details.
- User subsequently supplied the failed fresh `qsub -clear -w v` result quoted
  above, with explicit project and all resource constraints.

This draft is not sent and does not authorize contacting RCS on the user's behalf.
