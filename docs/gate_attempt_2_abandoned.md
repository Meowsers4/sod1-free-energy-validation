# Gate attempt 2 — abandoned after one variant (2026-09-12)

> Publication-review correction (2026-09-14): this is a historical run record.
> Claims that diagnostics contain no information, replicate range proves an error-bar
> multiplier, or the tested extension excludes further sampling are withdrawn.
> Range, SEM, model bias and discrepancy from unmatched experiments are distinct.
> Current interpretation: `methods_limitations_outline.md` and `cpu_improvement_plan.md`.

Attempt 2 raised folded-leg sampling 3 → 9 ns and equilibration 0.5 → 2.0 ns
(`5beab16`), leaving the already-converged unfolded leg untouched. It was run on **A4V
only** and stopped there.

**The result: sampling was genuinely inadequate, tripling it genuinely fixed the sampling,
and the answer is still wrong by the same amount.**

## A4V, 3 ns vs 9 ns folded

| | 3 ns folded | 9 ns folded |
|---|---|---|
| ΔΔG (exp 1.62) | 3.54 ± 0.39 | **3.36 ± 0.08** |
| error | +1.92 | **+1.74** |
| cycle closure | 0.66 | 0.51 |
| per-replicate ΔΔG | 2.95, 3.39, 4.29 | 3.27, 3.52, 3.28 |
| replicate spread | 1.34 | **0.25** |
| folded ΔG across boxes | −13.41, −12.96, −11.95 | −13.09, −12.82, −12.96 |
| **folded spread** | **1.46** | **0.27** |
| unfolded ΔG | −16.37, −16.35, −16.24 | −16.36, −16.35, −16.24 |
| independent samples | 60,562 | 81,743 |

Precision improved ~5×. Accuracy improved 0.18 kcal/mol, about 9%.

The unfolded leg reproduces to the second decimal, confirming that the unchanged unfolded
hash (`822108e9db71124d`) let those 60 windows be reused rather than recomputed — roughly
30% of the run's cost avoided.

## Why this ends attempt 2

The hypothesis was that more folded sampling would reduce the discrepancy from experiment.
The tested production/equilibration extension reduced box-to-box spread from 1.46 to 0.27
kcal/mol and reduced the reference discrepancy modestly. It did not demonstrate complete
conformational sampling or exclude sampling as a contributor. Force-field, unfolded-reference
and experimental-state differences also remain plausible. The decision to stop reflected
limited observed benefit and the project's budget, not a proof that further sampling cannot help.

Gate arithmetic with the improved A4V: SSE 31.5663 → 30.9075, RMSE 2.1235 → **2.1013**,
against a threshold of 1.5. G93V's −4.17 still contributes 17.39 of the total, and G93V is
the variant least likely to respond to folded-leg sampling.

## Cost, and what stopping saved

~400 CPU-hours (≈400 SUs) for A4V. Completing the seven would have been ~2,800 SUs on a
project already 890 SUs over allocation and one week from losing batch submission. The
single-variant test bought the answer for one seventh of the price.

This is also the empirical form of the recommendation in
[`post_pivot_review.md`](post_pivot_review.md) §4, which declined attempt 2 on opportunity
cost. The data now says the same thing directly.

## What it strengthens

The bounded result is:

> Under the tested A4V extension, the mean remained 1.74 kcal/mol from an unmatched
> experimental reference while replicate spread decreased about fivefold. The short-arm
> raw windows were overwritten; its run-time JSON preserves the comparison. This does
> not distinguish hidden sampling modes from model or reference bias.

## Status

- **Attempt 2 stopped.** G93A, G93S, G93V, I18V, I113T, I149A are NOT rerun at 9 ns.
- The gate of record remains [`gate_attempt_1.md`](gate_attempt_1.md): FAILED, r = 0.326,
  RMSE 2.123, pivot triggered.
- A4V's 3 ns files are archived at `results/archive/A4V_3ns_{ddg,convergence}.json`;
  `results/fep/A4V/` now holds the 9 ns folded + reused unfolded windows at
  `folded=cf1e632168579261|unfolded=822108e9db71124d`.
- No further GPU spend is planned.
