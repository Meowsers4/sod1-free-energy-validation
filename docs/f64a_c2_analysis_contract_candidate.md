# F64A C2 CPU analysis contract candidate

Status: **reviewable design, 2026-10-03; no protein analysis or production execution selected**. This follows the [accepted branch fixture](f64a_c2_branch_fixture_result.md) and [post-fixture design review](f64a_c2_post_fixture_production_design.md). It specifies what a CPU-only analyzer must validate before any C2 production registration. The agent did not access SCC.

The first pure [analysis core](../src/analysis/f64a_c2_analysis_core.py)
now validates a complete sampled-state ladder of finite, dimensionless
all-state energies against ordered lambda labels and an even retained-time
grid. It excludes an optional single boundary record and computes
covariance-safe squared-movement bounds. Eleven focused
[tests](../tests/test_f64a_c2_analysis_core.py) pass. They
test arithmetic and rejection behavior, including an independent-Gaussian
stationary example; they do **not** calibrate MBAR errors, HREX dependence,
the joint variance, or any protein outcome. A runnable analysis stage and
Snakemake target await those choices.

The new read-only [GROMACS XVG adapter](../src/analysis/f64a_c2_gromacs_inputs.py)
validates the observed total-energy/dH/dlambda/20-foreign-energy/pV legend
layout, sampled-state identity, temperature, ordered lambda labels, finite
numeric rows, self-state zero, and the fixed time grid relative to an explicit
branch origin. It verifies the SHA-256 of a JSON manifest and all files named
by that manifest before admitting explicitly named state XVGs. A second hash
check protects each XVG as it is parsed. Its
[tests](../tests/test_f64a_c2_gromacs_inputs.py) include a portable excerpt
from the user-supplied Stage P state-0 GROMACS output, fixture SHA-256
`b22fbc6c5d5a2f06c743bdd26d7234e81eaf554782f78b4c9118db03a45adbd0`,
and synthetic sealed-ladder corruption checks. The excerpt was a technical
4-ps output, not a C2 production sample. The parser retains **raw
foreign-state energy differences in kJ/mol**. A separate same-temperature
helper converts them to dimensionless, per-configuration-centered MBAR
potentials using `1/(RT)`. A constructed two-state harmonic test confirms
that PyMBAR's endpoint contrast is unchanged by this row-wise centering.
An independent `alchemlyb` 2.4.1 comparison on the **excerpt** now passes:
21 records and 20 state columns agreed after row-centering to a maximum
`2.7817e-11 kT`. A complete sealed multi-state GROMACS comparison is still
required before protein use. No complete SCC fixture output or manifest
was downloaded.
The [GROMACS 2025 MDP reference](https://manual.gromacs.org/2025.0/user-guide/mdp-options.html)
describes these foreign-lambda columns as Hamiltonian differences written
to `dhdl.xvg`; this parser checks their recorded identity and grid without
claiming to reproduce every alchemlyb parser behavior.

## Input and time-grid contract

Each independently prepared realization `r` has one common no-exchange phase and two sealed branch output trees. The analyzer takes the registered source/config/image identities, 20 ordered lambda states, complete all-state reduced-potential matrices and sample-time vectors per fixed lambda state, phase and part metadata, the HREX exchange/permutation history, output hashes and the measured cost ledger. It rejects an unsealed or incomplete ladder, missing state, nonfinite energy, wrong lambda labels, wrong atom/protocol identity, duplicate branch-boundary column or ambiguous absolute time. The analysis unit is the **realization pair**. State directories and walkers cannot increment `n`.

Let `t=0` be the end of the shared preparation. A post-branch boundary record, if present, is retained for integrity and excluded from estimation. With the proposed 1-ps energy grid, require **exactly** the retained records `t=1,...,T_a` ps for each arm `a`; `T_a` must be an even integer number of ps frozen before execution. Early uses `1,...,T_a/2`; late uses `T_a/2+1,...,T_a`. No gap, duplicate, outcome-dependent extension or adaptive boundary is permitted. A common-duration secondary comparison uses the common retained prefix and the same splitting rule, with both arms' actual costs reported.

## Block free energies and uncertainty

The primary block policy is **zero additional trimming after the fixed common preparation**. Estimate correlation within the predeclared early and late blocks without calling an adaptive equilibration selector. `src/analysis/f64a_sensitivity.py:fixed_trim_and_thin(fraction=0)` is a starting implementation to inspect; it is not automatically validated for HREX. For each block, fit the same 20-state MBAR estimator and record the endpoint folded-leg `G` in kcal/mol, the conditional MBAR standard error, per-state raw and retained counts, correlation estimates, overlap, solver notes and input hashes. Report these for every admitted pair before computing method contrasts.

PyMBAR documents that its MBAR uncertainty requires decorrelated configurations and provides timeseries methods to estimate statistical inefficiency ([MBAR documentation](https://pymbar.readthedocs.io/en/master/mbar.html), [timeseries documentation](https://github.com/choderalab/pymbar/blob/main/docs/timeseries.rst)). Its per-fit covariance is **not** the covariance between independently fitted early and late blocks. HREX can couple samples across fixed lambda states through exchanged walkers. A state-by-state thinning rule does not by itself prove that joint dependence has been removed; correlated-chain MBAR error analysis explicitly treats this concern ([Li et al., *J. Chem. Phys.*](https://arxiv.org/abs/2203.01227)). The existing [known-answer model](known_answer_model_results.md) found only 12/16 nominal-95% coverage in its harder exchange regime. Accordingly, label PyMBAR's per-block errors *conditional diagnostics* until a separate correlation/coverage calibration is accepted.

## Endpoints and covariance sensitivity

For complete pair `r` and arm `a`, compute signed movement `D[a,r]=G_late[a,r]−G_early[a,r]` and primary absolute movement `M[a,r]=|D[a,r]|`. The primary movement contrast is the mean of `M[HREX,r]−M[baseline,r]` across independent pairs. The co-primary spread quantities are the across-pair SDs of `G_late` in each arm, including all individual estimates. The provisional overall-benefit rule requires both movement and spread to meet separately registered useful-effect criteria; one improved component is reported as a component result. The spread effect threshold, interval method and final overall rule remain **unselected**.

Absolute movement is positive under a stationary zero-drift null when the difference estimate is noisy. Under an approximate normal null, `E(M)=sqrt(2/π) × SE(D)`. For the prespecified noise-adjusted squared-movement sensitivity, define `Q[a,r]=D[a,r]²−Var_hat(D[a,r])`. Negative values remain negative. A point `Q` is released only if the joint difference-variance method has passed the CPU calibration below; summing block variances assumes zero cross-block covariance and is insufficient.

If block errors `s_E` and `s_L` are calibrated but their covariance is unresolved, use the Cauchy–Schwarz bounds:

`(s_L−s_E)² ≤ Var(D) ≤ (s_L+s_E)²`, hence

`D²−(s_L+s_E)² ≤ Q ≤ D²−(s_L−s_E)²`.

Report that **interval of possible noise corrections** per realization and arm rather than a guessed point. It is a covariance sensitivity range, **not** a confidence interval. Its validity still depends on calibrated block standard errors. For an HREX-minus-baseline `Q` contrast, combine lower HREX with upper baseline and upper HREX with lower baseline, then separately quantify between-pair sampling uncertainty. If block-error calibration fails, report `M`, signed `D`, raw counts and the failure; do not label `Q` or its bounds validated.

## CPU qualification before protein use

1. Extend the parsed-file adapter to the **frozen production schema**: pin source/config/image identities, arm/phase/part metadata, all expected output paths, both branch-input seals, exchange history and the complete cost ledger. The current XVG/manifest adapter already rejects missing sampled states, wrong lambda labels, nonfinite or incomplete rows, duplicate t=0, missing/shifted times, odd block lengths and altered saved files. Its same-temperature unit conversion has a constructed PyMBAR invariance check and a passing independent alchemlyb comparison on the Stage P excerpt; the complete sealed ladder remains untested. It does not yet prove that a manifest contains every required production artifact or establish the source-chain identities; it has no SCC, GPU, submission or historical-result write path.
2. Exercise the zero-trim selector and MBAR fit on **separate constructed inputs** and verify that block selection never uses later samples to choose earlier indices. Record whether PyMBAR's conditional block errors are calibrated on held-out stationary examples with baseline-like and HREX-like cross-state dependence.
3. Evaluate a joint variance candidate on constructed stationary, drifting and long-correlation series while preserving **synchronized 20-state/walker time structure** in any resampling. Independent resampling of lambda states or separate early/late fits cannot estimate their joint covariance. Freeze resampling block length, seed, failure rule and acceptance criterion before inspecting C2 protein energies. Compare estimated `Var(D)` and point-`Q` behavior against known construction truth; if the method does not qualify, use only the covariance-bounded sensitivity when block errors qualify.
4. On complete independent pairs, check the paired movement interval and the spread interval method against synthetic repeats, including skewed absolute movements, positive/negative within-pair covariance and missing-arm attempts. Keep every failure in the attempted-pair availability denominator and cost ledger; the complete-pair contrast has its own stated denominator. Do not promote the idealized 7/18 half-width or 10/33 80%-power counts to a final sample size without this calibration and a spread target.
5. Review the analyzer, synthetic evidence, exact production input schema, output retention and locked scientific thresholds before any executable production registration. A failed uncertainty qualification is a design result; it is not repaired by examining a favorable protein outcome.

The earlier historical `f64a_blocks.py` and `f64a_sensitivity.py` remain immutable. New C2 code and outputs, when implemented, belong in fresh paths and a CPU-only Snakemake rule. No GPU job, new protein result or production endpoint follows from this candidate contract.

The first [held-out CPU uncertainty stress result](f64a_c2_uncertainty_stress_result.md)
now tests 20-state stationary harmonic data with independent and synchronized
serially correlated regimes. In the correlated held-out regime, per-state
thinning admitted 24/32 seeds and its nominal-95% conditional block
intervals covered the known endpoint in 5/24 early and 7/24 late blocks.
That diagnostic **does not qualify** the conditional block errors or a
point `Q`; actual exchange dependence, a calibrated joint variance and
production-specific exposure remain open. The independent alchemlyb
comparison passed on the supplied excerpt only; complete sealed multi-state
protein output remains unavailable locally.

The subsequent [joint stationary-bootstrap stress](f64a_c2_joint_bootstrap_stress_result.md)
kept the 20 state columns synchronized and resampled the complete early/late
series. Its frozen held-out screen passed IID data but failed synchronized
`phi=0.9` and long-correlation `phi=0.98` data. Their mean estimated joint
variances were 0.39 and 0.27 times the respective empirical across-seed
variances. This candidate does **not** qualify `Var(D)`, a point `Q`, or
covariance bounds for the protein analysis. Actual HREX walker dependence
has not been tested by either synthetic stress study.

The complete 20-state Stage P [XVG parser and numerical review](f64a_c2_stage_p_full_ladder_result.md)
now passes on the user-transferred, original-manifest-pinned subset. This
closes the full-ladder **technical parser comparison** mentioned above; it
does not create C2 production inputs or qualify the correlated-sampling
uncertainty, spread interval or scientific exposure.

The later [constructed walker-lineage stress](f64a_c2_walker_stress_result.md)
adds an explicit state-to-walker permutation and longer blocks. Its moderate
correlation case passed a frozen held-out screen, but its long-correlation
case failed. Its coordinate-independent swaps are not physical HREX; the
joint-variance and `Q` gates remain closed.

The accepted fixture's [local metadata subset review](f64a_c2_fixture_metadata_result.md)
now independently links the saved 20 common checkpoint hashes to both arm
starts and verifies the phase and exchange summaries. This closes a technical
ancestry/schema check, not the scientific uncertainty gates. A subsequent
[normal-model spread fallback](f64a_c2_paired_interval_bonferroni_result.md)
passed constructed coverage but gave intervals much wider than the simulated
effect at both 10 and 33 attempted pairs. It does not select a production
spread method or pair count for protein data.
