# Submission checklist — case-study manuscript (draft v1, 2026-10-13)

Draft: [`manuscript_draft_v1.md`](manuscript_draft_v1.md). Claims follow
[`methods_limitations_outline.md`](../methods_limitations_outline.md) and
[`conclusion_reconciliation_2026-09-18.md`](../conclusion_reconciliation_2026-09-18.md).
Nothing has been sent to any journal, mentor or repository.

## 1. Decisions only the rights holders can make

| Item | Status | Notes |
|---|---|---|
| Authorship and affiliations | open | Title block is a placeholder. |
| Public license (code and data) | open | Required before deposit (outline, "Submission boundaries"). |
| Target journal | open | Plan §10: PLOS ONE considers sound negative results; JCC suits a substantive computational comparison; LiveCoMS fits a best-practices resource, not this paper. The draft uses a journal-neutral structure. |
| Vlasov review | deferred by user | Not a prerequisite for drafting; record it accurately once it happens. |
| AI-assistance disclosure | open | Placeholder section; most journals require it. |
| Funding / computing acknowledgement | open | BU SCC allocation. |
| Data deposit (DOI) | open | Release bundle + raw reduced-potential archives (attempt 1, A4V 9 ns folded, G93A SS, F64A v1/v2). |
| Scope: include GPU qualification / known-answer model? | excluded from v1 | They support the prospective study, not this case study. Add only if a specific claim needs them. |

## 2. Discrepancies found while drafting

1. **Median gate hysteresis:** `gate_attempt_1.md` prints 0.220; re-derivation from archived
   windows gives 0.225 (I113T's 0.2245, the median, rounded to 0.22 at run time). The draft
   quotes both. Either passes the 0.75 threshold.
2. **pymbar version:** `env/analysis-lock.txt` pins 4.0.3 locally; the SCC v1/v2 reports record
   4.2.0. State the version per analysis in Methods before submission.
3. **Wells 2021 details:** README §11.1 notes the full text was reconstructed from search
   snippets. The draft cites Wells only for same toolchain, apo-2SH and non-equilibrium
   transitions; check those against the PDF.
4. **Unfolded-leg associations:** some unfolded-leg grouped intervals exclude zero (MBAR error;
   variant-grouped Pearson for H). The outline only said folded intervals include zero; the draft
   reports the unfolded result explicitly rather than implying a global null.

## 3. References to verify

Entries marked `[verify]` in the draft were added from general knowledge and are not in
[`citations.md`](../../citations.md): Klimovich 2015, Mey 2020 (author list), Shirts & Chodera
2008, Chodera 2016, Abraham 2015 (GROMACS), Best & Hummer 2009, Lindorff-Larsen 2010, Jorgensen
1983, and the Stathopulos 2006 author list/pages. Check each against the publisher record and
add it to `citations.md`.

## 4. Figure map

| Manuscript | File | Built by |
|---|---|---|
| Fig 1 | `docs/review/gate_of_record.png` | forensic CPU DAG |
| Fig 2 | `docs/review/diagnostic_cancellation.png` | `src/analysis/diagnostic_audit.py` |
| Fig 3 | `docs/manuscript/figures_v1/fig6_f64a_temporal.{pdf,png}` | `snakemake manuscript_figures_v1` (filename keeps the outline's "Figure 6" label) |
| Fig 4 | `docs/review/reference_sensitivity.png` | `src/analysis/reference_sensitivity.py` |
| Fig 5 | `docs/review/a4v_sampling_sensitivity.png` | `src/analysis/methods_figures.py` |
| Fig 6 | `docs/review/g93a_disulfide_diagnostic.png` | `src/analysis/methods_figures.py` |
| Fig S1 | `docs/review/convergence_diagnostic.png` | `src/analysis/methods_figures.py` |
| Figs S2–S4 | `docs/manuscript/figures_v1/figS2–S4_*.png` | byte-identical copies of the λ-comparator outputs |

Journals typically want TIFF/EPS at fixed widths; convert at submission time from the PDFs/PNGs.

## 5. Number source map

| Draft section | Source record |
|---|---|
| 3.1 gate, Table 1 | `docs/gate_attempt_1.md`; `docs/review/reference_reproduction.json`; `docs/stop_rule_reanalysis.md` |
| 3.2 cancellation, Table 2 | `docs/review/diagnostic_audit.json` (strata `folded/*`, `unfolded/*`, site/variant grouping) |
| 3.3 retrospective quarters | `docs/temporal_analysis_results.md` |
| 3.3 F64A v1/v2 | `docs/f64a_extension_review/f64a_blocks_v1.json`, `f64a_continuation_v2.json` (hash-verified by the figure builder); `docs/f64a_continuation_results.md` |
| 3.3 high-λ drift | `docs/conclusion_reconciliation_2026-09-18.md` §2 |
| 3.4 state audit, Table 3 | `data/benchmark_state_audit.csv`; `docs/reference_state_audit.md`; `docs/reference_sensitivity_analysis.md` |
| 3.5 A4V | `docs/gate_attempt_2_abandoned.md` |
| 3.6 G93A | `docs/review/redox_uncertainty.json`; `docs/methods_figure_package.md` |
| 2.x protocol | `config/pipeline.yaml`; `src/fep/pmx_engine.py`; `src/fep/analyze.py`; `src/prep/build.py` |

## 6. Converting the draft

The draft is Pandoc Markdown. For a Word file with numbered references, convert the reference
list to BibTeX first, then e.g. `pandoc manuscript_draft_v1.md --citeproc --bibliography refs.bib
-o manuscript.docx`. Figures are referenced by legend, not embedded.
