# F64A C2 paired timing scout: guarded GPU runtime candidate

Prepared locally 2026-09-29 after acceptance of the 381-entry CPU input
import. This is a **non-submitting technical candidate**, not a selected GPU
attempt, production protocol, or free-energy result. The agent did not log in
to SCC. The earlier CPU import remains unchanged; no new `grompp` is needed.

## Scope and provenance

The new package under `packages/f64a-c2-scout-gpu-runtime-candidate-20260929-v4`
reads the accepted prepared tree at
`/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-runtime-cpu-20260929-v1/prepared`.
The reviewer rehashes its 381-entry manifest and all 20 common/baseline/HREX
TPR identities, checks the imported provenance record, and rehashes the r6
SIF. The launch uses exactly the accepted F64A folded apo-2SH `r0` starts
and identical per-state TPRs for baseline and HREX. The only simulation
command difference is baseline `-replex 0` versus HREX `-replex 500
-reseed 20260929`.
The 13-entry package `SHA256SUMS` SHA-256 is
`71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df`.

The candidate package has no `qsub`, SGE job script or submission wrapper.
Its sealed contract says `execution_authorized=false`; `job`, `rank` and
`probe` modes reject execution before GPU access or an attempt directory.
No GPU job can be started by its provided review scripts. A selected attempt
would require a **new sealed release** and explicit selection; editing this
package or its guard in place would invalidate its manifest.

## Implemented runtime checks for a future selected release

The runner is coded, but unreachable in this candidate. It requires one SGE
host, `omp16`/16 slots, one assigned L40S, 20 one-thread MPI ranks inside
the exact r6 SIF, a 16-ID CPU affinity mask and 20 concurrent clients on a
job-private MPS service. It records device UUIDs, rank PIDs, command lines,
client overlap and cleanup. The attempt directory is created once per arm;
HREX checks the baseline's technical result and `qacct` review before it can
start. There is no automatic retry or planned checkpoint continuation.

Each arm targets 50,000 steps = 100 ps/state. The proposed scheduler request
is one L40S and 2 hours per arm, at most 4 allocated GPU-hours and 64
CPU-slot-hours across the pair. `mdrun -maxh 1.7` is the normal early stop;
the wrapper's work deadline is 105 minutes, leaving time to validate and
seal evidence. Separate scratch and persistent monitors stop at 768 MiB each,
below the 1-GiB per-location cap. The runner checks fresh `/project` quota
and filesystem free space before starting. A stopped or incomplete arm is
recorded as censored/inconclusive; it cannot supply a matched rate comparison.

On completion, checks require the same 50,000-step/100-ps final checkpoint
and state index in every directory; 101 finite all-state DHDL and EDR records
on the 1-ps grid; and three full-system XTC frames at 0, 50 and 100 ps.
The XTC envelope check verifies step, time, atom count and finite box; exact
r6 `gmx check` must also decompress each trajectory. Final GRO atom order is
compared with the accepted start. Baseline must have no exchange records.
HREX must have all 99 scheduled alternating-neighbor rounds and identical
walker permutations in every rank log. Exchange acceptance is descriptive,
not a pass threshold. The runner retains compact checkpoint metadata and
GROMACS performance, file hashes, byte totals by extension and separate
startup/dynamics/validation times. Post-job `qacct` review checks the job ID,
queue, project, slots and zero failure/exit status, then reports allocated
GPU-hours, CPU-slot-hours and setup-inclusive versus dynamics-only rate.

## Local validation and SCC boundary

The corrected read-only Stage P XTC probe supplied by the user returned
`xtc_check_exit=0`, 38,414 atoms and 11 complete frames from 0 to 4 ps at
0.4 ps. This confirmed the exact-r6 `gmx check` report layout. The first
read-only probe failed during MPI initialization because it lacked the
private `/tmp` bind; it did not alter the trajectory. The selected runner's
container helper already binds job-private scratch at `/tmp` and sets the
Open MPI temporary directory there.

Local tests cover the exact arm command difference, one-attempt guard,
paired-TPR source verification, storage stop behavior, XTC envelope and
decoder-report parsing, DHDL/EDR grids, checkpoint state, baseline/HREX
exchange histories, and `qacct` identity. The package checksum and local
review also passed (**15 targeted tests**). These tests do not replace a compute-node rehearsal or
prove the code can finish 100 ps on one L40S. Current SU balance/tariff is
unverified. A selected release needs an exact queue validation, fresh quota
and SU review, a real bounded job script and separate authorization before
either technical scout arm is submitted. Scientific C2 duration, repeats,
storage and production remain unselected.

## Read-only SCC package review

From a local Mac terminal in the repository root, transfer the package:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-scout-gpu-runtime-candidate-20260929-v4 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then on `scc-i01`:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-gpu-runtime-candidate-20260929-v4
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh
bash REVIEW_ON_SCC.sh
```

`REVIEW_ON_SCC.sh` is read-only; it checks the source tree and r6 image
without requesting a scheduler allocation. Preserve its full output and do
not submit a GPU job from this package. Its `SHA256SUMS` hash should match
the 64-character value above.

## SCC review result — 2026-09-29

The user transferred v4 to `/project/rise-batteries/bode/container-build-packages/`
and supplied its `scc-i01` review output. The remote `SHA256SUMS` SHA-256 was
`71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df`,
matching the local package. `REVIEW_PACKAGE.sh` checked all 13 listed files
and reported `C2_SCOUT_GPU_RUNTIME_PACKAGE_VERIFIED;
execution_authorized=False`. `REVIEW_ON_SCC.sh` independently reported
`C2_SCOUT_GPU_RUNTIME_CANDIDATE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`. Accept the remote package and
source review on this evidence. This is not a compute-node runtime result.
The next gate is a selected, separately sealed execution release with an
exact queue check, current storage and SU review, and explicit GPU-attempt
selection before either scout arm is submitted.

GROMACS source documents the XTC frame header and exact-r6 read path in
[`xtcio.cpp`](https://github.com/gromacs/gromacs/blob/v2025.3/src/gromacs/fileio/xtcio.cpp);
the [2025.3 mdrun reference](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-mdrun.html)
defines `-replex`, `-reseed`, `-cpt` and `-maxh`.
