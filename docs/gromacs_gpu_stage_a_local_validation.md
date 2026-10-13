# Stage A package validation — 2026-09-24

## Revision v2: temporary mount correction

Current package: `results/gpu_smoke_packages/gmx-gpu-stage-a-20260924-v2`.
Manifest SHA-256:
`59fc0d8e1e5a0e881f6f73d1060646ac5a2b568fd31cd6b6b81555a284c678c9`.
The user-supplied SCC v1 log demonstrated a successful first `grompp` followed by
the package rejecting a Singularity warning that the explicit `/tmp` bind had
been replaced. V2 disables automatic tmp mounts while retaining the explicit
private scratch bind, verifies a token read/write round-trip, and reports actual
warnings and failed-command output. It does not suppress input warnings.

All 14 focused tests passed, including the four-state real local CPU rehearsal,
warning-source diagnostics, the overridden-mount rejection and failed-command
reporting. Python 3.6 syntax, the one-job `gpu=0` dry-run, package generation and
both manifests were checked. V1's manifest is unchanged; all generated input and
contract bytes are identical between v1 and v2. The SIF remains unchanged.
Actual Singularity execution of the corrected command awaits SCC preparation;
these local checks cannot establish that remote mount behavior.

## Revision v1: original local validation

Package: `results/gpu_smoke_packages/gmx-gpu-stage-a-20260924-v1`.
Manifest (`SHA256SUMS`) SHA-256:
`0760ad1d635a6039f2283384b11d1825bc2cade46eea659ed56398fbc517db69`.
Packaged content was 100,011 bytes including Snakemake metadata at verification.
The runtime, generator and workflow source snapshots match their repository files.
Package contents and all manifest entries were checked locally. Preserve this
package; changes require a new version/path rather than replacing its manifest.

Validation completed:

- Full repository suite: 360 passed in 33.64 seconds.
- Focused Stage A suite after final packaging/EDR changes: 10 passed.
- Real local GROMACS 2025.3-conda_forge CPU rehearsal: all four input states
  compiled without warnings, completed 1,000 steps each, and yielded finite,
  correctly labelled DHDL, readable checkpoints, and potential/temperature
  extraction from EDR. This used thread-MPI and CPU computation on the Mac.
- Negative tests reject modified inputs, missing/changed prepared TPRs, incorrect
  PE/slots/hosts, duplicate GPU assignments, arrays/MPS inheritance, low quota,
  malformed exchange histories and an exceeded command deadline.
- Bash syntax checks passed; runtime syntax supports the container's Python 3.6.
- Main-workflow and standalone Snakemake dry-runs scheduled one `gpu=0` package
  job. The standalone rule then generated the package successfully.
- `git diff --check` passed.

This is local validation, not an SCC execution report. Singularity is unavailable
locally, and the remote SIF has not been executed by this preparation step. The
four exact-SIF TPRs will be generated and hashed by `PREPARE_ON_SCC.sh` on
`scc-i01`. No GPU job, MPI exchange simulation, MPS server or Stage B was launched.
Use the [package guide](gromacs_gpu_stage_a_package.md) for scope and remaining
review gates. Do not interpret a local fixture rehearsal as a GPU pass.
