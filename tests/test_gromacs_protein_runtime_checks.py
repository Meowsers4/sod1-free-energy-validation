import pytest

from src.analysis import gromacs_protein_runtime_checks as checks


def exchange_log(count=20, nsteps=2000, interval=100, accepted_steps=()):
    lines = []
    for step in range(interval, nsteps, interval):
        round_number = step // interval
        first = 0 if round_number % 2 else 1
        tokens = []
        for state in range(count):
            tokens.append(str(state))
            if step in accepted_steps and state in range(first, count - 1, 2):
                tokens.append("x")
        lines += [f"Replica exchange at step {step} time {step * 0.002}",
                  "Repl ex " + " ".join(tokens)]
    return "\n".join(lines) + "\n"


def test_zero_acceptance_is_valid_with_all_attempts():
    text = exchange_log()
    history, summary = checks.compare_exchange_logs([text] * 20, 20, 100, 2000)
    assert len(history) == 19
    assert summary["accepted_exchanges"] == 0
    assert summary["attempted_exchanges"] == 181
    assert len(summary["by_neighbor"]) == 19
    assert all(row["attempted"] > 0 for row in summary["by_neighbor"])
    assert history[-1]["state_to_walker"] == list(range(20))


def test_missing_round_and_inconsistent_rank_fail():
    good = exchange_log()
    bad = good.replace("Replica exchange at step 1000 time 2.0\nRepl ex " +
                       " ".join(map(str, range(20))) + "\n", "")
    with pytest.raises(ValueError, match="round"):
        checks.parse_exchange(bad, 20, 100, 2000)
    accepted = exchange_log(accepted_steps=(100,))
    with pytest.raises(ValueError, match="differ"):
        checks.compare_exchange_logs([good] * 19 + [accepted], 20, 100, 2000)


def test_acceptance_is_counted_without_becoming_a_threshold():
    history = checks.parse_exchange(exchange_log(accepted_steps=(100, 200)), 20, 100, 2000)
    summary = checks.exchange_summary(history, 20, 100, 2000)
    assert summary["accepted_exchanges"] == 19
    assert summary["by_neighbor"][0]["accepted"] == 1
    assert summary["by_neighbor"][1]["accepted"] == 1
    bad = checks.canonical_history(history)
    bad[0]["state_to_walker"] = list(range(20))
    with pytest.raises(ValueError, match="permutation"):
        checks.exchange_summary(bad, 20, 100, 2000)


def test_tpr_dump_rejects_wrong_atom_count_and_state():
    lambdas = [i / 19 for i in range(20)]
    dump = ("natoms = 40400\nnsteps = 2000\ninit-step = 0\n"
            "init-lambda-state = 7\nn-lambdas = 20\n"
            "calc-lambda-neighbors = -1\ndt = 0.002\nall-lambdas:\n"
            "fep-lambdas = " + " ".join(map(str, lambdas)) + "\n")
    checks.validate_tpr_dump(dump, 7, 40400, lambdas)
    with pytest.raises(ValueError, match="natoms"):
        checks.validate_tpr_dump(dump, 7, 40401, lambdas)
    with pytest.raises(ValueError, match="init-lambda-state"):
        checks.validate_tpr_dump(dump, 8, 40400, lambdas)
