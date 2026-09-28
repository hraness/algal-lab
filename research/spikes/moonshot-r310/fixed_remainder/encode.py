"""Exact fixed-remainder extension CNF, with full independent-set coverage."""

import itertools
import json
from pathlib import Path

from shared import Budget, Formula, SearchLimit, cardinality, checker, digest, graph_digest

MAX_CLAUSES = 1_000_000
MAX_CNF_BYTES = 128 * 1024**2


def independent_sets(adj, size, *, budget=None, node_limit=1_000_000):
    """Every fixed-size independent set once, ordered by its smallest vertex."""
    checker.validate_adjacency(adj)
    if type(size) is not int or not 0 <= size <= 63 or not 1 <= node_limit <= 1_000_000:
        raise ValueError("invalid independent-set enumeration bounds")
    budget = budget or Budget()
    nodes = 0

    def visit(available, chosen, left):
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise SearchLimit("independent-set enumeration node limit")
        if nodes == 1 or nodes % 256 == 0:
            budget.check()
        if left == 0:
            yield chosen
            return
        while available.bit_count() >= left:
            bit = available & -available
            available ^= bit
            vertex = bit.bit_length() - 1
            yield from visit(available & ~adj[vertex], chosen | bit, left - 1)

    yield from visit((1 << len(adj)) - 1, 0, size)


def validate_parameters(adj, target, neighbours, minimum, coverage, budget):
    checker.validate_adjacency(adj)
    n = len(adj)
    if (not all(type(x) is int for x in (target, neighbours, minimum))
            or not 3 <= target <= 10 or not 1 <= neighbours < target
            or not 0 <= minimum <= neighbours or type(coverage) is not bool
            or not 1 <= n <= 35 or not target <= n + neighbours + 1 <= 40):
        raise ValueError("unsupported fixed-remainder parameters")
    if checker.triangle(adj) is not None:
        raise ValueError("base graph contains a triangle")
    if target - 1 <= n and checker.independent_set(
            adj, target - 1, node_limit=1_000_000,
            deadline=budget.wall_start + budget.seconds) is not None:
        raise ValueError("base graph has an independent (target-1)-set")
    budget.check()


def encode(adj, emit, *, target=10, neighbours=6, minimum=6, coverage=True, budget=None):
    """Emit all clauses; only cardinality auxiliaries are retained in memory.

    Variables 1..n*neighbours encode H--A edges. No H-label or A-label symmetry
    restriction is used. The bounds also work on small exhaustive controls.
    """
    budget = budget or Budget()
    validate_parameters(adj, target, neighbours, minimum, coverage, budget)
    n = len(adj)
    formula, counts, set_counts = Formula(n * neighbours), {}, {}
    total = 0

    def variable(vertex, colour):
        return neighbours * vertex + colour + 1

    def append(clause):
        nonlocal total
        if total >= MAX_CLAUSES:
            raise SearchLimit("encoding clause limit")
        if total % 256 == 0:
            budget.check()
        emit(tuple(clause))
        total += 1

    for colour in range(neighbours):
        low, high = max(0, minimum - 1), min(n, target - 2)
        if low > high:
            formula.add()
        else:
            cardinality(formula, [variable(v, colour) for v in range(n)], low, high)
    counts["a_attachment_degrees"] = len(formula.clauses)
    before = len(formula.clauses)
    for v, row in enumerate(adj):
        low = max(int(coverage), minimum - row.bit_count())
        high = min(neighbours, target - 1 - row.bit_count())
        if low > high:
            formula.add()
        else:
            cardinality(formula, [variable(v, a) for a in range(neighbours)], low, high)
    counts["h_attachment_degrees"] = len(formula.clauses) - before
    for clause in formula.clauses:
        append(clause)
    before = total
    for u, v in itertools.combinations(range(n), 2):
        if adj[u] >> v & 1:
            for colour in range(neighbours):
                append((-variable(u, colour), -variable(v, colour)))
    counts["triangle_exclusions"] = total - before
    # A centre-containing independent set lies in {centre} union H and has
    # size <=target-1. Without the centre, B=A-intersection has size0..m.
    # B=0 is handled by alpha(H)<=target-2; enumerate every B of sizes1..m.
    for k in range(1, neighbours + 1):
        size, before, set_total = target - k, total, 0
        colours = list(itertools.combinations(range(neighbours), k))
        for mask in independent_sets(adj, size, budget=budget):
            set_total += 1
            vertices = [v for v in range(n) if mask >> v & 1]
            for selected in colours:
                append(variable(v, a) for v in vertices for a in selected)
        set_counts[str(size)] = set_total
        counts[f"cover_independent_{size}_sets"] = total - before
    budget.check()
    return {"schema_version": 1, "base_order": n, "extension_order": n + neighbours + 1,
            "independent_set_target": target, "neighbour_count": neighbours,
            "minimum_degree": minimum, "maximum_degree": target - 1,
            "centre_coverage_required": coverage, "attachment_variables": n * neighbours,
            "variables": formula.variables, "clauses": total, "clause_counts": counts,
            "independent_set_counts": set_counts, "independent_set_constraints_complete": True,
            "symmetry_breaking": False, "base_adjacency": adj,
            "base_adjacency_sha256": graph_digest(adj)}


def extension(adj, neighbours, positive_variables):
    n = len(adj)
    if (any(type(v) is not int for v in positive_variables)
            or not set(positive_variables) <= set(range(1, n * neighbours + 1))):
        raise ValueError("invalid attachment variable")
    result, centre = list(adj) + [0] * (neighbours + 1), n + neighbours
    for colour in range(neighbours):
        result[n + colour] |= 1 << centre
        result[centre] |= 1 << (n + colour)
    for value in positive_variables:
        vertex, colour = divmod(value - 1, neighbours)
        result[vertex] |= 1 << (n + colour)
        result[n + colour] |= 1 << vertex
    return result


def write_instance(output, adj, **parameters):
    """Publish instance.cnf only after complete enumeration and size checks."""
    output = Path(output)
    budget = parameters.pop("budget", None) or Budget()
    body = output / "clauses.partial"
    cnf_partial, cnf = output / "instance.cnf.partial", output / "instance.cnf"
    if any(path.exists() for path in (body, cnf_partial, cnf, output / "instance.json")):
        raise ValueError("instance output must be new")
    byte_count = 0
    with body.open("xb") as destination:
        def emit(clause):
            nonlocal byte_count
            raw = (" ".join(map(str, clause)) + " 0\n").encode("ascii")
            byte_count += len(raw)
            if byte_count + 64 > MAX_CNF_BYTES:
                raise SearchLimit("CNF byte limit")
            destination.write(raw)
        metadata = encode(adj, emit, budget=budget, **parameters)
    with cnf_partial.open("xb") as destination, body.open("rb") as source:
        destination.write(f"p cnf {metadata['variables']} {metadata['clauses']}\n".encode("ascii"))
        for block in iter(lambda: source.read(262144), b""):
            budget.check()
            destination.write(block)
    budget.check()
    cnf_partial.replace(cnf)
    body.unlink()
    metadata.update({"cnf_sha256": digest(cnf), "cnf_bytes": cnf.stat().st_size})
    (output / "instance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata
