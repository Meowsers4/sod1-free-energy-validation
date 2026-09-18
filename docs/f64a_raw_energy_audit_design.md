# F64A raw energy time-series audit — fixed 2026-09-18

## Status and scope

The user authorized this CPU-only follow-up after reviewing the
[15 ns continuation result](f64a_continuation_results.md). The implementation and
tests are prepared. **The scientific audit has not run:** none of the 60 production
NPZs are available in the local checkout. No new time-series findings are claimed.
The full fit report is preserved; raw matrices remain on SCC.

This is a post-result, exploratory description, not blind validation, a stationarity
test, a new convergence gate or authorization for another GPU experiment. Keep
F64A folded monomer apo-2SH, the failed historical gate/exclusion and the 15 ns stop
fixed. Mentor review remains deferred. No MBAR fit, new cutoff detection, policy
selection or structural-mechanism claim is introduced.

## Fixed data and quantities

Consume all **60 production** NPZs, each `(20, 15001)`, matching their exact SHA-256
hashes in the frozen SCC report. Do not consume staged baseline NPZs or first-light
outputs by mistake. Check finiteness, window/repeat/state metadata, provenance,
one protocol and both simulation ancestry identities. Missing, extra, changed or
short matrices are fatal; there is no GPU producer in the audit DAG.

Use exactly the registered raw slices:

- Retained 9–12 ns: `[9001:12001]`, 3000 records/window.
- Retained 12–15 ns: `[12001:15001]`, 3000 records/window.

For every path, inspect the sampled-state reduced potential and **both** available
adjacent-state minus sampled-state reduced potentials. The previous observable
is absent at window 0; the next is absent at window 19. Both directions are
included so the original one-neighbor selection observable does not hide the
other side of an adjacent pair. Values are in **kT/reduced-potential units**, not
mutation free energies or contributions to endpoint ΔG.

Describe each full raw block and each raw suffix beginning at its **previously
saved** adaptive, zero-trim and fixed-25% cutoff. Do not rerun equilibration
detection. Suffix statistics include every raw record after the cutoff, **not**
just the old thinned samples. Preserve the old cutoff/g/count records alongside
the new summaries. No new g or effective sample size is estimated.

The [configuration](f64a_raw_energy_audit.yaml) fixes:

- Contiguous 250-record bins (0.25 ns), with mean and standard deviation.
- Full-block and raw-suffix mean, standard deviation and 5/50/95% quantiles.
- Descriptive least-squares linear slope and second-half minus first-half mean.
- Empirical biased ACF at lags 1/10/100/250/500/1000 records (ps at the frozen stride).

For a centered series, ACF(lag) is the lagged cross-product sum divided by the
zero-lag squared sum. Compute by zero-padded FFT, with no circular wraparound.
Constant data or lags at least as long as the series give **null**, not zero or
invented correlation information. Whole-block and short-suffix ACF estimates are
not interchangeable; changing data confound their stationary interpretation.

These trends/moments are descriptive trajectory summaries, **not uncertainties,
free-energy estimates or independent-sample significance tests**. All repeats and
policies remain visible. A small suffix drift/ACF does not certify equilibration.

## Outputs and integrity

Implementation: [f64a_raw_energy_audit.py](../src/analysis/f64a_raw_energy_audit.py).
Separate CPU-only DAG: [f64a_raw_energy_audit.smk](../workflow/f64a_raw_energy_audit.smk).
The separate DAG intentionally preserves the registered simulation workflow and
all v2 dependency hashes; it is not a standalone GPU script.

Output namespace: `results/cpu_audits/f64a_raw_energy_v1/`:

- `raw_energy_audit.json`: 348 planned observable/block/path records, 1044 saved
  policy-suffix summaries and 4176 time-bin records, with hashes/config/runtime.
- Three full-ladder heatmaps, one for each observable, with all three repeats and
  the saved adaptive cutoffs overlaid. Subtract each observable's path mean before
  coloring, solely to display within-path variation. This centering hides baseline
  offsets between repeats; consult the uncentered JSON means for repeat comparisons.

Heatmap saturation at the configured 95th percentile is a display choice only;
no observations are removed. Colored trends do not identify a protein conformation
or a causal window. Binning can hide fast changes; full raw-block/suffix moments
and ACF are also retained. This audit does not persist coordinate trajectories or
claim structural coverage.

Fingerprint all NPZs and analysis dependencies before/after computation. Validate
all inputs before computing outputs. Refuse an existing output directory. Prepare
figures/report privately, then create the output directory exclusively and publish
the JSON **last**. A publication failure can leave partial figures; preserve them
and diagnose, do not delete evidence or duplicate a run blindly. Neither raw NPZs
nor the supplied scientific report are modified.

## Execution

Preferred here: copy **only the 60 NPZs**, not the large checkpoint/append trees,
into the corresponding local `results/pilots/.../production/fep/F64A/folded/`
directory. Then run from the repo root:

```bash
python -m src.analysis.f64a_raw_energy_audit
```

The module also supports explicit `--npz-dir` and fresh `--output-dir`. Equivalent
CPU DAG (requires all existing data):

```bash
snakemake --snakefile workflow/f64a_raw_energy_audit.smk --cores 1
```

If run on SCC, deploy/commit the CPU package first and run from the cluster repo
inside `tmux` or a CPU batch job, not a new GPU request. The audit does not depend
on GROMACS, pmx, PyMBAR or JAX: it uses NumPy, Matplotlib and PyYAML, and records
their actual versions. Local library versions need not reproduce the old MBAR
runtime because there are no new MBAR/thinning solves.

## Decision boundary

Review whether whole-block means/quantiles/ACF differ substantially from selected
short suffixes, where changes occur relative to saved cutoffs, and how patterns
differ across repeats. No data-dependent numerical pass criterion is added.
These checks can sharpen a separately designed sampling-method or different-start
test; they cannot alone distinguish shared trapping, model/reference mismatch,
stationarity in unsampled modes or a particular structural mechanism.

The next decision remains a human scientific design choice, **not automatic GPU
submission or an extension beyond 15 ns**.

## Verification before real-data execution

125 focused F64A/audit tests passed, including a complete deliberately synthetic
pipeline, direct ACF/slope checks, saved-suffix behavior, missing/extra/corrupt
NPZs, wrong protocol/shape, nonfinite energies, mid-run input changes and refusal
to overwrite outputs. Synthetic fixtures live only in test temporary directories;
they are not scientific result files. Plot layout was inspected on a synthetic
fixture. Ruff and `git diff --check` passed.

The real-data Snakemake dry-run correctly stops with `MissingInputException` for
the absent 60 NPZs, without offering any GPU producer. This is an expected data
blocker, not evidence that a scientific audit completed.
