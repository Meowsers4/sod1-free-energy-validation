# Retained-build runtime diagnostic — 2026-09-23

The subsequent complete r6 SIF has now been built and verified. See the
[artifact record](gromacs_hrex_sif_r6_verification.md). This page describes the
earlier recovery diagnostic; its commands do not need to be rerun.

## Result — 2026-09-24: retained-rootfs startup diagnostic passed

The user-supplied log
`/projectnb/rise-batteries/bode/containers/runtime-probes/probe.8c6hTH3H/pmix-check.e70ODU86.log`
ends with `RUNTIME_PROBE_PASSED` and `PMIx path-check exit status: 0`.
Dependency and identity checks, the two-process launcher, and two-rank GROMACS
MPI initialization completed with the OPAL path overrides below. The diagnostic
does not need to be repeated. Preserve this log and the retained rootfs.

CUDA driver warnings were nonfatal; actual GPU operation is untested. Singularity
replaced the requested host `/tmp` bind with its session `/tmp`; the test proves
the container `/tmp` was usable, not that the requested host bind was used.
This command created no SIF. The recovered rootfs remains an incomplete diagnostic
installation; next is a complete definition-built image, its SHA-256, and identity/
MPI verification before any GPU qualification. The full definition copies the
installed OpenMPI tree, so these recovery-specific OPAL overrides are not a new
requirement for the full build. The commands below document the completed check.

## Diagnostic history

The v1 diagnostic reached GROMACS 2025.3/OpenMPI 4.1.5/CUDA identity output, then
failed at the first `mpirun` command with PMIx `NOT-FOUND`. Missing
`share/pmix/help-pmix-runtime.txt` hid the failing framework's name. This exposes a
recovery-script packaging defect: v1 flattened PMIx help and plugin files into
`share/openmpi` and `lib/openmpi`. The pinned OpenMPI source's bundled PMIx
`config/pmix.m4` specifies `share/pmix` and `lib/pmix`; its
`src/mca/pinstalldirs/env/pmix_pinstalldirs_env.c` supports `PMIX_PKGDATADIR` and
`PMIX_PKGLIBDIR` overrides. The source script and regression test now preserve
PMIx's layout. The previously transferred v1 package is unchanged.

The failure log retained the rootfs, so test temporary path overrides against that
exact image first. This tests the plugin-path hypothesis and restores readable
diagnostics; the missing help file alone does not establish the startup cause.
The first override check (`pmix-check.R5qArABz.log`) exited 1: OpenMPI rejected
PMIx-only overrides with unset OPAL equivalents. Inspection of the pinned
`opal/mca/pmix/pmix3x/pmix3x_local.c:95` confirms that it rejects this mismatch
and explicitly forwards OPAL-only values to bundled PMIx. Therefore the current
command sets **OPAL**, not PMIX, directory overrides. This keeps the existing
OpenMPI paths and lets its integration code configure PMIx consistently. The
CUDA driver warning in that log did not stop singleton identity output; GPU
operation remains untested.

No source files or image contents are changed. Run on `scc-i01`:

```bash
bash <<'CHECK'
set -euo pipefail
ROOTFS=/scratch/bodeb/gmx-runtime-probe.BHWXJESK/tmp/build-temp-3284053732/rootfs
test -d "$ROOTFS"
CHECK_TMP=$(mktemp -d /scratch/bodeb/gmx-pmix-check.XXXXXXXX)
CHECK_LOG=$(mktemp /projectnb/rise-batteries/bode/containers/runtime-probes/probe.8c6hTH3H/pmix-check.XXXXXXXX.log)
printf 'Log: %s\n' "$CHECK_LOG"
(
  trap 'status=$?; printf "PMIx path-check exit status: %s\n" "$status"; exit "$status"' EXIT
  singularity test --cleanenv --contain \
    --env OPAL_PKGDATADIR=/opt/openmpi/4.1.5/share/openmpi \
    --env OPAL_PKGLIBDIR=/opt/openmpi/4.1.5/lib/openmpi \
    -B "$CHECK_TMP:/tmp" "$ROOTFS"
) 2>&1 | tee "$CHECK_LOG"
CHECK
```

Return the final output and log path. Success is only a runtime diagnostic under
these overrides; no SIF, full reproducible build, or GPU qualification is established.
The initial build/transfer/launch instructions below are historical; do not relaunch
v1 or create a new image to execute this check.

Two user-supplied SCC logs report `100% tests passed, 0 tests failed out of 96`.
The final container subsequently failed. No SIF or sandbox was found, but compiled
MPI, FFTW, and GROMACS products remain. The current diagnostic uses only the
`DwrrwCIz` tree, matched to build evidence `gmx-hrex.VkNOVnDY`, never mixing attempts.

This copies existing products into a **diagnostic-only** runtime image. It does
not invoke a compiler, `make`, CMake, a scheduler, or a protein simulation. It
installs the same runtime RPM dependencies as r5 and preserves all earlier bytes.
The image is deliberately incomplete for scientific use (e.g. no GROMACS data
installation). Passing is not GPU/HREX qualification or reproducible-build acceptance.
Further missing recovery artifacts are possible; stop and inspect its preserved
log if any copy, dependency, or startup check fails. Do not trigger a full rebuild.

Copies include OpenMPI's shared libraries, component plugins, local launcher,
daemon, identity tool, and help files. These are staged at the original `/opt`
prefix. Library aliases are dereferenced; temporary libtool `*.so.*T` outputs are
excluded; conflicting duplicate basenames fail closed. Selected source hashes,
payload hashes, source build log/definition, diagnostic definition and logs are
preserved in a fresh `/projectnb/rise-batteries/bode/containers/runtime-probes`
directory. Original scratch files are read only by this script. The script checks
the source log's scratch association and passing CTest summary before staging.

The self-test checks ELF dependencies, GROMACS/MPI/CUDA build identity, singleton
MPI initialization, a two-process launcher, and two MPI-initializing GROMACS version
commands. Each startup command has a 60-second timeout. It deliberately sets
`TMPDIR=/scratch` while `OMPI_MCA_orte_tmpdir_base=/tmp`; a fresh writable `/tmp`
bind is used. It runs during fakeroot assembly and again as the ordinary user with
`--cleanenv --contain`. Only both passing creates `RUNTIME_PROBE_COMPLETE`.

The [OpenMPI v4 FAQ](https://www.open-mpi.org/faq/?category=tuning) describes
component discovery under the installed prefix. The
[Singularity 4.5 build reference](https://docs.sylabs.io/guides/4.5/user-guide/cli/singularity_build.html)
documents `--no-cleanup`, used here to retain the bundle if assembly fails.

Prepare locally through the CPU-only DAG:

```bash
snakemake -s workflow/exchange_feasibility.smk -c 1 results/container_runtime_probe_packages/gmx-runtime-probe-20260923-v1
```

From the Mac, transfer a new package (the remote `mkdir` refuses an existing path):

```bash
cd /Users/bodebosell/sod1fep
ssh scc1.bu.edu 'mkdir /projectnb/rise-batteries/bode/container-build-packages/gmx-runtime-probe-20260923-v1' &&
scp -r results/container_runtime_probe_packages/gmx-runtime-probe-20260923-v1/. scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/gmx-runtime-probe-20260923-v1/
```

On `scc-i01`, launch once. The absolute log path is printed and the launch survives
a normal SSH disconnect. Keep it instead of relying on a variable after reconnect:

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-runtime-probe-20260923-v1 &&
sha256sum --check --strict SHA256SUMS && {
  PROBE_LOG=$(mktemp "$PWD/launch.XXXXXXXX.log")
  nohup bash RUN_PROBE_ON_SCC.sh \
    /scratch/bodeb/gmx-hrex-build.DwrrwCIz \
    /projectnb/rise-batteries/bode/containers/builds/gmx-hrex.VkNOVnDY \
    > "$PROBE_LOG" 2>&1 < /dev/null &
  printf 'Diagnostic PID: %s\nLog: %s\n' "$!" "$PROBE_LOG"
  tail -n 60 -f "$PROBE_LOG"
}
```

Ctrl-C stops the log viewer. Return the final log lines and the printed diagnostic
evidence directory; do not treat a background PID as proof of success. To view the
existing log after reconnect (without relaunching):

```bash
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-runtime-probe-20260923-v1 &&
tail -n 80 -f "$(ls -t launch.*.log | head -n 1)"
```
