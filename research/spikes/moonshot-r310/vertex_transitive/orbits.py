"""Enumerate every undirected edge orbit of an explicit permutation action."""

import hashlib
import json


def validate_action(action):
    if not isinstance(action, dict) or set(action) != {"name", "n", "generators"}:
        raise ValueError("action fields must be name, n, generators")
    n = action["n"]
    name = action["name"]
    generators = action["generators"]
    if type(n) is not int or not 2 <= n <= 63:
        raise ValueError("action order must be 2..63")
    if not isinstance(name, str) or not 1 <= len(name) <= 160:
        raise ValueError("invalid action name")
    if not isinstance(generators, list) or not 1 <= len(generators) <= 128:
        raise ValueError("expected 1..128 generators")
    for perm in generators:
        if (not isinstance(perm, list) or len(perm) != n
                or any(type(v) is not int for v in perm)
                or sorted(perm) != list(range(n))):
            raise ValueError("generator is not a permutation")
    reached, todo = {0}, [0]
    while todo:
        v = todo.pop()
        for perm in generators:
            w = perm[v]
            if w not in reached:
                reached.add(w)
                todo.append(w)
    if len(reached) != n:
        raise ValueError("action is not transitive")


def edge_orbits(action):
    validate_action(action)
    n = action["n"]
    generators = action["generators"]
    unseen = {(u, v) for u in range(n) for v in range(u + 1, n)}
    result = []
    while unseen:
        first = min(unseen)
        edges, todo = {first}, [first]
        unseen.remove(first)
        while todo:
            u, v = todo.pop()
            for perm in generators:
                edge = tuple(sorted((perm[u], perm[v])))
                if edge not in edges:
                    edges.add(edge)
                    unseen.remove(edge)
                    todo.append(edge)
        adj = [0] * n
        for u, v in edges:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        degree = adj[0].bit_count()
        if any(row.bit_count() != degree for row in adj):
            raise ValueError("nonregular orbital contradicts transitivity")
        result.append({"degree": degree, "adjacency": adj})
    if sum(orbit["degree"] for orbit in result) != n - 1:
        raise ValueError("edge orbit partition is incomplete")
    return result


def adjacency_from_selection(orbits, selection, n):
    if type(selection) is not int or selection < 0 or selection >> len(orbits):
        raise ValueError("invalid orbital selection")
    adj = [0] * n
    for i, orbit in enumerate(orbits):
        if selection >> i & 1:
            adj = [row | added for row, added in zip(adj, orbit["adjacency"])]
    return adj


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
