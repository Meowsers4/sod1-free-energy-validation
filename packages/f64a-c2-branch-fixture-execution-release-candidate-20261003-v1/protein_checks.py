"""Protein-specific checks for the bounded F64A exchange/restart qualification.

Unlike the synthetic ladder, protein exchange acceptance is not a pass threshold.
The complete attempt schedule and walker permutation remain mandatory.
"""

import json
import math
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_exchange(text, count, interval, nsteps):
    """Parse every expected alternating-neighbor exchange round, including rejects."""
    require(count > 1 and interval > 0 and nsteps > interval, "invalid exchange dimensions")
    headers = list(re.finditer(r"^Replica exchange at step (\d+) time [^\n]+$", text, re.M))
    steps = [int(match.group(1)) for match in headers]
    require(steps == list(range(interval, nsteps, interval)),
            "missing, repeated or out-of-order exchange round")
    walkers = list(range(count))
    history = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        section = text[header.end():end]
        lines = re.findall(r"^Repl\s+ex\s+(.+)$", section, re.M)
        require(len(lines) == 1, "missing or duplicate exchange outcome")
        tokens = lines[0].split()
        require([int(token) for token in tokens if token.isdigit()] == list(range(count)),
                "invalid state order in exchange outcome")
        require(all(token.isdigit() or token == "x" for token in tokens),
                "invalid exchange outcome token")
        first = 0 if (steps[index] // interval) % 2 else 1
        attempted = [[left, left + 1] for left in range(first, count - 1, 2)]
        allowed = {tuple(pair) for pair in attempted}
        accepted = []
        for position, token in enumerate(tokens):
            if token != "x":
                continue
            require(0 < position < len(tokens) - 1 and
                    tokens[position - 1].isdigit() and tokens[position + 1].isdigit(),
                    "invalid accepted-swap marker")
            pair = (int(tokens[position - 1]), int(tokens[position + 1]))
            require(pair in allowed, "swap was not an attempted neighbor pair")
            accepted.append(list(pair))
        require(len({value for pair in accepted for value in pair}) == 2 * len(accepted),
                "overlapping accepted swaps")
        for left, right in accepted:
            walkers[left], walkers[right] = walkers[right], walkers[left]
        history.append({"step": steps[index], "attempted_pairs": attempted,
                        "accepted_pairs": accepted, "state_to_walker": walkers[:]})
    return history


def exchange_summary(history, count, interval, nsteps):
    """Report per-link attempts and accepts; require complete scheduled coverage."""
    require([row["step"] for row in history] == list(range(interval, nsteps, interval)),
            "exchange history has wrong round schedule")
    attempts = {(left, left + 1): 0 for left in range(count - 1)}
    accepts = dict.fromkeys(attempts, 0)
    prior = list(range(count))
    for row in history:
        tried = [tuple(pair) for pair in row["attempted_pairs"]]
        taken = [tuple(pair) for pair in row["accepted_pairs"]]
        require(len(set(tried)) == len(tried) and all(pair in attempts for pair in tried),
                "invalid attempted exchange pairs")
        require(len(set(taken)) == len(taken) and set(taken).issubset(tried),
                "accepted pair was not attempted")
        require(sorted(row["state_to_walker"]) == list(range(count)),
                "exchange result is not a walker permutation")
        for pair in tried:
            attempts[pair] += 1
        for pair in taken:
            accepts[pair] += 1
            prior[pair[0]], prior[pair[1]] = prior[pair[1]], prior[pair[0]]
        require(row["state_to_walker"] == prior, "walker permutation disagrees with swaps")
    require(all(attempts.values()), "some protein neighbors had no exchange attempt")
    return {"states": count, "rounds": len(history),
            "attempted_exchanges": sum(attempts.values()),
            "accepted_exchanges": sum(accepts.values()),
            "by_neighbor": [{"pair": list(pair), "attempted": attempts[pair],
                             "accepted": accepts[pair]} for pair in sorted(attempts)],
            "all_neighbor_links_attempted": True,
            "acceptance_is_not_a_pass_threshold": True}


def validate_tpr_dump(text, state_index, atom_count, lambdas, nsteps=2000, dt_ps=0.002):
    """Check protein TPR identity after CPU-only exact-SIF dump."""
    require(atom_count > 0 and len(lambdas) == 20, "invalid protein reference dimensions")
    fields = {"natoms": atom_count, "nsteps": nsteps, "init-step": 0,
              "init-lambda-state": state_index, "n-lambdas": len(lambdas),
              "calc-lambda-neighbors": -1}
    for key, expected in fields.items():
        matches = re.findall(r"^\s*" + re.escape(key) + r"\s*=\s*(-?\d+)\s*$", text, re.M)
        require(len(matches) == 1 and int(matches[0]) == expected,
                "protein TPR mismatch: " + key)
    dt = re.findall(r"^\s*dt\s*=\s*([^\s]+)\s*$", text, re.M)
    require(len(dt) == 1 and math.isfinite(float(dt[0])) and
            abs(float(dt[0]) - dt_ps) < 1e-9, "protein TPR timestep mismatch")
    require(text.count("all-lambdas:") == 1, "ambiguous TPR lambda block")
    block = text.split("all-lambdas:", 1)[1]
    vector = re.findall(r"^\s*fep-lambdas\s*=\s*([^\n]+)", block, re.M)
    require(len(vector) == 1, "missing TPR FEP lambda vector")
    actual = [float(value) for value in vector[0].split()]
    require(len(actual) == len(lambdas) and
            all(math.isfinite(a) and abs(a - b) < 1e-6 for a, b in zip(actual, lambdas)),
            "protein TPR lambda vector mismatch")


def compare_exchange_logs(texts, count, interval, nsteps):
    """Require identical histories from every rank, then summarize the ladder."""
    require(len(texts) == count, "missing protein rank log")
    histories = [parse_exchange(text, count, interval, nsteps) for text in texts]
    reference = histories[0]
    require(all(history == reference for history in histories[1:]),
            "protein exchange histories differ across ranks")
    return reference, exchange_summary(reference, count, interval, nsteps)


def canonical_history(history):
    """Copy a history through JSON for stable archive comparisons."""
    return json.loads(json.dumps(history, sort_keys=True))
