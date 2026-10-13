"""Read-only inventory of one historical F64A folded-leg realization on SCC.

Print JSON to stdout. Never creates, repairs, or runs a simulation. Python 3.6+.
"""

import argparse
import hashlib
import json
from pathlib import Path

import yaml


SYSTEM_FILES = ("SYSTEM_READY", "hybrid.top", "em.gro", "conf.gro")
WINDOW_FILES = ("em.gro", "em.mdp", "prod.mdp", "prod.tpr")


def file_record(path):
    if not path.is_file():
        return {"exists": False}
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"exists": True, "bytes": path.stat().st_size,
            "sha256": digest.hexdigest()}


def mdp_values(path):
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text().splitlines():
        body = line.split(";", 1)[0]
        if "=" in body:
            key, value = body.split("=", 1)
            values[key.strip().lower()] = value.strip()
    return values


def inventory(source, repeat, config):
    source = source.resolve()
    with config.open() as stream:
        fep = yaml.safe_load(stream)["fep"]
    states = int(fep["lambda_windows"])
    expected_vector = [float(value) for value in fep["lambda_vector"]]
    if len(expected_vector) != states:
        raise ValueError("config lambda count differs from fep.lambda_windows")
    system = source / ("system_r{}".format(repeat))
    result = {
        "purpose": "read_only_f64a_folded_source_inventory",
        "source": str(source), "repeat": repeat, "states": states,
        "config": str(config.resolve()), "config_sha256": file_record(config)["sha256"],
        "system": {name: file_record(system / name) for name in SYSTEM_FILES},
        "windows": {}, "missing": [],
    }
    for name, record in result["system"].items():
        if not record["exists"]:
            result["missing"].append("system_r{}/{}".format(repeat, name))
    marker = system / "SYSTEM_READY"
    marker_text = marker.read_text() if marker.is_file() else ""
    result["system_marker_matches"] = all(
        token in marker_text.split() for token in
        ("variant=F64A", "leg=folded", "rep={}".format(repeat)))
    for state in range(states):
        directory = source / "w{}_r{}".format(state, repeat)
        files = {name: file_record(directory / name) for name in WINDOW_FILES}
        for name, record in files.items():
            if not record["exists"]:
                result["missing"].append("{}/{}".format(directory.name, name))
        mdp = mdp_values(directory / "prod.mdp")
        result["windows"][directory.name] = {
            "files": files,
            "mdp": {key: mdp.get(key) for key in (
                "init-lambda-state", "fep-lambdas", "free-energy", "dt", "nsteps",
                "constraints", "coulombtype", "pcoupl", "calc-lambda-neighbors",
                "sc-function", "sc-alpha", "sc-power", "sc-sigma", "sc-coul")},
        }
    vectors = {entry["mdp"]["fep-lambdas"] for entry in result["windows"].values()}
    result["consistent_lambda_vector"] = len(vectors) == 1 and None not in vectors
    try:
        actual_vector = [float(value) for value in next(iter(vectors)).split()]
    except (AttributeError, ValueError, StopIteration):
        actual_vector = []
    result["matches_config_lambda_vector"] = actual_vector == expected_vector
    physical = [tuple((key, value) for key, value in entry["mdp"].items()
                      if key != "init-lambda-state")
                for entry in result["windows"].values()]
    result["consistent_mdp_physics"] = len(set(physical)) == 1
    result["all_state_energies_requested"] = all(
        entry["mdp"]["calc-lambda-neighbors"] == "-1"
        for entry in result["windows"].values())
    result["correct_state_indices"] = all(
        result["windows"]["w{}_r{}".format(i, repeat)]["mdp"]["init-lambda-state"]
        == str(i) for i in range(states))
    result["complete"] = not result["missing"] and result["consistent_lambda_vector"] \
        and result["matches_config_lambda_vector"] and result["correct_state_indices"] \
        and result["system_marker_matches"] and result["consistent_mdp_physics"] \
        and result["all_state_energies_requested"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Historical results/fep/F64A/folded directory")
    parser.add_argument("--config", type=Path, required=True,
                        help="Repository config/pipeline.yaml")
    parser.add_argument("--repeat", type=int, required=True)
    args = parser.parse_args()
    if args.repeat < 0:
        parser.error("repeat must be nonnegative")
    result = inventory(args.source, args.repeat, args.config)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
