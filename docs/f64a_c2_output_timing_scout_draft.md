# C2 F64A output and paired timing scout — design draft

Prepared 2026-09-29. This develops the [C2 arm definition](f64a_c2_arm_definition_draft.md)
and [precision/resource analysis](f64a_c2_precision_resource_draft.md). It is a
**candidate technical design**, not a selected cluster attempt, production
protocol, budget or authorization. The user will operate SCC; this document
does not instruct an agent to log in or submit a job.

**Subsequent result, 2026-09-30:** A separately selected implementation of
this bounded pair completed and passed technical/accounting review; see the
[baseline](f64a_c2_scout_baseline_result.md) and
[HREX](f64a_c2_scout_hrex_result.md) results. The measured rates and
output sizes now inform the
[post-scout resource sensitivity](f64a_c2_precision_resource_draft.md).
The historical candidate text below remains a design record, not a new
execution instruction or a production selection.

## Why Stage P storage cannot be carried forward

The accepted four-ps Stage P attempt contains 615 files and 501,704,465
logical bytes, including 231,039,436 bytes of checkpoint text dumps and
47,842,536 bytes of compressed trajectories. It archived complete first-phase
state directories and wrote full-system coordinates every 200 steps = 0.4 ps.
Its 614-file checksum list was created before its own JSON was written.
These bytes establish a format and order-of-magnitude check, not a production
byte rate. Preserve the whole Stage P package without deletion or mutation.

The user-reported `/project/rise-batteries` quota has 26.77 decimal GB headroom
and the filesystem has about 32 GiB free; `/projectnb/rise-batteries` has only
3.68 decimal GB quota headroom. Both are shared resources whose usage can
change. `/project` is a candidate home for curated future C2 data, while
job-local scratch can serve as temporary workspace. The admission check must
use fresh quota and `df` results and reserve space for failed attempts.

## Candidate scientific output contract

This is a **proposed measurement setting**, common to both arms. It changes
output frequency from Stage P and from the historical estimates-only MDP, but
does not change the physical model. A CPU grompp comparison must verify every
physical MDP/TPR field and the 20-state lambda vector before any scout.

| Record | Candidate setting | Purpose and check |
| --- | --- | --- |
| Foreign-lambda energies and dH/dlambda | `calc-lambda-neighbors=-1`; `nstcalcenergy=500`, `nstdhdl=500` = 1 ps | Preserve all 20 evaluated states at each sampled frame for MBAR; verify labels, finite matrix and exact time grid. The 1-ps interval matches the historical intended density, not Stage P's 0.2-ps technical density. |
| Energy file | `nstenergy=500` = 1 ps | Keep matching potential/temperature diagnostics. Verify the EDR is readable and the energy/derivative times align. |
| Log | `nstlog=5000` = 10 ps | Retain performance, exchange and failure evidence without Stage P's dense technical log stride. |
| Full-system compressed coordinates | `nstxout-compressed=25000` = 50 ps; `compressed-x-grps=System`; retain default `compressed-x-precision=1000` unless exact-r6 preflight shows a reason to change | Keep protein, waters, ions and box information for occupancy and local geometry. Check atom count/order, frame times, box and endpoint identity against topology/TPR. Do not substitute protein-only coordinates for a hydration analysis. |
| Full-precision trajectory | Verify `nstxout=nstvout=nstfout=0` in `mdout.mdp` | No routine TRR force/velocity stream is needed for the registered endpoints. |
| Checkpoints | Candidate `mdrun -cpt 15` minutes, with final and previous binary checkpoint retained during active runs | Validate step, time and lambda state. Stage P already qualified synchronized resume; this scout has no planned restart. Keep outputs unchanged while appending; archive final checkpoint and a compact checkpoint audit after completion. |
| Exchange record | Baseline `-replex 0`; HREX candidate `-replex 500` = 1 ps, with a registered `-reseed` | Preserve per-round attempts, accepted pairs and the state-to-walker permutation across all restarts. The exchange interval is a **candidate for timing**, not yet selected for C2 science. |

GROMACS 2025.3 documents the distinct coordinate, energy and free-energy
output controls, and that `calc-lambda-neighbors=-1` writes all lambda
values for MBAR: [MDP options](https://manual.gromacs.org/documentation/2025.3/user-guide/mdp-options.html).
Its [mdrun documentation](https://manual.gromacs.org/documentation/2025.3/onlinehelp/gmx-mdrun.html)
describes periodic checkpoints and the previous-checkpoint backup. Its
[restart guidance](https://manual.gromacs.org/documentation/2025.3/user-guide/managing-simulations.html)
explains why all append-target outputs must remain intact until a checkpoint
continuation is finished. The 50-ps interval is for snapshot occupancy and
contact/torsion summaries; it **cannot resolve short water residence times**.
Whether it sufficiently resolves the predeclared descriptors must be decided
before production, using the technical scout and a structural-method review.

No routine full-text `gmx dump -cp` for every state and every phase is proposed
for future production. The binary `.cpt`, validation result, selected small
metadata, command/version records and hashes can provide restart evidence.
The Stage P `before-restart/` full-tree copy was necessary to prove that
technical restart; a future C2 policy should retain append-safe raw outputs,
per-phase hashes and a final checkpoint, rather than duplicating whole growing
trajectories at every scheduler boundary. Exact retention and recovery steps
need an implementation review; no files may be trimmed while GROMACS expects
to append to them.

## Illustrative trajectory capacity screen

At Stage P's 0.4-ps stride, 20 final files plus 20 archived first-part files
contain roughly 300–340 full-system frames. Dividing their 47,842,536 bytes
gives about **0.14–0.16 MB per frame** for this system and XTC precision.
For a 50-ps candidate stride, the following is a *trajectory-only* scale
calculation, assuming the same bytes/frame, the baseline and HREX each retain
the displayed duration, and no duplicate first-part archives:

| Sensitivity row | Ladders across both arms | ns/state | Approximate XTC bytes across both arms |
| --- | ---: | ---: | ---: |
| A | 6 | 8 | 2.7–3.1 GB |
| B | 10 | 16 | 9.0–10.2 GB |
| C | 16 | 32 | 28.7–32.8 GB |

The equal-cost primary comparison may give HREX a different duration, so
these are **not** C2 forecasts. They omit initial/final frames, prepared
inputs, TPRs, checkpoints, raw energy, logs, analyses, failed attempts and
copies. Row C already exceeds the reported `/project` quota headroom on
coordinates alone. Row B still needs a whole-study storage model and safety
reserve. A measured byte rate, production duration/repeat decision and fresh
quota determine any actual cap; moving data to `/project` is not a substitute.

## Candidate bounded two-arm timing scout

The sole purpose is to measure baseline and HREX rates and bytes with the
same 20-state physical inputs and candidate output settings. It will yield no
F64A effect estimate, pilot continuation or C2 observation. **Nothing here is
an executable package or submission.** A separate review and selection under
`CLAUDE.md` rule 6 would be needed before any GPU work.

| Field | Candidate technical boundary |
| --- | --- |
| Source | Previously inventoried F64A folded apo-2SH `r0` system and its 20 lambda-aware `em.gro` starts; make new technical TPRs in exact r6 using the output settings above. Do not restart from Stage P trajectories/checkpoints. |
| Pairing | Hash one TPR per state; copy the identical 20 TPRs into isolated baseline/HREX attempt trees. Only launch exchange settings differ. |
| Layout | One L40S, `omp16`/16 CPU slots, 20 one-thread MPI ranks, private MPS, one host; recheck queue and compute-node access. |
| Target | 50,000 steps = 100 ps/state for each arm, with no scientific discard or analysis. A full result would contain ~100 all-state energy records and ~3 full-system coordinate frames per state. |
| Exchange | Baseline disabled; HREX candidate 500-step neighbor attempts and fixed seed, with complete permutation validation. |
| Allocation cap | At most one attempt per arm, requested 2-hour hard walltime each: at most 4 allocated GPU-hours and 64 requested CPU-slot-hours in total. No automatic retry. This is a draft cap, pending queue limits and actual SU accounting. |
| Storage cap | Candidate 1 GiB per attempt on both scratch and the persistent copy, including inputs and retained logs; prospective aggregate at most 2 GiB. A predeclared lower stop threshold and graceful-stop behavior must be implemented and reviewed before submission. |
| Runtime checks | All 20 states must reach the same final step, energy/coordinate grids must align, no missing/NaN all-state values, expected exchange/identity history must match, 20 simultaneous MPS clients and cleanup must be recorded, and all retained outputs must be hashed. |
| Accounting | Record full allocated start/end time and `qacct`/SU for each arm, CPU slots, walltime, file bytes by type, startup/validation time, and per-state GROMACS performance. Report setup-inclusive `100 ps ÷ allocated GPU-hours` separately from dynamics-only throughput. |
| Incomplete attempt | Save hashes, checkpoint steps, elapsed cost and failure reason. Treat timing as censored/inconclusive if either arm cannot reach 100 ps within its cap; do not infer a production rate from Stage P or silently extend/retry. |

Both scout jobs use equal **time per state** only to measure their separate
costs. The scientific C2 comparison later converts a fixed equal allocated
GPU budget into possibly different retained durations using the measured
rates and full preparation/failure allowances. The 100-ps scout duration is
too short for convergence or an F64A free-energy result. It also does not
measure new-realization preparation, which requires a separate accounting
line. The candidate order is baseline first; run HREX only after the baseline
passes its technical checks. If there is no complete pair, there is no
matched rate comparison and no automatic replacement attempt. Before
selecting this scout, a CPU-only package should produce the
exact MDP/TPR diff, command/seed list, output-cap enforcement, quota check,
restart behavior and reviewer-visible submission guard. The SU tariff and
current allocation balance remain unverified.

## Decision after the scout

If both technical arms complete, use their measured allocated GPU-hours,
output bytes and GROMACS performance to update the [precision/resource table](f64a_c2_precision_resource_draft.md).
Then decide the scientifically useful effect/precision target, fresh-start
ancestry, paired or unpaired uncertainty model, retained durations/repeats,
coordinate cadence, complete storage and compute caps, and exact stop rules
before seeking any production selection. If one arm fails or the coordinate
data cannot support the planned structural summaries, revise the design
explicitly; do not use the favorable arm alone to choose a production rate.

The first implementation step is the
[sealed CPU-only input candidate](f64a_c2_scout_cpu_package.md). It prepares
identical baseline/HREX TPR copies and has no GPU runtime or submission path.
Its [v3 CPU preparation/review](f64a_c2_scout_cpu_result.md) has now passed
on user-supplied SCC evidence; this does not admit the GPU scout.
