"""Prepare sealed, CPU-only F64A protein technical TPRs in the exact r6 SIF.

No mdrun, MPI launch, scheduler call, GPU request, or source-tree mutation.
The input package remains for review even if preparation fails partway.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import yaml


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mdp_values(body):
    values = {}
    for line in body.splitlines():
        physical = line.split(";", 1)[0]
        if "=" not in physical:
            continue
        key, value = physical.split("=", 1)
        key = key.strip().lower()
        require(key not in values, "duplicate MDP key: " + key)
        values[key] = value.strip()
    return values


def technical_mdp(original, changes):
    """Change only registered timing/output keys; preserve all physical settings."""
    before = mdp_values(original)
    require(set(changes).issubset(before), "technical key absent from source MDP")
    lines = ["; F64A r0 technical qualification input; no free-energy estimate"]
    for line in original.splitlines():
        if line.lstrip().startswith("; equilibration steps discarded downstream:"):
            lines.append("; historical analysis-discard schedule does not apply to this technical input")
            continue
        body, separator, comment = line.partition(";")
        if "=" not in body:
            lines.append(line)
            continue
        key, _ = body.split("=", 1)
        normalized = key.strip().lower()
        if normalized in changes:
            line = key + "= " + str(changes[normalized])
            if separator:
                line += ";" + comment
        lines.append(line)
    result = "\n".join(lines) + "\n"
    after = mdp_values(result)
    require(set(before) == set(after), "MDP keys changed")
    require(all(after[k] == (str(changes[k]) if k in changes else v)
                for k, v in before.items()), "unregistered MDP value changed")
    return result


def validate_spec(spec, pipeline, inventory):
    require(spec["schema_version"] == 1 and spec["stage"] == "P", "wrong spec identity")
    require(spec["scope"] == "f64a_folded_apo_2sh_r0_technical_inputs_only", "wrong scope")
    require(spec["execution_authorized"] is False and
            spec["production_authorized"] is False, "executable scope forbidden")
    source = spec["source"]
    require(source["repeat"] == 0, "only inventoried r0 is qualified")
    count = int(source["states"])
    fep = pipeline["fep"]
    require(count == fep["lambda_windows"] == 20, "lambda count drift")
    require(fep["pmx_forcefield"] == source["pmx_forcefield_name"], "force field drift")
    require(fep.get("keep_disulfide_reduced", True) is True, "reduced source required")
    require(inventory["complete"] and inventory["states"] == count and
            inventory["repeat"] == 0 and not inventory["missing"], "source inventory failed")
    require(inventory["config_sha256"] == source["pipeline_sha256"], "inventory/config mismatch")
    t = spec["technical_mdp"]
    require(set(t) == {"nsteps", "first_stop_step", "replex", "nstcalcenergy",
                       "nstenergy", "nstdhdl", "nstlog", "nstxout-compressed"},
            "technical settings must be explicit")
    require(all(isinstance(v, int) and v > 0 for v in t.values()), "invalid technical step/stride")
    require(t["first_stop_step"] < t["nsteps"] and
            t["first_stop_step"] % t["replex"] == 0 and
            t["nsteps"] % t["replex"] == 0, "restart/exchange schedule mismatch")
    require(all(t["first_stop_step"] % t[k] == 0 and t["nsteps"] % t[k] == 0
                for k in ("nstcalcenergy", "nstenergy", "nstdhdl", "nstlog",
                          "nstxout-compressed")), "output stride misses restart boundary")
    require(spec["candidate_runtime"]["walltime_seconds"] is None and
            spec["candidate_runtime"]["attempts"] is None, "GPU runtime cannot be admitted here")


def verify_source(spec, inventory):
    source = Path(spec["source"]["root"])
    require(source.is_dir(), "source root missing")
    for name, record in inventory["system"].items():
        path = source / "system_r0" / name
        require(path.is_file() and digest(path) == record["sha256"], "system source changed: " + name)
    for i in range(spec["source"]["states"]):
        name = "w{}_r0".format(i)
        for filename, record in inventory["windows"][name]["files"].items():
            path = source / name / filename
            require(path.is_file() and digest(path) == record["sha256"],
                    "window source changed: {}/{}".format(name, filename))


def check_source_mdps(spec, pipeline):
    source = Path(spec["source"]["root"])
    vector = [float(x) for x in pipeline["fep"]["lambda_vector"]]
    reference = None
    for i in range(spec["source"]["states"]):
        values = mdp_values((source / "w{}_r0".format(i) / "prod.mdp").read_text())
        require(values.get("init-lambda-state") == str(i), "wrong source state index")
        require([float(x) for x in values["fep-lambdas"].split()] == vector,
                "source lambda vector drift")
        require(values.get("free-energy", "").lower() == "yes" and
                values.get("calc-lambda-neighbors") == "-1", "all-state energies missing")
        require(float(values["dt"]) == float(pipeline["fep"]["timestep_fs"]) / 1000,
                "timestep drift")
        common = {k: v for k, v in values.items()
                  if k not in ("init-lambda-state", "gen-seed", "ld-seed")}
        if reference is None:
            reference = common
        require(common == reference, "source MDP physical/output settings differ")


def container_environment(ffroot):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SINGULARITY", "APPTAINER", "OMPI_", "GMX_", "CUDA_"))}
    for key in ("LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    env["SINGULARITYENV_GMXLIB"] = str(ffroot)
    env["SINGULARITYENV_GMX_MAXBACKUP"] = "-1"
    return env


def run_grompp(spec, prepared, state, started):
    s = spec["source"]
    output = prepared / "states" / "state{:02d}".format(state)
    root = prepared / "inputs"
    ffcopy = prepared / "forcefield"
    ffroot = s["pmx_forcefield_root"]
    image = spec["image"]
    timeout = min(spec["preparation"]["command_timeout_seconds"],
                  spec["preparation"]["total_timeout_seconds"] - (time.monotonic() - started))
    require(timeout > 0, "total CPU preparation deadline expired")
    command = ["singularity", "exec", "--cleanenv", "--contain", "--no-mount",
               "bind-paths,hostfs,cwd,tmp", "--bind", str(root) + ":/protein:ro",
               "--bind", str(ffcopy) + ":" + ffroot + ":ro",
               "--bind", str(output) + ":/tmp", "--pwd", "/tmp",
               image["path"], image["gmx"], "grompp",
               "-f", "/protein/states/state{:02d}/technical.mdp".format(state),
               "-c", "/protein/states/state{:02d}/start.gro".format(state),
               "-p", "/protein/system/hybrid.top", "-o", "/tmp/topol.tpr"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=timeout, env=container_environment(ffroot))
    except subprocess.TimeoutExpired as exc:
        (output / "grompp.log").write_text(str(exc) + "\n")
        raise RuntimeError("grompp timeout at state {}".format(state))
    (output / "grompp.log").write_text(result.stdout)
    require(result.returncode == 0, "grompp failed at state {}; see {}".format(state, output))
    require(not re.search(r"^\s*WARNING", result.stdout, re.M),
            "grompp warning at state {}; see {}".format(state, output))
    require((output / "topol.tpr").is_file() and (output / "mdout.mdp").is_file(),
            "grompp outputs missing at state {}".format(state))
    return {"state": state, "tpr_sha256": digest(output / "topol.tpr"),
            "mdout_sha256": digest(output / "mdout.mdp"),
            "notes": len(re.findall(r"^NOTE\s+\d+", result.stdout, re.M))}


def manifest(root):
    lines = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            lines.append("{}  {}".format(digest(path), path.relative_to(root)))
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def tree_hashes(root):
    return {str(path.relative_to(root)): digest(path)
            for path in sorted(root.rglob("*")) if path.is_file()}


def prepare(spec_path, package):
    spec_path = spec_path.resolve()
    spec = yaml.safe_load(spec_path.read_text())
    source = spec["source"]
    pipeline_path = Path(source["pipeline"])
    require(digest(pipeline_path) == source["pipeline_sha256"], "pipeline hash changed")
    pipeline = yaml.safe_load(pipeline_path.read_text())
    inventory_path = Path(source["inventory"])
    inventory = json.loads(inventory_path.read_text())
    validate_spec(spec, pipeline, inventory)
    verify_source(spec, inventory)
    check_source_mdps(spec, pipeline)
    image = Path(spec["image"]["path"])
    require(digest(image) == spec["image"]["sha256"], "r6 SIF hash changed")
    ffroot = Path(source["pmx_forcefield_root"])
    require((ffroot / (source["pmx_forcefield_name"] + ".ff")).is_dir(),
            "pmx force field missing")
    prepared = package / "prepared"
    require(package.is_dir() and not prepared.exists(), "fresh prepared directory required")
    prepared.mkdir()
    started = time.monotonic()
    shutil.copy2(spec_path, prepared / "source-spec.yaml")
    shutil.copy2(Path(__file__), prepared / "builder.py")
    shutil.copy2(inventory_path, prepared / "source-inventory.json")
    shutil.copy2(pipeline_path, prepared / "historical-pipeline.yaml")
    shutil.copytree(ffroot, prepared / "forcefield")
    ff_hashes = tree_hashes(ffroot)
    require(ff_hashes == tree_hashes(prepared / "forcefield"),
            "pmx force-field snapshot differs from source")
    system = prepared / "inputs" / "system"
    system.mkdir(parents=True)
    source_root = Path(source["root"])
    for name in ("hybrid.top", "posre.itp"):
        shutil.copy2(source_root / "system_r0" / name, system / name)
    changes = {k: v for k, v in spec["technical_mdp"].items()
               if k not in ("first_stop_step", "replex")}
    for i in range(source["states"]):
        origin = source_root / "w{}_r0".format(i)
        target = prepared / "inputs" / "states" / "state{:02d}".format(i)
        target.mkdir(parents=True)
        shutil.copy2(origin / "em.gro", target / "start.gro")
        shutil.copy2(origin / "prod.mdp", target / "source.mdp")
        (target / "technical.mdp").write_text(technical_mdp(
            (origin / "prod.mdp").read_text(), changes))
    results = []
    for i in range(source["states"]):
        output = prepared / "states" / "state{:02d}".format(i)
        output.mkdir(parents=True)
        results.append(run_grompp(spec, prepared, i, started))
        print("state={} short_tpr_sha256={}".format(i, results[-1]["tpr_sha256"]), flush=True)
    record = {"stage": "P", "status": "cpu_inputs_prepared_pending_review",
              "production_authorized": False, "execution_authorized": False,
              "source_inventory_sha256": digest(inventory_path),
              "source_posre_sha256": digest(source_root / "system_r0" / "posre.itp"),
              "forcefield_tree_sha256": hashlib.sha256(json.dumps(
                  ff_hashes, sort_keys=True).encode()).hexdigest(),
              "source_spec_sha256": digest(spec_path), "sif_sha256": spec["image"]["sha256"],
              "states": results, "elapsed_seconds": time.monotonic() - started}
    (prepared / "PREPARED.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    manifest(prepared)
    print("F64A_PROTEIN_SHORT_TPRS_CPU_PREPARED_PENDING_REVIEW", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.spec, args.package)


if __name__ == "__main__":
    main()
