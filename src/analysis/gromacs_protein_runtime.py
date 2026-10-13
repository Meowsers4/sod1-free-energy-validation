"""Stage P protein runtime adapter and sealed-Tpr importer (Python 3.6+).

The proven synthetic wrapper supplies scheduler/MPS/restart mechanics. This
adapter replaces toy-only acceptance checks, verifies real-protein TPRs and
imports the already sealed CPU Stage P inputs. It never runs grompp or qsub.
"""

import json
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

if __name__ == "__main__":
    # The restart module imports `runtime`; reuse this running adapter instead
    # of executing it a second time and stacking the validator overrides.
    sys.modules.setdefault("runtime", sys.modules[__name__])

try:  # Names used in the standalone SCC transfer package.
    import smoke_runtime as base
    import protein_checks as protein
except ImportError:  # Names used by repository tests.
    from src.analysis import gromacs_gpu_smoke_runtime as base
    from src.analysis import gromacs_protein_runtime_checks as protein

# restart.py imports `runtime` in the transfer package and requires this API.
for _name in dir(base):
    if not _name.startswith("_"):
        globals()[_name] = getattr(base, _name)


def root_path():
    return Path(__file__).resolve().parent


def gro_identity(path):
    """Read atom labels/order while ignoring coordinates, velocities and title."""
    lines = Path(path).read_text().splitlines()
    base.require(len(lines) >= 3, "truncated GRO file: " + str(path))
    count = int(lines[1].strip())
    base.require(count > 0 and len(lines) == count + 3,
                 "GRO atom count/length mismatch: " + str(path))
    return count, tuple(line[:20] for line in lines[2:2 + count])


def validate_tpr_dump(text, state, spec):
    source = root_path() / "prepared" / state["directory"] / "start.gro"
    atom_count, _ = gro_identity(source)
    protein.validate_tpr_dump(text, state["local_index"], atom_count,
                              [item["lambda_value"] for item in spec["states"]],
                              spec["fixture"]["nsteps"], spec["fixture"]["dt_ps"])


def parse_exchange(text, count, interval, nsteps):
    return protein.parse_exchange(text, count, interval, nsteps)


_original_validate_results = base.validate_results


def validate_results(root, spec):
    """Run base output checks, then require complete protein attempt coverage."""
    history = _original_validate_results(root, spec)
    review = protein.exchange_summary(history, len(spec["states"]),
                                      spec["fixture"]["replex"],
                                      spec["fixture"]["nsteps"])
    name = ("protein-ladder-review-first.json" if spec["fixture"]["nsteps"] ==
            spec["restart"]["first_stop_step"] else "protein-ladder-review.json")
    base.write_json(root / "attempt" / name, review)
    return history


_original_verify_prepared = base.verify_prepared


def verify_prepared(root, spec):
    """Verify imported hashes, protein provenance and atom order."""
    _original_verify_prepared(root, spec)
    record = json.loads((root / "prepared/PREPARED.json").read_text())
    source = Path(spec["prepared_source"]["path"])
    base.require(record["source_manifest_sha256"] ==
                 spec["prepared_source"]["manifest_sha256"],
                 "wrong Stage P source manifest")
    base.require(base.sha(source / "SHA256SUMS") == record["source_manifest_sha256"],
                 "Stage P manifest changed")
    base.require(base.sha(source / "PREPARED.json") == record["source_record_sha256"],
                 "Stage P prepared record changed")
    identities = []
    for state in spec["states"]:
        name = state["directory"]
        path = root / "prepared" / name
        base.require(base.sha(path / "topol.tpr") == record["tpr_sha256"][name],
                     "protein TPR/source hash mismatch: " + name)
        identities.append(gro_identity(path / "start.gro"))
    base.require(all(item == identities[0] for item in identities),
                 "protein GRO atom count/order differs across states")


# Patch only the standalone package's private wrapper copy. Repository imports
# must not alter the accepted synthetic A/R/L validator in a shared process.
if base.__name__ == "smoke_runtime":
    base.validate_tpr_dump = validate_tpr_dump
    base.parse_exchange = parse_exchange
    base.validate_results = validate_results
    base.verify_prepared = verify_prepared


def verify_stage_p(source, spec):
    base.require(source.is_dir(), "Stage P prepared source missing")
    base.require(base.sha(source / "SHA256SUMS") ==
                 spec["prepared_source"]["manifest_sha256"],
                 "Stage P source manifest hash mismatch")
    base.verify_package(source)  # All 344 entries, not only TPRs.
    record = json.loads((source / "PREPARED.json").read_text())
    base.require(record["status"] == "cpu_inputs_prepared_pending_review" and
                 record["execution_authorized"] is False and
                 record["production_authorized"] is False,
                 "Stage P source status/scope mismatch")
    base.require(record["sif_sha256"] == spec["image"]["sha256"] and
                 record["source_spec_sha256"] == spec["prepared_source"]["source_spec_sha256"],
                 "Stage P source identity mismatch")
    base.require(base.sha(source / "source-spec.yaml") ==
                 spec["prepared_source"]["source_spec_sha256"],
                 "Stage P source spec changed")
    base.require(len(record["states"]) == len(spec["states"]),
                 "Stage P state count mismatch")
    hashes = {}
    for state, entry in zip(spec["states"], record["states"]):
        name = state["directory"]
        base.require(entry["state"] == state["local_index"],
                     "Stage P state order mismatch")
        tpr = source / "states" / name / "topol.tpr"
        base.require(base.sha(tpr) == entry["tpr_sha256"],
                     "Stage P TPR hash mismatch: " + name)
        hashes[name] = entry["tpr_sha256"]
    return hashes


def import_protein_prepared(root, spec):
    """CPU-only import of Stage P TPRs into a fresh runtime package."""
    base.require(not os.environ.get("JOB_ID"), "import outside an SGE allocation")
    base.verify_package(root)
    source = Path(spec["prepared_source"]["path"])
    hashes = verify_stage_p(source, spec)
    base.require(base.sha(spec["image"]["path"]) == spec["image"]["sha256"],
                 "r6 SIF hash mismatch")
    target = root / "prepared"
    target.mkdir()  # Never replace partial or accepted evidence.
    scratch = Path(tempfile.mkdtemp(prefix="gmx-protein-import.", dir="/scratch"))
    deadline = time.monotonic() + spec["preparation"]["total_timeout_seconds"]
    important = re.compile(r"^\s*(?:natoms|nsteps|init-step|init-lambda-state|"
                           r"n-lambdas|calc-lambda-neighbors|dt|fep-lambdas)\s*=|"
                           r"^\s*all-lambdas:")
    try:
        for state in spec["states"]:
            name = state["directory"]
            origin = source / "states" / name
            inputs = source / "inputs" / "states" / name
            output = target / name
            output.mkdir()
            shutil.copy2(origin / "topol.tpr", output / "topol.tpr")
            shutil.copy2(inputs / "start.gro", output / "start.gro")
            shutil.copy2(inputs / "technical.mdp", output / "technical.mdp")
            command = base.container_command(root, spec, scratch,
                     "/smoke/prepared/" + name) + [spec["image"]["gmx"],
                     "dump", "-s", "topol.tpr"]
            remaining = deadline - time.monotonic()
            base.require(remaining > 0, "CPU TPR import deadline expired")
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, universal_newlines=True,
                                        env=base.container_env(),
                                        timeout=min(remaining, spec["preparation"]["command_timeout_seconds"]))
            except subprocess.TimeoutExpired:
                raise ValueError("GROMACS dump timed out for " + name)
            full = result.stdout
            base.write_json(output / "tpr-dump-meta.json", {
                "command": command, "exit_status": result.returncode,
                "full_output_sha256": hashlib.sha256(full.encode()).hexdigest(),
                "full_output_bytes": len(full.encode()),
                "warnings": re.findall(r"^\s*WARNING[^\n]*", full, re.M),
                "tail": full.splitlines()[-20:]})
            selected = [line for line in full.splitlines() if important.match(line)]
            (output / "tpr.dump").write_text("\n".join(selected) + "\n")
            base.require(result.returncode == 0, "GROMACS dump failed for " + name)
            base.require(not re.search(r"^\s*WARNING", full, re.M),
                         "GROMACS dump warning for " + name)
            validate_tpr_dump((output / "tpr.dump").read_text(), state, spec)
            print("state={} imported_tpr_sha256={}".format(state["local_index"],
                  hashes[name]), flush=True)
        record = {"sif_sha256": spec["image"]["sha256"],
                  "package_manifest_sha256": base.sha(root / "SHA256SUMS"),
                  "source_manifest_sha256": spec["prepared_source"]["manifest_sha256"],
                  "source_record_sha256": base.sha(source / "PREPARED.json"),
                  "tpr_sha256": hashes, "files": base.inventory(target),
                  "gpu_executed": False, "execution_authorized": False}
        base.write_json(target / "PREPARED.json", record)
        verify_prepared(root, spec)
        print("PROTEIN_TPRS_IMPORTED_AND_REVIEWED_CPU_ONLY; no job submitted")
    finally:
        shutil.rmtree(str(scratch))


def main():
    if len(sys.argv) < 2:
        raise ValueError("command required")
    if sys.argv[1] == "prepare":
        raise ValueError("protein TPRs must be imported from sealed Stage P inputs")
    if sys.argv[1] == "import-protein-prepared":
        root = root_path()
        spec = json.loads((root / "contract.json").read_text())
        import_protein_prepared(root, spec)
        return
    base.main()


if __name__ == "__main__":
    main()
