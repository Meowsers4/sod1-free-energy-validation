# Current conclusions and interpretation corrections — 2026-09-18

This note reconciles the historical F64A narratives, completed 15 ns evidence,
and the supplied suggestion about high-λ localization. It changes interpretation
and planning, not historical data, gate thresholds, exclusions or registrations.
The [publication research plan](publication_research_plan.md) specifies future work.
Vlasov's review remains deferred until later at the user's direction.

## 1. Current conclusions

1. **The gate failed:** r = 0.326, RMSE = 2.123 kcal/mol, seven usable variants;
   F64A was excluded by its preregistered hysteresis cap. The reference panel is
   state/construct heterogeneous. This is not matched predictive validation and
   does not isolate force-field error. Post-verdict reference sensitivity is not
   a revised gate pass.
2. **Small early net hysteresis did not certify duration stability.** F64A folded
   r1 moved from 2.505942 kcal/mol in its initial retained 3 ns to 0.429467 in the
   disjoint 6–9 ns block (−2.076474), despite initial net hysteresis 0.022705.
   Neither block is established equilibrium truth.
3. **Instability remains unresolved through 15 ns.** The adaptive mean change
   −0.049510 hides r1 −0.695174 and r2 +0.598142; fixed-policy means move too.
   Short selected suffixes and a quiet aggregate cannot certify equilibrium.
4. **Late neighbor-energy movement is larger toward high λ in this archive.**
   This is descriptive localization of an energy observable, not structural
   localization, a causal diagnosis, or proof that low-λ paths are equilibrated.
5. **No protein diagnostic or intervention has been prospectively validated here.**
   Absolute/local diagnostics have some exploratory temporal associations, but
   do not yet demonstrate general superiority or a calibrated stopping rule.
6. **No new GPU arm is selected.** The two-start comparison is a reserve design;
   neither λ localization nor current uncertainty uniquely selects the next test.

Sources: [gate and archive reanalysis](stop_rule_reanalysis.md),
[v1 extension](f64a_extension_results.md),
[v2 continuation](f64a_continuation_results.md),
[raw-energy audit](f64a_raw_energy_audit_results.md),
[reference-state audit](reference_state_audit.md).

## 2. What was independently checked in this revision

This revision performed a read-only aggregation of the existing audit JSON, not
a new raw-NPZ/MBAR reproduction or a newly registered scientific audit.

Input: `results/cpu_audits/f64a_raw_energy_v1/raw_energy_audit.json`, SHA-256
`02afc46c3b76b3b3f1bc28d94f1aa5f4cb1898b4860b2a0981ce74df9398054b`.
The audit contains 348 series records: 120 sampled-state energy records and
**228 neighbor-difference records**. Only the latter enter the table below.

For each metric, take the median across available neighbor directions, both blocks
and all three repeats **within each window**, then take the median across the ten
window medians in each half. Spearman correlates the 20 window medians with window
index. Because λ is strictly increasing, its rank correlation is identical; the
window groups do not represent equal λ widths or ten physical WT states.

| Metric | Windows 0–9 | Windows 10–19 | Spearman |
| --- | ---: | ---: | ---: |
| Absolute half drift (kT) | 0.022298491 | 0.084271662 | 0.848120 |
| Absolute slope (kT/ns) | 0.014999039 | 0.055797158 | 0.893233 |
| Absolute half drift / raw-block standard deviation | 0.055932490 | 0.132314937 | 0.747368 |

These reproduce the supplied suggestion's rounded numbers. The median of all
pooled neighbor records is a different statistic: half drift is 0.025503614 vs
0.085434192 kT. Do not label the window-median result as the pooled-record median.

The pattern is present separately, with varying strength:

| Subset | Low/high median absolute half drift (kT) | Spearman |
| --- | --- | ---: |
| r0, both blocks | 0.042762 / 0.124195 | 0.580451 |
| r1, both blocks | 0.037259 / 0.158327 | 0.660150 |
| r2, both blocks | 0.023733 / 0.096034 | 0.664662 |
| 9–12 ns, all repeats | 0.022238 / 0.072797 | 0.512782 |
| 12–15 ns, all repeats | 0.025466 / 0.142758 | 0.816541 |

There are no new p-values or independent-window significance claims. Neighbor
directions share samples, windows sample different Hamiltonians, and repeats
share a protein start. Standard-deviation normalization does not eliminate all
observable-scale, nonstationarity or dependence issues.

Read-only reproduction of the principal table from the repository root:

```bash
python - <<'PY'
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

p = Path('results/cpu_audits/f64a_raw_energy_v1/raw_energy_audit.json')
raw = p.read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    '02afc46c3b76b3b3f1bc28d94f1aa5f4cb1898b4860b2a0981ce74df9398054b'
)
records = [r for r in json.loads(raw)['series_records']
           if r['observable'] != 'sampled_state_u']
assert len(records) == 228
metrics = {
    'half_drift': lambda f: abs(f['second_half_minus_first_half_mean_kT']),
    'slope': lambda f: abs(f['linear_slope_kT_per_ns']),
    'normalized': lambda f: abs(f['second_half_minus_first_half_mean_kT']) / f['std_kT'],
}
for label, metric in metrics.items():
    medians = [np.median([metric(r['full_block']) for r in records
                         if r['window'] == w]) for w in range(20)]
    print(label, np.median(medians[:10]), np.median(medians[10:]),
          spearmanr(range(20), medians).statistic)
PY
```

## 3. Corrected physical interpretation

The active schedule places window 9 at λ = 0.5294. Thus “windows 0–9 are
essentially WT” is not an adequate control argument. A slow conformational mode
can couple strongly to the mutation end and weakly to WT. An energy observable
may be quiet while unobserved structural modes remain trapped. “Global versus
local” is not an exhaustive choice, and start sensitivity and local repacking
can coexist.

The archived F64A folded r0 topology was inspected at
`~/sod1fep_archive_2026-09-11/fep/F64A/folded/system_r0/hybrid.top`, SHA-256
`13ed733e316238ccff5e2710c96a6e4c5e32070fa6237c9c3d397529f951aae5`.
In the F2A residue, CG/CD1/CD2/CE1/CE2/CZ become dummy atom types in state B;
three alanine hydrogen sites acquire real parameters. **Six ring heavy atoms
are removed; CB remains.** This corrects the old “seven heavy atoms/entire benzyl
group” wording. It also corrects the suggestion's appearing-heavy-atom analogy
to A4V. This one topology check establishes the mapping in that archived file;
it is not a new inventory certification of all checkpoints.

Cavity hydration and repacking are hypotheses. There are no retained structural
trajectories in the documented production output policy to demonstrate those
processes. Prepared/final coordinates and checkpoints may exist; saying “no
coordinates exist” or asserting that no trajectory ever existed anywhere exceeds
the inventory evidence. A hybrid checkpoint is not automatically a WT alternate.

For independent-window MD, inserting states leaves the Hamiltonian/dynamics of
unchanged states intact (assuming all other settings match). It can improve
statistical bridging; it does not itself enable communication between trajectories.
Smaller adjacent λ steps can reduce raw neighbor-energy differences mechanically.
Compare fixed-pair observables and endpoint-estimate stability before claiming
improvement. A soft-core change or exchange method is a different intervention.

Sources: [Mey et al.](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378)
and [GROMACS exchange documentation](https://manual.gromacs.org/2025.3/reference-manual/algorithms/replica-exchange.html).

## 4. Claims being replaced

| Earlier claim | Current interpretation |
| --- | --- |
| “High-λ drift proves local reorganization, not start trapping.” | Drift is λ-associated in selected observables; structural cause and start sensitivity remain unresolved. |
| “Densifying high λ removes drift, so the mechanism is found.” | A density intervention tests estimation/reproducibility; use common observables and independent repeats. It cannot by itself identify a structural mechanism. |
| “The 18→20 change proved endpoint refinement halved hysteresis.” | Schedule and system-preparation policy both changed; the observed aggregate change cannot be attributed to one factor. |
| “Each independent box settled in a different basin.” | Different estimates were observed; independently solvated boxes are not demonstrated independent protein basins. |
| “Closure measures within-basin equilibration.” | The historical metric is an absolute net of signed local discrepancies; cancellation is possible even without equilibration. It is not a closed thermodynamic cycle. |
| “Range exceeding SEM proves underestimated uncertainty by 3–10×.” | Range and uncertainty of the mean are different quantities. Existing uncertainty is conditional and excludes unsampled modes; its calibration has not been established by their ratio. |
| “The unfolded reference is perfect and cannot contribute.” | Its observed diagnostics were better in that run; neither equilibrium sampling nor adequacy as an unfolded-state model follows. |
| “MBAR solved, so the estimator/input mechanism is settled.” | Numerical solution is not physical equilibration or proof that analysis assumptions hold. |
| “6 ns will almost certainly fail; two SEM gives detectable effect/power.” | Existing drift motivates caution, not an outcome probability for fresh runs. Formal precision/power planning needs an effect, variance assumptions and small-sample treatment. |
| “The λ audit decisively chooses density versus starts.” | The audit informs hypotheses; it cannot uniquely select a causal experiment. |
| “Near-zero correlation shows no diagnostic information.” | Small, nested samples and dependent disagreement summaries limit inference; no population-level absence or superiority claim. |

### Frozen-source errata

`config/pipeline.yaml` contains historical explanatory comments claiming that
overlap identifies a cavity mechanism, denser windows uniquely prevent bias,
independent solvation samples a slow protein mode, and uncertainty was understated
approximately tenfold. The `lambda_ladder()` docstring in `src/fep/pmx_engine.py`
also calls other windows “already converged” from overlap and describes deletion
of the benzyl group. Those interpretations are superseded by this note.

The source/config bytes are retained because they are historical hashed inputs;
no simulation parameter or evidence hash is changed to repair prose. Current
operating notes point here. Future isolated source versions should use the
corrected wording, with new provenance, rather than rewriting historical inputs.

## 5. Current completion boundary

Since the initial reconciliation, the full [λ/comparator analysis](f64a_lambda_comparator_results.md)
and bounded [known-answer calibration](known_answer_model_results.md) have completed.
The first [exchange qualification](gromacs_exchange_feasibility_design.md) records
an incompatible standing build and unresolved coupled placement. The protein
intervention, prospective panel, structural evidence and new public release
remain unfinished; the toy model does not establish protein performance.

The revised [publication plan](publication_research_plan.md) makes the controlled
protein sampling comparison primary, diagnostics secondary and mechanism optional.
Cross-protein work is conditional on its scientific purpose; additional model
calibration is not a prerequisite. Sample size/duration are justified through
precision, coverage and resources, without calendar or student-capacity assumptions.
Actual billed v2 SU remains unreviewed without SCC records. Mentor review is later.

## 6. Verification of the initial reconciliation revision

The documented read-only reproduction produced the principal table above. Local
Markdown file links and code-fence balance were checked. The draft two-start
YAML's parsed values are unchanged; only explanatory comments were added.
Twenty protected file hashes (including historical config, simulation module,
pilot-package files, raw audit and v2 reports, and forensic manifest) match their
pre-edit values. All seven raw-audit dependency hashes still match the saved
audit. Read-only release verification passed for **1,217 files**. No simulation,
workflow or analysis executable was changed; numerical test suites and new study
stages were not run as part of this documentation-only revision.
