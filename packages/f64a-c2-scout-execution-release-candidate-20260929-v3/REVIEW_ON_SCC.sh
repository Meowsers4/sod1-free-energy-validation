#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONDONTWRITEBYTECODE=1
bash REVIEW_PACKAGE.sh
exec /usr/libexec/platform-python runtime.py review
