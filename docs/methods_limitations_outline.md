# Publication outline — failed gate, diagnostic cancellation, and benchmark compatibility

Revised 2026-09-14 following publication review; updated 2026-09-18 for completed
temporal evidence and corrected interpretation. This outline governs claims
supported **now**. The [prospective publication plan](publication_research_plan.md)
separately tracks completed supporting CPU work and proposed protein comparisons;
the latter are not completed evidence. See [conclusion reconciliation](conclusion_reconciliation_2026-09-18.md).

## Working title

**Local diagnostic cancellation and experimental-state incompatibility in a SOD1
free-energy validation campaign**

## Central claim

A prespecified apo-2SH SOD1 folding-stability gate failed against a heterogeneous experimental
compilation, stopping prospective predictions. An exploratory audit shows that the net
forward/reverse ladder diagnostic can conceal signed discrepancies between adjacent windows.
The benchmark audit separately shows that reference labels concealed differences in redox
state, construct, oligomeric transition and temperature. These findings explain limitations
of the validation procedure; they do not identify the physical cause of prediction error.
Separately registered F64A continuations demonstrate that small early net hysteresis
did not certify later duration stability on that selected path. Late instability
remains unresolved at 15 ns. None of these findings validates a general diagnostic,
identifies a structural mechanism, or establishes equilibrium free energy.

## Result 1 — the original decision and its scope

Seven usable variants: Pearson r = 0.326, RMSE = 2.123 kcal/mol; F64A excluded by the
prespecified 1.0 kcal/mol per-variant hysteresis cap. Preserve the original point estimates,
thresholds, and exclusion. A4V's original point survives only in its run-time JSON.

The comparison justified withholding prospective predictions. It does not measure accuracy
against matched apo-2SH experiments or isolate force-field error. State this beside the gate,
not only in the final limitations paragraph. The numerical threshold-crossing forensic
reference scenarios remain post-verdict sensitivities, never a second gate.

Evidence: `gate_attempt_1.md`, `reference_state_audit.md`, `review/reference_reproduction.json`.

## Result 2 — aggregate cancellation, with bounded statistical evidence

Define the historic metric explicitly: for signed adjacent discrepancies d_k,
H = |sum(d_k)|. This permits cancellation; compare it exploratorily with sum(|d_k|)
and max(|d_k|). These alternatives are descriptive summaries, not validated thresholds.
They depend on the number and placement of lambda windows; all comparisons here use 20 states.

F64A folded r1: H = 0.022705; sum(|d_k|) = 1.678103; max(|d_k|) = 0.222590 kcal/mol.
The cancellation fraction 1-H/sum(|d_k|) is 98.647%. Its sibling disagreement is 1.202554
kcal/mol. Cancellation concerns the reported diagnostic; it does not establish that this
caused the MBAR estimate to be wrong, or that either sibling is correct.

All 48 retained records (912 adjacent pairs) re-solve from raw NPZ energies. Report folded
and unfolded legs separately. The 24 folded records comprise eight variants at six sites.
The disagreement definition reuses sibling estimates, so rows are statistically dependent.
Use whole-variant/site resampling and leave-group-out sensitivity, with a separate seven-
variant attempt-1 cohort that excludes the longer A4V rerun. Do not present row-wise p-values.
Even grouped intervals are approximate with so few sites; no population-level absence claim.

The alternative summaries do **not** demonstrate improved prediction of repeat disagreement:
all folded-leg site-bootstrap correlation intervals include zero. This negative finding is
part of the result. No threshold is chosen from the F64A example.

Evidence: `review/diagnostic_audit.json`, `review/diagnostic_records.csv`,
`review/adjacent_discrepancies.csv`, `review/diagnostic_cancellation.png`.

## Result 3 — bounded A4V sampling sensitivity

A4V folded production increased from 3 to 9 ns/window; equilibration also increased from
0.5 to 2 ns. The unfolded leg was retained. Folded replicate range fell from 1.46 to 0.27
kcal/mol; discrepancy from the unmatched reference fell from +1.92 to +1.74 kcal/mol.
Describe this as a bundled sampling-protocol comparison, not an isolated production-length
intervention. Reduced spread is improved observed repeat precision, not proven basin coverage.
The result does not exclude effects from longer sampling or new starting conformations.

The original raw windows were overwritten, so this comparison relies on archived run-time
summaries for the shorter arm. No future rerun can retroactively repair that missing record.

## Result 4 — experimental-state and construct audit

All eight reference numbers trace to primary tables. Six are apo-SS monomer measurements
on C6A/C111A/F50E/G51E at 25 °C, pH 6.3. Two are apo native-dimer DSC transitions on
C6A/C111S at 49.4 °C, pH 7.8. The simulation uses reduced native-sequence monomers and
preparation pH 7.0. No gate control is fully state/construct matched.

The compilation's uniform ±0.3 kcal/mol is not a per-point experimental measurement error.
Halving a cooperative dimer transition does not make it an isolated monomer measurement.
Opposite-signed residuals reject a single additive offset; they do not reject mutation-
dependent responses to the same state or construct change.

Evidence: `reference_state_audit.md`, `../data/benchmark_state_audit.csv`,
`reference_sensitivity_analysis.md`. Source-derived scenarios remain separate from
`data/variants.csv`, which preserves the gate inputs.

## Result 5 — G93A disulfide contrast with conditional uncertainty

The point estimate of folded ΔG(SS)-ΔG(2SH) is −0.016918 kcal/mol, within the predeclared
point-estimate band of ±0.3. Both arms contain three separately built solvent systems;
physical atom/bond inspection verifies the intended redox states.

Report the contrast's standard error and unpaired Welch 95% interval from
`review/redox_uncertainty.json`. The interval uses between-run variation in both arms.
Matching replicate numbers or random seeds does not establish statistical pairing.
The interval is conditional on sampled basins; it excludes unsampled modes, force-field
bias and experimental uncertainty. It is not a prospective equivalence test, and a small
observed effect does not rule out slower redox-dependent structural rearrangements.

Retain the original preregistration and outcome band as historical records; distinguish
its frozen decision from the corrected interpretation. The identical protocol hashes in
the SS/2SH arms cannot identify their redox states; topology and manifest evidence do.

## Figure and table sequence

### Completed temporal evidence to add as Result 6

F64A folded r1 changed from **2.505942** kcal/mol over its initial retained 3 ns
to **0.429467** over the disjoint retained 6–9 ns block (−2.076474), despite early
net hysteresis **0.022705**. This is an exact-path temporal counterexample to
treating a small aggregate as a duration-stability certificate. It is a selected
case, not a prospective validation cohort or an experimental-accuracy result.

At 9–15 ns, adaptive signed mean movement **−0.049510** masks r1 **−0.695174**
and r2 **+0.598142**. Fixed-policy mean movements are **+0.579425** and
**+0.410739**; final adaptive repeat range is **1.946359**. Show all repeats and
policies and the short selected suffixes; do not select the near-zero mean as the
conclusion. Structural trajectories were not retained under this production policy.

The later read-only summary in the reconciliation note finds greater raw
neighbor-energy drift toward high λ, using window medians and actual λ labels.
It does not demonstrate cavity hydration, rule out trapping, or select a ladder
intervention. Keep this descriptive result separate from registered v1/v2 endpoints.

Evidence: `f64a_extension_results.md`, `f64a_continuation_results.md`,
`f64a_raw_energy_audit_results.md`, `conclusion_reconciliation_2026-09-18.md`.
Promote this temporal evidence ahead of the historical A4V/redox sensitivity
panels when assembling the manuscript. Those can move to the supplement if the
paper focuses on diagnostics; do not present every audit as a separate discovery.

| item | content | current output |
|---|---|---|
| Figure 1 | frozen failed gate, F64A exclusion, unmatched-state caveat | `review/gate_of_record.png` |
| Figure 2 | signed local discrepancies and alternative summaries | `review/diagnostic_cancellation.png` |
| Figure S1 | historical net metric against sibling disagreement | `review/convergence_diagnostic.png` |
| Figure 3 | A4V repeat spread and reference discrepancy | `review/a4v_sampling_sensitivity.png` |
| Figure 4 | reference scenarios, fixed predictions/exclusion | `review/reference_sensitivity.png` |
| Figure 5 | G93A replicate values and contrast interval | `review/g93a_disulfide_diagnostic.png` |
| Figure 6 (temporal main figure) | F64A disjoint 3-ns blocks 0–15 ns, net hysteresis per block, primary v2 contrast under all three policies, adaptive selected suffixes vs actual λ | `manuscript/figures_v1/fig6_f64a_temporal.{png,pdf,json}` (built 2026-10-13 by `manuscript_figures_v1`; reads only hashed v1/v2 reports and verifies every quoted Result 6 value) |
| Figures S2–S4 (λ supplement) | Fixed λ-pair drift, neighbor-energy descriptions and adaptive-selection context against actual λ | `manuscript/figures_v1/figS2–S4_*.png`, byte-identical copies of the hashed λ-comparator outputs |
| Table 1 | protocol and archive history, per leg | `raw_result_reconciliation.md` |
| Table 2 | state/construct/source compatibility | `../data/benchmark_state_audit.csv` |
| Table 3 | correlation intervals and leave-group-out results | `review/diagnostic_audit.json` |
| Table 4 | retained/lost data and limits of inference | `release_reproduction.md` |

## Discussion and practical recommendations

1. Preserve signed local diagnostics alongside aggregate values. A small net value may hide
   cancellation; no single alternative is established as an accuracy detector here.
2. Represent the experimental transition, state, construct, temperature, units and source
   table explicitly before choosing a validation panel.
3. Keep sampling uncertainty, repeat spread and discrepancy from experiment separate.
4. Archive immutable run identities, topology/force-field inputs and raw energies before any
   resubmission. MDP-only hashes and engine strings do not certify physical identity.
5. External-system evaluation is needed before proposing a generally useful stopping rule.
6. Distinguish statistical bridging between λ states from conformational exploration
   within states. Compare fixed observables when schedules differ; higher overlap
   and smaller neighbor differences alone cannot establish improved sampling.

## Boundary to the prospective manuscript

The λ/comparator analysis and bounded known-answer CPU calibration are now
complete; see [λ results](f64a_lambda_comparator_results.md) and
[model results](known_answer_model_results.md). They remain supporting evidence,
not a protein intervention result. The model's qualified exchange benefit and
incomplete interval coverage do not establish protein performance.

The revised plan centers on one **primary controlled protein sampling comparison
at matched cost**, then a frozen prospective SOD1 panel. Diagnostic assessment
is secondary; a general stopping rule is not an intended deliverable. Structural
mechanism is optional. Cross-protein testing addresses transferability only if
the preceding evidence makes that a useful next question. These protein stages
are not completed or resource-authorized. Current HREX build/placement limitations
remain recorded in [C1 qualification](gromacs_exchange_feasibility_design.md).

The future manuscript should lead with temporal-stability and independent-run
dispersion contrasts, their uncertainty, availability and cost. Diagnostics follow
the primary comparison; historical reference-state and toy-model material can
support the paper in supplements. An informative negative comparison needs
adequate precision; wide intervals alone cannot establish lack of benefit.
Neither a positive result nor a structural mechanism is required to report the
study. Keep the current case-study claim available if broader evidence remains
insufficient. No new protocol novelty is claimed in advance.

## Submission boundaries

No new FEP method, first-use, ALS mechanism, matched predictive validation, VUS classification,
charge-changing coverage, equivalence, diagnostic superiority or universal redox cancellation
claim is supported. Wells 2021's 0.81 is an apo-SS dimerization correlation; its 250 ns caveat
concerns residue-level dynamics. Neither is a directly matched folding benchmark.

This revision implements technical improvements 1–4 from the publication review. Independent
human review by Vlasov will occur later; it is not a prerequisite for local planning
or CPU work. No inquiry or manuscript has been sent; the LiveCoMS inquiry
remains parked. A public license and authorship must be chosen by the actual rights holders
before public deposition; this local review bundle does not assign either.
