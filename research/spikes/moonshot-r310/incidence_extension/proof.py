"""RUP-only text-LRAT replay, copied from the frozen column checker.

Only the dependency import changes; this profile supplies its stricter CNF caps.
"""

from pathlib import Path

from support import (MAX_CLAUSES, MAX_CNF_BYTES, MAX_PROOF_BYTES, MAX_VARIABLES,
                        PROFILE, digest, rup)


def lines(path, maximum_bytes, maximum_line=1_000_000):
    if Path(path).stat().st_size > maximum_bytes:
        raise ValueError("artifact byte limit")
    consumed = 0
    with Path(path).open("rb") as source:
        while True:
            line = source.readline(maximum_line + 1)
            if not line:
                return
            if len(line) > maximum_line:
                raise ValueError("artifact line limit")
            consumed += len(line)
            if consumed > maximum_bytes:
                raise ValueError("artifact grew past byte limit")
            yield line.decode("ascii")


def read_cnf(path, budget):
    variables, expected, clauses = None, None, {}
    for line in lines(path, MAX_CNF_BYTES, 100_000):
        if variables is None:
            fields = line.split()
            if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                raise ValueError("invalid DIMACS header")
            variables, expected = map(int, fields[2:])
            if not 1 <= variables <= MAX_VARIABLES or not 1 <= expected <= MAX_CLAUSES:
                raise ValueError("DIMACS bounds")
            continue
        tokens = list(map(int, line.split()))
        if (not tokens or tokens[-1] != 0 or 0 in tokens[:-1] or len(tokens) > 3001
                or any(not 1 <= abs(lit) <= variables for lit in tokens[:-1])):
            raise ValueError("invalid DIMACS clause")
        clauses[len(clauses) + 1] = tuple(dict.fromkeys(tokens[:-1]))
        if len(clauses) > expected:
            raise ValueError("excess DIMACS clauses")
        if len(clauses) % 256 == 1:
            budget.check()
    if variables is None or len(clauses) != expected:
        raise ValueError("incomplete DIMACS formula")
    return variables, clauses


def verify(cnf, proof, budget):
    variables, clauses = read_cnf(cnf, budget)
    last, additions, deletions, count = len(clauses), 0, 0, 0
    initial, empty = last, any(not clause for clause in clauses.values())
    for line in lines(proof, MAX_PROOF_BYTES, 2 * 1024**2):
        count += 1
        budget.check()
        if count > 2_000_000:
            raise ValueError("proof line-count bound")
        fields = line.split()
        if not fields or fields[0] == "c":
            continue
        identifier = int(fields[0])
        if identifier < 0:
            raise ValueError("negative LRAT identifier")
        if len(fields) >= 2 and fields[1] == "d":
            ids = list(map(int, fields[2:]))
            if not ids or ids[-1] != 0 or any(i <= 0 for i in ids[:-1]):
                raise ValueError("invalid LRAT deletion")
            for i in ids[:-1]:
                clauses.pop(i, None)
            deletions += len(ids) - 1
            continue
        if len(line) > 1_000_000:
            raise ValueError("oversized non-deletion LRAT line")
        tokens = list(map(int, fields[1:]))
        if identifier <= last or tokens.count(0) != 2 or tokens[-1] != 0:
            raise ValueError("invalid LRAT addition")
        middle = tokens.index(0)
        clause, hints = tuple(dict.fromkeys(tokens[:middle])), tokens[middle + 1:-1]
        if (any(not 1 <= abs(lit) <= variables for lit in clause)
                or any(hint <= 0 for hint in hints)):
            raise ValueError("unsupported LRAT variable or RAT hint")
        rup.check_rup(clause, hints, clauses)
        clauses[identifier] = clause
        last, additions, empty = identifier, additions + 1, empty or not clause
    if not empty:
        raise ValueError("proof has no verified empty clause")
    budget.check()
    return {"profile": PROFILE, "python_rup_verified": True, "initial_clauses": initial,
            "additions": additions, "deletions": deletions, "lines": count,
            "cnf_sha256": digest(cnf), "proof_sha256": digest(proof)}


def model(path, variables):
    values = {}
    for line in lines(path, 8 * 1024**2):
        if line.startswith("v "):
            for lit in map(int, line[2:].split()):
                if lit == 0:
                    continue
                if not 1 <= abs(lit) <= variables:
                    raise ValueError("model variable outside formula")
                if abs(lit) in values and values[abs(lit)] != (lit > 0):
                    raise ValueError("contradictory model")
                values[abs(lit)] = lit > 0
    if len(values) != variables:
        raise ValueError("incomplete model")
    return values


def check_model(cnf, output, budget):
    variables, clauses = read_cnf(cnf, budget)
    values = model(output, variables)
    for i, clause in clauses.items():
        if not any(values[abs(lit)] == (lit > 0) for lit in clause):
            raise ValueError("model violates archived CNF")
        if i % 256 == 1:
            budget.check()
    return values
