#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
python builder.py review-package --package "$PWD"
