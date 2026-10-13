# F64A C2 bounded live checkpoint-branch fixture

Status: **design candidate, updated 2026-10-01**. This is a technical qualification
of the selected shared no-exchange preparation and isolated baseline/HREX
fan-out. It is not an executable release, job selection, production protocol,
or free-energy study. The agent has not accessed SCC.

The [accepted CPU rehearsal](f64a_c2_branch_cpu_rehearsal_package.md)
qualified exact-r6 `grompp -t`, checkpoint copying, TPR dumps, and the
20-state input checker using archived Stage P checkpoints. Stage P had
exchange during its trajectory. This fixture must create **new** common
checkpoints without exchange; the Stage P terminal checkpoints must not be
used as branch starts.

The machine-readable candidate is
[f64a_c2_branch_fixture_candidate_v1.yaml](f64a_c2_branch_fixture_candidate_v1.yaml).
Values below are proposed for one bounded attempt and need a separately
reviewed execution package and explicit selection before any submission.

## Ancestry and schedule

Use the accepted Stage P **initial** 20-state prepared inputs, whose
344-entry manifest has SHA-256
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
Verify all manifest entries, per-state TPR hashes, atom/order, lambda
vector, effective MDPs and the exact r6 SIF SHA-256
`0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`
before launch. Read source inputs from `/projectnb/rise-batteries/bode` and
write the new attempt under `/project/rise-batteries/bode`. Do not reuse
Stage P job 7791102's `attempt/state*/smoke.cpt` files.

All phases use 20 one-thread MPI ranks, the same one L40S GPU and private
MPS, and `dt=0.002 ps`. Run the phases **sequentially in one allocation**:

| Phase | Exchange | Steps and absolute endpoint | Purpose |
| --- | --- | --- | --- |
| Common preparation | Off; no `-replex` | Start 0; stop normally at 1,100 steps = 2.2 ps, checkpoint part 1 | Produce one new, sealed 20-checkpoint set. The accepted 2,000-step source TPRs may be stopped with `mdrun -nsteps 1100`; confirm the actual endpoint in every dump. |
| Baseline continuation | Off; no `-replex` | `init-step=1100`, `nsteps=2000`; final step 3,100 = 6.2 ps, part 2 | Prove an isolated, longer no-exchange continuation. |
| HREX continuation | `-replex 500`, fixed registered `-reseed` | `init-step=1100`, `nsteps=1500`; final step 2,600 = 5.2 ps, part 2 | Prove post-branch exchange and a shorter, independently stored continuation. |

The proposed preparation endpoint **1,100 is not divisible by 500**. The
expected HREX exchange steps are 1,500, 2,000 and 2,500, all strictly
after the branch. Three alternating rounds should attempt all 19
neighboring state pairs. Acceptance counts are descriptive, with no
minimum swap count. Unequal continuation lengths exercise the actual C2
input contract; these tiny lengths are not matched-cost targets or an
equilibration choice. The historical 2-ns preparation remains an
unselected production candidate, and its boundary exchange behavior
would need its own registered resolution.

## Seal, fan-out and launch rules

1. Before the common launch, recheck the source manifest and refuse an
   existing attempt directory. Record the 20 initial TPR hashes, job
   allocation, rank/CPU/GPU mapping, MPS server, command lines and seeds.
   No automatic retry or scheduler reschedule is permitted.
2. After a normal common-phase stop, dump all 20 checkpoints and verify
   absolute step 1,100, time 2.2 ps, simulation part 1, correct FEP
   state and retained velocities. Confirm **zero exchange rounds**. Hash
   the complete common output tree and make a sealed 20-checkpoint
   manifest. A partial set cannot branch.
3. Copy each checkpoint byte-for-byte into separate baseline and HREX
   input trees. Verify all 40 copies against the sealed common hashes,
   then preserve the original common files. Do not copy the common
   output files into arm output trees.
4. With exact r6, preprocess 40 changed-MDP TPRs using `grompp -t` on
   the arm's copied checkpoint; reject any nonzero exit or GROMACS
   warning and do not use `-maxwarn`. Set `gen-vel=no`,
   `continuation=yes`, `tinit=0`, `init-step=1100` and
   `simulation-part=2`. Only the registered `nsteps` differs between
   arm MDPs. Keep all physical Hamiltonian, lambda, restraint, coupling,
   and output-stride fields identical. The accepted CPU input checker
   must pass on the *new no-exchange* checkpoint set and all 40 TPRs
   before any arm dynamics.
5. Immediately before each arm launch, verify all 20 input checkpoint
   hashes again. Pass the copied input to `mdrun -cpi`, a different
   output name to `-cpo`, and `-noappend` in an arm-specific directory.
   Use the 20-rank whole-ladder launch for each phase. Finish and review
   baseline before HREX starts; if any phase fails, preserve evidence
   and stop the attempt. The HREX seed must be frozen in the selected
   package; this draft proposes `20261001` only as a candidate.

GROMACS documents checkpoint-based continuation with `grompp -t` and
`mdrun -cpi`, and part-separated files with `-noappend`. Its `mdrun`
documentation says a missing `-cpi` path can start from the TPR instead,
so missing or changed checkpoints must fail in our wrapper *before*
GROMACS runs. See the [2025.3 simulation guide](https://manual.gromacs.org/documentation/2025.3/user-guide/managing-simulations.html),
[grompp](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-grompp.html),
and [mdrun](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-mdrun.html).

## Bounded resource candidate

Use one `l40s` host, one L40S, `omp16` with 16 CPU slots, 20 one-thread
ranks with the previously qualified explicit oversubscription/affinity
settings, and private MPS. Request one 30-minute job (`h_rt=00:30:00`),
one attempt and no automatic restart. The ceiling is **0.5 allocated GPU
hours and 8 requested CPU-slot-hours** if the entire allocation is used;
actual SCC SU charges remain unknown. Set a 26-minute work deadline
and earlier graceful-stop margin in the eventual runtime wrapper. The
short Stage P and scout timings make this a plausible *candidate*, not
a guaranteed completion time. Queue suitability must be checked for
this exact request before selection or submission.

Require a fresh `pquota rise-batteries` and filesystem-free-space snapshot.
The 2026-09-30 `/project` snapshot was 23.63/50 GB used, while `/projectnb`
was 46.32/50 GB; it is historical evidence, not current admission. Place
persistent outputs under `/project`. Propose a 1.5-GiB stop and 2-GiB hard
cap **for each of persistent and scratch**, with at least 3 GiB free
where each writes. Check both paths during the job, retain partial files
and logs on any failure, and record byte totals by phase and type. No
cleanup or guard reset should silently turn one attempt into a retry.
The prior permission to proceed with an unknown SU balance applied to
the completed paired scouts only; a selected fixture must make its own
cost decision.

## Acceptance evidence

The technical verdict is **pass** only when all of these hold:

- All 20 common checkpoints are correct for step/time/part/FEP state,
  their hashes remain unchanged after both arms, and the common logs
  show no exchange.
- The 40 copied checkpoint hashes match their sources; 40 TPRs and
  `mdout.mdp` files satisfy the CPU branch checker with no preprocessing
  warnings. Every arm starts from the registered checkpoint, not a fresh
  TPR start or regenerated velocities.
- Baseline ends at step 3,100 and shows zero exchange. HREX ends at
  step 2,600 and shows exactly three rounds at 1,500/2,000/2,500,
  attempted coverage of every neighboring pair, and one consistent
  final state/walker permutation across all ranks. Accepted swaps are
  recorded without a pass threshold.
- Every state has the expected output cadence and complete all-state
  energy/DHDL labels, finite numeric records, a final checkpoint and
  coordinates, and an internally consistent part-numbered post-branch
  trajectory. Preparation and arm outputs remain separate; an optional
  branch-boundary record occurs at most once per tree. Record the actual
  `.partXXXX` names rather than assuming a filename in advance.
- Each phase shows 20 matching MPS clients on the allocated GPU, and
  MPS cleanup is confirmed. Hash the saved output manifest, retain
  source/argument/phase timing records, and obtain `qacct` with
  `failed=0`, `exit_status=0`, actual host/PE/slots and walltime. If
  accounting is delayed, status is **pending**, not pass.

A missing checkpoint, warning, broken ancestry, wrong first exchange,
resource-cap breach, incomplete output, or nonzero accounting is a failed
technical attempt. Do not patch its files and call it passed; review the
failure before proposing a fresh package. A pass would qualify the live
fan-out mechanism only. It would not choose production preparation,
retained duration, repeat count, a useful-effect threshold, or extend the
historical 15-ns F64A pilot.

## Decision still required

The [non-submitting SCC preflight package](f64a_c2_branch_fixture_preflight_package.md)
has passed on user-supplied SCC evidence. The
[guarded runtime candidate](f64a_c2_branch_fixture_runtime_candidate.md)
has a user-supplied SCC static review pass marker. An
[inactive execution release candidate](f64a_c2_branch_fixture_execution_release_candidate.md)
has been sealed locally for separate static SCC review. A separate, explicit
selection of that bounded fixture and its unknown-SU condition is
required before a submission command becomes active.
