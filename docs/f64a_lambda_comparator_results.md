# F64A exploratory lambda/comparator analysis — work package A1

Completed 2026-09-18. This is a fresh-output, CPU-only exploratory audit of the
completed F64A folded apo-2SH v2 continuation. It does not refit MBAR, select a
threshold, establish stationarity or mechanism, reopen the failed gate, or
authorize GPU work.

## Inputs and execution

The analysis consumed all 60 production NPZs in the immutable v2 inventory. Each
file was rechecked against its saved SHA-256 digest, shape `(20, 15001)`, scalar
metadata, simulation protocol and source/simulation code identities using the same
validation path as the raw-energy audit. The frozen raw audit and continuation
report also matched their configured hashes.

Specification: [`f64a_lambda_comparator.yaml`](f64a_lambda_comparator.yaml).
Implementation: [`f64a_lambda_comparator.py`](../src/analysis/f64a_lambda_comparator.py).
CPU-only DAG: [`f64a_lambda_comparator.smk`](../workflow/f64a_lambda_comparator.smk).
Machine-readable result:
`results/cpu_audits/f64a_lambda_comparator_v1/lambda_comparator.json`, SHA-256
`49fe3be23a29026d4e9e0cca719d3a31bbae957b5303e8758c492a278520cca7`.

The report contains 240 planned neighbor-direction slots: 228 observed records
and 12 explicit missing endpoint directions. It also contains 480 fixed-pair
records: two blocks × three repeats × 20 sampled paths × four fixed pairs. The
two neighbor directions share configurations and are not independent replicates.

## Full-block neighbor-energy result

For each sampled window, the first table takes the median across available
directions, both blocks and all repeats. The low/high entries are medians of ten
window medians, not pooled-record medians. Spearman uses the 20 actual, strictly
increasing lambda values; there are no row-wise tests or p-values.

| Descriptive metric | lambda windows 0–9 | lambda windows 10–19 | Spearman vs lambda | pooled-record median, n=228 |
| --- | ---: | ---: | ---: | ---: |
| absolute half drift (kT) | 0.022298491 | 0.084271662 | 0.848120 | 0.044698585 |
| absolute slope (kT/ns) | 0.014999039 | 0.055797158 | 0.893233 | 0.024208988 |
| raw-block SD (kT) | 0.426332843 | 0.697442266 | 0.897744 | 0.502067536 |
| absolute half drift / raw-block SD | 0.055932490 | 0.132314937 | 0.747368 | 0.086459742 |

The report and figure preserve the signs as well as magnitudes for every repeat,
block and neighbor direction. Signed pooled summaries are near zero because
positive and negative movements coexist; they must not replace the magnitude
plots. Overlap and the previously saved adaptive raw-suffix/thinned lengths are
shown beside these metrics without treating any as a pass criterion.

## Common fixed-pair result

The common evaluation grid is the existing high-lambda sequence 0.8824, 0.9200,
0.9500, 0.9750 and 1.0000, giving four adjacent fixed pairs. The same four energy
differences are evaluated on every sampled path. These are reduced-potential
differences, not free energies or MBAR error contributions.

| block | fixed lambda pair | median absolute drift on sampled windows 0–9 (kT) | median on sampled windows 10–19 (kT) |
| --- | --- | ---: | ---: |
| 9–12 ns | 0.8824–0.9200 | 0.021987 | 0.033119 |
| 9–12 ns | 0.9200–0.9500 | 0.020012 | 0.026781 |
| 9–12 ns | 0.9500–0.9750 | 0.017138 | 0.025766 |
| 9–12 ns | 0.9750–1.0000 | 0.018738 | 0.024352 |
| 12–15 ns | 0.8824–0.9200 | 0.021301 | 0.091592 |
| 12–15 ns | 0.9200–0.9500 | 0.017560 | 0.061275 |
| 12–15 ns | 0.9500–0.9750 | 0.015651 | 0.049027 |
| 12–15 ns | 0.9750–1.0000 | 0.016205 | 0.039063 |

Visual QA rejected an initial draft grid containing widely separated state pairs:
far-state cross-evaluations reached roughly `10^21` kT on configurations with
negligible overlap and made the plot uninterpretable. That draft was not retained
as evidence. The final adjacent high-lambda grid was then fixed in the fresh
configuration and the output regenerated. This is an analysis-design correction,
not deletion or selection of trajectories; all paths, blocks and repeats remain.

## Interpretation

The new analysis confirms that the earlier high-lambda pattern is not an artifact
of plotting window number or pooling directions. Larger magnitudes and raw scatter
occur toward high lambda, and the exact high-lambda fixed-pair observables become
more variable when evaluated on high-lambda sampled paths. The pattern remains
repeat- and time-block-dependent.

It does **not** identify hydration, cavity opening, repacking, a distinct basin,
or starting-conformation independence. A denser ladder could preserve these exact
five states and compare the fixed-pair observables, but unchanged states would
still run independent dynamics. Reduced pair spacing can also shrink raw energy
differences mechanically. No universal drift/overlap threshold follows.

All requested paths and blocks appear in the JSON; endpoint missing directions
are explicit; every plotted value is drawn from named report records. The A1
acceptance conditions are therefore met. The diagnostic specification and
prior-art boundary are recorded separately in
[`diagnostic_comparator_specification.md`](diagnostic_comparator_specification.md).

## Verification

- 20 focused lambda/raw-audit tests passed together during implementation.
- Four new comparator tests pass after the final visual-QA revision.
- `git diff --check` passes.
- Both standalone and main-workflow dry runs are recorded in the handoff after
  completion; the default target remains read-only forensic verification.

