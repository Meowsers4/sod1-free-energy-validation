# F64A C2 paired timing-scout CPU input package

**V2 status, 2026-09-29:** user-reported CPU preparation reached successful
state-0 `grompp` and wrote `mdout.mdp`, then halted in the builder's
`effective_checks` with `effective physical/output MDP mismatch`. It did not
seal 20 TPRs or run GPU work. Preserve the entire failed remote v2 package;
do not rerun it. The user supplied the saved state-0 effective MDP fields:
all reported timing, energy, lambda, precision and full-precision trajectory
values matched the candidate, while `compressed-x-grps` was blank. GROMACS
2025.3 documents that a blank/default group writes the whole system when
compressed output is enabled. V2's literal `System` check caused the halt;
it was a validator error, not a failed `grompp` or an unexpected physics change.
The [official output option description](https://manual.gromacs.org/documentation/2025.3/user-guide/mdp-options.html)
supports this interpretation.

**V3 status, 2026-09-29:** the local builder accepts either the documented
blank default or explicit `System`, while still rejecting a smaller group.
It now reports the exact key and values on any effective-MDP mismatch. The
source spec, requested MDP changes and execution-disabled scope are unchanged.
The user subsequently completed SCC CPU preparation: all 20 common TPR
hashes printed, `prepared_manifest_entries=381`, and
`REVIEW_PREPARED.sh` returned its 20-state pass marker with `review_exit=0`.
Prepared-manifest SHA-256 is
`cffefe198d66e670ebc7db2960039e2cfc159e64bb238af7d5c3fe13c7f64487`.
The [accepted CPU result](f64a_c2_scout_cpu_result.md) records every TPR
hash and the evidence limits. Preserve v3; no rerun is needed.

**V1 status, 2026-09-29:** the user transferred the first candidate to SCC.
Its CPU preparation halted at state 0 with `grompp failed/warned`; no TPR
set was sealed and no GPU job ran. Preserve that entire remote v1 package,
including `prepare.log` and `prepared/common/states/state00/grompp.log`.
Do not rerun it in place. The user supplied the saved state-0 log: GROMACS
reached `grompp` but failed with `Topology include file
"amber99sb-star-ildn-mut.ff/forcefield.itp" not found`. Its CUDA-aware MPI
warning and two GROMACS notes were not the fatal error.

The v1 builder omitted `SINGULARITYENV_GMXLIB` from its `--cleanenv` GROMACS
call. The accepted Stage P builder and prior exact-r6 source probe both set
this variable to the pmx force-field root. The missing include confirms the
omission caused v1's state-0 failure. V2 restored it, and SCC state-0
`grompp` completed before the separate validator issue described above.

Prepared locally 2026-09-29 for the [output/timing-scout design](f64a_c2_output_timing_scout_draft.md).
The transferable bundle is
[`packages/f64a-c2-scout-cpu-20260929-v3`](../packages/f64a-c2-scout-cpu-20260929-v3).
It contains a pinned YAML spec, one standalone builder, three CPU-only
review/preparation wrappers and a six-entry SHA-256 manifest. There is **no
SGE script, `qsub`, `mdrun`, MPI launch, GPU passthrough, submission guard
or execution authorization**. It does not prepare a production arm.

Bundle `SHA256SUMS` SHA-256:
`b5d4888989cb60914d7643cda459e8de176cc54fc7aea46aba36867e3e8e9783`.
Builder SHA-256:
`21621ff1bc4ca59d5c94bc8ce5448fa04844fb4ca16d149b153311d613d530e6`.
Spec SHA-256:
`50d2964cfef6ca95091ae05c390e3f7626dc66028d0599bdb28f05c11520cb60`.
The failed remote v2 manifest was
`2deabb3533a5d6eed07406302386c10a767dbd47466e26fc8b2069e46b5c88d2`;
the remote v1 manifest was
`85575f749cf1605a984db6d0506dcc903fb087d3d924ffe0e1f7e778912afa1f`;
the source spec and all intended MDP values are unchanged in v3.

## CPU preparation contract

The source is the *accepted* Stage P CPU `prepared/` tree, manifest SHA-256
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`.
The builder checks all 344 manifest entries, `PREPARED.json`, original r0
MDPs, starts, topology, force-field snapshot, pipeline/lambda vector, source
inventory and exact-r6 SIF hash before writing a new `prepared/` tree. It
copies the accepted r0 `source.mdp` and lambda-aware `start.gro` per state;
Stage P's 4-ps checkpoint or trajectories are never used.

The only changed MDP keys are `nsteps=50000`, `nstcalcenergy=500`,
`nstenergy=500`, `nstdhdl=500`, `nstlog=5000` and
`nstxout-compressed=25000`. At 2 fs this is a 100-ps **technical target**,
1-ps energy/free-energy stride, 10-ps log stride and 50-ps full-system XTC
stride. The builder checks unchanged physical source keys, grompp's
`mdout.mdp` effective values, all-state lambda evaluation, state indices,
whole-system coordinate group/precision and no full-precision trajectory.
Every `grompp` call runs through the exact r6 SIF with CPU-only Singularity
flags and no `-maxwarn`. Any warning, timeout, hash mismatch or other failure
leaves the partial package in place for inspection; do not rerun into it.

Twenty common TPRs are generated once and copied to isolated baseline and
HREX state trees. Their SHA-256 values must match byte-for-byte within each
state. Exchange remains a *runtime CLI difference*, not a TPR difference:
baseline `-replex 0`, HREX candidate `-replex 500`. This CPU package cannot
run either setting.

Local verification: `python -m pytest -q tests/test_f64a_c2_scout_cpu.py`
passed five targeted checks, including a mocked 20-state CPU preparation
rehearsal, a reviewer that rejects divergent arm TPRs, and a check that
rejects protein-only coordinate output while allowing the blank whole-system
default. `REVIEW_PACKAGE.sh` passed all six transferred-file hashes. V2 reached
exact-r6 `grompp` for state 0; v3 subsequently completed all 20 states and
passed `REVIEW_PREPARED.sh` as recorded above.

## Historical v3 transfer and CPU-only review commands

The commands below record the accepted v3 preparation. **Do not run them
again.** The agent did not log into SCC. Preserve v1/v2 failures and v3.
On `scc-i01`, create the destination parent once:

```bash
mkdir -p /project/rise-batteries/bode/container-build-packages
```

In a local Mac terminal at the repository root, transfer the small bundle:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-scout-cpu-20260929-v3 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

On `scc-i01`, in the `sod1-fep` Python environment, verify and prepare once:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-cpu-20260929-v3
cd "$PKG" || exit
sha256sum SHA256SUMS builder.py source-spec.yaml
bash REVIEW_PACKAGE.sh || exit
bash PREPARE_ON_SCC.sh > prepare.log 2>&1
prep_rc=$?
printf 'prepare_exit=%s\n' "$prep_rc"
tail -n 30 prepare.log
```

If `prepare_exit` is nonzero, retain the entire package and log and stop.
If it is zero, run the separate CPU-only review:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-cpu-20260929-v3
cd "$PKG" || exit
bash REVIEW_PREPARED.sh
printf 'review_exit=%s\n' "$?"
sha256sum prepared/SHA256SUMS
```

Return the three transferred-file hashes, `prepare_exit`, the final marker
and log tail, `review_exit`, and the prepared-manifest SHA-256. A pass means
only that **CPU scout inputs are prepared and reviewed**. A separate runtime
package with capped output monitoring, queue validation, MPS checks,
accounting and explicit selection is required before any GPU timing scout.
