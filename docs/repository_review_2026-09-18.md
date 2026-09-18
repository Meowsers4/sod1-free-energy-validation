# Repository review — 2026-09-18

The supplied review was checked against repository files, report contents, the
historical release, collected/executed tests and workflow behavior. Its main
findings are adopted, with the qualifications below. No new GPU work is authorized.

## Preservation and current state

Commit `5df6d3e` preserves the v2 report and both CPU audit packages. The report's
SHA-256 is `ddb20589d809682f7ef72a4fddc55c6998c48ca3b7a06b1b466682291a24ab71`.
It is the analysis output associated with production job **7620241**, not an
archive of the 60 raw matrices/checkpoints. An identical report also exists in
Downloads, so “only local copy” was not literally correct. The lack of committed
preservation was nevertheless real. The raw matrices remain on SCC; the authorized
raw-energy audit has not run on scientific data.

CLAUDE.md now names both completed pilots and the standing decision to **stop at
15 ns**. README status, authorization/scope language and changelog are synchronized
with HANDOFF. Mentor review remains deferred at the user's direction.

## Historical release and provenance

The September 14 bundle is a historical snapshot, not a current full repository
release. Its 1,217 manifest entries omit temporal review, pilot packages and v2.
Preserve its existing SHA-256:
`09cc1b2c7575b60afa1af38216b78ca8f126a668b83aa6ef283c06ff8eba7114`.
It lacks a recorded build commit. Commit `83c39bb` preserves the corrected figure
source; its `methods_figures.py` bytes match those in the old bundle, SHA-256
`707dd46ce73a4f823a06f7af535f21de9bedd82a43afb3929ea68f6661a70b5f`.
That is retrospective file identity, not proof of the old bundle's build revision.

The default Snakemake target now performs read-only transport/internal verification.
A real default invocation verified all 1,217 entries without scheduling producers.
An explicit rebuild at the old path fails during DAG admission, before producers
could overwrite review outputs. New builds require fresh review/bundle paths and
committed, clean executable/configuration/environment dependencies. The builder
records the commit and source hashes, checks temporary output before publication,
and publishes without replacing an existing bundle/checksum. Existing partials or
build locks are refused, not silently removed. The historical bundle is unchanged.
See [reproduction instructions](release_reproduction.md). Extended F64A raw
matrices/checkpoint trees are not automatically included by this historical builder.

## Tests, accounting and workflow

The previous seven-file test group contained **75**, not 70, tests; the earlier
project suite contained **242**, not 133. At review start the new audit tests had
brought the suite to 276. Seven release guard/provenance cases now bring the
current suite to **283**, with **82** in that seven-file group. All 283 passed
locally; this is not a new fresh-lock installation certification.

The SU-rate requirement was explicitly waived by user approval to proceed on
an unconfirmed **1 SU/core-hour planning assumption**. It was not verified pricing.
The reported 130 GPU-hour/two-attempt caps do not establish actual billed SU.
Accounting closeout remains pending SCC records; preserve them promptly using
[the capture guide](f64a_accounting_closeout.md). A shared project balance alone
cannot isolate this array's bill.

Both CPU audit rule files are now included in the main Snakefile. Their inclusion
changes the live workflow hash after the completed v2 run. It does not change the
recorded original `802cc9e` workflow identity or retroactively certify a new GPU
protocol. The original report/provenance remains preserved.

The release module's E702 and the same issue in its test were fixed. Scoped lint
checks pass, but repository-wide Ruff still reports seven pre-existing errors;
the results document now explicitly scopes its Ruff claim to audit files.

## Benchmark attribution and scientific claim

The benchmark numbers **r=0.87 / AUE=0.61** apply to the 38 staphylococcal nuclease
single mutations, not both proteins. For the 24 T4 lysozyme mutations, Results
and Figure 6B report GROMACS **r=0.80 / AUE=0.55**. The paper's abstract swaps the
T4 software labels relative to those Results; README now uses the Results
attribution. [Primary paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0335829).

F64A folded r1's original 3 ns estimate is **2.505941565 kcal/mol**, with net
hysteresis **0.022704558 kcal/mol**. Its later disjoint 6–9 ns estimate is
**0.429467066 kcal/mol**, a change of **−2.076474499 kcal/mol**. This directly
demonstrates that a small net closure diagnostic did not guarantee duration
stability on this path. The reported net metric is the absolute net of signed
local discrepancies, not itself a signed quantity. The comparison does not prove
which estimate is correct, establish experimental accuracy, or validate a general
early-warning classifier. Calling it the project's “strongest evidence” is an
interpretive judgment, not a separately tested result.
