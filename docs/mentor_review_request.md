# Draft request for independent computational-biophysics review

Status: the user's existing mentor, Peter Vlasov, was identified on 2026-09-14 and a
request was drafted; **not sent**.

## Reviewer

Peter Vlasov, the user's existing mentor. His relationship to the user makes him the
appropriate first reviewer. A specialist in alchemical free-energy estimators can be added
later if he recommends one.

## Draft message

Subject: Request for a brief independent review of an SOD1 free-energy evidence package

Peter,

I have completed a retrospective methods-and-limitations analysis of replicated
GROMACS/pmx alchemical calculations for SOD1 folding stability variants. The prespecified
experimental gate failed, and I am trying to make sure the resulting claims are scientifically
bounded before deciding whether a small follow-up GPU experiment is justified.

Would you be willing to review the evidence package, or suggest a computational biophysicist
who would be a better fit? I am especially looking for a short assessment of three points:

1. Is the comparison between the simulated apo, disulfide-reduced folding observable and the
   heterogeneous experimental constructs/states defensible as presented?
2. Is the interpretation of signed forward/reverse ladder hysteresis correct, including the
   finding that signed cancellation can hide local discrepancies and repeat disagreement?
3. Is the reported disulfide sensitivity and its conditional uncertainty stated at an
   appropriate strength, without treating a small observed shift as equivalence?

A useful response would simply classify the main claims as defensible, incorrect, or still
untested. The compact entry points are:

- `docs/methods_limitations_outline.md`
- `docs/stop_rule_reanalysis.md`
- `docs/reference_state_audit.md`
- `docs/temporal_analysis_results.md`
- `docs/review/` and `docs/temporal_review/` for figures and machine-readable records

The work is exploratory after a known failed gate; I am not asking the reviewer to endorse a
positive predictive result. I would be grateful for even a brief high-level review.

Thank you,

Bode Bosell
