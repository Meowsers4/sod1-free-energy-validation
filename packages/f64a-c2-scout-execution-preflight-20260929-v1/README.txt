F64A C2 paired 100-ps timing scout: SCC execution preflight only.

This package requests no allocation and starts no GPU job. Its sole qsub call
uses scheduler verification mode (-w v) for the proposed one-L40S, omp16,
16-slot, two-hour request. It also queries current project quotas and SU
balance. The 20-state CPU inputs and guarded v4 GPU runtime candidate remain
unchanged. The reviewed v4 runtime candidate has SHA256SUMS SHA-256
71473b55c4d0805da489fe59fc61ced4b738360e05651f5556570c0e1bc7d4df.
No scout arm has been selected or submitted by this package.

On scc-i01, run bash PREFLIGHT_ON_SCC.sh, retain its complete output, and
return the queue, quota, filesystem and acctool results for review. Do not
interpret the displayed SU balance as a charge tariff.
