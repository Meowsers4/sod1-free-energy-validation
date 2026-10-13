# F64A raw-energy CPU audit — 2026-09-18

## Outcome

The fixed [exploratory design](f64a_raw_energy_audit_design.md) has now run on the
60 real production NPZs from SCC job **7620241**. All exact file hashes match the
frozen v2 report; all matrices are finite `(20, 15001)` and their metadata,
protocol and both simulation ancestry identities agree. Input and dependency
hashes remained unchanged during the successful computation. No new MBAR fits,
cutoffs, uncertainty estimates, stationarity tests or GPU work were performed.

Raw adjacent-energy differences show late time dependence and selected suffixes
can describe only a small portion of the original block. This supports keeping
duration/selection stability unresolved. It does not establish a structural cause,
identify a window's contribution to endpoint free energy, or resolve model/reference
mismatch versus unsampled conformations. **Stop GPU sampling at 15 ns.**

## Preserved outputs

Output directory: `results/cpu_audits/f64a_raw_energy_v1/`.

- [JSON](../results/cpu_audits/f64a_raw_energy_v1/raw_energy_audit.json): **348**
  observable/block/path records, **1044** saved-policy raw-suffix summaries and
  **4176** contiguous 250-record bins. SHA-256:
  `02afc46c3b76b3b3f1bc28d94f1aa5f4cb1898b4860b2a0981ce74df9398054b`.
- [Sampled-state energy](../results/cpu_audits/f64a_raw_energy_v1/sampled_state_u.png),
  [previous-neighbor difference](../results/cpu_audits/f64a_raw_energy_v1/previous_minus_sampled_u.png),
  [next-neighbor difference](../results/cpu_audits/f64a_raw_energy_v1/next_minus_sampled_u.png):
  all repeats/windows displayed and visually inspected. Each path is centered
  over the displayed 9–15 ns interval, so baseline repeat offsets are hidden;
  colors saturate at the fixed display percentile. Consult uncentered JSON means.

Runtime: Python **3.13.9**, NumPy **2.3.5**, Matplotlib **3.10.8**, PyYAML **6.0.3**.
Executable audit package at execution: repository commit `2c61ae6`. Configurations
and analysis modules were unchanged; exact dependency hashes are in the JSON.
The raw NPZs remain gitignored and are also retained on SCC. Committed derived
outputs are not a substitute for independent backup of the raw input matrices.

## Descriptive observations

All values below are reduced-potential **kT units**, not kcal/mol endpoint ΔG.
“Half drift” means second-half minus first-half raw-block mean. These are selected
examples from the complete ladder, not newly fitted thresholds or significance tests.

Window 17 in retained 12–15 ns makes the policy issue particularly clear:

| Repeat | Previous-neighbor half drift | Next-neighbor half drift | Adaptive raw suffix |
| --- | ---: | ---: | ---: |
| r0 | −0.128873 | +0.102360 | 860 / 3000 records |
| r1 | +0.926750 | −0.702933 | 125 / 3000 records |
| r2 | +0.438548 | −0.318354 | 32 / 3000 records |

For r1, the saved adaptive cutoff is at retained **14.876 ns**. Its suffix mean
differs from the full-block mean by **−0.736852 kT** (previous) and **+0.531935 kT**
(next). The fixed-25% next-neighbor suffix still has half drift **−0.961791 kT**.
The adaptive next-neighbor suffix itself has half drift **+0.138242 kT**; a short
suffix is not a uniformly stable version of the whole trajectory. For r2, the
saved adaptive cutoff is **14.969 ns**, leaving just 32 raw records (not 32
independent samples).

This is not confined to window 17. At window 18 in 9–12 ns, r1's previous/next
half drifts are **−0.771880 / +0.711962 kT**, and r2's are
**−0.596412 / +0.533380 kT**. At window 14, r2's full-block previous/next means
change between 9–12 and 12–15 ns from **1.175274 / −0.414925** to
**0.045057 / +0.412768 kT**. At window 16, r2's 9–12 ns adaptive suffix contains
186 records and shifts its previous/next mean by **+2.268692 / −1.558505 kT**
relative to that full block. Both adjacent directions reuse the same energies;
their opposing changes are not independent confirmations.

Window 17 r1's full 12–15 ns next-neighbor descriptive ACF is **0.471569** at
100 ps and **0.305021** at 250 ps. These describe correlation in a changing
series, not an equilibrium correlation time or effective sample size. Many
sampled-state energy bins fluctuate strongly without the same neighbor-difference
pattern; absolute-energy variation alone cannot assign an alchemical bottleneck.

## Execution and next decision

An explicit main-DAG dry-run scheduled exactly one CPU job. Its execution attempt
exited nonzero before publishing an output directory; the cause was not established
from the captured workflow log. With no existing evidence to overwrite, the
documented module command using the explicit analysis interpreter succeeded:

```bash
MPLCONFIGDIR=/private/tmp/sod1fep-raw-audit-mpl \
  /opt/anaconda3/bin/python -m src.analysis.f64a_raw_energy_audit
```

Do not rerun into this output directory: the module refuses existing evidence.
No claim is made that the main-DAG execution succeeded. Scientific input integrity
was checked both before analysis and again before output publication.

Next: follow the [scoped publication plan](publication_research_plan.md), starting
with the exploratory λ/comparator analysis before selecting a bounded intervention.
A separate [read-only aggregation and interpretation correction](conclusion_reconciliation_2026-09-18.md)
reproduces the suggested high-λ pattern from this report. It is not an addition
to the fixed audit's registered outputs. Localization does not choose uniquely
between schedule, sampling-method or different-start tests and does not establish
a structural cause. The two-start draft is a reserve option. Vlasov reviews later;
billed SU accounting remains pending.
