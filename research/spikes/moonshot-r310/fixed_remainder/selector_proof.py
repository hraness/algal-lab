"""Explicit selector-profile DIMACS reader and independent textual RUP replay.

The original fixed-attachment proof reader is unchanged. This reader has
separate, fixed caps; it reuses the original bounded CNF line input and the
independent degree-four RUP checker, never the selector encoder or solver
result. Only selector LRAT deletion records have a larger line allowance.
"""

from proof import lines
from shared import Budget, digest, rup

PROFILE = "fixed-h-column-selector-v1"
MAX_VARIABLES = 60_000
MAX_CLAUSES = 1_500_000
MAX_CNF_BYTES = 32 * 1024**2
MAX_PROOF_BYTES = 256 * 1024**2
MAX_ORDINARY_PROOF_LINE_BYTES = 1_000_000
MAX_DELETION_LINE_BYTES = 2 * 1024**2


def proof_lines(path, *, profile):
    if profile != PROFILE:
        raise ValueError("unknown selector proof profile")
    if path.stat().st_size > MAX_PROOF_BYTES:
        raise ValueError("selector proof exceeds byte limit")
    total_bytes = 0
    with path.open("rb") as source:
        while True:
            raw = source.readline(MAX_DELETION_LINE_BYTES + 1)
            if not raw:
                return
            total_bytes += len(raw)
            if total_bytes > MAX_PROOF_BYTES:
                raise ValueError("selector proof exceeds byte limit")
            if len(raw) > MAX_DELETION_LINE_BYTES:
                raise ValueError("selector LRAT deletion record exceeds line limit")
            if len(raw) > MAX_ORDINARY_PROOF_LINE_BYTES:
                prefix = raw.split(None, 2)
                if len(prefix) < 2 or not prefix[0].isdigit() or prefix[1] != b"d":
                    raise ValueError("oversized selector LRAT non-deletion record")
            yield raw.decode("ascii")


def read_cnf(path, budget, *, profile):
    if profile != PROFILE:
        raise ValueError("unknown selector proof profile")
    variables, expected, clauses, pending = None, None, {}, []
    for number, line in enumerate(lines(path, MAX_CNF_BYTES), 1):
        if number % 256 == 1:
            budget.check()
        if not line.strip() or line.startswith("c"):
            continue
        if line.startswith("p "):
            fields = line.split()
            if variables is not None or len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                raise ValueError("invalid selector DIMACS header")
            variables, expected = map(int, fields[2:])
            if not 1 <= variables <= MAX_VARIABLES or not 1 <= expected <= MAX_CLAUSES:
                raise ValueError("selector DIMACS bounds")
            continue
        if variables is None:
            raise ValueError("missing selector DIMACS header")
        for literal in map(int, line.split()):
            if literal == 0:
                clauses[len(clauses) + 1] = tuple(dict.fromkeys(pending))
                pending.clear()
                if len(clauses) > expected:
                    raise ValueError("too many selector DIMACS clauses")
            elif 1 <= abs(literal) <= variables:
                pending.append(literal)
                if len(pending) > 10_000:
                    raise ValueError("oversized selector DIMACS clause")
            else:
                raise ValueError("selector DIMACS variable outside header")
    if pending or variables is None or len(clauses) != expected:
        raise ValueError("incomplete selector DIMACS formula")
    budget.check()
    return variables, clauses


def verify(cnf, proof, *, profile, budget=None):
    budget = budget or Budget(90)
    variables, clauses = read_cnf(cnf, budget, profile=profile)
    initial_count = len(clauses)
    last_id, additions, deletions, count, maximum_line = initial_count, 0, 0, 0, 0
    empty = any(not clause for clause in clauses.values())
    for line in proof_lines(proof, profile=profile):
        count += 1
        maximum_line = max(maximum_line, len(line))
        budget.check()
        if count > 5_000_000:
            raise ValueError("selector LRAT line limit")
        fields = line.split()
        if not fields or fields[0] == "c":
            continue
        identifier = int(fields[0])
        if identifier < 0:
            raise ValueError("negative selector LRAT identifier")
        if len(fields) >= 2 and fields[1] == "d":
            ids = list(map(int, fields[2:]))
            if not ids or ids[-1] != 0 or any(value <= 0 for value in ids[:-1]):
                raise ValueError("invalid selector LRAT deletion")
            for removed in ids[:-1]:
                clauses.pop(removed, None)
            deletions += len(ids) - 1
            continue
        tokens = list(map(int, fields[1:]))
        if identifier <= last_id or tokens.count(0) != 2 or not tokens or tokens[-1] != 0:
            raise ValueError("invalid selector LRAT addition")
        separator = tokens.index(0)
        clause, hints = tuple(dict.fromkeys(tokens[:separator])), tokens[separator + 1:-1]
        if any(not 1 <= abs(literal) <= variables for literal in clause):
            raise ValueError("selector LRAT variable outside input range")
        if any(hint <= 0 for hint in hints):
            raise ValueError("selector RAT/negative hints are unsupported")
        rup.check_rup(clause, hints, clauses)
        clauses[identifier] = clause
        last_id = identifier
        additions += 1
        empty |= not clause
    if not empty:
        raise ValueError("selector proof has no verified empty clause")
    budget.check()
    return {"profile": PROFILE, "verified_unsatisfiable": True, "format": "text-LRAT-RUP-only",
            "initial_clauses": initial_count, "additions": additions, "deletions": deletions,
            "lines": count, "maximum_line_bytes": maximum_line,
            "ordinary_line_byte_limit": MAX_ORDINARY_PROOF_LINE_BYTES,
            "deletion_line_byte_limit": MAX_DELETION_LINE_BYTES,
            "cnf_sha256": digest(cnf), "proof_sha256": digest(proof)}
