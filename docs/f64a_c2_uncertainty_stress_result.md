# F64A C2 CPU uncertainty stress diagnostic v1

Completed 2026-10-03. This is a **constructed stationary-model diagnostic** for the proposed early/late MBAR block errors. It is not an HREX simulation, a protein result, or acceptance of a production uncertainty method. No SCC access or GPU job occurred.

## Frozen construction and scope

The [JSON specification](f64a_c2_uncertainty_stress_v1.json), SHA-256 `087162288ff94fc905e4fb8a5db3234dd1cfb61bd9fda284f9324d2829a12026`, fixes 20 equal-curvature harmonic states with centers from 0 to 2, 128 samples in each of two disjoint blocks, four development seeds and 32 separate held-out seeds per regime. Every state has the same Gaussian partition function, so the true endpoint free-energy difference is **zero** in both blocks. The `iid` regime has independent samples and states. The `correlated_synchronized` regime uses AR(1) coefficient 0.9 and 50% shared innovations across states at each time; it stresses both serial and cross-state dependence but does **not** model actual replica exchanges.

For each pre-split block, the [CPU runner](../src/analysis/f64a_c2_uncertainty_stress.py) fits the same 20-state MBAR in two ways: all 128 records per state (`raw`) and fixed-block per-state thinning using the ceiling of estimated statistical inefficiency in the nearest-neighbor energy difference (`thinned`). There is zero additional equilibration trim and no late-to-early block selection. Fewer than five selected samples in any state fails that fit; failures remain in the attempted-seed count. Conditional PyMBAR block SEs form nominal ±1.96-SE intervals. The sum of early and late SE² is recorded as a **naive zero-covariance comparator**, not a validated joint variance. [PyMBAR's timeseries guidance](https://pymbar.readthedocs.io/en/master/timeseries.html) states that MBAR requires uncorrelated samples and provides statistical-inefficiency tools; this stress run tests whether this particular per-state use is adequate.

## Held-out observations

| Regime | Selection | Complete / 32 | Early truth coverage | Late truth coverage | Empirical Var(late−early), kT² | Mean naive Var(late−early), kT² |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| IID | Raw | 32 | 28/32 | 31/32 | 0.00322 | 0.00313 |
| IID | Thinned | 32 | 29/32 | 31/32 | 0.00429 | 0.00435 |
| Correlated synchronized | Raw | 32 | 3/32 | 4/32 | 0.48498 | 0.00301 |
| Correlated synchronized | Thinned | **24** | 5/24 | 7/24 | 0.64049 | 0.03240 |

The correlated thinning failures were held-out seeds 3102, 3108, 3115, 3116, 3117, 3122, 3124 and 3126. Coverage and variance above are complete-case diagnostics; **24/32** is the availability result. Under the stationary truth, mean naive `D² − (SE_early² + SE_late²)` was **+0.472 kT²** for raw correlated fits and **+0.583 kT²** among the 24 thinned correlated fits. These positive values arise in a construction with no physical free-energy drift. The failure shows why the naive zero-covariance noise correction cannot be promoted to C2's `Q` endpoint, and why per-state thinning alone is insufficient in this stress case. It does not quantify a protein effect or prove any HREX method will behave identically.

## Integrity and next gate

- Machine [report](../results/cpu_calibration/f64a_c2_uncertainty_stress_v1/report.json): SHA-256 `3ddf9dfe24a286b4aff246a39d079620479802552cc8e9bebc0daf45241bf63a`; 72 unique regime/cohort/seed records, including every failure. A partial fit has explicit record status `partial_or_failed`.
- Runner SHA-256 `cb32bcd27837c4d9d4b1b95a2500d9bf08b0bee6b2457714addd55bc66a53910` at execution; PyMBAR 4.0.3, NumPy 2.3.5, SciPy 1.16.3. The report records these versions and its implementation digest.
- The read-only [GROMACS input adapter](../src/analysis/f64a_c2_gromacs_inputs.py) was compared with **alchemlyb 2.4.1** `extract_u_nk(filter=False)` on the user-supplied Stage P excerpt: all **21 records and 20 state columns** matched after row-centering, with maximum absolute difference `2.7817e-11 kT`. The installed reference parser file had SHA-256 `aec36f5ab8a78285fa2af4c00f6eca7b19cead23700889dcc65ac88d3c92a3ee`; the excerpt SHA-256 is `b22fbc6c5d5a2f06c743bdd26d7234e81eaf554782f78b4c9118db03a45adbd0`. The [published alchemlyb parser source](https://alchemlyb.readthedocs.io/en/latest/_modules/alchemlyb/parsing/gmx.html) adds total energy and pV to each foreign-state Hamiltonian difference before multiplying by `1/(RT)`; row-centering cancels those shared offsets. This **passes the independent parser check for the excerpt**. A complete sealed multi-state GROMACS output still needs the same check before protein analysis.

The next uncertainty work is to construct and calibrate a **joint** early/late variance method that preserves synchronized state/walker time structure, then test it on stationary, drifting and long-correlation held-out data with a stated acceptance rule. The present conditional block SEs do not validate `Q` or its covariance bounds under correlated sampling. Scientific exposure, repeat count and spread criteria remain unselected; no production analysis or allocation follows from this diagnostic.
