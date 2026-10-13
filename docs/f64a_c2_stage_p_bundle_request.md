# Stage P full-ladder XVG transfer for local C2 parser review

Status 2026-10-04: **transfer and local full-ladder review completed**; see the [result](f64a_c2_stage_p_full_ladder_result.md). No agent SCC access or job submission occurred. The accepted [Stage P job 7791102](gromacs_protein_runtime_result.md) has 20 short `smoke.xvg` files and an `output-hashes.json` manifest with 614 entries. The [read-only checker](../src/analysis/f64a_c2_stage_p_bundle.py) verifies the original manifest's pinned SHA-256, rehashes the 20 transferred XVGs and status file against it, validates all 20 state labels, temperatures, lambda vectors and 4-ps grids, and independently compares every state to alchemlyb. It explicitly does **not** claim to recheck the 593 untransferred manifest entries; the accepted SCC evidence already reports that full check.

When ready, the user can run this in a **Bash SCC terminal**. It only reads the accepted attempt and writes one small tarball under `/project`:

```bash
ATTEMPT=/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-runtime-20260928-v1/attempt
OUT=/project/rise-batteries/bode/container-build-packages/f64a-stage-p-xvg-7791102-20261004.tar.gz
files=(output-hashes.json status.json)
for i in {00..19}; do files+=("state${i}/smoke.xvg"); done
tar -C "$ATTEMPT" -czf "$OUT" "${files[@]}" || exit
sha256sum "$ATTEMPT/output-hashes.json" "$OUT"
ls -lh "$OUT"
```

Then from a **local Mac terminal**, copy the tarball into the shared workspace through BU's published `scc1.bu.edu` login hostname. The earlier `scc` alias suggestion was wrong for this Mac; it produced `Could not resolve hostname scc` and did not transfer a file.

```bash
mkdir -p /Users/bodebosell/sod1fep/data/fixture_bundles
scp bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/f64a-stage-p-xvg-7791102-20261004.tar.gz /Users/bodebosell/sod1fep/data/fixture_bundles/
```

Report the two SHA-256 lines printed on SCC. The agent can then inspect the local tarball, extract it into a private temporary directory, run the parser and independent full-ladder comparison, and record the result without logging into SCC. The tarball is a subset export for analysis, not a new runtime package, rerun or production authorization.
