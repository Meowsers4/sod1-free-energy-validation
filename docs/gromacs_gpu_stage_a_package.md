# Stage A package — four-rank synthetic GPU smoke

This package prepares a single-host, four-L40S, four-rank test with a ten-minute
SGE limit. It reuses the verified r6 SIF. No build, Stage B, MPS, protein work,
retry, or automatic submission is included. Preparation is authorized; GPU
submission remains separate. Generation is a CPU-only Snakemake rule.

Submitted package revision: `gmx-gpu-stage-a-20260924-v2`. Revision v1 stopped
after its first successful `grompp` because Singularity's automatic contained
`/tmp` replaced the explicit scratch bind. Revision v2 disables that automatic
mount and verifies a read/write round-trip to the private scratch directory
before input generation or GPU work. It also prints warning text/log paths and
the tail of failed command output. Preserve v1 and its preparation logs.

Replacement candidate: `gmx-gpu-stage-a-20260927-v3-omp4`, generated from
`docs/gromacs_gpu_stage_a_omp4_v1.yaml`. It requests `omp`/four CPU slots for
the same four one-thread MPI ranks. All GPU, physics, seed, image and time-limit
settings are unchanged. The existing job 7726162 must not overlap this candidate.
Do not change its PE with `qalter`: v2's immutable contract would reject that.
Prepare and review the candidate first, inspect current queue/quota and `omp`
configuration, then resolve the old job's state before any replacement submission.
An old job that has started must be reviewed, not treated as an unused attempt.
Package preparation is not a submission and does not consume the GPU attempt.

## Frozen toy inputs

`source-spec.yaml` declares the new toy physics parameters. This separate fixture
specification preserves historical `config/pipeline.yaml` unchanged; the latter
supplies only the lambda vector and is copied with its hash. `contract.json`
maps source indices 0, 6, 13, 19 to local indices 0–3 (0, 0.3529, 0.7647, 1).

There are 512 neutral LJ particles on an 8×8×8 lattice in a 4 nm periodic cube,
with spacing 0.5 nm, mass 39.948 u, sigma 0.34 nm and epsilon 0.997 kJ/mol.
Only the first particle changes epsilon, to 1.047 kJ/mol at B. Each particle is
its own molecule. None disappears; the lattice has no overlapping particles.
There is no protein force field, constraint, PME or bonded interaction.

Stochastic dynamics uses 120 K, a 1 fs timestep, 1 ps friction timescale, fixed
volume, a 1 nm cutoff and 1,000 steps. Explicit state-dependent velocity and
thermostat seeds and lambda index are the only MDP differences. Outputs include
all four foreign-state energy differences every 100 steps, and coordinates every
200 steps. Neighbor exchange uses interval 100 and a fixed seed. This operational
fixture is not equilibrated argon or a free-energy result. No extension is allowed.

## CPU-only preparation on SCC

Transfer the fresh package to the SCC project package area. Never merge into an
existing preparation/attempt. On `scc-i01`, inside that transferred directory:

```bash
sha256sum --check --strict SHA256SUMS
bash PREPARE_ON_SCC.sh
```

Preparation verifies package files and the existing SIF hash, checks runtime
Python inside that image, and runs `grompp`/`dump` for all four states. No `mdrun`,
`qsub` or allocation is invoked. It writes `prepared/PREPARED.json` with hashed
TPRs/inspection evidence, printing `INPUTS_PREPARED` only after all checks pass.
The preparation subprocesses have a ten-minute combined limit and per-grompp/dump
limits of three minutes. Warnings fail; there is no `-maxwarn` override.

Logs remain under `prepared/`. Partial preparation is preserved; rerunning refuses
to overwrite it. Return the terminal output and `prepared/PREPARED.json` for
review. No background process, `tail -f`, or persistent shell variable is needed.
The image is not rebuilt or changed.

## Container and rank mapping

Direct `singularity exec` follows the corrected r6 dependency-check route, avoiding
the wrapper's host-dependent GPU detection. Explicit `--nv` is used only for GPU
probes/dynamics. `--cleanenv`, `--contain` and `--no-mount bind-paths,hostfs,cwd,tmp`
disable environment leakage and configured mounts. Explicit binds expose this
package at `/smoke` and fresh private scratch at `/tmp`. The image's CUDA under
`/usr/local` stays visible and MPI gets a writable session directory. CPU
preparation verifies the private `/tmp` bind before GPU time is requested.
The same mount check runs again inside the GPU allocation. Container/runtime
warnings and numbered GROMACS input warnings remain blocking and are reported
with their actual text. On a non-GPU preparation host, OpenMPI's missing-driver
message is retained in the log; it is not evidence of a failed `grompp`.

The original scheduler `CUDA_VISIBLE_DEVICES` is forwarded unchanged through
`SINGULARITYENV_CUDA_VISIBLE_DEVICES`; host MPI/library paths and other container
overrides are removed. A CUDA driver probe enumerates visible UUIDs without
creating competing GPU contexts and compares them with the scheduler's assigned
devices in `nvidia-smi`. Each rank selects one verified ordinal through `-gpu_id`;
it does not alter the assigned device list. GROMACS's `PP:` map must agree.
Short-range GPU work is explicit; update/constraints remain on CPU.

One container-local MPI launcher starts four local ranks (`localhost:4`, isolated
launcher, no host MPI or oversubscription). Each rank controls one multidir state.
The SGE reservation is 32 slots in v2 and four slots in v3-omp4. Clean container startup does not import the
host SGE remote-launch environment. Single-host placement and slots are checked
before launch. CPU binding is off for this short operational test.
See [Singularity mounts](https://docs.sylabs.io/guides/4.0/user-guide/bind_paths_and_mounts.html)
and [GROMACS GPU selection/update](https://manual.gromacs.org/2025.3/user-guide/mdrun-performance.html).

## Job review and bounds

`stage_A.sge` requests `rise-batteries`, `l40s`, the PE/slots in `contract.json`
(`mpi32`/32 in v2; `omp`/4 in v3-omp4), four L40S GPUs,
ten minutes, no array and no rescheduling. Submit only from the verified package
directory after separate review; no submission helper is included.
`bash REVIEW_ON_SCC.sh` rechecks sealed inputs without submitting. Current SU
balance remains unresolved (`acctool` was unavailable on `scc-i01`); the user
accepted this uncertainty for the single Stage A attempt. Do not infer permission
for an additional attempt or overlap with the existing job.

One attempt is permitted per package: job startup atomically creates `attempt/`
and refuses an existing attempt, including failed attempts. Never remove the marker
to retry. The job checks SIF/input hashes, PE hostfile, slots, device assignment,
current quota and local free space before dynamics.

Preflight/dynamics commands share a seven-minute deadline; three minutes remain
for evidence inside SGE's ten-minute limit. A deadline or 1.5 GiB storage stop
sends TERM, then KILL if needed, to the command's process group. Any nonzero exit
is terminal. The 2 GiB new-file budget includes preparation, outputs and private
scratch, excluding the existing SIF. Periodic storage monitoring uses a 0.5 GiB
margin; it is not an exact filesystem quota. Scratch is recorded and retained
after the GPU attempt.

## Results

`attempt/` retains command arrays, allocation/device/rank records, logs, DHDL,
EDR, XTC, coordinates, checkpoints and hashes. Validation requires complete finite
DHDL with correct state/foreign-state labels, checkpoints at step 1,000, correct
GPU mapping, matching neighbor exchange records, at least one accepted swap and
consistent state-to-walker permutations. Stage A does not test restart.

`attempt/status.json` reports failure or `pass_pending_review_and_accounting`.
Retain `qacct -j JOB_ID` after accounting appears; account for actual PE records
and scheduler walltime. The runner's observed duration is not billed usage.
Local CPU checks do not establish SCC MPI/GPU behavior. A technical pass does
not authorize Stage B or protein sampling.
