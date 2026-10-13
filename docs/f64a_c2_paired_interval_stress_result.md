# F64A C2 paired movement and spread interval stress v1

Completed locally on 2026-10-03. This CPU-only normal-model calibration tests proposed interval *methods*, not C2 protein outcomes, useful-effect thresholds or final pair counts. No SCC access or GPU job occurred.

The frozen [specification](f64a_c2_paired_interval_stress_v1.json), SHA-256 `353844752e905a0f4bac7df56dc67486227a3dec5cb2e3d8b7566e2ca2e2ab9f`, fixes 1,000 independent trials for each combination of 10 or 33 attempted pairs, positive or negative 0.6 within-pair correlation, and complete, missing-completely-at-random (MCAR), or outcome-dependent missingness. Each pair has coherent early and late signed movement, with known normal marginal parameters. The true HREX-minus-baseline mean absolute-movement contrast is **−0.2647** in constructed kT units; the true late-spread (SD) contrast is **−0.25**. The [runner](../src/analysis/f64a_c2_paired_interval_stress.py), SHA-256 `fd83e87a067e7f5535d7295b7845c592f4986371aa4b5178611f066a9de292ef`, uses a paired Student-t interval for mean absolute movement and a paired percentile bootstrap (399 resamples) for the late-SD difference. It retains every attempted pair, reports missing arms separately, and calculates intervals only with at least five complete pairs.

Frozen screening required each nominal-95% interval's conditional coverage to reach at least 92% in complete and MCAR cases. Outcome-dependent missingness was a failure probe, with no pass rule. The table gives the percentage of **available** trial intervals covering the known truth; availability is separate.

| Attempted pairs | Pair correlation | Missingness | Available / 1000 | Mean complete pairs | Movement coverage | Spread coverage | Both pass? |
|---:|---:|---|---:|---:|---:|---:|---|
| 10 | +0.6 | Complete | 1000 | 10.0 | 94.9% | 90.4% | No |
| 10 | +0.6 | MCAR | 989 | 8.0 | 93.3% | 88.7% | No |
| 10 | −0.6 | Complete | 1000 | 10.0 | 94.1% | 88.7% | No |
| 10 | −0.6 | MCAR | 998 | 8.1 | 94.9% | 88.5% | No |
| 33 | +0.6 | Complete | 1000 | 33.0 | 95.3% | 93.6% | Yes |
| 33 | +0.6 | MCAR | 1000 | 26.8 | 95.4% | 92.3% | Yes |
| 33 | −0.6 | Complete | 1000 | 33.0 | 93.5% | 91.3% | No |
| 33 | −0.6 | MCAR | 1000 | 26.7 | 94.1% | 90.6% | No |

The Student-t movement interval cleared this diagnostic in all eight complete/MCAR combinations. The spread percentile interval did not. The three outcome-dependent missingness cases per pair count remain in the [machine report](../results/cpu_calibration/f64a_c2_paired_interval_stress_v1/report.json), SHA-256 `973b83ec957aaf1248c796dbcbf0cf4b0e8c453c8ff6743d5b863d4b118bd98f`; their coverage is descriptive because missingness depends on the outcome. The report records all 12 scenario summaries and conditional denominators. The synthetic units and normal model do not establish protein precision or sample size. A separately frozen spread-interval candidate is required. The C2 overall-benefit rule and exposure/repeat thresholds remain unselected.
