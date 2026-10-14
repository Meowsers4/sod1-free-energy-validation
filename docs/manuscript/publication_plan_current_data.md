# Publication plan using the existing SOD1 data

Prepared October 14, 2026. This is a proposed revision and submission plan, not a record of completed revisions or a journal submission.

**Recommendation: develop the existing work into a focused, reproducible research article and target PLOS ONE first.** The strongest paper will explain exactly what this SOD1 campaign establishes about diagnostic interpretation and experimental benchmarking, with enough accessible evidence for another researcher to check those conclusions.

The new sampling project does not need to be a prerequisite. This plan uses the surviving simulations, archived energies, existing continuations, experimental literature, and analysis code. Additional computation would be limited to checking or reanalyzing those existing data.

The manuscript and supplement were reread and journal policies and relevant literature researched for this plan. Journal information reflects what could be verified on **October 14, 2026**. The rankings are assessments of fit, not estimated acceptance probabilities. Fees and policies should be checked again at submission.

On Vlasov: **no PI requirement was found in the published authorship/submission policies checked for the leading targets.** PLOS ONE and Scientific Reports base authorship on substantive contribution, approval, and accountability. Vlasov could contribute substantially through interpretation and revision and become a coauthor on that basis; a PI title by itself is not the requirement. [PLOS authorship policy](https://journals.plos.org/plosone/s/authorship), [Scientific Reports author responsibilities](https://www.nature.com/srep/journal-policies/editorial-policies)

**The scientific objective should be explicit from the beginning.** The proposed formulation is:

> Determine what the archived convergence diagnostics and experimental comparisons can support in one SOD1 folding free-energy campaign, using local diagnostic decomposition, continued sampling of existing paths, and an audit of experimental reference states.

That question is answerable with the existing evidence. It gives the paper a coherent purpose even though the original prediction campaign failed its gate.

The current title is already defensible:

> **Diagnostic cancellation and benchmark mismatch in SOD1 folding free energy calculations**

An alternative that makes the bounded scope especially clear is:

> **A SOD1 case study of diagnostic cancellation and experimental benchmark mismatch**

Retain the current title unless revisions substantially change the emphasis.

**Journal selection should balance scientific fit, editorial expectations, cost, and the time spent on unsuccessful submissions.** The recommended shortlist is:

| Target | Assessment for this paper | Main advantage | Main rejection risk |
|---|---|---|---|
| **PLOS ONE** | **Recommended first submission** | Explicitly considers negative results; suitable for a rigorous empirical audit | Reviewers may see an inadequately designed original benchmark rather than a sufficiently informative analysis |
| **Scientific Reports** | **Strong alternative** | Explicitly welcomes technically sound negative results and niche studies | Broad readership requires particularly clear motivation and presentation |
| **ACS Omega** | **Realistic chemistry-focused alternative** | Explicitly welcomes negative results supported by robust computational protocols | Must establish original chemical insight; a project-management narrative would be weak |
| **Molecular Simulation** | **Plausible specialist option, especially if budget matters** | Direct audience for simulation methodology and its practical limitations | Still requires an informative contribution; it is not an automatic fallback |
| **Journal of Computational Chemistry** | **Conditional stretch target** | Excellent computational-chemistry readership | Its stated emphasis on important advances and significant insight is harder to meet with one selected case |
| **RSC Advances** | **Conditional additional option** | Broad chemical-sciences audience; potentially relevant institutional funding | Requires an advance in chemical understanding, which is less direct in this manuscript |

PLOS ONE explicitly considers negative and null results. Scientific Reports tells reviewers to assess scientific validity and technical soundness rather than perceived impact. ACS Omega welcomes negative results but still asks for original chemical insight and robust methods. Those policies make these three the most natural starting points. [PLOS criteria](https://journals.plos.org/plosone/s/criteria-for-publication), [Scientific Reports reviewer criteria](https://www.nature.com/srep/guide-to-referees), [ACS Omega guidelines](https://researcher-resources.acs.org/publish/author_guidelines?coden=acsodf)

There is also a concrete topical precedent: **Gupta, Sun and Levy published a protein-stability free-energy benchmarking study in PLOS ONE in April 2026**, comparing calculations involving staphylococcal nuclease and T4 lysozyme. It is a larger and scientifically different study, so it does not establish that this manuscript will be accepted, but it confirms that this research area has an audience there. [Published study](https://doi.org/10.1371/journal.pone.0335829)

For JCC, be more cautious than the original “PLOS ONE or JCC” wording suggests. Its Full Paper criteria explicitly emphasize significant advances and insight. Attempt it only if the revised paper makes a convincing contribution beyond illustrating established warnings. [JCC author guidelines](https://onlinelibrary.wiley.com/page/journal/1096987x/homepage/forauthors.html)

Do not build the short-term strategy around JCTC, JCIM, PLOS Computational Biology, or a broad high-impact venue. That is a judgment about the present evidence: the manuscript offers neither a validated new method nor a broad benchmark nor a demonstrated biological mechanism.

**Publication cost is worth resolving before selecting the submission order.**

| Journal | Verified cost information | Practical implication |
|---|---|---|
| PLOS ONE | Current standard article fee: **US$2,477** | Check institutional coverage or request assistance at submission |
| ACS Omega | Listed APC: **US$1,935**, for either listed CC licence option | Potentially less expensive than PLOS ONE before discounts |
| Molecular Simulation | **No APC if the subscription route is chosen** | Useful option if open-access funding is unavailable |
| JCC | Optional open-access APC: **US$4,560**; subscription publication is also offered | Do not assume the optional OA charge is mandatory |
| RSC Advances | Listed APC: **£2,200**, before applicable taxes | Investigate institutional coverage if affiliation qualifies |
| Scientific Reports | Fully open access; exact current fee was not reliably retrievable in this research | Obtain the current quote before choosing it |

These are listed fees, not promises about the amount the authors would personally pay. [PLOS fees](https://plos.org/fees/), [ACS pricing](https://acsopenscience.org/oa-pricing-tables/), [Molecular Simulation publishing options](https://www.tandfonline.com/journals/gmos20/about-this-journal), [JCC OA pricing](https://onlinelibrary.wiley.com/page/journal/1096987x/homepage/fundedaccess.html), [RSC Advances](https://www.rsc.org/publishing/journals/rsc-advances)

Because the project used BU computing resources, BU’s library information was also checked. Its page lists agreements with the Royal Society of Chemistry, Cambridge University Press, and ACM. **Using SCC alone does not establish eligibility**: an author’s actual affiliation and the agreement’s terms must qualify. RSC Advances becomes more attractive financially only if the library confirms coverage for this paper. [BU open-access publishing information](https://www.bu.edu/library/help-research-support/scholarly-publishing/open-access-publishing/)

The default submission sequence is **PLOS ONE, then Scientific Reports or ACS Omega**, choosing between the latter two after seeing the first decision and confirming costs. If funding is the binding constraint, consider Molecular Simulation earlier. If Vlasov helps develop a substantially stronger specialist argument, one JCC attempt before PLOS ONE would be reasonable—but do not spend months adding work solely to chase that placement.

**The first revision task is to establish a precise hierarchy of claims.** This is more important than adding another analysis.

| Claim | What the current evidence can support | What the manuscript must avoid implying |
|---|---|---|
| Signed local discrepancies cancel in the historical aggregate | A direct mathematical property, quantified in the archive | Cancellation proves that the MBAR estimate is wrong |
| Small early ladder hysteresis coexists with later movement | An observed counterexample on a selected continued path | A measured general false-negative rate for convergence diagnostics |
| F64A estimates remain sensitive to duration and trimming policy | Descriptive instability through the observed 15 ns | The equilibrium answer is known, or further sampling cannot help |
| Folded-leg diagnostic associations are unresolved | Small-sample estimates with grouped uncertainty | The diagnostics have no information in general |
| Experimental references differ from the simulated state | A documented incompatibility audit | State mismatch quantitatively explains the prediction residuals |
| The original gate failed | A preserved historical decision | A valid accuracy estimate for state-matched apo-2SH SOD1 |

Every abstract sentence, result heading, figure caption, and conclusion should be checked against this table.

One particularly important distinction deserves an explicit sentence in the paper:

> F64A was excluded by the original variant-level rule because another ladder exceeded the hysteresis cap; the low-hysteresis example concerns one individual ladder.

This protects against a serious misunderstanding. The current data show that a quiet individual ladder can be misleading. They do **not** show that the complete gate mistakenly accepted F64A.

The paper should also consistently distinguish three meanings of “agreement”: forward/reverse estimator agreement within a ladder, agreement among separately initialized repeats, and agreement with an experimental reference. Each addresses a different question.

**The second task is to strengthen the relationship to prior work.** The manuscript should acknowledge established knowledge early, then explain the additional evidence provided here.

The literature work should produce a compact internal comparison table covering:

| Literature | Why it matters here | What to establish before citing it |
|---|---|---|
| Wells et al., 2021, SOD1 | Directly related protein, maturation states, and GROMACS/pmx work | Which states, sampling protocol, and conclusions overlap with this study |
| Klimovich, Shirts and Mobley, 2015 | Established free-energy analysis guidance | Which diagnostic limitations were already recognized |
| Mey et al., best-practices guide | Sampling, uncertainty, and experimental comparison | Which recommendations this case illustrates |
| Grossfield et al., uncertainty and sampling guide | Interpretation of statistical uncertainty and sampling quality | Language separating conditional precision from broader uncertainty |
| Recent protein-stability FEP benchmarks | Current context and reasonable expectations | Why this study addresses interpretation rather than competing on predictive accuracy |

Wells already applied free-energy calculations to SOD1 using pmx and nonequilibrium transformations. The best-practice literature already discusses sampling and diagnostic limitations. The contribution must therefore rest on the **specific evidence chain and its reproducibility**, rather than priority claims about the underlying principles. [Wells et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8376412/), [Klimovich et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/), [Mey et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8388617/), [Grossfield et al.](https://doi.org/10.33011/livecoms.1.1.5067)

This should be a bounded literature pass. The stopping condition is that every statement about established practice, prior SOD1 calculations, and the paper’s incremental contribution is supported. An exhaustive review or a target number of references is unnecessary.

**The third task is to close the scientific provenance gaps that could undermine the main argument.** Much of the numerical reproduction is already done; build on that work.

Create a claim-to-evidence register with one row for every headline number and conclusion. Each row should identify the source data, analysis version, cohort, units, uncertainty definition, figure location, and reproduction status. Use three explicit statuses:

- Reproduced from surviving raw reduced potentials.
- Reproduced from a saved numerical report.
- Preserved historical result whose original raw inputs are unavailable.

This is where the A4V exception and the continuation software environments belong. It prevents “reproducible” from becoming an overly broad label.

Then perform a targeted physical and computational consistency check of the inputs supporting the central claims: mutation identity, residue numbering, folded versus unfolded leg, intended redox state, λ ordering, energy units, sign convention, and analysis inclusion. Use the archived physical inputs where available. Current code or parameter hashes alone are insufficient evidence of what was actually simulated.

The completion criterion is straightforward: **no unresolved identity, unit, sign, or data-selection issue may affect a headline result.** Historical limitations that cannot be repaired must remain explicit.

**The fourth task is to make the diagnostic result understandable and scientifically proportionate.** The core mathematics should take only a few lines:

```text
H = |Σ_k d_k|
S = Σ_k |d_k|
M = max_k |d_k|
```

Explain precisely how the forward and reverse estimates are expressed in the same transformation direction before forming `d_k`. Define the energy units and sampling intervals.

Then show why `H` can be much smaller than `S`, using the actual F64A data. The reader should be able to understand the cancellation without trusting a verbal assertion or reading the implementation.

Use the existing whole-archive results to place the selected example in context. Show the distribution of `H`, `S`, and cancellation, keeping folded and unfolded legs separate. The purpose is to reveal where the example sits in this archive—not to search for an impressive frequency or a new threshold.

For any new summary, specify its definition before calculating it. Avoid choosing “high cancellation” cutoffs after inspecting the results. A continuous plot may communicate the evidence better than a percentage above an arbitrary threshold.

Also check how cancellation fractions behave when `S` is very small. A large percentage can be visually dramatic while representing a negligible absolute discrepancy. Present absolute magnitudes alongside fractions.

**The fifth task is to give the temporal continuation evidence the greatest prominence.** This is the strongest empirical extension beyond the simple observation that signed quantities can cancel.

The main presentation should let the reader follow all three F64A repeats through the same retained blocks. It should display:

- Blockwise folded-leg estimates through 15 ns.
- The corresponding historical diagnostic.
- Individual repeat movements between the final two blocks.
- Results under all three existing analysis policies.
- Enough retained-sample information to interpret the estimates.

Keep the primary planned comparison identifiable. Show the other policies as sensitivity analyses using the same underlying data.

A near-zero mean movement must always appear alongside the three repeat movements. The important observation is that opposing movements can produce a small mean while substantial repeat disagreement remains.

Use clear language for uncertainty. The error bars quantify the estimator’s conditional uncertainty under its assumptions and selected samples. They do not include unseen conformational states, force-field error, or experimental-state mismatch. A count after thinning should not be presented as proof that those samples are independent.

The remaining high-value computational check is to reproduce the central continuation numbers from the surviving cumulative energy archive in an explicitly recorded environment. Earlier work verified hashes and dimensions and reproduced other analyses; it did not freshly repeat every continuation MBAR solve locally.

That reproduction should check block boundaries, record counts, trimming, thinning, λ order, and numerical tolerances. If an environment difference changes a result materially, resolve and document it before revising the paper. Do not silently replace the historical result with whichever environment produces the preferred answer.

**The sixth task is to simplify the statistics and make the units of replication unmistakable.**

The archive contains several different sample counts, and reviewers should never have to reconstruct them:

| Analysis population | Appropriate description |
|---|---|
| Full folded archive | 24 ladders, eight variants, six mutation sites; includes longer A4V sampling |
| Attempt-1 folded cohort excluding A4V | 21 ladders, seven variants, five sites |
| Historical gate | Seven usable variant estimates after F64A exclusion |
| F64A continuation | Three continued repeat paths for one selected variant |

The seven variants in the gate and the seven variants in the A4V-excluded analysis are **different sets**. That distinction deserves explicit labels.

For comparisons intended to describe the original common protocol, foreground the cohort excluding A4V’s longer replacement data. Retain the full archive as a sensitivity analysis. Record this editorial choice openly; it does not revise the historical gate.

Keep grouped uncertainty estimates and leave-one-group-out results, but interpret them as exploratory. Six sites—or five in the reduced cohort—cannot support strong claims about population-wide diagnostic performance. Show how estimates change when influential sites are removed.

Do not add row-wise significance tests that treat sibling disagreements as independent. Do not interpret intervals containing zero as demonstrating no association. Retain the unfolded-leg associations that differ from the folded results.

For the movement-to-error ratios, preserve their descriptive role. They are not calibrated hypothesis tests, particularly when time blocks share slow dynamics.

**A small number of additional CPU checks could strengthen the paper, but each should answer a specific objection.** Prioritize them as follows:

| Proposed check using existing data | Value | Priority and stopping rule |
|---|---|---|
| Fresh reproduction of central continuation estimates | Establishes the strongest result directly from archived energies | Essential if feasible with surviving inputs |
| Audit of cohort labels, block boundaries, units, and signs | Prevents interpretation or implementation errors | Essential |
| All-ladder context for the selected cancellation example | Reduces concern about selective presentation | High value; reuse existing results wherever possible |
| Review existing leave-one-site/variant-out summaries | Reveals sensitivity to the small panel | High value; do not duplicate completed work |
| Bounded BAR–MBAR comparison on the same samples | Could address an estimator-implementation objection | Optional; agreement would not establish convergence |
| More trim percentages, new thresholds, many correlation variants | Adds analysis flexibility without necessarily adding information | Omit unless a concrete unresolved issue requires it |
| A new predictive model or optimized stopping rule | Requires validation beyond this archive | Outside this paper |

The optional estimator comparison should be specified in advance and remain supplementary. It must not become a contest to find the estimator that produces the most favorable result.

**The seventh task is to make the experimental-state audit a substantive result.** The existing table is useful, but the supporting evidence should be accessible enough that a reviewer can verify every classification.

For every experimental value, provide the original source, table or figure, construct, redox state, metal state, oligomeric transition, temperature, pH, sign convention, units, and uncertainty provenance. Distinguish facts directly stated in the source from interpretations made during the audit.

The main text should explain the thermodynamic consequence of those distinctions. Comparing a reduced native-sequence monomer calculation with measurements on disulfide-intact substituted constructs is a comparison between different physical systems. Converting a temperature or dividing a dimer transition by two does not remove the other differences.

The reference-sensitivity analysis should therefore demonstrate **how the reported comparison depends on reference construction**. It must not look like a route to recovering a passing gate.

Make the compatibility table the main visual element and reduce the prominence of the scenario that happens to improve correlation. Preserve every predefined scenario and its assumptions in the supplement. A compact main-text summary may be enough.

The audit should also avoid assigning blame to the original experimental studies. Their measurements can be entirely appropriate for their own questions while being unsuitable as matched controls for this simulation.

**The eighth task is to resolve the missing A4V data as a publication issue, not just a footnote.**

The overwritten attempt-1 folded windows cannot be reconstructed. Repeating that calculation would generate new data, not restore the old record.

The defensible approach is to:

- Preserve the original gate estimate as a clearly identified historical record.
- Make the central diagnostic and continuation findings reproducible without that missing dataset.
- Provide the existing A4V-excluded analyses.
- Label the A4V extension comparison according to the different provenance of its two arms.
- State exactly which conclusions depend on saved summaries rather than raw-energy reanalysis.

However, disclosure alone does not guarantee that a journal will accept the missing-data limitation. PLOS requires the data needed to replicate reported findings and asks authors with unlisted sharing limitations to contact the journal office. A focused policy inquiry would be sensible once the revised scope and data inventory are concrete. **No inquiry is sent or authorized by saving this plan.** [PLOS data policy](https://journals.plos.org/plosone/s/data-availability)

If the journal considers the A4V sensitivity result insufficiently supported, be prepared to remove it as a scientific result while retaining an accurate account of the historical gate. Moving an unsupported result to supplementary material does not eliminate the issue.

**The ninth task is to reorganize the manuscript around the scientific argument.** Aim for approximately **4,500–5,500 words of main narrative**, subject to the chosen journal’s rules, with detailed provenance in the appendix. This is an editorial target, not a universal journal limit.

The introduction should do four things: explain the validation problem, summarize established diagnostic cautions, establish the experimental-state issue, and state the bounded question this dataset answers.

The Methods should make the physical system, estimator, historical diagnostic, cohorts, and timing of analyses easy to reconstruct. Put operational details that do not affect interpretation into the supplement.

The Results should follow this sequence:

1. Brief campaign and gate context, including F64A’s actual exclusion.
2. Local cancellation in the historical diagnostic.
3. Continued-path duration and selection-policy dependence.
4. Experimental reference incompatibility.
5. A short summary of the supporting sensitivities.

The Discussion should explain the consequences of those findings, acknowledge their relationship to established guidance, and give a small number of directly supported recommendations.

The failed gate remains important context, but it should not dominate the abstract or opening pages. Likewise, the repository’s job history, scheduler fixes, and later GPU qualification work should not enter the manuscript unless they are necessary to understand an included result.

**The tenth task is to redesign the figures so each answers a distinct question.**

| Proposed main figure | Question answered | Recommended content |
|---|---|---|
| **Figure 1: Study and evidence map** | What was calculated, compared, and retained? | Thermodynamic-cycle schematic, panel summary, gate context, and distinction between historical and reproducible evidence |
| **Figure 2: Diagnostic cancellation** | How can the aggregate hide local disagreement? | Signed adjacent discrepancies, their cumulative sum, H/S/M, and whole-archive context |
| **Figure 3: F64A temporal behavior** | What happened after the quiet early diagnostic? | All three blockwise paths, final paired movements, all existing policies, clearly defined uncertainties |
| **Figure 4: Experimental compatibility** | What did the benchmark actually measure? | State/construct/transition comparison and a restrained summary of reference sensitivity |

This is a proposed improvement to the existing four-figure package, not a requirement to replace every plot. The current gate scatter could become a panel in Figure 1 or move to the supplement if the page becomes crowded.

For the supplement, retain full correlation summaries, leave-one-group-out results, λ-dependent energy analyses, selection/sample-count diagnostics, G93A sensitivity, and any defensible A4V comparison.

Every figure should have machine-readable source values. Use consistent repeat colours, consistent units, explicit cohort labels, and readable text at final publication size. Check the final PDF visually; successful rendering is not sufficient.

A useful reader test is whether someone can understand the central evidence from Figures 2–4 and their captions without navigating the repository.

**The eleventh task is to convert the archive into a usable scientific resource.** The existing deposit candidate is a substantial head start. Refresh it for the final manuscript version rather than replacing it with another loosely organized bundle.

Prepare a concise entry point explaining which command reproduces each main figure and table. Separate:

- Raw-energy reanalysis.
- Figure generation from saved reports.
- Historical values that cannot be re-derived.
- Original simulation setup materials.
- Explicitly unavailable records.

Archive the exact paper code version and environments. Keep the historical sealed bundle unchanged, and place later evidence in clearly identified additions. Use a persistent repository accession for the manuscript’s data citation, with GitHub serving as the development and navigation location.

The strongest practical validation is a clean reconstruction of the central figures and tables from the deposited files, without SCC access or undocumented local paths. Document numerical tolerances and the expected runtime once measured.

There is also an immediate documentation inconsistency to fix during revision: the draft still says that no public repository accession has been assigned, while the code and paper files are now on GitHub. The corrected statement must distinguish **the public GitHub repository** from **the still-unpublished raw-data deposit candidate**.

**The twelfth task is to make Vlasov’s possible involvement concrete and useful.** There is no need to invent an authorship arrangement now.

The most valuable substantive contributions would be:

- Assessing whether the central scientific question and interpretation are convincing.
- Checking that the diagnostic terminology and statistical reasoning are defensible.
- Challenging the state-mismatch interpretation.
- Helping decide whether the manuscript meets JCC’s higher contribution threshold.
- Revising the argument and taking responsibility for the submitted version.

The lead researcher can remain first author if that reflects the work. Corresponding authorship should go to the person who will manage submission, responses, and future questions; it need not be assigned simply because someone is the PI.

If Vlasov joins as an author, final approval is required. Until then, preparation can continue. An early mentor review need not be a dependency for completing the evidence register, figures, or manuscript revision.

The AI disclosure also needs substantive attention. It should accurately describe the assistance with code, analysis support, drafting, and figure preparation, together with the human checks actually performed. PLOS’s current policy specifically requires disclosure of relevant AI-assisted code development and research/manuscript work; a generic “grammar assistance” statement would not accurately describe this project. [PLOS AI policy](https://journals.plos.org/plosone/s/ethical-publishing-practice)

**The thirteenth task is to prepare for the objections reviewers are most likely to raise.** Maintain this response matrix while revising:

| Likely objection | What the revised paper must provide |
|---|---|
| “Cancellation is mathematically obvious.” | Acknowledge that; explain the empirical magnitude, archive context, and connection to subsequent instability |
| “F64A was cherry-picked.” | Explain selection, show all three continued repeats, and supply whole-archive context |
| “The original gate already caught F64A.” | Agree explicitly; distinguish the individual diagnostic from the complete decision rule |
| “These simulations are too short to establish equilibrium.” | Make no equilibrium claim; demonstrate what the observed estimates and diagnostics did over the recorded intervals |
| “The benchmark was inappropriate.” | Treat incompatibility as an audited result and avoid interpreting the gate as matched-state accuracy |
| “There are too few independent observations.” | Show the grouping structure and restrict association claims |
| “A different estimator might fix this.” | Separate estimator behavior from sampling; use a bounded supplementary check if needed |
| “The missing A4V data undermine reproducibility.” | Identify the exact dependency, provide surviving records, and keep the central findings independent of the missing windows |
| “There is no mechanism.” | Keep structural hypotheses out of the claimed findings |
| “This only describes one pipeline.” | State the empirical scope and provide reusable diagnostic outputs and benchmark metadata that make the case useful |

The response should change the manuscript, not merely defend it. If a reviewer identifies a valid implementation error, correct the affected results. If they ask for a different scientific study, explain the boundary of this paper—but only after ensuring that the bounded claims stand on their own.

**The work should be scheduled as a finite revision project.** Assuming the existing archives are accessible and reproduction does not reveal a major issue, budget roughly **three to four weeks of preparation**, with several tasks overlapping. This is an estimate of work organization, not a journal publication timeline.

| Stage | Approximate effort | Deliverable | Completion criterion |
|---|---:|---|---|
| Scope and claim decisions | 1–2 days | Claim matrix and revised argument | Every main claim has a defensible scope |
| Literature and source audit | 2–3 days | Prior-work comparison and verified experimental references | No unsupported priority or benchmark statement |
| Numerical and provenance closeout | 3–5 days | Reproduction report and final cohorts | Central numbers trace to identified inputs |
| Figures and source data | 2–3 days | Main figures, supplement, plotting data | Each figure answers one clear question |
| Manuscript revision | 3–4 days | Complete revised paper | Abstract, Results, and conclusions agree |
| Deposit and submission preparation | 2–3 days | Versioned package, declarations, cover letter | Reviewers can access the supporting evidence |
| Final human approval and journal choice | Availability-dependent | Approved submission version | Authors accept the claims and responsibilities |

The order matters. Resolve claims and data provenance before polishing the prose. Do not spend a week making an elegant figure for a result that later has to be demoted or removed.

**Use explicit stopping conditions to prevent this from growing into the new project.** The paper is ready for submission when:

- Every headline number has an identified source and reproduction status.
- The main findings survive the appropriate cohort and policy sensitivities.
- F64A’s selection and original exclusion are unambiguous.
- No conclusion depends on treating an unmatched reference as ground truth.
- The missing-data limitation has a defensible treatment consistent with the target journal.
- Figures, text, supplement, and deposited values agree.
- Data and code are accessible to reviewers.
- Authorship, funding, rights, AI disclosure, and author approval are complete.

Stop adding analyses when they no longer resolve a specific scientific objection. New protein systems, enhanced-sampling comparisons, fresh starts, a matched experimental campaign, and structural mechanism work would support a different paper.

For the first revision pass, prioritize **three concrete outputs**: a claim-to-evidence register, a revised figure storyboard, and a new abstract/introduction that makes the diagnostic–continuation–benchmark argument clear. Those will reveal whether the remaining work is mostly presentation and reproducibility, as currently expected, or whether a particular claim needs to be narrowed further.
