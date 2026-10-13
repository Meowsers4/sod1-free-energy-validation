# F64A under the redistributed ladder — protocol `822108e9db71124d` (2026-08-30)

**Interpretation corrected 2026-09-18.** This is a historical run report; its
numerical tables are preserved. Current claims and future work are governed by
[the reconciliation](conclusion_reconciliation_2026-09-18.md) and
[publication plan](publication_research_plan.md). “Cycle closure” below is the
historical field name for net ladder hysteresis, not a closed thermodynamic cycle.

The rerun that [`f64a_folded_leg_failure.md`](f64a_folded_leg_failure.md) called for.
120 windows (20 λ × 3 replicates × 2 legs), refined λ endpoint, and
`independent_replicate_systems: true`.

**Outcome: reported net hysteresis fell, but F64A still fails the gate's
convergence criterion.** Hysteresis 2.52 → 1.10 against a cap of 1.0. Schedule
and replicate preparation both changed, preventing single-factor attribution.

## Result

| | 18-window `f9bded6f07b4abe5` | 20-window `822108e9db71124d` |
|---|---|---|
| ΔΔG | 6.63 ± 0.19 | **6.94 ± 0.34** |
| cycle closure (cap 1.0) | 2.52 | **1.10** |
| `converged` | false | **false** |
| replicate spread | 0.64 | **1.02** |
| min adjacent overlap | 0.018 | 0.015 |
| selected samples (not proven independent conformations) | 54,299 / 324,108 | 60,617 / 360,120 |
| `solver_notes` | JAX banner only | none |

Experimental reference is −0.20, but see the caveat below before treating +7.1 as the error.

### Per leg

| leg | r0 | r1 | r2 | spread |
|---|---|---|---|---|
| folded | +1.25 (hyst 0.79, ovl 0.015) | **+2.51 (hyst 0.02, ovl 0.055)** | +1.36 (hyst 1.10, ovl 0.029) |
| unfolded | −5.36 (hyst 0.18) | −5.12 (hyst 0.13) | −5.25 (hyst 0.19) | 0.24 |

Per-replicate ΔΔG: 6.61, 7.62, 6.60.

## What the changes bought

Replicate spread rose 0.64 → 1.02 and `ddg_err` rose 0.19 → 0.34. Independently
prepared solvent systems expose additional run-to-run variation, but these data
do not establish distinct conformational basins or why the earlier runs agreed.
Range exceeding an uncertainty of the mean is not evidence of a particular
uncertainty-underestimation factor.

Net hysteresis fell 2.52 → 1.10 while minimum overlap changed 0.018 → 0.015.
Because both the schedule and preparation policy changed, neither observation
isolates the effect of endpoint refinement. Low overlap alone cannot decide
between insufficient bridging and inadequate conformational sampling.

## Low net hysteresis coexists with repeat disagreement

| folded replicate | ΔG | hysteresis |
|---|---|---|
| r0 | +1.25 | 0.79 |
| **r1** | **+2.51** | **0.02** |
| r2 | +1.36 | 1.10 |

r1 has the **lowest hysteresis of F64A's six leg-replicate records** — and it is the
replicate that disagrees with the other two by ~1.2 kcal/mol. This does not
identify which estimate is correct or establish within-basin equilibration.
Signed local discrepancies can cancel in the net metric. Later continuation
demonstrates duration sensitivity on this path; the structural explanation remains open.

> **Correction (2026-09-12).** This line originally read "the lowest hysteresis recorded
> anywhere in this project". Ranking all 48 records in the archive puts it **10th**; G93A
> unfolded r2 (0.0017) is 13x lower, and two G93S *folded* records are lower too. What is
> extremal is the *disagreement*: 1.2026 kcal/mol is the largest of the 48. Over all 48,
> folded-leg hysteresis and independent-box disagreement are near-uncorrelated (Pearson
> +0.072, n=24). These nested, dependent records do not establish a population-level
> absence of association or superiority of another diagnostic.
> See [`stop_rule_reanalysis.md`](stop_rule_reanalysis.md) §5-6.

The G93A values formerly quoted here (0.08 and 1.05) belonged to the superseded
18-window protocol. The 20-window values are net hysteresis 0.045 and a 1.17
kcal/mol discrepancy from the unmatched reference. Neither that discrepancy nor
F64A's sibling disagreement establishes true error. Report temporal movement,
repeat dispersion and local diagnostics together; none has demonstrated general
superiority in this archive.

## Historical experimental-value argument — retracted

The atom-count argument below is retained only to document the reasoning error;
it is not a current conclusion. The primary F64A reference value has been verified.

Complements the F45A/F64A comparison in the failure doc. Within Nordlund & Oliveberg 2006
alone — one source, one method, one lab:

| variant | side-chain heavy atoms deleted | burial (neighbours <6 Å) | exp ΔΔG |
|---|---|---|---|
| I18V | 1 | 66 | 0.37 |
| I149A | 3 | 72 | 4.05 |
| **F64A** | **6** | **70** | **−0.20** |

**Retracted argument:** F64A deletes twice what I149A does from an equally buried site and is reported at roughly
zero. Extrapolating the other two gives ~1.35 kcal/mol per deleted atom, i.e. ~8 for F64A —
so the FEP value sits on that trend and the experimental value is the outlier.

> **Retracted (2026-09-12).** The argument in this subsection does not survive the primary
> source. Nordlund & Oliveberg's Table 1 gives F64A ΔG = **3.07** against pWT **2.87** — F64A
> is measurably *more* stable than its own reference, and −0.20 is that difference sitting in
> an internally consistent series (I18V 2.50 → 0.37, I149A −1.18 → 4.05, each matching
> `variants.csv` exactly). The atom-count extrapolation below predicts ~8 kcal/mol of
> destabilization and concludes "the experimental value is the outlier"; that conclusion is
> **withdrawn**. The measurement is not an outlier in a table, and "the experiment is probably
> wrong" is no longer an available explanation for the ~7 kcal/mol gap. See
> [`reference_state_audit.md`](reference_state_audit.md) §4.1. The paragraph is kept, struck
> through in effect, because the reasoning error — extrapolating a trend across three points
> and preferring it to a direct measurement — is worth remembering.

**This is not grounds to drop F64A**, for the reason already argued in the failure doc:
excluding a control because it produced an inconvenient FEP number is the same category of
post-hoc adjustment as lowering `min_pearson`. It is recorded so that the +7 "error" is not
uncritically attributed to the calculation. Those primary values have since been
checked; the remaining mismatch concerns physical state and construct, not an
unverified F64A table entry.

## Status

**Not gate data.** `converged: false` (closure 1.10 > 1.0), so `evaluate_gate` excludes it
on a pre-registered criterion, independent of any question about the reference value.

At this historical checkpoint, at least six usable gate variants were required;
one further exclusion among the other seven would leave six, not automatically
end the gate. The completed gate subsequently used seven and failed Pearson/RMSE.

Raw data: `results/fep/F64A` (120 windows). The superseded 18-window run is archived at
`results/archive/F64A_f9bded6f07b4abe5`.
