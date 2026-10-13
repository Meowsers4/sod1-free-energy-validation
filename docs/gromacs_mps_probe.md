# One-GPU MPS sharing diagnostic

Prepared 2026-09-27 following the user's request to check sharing without email.
The user reports one assigned L40S in Exclusive_Process mode and the MPS control
binary installed. This is metadata, not a successful sharing test or a BU policy
statement. The probe uses one allocated L40S, omp/four slots, and a five-minute
hard limit (at most 1/12 allocated GPU-hour). One attempt, no automatic retry.
No GROMACS dynamics or MPI exchange is run; the existing job 7758910 is unchanged.

The probe verifies the r6 image checksum, stops if the assigned GPU is busy or an
MPS service is already visible on the node, and starts an unprivileged private
MPS daemon restricted to the scheduler-assigned GPU UUID. It does not change
compute mode. Four processes inside the exact SIF each create a CUDA context,
write/read 4096 bytes on the device, synchronize, and hold their contexts open.
All four PIDs must appear together in this private MPS server's client list.
Clients exit before that service is stopped. Private scratch and evidence are
retained. CUDA operations have no injected faults or long-running kernels.
An unexpected driver hang may prevent cleanup; a cleanup failure is not a pass
and must be reviewed before further attempts. No global service is controlled.

NVIDIA documents UUID selection for both server and client (avoids ordinal
remapping), private pipe directories, and the control commands used here:

- https://docs.nvidia.com/deploy/topics/topic_5_2_1.html
- https://docs.nvidia.com/deploy/mps/appendix-tools-and-interface-reference.html
- https://docs.nvidia.com/deploy/mps/appendix-common-tasks.html

The runtime deliberately uses Python 3.6-compatible stdlib for Rocky 8 and the
container's `/usr/libexec/platform-python`. Local tests cover the orchestration
with simulated commands; actual GPU/MPS behavior remains untested until SCC runs.

## Transfer and run

From the laptop, in the repository:

```bash
scp -r results/gpu_sharing_probe_packages/gmx-mps-probe-20260927-v1 \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

On SCC, from a login terminal (exit the old two-minute metadata allocation first):

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-mps-probe-20260927-v1
sha256sum -c SHA256SUMS
qrsh -now y -P rise-batteries -q l40s -pe omp 4 \
  -l gpus=1,gpu_type=L40S,h_rt=00:05:00
```

If a compute shell opens, run:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-mps-probe-20260927-v1
bash RUN_ON_COMPUTE.sh > probe.log 2>&1
cat probe.log
cat attempt/result.json
```

Success ends with `FOUR_CUDA_CLIENTS_SHARED_ONE_GPU; MPS_CLEANUP_CONFIRMED`.
Then `exit` releases the allocation. If qrsh cannot place the request immediately,
no check ran. If it fails, retain `probe.log`, `attempt/`, and printed scratch;
do not delete the attempt guard or retry automatically. A cleanup failure needs
inspection in the same allocation. Share the result and the client logs on failure.

A pass establishes simultaneous CUDA context/memory operations through MPS
inside r6. It does not establish MPI/HREX execution, numerical correctness,
performance, production readiness, or site-wide permission. A one-GPU/four-rank
GROMACS smoke package still requires its own mapping and execution validation.
