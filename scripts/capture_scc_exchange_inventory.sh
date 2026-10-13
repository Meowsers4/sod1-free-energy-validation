#!/usr/bin/env bash
# Read-only SCC inventory for C1 GROMACS HREX feasibility.
#
# This script writes only to standard output. It does not submit jobs, start an
# interactive allocation, load a GROMACS module, compile software, or alter files.
# It does load the installed compiler/MKL/CUDA/OpenMPI runtime modules in this
# temporary probe shell so the packaged executables can print their build metadata.
# Run it on an SCC login node and return the complete output.

set -uo pipefail
inventory_incomplete=0

section() {
  printf '\n===== %s =====\n' "$1"
}

run() {
  printf '\n$'
  printf ' %q' "$@"
  printf '\n'
  "$@" 2>&1
  local status=$?
  if [[ ${status} -ne 0 ]]; then
    printf '[exit status %d]\n' "${status}"
  fi
  return 0
}

section "snapshot identity"
run hostname -f
run date -u +%Y-%m-%dT%H:%M:%SZ
run uname -srm

section "SCC login environment"
printf 'SGE_ROOT=%s\n' "${SGE_ROOT:-<unset>}"
printf 'SGE_CELL=%s\n' "${SGE_CELL:-<unset>}"
printf 'MODULEPATH=%s\n' "${MODULEPATH:-<unset>}"
if [[ -z "${SGE_ROOT:-}" || -z "${MODULEPATH:-}" ]]; then
  inventory_incomplete=1
  printf 'INCOMPLETE: rerun through an SCC login shell (bash -l -s).\n'
fi

section "Lmod discovery"
if ! type module >/dev/null 2>&1; then
  if [[ -f /usr/local/lmod/8.7.12/init/bash ]]; then
    # shellcheck disable=SC1091
    source /usr/local/lmod/8.7.12/init/bash
  fi
fi
if type module >/dev/null 2>&1; then
  run type module
  run module --version
  run module spider gromacs/2025.3
  run module avail gromacs

  section "runtime modules for executable metadata"
  for runtime_module in cuda/12.8 intel/2024.0 gcc/12.2.0; do
    printf '\n$ module load %q\n' "${runtime_module}"
    module load "${runtime_module}" 2>&1 || inventory_incomplete=1
  done
  printf '\n$ module load openmpi/4.1.5_gnu-12.2.0\n'
  if ! module load openmpi/4.1.5_gnu-12.2.0 2>&1; then
    printf '\n$ module load openmpi\n'
    module load openmpi 2>&1 || inventory_incomplete=1
  fi
  run module list
else
  inventory_incomplete=1
  printf 'module command unavailable after the pinned Lmod bootstrap\n'
fi

section "Grid Engine parallel environments"
if command -v qconf >/dev/null 2>&1; then
  run command -v qconf
  pe_names="$(qconf -spl 2>&1)"
  printf '\n$ qconf -spl\n%s\n' "${pe_names}"
  while IFS= read -r pe_name; do
    [[ -z "${pe_name}" || "${pe_name}" == *" "* || "${pe_name}" == error:* ]] && continue
    run qconf -sp "${pe_name}"
  done <<< "${pe_names}"
else
  inventory_incomplete=1
  printf 'qconf unavailable\n'
fi

section "Grid Engine GPU complexes and L40S queues"
if command -v qconf >/dev/null 2>&1; then
  printf '\n$ qconf -sc | GPU-related rows\n'
  qconf -sc 2>&1 | awk '
    NR <= 2 || tolower($0) ~ /(^|[[:space:]_])(gpu|cuda)/ || tolower($0) ~ /gpu_/ {print}
  '
  queue_names="$(qconf -sql 2>&1)"
  printf '\n$ qconf -sql\n%s\n' "${queue_names}"
  while IFS= read -r queue_name; do
    [[ "${queue_name}" == *l40s* ]] || continue
    run qconf -sq "${queue_name}"
  done <<< "${queue_names}"
fi
if command -v qhost >/dev/null 2>&1; then
  run qhost -q -F gpus,gpu_c,gpu_type
else
  inventory_incomplete=1
  printf 'qhost unavailable\n'
fi

section "GROMACS 2025.3 executable inventory"
gmx_root=/share/pkg.8/gromacs/2025.3
printf 'search root: %s\n' "${gmx_root}"
if [[ -d "${gmx_root}" ]]; then
  while IFS= read -r binary; do
    section "binary ${binary}"
    run readlink -f "${binary}"
    run "${binary}" --version
    if command -v ldd >/dev/null 2>&1; then
      printf '\n$ ldd %q | MPI/CUDA-related rows\n' "${binary}"
      ldd "${binary}" 2>&1 | awk '
        tolower($0) ~ /mpi|cuda|cudart|nvrtc|ucx|libgomp|libiomp/ {print}
      '
    fi
    if [[ "$(basename "${binary}")" == gmx_mpi ]]; then
      printf '\n$ %q mdrun -h | exchange/runtime option rows\n' "${binary}"
      "${binary}" mdrun -h 2>&1 | awk '
        /-multidir|-replex|-reseed|-gputasks|-gpu_id|-cpi|-cpo|-append|-maxh/ {print}
      '
    fi
  done < <(
    find "${gmx_root}" -maxdepth 4 -type f -perm -111 \
      \( -name gmx -o -name gmx_mpi \) -print | sort
  )
else
  printf '%s is unavailable\n' "${gmx_root}"
fi

section "PATH-visible MPI launchers and GROMACS"
for executable in mpirun mpiexec gmx_mpi gmx; do
  if command -v "${executable}" >/dev/null 2>&1; then
    run command -v "${executable}"
    case "${executable}" in
      mpirun|mpiexec) run "${executable}" --version ;;
      gmx_mpi|gmx) run "${executable}" --version ;;
    esac
  else
    printf '%s: not on PATH\n' "${executable}"
  fi
done

section "inventory complete"
printf 'No job was submitted and no allocation was requested.\n'
if [[ ${inventory_incomplete} -ne 0 ]]; then
  printf 'INCOMPLETE: one or more environment/runtime queries failed; preserve the output and rerun as documented.\n'
else
  printf 'All read-only inventory sections completed.\n'
fi
