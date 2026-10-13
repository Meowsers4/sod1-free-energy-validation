#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd -- "$(dirname -- "$0")"
bash REVIEW_PACKAGE.sh
/usr/libexec/platform-python runtime.py review
