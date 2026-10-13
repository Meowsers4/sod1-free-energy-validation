#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python builder.py review-package --package "$PWD"
