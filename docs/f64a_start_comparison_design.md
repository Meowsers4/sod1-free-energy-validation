# F64A starting-conformation comparison — draft 2026-09-18

## Status and recommendation

**Planning only: not selected, not preregistered, not runnable and no submission.**
The user requested a bounded next design after the completed
[raw-energy audit](f64a_raw_energy_audit_results.md). The historical campaign still
stops at 15 ns. Mentor review remains deferred. Parameter proposals and unresolved
inputs are explicit in [the draft specification](f64a_start_comparison_draft.yaml);
do not modify the base configuration or completed pilot packages.

Recommend a **matched two-start comparison with the existing method**, rather than
changing both starting conformation and sampling algorithm. Question:
**at the same fresh-run duration and preparation protocol, how much do the observed
folded-leg estimate and its temporal movement depend on the initial protein coordinates?**
This tests starting-coordinate sensitivity, not a demonstrated mechanism or an
improvement in accuracy. Current evidence does not establish stable individual
repeats, so it is not the simple “stable repeats disagree” case. Starting sensitivity
is nevertheless a controllable next factor; this recommendation is a design choice,
not a conclusion that the audit identified conformational trapping.

Do not run only windows 17–19: the audit shows changes elsewhere, and local
discrepancies do not identify contributions to MBAR endpoint movement. Do not extend
the old paths to 21 ns or use them as a matched fresh-start control.

## Arms and control of confounding

| Arm | Protein coordinates | Method / model | Independent repeats | Retained duration |
| --- | --- | --- | ---: | ---: |
| A: reference | Provenance-matched original prepared WT start | Existing independent-window GROMACS+pmx, folded monomer apo-2SH | 3 | 6 ns/window |
| B: alternate | A justified, model-compatible alternative prepared WT start | Same as A | 3 | 6 ns/window |

Both arms are **fresh** WT→F64A hybrid systems, all 20 lambda states. The intentional
factor is starting protein coordinates. Same sequence/construct, mature numbering,
protonation choices, free-thiol Cys57/Cys146, no metals, force field, water, ions,
lambda schedule, timestep, thermostat/barostat, constraints, cutoffs and energy
cadence. Use the same preparation procedure in both arms and per-window lambda-aware
minimisation. Propose **2 ns fixed preparation + 6 ns retained production** per
window. Two ns is a bounded protocol choice, not proof of equilibration.

Preparation differs from the historical short-start protocol; therefore historical
v1/v2 fits are descriptive context, not experimental controls. Verify the original
prepared start rather than assume raw 3ECU chain A equals the structure actually used.
The existing builder defaults to chain A: it cannot silently create a chain-B arm
just because a different source filename is supplied. A future isolated package
must make chain selection explicit and test that it was honored.

Each repeat has independent velocity and solvation/ion seeds, frozen before execution.
Use the same randomisation rules across arms, comparable box construction and fixed
ion composition rules; record resulting atom/ion counts and box geometry. Avoid
arm-specific protonation/loop-rebuild choices. Analyze within each valid ladder;
do not concatenate ladders with different solvent counts/topologies. Repeats are
independent simulation realisations conditional on a start family, **not three
independent starting conformations**. Arm A/B repeats are not paired samples merely
because both are numbered r0–r2. Any arm difference remains conditional on these two
starts and includes finite-sampling/preparation variability.

## Alternate-start feasibility: not yet resolved

An original prepared WT **candidate** was located read-only in the local September
11 archive: `fep/F64A/inputs/wt_apo.pdb`. Its SHA-256 is
`394776d7388e79c8de7ecd46b96b16c1eaf3aaa3a7e4a4a1a2173db397bc6f29`, identical
to all three archived `folded/system_r{0,1,2}/wt.pdb` copies. Its local path/hash
are recorded in the draft YAML. This is useful archived-input agreement, not yet
a staged, admitted start or a cryptographic linkage to every v2 checkpoint.

Read-only local inspection of `data/structures/3ECU.pdb` found 153 observed residues
and matching residue names/Cα positions available in both chains A and B; C/D have
126/123 observed residues. A/B least-squares, proper-rotation Cα alignment over all
153 common residues gives RMSD **0.566258 Å**, median displacement **0.217890 Å**.
The maximum is **6.179676 Å at residue 1**; F64's Cα displacement is **0.464329 Å**.
Those are coordinate descriptors, not evidence of two slow basins. Chains C/D would
require substantial missing-loop reconstruction, adding another potential factor.
The file hash and reproducible measurement details are recorded below.
F64 χ1/χ2 are **166.224° / 46.475°** in A and **−175.151° / 41.890°** in B;
the χ1 difference wraps across ±180°. These small circular differences do not
establish different local rotamers or a meaningful alternate ensemble.

Do **not** automatically designate B as a scientifically informative alternate.
Before a GPU arm is selected:

- Recover/hash the actual original prepared WT start and inspect available SCC
  coordinate snapshots. NPZ energies alone cannot reconstruct a conformation.
- Identify candidate provenance, sequence, residue completeness and preparation
  compatibility; verify the F64 mutation site from `data/variants.csv`.
- Compare common heavy-atom/backbone coordinates and relevant torsions/contacts
  before and after identical preparation/minimisation. Require a reasoned structural
  distinction beyond a global RMSD dominated by terminal atoms. Freeze descriptors,
  atom mappings and chosen start hashes before production, without selecting on
  favorable ΔG or experimental agreement. No new numerical basin threshold is invented.
- If available candidates differ only trivially, or require incompatible rebuilding,
  report that this two-start test is not currently informative. Do not manufacture a
  “different basin,” choose a historical repeat based on its ΔG, or generate a new
  scouting MD ensemble without a separate bounded allocation and design.

An external alternate structure or snapshots from one old trajectory are possible
future sources, but neither has been selected. A snapshot from an alchemical window
must not be mistaken for an unmutated WT input; topology/atom mapping must be verified.
Starts from one trajectory are not independent evidence of equilibrium basin weights.

## Fixed prospective analysis proposal

Retained time zero follows the fixed preparation period. At 1 ps cadence, proposed
NPZs contain `(20, 6001)` energies; the boundary column zero is retained for integrity,
not duplicated in disjoint blocks. Raw retained slices are `[1:3001]` and
`[3001:6001]`, 3000 records each. Freeze export/time-grid details in the executable
registration and verify them in first light rather than reuse v2's absolute columns.

Primary policy is **zero additional trimming, with the existing correlation thinning**.
This avoids making adaptive removal the main definition of observed stability. Keep
fixed-25% and adaptive trim-and-thin as declared sensitivity analyses on the same data;
no policy is chosen afterward because it agrees with a desired result. Reuse the
established sampled-state/neighbor observables and larger-of g rule, recording all
g/count/cutoff decisions. Audit both neighbor differences on raw blocks/suffixes too.

Two descriptive endpoints under the primary policy:

1. **Starting-coordinate sensitivity:** final-block mean folded-leg ΔG(B) minus
   mean ΔG(A). Report all six repeat estimates, within-arm range/SEM, conditional
   MBAR errors and an unpaired propagated arm-difference uncertainty. The repeat
   SEM component is `sqrt(s_A²/3 + s_B²/3)`; the conditional MBAR component is
   `sqrt(sum(error_A²)/9 + sum(error_B²)/9)`. Report both and their larger value,
   without claiming it covers unsampled conformations or uncertainty over start families.
2. **Within-arm time dependence:** every repeat's final-minus-first block movement;
   within each arm report signed mean/SEM **and mean absolute movement** so opposite
   changes cannot cancel unnoticed. Do not infer absence of drift from a small signed mean.

Repeat both summaries under both sensitivity policies. Two arms × three repeats ×
two blocks × three policies = **36 declared MBAR fits**. Do not pool arms or policies
as independent corroborating data. Report net/sum-absolute/max-local hysteresis, full
overlap matrices, minimum adjacency overlap, cutoffs/g/selected counts/times, solver
notes and raw observable summaries. No selected fit or failed repeat is silently dropped.
An incomplete ladder blocks the complete comparison; retain failures and accounting.

No experimental target is optimized, no unfolded leg is added and no folding ΔΔG,
gate pass, structural mechanism, independent-sample significance claim or new
convergence pass threshold is introduced. Disjoint blocks can remain correlated.

## Proposed allocation and admission

120 production paths = two arms × three repeats × 20 states. Retained production
totals **720 ns**, fixed preparation **240 ns**, total **960 ns** excluding technical
first light. These are two new finite 6 ns retained arms, not permission to continue
the completed trajectories.

Propose one L40S/eight CPU slots per path and **eight concurrent tasks shared across
both arms**, not eight per arm. Alternate/balance queued arm labels to limit systematic
time/host confounding; record actual node placement. Proposed aggregate maximum:
**370 GPU-hours**, including all GPU preparation, first light, failed attempts and
resumes. Proposed task ceiling is **1.5 hours/attempt**, two attempts maximum.
Four technical first-light tasks (windows 0 and 17 in each arm), each capped at one
hour and two attempts, give a reservation bound:
`120 × 2 × 1.5 + 4 × 2 × 1 = 368 GPU-hours`. The remaining two hours are contingency
inside the 370-hour cap, not an additional scouting allocation. CPU preparation
also needs a separate bounded core-hour accounting line, not omission from SU costs.
Each first-light task covers its fresh preparation plus only 10 ps retained sampling;
any GPU preparation is included in that task's one-hour limit. Successful short
first light is a technical check, not a reliable forecast of production runtime.

These are **proposals, not user-approved budgets or forecasts**. Inspect complete
job 7620241 accounting, preparation cost, current quota/balance and actual applicable
charging before admission. Derive a runtime margin using measured peak task times,
explicitly allowing for fresh preparation; 6 ns checkpoint-extension timings alone
do not certify an 8 ns fresh task. If conservative measured timing does not fit the
ceiling, stop for redesign rather than silently enlarge it. No current capacity,
SU tariff or balance is assumed. SU/storage caps remain unresolved in the draft.
The earlier v2 rate waiver does not automatically carry forward to this proposal.

Keep energies, final coordinates, checkpoints and logs only; no trajectory retention
change or structural-mechanism endpoint. Estimate actual private build/staging/append
storage plus a 2× margin from audited file sizes, and reserve explicit quota headroom.
Never stage into historical directories or count filesystem-wide free space as quota.

## Integrity, implementation and interpretation

Only after start selection, resource approval and registration: implement an isolated
package and main-DAG rules for preparation, source validation, staging, technical
first light, guarded submission, output validation and CPU-only comparison. Include
clean committed code/config/environment/start hashes, distinct arm/start IDs,
protocol/topology identities and finite attempt/job ledgers. First light verifies
intended start/active lambda, GPU execution, full energy grid/shape, checkpoint resume
and metadata; window 17 is included for technical coverage, not a declared causal
bottleneck. Production uses fresh copies, not exploratory first-light outputs.
No protocol change while an array is queued/running. Never overwrite old evidence.

Interpret all declared results at the fixed 6 ns endpoint. Persistent temporal
movement in either arm keeps the comparison inconclusive about start-independent
free energy, even if final arm means agree. A persistent start-family difference
with less observed within-arm movement supports start sensitivity at this budget,
not verified equilibrium basin populations. Less drift and agreement across starts
supports improved observed reproducibility, not correctness or coverage. Stable
agreement still cannot separate shared trapping from model/reference mismatch.
No automatic extension follows any outcome.

A sampling-method arm is an alternative **separate design**, not a third arm added
to this test. For example, GROMACS documents lambda-Hamiltonian replica exchange
and its MPI requirement, but it would need a coupled-rank scheduler/build validation
and a changed job-granularity contract; it is not a switch on today's independent
one-window tasks. This draft does not implement or select it.
[Official GROMACS 2025.3 documentation](https://manual.gromacs.org/2025.3/reference-manual/algorithms/replica-exchange.html).

### Coordinate-inspection provenance

Local 3ECU source SHA-256:
`c8cc3ea0abe43ab03575b934327ed4dd9eee6e380651097b49d8f2bb665d50b3`.
Parsed ATOM records only,
using Cα entries with blank/A alternate-location labels; residue identity keyed by
PDB mature residue number. Center each chain's 153 Cα coordinates, fit a proper
rotation by SVD of the cross-product matrix with determinant correction, then
compute RMSD, median and maximum Euclidean displacement. F64 position came from
the F64A row of `data/variants.csv`, not a precursor offset hardcoded into code.
These read-only checks do not validate prepared starts, disulfide reduction,
protonation, or original simulation ancestry. No candidate coordinates were changed.
Torsions use N–Cα–Cβ–Cγ for χ1 and Cα–Cβ–Cγ–CD1 for χ2, with the signed atan2
of the projected bond vectors; angular differences must be treated circularly.
