# CLAUDE.md — SOD1 FEP variant pipeline

Operating instructions for Claude Code on this repository. Read `README.md` for the
full design; this file is the short list of rules that must shape every action.

<!-- Maintainer note: block-level HTML comments are stripped before injection, so
     they cost no context. Use them for notes to humans, not to Claude. -->

## What this project is
A completed GPU-cluster validation campaign for SOD1 (UniProt P00441) folding ΔΔG,
now being reported as a methods-and-limitations study after its pre-registered gate
failed. The current project does not triage uncharacterized variants. `config/pipeline.yaml`
is the single source of historical run parameters; `data/variants.csv` is the single
source of truth for the panel.

## Current state — 2026-10-13

The user-run SCC preflight and static inactive-release review for the
isolated F64A folded r3 CPU system-build candidate passed on 2026-10-11.
The user subsequently selected one eight-slot, one-hour CPU-only technical
build. Its separately sealed package passed user-run SCC static review; the
user submitted **job 8032575** after verifying the expected manifest digest.
`qacct` reports `exit_status 1` after one second. The job log shows
`MODULEPATH` unset, failed module/conda setup and an old fallback Python;
no system build started. Preserve the single-attempt guard and do not retry
that package. A first inactive login-shell correction passed user-run SCC
static review, but SGE's `-S /bin/bash` leaves the shebang effect uncertain.
A second inactive candidate explicitly execs login Bash and passed user-run
SCC static review. The failed job consumed its one-attempt selection. The
user selected one corrected eight-slot, one-hour CPU-only attempt; its fresh
sealed package passed user-run SCC static review and no new job is submitted.
The pasted excerpt omitted the standalone exact manifest check; require it
immediately before the guarded one-attempt submission.
See
`docs/f64a_c2_fresh_system_cpu_8032575_failure.md` and
`docs/f64a_c2_fresh_system_cpu_explicit_login_selected.md`.

The bounded C2 shared-checkpoint branch fixture, job 7865574, is accepted as
technical mechanism evidence. Its ten-file metadata subset was transferred
and independently reviewed locally; all 20 common checkpoint hashes link to
both arms, and the saved exchange and accounting summaries agree. The Stage P
full 20-state XVG parser comparison also passed locally. See `HANDOFF.md`,
`docs/f64a_c2_branch_fixture_result.md`,
`docs/f64a_c2_fixture_metadata_result.md`, and
`docs/f64a_c2_stage_p_full_ladder_result.md`. These short tests do not qualify
protein production or C2 scientific inference. Long-correlation uncertainty
and paired percentile spread intervals have failed CPU screens. A conservative
normal-model spread bound passed synthetic coverage but was much too wide to
set a useful repeat count. Repeat count, retained duration, and production
allocation remain unselected. The user
explicitly requires agents not to access SCC; SCC commands and transfers are
performed by the user in their own terminals.

The separately authorized F64A folded apo-2SH pilots are **complete**: v1 retained
3→9 ns (array 7589742), then v2 9→15 ns (array 7620241; first light 7619903).
Their registered packages remain under `pilots/f64a_sampling_extension_v1/` and
`pilots/f64a_sampling_extension_v2/`; they did not reopen the failed validation gate.
The standing decision is **stop GPU sampling at 15 ns**. No new array, duration,
starting-conformation or sampling-method arm is selected. See
`docs/f64a_continuation_results.md` and `HANDOFF.md`.

The report-only late-window and raw-energy CPU audits are complete. All 60 v2
production NPZs were downloaded and hash/metadata/ancestry validated locally.
Raw adjacent-energy changes and short selected suffixes reinforce unresolved
duration/selection stability; they do not establish a structural cause or true
free energy. See `docs/f64a_raw_energy_audit_results.md`.
The publication plan's work-package A lambda/comparator analysis is also complete
under `results/cpu_audits/f64a_lambda_comparator_v1/`; it adds actual-lambda and
fixed high-lambda-pair descriptions, not a stopping threshold or causal selector.
See `docs/f64a_lambda_comparator_results.md` and
`docs/diagnostic_comparator_specification.md`.
The bounded known-answer CPU calibration is complete in
`results/cpu_calibration/known_answer_model_v2/`; v1 is a rejected technical
rehearsal because it omitted correlation treatment. The constructed metastable
model favored neighbor exchange at equal potential-evaluation cost, but this does
not select a protein arm or prove SCC/GROMACS feasibility. See
`docs/known_answer_model_results.md`.
A planning-only publication extension is scoped in `docs/publication_research_plan.md`:
one primary matched-cost protein sampling comparison, with diagnostics secondary,
mechanism optional and external-protein testing conditional on the scientific
question. Completed discovery/calibration evidence is supporting material, not
a prerequisite to repeat. The initial panel size must be justified by precision
and coverage, not assumed calendar or student-capacity limits. HREX on an identical
ladder is the priority design to qualify, not an authorized protein arm.
The project-owned Singularity image milestone is complete as of 2026-09-24.
The user built package `gmx-hrex-20260924-r6` on `scc-i01`; the full GROMACS 2025.3
+ OpenMPI 4.1.5 + CUDA 12.8 installation and startup checks completed. The original
final dependency report failed through a wrapper-mediated shell command; a direct
follow-up verified the SIF checksum and resolved all listed dependencies for
`gmx_mpi` and `libmpi.so`, without rebuilding. See
`docs/gromacs_hrex_sif_r6_verification.md` for evidence provenance, complete paths,
and the SHA-256 `0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.
The image and hashed full-install recovery archive are in SCC build directory
`/projectnb/rise-batteries/bode/containers/builds/gmx-hrex.IylQZ9Uj`.
Verification is based on user-supplied SCC output; the agent has not downloaded
or independently hashed the remote image. Preserve the immutable r6 package and
all logs, including corrected `final-verification.fEYjP0D0.log`; the original
completion marker alone is not the full evidence. No further image build or CPU
startup rerun is needed on current evidence. The earlier recovered rootfs is an
incomplete diagnostic artifact, not the final image.
The design remains restricted to one L40S host. The user requested planning a
bounded GPU qualification on 2026-09-24; the draft is in
`docs/gromacs_gpu_smoke_plan.md` and `docs/gromacs_gpu_smoke_v1.yaml`.
It proposes separate four-rank/10-minute and 20-rank/20-minute synthetic jobs on
four GPUs, capped together at 2 allocated GPU-hours, with no automatic retries.
Stage B requires stage A to pass and a supported GPU sharing method.
The user authorized Stage A package preparation; see
`docs/gromacs_gpu_stage_a_package.md` and `docs/gromacs_gpu_stage_a_v1.yaml`.
Toy inputs and launch/validation code are packaged locally, with a successful
local GROMACS 2025.3 CPU fixture rehearsal. Exact-SIF TPR generation on SCC is
now complete: the user supplied v2 `INPUTS_PREPARED` and matching package/SIF
identities. See `docs/gromacs_gpu_stage_a_scc_preparation.md` for per-state hashes
and evidence limits. The user has now submitted Stage A as job 7726162; it was
still `qw` in the September 25 output. Resources match the approved scope.
Scheduler explanations are disabled, so the actual waiting reason is unknown.
Do not submit a duplicate, clear guards or change the queued job's resources.
The user subsequently authorized exactly one v2 Stage A GPU attempt with the
current SU balance still unverified: four L40S GPUs, four MPI ranks, 32 slots,
one host and ten minutes maximum. Stage B, retries and protein work remain
unauthorized. Agent SSH authentication was rejected; the user submitted through
their authenticated SCC terminal. Do not ask again for this already-authorized
scope. On September 27, following the user's CPU-change request, the user completed
the guarded replacement of pending job 7726162 with job 7758910 from
`gmx-gpu-stage-a-20260927-v3-omp4`: omp/four slots, same four GPUs/ranks, one host,
ten minutes and one unexecuted attempt. Package preparation/review succeeded.
Monitor 7758910 and retain its output/accounting; its execution state is not yet
reported. Do not repeat preparation, the switch block or submission. See
`docs/gromacs_gpu_stage_a_omp4_change.md` for provenance and current package identity.
On September 27 the user's private MPS probe passed on scc-505: four CUDA
clients shared one allocated L40S inside r6 and cleanup was confirmed. This did
not test MPI or dynamics. At the user's request, the one-GPU/four-rank Stage A
replacement `gmx-gpu-stage-a-20260927-v4-mps` is now prepared locally; see
`docs/gromacs_gpu_stage_a_mps_package.md`. It imports the unchanged exact-SIF
TPRs, uses private MPS, and has a guarded transition from still-unexecuted job
7758910. The user subsequently reported verified preparation, suitable queues,
and successful guarded replacement submission as **7762792**. The user then
supplied `pass_pending_review_and_accounting`, four MPS clients observed,
cleanup confirmed and 8.91 seconds of wrapper elapsed time. Subsequent supplied
overlap/permutation/qacct evidence was reviewed: four matching rank/client PIDs,
nine exchange rounds, 14 accepted swaps with matching permutations, and
`failed 0`/`exit_status 0` on scc-502 with 14 seconds scheduler wallclock.
Stage A is accepted for the synthetic one-GPU/four-rank layout; see
`docs/gromacs_gpu_stage_a_mps_result.md`. Raw binary outputs were not independently
downloaded and billed SU is not reported. Preserve packages/logs; no rerun.
The user then requested checkpoint/restart test preparation. Stage R package
`gmx-gpu-restart-20260927-v1` was prepared; see
`docs/gromacs_gpu_restart_package.md`. It keeps the four-rank/one-L40S layout,
stops normally at step 500, seals all checkpoints/outputs, and appends to step
1,000 in a second MPI launch. Local CPU restart mechanics passed for all four
states; the subsequent SCC runtime now reports MPI/GPU continuation success.
This qualification does not select
20-rank Stage B or authorize further production. The user subsequently supplied
successful SCC TPR import and package/input verification. Do not repeat
preparation. The user then selected/submitted the bounded restart attempt as
**7763081**. On September 28 the user supplied a technical pass with restart
verified, four MPS clients observed, cleanup confirmed and 14.49 seconds wrapper
elapsed. Subsequent restart/permutation/qacct evidence was reviewed: all four
checkpoint step/time/part transitions match, new MPI PIDs share the same MPS
server/GPU, nine rounds and 14 accepted swaps have consistent permutations,
and qacct reports failed 0/exit_status 0 on scc-512 with 18 seconds wall time.
Stage R is accepted on the supplied evidence; see
`docs/gromacs_gpu_restart_result.md`. Preserve evidence; no rerun is needed.
Stage A package v1 reached a successful first `grompp` but stopped on a Singularity
`/tmp` mount override warning. Package v2 disables the competing automatic tmp
mount, verifies the explicit scratch bind and improves warning diagnostics.
V2 CPU preparation succeeded; do not repeat it. Preserve v1/v2 and their logs.
The one-GPU Stage A runtime now reports successful GPU visibility, sharing and
exchange and graceful one-GPU/four-rank restart; scheduler accounting for both
has been reviewed. Larger ladders and protein qualification remain untested.
On September 28 the user requested larger-ladder qualification. The selected
preparation scope is Stage L in `docs/gromacs_gpu_ladder_v1.yaml` and
`docs/gromacs_gpu_ladder_package.md`: all 20 historical lambda values in the toy,
20 one-thread MPI ranks, omp/20 slots, one L40S/private MPS, one 20-minute attempt,
normal stop at 1,000 then append to 2,000 steps. Reuse r6, generate fresh full-ladder
TPRs, and validate scheduler eligibility before CPU preparation. Do not import
the old four-state TPRs, rebuild the image or repeat completed A/R jobs. Local
preparation does not demonstrate 20-client GPU behavior or queue availability.
No Stage L submission or SCC preparation result is yet reported; use the fresh
package `gmx-gpu-ladder-20260928-v1` and retain all new evidence. Original four-GPU
Stage B and protein qualification are separate scopes.
The subsequent user-supplied scheduler matrix rejected omp/20, /28, /32 and
accepted /4, /8, /16 for one L40S. The /20 v1 preflight submitted nothing and
stopped before CPU preparation. Preserve it. The new candidate is
`gmx-gpu-ladder-20260928-v2-omp16`, registered in
`docs/gromacs_gpu_ladder_omp16_v2.yaml`: 20 ranks on 16 slots with explicit MPI
oversubscription and a shared 16-ID inherited Linux CPU affinity mask, verified
before GROMACS exec; MPI reports localhost:16 and yields during waits. All 20
states, restart schedule, one-GPU/20-minute/one-attempt scope remain unchanged.
This is a functional test, not a performance benchmark. See the scheduler evidence
and new package guide. The user subsequently supplied successful exact-request
scheduler validation, INPUTS_PREPARED and PACKAGE_AND_PREPARED_INPUTS_VERIFIED for
v2. Do not repeat preparation. The guarded SUBMIT_ON_SCC.sh command is now supplied
for the requested one-attempt milestone; no returned job ID or GPU result is yet
reported. Agent has not independently downloaded the prepared inputs. The user
subsequently reported successful guarded submission as **7763245**. Monitor this
single Stage L job and preserve its logs/accounting; no execution state or result
is yet supplied. Do not repeat preparation/submission or clear attempt guards.
The user subsequently supplied a failed v2 attempt: SCC reports effective PE
`omp16` while the sealed contract required `omp`, causing `wrong PE/slots` before
CPU-affinity setup, MPS or MPI/GPU dynamics. Preserve job 7763245 and its accounting;
see `docs/gromacs_ladder_7763245_failure.md`. The corrected fresh candidate
`gmx-gpu-ladder-20260928-v3-pe-omp16` explicitly requests/requires `omp16` and imports
the verified 20-state v2 TPRs. All other bounds remain unchanged. No automatic
retry, guard deletion, grompp repetition or image rebuild; remote v3 import and
execution are not yet reported. The user subsequently supplied v3 successful resource
validation, verified TPR import and package review; do not repeat import.
V2 accounting confirms omp16/16 on scc-502, four seconds wallclock, failed 0 and
exit_status 1; allocation.json directly confirms PE=omp16 and NSLOTS=16. The v3
SUBMIT_ON_SCC.sh command is supplied for the bounded qualification. No new v3
job ID or execution result is yet reported. The user subsequently reported
successful corrected v3 submission as **7763284**. Monitor this single current
Stage L attempt; no execution state/result is yet reported. Preserve failed v2
7763245 separately and do not repeat v3 import/submission or clear guards. The user
subsequently supplied job 7763284 technical pass: full 20-state ladder and restart
verified, all 20 MPS clients observed and cleanup confirmed, wrapper elapsed
48.212 seconds. Detailed ladder/restart/permutation/CPU-mask evidence and qacct
are pending review. Do not rerun. No protein/scientific validation follows from
this provisional synthetic runtime success.
Subsequent user-supplied ladder/restart/permutation/affinity/qacct evidence was
reviewed: **Stage L job 7763284 is accepted**. All 20 checkpoint transitions,
19 exchange rounds/181 swaps across all 19 links, and both matching 20-client
MPS PID sets check out. qacct on scc-503 reports failed 0/exit_status 0,
52 seconds wallclock and 132 seconds queued. See
`docs/gromacs_gpu_ladder_result.md` for provenance and limits. A/R/L synthetic
qualification is complete; preserve evidence, do not rerun. No protein or
further GPU simulation is selected, and the original four-GPU Stage B remains
unqualified. Raw remote binaries were not independently downloaded.
No GPU allocation, smoke test or protein simulation
is authorized by completing this image milestone. The failed historical science
gate is unchanged. The pinned build-candidate YAML remains unchanged; actual r6
artifact identity/execution evidence is carried by the verification record.
After Stage L acceptance, a read-only F64A folded-protein source inventory and
technical qualification design were prepared in
`docs/gromacs_protein_qualification_plan.md`. The user ran the inventory on
`scc-i01`: its supplied summary passes all 20-state source-file, lambda and
marker checks; see `docs/gromacs_protein_source_inventory_result.md`. The full
JSON remains on SCC. User-supplied host checks passed for reduced cysteines,
Cu/Zn absence and direct topology includes. The exact r6 SIF can read the
source and host pmx force-field files through explicit binds. Recursive includes
and r6 `grompp` passed for state 0 without input warnings; its new TPR hash
matches the historical state-0 TPR. The guarded r6 CPU `grompp` sweep then
passed for states 1–19, each with matching historical TPR hash. See
`docs/gromacs_protein_source_inventory_result.md`. No rerun is needed.
Short-run r6 input preparation subsequently passed on SCC: all 20 short TPRs
were built, and the 344-entry prepared-file checksum check exited 0. See
`docs/gromacs_protein_technical_inputs_result.md`; preserve that package and do
not rerun it. A separate protein technical runtime candidate
was transferred and CPU-imported successfully on SCC; see
`docs/gromacs_protein_runtime_local_validation.md`. Its package and queue
review passed on the user-supplied SCC output, and the user selected/submitted
the single bounded protein technical attempt as job **7791102**. The selected
short Stage P technical qualification is now accepted on the user-supplied
exchange, checkpoint, MPS, CPU-affinity, 614-file hash and `qacct` evidence;
see `docs/gromacs_protein_runtime_result.md`. Scheduler accounting reports
`failed 0`, `exit_status 0` and 146 s on one L40S with 16 CPU slots. No
rerun is needed. No C2 production
arm exists. The CPU-only Stage P input spec/builder/guide are in
`docs/gromacs_protein_technical_inputs_v1.yaml`,
`src/analysis/gromacs_protein_technical_inputs.py`, and
`docs/gromacs_protein_technical_inputs_package.md`.
The later C2 work is tracked in `HANDOFF.md`. As of 2026-10-03, both
100-ps folded-leg timing scouts and the one-job live no-exchange
checkpoint-branch fixture have passed their bounded technical reviews.
Fixture job 7865574 exited 0 on one L40S after 306 s, with all 20
common/baseline/HREX state checkpoints valid and three HREX rounds
attempting all neighboring links; see
`docs/f64a_c2_branch_fixture_result.md`. The
`docs/f64a_c2_post_fixture_production_design.md` review records the
remaining scientific precision, exposure, ancestry and resource choices.
Technical acceptance does not select a production run, reopen the
historical failed validation gate, or lift the 15-ns F64A stop. The agent
did not access SCC; cluster evidence was supplied by the user.
The two-start draft is a reserve option, not the current selected
next test; its 6 ns/370 GPU-hour proposals are not inherited by the new plan.
`docs/conclusion_reconciliation_2026-09-18.md` governs current interpretation,
including corrections to historical config comments and the lambda-ladder docstring.
High-λ drift does not select a cause; independent solvation does not prove distinct
basins; denser independent windows do not accelerate unchanged-state dynamics.
Keep hashed historical config/simulation bytes intact; correct their stale explanatory
prose through the linked errata. No new simulation is authorized by the plan.
Vlasov will review later; mentor review is not a prerequisite for local planning/CPU
work. The user explicitly waived confirmed
SU pricing before v2 submission: 1 SU/core-hour was an assumption, 1040 SU was
conditional; 130 GPU-hours and two attempts/task were the approved limits. Actual
billed SU remains unreviewed; preserve accounting promptly, do not invent a tariff.

The September 14 forensic bundle is an immutable **historical snapshot**, not a
current pilot release. Default Snakemake execution must verify it read-only.
Building/recomputing requires explicit targets and fresh review/release paths.
Never replace an existing bundle, checksum, manifest or evidence product silently.

## Non-negotiable rules
1. **Apo-first.** v1 simulates the apo, disulfide-reduced form. Do NOT switch to
   holo/metal-bound. If holo seems needed, STOP and ask — it is a separate
   parameterized arm, not a config flag or a refactor.
2. **The validation gate is go/no-go.** Do not run FEP on uncharacterized variants
   until FEP reproduces the experimental ΔΔG of the positive controls above
   `validation.min_pearson` AND within `validation.max_rmse_kcal` AND with a median
   |cycle closure| under `validation.max_median_cycle_closure_kcal`. All three are
   **pre-registered** (fixed 2026-08-07, before any gate evaluation) — never bypass,
   lower, or "temporarily relax" one to make progress; that destroys the only thing
   pre-registration buys. `validation.pivot_pearson` is a *different* number: falling
   below it means reframe per README §10, not retune. The gate subset is
   **charge-neutral only**: a net-charge change carries a PME finite-size artifact that
   does not cancel between the folded and unfolded legs (different box sizes), and the
   pmx engine has no counterion co-alchemy. Charge-changing variants get their own
   **sub-gate** once that is solved — see rule 6.
3. **Mature numbering.** Variant names use mature (153-residue) numbering; the
   precursor has an extra N-terminal Met. The offset lives ONLY in
   `pipeline.yaml:project.mature_offset`. Never hardcode residue indices anywhere.
   `tests/test_numbering.py` guards this — keep it passing.
4. **No parameters in code.** Read everything from `config/pipeline.yaml`. If a value
   is missing or `TODO`, ask the user rather than inventing a default.
5. **Replicates and error bars are mandatory** for any free-energy result. A ΔΔG
   without an uncertainty and a cycle-closure check is not a result. The former plan
   to raise `fep.replicates` from 3 → 5 was retired with the GPU campaign on 2026-09-14;
   do not change it now. If a future project explicitly reopens compute, never raise it
   while an array is in flight:
   every task re-reads this config and `submit_array.sh` aborts when
   `legs*windows*replicates` disagrees with `SGE_TASK_LAST`. Raise it between arrays;
   r3/r4 are then additive (80 new tasks per variant at 20 windows), not a rerun — the
   protocol hash is identical at 3 and 5 replicates, so existing windows stay valid.
   `#$ -t` must go 120 → 200 in the SAME commit.
6. **The approved scope pivot is a contract.** The original C1–C4 claims are
   preserved in README §2.3 as project history. On 2026-09-14 the user explicitly
   approved retaining apo-2SH, ending the current GPU campaign, and retiring C1
   (charge-changing coverage) and C3 (DMS-independent VUS triage). Because there
   will be no VUS prediction campaign, C4 is deferred and must not be claimed. C2
   remains only as a methods-and-limitations result about apo-2SH convergence
   diagnostics; do not describe the failed gate as successful predictive validation.
   On 2026-09-14 the user authorized the publication-review corrections, CPU analysis,
   release packaging, and planning with GPU availability. The subsequent separately
   selected/registered F64A pilots are now complete; the current stop is 15 ns as
   recorded above. Planning does not authorize more production. A new FEP/MD arm
   still needs a concrete design,
   explicit selection and preregistration before arrays are submitted. Never write "first",
   "novel FEP protocol", or "we show SOD1 variants are destabilizing": all three are
   occupied by Wells 2021, which used **this same toolchain** (README §11.2).

## Stage 3 stack — RESOLVED, do not relitigate
**GROMACS + pmx.** Not OpenMM+Perses. A research spike (2026-07-21) proved perses
hard-requires OpenEye for protein-mutation atom mapping in every version — including the
"OpenEye-free" lower-level path — confirmed by a GPU smoke test dying at
`_construct_atom_map -> import openeye.oechem`. The SCC has no OpenEye and no licence.
`src/fep/perses_engine.py` is kept only as dead reference; the live engine is
`src/fep/pmx_engine.py`, selected by `fep.framework: gromacs_pmx` through the dispatch
map in `src/fep/window.py`.

Per (variant, leg) the engine runs: `pdb2gmx` → `pmx mutate` → `pdb2gmx` → `pmx gentop`
→ box/solvate/genion → EM, cached behind a `SYSTEM_READY` marker; then per window a
generated `.mdp`, `grompp`, `mdrun`, and `alchemlyb` on `dhdl.xvg` → the same
`u_kn_window` NPZ schema `src/fep/analyze.py` has always consumed. Force field is
`amber99sb-star-ildn-mut` (pdb2gmx finds it only via `GMXLIB`).

**pmx must be new enough to read a PDB.** Require a revision at or after upstream
`866f34cf0` (2022-03-30, "do not relabel chain IDs if the chain already has an ID").
In `2.0+38.ga2311b9` the `self.atoms.append(a)` in `Model.__readPDBTER` is mis-indented
into an inner `if (a.chain_id==' ') or ...` branch, so a PDB whose atoms carry a non-blank
chain id — i.e. anything `pdb2gmx` writes — parses to ZERO atoms. `make_chains()` then
appends its still-`None` accumulator and dies with `'NoneType' object has no attribute
'model'`. Blanking the chain id does NOT work around it: the same block sets
`bNewChain = False`, so only the first atom would ever land. Verified on the SCC 2026-08-01.

**The force-field directory name is version dependent** — `data/mutff45` on 2.0-era
snapshots (where a flat legacy `data/mutff` also exists and is NOT the one to use),
`data/mutff` on current develop, which dropped mutff45 and is now the maintained set.
Never hardcode either: `pmx_engine.pmx_ff_dir()` probes both and picks whichever holds
`fep.pmx_forcefield`, and `scripts/scc_env.sh` calls that same function to set `GMXLIB`.

**pdb2gmx order matters:** pmx's own help requires its input to have come from pdb2gmx.
Feeding it a raw PDBFixer file makes pmx parse zero residues and die in `make_chains()` —
the SAME traceback as the stale-pmx bug above, so check the pmx revision before assuming
it is an input-ordering problem.

## Invariants GROMACS will silently undo
Stage 1 enforces these on an OpenMM topology; the GROMACS path needs its OWN guard:
- **Reduced disulfide.** `pdb2gmx` re-detects Cys57–Cys146 by SG–SG distance and rebuilds
  it. The engine answers `-ss` prompts "n" per cysteine (`fep.keep_disulfide_reduced`).
- **Which residue gets mutated.** PDBFixer/pdb2gmx RENUMBER. In the capped tripeptide the
  site is the *middle* residue (3), not `mature_pos` — sending `mature_pos` mutates a
  neighbour and yields a plausible, wrong ΔΔG. `pmx_engine.mutation_resid()` reads the id
  from the actual file and verifies the residue name against the panel's wild type.

## First-light traps — the first real GROMACS+pmx window (2026-08-06)
Until 2026-08-06 no Stage 3 window had ever run; the smoke test found these in
order. All are encoded in `pmx_engine.py` / `submit_array.sh` — do not
reintroduce them:
1. `pmx mutate` takes `--script`, not `-script`. A single dash is silently
   dropped by argparse, pmx falls into its interactive residue picker and blocks
   on stdin (`Enter residue number:`). The engine captures stdout, so it looks
   like a hang.
2. No `-ignh` on the hybrid `pdb2gmx` (pmx's own tutorial omits it). With it,
   pdb2gmx discards pmx's hydrogens and rebuilds them from `mutres.hdb`, which
   has no entry for hybrid residues (A2V, …) → "N missing atoms" fatal. Keep
   `-ignh` only on the WT pass.
3. `OMP_NUM_THREADS` must equal `-ntomp` for mdrun (GROMACS ≥ 2025). SCC shells
   export `OMP_NUM_THREADS=1`. Set it on the mdrun subprocess env from
   `cluster.mdrun_ntomp`; exporting it in `scc_env.sh` does not stick (later
   module/GMXRC sourcing resets it).
4. Resume flags are conditional: `-cpi X.cpt -append` fails on a fresh run. Pass
   them only when the checkpoint exists.
5. System build is serialized with an flock — all array tasks of a (variant, leg)
   start at once and would `rmtree` each other's half-built system.
6. `set -u` kills array tasks: GROMACS's `GMXRC` references unbound variables
   (`$shell`, `$GMXLDLIB`), so `submit_array.sh` must use `set -eo pipefail`
   (batch must match interactive).

Cost/monitoring: a real folded window is ~15 min on one GPU (A4V w0_r0 = 892.8 s);
unfolded ~2–3 min. An A4V array (108 windows) is ~16 GPU-hours. `h_rt=12:00:00`
is per-task, never hit. Progress = count `results/fep/<variant>/**/w*_r*.npz`.
SGE log files appear when a task STARTS; grep them for python Tracebacks AND bash
`unbound variable` errors.

## Minimisation must be lambda-aware
`grompp` without `free-energy = yes` builds the system from **A-state parameters alone**.
In a pmx hybrid topology the appearing atoms are dummies in state A — no charge, no LJ —
so minimisation relaxes real atoms *into* them. Switching them on at a high lambda then
explodes the system on step 1: LINCS reports bond lengths in the millions and the GPU
faults with `cudaErrorIllegalAddress` (a symptom, not the cause — do not go looking for a
CUDA bug). A4V folded w17 (λ=1.0) died this way in all three replicates while every
unfolded window survived, because position 4 is buried and the tripeptide is not.

`_minim_mdp(cfg, window)` therefore emits the free-energy + soft-core block, and
`run_pmx_window` minimises **per window at that window's λ** before production, starting
from the shared `system/em.gro`. The shared build still calls `_minim_mdp(cfg)` with no
window — solvation and ions only care about the physical topology.
`tests/test_fep.py:test_window_minimisation_is_lambda_aware` guards this.

Corollary: a window that merely *survives* is not evidence the protocol is right. The
high-λ windows that did not crash were started from the same A-state-minimised structure.

## Never `git pull` the SCC while an array is in flight
Array tasks read the repo code and `config/pipeline.yaml` when EACH TASK STARTS, not at
submit time. Pulling mid-array gives tasks 1..n one protocol and n+1..108 another, and
the result is a complete-looking dataset that MBAR will happily combine. Pull only
between arrays. `run_pmx_window` now hashes the production `.mdp` (minus seed and
`init-lambda-state`) into each window's NPZ as `protocol`, and
`analyze._check_single_protocol` refuses to analyse a variant whose windows disagree —
the settings-level counterpart to the engine-level provenance rule below.

## Cycle closure is not a correctness check
`cycle_closure_kcal` is the forward/reverse Zwanzig hysteresis of ONE ladder, not a closed
thermodynamic cycle. It is an aggregate self-consistency proxy, not proof of within-basin equilibration.
Signed adjacent-window discrepancies can cancel before the absolute value is taken.
The exploratory audit in `docs/cpu_improvement_plan.md` and `docs/review/` measures this
explicitly without altering the historical metric or gate. Three archived observations are:

- G93A reports the cleanest closure in the project (**0.045**) and is **1.17 kcal/mol**
  wrong (1.259 vs exp 2.43).
- F64A's folded r1 has hysteresis **0.023** and is the replicate that disagrees with its
  two independently-solvated siblings by **1.20 kcal/mol** — the largest replicate
  disagreement of the 48 (variant, leg, replicate) records in the archive, at a hysteresis
  in the lowest ~20% (rank 10/48). It is NOT "the lowest hysteresis recorded anywhere":
  that claim stood in three files until 2026-09-12 and is false (G93A unfolded r2 is 0.0017,
  13x lower). Over all 48 records, folded-leg hysteresis and independent-box disagreement are
  near-uncorrelated (Pearson +0.072, Spearman +0.080, n=24) —
  `docs/stop_rule_reanalysis.md` §6, which is the measured version of this bullet.
- G93A's minimum adjacent overlap (**0.025**) is the same order as F64A's (**0.015**), yet
  G93A passes every convergence criterion and F64A fails. Neither is the project's thinnest
  ladder: I18V is 0.0054 and I149A 0.0096, and both pass. Overlap does not order the
  failures either.

The exact-path v1 follow-up adds direct temporal evidence: F64A folded r1 changed
from **2.505942** in its first retained 3 ns to **0.429467 kcal/mol** in the disjoint
6–9 ns block, movement **−2.076474**, despite early net hysteresis **0.022705**.
The metric is the absolute net of signed local discrepancies, not a closed cycle.
Low early hysteresis did not certify future duration stability on this path; neither
the later block nor this selected case establishes true free energy, general
diagnostic performance or experimental accuracy. See `docs/f64a_extension_results.md`.

All three bullets were previously quoted from the **superseded 18-window** protocol
(`f9bded6f07b4abe5`: closure 0.08, overlaps 0.017/0.018, error 1.05) while describing the
20-window gate dataset. Corrected 2026-09-12 against values re-derived from the archived
windows — `docs/stop_rule_reanalysis.md`. The qualitative claim is unchanged; check the
protocol before quoting a number from `docs/postfix_18window_results.md` or
`docs/f64a_folded_leg_failure.md`, which describe earlier ladders.

Consequences for day-to-day work: never report `converged: true` as evidence a number is
right; read `min_adjacent_overlap` and `replicate_spread_kcal` alongside it. Since
`fep.independent_replicate_systems` was enabled the spread is meaningful (replicates no
longer share a box). Independent solvation does not establish independent conformational
basin coverage. `ddg_err` is the larger of propagated MBAR error and replicate SEM; it
does not cover model/reference bias or unsampled modes. The former blanket “3–10×”
understatement claim confused replicate range or reference discrepancy with uncertainty
of a mean and is withdrawn. Correlations are descriptive: 24 folded records are nested
within eight variants at six sites; sibling-disagreement values are dependent.

## Results must carry provenance
Every window records the engine that produced it; `analyze.py` refuses to mix engines or
accept an unlabelled window; `validate.py` gates only on `provenance == fep.framework`.
This exists because fabricated ΔΔG files (experimental values + noise) once produced a
`validation_gate.json` reading "passed, pearson 0.994". Never hand-write a result file.

## How to work here
- Prefer editing existing modules under `src/<stage>/` over adding new top-level code.
- Every stage is a Snakemake rule; wire new work into the DAG in `workflow/Snakefile`,
  don't create standalone run scripts. The post-result CPU audit `.smk` files are
  included from that DAG and may also be invoked separately. For historical v2
  reproduction use its recorded commit (802cc9e), not today's changed workflow;
  keep the simulation modules, pilot configs and supplied reports immutable.
- Stage 3 is submitted as SGE job arrays (`qsub -t`) on the BU SCC — one task per
  `(variant, leg, window, replicate)`. Keep that granularity — it's the whole point.
- GPUs are requested via `-l gpus=1 -l gpu_c=7.0` and assigned by the scheduler
  through `CUDA_VISIBLE_DEVICES`; never hardcode device IDs (one window = one GPU).
- `source scripts/scc_env.sh` is the ONE way to get a working shell (interactive or
  batch); `submit_array.sh` sources the same file so the two cannot drift. It bootstraps
  Lmod, loads the module chain, activates conda, and exports `PYTHONPATH`/`GMXLIB`.
- SCC modules are versioned (no bare names) and live in `config/pipeline.yaml:cluster.*`.
  Three traps, all already encoded in config — don't rediscover them:
  1. `module load gromacs/2025.3` gives the **CPU-only** build. The CUDA build is a
     separate tree (`install_gpu`), selected via `cluster.gmx_gmxrc`. It needs
     `cuda/12.8 intel/2024.0 gcc/12.2.0` at runtime (it links MKL), not openmpi.
  2. `/etc/profile.d` skips Lmod in **non-interactive** shells (`qrsh ... bash -lc`, SGE
     tasks), so `module` is undefined. `cluster.lmod_init` pins
     `/usr/local/lmod/8.7.12/init/bash`; a stale broken 7.8 tree sorts ahead of it in globs.
  3. SCC home has a 10 GB quota — conda envs must live under `/projectnb`.
  4. **A scheduler-assigned GPU is not a guaranteed GPU.** `gpus` is a JOB consumable used
     for bookkeeping, not enforcement, and the cards run in `Exclusive_Process` mode — so
     another user's context makes a device unusable while SGE still counts it free. mdrun
     then dies with `CUDA error #46` / "no GPU is detected". Waiting cannot help (F64A
     burned 12 retries over 24 min on two different nodes); only moving the task can.
     `_run_mdrun_with_gpu_retry` raises `GpuUnavailableError`, `src.fep.window` exits
     **99**, and `submit_array.sh` sets `#$ -r y` so Grid Engine reschedules. Retry a few
     times first (`cluster.gpu_retry_*`) for the genuinely brief case; do NOT reschedule
     on any other failure, or a blown-up system loops forever.
  5. `-l gpu_c=7.0` is a **minimum** (SGE relation `<=`), so it also admits cards NEWER
     than the GROMACS build. `scc-702`'s RTX PRO 6000 Blackwell (compute 12.0) has no
     sm_120 kernels in GROMACS 2025.3/CUDA 12.8, so mdrun starts, JIT-compiles the
     embedded PTX, and dies with `CUDA error #218 (cudaErrorInvalidPtx)`. `submit_array.sh`
     therefore also pins `-l gpu_type=L40S` (32 nodes; all timings are measured there).
     Do NOT add this error to the mdrun retry signatures — it is deterministic per node,
     so a retry on the same host fails identically and hides a placement problem.
- Checkpoint long GPU jobs; assume windows will die and must resume.
- Honor `cluster.trajectory_retention` — do not persist raw frames when the config
  says estimates only (disk fills fast).

## Verification
- Run `pytest tests/` after touching numbering, panel parsing, or config loading.
- Dry-run the DAG with `snakemake -n` after changing any rule's inputs/outputs.
- Report any command you could not run rather than assuming it passed.
- When diagnosing array failures, grep `logs/fep/` for both `Traceback|ToolError`
  and `unbound variable` — bash env errors abort before python ever runs.

## Style
- Python 3.11+, type hints, docstrings on public functions.
- Write rules as actions, not vibes: name the file/function to touch, not "be careful".
- If a rule here conflicts with something you infer from the code, surface the conflict
  to the user instead of silently choosing.
