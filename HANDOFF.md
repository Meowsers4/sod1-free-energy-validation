# HANDOFF — SOD1 FEP pipeline

## Current update — 2026-09-18: F64A completed through 15 ns

The subsequent raw-energy follow-up is complete; see
[results](docs/f64a_raw_energy_audit_results.md) and
[fixed CPU audit design](docs/f64a_raw_energy_audit_design.md). All 60 production
NPZs are now local and exactly match the frozen report hashes, shapes, metadata
and simulation ancestry. The audit describes 348 raw series and 1044 saved-policy
suffixes, with no new MBAR/GPU work. Late changes in adjacent energies and very
short selected suffixes remain visible; neither this audit nor a quiet suffix
certifies equilibration. The next step is a separately specified sampling test,
not an automatic extension or GPU submission.

The separately selected v2 continuation completed on SCC: first light **7619903**
passed; production array **7620241** left the queue, and the full 54-fit CPU report
was supplied and preserved. See [results and late-window audit](docs/f64a_continuation_results.md).
Local review reconciled all summaries, 1080 selections, 1026 adjacent records and
513 paired changes; report-only audit outputs are in `docs/f64a_extension_review/`.
This is not independent local raw-NPZ/MBAR reproduction.

The primary adaptive mean movement is −0.049510 kcal/mol but masks r1 −0.695174
and r2 +0.598142; fixed-policy means move +0.579425 and +0.410739. Adaptive final
repeat range is 1.946359. Sparse window 17 persists even with fixed policies.
Duration stability is unresolved; **stop GPU sampling at 15 ns**. Next evidence:
CPU-only raw energy time-series inspection, not an automatic extension or new starts.
No new arm is selected. Mentor review remains deferred.

The user explicitly accepted unconfirmed pricing before submission: 1 SU/core-hour
is a planning assumption; 1040 SU is conditional. The 130 GPU-hour/two-attempt
limits remain approved. Actual v2 billed SU is still unreviewed locally.
Capture the SCC records promptly using [accounting closeout](docs/f64a_accounting_closeout.md).
The [repository review](docs/repository_review_2026-09-18.md) records verified findings,
preservation commits, release safeguards and remaining limits. The current default
Snakemake target only verifies the historical bundle; it does not rebuild it.
Earlier sections below preserve project history and are not current pending steps.

Updated 2026-09-15 after explicit user authorization of the F64A continuation pilot. Read
[`CLAUDE.md`](CLAUDE.md) first; it is the operating rulebook. Read [`README.md`](README.md)
for the scientific design.

## F64A continuation pilot authorized and packaged (2026-09-15)

The user authorized the bounded pilot after reviewing the temporal result and GPU capacity.
The registered package is [`pilots/f64a_sampling_extension_v1/`](pilots/f64a_sampling_extension_v1/).
It copies the exact archived F64A folded checkpoints and continues all 20 lambda states ×
3 repeats for 6 ns, extending retained sampling from 3 to 9 ns. It is folded-only,
apo-2SH, L40S-pinned, capped at eight simultaneous tasks, and isolated below
`results/pilots/f64a_sampling_extension_v1/`. A real one-GPU 10 ps first-light continuation
must pass before the 60-task production array. No submission has been made from this local
workspace; follow the package README on the SCC.

The pilot is an exploratory sampling diagnosis and does not reopen or replace the frozen
gate. Its primary endpoint is folded-leg time dependence; it is not a new experimental-
accuracy test. The package validates every source NPZ against the frozen forensic manifest
and refuses missing/mismatched checkpoints, protocols, or historical output paths.

## Temporal analysis completed (2026-09-14)

The retrospective 25/50/75/100% analysis in
[`docs/temporal_analysis_design.md`](docs/temporal_analysis_design.md) has been run. All 240
leg intervals solved, no failed block was dropped, and the 100% estimates reconciled with the
frozen audit to numerical precision. The main cohort still moved relative to its disjoint
final quarter: at 75%, folded-leg movement had median 0.311 and maximum 1.070 kcal/mol.
F64A folded r1 was already the largest mover at 25% (1.808 kcal/mol); signed net hysteresis
ranked 19/21 while maximum local discrepancy ranked 1/21. See
[`docs/temporal_analysis_results.md`](docs/temporal_analysis_results.md) and
[`docs/temporal_review/`](docs/temporal_review/).

This motivated the bounded, subsequently authorized pilot described above.
The user identified their existing mentor, Peter Vlasov, as the human reviewer;
[`docs/mentor_review_request.md`](docs/mentor_review_request.md) contains an unsent draft.

GPU availability was subsequently checked. The pipeline-compatible shared `l40s` queue has
40 physical GPUs; nine were free in the snapshot, so eight-way concurrency is a conservative
planning value. The `rise-batteries` balance is 15,987.0494 SU. Compute allocation is ample
for a one-variant pilot; `/projectnb/rise-batteries` storage (38.16/50 GB) is the tighter
constraint. See [`docs/gpu_access_snapshot.md`](docs/gpu_access_snapshot.md).

## Publication-review revision (2026-09-14)

The user authorized fixes to the publication review and planning with GPU availability.
The CPU correction work is complete: raw local-diagnostic audit, grouped statistical
sensitivity, revised claims, conditional redox uncertainty, and a portable release.
Read [`docs/cpu_improvement_plan.md`](docs/cpu_improvement_plan.md) for results and next steps,
and [`docs/release_reproduction.md`](docs/release_reproduction.md) for reproduction.
The current figure/JSON set is `docs/review/`; `docs/figures/` retains earlier graphics.

The new audit reconciles 48 records and 912 adjacent pairs. F64A r1's small aggregate
hysteresis contains 98.647% signed cancellation; alternative summaries have not demonstrated
better prediction of sibling disagreement. Grouped intervals include zero on the folded leg.
The G93A SS−2SH shift is −0.016918 kcal/mol, conditional unpaired Welch 95% interval
[−0.296618, +0.262781]. It does not exclude slow redox-dependent ensemble changes.

The historical manifest is preserved. Its five original repository inputs are frozen under
`data/forensic_baseline_repository/`; the release adds a new manifest covering revised source
and outputs. The A4V original raw-window loss remains explicit. Independent **human** review
is still outstanding. No inquiry, manuscript, public data deposition, or GPU submission was sent.

At that historical checkpoint the default target built the CPU forensic release.
After the 2026-09-18 review it only verifies the existing bundle. The subsequently
selected F64A v1/v2 continuations are complete; stop GPU sampling at 15 ns.

## Historical stop condition and current exception

On 2026-09-14 the user explicitly approved retaining apo-2SH,
ending the current GPU campaign, and retiring C1 and C3. C4 is deferred and not claimed because
there will be no VUS prediction campaign. The validation gate, attempt-2 sampling test, and
G93A SS diagnostic are finished. The sole current exception is the explicitly authorized,
preregistered F64A folded continuation pilot above. It does not authorize an apo-SS campaign,
a broad rerun, or any VUS work; those still require a separate explicit decision.

Gate of record: **Pearson r = 0.326, RMSE = 2.123 kcal/mol, n = 7; failed on Pearson and
RMSE; pivot triggered.** F64A was the sole excluded point because closure 1.1038 exceeded
the pre-registered 1.0 per-variant cap. Preserve that verdict and exclusion.

Primary records:

- [`docs/gate_attempt_1.md`](docs/gate_attempt_1.md) — gate verdict.
- [`docs/stop_rule_reanalysis.md`](docs/stop_rule_reanalysis.md) — seven raw-window
  re-derivations plus A4V's attested run-time record.
- [`docs/gate_attempt_2_abandoned.md`](docs/gate_attempt_2_abandoned.md) — A4V 3→9 ns
  sampling test; precision improved ~5×, accuracy only 9%.
- [`docs/reference_state_audit.md`](docs/reference_state_audit.md) — primary-source audit.
- [`docs/reference_sensitivity_analysis.md`](docs/reference_sensitivity_analysis.md) —
  frozen-prediction CPU sensitivity and approved scope decision.
- [`docs/prereg_g93a_disulfide_diagnostic.md`](docs/prereg_g93a_disulfide_diagnostic.md) —
  completed negative SS test.

## Scientific state

### 1. The calculation result

The original seven-point comparison is reproduced at r = 0.326020 and RMSE = 2.123481.
Six points re-derive from archived NPZs. A4V's attempt-1 windows were overwritten by the
9 ns test, so its original point survives only in
`~/sod1fep_archive_2026-09-11/archive/A4V_3ns_ddg.json`. Do not replace it with the 9 ns A4V
result when quoting the gate.

The strongest convergence finding remains negative: within-ladder hysteresis does not order
independent-box disagreement in this archive. F64A folded r1 has hysteresis 0.0227 (rank
10/48, not the lowest) and the largest replicate disagreement, 1.2026 kcal/mol.

### 2. The benchmark result

All eight gate values trace to primary tables, but the benchmark is not state-homogeneous:

- all experiments are disulfide-intact (apo-SS); the simulation is apo-2SH;
- six controls are monomeric urea measurements at 25 °C on C6A/C111A/F50E/G51E;
- G93S/G93V are apo native-dimer DSC measurements on C6A/C111S at 49.4 °C, copied by Kumar
  into a column labeled apo-monomer;
- Kumar's uniform ±0.3 kcal/mol is a compilation-level methodological estimate, not the
  measurement uncertainty of each point.

Table 2 correction: its final paired G93S/G93V values are the constant-ΔCp and
temperature-dependent-ΔCp calculations at 49.4 °C, not the 49.4 °C and 25 °C ΔΔGs. Nominal
25 °C whole-dimer effects computed from the table's absolute ΔGs are G93S **2.0/1.4** and
G93V **5.1/4.2** kcal/mol (constant/temperature-dependent ΔCp), with roughly ±2.4 kcal/mol
uncertainty before any division by two.

### 3. Forensic sensitivity — not a gate

Holding the predictions, usable set, thresholds, and all other references fixed:

| scenario | Pearson r | RMSE (kcal/mol) |
|---|---:|---:|
| gate of record | **0.326** | **2.123** |
| halve G93S/G93V dimer totals only | 0.657 | 1.122 |
| move G93S/G93V to 25 °C only, constant ΔCp, still dimer | 0.539 | 1.401 |
| 25 °C + halve, constant ΔCp | 0.754 | 1.074 |
| 25 °C + halve, temperature-dependent ΔCp | 0.767 | 1.117 |

The combined nominal rows happen to cross the original numerical thresholds. They are
**post-verdict sensitivities, not passes**: the values are model-dependent, imprecise, and
still derived from a cooperative dimer transition. Dividing by two does not create an
isolated-monomer measurement.

### 4. G93A disulfide diagnostic

The pre-registered primary endpoint was folded ΔG(SS) − folded ΔG(2SH). Result:
**−0.0169 kcal/mol**, inside the pre-declared `|Δ| < 0.3` negligible band. The diagnostic
is converged and its physical topology was verified in all three independent folded systems.
It records a small observed effect under the tested protocol. It does not rule out slow
redox-dependent changes or establish equivalence, even for G93A; see the conditional
contrast interval in `docs/review/redox_uncertainty.json`.

## Reference-state scope

The scope decision approved by the user on 2026-09-14 is:

1. **Retain apo-2SH and stop GPU work.** It remains the biologically motivated state and the
   single SS diagnostic gives no basis for switching the campaign.
2. **Report the failed gate as a heterogeneous-benchmark result**, with the sensitivity
   analysis and negative SS test beside it. Do not claim the gate isolates force-field error.
3. **Require matched apo-2SH controls for any future predictive campaign.** Pre-register that
   benchmark before new predictions. If an adequate matched set cannot be assembled, a
   separate apo-SS campaign is the alternative and needs explicit user approval.

This decision retires C1 and C3. C4 is deferred and must not be claimed because C3 will not
produce VUS FEP inputs. C2 remains only as a methods-and-limitations result; the failed gate is
not successful predictive validation. The decision does not authorize changing v1 to apo-SS.

## Archive status

Verified locally on 2026-09-14:

- `~/sod1fep_archive_2026-09-14/G93A_SS_diagnostic/` contains `MANIFEST.md`, `ddg_SS.json`,
  `convergence_SS.json`, and 120 finite NPZs (60 per leg), all `(20, 3001)`, protocol
  `822108e9db71124d`, provenance `gromacs_pmx`.
- All three SS folded `hybrid.top` files contain the C57–C146 SG–SG bond, omit HG on C57/C146,
  and retain HG on C6/C111.
- `~/sod1fep_archive_2026-09-11/fep/G93A/` remains a complete, separate 120-window 2SH
  baseline. Its folded topologies have no SG–SG bond and retain HG on all four cysteines.
- The two trees share the same protocol hash, so the manifest and physical topology—not the
  hash—identify redox state.

**Live baseline verified remotely 2026-09-14.** The user confirmed 120 NPZs under live
`results/fep/G93A` and SHA-256
`ed830d0b5085113245f8c914437684b79cac624d8343c796839803bfb446a8b5` for all three folded
`hybrid.top` files. This matches the local 2SH archive (and differs from the SS topology hash
`9ce591304f918ac1fab989588d0f0b5d5768ded0cf71297dca4a1f480b17f7d8`), so the live baseline
restoration is closed.

**Second SS copy verified remotely 2026-09-14.** The user copied the live diagnostic to
`/projectnb/rise-batteries/bode/archive_2026-09-14/G93A_SS_diagnostic`, confirmed 120 NPZs and
the manifest, and obtained no output from `diff -qr` against the live tree. SCC archival
verification is complete. The first copy attempt from the login home failed before writing
anything because its relative source path did not exist; the successful copy was made from the
repository root.

## CPU-only reproduction

For the current portable package use `docs/release_reproduction.md`. Commands below reproduce
earlier outputs. Do not overwrite the historical manifest; a newly generated inventory uses
current source and cannot replace its historical checksum contract.

```bash
MPLCONFIGDIR=/tmp/sod1fep-mpl python -m src.analysis.reference_sensitivity \
  --archive-root ~/sod1fep_archive_2026-09-11 \
  --figure docs/figures/reference_sensitivity.png

MPLCONFIGDIR=/tmp/sod1fep-mpl python -m src.analysis.methods_figures \
  --attempt1-archive ~/sod1fep_archive_2026-09-11 \
  --reanalysis-convergence ~/sod1fep_archive_2026-09-11/reanalysis_2026-09-12/convergence \
  --ss-archive ~/sod1fep_archive_2026-09-14/G93A_SS_diagnostic \
  --output-dir docs/figures

python -m src.analysis.archive_manifest \
  --attempt1-archive ~/sod1fep_archive_2026-09-11 \
  --ss-archive ~/sod1fep_archive_2026-09-14/G93A_SS_diagnostic \
  --output /tmp/sod1fep-current-archive-manifest.json

python -m pytest tests/
```

The analysis reads A4V's original run-time record explicitly, applies the original convergence
filter once, and fails if F64A is no longer the sole exclusion. It never writes
`results/validation_gate.json` and cannot re-open the gate.

## Methods-and-limitations deliverable

Current assembly plan: [`docs/methods_limitations_outline.md`](docs/methods_limitations_outline.md).
The executable figures and archived-input contract are in
[`docs/methods_figure_package.md`](docs/methods_figure_package.md); the checksum inventory is
[`data/forensic_archive_manifest.json`](data/forensic_archive_manifest.json).
The minimum evidence package is:

1. failed gate scatter and frozen metrics;
2. convergence-diagnostic failure (48-record hysteresis vs independent-box disagreement);
3. A4V sampling sensitivity;
4. eight-point primary-source benchmark audit plus the reference sensitivity figure;
5. G93A negative disulfide test with topology evidence;
6. archive/protocol history and the A4V raw-window loss stated explicitly.

Table 3 and Figure 4 were independently reproduced through a clean-room standard-library
implementation that imports none of the production analysis modules. All eight rows agree at
displayed precision and all four plotted point sets agree. See
[`docs/independent_reference_reproduction.md`](docs/independent_reference_reproduction.md).
This is an independent implementation, not a second-human certification.

These SCC archive checks and the computational reproduction closed the earlier technical
scope. The subsequently authorized publication-review revision is described at the top of
this handoff. External human certification and a
polished manuscript are optional follow-up activities.

The LiveCoMS presubmission inquiry is **parked by user direction as of 2026-09-14**. Its draft
remains in [`docs/livecoms_inquiry.md`](docs/livecoms_inquiry.md) for provenance, but it is not
an active deliverable and must not be sent autonomously.

## Things not to do

- Do not submit A4V, finish gate attempt 2, rerun G93A SS, or run VUS FEP.
- Do not edit `data/variants.csv` to replace G93S/G93V gate references; keep the historical
  record and the forensic scenarios separate.
- Do not describe halved dimer values as monomer experiments.
- Do not merge `diag/g93a-ss`; main correctly retains `keep_disulfide_reduced: true`.
- Do not treat `converged: true`, cycle closure, or a protocol hash as physical-state proof.
- Do not claim “first,” “novel FEP protocol,” or “we show SOD1 variants are destabilizing.”
