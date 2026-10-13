# F64A under the post-fix protocol — folded-leg sampling failure (2026-08-15)

**Interpretation corrected 2026-09-18.** Numerical records below describe the
superseded 18-window protocol, not the gate-of-record or current 15 ns pilot.
Earlier structural-cause and uncertainty claims are withdrawn as detailed in
[the reconciliation](conclusion_reconciliation_2026-09-18.md). The experimental
value has been source-verified but is not state/construct matched to this model.

First variant run under the **post-fix** protocol (`sc-coul = yes`, 3001 dH/dλ records per
window, corrected ACE/NME caps, `solvent_padding_nm` 1.2), protocol fingerprint
`f9bded6f07b4abe5`, 18 uniform λ-windows, 3 replicates, one shared solvated box per
(variant, leg). Recorded here because `results/` is gitignored and this run is being
archived and rerun. The folded leg showed the larger observed diagnostic problems
in this run; that does not establish a general failure class or structural cause.

## Result

| | value | |
|---|---|---|
| FEP ΔΔG | **+6.63 ± 0.19** kcal/mol | unmatched apo-SS monomer reference **−0.20** → discrepancy **+6.83** |
| cycle closure | **2.52** | cap 1.0 → `converged: false` |
| min adjacent overlap | **0.018** | pre-fix runs were 0.040–0.056, already called marginal |
| per-replicate ΔΔG | 6.74 / 6.89 / 6.26 | spread 0.64 against a quoted error of 0.19 |
| selected samples | 54,299 of 324,108 | 108 × 3001 exactly — not proven independent conformations |

This was the largest reference discrepancy recorded: 2.8× A4V's pre-fix +2.40, and on a variant
whose experimental value is ≈0. F64A is one of the near-zero controls whose job is to
catch a method that calls everything destabilizing.

## Observed diagnostic problems are larger in the folded leg

| leg | rep | dG (kcal/mol) | hysteresis | min overlap | fewest samples |
|---|---|---|---|---|---|
| folded | r0 | +1.62 | 1.23 | 0.018 | 27 @ w13 |
| folded | r1 | +1.76 | 1.00 | 0.033 | 14 @ w17 |
| folded | r2 | +1.09 | **2.52** | 0.030 | 16 @ w17 |
| unfolded | r0 | −5.12 | 0.14 | 0.115 | 323 @ w17 |
| unfolded | r1 | −5.14 | 0.26 | 0.115 | 183 @ w17 |
| unfolded | r2 | −5.17 | 0.23 | 0.072 | 227 @ w2 |

The unfolded leg's three estimates agree to **0.05 kcal/mol**, with lower
hysteresis and greater observed overlap than the folded leg. This does not prove
equilibration or adequacy of a capped tripeptide as an unfolded-state model.
Every folded replicate is at or over the 1.0 hysteresis cap at displayed precision.

Folded r0 selected samples per window (3001 raw records each, 1 ps apart):

```
w0..w8    735  269  626  473  744  689  694  684  408
w9..w17   554  495  143  398   27  319  207  271   45
```

The historical correlation analysis reported **~4 ps at low λ and ~111 ps at w13**.
Windows 13 and 17 retained 27 and 45 selected records. Such estimates in changing
series are heuristic; they are not verified equilibrium correlation times or
counts of independent conformational samples.

## Structural hypotheses, not a demonstrated mechanism

F→A removes six aromatic-ring heavy atoms while retaining CB. Cavity hydration
and protein repacking are plausible responses. These energy records do not
demonstrate either process, determine its timescale, or establish the sign of
sampling bias. The +6.83 kcal/mol discrepancy also contains model/reference-state
differences. The earlier claim that the mechanism was localized is withdrawn.

## What this establishes

1. **`ddg_err` is conditional uncertainty.** Comparing it with net hysteresis
   does not quantify its undercoverage. All three repeats shared one prepared
   system, limiting the variability explored; a common solvent barrier was not
   demonstrated. Future independent preparation can expose additional variation
   without guaranteeing protein-basin coverage.
2. **The convergence machinery does fire.** Unlike the pre-fix three — all of which
   reported `converged: true` despite unmatched-reference discrepancies of 0.8–2.4 —
   F64A was excluded by the prespecified rule. This is a rule outcome, not validation
   of diagnostic sensitivity or an invitation to tune the threshold.
3. **MBAR itself was clean.** `solver_notes` contained only pymbar's JAX import banner and
   no fallback warnings. Numerical solution does not certify equilibrium or settle
   whether analysis assumptions hold. (The banner is filtered out as of this change; it made the field
   unreadable without ever hiding anything.)
4. **F64A failed this protocol's diagnostic criterion.** One selected aromatic
   deletion does not establish a general difference between mutation classes.

## Consequence for the gate

F64A is the **only** sub-zero point in the 8-variant `gate_subset`:

```
F64A -0.20 | I18V +0.37 | I113T +1.25 | A4V +1.62
G93A +2.43 | G93S +3.70 | I149A +4.05 | G93V +7.00
```

It is the single anchor for the "does not destabilize" end of the gate. Without it the
subset spans +0.37 … +7.00 and the Pearson is dominated by G93V — already flagged in
`HANDOFF.md` as the gate's leverage point and a possibly wrong reference state (G93V comes
from Stathopulos 2006, the only control source where monomer > dimer). A gate that loses
F64A and leans on G93V is measuring one point twice.

## A separate concern: the experimental reference value

Raised here because it was found while diagnosing this run, and it must be on record
*before* the gate is evaluated rather than discovered afterwards.

F64 is genuinely buried — burial rank 45/153 by heavy-atom neighbour count within 8 Å of
the side-chain centroid in `3ECU` chain A, comparable to I149 (99 neighbours) and L106
(102). It is not a surface phenylalanine whose truncation would be expected to cost
nothing. Its closest structural analogue in the same control set disagrees sharply:

| variant | burial | mutation | heavy atoms deleted | exp ΔΔG |
|---|---|---|---|---|
| F45A | 93 | Phe→Ala | 6 | **+2.07** |
| F64A | 94 | Phe→Ala | 6 | **−0.20** |

The mutations occur at different sites; similar burial and atom counts do not
predict identical thermodynamic effects or invalidate a measurement. F64A's
−0.20 has since been corroborated in the primary table. The compilation's ±0.3
is a methodological estimate, not an individual measurement uncertainty. See
[the primary-source audit](reference_state_audit.md).

**This is not grounds to remove F64A from the gate.** Dropping a control because it
produced a bad FEP number is the same category of post-hoc adjustment as lowering
`min_pearson`, and it would destroy what pre-registration buys. If F64A is ever excluded it
must be on independently established grounds, argued and written down before a gate
evaluation. The source-value question was subsequently resolved; the frozen gate
excluded F64A using its diagnostic cap, not because of disagreement with experiment.

## Status

**Excluded from predictive validation.** The diagnostic failure is itself a
reportable observation. This 18-window run was superseded by the redistributed
ladder and is retained as historical evidence, not a current production recommendation.
