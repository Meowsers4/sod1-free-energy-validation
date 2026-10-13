"""Process-stable seeds for every stochastic step in the pipeline.

Python's built-in :func:`hash` is randomized per process (PYTHONHASHSEED), so
``hash((variant, leg))`` returns a DIFFERENT value in every SGE array task. Anything
seeded that way is not reproducible and -- worse -- windows of the same leg, which run
as separate processes, silently disagree about what they are sampling. This module is
the single source of deterministic seeds; never seed from :func:`hash`.

Seed scope matters (see :mod:`src.fep.perses_engine`):

* The Perses engine uses ``stable_seed(variant, leg, "system")`` for its shared
  system. The pmx engine uses that key only with shared-system mode; with
  ``independent_replicate_systems=true`` it uses
  ``stable_seed(variant, leg, rep, "system")`` for distinct ion placement.
  Every window *within one replicate* still uses the same solvated system.
* The pmx engine uses ``stable_seed(variant, leg, window, rep, "sampling")``
  for per-window sampling seeds; the Perses engine uses the same key. These
  are distinct from the system seed and deterministic across processes.
"""

from __future__ import annotations

import hashlib

_MAX_SEED = 2**31 - 1  # OpenMM RNG seeds are signed 32-bit; numpy accepts this range too


def stable_seed(*parts: object) -> int:
    """Deterministic non-negative seed for ``parts``, identical across processes/hosts.

    Args:
        parts: Any values identifying the thing being seeded; rendered with ``str``.

    Returns:
        A seed in ``[0, 2**31 - 1]``, stable across processes, Python versions and hosts.
    """
    key = "|".join(str(p) for p in parts).encode()
    return int.from_bytes(hashlib.blake2b(key, digest_size=8).digest(), "big") % _MAX_SEED
