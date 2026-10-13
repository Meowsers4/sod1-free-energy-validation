# GPU access snapshot — 2026-09-14

Source: user-pasted output from `qgpus -v`, `qstat`, `qconf`, `acctool -help`, and
`pquota`. This is a point-in-time planning record, not a scheduler entitlement.

## Compatible GPU capacity

The current pipeline pins `gpu_type=L40S` because the GROMACS 2025.3/CUDA 12.8 build is
known to run there and fails deterministically on the compute-12.0 RTX PRO 6000 nodes.

- SCC-wide L40S inventory: 118 GPUs, 94 in use, 21 reported available in the pasted
  snapshot. The three counts do not sum exactly in `qgpus`, so treat them as scheduler
  status fields rather than an accounting identity.
- Nodes carrying the shared `l40s` queue: ten nodes (`scc-501` through `scc-506` and
  `scc-510` through `scc-513`), 40 GPUs total.
- Immediately free on those ten nodes in the snapshot: nine GPUs, before fair-share,
  CPU-slot, project, and scheduler-placement constraints.
- User queue at the snapshot: empty (`qstat -u "$USER"` returned no jobs).
- Project object exists and grants the `rise-batteries` ACL.

Use **eight simultaneous one-GPU tasks** as a conservative planning value until an actual
array demonstrates otherwise. Forty is a physical shared-queue ceiling, not a guaranteed
per-user concurrency allocation. The array may start fewer tasks under fair share.

## Wall time and allocation

The production helper currently requests 12 hours per task. The pasted output does not test
a 24-hour request. Individual FEP windows are expected to remain well below either limit.

The user then ran the allocation query. September usage through 2026-09-13 was 1,642.76
CPU-hours across 990 jobs (1,341.60 shared, 301.14 `czcb_buyin`, and 0.02
`apolkovnikov`). The reported `rise-batteries` balance was **15,987.0494 SU**.

Reproduction command:

```bash
acctool -project rise-batteries -detail -1 -balance 09/01/26 yesterday
```

GPU use is currently charged through requested CPU time. With the pipeline's eight CPU cores
per one-GPU task, multiply occupied GPU-hours by approximately eight before applying the node's
SU rate.

The selected pilot continues the exact retained paths by 6 ns rather than launching fresh
9 ns runs. Its 60 windows are approximately 36 GPU-hours from the historical timing, or
roughly 288 SU at a 1.0 node rate. That is about 1.8% of the reported balance. At eight
simultaneous tasks its ideal occupied wall time is about 4.5 hours; queueing, first light,
retries, and imbalance add overhead. See `pilots/f64a_sampling_extension_v1/`.

## Storage constraint

`/projectnb/rise-batteries` uses 38.16 of its 50 GB soft quota, leaving approximately
11.84 GB. The user accounts for 32.97 GB. A new arm that retains downsampled structural
trajectories must declare a storage budget and archive/cleanup plan before submission.
