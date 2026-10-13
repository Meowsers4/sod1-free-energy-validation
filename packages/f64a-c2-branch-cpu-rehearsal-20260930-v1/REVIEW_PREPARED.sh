#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
bash REVIEW_PACKAGE.sh
python builder.py review --package "$PWD"
