#!/bin/bash
# Packaged by the CPU-only gromacs_hrex_runtime_probe_package Snakemake rule.
# Copy retained build products into an isolated diagnostic image; never compile.
set -euo pipefail
case "$(hostname -s)" in
  scc-i01|scc-i02) ;;
  *) echo 'Run this diagnostic on scc-i01 or scc-i02.' >&2; exit 1 ;;
esac
if [ "$#" -ne 2 ]; then
  echo 'Usage: bash RUN_PROBE_ON_SCC.sh RETAINED_SCRATCH_DIR BUILD_EVIDENCE_DIR' >&2
  exit 2
fi
retained=$(cd "$1" && pwd -P)
evidence=$(cd "$2" && pwd -P)
package=$(cd "$(dirname "$0")" && pwd -P)
cd "$package"
sha256sum --check --strict SHA256SUMS
grep -Fx "Scratch directory (retained for inspection): $retained" "$evidence/build.log"
grep -E '^100% tests passed, 0 tests failed out of 96[[:space:]]*$' "$evidence/build.log"
test -f "$evidence/source/containers/gromacs-2025.3-mpi-cuda-l40s.def"
test -x "$retained/work/gromacs-build/bin/gmx_mpi"
probe_parent=/projectnb/rise-batteries/bode/containers/runtime-probes
mkdir -p "$probe_parent"
probe=$(mktemp -d "$probe_parent/probe.XXXXXXXX")
printf 'Diagnostic evidence: %s\n' "$probe"
(
  set -euo pipefail
  trap 'status=$?; printf "Runtime diagnostic exit status: %s\n" "$status"; exit "$status"' EXIT
  cp "$evidence/build.log" "$probe/original-build.log"
  cp "$evidence/source/containers/gromacs-2025.3-mpi-cuda-l40s.def" "$probe/original-build.def"
  cp "$package/gromacs-runtime-probe.def" "$probe/"
  cp "$package/RUN_PROBE_ON_SCC.sh" "$probe/"
  cp "$package/SHA256SUMS" "$probe/package-SHA256SUMS"
  printf 'retained=%s\nevidence=%s\n' "$retained" "$evidence" > "$probe/source-paths.txt"
  mkdir -p "$probe/payload/gromacs/2025.3/bin" "$probe/payload/gromacs/2025.3/lib64" \
    "$probe/payload/openmpi/4.1.5/bin" "$probe/payload/openmpi/4.1.5/lib/openmpi" \
    "$probe/payload/openmpi/4.1.5/share/openmpi" "$probe/payload/openmpi/4.1.5/share/pmix" \
    "$probe/payload/openmpi/4.1.5/lib/pmix" "$probe/payload/fftw/3.3.10/lib"
  : > "$probe/copied-source-sha256.txt"
  copy_product() {
    local source=$1 destination=$2
    if [ -e "$destination" ]; then
      cmp -s "$source" "$destination" || {
        printf 'Conflicting retained files for %s\n' "$destination" >&2; exit 1;
      }
    else
      # Dereference library aliases to avoid links back into retained scratch.
      cp -L "$source" "$destination"
    fi
    sha256sum "$source" >> "$probe/copied-source-sha256.txt"
  }
  copy_product "$retained/work/gromacs-build/bin/gmx_mpi" "$probe/payload/gromacs/2025.3/bin/gmx_mpi"
  for component in openmpi-4.1.5 fftw-3.3.10 gromacs-build; do
    find "$retained/work/$component" \( -type f -o -type l \) -name '*.so*' -print0 > "$probe/$component.libraries"
    while IFS= read -r -d '' source; do
      name=${source##*/}
      # Exclude libtool's temporary relinking outputs (e.g. libmpi.so.40.30.5T).
      [[ "$name" =~ \.so(\.[0-9]+)*$ ]] || continue
      case "$component" in
        openmpi-4.1.5)
          case "$source" in */.libs/*) ;; *) continue ;; esac
          case "$name" in
            mca_*)
              case "$source" in
                */opal/mca/pmix/pmix3x/pmix/*) target="$probe/payload/openmpi/4.1.5/lib/pmix/$name" ;;
                *) target="$probe/payload/openmpi/4.1.5/lib/openmpi/$name" ;;
              esac ;;
            *) target="$probe/payload/openmpi/4.1.5/lib/$name" ;;
          esac ;;
        fftw-3.3.10) target="$probe/payload/fftw/3.3.10/lib/$name" ;;
        gromacs-build) target="$probe/payload/gromacs/2025.3/lib64/$name" ;;
      esac
      copy_product "$source" "$target"
    done < "$probe/$component.libraries"
  done
  for item in orte/tools/orterun/orterun orte/tools/orted/orted ompi/tools/ompi_info/ompi_info; do
    name=${item##*/}
    source="$retained/work/openmpi-4.1.5/${item%/*}/.libs/$name"
    test -x "$source"
    copy_product "$source" "$probe/payload/openmpi/4.1.5/bin/$name"
  done
  ln -s orterun "$probe/payload/openmpi/4.1.5/bin/mpirun"
  ln -s orterun "$probe/payload/openmpi/4.1.5/bin/mpiexec"
  find "$retained/work/openmpi-4.1.5" -type f -name 'help-*.txt' -print0 > "$probe/help-files.list"
  while IFS= read -r -d '' source; do
    case "$source" in
      */opal/mca/pmix/pmix3x/pmix/*) target="$probe/payload/openmpi/4.1.5/share/pmix/${source##*/}" ;;
      *) target="$probe/payload/openmpi/4.1.5/share/openmpi/${source##*/}" ;;
    esac
    copy_product "$source" "$target"
  done < "$probe/help-files.list"
  for library in openmpi/4.1.5/lib/libmpi.so openmpi/4.1.5/lib/libopen-rte.so \
      openmpi/4.1.5/lib/libopen-pal.so fftw/3.3.10/lib/libfftw3f.so; do
    test -f "$probe/payload/$library"
  done
  cd "$probe/payload"
  find gromacs openmpi fftw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
  cd "$probe"
  scratch_probe=$(mktemp -d "/scratch/$USER/gmx-runtime-probe.XXXXXXXX")
  printf 'Diagnostic scratch (retained): %s\n' "$scratch_probe"
  mkdir "$scratch_probe/tmp" "$scratch_probe/cache" "$scratch_probe/work"
  export SINGULARITY_TMPDIR="$scratch_probe/tmp" SINGULARITY_CACHEDIR="$scratch_probe/cache"
  singularity build --fakeroot --no-cleanup -B "$scratch_probe/work:/tmp" \
    "$scratch_probe/runtime-probe.sif" gromacs-runtime-probe.def
  mv "$scratch_probe/runtime-probe.sif" "$probe/runtime-probe.sif"
  sha256sum runtime-probe.sif > SIF.sha256
  # Repeat as the ordinary user, with a clean container environment and private /tmp.
  singularity test --cleanenv --contain -B "$scratch_probe/work:/tmp" "$probe/runtime-probe.sif"
  touch "$probe/RUNTIME_PROBE_COMPLETE"
) 2>&1 | tee "$probe/probe.log"
