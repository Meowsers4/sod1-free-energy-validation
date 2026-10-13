# One-GPU MPS sharing result — 2026-09-27

The user supplied the following completion marker and `attempt/result.json`
from package `gmx-mps-probe-20260927-v1`, with shell prompt on `scc-505`:

```text
FOUR_CUDA_CLIENTS_SHARED_ONE_GPU; MPS_CLEANUP_CONFIRMED
```

```json
{
  "sharing_passed": true,
  "cleanup_confirmed": true,
  "gpu_uuid": "GPU-7ab63c30-8edc-e49c-e306-922c040486e6",
  "mpi_tested": false,
  "dynamics_tested": false
}
```

This is user-supplied SCC evidence, not an independently downloaded artifact.
The full log, overlap record, client logs, allocation ID and accounting have not
been retrieved. The package's pass condition requires four simultaneous CUDA
clients inside the pinned r6 SIF, verified device-memory operations, matching
client PIDs attached to one private MPS server, successful client exits and
confirmed MPS shutdown. That condition passed according to the supplied output.

The observation establishes functional sharing in this allocation. It does not
test GROMACS dynamics, MPI communication, replica exchange, performance, or a
different node/allocation; it does not explain the four-GPU queue restriction.
The next execution milestone is a separately packaged bounded synthetic test
with four MPI ranks sharing one allocated L40S through private MPS. The existing
four-GPU package cannot simply be submitted requesting one GPU. No new smoke
package was submitted, and job 7758910 was not changed by recording this result.

Release the completed interactive allocation with `exit`; retain the probe
package's `probe.log`, `attempt/` and recorded scratch path. No rerun is needed
for the sharing question on current evidence.
