# HANDOFF — SOD1 FEP pipeline

## Next SCC action: selected r3 CPU package static review — 2026-10-13

The user-run [isolated r3 source and software preflight](docs/f64a_c2_fresh_system_cpu_candidate.md)
passed with the pinned WT/config hashes, older ion placements, r3 seed
`2072077476`, pmx force field and host GROMACS 2025.3. No system was built.
The user-run static review of the separately sealed
[inactive CPU execution release](docs/f64a_c2_fresh_system_cpu_release_candidate.md)
also passed: exact manifest hash, source recheck, 24.75/50 GB project quota
use, 31 GB filesystem free, and a suitable CPU queue for eight slots and
one hour. Its execution guard remains false and no job was submitted.
Preserve that package and `review.log`. The user then selected one isolated
technical CPU build, capped at eight CPU-slot-hours with no GPU or retry.
A new [sealed selected package](docs/f64a_c2_fresh_system_cpu_selected_release.md)
passed user-run SCC package, source and queue review. The pasted excerpt omitted
the standalone manifest digest, but the subsequent exact-hash check returned
`SHA256SUMS: OK`. The user ran the guarded submission once: SGE validated a
suitable queue and returned **8032575**. The user-supplied `qacct` excerpt
reports `omp8`/8 slots, `failed 0`, **`exit_status 1`**, and one second of
wallclock. The saved job log identifies an unset `MODULEPATH`, failed module
and conda loads, then a syntax error from an old fallback Python. Neither
`prepared/` nor `prepared.incomplete/` exists; system construction never
began. See the [failure record](docs/f64a_c2_fresh_system_cpu_8032575_failure.md).
Preserve job and package evidence; do not resubmit or clear guards. The first
[inactive login-shell correction](docs/f64a_c2_fresh_system_cpu_login_candidate.md)
passed user-run SCC static review. Its final marker confirms package/source,
storage and queue checks; the pasted excerpt omits the standalone manifest
digest and `review_exit` line. A follow-up source review found that SGE's
`-S /bin/bash` may interpret that job script without applying its login
shebang. The new [explicit-login v2 candidate](docs/f64a_c2_fresh_system_cpu_explicit_login_candidate.md)
execs `/bin/bash -l` on a separate sealed body. It passed local checks and
user-run SCC static review: pinned source/seed, project storage and suitable
queue. The excerpt omitted standalone checksum and review-exit lines, but
included the review's final pass marker. It cannot submit a job.
The startup repair has not run on a compute node. The failed job consumed
its one selected attempt. The user then selected one corrected eight-slot,
one-hour CPU-only attempt. Its fresh
[sealed selected package](docs/f64a_c2_fresh_system_cpu_explicit_login_selected.md)
passed local checks and user-run SCC static review (`review_exit=0`, expected
final marker, pinned source/seed, project storage and suitable queue). The
pasted excerpt omitted `SHA256SUMS: OK`. The user ran the selected package's
guard once; it passed and SGE returned **8059683** after queue validation.
The separate exact-check output was not pasted. The user then supplied job
log and accounting: explicit login Bash, `MODULEPATH` and Python 3.11.15
passed; the build stopped at `gmx grompp -f ions.mdp` when the wrapper
rejected a warning. `prepared.incomplete/` exists, `prepared/` is absent,
and `qacct` reports `failed 0`, `exit_status 1`, 8 slots, 77 seconds.
The user supplied the exact warning text: pre-ion charge −5, one Ewald
net-charge warning, with `-maxwarn 2` in the historical `ions.mdp` command.
The fresh
[inactive ion-warning candidate](docs/f64a_c2_fresh_system_cpu_ion_warning_candidate.md)
allows only that one warning before `genion -neutral`. Its user-run SCC static
review passed with `review_exit=0`: old `command-07.json` returned 0, contained
one matching warning for charge −5, and had reported SHA-256
`e1ba44209ac4b849c5e731446a99fcf51624e22819284f9b174c55eedaee5418`.
The reviewer also reported 24.76/50 GB project quota use, 31 GB filesystem
free and a suitable CPU queue. The package's execution guard remains false;
no job was submitted. Preserve both failed job packages, output and guards.
A separate decision was made: the user selected one fresh technical CPU-only
attempt after this review. The new
[sealed selected package](docs/f64a_c2_fresh_system_cpu_ion_warning_selected.md)
pins the reviewed `command-07.json` SHA-256, the inactive candidate manifest,
the same WT/config and seed, eight CPU slots, a one-hour limit, no GPU and no
automatic retry. Local package review, all 25 file hashes, shell syntax and
focused guard tests passed. Its `SHA256SUMS` SHA-256 is
`836d869a293034fa275af079cba508e261b34cd0fd255ed02b21cebc48cf8316`.
The user must transfer it and run the SCC static review. No new job has been
submitted; the new submission guard requires the selected review marker.
The agent must not access SCC or infer production readiness.

## Read-only fresh-source preflight passed — 2026-10-06

The [local r3 source/seed plan](docs/f64a_c2_fresh_source_preflight.md)
pins the vetted prepared WT and historical config, reproduces r0–r2 ion
seeds, and derives a distinct r3 technical seed map. The user completed the
documented **read-only check in their SCC terminal**: remote WT/config hashes
and r0–r2 marker seeds matched, and no r3 paths were present. No system
build or job was submitted. The agent must not log in to SCC. The separate
candidate package and its remaining preflight are recorded above.

## C2 paired spread interval CPU calibration — 2026-10-05

The [inverse-Wishart candidate](docs/f64a_c2_paired_interval_wishart_development.md)
failed its frozen 33-pair, negative-correlation development case (89.5%
coverage versus 92% required); its held-out cohort was not run. A separately
frozen [Bonferroni marginal-normal bound](docs/f64a_c2_paired_interval_bonferroni_result.md)
passed all eight complete/MCAR development and held-out coverage screens,
but produced very broad spread intervals: mean widths 2.31–2.91 at 10
attempted pairs and 1.04–1.19 at 33, against a constructed true contrast
of −0.25. Its guarantee requires normal independent realizations within
each arm; protein normality and useful precision remain unestablished. No
final spread method, pair count, production duration or allocation is
selected. Next work is local scientific design and stronger uncertainty
calibration; no SCC transfer is currently required.

## C2 fixture metadata reviewed locally — 2026-10-05

The user transferred ten JSON files from accepted job 7865574. The local
archive and post-accounting manifest hashes matched the SCC values. The
[independent metadata result](docs/f64a_c2_fixture_metadata_result.md)
checks the preserved 1608-entry original seal inside the 1611-entry final
seal, all 20 common-to-both-arms checkpoint hashes, three phase summaries,
exchange permutation history, and successful accounting. The large binaries
were not transferred or rehashed locally. This closes the technical metadata
review; no repeat transfer or GPU job is needed. Production uncertainty,
spread inference, pair count and allocation remain unselected. Continue with
local CPU method calibration and production design. Do not access SCC as the
agent; the user handles any later transfer from their own terminals.

## Stage P full-ladder parser gate closed locally — 2026-10-04

The user transferred a 22-file subset of accepted job 7791102. SCC and local
tarball/manifest SHA-256 values matched. The [full-ladder CPU result](docs/f64a_c2_stage_p_full_ladder_result.md)
rehashed all 21 copied attempt files against the 614-entry saved manifest,
validated all 20 4-ps XVGs, and compared every reduced-energy matrix with
alchemlyb 2.4.1. Parser differences were within a declared roundoff-scale
absolute/relative allowance. Early, late and full 20-state MBAR numerical
fits were finite and agreed between parsers to at most `4.04e-12` kT in the
endpoint. Those four-ps fits are technical outputs; the conditional errors,
long-correlation joint variance, spread interval and production schema remain
unqualified. Some remote-lambda energies reached about `1.32e15` kT; finite
fit behavior does not establish their physical origin. No agent SCC access or
new GPU job occurred.

## C2 BCa spread candidate stopped after development — 2026-10-04

The [separately frozen BCa candidate](docs/f64a_c2_paired_interval_bca_development.md)
had only 83.5–85.9% late-spread coverage in the four 10-pair development
scenarios, below the 92% screen. Its reserved held-out cohort was **not run**.
No spread interval or final pair count is selected. No SCC access occurred.

## C2 paired interval CPU screen — 2026-10-03

The [frozen synthetic paired-interval test](docs/f64a_c2_paired_interval_stress_result.md)
found adequate diagnostic coverage for a paired Student-t mean absolute-
movement interval in all complete/MCAR cases at 10 and 33 attempted pairs.
The paired percentile bootstrap for the late-SD contrast failed the frozen
92% screen at 10 pairs and for negative pair correlation at 33 pairs.
Availability and missing arms are reported separately. These are constructed
normal-model checks, not selected C2 pair counts or protein results. A new
spread interval candidate is needed; no SCC access or GPU work occurred.

## C2 synthetic walker-lineage CPU stress — 2026-10-03

The [second joint-variance stress](docs/f64a_c2_walker_stress_result.md)
used 20 tracked exchangeable walkers, 256 early and 256 late observations,
and synchronized stationary-bootstrap rows. At the frozen mean block length
96, IID and moderate (`phi=0.9`) walker correlation passed their held-out
screens, but long correlation (`phi=0.98`) failed (26/32 zero coverage,
estimated/empirical variance ratio 0.47). Swaps were coordinate-independent,
so this is not physical HREX. `Q`, its covariance bounds and production
uncertainty remain unqualified. Continue locally with paired movement/spread
interval calibration and exact input-schema work. No SCC access or GPU job
occurred.

## C2 joint-variance CPU stress failed under correlation — 2026-10-03

The [frozen joint stationary-bootstrap diagnostic](docs/f64a_c2_joint_bootstrap_stress_result.md)
resampled complete synchronized 20-state time rows across early and late blocks.
Its 32-seed held-out IID case passed the predeclared screen (29/32 zero coverage,
variance ratio 0.89), but the correlated cases failed: `phi=0.9` covered
25/32 with variance ratio 0.39; `phi=0.98` covered 18/32 with ratio 0.27.
The drifting series was a predeclared failure probe. These are synthetic
MBAR tests without actual HREX walkers or protein data. Joint `Var(D)`,
`Q`, its covariance bounds and production uncertainty are **not qualified**.
The next local research step is a separately frozen candidate with longer
trajectories, block-length sensitivity and walker-history handling; no SCC
access, GPU job or C2 production allocation follows. The agent did not access SCC.

## C2 held-out CPU uncertainty stress — 2026-10-03

The [frozen 20-state constructed stress study](docs/f64a_c2_uncertainty_stress_result.md)
ran locally with 4 development and 32 held-out seeds in each of an IID and a
synchronized serially correlated regime. In the correlated held-out case,
per-state thinning admitted 24/32 runs; nominal-95% conditional MBAR block
intervals covered the known zero endpoint in only 5/24 early and 7/24 late
fits. The naive zero-covariance noise correction averaged +0.583 kT² in
this stationary complete-case set. Treat that as a diagnostic failure of
this simple thinning/error approach, **not** an HREX protein outcome.
`Q`, its covariance bounds and production uncertainty remain unqualified.
The independent XVG comparison **passed on the supplied Stage P excerpt**:
temporary local alchemlyb 2.4.1 returned 21 records and 20 columns, with
maximum row-centered difference `2.7817e-11 kT`. The complete sealed
multi-state protein output remains unavailable locally. No SCC access or
GPU work occurred.

## C2 CPU analysis contract and pure validation core — 2026-10-03

The [candidate analysis contract](docs/f64a_c2_analysis_contract_candidate.md)
specifies paired early/late movement, the noise-adjusted squared-movement
sensitivity, covariance bounds, complete-pair denominators and synthetic
qualification gates. The pure
[CPU core](src/analysis/f64a_c2_analysis_core.py) validates a complete
sampled-state ladder, ordered lambda labels, finite all-state reduced
potentials and fixed even time grids, then computes covariance-sensitivity
bounds. Eleven focused tests pass. These arithmetic/input checks do not
parse or hash GROMACS files, estimate MBAR free energies, calibrate
correlation-aware standard errors or validate HREX cross-state dependence.
The next local step added a read-only
[GROMACS XVG/manifest adapter](src/analysis/f64a_c2_gromacs_inputs.py).
It accepts the actual user-supplied Stage P legend layout, checks state,
temperature, all foreign-lambda labels, finite rows and branch-relative
times, and verifies a pinned JSON manifest and every named file. Its
[portable tests](tests/test_f64a_c2_gromacs_inputs.py) use the 4-ps
state-0 excerpt plus synthetic manifest tampering. A separate conversion
helper maps the same-temperature foreign energy differences to kT units;
a constructed two-state PyMBAR test confirms row-centering invariance.
The independent alchemlyb parser comparison now passes on the supplied
state-0 excerpt. A complete sealed-ladder comparison, the full production
provenance schema and held-out joint uncertainty calibration remain next.
No SCC access or GPU job occurred; production remains unselected.

## C2 post-fixture production design review — 2026-10-03

The [post-fixture CPU-only review](docs/f64a_c2_post_fixture_production_design.md)
records the now-qualified shared-checkpoint branch and the remaining
scientific registration decisions. A local read-only audit linked the archived
prepared WT to all three archived `wt.pdb` copies and matched the r0
`conf.gro`, `em.gro` and `hybrid.top` hashes to the user-supplied SCC source
inventory. All repeats share the same prepared protein and initial water
template; their ion-placement seeds, `ions.gro` and minimized `em.gro`
files differ. That is distinct ion placement within one protein-start
family, not evidence of distinct protein conformations. The 0.5–1.0
kcal/mol useful-effect range, common preparation length, finite retained
durations, spread precision, repeat count, full cost/storage caps and
analysis/failure rules remain to be fixed before any production selection.
The review includes explicitly unselected cost/storage stress cases. No
SCC access or further GPU job occurred.

**Correction after review:** The archived 18-window `wt_apo.pdb` has a
different hash from the current 20-window source. The archived r0–r2
minimized protein heavy-atom RMSDs are 0.214–0.228 Å without fitting.
The earlier 6/17 repeat figures came from an unpaired half-width formula;
under zero pair covariance, paired half-width planning needs 7/18 pairs,
while exact two-sided paired-t 80%-power planning needs 10/33 pairs under
the same idealized SD. The review now names block-estimator noise,
requires block SE reporting, and proposes a noise-adjusted squared-movement
sensitivity. Storage stress cases include shared common-phase XTC and
use the newer 26.04-GB pre-fixture quota headroom. No scientific threshold,
sample size or production allocation has been selected.

## C2 live checkpoint-branch fixture 7865574 accepted — 2026-10-03

The user supplied the saved common/baseline/HREX phase summaries after
successful one-time accounting. The [bounded technical result](docs/f64a_c2_branch_fixture_result.md)
is accepted: all 20 checkpoints and output grids reached their planned
steps; HREX made 29 attempts and 23 accepts across three rounds, attempting
all 19 neighboring links with a consistent final permutation. Common and
branch-input seals contain 330/361 entries; the accounting call verified
the 1608-entry output manifest, and 1611 entries were registered after
accounting. `qacct` reports `failed=0`, `exit_status=0`, 306 seconds on
one L40S (0.085 allocated GPU-hours, 1.36 CPU-slot-hours). Preserve all
package, attempt, log and manifest evidence. Do not rerun accounting or
submission. This technical fixture does not select production, establish
ΔG/ΔΔG convergence or reopen the historical failed validation gate and
15-ns F64A stop. No further GPU job is selected. The agent did not
access SCC.

The dated entries below retain earlier pending states for provenance;
this accepted result is the current status.

## C2 live branch fixture 7865574 accounting pass — 2026-10-03

The user ran the post-job accounting command. The first invocation
exited 0 and reported `C2_BRANCH_FIXTURE_ACCOUNTING_REVIEW_PASS
job_id=7865574 gpu_hours=0.085000`; its code verifies the saved
output-hash manifest before recording qacct. A second invocation
failed at the expected `accounting already recorded` guard, before
writing attempt files. Do not run accounting again. The saved
[job record](docs/f64a_c2_branch_fixture_job_7865574.md) has the next
**read-only** concise phase-review command. Check common/baseline/HREX
checkpoint, grid, exchange, seal and hash summaries before final technical
acceptance. No new GPU job is selected. The agent did not access SCC.

## C2 live branch fixture 7865574 provisional runtime pass — 2026-10-03

The user supplied the [job 7865574](docs/f64a_c2_branch_fixture_job_7865574.md)
runtime status and scheduler accounting. The wrapper reports
`pass_pending_accounting_and_review`, no failure, all three phases
finished, matching 20-client MPS and cleanup for each, and a passing
no-exchange-common branch-input checker. Peak recorded persistent/scratch
bytes were 524,885,081/142,801,721. `qacct` on scc-504 reports
`failed=0`, `exit_status=0`, l40s/omp16/16 and 306 seconds (0.085
allocated GPU-hours, 1.36 requested slot-hours). This is a provisional
technical pass, not final acceptance: run the selected package's separate
`runtime.py accounting` and inspect saved common/baseline/HREX reviews,
seals and output hashes. Do not rerun submission. The agent did not
access SCC.

## C2 live branch fixture job 7865574 submitted — 2026-10-03

The user supplied the full selected-release SCC transcript. Remote
`SHA256SUMS` SHA-256 matched local
`a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`;
package and source reviews passed. `SUBMIT_ON_SCC.sh` exited 0 after its
one-job guard and suitable-queue check, returning **7865574**. Preserve
the selected package and [attempt record](docs/f64a_c2_branch_fixture_job_7865574.md).
No runtime `status.json`, job log or `qacct` has yet been supplied, so
technical and accounting status remain pending. Next ask the user for the
read-only outputs in the attempt record; do not repeat submission, clear
guards or request another job. The agent did not access SCC.

## C2 live branch fixture selected SCC review accepted — 2026-10-03

The user supplied `review_exit=0` for the selected 21-entry release on
`scc-i01`, with all 20 matching initial TPR hashes and
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=True; no job submitted`. Accept the static review;
the standalone remote manifest digest appeared in the subsequent full
transcript and matched the local seal. The user has already selected this
one bounded technical job and reported 15,000 SUs. Submission has since
succeeded as job 7865574; see the newer entry above. The agent did not
access SCC.

## C2 live branch fixture selected release — 2026-10-03

In response to the exact one-job selection question, the user replied
“continue. SU balance is 15k, which is more than enough.” The
[selection record](docs/f64a_c2_branch_fixture_selection.md) treats
15,000 SUs as user reported; the agent has not independently verified the
balance or SU charge rate. This selects one bounded technical job only:
one L40S, omp16/16 slots, 20 ranks, 30 minutes, 0.5 allocated GPU-hour
and 8 requested CPU-slot-hours maximum, no retry or production.
The [21-entry selected release](docs/f64a_c2_branch_fixture_selected_release.md)
is sealed locally at a fresh path with `SHA256SUMS` SHA-256
`a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`.
It binds to the SCC-reviewed inactive release and its v2 runtime. Local
manifest, shell, guard/provenance and 25 focused tests pass. The
user-run static SCC review passed, as recorded above; the guarded
one-attempt submission was subsequently completed as job 7865574; see
the latest entry above. The agent did not access SCC.

## C2 live branch fixture inactive release review — 2026-10-03

The user supplied `review_exit=0` and the
`C2_BRANCH_FIXTURE_EXECUTION_RELEASE_REVIEW_PASS` marker for the inactive
17-entry release candidate, with all 20 initial TPR hashes and no job
submitted. Accept its SCC static review; preserve the package and log.
The standalone remote `SHA256SUMS` digest was not in the pasted excerpt,
although manifest entry verification passed. The
[concrete one-job selection scope](docs/f64a_c2_branch_fixture_selection.md)
is ready: at most 0.5 allocated GPU-hours/8 requested CPU-slot-hours,
one L40S/omp16/16-slot/20-rank/30-minute attempt, no retry or production.
At that review point, current SU balance and rate were unknown and the
paired-scout waiver did not apply. The user subsequently reported a
15,000-SU balance and selected this fixture; see the newer entry above.
The agent did not access SCC.

## C2 live branch fixture inactive execution release — 2026-10-03

At the user's request, a [17-entry inactive execution release candidate](docs/f64a_c2_branch_fixture_execution_release_candidate.md)
was prepared locally from the SCC-reviewed v2 runtime. Its `SHA256SUMS`
SHA-256 is
`951d9f722fe693935fb3c7d2788bc4d503125e3dae6746551d854dbf5896268f`.
It includes the exact one-L40S/omp16/16-slot/20-rank/30-minute SGE request
and a guarded submission wrapper. `execution_authorized=false` and the
permit path stops before any attempt, submission directory or `qsub`.
Local manifest, shell, provenance/guard and 22 targeted tests pass. The
ceiling is 0.5 allocated GPU-hours and 8 requested CPU-slot-hours; actual
SCC SU rate and current balance remain unknown and unwaived for this
fixture. The subsequent user-run static SCC review passed, as recorded
above. Do not run `SUBMIT_ON_SCC.sh` or submit a job from this
candidate. No preflight or v2 review rerun is needed. The agent did not
access SCC.

## C2 live branch fixture v2 static review — 2026-10-03

The user supplied the SCC static review pass for inactive runtime candidate
v1: all 20 initial TPR hashes matched and
`C2_BRANCH_FIXTURE_RUNTIME_CANDIDATE_REVIEW_PASS` reported
`execution_authorized=False; no job submitted`. Accept this as static
source/image compatibility, preserving v1 and the preflight record. Local
independent review found copied older helper modules with callable job
routines outside the fixture guard. A new
[inactive helper-only v2 package](docs/f64a_c2_branch_fixture_runtime_candidate.md)
is sealed locally with `SHA256SUMS` SHA-256
`27e712a4dfc1e43d8e1d1eb3a8544224d86be95b4e758a33a27f327eb5de92d3`.
Local manifest, storage-stop, inactive-entry and 19 checker/MPS tests pass.
The user supplied v2's SCC review pass marker and the tail of the state
hash list through state 19. The standalone manifest-hash and shell-exit lines were
not in the excerpt and have been requested from the existing output; do
not rerun preflight or v2 review solely for them. The next step is a
separately reviewed executable release candidate and cost/SU decision,
without selecting a job yet. The fixture remains unselected,
the SU balance is unknown and unwaived for it, and production is not
authorized. The agent did not access SCC.

## C2 live branch fixture runtime candidate — 2026-10-01

The user supplied `preflight_exit=0` for the sealed preflight package,
20 matching initial TPR hashes, exact 30-minute queue eligibility and
`C2_BRANCH_FIXTURE_PREFLIGHT_PASS_PENDING_SELECTION`. `preflight.json`
reports 26,040,000,000 bytes of `/project` quota headroom and
33,327,939,584 filesystem-free bytes at 2026-10-02 02:05:39 UTC.
Accept the preflight; preserve it, no rerun. It does not waive unknown
SU balance or select execution. A
[12-file inactive runtime candidate](docs/f64a_c2_branch_fixture_runtime_candidate.md)
is prepared locally with manifest SHA-256
`fcf880535ba54aae1e0efc779fd8907b7d49ae549b81519a894afcbdb30ccd3b`.
It contains no job script, and `job`/`probe` fail at the false-authorization
guard before GPU effects. The package guide has user-run SCC transfer and
static review commands. The v1 SCC review and independent runtime-code
review have since completed, with corrected v2 awaiting its own SCC
review; no new common checkpoints, branch TPRs or GPU job exist.
The agent did not access SCC.

## C2 live branch fixture preflight package — 2026-10-01

The user supplied a fresh SCC storage snapshot: `/project/rise-batteries`
23.96/50 GB used with 206,368 files, `/projectnb/rise-batteries`
46.32/50 GB used, 32G filesystem free on `/project`, and `/project`
writable. A [sealed, non-submitting preflight package](docs/f64a_c2_branch_fixture_preflight_package.md)
is prepared locally, with `SHA256SUMS` SHA-256
`66ecf45d671fca74909d897ae356dec3bd515197dfbcf0851225744773e3389e`.
It verifies the 344-file Stage P **initial-input** source, exact r6 image,
20 state TPR/MDP identities and atom order; `qsub -w v` checks only the
candidate one-L40S/omp16/16-slot/30-minute request. It checks fresh
quota/write access and records `preflight.json`. It has no job script,
GPU/MPI launch or `mdrun`; it cannot branch until a new no-exchange
common run exists. The subsequent user-run SCC preflight passed, as
recorded above; do not repeat it. The earlier unknown-SU waiver applied only to the
completed paired scouts. The agent did not access SCC.

## C2 live checkpoint-branch fixture design — 2026-09-30

The user asked to design the next bounded live fan-out test after the
accepted CPU rehearsal. The new
[design candidate](docs/f64a_c2_branch_fixture_design.md) and
[machine-readable schedule](docs/f64a_c2_branch_fixture_candidate_v1.yaml)
specify one 30-minute, one-L40S/20-rank/omp16 technical attempt with a
new no-exchange common phase ending at step 1,100. Its sealed 20
checkpoints would feed isolated baseline (2,000 more steps, no exchange)
and HREX (1,500 more steps, replex 500) phases sequentially; HREX should
exchange at steps 1,500/2,000/2,500. The design requires 40 changed-MDP
TPRs, the existing CPU input checker on the *new* checkpoints, output and
permutation validation, private-MPS cleanup, hashes and qacct. Persistent
outputs belong under `/project`. This is design only: no executable
release, queue check, new SCC inputs, GPU attempt, production duration or
SU-balance waiver is selected. Next implement/review a non-submitting
runtime candidate and collect fresh SCC admission evidence; explicit
fixture selection is separate. The agent did not access SCC.

## C2 Stage P checkpoint CPU rehearsal package — 2026-09-30

The user asked to start the CPU rehearsal and again directed the agent
not to access SCC. A local, non-submitting
[rehearsal package](docs/f64a_c2_branch_cpu_rehearsal_package.md)
now collects exact-r6 `grompp -t`/`gmx dump` evidence from copies of the
accepted Stage P job 7791102 checkpoints and runs the 20-state branch
input checker. Its 1,000/500-step arm targets are technical only; Stage P
had exchange and cannot stand in for the selected no-exchange common
preparation. Local mock collection and targeted checks passed. The user
subsequently ran CPU preparation on SCC and pasted the package review,
20 checkpoint SHA-256 lines, the expected 363-entry prepared manifest
count and `C2_STAGE_P_CHECKPOINT_CPU_REHEARSAL_PREPARED` marker. The
separate `REVIEW_PREPARED.sh` then returned `review_exit=0` and the
363-entry review pass marker. The package manifest SHA matches the local
sealed `f6a935f5...`, and the prepared manifest SHA is
`2ed9a0f0166bf0db6a1962a8a854a4e978f4a08d85d11abe1e1efbbb14375a04`.
**Accept the CPU rehearsal** for exact-r6 preprocessing and checker
mechanics; preserve the 363-file tree and logs, no rerun. Stage P's
exchange-enabled checkpoints do not qualify the selected no-exchange
common preparation or live fan-out. Next: design/select a bounded live
branch fixture, then package and submit it separately if selected.
The agent did not access SCC; no GPU execution occurred for this rehearsal.

## C2 branch CPU input checker implemented — 2026-09-30

At the user's request, the [CPU-only branch input checker](docs/f64a_c2_branch_input_checker.md)
is implemented locally, including a small transferable package. It
reviews saved common/arm checkpoint hashes and dumps, 40 TPRs and their
effective MDPs, grompp exit/log/argv evidence, step/time/part/lambda
identity, exact-r6 image hash, output strides, and all arm MDP differences.
It rejects missing source checkpoints, old arm outputs, velocity
regeneration, and unregistered arm physics. Seven synthetic tests pass.
It is read-only and contains no scheduler or GROMACS execution command.
Its archived Stage P mechanics rehearsal passed as noted above. No
common no-exchange preparation checkpoints or scientifically selected
branch inputs exist yet. Next is a bounded fan-out fixture design, with
actual selected-ancestry input generation after common preparation. The
agent did not access SCC.

## C2 checkpoint branch static review — 2026-09-30

The user selected shared no-exchange preparation followed by two isolated
retained arms. The [checkpoint-branch review](docs/f64a_c2_checkpoint_branch_review.md)
compares that design with the accepted Stage P and C2 scout code and the
GROMACS 2025.3 continuation interface. Stage P proved same-tree append; the
scouts proved fresh starts. Neither qualifies fan-out from one checkpoint
set. The review specifies sealed 20-state checkpoint ancestry, hash-verified
copies, distinct `-cpi`/`-cpo`, `-noappend` output isolation, effective
arm-TPR comparison, step/time and exchange validation, and common-cost
accounting. GROMACS may start afresh when `-cpi` is missing, so the wrapper
must fail before launch. No dynamic fixture was run, and no new GPU job or
production protocol is selected. Next: implement/review the CPU-only input
checks, then seek a separately selected bounded fan-out fixture.

## C2 scientific windows and fresh-start ancestry draft — 2026-09-30

The user asked to continue the next design decisions. A new CPU-only
[decision draft](docs/f64a_c2_design_decisions_2026-09-30.md) defines the
equal-cost method-plus-exposure estimand and a common-duration secondary
analysis. For a candidate 1-ps retained energy grid it excludes the
preparation-boundary `t=0` record, then uses equal disjoint early/late
record counts on each arm's own duration. It proposes one vetted prepared
WT F64A apo-2SH protein-start family, new per-realization systems/seeds,
file-level solvent/ion ancestry checks, and paired baseline/HREX branches;
claims remain conditional on that one protein family. It corrects the
arm-definition draft's byte-identical-TPR assumption: equal-cost target
steps may differ, so require identical starts and directly compare
effective physical/output fields instead. The user chose a **common
no-exchange preparation followed by an isolated baseline/HREX checkpoint
branch** as the design contrast; separate arm-specific equilibration
remains a sensitivity only. The candidate 2-ns preparation length and
short-scout rate ratio give illustrative HREX durations, but the exact
duration, branch mechanics, realization count, production protocol and
GPU budget remain unselected. Next is a CPU-only branch input/restart
contract and read-only archived ancestry/cost review.

## C2 post-scout CPU resource/precision sensitivity — 2026-09-30

The [precision/resource draft](docs/f64a_c2_precision_resource_draft.md)
now incorporates both accepted 100-ps scout rates. Dynamics-only rates
are 0.552168 baseline and 0.241447 HREX ns/state per allocated GPU-hour;
their ratio is 0.43727. A deliberately mechanical equal-cost table crosses
the existing 3/5/8-repeat, 8/16/32-ns baseline probes with that ratio,
½×/1×/2× common rate stress cases and the existing nominal precision
scenario. It separates dynamics-only cost from fresh-start preparation,
failures, billed SU and storage. The equal-cost comparison would use
different physical-time windows if the observed ratio persisted; a common
duration comparison is a separate secondary estimand. Observed persistent
scout peaks total 241,435,027 bytes across both arms, but one 100-ps
point cannot establish a production storage slope. The user supplied the
read-only by-extension summary: current attempt trees contain 111,244,910
and 130,525,018 bytes; XTC totaled 16,859,860 bytes across 120
state-frames. The draft now gives XTC-only stress projections of 1.96,
6.49 and 20.73 GB for its A/B/C equal-cost probes, with substantial
other storage excluded. The user chose **0.5–1.0 kcal/mol** as a
scientifically useful movement-reduction sensitivity range, not a single
registered effect target; the idealized half-width table now shows both
bounds. No production duration, repeat count, budget or GPU job is selected.

## C2 paired 100-ps technical scout accepted — 2026-09-30

The user ran the selected HREX wrapper on `scc-i01` after baseline 7796136
was accepted. Package/source reviews and the HREX gate passed; the wrapper
reverified the baseline's 365-file post-accounting inventory. Exact
two-hour L40S/`omp16` queue verification found suitable queues, `qsub
-terse` returned **7799011**, and `hrex_submit_exit=0`. See
`docs/f64a_c2_scout_hrex_result.md`. A first `qstat -j` check found it
running; the later user-supplied status and job log report a technical pass,
20 MPS clients observed and cleanup confirmed, 1491.007 s dynamics and
1530.295 s wrapper wall time. `qacct` reports `l40s` on scc-510,
`omp16`/16 slots, `failed=0`, `exit_status=0`, and 1540 s wall time
(0.427778 allocated GPU-hours). The user then supplied the one-time
accounting review's conditional summary: `reviewed=true`, 385-file
post-accounting inventory, all 20 checkpoints at step 50,000/100 ps,
101 energy records and three XTC frames per state, 20 performance records,
and 99 common exchange rounds with 941 attempts and 629 accepts across
all 19 neighboring links. The per-link counts sum correctly and the final
walker vector is a permutation. Accept the HREX technical result and the
paired scout. HREX measured 233.77 setup-inclusive and 241.45
dynamics-only ps/allocated-GPU-hour, versus baseline 519.48 and 552.17;
for the same 100 ps/state, HREX used 2.22 times the allocated GPU time.
The pair used 0.620278 allocated GPU-hours and 9.924444 requested
CPU-slot-hours; billed SU remains unknown. Preserve both attempts and
scratch; do not resubmit or clear one-attempt guards. Next is CPU-only
resource/precision design, not a production launch. No production arm
is authorized.

## C2 baseline 7796136 accepted; HREX gate open — 2026-09-30

The user supplied the single selected baseline job's `status.json`, job-log
tail and `qacct` output. See `docs/f64a_c2_scout_baseline_result.md`.
`technical_status=pass_pending_accounting_and_review`, `failure=null`, all
20 MPS clients observed and cleanup confirmed. Wrapper wall time was
689.950 s (651.975 s dynamics); observed persistent/scratch maxima were
111,144,766/142,742,154 bytes. `qacct -j 7796136` reports `l40s` on
scc-513, `omp16`/16 slots, `failed=0`, `exit_status=0`, 693 s walltime
(0.1925 allocated GPU-hours and 3.08 requested CPU-slot-hours). Actual
SU remains unknown. The user then ran the selected package's one-time
`runtime.py accounting baseline` checker: pass marker with exit 0, original
output hashes reverified, and a 365-file post-accounting inventory. The
compact review shows all 20 checkpoints at 50,000 steps/100 ps, 101 energy
records and three XTC frames per state, 20 performance records, zero
exchange activity, and an identity state-to-walker mapping. The reviewed
accounting record confirms 0.1925 GPU-hours and 3.08 requested slot-hours,
with 519.48 ps/allocated-GPU-hour setup-inclusive and 552.17 ps/GPU-hour
dynamics-only. Accept this one technical baseline for the registered
conditional HREX gate. The selected HREX submission wrapper subsequently
reverified the 365-file inventory for job 7799011 above. Preserve all
baseline outputs, private scratch and the one-attempt guard; do not
resubmit baseline. These timings do not validate C2 production or FEP
convergence.

## C2 scout baseline submitted as 7796136 — 2026-09-30

The user replied “proceed with balance unknown” to the exact one-baseline,
conditional-one-HREX, 100-ps technical scout pair (maximum 4 allocated
GPU-hours and 64 requested CPU-slot-hours). The selection and SU uncertainty
are recorded in `docs/f64a_c2_scout_execution_selection.md` and its JSON.
A new, separate selected release was sealed locally at
`packages/f64a-c2-scout-execution-selected-20260929-v1`; see
`docs/f64a_c2_scout_execution_selected_release.md`. Its 20-entry manifest
SHA-256 is `a4d353e5571beaae97fbbeddb413796fa10d0a97894018e2ba9d25f0f539a587`.
`execution_authorized=True` applies only to the registered two technical
arms, baseline first; production remains false. Local package/shell review
and 19 targeted tests passed, including the later actual-format DHDL
regression. The user transferred v1; remote manifest SHA
matches and both package/SCC reviews passed with
`execution_authorized=True; no job submitted`. All 20 accepted Stage P state
logs matched the runner's GPU/performance/completion patterns. The state-0
quick probe for literal `energy to <lambda>` legends returned zero because
actual GROMACS writes `\xD\f{}H \xl\f{} to <lambda>`. The unmodified
selected validator accepted the user-pasted Stage P XVG: all 20 foreign
lambda labels, 23 legends and 21 finite rows on the 0–4 ps/0.2-ps grid.
An actual-format regression test passed. The parser hold is resolved and
selected v1 needs no change. The user subsequently ran its guarded baseline
wrapper on `scc-i01`: package/source and arm checks passed, exact queue
verification found suitable queues, `qsub -terse` returned **7796136**, and
`baseline_submit_exit=0`. This proves submission only; no execution result
has yet been supplied. Monitor this one job, preserve
`submission-baseline/` and any attempt files, and do not resubmit baseline.
HREX requires baseline technical and qacct review and cannot launch
automatically. Preserve v1 and inactive v3 unchanged.

## C2 inactive execution candidate reviewed before selection — 2026-09-29

After the user-supplied preflight found a suitable two-hour L40S queue and
ample `/project` quota/free space, a new reviewable execution candidate was
sealed locally as `packages/f64a-c2-scout-execution-release-candidate-20260929-v3`.
See `docs/f64a_c2_scout_execution_release_candidate.md`. Its 20-entry
manifest SHA-256 is `abb0439e1f39c210edd8cd5f3c3eedd66688a433052f6027629fffef2705861e`.
It contains exact baseline/HREX SGE and guarded submission scripts, but
`execution_authorized=False` and no arms are selected. Local package/shell
checks and inactive permit rejection passed. The user transferred v3 and
supplied `scc-i01` output: remote manifest SHA-256 matches, all 20 package
files passed both reviews, and
`C2_SCOUT_EXECUTION_RELEASE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`. Accept this read-only review;
do not rerun it. The current SU balance remains unavailable because
`acctool` is missing on `scc-i01`. The exact bounded scout and subsequent
selection are in `docs/f64a_c2_scout_execution_selection.md`. The new selected
release is recorded above. Preserve the inactive package and do not edit
its contract or bypass its guard.

## C2 execution preflight packaged, pending fresh SCC evidence — 2026-09-29

The user requested the next step after the guarded GPU runtime candidate's
SCC review. A separate non-submitting preflight package is locally sealed at
`packages/f64a-c2-scout-execution-preflight-20260929-v1`; see
`docs/f64a_c2_scout_execution_preflight.md`. Its three-entry manifest SHA-256
is `8251a19e93c6941d5f1720ce3c8ff07f746a7be8abd70c7858b109b81959bd29`.
It validated the exact one-L40S, `omp16`/16-slot, two-hour request with
`qsub -w v` only; the user-supplied SCC output reports a suitable queue,
`/project` 23.63/50 GB quota usage, 32G filesystem free and write access.
The `acctool` query failed with exit 127 (`command not found`), as in an
earlier GPU preflight. See the result section in the linked document. The SU
tariff and current balance remain unverified. No baseline or HREX scout arm
has been submitted.

## Guarded C2 paired scout GPU runtime candidate reviewed on SCC — 2026-09-29

At the user's request, the baseline/HREX timing-scout runner and
output/accounting validators were implemented locally and sealed as
`packages/f64a-c2-scout-gpu-runtime-candidate-20260929-v4`. See
`docs/f64a_c2_scout_gpu_runtime_candidate.md`. The 13-entry package manifest
SHA-256 is `71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df`.
It reuses the accepted 381-entry CPU import and exact r6 SIF, pins 20 TPR
hashes, separates baseline and HREX attempts, enforces proposed time/storage
caps, and checks MPS, energy/coordinate/exchange output and qacct. Local
package review and 15 targeted tests passed. A user-supplied read-only Stage P
`gmx check` probe returned exit 0, 38,414 atoms and 11 complete frames at
0.4 ps; its first invocation failed because the probe lacked a private `/tmp`
bind, then a corrected invocation passed. The user transferred v4 to
`/project/rise-batteries/bode/container-build-packages/` and supplied
`scc-i01` review output: remote manifest SHA-256 matches the local value,
all 13 package files passed `sha256sum -c`, and
`C2_SCOUT_GPU_RUNTIME_CANDIDATE_REVIEW_PASS states=20
execution_authorized=False; no job submitted`. Accept the remote read-only
review. The candidate contract has `execution_authorized=False` and no
submission script; `job`/`rank`/`probe` are guarded. No GPU scout has run.
Next: a separately sealed selected release with an exact queue check,
current quota and SU review, and explicit GPU-attempt selection before
submission. Do not rerun the accepted v1 CPU import.

## C2 scout runtime candidate CPU import accepted — 2026-09-29

User-supplied `scc-i01` output shows v1 transfer manifest SHA-256
`8d8919e005da81b44e8dbd973a5935eda406f4e23c9c1f8b3d8abd59f4a288af`
matching the local sealed candidate, package review pass, one-time import pass,
and separate imported-tree review pass for all 20 states and 381 source
manifest entries. The review explicitly reports `execution_authorized=False`.
Accept the CPU import on this evidence; preserve it and do not rerun import.
See `docs/f64a_c2_scout_runtime_candidate.md`. No GPU job was submitted.
The guarded GPU runtime candidate and its SCC review are recorded above;
GPU selection remains separate.

## C2 scout runtime candidate CPU review package — 2026-09-29

At the user's request to start the second design step, a non-submitting
runtime-contract and CPU-import candidate was created locally at
`packages/f64a-c2-scout-runtime-cpu-20260929-v1`. See
`docs/f64a_c2_scout_runtime_candidate.md`. Its 9-entry package manifest SHA-256
is `8d8919e005da81b44e8dbd973a5935eda406f4e23c9c1f8b3d8abd59f4a288af`.
It pins the accepted 381-entry prepared manifest and 20 TPR hashes, separate
baseline/HREX launch plans, one-L40S/omp16 bounds, and CPU-only import/review.
Local package review, deliberate job-mode rejection, and three targeted tests
passed. No SCC import has been reported and the agent did not log into SCC.
The package has no qsub, SGE job script, or GPU execution path; a new runtime
revision must implement and validate live resource monitoring, MPS launch,
outputs and accounting before any scout selection. No GPU job is authorized.

## C2 paired timing-scout CPU inputs accepted — 2026-09-29

The user completed SCC v3 CPU preparation and separate review for
`f64a-c2-scout-cpu-20260929-v3`: 20 exact-r6 scout TPR hashes,
`prepared_manifest_entries=381`, pass marker
`F64A_C2_PAIRED_SCOUT_CPU_REVIEW_PASS states=20 manifest_entries=381
execution_authorized=False`, and `review_exit=0`. Prepared manifest SHA-256:
`cffefe198d66e670ebc7db2960039e2cfc159e64bb238af7d5c3fe13c7f64487`.
See `docs/f64a_c2_scout_cpu_result.md` for all hashes and limitations.
The sealed reviewer checks byte-identical baseline/HREX TPR copies. Accept
CPU input scope on the supplied evidence; preserve v1/v2 failures and v3,
and do not rerun CPU preparation. No GPU job ran, no scientific C2 arm is
selected, and the agent did not log into SCC. Next: a separate non-submitting
runtime candidate with bounded one-GPU launch and full output/accounting
validation, followed by independent review and explicit scout selection.

## C2 scout CPU v3 sealed after documented default-group correction — 2026-09-29

The user supplied v2 state-0 `mdout.mdp` values: all reported 100-ps,
1-ps energy/dHdl, 10-ps log, 50-ps compressed-coordinate, lambda and
zero-TRR fields matched; `compressed-x-grps` alone was blank. GROMACS 2025.3
defines that blank/default value as whole-system output. V2's literal
`System` comparison caused its halt after successful state-0 `grompp`.
The new local package `packages/f64a-c2-scout-cpu-20260929-v3` accepts blank
default or explicit System, rejects a smaller coordinate group, and reports
specific field mismatches. Its source spec is unchanged. Manifest SHA-256:
`b5d4888989cb60914d7643cda459e8de176cc54fc7aea46aba36867e3e8e9783`.
Seven combined targeted tests and local package review passed before transfer.
The subsequently accepted SCC v3 preparation/review is recorded above.
Preserve failed v1/v2 packages and logs; no GPU job has run. See
`docs/f64a_c2_scout_cpu_package.md`.

## C2 scout CPU v2 grompp passed, effective-MDP check halted — 2026-09-29

The user's SCC v2 CPU preparation printed
`CPU_ONLY_PACKAGE_VERIFIED; no job submitted`, then halted at state 0 in
`effective_checks` after `grompp` returned successfully and wrote
`mdout.mdp`. No 20-state TPR set was sealed and no GPU job ran. Preserve the
remote v2 package and logs; do not rerun it in place. A read-only report of
state-0 `mdout.mdp` fields was subsequently supplied and reviewed as recorded
above. The validator compared the literal `compressed-x-grps` value to
`System`; the actual blank value is the documented whole-system default.

## C2 scout CPU v1 include failure confirmed; v2 local correction — 2026-09-29

The user's SCC CPU preparation of
`/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-cpu-20260929-v1`
halted at `grompp` state 0 with `ValueError: grompp failed/warned at state 0`.
It did not seal 20 TPRs or submit/run GPU work. Preserve the failed remote
package and logs; do not rerun in place. The user then supplied state-0
`grompp.log`: its fatal error is `Topology include file
"amber99sb-star-ildn-mut.ff/forcefield.itp" not found`. The CUDA-aware MPI
warning and two GROMACS notes were incidental. V1 omitted
`SINGULARITYENV_GMXLIB` in its clean container environment, whereas the
accepted Stage P builder set it. This confirms the missing include cause.
The locally sealed v2 at `packages/f64a-c2-scout-cpu-20260929-v2` restores
that variable; package manifest SHA-256 is
`2deabb3533a5d6eed07406302386c10a767dbd47466e26fc8b2069e46b5c88d2`.
The v1→v2 builder diff is only this environment pass-through. Targeted tests
and local package review passed. V2 was subsequently transferred and reached
successful state-0 `grompp`, then halted at its validator as recorded above.

## C2 paired timing-scout CPU package prepared locally — 2026-09-29

At the user's request, a sealed, transferable CPU-only candidate is in
`packages/f64a-c2-scout-cpu-20260929-v1`; see
`docs/f64a_c2_scout_cpu_package.md`. Manifest SHA-256 is
`85575f749cf1605a984db6d0506dcc903fb087d3d924ffe0e1f7e778912afa1f`.
It checks the accepted 344-entry Stage P CPU source manifest, original r0
MDPs/starts, exact-r6 image and 20-state lambda vector; only timing/output
MDP fields change. On SCC its CPU-only builder will `grompp` 20 common TPRs
and copy them byte-identically into baseline/HREX trees. Local 20-state mock
rehearsal and four targeted tests passed at the time. This is the historical
initial package record; its SCC failure and the later versions are recorded
above. No agent SCC login, GPU job, runtime package or C2 production has
occurred. Preserve each failed package for inspection.

## C2 output and paired timing-scout design draft — 2026-09-29

At the user's request, `docs/f64a_c2_output_timing_scout_draft.md` now
proposes full-system XTC every 50 ps and all-state dH/dlambda/EDR every 1 ps,
with 10-ps logs and compact checkpoint evidence. These are candidate output
settings, not selected production settings. Stage P's 0.4-ps coordinate
stride would produce order-of-100-GB trajectories for a hypothetical 16-ns
ladder. At the candidate 50-ps stride, a rough Stage-P-frame-size screen
gives 9.0–10.2 GB of XTC alone for ten 16-ns ladders, and 28.7–32.8 GB
for sixteen 32-ns ladders. The latter exceeds current `/project` quota
headroom before other files. The draft also defines a *not yet selected*
two-arm technical rate scout: identical r0 inputs, 100 ps/state per arm,
one L40S/omp16/20 ranks, at most one 2-hour job and 1-GiB retained attempt
per arm. Its maximum proposed allocation is 4 GPU-hours and 64 CPU-slot-hours.
No package, submission or C2 production is authorized; fresh rate, byte,
SU and structural-resolution measurements remain prerequisites.

## Post-Stage-P storage snapshot supplied — 2026-09-29

User `pquota` on `scc-i01` reports 46.32/50 GB used on
`/projectnb/rise-batteries` (3.68 decimal GB remaining) and 23.23/50 GB
on `/project/rise-batteries` (26.77 GB remaining). `df -h` reports 8.7 GiB
filesystem free on `/projectnb`; project quota is tighter. The Stage P runtime
package totals `541M` by `du -sh`; separate measurements give `480M` for
`attempt/` and `61M` for `prepared/` (rounded MiB display values).
Read-only file inventory: 615 attempt files, 501,704,465 logical bytes;
40 checkpoint text dumps account for 231,039,436 bytes (46.1%), and 40
compressed trajectories for 47,842,536 bytes (9.5%). The 614-file hash
list excludes its subsequently written `output-hashes.json`. Stage P's
full first-phase archive and validation dumps make its footprint unsuitable
for a simple per-ns production projection.
Official SCC guidance describes identical performance for `/project` and
`/projectnb`, with `/project` backed up for harder-to-regenerate files.
The user confirmed `/project/rise-batteries` is writable on `scc-i01` and
`df -h` shows 32 GiB filesystem free there; its 26.77-decimal-GB quota
headroom is tighter. Use that allowance for curated future C2 evidence only
after a concrete storage budget and compute-node access check. Preserve
Stage P and historical evidence; no deletion or C2 GPU job has been selected.
See `docs/f64a_c2_precision_resource_draft.md`.

## C2 precision/resource sensitivity draft — 2026-09-29

At the user's request, `docs/f64a_c2_precision_resource_draft.md` now
recalculates the old three-repeat F64A late-block movement and spread SDs,
shows illustrative mean-contrast and dispersion precision for 3/5/8 fresh
ladders per arm, and gives equal-cost formulas plus 8/16/32 ns rate
sensitivities. None of these probes is selected. Stage P 4-ps timing is
setup-dominated, and the older one-window 36-GPU-hour estimate is a different
layout; neither measures C2 baseline/HREX steady rates. Actual billed SU,
current quota/bytes, production output cadence, useful-effect target and
finite duration/repeats remain unresolved. No C2 GPU work is authorized.

## C2 arm definition draft begun — 2026-09-29

At the user's request, step 1 of the post-Stage-P plan is drafted in
`docs/f64a_c2_arm_definition_draft.md`. It defines fresh paired-input F64A
folded apo-2SH independent-window and neighbor-HREX arms on the same 20-state
ladder, exact r6 build and candidate one-L40S multisimulation layout. The
intended runtime difference is exchange disabled versus enabled; both arms
have identical initial per-state TPRs within each realization and the same
MBAR/energy and retention rules. Stage P and historical pilot trajectories
remain outside the C2 comparison. Start ancestry, production interval/length,
output cadence, measured cost, repeat count and analysis details still need
registration. This is planning only; no C2 GPU work or production is selected.

## Stage P accepted; F64A protein technical qualification complete — 2026-09-29

Job **7791102** passed the selected short F64A folded apo-2SH protein
qualification on user-supplied evidence. See
`docs/gromacs_protein_runtime_result.md`. The read-only SCC evidence check
reconstructed all 19 alternating exchange rounds and walker permutations:
181 neighbor attempts, 113 accepted swaps, all 19 links covered. All 20
checkpoints advanced 1000/2 ps/part 1 → 2000/4 ps/part 2 with correct state
indices; first-phase data was preserved and the boundary unique. Both 20-rank
sets matched their 20 MPS clients on the same server/GPU. All rank records
matched the 16-CPU mask, and 614 saved file hashes verified. Scheduler
accounting: scc-504, l40s, omp16/16, `failed 0`, `exit_status 0`, 146 s.
Billed SU and peak GPU memory were not supplied. Preserve the attempt and
accounting; **no rerun is needed**. This completes Stage P technical scope,
not production validation, convergence or a free-energy result. No C2 or
other GPU sampling arm is selected. The agent did not log into SCC or download
the raw outputs.

## Stage P provisional report before accepted review — 2026-09-29

The user supplied `submission-P/job.log`, `attempt/status.json`, and `qacct`
for the single authorized F64A folded apo-2SH protein technical job. The
wrapper reports `pass_pending_review_and_accounting`, `failure: null`,
20 MPI ranks on 16 CPU slots, 20 MPS clients observed in both launches,
restart verified, and MPS cleanup confirmed. Its elapsed time is 141.026 s
(0.039174 observed allocated GPU-hour). Scratch was retained at
`/scratch/gmx-smoke-P-7791102.fsx6uj_5`.

Scheduler accounting is now available: `l40s` on `scc-504.scc.bu.edu`,
`omp16`/16 slots, `failed 0`, `exit_status 0`, 146 s wallclock, from
19:02:29 to 19:04:55 on September 29. Scheduler wallclock corresponds to
about 0.0406 allocated GPU-hour; billed SU was not supplied. The scheduler's
`maxvmem` of 120.739G is virtual memory, not GPU memory. `qstat` no longer
finding the completed job is expected. At this point the technical pass was
provisional; the subsequent saved-evidence review is accepted above. Do not
rerun, clear guards, or submit production/C2. The agent has not logged into
SCC or downloaded the remote binary outputs.

## One bounded protein technical GPU job submitted as 7791102 (historical submission record) — 2026-09-29

After accepted SCC CPU import, package review and suitable-queue validation,
the user ran the guarded `SUBMIT_ON_SCC.sh` for
`f64a-protein-technical-runtime-20260928-v1`. It reprinted the package review
marker and suitable-queue result, returned job ID **7791102**, and confirmed
one bounded protein technical job submitted. This is the user's explicit
selection of the registered one-attempt Stage P technical arm under
`CLAUDE.md` rule 6. Package manifest SHA-256 remains
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`.
The request is one L40S, `omp16`/16 slots, 20 MPI ranks/private MPS, 30-minute
hard walltime, 2,000 steps with synchronized 1,000-step restart, one attempt,
no automatic retry. Results and accounting were subsequently reviewed and
accepted above. Do not rerun the submit/import scripts or clear guards.
Production and C2 remain unselected.

## Protein runtime package and queue review (before submission) — 2026-09-29

The user ran the Stage P runtime candidate's CPU-only SCC importer on
`scc-i01`. It returned `import_exit=0`, hashes for states 0–19 identical to
the accepted short TPRs, and
`PROTEIN_TPRS_IMPORTED_AND_REVIEWED_CPU_ONLY; no job submitted`. The importer
checks the 344-entry source manifest, source spec/SIF identities, common GRO
atom labels/order and exact-r6 TPR dump fields before sealing the runtime
`prepared/` copy. The subsequent user output shows runtime package
`SHA256SUMS` SHA-256
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`,
`REVIEW_ON_SCC.sh` marker `PACKAGE_AND_PREPARED_INPUTS_VERIFIED` with exit 0,
and saved `queue-validation.iXRbyNjL.log` containing
`verification: found suitable queue(s)`. CPU import and package/queue review
are accepted on supplied evidence; preserve all files and do not repeat them.
The exact candidate is one L40S, `omp16`/16 slots, 20 ranks, 2,000 steps
(4 ps) with synchronized 1,000-step restart, 30-minute hard walltime, one
attempt, 2 GiB storage cap and no automatic retry. This is at most 0.5
allocated GPU-hour and 8 CPU-slot-hours. Under CLAUDE.md rule 6, a new MD arm
needed explicit selection/preregistration before submission. The user later
selected and submitted the sealed one-attempt Stage P arm as recorded above.

## Stage P short-input CPU preparation accepted — 2026-09-28

The user transferred the Stage P builder and spec to SCC with the expected
SHA-256 values (`bebb3fc721db97895191e6ed53c589126a0e2ac6c9433433add804868bf90987`
and `155a24a60191334c0c06a3e02d3c21ecf51cea0902f5ebe5e53370b3c6c322cf`).
On `scc-i01`, the CPU-only exact-r6 preparation reported short TPR hashes for
all 20 states and the final marker
`F64A_PROTEIN_SHORT_TPRS_CPU_PREPARED_PENDING_REVIEW`. The user then reported
`PREPARED.json` with 20 states, 20 total GROMACS notes, 21.712 seconds builder
elapsed, source inventory SHA-256
`c908e1c1695e0ebe8bd02dce2fece5bdbc83332d617528ca81495bd826c51fe2`,
the expected spec and SIF hashes, and both execution and production authorization
false. The user then reported `sha256sum -c SHA256SUMS` exit status **0** for
**344** entries; manifest SHA-256
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
The sealed CPU inputs are accepted on the supplied evidence. See
`docs/gromacs_protein_technical_inputs_result.md` for all 20 short TPR hashes
and limits. Preserve the package and logs; no rerun. No protein GPU run has
been submitted or authorized. Next: build a separate protein-specific runtime
qualification package and validators, estimate resource/storage needs, then
seek separate one-attempt GPU admission.
User-supplied read-only sizing: `prepared/` 89 MB, 20 TPRs 28 MB, and each
`grompp.log` estimates 5 Mb of run output (roughly 100 MB total). `df -h`
reported 9.3 GB available on `/projectnb`; project quota was checked next.
No protein runtime or GPU-memory measurement exists yet.
Subsequent `pquota rise-batteries` reported 50 GB quota, 45.79 GB use and
465632/1638400 files on `/projectnb/rise-batteries`; about 4.21 decimal GB
quota remained at that snapshot. The runtime candidate now requires 3 GiB free
at admission and still caps output at 2 GiB. Recheck on the allocated host.
An unapproved protein runtime package candidate now exists locally at
`results/gpu_smoke_packages/f64a-protein-technical-runtime-20260928-v1`.
Its manifest SHA-256 is
`5da65443e739c9540834596306ced78182fef5f0048726d26504021fd1df2a00`.
See `docs/gromacs_protein_runtime_design.md`,
`docs/gromacs_protein_runtime_package.md` and
`docs/gromacs_protein_runtime_local_validation.md`. It proposes the proven
one-L40S/omp16/20-rank private-MPS layout, a 30-minute scheduler ceiling and
2 GiB storage cap, with a 3 GiB free-quota admission guard. Protein-specific
checks allow zero accepted swaps while requiring complete attempts/permutations;
the restart copy removes the toy-only post-restart acceptance threshold.
Ten targeted local tests passed, including mocked 20-state CPU import and
zero-acceptance restart. Next: transfer candidate to SCC, validate queue and
import/review the exact Stage P TPRs on CPU. The package has a sealed submit
script for later explicit one-attempt review; **do not run it yet**. No protein
job was submitted.

## Protein C1 CPU compatibility complete; short-input preparation followed — 2026-09-28

The user ran the F64A folded apo-2SH r0 source inventory, chemistry/include
check and exact-r6 visibility check on `scc-i01`; all passed on supplied output.
The no-`-maxwarn` r6 CPU `grompp` state-0 probe and guarded states-1–19 sweep
each reproduced the historical TPR SHA-256, with no reported GROMACS WARNING.
The first sweep paste failed before preparation because `set -u` preceded SCC
environment sourcing; the corrected sweep passed. Preserve both attempts, the
inventory JSON, logs and TPRs; no rerun. See
`docs/gromacs_protein_source_inventory_result.md` for provenance and limits.
The agent has not downloaded or independently rehashed the remote binaries.

A separate CPU-only short-input candidate was prepared locally:
`docs/gromacs_protein_technical_inputs_v1.yaml`,
`src/analysis/gromacs_protein_technical_inputs.py`, and
`docs/gromacs_protein_technical_inputs_package.md`. It snapshots the source
and pmx force field, changes only registered short-run timing/output MDP keys,
performs 20 exact-r6 no-`-maxwarn` `grompp` calls, and seals its results.
Local candidate validation and two targeted MDP tests passed. It was
subsequently transferred, run and integrity-checked on SCC as recorded above.
There is no scheduler script, protein GPU allocation, or C2 production arm.
Agent SSH authentication was rejected; the user operates SCC from their
authenticated terminal.

## Stage L accepted; full 20-state ladder and accounting reviewed — 2026-09-28

Job **7763284** passed the selected synthetic larger-ladder qualification on the
user-supplied evidence. See `docs/gromacs_gpu_ladder_result.md`. Preserved transcript:
`docs/review/gromacs_ladder_7763284_user_transcript.txt`, SHA-256
`ae0590d27c186c35c78a4db71d359b3d0dec711c794db4e9e744dc50d8a1c35a`.

Independently checked all 20 checkpoint transitions 1000/1 ps/part 1 →
2000/2 ps/part 2; all correct state indices. Reconstructed all 19 exchange-round
permutations and 181 accepted neighbor swaps, covering all 19 links; step 1000
occurs once and 95 swaps occur in the resumed phase including that boundary.
Two distinct 20-rank PID sets match their MPS client sets on the same server/GPU.
CPU record selects 16 IDs from the inherited 32-ID mask. Runtime reports finite
complete outputs, preserved earlier rows/archive hashes, unique boundary and
MPS cleanup; raw binaries/rank files were not independently downloaded.

qacct: scc-503, l40s, omp16/16, failed 0, exit_status 0, 52 seconds wallclock,
132 seconds queued. Billed SU not supplied. Wrapper elapsed 48.212 seconds is
separate. Accepted scope: 20-state toy, 20 MPI ranks explicitly oversubscribed
on 16 CPU slots, one L40S/private MPS, graceful restart in one allocation.
A/R/L are complete; no rerun is needed. Preserve failed v2 job 7763245 separately.
Original four-GPU Stage B, protein qualification, performance and scientific
convergence remain outside this result. No next GPU simulation is selected.

## Stage L job 7763284 reports technical pass; review/accounting pending — 2026-09-28

User supplied v3 submission-L/job.log status: pass_pending_review_and_accounting,
stage L, production_authorized false, job_id 7763284, failure null,
allocated_cpu_slots 16, mpi_ranks 20, cpu_oversubscribed true,
restart_verified true, larger_ladder_verified true, mps_cleanup_confirmed true,
mps_expected_clients 20, mps_all_clients_observed true. Wrapper elapsed
48.21217385798809 seconds; derived allocation GPU-hours 0.013392270516107804
are not billed SU or scheduler wallclock. Retained scratch:
/scratch/gmx-smoke-L-7763284.cvq4nam4.

This is the runtime-reported full-ladder pass, pending detailed evidence review
and qacct. Do not rerun or remove guards. Request attempt/ladder-review.json,
restart-review.json, permutations.json, cpu-affinity.json and qacct -j 7763284.
Restart review includes both 20-client MPS overlap records. Review checkpoint
transitions, complete exchange schedule/link coverage/permutations, CPU mask,
client PID mapping and scheduler exit status before recording accepted status.
Raw remote files have not been independently downloaded. No further GPU stage
or protein simulation is selected by this provisional technical result.

## Corrected Stage L v3 submitted as 7763284 — 2026-09-28

User supplied verified package/prepared inputs, suitable-queue validation,
job ID **7763284**, and the bounded Stage L submission confirmation.
Package gmx-gpu-ladder-20260928-v3-pe-omp16; manifest
4faa2d6c66a896d21420fb4c08cd8520870d4a6f9be02d5cbc4742a5f5ae28a8.
One L40S, explicit omp16/16 slots, 20 oversubscribed MPI ranks sharing the
verified 16-CPU mask, full 20-state toy, normal stop at 1000 then append to 2000,
one fresh attempt, twenty-minute maximum. Submitted by the user; the agent has
not submitted remotely. Queued/running/completed state and results are unknown.
Monitor 7763284 and v3 submission-L/job.log; do not repeat submission/import or
remove guards. Retain status, ladder/restart reviews, permutations, affinity,
both MPS overlap records, first-phase archives, output hashes and final qacct.
Failed v2 job 7763245 and its four-second accounting remain separate evidence.

## Stage L v3 import verified; v2 accounting closed — 2026-09-28

User supplied successful v3 resource validation, verified existing-TPR import,
and package/prepared-input verification. Do not repeat preparation. The sealed
v3 manifest still matches 4faa2d6c66a896d21420fb4c08cd8520870d4a6f9be02d5cbc4742a5f5ae28a8.
Allocation.json directly confirms PE=omp16, NSLOTS=16 for failed v2 job 7763245.
qacct: scc-502, omp16/16, failed 0, exit_status 1, four seconds wallclock,
107 seconds queued. No dynamics started; billed SU not supplied. This closes
accounting for the failed wrapper attempt, not a technical pass.

The corrected v3 submission command is now supplied for the ongoing bounded
qualification: bash SUBMIT_ON_SCC.sh from gmx-gpu-ladder-20260928-v3-pe-omp16.
Requests omp16/16, one L40S, 20 ranks, twenty minutes, one fresh attempt. All
checks remain strict and it creates a new submission guard. No v3 job ID or
execution result yet reported; agent has not submitted remotely. Preserve v2
and its logs, never clear guards or reuse the failed attempt.

## Stage L v2 failed on PE name; v3 import candidate prepared — 2026-09-28

User qstat reports effective PE **omp16**, range 16, for job 7763245. V2 requested
omp/16 and its exact-name allocation guard requires omp, producing wrong PE/slots.
Trace shows failure before CPU-affinity setup, MPS or MPI/GPU dynamics. Runtime
wall_seconds=2.5483192420215346; qacct is pending. See
`docs/gromacs_ladder_7763245_failure.md`. Preserve v2 attempt and submission guards;
this is a consumed failed allocated attempt, not a validation-only failure.

Prepared `gmx-gpu-ladder-20260928-v3-pe-omp16`; manifest SHA-256
`4faa2d6c66a896d21420fb4c08cd8520870d4a6f9be02d5cbc4742a5f5ae28a8`. Spec: docs/gromacs_gpu_ladder_pe_omp16_v3.yaml;
commands: docs/gromacs_gpu_ladder_pe_omp16_package.md. It explicitly requests and
requires **omp16/16**. All other settings and bounds match v2. All 20 fixture
inputs are byte-identical. Import the already verified v2 prepared TPRs with
source-manifest, file, fixture, state-vector and SIF checks plus ancestry; no
grompp, container rebuild, old-attempt copy or dynamics needed for preparation.
No runtime allocation guard was loosened; exact PE/slot/single-host checks remain.

Full suite **421 passed, one skipped in 51.65 seconds**, including CPU restart
rehearsals, actual-reported-PE regression test, and valid/tampered full-ladder
imports including state19. Captured output:
`docs/review/gromacs_ladder_pe_omp16_20260928_pytest.txt`. Fresh-cache Snakemake
validation/packaging each one gpu=0 job; sealed checksums verified and v2 unchanged.
No remote v3 preparation, validation or submission yet reported. User next actions:
transfer v3, run VALIDATE_QUEUE_ON_SCC.sh / PREPARE_ON_SCC.sh / REVIEW_ON_SCC.sh,
return output plus qacct -j 7763245 and old attempt/allocation.json. These actions
do not submit. A further bounded GPU attempt must be selected after review;
never rerun v2 or silently reset its attempt allowance.

## Stage L v2 submitted as 7763245 — 2026-09-28

User supplied PACKAGE_AND_PREPARED_INPUTS_VERIFIED, successful resource validation,
job ID **7763245**, and "One bounded Stage L job submitted; retain this job ID."
Package: gmx-gpu-ladder-20260928-v2-omp16. One L40S, omp/16 slots, 20 explicitly
oversubscribed MPI ranks with a shared 16-CPU affinity mask; full 20-state toy,
normal stop at 1000 and append to 2000; one attempt, 20 minutes maximum.
Submission was performed by the user, not the agent. Queued/running/completed
state and GPU results are not yet supplied. Do not repeat preparation/submission
or clear guards. Monitor qstat -j 7763245 and package submission-L/job.log.
After completion collect attempt/status.json, ladder-review.json,
restart-review.json, permutations.json, CPU-affinity and both MPS overlap records,
plus qacct -j 7763245. Preserve all first-phase archives and output hashes.

## Stage L v2 SCC inputs verified; submission command supplied — 2026-09-28

User supplied successful exact-request scheduler validation, INPUTS_PREPARED at
`/projectnb/rise-batteries/bode/container-build-packages/gmx-gpu-ladder-20260928-v2-omp16/prepared/PREPARED.json`,
and PACKAGE_AND_PREPARED_INPUTS_VERIFIED. Preparation is complete on the user's
reported runtime checks; raw remote prepared files have not been downloaded.
Do not repeat preparation or remove its guards. Local sealed package checksums
and submission script were reviewed again; resource request remains one L40S,
omp/16 slots, 20 explicitly oversubscribed ranks, one 20-minute attempt.

User-facing next command: from that SCC package directory, bash SUBMIT_ON_SCC.sh.
It rechecks package/prepared hashes, validates the exact request, creates the
submission-L guard and submits once. This is the concrete bounded larger-ladder
milestone requested by the user; no repeat approval question is needed merely
to provide its command. No job ID, submission result or GPU execution is yet
reported, and the agent has not submitted remotely. Await returned ID/logs.

## Stage L v2 prepared after CPU-count eligibility matrix — 2026-09-28

User attachment `9e16e9ea-9eef-4965-b919-c97d76edb1be/Pasted text.txt` confirms
one-L40S omp/4, /8, /16 requests validate; /20, /28, /32 do not. Underlying
restriction still unspecified; this is not proof of a universal CPU limit.
See `docs/gromacs_gpu_ladder_scheduler_result.md` and the preserved transcript.
No validation command submitted a job. V1 preparation was not reached.

Prepared **gmx-gpu-ladder-20260928-v2-omp16**, manifest SHA-256
`f49e471b32d222986145fb4665edaa44b464ca3aaad80c97b89b369ee5ccfb07`. Spec `docs/gromacs_gpu_ladder_omp16_v2.yaml`,
instructions `docs/gromacs_gpu_ladder_omp16_package.md`.
Same 20 MPI ranks, full 20-state toy inputs, one L40S and private MPS, stop at
1000 then append to 2000, one attempt/20-minute cap. Reserve 16 CPU slots and
explicitly oversubscribe: localhost:16, --np 20, --oversubscribe, --bind-to none,
mpi_yield_when_idle=1. Before MPS/MPI, restrict the parent to 16 inherited Linux
CPU IDs; every rank verifies/records the same mask before GROMACS exec. Fewer
than 16 available IDs or a changed mask aborts. Masks are included in the first
phase archive. These are functional checks; no speedup/throughput claim.

Full suite **418 passed, one skipped in 47.32 seconds**. Rehearsed CPU preparation
and append for the unchanged 20-state fixture and old four-state fixture.
New tests check truthful MPI slot count, registered oversubscription, bounded
inherited affinity and rejection of escaped masks; affinity calls are mocked
on macOS. Actual Linux affinity inheritance and 20-rank oversubscribed MPI/MPS
remain SCC qualifications. Shell syntax and Python 3.6 runtime grammar pass.
Fresh-cache Snakemake dry-run/packaging each contain one gpu=0 job. Checksums pass;
A/R/L-v1 packages remain unchanged; all 20 v2 fixture inputs are byte-identical
to L-v1. Captured test output: docs/review/gromacs_ladder_omp16_20260928_pytest.txt.

Next user action: transfer v2, then VALIDATE_QUEUE_ON_SCC.sh, PREPARE_ON_SCC.sh,
REVIEW_ON_SCC.sh in the login shell. Existing r6 image is reused; fresh exact-SIF
TPRs still needed because no Stage L preparation has completed. No v2 remote
preparation, scheduler job ID or GPU result yet supplied. The guarded SUBMIT
script is ready for use after prepared-input review. Do not submit/edit old v1,
repeat completed A/R jobs, or change physical parameters to work around scheduling.

## Stage L scheduler preflight rejected — 2026-09-28

User ran the validation-only Stage L preflight and supplied:

```
Job 7763168 cannot run in PE "omp" because it only offers 0 slots
verification: no suitable queues.
Exiting.
```

7763168 is the number printed by qsub -w v, not evidence of a submitted job.
With the supplied && command chain, CPU preparation/review were not reached.
No new GPU attempt has been reported. Preserve v1; do not submit it, clear guards,
change its sealed contract, or rebuild the SIF. The exact restriction is not yet
known. Prior one-GPU/omp4 A and R jobs completed, but that does not establish
one-GPU/omp20 eligibility. Next collect a validation-only CPU-count comparison
(4, 8, 16, 20, 28, 32) with all other resources fixed, using -b y /bin/true so the
package's script directives cannot interfere. These checks cannot execute the
binary or submit jobs under -w v. Do not reduce reserved CPUs while keeping 20
ranks without a separately reviewed oversubscription design. Choose a revised
package only after an eligible resource shape is demonstrated.

## Larger-ladder Stage L prepared locally — 2026-09-28

User requested continuation with larger-ladder qualification. Prepared immutable
`results/gpu_smoke_packages/gmx-gpu-ladder-20260928-v1`; manifest SHA-256
`f3ab36b8fe46d8f768b826186edd462505b03b682bb8905e9d3b027dc72c44d8`.
Spec: `docs/gromacs_gpu_ladder_v1.yaml`; user commands and registered acceptance:
`docs/gromacs_gpu_ladder_package.md`.

20-state/512-atom synthetic LJ fixture, all historical lambda values; 20 MPI ranks,
one thread/rank, omp/20 slots on one host, one L40S shared through private MPS.
One attempt, 20-minute cap (1/3 allocated GPU-hour), 17-minute shared work deadline.
Normal stop at step 1,000, seal every checkpoint/output, then append to step 2,000.
Require both 20-client MPS overlaps, all 20 checkpoint transitions, 19 exchange
rounds with step 1,000 exactly once, accepted swaps over each of 19 neighbor links,
finite complete outputs, preserved pre-checkpoint rows, archive hashes and cleanup.
This is single-GPU Stage L, not a claim that original four-GPU Stage B is qualified.

Full suite **408 passed, one skipped**, including actual local CPU grompp/dump and
restart rehearsals for all 20 states plus the old four-state layout. Every state
passes checkpoint part/time/index, full foreign-lambda and append-output checks.
CPU tests use independent thread-MPI simulations; external MPI/exchange/MPS/CUDA
are not available locally and remain for SCC. Runtime parses as Python 3.6; shell
scripts parse under Bash. Fresh-cache Snakemake dry-run and packaging each have
one gpu=0 job. Package checksums pass; completed A/R package hashes unchanged.
See `docs/gromacs_gpu_ladder_local_validation.md` for validation evidence.

Next: user transfers package, runs VALIDATE_QUEUE_ON_SCC.sh, PREPARE_ON_SCC.sh,
REVIEW_ON_SCC.sh in the SCC login shell. Validation uses qsub -w v only and does
not reserve/submit; omp/20-slot eligibility is not yet verified. CPU preparation
must generate fresh exact-SIF 20-lambda TPRs; old four-state TPRs are inapplicable.
No image rebuild. Return preparation output for review before the packaged guarded
SUBMIT_ON_SCC.sh. No new SCC job or allocation was started by the agent; no remote
preparation/eligibility result or job ID is yet supplied. Preserve A/R; no repeats.

## Stage R accepted; checkpoint and accounting review complete — 2026-09-28

Reviewed attachment `5663d4ca-aab6-49de-9938-4a9f8af929c4/Pasted text.txt` for
job 7763081. All four checkpoints advance 500/0.5 ps/part 1 → 1000/1.0 ps/part 2
with correct lambda indices. Distinct first/resumed four-rank PID sets each
match their MPS clients on the same server/GPU. Independently reconstructed
nine exchange rounds/14 accepted swaps, eight in the resumed phase including
step 500 exactly once. Runtime reports unchanged earlier data, unique boundary
output and successful cleanup. qacct: scc-512, omp/four slots, failed 0,
exit_status 0, 18 seconds wall time, 93 seconds queued. Billed SU not supplied.

Stage R is accepted for graceful four-rank/one-L40S restart on this evidence.
See `docs/gromacs_gpu_restart_result.md`; verbatim transcript preserved under
`docs/review/gromacs_restart_7763081_user_transcript.txt`. Binary/raw outputs
have not been independently downloaded; runtime status pending fields remain
untouched as historical output. No rerun needed. Larger-ladder qualification
is a separate next scope; no new GPU job or protein work was started.

## Stage R reports technical pass; review/accounting pending — 2026-09-28

User supplied job 7763081 status `pass_pending_review_and_accounting`, stage R,
`restart_verified: true`, `mps_four_clients_observed: true`, confirmed cleanup,
and no failure. Wrapper elapsed 14.486157707986422 seconds; derived GPU-hours
0.004023932696662895 are not billing/accounting. Retained scratch:
`/scratch/gmx-smoke-A-7763081.10mnahsl`. See
`docs/gromacs_gpu_restart_result.md` for verbatim status and evidence limits.
Next: read `attempt/restart-review.json`, `attempt/permutations.json`, and
`qacct -j 7763081`. Raw artifacts have not been independently retrieved/reviewed.
Do not rerun preparation or submission. No further GPU stage is started.

## Restart test submitted as 7763081 — 2026-09-27

After receiving the bounded submission command, the user supplied job ID
**7763081** for `gmx-gpu-restart-20260927-v1`. Record one user-selected Stage R
attempt: one L40S, omp/four slots, four MPI ranks, ten-minute maximum, planned
stop at 500 then append to 1,000 steps. No execution state/result is yet supplied.
Monitor 7763081 and `submission-R/job.log`; collect `attempt/status.json`,
`attempt/restart-review.json`, permutations and qacct after completion.
Do not resubmit, repeat preparation, or remove guards. Completed Stage A job
7762792 remains separate. Agent did not submit this job.

## Restart package inputs verified on SCC — 2026-09-27

User supplied `EXISTING_TPRS_IMPORTED_AND_VERIFIED; no grompp or GPU job run`
and `PACKAGE_AND_PREPARED_INPUTS_VERIFIED` for restart package
`gmx-gpu-restart-20260927-v1`. Preparation is complete on the supplied evidence;
do not repeat import or remove its guards. No Stage R submission/execution is
yet reported. The next user-selected action is the packaged SUBMIT_ON_SCC.sh,
which requests one L40S, omp/four slots, four ranks, ten minutes and one attempt.
It validates feasibility, retains submission-R logs and submits once. This is
a new restart qualification, with no deletion/replacement of completed Stage A.
Agent did not submit; await a new job ID before changing submission status.

## Four-rank restart package prepared, not submitted — 2026-09-27

User requested preparation of the next checkpoint/restart qualification.
Prepared `results/gpu_smoke_packages/gmx-gpu-restart-20260927-v1`, manifest
SHA-256 `195331e4357bf28347b85b4a4d735d10307fd4ea348c2d8e8bba1fba67d59a11`.
Spec: `docs/gromacs_gpu_restart_v1.yaml`; instructions:
`docs/gromacs_gpu_restart_package.md`. This is Stage R, not the 20-rank Stage B.

Same r6 SIF and byte-identical four-state fixture/1,000-step TPRs imported from
completed Stage A v4. One L40S, omp/four slots, four MPI ranks, one thread/rank,
ten-minute maximum, one attempt. First launch uses `-nsteps 500`; require four
step-500/time-0.5/part-1 checkpoints, seal first-phase files read-only with hashes,
then start a fresh MPI process set with `-cpi smoke.cpt -append` and no step
override. MPS remains idle between launches and closes after the second.
Every checkpoint/TPR must match its seal before continuation; output/archival
hashes, part-2/step-1000 checkpoints, unchanged pre-checkpoint data, unique
boundary rows, and all nine exchange rounds are required. Step 500 is expected
once on continuation, based on version-pinned GROMACS MD source; GPU/MPI boundary
behavior itself remains for SCC qualification.

Validation: **397 passed, one skipped**, with the real local GROMACS 2025.3 CPU
restart rehearsal enabled for all four independent states. Verified step/part/
time transitions, unchanged earlier DHDL/energy rows and exactly one row per
output time. This CPU rehearsal does not exercise external MPI, exchange or GPU.
Runtime modules parse as Python 3.6. Snakemake dry-run/packaging were one gpu=0
job; checksums passed and the completed v4 package remains unchanged.

User action supplied: transfer, then PREPARE_ON_SCC.sh and REVIEW_ON_SCC.sh on
the login node. These import and verify existing exact-SIF TPRs only. No remote
preparation result, GPU allocation or new submission is yet reported. The
reviewable stage_R.sge and guarded SUBMIT_ON_SCC.sh are prepared, but no execution
of this new attempt was requested/started in this preparation turn. Do not
replace/delete completed Stage A job 7762792 or rerun its package.

## Stage A accepted; scheduler completion reviewed — 2026-09-27

Reviewed attachment `820ba058-cbd6-4de4-9177-d7a4d00186f3/Pasted text.txt`.
Job 7762792 on scc-502 has qacct `failed 0`, `exit_status 0`, omp/four slots,
project rise-batteries, 14 seconds wallclock; queue wait was 102 seconds.
Parsed overlap JSON: exactly four matching rank/client PIDs on one private MPS
server, shared GPU UUID `GPU-48f8c4f9-3f7d-4979-a18d-0916a5aa435c`.
Independently reconstructed all nine exchange rounds and 14 accepted swaps;
all recorded walker permutations and pair parity match. Runtime reports finite
outputs/final-checkpoint checks and successful MPS cleanup. Stage A is accepted
for the synthetic four-rank/one-L40S layout on this supplied evidence.

Evidence/result: `docs/gromacs_gpu_stage_a_mps_result.md`; verbatim transcript
retained in `docs/review/gromacs_stage_a_7762792_user_transcript.txt`.
Raw SCC binary outputs were not independently downloaded. Runtime status.json's
pending-review label is historical and remains untouched. qacct evidence is
received; billed SU is not present in that record and must not be invented.
No rerun is needed. Next possible work is separately bounded restart/larger-
ladder qualification; no Stage B, protein work or further job was started.

## Stage A reports technical pass; review/accounting pending — 2026-09-27

User supplied job 7762792 status `pass_pending_review_and_accounting`, no
failure, `mps_four_clients_observed: true`, and `mps_cleanup_confirmed: true`.
Wrapper elapsed time: 8.91108157596318 seconds; its derived GPU-hours field is
0.0024753004377675502, not scheduler accounting or billed SU. Private scratch:
`/scratch/gmx-smoke-A-7762792.tpam9sla`. Record and evidence limits:
`docs/gromacs_gpu_stage_a_mps_result.md`.
The sealed runtime reports passing the four-rank/one-GPU synthetic dynamics,
GPU mapping, exchange, finite outputs and final-checkpoint checks. Raw files
have not been independently reviewed. Next: collect MPS overlap, permutations,
complete job log and `qacct -j 7762792`; preserve all inputs/outputs/hashes.
Do not rerun preparation, submission or dynamics. Restart/20-rank/four-GPU/
protein qualification is not established by this result. No new GPU job started.

## One-GPU MPS Stage A submitted as 7762792 — 2026-09-27

User supplied `PACKAGE_AND_PREPARED_INPUTS_VERIFIED`, scheduler validation
`found suitable queue(s)`, job ID **7762792**, and the guarded replacement's
completion message. Current package is `gmx-gpu-stage-a-20260927-v4-mps`.
This reports successful verified preparation and replacement of unexecuted
job 7758910; the agent has not independently fetched remote transition logs.
Resources: one L40S, omp/four slots, four MPI ranks, private MPS, one host,
ten minutes maximum and one attempt. Execution state/result is not yet supplied.
Monitor 7762792 and the package's `submission-A/job.log`; after completion
collect `attempt/status.json`, MPS overlap evidence and `qacct -j 7762792`.
Do not rerun preparation/replacement/submission or delete guards. MPI/GROMACS
success is not established by scheduler acceptance. No agent submission occurred.

## One-GPU/four-rank Stage A package ready — 2026-09-27

Following the successful MPS probe, the user said "ok let's get started with
that" in response to the four-rank/one-GPU GROMACS smoke milestone. Prepared
`results/gpu_smoke_packages/gmx-gpu-stage-a-20260927-v4-mps` with manifest SHA-256
`6557fcd03adad353d60b65f6f2d1d57547d50f127c116dddd139b8f3e3421904`.
Spec: `docs/gromacs_gpu_stage_a_mps_v1.yaml`; instructions:
`docs/gromacs_gpu_stage_a_mps_package.md`.

One L40S, omp/four slots, four container-local MPI ranks, one thread/rank,
ten-minute maximum and one attempt. Same r6 image and byte-identical synthetic
fixture. Preparation imports and verifies the existing v3 exact-SIF TPRs with
source provenance; no image build or grompp rerun. New runtime starts a private
MPS service, maps all ranks to the sole assigned UUID/visible ordinal zero,
requires simultaneous four-rank MPS membership and the existing dynamics/
exchange/output checks, and shuts MPS down before CPU postprocessing.
Timeout cleanup checks CUDA_SUCCESS from terminate_client before forced teardown.

The packaged `REPLACE_AND_SUBMIT_ON_SCC.sh` verifies scheduler feasibility,
requires old job 7758910 to be the expected owner's/package's unexecuted qw job,
holds and rechecks hqw/no attempt, then deletes and submits exactly once.
Running/completed/absent/otherwise-changed old jobs stop the transition.
No remote job was cancelled or submitted by the agent; old state remains last
reported qw. User commands include transfer, CPU import/review, then guarded
replacement. Await actual SCC output/new job ID; do not assume submitted.

Validation: full suite 386 passed/one optional CPU rehearsal skipped; after the
final CUDA_SUCCESS guard and result-mapping regression test, focused suites
37 passed/one skipped. Snakemake dry-run was exactly one gpu=0 packaging job;
package generation/checksums passed. Local immutable v3 hashes remain unchanged
and v4 fixture bytes match v3. Real GROMACS MPI/GPU dynamics are still untested.

## Private MPS sharing probe passed on SCC — 2026-09-27

User supplied `FOUR_CUDA_CLIENTS_SHARED_ONE_GPU; MPS_CLEANUP_CONFIRMED` and
`attempt/result.json` with sharing/cleanup true, MPI/dynamics false, from
`gmx-mps-probe-20260927-v1` on `scc-505`. Allocated GPU UUID:
`GPU-7ab63c30-8edc-e49c-e306-922c040486e6`. See
`docs/gromacs_mps_probe_result_2026-09-27.md` for evidence and limits.
Functional four-client sharing inside the r6 SIF is now established by the
user-supplied result. Full logs/accounting were not independently retrieved.
No need to repeat this diagnostic; user should exit the completed allocation.
Next milestone is a bounded synthetic four-MPI-rank/one-GPU GROMACS smoke package
with private MPS and corrected rank mapping. MPI/exchange remain untested.
Existing four-GPU job 7758910 is unchanged; its last reported status is qw.

## Sharing metadata received; private MPS probe prepared — 2026-09-27

User reports assigned GPU index 3, L40S UUID
`GPU-d1609426-3406-79b2-051a-0a57dffc5956`, Exclusive_Process,
`/usr/bin/nvidia-cuda-mps-control` installed, and unset MPS pipe environment.
No allocation ID/hostname was supplied. Never reuse that index in a new allocation.
This establishes the sharing constraint, not functional MPS or site policy.
The user's request is to check directly without email; no message was sent.

Prepared a separate diagnostic in `docs/gromacs_mps_probe.md` and
`docs/gromacs_mps_probe_v1.json`, packaged by Snakemake rule
`gromacs_mps_probe_package`: one assigned L40S, omp/4, five minutes maximum,
four concurrent CUDA contexts in the verified r6 SIF. Uses only a private
unprivileged MPS daemon and assigned UUID; aborts on busy GPU/existing service,
requires four matching client PIDs simultaneously, and checks orderly shutdown.
No compute-mode change, MPI, dynamics, global service or support message.
Local mocked tests passed; actual MPS/container sharing remains untested.
Local validation: seven focused tests passed, Snakemake dry-run contained one
gpu=0 packaging job, and package generation/checksums passed. Package:
`results/gpu_sharing_probe_packages/gmx-mps-probe-20260927-v1`;
SHA256SUMS hash `53a9b3f568d103792c4cb59731311aa79259669904e6be44df6cc5bc8554d88c`.
The agent has not allocated/submitted this probe. User runs the supplied commands
in their authenticated SCC terminal. Old metadata allocation must be exited first.
Stage A job 7758910 and immutable v2/v3 packages remain unchanged; its last state
was qw. A successful sharing probe would enable preparation of a distinct
one-GPU/four-rank smoke package, not silently modify the current four-GPU runtime.
This current direct-check plan supersedes the earlier recommendation to require
an email before implementing a private diagnostic.

## User requests sharing inspection without email — 2026-09-27

Proceed with direct observation rather than requiring a support message. A bounded
metadata-only interactive request is supplied: qrsh, one L40S, one CPU slot,
two-minute maximum, `-now y` (no waiting allocation on failure). User runs it in
their authenticated SCC terminal; agent has no working SSH authentication.
Within that allocation, query only the scheduler-assigned device's UUID/model/
compute mode, inspect CUDA 12.8 module help and availability of the MPS control
binary/environment. Do not invoke the control binary, start MPS, change compute
mode, run dynamics, or use another job's MPS service. This is the requested
sharing inspection, separate from the still-pending Stage A dynamics attempt.
No probe result or interactive job ID is yet supplied. Metadata distinguishes
Default from Exclusive_Process; binary availability alone is not a functional
sharing test or proof of site policy. Keep 7758910 and immutable packages intact.

## One-GPU/four-slot validation passes — 2026-09-27

User reports `verification: found suitable queue(s)` for l40s, omp/4 slots,
one L40S GPU, rise-batteries, ten minutes and soft buyin=TRUE. Four-GPU/four-slot
validation failed earlier. GPU count distinguishes these feasibility results;
the reason the four-GPU request has no placement is still unknown. This does not
validate container GPU execution or prove immediate dispatch availability.
Next requirement for four GPU-using MPI replicas on one GPU is supported sharing.
Earlier SCC evidence was Exclusive_Process. Public BU documentation search did
not establish a supported per-job NVIDIA MPS procedure. Do not assume MPS is
forbidden or enabled. Request RCS's supported procedure before implementing MPS,
or obtain actual Default compute-mode evidence within an authorized allocation.
Existing four-device runtime cannot be used unchanged or qaltered to one GPU.
No MPS daemon, GPU-mode change, new package submission or job cancellation occurred.

## One-GPU/one-slot validation passes — 2026-09-27

User reports `verification: found suitable queue(s)` for the validation-only
request with l40s, omp/1 slot, one L40S GPU, rise-batteries, ten minutes and the
existing soft buyin preference. No allocation or container run occurred. User asks
whether MPI can use one GPU: yes, multiple ranks can share a supported GPU, but
four-replica exchange needs simultaneous communicating ranks. The site's earlier
Exclusive_Process evidence means a supported sharing mode/MPS must be established
before four separate GPU processes; no MPS setup is authorized by this question.
Next diagnostic is otherwise identical validation with omp/4 slots and one GPU,
to separate GPU-count placement from CPU-count placement. Existing job 7758910
remains unchanged; no smaller execution package or submission has been selected.

## Explicit fresh validation also fails; scheduler support recommended — 2026-09-27

User ran the supplied `qsub -clear -w v` with explicit project rise-batteries,
l40s, omp/4, four L40S GPUs, 600 seconds and soft buyin=TRUE. Result:
`Job 7761829 cannot run in PE "omp" because it only offers 0 slots`,
`verification: no suitable queues`, `Exiting.` The number 7761829 is from
validation, not evidence of another submitted job; actual job remains 7758910.
Do not infer physical zero CPU capacity or a proven root cause. No additional
resource changes, rebuild or cancellation is selected. Recommend RCS inspect
actual dispatch/eligibility for 7758910. Updated unsent support draft:
`docs/gromacs_stage_a_scheduler_support_draft.md`. No support message has been
sent or authorized for agent delivery. Await scheduler-side explanation or actual
job status/result; preserve existing package and submission guards.

## Validation has project-context inconsistency — 2026-09-27

Attachment `7f78e625-5ec0-46a8-954f-794edd3884ac/Pasted text.txt` confirms the
all-queue validation trial also failed with omp/zero slots. However it reports
`(no project)` on restricted queues, while subsequent `qstat -j 7758910` confirms
project rise-batteries, hard queue l40s, omp/4, four L40S GPUs, 600 seconds and
soft buyin=TRUE. The trial did not change the actual queue request. Do not claim
the project is missing or that all-queue placement has been conclusively ruled out.
Next: a fresh non-submitting `qsub -clear -w v` with explicit project, PE, queues
and all resources, including the existing soft preference, to avoid relying on
qalter's inconsistent context. No further cancellation/repackaging is selected.
Support draft ready at `docs/gromacs_stage_a_scheduler_support_draft.md`, not sent.

## Scheduler validation rejects replacement even with empty-cluster model — 2026-09-27

Attachment `145ac4e6-d2d4-4e12-8505-4092cc3bdd3c/Pasted text.txt` shows 7758910
still `qw`, submitted September 27 15:15:19 (scheduler timezone unspecified).
Both `qalter -w p` and `-w v` end with `cannot run in PE "omp" because it only
offers 0 slots` and `verification: no suitable queues`. All other rejection lines
exclude queues outside the hard queue list. No per-instance l40s cause is printed.
This is no longer explained by observed CPU/GPU occupancy alone; the generic PE
message does not establish that global omp capacity is zero (configured 99999).
Next diagnostic: `qalter -w v -hard -q '*' 7758910` to test all queues without
applying the trial change, retaining L40S/four GPUs/four slots. Also capture
`qstat -j 7758910` for actual current requests. Do not remove GPU type or submit
another job. No scheduler resource change has been made by the agent.

## Replacement still queued; request scheduler validation — 2026-09-27

User reports 7758910 remains queued after the CPU reduction. No execution result.
Next commands are `qalter -w p 7758910` (current-cluster validation) and
`qalter -w v 7758910` (empty-cluster feasibility). These are diagnostic validation
modes, not a resource change or resubmission. Do not keep revising resources
without their evidence; the CPU reduction has not established the waiting cause.

## Four-slot replacement submitted: job 7758910 — 2026-09-27

User returned `7758910` and `Replacement submitted. Return the new job ID above.`
after the guarded switch block. This reports successful pending-job replacement
of 7726162, not a running or passing GPU test. Agent has not independently queried
SCC. Monitor 7758910 and v3-omp4 `submission-A/job.log`; retain transition logs.
Scope is now omp/four CPU slots, four L40S GPUs/four ranks, one host and ten minutes.
No duplicate, retry or Stage B. If it disappears from qstat, inspect
`attempt/status.json`, job/runtime logs and `qacct -j 7758910` before interpreting
completion. Do not repeat preparation or the switch block.

## Four-slot inputs prepared; guarded replacement ready — 2026-09-27

User supplied v3-omp4 `INPUTS_PREPARED` and
`PACKAGE_AND_PREPARED_INPUTS_VERIFIED` after manifest checks on SCC. This is
reported remote evidence, not an independent download. No new job ID supplied.
User's CPU-change request plus existing one-attempt Stage A authorization permits
replacement of the still-unexecuted pending request with the smaller CPU request;
it does not permit another executed attempt. `scripts/replace_queued_gmx_stage_a.sh`
rechecks the pinned package and prepared inputs, claims a submission guard, requires
old `qw`, holds and requires `hqw`, checks no old attempt, deletes only that pending
job and confirms disappearance before one qsub. Any unexpected state/query failure
stops. No automatic guard clearing or retry. Provide this block in the user's SCC
terminal; agent SSH is still unavailable. Old and replacement submissions remain
unconfirmed as changed until the user returns results. GPU/rank/time bounds persist.

## Four-slot scheduler configuration checked — 2026-09-27

Attachment `0fa45a30-60c1-457a-ae22-e7fd49ea955d/Pasted text.txt` confirms
7726162 remains `qw`, `omp` allocation rule is `$pe_slots` (single host), no PE
user restriction or start/stop hook. All l40s instances show blank state flags;
scc-501/504/505/512/513 report 0/0/32 reserved/used/total CPU slots. Full `qquota`
output has only host CPU/GPU limits and unrelated linga-project limits; it does
not identify a blocking user/project quota. No confirmed waiting cause.
Next: transfer v3-omp4 and prepare its tiny inputs on SCC; no SIF rebuild or
additional scheduler query needed before preparation. Existing job stays intact
until replacement preparation is reviewed and old-job state resolved. No overlap
or additional GPU attempt is authorized. See the omp4 change guide.

## Four-slot Stage A replacement prepared locally — 2026-09-27

User reports job 7726162 still queued and asks about changing CPU configuration.
Prepared candidate `gmx-gpu-stage-a-20260927-v3-omp4`: `omp`/4 slots instead of
`mpi32`/32, same four GPUs/ranks, one thread/rank, SIF, toy inputs and ten-minute
limit. No existing package or job was modified; no replacement was submitted.
See `docs/gromacs_gpu_stage_a_omp4_change.md` for checks and transfer/preparation.
The September 26 idle-node snapshot means CPU count is not a proven waiting cause.
Need current job state, `qconf -sp omp`, queue-instance states and user quotas.
Do not alter the old job's PE alone: its runtime validates the v2 contract. Resolve
the old job's state before replacement; an executed attempt is not an unused one.

## L40S capacity now visible; queue eligibility unresolved — 2026-09-26

User attachment `691fccdd-ba1a-4593-a407-2b9f4a3de770/Pasted text.txt`
contains unchanged job 7726162 resource requests and a new `qgpus` snapshot.
Four `l40s` hosts (scc-503, scc-504, scc-510, scc-511) each report four GPUs
available and zero of 32 CPU slots in use. The prior capacity-shortage explanation
does not explain this snapshot. Free counters alone do not establish scheduler
eligibility; queue states, reservations, quotas and policy remain unreported.
Scheduling explanations remain disabled. Next read-only checks are queue-instance
status (`qstat -f -explain a -q l40s`) and user resource quotas (`qquota -u bodeb`).
The September 24 preflight already confirmed `mpi32` in the queue's PE list and
allocation rule 32; do not assume a PE mismatch. Keep existing job unchanged.

## L40S snapshot shows insufficient capacity — 2026-09-25

User supplied `qgpus -v -q l40s` output (attachment
`91c8863f-0802-48c4-8502-0ba4ed512ff9/Pasted text.txt`). The command printed all
queues; selecting rows whose queue list contains exactly `l40s` gives ten hosts,
40 GPUs total, 39 in use and one available. The only available GPU is on scc-513,
which has 26/32 CPU slots in use (six free). No listed `l40s` host can currently
satisfy job 7726162's four-GPU/32-slot single-host request. This observable capacity
shortage is sufficient to prevent startup at the snapshot; other scheduler
constraints/priorities remain unreported because scheduling explanations are off.
Leave the existing authorized job queued; no cancellation, resource change or
resubmission has been authorized. No start-time estimate follows from this snapshot.

## Stage A job 7726162 submitted; still queued — 2026-09-25

User supplied `submission-A/qsub.log` containing `7726162`, `qstat -u bodeb`
showing `qw`, and `qstat -j 7726162`. SCC reports submission on September 24 at
14:40:41 (scheduler-displayed timezone unspecified). The job matches the approved
v2 package directory, `rise-batteries`, `l40s`, `mpi32`/32 slots, four L40S GPUs,
`h_rt=600`, and `restart=n`. Output is `submission-A/job.log` in that package.
Scheduler job explanations are disabled; the actual reason for waiting is unknown.
Next read-only diagnostic is `qgpus -v -q l40s` to inspect per-host GPU/CPU usage.
Do not cancel, alter resources, clear submission guards or submit another copy.
No GPU execution result has been reported. Existing Stage A authorization persists;
Stage B and retries remain unauthorized.

## Stage A authorized; SCC terminal submission needed — 2026-09-24

User explicitly said "yes I authorize it" for the concrete single Stage A job:
v2 package, four L40S GPUs/four ranks, 32 slots, one host, ten minutes maximum
(2/3 GPU-hour, 16/3 CPU-slot-hours), one attempt, no automatic retries or Stage B.
The unknown current SU balance was explicitly disclosed and accepted. This
authorization persists; do not ask again within that scope. Immutable package
files retain their preparation-time flags; the current authorization is recorded
here and in `docs/gromacs_gpu_smoke_v1.yaml`, not by editing a sealed manifest.

Agent SSH initially could not resolve the host inside the network sandbox. The
network-enabled retry reached SCC but was denied noninteractive authentication.
No qsub occurred. The user must submit in their authenticated SCC terminal using
the verified v2 directory. The provided block verifies prepared files, requires
no `attempt/`, creates `submission-A/` atomically, and writes qsub output plus
`submission-A/job.log`. An existing guard must stop duplicate submission; do not
remove it after an ambiguous qsub error. Await the job ID before monitoring.

## Stage A SCC inputs prepared and identities reviewed — 2026-09-24

The user supplied v2 `INPUTS_PREPARED` and `prepared/PREPARED.json`. Its SIF and
package hashes match the pinned image and locally verified v2 package. All four
TPRs were created and inspected by the package; all processed topologies have
the same hash. The corrected private tmp round-trip passed. Record and per-state
TPR identities: `docs/gromacs_gpu_stage_a_scc_preparation.md`. This is reported
remote evidence, not an independent download of the prepared files.

CPU preparation is complete; no rebuild or preparation rerun is needed. The next
decision is the concrete Stage A job: one host, 32 slots, four L40S GPUs/four MPI
ranks, ten minutes maximum (2/3 allocated GPU-hour, 16/3 CPU-slot-hours), one attempt
and no automatic Stage B. GPU execution remains unauthorized/unsubmitted, and
current SU balance remains unavailable. Runtime device/placement/quota checks
occur within the Stage A allocation before dynamics. Preserve v1/v2 and logs.

## Stage A v1 mount warning diagnosed; v2 prepared — 2026-09-24

User supplied the v1 `grompp.log`: the first `grompp` succeeded, but Singularity
reported that contained session `/tmp` replaced the explicit scratch bind.
The blanket `^WARNING` check then mislabelled this as a GROMACS input warning.
There was also the expected missing `libcuda` message from MPI on `scc-i01`.
No input warning, failed image build or GPU execution was demonstrated.

Revision `gmx-gpu-stage-a-20260924-v2` adds `tmp` to `--no-mount`, retaining the
explicit private scratch bind. A token round-trip checks both read and write
through that bind before preparation and again before GPU work. Warning rejection
remains enabled, now including origin category, actual warning text and log path;
failed command reports include their last 30 output lines. Physics, state inputs,
SIF and resource caps are unchanged. Preserve immutable v1 and its remote logs.
Transfer v2 and run its CPU-only preparation; do not rebuild the SIF or submit a
GPU job. The actual Singularity fix still needs the SCC execution evidence.

## Stage A package prepared locally — 2026-09-24

User authorized preparing the bounded smoke package. The new CPU-only
`gromacs_gpu_stage_a_package` rule in `workflow/exchange_feasibility.smk` creates
`results/gpu_smoke_packages/gmx-gpu-stage-a-20260924-v1`. Its guide is
`docs/gromacs_gpu_stage_a_package.md`; all new toy parameters are explicit in
`docs/gromacs_gpu_stage_a_v1.yaml`. Historical pipeline parameters remain intact.
The package contains synthetic coordinates/topology/four MDPs, hashed source and
state identity, a CPU-only SCC TPR preparation command, a 32-slot/four-GPU/10-minute
SGE script, and a standalone runtime validator. No qsub, Stage B or MPS setup is
included. Exact-SIF TPRs have not yet been generated; transfer and run
`PREPARE_ON_SCC.sh` on `scc-i01`, then review `prepared/PREPARED.json` before any
submission. Current balance is still unresolved; GPU execution is not authorized.

Local GROMACS 2025.3 CPU rehearsal compiled all four states without warnings and
completed 1,000 steps/state with finite labelled DHDL and readable checkpoints/
energy files. This does not test external MPI, CUDA or Singularity. The full test
suite passed 360 tests; focused tests passed after the EDR validation addition.
The dry-run scheduled one `gpu=0` packaging job. Use a writable runtime source
cache for Snakemake on this Mac (its default Library cache is sandbox-restricted).

## GPU smoke preflight received — 2026-09-24

User supplied `gpu-preflight.tZDtopSs.log` output from `scc-i01` at 17:58 UTC.
See `docs/gromacs_gpu_preflight_2026-09-24.md` for provenance and limits. `mpi32`
and `l40s` configuration support the proposed 32-slot reservation. Projectnb
quota usage is 42.97/50 GB (about 7.03 GB remaining). The `--nolocal` wrapper
preview completed without executing the image. `acctool` was not found, so the
current allocation balance is unknown. Compute-node scratch, driver/device
forwarding, rank mapping and stage B sharing remain untested. Next is concrete
stage A package preparation; no image rebuild is needed. No GPU job was started.

## Bounded GPU smoke plan drafted — 2026-09-24

The user requested planning the next GPU milestone. See
`docs/gromacs_gpu_smoke_plan.md` and `docs/gromacs_gpu_smoke_v1.yaml`.
Reuse the verified r6 SIF; no rebuild is needed. Proposed stage A uses four ranks
on four L40S GPUs for at most 10 minutes. Stage B uses 20 ranks on four GPUs for
at most 20 minutes, conditional on A passing and a supported sharing method.
Each reserves 32 CPU slots on one host and permits one attempt, with no automatic
retry/reschedule or stage chaining. Combined caps are 2 allocated GPU-hours and
16 CPU-slot-hours. The fixture is synthetic, with a graceful whole-ladder restart
in B; this does not qualify abrupt failure recovery or protein sampling.

Planning only: fixture physics/seeds, hashed TPRs, exact device/driver forwarding,
sharing setup, scheduler/quota refresh and an executable Snakemake package still
need preparation/review. No GPU job, MPS daemon or simulation was started. Earlier
frozen qualification YAML/results and the immutable r6 package were not changed.

## Complete SIF milestone verified — 2026-09-24

The user supplied `final-verification.fEYjP0D0.log` from
`/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj`. It reports
the SIF checksum OK, no unresolved dependencies for `gmx_mpi` or `libmpi.so`, and
`SIF_HASH_AND_DEPENDENCIES_VERIFIED`. Actual SIF SHA-256:
`0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
This closes the final dependency-report issue without rebuilding. Full artifact
paths, evidence provenance, retention and limits are recorded in
`docs/gromacs_hrex_sif_r6_verification.md`. Evidence is user-supplied SCC output;
the agent did not download or independently hash the remote image.

The complete-image milestone is done. No more build/CPU startup reruns are needed
on current evidence. Next is planning a bounded GPU qualification; no GPU job,
exchange run, restart test, or protein simulation has been launched or authorized.
The incomplete recovery rootfs is historical diagnostic material, not the final SIF.

## r6 SIF created; final dependency-report error must be checked — 2026-09-24

User supplied the end of `launch.l7pEOpGW.log`: r6 reached identity/MPI output,
preserved and verified `installed-toolchain.tar.gz`, and reported exit 0 in
`/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj`.
However, the final `scc-singularity ... sh -c 'ldd ...; ldd ...'` emitted
`ldd: missing file arguments` and a missing `/opt/openmpi/.../libmpi.so` path.
Do not accept the old completion marker as a clean dependency report. Wrapper
argument handling is suspected, not proven. The SIF itself was created before
this reporting error; do not rebuild it.

The source build block now calls `singularity exec --cleanenv IMAGE ldd BINARY`
twice with direct arguments, writes a separate dependencies.log, and rejects
nonzero commands as well as missing-library/missing-file/missing-argument output.
Mock regression cases cover zero-exit error output. The immutable r6 package and
SCC artifacts remain unchanged. The current plan starts with a short one-off
hash/dependency verification block for the existing SIF, writing a fresh log.
The actual SIF SHA-256 value has not yet been supplied. GPU work is still untested.

## Complete SIF milestone started locally; remote authentication blocked — 2026-09-24

User explicitly asked to start the complete-image milestone. Package r6
(`gmx-hrex-20260924-r6`) keeps the pinned software/build flags and verified `/tmp`
MPI setting. It performs the full source build and complete install, saves a
hashed installed-toolchain archive on scratch before final assembly, and copies
that archive into persistent build evidence on exit even if later checks fail.
`--no-cleanup` also retains failed bundles. Final `%test` verifies GROMACS data and
PMIx help files and runs `mpirun -np 2 gmx_mpi --version`; the full self-test runs
again as the ordinary user before the completion marker is written. Full regression
tests remain enabled. Recovery-probe-specific OPAL path overrides are not copied
into the full image, which uses the complete normal installation layout.

Remote read-only SSH check reached SCC but returned `Permission denied
(publickey,keyboard-interactive,hostbased)` with BatchMode enabled. No remote
transfer or build was launched by the agent. Interactive user authentication is
needed to transfer and launch the new package. No GPU allocation is authorized.
Local verification: **346 tests passed**; the package dry-run and creation each
selected one CPU-only (`gpu=0`) job. r6 definition SHA-256:
`932efb5d1c9954ee859ac940ed72d6eb79e87cd4430251d9c5ffe51ff676f7ce`.
All package manifest entries and generated launcher/definition shell syntax were
verified. The real SIF and its SHA-256 do not exist locally; remote build is pending.

## Retained-rootfs runtime diagnostic PASSED — 2026-09-24

User-supplied `pmix-check.e70ODU86.log` ends with `RUNTIME_PROBE_PASSED` and
`PMIx path-check exit status: 0`. SCC log:
`/projectnb/rise-batteries/bode/containers/runtime-probes/probe.8c6hTH3H/pmix-check.e70ODU86.log`.
The documented self-test completed dependency/identity checks, a two-process
`/bin/true` launch, and two-rank `gmx_mpi --version` (MPI initialization) with
OPAL_PKGDATADIR/OPAL_PKGLIBDIR overrides pointing at the recovered flattened paths.
TMPDIR was `/scratch` and the MPI session root `/tmp`. Singularity reported that
its session `/tmp` replaced the explicit bind: the pass establishes writable
container `/tmp`, not use of the named host CHECK_TMP directory.

Missing `libcuda.so.1` warnings were nonfatal in this CPU startup test; CUDA driver
visibility, GPU execution, 20 ranks, exchange, and restart remain untested. No SIF
was created by this path check. The rootfs lacks a complete GROMACS data install;
do not promote it to a scientific runtime. The temporary OPAL overrides repair
the recovery layout, not the normal full `make install` layout of the r5 recipe.

The runtime diagnostic loop is complete. Next milestone is a complete image from
the reviewed full definition, retaining failed build bundles, then SIF SHA-256
and ordinary-user identity/MPI checks. r5's transfer/build is still unconfirmed.
Keep all probe logs/rootfs and earlier compiled scratch products. No new build,
allocation, or simulation was launched by the agent in response to this result.

## PMIx-only path check rejected by OpenMPI; use OPAL forwarding — 2026-09-24

User attachment confirms `pmix-check.R5qArABz.log` exited 1 after singleton
identity output. The fatal error was an explicit OPAL/PMIx directory-override
conflict, not missing CUDA driver libraries. The diagnostic command was incomplete:
it set PMIX_PKGDATADIR/PMIX_PKGLIBDIR with OPAL equivalents unset.
Pinned OpenMPI source `opal/mca/pmix/pmix3x/pmix3x_local.c:95–134` rejects that
combination and forwards OPAL-only values to bundled PMIx. The current command
in `docs/gromacs_runtime_probe.md` uses OPAL_PKGDATADIR/OPAL_PKGLIBDIR instead.
This reruns the retained rootfs test with no image build, package transfer, or
filesystem modification inside the container. SCC execution of the corrected
command remains pending; no successful MPI multi-process diagnostic exists yet.

## Runtime probe failed at PMIx startup; retained rootfs available — 2026-09-24

User output from probe `probe.8c6hTH3H` confirms GROMACS 2025.3, OpenMPI 4.1.5,
OpenMP and CUDA identity output. The first two-process launcher then failed with
PMIx `NOT-FOUND` at bundled PMIx `server/pmix_server.c:237`. Missing
`/opt/openmpi/4.1.5/share/pmix/help-pmix-runtime.txt` suppressed the detailed error.
The v1 recovery script incorrectly flattened bundled PMIx plugin/help directories
into OpenMPI directories. Source now preserves `lib/pmix` and `share/pmix`; its
synthetic staging test includes PMIx artifacts. Do not overwrite the v1 package.

Retained rootfs from the actual failure log:
`/scratch/bodeb/gmx-runtime-probe.BHWXJESK/tmp/build-temp-3284053732/rootfs`.
Next: run the documented no-build path-override check in
`docs/gromacs_runtime_probe.md` using `PMIX_PKGDATADIR` and `PMIX_PKGLIBDIR` against
this rootfs. This checks the plugin-path hypothesis and makes help readable; it
does not assume that fixing help alone resolves startup. No new package or full
build is needed for that check, and no successful SIF/GPU qualification exists.

## Retained-build runtime probe prepared — 2026-09-23

User supplied library inventories for all three compiled scratch trees. The logs
associate `FLJnrPFY` with `gmx-hrex.qQRhMhqB` and `DwrrwCIz` with
`gmx-hrex.VkNOVnDY`; both report 100% tests passed, zero failures out of 96, before
an overall build exit of 255. `yG5GagVH` maps to `gmx-hrex.CZWHYhL1` and the older
25-test MPI-launch failure. Do not mix products between these attempts.

The next action is the runtime-only diagnostic documented in
`docs/gromacs_runtime_probe.md`, using the `DwrrwCIz` products. Its local CPU-only
Snakemake package target is
`results/container_runtime_probe_packages/gmx-runtime-probe-20260923-v1`.
It copies binaries, libraries, MPI plugins and help data into a diagnostic image;
no compiler or build system is invoked. Runtime RPMs are installed, and dependency,
identity and two-process MPI startup checks exercise the `/tmp` override while
TMPDIR remains `/scratch`. It preserves source bytes, hashes and logs; conflicting
copies and failed tests stop it. Singularity `--no-cleanup` retains a failed bundle.
This is an incomplete recovery image, never a production/GPU qualification result.
Local shell-flow tests use synthetic files and a fake container engine; real SCC
execution remains pending. Full software rebuilds remain paused.
Local verification completed: 47 container-spec/recovery tests passed; the
Snakemake dry-run and package generation each selected one `gpu=0` job. The new
package's three manifest entries and launcher shell syntax verified successfully.
No SCC transfer, image assembly, allocation, or simulation was run by the agent.

## SCC retained-artifact inventory received — 2026-09-23

User output confirms `scc-i01`, Singularity CE `4.5.1-1.el8`, and host
`TMPDIR=/scratch`. The bounded search found no `*.sif` or `.singularity.d` under
the searched persistent/scratch build directories. It found
`work/gromacs-build/bin/gmx_mpi` under scratch suffixes `DwrrwCIz`, `FLJnrPFY`,
and `yG5GagVH`; `OwniQN0g` had no matching artifact. These binaries alone do not
establish a reusable runtime: the definition installed MPI, FFTW, and the compiler
runtime under the image's `/opt`, outside the retained `/tmp` bind. Next inspect
the retained MPI/FFTW/GROMACS build libraries and correlate scratch paths with
the persistent build logs. Do not run a scratch binary against arbitrary host
libraries or infer which scratch directory belongs to r4 from its name.
Full rebuilds remain paused; no remote diagnostic was executed by the agent.

## Rebuilds paused pending retained-artifact inventory — 2026-09-23

After repeated SCC failures, the next action is a read-only inventory on `scc-i01`,
not another full build. r5 is locally prepared but its transfer and execution are
unconfirmed. The most recent supplied directory check found no r5 package on SCC.
Inspect retained scratch build directories and persistent build directories for
compiled binaries, a sandbox, or a SIF before choosing a small runtime diagnostic.
The failed build may have cleaned its image root filesystem; do not assume that a
runnable image survived. See the current-status block at the top of
`docs/gromacs_hrex_singularity_plan.md`. Existing packages and logs stay unchanged.

## r5 corrects the final-image MPI session-directory failure

The user supplied r4's final self-test failure: ORTE could not create `/scratch`
because the image filesystem was read-only, then MPI_Init_thread aborted. The
test exited 1 (outer status 255). The selected path is established by the log;
the exact inherited TMPDIR/MCA environment was not supplied.

The pinned OpenMPI 4.1.5 source archive was rechecked: `orte/runtime/orte_mca_params.c`
supports `orte_tmpdir_base` for all processes and rejects conflicting local/remote
overrides; `orte/util/session_dir.c` uses the general temporary directory as fallback.
Package `results/container_build_packages/gmx-hrex-20260922-r5` explicitly exports
`OMPI_MCA_orte_tmpdir_base=/tmp` and unsets the conflicting local/remote overrides in
the build, image environment, and final test, before any MPI command. Host TMPDIR
and Singularity assembly paths are unchanged. Build `/tmp` still maps to the private
scratch work directory. Tests inject unusable scratch settings and check the shell
snippet passes the corrected settings to mocked GROMACS/MPI commands.

Earlier packages and logs remain immutable. r5 needs transfer and an actual SCC
rebuild; no successful SIF or GPU qualification is established. No build or simulation
was launched by the agent.
Local verification: **340 tests passed**; package dry-run/build each selected one
`gpu=0` job; all package hashes and generated shell syntax passed. r4's definition
hash is unchanged. r5 definition SHA-256:
`4d3a1d6ee329b595407957400f6182704ab5b5854015c94b4f32e4ebad14bf4b`.

## r4 corrects the final-image OpenMP dependency failure

The user supplied r3's final-stage output and then `work/gmx-version.txt`:
`gmx_mpi: error while loading shared libraries: libgomp.so.1: cannot open shared object file`.
The build reached the final image's `%test` and exited 127 (outer build status 255).
The earlier build-stage checks completed far enough to install/copy GROMACS, but
the full CTest pass/skip summary has not been supplied. No successful SIF is established.

Package `results/container_build_packages/gmx-hrex-20260922-r4` adds explicit final
runtime packages `libgcc`, `libgomp`, and `libstdc++`. Their actual RPM versions are
captured in the image and identity log. The validator reconciles the final package
list with the contract. The final self-test now prints and checks `ldd` output for
GROMACS, the MPI launcher, `ompi_info`, and `libmpi`, and prints failed GROMACS
startup output before exiting. All regression tests and the isolated MPI launcher
remain enabled. r1–r3 packages are preserved. A new transfer and SCC build are needed;
the agent has not launched them. GPU qualification and sampling remain unexecuted.
Local verification: **339 tests passed**; package dry-run/build each selected one
`gpu=0` job; all packaged checksums and generated shell syntax passed. Definition
SHA-256: `202558e20f1e578b37b7c3e3ee5c2c3c0b8f93a59971125cb071b142f83cd8fc`.

## r3 corrects the observed MPI launcher failure

The user supplied the first failing MPI test's detailed output. OpenMPI aborted in
`plm_rsh_component.c` because `plm_rsh_agent: ssh : rsh` could not be found; the
GmxapiMpiTests binary never started. This confirms that failure's startup cause, not
the causes of all 25 failures. OpenMPI 4.1.5's pinned source archive was downloaded,
SHA-256 verified, and its `plm/isolated` implementation inspected. The r3 definition
sets `OMPI_MCA_plm=isolated` during the build, in the runtime environment, and in
the final self-test, consistently with the one-host contract. A two-process launch
probe now runs immediately after OpenMPI installation. All GROMACS tests remain.

New package: `results/container_build_packages/gmx-hrex-20260922-r3`; the YAML pins
its changed definition hash. The reviewed build instructions use r3 and preserve
the earlier packages. This correction requires transfer and a successful SCC rebuild;
local mocks do not establish an MPI or GPU qualification. No new build was launched
by the agent.
Local verification: **336 tests passed**; the main DAG dry-run and package build each
selected one `gpu=0` package job. All package checksums and generated shell syntax
passed. New definition SHA-256:
`aebfefba27b28e45bf42882b414b0d981ce3645524eb16e5b16fc8c563a56bb5`.

## r2 container reached regression testing, then failed — user-supplied output

The user supplied the r2 CTest summary: 74% passed, 25/96 failed, including the
MPI unit/integration/multisim/replex tests and complex/essential-dynamics regression
groups. The essential-dynamics commands reported abnormal return -1 from
`mpiexec -np 8`; `make check` failed and the outer build exited 255. This supersedes
the earlier statement that real compilation was unverified: the build reached its
test suite, but no successful SIF or runtime qualification has been established.
The clustering suggests a common MPI launch/runtime issue, not a confirmed cause.
Obtain the first failing test's output from the retained scratch
`work/gromacs-build/Testing/Temporary/LastTest.log` before selecting a fix or retrying.
Do not disable tests or treat the 74% pass rate as acceptance. The old r1/r2 packages
remain immutable; no r3 has been prepared.

## First container build failed before compilation — 2026-09-22

The user transferred r1 and supplied a real SCC build failure: Singularity fetched
and extracted the OCI image, then exited 255 because `-B /scratch` targeted a missing
`/scratch` directory inside the base image. Scratch attempt:
`/scratch/bodeb/gmx-hrex-build.OwniQN0g`. Closing the laptop is not the cause shown
by this log. Keep the failed build log and r1 package unchanged.

The corrected package is `results/container_build_packages/gmx-hrex-20260922-r2`.
Its generated launcher binds a dedicated scratch work directory to the existing
container `/tmp`; image assembly uses a separate scratch temporary directory.
The definition and its hash are unchanged. Instructions now launch via `nohup`
with file-backed stdin/stdout/stderr so normal SSH disconnects do not end the build.
The local mocked build-flow tests require the new mount and an existing source
directory. Real SCC compilation and runtime qualification remain unverified.
Transfer r2 and verify its hashes before the retry; do not rerun or overwrite r1.

## Container build review — 2026-09-22

The user authorized correcting the C1 container package and transferring it to SCC.
The image self-test now checks `MPI library: MPI` separately from
`MPI library version: Open MPI v4.1.5`, permits GPU-awareness annotations, and
preserves failure from `gmx_mpi --version`. Static validation reconciles archive
versions/URLs/checksums, base images, compiler, CMake flags and the exact definition
SHA-256. The CPU-only `gromacs_hrex_container_package` rule prepares a fresh isolated
transfer directory with `SHA256SUMS`, a validation report, and `BUILD_ON_SCC.sh`
generated from the reviewed documentation. Existing packages/reports are protected
before Snakemake can delete outputs. The build saves logs and source snapshots in a
unique directory under `/projectnb/rise-batteries/bode/containers/builds`.

Package: `results/container_build_packages/gmx-hrex-20260922-r1`.
Verification: **335 tests passed**; the package DAG ran exactly one `gpu=0` job;
all ten packaged file hashes and the generated shell syntax passed. A forced package
rebuild was rejected during DAG construction, preserving the package. Default DAG
execution still selects only historical read-only verification. Definition SHA-256:
`137194fedc3f76340c125bb3eec3a6e34a790d6d3a7eee8c356bf2af1b0b812e`.
The SCC connection reached the server, but noninteractive authentication was rejected;
transfer and remote hash verification require the user's interactive SSH login.
Follow `docs/gromacs_hrex_singularity_plan.md` for transfer and build commands.
No SCC build, allocation or simulation was started. GPU sharing remains unresolved:
the proposed five processes per GPU require checking actual compute mode and an
admitted MPS or other supported sharing arrangement. The image build does not settle
that issue or authorize protein sampling.

## Current planning update — 2026-09-18: prospective methods study

The user requested a detailed publication plan and corrected conclusions, with
Vlasov reviewing later. See [the scoped plan](docs/publication_research_plan.md)
and [interpretation reconciliation](docs/conclusion_reconciliation_2026-09-18.md).
The subsequent focus revision makes a matched-cost protein sampling comparison
the primary study, diagnostics secondary, and mechanism optional. Independent
windows versus same-ladder HREX is the priority design to qualify; it is not a
selected GPU arm. Completed A/B work is retained as supporting evidence. The
four-site/five-realization panel is an initial design to justify by precision and
coverage, not a limit based on the user's pace. An external protein follows only
if transferability is the question the evidence warrants testing.
The λ-localization summary was reproduced from the existing audit JSON; this was
a read-only aggregation, not a new raw-data/MBAR audit. It does not establish a
structural mechanism or rule out starting-conformation sensitivity.

The fresh-output CPU lambda/comparator analysis in plan work package A is complete.
See [results](docs/f64a_lambda_comparator_results.md), the
[diagnostic specification/prior-art boundary](docs/diagnostic_comparator_specification.md),
and `results/cpu_audits/f64a_lambda_comparator_v1/`. All 60 NPZs reconciled;
the report contains 228 observed neighbor records plus 12 explicit endpoint
missing-direction slots and 480 fixed high-lambda pair/path records. It reproduces
the descriptive high-lambda pattern without assigning a structural cause or a
stopping threshold.

Work package B's frozen known-answer model is also complete; see
[results](docs/known_answer_model_results.md). Two independent quadratures agree
to about `1e-15 kT`. At equal potential-evaluation cost, all 16 held-out exchange
runs were admitted in the constructed metastable regime, while only 4/16
independent-window runs met the frozen decorrelated-sample minimum. Exchange RMSE
was 0.208 kT; the four admitted baseline runs had RMSE 0.956 kT, but that
complete-case contrast is conditional. Exchange interval coverage was only 0.75,
so uncertainty was not automatically calibrated. The v1 rehearsal is preserved
but rejected because it omitted correlation treatment.

The first C1 feasibility pass is complete; see
[the GROMACS exchange design](docs/gromacs_exchange_feasibility_design.md) and
[machine-readable qualification](docs/gromacs_exchange_qualification_v1.yaml).
GROMACS 2025.3 supports HREX, but the standing SCC CUDA binary is serial
(`GMX_MPI=off`, `GMX_THREAD_MPI=off`) and the one-window array cannot provide exchange.
The current decision is **conditionally feasible, new build required** with 10 blocking
required gates (two fail, eight unresolved). The authenticated 2026-09-19 inventory found
separate CUDA and MPI executables but no combined binary in the installed 2025.3 tree.
The completed login-shell capture confirms L40S MPI PE support. No further read-only
inventory is required. On 2026-09-21 the user selected a project-owned Singularity route
because native installation and sending the SCC request were not practical. The pinned
single-node definition, machine-readable contract, and SCC build instructions are in
`containers/gromacs-2025.3-mpi-cuda-l40s.def`,
`docs/gromacs_hrex_container_v1.yaml`, and
`docs/gromacs_hrex_singularity_plan.md`. It packages GROMACS 2025.3 + OpenMPI 4.1.5 +
CUDA 12.8 and is restricted to one `mpi32` L40S host, 20 container-local ranks, and a
prospective four-GPU layout. This avoids cross-host MPI interoperability; it does not
prove scheduler GPU exposure or performance. The earlier SCC request remains an unsent
fallback. No SIF build, scheduler script, GPU smoke test, protein arm, or submission has
been created or executed.
The qualification now follows the focus revision: one technical ladder is a 20-state,
independently initialized **folded-leg** realization. No new unfolded legs are in the core
comparison; the initial five-realization count is a precision/resource planning choice,
not a requirement to allocate five coupled ladders together.
The toy-model result does not select or authorize a protein arm.
The container definition has a CPU-only static validation target; it cannot pull an image,
invoke Singularity, start MPI, or submit a job. The forced standalone dry run scheduled
exactly one `gpu=0` comparator job; the
main-workflow dry run scheduled only the read-only default verification target.
The known-answer target dry run schedules three CPU-only (`gpu=0`) jobs: primary
reference, independent reference and calibration. The forced C1 qualification and
container-spec dry runs each schedule one CPU-only (`gpu=0`) job. The full local test
suite passes: **302 passed**.
Future stages propose one controlled F64A comparison and a prospective SOD1
panel, initially four mutations with five independent ladders per method.
Further calibration is not required; external-protein testing is a conditional
extension, and no structural mechanism is required for the core paper.
These stages are specified but not implemented or executed. Exact protocols,
durations, precision targets and resource caps remain to be registered before
production. The two-start draft is now a reserve option. **No GPU arm is selected;
the stop at 15 ns remains.** Vlasov's later review is not a current work blocker.
Accounting closeout still requires SCC evidence.

## Current update — 2026-09-18: F64A completed through 15 ns

The subsequent raw-energy follow-up is complete; see
[results](docs/f64a_raw_energy_audit_results.md) and
[fixed CPU audit design](docs/f64a_raw_energy_audit_design.md). All 60 production
NPZs are now local and exactly match the frozen report hashes, shapes, metadata
and simulation ancestry. The audit describes 348 raw series and 1044 saved-policy
suffixes, with no new MBAR/GPU work. Late changes in adjacent energies and very
short selected suffixes remain visible; neither this audit nor a quiet suffix
certifies equilibration. The next step is the scoped CPU/comparator work above,
followed by selection of a separately specified sampling test; there is no
automatic extension or GPU submission.

The separately selected v2 continuation completed on SCC: first light **7619903**
passed; production array **7620241** left the queue, and the full 54-fit CPU report
was supplied and preserved. See [results and late-window audit](docs/f64a_continuation_results.md).
Local review reconciled all summaries, 1080 selections, 1026 adjacent records and
513 paired changes; report-only audit outputs are in `docs/f64a_extension_review/`.
This is not independent local raw-NPZ/MBAR reproduction.

The primary adaptive mean movement is −0.049510 kcal/mol but masks r1 −0.695174
and r2 +0.598142; fixed-policy means move +0.579425 and +0.410739. Adaptive final
repeat range is 1.946359. Sparse window 17 persists even with fixed policies.
Duration stability is unresolved; **stop GPU sampling at 15 ns**. The raw-energy
inspection is now complete. A [two-start comparison draft](docs/f64a_start_comparison_design.md)
is retained as an unselected, unregistered reserve option under the new publication
plan. An archived WT reference candidate was found, but a justified alternate
start and current SU/storage admission remain unresolved. No executable GPU package
or submission was created.
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
