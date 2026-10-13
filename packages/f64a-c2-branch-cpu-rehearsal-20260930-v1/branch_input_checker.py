"""Read-only CPU review of a 20-state F64A C2 checkpoint branch.

Inputs are saved outputs of a separate CPU grompp/dump preparation. This
module never invokes GROMACS, Singularity, a scheduler, or mdrun.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


ARMS = ("baseline", "hrex")
STATES = 20
IMAGE_SHA256 = "0e3770f4506a2c376a3cf7a635971c0dd01161417cc3e613c8351446bb0d45ee"
SCOPE = "f64a_c2_shared_checkpoint_branch_cpu_input_review"
HEX = re.compile(r"[0-9a-f]{64}\Z")
STATE_NAMES = tuple("state{:02d}".format(i) for i in range(STATES))
REQUIRED_MDP = ("nsteps", "init-step", "tinit", "simulation-part", "dt",
                "gen-vel", "continuation", "init-lambda-state", "fep-lambdas",
                "free-energy", "calc-lambda-neighbors", "nstdhdl", "nstenergy",
                "nstxout-compressed")
TPR_INTEGER_KEYS = ("natoms", "nsteps", "init-step", "init-lambda-state",
                    "n-lambdas", "calc-lambda-neighbors")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_under(root, relative):
    path = Path(relative)
    require(not path.is_absolute() and path.parts and ".." not in path.parts,
            "invalid relative artifact path: " + str(relative))
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), "symlink artifact: " + str(relative))
    require(current.is_file(), "missing artifact: " + str(relative))
    return current


def exact_files(directory, names):
    require(directory.is_dir() and not directory.is_symlink() and
            {p.name for p in directory.iterdir()} == set(names) and
            all(p.is_file() and not p.is_symlink() for p in directory.iterdir()),
            "unexpected or missing branch input file: " + str(directory))


def mdp_values(text):
    values = {}
    for line in text.splitlines():
        body = line.split(";", 1)[0]
        if "=" not in body:
            continue
        key, value = body.split("=", 1)
        key = key.strip().lower().replace("_", "-")
        require(key and key not in values, "duplicate/empty MDP key: " + key)
        values[key] = value.strip()
    return values


def unique_field(text, key, cast):
    matches = re.findall(r"^\s*" + re.escape(key) + r"\s*=\s*([^\n]+?)\s*$",
                         text, re.M)
    require(len(matches) == 1, "missing/ambiguous field: " + key)
    try:
        return cast(matches[0].strip())
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid field: " + key) from exc


def checkpoint_metadata(text, state, plan):
    step = unique_field(text, "step", int)
    time_ps = unique_field(text, "t", float)
    part = unique_field(text, "simulation part #", int)
    fep = unique_field(text, "fep_state[0]", int)
    require(step == plan["prep_step"] and
            math.isfinite(time_ps) and
            abs(time_ps - plan["prep_time_ps"]) < 1e-5 and
            part == plan["prep_checkpoint_part"] and fep == state,
            "checkpoint step/time/part/FEP-state mismatch")
    return {"step": step, "time_ps": time_ps, "part": part, "fep_state": fep}


def parse_tpr(text, state, plan, arm):
    fields = {key: unique_field(text, key, int) for key in TPR_INTEGER_KEYS}
    dt = unique_field(text, "dt", float)
    require(math.isfinite(dt) and abs(dt - plan["dt_ps"]) < 1e-9,
            "TPR timestep mismatch")
    require(fields["natoms"] == plan["atom_count"] and
            fields["nsteps"] == plan["retained_steps"][arm] and
            fields["init-step"] == plan["prep_step"] and
            fields["init-lambda-state"] == state and
            fields["n-lambdas"] == STATES and
            fields["calc-lambda-neighbors"] == -1,
            "TPR dimension/step/lambda-state mismatch")
    require(text.count("all-lambdas:") == 1, "ambiguous TPR lambda block")
    block = text.split("all-lambdas:", 1)[1]
    vector = [float(v) for v in unique_field(block, "fep-lambdas", str).split()]
    require(len(vector) == STATES and all(
        math.isfinite(a) and abs(a - b) < 1e-6
        for a, b in zip(vector, plan["lambda_vector"])),
        "TPR lambda vector mismatch")
    return fields


def check_mdp(values, state, plan, arm):
    require(all(key in values for key in REQUIRED_MDP), "effective MDP key missing")
    require(values["gen-vel"].lower() == "no" and
            values["continuation"].lower() == "yes" and
            values["free-energy"].lower() == "yes" and
            int(values["calc-lambda-neighbors"]) == -1,
            "effective continuation/free-energy settings mismatch")
    require(int(values["nsteps"]) == plan["retained_steps"][arm] and
            int(values["init-step"]) == plan["prep_step"] and
            int(values["simulation-part"]) == plan["branch_simulation_part"] and
            int(values["init-lambda-state"]) == state,
            "effective step/part/lambda-state mismatch")
    dt, tinit = float(values["dt"]), float(values["tinit"])
    require(math.isfinite(dt) and math.isfinite(tinit) and
            abs(dt - plan["dt_ps"]) < 1e-9 and
            abs(tinit + plan["prep_step"] * dt - plan["prep_time_ps"]) < 1e-5,
            "effective starting time mismatch")
    vector = [float(v) for v in values["fep-lambdas"].split()]
    require(len(vector) == STATES and all(
        math.isfinite(a) and abs(a - b) < 1e-6
        for a, b in zip(vector, plan["lambda_vector"])),
        "effective lambda vector mismatch")
    for key, expected in plan["output_strides"].items():
        require(int(values[key]) == expected, "output stride mismatch: " + key)


def check_command(argv, state):
    require(isinstance(argv, list) and all(isinstance(x, str) for x in argv) and
            "grompp" in argv and "-t" in argv and "-f" in argv and
            "-p" in argv and "-c" in argv and "-o" in argv and
            not any(x.startswith("-maxwarn") for x in argv) and
            "mdrun" not in argv and argv.index("-t") + 1 < len(argv),
            "grompp command missing checkpoint/source or uses forbidden option")
    checkpoint_arg = argv[argv.index("-t") + 1]
    require(checkpoint_arg.endswith("/" + STATE_NAMES[state] + "/start.cpt"),
            "grompp checkpoint state path mismatch")


def validate_plan(plan):
    require(plan.get("schema_version") == 1 and plan.get("scope") == SCOPE and
            plan.get("execution_authorized") is False and
            plan.get("production_authorized") is False and
            plan.get("image_sha256") == IMAGE_SHA256,
            "wrong or executable branch review plan")
    require(plan.get("state_count") == STATES and
            type(plan.get("atom_count")) is int and plan["atom_count"] > 0 and
            type(plan.get("prep_step")) is int and plan["prep_step"] > 0 and
            type(plan.get("prep_checkpoint_part")) is int and
            plan["prep_checkpoint_part"] >= 1 and
            type(plan.get("branch_simulation_part")) is int and
            plan["branch_simulation_part"] >= plan["prep_checkpoint_part"] and
            isinstance(plan.get("prep_time_ps"), (int, float)) and
            isinstance(plan.get("dt_ps"), (int, float)) and plan["dt_ps"] > 0 and
            math.isfinite(plan["prep_time_ps"]) and
            math.isfinite(plan["dt_ps"]), "invalid common preparation metadata")
    require(plan["prep_step"] * plan["dt_ps"] <= plan["prep_time_ps"] + 1e-5,
            "invalid preparation time")
    steps = plan.get("retained_steps")
    require(isinstance(steps, dict) and set(steps) == set(ARMS) and
            all(type(v) is int and v > 0 for v in steps.values()),
            "both positive retained step targets required")
    vector = plan.get("lambda_vector")
    require(isinstance(vector, list) and len(vector) == STATES and
            all(isinstance(x, (int, float)) and math.isfinite(x) for x in vector) and
            all(a < b for a, b in zip(vector, vector[1:])),
            "invalid 20-state lambda vector")
    hashes = plan.get("checkpoint_sha256")
    require(isinstance(hashes, dict) and set(hashes) == set(STATE_NAMES) and
            all(isinstance(v, str) and HEX.fullmatch(v) for v in hashes.values()),
            "exact 20-checkpoint hash map required")
    strides = plan.get("output_strides")
    require(isinstance(strides, dict) and
            set(strides) == {"nstdhdl", "nstenergy", "nstxout-compressed"} and
            all(type(v) is int and v > 0 for v in strides.values()),
            "invalid registered output strides")
    require(isinstance(plan.get("image_path"), str) and
            Path(plan["image_path"]).is_absolute(), "absolute r6 image path required")


def review(root, plan):
    """Verify existing saved branch inputs; do not create or change files."""
    root = Path(root).resolve()
    validate_plan(plan)
    image = Path(plan["image_path"])
    require(image.is_file() and not image.is_symlink() and
            sha256(image) == IMAGE_SHA256, "r6 image identity mismatch")
    canonical = None
    rows = []
    for state, name in enumerate(STATE_NAMES):
        exact_files(root / "common" / name, ("start.cpt", "start.cpt.dump"))
        common = "common/{}/start.cpt".format(name)
        original = file_under(root, common)
        expected = plan["checkpoint_sha256"][name]
        require(sha256(original) == expected, "common checkpoint hash mismatch: " + name)
        checkpoint_metadata(file_under(root, common + ".dump").read_text(), state, plan)
        per_state = {}
        for arm in ARMS:
            prefix = "arms/{}/{}".format(arm, name)
            exact_files(root / prefix,
                        ("start.cpt", "start.cpt.dump", "grompp-result.json",
                         "grompp.log", "mdout.mdp", "topol.tpr", "topol.tpr.dump"))
            copied = file_under(root, prefix + "/start.cpt")
            require(sha256(copied) == expected,
                    "branch checkpoint differs from common: " + prefix)
            checkpoint_metadata(
                file_under(root, prefix + "/start.cpt.dump").read_text(), state, plan)
            metadata = json.loads(file_under(root, prefix + "/grompp-result.json").read_text())
            require(metadata.get("exit_status") == 0, "grompp exit mismatch: " + prefix)
            check_command(metadata.get("argv"), state)
            log = file_under(root, prefix + "/grompp.log").read_text()
            require(not re.search(r"^\s*(?:WARNING|Fatal error:)", log, re.M),
                    "grompp warning/fatal error: " + prefix)
            values = mdp_values(file_under(root, prefix + "/mdout.mdp").read_text())
            check_mdp(values, state, plan, arm)
            tpr = file_under(root, prefix + "/topol.tpr")
            fields = parse_tpr(file_under(root, prefix + "/topol.tpr.dump").read_text(),
                               state, plan, arm)
            require(fields["nsteps"] == int(values["nsteps"]) and
                    fields["init-step"] == int(values["init-step"]),
                    "TPR/effective MDP step mismatch: " + prefix)
            per_state[arm] = values
            rows.append({"state": state, "arm": arm, "checkpoint_sha256": expected,
                         "tpr_sha256": sha256(tpr),
                         "final_step": plan["prep_step"] + plan["retained_steps"][arm]})
        left = {k: v for k, v in per_state["baseline"].items() if k != "nsteps"}
        right = {k: v for k, v in per_state["hrex"].items() if k != "nsteps"}
        require(left == right, "unregistered arm MDP difference: " + name)
        across = {k: v for k, v in left.items()
                  if k not in ("init-lambda-state", "gen-seed", "ld-seed")}
        if canonical is None:
            canonical = across
        require(across == canonical, "effective MDP differs across states: " + name)
    return {"status": "cpu_branch_inputs_review_pass", "states": STATES,
            "execution_authorized": False, "production_authorized": False,
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    result = review(args.root, json.loads(args.plan.read_text()))
    print("plan_sha256={}".format(sha256(args.plan)))
    for row in result["rows"]:
        print("state={state} arm={arm} tpr_sha256={tpr_sha256} final_step={final_step}".format(
            **row))
    print("C2_BRANCH_CPU_INPUT_REVIEW_PASS states={} arms=2; no job submitted".format(
        result["states"]))


if __name__ == "__main__":
    main()
