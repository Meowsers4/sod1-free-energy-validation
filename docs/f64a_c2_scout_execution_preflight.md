# F64A C2 paired scout: SCC execution preflight

Prepared 2026-09-29 after the user-reported `scc-i01` review pass of the
[guarded v4 runtime candidate](f64a_c2_scout_gpu_runtime_candidate.md).
This package is a **non-submitting preflight**, not the executable scout
release. It does not change the accepted CPU inputs or reviewed v4 package.

The locally sealed package is
`packages/f64a-c2-scout-execution-preflight-20260929-v1`. Its three-entry
`SHA256SUMS` SHA-256 is
`8251a19e93c6941d5f1720ce3c8ff07f746a7be8abd70c7858b109b81959bd29`.
`PREFLIGHT_ON_SCC.sh` uses only
`qsub -w v` on an inert temporary script to test the exact proposed
one-L40S, `omp16`/16-slot, two-hour request. It then queries `pquota`, both
project filesystems, project write access and the `acctool` balance. The
balance query is through yesterday, so it may lag today's jobs. It does not
establish a billed SU tariff.

The proposed pair remains baseline first, then HREX only after a technical
and accounting pass of baseline. Each arm has one two-hour request and no
automatic retry, for at most four allocated GPU-hours and 64 requested
CPU-slot-hours across the pair. Both arms use the accepted identical 20
TPRs and exact r6 SIF. Neither arm is yet selected for submission, and no
production or free-energy arm is authorized.

## Run on SCC

From a local Mac terminal in the repository root:

```bash
cd /Users/bodebosell/sod1fep || exit
scp -r packages/f64a-c2-scout-execution-preflight-20260929-v1 \
  bodeb@scc1.bu.edu:/project/rise-batteries/bode/container-build-packages/
```

Then in the user's `scc-i01` terminal:

```bash
PKG=/project/rise-batteries/bode/container-build-packages/f64a-c2-scout-execution-preflight-20260929-v1
cd "$PKG" || exit
sha256sum SHA256SUMS
bash PREFLIGHT_ON_SCC.sh > preflight.log 2>&1
preflight_rc=$?
printf 'preflight_exit=%s\n' "$preflight_rc"
cat preflight.log
```

Keep the complete `preflight.log` and paste the output, including any error.
The script has no execution-release contract or submission command. After
reviewing the queue, quota and SU evidence, prepare the separate sealed
execution release with the actual SGE script and explicit one-attempt guard.
Its submission remains a separate decision under `CLAUDE.md` rule 6.

## SCC preflight result — 2026-09-30 UTC

The user supplied `scc-i01` output for the exact package SHA-256 above. All
three files passed `sha256sum -c`; `qsub -w v` found a suitable queue for one
L40S, `omp16`/16 slots and `h_rt=02:00:00`, with no job submitted. The fresh
project quota was 23.63/50 GB and 205,061/1,638,400 files for `/project`,
and 46.32/50 GB and 466,518/1,638,400 files for `/projectnb`. `df` reported
32G free on `/project` and 8.7G on `/projectnb`; `/project/rise-batteries`
was writable. These are point-in-time login-node checks. The job will still
check quota and compute-node scratch before dynamics.

The overall script exited 127 at `acctool: command not found`. This exact
limitation had already appeared in the [September GPU preflight](gromacs_gpu_preflight_2026-09-24.md);
the package should have treated it as an unavailable query and preserved the
completed checks. Do not rerun the queue/storage work just to reproduce the
same error. Current SU balance and the applicable L40S tariff remain
unverified. [BU's project management guide](https://www.bu.edu/tech/support/research/account-management/manage-project/)
says an individual project member can view remaining SUs on the RCS User
Information page linked there. Its documentation also describes accounting
by requested CPU-slot walltime and node-specific SU rate. An explicit
decision is needed if that balance remains unavailable before the scout.
