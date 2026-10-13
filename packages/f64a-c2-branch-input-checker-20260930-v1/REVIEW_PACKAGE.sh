#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
printf 'C2_BRANCH_CPU_CHECKER_PACKAGE_VERIFIED; no job submitted\n'
