# Submission checklist — paper body v2, 2026-10-13

Current paper: [`manuscript_draft_v2.md`](manuscript_draft_v2.md), with
[`supplement_v1.md`](supplement_v1.md). The reviewed v1 is retained as an earlier draft.
Full preparation status: [`submission_notes.txt`](submission_notes.txt). Claims follow
[`methods_limitations_outline.md`](../methods_limitations_outline.md) and
[`conclusion_reconciliation_2026-09-18.md`](../conclusion_reconciliation_2026-09-18.md).
Nothing has been sent to any journal, mentor or repository.

## 1. Decisions only the rights holders can make

| Item | Status | Notes |
|---|---|---|
| Authorship and affiliations | deferred by user | Omitted from paper-body files; add the real title page later. |
| Public license (code and data) | open | Required before deposit (outline, "Submission boundaries"). |
| Target journal | PLOS ONE working format | Final external submission choice remains open; local formatting uses the current PLOS ONE instructions. |
| Vlasov review | deferred by user | Not a prerequisite for drafting; record it accurately once it happens. |
| AI-assistance disclosure | draft prepared | See submission_notes.txt; tool inventory and author responsibility statement need truthful completion. |
| Funding / computing acknowledgement | open | BU SCC allocation. |
| Data deposit (DOI) | open | Historical release + later reports/code + surviving raw energies. A4V attempt-1 folded windows are lost; deposit its historical estimate/uncertainty with this exception disclosed. |
| Scope: include GPU qualification / known-answer model? | excluded from v1 | They support the prospective study, not this case study. Add only if a specific claim needs them. |

## 2. Review corrections and remaining provenance limit

1. **Median gate hysteresis:** `gate_attempt_1.md` prints 0.220; re-derivation from archived
   windows gives 0.225 (I113T's 0.224926913, the median; 0.22 at two decimal places).
   The draft quotes both. Either passes the 0.75 threshold.
2. **pymbar version:** `env/analysis-lock.txt` pins 4.0.3 locally; the SCC v1/v2 reports record
   4.2.0. Methods §2.7 now distinguishes these and their recorded Python/NumPy versions.
   **Remaining limit:** the original gate's exact PyMBAR runtime is not established by the
   available records (`env/environment.yml` only requires ≥4). Do not substitute a later
   version. The draft discloses this limitation.
3. **Wells 2021 details:** the draft's same-toolchain, apo-2SH and nonequilibrium-transition
   claims were checked directly against the PMC full text, §§2.1, 4.2–4.3, on 2026-10-13.
   See `citations.md` §5. Historical claims beyond this scope have not all been re-audited.
4. **Unfolded-leg associations:** some unfolded-leg grouped intervals exclude zero (MBAR error;
   variant-grouped Pearson for H). The outline only said folded intervals include zero; the draft
   reports the unfolded result explicitly. The abstract, Introduction and Discussion now
   restrict the unresolved-association summary to the folded leg.
5. **Temporal summaries:** 2.43 is the median of 21 individual movement/combined-error ratios,
   not the ratio of their medians (2.214). The draft defines the quadrature denominator and
   retains the descriptive, correlated-block caveat. Removed the unsupported largest-subsequent-
   movement assertion and made the other two v1 movements explicitly negative.
6. **Reproduction/deposit:** A4V attempt-1 is a preserved historical point, not a raw-data
   re-derivation. Both Methods and Data availability now disclose the exception and distinguish
   the September 14 bundle from later continuation/manuscript artifacts. Table 1 restores
   F64A's ±0.34 kcal/mol uncertainty; Methods notes the 3,001 attempt-1 boundary records.
7. **Figure preservation:** the explicit target has no Snakemake-managed output, preventing
   pre-job/failure cleanup of existing figures. Normal and forced reruns are tested on disposable
   fixtures. The three supplementary source images now have pinned, pre-copy SHA-256 checks.

## 3. Reference verification completed

All nine formerly flagged entries were checked and added to
[`citations.md`](../../citations.md) §5 with source links and the verification date:
Klimovich 2015, Mey 2020 (original v1.0 author list), Shirts & Chodera 2008, Chodera 2016,
Abraham 2015, Best & Hummer 2009, Lindorff-Larsen 2010, Jorgensen 1983 and Stathopulos 2006.
Stathopulos's DOI was added. Bibliographic verification does not imply that every paper's
full text or every historical project interpretation was independently re-audited.

## 4. Figure map

| Manuscript | File | Built by |
|---|---|---|
| Fig 1 | `docs/review/gate_of_record.png` | forensic CPU DAG |
| Fig 2 | `docs/review/diagnostic_cancellation.png` | `src/analysis/diagnostic_audit.py` |
| Fig 3 | `docs/manuscript/figures_v1/fig6_f64a_temporal.{pdf,png}` | `snakemake manuscript_figures_v1` (filename keeps the outline's "Figure 6" label) |
| Fig 4 | `docs/review/reference_sensitivity.png` | `src/analysis/reference_sensitivity.py` |
| Fig S5 (v2; Fig 5 in v1) | `docs/review/a4v_sampling_sensitivity.png` | `src/analysis/methods_figures.py` |
| Fig S6 (v2; Fig 6 in v1) | `docs/review/g93a_disulfide_diagnostic.png` | `src/analysis/methods_figures.py` |
| Fig S1 | `docs/review/convergence_diagnostic.png` | `src/analysis/methods_figures.py` |
| Figs S2–S4 | `docs/manuscript/figures_v1/figS2–S4_*.png` | byte-identical copies of the λ-comparator outputs |

Journals typically want TIFF/EPS at fixed widths; convert at submission time from the PDFs/PNGs.

The committed `figures_v1/` directory and its original trace remain unchanged. Its trace records
the original spec/builder identities; the reviewed spec now additionally pins the three image
hashes already present in that trace. To exercise the revised builder, choose a **nonexistent**
destination (including for forced reruns):

```bash
snakemake manuscript_figures_v1 --cores 1 \
  --config manuscript_figure_output_dir=/tmp/sod1fep-manuscript-review-new
```

The target reads existing evidence only; it does not schedule upstream report regeneration.
Missing reports or hash mismatches fail. Running without a fresh destination intentionally
fails if `figures_v1/` already exists. The default DAG remains read-only release verification.

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

## 6. Paper files and rebuilds

Prepared local files are under `results/manuscript_submission_v2/`:
`documents/` (main Word, appendix Word, cover letter), `pdf/` (matching PDFs and a reading
copy with main figures appended), `figures/` (four 300-dpi TIFFs), and `deposit/` (data/code
staging candidate). Large generated outputs are gitignored. Source texts, reference map,
hash specification and builders are ordinary repository files.

New explicit CPU-only targets, all refusing existing destinations:

```bash
snakemake manuscript_documents_v1 --cores 1 \
  --config paper_document_python=/path/to/document/python \
  paper_document_output_dir=/fresh/paper/documents
snakemake manuscript_journal_figures_v1 --cores 1 \
  --config paper_journal_figure_output_dir=/fresh/paper/figures
snakemake manuscript_pdfs_v1 --cores 1 \
  --config paper_document_python=/path/to/document/python \
  paper_renderer=/path/to/render_docx.py \
  paper_font_file=/path/to/TimesNewRoman.ttf \
  paper_document_output_dir=/fresh/paper/documents \
  paper_journal_figure_output_dir=/fresh/paper/figures \
  paper_pdf_output_dir=/fresh/paper/pdf
snakemake manuscript_deposit_candidate_v1 --cores 1 \
  --config paper_deposit_output_dir=/fresh/paper/deposit
```

Run document/figure production before PDF rendering. Document Python needs python-docx,
Pillow, reportlab and pypdf; the supplied renderer needs its documented LibreOffice/Poppler
runtime. Scientific plots and deposit validation use the local analysis environment.
The paper spec pins source/report hashes; intentional textual edits require an explicit
spec refresh before producing a new version. Visual page inspection remains required
before delivery even when rendering succeeds. The default DAG is unchanged.

The main Word manuscript omits figures per the journal instructions; its captions appear
at the first callout. The separate reading PDF appends main figure viewing copies. The
appendix contains Figs S1–S6. Author front matter remains intentionally deferred.

## 7. Revision validation — 2026-10-13

- Full local suite: **531 passed, 5 skipped**. The manuscript module's nine tests include
  normal/forced Snakemake rerun preservation and rejection of a replaced supplementary image.
- Default DAG dry-run: only the read-only release-verification target.
- Fresh explicit Snakemake build: succeeded in a temporary directory; all 12 specified
  quoted values checked. Its temporal PNG and three supplementary PNGs are byte-identical
  to the committed originals. The new PDF was generated successfully; byte identity is
  not asserted because PDF metadata can change on rebuild.
- Original committed figures, source reports, simulation configuration and sealed packages
  were not changed by this revision. Submission/rights-holder choices remain open.

## 8. Paper preparation checks

- Gate chronology checked against full commits `23f057854762a8b8adb8f211a636c77c5fa06a3f`
  and `3a90c21d2d99d2f5fef8bf2a173bfc7547ecb66a`, including ancestor relationship.
  The paper now says internally prespecified, not publicly preregistered.
- Fresh CPU reproduction reconciled 48 ladders and 912 adjacent pairs. All original
  diagnostic rows and numerical grouped statistics match exactly; newer metadata adds
  an outcome label and temporal configuration. Reference and redox JSON match exactly.
- Continuation evidence is hash/dimension checked; full SCC continuation MBAR solves
  are not rerun in the different local environment.
- Journal instructions checked directly on 2026-10-13: [submission guidelines](https://journals.plos.org/plosone/s/submission-guidelines)
  and [figures](https://journals.plos.org/plosone/s/figures).
- Final generated artifacts carry manifests; deposit instructions disclose lost A4V raw
  data, unknown original gate PyMBAR version and the uncommitted source overlays.
