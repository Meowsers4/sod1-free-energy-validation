# Sensitivity studies and evidence provenance

Supporting information for Diagnostic cancellation and benchmark mismatch in SOD1 folding free energy calculations.

# S1 Extending A4V folded sampling narrowed repeat spread but left the reference discrepancy

Attempt 2 extended the A4V folded leg from 3 to 9 ns of production and from 0.5 to 2 ns of
equilibration, reusing the unchanged unfolded leg (Fig S5). The folded ΔG range across three
independently solvated repeats fell from 1.46 to 0.27 kcal/mol, and the replicate ΔΔG range from
1.34 to 0.25 kcal/mol. ΔΔG moved from 3.54 ± 0.39 to 3.36 ± 0.08 kcal/mol, and its discrepancy
from the unmatched reference from +1.92 to +1.74 kcal/mol. Production length and equilibration
changed together, so this is a bundled protocol comparison, not an isolated duration effect.
Reduced spread is improved observed repeat precision, not demonstrated basin coverage, and the
result does not exclude effects of longer sampling or other starting conformations. Attempt 2
was stopped after A4V on cost and limited observed benefit; this is not evidence that further
sampling cannot help. The gate of record remains attempt 1.

# S2 The G93A disulfide contrast showed a small conditional shift

Physical inspection of all six folded topologies confirmed the intended redox states: the three
2SH topologies lack the SG–SG bond and retain both thiol hydrogens, and the three SS topologies
contain the bond and lack them. The folded ΔG(SS) − ΔG(2SH) was −0.016918 kcal/mol (standard
error 0.082; unpaired Welch 95% interval −0.297 to 0.263 kcal/mol, 2.68 degrees of freedom;
Fig S6), inside the pre-declared ±0.3 kcal/mol point-estimate band. The interval uses
between-run variation in both arms; matching replicate indices or seeds does not establish
pairing. It is conditional on the sampled basins, excludes force-field bias, unsampled modes
and experimental uncertainty, and is not an equivalence test. A small observed effect over 3 ns
does not rule out slower redox-dependent rearrangements, and this single contrast cannot
explain the gate residuals at other sites.

# S3 Gate chronology and analysis status

The gate thresholds appear in commit 23f057854762a8b8adb8f211a636c77c5fa06a3f, with author
and committer timestamp 2026-08-07T02:37:10-04:00. The configuration specifies Pearson r ≥ 0.70,
RMSE ≤ 1.5 kcal/mol, median hysteresis ≤ 0.75 kcal/mol, a 1.0 kcal/mol per-variant hysteresis
cap, at least six usable points and the r < 0.60 pivot. This commit is an ancestor of the
first gate-verdict record, commit 3a90c21d2d99d2f5fef8bf2a173bfc7547ecb66a, timestamp
2026-09-04T11:32:56-05:00. These are the timestamps recorded in Git, including their offsets.

This is evidence of internal prespecification in the retained repository history. Git timestamps
are not independent public registration timestamps. The threshold commit also contains an
inline request to confirm the RMSE threshold; its numeric value is 1.5 kcal/mol, the value
used in the gate. Protocol implementation changed during development. We therefore do not
claim that every simulation detail was fixed at threshold registration or that the campaign
was publicly preregistered.

The grouped archive audit, temporal quarter audit and reference-sensitivity scenarios were
post-verdict analyses. The F64A continuations used separately saved simulation and analysis
plans; those plans do not make the selected F64A path an unbiased validation cohort.
The later raw-energy and λ-comparator audits are exploratory descriptions. None changes
the gate verdict or supplies a new stopping threshold.

# S4 Data inventory and reproduction scope

The historical September 14 forensic release is retained unchanged. It contains 1,217
inventoried files and has SHA-256 09cc1b2c7575b60afa1af38216b78ca8f126a668b83aa6ef283c06ff8eba7114.
Its main archive contains 960 reduced-potential window files: 840 are retained attempt-1
windows from the seven variants other than A4V, and the 120 A4V windows are retained attempt-2
data. A4V attempt-1 folded windows were overwritten. Historical estimate and convergence
records preserve that gate point but cannot restore its raw folded data. A further 120
window files record the G93A disulfide-intact diagnostic. The six folded G93A topologies
permit the recorded redox identity checks.

The later evidence includes 60 F64A v2 window files with 15,001 records per file, carrying
cumulative reduced potentials through 15 ns, as well as the v1 and v2 analysis reports,
continuation plans, temporal reports, raw-energy audit and λ-comparator outputs. These
supplement the historical release and are not represented as contents of that older archive.
Saved report digests identify the exact inputs to the manuscript temporal figure.

The local deposit candidate includes a file-level SHA-256 inventory and a source snapshot
with the base Git commit and local revision status. It is a staging artifact, not a public
release or an independently certified dataset. Its reproduction instructions separate
historical energy analysis, saved-report figure assembly and continuation analyses under
their recorded software environments. A4V attempt-1 folded estimates and the exact original
gate software runtime remain the disclosed provenance limits. Reconstructing all original
simulations from structural trajectories is outside the available archive: those trajectories
were not retained.

**Fig S1. ** Historical net hysteresis against sibling disagreement for 24 folded ladders.

**Fig S2. ** Fixed λ-pair reduced-energy half-block drift on every v2 path against actual λ.

**Fig S3. ** Neighbor reduced-energy drift, slope and variability per window against actual λ.

**Fig S4. ** Directional adjacent overlap and adaptive-selection context against actual λ.

**Fig S5. A4V bundled sampling extension.** Left: folded ΔG of three independently solvated repeats at 3 ns and 9 ns folded production (bars, means; spread 1.46 and 0.27 kcal/mol). Right: replicate ΔΔG and mean ± reported uncertainty against the unmatched experimental reference (1.62 kcal/mol). Production and equilibration changed together.

**Fig S6. G93A disulfide contrast.** Replicate folded ΔG for 2SH and SS arms (diamonds, mean ± replicate SD) and the conditional unpaired Welch interval for SS − 2SH.

