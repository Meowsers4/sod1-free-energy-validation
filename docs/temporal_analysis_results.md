# Time-resolved diagnostic analysis — results

Executed 2026-09-14 from the specification in
[`temporal_analysis_design.md`](temporal_analysis_design.md). This is retrospective,
exploratory analysis of a known failed gate. It does not define a stopping threshold,
re-open the gate, or treat later data as ground truth.

## Execution and reconciliation

- Primary cohort: F64A, I18V, I113T, G93A, G93S, I149A and G93V under the shared
  attempt-1 protocol.
- Separate cohort: A4V's retained attempt-2 data (9 ns folded, 3 ns unfolded). The lost
  attempt-1 folded energy history was not reconstructed.
- Each raw window was divided deterministically into four non-overlapping blocks. Prefixes
  ended at 25%, 50%, 75% and 100%; the comparison block used only the final 25%.
- Equilibration detection and correlation thinning were recomputed after raw column
  selection for every interval.
- All 240 leg intervals and 120 folding-difference intervals solved. No interval was
  dropped or replaced.
- The 48 full-duration leg estimates reproduced the frozen audit. Maximum absolute
  discrepancy was `1.28e-13` kcal/mol for ΔG and `6.86e-15` kcal/mol for net hysteresis.

The machine-readable record is
[`temporal_diagnostic.json`](temporal_review/temporal_diagnostic.json); flat records and
figures are in [`temporal_review/`](temporal_review/).

## Main result

The estimates were still changing within the retained simulations. Direct temporal
analysis demonstrated movement that small historical aggregate hysteresis could
miss in selected records. This retrospective observation is not validated
predictive superiority across variants; see the bounded associations below and
[current interpretation](conclusion_reconciliation_2026-09-18.md).

| leg / checkpoint | median |prefix − final quarter| | maximum | median conditional MBAR error |
|---|---:|---:|---:|
| folded, 25% | 0.368 | 1.808 | 0.118 |
| folded, 50% | 0.313 | 1.340 | 0.086 |
| folded, 75% | 0.311 | 1.070 | 0.071 |
| unfolded, 25% | 0.238 | 0.652 | 0.105 |
| unfolded, 50% | 0.240 | 0.526 | 0.074 |
| unfolded, 75% | 0.147 | 0.462 | 0.061 |

Values are kcal/mol across 21 primary-cohort repeat records per row. The comparison is
disjoint through 75%, but the two blocks can still be temporally correlated. At 75%, the
median folded movement was 2.43 times the combined conditional MBAR uncertainty of the
prefix and late-block estimates; 12 of 21 records exceeded a ratio of two. This is a
descriptive scale comparison, not a hypothesis test.

The secondary A4V result is compatible with the earlier conclusion that longer sampling
improved repeat agreement, but it does not look perfectly stationary. Its folded repeat
range narrowed from 1.26 kcal/mol at 25% to 0.27 kcal/mol at 100%; at 75%, movement versus
the final quarter had median 0.254 and maximum 0.496 kcal/mol.

## Could instability have been recognized earlier?

Yes for important individual records, but not by one universal diagnostic.

F64A folded r1 was the clearest case. At 25%, its movement versus the final quarter was
1.808 kcal/mol, largest of the 21 folded records. Its net hysteresis was only 0.093
kcal/mol (rank 19/21), while the sum of absolute local discrepancies was 3.571 (rank
4/21), the maximum local discrepancy was 0.970 (rank 1/21), and its conditional MBAR
error was 0.191 (rank 1/21). At full duration it had the largest sibling disagreement,
1.203 kcal/mol, while net hysteresis was again small, 0.023 (rank 17/21).

Across the primary cohort at 25%, folded maximum-local discrepancy associated with later
movement at Pearson/Spearman 0.616/0.443; sum-absolute discrepancy associated at
0.514/0.401. The corresponding signed-net association was only 0.208/0.091. Some grouped
bootstrap intervals for the absolute metrics excluded zero, but associations changed by
checkpoint and metric, there are only five sites, and sibling-derived observations are
dependent. These results motivate the metrics as warning signals; they do not validate a
decision threshold or demonstrate superiority.

G93V folded r0 supplies a different warning: its 75% prefix moved 1.070 kcal/mol relative
to the final quarter even though its full-duration estimate nearly matched the two sibling
repeats. Agreement at one cumulative endpoint can therefore hide time sensitivity.

## GPU implication

The observed branch is **estimates keep moving**, with persistent repeat disagreement in
F64A. The next GPU work should therefore be a bounded sampling experiment on a known case,
not a broad rerun or a new prediction campaign. F64A is the strongest development case.

A concrete pilot still needs its model, usable concurrency, allocation and retention budget
fixed before preregistration. The design should distinguish longer within-start sampling
from dependence on genuinely different protein starting conformations; additional solvent
boxes alone do not test the latter. No GPU array is authorized by this analysis.
