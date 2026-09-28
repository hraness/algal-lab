"""Bounded DIMACS/LRAT reader using the reviewed independent RUP checker.

The parser admits the larger cardinality-variable count for this experiment.
It neither imports the encoder nor trusts a solver's UNSAT exit code.
"""

from shared import Budget, digest, rup


def lines(path, maximum_bytes):
    if path.stat().st_size > maximum_bytes:
        raise ValueError("artifact exceeds byte limit")
    with path.open() as source:
        while True:
            line = source.readline(1_000_001)
            if not line:
                return
            if len(line) > 1_000_000:
                raise ValueError("oversized artifact line")
            yield line


def read_cnf(path, budget):
    variables, expected, clauses, pending = None, None, {}, []
    for number, line in enumerate(lines(path, 128 * 1024**2), 1):
        if number % 256 == 1:
            budget.check()
        if not line.strip() or line.startswith("c"):
            continue
        if line.startswith("p "):
            fields = line.split()
            if variables is not None or len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                raise ValueError("invalid DIMACS header")
            variables, expected = map(int, fields[2:])
            if not 1 <= variables <= 10_000 or not 1 <= expected <= 1_000_000:
                raise ValueError("DIMACS bounds")
            continue
        if variables is None:
            raise ValueError("missing DIMACS header")
        for literal in map(int, line.split()):
            if literal == 0:
                clauses[len(clauses) + 1] = tuple(dict.fromkeys(pending))
                pending.clear()
                if len(clauses) > expected:
                    raise ValueError("too many DIMACS clauses")
            elif 1 <= abs(literal) <= variables:
                pending.append(literal)
                if len(pending) > 10_000:
                    raise ValueError("oversized DIMACS clause")
            else:
                raise ValueError("DIMACS variable outside header")
    if pending or variables is None or len(clauses) != expected:
        raise ValueError("incomplete DIMACS formula")
    budget.check()
    return variables, clauses


def verify(cnf, proof, *, budget=None):
    budget = budget or Budget(300)
    variables, clauses = read_cnf(cnf, budget)
    initial_count = len(clauses)
    last_id, additions, deletions, count = initial_count, 0, 0, 0
    empty = any(not clause for clause in clauses.values())
    for line in lines(proof, 256 * 1024**2):
        count += 1
        budget.check()
        if count > 5_000_000:
            raise ValueError("LRAT line limit")
        fields = line.split()
        if not fields or fields[0] == "c":
            continue
        identifier = int(fields[0])
        if identifier < 0:
            raise ValueError("negative LRAT identifier")
        if len(fields) >= 2 and fields[1] == "d":
            ids = list(map(int, fields[2:]))
            if not ids or ids[-1] != 0 or any(value <= 0 for value in ids[:-1]):
                raise ValueError("invalid LRAT deletion")
            for removed in ids[:-1]:
                clauses.pop(removed, None)
            deletions += len(ids) - 1
            continue
        tokens = list(map(int, fields[1:]))
        if identifier <= last_id or tokens.count(0) != 2 or not tokens or tokens[-1] != 0:
            raise ValueError("invalid LRAT addition")
        separator = tokens.index(0)
        clause = tuple(dict.fromkeys(tokens[:separator]))
        hints = tokens[separator + 1:-1]
        if any(not 1 <= abs(literal) <= variables for literal in clause):
            raise ValueError("LRAT variable outside input range")
        if any(hint <= 0 for hint in hints):
            raise ValueError("RAT/negative hints are unsupported")
        rup.check_rup(clause, hints, clauses)
        clauses[identifier] = clause
        last_id = identifier
        additions += 1
        empty |= not clause
    if not empty:
        raise ValueError("proof has no verified empty clause")
    budget.check()
    return {"verified_unsatisfiable": True, "format": "text-LRAT-RUP-only",
            "initial_clauses": initial_count, "additions": additions, "deletions": deletions,
            "lines": count, "cnf_sha256": digest(cnf), "proof_sha256": digest(proof)}
