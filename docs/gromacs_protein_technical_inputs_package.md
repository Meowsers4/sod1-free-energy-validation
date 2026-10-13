# F64A folded-protein short-input candidate — CPU preparation only

Stage P candidate `f64a-protein-technical-20260928-v1`, prepared after all 20
historical F64A r0 states reproduced their TPR hashes under the exact r6 SIF.
Spec: [`gromacs_protein_technical_inputs_v1.yaml`](gromacs_protein_technical_inputs_v1.yaml).
Builder: [`gromacs_protein_technical_inputs.py`](../src/analysis/gromacs_protein_technical_inputs.py).
The source/result evidence is in
[`gromacs_protein_source_inventory_result.md`](gromacs_protein_source_inventory_result.md).
This package has **no scheduler script and no GPU execution authorization**.

The candidate keeps F64A r0's apo-2SH hybrid topology, coordinates, pmx force
field, 20-value lambda vector, timestep, PME, constraints, NPT and soft-core
settings. Each state starts from its own historical lambda-minimized `em.gro`.
The builder changes only registered time/output MDP values: 2,000 steps total,
first stop at 1,000, exchange interval 100, energy/DHDL/log stride 100 and
compressed-coordinate stride 200. These steps are a technical check (4 ps at
the historical 2 fs timestep), not equilibration or a free-energy estimate.
The first stop, exchange interval and candidate one-L40S/20-rank layout remain
in the spec for a later runtime package; this CPU builder does not launch MD.

## Fail-closed preparation

The builder verifies the saved source-inventory hashes, pipeline hash, reduced
source selection, identical physical MDP settings, source state indices and
lambda vector, and r6 SIF SHA-256 before creating `prepared/`. It copies only
the hybrid topology, local position restraints, 20 MDPs and minimized starts,
and a snapshot of the pmx force-field root. It then performs no-`-maxwarn`
`grompp` for all states inside r6, with the force-field snapshot mounted at
the original absolute include path. A warning, timeout or failure stops the
package and leaves its logs. Successful preparation writes `PREPARED.json` and
`SHA256SUMS`; review must verify every sealed file before any runtime design.
The long-duration historical TPRs are never copied into the candidate inputs.
Local checks: two targeted MDP tests passed, a 20-state builder orchestration
rehearsal passed with a fake Singularity command, and force-field snapshot hash
comparison passed. The rehearsal did not run GROMACS; exact-r6 short-input
`grompp` remains for SCC.

The source spec and builder are currently local and uncommitted; they must be
transferred as exact files. Do not `git pull` to obtain them or modify the SCC
historical tree. On SCC, create the fresh package directory once:

Expected transfer SHA-256 values: builder
`bebb3fc721db97895191e6ed53c589126a0e2ac6c9433433add804868bf90987`;
source spec
`155a24a60191334c0c06a3e02d3c21ecf51cea0902f5ebe5e53370b3c6c322cf`.

```bash
mkdir /projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1
```

In a Mac terminal, from the repository root, copy the two files:

```bash
scp src/analysis/gromacs_protein_technical_inputs.py \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1/builder.py
scp docs/gromacs_protein_technical_inputs_v1.yaml \
  bodeb@scc1.bu.edu:/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1/source-spec.yaml
```

On `scc-i01`, from the repository root in the `sod1-fep` environment, compare
both transferred hashes against those reported locally, then prepare once:

```bash
cd /projectnb/rise-batteries/bode/rise-project || exit
source scripts/scc_env.sh || exit
PKG=/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1
sha256sum "$PKG/builder.py" "$PKG/source-spec.yaml"
python "$PKG/builder.py" --spec "$PKG/source-spec.yaml" --package "$PKG" \
  > "$PKG/prepare.log" 2>&1
prep_rc=$?
printf 'prepare_exit=%s\n' "$prep_rc"
tail -n 100 "$PKG/prepare.log"
```

If `prepare_exit` is nonzero, keep the package and log, and stop; do not remove
`prepared/` or retry in place. On success, review with:

```bash
cd "$PKG/prepared" && sha256sum -c SHA256SUMS
python - "$PKG/prepared/PREPARED.json" <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
print('status=', d['status'], 'states=', len(d['states']),
      'execution_authorized=', d['execution_authorized'])
print('source_inventory_sha256=', d['source_inventory_sha256'])
print('sif_sha256=', d['sif_sha256'])
print('elapsed_seconds=', d['elapsed_seconds'])
PY
```

Return the transfer hashes, preparation status/log tail, manifest-check result
and `PREPARED.json` summary. No protein GPU test should be submitted from this
package. The runtime package still needs protein-specific exchange/restart and
energy validators, a measured storage/runtime estimate, a fixed walltime and a
separate single-attempt admission.

## SCC preparation accepted

On 2026-09-28, the user reported that both transferred file hashes matched the
values above. The SCC builder printed short TPR SHA-256 values for states 0–19
and `F64A_PROTEIN_SHORT_TPRS_CPU_PREPARED_PENDING_REVIEW`. The reported
`PREPARED.json` has `status=cpu_inputs_prepared_pending_review`, 20 states, 20
total GROMACS notes and 21.712 seconds elapsed. Its source inventory SHA-256 is
`c908e1c1695e0ebe8bd02dce2fece5bdbc83332d617528ca81495bd826c51fe2`;
the spec and SIF hashes match this plan. Both authorization fields are false.
The subsequent manifest check exited 0 for all 344 entries. The SHA-256 of
`SHA256SUMS` is
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
The CPU inputs are accepted; see the [result](gromacs_protein_technical_inputs_result.md).
No GPU execution follows from CPU preparation.
