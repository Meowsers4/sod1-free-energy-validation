# Complete SIF milestone — verified 2026-09-24

Status: complete for image creation, identity, CPU/MPI startup and the reported
linked-library checks. GPU/HREX qualification and production authorization remain
false. Evidence below was supplied by the user from SCC; the agent has not
downloaded or independently hashed the remote SIF.

## Artifact

- Package: `gmx-hrex-20260924-r6`.
- SCC host: `scc-i01`.
- Build directory: `/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj`.
- SIF: `/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gromacs-2025.3-mpi-cuda-l40s.sif`.
- SIF SHA-256: `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
- Packaged definition SHA-256: `932efb5d1c9954ee859ac940ed72d6eb79e87cd4430251d9c5ffe51ff676f7ce`.
- Verification log: `/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/final-verification.fEYjP0D0.log`.
- Launch log: `/projectnb/rise-batteries/bode/container-build-packages/gmx-hrex-20260924-r6/launch.l7pEOpGW.log`.

## Evidence and limits

The full r6 build reported `Build/identity exit status: 0`, reached the installed
GROMACS 2025.3 / OpenMPI 4.1.5 / CUDA 12.8 identity output, and preserved the hashed
complete-install archive. Its definition runs the GROMACS test target, checks
installed data and PMIx help files, and performs singleton and two-rank MPI startup;
the launcher repeats the image self-test as the ordinary user. These version
commands do not run a protein simulation or test GPU execution.

The original final dependency-report command failed despite the overall zero
status. That report and its completion marker alone are insufficient evidence.
A subsequent direct `singularity exec --cleanenv IMAGE ldd BINARY` check resolved
all listed dependencies for both `gmx_mpi` and `libmpi.so`. The supplied final
verification output reports the SIF checksum `OK`, the exact hash above, and
`SIF_HASH_AND_DEPENDENCIES_VERIFIED`. This closes the reporting issue without
rebuilding or modifying the SIF. Optional dynamically loaded GPU driver libraries
are not established by these ELF dependency checks.

Preserve the SIF, `SIF.sha256`, `build.log`, `identity.log`, the corrected verification
log, `source/`, and `installed-toolchain.tar.gz` with `installed-toolchain.sha256` in
the build directory. The archive checksum passed during preservation; its digest
has not been supplied in this conversation. Earlier logs and packages stay intact.

## Next milestone

Prepare a bounded, separately authorized single-node GPU qualification. Remaining
checks include scheduler-assigned driver/device visibility, the intended rank/GPU
sharing arrangement, 20-rank placement, exchange, restart, and resource accounting.
The user requested planning on September 24; the
[bounded smoke-test draft](gromacs_gpu_smoke_plan.md) now scopes two synthetic jobs
and records the unresolved admission checks. It does not authorize execution.
No further build or CPU startup rerun is needed on the evidence currently available.
Do not use the incomplete earlier recovery rootfs for scientific work.

The pinned container YAML describes the build candidate and remains unchanged;
this record carries the actual r6 artifact identity and reported execution evidence.
