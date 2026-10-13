# F64A C2 paired timing-scout runtime candidate, CPU review stage

Prepared locally 2026-09-29 after the user supplied the accepted v3 CPU
preparation and review. This is the **second design step** for the prospective
100-ps technical timing scout. It is a sealed, non-submitting runtime contract
and CPU importer, not an executable GPU release, C2 selection, or production
protocol. The agent has not logged into SCC or copied the remote inputs.

## SCC CPU import accepted, 2026-09-29

The user transferred v1 to `scc-i01` and supplied the terminal output. The
remote `SHA256SUMS` SHA-256 was
`8d8919e005da81b44e8dbd973a5935eda406f4e23c9c1f8b3d8abd59f4a288af`,
matching the local package. `REVIEW_PACKAGE.sh` reported
`F64A_C2_SCOUT_RUNTIME_CANDIDATE_CPU_ONLY_VERIFIED`; the one-time
`IMPORT_ON_SCC.sh` reported an imported 381-entry tree and
`F64A_C2_SCOUT_RUNTIME_CANDIDATE_CPU_ONLY_IMPORTED` after its internal review.
The separate `REVIEW_IMPORTED.sh` again reported
`F64A_C2_SCOUT_RUNTIME_CANDIDATE_CPU_ONLY_REVIEW_PASS states=20
manifest_entries=381 execution_authorized=False`. The pasted output is the
evidence source; the local agent did not independently hash the SCC tree.
Accept this CPU import/review. Preserve it without rerunning the import. No
GPU job was submitted.

## What is sealed

`packages/f64a-c2-scout-runtime-cpu-20260929-v1/` contains a 9-entry package
manifest, the 20 accepted TPR hashes, a full 381-entry source-manifest identity,
the exact r6 image identity, and separate baseline/HREX launch plans. The local
package `SHA256SUMS` SHA-256 is
`8d8919e005da81b44e8dbd973a5935eda406f4e23c9c1f8b3d8abd59f4a288af`.
The only proposed GROMACS launch difference is baseline `-replex 0` versus HREX
`-replex 500 -reseed 20260929`; each uses the same 20 TPR hashes, 50,000 steps
at 0.002 ps, one assigned L40S, 20 ranks on `omp16`/16 slots, one thread per
rank and private MPS. The plan records the per-arm 2-hour scheduler request,
105-minute work deadline, 768-MiB prospective stop threshold and 1-GiB cap at
each scratch and persistent location. One attempt per arm, baseline first, no
automatic retry. These are proposed bounds, not permission to request resources.

The package reviewer checks all 9 package entries and compares the sealed
contract and both generated plans. The CPU importer verifies all 381 source
manifest entries, the source metadata, and all 60 common/paired TPR copies
against the accepted 20 hashes, then copies the prepared tree without grompp.
It refuses overwrite and refuses import inside an SGE allocation. The separate
import reviewer rehashes the full copy and source and confirms provenance. The
`job` entry point always raises `GPU execution is not authorized by this
candidate`. No `qsub`, SGE job script or GPU launch entry point is packaged.

## SCC CPU-only review and import

Copy the local directory to
`/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-runtime-cpu-20260929-v1`
using the established transfer method. In the user's `scc-i01` terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-runtime-cpu-20260929-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh
bash IMPORT_ON_SCC.sh
bash REVIEW_IMPORTED.sh
```

The first checksum should be the 64-character value above. The import/review
should report `F64A_C2_SCOUT_RUNTIME_CANDIDATE_CPU_ONLY_REVIEW_PASS
states=20 manifest_entries=381 execution_authorized=False`. Preserve the full
output, including any failure; do not rerun an interrupted import in place.
No GPU allocation or simulation occurs in these commands.

## Requirements before a selectable GPU scout release

This candidate makes the input and launch distinction concrete but intentionally
has no runnable GPU job. The next **new** package revision must add and test:

1. An exact-r6 one-GPU job wrapper with one-host allocation, UUID, 16-CPU-ID
   affinity, private MPS 20-client overlap and cleanup checks. Reuse the
   accepted Stage P implementation where applicable. Maintain separate
   one-attempt markers for baseline and HREX, requiring baseline review before
   HREX is eligible.
2. Active walltime and *separate* scratch/persistent byte monitors, including
   GROMACS graceful stop, final evidence reserve and incomplete/censored status.
   Recheck project quota, filesystem free space, queue validity and SU balance
   at selection time. A full 2-hour allocation consumes up to 2 allocated
   GPU-hours and 32 CPU-slot-hours per arm.
3. Per-state final-step/checkpoint, all-state DHDL and EDR 1-ps grid, 0/50/100
   ps full-system XTC frame/atom/box checks, baseline no-exchange history, and
   HREX 99 scheduled neighbor-exchange rounds with identical permutations in
   all 20 logs. Acceptance counts are observations, not pass thresholds.
4. Compact checkpoint and output hashes, timing split between startup and MD,
   GROMACS performance, storage-by-type and `qacct`/SU review. Do not archive
   full checkpoint text dumps or duplicate entire phase trees as Stage P did.

The GPU job release must be a separately sealed package after these checks and
an explicit scope selection under `CLAUDE.md` rule 6. A complete timing pair
will inform the C2 resource model; it will not yield an F64A effect estimate or
authorize production. GROMACS 2025.3 defines `-replex 0` as the disabled
default, `-reseed` for exchange and `-cpt` in minutes in its
[mdrun reference](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-mdrun.html).

Local validation: the package reviewer passed; a `job` invocation failed with
its deliberate authorization error; three targeted tests passed, including
plan separation, resource-change rejection and manifest tamper rejection.
