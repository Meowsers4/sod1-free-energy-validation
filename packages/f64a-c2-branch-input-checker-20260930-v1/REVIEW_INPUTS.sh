#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [ "$#" -ne 2 ]; then
  printf 'usage: %s ROOT PLAN.json\n' "$0" >&2
  exit 2
fi
bash REVIEW_PACKAGE.sh
exec python branch_input_checker.py --root "$1" --plan "$2"
