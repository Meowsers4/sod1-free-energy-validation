# C1 single-node Singularity build plan — 2026-09-21

## Current result — 2026-09-24: complete SIF milestone verified

The final SIF checksum and direct dependency checks passed in the user-supplied
`final-verification.fEYjP0D0.log`. See the
[r6 verification record](gromacs_hrex_sif_r6_verification.md) for the exact image
path, SHA-256, evidence and remaining GPU qualification scope. No further build
or CPU startup rerun is needed. The commands below document the completed work
and remain reference instructions, not a request to launch another build.

## Reporting issue and completed correction — 2026-09-24

r6 completed in `/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj`.
The user-supplied log shows identity output, preserved complete-install archive,
and exit 0, but the last wrapper-mediated `sh -c` dependency command emitted
`ldd: missing file arguments` and a missing-path error. The zero status and old
completion marker therefore do not establish a clean final dependency report.
Wrapper command-string handling is suspected; its implementation is not verified.
Do not rebuild or overwrite the original package, SIF, logs, or marker.

On `scc-i01`, verify the existing SIF hash and inspect dependencies using direct
argument calls to Singularity, saving a fresh log:

```bash
bash <<'VERIFY'
set -euo pipefail
cd /projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj
VERIFY_LOG=$(mktemp "$PWD/final-verification.XXXXXXXX.log")
printf 'Verification log: %s\n' "$VERIFY_LOG"
(
  sha256sum --check --strict SIF.sha256
  cat SIF.sha256
  singularity exec --cleanenv gromacs-2025.3-mpi-cuda-l40s.sif ldd /opt/gromacs/2025.3/bin/gmx_mpi
  singularity exec --cleanenv gromacs-2025.3-mpi-cuda-l40s.sif ldd /opt/openmpi/4.1.5/lib/libmpi.so
) 2>&1 | tee "$VERIFY_LOG"
if grep -Eiq 'not found|no such file|missing file arguments' "$VERIFY_LOG"; then
  echo 'Dependency verification failed; preserve this log.' >&2
  exit 1
fi
echo 'SIF_HASH_AND_DEPENDENCIES_VERIFIED' | tee -a "$VERIFY_LOG"
VERIFY
```

This verification completed successfully; its output is recorded above. GPU-driver
warnings in earlier startup output were nonfatal; GPU execution remains untested.
The source launcher below has been corrected for future packages, with a separate
dependency log and fail-closed checks. This does not require repackaging r6.

## Current status — 2026-09-24: complete SIF milestone authorized

After the runtime diagnostic passed, the user asked to start the complete-image
milestone. The reviewed package is `gmx-hrex-20260924-r6`; earlier packages remain
immutable. It performs a full source build and complete installation, then creates
and hashes the SIF. Before final-image assembly, it archives the installed GROMACS,
OpenMPI, FFTW, compiler runtimes, and build manifest into
`installed-toolchain.tar.gz` with `installed-toolchain.sha256` on retained scratch.
The launcher verifies and copies this archive to the persistent build directory on
exit, including after a later image-test failure. An archive is a recovery artifact,
not evidence of a successful SIF.

Singularity runs with `--no-cleanup` so a failed bundle survives. Final-image tests
check GROMACS data and PMIx help installation, then exercise singleton and two-rank
GROMACS MPI initialization. The full self-test repeats as the ordinary user after
SIF creation; identity evidence is also captured through the SCC wrapper.
`BUILD_AND_IDENTITY_COMPLETE` is written only after these checks and archive
preservation succeed. None of this submits a GPU job or qualifies HREX.

Non-interactive SSH authentication from the agent was rejected by SCC on
2026-09-24. The package can be prepared locally, but transfer and launch require
the user's interactive SCC authentication using the commands below.

## Runtime diagnostic result — 2026-09-24

The [runtime-only diagnostic](gromacs_runtime_probe.md) passed in user-supplied
`pmix-check.e70ODU86.log` with exit 0, including two-rank MPI initialization.
The diagnostic loop is complete. Its recovery-specific path overrides do not
change the normal complete OpenMPI installation produced by the full definition.
No complete SIF or GPU qualification is established. Next milestone is the full
definition-built SIF, preserving failed bundles, with SHA-256 and identity/MPI
verification. Keep the passing log, retained rootfs, and earlier scratch products.

## Prior status — 2026-09-23: pause full rebuilds

**Inventory received; next step is now the [runtime-only diagnostic](gromacs_runtime_probe.md).**
Two build logs report all 96 tests passing, and the retained MPI/FFTW/GROMACS
libraries are present. Use that diagnostic's fresh package and launch instructions.
The inventory commands below are retained for troubleshooting history; they have
already been run. A full rebuild remains paused pending diagnostic results.

The first user-run inventory found three retained `gmx_mpi` build binaries but no
SIF or `.singularity.d` in the searched paths. SCC reports Singularity CE 4.5.1
and host `TMPDIR=/scratch`. Before attempting recovery, inspect retained library
build products and associate each scratch directory with its build log:

```bash
for d in /scratch/"$USER"/gmx-hrex-build.*; do
  [ -d "$d/work/gromacs-build" ] || continue
  printf '\nLibraries retained in %s\n' "$d"
  find "$d/work" -maxdepth 12 -type f \
    \( -name 'libmpi.so*' -o -name 'libopen-rte.so*' \
       -o -name 'libopen-pal.so*' -o -name 'libfftw3f*.so*' \
       -o -name 'libgromacs*.so*' -o -name 'orterun' \) -print
done
grep -H -E 'Scratch directory \(retained|[0-9]+% tests passed|Build/identity exit status' \
  /projectnb/rise-batteries/bode/containers/builds/gmx-hrex.*/build.log
```

This is read-only. Surviving build libraries may allow a runtime-only diagnostic;
their presence and completeness are not yet established. Installed `/opt` trees
were inside the build image, not the retained scratch work bind. No recovery image
would be a qualified replacement for the reproducible definition build.

r5 is locally prepared, but SCC transfer/execution and a successful image remain
unconfirmed. Before another compilation, run this read-only inventory on `scc-i01`
and inspect the output to choose a runtime diagnostic using retained artifacts if
available. A failed build may have cleaned its root filesystem, so the presence of
compiled files alone does not establish that a runnable image exists. The build
commands later in this document are reference instructions, not the next action.

```bash
hostname
singularity --version
printf 'TMPDIR=%s\nOMPI_MCA_orte_tmpdir_base=%s\n' \
  "${TMPDIR-}" "${OMPI_MCA_orte_tmpdir_base-}"
for d in /projectnb/rise-batteries/bode/containers/builds \
         /scratch/"$USER"/gmx-hrex-build.*; do
  [ -d "$d" ] || continue
  printf '\nInspecting %s\n' "$d"
  find "$d" -maxdepth 10 \
    \( -name '*.sif' -o -name '.singularity.d' -o -name 'gmx_mpi' \) -print
done
```

## Decision

Use a project-owned Singularity image containing one combined GROMACS 2025.3 build
with external OpenMPI 4.1.5 and CUDA 12.8 support. The first candidate layout is
restricted to **one L40S host**: 20 MPI ranks, one rank for each of the 20 lambda
states, sharing that host's four GPUs. OpenMPI runs wholly inside the container.

This route removes the dependency on a native SCC combined MPI+CUDA installation and
avoids cross-host host/container MPI compatibility. It does **not** prove that HREX is
ready to run. The SIF still has to build successfully, and a later separately authorized
non-production allocation must establish GPU visibility, `multidir`/`replex`, checkpoint
restart, exchange records, and measured performance.

The frozen contract is
[`gromacs_hrex_container_v1.yaml`](gromacs_hrex_container_v1.yaml), and the definition is
[`gromacs-2025.3-mpi-cuda-l40s.def`](../containers/gromacs-2025.3-mpi-cuda-l40s.def).
Static validation is a CPU-only Snakemake target and cannot build an image or submit a job:

```bash
snakemake -s workflow/Snakefile -n gromacs_hrex_container_spec
snakemake -s workflow/Snakefile -c 1 gromacs_hrex_container_spec
```

An existing validation report is preserved and cannot be regenerated in place. Use a
fresh package below to obtain a new validation report for a revised definition.

## Why this combination

GROMACS supports an external-MPI CUDA build by combining `GMX_MPI=ON` and
`GMX_GPU=CUDA`; the 2025.3 release requires CMake 3.28 or newer, GCC 11 or newer,
and CUDA 12.1 or newer. The definition pins compatible versions and targets `sm_89`,
the architecture of SCC's L40S cards. The GROMACS and regression-test archives use the
checksums published on the [GROMACS 2025.3 download page](https://manual.gromacs.org/2025.3/download.html).
The build flags follow the [official installation guide](https://manual.gromacs.org/2025.3/install-guide/index.html).

BU documents user image builds with fakeroot on the dedicated `scc-i01` or `scc-i02`
build hosts, with temporary files on `/scratch` and the completed SIF moved to
`/projectnb`. BU's `scc-singularity` wrapper carries the scheduler environment and
automatically exposes assigned NVIDIA devices; `--nolocal` prevents accidental use of
host `/usr/local`. See BU's [building instructions](https://www.bu.edu/tech/support/research/software-and-programming/containers/building/)
and [SCC Singularity wrapper documentation](https://www.bu.edu/tech/support/research/software-and-programming/containers/singularity/).

## Prepare and transfer a reviewed package

The CPU-only package target validates a copy of the definition, contract, instructions,
validator and tests, then records every file in `SHA256SUMS`. It writes no simulation
outputs and does not modify the SCC repository. Choose a fresh package name for every
revision; do not force or overwrite an existing package or validation report.
It also generates `BUILD_ON_SCC.sh` from the exact reviewed build block below, so no
manual transcription is needed on SCC.

```bash
snakemake -s workflow/exchange_feasibility.smk -n results/container_build_packages/gmx-hrex-20260924-r6
snakemake -s workflow/exchange_feasibility.smk -c 1 results/container_build_packages/gmx-hrex-20260924-r6
```

From the Mac, transfer into a new directory, then verify the received bytes:

```bash
cd /Users/bodebosell/sod1fep
ssh scc1.bu.edu 'mkdir -p /projectnb/rise-batteries/bode/container-build-packages && mkdir /projectnb/rise-batteries/bode/container-build-packages/gmx-hrex-20260924-r6' &&
scp -r results/container_build_packages/gmx-hrex-20260924-r6/. scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/gmx-hrex-20260924-r6/ &&
ssh scc1.bu.edu 'cd /projectnb/rise-batteries/bode/container-build-packages/gmx-hrex-20260924-r6 && sha256sum --check --strict SHA256SUMS && sha256sum containers/gromacs-2025.3-mpi-cuda-l40s.def'
```

If interrupted, use a fresh destination name or inspect the partial transfer before
continuing. Do not sync over the historical simulation checkout. The definition hash
must equal `artifact.definition_sha256` in the transferred YAML and the locally reported
hash. Image tags and distribution packages can change upstream; the definition hash
identifies the recipe, while the resulting SIF hash identifies the actual built image.

## Correction after the first SCC attempt

The r1 attempt stopped with exit 255 before compilation: `-B /scratch` requested a
container destination that did not exist in the NVIDIA base image. This was a build
procedure error, not evidence of laptop-disconnect failure. Preserve the r1 package
and its failed log. Revision r2 binds a dedicated host scratch work directory to the
container's existing `/tmp`, where the definition already downloads and compiles.
`SINGULARITY_TMPDIR` remains a separate scratch directory for image assembly. No
image-definition bytes, dependency pins or scientific settings changed. Bind syntax
is documented in the [Singularity guide](https://docs.sylabs.io/guides/latest/user-guide/bind_paths_and_mounts.html).
BU also [documents](https://www.bu.edu/tech/support/research/software-and-programming/containers/building/)
the need for an existing `/scratch` destination when that destination is used.

## Correction after the r2 MPI test failure

The captured first failing MPI test aborted before launching its test binary because
OpenMPI's remote-shell component could not find `ssh : rsh` inside the image. This
identifies that startup failure; it does not establish the cause of every failed test.
Revision r3 selects `OMPI_MCA_plm=isolated` in the build, final runtime environment,
and final image self-test, matching the one-host scope. It retains the full GROMACS
test suite and adds a two-process `/bin/true` launcher check immediately after OpenMPI
installation, before GROMACS compilation. That early check verifies launching only;
MPI communication and GROMACS correctness still require the full tests.

The launcher was checked against `orte/mca/plm/isolated/plm_isolated.c` and
`plm_isolated_component.c` in the [pinned OpenMPI 4.1.5 source archive](https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.5.tar.gz),
whose SHA-256 matches the contract. Unlike r2's mount-only correction, r3 changes the
definition bytes and updates their pinned hash. Preserve both earlier packages and
failed logs. No regression test is disabled and no multi-host support is introduced.
A successful SCC rebuild is still required; local Python tests cannot establish that.

## Correction after the r3 final-image failure

The r3 attempt reached the final image's self-test, where the dynamic loader reported
`libgomp.so.1` missing. Compilation and build-stage testing had completed far enough
for the final stage to copy the installed artifacts, but the final image lacked the
GCC OpenMP runtime. The supplied excerpt does not include the full CTest pass/skip
summary; preserve that log before making claims about all tests.

Revision r4 explicitly installs `libgomp`, `libgcc`, and `libstdc++` in the final
Rocky Linux image. Copying the compiler toolset directory alone did not include every
system runtime dependency. The [Rocky Linux BaseOS repository](https://dl.rockylinux.org/pub/rocky/8/BaseOS/x86_64/os/Packages/l/)
provides these runtime packages. The actual installed RPM versions are saved inside
the image and captured with the identity evidence. The final self-test now prints
`ldd` reports for GROMACS, the MPI launcher, `ompi_info`, and `libmpi`, rejects missing
libraries or inspection failures, and prints any `gmx_mpi --version` failure directly
into the build log. All earlier tests and the isolated MPI launcher remain enabled.
Local tests check this failure handling with mocked executables; only the SCC rebuild
can verify the real final image. Earlier packages remain unchanged.

## Correction after the r4 MPI session-directory failure

The r4 final image test reached MPI initialization, then ORTE attempted to create
`/scratch` on the read-only image filesystem and failed. The supplied log establishes
that the selected session path is inaccessible; the exact inherited environment
variable was not captured. OpenMPI can select its session root from `TMPDIR` or an
MCA override. Revision r5 sets `OMPI_MCA_orte_tmpdir_base=/tmp` during the build,
in the image environment, and explicitly in `%test`, ensuring the override is in
place before singleton `gmx_mpi --version` as well as `mpirun`.
Conflicting local/remote MPI temporary-directory overrides are unset in those same
three contexts. The pinned OpenMPI 4.1.5 source explicitly rejects combining those
local/remote settings with the global override. The host's general `TMPDIR` and
`SINGULARITY_TMPDIR` remain unchanged; `/tmp` inside the build is backed by the
existing private scratch work mount. See [OpenMPI's session-directory guidance](https://www.open-mpi.org/faq/?category=all).

This change is an environment correction and retains all tests, runtime packages,
and the local-only launcher. Tests inject unusable host scratch settings into the
actual `%test` shell snippet and verify the explicit override reaches its mocked
GROMACS and MPI commands. They do not substitute for a successful SCC image test.
The prior packages and failed logs remain intact.

## Build on SCC

First connect and enter the verified package:

```bash
ssh scc1.bu.edu
ssh scc-i01
cd /projectnb/rise-batteries/bode/container-build-packages/gmx-hrex-20260924-r6
sha256sum --check --strict SHA256SUMS && {
  LAUNCH_LOG=$(mktemp "$PWD/launch.XXXXXXXX.log")
  nohup bash BUILD_ON_SCC.sh > "$LAUNCH_LOG" 2>&1 < /dev/null &
  printf 'Build launcher PID: %s; log: %s\n' "$!" "$LAUNCH_LOG"
}
```

The launcher uses `nohup` with file-backed input/output so a normal SSH disconnect
or laptop sleep does not terminate the build. It cannot protect against host reboot or
administrative termination. Read the printed launch log with `tail -f PATH_TO_LOG`;
Ctrl-C stops only the log viewer. Do not launch a second copy just because the laptop
was disconnected; inspect the logs first.

`BUILD_ON_SCC.sh` executes the following block. It checks the host and package, snapshots the source into
a unique persistent build directory, and saves both build and identity logs. A failed
build stops before moving the image. Each attempt gets its own directory; earlier SIFs
and evidence are never replaced. No GPU allocation is requested. The image build runs
its software regression tests; it does not run a project protein simulation.

```bash
bash <<'BUILD'
set -euo pipefail
case "$(hostname -s)" in
  scc-i01|scc-i02) ;;
  *) echo "Use scc-i01 or scc-i02 for this build." >&2; exit 1 ;;
esac
sha256sum --check --strict SHA256SUMS
BUILD_PARENT=/projectnb/rise-batteries/bode/containers/builds
mkdir -p "$BUILD_PARENT"
BUILD_DIR=$(mktemp -d "$BUILD_PARENT/gmx-hrex.XXXXXXXX")
mkdir "$BUILD_DIR/source"
cp -R containers docs src tests workflow container_spec.json BUILD_ON_SCC.sh SHA256SUMS "$BUILD_DIR/source/"
printf 'Build evidence directory: %s\n' "$BUILD_DIR"
(
  set -euo pipefail
  preserve_build_exit() {
    status=$?
    trap - EXIT
    if [ -n "${CONTAINER_TMP:-}" ] && [ -f "$CONTAINER_TMP/work/installed-toolchain.sha256" ]; then
      if (cd "$CONTAINER_TMP/work" && sha256sum --check --strict installed-toolchain.sha256) &&
          cp "$CONTAINER_TMP/work/installed-toolchain.tar.gz" "$CONTAINER_TMP/work/installed-toolchain.sha256" "$BUILD_DIR/"; then
        printf 'Complete installed toolchain preserved: %s/installed-toolchain.tar.gz\n' "$BUILD_DIR"
      else
        echo 'Failed to preserve the installed toolchain; keep the scratch directory.' >&2
        status=1
      fi
    fi
    printf 'Build/identity exit status: %s\n' "$status"
    exit "$status"
  }
  trap preserve_build_exit EXIT
  cd "$BUILD_DIR/source"
  sha256sum --check --strict SHA256SUMS
  hostname
  date -u
  singularity --version
  mkdir -p "/scratch/$USER"
  CONTAINER_TMP=$(mktemp -d "/scratch/$USER/gmx-hrex-build.XXXXXXXX")
  printf 'Scratch directory (retained for inspection): %s\n' "$CONTAINER_TMP"
  mkdir "$CONTAINER_TMP/cache" "$CONTAINER_TMP/tmp" "$CONTAINER_TMP/work"
  export SINGULARITY_CACHEDIR="$CONTAINER_TMP/cache"
  export SINGULARITY_TMPDIR="$CONTAINER_TMP/tmp"
  singularity build --fakeroot --no-cleanup -B "$CONTAINER_TMP/work:/tmp" \
    "$CONTAINER_TMP/gromacs-2025.3-mpi-cuda-l40s.sif" \
    containers/gromacs-2025.3-mpi-cuda-l40s.def
  sha256sum --check --strict SHA256SUMS
  IMAGE="$BUILD_DIR/gromacs-2025.3-mpi-cuda-l40s.sif"
  test ! -e "$IMAGE"
  mv "$CONTAINER_TMP/gromacs-2025.3-mpi-cuda-l40s.sif" "$IMAGE"
  cd "$BUILD_DIR"
  sha256sum gromacs-2025.3-mpi-cuda-l40s.sif > SIF.sha256
  sha256sum --check --strict SIF.sha256
  (
    set -euo pipefail
    singularity test --cleanenv --contain "$IMAGE"
    scc-singularity --nolocal exec "$IMAGE" gmx_mpi --version
    scc-singularity --nolocal exec "$IMAGE" ompi_info --version
    scc-singularity --nolocal exec "$IMAGE" printenv OMPI_MCA_plm OMPI_MCA_orte_tmpdir_base
    scc-singularity --nolocal exec "$IMAGE" cat /opt/sod1fep-container-build.txt
    scc-singularity --nolocal exec "$IMAGE" cat /opt/sod1fep-runtime-rpms.txt
  ) 2>&1 | tee "$BUILD_DIR/identity.log"
  (
    set -euo pipefail
    singularity exec --cleanenv "$IMAGE" ldd /opt/gromacs/2025.3/bin/gmx_mpi
    singularity exec --cleanenv "$IMAGE" ldd /opt/openmpi/4.1.5/lib/libmpi.so
  ) 2>&1 | tee "$BUILD_DIR/dependencies.log"
  if grep -Eiq 'not found|no such file|missing file arguments' "$BUILD_DIR/dependencies.log"; then
    echo "Dependency inspection failed: inspect dependencies.log before accepting this image." >&2
    exit 1
  fi
) 2>&1 | tee "$BUILD_DIR/build.log"
touch "$BUILD_DIR/BUILD_AND_IDENTITY_COMPLETE"
printf 'Build and identity checks finished. Evidence: %s\n' "$BUILD_DIR"
BUILD
```

Build time depends on host load and cache state. Keep `build.log`, `identity.log`,
`SIF.sha256`, the SIF, `installed-toolchain.tar.gz`, its checksum, and the `source/`
snapshot together. A missing
`BUILD_AND_IDENTITY_COMPLETE` means the process did not finish successfully. If any
command fails, retain the evidence and fix the reviewed package; do not remove tests or
substitute dependency versions during the build. Scratch cleanup is manual after evidence
has been checked; never delete another attempt's directory.

The acceptance evidence must show GROMACS 2025.3, `MPI library: MPI` (possibly with a
GPU-awareness annotation), `MPI library version: Open MPI v4.1.5`, `GPU support: CUDA`,
and the pinned manifest, with no unresolved linked libraries. These software identity
checks cannot demonstrate working GPU access, exchange or restart.

## Boundary for the next step

After the build and identity evidence are preserved, the next request is a bounded,
non-production, single-node scheduler smoke test. Its prospective allocation is one
`mpi32` host, 20 local MPI ranks, and four L40S GPUs; the exact SGE request and launch
command must be frozen only after confirming how the SCC wrapper exposes all four devices.
The captured `mpi32` PE uses `allocation_rule 32`: distinguish a prospective 32-slot
reservation from the 20 application ranks, and verify one-host placement at runtime.
The operating notes report `Exclusive_Process` mode, which prevents five independent
CUDA processes from sharing a GPU directly. Before the GPU smoke test, establish the
actual compute mode and a supported sharing arrangement (such as MPS); GPU visibility
alone is insufficient. Do not change a GPU's compute mode or start a shared daemon as
part of this build. See [NVIDIA's MPS compute-mode guidance](https://docs.nvidia.com/deploy/mps/when-to-use-mps.html).
No multi-host launch is allowed for container v1. No F64A or other protein sampling is
authorized by building or validating this image.
