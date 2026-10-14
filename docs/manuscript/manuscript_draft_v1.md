---
title: "Local diagnostic cancellation and experimental-state incompatibility in a SOD1 free-energy validation campaign"
author: "[AUTHORS AND AFFILIATIONS — to be decided by the rights holders]"
date: "Draft v1, revised 2026-10-13 — not submitted"
---

<!--
Drafting rules for this file (remove before submission):
- Numbers are traced to analysis reports or explicitly identified historical records;
  see SUBMISSION_CHECKLIST.md for the source map and missing-data exception.
- Claim boundaries: docs/methods_limitations_outline.md "Submission boundaries" and
  docs/conclusion_reconciliation_2026-09-18.md govern. Do not add "first", "novel", a new FEP
  method, matched predictive validation, a diagnostic-superiority claim, a structural mechanism,
  or "we show SOD1 variants are destabilizing".
- Reference verification sources are recorded in citations.md.
-->

# Abstract

Alchemical free-energy calculations are increasingly used to estimate how missense mutations
change protein folding stability, and their reliability is usually judged with aggregate
convergence diagnostics and agreement with experimental controls. We report a pre-registered
validation campaign for the apo, disulfide-reduced (apo-2SH) monomer of human Cu/Zn superoxide
dismutase 1 (SOD1), computed with GROMACS, pmx hybrid topologies and equilibrium λ-window
sampling analyzed by MBAR. The gate required Pearson r ≥ 0.70, RMSE ≤ 1.5 kcal/mol and median
net forward/reverse hysteresis ≤ 0.75 kcal/mol against eight charge-conserving experimental
controls. It failed: seven usable variants gave r = 0.326 and RMSE = 2.123 kcal/mol, and F64A
was excluded by a pre-specified per-variant hysteresis cap. Prospective predictions were
therefore withheld. Post-verdict audits identified two limitations of the validation procedure
itself. First, the historical diagnostic is the absolute value of a sum of signed adjacent-window
discrepancies and can conceal large local disagreement: in one F64A folded-leg ladder, net
hysteresis was 0.023 kcal/mol while the summed absolute discrepancy was 1.678 kcal/mol (98.6%
cancellation). Separately registered continuations of that ladder showed that the small early
aggregate did not certify duration stability: the estimate moved by −2.08 kcal/mol between
disjoint 3-ns blocks, and repeat movements of opposite sign persisted through 15 ns. Across
the folded-leg archive, neither net nor absolute local diagnostics showed a resolvable
association with disagreement between independently solvated repeats. Second, the experimental references were
not state-matched: all were measured with the Cys57–Cys146 disulfide intact, on cysteine-
substituted constructs, and two were whole-dimer calorimetric transitions at 49.4 °C. We report
these as limitations of one validation design, not as a validated diagnostic, a structural
mechanism, or an accuracy estimate for apo-2SH SOD1.

# 1. Introduction

Mutations in *SOD1* cause a subset of familial amyotrophic lateral sclerosis, and many
disease-associated variants destabilize the immature, metal-free protein [@lindberg2005;
@nordlund2006; @nordlund2009]. Alchemical free-energy (FE) calculations offer a physics-based
estimate of the folding free-energy change of a point mutation, ΔΔG, through a thermodynamic
cycle that transforms the residue in a folded protein and in an unfolded-state reference
[@seeliger2010; @gapsys2016]. The approach has been benchmarked extensively on other proteins
[@seeliger2010; @gapsys2016], and the GROMACS/pmx toolchain used here has been applied to
SOD1 variants along the maturation pathway, including the apo-2SH state, with non-equilibrium
transitions [@wells2021]. This study does not introduce a new FE method, nor is it the first
application of this toolchain to SOD1.

Before applying such a calculation to uncharacterized variants, a common safeguard is a
validation gate: reproduce experimental controls to a pre-declared accuracy, and require
convergence diagnostics to pass. Best-practice guidance emphasizes that diagnostics such as
overlap and forward/reverse agreement are necessary rather than sufficient indicators of
adequate sampling, and recommends time-resolved checks and independent repeats [@klimovich2015;
@mey2020]. Two practical questions are less often reported for a concrete campaign: what a
specific aggregate diagnostic can conceal, and whether the experimental controls describe the
same thermodynamic state as the simulation.

Here we report a campaign that pre-registered its gate thresholds before any evaluation, failed
that gate, and then audited both the diagnostic and the benchmark. We preserve the original
verdict, exclusion and thresholds, and we label every subsequent analysis as post-verdict and
exploratory unless it was separately registered. Our contributions are bounded: (i) a
quantified example of signed-discrepancy cancellation in the historical net hysteresis metric,
with a grouped analysis showing that neither that metric nor simple absolute alternatives
resolved folded-leg repeat disagreement in this archive; (ii) registered exact-path continuations
showing that a small early aggregate did not certify later duration stability on one selected path;
(iii) a chain-of-custody audit showing that the experimental controls differed from the
simulated state in redox state, construct, oligomeric transition and temperature; and (iv) two
bounded sensitivity results (A4V sampling extension and a G93A disulfide contrast).

# 2. Methods

## 2.1 Simulated state and variant panel

The simulated species was the apo, disulfide-reduced SOD1 monomer (153 residues, mature
numbering; the precursor N-terminal Met is excluded). This state was chosen before the campaign
as the aggregation-prone, metal-free species and to avoid metalloprotein parameterization; it
was not chosen to match the experimental controls (Section 3.4). The validation subset
comprised eight charge-conserving variants with tabulated experimental ΔΔG: F64A, I18V, I113T,
A4V, G93A, G93S, I149A and G93V. Charge-changing variants were excluded because a net-charge
change under PME introduces finite-size artifacts that do not cancel between legs with
different box sizes, and the engine had no counterion co-alchemy. Experimental values were
taken from a published compilation [@kumar2017] and traced to primary tables (Section 3.4).

## 2.2 System preparation

The folded leg started from chain A of PDB 3ECU. Disordered internal loops were rebuilt with
PDBFixer, heteroatoms including metals and crystallographic waters were removed, and the
Cys57–Cys146 disulfide recorded in the deposited structure was broken before protonation at
pH 7.0 so that both cysteines carried thiol hydrogens. The wild-type structure was processed
with `pdb2gmx`; hybrid residues were generated with `pmx mutate` and `pmx gentop` [@gapsys2015]
using the `amber99sb-star-ildn-mut` force field [@best2009; @lindorfflarsen2010] and TIP3P water
[@jorgensen1983]. `pdb2gmx` disulfide prompts were answered "no" for every cysteine, and a
topology guard failed the build if any SG–SG bond was present. The unfolded-state reference
was a capped tripeptide (ACE–X–Y–Z–NME) carrying the native flanking residues, with the
mutated residue in the central position. Each system was placed in a cubic box with 1.2 nm
padding, solvated, neutralized and brought to 0.15 M NaCl, and energy-minimized.

Each of three replicates per leg used an independently solvated and ion-placed system
(`independent_replicate_systems`), with deterministic seeds. Independent solvation does not
establish independent coverage of protein conformational basins; it removes the shared-box
dependence of earlier replicates.

## 2.3 Alchemical sampling

Each leg used 20 λ states with a refined high-λ endpoint (λ = 0, 0.0588, 0.1176, 0.1765, 0.2353,
0.2941, 0.3529, 0.4118, 0.4706, 0.5294, 0.5882, 0.6471, 0.7059, 0.7647, 0.8235, 0.8824, 0.92,
0.95, 0.975, 1.0). A single λ vector drove both electrostatic and Lennard-Jones terms with
Beutler soft-core (α = 0.3, power 1, σ = 0.25 nm, soft-core Coulomb enabled). Because a
minimization without the free-energy block relaxes real atoms into appearing dummy atoms,
each window was minimized at its own λ before production. Production used the GROMACS
stochastic-dynamics integrator (2 fs, collision rate 1 ps⁻¹) at 298.15 K, C-rescale isotropic
pressure coupling at 1 atm, PME electrostatics with 1.0 nm real-space and van der Waals
cutoffs, long-range dispersion corrections, and LINCS constraints on bonds to hydrogen.
Reduced potentials at all 20 states were written at a stride targeting 3,000 retained
records per window (3,001 in the surviving attempt-1 archive because the boundary record
was retained).
GROMACS 2025.3 (CUDA build) [@abraham2015] ran one window per NVIDIA
L40S GPU.

In gate attempt 1 (protocol identifier `822108e9db71124d`), each window of both legs used
0.5 ns discarded equilibration and 3 ns production (8 variants × 2 legs × 20 states × 3
replicates = 960 windows). A single registered protocol change for attempt 2 (Section 3.5)
extended the folded leg of A4V only to 2 ns equilibration and 9 ns production; the unfolded
windows were reused unchanged. Every window recorded its engine and a hash of its production
parameters, and the analysis refused to combine windows with differing hashes or engines.

## 2.4 Free-energy estimation and the historical diagnostic

For each leg and replicate, every window's reduced-potential series was trimmed at the later
of two automatically detected equilibration times — for the sampled-state energy and for the
neighbor energy difference — and thinned at the larger of the two statistical inefficiencies
[@chodera2016]. Leg free energies were estimated by MBAR [@shirts2008] with pymbar. ΔΔG was
the folded-minus-unfolded difference averaged over replicates; its reported uncertainty was
the larger of the propagated MBAR error and the replicate standard error of the mean. That
uncertainty is conditional on the sampled states; it does not include force-field or
reference-state error or unvisited conformational modes.

The historical diagnostic, termed "cycle closure" in the project code, is a forward/reverse
hysteresis of one λ ladder, not a closed thermodynamic cycle. For adjacent states k and k+1,
let d_k be the difference between the forward exponential-averaging estimate (samples from k)
and the reverse estimate (samples from k+1). The ladder hysteresis is

H = |Σ_k d_k|,

and each variant's value was the maximum H over its six leg–replicate ladders. Because signed
d_k can cancel, we also report the descriptive summaries S = Σ_k |d_k| and M = max_k |d_k|,
and the cancellation fraction 1 − H/S. These depend on the number and placement of λ states;
all comparisons here use the same 20-state schedule.

## 2.5 Pre-registered gate

Thresholds were fixed on 2026-08-07, before any gate evaluation: Pearson r ≥ 0.70, RMSE ≤ 1.5
kcal/mol, median per-variant hysteresis ≤ 0.75 kcal/mol, at least six usable variants, and a
per-variant hysteresis cap of 1.0 kcal/mol for exclusion. Spearman ρ was reported without a
threshold. A pre-declared pivot applied if r fell below 0.60: reframe the work as a methods and
sampling-limits study rather than retune. Failure of the gate prohibited predictions for
uncharacterized variants, and this prohibition was enforced in code.

## 2.6 Post-verdict audits

All analyses in this section were defined after the gate verdict and are exploratory unless
stated otherwise. None revises the verdict.

*Archive re-derivation.* All 48 retained (variant, leg, replicate) ladders (912 adjacent pairs)
were re-solved from the archived reduced-potential files. A4V's attempt-1 folded windows had
been overwritten by the attempt-2 run, so its gate point survives only as a run-time record;
its retained ladders are the 9-ns folded data.

*Grouped diagnostic association.* For each folded and unfolded ladder we computed the
disagreement with its two independently solvated siblings, |ΔG_i − mean(ΔG_j, j ≠ i)|, and
its association with H, S, M, minimum adjacent overlap and conditional MBAR error. Because
disagreements reuse sibling estimates, rows are dependent; 24 folded ladders are nested in
eight variants at six sites. We therefore report Pearson and Spearman coefficients with 95%
percentile intervals from 2,000 whole-variant and whole-site bootstrap draws, leave-one-group-
out values, and a separate seven-variant attempt-1 cohort excluding A4V. No row-wise p-values
are reported.

*Retrospective temporal analysis.* Each attempt-1 window was split into four non-overlapping
quarters. Estimates from cumulative prefixes ending at 25%, 50% and 75% were compared with an
estimate from the final quarter alone, recomputing trimming and thinning for every interval.

*Registered F64A continuations.* Two separately registered folded-only continuations extended
the identical F64A apo-2SH paths (same 20 states × 3 repeats; no new starts, velocities or
unfolded legs): v1 from 3 to 9 ns of retained sampling and v2 from 9 to 15 ns. The v2 primary
endpoint was the paired movement from the retained 9–12 ns block to the 12–15 ns block under
the adaptive trimming policy, reported alongside two fixed policies (untrimmed with thinning;
fixed 25% trim with thinning) that reuse the same data. No structural trajectories were
retained under the production output policy. A further descriptive audit computed neighbor
and fixed λ-pair reduced-energy drift against actual λ from all 60 v2 energy files.

*Benchmark-state audit.* Each control value was traced from the compilation to its primary
table, recording transition, redox state, metal state, construct, temperature, pH and method.
A post-verdict sensitivity analysis varied only the normalization and temperature treatment of
the two dimer calorimetric controls, keeping every prediction and the exclusion fixed.

*G93A disulfide contrast.* A pre-registered diagnostic repeated the G93A attempt-1 protocol
with the Cys57–Cys146 disulfide intact (three independently solvated folded and unfolded
systems), verified the redox state of each arm by parsing atom and bond tables, and compared
folded ΔG between arms with an unpaired Welch interval.

## 2.7 Reproducibility

CPU-only workflow targets re-derived estimates and diagnostics from the surviving energy
archives. The gate-of-record comparison preserves A4V's attempt-1 estimate from its historical
run-time record: its folded raw windows were overwritten and cannot be re-derived. The source
map distinguishes this preserved value from estimates regenerated from raw energies.
The F64A temporal figure builder checks its source-report hashes and specified quoted values;
supplementary images are checked against pinned hashes before copying. A forensic release
bundles the historical archive manifest, configuration, analysis code and figure builders;
the later continuation reports and manuscript figure assembly are separate repository
artifacts (Data availability).

Software versions are recorded by analysis rather than assigned retrospectively to all runs.
The local forensic reproduction environment is pinned in `env/analysis-lock.txt` (Python
3.13.9, pymbar 4.0.3, NumPy 2.3.5 and SciPy 1.16.3). The saved F64A v1 block and v2 continuation
reports instead record Python 3.11.15, pymbar 4.2.0, NumPy 2.4.6, and JAX/jaxlib 0.10.2 on SCC.
The original gate environment specification required pymbar ≥ 4 without an exact pin;
neither the local lock nor the later continuation versions establishes its original runtime
version. This is a historical software-provenance limitation. Recorded per-analysis identities
are retained with the reports.

# 3. Results

## 3.1 The pre-registered gate failed

The gate failed on correlation and error (Table 1; Fig 1). Seven usable variants gave Pearson
r = 0.326, Spearman ρ = 0.500, RMSE = 2.123 kcal/mol and mean unsigned error 1.785 kcal/mol;
median hysteresis (0.22 kcal/mol at evaluation; 0.225 when re-derived from the archived windows)
and the point count passed. F64A was excluded because its maximum ladder hysteresis was 1.104
kcal/mol, above the pre-specified 1.0 kcal/mol cap; the exclusion followed the registered
criterion, not the value of its estimate. Pearson r fell below the 0.60 pivot line, so the work
was reframed as reported here and no uncharacterized variant was simulated.

Errors were positive for all four non-glycine variants and negative for all three G93
substitutions; the experimental span at position 93 was 4.57 kcal/mol, and the computed span
1.63 kcal/mol. We record this pattern without assigning a cause: Sections 3.4–3.6 show that
the comparison combines calculation error with benchmark heterogeneity, and the present data
cannot separate them. The gate justified withholding predictions. It does not measure accuracy
against matched apo-2SH experiments or isolate force-field error.

**Table 1. Gate of record (attempt 1).** Experimental values are the compilation values used
by the gate (kcal/mol, positive = destabilizing). FEP values are mean ± reported uncertainty
over three replicates.

| Variant | Experimental | FEP | Error | Max. ladder H |
|---|---:|---:|---:|---:|
| I18V | 0.37 | 0.83 ± 0.21 | +0.46 | 0.18 |
| I113T | 1.25 | 2.59 ± 0.23 | +1.34 | 0.22 |
| A4V | 1.62 | 3.54 ± 0.39 | +1.92 | 0.66 |
| G93A | 2.43 | 1.26 ± 0.06 | −1.17 | 0.04 |
| G93S | 3.70 | 1.20 ± 0.07 | −2.50 | 0.12 |
| I149A | 4.05 | 4.98 ± 0.16 | +0.93 | 0.77 |
| G93V | 7.00 | 2.83 ± 0.08 | −4.17 | 0.67 |
| F64A | −0.20 | 6.94 ± 0.34 | excluded | 1.10 |

All documented attempt-1 estimates except A4V's gate point re-derive from the archived windows
to floating-point rounding; A4V's 3-ns folded windows were overwritten in place by the attempt-2
run, and no later analysis can repair that missing record.

## 3.2 The net hysteresis metric cancels signed local discrepancies

H can be small while adjacent forward/reverse estimates disagree substantially, because d_k of
opposite sign cancel in the sum. In F64A folded replicate r1 at 3 ns, H = 0.022705 kcal/mol,
whereas S = 1.678103 and M = 0.222590 kcal/mol, a cancellation fraction of 98.647% (Fig 2).
The same ladder had the largest disagreement with its independently solvated siblings in the
archive, 1.202554 kcal/mol. Cancellation concerns the reported diagnostic; it does not show
that cancellation caused the MBAR estimate to be wrong, or that either sibling is correct.

Across the archive, the historical metric did not track sibling disagreement on the folded leg:
over 24 folded ladders, Pearson r = +0.072 and Spearman ρ = +0.080 (Fig S1). The descriptive
alternatives did not resolve an association either (Table 2). Every folded-leg 95% interval,
under both variant and site resampling and in both cohorts, included zero. On the unfolded leg,
conditional MBAR error was positively associated with disagreement (r = 0.421; variant-bootstrap
interval 0.087 to 0.646; site-bootstrap 0.025 to 0.609), and the variant-grouped Pearson
interval for H narrowly excluded zero (0.020 to 0.759) while its site-grouped interval did not.
With so few groups these intervals are approximate, and the near-zero folded correlations do
not establish an absence of diagnostic information in a wider population. We select no
threshold from the F64A example.

**Table 2. Association between ladder diagnostics and sibling disagreement, folded leg.**
Point estimates over 24 ladders (eight variants, six sites); 95% percentile intervals from
2,000 site-bootstrap draws.

| Diagnostic | Pearson r [95% site interval] | Spearman ρ [95% site interval] |
|---|---|---|
| Net hysteresis H | +0.072 [−0.29, +0.16] | +0.080 [−0.31, +0.32] |
| Sum of absolute discrepancies S | +0.104 [−0.48, +0.34] | +0.162 [−0.49, +0.47] |
| Maximum local discrepancy M | +0.158 [−0.45, +0.28] | +0.136 [−0.61, +0.42] |
| Minimum adjacent overlap | −0.120 [−0.25, +0.65] | −0.189 [−0.31, +0.55] |
| Conditional MBAR error | +0.233 [−0.43, +0.68] | +0.017 [−0.47, +0.65] |

Overlap did not order the gate errors either. The two thinnest ladders in the archive (I18V,
minimum adjacent overlap 0.0054; I149A, 0.0096) belonged to the two variants with the smallest
gate errors, and G93A had the lowest variant hysteresis (0.045) but an error of −1.17 kcal/mol.

## 3.3 A small early aggregate did not certify duration stability

The retrospective quarter analysis showed that attempt-1 estimates were still moving within
the retained 3 ns. For folded ladders, the median absolute difference between the 75% prefix
and the final quarter was 0.311 kcal/mol (maximum 1.070). The median of the 21 per-record
ratios of absolute movement to combined conditional MBAR uncertainty was 2.43, with each
denominator calculated as the square root of the sum of the two squared MBAR errors;
12 of 21 primary-cohort records exceeded a ratio of two. This quadrature scale does not
estimate covariance between the blocks. At the 25% prefix the folded median was 0.368 kcal/mol
(maximum 1.808, F64A r1). These are descriptive scale comparisons on dependent data, not tests.

The registered v1 continuation extended all three F64A folded paths from 3 to 9 ns (Fig 3a).
Replicate r1 moved from 2.505942 kcal/mol in its first retained 3-ns block to 0.429467 kcal/mol
in the disjoint 6–9 ns block, a change of −2.076474 kcal/mol, despite an early net hysteresis of
0.022705 kcal/mol. The other two repeats moved by −0.691 and −0.584 kcal/mol between the same
blocks. The cumulative mean changed from 1.704 to 0.771 kcal/mol between 3 and 9 ns, and the
repeat range narrowed by 71%. The small early net hysteresis coexisted with the
−2.076474 kcal/mol movement between the 0–3 and 6–9 ns blocks (Fig 3b). This is an
exact-path counterexample to treating a small aggregate as a duration-stability certificate.
It is a selected case, not a prospective validation cohort, and neither block is an
established equilibrium value.

The registered v2 continuation extended the same paths to 15 ns. Under the adaptive policy, the
primary paired movement from 9–12 to 12–15 ns averaged −0.049510 kcal/mol, but this small mean
reflected opposing repeat movements: r0 −0.051, r1 −0.695174 and r2 +0.598142 kcal/mol (Fig 3c).
Both fixed policies gave upward mean movements, +0.579425 (untrimmed) and +0.410739 kcal/mol
(fixed 25% trim), from the same raw data. The adaptive repeat range was 2.047618 kcal/mol in the
9–12 ns block and 1.946359 kcal/mol in the 12–15 ns block. Repeat estimates therefore did not
agree, and their movement depended on the selection policy, through 15 ns.

Adaptive selection was strongly time-local at the highest λ values (Fig 3d; Fig S4). In the
12–15 ns block, the selected suffix for r2 at λ = 0.95 kept 32 of 3,000 raw records, leaving
seven samples after thinning. Sparsity was not confined to the adaptive cutoff: in the same
block both fixed policies retained 10 or fewer samples for r1 at that window, with estimated
statistical inefficiencies near 330. Short selected suffixes and a quiet aggregate cannot
certify equilibrium.

A descriptive audit of all 60 v2 energy files found larger neighbor-energy drift toward high λ.
Taking window medians over repeats, blocks and directions, the median absolute half-block drift
was 0.0223 kT for windows 0–9 and 0.0843 kT for windows 10–19 (Spearman ρ with window index,
0.848), and the pattern was present in each repeat separately (Figs S2–S3). This localizes an
energy observable. It does not establish a structural mechanism, cavity hydration or that
low-λ paths are equilibrated; window 9 lies at λ = 0.53, so low-index windows are not
wild-type-like controls. The F64A hybrid removes six ring heavy atoms while retaining CB;
cavity hydration or repacking around that site remain hypotheses, untested here because no
structural trajectories were retained.

## 3.4 The experimental controls were not state-matched

All eight gate values traced to primary tables (Table 3). Six — A4V, G93A and I113T [@lindberg2005];
F64A, I18V and I149A [@nordlund2006] — are monomer urea-unfolding measurements on a C6A/C111A/
F50E/G51E construct in 10 mM MES, pH 6.3, at 25 °C. Both sources state that the Cys57–Cys146
disulfide was kept intact. The remaining two, G93S and G93V [@stathopulos2006], are apo
native-dimer differential scanning calorimetry results on a C6A/C111S construct at pH 7.8,
analyzed as a cooperative two-unfolded-monomer transition and reported at a common 49.4 °C,
also under non-reducing conditions. The simulation used the reduced, native-sequence monomer,
prepared at pH 7.0 and simulated at 298.15 K. No control was fully matched.

The compilation's uniform ±0.3 kcal/mol [@kumar2017] is a blanket methodological estimate
across sources, not a per-point measurement error. Opposite-signed residuals reject a single
additive offset between states, but not mutation-dependent responses to the same state or
construct change.

**Table 3. Experimental-state compatibility of the gate controls.**

| Variants | Source | Transition | Redox | Construct | T (°C) | pH | Method |
|---|---|---|---|---|---:|---:|---|
| A4V, G93A, I113T | Lindberg 2005, Table 1 | monomer unfolding | SS | C6A/C111A/F50E/G51E | 25 | 6.3 | urea |
| F64A, I18V, I149A | Nordlund & Oliveberg 2006, Table 1 | monomer unfolding | SS | C6A/C111A/F50E/G51E | 25 | 6.3 | urea |
| G93S, G93V | Stathopulos 2006, Table 2 | native dimer → 2 unfolded | SS | C6A/C111S | 49.4 | 7.8 | DSC |
| Simulation | this work | monomer mutation cycle | 2SH | native sequence | 25 | 7.0 (prep.) | MD/MBAR |

Because G93S and G93V carry the largest gate residuals, the aggregate metrics were sensitive to
how those two references are treated (Fig 4). Converting both to 25 °C and halving the dimer
transition, with every prediction fixed, gave r = 0.754 and RMSE = 1.074 kcal/mol under a
constant heat-capacity assumption, or r = 0.767 and RMSE = 1.117 with a temperature-dependent
heat capacity. Neither scenario is a gate pass. The scenarios were constructed after the
verdict; halving a cooperative dimer transition does not make it an isolated-monomer
measurement or match construct and redox state; and naive propagation of the reported absolute
uncertainties gives about ±1.2 kcal/mol per halved 25 °C reference, not ±0.3. The analysis shows
only that the failed gate measured calculation error together with benchmark heterogeneity.

## 3.5 Extending A4V folded sampling narrowed repeat spread but left the reference discrepancy

Attempt 2 extended the A4V folded leg from 3 to 9 ns of production and from 0.5 to 2 ns of
equilibration, reusing the unchanged unfolded leg (Fig 5). The folded ΔG range across three
independently solvated repeats fell from 1.46 to 0.27 kcal/mol, and the replicate ΔΔG range from
1.34 to 0.25 kcal/mol. ΔΔG moved from 3.54 ± 0.39 to 3.36 ± 0.08 kcal/mol, and its discrepancy
from the unmatched reference from +1.92 to +1.74 kcal/mol. Production length and equilibration
changed together, so this is a bundled protocol comparison, not an isolated duration effect.
Reduced spread is improved observed repeat precision, not demonstrated basin coverage, and the
result does not exclude effects of longer sampling or other starting conformations. Attempt 2
was stopped after A4V on cost and limited observed benefit; this is not evidence that further
sampling cannot help. The gate of record remains attempt 1.

## 3.6 Restoring the G93A disulfide did not shift the folded estimate under the tested protocol

Physical inspection of all six folded topologies confirmed the intended redox states: the three
2SH topologies lack the SG–SG bond and retain both thiol hydrogens, and the three SS topologies
contain the bond and lack them. The folded ΔG(SS) − ΔG(2SH) was −0.016918 kcal/mol (standard
error 0.082; unpaired Welch 95% interval −0.297 to 0.263 kcal/mol, 2.68 degrees of freedom;
Fig 6), inside the pre-declared ±0.3 kcal/mol point-estimate band. The interval uses
between-run variation in both arms; matching replicate indices or seeds does not establish
pairing. It is conditional on the sampled basins, excludes force-field bias, unsampled modes
and experimental uncertainty, and is not an equivalence test. A small observed effect over 3 ns
does not rule out slower redox-dependent rearrangements, and this single contrast cannot
explain the gate residuals at other sites.

# 4. Discussion

The campaign did what a pre-registered gate is for: it stopped prospective predictions when
the calculation did not reproduce its controls. The more transferable findings concern why a
gate of this design can be hard to interpret in either direction.

**Aggregate diagnostics.** The historical metric took an absolute value after summing signed
local discrepancies, so it could report near-perfect agreement for a ladder whose local
forward/reverse estimates disagreed by a cumulative 1.7 kcal/mol, and whose estimate later
moved by 2.1 kcal/mol. Reporting signed local discrepancies, their absolute sum and their
maximum alongside any aggregate costs nothing once all-state energies are saved. We do not,
however, resolve an association between these alternatives and folded-leg repeat disagreement
in this archive, and we do not propose a threshold. The appropriate conclusion is narrower:
an aggregate that permits
cancellation should not be presented as evidence of convergence on its own, consistent with
existing guidance [@klimovich2015; @mey2020].

**Duration and selection.** Small early hysteresis preceded a 2.08 kcal/mol difference between
the 0–3 and 6–9 ns blocks on the selected F64A path. Through 15 ns the paired movement depended
on the trimming policy while repeats moved in opposite directions. Adaptive equilibration detection [@chodera2016]
sometimes retained only a few late samples in high-λ windows. A near-zero mean movement is
therefore not evidence of stability when the repeats disagree, and policy dependence should be
reported rather than resolved by choosing a preferred policy after the data are seen.
Independent solvation of repeats is useful but does not establish independent conformational
coverage; denser λ placement can improve statistical bridging between states but does not by
itself accelerate slow dynamics within unchanged states.

**Benchmark state.** Every control was measured on a different chemical species than the one
simulated (disulfide intact, cysteine-substituted constructs), and two were whole-dimer
calorimetric transitions at a different temperature. Uniform compilation uncertainties concealed
this. A failed comparison against such a benchmark does not show that apo-2SH FE calculations
are inaccurate, and a passing comparison would not have shown that they are accurate. For future
validation we recommend recording, for each control, the transition, redox and metal state,
construct, temperature, pH, method and source table before selecting the panel; we did not
assemble a matched apo-2SH benchmark here.

**Practical recommendations.** (1) Preserve signed local diagnostics alongside aggregate values.
(2) Represent the experimental transition and state explicitly when choosing a validation panel.
(3) Keep conditional sampling uncertainty, repeat spread and discrepancy from experiment
separate. (4) Archive immutable run identities, topologies and raw energies before any
resubmission; the A4V attempt-1 windows were lost by overwriting, and a parameter hash alone does
not certify physical identity. (5) Distinguish statistical bridging between λ states from
conformational exploration within states, and compare fixed observables when schedules differ.
(6) Evaluate any proposed stopping rule on external systems before treating it as general.

## Limitations

The archive contains eight variants at six sites with three repeats each, so grouped intervals
are wide and approximate, and diagnostic associations cannot be generalized. Disagreement
values reuse sibling estimates and are dependent. The temporal counterexample is a single
selected path; continuation blocks remain correlated through slow modes; the adaptive and fixed
policies reuse the same data. Conditional MBAR uncertainties exclude unvisited conformations.
No structural trajectories were retained, so no structural interpretation is offered. One force
field, one water model, one starting structure and one soft-core form were used. The unfolded
reference is a capped tripeptide whose adequacy as an unfolded-state model was not tested.
A4V's attempt-1 folded windows are lost. The G93A contrast covers one variant at 3 ns. The
benchmark audit identifies incompatibility; it does not estimate the size of any state-
dependent correction for the simulated species.

# 5. Conclusions

A pre-registered apo-2SH SOD1 folding-stability gate failed against a heterogeneous
experimental compilation and stopped prospective predictions. Its convergence diagnostic could
hide substantial signed local disagreement, a small early value did not certify later duration
stability on a registered continuation, and its experimental controls differed from the
simulated species in redox state, construct, oligomeric transition and temperature. These
findings describe limitations of the validation procedure. They do not identify the physical
cause of the prediction errors, validate an alternative diagnostic, or establish an equilibrium
free energy or an accuracy estimate for apo-2SH SOD1.

# Data availability

[TO COMPLETE BEFORE SUBMISSION — repository/DOI, license.] The analysis code, configuration,
hashed archive manifest, figure builders and all derived reports are in the project repository.
The forensic release (`releases/sod1fep-forensic-review.tar.gz`, with SHA-256 file) and the raw
reduced-potential archives (the surviving attempt-1 windows, the A4V attempt-2 folded leg,
the G93A SS diagnostic, and the F64A v1/v2 continuation energies) must be deposited in a public
archive with a chosen license before submission. A4V's attempt-1 folded raw windows are missing
and will not be part of that deposit; only its historical run-time estimate and uncertainty
survive. The deposit must identify this exception explicitly and include the later continuation
reports and manuscript figure assembly alongside the historical forensic release. Structural
trajectories were not retained under the production output policy.

# Author contributions, funding, competing interests

[TO COMPLETE — by the rights holders. Include computing allocation acknowledgement (Boston
University Shared Computing Cluster) and any funding.]

# Use of AI assistance

[TO COMPLETE — journal policies require disclosure. Describe the use of AI coding and writing
assistance for analysis code, auditing and drafting, and state that all results, numbers and
claims were verified by the authors against the recorded data.]

# References

<!-- Bibliographic verification sources and dates are recorded in citations.md. -->

[@wells2021]: Wells NGM, Tillinghast GA, O'Neil AL, Smith CA. Free energy calculations of
ALS-causing SOD1 mutants reveal common perturbations to stability and dynamics along the
maturation pathway. Protein Sci. 2021;30(9):1804–1817. doi:10.1002/pro.4132.

[@lindberg2005]: Lindberg MJ, Byström R, Boknäs N, Andersen PM, Oliveberg M. Systematically
perturbed folding patterns of amyotrophic lateral sclerosis (ALS)-associated SOD1 mutants. Proc
Natl Acad Sci USA. 2005;102(28):9754–9759. doi:10.1073/pnas.0501957102.

[@nordlund2006]: Nordlund A, Oliveberg M. Folding of Cu/Zn superoxide dismutase suggests
structural hotspots for gain of neurotoxic function in ALS: parallels to precursors in amyloid
disease. Proc Natl Acad Sci USA. 2006;103(27):10218–10223. doi:10.1073/pnas.0601696103.

[@nordlund2009]: Nordlund A, Leinartaite L, Saraboji K, Aisenbrey C, Gröbner G, Zetterström P,
Danielsson J, Logan DT, Oliveberg M. Functional features cause misfolding of the ALS-provoking
enzyme SOD1. Proc Natl Acad Sci USA. 2009;106(24):9667–9672. doi:10.1073/pnas.0812046106.

[@stathopulos2006]: Stathopulos PB, Rumfeldt JAO, Karbassi F, Siddall CA, Lepock JR, Meiering EM.
Calorimetric analysis of thermodynamic stability and aggregation for apo and holo amyotrophic
lateral sclerosis-associated Gly-93 mutants of superoxide dismutase. J Biol Chem.
2006;281(10):6184–6193. doi:10.1074/jbc.M509496200.

[@kumar2017]: Kumar V, Rahman S, Choudhry H, Zamzami MA, Jamal MS, Islam A, Ahmad F, Hassan MI.
Computing disease-linked SOD1 mutations: deciphering protein stability and patient-phenotype
relations. Sci Rep. 2017;7:4678. doi:10.1038/s41598-017-04950-9.

[@seeliger2010]: Seeliger D, de Groot BL. Protein thermostability calculations using alchemical
free energy simulations. Biophys J. 2010;98(10):2309–2316. doi:10.1016/j.bpj.2010.01.051.

[@gapsys2015]: Gapsys V, Michielssens S, Seeliger D, de Groot BL. pmx: Automated protein
structure and topology generation for alchemical perturbations. J Comput Chem.
2015;36(5):348–354. doi:10.1002/jcc.23804.

[@gapsys2016]: Gapsys V, Michielssens S, Seeliger D, de Groot BL. Accurate and rigorous
prediction of the changes in protein free energies in a large-scale mutation scan. Angew Chem
Int Ed. 2016;55(26):7364–7368. doi:10.1002/anie.201510054.

[@klimovich2015]: Klimovich PV, Shirts MR, Mobley DL. Guidelines for the analysis of free energy
calculations. J Comput Aided Mol Des. 2015;29(5):397–411. doi:10.1007/s10822-015-9840-9.

[@mey2020]: Mey ASJS, Allen BK, Bruce Macdonald HE, Chodera JD, Hahn DF, Kuhn M, Michel J,
Mobley DL, Naden LN, Prasad S, Rizzi A, Scheen J, Shirts MR, Tresadern G, Xu H. Best practices
for alchemical free energy calculations [Article v1.0]. Living J Comput Mol Sci. 2020;2(1):18378.
doi:10.33011/livecoms.2.1.18378.

[@shirts2008]: Shirts MR, Chodera JD. Statistically optimal analysis of samples from multiple
equilibrium states. J Chem Phys. 2008;129(12):124105. doi:10.1063/1.2978177.

[@chodera2016]: Chodera JD. A simple method for automated equilibration detection in molecular
simulations. J Chem Theory Comput. 2016;12(4):1799–1805. doi:10.1021/acs.jctc.5b00784.

[@abraham2015]: Abraham MJ, Murtola T, Schulz R, Páll S, Smith JC, Hess B, Lindahl E. GROMACS:
High performance molecular simulations through multi-level parallelism from laptops to
supercomputers. SoftwareX. 2015;1–2:19–25. doi:10.1016/j.softx.2015.06.001.

[@best2009]: Best RB, Hummer G. Optimized molecular dynamics force fields applied to the
helix–coil transition of polypeptides. J Phys Chem B. 2009;113(26):9004–9015.
doi:10.1021/jp901540t.

[@lindorfflarsen2010]: Lindorff-Larsen K, Piana S, Palmo K, Maragakis P, Klepeis JL, Dror RO,
Shaw DE. Improved side-chain torsion potentials for the Amber ff99SB protein force field.
Proteins. 2010;78(8):1950–1958. doi:10.1002/prot.22711.

[@jorgensen1983]: Jorgensen WL, Chandrasekhar J, Madura JD, Impey RW, Klein ML. Comparison of
simple potential functions for simulating liquid water. J Chem Phys. 1983;79(2):926–935.
doi:10.1063/1.445869.

# Figure legends

**Fig 1. Gate of record.** Computed versus experimental ΔΔG for the seven usable controls of
attempt 1, with the excluded F64A marked by its pre-specified hysteresis exclusion. Experimental
references are not state-matched to the simulation (Table 3). File: `docs/review/gate_of_record.png`.

**Fig 2. Signed local discrepancies and alternative summaries.** Top left: signed adjacent
forward/reverse discrepancies d_k along the 20-state ladder for F64A folded r1 at 3 ns (H = 0.023,
S = 1.678, M = 0.223 kcal/mol; 98.6% cancellation). Other panels: sibling disagreement against
H, S and M for all 24 folded ladders (eight variants, six sites; points are dependent). Squares
are A4V's retained 9-ns ladders; red marks F64A r1. File: `docs/review/diagnostic_cancellation.png`.

**Fig 3. F64A folded-leg temporal behavior on registered exact-path continuations.**
(a) Folded-leg ΔG estimates in disjoint 3-ns retained blocks for three repeats (adaptive policy;
error bars, conditional MBAR uncertainty, which excludes unvisited conformations). v1 covers
0–9 ns and v2 9–15 ns; the 6–9 ns block is identical in both reports. (b) Net hysteresis H for the
same blocks. (c) Primary v2 paired movement from 9–12 to 12–15 ns for each repeat under the three
saved policies, which reuse the same data; bars are policy means. (d) Adaptive retained suffix
length per window against actual λ in the 12–15 ns block. Values are not equilibrium free
energies or experimental comparisons. File: `docs/manuscript/figures_v1/fig6_f64a_temporal.pdf`.

**Fig 4. Reference sensitivity with fixed predictions.** Frozen predictions against four
reference constructions that differ only in G93S/G93V: gate of record, dimer normalization only,
25 °C conversion only, and both (constant heat capacity). Temperature-dependent heat-capacity
scenarios are reported in the text. Post-verdict scenarios, not gate evaluations.
File: `docs/review/reference_sensitivity.png`.

**Fig 5. A4V bundled sampling extension.** Left: folded ΔG of three independently solvated
repeats at 3 ns and 9 ns folded production (bars, means; spread 1.46 and 0.27 kcal/mol). Right:
replicate ΔΔG and mean ± reported uncertainty against the unmatched experimental reference
(1.62 kcal/mol). Production and equilibration changed together. File:
`docs/review/a4v_sampling_sensitivity.png`.

**Fig 6. G93A disulfide contrast.** Replicate folded ΔG for 2SH and SS arms (diamonds, mean ±
replicate SD) and the conditional unpaired Welch interval for SS − 2SH. File:
`docs/review/g93a_disulfide_diagnostic.png`.

**Fig S1.** Historical net hysteresis against sibling disagreement for 24 folded ladders.
File: `docs/review/convergence_diagnostic.png`.

**Fig S2.** Fixed λ-pair reduced-energy half-block drift on every v2 path against actual λ.
File: `docs/manuscript/figures_v1/figS2_lambda_fixed_pair.png`.

**Fig S3.** Neighbor reduced-energy drift, slope and variability per window against actual λ.
File: `docs/manuscript/figures_v1/figS3_lambda_neighbor.png`.

**Fig S4.** Directional adjacent overlap and adaptive-selection context against actual λ.
File: `docs/manuscript/figures_v1/figS4_adaptive_selection.png`.
