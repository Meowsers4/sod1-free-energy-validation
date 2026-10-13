#!/bin/bash
set -eo pipefail
cd -- "$(dirname -- "$0")"
package_dir=$PWD
python builder.py verify-package --package "$package_dir"
cd /projectnb/rise-batteries/bode/rise-project
source scripts/scc_env.sh
cd "$package_dir"
python builder.py preflight --package "$package_dir"
