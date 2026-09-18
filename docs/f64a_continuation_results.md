# F64A 9→15 ns continuation and late-window audit — 2026-09-18

## Status and evidence

The selected [design](f64a_continuation_9_to_15_design.md) and registered
[v2 package](../pilots/f64a_sampling_extension_v2/PREREGISTRATION.md) have been run
on SCC. First-light job **7619903** passed with `(20, 9011)`; production array
**7620241** has left the queue. The user supplied the completed
[54-fit report](f64a_extension_review/f64a_continuation_v2.json), preserved without
editing. Its SHA-256 is
`ddb20589d809682f7ef72a4fddc55c6998c48ca3b7a06b1b466682291a24ab71`.
Simulation and analysis commit: `802cc9ef9a445a9010ae721c9f5bf6cc5ff8afe3`.

This is an exact-path continuation of F64A folded monomer apo-2SH, all 20 lambda
states × three repeats. No new protein starts, velocities, repeats or unfolded
leg were added. The historical failed gate and F64A exclusion remain unchanged.
The fixed endpoint is 15 ns retained sampling (15500 ps simulation time).

Local review verified:

- All 45 disjoint-block and nine dependent cumulative fits, 1080 window-selection
  records, 1026 adjacent-pair records and 513 paired local-change records.
- Complete fit/contrast identities, slice bounds, sample counts, global indices,
  overlap-matrix entries, forward/reverse hysteresis arithmetic and local changes.
- All block/cumulative means, ranges, repeat SEMs, propagated MBAR errors,
  larger-of uncertainties and paired movement summaries by recomputation.
- All ten recorded analysis dependency hashes and all 23 simulation dependency
  hashes against the local repository at review time.
- All 60 recorded frozen source NPZ hashes against the preserved v1 sensitivity
  report. The SCC report records successful v1 reproduction and unchanged inputs
  during analysis.

This is review of a user-supplied SCC report, **not independent local NPZ/XVG
validation or MBAR reproduction** at that review checkpoint. Subsequently, all
60 extended NPZs were downloaded and validated in the
[raw-energy CPU audit](f64a_raw_energy_audit_results.md); checkpoints/XVG were not
downloaded or independently validated, and no MBAR reproduction was performed.
The report was written despite the user's subsequent SSH timeout; no restart was
needed. No failed fit was dropped.

## Registered primary endpoint

Paired movement from retained 9–12 to 12–15 ns, later minus earlier, in kcal/mol:

| Policy | r0 | r1 | r2 | Mean movement | Paired repeat SEM |
|---|---:|---:|---:|---:|---:|
| Adaptive | −0.051499 | −0.695174 | +0.598142 | −0.049510 | 0.373350 |
| Untrimmed, with thinning | +0.801544 | +0.301255 | +0.635475 | +0.579425 | 0.147115 |
| Fixed 25% trim, with thinning | +0.745504 | −0.057160 | +0.543874 | +0.410739 | 0.241081 |

The small adaptive mean reflects **opposing repeat movements**, not uniformly
stable repeats. Both fixed policies show upward mean movement; the adaptive/fixed
mean difference spans 0.628935 kcal/mol. Policies reuse the same raw data, so they
are not independent confirmations. Paired SEMs describe three repeat movements;
they are not 95% intervals or formal independent-sample significance tests.

## Blocks, repeats and cumulative estimates

Adaptive block summaries (uncertainty is the larger of repeat SEM and propagated
MBAR error; all values in kcal/mol):

| Retained block | Mean ± reported uncertainty | Repeat range | Propagated MBAR error |
|---|---:|---:|---:|
| 6–9 ns | 0.587070 ± 0.100329 | 0.343963 | 0.062048 |
| 9–12 ns | 1.235524 ± 0.598056 | 2.047618 | 0.053877 |
| 12–15 ns | 1.186014 ± 0.579923 | 1.946359 | 0.064200 |

Adaptive cumulative estimates are 0.770941 ± 0.105017 at 9 ns,
1.124952 ± 0.360996 at 12 ns and 1.326840 ± 0.286567 at 15 ns. They overlap in
data and must not be treated as independent estimates. The 9→15 ns cumulative
mean movement is +0.555899 kcal/mol; no paired uncertainty is invented for it.

The final-block r0 estimate is especially selection-sensitive: 0.069247 adaptive,
0.931051 untrimmed and 0.887450 fixed-25%. This does not license selecting a
preferred policy. Final-block repeat ranges are 1.946359 adaptive, 0.931648
untrimmed and 0.854022 fixed-25%; agreement is not established by any of these
descriptive summaries. All secondary contrasts are retained in the full report.

## Post-result, CPU-only late-window audit

The user authorized this descriptive follow-up on 2026-09-18, **after** the results
were visible. It is not a preregistered new test. The [audit configuration](f64a_late_window_audit.yaml)
defines the two new blocks and labels trimming of at least 90% as "heavy" solely
for reporting. That label is not a convergence threshold or an exclusion rule.
The [computed audit](f64a_extension_review/f64a_late_window_audit.json) contains
all selections/pairs, joined counts, per-fit summaries and all 114 policy/block/pair
summaries across repeats. No new MBAR fit or simulation was run.

### Selection is highly time-local and fixed policies are also sparse

Each new block has five heavily trimmed adaptive window/repeat combinations:
9–12 ns involves windows 15, 16, 18 and 19; 12–15 ns involves 17, 18 and 19.
These are ten combinations out of 120 adaptive window/block/repeat observations,
not ten independent scientific samples.

In 12–15 ns, adaptive r2/window 17 discards 2968/3000 records (98.933%), leaving
32 raw records and **seven samples after thinning**. Its selected data span
14.969–14.999 ns retained time. Adaptive r0/window 19 retains 24 selected samples
after discarding 96.533%; r1/window 17 retains 31 after discarding 95.833%.
Thus some windows in a nominal three-ns estimate represent only a short late suffix.

This is **not solely an adaptive-cutoff problem**. In the same final block,
untrimmed r1/window 17 retains ten samples with estimated g = 328.865;
fixed-25% r1/window 17 retains seven with g = 330.323. For r2/window 17, the two
fixed policies retain 18 and 12 samples with g = 173.025 and 190.279 respectively.
The adaptive r2 suffix has g = 5.048. These estimates use different time spans;
a small suffix correlation estimate cannot establish whole-block stationarity.
The counts are selection outputs, not verified independent basin samples.

### Local diagnostics do not identify one intervention target

Final-block pair rankings (mean absolute local hysteresis pooled over three
repeats; weakest overlap is the minimum directional entry over pairs/repeats):

| Policy | Largest mean absolute local hysteresis | Weakest overlap pair/value |
|---|---|---|
| Adaptive | 18–19: 0.681529 kcal/mol | 16–17: 0.008715 |
| Untrimmed | 17–18: 0.480813 kcal/mol | 10–11: 0.009567 |
| Fixed 25% | 18–19: 0.416515 kcal/mol | 16–17: 0.006837 |

In 9–12 ns the largest hysteresis pair is 18–19 under adaptive selection but
13–14 under both fixed policies; the weakest-overlap pair is 14–15 adaptive and
8–9 fixed. Heavy trimming, low overlap and large discrepancy are different
diagnostics and need not peak at the same pair. A rank is not proof of a causal
bottleneck, and adjacent Zwanzig changes do not sum to MBAR endpoint drift.

### Small net hysteresis still hides local discrepancies and repeat disagreement

Adaptive cumulative r1 at 12 ns has net hysteresis **0.017751 kcal/mol** while
sum-absolute local hysteresis is **1.806754**, maximum-local hysteresis is 0.451784,
and the cumulative repeat range is **1.227772**. About 99.02% of the sum-absolute
discrepancy cancels in the net value. No aggregate self-consistency value proves
repeat agreement or unvisited-state coverage.

## Interpretation and next decision

**Duration stability remains unresolved at the registered 15 ns endpoint.** The
continuation revealed renewed repeat disagreement, opposing adaptive movements,
and substantial selection sensitivity. It does not show uniform stabilization;
it also does not isolate a structural mechanism, shared trapping, force-field
error or experimental/reference mismatch. Disjoint blocks can remain slow-mode
correlated; small conditional uncertainties cannot cover conformations never visited.
These are folded-leg mutation free energies, not folding ΔΔGs or a new gate pass.

Stop GPU sampling here. No single-window extension, automatic additional duration,
different-start arm, new pass threshold or policy retuning is authorized by this
audit. The next useful evidence would be a **CPU-only review of the raw late energy
time series**: inspect whole-block versus selected-suffix behavior and correlations
around the sparse windows, while retaining the complete ladder. The current report
cannot perform that raw-data check or establish within-repeat stationarity. Such a
check can inform a separately designed different-start or sampling-method test;
do not assume that either has already been selected.

Mentor review remains deferred at user direction. No reviewer was contacted.

## Resource amendment and reproducibility

Before GPU submission, the user explicitly approved proceeding without confirmed
L40S SU pricing. The entered **1 SU/core-hour was a planning assumption**, overriding
the registration's confirmed-rate requirement, not a verified node tariff. The
approved aggregate 130 GPU-hour limit and maximum two attempts per task remained
enforced. **1040 SU is conditional on that rate, not a guaranteed billing ceiling.**
Actual v2 job accounting/billed SU has not been supplied for local review; no measured
cost or tariff is inferred from the scientific report. Preserve SCC admission and
submission records and review actual accounting separately.

Audit code: [f64a_late_window_audit.py](../src/analysis/f64a_late_window_audit.py).
It consumes only the preserved report, refuses a changed input hash/incomplete or
inconsistent records, records source/config hashes and publishes atomically without
overwriting. The original report-only audit did not edit v2 configs, simulation
modules or its registered workflow. The subsequent repository review included the
CPU audit rules from the live main DAG. That live workflow now differs from the
execution snapshot: reproduce the original v2 identity at **802cc9e**, not current
HEAD. The standalone CPU DAG remains available:

```bash
snakemake -n --snakefile workflow/f64a_late_window_audit.smk --cores 1
```

The computed audit is already preserved. To independently regenerate it, copy the
audit YAML to a new file, set its `output` to a fresh path, and run
`python -m src.analysis.f64a_late_window_audit --config YOUR_AUDIT_CONFIG`.
Never overwrite the supplied report or remove evidence to get a rerun to pass.

Verification: 109 focused F64A/audit tests passed; Ruff on the two audit modules
and their tests, and `git diff --check`, passed; the separate Snakemake DAG dry-run passed (one CPU-only audit job when
forced, no GPU producers). Input preservation was checked byte-for-byte. The
audit ran locally with Python 3.13.9 and does not import MBAR/JAX; the original
SCC scientific fits record Python 3.11.15 and their own package identities.
