#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
echo 'C2_SCOUT_EXECUTION_PREFLIGHT_PACKAGE_VERIFIED; no job submitted'
