"""Independently audit the degree-four CNF, receipt, and textual RUP proof.

Usage: python3 independent_audit.py PATH_TO_RUN_DIRECTORY

This implementation imports neither the encoder nor its checker. It derives
the base graph from the distances in Goedgebeur--Radziszowski, Theorem 3,
independently enumerates its relevant independent sets, checks every actual
CNF clause, and replays the proof using sets of true and false literals.
The sibling encode.py, lrat.py, and solve.py are read only for receipt hashes.
The recorded solver executable is not needed or opened. Successful output is
a JSON receipt on stdout; any failed condition raises an exception.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time


def require(condition, message):
    # Explicit exceptions retain all verification under python -O.
    if not condition:
        raise ValueError(message)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(262144), b""):
            result.update(block)
    return result.hexdigest()


def audit(run):
    started = time.monotonic()
    source_directory = Path(__file__).resolve().parent
    receipt = json.loads((run / "result.json").read_text())
    metadata = json.loads((run / "instance.json").read_text())
    source_names = {"encode.py", "lrat.py", "solve.py"}
    require(set(receipt["source_sha256"]) == source_names, "unexpected source inventory")
    for name in sorted(source_names):
        require(digest(source_directory / name) == receipt["source_sha256"][name],
                f"source hash mismatch: {name}")
    cnf_hash, proof_hash = digest(run / "instance.cnf"), digest(run / "proof.lrat")
    require(cnf_hash == receipt["cnf_sha256"] == metadata["cnf_sha256"],
            "CNF hash mismatch")
    require(proof_hash == receipt["proof_sha256"], "proof hash mismatch")
    require(digest(run / "solver.log") == receipt["solver_log_sha256"],
            "solver-log hash mismatch")
    require(metadata["encoder_sha256"] == receipt["source_sha256"]["encode.py"],
            "encoder provenance mismatch")

    # Multiplication by 22 maps the encoder's labels to the published graph.
    published = {distance % 35 for distance in (1, -1, 7, -7, 11, -11, 16, -16)}
    adjacency = [sum(1 << v for v in range(35) if 22 * (u - v) % 35 in published)
                 for u in range(35)]
    require(adjacency == metadata["base_adjacency"], "published base graph mismatch")
    for key, expected in (("base_order", 35), ("extension_order", 40),
                          ("independent_set_target", 10), ("neighbour_count", 4),
                          ("variables", 140), ("clauses", 98965),
                          ("symmetry_breaking", False)):
        require(metadata[key] == expected, f"unexpected metadata: {key}")

    families = {6: set(), 7: set(), 8: set(), 9: set()}

    def enumerate_sets(chosen, candidates):
        size = chosen.bit_count()
        if size >= 6:
            families[size].add(chosen)
        if size == 9:
            return
        while candidates:
            bit = candidates & -candidates
            candidates -= bit
            enumerate_sets(chosen | bit,
                           candidates & ~adjacency[bit.bit_length() - 1])

    enumerate_sets(0, (1 << 35) - 1)
    inventory = {size: len(family) for size, family in families.items()}
    require(inventory == {6: 22995, 7: 13760, 8: 3360, 9: 0},
            "independent-set inventory mismatch")
    require(metadata["independent_set_counts"] ==
            {str(size): inventory[size] for size in (6, 7, 8)},
            "independent-set metadata mismatch")

    clauses, negative, positive = {}, set(), set()
    with (run / "instance.cnf").open() as source:
        require(source.readline().split() == ["p", "cnf", "140", "98965"],
                "unexpected DIMACS header")
        for number, line in enumerate(source, 1):
            tokens = list(map(int, line.split()))
            require(bool(tokens) and tokens[-1] == 0 and 0 not in tokens[:-1],
                    f"invalid CNF line: {number}")
            clause = frozenset(tokens[:-1])
            require(len(clause) == len(tokens) - 1, "repeated CNF literal")
            require(all(1 <= abs(lit) <= 140 for lit in clause), "invalid CNF variable")
            clauses[number] = clause
            if all(lit < 0 for lit in clause):
                require(len(clause) == 2, "invalid negative constraint")
                (v1, c1), (v2, c2) = [divmod(-lit - 1, 4) for lit in clause]
                require((v1 == v2 and c1 != c2) or
                        (c1 == c2 and (adjacency[v1] >> v2 & 1)),
                        "negative constraint excludes an allowed assignment")
                require(clause not in negative, "duplicate negative constraint")
                negative.add(clause)
            else:
                require(all(lit > 0 for lit in clause), "mixed-sign constraint")
                vertices = {divmod(lit - 1, 4)[0] for lit in clause}
                colours = {divmod(lit - 1, 4)[1] for lit in clause}
                size = len(vertices)
                require(size in (6, 7, 8) and len(colours) == 10 - size,
                        "invalid covering constraint dimensions")
                require(len(clause) == len(vertices) * len(colours),
                        "covering constraint is not the full Cartesian product")
                vertex_mask = sum(1 << v for v in vertices)
                colour_mask = sum(1 << colour for colour in colours)
                require(vertex_mask in families[size], "covering set is not independent")
                key = (vertex_mask, colour_mask)
                require(key not in positive, "duplicate covering constraint")
                positive.add(key)

    # Every clause is valid and distinct, and the inventory attains the number
    # of all required clauses. Together these establish equality, not inclusion.
    require(len(clauses) == 98965 and len(negative) == 770 and len(positive) == 98195,
            "CNF clause inventory mismatch")
    require(len(negative) == 35 * 6 + sum(row.bit_count() for row in adjacency) // 2 * 4,
            "incomplete negative constraints")
    require(len(positive) == inventory[8] * 6 + inventory[7] * 4 + inventory[6],
            "incomplete covering constraints")

    last_id = len(clauses)
    additions = deletions = lines = 0
    empty = False
    with (run / "proof.lrat").open() as proof:
        for line in proof:
            lines += 1
            words = line.split()
            if not words or words[0] == "c":
                continue
            require(len(words) >= 2, "incomplete LRAT line")
            identifier = int(words[0])
            require(identifier >= 0, "negative LRAT identifier")
            if words[1] == "d":
                removed = list(map(int, words[2:]))
                require(bool(removed) and removed[-1] == 0 and
                        all(value > 0 for value in removed[:-1]), "invalid deletion")
                for value in removed[:-1]:
                    clauses.pop(value, None)
                deletions += len(removed) - 1
                continue
            require(identifier > last_id, "non-increasing LRAT addition identifier")
            numbers = list(map(int, words[1:]))
            require(bool(numbers) and numbers[-1] == 0 and numbers.count(0) == 2,
                    "invalid LRAT addition delimiters")
            separator = numbers.index(0)
            conclusion = frozenset(numbers[:separator])
            hints = numbers[separator + 1:-1]
            require(all(1 <= abs(lit) <= 140 for lit in conclusion),
                    "LRAT variable outside the input range")
            require(all(hint > 0 for hint in hints), "RAT/negative hints unsupported")
            truth = {-lit for lit in conclusion}
            falsehood = {-lit for lit in truth}
            conflict = bool(truth & falsehood)  # A tautology needs no propagation.
            if not conflict:
                for hint in hints:
                    require(hint in clauses, "LRAT hint names an absent clause")
                    old = clauses[hint]
                    require(not old & truth, "hinted clause is already satisfied")
                    remainder = old - falsehood
                    if not remainder:
                        conflict = True
                        break
                    require(len(remainder) == 1, "hinted clause is not unit")
                    forced = next(iter(remainder))
                    truth.add(forced)
                    falsehood.add(-forced)
            require(conflict, "RUP hints did not derive a contradiction")
            clauses[identifier] = conclusion
            last_id = identifier
            additions += 1
            if not conclusion:
                empty = True
    require(empty, "proof contains no verified empty clause")
    earlier = receipt["proof_verification"]
    require(additions == earlier["additions"] and deletions == earlier["deletions"]
            and lines == earlier["lines"], "proof replay disagrees with recorded inventory")
    require(cnf_hash == earlier["cnf_sha256"] and proof_hash == earlier["proof_sha256"],
            "recorded proof verification refers to different bytes")
    return {"status": "independently_verified", "exact_cnf_equivalence": True,
            "published_base_graph_match": True, "independent_set_counts": inventory,
            "clauses": 98965, "rup_additions": additions, "deletions": deletions,
            "proof_lines": lines, "verified_empty_clause": True,
            "receipt_file_hashes_match": True, "cnf_sha256": cnf_hash,
            "proof_sha256": proof_hash, "reviewer_script_sha256": digest(Path(__file__)),
            "seconds": round(time.monotonic() - started, 6)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run_dir), indent=2))
