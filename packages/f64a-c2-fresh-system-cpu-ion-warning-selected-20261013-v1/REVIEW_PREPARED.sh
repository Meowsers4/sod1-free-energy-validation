#!/bin/bash
set -eo pipefail
cd -- "$(dirname -- "$0")"
package_dir=$PWD
cd /projectnb/rise-batteries/bode/rise-project
source scripts/scc_env.sh
cd "$package_dir"
python builder.py review-prepared --package "$package_dir"
