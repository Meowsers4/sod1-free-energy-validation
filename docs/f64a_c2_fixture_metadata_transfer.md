# C2 fixture metadata subset for local schema review

Status 2026-10-05: the user transferred the archive, and the local read-only [checker](../src/analysis/f64a_c2_fixture_metadata_bundle.py) passed. See the [recorded result](f64a_c2_fixture_metadata_result.md). The commands below are retained as a provenance recipe; no repeat transfer is needed. This follows the accepted [live fixture 7865574](f64a_c2_branch_fixture_result.md) and the completed [Stage P full-ladder parser review](f64a_c2_stage_p_full_ladder_result.md). It is a technical production-schema rehearsal, not selection of scientific C2 production.

The proposed bundle copies only ten small JSON files: the 1611-entry post-accounting hash manifest; its 1608-entry pre-accounting predecessor; `status.json`; `accounting.json`; `common-seal.json`; `branch-input-seal.json`; the three phase-review JSONs; and `branch-inputs/plan.json`. The checker pins the post-accounting manifest by its SCC SHA-256, rehashes the other nine copied files against it, checks all 20 common-to-baseline/HREX checkpoint identities in the nested seals, and replays the three saved HREX exchange permutations. It does **not** rehash untransferred checkpoint, TPR, trajectory or coordinate binaries. The accepted SCC runtime and accounting checks already cover those files.

The user ran the following in a **Bash SCC terminal**. It reads the accepted attempt and writes one tarball under `/project`; it does not submit a job or modify the attempt:

```bash
ATTEMPT=/project/rise-batteries/bode/container-build-packages/f64a-c2-branch-fixture-execution-selected-20261003-v1/attempt
OUT=/project/rise-batteries/bode/container-build-packages/f64a-c2-fixture-metadata-7865574-20261004.tar.gz
files=(output-hashes-after-accounting.json output-hashes.json status.json accounting.json common-seal.json branch-input-seal.json common-review.json baseline-review.json hrex-review.json branch-inputs/plan.json)
tar -C "$ATTEMPT" -czf "$OUT" "${files[@]}" || exit
sha256sum "$ATTEMPT/output-hashes-after-accounting.json" "$OUT"
ls -lh "$OUT"
```

The user then copied the archive from the **local Mac terminal**:

```bash
mkdir -p /Users/bodebosell/sod1fep/data/fixture_bundles
scp bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/f64a-c2-fixture-metadata-7865574-20261004.tar.gz /Users/bodebosell/sod1fep/data/fixture_bundles/
```

The supplied SCC SHA-256 lines matched the local archive and manifest. No new GPU work, scientific threshold or production arm was authorized by this transfer.
