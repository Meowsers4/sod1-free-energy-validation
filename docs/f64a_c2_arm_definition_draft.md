# C2 draft: fresh F64A independent-window versus HREX arms

**Subsequent result, 2026-10-03:** The [bounded live checkpoint-branch fixture](f64a_c2_branch_fixture_result.md)
passed. Its shared no-exchange preparation and isolated arms are now
technically qualified at the fixture scale. See the
[post-fixture design review](f64a_c2_post_fixture_production_design.md) for
the local source audit and remaining production choices. Earlier pending
statements below are retained as design history.

Status: design draft begun 2026-09-29. This defines the intended scientific
contrast for [work package C2](publication_research_plan.md#c2-fresh-f64a-development-comparison).
It is neither a preregistration nor an executable simulation specification.
No C2 preparation, GPU scouting, production, retry or submission is authorized
by this document. The [short protein Stage P result](gromacs_protein_runtime_result.md)
establishes one-GPU exchange/restart mechanics for one F64A realization, not a
production duration, throughput estimate or comparison result.

## Question and unit

At a matched total allocated GPU cost, does enabling neighbor Hamiltonian
exchange reduce the observed temporal movement and independent-realization
spread of the **folded-leg F64A mutation free-energy estimate**? The experimental
unit is a complete, independently initialized 20-state F64A folded ladder.
Twenty lambda states and exchanging walkers within one ladder are not 20
independent repeats. No unfolded leg is included in this C2 contrast, so its
result is not a folding ΔΔG or experimental validation.

The shared physical-protocol candidate comes from the unchanged
`config/pipeline.yaml` (SHA-256
`af866a49f017d40af13101b561906cb049e336be1741d2d2255ce50b2e9dde29`)
and the exact-r6 Stage P source checks. It is common to both arms:

| Property | Common candidate setting |
| --- | --- |
| Protein | Mature 153-residue F64A folded monomer, apo, Cys57/Cys146 reduced; no Cu/Zn |
| Force field and solvent | pmx `amber99sb-star-ildn-mut`, TIP3P, 0.15 M ion target, 1.2 nm solvent padding |
| Ensemble and dynamics | 298.15 K, NPT with GROMACS `ref-p=1.0` bar, stochastic dynamics, 2 fs step, hydrogen-bond constraints |
| Nonbonded and alchemy | PME, 1.0 nm cutoff, Beutler soft core (`sc-alpha=0.3`, `sc-power=1`, `sc-sigma=0.25`, `sc-coul=yes`), all-state energy evaluation |
| Lambda vector | `0.0000 0.0588 0.1176 0.1765 0.2353 0.2941 0.3529 0.4118 0.4706 0.5294 0.5882 0.6471 0.7059 0.7647 0.8235 0.8824 0.9200 0.9500 0.9750 1.0000` |

Before registration, compare the generated arm MDP/TPR fields directly; this
table is a design anchor, not a substitute for a byte-level input inventory.
The config key is named `pressure_atm` but `src/fep/pmx_engine.py` writes its
numeric value directly to GROMACS `ref-p`, whose unit is **bar** in the
[2025.3 MDP documentation](https://manual.gromacs.org/2025.3/user-guide/mdp-options.html).
Thus the historical and Stage P generated value `1.0` means 1.0 bar in
GROMACS. Keep the actual value common across C2 arms and document this unit
label before registration; do not silently change a physical parameter in
only one arm.

## Arm matrix

| Design feature | Fresh independent-window baseline | Fresh HREX intervention |
| --- | --- | --- |
| System and physical model | F64A folded apo-2SH, one common pmx hybrid system per realization; same topology, 153-residue monomer, solvent/ions, force field, temperature, pressure, constraints and soft-core settings | Exactly the same system and settings within the corresponding realization |
| Lambda ladder | The 20 ordered values from `config/pipeline.yaml:fep.lambda_vector`; local state 0–19 fixed in each directory | The same vector and directory order |
| Build and input | Exact r6 GROMACS 2025.3 MPI/CUDA SIF; one verified prepared system and 20 lambda-aware state starts per realization, copied into isolated arm trees | The same SIF and byte-identical **state starts** within each paired realization; equal-cost production TPRs may differ in `nsteps`, so compare their effective physical/output fields and ancestry directly |
| Launch shape | 20 one-thread ranks on one admitted L40S host, `-multidir state00 ... state19`, with exchange disabled (`-replex 0`) | Same rank/GPU/CPU/MPS placement and ordered `-multidir`; neighbor exchange enabled with a separately registered positive `-replex N` and `-reseed S` |
| Energy and coordinates | All-state foreign-lambda energies and the same energy/coordinate cadence and retention policy | Same outputs plus attempted/accepted exchange and state-to-walker history |
| Estimator | Same MBAR construction, state labels, temperature, equilibration discard, correlation treatment and time splits | Same estimator and rules; classify energies by fixed lambda state and reconstruct walker paths separately for exchange diagnostics |
| Scientific factor | No exchanges | Exchanges between neighboring Hamiltonians |

GROMACS 2025.3 defines `-replex 0` as the disabled setting and a positive
`-replex` interval as periodic exchange attempts. Its multisimulation guide
allows related lambda simulations in one ordered `-multidir` launch even when
they do not exchange. The controlled baseline therefore uses the **same coupled
MPI launch**, image and allocation layout rather than the historical one-window
array. This holds executable and scheduler architecture fixed; communication
and synchronization caused by exchange are part of the measured intervention.
Sources: [2025.3 mdrun options](https://manual.gromacs.org/2025.3/onlinehelp/gmx-mdrun.html),
[multisimulation and load-balance guide](https://manual.gromacs.org/2025.3/user-guide/mdrun-features.html),
[Hamiltonian exchange reference](https://manual.gromacs.org/2025.3/reference-manual/algorithms/replica-exchange.html).

The qualified Stage P candidate layout is one L40S, `omp16`/16 CPU slots,
20 explicit oversubscribed MPI ranks on a common 16-CPU affinity mask, private
MPS and one host. It is the **first C2 layout candidate**, not an admitted
production performance setting. The Stage P 100-step exchange interval,
2,000-step length and output strides were technical-test settings, not C2
science settings. The old four-GPU C1 proposal is superseded for this candidate.

## Fresh input and repeat ancestry

For each new realization `r`, start from a documented, common F64A apo-2SH
protein-source family and prepare a new hybrid system with a recorded
realization-specific ion-placement seed under the frozen physical protocol.
Audit actual water/ion coordinate differences; the existing builder's
`gmx solvate` step may reproduce the same water template across repeats.
Prepare and hash each of its 20 lambda-aware state starts once. Branch
**that realization's identical state inputs and initial velocities** into
two isolated arm trees before arm-specific dynamics. Record source structure,
topology/include hashes, box/ion placement,
atom order, local lambda index, TPR/MDP hashes and deterministic preparation,
velocity and exchange seeds. Seeds are distinct across realizations; paired
arms share their preparation and initial-state seeds. HREX has an additional
registered exchange seed; the baseline records exchange disabled. This pairing
is an input-control design, not an assumption that outputs are statistically
paired after exchange. The analysis must justify any paired inference separately.

No Stage P 4-ps trajectory, checkpoint or old 15-ns F64A continuation is a C2
baseline observation. The Stage P package and historical r0 source provide
ancestry/protocol evidence only. If all fresh realizations use one protein
conformation family, the resulting claim remains conditional on that start
family; independent solvent boxes alone do not establish conformational
coverage. No alternative start family is selected in this draft.

## Common analysis and evidence rules

Use each state directory as the fixed-lambda sampling record. For HREX,
archive the ordered exchange attempts, accepted swaps and complete
state-to-walker permutation at every registered round, including across a
whole-ladder restart. Analyze free energies from energy samples labeled by
sampled lambda state; reconstruct walker paths only for exchange/mixing and
coordinate diagnostics. Baseline permutations are identities. Check that both
arms evaluate all 20 states with finite energy matrices and matching labels.

The subsequent registration must state the common preparation interval,
retained duration or equal-cost stopping rule, early/late split, MBAR
uncertainty/correlation method, incomplete-ladder policy, structural retention
cadence and primary F64A development summaries **before** inspecting new
trajectories. Report per-realization estimates and both arms' failures and
actual cost. Exchange acceptance and round trips are diagnostics, not a
substitute for the free-energy stability/reproducibility endpoints. A favorable
or unfavorable C2 outcome can both inform the later frozen prospective panel;
neither changes the historical gate.

## Decisions still needed before a C2 registration

1. **Fresh-start protocol:** exact source structure/conformation family,
   independent-system seed mapping, and the shared no-exchange
   preparation/checkpoint branch chosen in the
   [post-scout decision draft](f64a_c2_design_decisions_2026-09-30.md).
   Its length and exact restart mechanics remain to be validated.
2. **Exchange, preparation and output settings:** register the positive
   post-branch neighbor `-replex` interval, exchange-seed list,
   steps/checkpoint cadence, all-state energy stride and coordinate cadence.
   The Stage P values do not supply these automatically.
3. **Measured resource model:** the accepted paired 100-ps technical scout
   supplies short-run baseline/HREX rates on the proposed layout, but
   long-run rate uncertainty, new-realization preparation, CPU setup,
   production storage slope, failure allowance and billed SU remain open.
   The 146-second/4-ps Stage P run is not a production throughput benchmark.
4. **Finite C2 size:** duration and independent-realization count justified by
   a useful effect and expected precision, followed by explicit per-arm cost,
   attempt and stop caps. The historical 9/15-ns pilots and old two-start
   6-ns draft are not defaults.
5. **Frozen analysis and admission:** estimator/time-split details, failure
   treatment, output/provenance validators and a separate explicit user
   selection under `CLAUDE.md` rule 6. An unresolved field blocks an executable
   C2 package, not continued CPU/design work.

The [precision/resource table](f64a_c2_precision_resource_draft.md) now
includes the [accepted paired scout](f64a_c2_scout_hrex_result.md) as a
short-run rate anchor alongside explicit extrapolation scenarios. The
[output and timing-scout design](f64a_c2_output_timing_scout_draft.md)
records candidate coordinate/energy settings, not selected C2 production
settings. A declared useful-effect target, duration-dependent variance,
production storage and complete resource budget are still needed. Nothing
in this draft submits a cluster job or changes the historical
`config/pipeline.yaml` protocol.
