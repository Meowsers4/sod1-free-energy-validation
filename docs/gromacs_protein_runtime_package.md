# F64A protein technical runtime candidate — SCC import and review

This package imports the [accepted Stage P CPU short inputs](gromacs_protein_technical_inputs_result.md)
and adapts the [accepted synthetic Stage L mechanics](gromacs_gpu_ladder_result.md)
to real protein. It does not rebuild TPRs. The resource/validation contract is
in [the runtime design](gromacs_protein_runtime_design.md) and
[`gromacs_protein_runtime_v1.yaml`](gromacs_protein_runtime_v1.yaml).

**No protein GPU submission is authorized by package creation, transfer,
queue validation or CPU import.** `SUBMIT_ON_SCC.sh` is present for concrete
review but must not be run until a separate one-attempt decision. Preserve the
Stage P source and this package, including any partial import.

## Transfer and read-only/CPU checks

From a **Mac terminal**, copy the exact local package directory:

```bash
scp -r /Users/bodebosell/sod1fep/results/gpu_smoke_packages/f64a-protein-technical-runtime-20260928-v1 \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/
```

From an **SCC terminal**, validate the queue request and import once:

```bash
PKG=/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-runtime-20260928-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash VALIDATE_QUEUE_ON_SCC.sh
bash IMPORT_ON_SCC.sh > import.log 2>&1
import_rc=$?
printf 'import_exit=%s\n' "$import_rc"
tail -n 60 import.log
```

`VALIDATE_QUEUE_ON_SCC.sh` uses `qsub -w v` only; it does not submit. The import
checks every Stage P source manifest entry, its expected manifest/SIF/spec
hashes, 20 TPR hashes and common GRO atom labels/order. It copies the short
TPRs into a new `prepared/` directory, obtains CPU-only `gmx dump -s` metadata
with exact r6, checks state/lambda/atom/time identity and seals all copied files.
It runs no MD, MPS or GPU task. If `prepared/` already exists or import fails,
stop and preserve it; do not delete the fresh-directory guard or retry in place.

If import succeeds, review:

```bash
cd "$PKG" || exit
bash REVIEW_ON_SCC.sh
sha256sum -c SHA256SUMS > package-check.log 2>&1
printf 'package_check_exit=%s\n' "$?"
python - <<'PY'
import json
with open('prepared/PREPARED.json') as stream:
    record = json.load(stream)
print('imported_states=', len(record['tpr_sha256']))
print('source_manifest_sha256=', record['source_manifest_sha256'])
print('package_manifest_sha256=', record['package_manifest_sha256'])
print('gpu_executed=', record['gpu_executed'])
PY
```

Report the package manifest hash, queue validation, import exit/log tail and
review output. The reviewed package can then be considered for one bounded GPU
attempt. The technical pass criteria require 20 states, complete exchange
attempt coverage and permutations, two matching 20-client MPS records, correct
whole-ladder restart, finite all-state energies, preserved first-phase outputs,
cleanup and `qacct` `failed 0`/`exit_status 0`. Zero accepted swaps on a protein
link is allowed. Production and scientific convergence remain unvalidated.
