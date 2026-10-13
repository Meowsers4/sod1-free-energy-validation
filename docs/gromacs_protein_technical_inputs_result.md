# Stage P F64A protein short-input preparation — accepted CPU result

Date: 2026-09-28. Source: user-supplied `scc-i01` terminal output; the agent did
not download or independently rehash the SCC package. Scope: F64A folded
apo-2SH `r0`, 20 states, exact r6 SIF, CPU `grompp` only. The synthetic Stage L
result and source compatibility checks are separate preceding evidence.

The transferred `builder.py` and `source-spec.yaml` matched their expected
SHA-256 values:

| File | SHA-256 |
| --- | --- |
| builder.py | `bebb3fc721db97895191e6ed53c589126a0e2ac6c9433433add804868bf90987` |
| source-spec.yaml | `155a24a60191334c0c06a3e02d3c21ecf51cea0902f5ebe5e53370b3c6c322cf` |

The builder reported `F64A_PROTEIN_SHORT_TPRS_CPU_PREPARED_PENDING_REVIEW`
after emitting all 20 short TPR hashes. `PREPARED.json` reported
`status=cpu_inputs_prepared_pending_review`, 20 states, 20 total GROMACS notes,
21.71199191501364 seconds builder elapsed, and both `execution_authorized` and
`production_authorized` false. The source inventory SHA-256 is
`c908e1c1695e0ebe8bd02dce2fece5bdbc83332d617528ca81495bd826c51fe2`;
the spec SHA-256 matches the transferred file, and the SIF SHA-256 matches
`0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee`.

The user then ran `sha256sum -c SHA256SUMS` in the prepared directory. Its exit
status was **0** for **344** entries. The manifest SHA-256 is
`858070ac1c8d757d0fdb0fa744148865e24abdccb8d82e3d1a670698734e77b9`;
the last three check lines (state 19 log, MDP and TPR) each said `OK`.
Thus the CPU short-input preparation is accepted on the supplied evidence.
Preserve `/projectnb/rise-batteries/bode/container-build-packages/f64a-protein-technical-20260928-v1`
including `prepare.log`, `sha256-check-final.log`, `prepared/` and its manifest.
Do not rerun preparation or clear its fresh-directory guard.

Reported short TPR SHA-256 values:

| State | SHA-256 | State | SHA-256 |
| ---: | --- | ---: | --- |
| 0 | `0c079617ddd45bdc8548e6c0ab11a9af156dbeaef77fb0bf6665c531803b31a6` | 10 | `62863e957f3a694d46c78208212edceeed89d1c071c888c3378c55050fa347fc` |
| 1 | `7df76e5c769e9dc8c197cc4b15bb09a75b5f8dc7ad2377e29d2a3ccb16e9dfe3` | 11 | `c8c4595ccc4633953b80197132c1b271ea37fda21f5e8b1b31c6f040f4a9737c` |
| 2 | `9839dfcda4d6322470193986a5e89e6bcb085441c61a33231082ddee0727bd86` | 12 | `c99956ea00e6c3f366ab3794911768b7ced9459b94820de705e9079f5bfd7972` |
| 3 | `7afb8d0d14b41721a67b0c55d113c2684fc7bb559826aeb77341de006b071613` | 13 | `7011d763ea7e999a9c94b551623cca99d73435fd9ca6cdb292d45276a46d5b06` |
| 4 | `fe52f50ffd6b915d9df8d88b494ed879e96b28f8d03807a6710efe34c9b69ec4` | 14 | `2b03f9b40b9c152ae254d487e1726c6dc1812cf33d6461a03ee422eed76a7fab` |
| 5 | `392c5ed26427bf0dd1d0271b8c9691d6849f0d6cc91f138ad02c26066ed49aca` | 15 | `84c44dff148f43756a90a2f3e0a4ea451800be6e5cf121578fbd33cc0ca3cee4` |
| 6 | `5a767a7565d21b6b902af853693946a3d47b8a9291d7cc669859f213bf8cb088` | 16 | `ad0ce7703d24400931c4da88bfc9b04a6e5ae9f72df8bb42f7dc8d02eaf5def7` |
| 7 | `484226714cd7b8f522c6f93454ab2134f25d9f57a5963aaeefc4b7dae27d64ba` | 17 | `07262424bc9492aee3207ba654d8675a1f1fd4c84611685ca59513c3488a6400` |
| 8 | `f8489bee0d3ed7f27353136d909651df54f9336967c10a50cf3c17c4f77c39c6` | 18 | `9e76466d389c22f7f3a66b8ab7a97d3eb163fae4d17bfd3925ea159527500d0f` |
| 9 | `1f7355e7341184117ba432f810c895b500e54a59c68cc67f2b7d542309bc0d5f` | 19 | `37f47a745f0d2ecfa7cf6aed7aa850be2cfb225c653dcc4532d92568d99b72e6` |

This result establishes TPR generation and integrity, not protein GPU memory,
MPI/MPS exchange, checkpoint/restart, finite output, throughput or scientific
sampling quality. A new runtime package needs protein-specific validators,
measured input/storage estimates, fixed walltime and a separate single-attempt
resource admission. No GPU simulation has been launched from Stage P.

## Read-only sizing supplied after acceptance

On `scc-i01`, the user reported `du -sh` of the sealed `prepared/` tree as
**89 MB** and the total of its 20 `topol.tpr` files as **28 MB**. All 20
`grompp.log` files contain the estimate “This run will generate roughly 5 Mb of
data,” giving roughly **100 MB of GROMACS-estimated run data** across the ladder.
This estimate omits runtime wrapper logs, duplicate checkpoint archives and
diagnostic extraction, so it is not a storage cap. `df -h` reported 9.3 GB
available on `/projectnb`. A subsequent `pquota rise-batteries` reported
50 GB quota and 45.79 GB use for `/projectnb/rise-batteries`, or about
4.21 decimal GB remaining at that snapshot. Runtime import and execution
must recheck quota and compute-node `/scratch` free space. These measurements provide no timing or
GPU-memory estimate.
