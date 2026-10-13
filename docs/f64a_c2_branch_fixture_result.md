# F64A C2 live branch fixture: accepted technical result

**Verdict: accepted for the bounded checkpoint-branch mechanism, 2026-10-03.** The user ran the selected one-job release as job **7865574** on `scc-504.scc.bu.edu` and supplied the saved phase summaries and scheduler accounting. The agent did not access SCC or independently download the remote output files. Preserve the selected package, manifests, `attempt/`, job log, accounting record, and retained scratch. No rerun is needed.

The selected package's remote `SHA256SUMS` digest matched the local seal `a91fa357fbce0d54295fdfe97da5e415aad0c5995b2a6e0243c341df91577f64`. Package and source reviews passed. Runtime reported no failure, 20 matching MPS clients and cleanup in each phase, and `C2_BRANCH_INPUTS_FROM_NO_EXCHANGE_COMMON_REVIEW_PASS`.

| Phase | States | Final checkpoint | DHDL/energy records per state | XTC frames per state | Exchange |
|---|---:|---|---:|---:|---|
| Shared common | 20 | Step 1100, part 1 | 12/12 | 6 | No rounds |
| Baseline branch | 20 | Step 3100, part 2 | 21/21 | 10 | No rounds |
| HREX branch | 20 | Step 2600, part 2 | 16/16 | 8 | 3 rounds |

HREX rounds occurred at steps 1500, 2000 and 2500. They attempted 29 neighboring swaps, accepted 23, and attempted every one of the 19 neighboring links. The saved final state-to-walker mapping is a permutation of 0–19 consistent with the three reported rounds. Links 0–1, 3–4 and 17–18 had no accepted swap in this short fixture; the registered technical rule requires attempts and consistent permutations, not acceptance on every link.

The common seal lists 330 entries, the branch-input seal 361, the output-hash manifest 1608, and the post-accounting manifest 1611. The first, successful one-time accounting call verified the output-hash manifest before saving scheduler accounting. The attempt's storage summary totals 524,954,094 bytes. Runtime maxima of 524,885,081 persistent bytes and 142,801,721 scratch bytes were below the 1.5-GiB stop thresholds. These checks are supported by user-supplied SCC summaries; the agent has not independently rehashed the remote binaries.

`qacct` reports one `l40s` job, `omp16`/16 slots, `failed=0`, `exit_status=0` and 306 seconds. Its allocation was 0.085 GPU-hours and 1.36 CPU-slot-hours, below the selected 0.5/8 ceilings. Actual billed SU remains unknown. A second accounting call stopped at the expected `accounting already recorded` guard; the first success and saved accounting record remain valid.

This result qualifies the live shared no-exchange checkpoint, sealed two-arm branch, baseline/HREX execution, and post-branch exchange mechanics. It does **not** establish a production preparation length, retained sampling duration, replication, convergence, a reliable ΔG/ΔΔG estimate, or a scientific HREX advantage. The historical failed validation gate and 15-ns F64A stop remain in force. No production comparison or further GPU job is selected by this result.
