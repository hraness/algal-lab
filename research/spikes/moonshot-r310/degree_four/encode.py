"""Exact attachment encoding around an extremal, regular Ramsey graph."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vertex_transitive"))
from checker import SearchLimit, independent_set, triangle, validate_adjacency


def base_graph():
    """A directly verified representative of the unique (3,9,35)-graph."""
    return [sum(1 << ((v + d) % 35) for d in (8, 12, 14, 17, 18, 21, 23, 27))
            for v in range(35)]


def independent_sets(adj, size, *, deadline=None, node_limit=1_000_000):
    """Enumerate every fixed-size independent set once, in vertex order."""
    validate_adjacency(adj)
    if not 0 <= size <= len(adj) or not 1 <= node_limit <= 10_000_000:
        raise ValueError("independent-set enumeration bound")
    nodes = 0

    def visit(available, chosen, left):
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise SearchLimit("independent-set enumeration node limit")
        if deadline is not None and (nodes == 1 or nodes % 256 == 0) and time.monotonic() >= deadline:
            raise SearchLimit("independent-set enumeration deadline")
        if left == 0:
            yield chosen
            return
        while available.bit_count() >= left:
            bit = available & -available
            available ^= bit
            v = bit.bit_length() - 1
            yield from visit(available & ~adj[v], chosen | bit, left - 1)

    yield from visit((1 << len(adj)) - 1, 0, size)


def encode(adj, target=10, neighbours=4, *, seconds=10):
    """Return a CNF and its inventory; no symmetry breaking is imposed.

    H is required to be (target-2)-regular, triangle-free, and free of
    independent (target-1)-sets. A qualifying extension has maximum degree
    target-1, so each H vertex can attach to at most one new neighbour.
    """
    validate_adjacency(adj)
    n = len(adj)
    if (not 3 <= target <= 10 or not 1 <= neighbours < target
            or n + neighbours + 1 > 63 or not 0 < seconds <= 60):
        raise ValueError("unsupported encoding parameters")
    deadline = time.monotonic() + seconds
    if any(row.bit_count() != target - 2 for row in adj):
        raise ValueError("base graph must be (target-2)-regular")
    if triangle(adj) is not None or independent_set(adj, target - 1,
            node_limit=1_000_000, deadline=deadline) is not None:
        raise ValueError("base graph is not a (3,target-1)-graph")
    clauses, counts, set_counts = [], {}, {}

    def variable(v, colour):
        return neighbours * v + colour + 1

    def append(clause):
        if len(clauses) >= 1_000_000:
            raise SearchLimit("encoding clause limit")
        clauses.append(tuple(clause))

    for v in range(n):
        for a, b in itertools.combinations(range(neighbours), 2):
            append([-variable(v, a), -variable(v, b)])
    counts["disjoint_attachments"] = len(clauses)

    before = len(clauses)
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u] >> v & 1:
                for colour in range(neighbours):
                    append([-variable(u, colour), -variable(v, colour)])
    counts["independent_attachments"] = len(clauses) - before

    # Cases containing v have size <= 1 + alpha(H) <= target-1.
    # Without v, zero or one new neighbour cannot reach target either.
    for k in range(2, neighbours + 1):
        size = target - k
        before, total = len(clauses), 0
        for selected in independent_sets(adj, size, deadline=deadline):
            total += 1
            vertices = [v for v in range(n) if selected >> v & 1]
            for colours in itertools.combinations(range(neighbours), k):
                append([variable(v, colour) for v in vertices for colour in colours])
        set_counts[str(size)] = total
        counts[f"cover_independent_{size}_sets"] = len(clauses) - before
    if time.monotonic() >= deadline:
        raise SearchLimit("encoding deadline")
    return clauses, {
        "schema_version": 1, "base_order": n, "extension_order": n + neighbours + 1,
        "independent_set_target": target, "neighbour_count": neighbours,
        "variables": n * neighbours, "clauses": len(clauses), "clause_counts": counts,
        "independent_set_counts": set_counts, "symmetry_breaking": False,
        "base_adjacency": adj,
        "base_adjacency_sha256": hashlib.sha256(json.dumps(adj, separators=(",", ":")).encode()).hexdigest(),
    }


def extension(adj, neighbours, positive_variables):
    n = len(adj)
    valid = set(range(1, n * neighbours + 1))
    if any(type(v) is not int for v in positive_variables) or not set(positive_variables) <= valid:
        raise ValueError("invalid attachment variable")
    result = list(adj) + [0] * (neighbours + 1)
    centre = n + neighbours
    for colour in range(neighbours):
        result[n + colour] |= 1 << centre
        result[centre] |= 1 << (n + colour)
    for variable in positive_variables:
        v, colour = divmod(variable - 1, neighbours)
        result[v] |= 1 << (n + colour)
        result[n + colour] |= 1 << v
    return result


def write_instance(output, *, adj=None, target=10, neighbours=4):
    clauses, metadata = encode(base_graph() if adj is None else adj, target, neighbours)
    output.mkdir(parents=True, exist_ok=False)
    dimacs = f"p cnf {metadata['variables']} {len(clauses)}\n" + "".join(
        " ".join(map(str, clause)) + " 0\n" for clause in clauses)
    raw = dimacs.encode("ascii")
    (output / "instance.cnf").write_bytes(raw)
    metadata["cnf_sha256"] = hashlib.sha256(raw).hexdigest()
    metadata["cnf_bytes"] = len(raw)
    metadata["encoder_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / "instance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new directory under ignored runs/")
    args = parser.parse_args()
    print(json.dumps(write_instance(args.output), indent=2))
