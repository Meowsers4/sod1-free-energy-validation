# Publication improvement plan — CPU work and optional GPU follow-up

Updated 2026-09-14. The user authorized publication-review fixes and stated that GPU access
is available. GPU use is worth considering when it answers a defined scientific question;
availability alone does not repair the mismatched benchmark or establish generality.
This plan preserves the historical gate and introduces no new simulation submission.

## 1. Completed in this revision

| review request | delivered | scientific limit |
|---|---|---|
| Analyze aggregate cancellation | raw reanalysis of 48 records / 912 adjacent pairs; local, net, absolute-sum and maximum diagnostics | alternatives have not demonstrated predictive superiority |
| Strengthen statistics | whole-variant/site bootstrap intervals; leave-one-variant/site-out results; separate 3 ns cohort excluding A4V | only 6 sites overall, 5 in uniform cohort; intervals approximate |
| Clarify benchmark | machine-readable eight-control state/construct/source table; unmatched comparison stated beside gate | no matched experimental measurements were created |
| Correct claims | revised outline, operating document, handoff, current figures; historical preregistration annotated | no causal attribution, equivalence, error multiplier or zero-information claim |
| Quantify disulfide contrast | −0.016918 kcal/mol; SE 0.081993; unpaired Welch 95% interval [−0.296618, +0.262781] | conditional on sampled basins; not a prospective equivalence test |
| Package reproducibility | exact installed CPU dependency closure, runtime record, source/input/derived manifests and portable archive | A4V original raw data remain lost; public release/license not yet selected |

The original seven-point gate still fails at r = 0.326020 and RMSE = 2.123481 kcal/mol.
F64A remains its sole excluded point. The exploratory analysis includes F64A because its
question concerns diagnostic behavior; this does not change the original gate selection.

### What the new audit actually found

F64A folded r1: 0.022705 net hysteresis, 1.678103 absolute local sum, 0.222590 maximum local
magnitude, and 1.202554 sibling disagreement (all kcal/mol). Opposite signs cancel 98.647%
of the absolute local sum in the aggregate.

| folded diagnostic | Pearson, all 24 | site-bootstrap 95% interval | Pearson, uniform 21 |
|---|---:|---|---:|
| net hysteresis | +0.072 | [−0.287, +0.165] | +0.106 |
| sum absolute local discrepancies | +0.104 | [−0.482, +0.341] | +0.189 |
| maximum absolute local discrepancy | +0.158 | [−0.449, +0.285] | +0.206 |
| minimum adjacent overlap | −0.120 | [−0.250, +0.655] | −0.119 |
| within-leg MBAR error | +0.233 | [−0.435, +0.680] | +0.227 |

Intervals describe an empirical resampling exercise on a small, selected set of sites.
They are not population guarantees or evidence of equivalence to zero. See the JSON for
Spearman, variant-bootstrap and every leave-group-out result. Do not select a new acceptance
threshold from this table. The cancellation example explains how the historic summary can
be small; it does not identify the correct free energy or demonstrate a better predictor.

## 2. Next CPU-only work, in order

### A. Independent review of the current paper (roughly 1–2 researcher days)

- Have a computational biophysicist run `release_reproduction.md`, independently inspect the
  F64A equations and redox interval assumptions, and compare Table 2 with primary sources.
- Ask specifically whether native-sequence apo-2SH monomers and the capped-tripeptide
  reference define a defensible observable for the claims being made.
- Record the person's corrections and contributions; do not call a second script by the
  same agent independent human certification.
- Completion criterion: all headline claims are either reproduced and bounded or removed.

### B. Temporal sensitivity within the retained archive (roughly 2–4 CPU work days)

Purpose: determine whether terminal diagnostics conceal early warning or late drift.

1. Add an analysis section to `config/pipeline.yaml` recording selected trajectory-prefix
   fractions, uncertainty procedure, and endpoints **before** looking at prefix results.
2. Extend `src/analysis/diagnostic_audit.py` and its Snakemake rule to re-solve each retained
   leg at those prefixes. Perform equilibration detection/decorrelation using only the prefix;
   full-trajectory thinning would leak future information into an early-stop diagnostic.
3. Compare early summaries with later disjoint time blocks and independently simulated
   repeats. Nested-prefix differences are dependent and cannot be treated as independent errors.
4. Retain the A4V 9 ns cohort separately; the missing 3 ns history cannot be reconstructed.
5. Report trajectories and effect sizes across variants/sites, including all failures. Do not
   train and evaluate a stopping threshold on these same eight variants.

Completion criterion: reproducible temporal trajectories and explicit dependence accounting.
A plateau would still not exclude an unvisited slow mode. This is exploratory SOD1 analysis,
not a prospective performance test.

### C. Feasibility of an external diagnostic benchmark (roughly one week)

Use public archives before considering new simulations. The
[OpenFE industry benchmark](https://github.com/OpenFreeEnergy/IndustryBenchmarks2024) contains
setup/analysis resources and links to its public benchmark; confirm which raw/cumulative data,
repeat IDs, protocol versions and uncertainty fields are actually downloadable.

- Reproduce published terminal estimates on two development targets.
- Inventory independent repeats and time-resolved data, missingness, licenses and observable.
- Choose a separate held-out target pool before evaluating outcomes. Keep chemical series,
  shared ligands and transformations together to limit leakage.
- Binding free energies are a **new validation domain**, not additional SOD1 folding points.
  Equilibrium ladder hysteresis may not transfer directly to replica-exchange or
  nonequilibrium work data; preserve estimator-specific definitions.
- Stop this route if the data cannot support independently repeated outcomes and diagnostics
  measured at the proposed decision time. Final ΔΔG tables alone are insufficient.

### D. Preregister the external evaluation before testing held-out targets

Primary question: at a fixed compute budget or retained fraction, which observable diagnostics
reduce false reassurance about disagreement with an independent repeat?

Secondary, separate question: do they flag discrepancy from **state-matched** experiment?
Repeat agreement is not experimental accuracy. Include experimental uncertainty when available.

- Compare with simple baselines: elapsed simulation time, MBAR-reported uncertainty, overlap,
  and independent-repeat SEM when the deployment budget includes multiple repeats.
- Choose the scientifically meaningful discrepancy tolerance, reporting fraction and required
  improvement on development data and practical needs; freeze them before held-out evaluation.
- Report false reassurance, retained fraction, calibration/coverage, and uncertainty grouped
  by target. An additional diagnostic must improve decisions at comparable cost/retention.
- Maintain failure/incomplete-case accounting and validate software on analytical examples.
- Success criterion: reproducible held-out benefit with uncertainty supporting the claimed
  improvement; otherwise publish the bounded negative result without claiming a new rule.

This is a substantial follow-up project. The present SOD1 note need not wait for it, provided
its claims remain local. The principle that self-consistency can miss error is established
prior art, including [Kang et al. 2026](https://www.nature.com/articles/s41467-026-74165-y).

## 3. Where GPU work could add evidence

### Highest-value use for the current diagnostic story: independent conformational starts

Question: are repeat agreement and the diagnostic's apparent stability sensitive to protein
starting conformations, beyond changing solvent boxes and velocities?

Candidate development case: F64A, chosen because the observed discrepancy motivates the test.
A second case should be selected by a fixed structural/protocol criterion before results,
not retrospectively because it helps the story. This selection would make the experiment a
mechanistic follow-up on known cases, not an unbiased external benchmark.

Design requirements before submission:

1. Keep apo-2SH and the same force field, observable and reference. Generate demonstrably
   distinct equilibrated protein conformations; independent solvent placement is insufficient.
2. Separate conformation generation from evaluation. Record selection rules, random seeds,
   total burn-in, and retained frames; do not select starts based on desired ΔG outcomes.
3. Use repeated simulations per starting-conformation group so start effects can be separated
   from velocity/solvation variability. Preregister the number of starts/repeats and duration.
4. Preserve energy histories and enough downsampled structural trajectories to inspect the
   putative slow mode. This requires an explicit arm-specific retention policy and disk budget.
5. Compare local diagnostics, conditional uncertainty and between-start disagreement at fixed
   lengths. No re-gate and no claim that disagreement identifies the correct basin.
6. Use a new immutable arm directory and manifest containing full topology, force-field files,
   software versions, generated MDPs and all seeds. Never overwrite or resume historical runs.

Cost anchor: the recorded 3 ns folded window took about 15 min on an L40S. One folded
20-window ladder is about 5 GPU-hours, plus preparation and unfolded work. Nine ladders
(three starts × three repeats) for one variant are therefore about 45 GPU-hours of **folded
production only**, at the historical speed. Conformation generation, equilibration, failed
runs and any longer production are additional. At 9 ns the production component is roughly
three times larger. These are planning estimates, not scheduler accounting or a commitment.

A GPU budget around 100 hours could support a tightly bounded pilot if usable starts can be
obtained cheaply. Several hundred hours could support more starts/cases or longer trajectories.
Spending it across many windows started from the same protein conformation may leave the
central uncertainty unchanged. No automatic time extension after inspecting outcomes.

### If the objective is a stronger SOD1 biology/prediction paper

A matched experimental benchmark comes first. Assemble apo-2SH measurements with compatible
construct, temperature, pH and unfolding definition. If inadequate, a separate apo-SS arm
matched to the monomeric experimental construct is a possible new project, requiring explicit
selection and preregistration. Matching redox alone does not fix F50E/G51E/C6A/C111A, pH,
unfolded-reference adequacy or dimer measurements. New wet-lab collaboration may be more
valuable than additional GPU time if the desired physical-state measurements do not exist.

Only after that audit should one allocate GPU time to blinded, replicated predictions over
multiple independent sites, with uncertainty and prespecified exclusions. Keep the historical
failed gate visible. No VUS, charge-changing or holo prediction campaign follows from the
current GPU availability statement.

## 4. Recommended sequence

Finish the current release and independent human review → temporal CPU sensitivity → external
archive feasibility → preregister the selected independent test. Use GPUs when that test
requires new conformation/trajectory evidence. The subsequently selected GPU experiment is the
bounded F64A exact-path continuation pilot; no other
arm has been selected or submitted. Its L40S model, eight-task concurrency, and resource
budget are fixed in `pilots/f64a_sampling_extension_v1/`.
