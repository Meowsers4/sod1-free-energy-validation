# F64A C2 design review after the live branch fixture

Status: **CPU-only design review, 2026-10-03**. The [live branch fixture](f64a_c2_branch_fixture_result.md) passed its bounded technical gate. This review advances the proposed fresh folded-leg baseline/HREX comparison; it does not register a production protocol, select a GPU job, or change the historical 15-ns stop or failed validation gate. The agent did not access SCC.

## Technical boundary now closed

One no-exchange common run produced 20 sealed checkpoints. Two isolated continuations reached their planned steps, and HREX completed three exchange rounds with all 19 neighbor links attempted. The saved output and accounting checks passed. The checkpoint fan-out, part-numbered continuation, MPS sharing and cleanup therefore have live evidence. The fixture lasted only 2.2 ps of common dynamics followed by 4.0/3.0 ps in the branches; it gives no production equilibration length, steady rate, duration-dependent variance, or free-energy effect.

The design choice remains one shared no-exchange preparation per independent realization, then sealed checkpoint copies feeding baseline and HREX. The experimental unit is one 20-state ladder pair, not a state or walker. The primary contrast is method plus attainable retained exposure at equal **allocated GPU cost**; a same-duration prefix comparison is secondary and must state its unequal costs.

For each complete realization `r` and arm `a`, the candidate movement is
`M[a,r] = |G_late[a,r] − G_early[a,r]|`, using the disjoint retained-time
blocks in the [prior design](f64a_c2_design_decisions_2026-09-30.md).
The candidate contrast is the average of `M[HREX,r] − M[baseline,r]`
over independent realization pairs; negative values favor HREX for this
observed-stability endpoint. The co-primary reproducibility quantities
are the across-realization standard deviations of each arm's `G_late`.
Report all individual `G_early`, `G_late`, signed changes and costs.
The exact uncertainty and decision rule are not yet registered. Shared
preparation creates possible within-pair covariance: for a paired
difference its variance is `Var(M_H) + Var(M_B) − 2 Cov(M_H,M_B)`.
Plan across plausible covariance signs and analyze independent *pairs*,
not the 20 lambda states, as the replication units. The unpaired 6/17
counts in the earlier sensitivity table use `2n−2` degrees of freedom;
they cannot be relabeled as paired sample sizes with `n−1` degrees of
freedom.

The absolute movement also contains estimation noise. Under a stationary
zero-drift null and an approximately normal difference estimate with
standard error `s_Δ`, its expected value is `sqrt(2/π) × s_Δ`, not zero.
At the older *unselected* 16/7-ns equal-cost example, baseline halves
contain about 8 ns each and HREX halves about 3.5 ns each. Shorter HREX
blocks can therefore have larger estimator noise and an inflated absolute
movement even without more physical drift; improved mixing could offset
some of that, so the uncertainty must be measured, not assumed. Report
each block's correlation-corrected `SE(G_early)` and `SE(G_late)`, plus a
joint estimate of `Var(G_late − G_early)` that includes covariance between
the disjoint but potentially dependent blocks. A prespecified sensitivity
endpoint is `Q[a,r] = (G_late[a,r] − G_early[a,r])² −
estimated Var(G_late[a,r] − G_early[a,r])`, compared between arms over
complete pairs. Keep negative `Q` values rather than truncating them to
zero. This attempts to remove the squared-movement component expected
from estimator noise; its interpretation depends on calibrated variance
estimation and does not replace the primary absolute-movement endpoint.

### CPU analysis implementation boundary

The current `src/fep/analyze.py:solve_leg_mbar` returns a conditional
MBAR error for one fitted block. `src/analysis/f64a_blocks.py` records
those errors for separate early/late fits, but it does **not** estimate
the covariance of their difference. Its default window selector calls
`decorrelate_window_with_diagnostics`, which chooses an adaptive
equilibration cutoff. C2's primary policy is zero additional trimming
after fixed preparation, so that historical selector cannot simply be
reused as the primary C2 selector. A CPU-only C2 analyzer must preserve
the frozen raw early/late grids, estimate correlation within each block,
produce the two conditional block errors, and validate a joint
difference-variance method before reporting `Q`. Adding block errors in
quadrature silently assumes zero covariance and is not the registered
method. Synthetic stationary and drifting correlated-energy fixtures can
check the proposed noise adjustment and its failure behavior before any
scientific data are examined.

## Local archived-source audit

This is a read-only inspection of `/Users/bodebosell/sod1fep_archive_2026-09-11`, separate from the user-run SCC checks:

| Archived file or property | Local observation |
| --- | --- |
| `fep/F64A/inputs/wt_apo.pdb` | SHA-256 `394776d7388e79c8de7ecd46b96b16c1eaf3aaa3a7e4a4a1a2173db397bc6f29` |
| `archive/F64A_f9bded6f07b4abe5/inputs/wt_apo.pdb` | Different SHA-256 `6a097641ef8d4e75c8d8d733cdf7c0559ab341c0a589b737441bdb04b78a5dc7`; this belongs to the superseded 18-window protocol and must not be substituted when pinning the current prepared input. |
| `folded/system_r0/wt.pdb` through `system_r2/wt.pdb` | All byte-identical to the prepared WT input |
| Prepared WT contents | 2,189 ATOM records, one chain A, contiguous mature residues 1–153, no HETATM; residue 64 is PHE; Cys57 and Cys146 each have an HG thiol hydrogen |
| `system_r0/conf.gro`, `em.gro`, `hybrid.top` | SHA-256 `62153c8c5c5263ff2156fad5add20db3486d3fca1de4a6db7e7a68fbad61e9b2`, `c208023feb47b9c7c9835acfdf50299bda32d2d09fc15af8838e92eb29e3ae55`, `13ed733e316238ccff5e2710c96a6e4c5e32070fa6237c9c3d397529f951aae5`; all match the [user-supplied SCC source inventory](gromacs_protein_source_inventory_result.md) |
| Archived r0–r2 `conf.gro`, `box.gro`, `solv.gro` | Each file is byte-identical across repeats. `conf.gro` is unsolvated protein, and `solv.gro` uses the same water template. |
| Archived r0–r2 `ions.gro` and `SYSTEM_READY` | `ions.gro` hashes and example ion coordinates differ. Each has 41 NA and 36 CL; the markers record distinct `genion` seeds 331504349, 313761282 and 1063212952. This supports distinct ion placement, not a distinct protein start. |
| Archived r0–r2 `em.gro` | Distinct hashes after minimization; this alone does not establish independent protein conformations. |
| Archived r0–r2 minimized protein heavy atoms | 1,110 matched atoms; no-fit pairwise RMSD 0.228 Å (r0/r1), 0.218 Å (r0/r2), 0.214 Å (r1/r2). This directly supports describing them as one closely related protein-start family. |

The prepared WT PDB has Cys57–Cys146 SG atoms 2.038 Å apart even though both HG atoms are present. In the archived r0 minimized `em.gro` they are 3.499 Å apart. The file-level thiol evidence and the user's topology guard support the intended reduced model; the initial close sulfur geometry reinforces the need to check minimized geometry and topology for each *new* realization rather than infer chemistry from a PDB label. Local archive linkage plus the matching r0 SCC hashes strengthens the ancestry record, but the actual SCC `wt.pdb` hash and complete source-chain provenance have not been independently verified here. The configured build path selects chain A; this audit does not reconstruct every step that produced the archived coordinates.

For fresh C2 realizations, register seed rules, then verify actual coordinate/ion differences, hashes, and lambda-aware minimized starts. Identical directory names with different `r` numbers are insufficient. Multiple solvent realizations from one prepared protein still represent one protein-start family, so conclusions remain conditional on that family.

## Scientific and resource choices still open

| Choice | Current evidence and decision required before registration |
| --- | --- |
| Useful effect and precision | The user retained **0.5–1.0 kcal/mol** as a sensitivity range for reduced mean absolute early-to-late movement. No single threshold or required precision for the co-primary across-ladder spread is selected. Use the paired planning calculation below; its half-width and power targets answer different questions and neither accounts for duration-dependent estimator noise or the spread endpoint. |
| Preparation and retained exposure | Historical 2-ns fixed preparation is a candidate, not demonstrated equilibration. Choose a fixed no-exchange preparation length, minimum scientifically usable early/late block length, and finite baseline/HREX retained targets on the 1-ps all-state energy grid. A short fixture cannot validate a 3–7-ns HREX late block. |
| Rate and equal-cost conversion | The 100-ps scouts measured baseline/HREX dynamics rates of 0.552168/0.241447 ns per state per allocated GPU-hour. Their 0.43727 ratio is a sensitivity anchor, not a long-run slope. Freeze duration conversion from a technical rate model and include common preparation once, split half to each arm, plus setup, first lights, failed attempts and resumes. Report actual unequal costs without outcome-driven extensions. |
| Output and storage | The scout's 1-ps energy and 50-ps full-system coordinate cadences are candidates. The live fixture saved 524,954,094 bytes but used very dense short-run outputs and validation files; its total cannot be scaled by ns. Estimate fixed and growing bytes separately, decide checkpoint and coordinate retention, then compare the whole-study projection plus failure reserve against fresh project quota. |
| Inference and failure treatment | Freeze MBAR inputs, disjoint time records, each block's correlation-corrected SE, joint difference variance, analysis unit, uncertainty method, complete-pair rule and missing-ladder handling. Because both arms share a preparation, report per-pair outcomes and assess covariance; do not count lambda states or walkers as independent repeats. Predeclare how the two co-primary endpoints combine: both required, either one, or an ordered hierarchy. A provisional rule for an *overall* benefit claim is that both meet their registered useful-effect criteria; otherwise report component-specific findings. Preserve signed movement, absolute movement, noise-adjusted squared-movement sensitivity and final-half spread. |
| Admission | Freeze exact start source, per-realization seed map, physical/output TPR field checks, post-branch exchange interval and seed, duration and repeat count, attempt/restart caps, GPU/CPU/SU/storage limits, and outcome-independent stop rules. Obtain an independent review of the resulting registration before any separate execution selection. |

Under the **illustrative** assumptions `SD(M_B)=SD(M_H)=0.70 kcal/mol`, zero
within-pair covariance, independent normally distributed pair differences,
a two-sided 5% paired t test and no missing pairs, the pair-difference SD is
`sqrt(2) × 0.70 = 0.990 kcal/mol`. A nominal 95% half-width is
`t(0.975,n−1) × 0.990/sqrt(n)`. Exact noncentral-t power, computed with
SciPy 1.16.3, gives:

| Movement effect (kcal/mol) | Smallest pairs with half-width ≤ effect | Half-width at that count | Smallest pairs with ≥80% power |
| ---: | ---: | ---: | ---: |
| 1.0 | 7 | ±0.916 | 10 |
| 0.5 | 18 | ±0.492 | 33 |

At 6 and 17 pairs the paired half-widths are ±1.039 and ±0.509,
respectively. Half-width approximately equal to the true effect gives
only about 50–60% power here; it is not a suitable detection target.
The rough normal-approximation power counts are 8 and 31, but the exact
small-sample paired-t counts above are the relevant values under these
assumptions. Positive within-pair covariance can reduce counts; negative
covariance can increase them. Absolute movement may be skewed, its SD may
depend on duration, and the co-primary spread outcome may require more
pairs. None of these rows selects the final repeat count.

For resource scale only, take the older **unselected** 16-ns baseline
probe, the scout rate ratio (approximately 7.0 ns HREX), and the
hypothetical 2-ns common phase running at the baseline scout speed:

| Complete pairs | Branch dynamics GPU-hours | Common preparation GPU-hours | Branch XTC only | Additional common XTC | All three phases' XTC |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 347.7 | 21.7 | 7.79 GB | 0.69 GB | 8.48 GB |
| 7 | 405.7 | 25.4 | 9.09 GB | 0.81 GB | 9.89 GB |
| 10 | 579.5 | 36.2 | 12.98 GB | 1.15 GB | 14.13 GB |
| 17 | 985.2 | 61.6 | 22.07 GB | 1.96 GB | 24.03 GB |
| 18 | 1,043.2 | 65.2 | 23.37 GB | 2.07 GB | 25.44 GB |
| 33 | 1,912.5 | 119.5 | 42.84 GB | 3.80 GB | 46.64 GB |

The common XTC projection uses one shared 20-state trajectory per pair,
41 frames/state for 2 ns at the scout's 50-ps cadence and 140,499
bytes/frame. The table retains the earlier 6/17 resource probes for
comparison and adds the paired half-width and power counts. The 6/17
rows do **not** meet the paired precision or power targets above. At the
earlier 26.77-GB quota headroom, 22.07 GB
of branch XTC alone was about 82%. The newer, still **pre-fixture**
`/project` snapshot was 23.96/50 GB used, or 26.04 GB headroom: branch
XTC alone would use about 85%, and all three phases' XTC about 92%.
Current headroom after the fixture is unknown. All projections omit arm
setup, failures, resumes, non-XTC files and copies. Scout rates, proposed
durations and precision assumptions are not production forecasts; billed
SU and a whole-study storage cap remain unestablished. In the 33-pair
stress case, XTC alone would exceed even the pre-fixture quota headroom.

## Next design work

1. Complete a CPU-only, reproducible source and repeat-ancestry specification. Pin the vetted prepared WT file and verify the fresh system builder can create demonstrably distinct, chemically valid realizations without changing the paired-arm physical model.
2. Write the prospective analysis specification, including the two co-primary contrasts, the 0.5–1.0 movement sensitivity, a spread precision target, and complete-pair/failure rules. Keep both effect thresholds visible until a single decision is selected before production.
3. Construct a fixed-versus-growing cost/storage ledger with conservative long-run rate and failure scenarios. Use it to choose a finite preparation, retained durations, complete-repeat count and caps. A fresh SCC quota/SU check belongs at eventual admission; this review makes no cluster request.

The [earlier decision draft](f64a_c2_design_decisions_2026-09-30.md) and [precision/resource table](f64a_c2_precision_resource_draft.md) retain the full candidate analysis. No executable production package or further GPU attempt follows automatically from this review.

The next CPU-only artifact is an [analysis contract candidate](f64a_c2_analysis_contract_candidate.md)
with a small pure grid/noise-bound core. It explicitly leaves MBAR joint
uncertainty and HREX cross-state correlation calibration open; its synthetic
arithmetic tests are not a scientific validation.
