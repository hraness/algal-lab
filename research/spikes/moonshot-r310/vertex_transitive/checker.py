"""Small, independent graph checks; no search-generator imports or dependencies."""

import argparse
import json
import time


class SearchLimit(RuntimeError):
    """An interrupted decision is not a negative result."""


def validate_adjacency(adj):
    n = len(adj)
    if not 1 <= n <= 63:
        raise ValueError("expected 1..63 vertices")
    for v, row in enumerate(adj):
        if type(row) is not int or not 0 <= row < 1 << n:
            raise ValueError("invalid adjacency mask")
        if row >> v & 1:
            raise ValueError("loop")
        for w in range(n):
            if (row >> w & 1) != (adj[w] >> v & 1):
                raise ValueError("asymmetric adjacency")


def triangle(adj):
    """Return a triangle, or None, by directly inspecting triples."""
    for u in range(len(adj)):
        for v in range(u + 1, len(adj)):
            if not adj[u] >> v & 1:
                continue
            common = adj[u] & adj[v] & ~((1 << (v + 1)) - 1)
            if common:
                return (u, v, (common & -common).bit_length() - 1)
    return None


def verify_independent(adj, mask, target):
    if type(mask) is not int or mask < 0 or mask >> len(adj):
        return False
    return mask.bit_count() >= target and all(
        not (adj[v] & mask) for v in range(len(adj)) if mask >> v & 1
    )


def independent_set(adj, target, *, node_limit=None, deadline=None):
    """Exact threshold decision via complement coloring, unlike the C search.

    This returns a real witness, not a floating point bound. At each node the
    greedy coloring is a proper coloring of the complement induced by P. Its
    color count bounds the size of any independent extension in the graph.
    """
    validate_adjacency(adj)
    n = len(adj)
    if not 1 <= target <= n:
        raise ValueError("target outside 1..n")
    full = (1 << n) - 1
    comp = [full & ~row & ~(1 << v) for v, row in enumerate(adj)]
    nodes = 0

    def visit(p, chosen):
        nonlocal nodes
        nodes += 1
        if node_limit is not None and nodes > node_limit:
            raise SearchLimit("independent-set node limit")
        if deadline is not None and (nodes == 1 or nodes % 256 == 0) and time.monotonic() >= deadline:
            raise SearchLimit("independent-set deadline")
        if chosen.bit_count() >= target:
            return chosen
        if p.bit_count() + chosen.bit_count() < target:
            return None
        order, bounds = [], []
        remaining = p
        color = 0
        while remaining:
            color += 1
            available = remaining
            while available:
                bit = available & -available
                v = bit.bit_length() - 1
                order.append(v)
                bounds.append(color)
                remaining ^= bit
                available &= ~bit & ~comp[v]
        for v, bound in reversed(list(zip(order, bounds))):
            if chosen.bit_count() + bound < target:
                return None
            bit = 1 << v
            result = visit(p & comp[v], chosen | bit)
            if result is not None:
                return result
            p &= ~bit
        return None

    return visit(full, 0)


def verify_candidate(adj, target=10, expected_order=40):
    validate_adjacency(adj)
    if len(adj) != expected_order:
        raise ValueError("wrong graph order")
    tri = triangle(adj)
    independent = independent_set(adj, target) if tri is None else None
    return {
        "order": len(adj),
        "edges": sum(row.bit_count() for row in adj) // 2,
        "triangle": tri,
        "independent_set": (
            [v for v in range(len(adj)) if independent >> v & 1]
            if independent is not None else None
        ),
        "is_ramsey_witness": tri is None and independent is None,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="JSON array of integer adjacency masks")
    parser.add_argument("--order", type=int, default=40)
    parser.add_argument("--target", type=int, default=10)
    args = parser.parse_args()
    with open(args.graph) as source:
        graph = json.load(source)
    print(json.dumps(verify_candidate(graph, args.target, args.order), indent=2))
