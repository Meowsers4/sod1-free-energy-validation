#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python builder.py import --package "$PWD"
