# Known-answer CPU calibration — work package B

Completed 2026-09-18. This constructed-model study is CPU-only. It does not
identify a protein mechanism, select a SOD1 intervention, authorize GPU work, or
establish a transferable convergence threshold.

## Frozen model and reference

The registered v2 specification is
[`known_answer_model_v2.yaml`](known_answer_model_v2.yaml). It defines a
lambda-coupled coordinate `x` and a double-well slow coordinate `y`. The easy
regime has a low barrier throughout. The metastable regime has high endpoint
barriers and a lower barrier at intermediate lambda, making neighboring
Hamiltonian exchange a meaningful constructed intervention.

Both methods receive exactly 60,000 potential evaluations per experiment.
Exchange cross-evaluations count against that budget. All runs start from the
same declared `y=-1` distribution. Four development seeds and sixteen held-out
seeds are disjoint. Fixed 20% burn-in is followed by per-state thinning using
the larger statistical inefficiency estimated from `y` and sampled-state energy;
each full/early/late block fits that treatment independently.

Primary tensor Gauss-Legendre quadrature and an independent nested adaptive
quadrature script agree across all ten lambda states to:

| regime | endpoint truth (kT) | selected Gauss-Legendre order | max independent disagreement (kT) |
| --- | ---: | ---: | ---: |
| easy | 0.7705551151 | 96 | 6.66e-16 |
| metastable | 0.7355290500 | 192 | 1.03e-15 |

The agreement is far inside the frozen `1e-7 kT` tolerance. The two reference
implementations do not import one another.

## Held-out results

Every row below has sixteen registered held-out seeds in its denominator.
Accuracy, coverage and interval summaries are complete-case quantities; failures
are stated separately and were not replaced.

| regime | method | complete / 16 | bias (kT) | RMSE (kT) | nominal 95% coverage | within 0.5 kT | mean y sign transitions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| easy | independent windows | 16 | +0.0289 | 0.1545 | 0.9375 | 1.000 | 417.4 |
| easy | neighbor exchange | 16 | -0.0625 | 0.1040 | 0.9375 | 1.000 | 1232.1 |
| metastable | independent windows | **4** | -0.7361 | 0.9561 | 0.0000 | 0.250 | 164.0 |
| metastable | neighbor exchange | **16** | -0.1019 | 0.2076 | 0.7500 | 1.000 | 1064.4 |

Twelve metastable independent-window runs failed the frozen minimum of five
decorrelated samples in at least one full/early/late state block. Their absence
from the complete-case bias/RMSE is not success and makes the `4 versus 16`
accuracy comparison conditional. Availability improved from 4/16 to 16/16 in
this constructed regime. Exchange acceptance averaged 0.717 and every exchange
experiment had all ten walkers visit both endpoints. The easy-regime exchange
acceptance was 0.761.

Conditional MBAR intervals were not fully calibrated in the harder regime even
with exchange: held-out coverage was 12/16, not the nominal 95%. The intervention
improved sampling and accuracy here but did not make conditional uncertainty
automatically reliable.

Among the four admitted metastable baseline runs, the frozen interval-width rule
was falsely reassuring in three. Net hysteresis and minimum-overlap rules did not
produce false reassurance among those four because they generally warned rather
than passed. This tiny, selected complete-case subset is not a comparative
diagnostic-performance estimate. All model-specific rules remain nontransferable.

## Rejected v1 rehearsal

`results/cpu_calibration/known_answer_model_v1/` is retained as a technical
rehearsal, not scientific evidence. V1 regularly spaced snapshots were passed
directly to MBAR without an explicit correlation treatment, so its covariance
and coverage results were not interpretable. After detecting this during review,
v2 was registered in a new namespace with new development and held-out seeds.
No v1 seed was reused. The v2 minimum-sample failure initially aborted execution;
the handler was corrected to retain failures in the denominator without changing
the threshold or replacing seeds.

## Files and integrity

- Primary implementation: [`known_answer_model.py`](../src/analysis/known_answer_model.py)
- Independent reference: [`known_answer_reference_independent.py`](../scripts/known_answer_reference_independent.py)
- CPU-only DAG: [`known_answer_model.smk`](../workflow/known_answer_model.smk)
- Machine report: `results/cpu_calibration/known_answer_model_v2/calibration.json`
- Final report SHA-256:
  `05552b8e2720c2ebcba9e9d16e62f498629eaab5b1f2d8f8ac23cf3e2b5275b1`

The report contains all 80 experiments: 16 development and 64 held-out across
two regimes and two methods. Figure failures are marked at their registered seed
positions. Every plot value and admission outcome is present in the JSON.

## Interpretation and exit

Work package B's exit condition is met: the reference is independently validated,
the evaluation is executable and hash-bound, and held-out outcomes—including
failures—are reported. In the deliberately metastable model, neighbor exchange
improved state traversal and endpoint estimation at fixed potential-evaluation
cost. This demonstrates the intended intervention under constructed assumptions;
it is not evidence that F64A has this slow coordinate or that GROMACS exchange is
feasible on the SCC.

The next step is C1 technical feasibility: verify the actual GROMACS build,
MPI/multisim allocation, state/energy mapping, checkpointing, exchange histories,
storage and equal-cost accounting before selecting any protein arm.
