# F64A C2 isolated r3 CPU system-build candidate

**Update 2026-10-11:** The user ran the read-only SCC checks. `SHA256SUMS` matched `3d81f4c8c077e736919da9e54b7d60bcdcc432748cccf6d21548b76c4b02559d`, `REVIEW_PACKAGE.sh` passed, and `PREFLIGHT_ON_SCC.sh` exited 0. The supplied log reported `cpu_system_source_preflight_pass`, pinned WT/config hashes, seed `2072077476`, the pmx force-field root, host GROMACS 2025.3 and `historical_output_tree_unchanged=true`. No job was submitted. The next action is the separately sealed [inactive execution release review](f64a_c2_fresh_system_cpu_release_candidate.md); the older preflight commands below are retained as historical instructions and should not be rerun.

Status 2026-10-06: the [candidate package](../packages/f64a-c2-fresh-system-cpu-candidate-20261006-v1) is prepared locally for a **read-only SCC preflight**. Its `SHA256SUMS` SHA-256 is `3d81f4c8c077e736919da9e54b7d60bcdcc432748cccf6d21548b76c4b02559d`; [builder](../packages/f64a-c2-fresh-system-cpu-candidate-20261006-v1/builder.py) SHA-256 is `af536bdcd958eeb85bf5429c726dc2fffa70d3977e3f1819bc285f0df48092b2`; [source spec](../packages/f64a-c2-fresh-system-cpu-candidate-20261006-v1/source-spec.json) SHA-256 is `50553cc6eef4c9c306c1429f5832b0a7b33c693ca18c0387f58e9f5a8cae81fb`. `REVIEW_PACKAGE.sh` and three focused tamper/guard tests pass locally; all four shell scripts pass `bash -n`. No agent SCC access occurred.

The user's [read-only SCC source check](f64a_c2_fresh_source_preflight.md) matched the historical config and prepared WT hashes, reproduced all three archived ion seeds, and found no `system_r3` or `w*_r3` paths. The package adds checks for the panel CSV, source modules, older ion-coordinate hashes, pmx force field, and host GROMACS 2025.3. These still need SCC review. A mismatch stops the preflight without changing the historical tree.

The proposed build would use the existing pmx system builder with its output `ROOT` redirected to a **package-local workspace** on `/project`. It would copy the pinned prepared WT, historical config and panel CSV there, derive r3's ion-placement seed `2072077476`, run the normal CPU system construction/minimization, save full external-command output, and require reduced cysteines, no Cu/Zn, 38,414 atoms, 41 NA, 36 CL and an ion-coordinate hash distinct from r0–r2. It would then seal the output and run a separate read-only review. It does not generate lambda-aware state starts or run retained FEP dynamics. The included CPU job draft requests eight slots and one hour with no GPU resource, but **this candidate's `execution_authorized=false` guard rejects the build**. Do not submit the draft job. Any build requires a separately selected package after review.

## Next user-run SCC action: preflight only

From the local Mac terminal, transfer the sealed candidate:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-fresh-system-cpu-candidate-20261006-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then in the user's SCC Bash terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-fresh-system-cpu-candidate-20261006-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash REVIEW_PACKAGE.sh
bash PREFLIGHT_ON_SCC.sh > preflight.log 2>&1
preflight_rc=$?
printf 'preflight_exit=%s\n' "$preflight_rc"
tail -n 45 preflight.log
```

Expected `SHA256SUMS` digest is `3d81f4c8…2559d`. Retain the complete preflight log and paste the digest, exit status, and log tail. This preflight reads the source and software environment; it does **not** submit a job or create a fresh system. If it passes, review a separate execution-selected CPU package before one scheduled technical build. It does not authorize protein production.
