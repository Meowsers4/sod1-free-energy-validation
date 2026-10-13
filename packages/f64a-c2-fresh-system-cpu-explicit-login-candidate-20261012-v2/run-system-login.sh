#!/bin/bash
set -eo pipefail
if ! shopt -q login_shell; then
  echo 'ERROR: explicit login Bash did not start' >&2
  exit 2
fi
package_dir=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-explicit-login-candidate-20261012-v2
export CUDA_VISIBLE_DEVICES=""
if [[ -z "${MODULEPATH:-}" && -r /etc/profile ]]; then
  source /etc/profile || true
fi
if [[ -z "${MODULEPATH:-}" ]]; then
  echo 'ERROR: SCC login module path unavailable in batch shell' >&2
  exit 2
fi
cd /projectnb/rise-batteries/bode/rise-project
source scripts/scc_env.sh
if [[ "${CONDA_DEFAULT_ENV:-}" != sod1-fep ]]; then
  echo 'ERROR: sod1-fep conda environment did not activate' >&2
  exit 2
fi
python - <<'PY'
import sys
if sys.version_info[:2] < (3, 11):
    raise SystemExit('ERROR: Python 3.11 or newer is required')
import pmx, yaml
print('batch_python=' + sys.executable)
print('batch_python_version=' + sys.version.split()[0])
PY
cd "$package_dir"
export PYTHONDONTWRITEBYTECODE=1
python builder.py prepare --package "$package_dir"
