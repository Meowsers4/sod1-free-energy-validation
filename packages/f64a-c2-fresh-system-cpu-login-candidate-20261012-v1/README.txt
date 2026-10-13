F64A C2 isolated r3 CPU system-build login-shell correction candidate,
2026-10-12. This package is INACTIVE: execution_authorized=false.

Selected job 8032575 failed before system construction because MODULEPATH
was absent in its non-login batch shell, conda could not activate and old
fallback Python could not parse builder.py. The original job/package and
its one-attempt guard must be preserved. This fresh package archives its
manifest and the earlier source/release manifests, plus a failure summary.

The candidate batch script starts Bash as a login shell, attempts the site
profile if MODULEPATH is still empty, and refuses to continue unless the
module path, sod1-fep conda environment, and Python 3.11+ with pmx/yaml
are present. It still requests omp/8 for one hour and no GPU. The build
code and pinned F64A r3 source are otherwise the same. The builder and
submission guard reject execution while this package is inactive.

REVIEW_PACKAGE.sh and REVIEW_ON_SCC.sh are read-only static checks. They
do not establish that the corrected batch environment works on a compute
node. A new, separately selected and sealed execution package would be
required for any further scheduled probe or system build. No automatic
retry, FEP window dynamics, lambda-aware starts, GPU job, or production
inference is authorized.
