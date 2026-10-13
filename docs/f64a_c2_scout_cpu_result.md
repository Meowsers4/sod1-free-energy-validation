# F64A C2 paired timing-scout CPU inputs — accepted review

Recorded 2026-09-29 from user-supplied `scc-i01` output for the fresh
[`f64a-c2-scout-cpu-20260929-v3` package](f64a_c2_scout_cpu_package.md).
This accepts **CPU input preparation only** for a prospective bounded paired
timing scout. It is not a GPU qualification, a production simulation, an
F64A free-energy result or authorization to submit a job. The agent did not
log into SCC or download the remote binaries.

The builder printed a SHA-256 for each exact-r6 `grompp` TPR and the marker
`F64A_C2_PAIRED_SCOUT_TPRS_CPU_PREPARED_PENDING_REVIEW; no job submitted`.
The separate `REVIEW_PREPARED.sh` returned
`F64A_C2_PAIRED_SCOUT_CPU_REVIEW_PASS states=20 manifest_entries=381
execution_authorized=False`, with `review_exit=0`. The reviewer checks the
prepared manifest, effective MDP values, source/scout MDP relation and
byte-identical baseline/HREX TPR copies for every state. The prepared
`SHA256SUMS` has **381 entries** and SHA-256
`cffefe198d66e670ebc7db2960039e2cfc159e64bb238af7d5c3fe13c7f64487`.
These assertions are accepted on the supplied terminal output; the local
agent has not independently rehashed files on SCC.

| State | Common and paired-arm TPR SHA-256 |
| ---: | --- |
| 0 | `f31aef6118cad78fbe9313944fe3d5a60c849603bab055131e32fa19795d3e45` |
| 1 | `9dcd6f1d8c28fd8165936af2c059631a2a6f5ab272eb47d3cf3802ee642973ab` |
| 2 | `6e35a82de4d086da9ed171da40ac10d847ce9b34947741ea62f2b94642896f21` |
| 3 | `d720c3adbed2eece8e10998f73841d7eb16909afc105493a7c0ef36724f449df` |
| 4 | `004a006b88a7ed22c074e1970684929c2b968d41732972b72d78f96ccd686da5` |
| 5 | `e93353614b4da850b9d76b82719523c3d7283f9d85622e849e14121769e15b0f` |
| 6 | `4248023977b40b47e683fd22f5c14545bd9eaa39b3cb6aaabb39d38d03f97388` |
| 7 | `927d24c6a0fada265f85ef44437b13a124235ab4798f4fb690b3286dec83fd5b` |
| 8 | `c676ed15ed8719bb791dc5160bb0e6b286c7e944b49ac7959acf3a0d86fac7eb` |
| 9 | `112638bd36ce97e1f24a22eddc07763528a8f596f0fafccb5676d324d06c1d3c` |
| 10 | `fed2927b6c22845fe3eb2ee754668ef3021ccd1623480ae09d9a85fa0320e549` |
| 11 | `1918206efe4d620e8e4ff743a4e72398aa90050df1ab4dcb88bb3e6d4f200e19` |
| 12 | `933dfea6035c86de7a0a27a8ef764d372ffa78628b94e4de2d14d66fb8b892c8` |
| 13 | `4b6635bbf606cde3fd1c867d96d3e82f35183cb42623cac309d6fe50d0e4f0e0` |
| 14 | `757837bfe91fcb926893f649b672405d675c47df3ff4d9d1437239b36ed701e1` |
| 15 | `715e59962573a1d32d37142f5c5ddfcdfa4f91fd7b78401900b2bf5f1a4b21f9` |
| 16 | `254c7985ee21f54652b020fe139c9b91d8e53c77b973f4b34c00e907dcdd67fc` |
| 17 | `347dc12d983efe6561e5e660c108bfdbfe09b22d5159f82d066bbfe1a4d9baa8` |
| 18 | `931f266ce03071ee97acdeeb97f31421ffa3424efb373892d31300044439d608` |
| 19 | `7a3f65cf4103d7a6bce350e34fa6aa59e4a3ebc8bdad59c4835dc8139f985699` |

The source is the accepted Stage P CPU-prepared r0 F64A folded apo-2SH
system. Only the registered timing/output MDP keys changed: 50,000 steps
(100 ps technical target), 1-ps all-state energy/dHdl stride, 10-ps log
stride and 50-ps full-system compressed-coordinate stride. A blank
`compressed-x-grps` in GROMACS 2025.3 is the documented whole-system
default. V1's missing `GMXLIB` and v2's over-strict group validator were
corrected in v3; preserve all three package histories and logs. No rerun of
the accepted v3 CPU preparation is needed.

**Next separate work:** build and review a non-submitting runtime candidate
that imports this exact 381-entry manifest and TPR hash set, implements the
one-GPU/20-rank/private-MPS baseline and HREX launch distinction, enforces
the proposed walltime/storage bounds, validates exchange/energy/coordinate
outputs and accounting, and guards one attempt per arm. Before any GPU scout,
check current queue/quota/SU and obtain explicit selection for its registered
scope. Scientific C2 duration, repeats and production remain unselected.
