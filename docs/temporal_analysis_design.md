# Next step: time-resolved diagnostic analysis

Status: specification fixed before execution on 2026-09-14; analysis completed the same day.
Results: [`temporal_analysis_results.md`](temporal_analysis_results.md). Terminal results and the F64A cancellation example were
already known, so this is **exploratory retrospective analysis**, not prospective validation
or a newly preregistered prediction test. The completed release remains a frozen snapshot.

## Question

Do early energy-space diagnostics flag estimates that later change or disagree with a
separately simulated repeat? A stable time series cannot rule out an unvisited protein
conformation, and a later estimate is not ground truth.

## Proposed design to record in config before execution

- Primary cohort: the seven variants with retained attempt-1 data, including F64A. Analyze
  folded and unfolded legs separately; report folding differences as a secondary summary.
- Secondary cohort: A4V's retained 9 ns folded / 3 ns unfolded attempt-2 data, kept separate.
  Its original 3 ns raw history is lost.
- Cumulative checkpoints: first 25%, 50%, 75%, and 100% of each window's retained production
  energy columns, selected before decorrelation. These fractions are the proposed new settings,
  not existing pipeline configuration. Use deterministic integer boundaries with every column
  assigned once in a block split.
- Disjoint comparison block: final 25% of retained production, independently reanalyzed.
  It does not share columns with any prefix ending at or before 75%. Consecutive blocks still
  may be correlated; describe the comparison as temporal sensitivity, not independent truth.
- Recompute equilibration detection and correlation thinning using only the data in each
  prefix/block. Do not use a full-trajectory equilibration cutoff or statistical inefficiency
  to choose samples for an early estimate.
- Preserve the existing 20 lambda states. Validate sample ordering and the archived output
  cadence before mapping fractions onto nanoseconds; current config contains later per-leg
  timing settings and is not sufficient to reconstruct historical elapsed times by itself.
- Compare the same five diagnostics already audited: net hysteresis, sum and maximum of
  absolute adjacent discrepancies, minimum adjacent overlap, and within-leg MBAR error.
- Continuous primary outcome: absolute difference between a prefix free-energy estimate and
  the later disjoint-block estimate for the same replicate. It measures subsequent movement.
- Separate repeat outcome: absolute difference from the mean of the other two repeats at
  their full retained duration. This is sibling disagreement, not experimental accuracy.
  It excludes the evaluated repeat from its reference but reuses siblings across outcomes.
- No fitted diagnostic thresholds, no “converged” labels inferred from a plateau, and no
  new validation gate. Record solver failures and insufficient-sample cases instead of
  silently dropping them or replacing them with zeros.

## Reporting and uncertainty

Plot all repeat trajectories by variant/leg with conditional MBAR uncertainties, show the
late-block estimates separately, and expose signed local discrepancies over time. Summarize
associations separately at each checkpoint. Reuse the existing configured whole-variant/site
bootstrap settings and leave-group-out sensitivity; keep all repeated time points/siblings
within their original group. Do not count checkpoints as extra independent mutations.
With only five primary-cohort sites, all intervals remain approximate. Do not infer a new
stopping rule from these data.

## Implementation work

1. Add the fractions, comparison block, output location and endpoint definitions under a
   new temporal subsection of `config/pipeline.yaml:forensic_review` before running analyses.
2. Extend `src/analysis/diagnostic_audit.py` with prefix/block selection on raw energy arrays;
   reuse the current decorrelation and MBAR routines on each selected subset.
3. Add a separate Snakemake rule and separate outputs; preserve `docs/review/` and the original
   gate/release. Do not run the existing audit command expecting temporal outputs.
4. Test the critical scientific contracts: no future columns passed into early analysis,
   no overlap at block boundaries, correct A4V cohort separation, failed-block accounting,
   and full-duration estimates reconciling with the existing audit.
5. Run the CPU analysis and inspect the plots before choosing a new GPU experiment.

## How the result guides GPU use

- Visible drift or persistent repeat disagreement: a targeted sampling experiment has an
  observed phenomenon to investigate. Check whether distinct protein starting conformations
  change the estimates; do not assume more solvent-box repeats explore new conformations.
- Stable prefixes with repeat disagreement: investigate dependence on protein starting
  conformations. Stability within each repeat does not establish agreement between basins.
- Stable prefixes with repeat agreement: the energy archive cannot distinguish shared trapping
  from model/reference bias. Prioritize benchmark compatibility and external-system evidence.

These are hypotheses for choosing the next test, not causal conclusions. GPU counts, model,
allocation and walltime limits will determine the concrete pilot. Any new production arm
needs an explicit design and preregistration under `CLAUDE.md` before submission.

## Parallel human task

Ask a computational biophysicist to inspect the existing release and especially (a) the
thermodynamic observable and experimental construct/state mismatch, (b) the signed-ladder
hysteresis definition, and (c) the conditional redox uncertainty. A useful outcome is a short
list of claims they consider defensible, incorrect or still untested. Human review can
proceed alongside CPU work and is not a reason to leave that work idle.

Background: [Mey et al., Best Practices for Alchemical Free Energy Calculations](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378)
discusses convergence, uncertainty and experimental comparability. The checkpoint choices
and outcome definitions above are this project's proposed exploratory design.
