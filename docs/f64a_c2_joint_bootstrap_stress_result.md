# F64A C2 joint early/late bootstrap stress v1

Completed locally on 2026-10-03. **The proposed synchronized stationary bootstrap failed the correlated held-out diagnostics.** It is a CPU-only constructed-data test, not protein HREX evidence. No SCC access or GPU job occurred. The C2 noise-adjusted `Q` endpoint, its covariance bounds, and production uncertainty remain unqualified.

## Frozen method and scope

The [specification](f64a_c2_joint_bootstrap_stress_v1.json), SHA-256 `8dc0e863bd716bbbc838f8e4aa22e7c8ae15ec87c1450019510c92f2b8301e9d`, fixed four development seeds and 32 disjoint held-out seeds per regime before the held-out run. The [runner](../src/analysis/f64a_c2_joint_bootstrap_stress.py), SHA-256 `39d66f6644e879c4a3bfd6c8d3a6cf1cd5afea6913bf087f59a560ba13ed4887`, fits 20-state MBAR separately to 128 early and 128 late observations. For each seed it then generates 24 stationary-bootstrap copies of the **whole 256-time-point series** with geometric mean block length 32. Each resampled time index selects the complete 20-state row, and the early/late split is restored *after* resampling. This retains within-block synchronized state fluctuations and permits a resampled contiguous run to cross the early/late boundary. Failed MBAR fits remain in the attempted denominator; at least 20 of 24 bootstrap fits are required for an estimated `Var(D)`, where `D = G_late − G_early`.

The construction has 20 equal-curvature harmonic states, so the equilibrium endpoint is exactly zero. Its regimes are IID, synchronized AR(1) with `phi=0.9` and 50% shared innovations, a longer-correlation `phi=0.98` version, and a nonstationary linear-shift failure probe. The shift is 0.6 coordinate units over the 256 observations. None has actual HREX walker swaps, protein interactions or SCC timing. This is a test of a joint variance candidate, not its validation for the real C2 arms. The resampling design follows the [stationary bootstrap](https://www.tandfonline.com/doi/abs/10.1080/01621459.1994.10476870); [correlated MBAR error analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC10845960/) explains why joint time dependence matters. The sources motivate the method; neither certifies this finite-sample application.

The frozen stationary-regime diagnostic required at least 30/32 completed seeds, at least 27/32 nominal-95% intervals for `D` containing the known zero value, and a mean estimated `Var(D)` between 0.5 and 2 times the empirical across-seed variance. The drifting regime was predeclared a failure probe with **no** stationary coverage pass rule. A pass here would still not have qualified protein uncertainty.

## Held-out results

| Regime | Complete | Zero covered | Empirical `Var(D)`, kT² | Mean estimated `Var(D)`, kT² | Ratio | Frozen diagnostic |
|---|---:|---:|---:|---:|---:|---|
| IID | 32/32 | 29/32 | 0.00290 | 0.00259 | 0.89 | Pass |
| Synchronized `phi=0.9` | 32/32 | 25/32 | 0.67578 | 0.26619 | 0.39 | **Fail** |
| Long correlation `phi=0.98` | 32/32 | 18/32 | 1.64682 | 0.43804 | 0.27 | **Fail** |
| Drifting `phi=0.9` | 32/32 | Undefined | 0.67604 | 0.33175 | 0.49 | Failure probe only |

All 24 bootstrap fits succeeded in every complete seed. The drift case's across-seed mean `D` was −0.794 kT, versus +0.004 kT in IID, −0.191 kT in synchronized correlation and −0.152 kT in long correlation. These means are finite-seed diagnostics, not protein free-energy estimates. The drift variance ratio is descriptive only: resampling a nonstationary whole series cannot supply a valid stationary-bootstrap interval. A 32-seed coverage estimate itself has sampling uncertainty, but both correlated regimes also fail the independently frozen variance-ratio criterion. The stronger long-correlation shortfall is consistent with finite 128-record blocks and the frozen mean bootstrap length of 32; it does not identify a unique cause.

## Reproducibility and decision

- [Development report](../results/cpu_calibration/f64a_c2_joint_bootstrap_stress_v1/development.json): SHA-256 `caab098aeca7a1df10e549eaac37a07f4a29dea745347f49aae51e849d7eebf8`.
- [Held-out report](../results/cpu_calibration/f64a_c2_joint_bootstrap_stress_v1/heldout.json): SHA-256 `247e51f1f84c9f873f1be8fbb65f699a4905ee654701d27e0ad0ee3a77a77047`. It includes all 128 held-out records and failures, if any.
- `python -m pytest tests/test_f64a_c2_joint_bootstrap_stress.py tests/test_f64a_c2_uncertainty_stress.py -q` passed 4 tests; `git diff --check` passed.

To reproduce on a local CPU, run `python -m src.analysis.f64a_c2_joint_bootstrap_stress --cohort development --output /tmp/c2-joint-development.json` and then the same command with `--cohort heldout --output /tmp/c2-joint-heldout.json`. Use separate output paths because the runner refuses to overwrite an existing report.

This v1 method cannot provide a calibrated C2 `Var(D)` under the correlated cases and therefore cannot support a point `Q = D² − Var(D)`. The earlier per-state thinning method also failed its [held-out stress](f64a_c2_uncertainty_stress_result.md). Keep signed `D`, absolute movement `M`, raw counts and any *unvalidated* conditional errors clearly labeled. Do not compute a validated `Q`, assert an HREX advantage or select production from these synthetic results. A next candidate needs a separate frozen specification, longer synchronized trajectories and block-length sensitivity, with actual walker-history handling before use on protein HREX data. No new GPU allocation is implied.
