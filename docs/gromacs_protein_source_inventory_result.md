# F64A folded source inventory — supplied SCC result, 2026-09-28

The user ran the read-only `scripts/inventory_f64a_protein_source.py` on
`scc-i01` from `/projectnb/rise-batteries/bode/rise-project` and supplied its
summary. Script SHA-256 matched the local reviewed file:
`0860331c71bc40017f0598f8b8ff34640e1058d9b7a13103c4e4113985c14475`.
The reported exit status was **0**. The full JSON remains on SCC at
`/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-inventory-20260928/f64a_protein_source_inventory.json`;
it has not been downloaded or independently rehashed locally.

Source root:
`/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded`.
The reported config SHA-256 `af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29`
matches the local `config/pipeline.yaml` hash checked after receipt.

| Check | Supplied result |
| --- | --- |
| States / missing files | 20 / none |
| Complete inventory | true |
| Shared lambda vector / matches config | true / true |
| State indices / shared MDP physics | true / true |
| All-state energies requested | true |
| F64A folded r0 system marker | true |

The user supplied SHA-256 values for `system_r0/SYSTEM_READY`, `conf.gro`,
`em.gro`, `hybrid.top`, and the `em.gro`/`prod.tpr` pair for each of the 20
windows. The system hashes are:

| File | SHA-256 |
| --- | --- |
| `SYSTEM_READY` | `385b378a54574b93d9decc4d781519218f844063a13d17bf0ff18220378940df` |
| `conf.gro` | `62153c8c5c5263ff2156fad5add20db3486d3fca1de4a6db7e7a68fbad61e9b2` |
| `em.gro` | `c208023feb47b9c7c9835acfdf50299bda32d2d09fc15af8838e92eb29e3ae55` |
| `hybrid.top` | `13ed733e316238ccff5e2710c96a6e4c5e32070fa6237c9c3d397529f951aae5` |

The supplied endpoint MDPs both specify the same 20-value vector, 0 through 1,
2 fs timestep, PME, H-bond constraints, C-rescale pressure coupling, Beutler
soft core (`sc-alpha=0.3`, `sc-power=1`, `sc-sigma=0.25`, `sc-coul=yes`), free
energy enabled and `calc-lambda-neighbors=-1`; their active state indices are
0 and 19 respectively. Each historical production TPR is a provenance file,
**not** a compatible r6 execution input.

This accepts the **source-file inventory gate on user-supplied evidence**. It
does not yet establish topology include closure, exact force-field availability
inside the r6 preparation environment, reduced-cysteine chemistry on these
coordinates, apo metal absence, new TPR compatibility or protein GPU runtime.
The next action is read-only topology/chemistry inspection, followed by a fresh
isolated CPU-only preparation package if that inspection passes. No protein
GPU attempt or production arm is admitted by this result.

## Next read-only check on `scc-i01`

From `/projectnb/rise-batteries/bode/rise-project` in the `sod1-fep` environment:

```bash
python - <<'PY'
from pathlib import Path
import re
import yaml
from src.fep.pmx_engine import assert_topology_disulfide_free, pmx_ff_dir

root = Path('/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded/system_r0')
top = root / 'hybrid.top'
with open('config/pipeline.yaml') as f:
    cfg = yaml.safe_load(f)

for name in ('conf.gro', 'em.gro'):
    gro = root / name
    assert_topology_disulfide_free(top, gro)
    atoms = gro.read_text().splitlines()[2:-1]
    metals = [line[:15].strip() for line in atoms
              if line[5:10].strip().upper().startswith(('CU', 'ZN'))]
    print(name, 'reduced_cysteines=PASS', 'Cu_Zn_atoms=', metals)

ffroot = pmx_ff_dir(cfg)
print('pmx_forcefield_root=', ffroot)
print('forcefield_exists=', (ffroot / (cfg['fep']['pmx_forcefield'] + '.ff')).is_dir())
for line in top.read_text().splitlines():
    match = re.match(r'\s*#include\s+["<]([^">]+)[">]', line)
    if match:
        name = match.group(1)
        found = [str(p) for p in (root / name, ffroot / name) if p.is_file()]
        print('include', name, 'resolved=', found)
PY
```

This reports only the direct includes of `hybrid.top`. Resolve their recursive
includes and exact-SIF visibility before `grompp`; do not treat this command's
pass as an r6 compatibility result.

## Supplied topology/chemistry check

The user ran the read-only command on `scc-i01` and supplied:

- `conf.gro` and `em.gro`: `reduced_cysteines=PASS`, `Cu_Zn_atoms=[]`.
- Host pmx force-field root:
  `/projectnb/rise-batteries/bode/.conda/envs/sod1-fep/lib/python3.11/site-packages/pmx/data/mutff`;
  `amber99sb-star-ildn-mut.ff` exists.
- Direct includes all resolved on the host: forcefield.itp under that pmx
  force field, `system_r0/posre.itp`, and absolute-path `tip3p.itp` and
  `ions.itp` under the same pmx force field.

The reduced-cysteine check uses the project's existing
`assert_topology_disulfide_free` guard against `hybrid.top` and each coordinate
file. The reported absence of Cu/Zn is based on residue names in those GRO
files. This accepts the read-only source chemistry/direct-include gate on
user-supplied output. Recursive include closure and visibility of the host pmx
force field inside r6 remain unverified; no TPR has been rebuilt.

## Next exact-r6 visibility check

On `scc-i01`, with no GPU allocation, run:

```bash
SRC=/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded
FF=/projectnb/rise-batteries/bode/.conda/envs/sod1-fep/lib/python3.11/site-packages/pmx/data/mutff
SIF=/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gromacs-2025.3-mpi-cuda-l40s.sif

SINGULARITYENV_GMXLIB="$FF" singularity exec --cleanenv --contain \
  --no-mount bind-paths,hostfs,cwd,tmp \
  --bind "$SRC:/protein:ro" --bind "$FF:$FF:ro" \
  --pwd /protein "$SIF" /bin/sh -c '
    set -eu
    test -r /protein/system_r0/hybrid.top
    test -r /protein/system_r0/posre.itp
    test -r /protein/w0_r0/em.gro
    test -r "$GMXLIB/amber99sb-star-ildn-mut.ff/forcefield.itp"
    test -r "$GMXLIB/amber99sb-star-ildn-mut.ff/tip3p.itp"
    test -r "$GMXLIB/amber99sb-star-ildn-mut.ff/ions.itp"
    printf "R6_PROTEIN_SOURCE_AND_DIRECT_INCLUDES_VISIBLE\nGMXLIB=%s\n" "$GMXLIB"
  '
printf 'visibility_exit=%s\n' "$?"
```

This checks direct file visibility in the exact image and does not create a
TPR. The full topology include graph and GROMACS input warnings remain for a
separate CPU-only `grompp` preparation check.

The user subsequently reported
`R6_PROTEIN_SOURCE_AND_DIRECT_INCLUDES_VISIBLE`, the expected `GMXLIB` path,
and `visibility_exit=0` from `scc-i01`. This accepts direct source/include
visibility inside the exact r6 image on user-supplied output. The host pmx
directory remains an external, explicitly mounted dependency; the SIF alone
does not carry this protein force field. No TPR was created by this check.

## Next: one-state exact-r6 CPU `grompp` probe

This is a one-time **input compatibility probe**, not an MD run or a production
TPR. It uses the historical state-0 MDP and lambda-minimized coordinate only
to test the complete topology include graph and GROMACS input validation. It
writes to a fresh isolated directory, never to the historical F64A tree. Do not
use `-maxwarn` or continue to other states if this reports a warning/error.

On `scc-i01`:

```bash
cd /projectnb/rise-batteries/bode/rise-project || exit
source scripts/scc_env.sh || exit
SRC=/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded
FF=/projectnb/rise-batteries/bode/.conda/envs/sod1-fep/lib/python3.11/site-packages/pmx/data/mutff
SIF=/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gromacs-2025.3-mpi-cuda-l40s.sif
PROBE=/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-inventory-20260928/r6-grompp-w0
mkdir "$PROBE" || exit
sha256sum "$SRC/system_r0/hybrid.top" "$SRC/w0_r0/em.gro" "$SRC/w0_r0/prod.mdp"
SINGULARITYENV_GMXLIB="$FF" SINGULARITYENV_GMX_MAXBACKUP=-1 \
singularity exec --cleanenv --contain \
  --no-mount bind-paths,hostfs,cwd,tmp \
  --bind "$SRC:/protein:ro" --bind "$FF:$FF:ro" --bind "$PROBE:/tmp" \
  --pwd /tmp "$SIF" /opt/gromacs/2025.3/bin/gmx_mpi grompp \
  -f /protein/w0_r0/prod.mdp -c /protein/w0_r0/em.gro \
  -p /protein/system_r0/hybrid.top -o /tmp/w0.tpr \
  > "$PROBE/grompp.log" 2>&1
probe_rc=$?
printf 'grompp_exit=%s\n' "$probe_rc"
cat "$PROBE/grompp.log"
if [ "$probe_rc" -eq 0 ]; then
  sha256sum "$PROBE/w0.tpr" "$PROBE/mdout.mdp"
fi
```

Retain the probe directory and full log whether it passes or fails. A zero
exit without warnings would permit designing a fresh short-run MDP and
preparing all 20 exact-r6 TPRs in a new sealed package; it would not authorize
protein GPU execution or validate the scientific protocol.

## State-0 r6 probe result

The user supplied the `grompp` output and the conditional SHA-256 output from
the one-time `r6-grompp-w0` directory. Because the conditional hash block ran,
`probe_rc` was zero, although the `grompp_exit=0` line itself was not included
in the pasted excerpt. GROMACS 2025.3 generated the TPR without `-maxwarn` and
reported **two NOTES, zero WARNINGs**: a small PME soft-core cutoff effect and
`nstcomm < nstcalcenergy` overhead. The log identified 153 protein residues,
12,048 waters, 77 ions, PME grid 64³ and an approximately 9 MB output estimate
for the historical 1,750,000-step MDP. These are input-preparation observations,
not protein dynamics or a runtime/cost measurement.

| Output | Supplied SHA-256 |
| --- | --- |
| `r6-grompp-w0/w0.tpr` | `c6ce0e0e18b08564bb95a9597073ce5a36890ffb7fc4539a548905eec41bf7cf` |
| `r6-grompp-w0/mdout.mdp` | `436a9d56e951b5b7ad40f86f4246f9eddf99275ab35d094b9aa2e3bbffdc0824` |

The new state-0 TPR hash is **identical** to the historical `w0_r0/prod.tpr`
hash reported by the source inventory. This is strong evidence that the exact
r6 build reproduces this specific GROMACS input, but it does not establish that
the other 19 states or a shortened technical MDP have been prepared. The
OpenMPI notice about unavailable `libcuda.so.1` occurred on the CPU build host;
it is not a GROMACS input warning and does not contradict the earlier GPU
qualification on L40S. Do not suppress it for this record or infer GPU behavior
from this CPU probe.

## Next: remaining 19-state CPU compatibility sweep

The state-0 probe passed. The next bounded CPU-only check rebuilds states 1–19
under r6 from their historical MDPs and lambda-minimized coordinates. It does
not run MD and its long-duration TPRs must not be submitted as a protein
qualification. The script below first requires the source inventory to be
byte-identical to the saved JSON, then creates a fresh sweep directory. Each
new TPR must match its historical source hash; any GROMACS warning, failure or
hash mismatch stops the sweep without a retry. All per-state logs remain on
SCC. State 0 is not repeated.

```bash
bash <<'BASH'
cd /projectnb/rise-batteries/bode/rise-project || exit
set +u
source scripts/scc_env.sh || exit
set -euo pipefail
SRC=/projectnb/rise-batteries/bode/rise-project/results/fep/F64A/folded
FF=/projectnb/rise-batteries/bode/.conda/envs/sod1-fep/lib/python3.11/site-packages/pmx/data/mutff
SIF=/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj/gromacs-2025.3-mpi-cuda-l40s.sif
INV=/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-inventory-20260928
SWEEP="$INV/r6-grompp-sweep-w1-w19"
mkdir "$SWEEP"
python "$INV/inventory_f64a_protein_source.py" --source "$SRC" \
  --config config/pipeline.yaml --repeat 0 > "$SWEEP/source-recheck.json"
cmp "$INV/f64a_protein_source_inventory.json" "$SWEEP/source-recheck.json"
for i in $(seq 1 19); do
  OUT="$SWEEP/w$i"
  mkdir "$OUT"
  if ! SINGULARITYENV_GMXLIB="$FF" SINGULARITYENV_GMX_MAXBACKUP=-1 \
    singularity exec --cleanenv --contain \
      --no-mount bind-paths,hostfs,cwd,tmp \
      --bind "$SRC:/protein:ro" --bind "$FF:$FF:ro" --bind "$OUT:/tmp" \
      --pwd /tmp "$SIF" /opt/gromacs/2025.3/bin/gmx_mpi grompp \
      -f "/protein/w${i}_r0/prod.mdp" -c "/protein/w${i}_r0/em.gro" \
      -p /protein/system_r0/hybrid.top -o "/tmp/w${i}.tpr" \
      > "$OUT/grompp.log" 2>&1; then
    echo "state $i grompp failed; preserve $OUT" >&2
    tail -n 80 "$OUT/grompp.log" >&2
    exit 1
  fi
  if grep -Eq '^[[:space:]]*WARNING' "$OUT/grompp.log"; then
    echo "state $i warning; preserve $OUT" >&2
    tail -n 80 "$OUT/grompp.log" >&2
    exit 1
  fi
  expected=$(python - "$INV/f64a_protein_source_inventory.json" "$i" <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
print(d['windows']['w{}_r0'.format(sys.argv[2])]['files']['prod.tpr']['sha256'])
PY
)
  actual=$(sha256sum "$OUT/w${i}.tpr" | awk '{print $1}')
  if [ "$actual" != "$expected" ]; then
    echo "state $i TPR hash mismatch: $actual != $expected; preserve $OUT" >&2
    exit 1
  fi
  printf 'state=%s grompp=pass tpr_sha256=%s\n' "$i" "$actual"
done
echo 'R6_F64A_W1_TO_W19_CPU_COMPATIBILITY_PASS'
BASH
```

Report the complete terminal output and preserve `SWEEP`. The source inventory
JSON and logs provide the detailed provenance; the final marker is only a
summary. No GPU or production authorization follows from this CPU check.

The first user paste of the sweep stopped while sourcing `scripts/scc_env.sh`:
the original block enabled `set -u` before the sourced GROMACS `GMXRC`, whose
`shell` and `GMXLDLIB` variables were unset. The supplied trace contains no
`grompp` or `mkdir` output; the command above is corrected to source the
environment before strict shell mode. `mkdir "$SWEEP"` remains a fresh-path
guard, so do not remove it if an unexpected directory already exists. No
state-1–19 result has been reported.

## Completed 19-state r6 compatibility sweep

The corrected sweep returned `state=1` through `state=19`, each with
`grompp=pass` and a TPR SHA-256 matching the corresponding source-inventory
TPR hash, followed by `R6_F64A_W1_TO_W19_CPU_COMPATIBILITY_PASS`. The script
could reach that marker only after its fresh source inventory matched the
saved JSON byte-for-byte and every per-state no-`-maxwarn` `grompp` completed
without a logged `WARNING` or TPR hash mismatch. State 0 had already passed
separately with the same hash equality. Therefore all 20 historical F64A r0
states are accepted for **CPU input compatibility with the exact r6 image** on
the user-supplied SCC output. No rerun is needed.

Sweep directory:
`/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-inventory-20260928/r6-grompp-sweep-w1-w19`.
Preserve its source recheck JSON, all 19 `grompp.log` files, new TPRs and
`mdout.mdp` files alongside the state-0 probe and original inventory JSON.
The agent has not downloaded these binaries/logs or independently rehashed
them locally. Hash equality is a strong build/input identity check, not an
exchange, restart, GPU-memory, performance or scientific convergence result.
These historical TPRs contain 1,750,000 steps and are **not** the bounded
protein technical test inputs. A fresh short-run package and its own admission
checks are required before any protein GPU job.
