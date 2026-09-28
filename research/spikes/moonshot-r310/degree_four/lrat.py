"""Small independent checker for the RUP-only subset of textual LRAT.

Unsupported negative/RAT hints are rejected, never accepted as proof. This
module imports neither the encoder nor the SAT solver. The accepted final
empty clause must follow from the DIMACS formula by checked unit propagation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time


def read_cnf(path):
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("CNF exceeds 64 MiB")
    clauses, variables, expected = {}, None, None
    pending = []
    with path.open() as source:
        for line in source:
            if len(line) > 1_000_000:
                raise ValueError("oversized CNF line")
            if not line.strip() or line.startswith("c"):
                continue
            if line.startswith("p "):
                fields = line.split()
                if variables is not None or len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                    raise ValueError("invalid DIMACS header")
                variables, expected = map(int, fields[2:])
                if not 1 <= variables <= 1000 or not 1 <= expected <= 1_000_000:
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
                elif abs(literal) <= variables:
                    pending.append(literal)
                else:
                    raise ValueError("DIMACS variable outside header")
    if pending or variables is None or len(clauses) != expected:
        raise ValueError("incomplete DIMACS formula")
    return variables, clauses


def check_rup(clause, hints, clauses):
    values = {}
    for literal in clause:
        variable, value = abs(literal), -1 if literal > 0 else 1
        if variable in values and values[variable] != value:
            return  # A tautology is always implied.
        values[variable] = value
    for hint in hints:
        if hint <= 0:
            raise ValueError("RAT/negative hints are unsupported")
        if hint not in clauses:
            raise ValueError("hint refers to an absent clause")
        unit = None
        for literal in clauses[hint]:
            value = values.get(abs(literal))
            if value == (1 if literal > 0 else -1):
                raise ValueError("hinted clause is already satisfied")
            if value is None:
                if unit is not None:
                    raise ValueError("hinted clause is not unit")
                unit = literal
        if unit is None:
            return  # Conflict under the negation of the proposed clause.
        values[abs(unit)] = 1 if unit > 0 else -1
    raise ValueError("hints did not derive a conflict")


def verify(cnf_path, proof_path, *, seconds=60, max_lines=2_000_000):
    if not 0 < seconds <= 300 or not 1 <= max_lines <= 5_000_000:
        raise ValueError("invalid checker limits")
    if proof_path.stat().st_size > 256 * 1024 * 1024:
        raise ValueError("proof exceeds 256 MiB")
    started = time.monotonic()
    deadline = started + seconds
    variables, clauses = read_cnf(cnf_path)
    initial_count = len(clauses)
    last_id, additions, deletions, lines = initial_count, 0, 0, 0
    empty = any(not clause for clause in clauses.values())
    with proof_path.open() as source:
        for line in source:
            lines += 1
            if lines > max_lines or time.monotonic() >= deadline:
                raise ValueError("LRAT verification limit")
            if len(line) > 1_000_000:
                raise ValueError("oversized LRAT line")
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
            if identifier <= last_id or tokens.count(0) != 2 or tokens[-1] != 0:
                raise ValueError("invalid LRAT addition")
            separator = tokens.index(0)
            clause = tuple(dict.fromkeys(tokens[:separator]))
            hints = tokens[separator + 1:-1]
            if any(not 1 <= abs(literal) <= variables for literal in clause):
                raise ValueError("LRAT variable outside input range")
            if any(hint <= 0 for hint in hints):
                raise ValueError("RAT/negative hints are unsupported")
            check_rup(clause, hints, clauses)
            clauses[identifier] = clause
            last_id = identifier
            additions += 1
            empty |= not clause
    if not empty:
        raise ValueError("proof has no verified empty clause")
    return {"verified_unsatisfiable": True, "format": "text-LRAT-RUP-only",
            "initial_clauses": initial_count, "additions": additions, "deletions": deletions,
            "lines": lines, "seconds": round(time.monotonic() - started, 6),
            "cnf_sha256": hashlib.sha256(cnf_path.read_bytes()).hexdigest(),
            "proof_sha256": hashlib.sha256(proof_path.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cnf", type=Path)
    parser.add_argument("proof", type=Path)
    parser.add_argument("--seconds", type=float, default=60)
    args = parser.parse_args()
    print(json.dumps(verify(args.cnf, args.proof, seconds=args.seconds), indent=2))
