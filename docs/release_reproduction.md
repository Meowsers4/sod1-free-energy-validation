# Verify or reproduce the historical publication-review snapshot

## Current status — 2026-09-18

The existing September 14 bundle is **immutable historical evidence**, not the
current repo or a current F64A release. It contains 1217 inventoried files and no
`docs/temporal_review/`, pilot packages or v2 continuation report. Its recorded
transport SHA-256 remains
`09cc1b2c7575b60afa1af38216b78ca8f126a668b83aa6ef283c06ff8eba7114`.
New evidence in the checkout does not silently update this bundle or checksum.

The original schema-1 manifest did **not record a build commit**. Its corrected
`src/analysis/methods_figures.py` bytes match repository commit **83c39bb**, SHA-256
`707dd46ce73a4f823a06f7af535f21de9bedd82a43afb3929ea68f6661a70b5f`.
This is a retrospective source-file match, **not** a claim that the old complete
bundle was built at that commit. New schema-2 builds record a clean, committed
executable/config/environment inventory; refuse uncommitted sources and existing
bundle/checksum/partial/lock paths; verify the temporary archive before publication.

In the current checkout, bare `snakemake` **only verifies** the existing bundle and
sidecar read-only, with no analysis or GPU producers. The old workflow shipped
inside the historical bundle predates this safety correction: do not run its bare
default target. Use explicit CPU targets with fresh output paths as below.

This is a portable **energy-analysis** release. It contains revised source, archived reduced
potentials, run-time JSON, the six G93A folded topology files, audited references and generated
figures/statistics. It does not require GROMACS, pmx, OpenMM or a GPU for reproduction.

## Files and their identity

- `releases/sod1fep-forensic-review.tar.gz` — local review bundle (generated, gitignored).
- Matching `.sha256` — transport checksum.
- `RELEASE_MANIFEST.json` inside the bundle — exact relative paths, sizes and SHA-256 hashes
  for every included file. The manifest is the only member excluded from its own inventory.
- `project/data/forensic_archive_manifest.json` — original immutable 1,120-entry inventory.
  Its `repository` root maps to `project/data/forensic_baseline_repository/`, which contains
  the five original source/config inputs byte-for-byte. New source has its own release hashes.
- `project/env/analysis-lock.txt` — exact installed CPU package/dependency versions.
- `project/env/analysis-runtime.json` — observed original analysis runtime (Python 3.13.9,
  macOS ARM64, NumPy/SciPy PyMBAR backend). Version pins are not cross-platform binary hashes.

The bundle has `project/`, `archives/main/`, and `archives/ss/` as sibling paths. The two
archive roots are mapped by `env/portable-archives.yaml`; original host-specific paths in
historical documents are not required by the executable workflow.

## Verify before extraction

From the repository, using Python's standard library only:

```bash
python -m src.analysis.forensic_release --verify releases/sod1fep-forensic-review.tar.gz
```

The current CLI checks the transport sidecar, then requires an exact member inventory,
checks every digest/size, rejects duplicate
and unsafe members, and never executes or extracts the bundled code. Check the external
SHA-256 as well after transferring the file. Checksums establish identity relative to the
supplied manifests, not independent scientific certification or authenticity of the author.

Extract the verified bundle to an empty directory and enter its `project/` directory.

## Install the CPU environment

Use Python 3.13.9 to most closely match the tested runtime. No simulation dependencies are
included in this lock; the historical GPU environment remains documented in `env/environment.yml`.

```bash
python3.13 -m venv /tmp/sod1fep-reproduction-env
/tmp/sod1fep-reproduction-env/bin/python -m pip install -r env/analysis-lock.txt
source /tmp/sod1fep-reproduction-env/bin/activate
```

The lock was successfully installed into a fresh isolated environment from PyPI. This checks
installability on the current macOS ARM64 platform; other operating systems/BLAS builds have
not been certified. Package installation needs network access unless dependencies are cached.

## Recompute CPU analyses into a fresh namespace

From an extracted bundle's `project/` directory, first create a fresh override YAML
(for example `reproduction-output.yaml`) with reviewed output paths:

```yaml
forensic_review:
  output_dir: docs/reproductions/forensic-review-2026-09-18
  release_file: releases/forensic-review-2026-09-18.tar.gz
```

The chosen output directory must not already exist. Then request **only** the
three CPU producers, not the release/default target:

```bash
snakemake forensic_diagnostic_audit forensic_methods_figures forensic_reference_reproduction \
  -s workflow/Snakefile --cores 2 \
  --configfile config/pipeline.yaml env/portable-archives.yaml reproduction-output.yaml \
  --runtime-source-cache-path "$(mktemp -d /tmp/sod1fep-source.XXXXXX)" \
  --forcerun forensic_diagnostic_audit forensic_methods_figures forensic_reference_reproduction
```

From the original working repository with the archives in their original sibling directories,
omit `env/portable-archives.yaml`, but retain the fresh output override.

A fresh runtime source-cache directory avoids reusing cached Snakefile content on repeated
runs and avoids writing to a restricted user cache. In the current repo the default
target is read-only verification, not release regeneration. The explicit historical
simulation rules are retained for provenance and are not part of this reproduction command.

All numerical analysis settings are in `config/pipeline.yaml:forensic_review`. Bootstrap
settings (2,000 draws, seed 20260914, 95% percentile intervals) are exploratory post-verdict
choices. They do not affect the original simulation protocol or pass/fail thresholds.

The command writes products to the fresh configured review directory and does not
build a bundle. Existing `docs/review/`, `docs/figures/` and the old release remain
untouched. Raw archives are read-only. To create a **new** release from a clean,
committed current checkout, explicitly target `forensic_release` with a fresh
`forensic_review.output_dir` and `release_file` override. The DAG admission checks
these conditions before scheduling producers or deleting declared outputs. An
extracted snapshot without git identity is for analysis reproduction, not building
a schema-2 committed-source release.
Expected numerical outputs:

| check | expected |
|---|---|
| original gate | Pearson 0.32601995; RMSE 2.12348058; F64A excluded |
| raw diagnostic inventory | 48 leg/replicate records; 912 adjacent pairs |
| F64A folded r1 | net 0.0227045584; absolute local sum 1.6781026848 kcal/mol |
| G93A SS−2SH | −0.0169183127 kcal/mol |
| conditional unpaired Welch 95% interval | [−0.2966175980, +0.2627809727] kcal/mol |

Floating-point differences between BLAS/platform builds may occur; raw archived-estimate
reconciliation uses the numerical tolerance in the config. PNG hashes can differ across
font/rendering environments even when plotted numbers agree. The new release manifest records
exact bytes of whichever environment generated it.

## Tests and scope of verification

```bash
python -m pytest tests/test_diagnostic_audit.py tests/test_methods_figures.py \
  tests/test_reference_sensitivity.py tests/test_independent_reference_reproduction.py \
  tests/test_forensic_release.py tests/test_fep.py tests/test_validate.py -q
```

The previous 70/133 counts were stale: before the new CPU audits/release guards,
these seven files collected **75 tests**, and the full project collected **242**.
The current 2026-09-18 checkout collects **82 tests** in these seven files and
**283** across the full suite, including 34 new F64A audit tests and seven release
guard/provenance tests. Current tests run in the original analysis environment;
do not treat these updated counts as a new fresh-lock install certification.
All **283 tests passed** locally in the 2026-09-18 repository review.
Regression tests cover signed cancellation, preservation of sibling groups in resampling,
tied ranks, uncertainty from both redox arms and detection of altered release contents.

## Missing data and inference limits

- **A4V attempt-1 raw windows were overwritten.** Original `A4V_3ns_ddg.json` and convergence
  JSON preserve its run-time estimates; the 120 retained A4V NPZs are attempt 2. The 840 other
  main-archive windows are attempt 1. No file is relabeled to conceal that distinction.
- The SS diagnostic adds 120 NPZs. SS and 2SH have the same protocol hash, so topology and
  manifest evidence—not that hash—identify redox state.
- The archive lacks a complete structural trajectory/force-field/runtime record sufficient
  to reconstruct all original simulations from scratch. This release reproduces energy
  analysis and available topology checks, not every physical preparation or trajectory.
- Source-state compatibility is audited, not repaired. All original gate controls differ
  from the simulated state/construct; post-verdict reference scenarios are not new validation.
- Sibling disagreement values are dependent. Variant/site grouped intervals remain approximate
  with few groups; no general diagnostic superiority is established.
- The G93A interval is conditional sampling uncertainty, excluding hidden modes/model bias.
- The separate reference script is an independent implementation, not independent human review.

This bundle is local and ready for another researcher to inspect. It has not been uploaded,
given a DOI, or assigned a public license. Public deposition and publication should follow
rights-holder and authorship decisions, with source references and licenses retained.
