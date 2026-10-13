# Stage A SCC input preparation completed — 2026-09-24

The user supplied `INPUTS_PREPARED` and the contents of `prepared/PREPARED.json`
for `gmx-gpu-stage-a-20260924-v2`. This is reported SCC evidence, not an independent
download/hash of remote files by the agent. The local package manifest was
independently verified and matches the supplied manifest identity.

Prepared record:
`/projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-stage-a-20260924-v2/prepared/PREPARED.json`.

- Package manifest SHA-256: `59fc0d8e1e5a0e881f6f73d1060646ac5a2b568fd31cd6b6b81555a284c678c9`.
- SIF SHA-256: `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
- Reported `gpu_executed`: `false`.
- All four processed topology hashes match:
  `eb910cdb7c2ba0dfc13a39531ad49117412cc56ee0003ad4cc33abea2d2ef670`.

| State | Source lambda index | Lambda | Reported TPR SHA-256 |
| --- | --- | --- | --- |
| state00 | 0 | 0 | `5cce804cec2e3e40d20e83a9e614a8eb8964689cc22a0ce2f9f18d12268445a8` |
| state01 | 6 | 0.3529 | `d28739d7d2a587fc2081edee88eaa3f1087eccc8184b1c45c5c1f858893758b0` |
| state02 | 13 | 0.7647 | `33a763564d63953bd70b79840a31ea0bf99f86957e62d766c83584e40804b208` |
| state03 | 19 | 1 | `7aca4b8e778a820414bee2beb056e658c63d9c15b95cdc74377ff4b226979da9` |

The reviewed v2 program emits this completion marker only after verifying the
SIF, the container Python/private tmp read-write round-trip, successful warning-free
preparation of each state and the inspected TPR state indices, lambda arrays,
atom counts and step counts. The supplied record seals those logs and TPR dumps.
The full logs/dumps were not separately inspected in this turn. This closes the
CPU preparation milestone, including the earlier contained-tmp mount problem.
No rebuild or repeat of preparation is indicated by this output.

## Stage A authorization and submission status

The reviewed `stage_A.sge` in this exact package requests one `l40s` host using
`mpi32` with 32 CPU slots, four L40S GPUs, four container-local MPI ranks and a
ten-minute hard walltime limit. Its maximum reservation is 2/3 GPU-hour and
16/3 CPU-slot-hours. It runs only this synthetic four-state fixture, with no
automatic retry, reschedule, Stage B or MPS server. The internal work deadline is
seven minutes; remaining time is reserved for evidence collection.

The user explicitly authorized this single Stage A attempt on 2026-09-24 after
reviewing these resource bounds and the unverified current SU balance. The user
said: "yes I authorize it". The resource cap does not establish billed SU, and
the older balance is not treated as current. No further authorization is needed
for this exact attempt. Stage B, retries and protein work remain unauthorized.

The agent's noninteractive SSH connection reached SCC but was rejected with
`Permission denied (publickey,keyboard-interactive,hostbased)`. No job was submitted
by the agent. Submission must be made through the user's authenticated terminal.
Recheck the immutable prepared package, require no prior `attempt/`, and atomically
create a `submission-A/` guard before qsub. Preserve that directory on an ambiguous
submission error; inspect qstat/logs instead of resubmitting.
GPU driver/device/rank mapping and actual placement/quota checks run inside the
allocation before dynamics; they are not prerequisites to repeat CPU preparation.

Preserve both package versions, the exact prepared files and all original logs.
The submission decision concerns Stage A only. Stage B and protein work remain
outside this prepared execution scope.
