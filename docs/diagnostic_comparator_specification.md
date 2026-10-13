# Diagnostic comparator specification and prior-art boundary — work package A2

Prepared 2026-09-18. This is an exploratory specification for the completed
archive and future prospective registration. It defines observables; it does not
calibrate a stopping threshold, declare one diagnostic superior, or create an
independent equilibrium reference.

## Comparator definitions

For adjacent states `i` and `i+1`, let `F_i` be the one-sided Zwanzig estimate
from samples at `i`, `R_i` the reverse estimate from samples at `i+1`, and
`delta_i = F_i - R_i`. Let `G_b,r` be the MBAR endpoint estimate for time block
`b` and realization `r`.

| diagnostic | mathematical definition in this project | warning direction | required saved data / incremental analysis cost | principal limitation | primary methodological source |
| --- | --- | --- | --- | --- | --- |
| historical net hysteresis | `abs(sum_i delta_i)` | larger | adjacent all-state energies; low | signed local discrepancies cancel; not a closed thermodynamic cycle or equilibrium proof | [Klimovich, Shirts & Mobley 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/) for forward/reverse and analysis context |
| absolute local sum | `sum_i abs(delta_i)` | larger | same as net; low | schedule-length and spacing dependent; correlated terms; not endpoint-error decomposition | [Mey et al. 2020](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378) |
| maximum local discrepancy | `max_i abs(delta_i)` | larger | same as net; low | multiple correlated opportunities; sensitive to one noisy pair and schedule | [Mey et al. 2020](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378) |
| adjacent overlap | minimum/report both directed off-diagonal MBAR overlap entries | smaller | all-state energies plus MBAR; low once energies exist | overlap measures statistical bridging, not slow orthogonal modes or experimental accuracy | [Klimovich, Shirts & Mobley 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/) |
| temporal block movement | `abs(G_later,r - G_earlier,r)` for disjoint saved blocks; signed change also retained | larger | time-resolved all-state energies and two fits; moderate | blocks share preparation and may remain dynamically correlated; neither is truth | [Klimovich, Shirts & Mobley 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/) |
| between-realization dispersion | SD, range and all `G_b,r` across independently initialized ladders | larger | multiple complete ladders; high simulation cost, low analysis cost | common start/model bias can be stable; independent solvent boxes do not prove basin coverage | [Mey et al. 2020](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378) |
| conditional MBAR uncertainty | asymptotic MBAR endpoint standard error after the declared trimming/correlation treatment | larger | all-state energies plus MBAR; low | conditional on sampled equilibrium support; does not include force-field, reference-state or unvisited-mode error | [Shirts & Chodera 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2671659/) |
| adaptive selected count | number retained after the saved trim/statistical-inefficiency policy; raw suffix length reported separately | smaller | time series; low | observable-specific heuristic; selection can vary by block and does not certify equilibration | [Chodera 2016](https://pubmed.ncbi.nlm.nih.gov/26771390/) |
| fixed-pair energy movement | half-block/slope change of `u_j(x_i)-u_k(x_i)` for preselected common `(j,k)` evaluated on each sampled path `i` | larger | saved all-state energies; low | reduced-potential observable, not free energy; pair/path records are correlated and can diverge for negligible overlap | [Shirts & Chodera 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2671659/) |
| BAR/MBAR agreement | absolute difference between endpoint estimates produced from the same admitted samples | larger | same all-state energies; low | shared samples and assumptions; agreement is not independent confirmation | [Bennett 1976](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FreeEnergy/BennettJCompPhys1976.pdf), [Shirts & Chodera 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2671659/) |

The current v2 NPZs contain `u_kn_window` but no genuine `dH/dlambda` series.
Thermodynamic integration is therefore omitted. Finite differences of saved
energies are not silently relabeled as derivative data, and no quadrature is
invented.

## What has actually been compared

The archive-wide discovery audit already compares the first five historical
diagnostics against independently solvated sibling disagreement. On the folded
leg (`n=24` dependent records), Pearson associations with sibling disagreement
were +0.072 for net hysteresis, +0.104 for the absolute local sum, +0.158 for the
maximum local discrepancy, -0.120 for minimum adjacent overlap and +0.233 for
conditional MBAR error. Site-bootstrap intervals included zero. These are small,
nested discovery data—not a ranking of population performance.

The temporal analyses then supplied the harder counterexample: F64A folded r1's
initial 0.022705 kcal/mol net hysteresis accompanied a -2.076474 kcal/mol change
in a later disjoint block. The completed 15 ns analysis adds block movement,
between-repeat dispersion and saved selection behavior. The new A1 result adds
actual-lambda plots and common fixed-pair observables while preserving every
repeat/direction and explicit denominator. None has a calibrated decision rule.

BAR/MBAR agreement is retained as a future sensitivity, not counted as a second
reference. The present A stage does not need another estimator to establish that
the observed path is duration-sensitive. If implemented for the known-answer or
prospective study, its sample policy and endpoint definition must be frozen first.

## One-page prior-art boundary

Best-practices literature already recommends time-dependent convergence checks,
adjacent-state overlap, uncertainty analysis, estimator comparison and multiple
replicates. It also treats adequate overlap as necessary for reliable reweighting.
Accordingly, neither `abs(sum delta_i)` cancellation nor the instruction to plot
time dependence is a new general method.

[Wells et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8376412/) studied
SOD1 maturation with GROMACS and pmx, but used a different nonequilibrium
fast-growth design: long WT/MUT equilibrium trajectories supplied snapshots for
forward and reverse morphs, whose work distributions were analyzed. The present
project uses independently simulated equilibrium lambda windows and MBAR. Wells
does not establish external use of this project's specific ladder aggregate
`abs(sum delta_i)`. Therefore:

- the shared biological system/tool names require explicit citation and prevent
  any “first SOD1 FEP” or “novel pmx protocol” claim;
- Wells is not a direct validation of the present equilibrium-window diagnostic;
- failure of the local aggregate must not be described as failure of a standard
  field-wide stopping rule;
- the potentially publishable contribution is a reproducible SOD1 case study plus
  a **prospectively tested** diagnostic/intervention, if later stages succeed.

[Klimovich et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/)
describes overlap matrices and convergence-over-time analysis, while
[Mey et al. 2020](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378)
places overlap, cycle closure/hysteresis, estimator consistency and replicates in
a broader best-practices workflow. The current evidence sharpens why a single
cancellable scalar can reassure falsely in one archive; it does not establish a
replacement stopping rule. Work packages B–D are what could earn a transferable
claim through known-answer calibration and frozen prospective evaluation.

