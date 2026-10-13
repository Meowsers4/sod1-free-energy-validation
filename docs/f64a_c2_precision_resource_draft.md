# C2 F64A precision and resource table — design draft

**Subsequent result, 2026-10-03:** The [live branch fixture](f64a_c2_branch_fixture_result.md)
passed its technical/accounting checks. Its short phases and validation-heavy
524,954,094-byte attempt do not establish long-run rates or a production
storage slope. The [post-fixture design review](f64a_c2_post_fixture_production_design.md)
records the remaining precision and admission choices; the sensitivity
calculations below are still unselected scenarios.

Prepared 2026-09-29 for the [fresh two-arm C2 design](f64a_c2_arm_definition_draft.md)
and [publication plan §7](publication_research_plan.md#7-precision-and-resources--decisions-before-production).
This is a **sensitivity calculation**, not a selected duration, repeat count,
budget, preregistration or authorization for a cluster job. The primary study
compares independent windows with neighbor HREX for the F64A folded leg at
equal total allocated GPU cost, including GPU preparation and failed attempts.
The historical 15-ns stop remains intact.

## Inputs that exist and what they measure

| Input | Observed information | Limit for C2 planning |
| --- | --- | --- |
| [F64A 9–15 ns continuation report](f64a_extension_review/f64a_continuation_v2.json) | Three historical independent-window repeats, with per-repeat disjoint 9–12 and 12–15 ns folded-leg estimates under three selection policies | Same old trajectories and one prior method; small sample, different time split and no HREX variance |
| [Continuation result](f64a_continuation_results.md) | The 15-ns endpoint remained unstable and selection-sensitive | A longer C2 duration cannot be assumed to reduce variance by a known law |
| [Historical extension estimate](f64a_continuation_9_to_15_design.md) | About 36 GPU-hours for 60 separate-window paths extended by 6 ns, or 10 aggregate state-ns per GPU-hour | Estimated older one-window execution, not measured throughput for one 20-rank coupled r6/MPS ladder |
| [Stage P accounting](gromacs_protein_runtime_result.md) | One 20-state ladder advanced 0.004 ns/state with two launches in 146 s on one L40S: 0.0986 state-ns per allocated GPU-hour, **including fixed technical overhead** | A four-ps technical attempt cannot estimate steady production speed; this is not a lower bound on future speed |
| [Accepted paired 100-ps technical scout](f64a_c2_scout_hrex_result.md) | Baseline: 0.1925 allocated GPU-hours, 519.48 ps/state per allocated GPU-hour setup-inclusive; HREX: 0.427778 allocated GPU-hours, 233.77 ps/state per allocated GPU-hour setup-inclusive. The HREX rate is 45.0% of baseline for these jobs. | Exact 100-ps one-L40S/20-rank/output-cadence measurement; neither a long-run rate forecast nor a convergence or FEP result. GPU preparation, failed-attempt allowance and billed SU remain unmeasured. |
| [Historical v2 accounting closeout](f64a_accounting_closeout.md) | Actual billed SU and applicable tariff have not been reviewed locally | No SU price or currently spendable C2 budget can be inferred |

The frozen continuation JSON has SHA-256
`ddb20589d809682f7ef72a4fddc55c6998c48ca3b7a06b1b466682291a24ab71`.
The historical SDs below are ordinary sample SDs (`ddof=1`) across its three
reported replicate values, rounded to 0.001 kcal/mol.

The accepted scout also measured dynamics-only rates of **552.17** baseline
and **241.45** HREX ps/state per GPU-hour, and observed persistent-output
maxima of 111,144,766 and 130,290,261 bytes. These are peak values for
complete technical attempt trees, not a scalable per-ns storage slope.
The jobs jointly used 0.620278 allocated GPU-hours and 9.924444 requested
CPU-slot-hours. The observed HREX/baseline setup-inclusive rate ratio is
0.45, but the equal-cost production durations must account separately for
fresh-start preparation, failed attempts, longer-run overhead and any
different chosen output or restart settings. Do not substitute this ratio
directly into a selected production duration.

The report's `primary_new_blocks` absolute movement values and late-block
free-energy estimates give the following **sample** SDs across only three
historical repeats. They are inputs to sensitivity scenarios, not estimates
for the fresh C2 population:

| Selection policy | SD of `|ΔG_12–15 − ΔG_9–12|` (kcal/mol) | SD of `ΔG_12–15` (kcal/mol) |
| --- | ---: | ---: |
| Untrimmed | 0.255 | 0.487 |
| Fixed 25% | 0.354 | 0.482 |
| Adaptive | 0.347 | 1.004 |

These are 3-ns blocks late in an existing 15-ns run, not C2's future fixed
early/late halves. The three selection policies reuse the same trajectories;
they are not independent variance estimates. C2's primary analysis will use
the plan's zero-additional-trimming policy; the others only stress-test a
variance assumption. No HREX variance or cross-arm correlation is observed.

## Precision scenarios for the movement endpoint

Let `M_r = |ΔG_late,r − ΔG_early,r|` for a complete ladder. For this **idealized**
table, assume `n` independent ladders per arm, equal movement SD `σ_M` in each
arm, no missing runs, approximately normal arm means and an unpaired comparison.
The nominal two-sided 95% half-width for the difference of arm means is

`h = t(0.975, 2n−2) × σ_M × sqrt(2/n)`.

The [NIST two-sample mean formula](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/diffmean.htm)
supplies the statistical reference; numbers below use SciPy 1.16.3 `t.ppf`.
Absolute movements can be skewed, shared initial inputs may correlate arms,
and failed ladders may be informative. This table is **not** a calibrated
confidence interval or power calculation for C2.

| Complete ladders per arm `n` | `σ_M=0.35` | `σ_M=0.70` | `σ_M=1.00` |
| ---: | ---: | ---: | ---: |
| 3 | ±0.79 | ±1.59 | ±2.27 |
| 5 | ±0.51 | ±1.02 | ±1.46 |
| 8 | ±0.38 | ±0.75 | ±1.07 |

Units are kcal/mol of difference in mean absolute movement. `0.35` is near
the old three-repeat movement SD under fixed/adaptive policies; `0.70` and
`1.00` are explicit stress scenarios, **not measured new-arm variances**. At
`n=5`, a half-width near 1 kcal/mol in the middle scenario would leave a
0.5-kcal/mol useful improvement poorly resolved. No single useful-effect
target is selected here. The user chose **0.5–1.0 kcal/mol as a sensitivity range**
for the smallest scientifically useful reduction, not a single registered
effect threshold. Under the same idealized unpaired model, the minimum
complete ladders per arm for a nominal half-width no greater than each
value are:

| Assumed `σ_M` (kcal/mol) | `h≤1.0` | `h≤0.5` |
| ---: | ---: | ---: |
| 0.35 | 3 | 6 |
| 0.70 | 6 | 17 |
| 1.00 | 9 | 32 |

**Paired-design correction (2026-10-03):** This table uses an unpaired
`2n−2`-degree-of-freedom formula. It must not be read as 6 or 17
matched-pair counts. Under zero within-pair covariance and the same
0.70-kcal/mol arm SD, a paired `n−1`-degree-of-freedom calculation needs
**7** pairs for a ±1.0 half-width and **18** for ±0.5; exact two-sided
paired-t 80%-power planning needs **10** and **33** pairs. See the
[post-fixture review](f64a_c2_post_fixture_production_design.md) for
assumptions, shorter-block estimator noise and resource consequences.

A half-width equal to an observed effect would only put zero at the
interval boundary; this is **not** a power calculation or assurance that
the benefit can be detected. A final
decision must also address bias, missingness and the co-primary spread
endpoint; simply reaching a nominal half-width is insufficient.

## Precision of the dispersion endpoint

The second planned endpoint is the across-ladder SD of `ΔG_late` within each
arm. Even under an ideal normal model, a two-sided 95% chi-square interval
for a **single arm's** true SD, expressed as a multiple of its observed `s`,
is broad:

| Complete ladders in one arm | Lower × `s` | Upper × `s` |
| ---: | ---: | ---: |
| 3 | 0.52 | 6.29 |
| 5 | 0.60 | 2.87 |
| 8 | 0.66 | 2.04 |

Formula: `s sqrt((n−1)/χ²(0.975,n−1))` to
`s sqrt((n−1)/χ²(0.025,n−1))`, from the
[NIST standard-deviation interval](https://www.itl.nist.gov/div898/handbook/prc/section2/prc231.htm).
These are **not intervals for the difference of two SDs**, and their normality
assumption may fail. For example, if `n=5` and observed `s=0.5 kcal/mol`,
even this one-arm model gives roughly `0.30–1.44 kcal/mol` for the underlying
SD. Five repeats are a starting design, not automatic precision for a spread
contrast. The old late-block SDs near 0.48 and 1.00 show why the scenario
must include large dispersion. No normal-model SD interval will be presented
as a final scientific conclusion without checking its assumptions.

## Equal-cost algebra

Define, for one 20-state ladder on the candidate one-L40S layout:

- `R_B` and `R_H`: **retained ns per state per allocated GPU-hour** during
  baseline and HREX dynamics, measured separately with the proposed output
  and restart settings. The two rates need not match.
- `P_common`: allocated GPU-hours to prepare common inputs for one new
  realization, counted once across the pair and split equally in an arm
  comparison. The user has chosen one shared **no-exchange** preparation
  before the baseline/HREX checkpoint branch as the C2 design contrast;
  its duration and actual GPU hours remain unselected. CPU preparation
  hours are recorded separately.
- `P_B` and `P_H`: other arm-specific allocated GPU-hours before retained
  sampling, including any GPU equilibration. These must include their actual
  walltime and allocated GPU count.
- `F_B` and `F_H`: the sum of allocated GPU-hours from first lights, failed
  attempts, incremental resume work and scheduler time **not already included**
  in `P` or the measured `R` rates, assigned to each arm. They are recorded
  even if no usable estimate results; do not count the same walltime twice.

For `n` complete planned realizations per arm and retained durations `T_B`,
`T_H` ns/state, the provisional cost equations are

`C_B = n(P_common/2 + P_B + T_B/R_B) + F_B`, and

`C_H = n(P_common/2 + P_H + T_H/R_H) + F_H`.

The **planned** equality is `C_B ≈ C_H` under frozen target steps, measured
rates and declared failure allowances before scientific production. Replace
allowances with actual attempt costs in the final ledger. Actual deviations
are reported;
do not extend a scientifically disappointing arm to force equality after
examining outcomes. If arm-specific preparation and failure allowances are
equal, `T_H = T_B × R_H/R_B`. For illustration, a measured ratio of 0.8 would
give HREX 80% of the baseline retained ns/state at the same allocated cost.
That ratio is a what-if value, **not** a measurement. Equal-time-per-state
comparisons, where both have data, remain secondary. Using the same steps in
both arms would generally fail the equal-cost primary design when rates differ.

### Post-scout equal-cost sensitivity, not a production forecast

The accepted 100-ps scouts provide dynamics-only rates of `R_B=0.552168`
and `R_H=0.241447` ns/state per allocated GPU-hour. Their ratio is
`R_H/R_B=0.43727`. Holding that ratio and assuming equal arm-specific
preparation/failure costs, a purely mechanical equal-cost conversion would
give `T_H=0.43727 T_B`. The setup-inclusive short-job ratio is 0.45;
using it as a long-run dynamics rate would count the scout's fixed setup
time repeatedly, so this table uses the dynamics-only rates and leaves
`P` and `F` explicit above.

| Existing design probe | Complete ladders per arm | Baseline `T_B` (ns/state) | HREX `T_H` if scout ratio persisted (ns/state) | Nominal movement half-width if `σ_M=0.70` (kcal/mol) | Pair dynamics GPUh at 2× scout speeds | Pair dynamics GPUh at scout speeds | Pair dynamics GPUh at ½ scout speeds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 3 | 8 | 3.50 | ±1.59 | 43.5 | 86.9 | 173.9 |
| B | 5 | 16 | 7.00 | ±1.02 | 144.9 | 289.8 | 579.5 |
| C | 8 | 32 | 13.99 | ±0.75 | 463.6 | 927.3 | 1,854.5 |

Each pair-cost cell is `2nT_B/R_B` under the indicated common rate
multiplier. Its two arms each receive half of that dynamics allocation.
The HREX durations assume the **ratio** stays 0.43727 even when both rates
scale; if the ratio changes, those durations must change. These figures
exclude the selected shared new-realization preparation, retries, resume
overhead, first lights, CPU setup/analysis, storage and SU. A single
100-ps point cannot establish a long-run slope, a speed uncertainty
distribution or a defensible production budget. The ½×/2× multipliers are
stress cases, not measured uncertainty bounds. The precision column is the
earlier hypothetical `σ_M=0.70` t-interval at each repeat count; it does
not incorporate duration-dependent variance, unequal arm variances,
within-pair correlation or failures, and does not certify that a 3.50- or
7.00-ns HREX trajectory has the same precision as the longer baseline.

The unequal durations make the primary endpoint an **equal-cost
method-and-exposure comparison**. If each arm is split into its own early
and late fractions, the underlying physical-time windows differ. Freeze
those windows in both cost fraction and ns/state before production, and
report the actual durations. A common-duration analysis of the overlapping
portion can be a secondary method comparison at equal simulation time,
with its unequal cost stated. Do not interpret a change in temporal
movement from different time windows as an isolated exchange effect.

The user chose one **shared no-exchange preparation** per realization
before the baseline/HREX checkpoint branch; its length is not selected.
If a candidate 2-ns common preparation ran at the baseline scout
dynamics-only rate, it would cost `2/0.552168 = 3.62` GPU-hours per
realization, charged **once** to the pair. It would add approximately
10.9/18.1/29.0 GPU-hours to rows A/B/C, yielding central pair totals
of 97.8/307.9/956.2 GPU-hours before all other overhead. The 2-ns
common-preparation rate and length are unmeasured/unselected, so these
are arithmetic stress cases, not budget forecasts. The
[branch design](f64a_c2_design_decisions_2026-09-30.md) specifies the
checkpoint and analysis checks needed before production registration.

## Duration, repeat and rate sensitivity grid

The three rows below are **design probes**, chosen to span factors of two
in duration and increasing repeat count. They are not recommended or admitted
C2 runs. `T_B` is the baseline's retained ns/state. The numbers are combined
two-arm **dynamics-only GPU-hours** under equal cost and identical hypothetical
rates `R_B=R_H=R`, calculated as `2nT_B/R`. They omit all `P`, `F`, storage
and SU costs. HREX duration must be adjusted using measured `R_H/R_B`.

| Probe | Complete ladders per arm | Baseline retained `T_B` (ns/state) | GPUh if `R=0.10` | GPUh if `R=0.25` | GPUh if `R=0.50` |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 3 | 8 | 480 | 192 | 96 |
| B | 5 | 16 | 1,600 | 640 | 320 |
| C | 8 | 32 | 5,120 | 2,048 | 1,024 |

`R=0.10` resembles Stage P's setup-inclusive four-ps rate but is not a
steady-state benchmark. `R=0.50` is the historical 10 aggregate
state-ns/GPU-hour **estimate** divided by 20 states, from a different
one-window architecture; it is not an r6 coupled-ladder benchmark. `0.25`
is an interpolation for sensitivity only. No rate is an entitlement or
forecast. If one full-duration attempt in **each** arm were lost, the
dynamics-only additions would be `2T_B/R` under equal-rate assumptions
(20% of a five-repeat row). This is a failure-cost scenario, not permission
for a retry. At 16 requested CPU slots, an allocation of `G` GPU-hours on
this one-GPU layout corresponds to `16G` requested CPU-slot-hours; billed SU
remains unverified and must be recorded separately.

## Storage and admission gaps

The paired scout observed peak persistent attempt-tree sizes of
111,144,766 bytes (baseline) and 130,290,261 bytes (HREX) during its
100-ps jobs. The user then read the retained `storage-by-extension.json`
files and measured the current full attempt trees at **111,244,910** and
**130,525,018** bytes, respectively, or **241,769,928** bytes combined.
The by-extension snapshots preceded some final accounting metadata, so
their listed categories do not sum exactly to the later current-tree sizes.

| Output category in 100-ps by-extension snapshot | Baseline bytes | HREX bytes | Interpretation |
| --- | ---: | ---: | --- |
| `.xtc` (20 files, three frames/state) | 8,430,480 | 8,429,380 | Full-system compressed-coordinate sample |
| `.xvg` (40 files) | 628,601 | 628,687 | DHDL plus extracted energy text; 101 energy records/state |
| `.edr` (20 files) | 530,480 | 530,480 | Binary energy files |
| `.tpr` (20 files) | 29,061,760 | 29,061,760 | Input copies present once per arm |
| `.gro` (20 files) | 53,012,440 | 53,012,440 | Final full-system coordinates |
| `.cpt` | 18,465,760 (20 files) | 36,931,520 (40 files) | HREX retained 20 additional checkpoint files |

The XTC total across both arms is 16,859,860 bytes for **120 stored
state-frames**, about **140,499 bytes per full-system frame** in this
particular pair. If that sample size stayed constant at the scout's
50-ps cadence, the equal-cost sensitivity rows above would imply the
following **XTC-only** amounts after rounding the illustrative HREX
durations to 3.5, 7 and 14 ns (whole 50-ps frames):

| Probe | Baseline/HREX frames per state | Approximate XTC across both arms and all repeats |
| --- | ---: | ---: |
| A: 3 pairs, 8/3.5 ns | 161 / 71 | 1.96 GB |
| B: 5 pairs, 16/7 ns | 321 / 141 | 6.49 GB |
| C: 8 pairs, 32/14 ns | 641 / 281 | 20.73 GB |

This is `pairs × 20 states × (baseline frames + HREX frames) × 140,499
bytes/frame`, using decimal GB. It is an illustrative trajectory scale,
not a storage budget: compression can change with conformation, and it
excludes TPRs, final GROs, checkpoints, energy matrices, logs, provenance,
failed attempts, replicas, backup copies and analysis files. Row C's
XTC-only figure is already close to the earlier 26.77-GB `/project`
quota headroom; it cannot be admitted from that snapshot. Multiplying
the whole 100-ps trees by duration would also multiply fixed files
incorrectly. A complete storage projection needs separate fixed bytes,
energy/trajectory growth, checkpoint and validation retention, plus a
fresh quota check. One duration per arm cannot identify a reliable
whole-tree growth slope. Preserve the original Stage P and scout evidence.

The user supplied a newer `pquota rise-batteries` snapshot from `scc-i01`
after Stage P: **46.32/50 GB** used on `/projectnb/rise-batteries`, leaving
**3.68 decimal GB**, and **23.23/50 GB** used on
`/project/rise-batteries`, leaving **26.77 decimal GB**. File-count quotas
have ample headroom at 466,518/1,638,400 and 203,413/1,638,400,
respectively. `df -h` reported 8.7 GiB available on the `/projectnb`
filesystem; the **project-specific 3.68-GB quota** is the tighter limit
for new data there. Quota and filesystem free space can change.

**Later snapshot:** The user-run 2026-10-02 branch-fixture preflight
reported `/project/rise-batteries` at **23.96/50 GB** used, leaving
**26.04 decimal GB** before the fixture ran. Current post-fixture
headroom has not been measured here.

The accepted Stage P runtime package totals approximately **541 MiB** by
`du -sh`: separate measurements give **480 MiB** for `attempt/` and
**61 MiB** for `prepared/` (rounded disk-use display values). Stage P's
614 hashed outputs must be preserved. Its four-ps output footprint cannot be
scaled linearly to C2 durations: fixed package/checkpoint costs and the
chosen production trajectory/energy cadence can change the rate of growth.

A subsequent read-only scan of `attempt/` found **615 files totaling
501,704,465 logical bytes** (about 478.5 MiB). The 614-file hash inventory
is consistent with the scan: the runtime writes `output-hashes.json` *after*
inventorying the other files. The output-type totals are:

| Extension | Files | Logical bytes | Share of attempt bytes |
| --- | ---: | ---: | ---: |
| `.dump` | 40 | 231,039,436 | 46.1% |
| `.gro` | 40 | 106,024,880 | 21.1% |
| `.tpr` | 40 | 58,123,520 | 11.6% |
| `.cpt` | 60 | 55,397,280 | 11.0% |
| `.xtc` | 40 | 47,842,536 | 9.5% |
| All other extensions | 395 | 3,276,813 | 0.7% |

The 40 large `.dump` files are `gmx dump -cp` checkpoint text produced for
Stage P validation; `src/analysis/gromacs_gpu_smoke_runtime.py` generates
them from the binary checkpoints. The restart test also copied complete
first-phase state directories into `before-restart/`, explaining repeated
TPR, coordinate and trajectory files. A future C2 retention policy may avoid
routine duplicate text dumps after validating compact checkpoint metadata,
but must still preserve the binary checkpoints, raw analysis energies,
coordinates, exchange history and sufficient restart audit evidence. That
policy must be specified before execution. **No Stage P files should be
removed or rewritten.** The observed 47.8-MB trajectory total reflects only
four ps and Stage P's output cadence; it provides no reliable per-ns forecast.

Stage P wrote compressed coordinates every 200 steps, or **0.4 ps**, and
archived the first-phase copies of all state directories. Keeping that dense
coordinate cadence across a hypothetical 16-ns ladder would make even the
trajectory files alone an **order-of-100-GB** item, before repeats, energies,
checkpoints or failed attempts. This is only a scale warning based on the
four-ps technical output, not a production storage prediction: snapshot
compression and the new retention plan may differ. In particular, moving C2
outputs to `/project` does not itself make the duration grid affordable.
The [output/timing-scout draft](f64a_c2_output_timing_scout_draft.md)
proposes full-system coordinates every 50 ps and all-state energies every
1 ps as a candidate for bounded measurement. Neither cadence is selected
for production; the scout must measure bytes per retained ns, and structural
resolution must be assessed before registration.

BU SCC says `/project` and `/projectnb` have identical performance
characteristics, but `/project` is backed up nightly and is intended for
files that cannot readily be regenerated; `/projectnb` is suitable for
temporary or reproducible data. [SCC Project Disk guidance](https://www.bu.edu/tech/support/research/computing-resources/file-storage/proj-diskspace/).
The user confirmed `/project/rise-batteries` is writable on `scc-i01`, and
`df -h` shows about **32 GiB** free on its filesystem. Its **26.77-decimal-GB
project quota headroom** is the tighter planning limit. This provides a
candidate location for curated C2 inputs, evidence and irreplaceable outputs,
subject to a concrete whole-study storage budget and a later compute-node
access check.
Use job-local scratch only as temporary workspace and copy required output
out before it expires; SCC describes scratch as unbacked and subject to
automatic removal after 30 days.
[SCC storage guidance](https://www.bu.edu/tech/support/research/computing-resources/file-storage/).
Do not delete or relocate the accepted Stage P package or historical evidence
to create capacity without a verified inventory, backup and separate plan.

Production coordinate cadence and its measured byte rate remain unknown.
Storage must be estimated from the chosen TPR, energy, checkpoint and
trajectory cadence and both arms' complete output inventory, including
first-phase archives and any retained failure evidence. Mechanism-capable coordinates
require protein, solvent, topology, box and state/walker history together.
No cleanup of immutable earlier evidence is implied by this table.

**Before choosing one row or submitting any C2 production job:** set a
scientifically useful movement and dispersion effect/precision target;
specify the final early/late interval and normal/non-normal uncertainty
method; use the accepted short-scout `R_B`/`R_H` measurements only as
sensitivity anchors; estimate GPU preparation, long-run rate uncertainty
and output growth; then complete
the per-arm GPU-hour, CPU-slot-hour, SU, storage, attempt and stop caps.
Choose the final duration and repeat count jointly, with the expected
precision and technical-failure allowance shown. The four-ps Stage P run
cannot fill those fields. Any scouting GPU execution requires its own
separate admission; this draft itself makes no cluster request.
This is an F64A **development** calculation only. The later prospective
SOD1 panel needs a separate precision analysis across mutation sites; adding
F64A ladders does not increase the number of independent sites.
