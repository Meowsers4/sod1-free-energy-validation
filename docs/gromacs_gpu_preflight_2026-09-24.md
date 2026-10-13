# GPU smoke preflight — 2026-09-24 17:58 UTC

User-supplied SCC output, reviewed locally. This was a read-only scheduler/storage
query and wrapper preview on `scc-i01`, not a GPU allocation or simulation.

SCC log:
`/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gpu-preflight.tZDtopSs.log`.
Supplied attachment: `cdd5cd14-164f-49b3-a766-cd150a1cd450/Pasted text.txt`;
attachment SHA-256:
`6fe91f98bc1e2cb52088033d517cfd8c5b2a5f69c146806c8a461bd9873f66d4`.
This digest identifies the pasted text, not an independently downloaded SCC log.

## Findings

| Check | Evidence | Interpretation |
| --- | --- | --- |
| Existing SIF | Listed at the verified r6 path, 2.1G | Present; this listing does not repeat the earlier checksum validation |
| PE | `mpi32`, `allocation_rule 32`, `control_slaves TRUE`, `job_is_first_task FALSE`, `accounting_summary FALSE` | Supports the proposed 32-slot request; preserve PE integration/accounting details when preparing the launcher |
| Queue | `l40s`, 32 slots/host, `mpi32` in `pe_list`, ten listed hosts, 48-hour maximum | Proposed 10/20-minute requests fit the reported queue configuration; actual placement and admission still require runtime checks |
| GPU resource | `gpus`: requestable, `JOB` consumable; `gpu_type` requestable | Four GPUs must be explicitly requested; this is not proof of available devices or uncontested CUDA contexts |
| Project quota | `/projectnb/rise-batteries`: 42.97 / 50 GB, 434105 / 1638400 files | About 7.03 GB of reported quota headroom, sufficient for the proposed 2 GiB file budget and 4 GiB admission threshold at this snapshot |
| Scratch | `scc-i01` `/scratch`: 1.3T available | Build-host scratch only; compute-node scratch must be checked in the job |
| Allocation balance | `acctool: command not found` | Not measured; do not reuse the old September balance as current |
| Wrapper preview | `/usr/bin/singularity exec -e`, project/scratch binds, no `/usr/local` bind, explicit image/executable paths | `--nolocal` preview completed and preserved the intended executable argument |

The wrapper reported `preview mode - command not executed`. Its preview on this
host did not include `--nv`. GPU-host driver injection, CUDA-visible device UUIDs,
rank mapping and sharing therefore remain untested; absence of `--nv` here does
not establish failure of the GPU-host wrapper path. Likewise, the preview does
not establish how all necessary environment variables will reach MPI ranks.

`df` reported 13G filesystem availability for `/projectnb`; admission should use
the more restrictive project quota headroom, not that number alone. Both quota
and actual compute-node free space must be checked again at execution time.

## Next preparation

The [bounded smoke plan](gromacs_gpu_smoke_plan.md) remains a draft. No rebuild or
repeat of these successful configuration queries is needed to continue package
preparation. Remaining work is the concrete synthetic fixture, hashed inputs,
container-local rank/device launcher and evidence validation, plus obtaining a
current allocation balance through an available SCC accounting interface.
Stage B additionally requires a supported sharing method. Neither stage has
been submitted or made eligible for submission by this evidence.
