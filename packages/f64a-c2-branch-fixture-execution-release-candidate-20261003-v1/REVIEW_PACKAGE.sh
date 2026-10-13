#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd -- "$(dirname -- "$0")"
sha256sum -c SHA256SUMS
/usr/libexec/platform-python runtime.py verify-package
