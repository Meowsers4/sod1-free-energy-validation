#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
bash REVIEW_PACKAGE.sh
/usr/libexec/platform-python preflight.py run --package "$PWD"
