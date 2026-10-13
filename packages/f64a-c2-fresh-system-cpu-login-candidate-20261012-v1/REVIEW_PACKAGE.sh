#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python builder.py verify-package --package "$PWD"
