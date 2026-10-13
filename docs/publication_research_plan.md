# Prospective sampling comparison — publication research plan

Prepared 2026-09-18 at the user's request. **Planning document, not a registration
or authorization to submit simulations.** Vlasov will review the work later;
mentor recruitment/review is not a prerequisite for the planning and CPU work
described here. The completed campaign remains stopped at 15 ns. The historical
gate, exclusions, configurations, reports and release stay intact.

**Progress note, 2026-09-29:** The bounded one-GPU, 20-state F64A folded-protein
technical qualification passed; see [the Stage P result](gromacs_protein_runtime_result.md).
The fresh baseline/HREX C2 arm definition is now a
[design draft](f64a_c2_arm_definition_draft.md). Its scientific duration,
independent-repeat count, output cadence and equal-cost budget remain open.
The first [precision/resource sensitivity table](f64a_c2_precision_resource_draft.md)
quantifies those open choices with historical variance and timing anchors,
while explicitly leaving C2 rates and the useful-effect target unresolved.
No C2 production arm has been registered or selected.

**Progress note, 2026-09-30:** The separately selected 100-ps F64A C2
baseline/HREX technical scout pair completed and passed its saved-output and
accounting review on user-supplied SCC evidence; see the
[baseline](f64a_c2_scout_baseline_result.md) and
[HREX](f64a_c2_scout_hrex_result.md) records. The
[resource sensitivity draft](f64a_c2_precision_resource_draft.md) now uses
their short-run rates to show equal-cost stress cases. This resolves the
previous lack of arm-specific technical rate measurements, while long-run
rate uncertainty, storage growth, billed SU, a useful-effect threshold and
finite C2 duration/repeats remain open. No C2 production arm is selected.
The subsequent [C2 design-decision draft](f64a_c2_design_decisions_2026-09-30.md)
records the user's choice of one shared no-exchange preparation before an
isolated baseline/HREX checkpoint branch; its length and implementation
remain unselected.

**Focus revision, 2026-09-18:** the controlled protein sampling comparison is
the primary study. Diagnostics are a prespecified secondary assessment; structural
mechanism is optional. Cross-protein testing is an evidence-driven extension.
The completed CPU discovery and known-answer studies remain supporting evidence;
they are not tasks to repeat before proceeding. Scope is determined by the
scientific question, precision and measured resources, not an assumed limit on
the user's pace or ability. There is no calendar estimate or admissions deadline
in this plan. Compute accounting remains necessary for a fair method comparison.

## 1. Objective and intended contribution

Primary question: **at matched computational cost, does a specified sampling
intervention improve the temporal stability and independent-run reproducibility
of protein-mutation free-energy estimates?**

Secondary question: **do conventional diagnostics reflect those improvements
and the instability that remains?** The recommended comparison to qualify is
independent λ windows versus Hamiltonian replica exchange (HREX) on the same
ladder. No protein arm is yet selected or resource-admitted.

The present evidence supports a SOD1 methods-and-limitations case study. The
proposed extension earns a broader claim only by testing frozen analyses on new
cases. Neither a successful F64A rescue nor beating the project's historical net
hysteresis metric alone establishes a new general method.

The intended contribution is a quantified, prospective comparison: effect size,
uncertainty, variation across mutations, failure rate and actual cost. Familiar
warnings that overlap does not guarantee equilibrium are motivation, not the
novel result. Developing a universal stopping rule, inventing an algorithm and
proving a structural mechanism are not requirements of the core paper.

| Priority | Question | Evidence needed |
| --- | --- | --- |
| Primary | Does the intervention improve observed stability and reproducibility at matched cost? | Fresh controlled protein arms and a frozen prospective panel, with all failures/costs reported |
| Secondary | Which diagnostic changes accompany or anticipate remaining instability? | Prespecified observables and time splits; bounded associations, not a trained general classifier |
| Optional mechanism | What structural changes could explain the behavior? | Retained coordinates and reproducible associations; causal claims need a distinguishing perturbation |
| Conditional extension | Does the comparison transfer beyond SOD1? | A separately admitted external protein using frozen methods and analysis |

Keep three questions separate:

1. **Stability:** do estimates change with more sampling or independent runs?
2. **Computational accuracy:** do estimates agree with an independently justified
   equilibrium reference for the same Hamiltonian?
3. **Experimental accuracy:** does a folding ΔΔG agree with a state/construct-
   matched experiment?

The core plan addresses question 1. The completed small known-answer model
addresses question 2 under constructed assumptions and belongs in the supporting
evidence unless essential to a specific claim. It does not establish protein
accuracy or calibrate protein intervals. Question 3 is a separate project; the
heterogeneous historical benchmark cannot answer it.

## 2. Scope and finite study size

| Component | Proposed scope | Role |
| --- | --- | --- |
| Existing archive | All usable completed records, with cohorts/protocols separated | Discovery and historical evidence only |
| Known-answer CPU model (complete) | Preserve bounded v2 and rejected v1; no additional model required | Supporting demonstration with a computable answer; further calibration only for a specific accuracy/coverage claim |
| Protein development experiment | F64A only; fresh baseline plus **one** selected intervention | Establish technical feasibility and freeze the transferable protocol |
| Prospective SOD1 evaluation | Initial design: four new charge-neutral mutations at four sites, five independent full-ladder realizations per method, two methods | Primary controlled comparison within the tested SOD1 panel; final size justified before registration |
| External-system extension | One additional protein, four mutations at distinct sites, same two frozen methods and five realizations | Stronger transfer claim; separate admission after the SOD1 test |
| Optional mechanism | At most two predeclared local structural descriptors plus a backbone control | Supporting interpretation; absence of a clean mechanism does not invalidate the primary comparison |

These counts are **planning choices, not a demonstrated power calculation**.
Five realizations improve estimation of within-case scatter but do not turn four
mutations into a large population study. If precision planning shows the design
cannot resolve a useful effect, revise it before registration or retain descriptive
claims. Do not add repeats selectively to mutations with promising results.
Four mutations are a starting design, not a ceiling based on presumed student
capacity. Expand the panel before registration if precision or mutation coverage
requires it; state how the added cases address the scientific question. A later
expansion after viewing outcomes must be labeled a new stage and separately frozen.

The primary molecular observable is the **folded-leg mutation free energy**.
No new unfolded legs are included in the core comparison; consequently no new
folding ΔΔG or variant pathogenicity predictions result. The historical folded
and unfolded data may be analyzed separately as discovery material.

Out of scope: VUS triage, charge changes, metals/holo SOD1, a new force-field
survey, many soft-core parameter combinations, indefinite trajectory extension,
clinical classification and new experimental measurements. The second protein
is a scope extension requiring its own structure/panel configuration; do not
repurpose the SOD1 mature-numbering offset or silently generalize the live engine.

## 3. Work package A — reconcile conclusions and complete discovery analysis

**Current status:** conclusions are reconciled in
[the interpretation correction](conclusion_reconciliation_2026-09-18.md).
The pasted λ summary was independently recalculated from the saved audit JSON.
The fresh-output A1 lambda characterization is now implemented and complete; see
[results](f64a_lambda_comparator_results.md), the
[machine-readable specification](f64a_lambda_comparator.yaml), and the
[diagnostic/prior-art table](diagnostic_comparator_specification.md). It validates
all 60 frozen NPZs and reports actual-lambda neighbor and fixed-pair observables.
This completes the bounded discovery/comparator deliverables, not prospective
validation or a stopping rule. BAR/MBAR agreement remains an optional future
sensitivity using shared samples; TI is excluded because the saved matrices do
not contain genuine derivative data.

### A1. Complete the exploratory λ characterization

Use the immutable 60-NPZ v2 inventory and saved report; write new outputs to a
fresh namespace. Do not overwrite `results/cpu_audits/f64a_raw_energy_v1/`.

- Plot actual λ, not just window number. Show each repeat and both 9–12/12–15 ns
  blocks, both neighbor directions, signs as well as magnitudes, and full-block
  results before suffix sensitivities.
- Report window-median summaries and pooled-record summaries with explicit
  denominators. The 348 records include 120 sampled-state energy records; only
  228 are neighbor differences. Two directions share configurations and are not
  independent replications.
- Show drift, slope, scatter, overlap and selected suffix length side by side.
  Normalized drift is descriptive, not a stationarity test or effective sample size.
- Use existing all-state energies to evaluate **fixed λ-pair energy differences**
  on each sampled path, so a future denser ladder can retain comparable observables.
  Select a small common evaluation grid from the historical ladder before future
  runs. Divide-by-spacing summaries may be a sensitivity analysis; they are not
  identical observables when the alchemical Hamiltonian is nonlinear.
- Do not choose a universal overlap/drift threshold, perform row-wise significance
  tests across correlated windows, or infer per-window MBAR error contributions.

**Acceptance:** exact input hashes/metadata reconcile; every requested path/block
appears; endpoint missing-neighbor entries are explicit; all plot values trace to
the new report. These conditions are met in the A1 result. This is an exploratory
audit, even though it is implemented with refusal-on-overwrite and hash checks.

### A2. Establish the comparator and prior-art table

Compare the historic net diagnostic with adjacent overlap, temporal block movement,
between-run dispersion, conditional estimator uncertainty and absolute/local
hysteresis summaries. BAR/MBAR agreement is a sensitivity check sharing the same
samples, not independent equilibrium confirmation. TI is included only if genuine
derivative data are available and its quadrature is specified; do not invent it
from a different saved observable.

For each diagnostic record: mathematical definition, direction of warning, required
data, analysis cost, known limitations and primary citation. Check whether the
historical aggregate is used externally before calling its failure a field-wide
problem. A cancellation identity alone is not a novel convergence result.

**Deliverables:** exploratory λ report/figure, diagnostic specification table,
and a one-page comparison with Wells 2021 and free-energy analysis best practices.
If no credible transferable question remains, finish the bounded case-study paper
rather than automatically expand compute.

## 4. Work package B — completed supporting calibration

**Current status:** complete in the bounded v2 implementation; see
[results](known_answer_model_results.md) and the frozen
[specification](known_answer_model_v2.yaml). Independent quadrature implementations
agree to approximately `1e-15 kT`. Eighty registered experiments were retained,
including twelve held-out metastable baseline failures under the frozen
decorrelated-sample minimum. Neighbor exchange improved availability and RMSE in
the constructed metastable regime, but nominal interval coverage remained 0.75.
This is a model demonstration, not a protein result or intervention selection.

Use the existing model to explain a concrete limitation or to verify a necessary
analysis assumption. Preserve its fixed regimes, seeds, correlation treatment,
reference checks, failures and conditional complete-case statistics. Its equal
potential-evaluation budget is not identical to a protein GPU-cost comparison.
The constructed pathway was chosen to make exchange a meaningful intervention;
favorable performance there is not independent evidence that it will help SOD1.

**No new calibration is on the critical path.** Add a new model or model regime
only if a precise manuscript claim needs a known-answer check not supplied by
v2. Such additions need their own frozen design and unused evaluation data;
do not tune v2 retrospectively or transfer its warning thresholds to proteins.
If a protein accuracy/coverage reference remains unavailable, omit those claims
and report observed stability/reproducibility. Keep the toy model in a supplement
unless it is necessary to understand the main protein result.

## 5. Work package C — qualify the primary protein comparison

Do not treat λ localization as a causal selector. Choose an intervention using
the question it can answer, technical feasibility and a measured resource model.

| Candidate | Controlled contrast | What a favorable result supports | Limitation/admission condition |
| --- | --- | --- | --- |
| Denser schedule | Add intermediate λ values while preserving common states, endpoints and soft-core model | Better estimation/reproducibility at the tested cost | Independent common-state dynamics are unchanged; smaller adjacent differences or higher overlap alone are insufficient |
| Hamiltonian replica exchange | Same λ states, physical model and estimator; enable exchanges | Benefit of the exchange-enabled sampling protocol | Requires a working MPI/multisim build and coupled job allocation; a ladder's exchanging walkers are not independent repeats |
| Different starts | Same schedule/method/preparation with justified alternative coordinates | Sensitivity to the admitted start families | No alternate is currently selected; chain B similarity does not establish a new basin |
| Soft-core change | Preserve endpoints; change one specified intermediate-state potential | Sensitivity to the alchemical pathway | Separate from schedule density; validate endpoint identity and topology/energy behavior |

**Recommended design priority:** assess feasibility of a baseline versus
Hamiltonian-exchange comparison on an identical ladder. This directly changes
communication between states and targets a distinct question from adding states.
It is a proposed priority, not evidence that exchange will solve F64A or cross
all slow modes. This is the primary design direction, not a menu of four arms
to run in parallel. If the cluster/build contract cannot support it, resolve the
build/scheduler requirements or explicitly redesign the scientific contrast.
A density-only comparison is a legitimate narrower study of estimation efficiency,
but changes the question and cannot inherit the enhanced-sampling claim. Do not
substitute a new engine or add soft-core/start factors automatically.

The two-start draft is retained as a reserve option, not the selected next arm.
It need not wait for a “λ fix” if justified starts become available. Its old
6 ns and 370 GPU-hour numbers are not this plan's duration or budget.

### C1. Technical qualification

Before any production, separately specify and admit bounded technical work:
exact build/hardware, scheduler granularity, model/endpoints, active λ identity,
independent realization seeds, checkpoint/resume behavior, energy export,
coordinate export, accounting and storage. Exchange additionally requires
replica/state assignment histories, energy-to-state alignment, permutation-aware
coordinate analysis, and exchange/mixing diagnostics. Exchanges require compatible
systems within one ladder; independently solvated realizations remain separate.

GROMACS documents MPI-based multisim exchange. This does not fit the standing
one-window-per-job contract without an explicitly approved separate scheduler
design; no modification of existing arrays is implied.
[GROMACS 2025.3 replica exchange documentation](https://manual.gromacs.org/2025.3/reference-manual/algorithms/replica-exchange.html).

**C1 status, updated 2026-09-21:** the first fail-closed qualification is recorded in
[`gromacs_exchange_feasibility_design.md`](gromacs_exchange_feasibility_design.md).
The standing CUDA binary has neither external MPI nor thread-MPI, so it fails the
exchange-build gate. The authenticated 2026-09-19 inventory found separate CUDA
and MPI executables but no combined build in the installed GROMACS 2025.3 tree. The
completed login-shell capture confirms that the L40S queue supports MPI parallel
environments. The selected build route is now a pinned project-owned Singularity image,
restricted first to one `mpi32` L40S host with 20 container-local MPI ranks and four
GPUs; see [`gromacs_hrex_singularity_plan.md`](gromacs_hrex_singularity_plan.md).
The definition is ready, but the SIF has not been built and GPU visibility/rank mapping
remain runtime qualification items. The outcome remains
"conditionally feasible, new build required," not a protein-arm or GPU authorization.
The earlier SCC-supported build request remains an unsent fallback.

### C2. Fresh F64A development comparison

Use two fresh arms and the same preparation/start distribution. Freeze the
baseline and the single intended factor; preserve force field, physical state,
construct, protonation, solvent/ions rules and estimator. Include all λ states.
Historical continuation paths remain context, never matched controls.
Run both fresh arms with the same qualified GROMACS/force-field build, with
exchange disabled for the independent-window arm. Match rank/GPU layout where
feasible; document remaining execution differences and include their overhead in
cost. Do not compare the new exchange build against historical serial-build data
and attribute the entire difference to exchange.

Choose finite duration and repeat count using the precision/resource exercise in
§7. F64A is development data even after a new registration. Freeze the final
method and analysis after this stage; no additional intervention is added to the
prospective panel after seeing its results.

**Exit:** a technically valid comparator and frozen protocol, including a negative
development result if still scientifically informative. A favorable F64A result
is not a prerequisite for the prospective panel: a qualified comparison can test
whether a negative development observation also occurs elsewhere. Technical
failure or inadequate precision requires correction/redesign before evaluation;
it is not evidence that exchange is scientifically ineffective. No automatic
extension follows a disappointing or inconclusive run.

## 6. Work package D — prospective protein evaluation

### D1. Select the SOD1 panel without new outcome information

Exclude all eight historical gate variants from the primary prospective panel.
Their outcomes have already informed the design. Existing records can remain
explicitly exploratory controls.

Shortlist from the current characterized, charge-neutral panel: **F45A** (another
aromatic deletion), **I35V** (conservative hydrophobic change), **G41S** (polar
addition), and **N86S** (polar shortening). These are candidate names, not admitted
systems or verified buried/exposed assignments. Audit their source identities,
actual hybrid net charge and previous simulation exposure. Use prepared-structure
descriptors to document burial and mutation size. Experimental ΔΔG values are not
selection targets and are not matched validation references.

If a candidate fails eligibility, record the reason and choose a replacement
from the same intended structural/chemical category before simulation. Freeze
all four sites, start provenance, inclusion/exclusion rules and model identities
together. If diversity cannot be achieved, narrow the generalization claim.

### D2. Freeze methods, runs and evaluation

Two methods × four mutations × five independent full-ladder realizations =
**40 ladders**. With the existing 20-state ladder this is 800 state trajectories
across both methods; a denser comparator changes that count. For exchange, the
experimental repeat is an entire independently initialized ladder, not a walker.
These counts describe the initial design. Final panel size, repeat count and
duration must follow the precision/coverage rationale in §7 before registration.
Four sites support a bounded case-panel comparison, not mutation-class response
models or a general stopping-rule validation.

Use the same start distribution across methods. If all realizations use one
protein start, label conclusions conditional on that start. Multiple independently
prepared boxes do not establish independent conformational coverage. More than
one justified start family is desirable but must not introduce arm-specific
preparation. No “equilibrium ensemble” label follows simply from multiple starts.

Freeze analysis before any prospective trajectory is examined:

- For each realization with retained duration T, compute early diagnostics from
  `[0, T/2)` only. Within that prefix compare its two quarters when defining an
  early temporal diagnostic. Use `[T/2, T)` as the disjoint later evaluation block.
  Exclude boundary duplication. Define T and every absolute time before submission.
- Primary temporal endpoint: `|ΔG_late − ΔG_early|` per realization. Report signed
  changes too. Summarize equal-weight case means, not pooled windows. This endpoint
  measures future instability, not error against truth; adjacent blocks may remain
  correlated and share preparation history.
- Co-primary reproducibility endpoint: within-case standard deviation of final-half
  ΔG across independent ladders, alongside all individual estimates. Report spread
  and uncertainty of the mean separately. Stable shared bias remains possible.
- Secondary diagnostic assessment: association of each frozen early diagnostic with
  later absolute movement, showing all cases and leave-one-site-out sensitivity.
  Do not train a multivariable classifier on four mutation sites. Threshold-based
  sensitivity/specificity is secondary and allowed only for a rule frozen on
  development data; count clustered outcomes appropriately.
  Toy-model thresholds are not protein thresholds. Diagnostic association or an
  attractive ROC curve is not a separate success criterion for the core study.
- The early estimate appears in the movement endpoint, so shared estimation noise
  can contribute to associations. Predeclare a sensitivity endpoint comparing the
  two quarters **within the later half**; it shares no frames with the early
  diagnostic. Correlation across blocks can remain. Do not interpret either
  association as proof that the diagnostic identifies a physical cause.
- Primary analysis policy: zero additional trimming after fixed preparation, with
  the declared correlation treatment. Fixed-25% and adaptive trimming are sensitivity
  analyses. Every cutoff is fitted on its own allowed interval: later data must
  not choose an early cutoff. No trimming rule is selected because it gives the
  desired answer.
- Secondary diagnostics: common-state fixed-pair energy movement, overlap,
  local/net hysteresis, selected counts, estimator agreement and structural
  descriptors. Native-ladder absolute sums/maxima are not directly comparable
  across different schedules; also compute a declared common-grid version.
- Freeze uncertainty methods for method contrasts before evaluation. Whole
  realizations stay together within cases; sites stay together for generalization.
  Report conditional case-level intervals and emphasize only four site groups.
  Repeated checkpoints/directions/methods do not increase the site sample size.
- Technical failures remain in the denominator and cost ledger. A missing ladder
  has no free-energy endpoint; report availability and complete-case contrasts,
  with the prespecified minimum complete-repeat requirement. Never drop a bad
  scientific result or replace a completed run because its estimate is inconvenient.

For case c and method m, define `M_c,m = mean_r |ΔG_late,c,m,r − ΔG_early,c,m,r|`
and `S_c,m = SD_r(ΔG_late,c,m,r)`. Report intervention-minus-baseline contrasts
for each quantity in kcal/mol, all case values, and equal-weight averages across
cases. Negative contrasts indicate less observed movement/dispersion. Ratios may
be secondary but are unstable near a zero baseline. Freeze interval construction
and dependence assumptions before evaluation; matching repeat labels alone does
not justify paired inference. These are sampling-performance endpoints, not
proof of computational or experimental accuracy.

**Interpretation:** broad improvement requires practically useful reductions in
both prespecified endpoints at the chosen budget, with uncertainty reported.
Mixed outcomes support endpoint-specific conclusions. A qualified method with
intervals excluding the predeclared useful improvement can support a bounded
negative conclusion; intervals spanning useful benefit and no benefit remain
inconclusive. A nonsignificant test alone does not establish equivalence or no
effect. Freeze effect/precision targets before execution. Do not select a success
endpoint after seeing the panel or hide availability failures behind complete-case
improvements. Increased exchange acceptance or round trips alone is not success.

### D3. External protein extension

First establish what the SOD1 comparison answers and what remains uncertain.
An external protein is justified when transferability is the key unresolved
question and the protocol/analysis are qualified. It can test transfer of a
positive, mixed or informative negative result; it is not restricted to a
favorable SOD1 outcome. If SOD1 is technically invalid or too imprecise to
interpret, resolve that issue rather than multiply systems.

Then admit one additional protein with a mature, well-documented
mutation-FEP setup, no metal parameterization requirement, available coordinates
and four eligible charge-neutral mutations at distinct sites. T4 lysozyme or
staphylococcal nuclease are **literature-screening candidates**, not selected
systems. Audit primary inputs and licensing before choosing either.

Keep the analysis and method contrast frozen. System-specific preparation is
documented before outcomes; tuning on this protein makes it development data and
requires a new independent test for transfer claims. Another 40 ladders is the
initial extension design, subject to its own precision/coverage justification.
One external protein supports transfer to that protein,
not universal performance across proteins.

## 7. Precision and resources — decisions before production

Do not choose sample size or simulation duration to fit an assumed calendar or
an assessment of the user's ability. Choose them to resolve the scientific
contrast, using measured cost and explicitly admitted resources. The comparison
still needs finite registered endpoints; unlimited continuation would undermine
its interpretation even when calendar time is not a constraint.

Do not inherit a duration, SU tariff or budget from old pilots. Complete the
[v2 accounting closeout](f64a_accounting_closeout.md) when SCC records are available.
Report measured GPU wall-hours, requested core-wall-hours and actual billed SU
separately. Missing remote records do not block local design work.

Produce a design table with candidate durations/repeat counts, expected precision
under conservative variance scenarios, technical failure allowance and cost.
Use historical scatter as uncertain planning input, not a guarantee. With small
repeat counts, a two-SEM heuristic is neither a power calculation nor a reliable
95% interval. Set a scientifically useful effect/precision target before choosing
the final design. Repeated data-dependent stopping needs its own statistical plan;
the default here is one fixed evaluation endpoint.

For independent windows, calculate:

`production GPU-hours = sum_over_arms,cases,repeats,states (prep_ns + retained_ns) / measured_ns_per_GPU_hour`

Add first light, failures, resumes and any scouting allocation explicitly. For
exchange, use allocated GPUs × full coupled-job walltime, including imbalance and
idle ranks. CPU setup/analysis and storage are separate budget lines.

Primary method comparison is at **equal total allocated GPU cost including
preparation**. Fix the conversion from budget to production steps using technical
timings before scientific production; reserve contingency for measured timing
variation. Preserve equal-time-per-state comparisons as a clearly labeled
secondary analysis where available. If a denser method uses fewer ns/state at
equal cost, report that tradeoff explicitly. Do not call a longer, more expensive
arm intrinsically more efficient.

Admission table must contain exact λ vectors, preparation and retained durations,
repeat counts, seeds, all-state evaluation grid/cadence, structural cadence,
compute/storage/attempt caps and restart rules. Null/unresolved fields block
production, not further planning. Each new arm needs explicit user selection and
registration under the standing operating rules. No current budget is implied.

## 8. Structural retention and interpretation

Structural interpretation is optional; retaining interpretable coordinates in
the new study is a design priority so that useful evidence is not irretrievably
lost. Failure to identify a clean structural explanation does not block completion
or reporting of a qualified primary sampling comparison.

Future mechanism-capable runs require an isolated configuration that changes the
historical estimates-only retention policy. Preserve protein coordinates and
enough solvent information to reconstruct local water occupancy; storing protein
alone cannot support a hydration mechanism. Keep topology, atom mapping, box/PBC
information, endpoint identity and synchronized energies. Preserve exchange state
assignments where relevant. Cadence and quota are fixed after a storage estimate,
not assumed from the old 11.84 GB snapshot.

Predeclare at most two local descriptors: a defined pocket water occupancy and a
defined local contact/torsion descriptor, plus backbone displacement as a control.
Define region/atoms/alignment/cutoffs and the mapping across λ before production.
Use stable/common atoms for comparisons; dummy-atom coordinates are not physical
side chains. Choose descriptors from structural hypotheses, not post hoc because
one curve resembles ΔG.

Associations between structural changes and energy drift support a candidate
explanation. A mechanism claim needs reproducibility and a controlled perturbation
that distinguishes alternatives; denser λ states alone do not establish hydration
or repacking as the cause. This study can succeed without a mechanism claim.

## 9. Implementation and deliverables

Keep completed configs/pilots and the historical bundle immutable. New settings
belong in isolated registered configurations; no missing value is filled by a
silent code default. Extend `src/analysis/` and, only after method admission, the
relevant simulation modules. Wire every new stage into `workflow/Snakefile` via
explicit non-default targets. Default execution must remain historical verification.

| Deliverable | Completion criterion |
| --- | --- |
| Corrected current interpretation | Claims distinguish observed behavior, hypotheses and unknowns; historical numbers unchanged |
| Discovery package | Hash-bound λ report, complete figures and comparator definitions |
| Supporting CPU calibration (complete) | Preserve bounded v2; use only for claims it supports; no mandatory rerun or new toy model |
| Registration package | Exact panel/methods/analysis/budgets; no unresolved production fields |
| Prospective report | Every admitted case/attempt accounted for; both primary sampling contrasts, uncertainty, availability, cost and all declared secondary analyses |
| Manuscript | One central question; prospective evidence leads; historical gate/state audit supplies context |
| Reproducible release | New version/path, raw energies and required coordinates, environment/source hashes, license/authorship resolved before deposition |
| Independent reproduction | A fresh environment reproduces a main figure; later Vlasov review is recorded accurately |

Meaningful implementation checks include synthetic known-answer estimator tests,
time-split leakage checks, exchange state/energy mapping, equal-cost accounting,
incomplete-ladder handling, numbering/topology guards and immutable-output refusal.
Run relevant tests and main-DAG dry runs when code/rules are implemented. A passing
unit test suite does not certify scientific equilibrium.

Draft manuscript sequence: the sampling question and historical motivation;
prospective protocol/panel; primary method comparison; secondary diagnostic
behavior; supported structural interpretation; limits and reproducible resource.
Keep benchmark-state mismatch distinct from within-Hamiltonian sampling performance.

| Manuscript component | Intended content |
| --- | --- |
| Figure 1 | Matched methods, prospective panel and registered cost/time-split design |
| Figure 2 | Per-case temporal movement and intervention contrasts with uncertainty |
| Figure 3 | Independent-ladder dispersion, availability and measured cost |
| Figure 4 | Prespecified diagnostic behavior against remaining instability; no general classifier claim |
| Optional figure or supplement | Structural evidence or external-protein replication, if completed and informative |
| Supporting information | F64A discovery history, benchmark-state audit, known-answer calibration, complete diagnostics and reproducibility details |

No fixed number of figures, extra protein or mechanism claim earns publication
by itself. The paper must provide an informative quantified comparison beyond
restating familiar convergence cautions. A qualified negative comparison can
meet that objective; an under-resolved experiment cannot claim a demonstrated
lack of benefit. Article framing follows the evidence rather than the desired venue.

## 10. Outcome branches and publication scope

| Outcome | Defensible paper scope |
| --- | --- |
| Only current evidence survives | Reproducible SOD1 case study with diagnostic cancellation, duration instability and benchmark audit |
| Both primary contrasts show useful improvement | Bounded evidence for improved observed sampling performance in the tested SOD1 panel; diagnostics are secondary |
| Primary contrasts differ | Report the tradeoff; no blanket improvement claim |
| Qualified comparison excludes the declared useful benefit | Prospective negative comparison within the tested models, cost and precision; no universal ineffectiveness claim |
| Intervals span useful benefit and no benefit | Inconclusive effect estimate; do not label this an established negative result |
| Diagnostics do not track the primary outcome | Secondary limitation of those diagnostics on this panel; does not invalidate an informative primary comparison |
| Frozen approach transfers to external protein | Stronger comparative methods study; still state system/sample limits |
| All protein references remain unstable | Report instability; omit accuracy and coverage claims for proteins |

Journal fit follows the result. A substantive computational comparison could
target Journal of Computational Chemistry; JCTC requires a stronger methodological
or important-application contribution and excludes routine single-class
applications. PLOS ONE considers sound negative results. LiveCoMS fits a separately
developed best-practices/tutorial resource, not automatically this research paper.
These are scope assessments, not acceptance forecasts.

For the user's application, keep a contribution log, a clear poster/talk, an
executable research artifact and an accurate manuscript status. Explain personal
decisions and collaborator/AI assistance. Do not claim a journal outcome or a
guaranteed extracurricular ranking. These outputs accompany the research; they
do not justify expanding its scientific claims.

## 11. Immediate sequence

1. Preserve completed A/B evidence and corrected conclusions; no CPU-stage restart.
2. Build and hash the selected C1 single-node Singularity image on an SCC build host,
   then qualify runtime GPU visibility, state mapping, restarts and accounting under a
   separately admitted non-production technical package. The read-only inventory and
   build-route choice are complete.
3. In parallel with that design work, audit candidate mutations and specify the
   primary effects/precision targets, secondary diagnostics and structural retention.
4. Finalize and register the fresh F64A baseline/HREX development comparison once
   technically qualified and explicitly selected. Its outcome need not be positive.
5. Freeze the method and analysis, justify final panel/repeat/duration choices,
   then register and perform the prospective SOD1 comparison through separate admission.
6. Assess the primary result and its precision before selecting the next scientific
   extension. Add an external protein for transferability; add further known-answer
   work only for a specific unresolved calibration claim. Neither is an automatic task.
7. Assemble the paper around the controlled comparison; retain diagnostics as
   secondary and mechanism as optional. Vlasov reviews later as requested.

## 12. Revision record

- Initial plan: discovery and known-answer work followed by an intervention and
  prospective evaluation, with several scientific aims at similar priority.
- Current focus revision: one primary protein sampling comparison; secondary
  diagnostic assessment; optional mechanism and conditional cross-protein extension.
  Completed A/B and the first C1 findings are preserved. The initial four-site,
  five-realization design is subject to scientific precision/coverage justification,
  not a calendar or presumed-capacity limit. No simulation or resource authorization
  is added by this revision.

## Primary methodological and journal sources

- [Mey et al., Best Practices for Alchemical Free Energy Calculations](https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378).
- [Klimovich, Shirts and Mobley, Guidelines for the analysis of free energy calculations](https://pubmed.ncbi.nlm.nih.gov/25808134/).
- [Wells et al., SOD1 maturation-state free-energy calculations](https://pubmed.ncbi.nlm.nih.gov/34076319/).
- [JCC scope](https://onlinelibrary.wiley.com/page/journal/1096987x/homepage/productinformation.html),
  [JCTC guidelines](https://researcher-resources.acs.org/publish/author_guidelines?coden=jctcce),
  [PLOS ONE criteria](https://journals.plos.org/plosone/s/criteria-for-publication),
  [LiveCoMS remit](https://livecomsjournal.org/index.php/livecoms/about).
