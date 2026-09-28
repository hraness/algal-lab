"""A finite family: every two-vertex deletion of one verified 35-vertex graph.

Only affine permutations checked against every edge AND nonedge may identify
deletion pairs. Each of the 595 pairs retains an explicit induced isomorphism.
No assertion is made about completeness among all 33-vertex Ramsey graphs.
"""

import itertools
import math

from shared import Budget, checker, graph_digest

DIFFERENCES = (8, 12, 14, 17, 18, 21, 23, 27)
PUBLISHED_DIFFERENCES = (1, 7, 11, 16, 19, 24, 28, 34)


def base_graph():
    return [sum(1 << ((v + d) % 35) for d in DIFFERENCES) for v in range(35)]


def is_isomorphism(left, right, permutation):
    if (len(left) != len(right) or len(permutation) != len(left)
            or any(type(v) is not int for v in permutation)
            or sorted(permutation) != list(range(len(left)))):
        return False
    return all(((left[u] >> v) & 1) == ((right[permutation[u]] >> permutation[v]) & 1)
               for u in range(len(left)) for v in range(len(left)))


def induced(adj, retained):
    if (any(type(v) is not int for v in retained) or len(set(retained)) != len(retained)
            or not set(retained) <= set(range(len(adj))) or not retained):
        raise ValueError("invalid induced vertex list")
    return [sum(1 << j for j, v in enumerate(retained) if adj[u] >> v & 1)
            for u in retained]


def verified_affine_maps(adj, *, budget=None):
    checker.validate_adjacency(adj)
    n = len(adj)
    if not 3 <= n <= 40:
        raise ValueError("affine catalogue order outside 3..40")
    budget = budget or Budget()
    result = []
    for a in range(n):
        if math.gcd(a, n) != 1:
            continue
        for b in range(n):
            budget.check()
            permutation = [(a * x + b) % n for x in range(n)]
            if is_isomorphism(adj, adj, permutation):
                result.append({"a": a, "b": b, "permutation": permutation})
    if not any(item["permutation"] == list(range(n)) for item in result):
        raise ValueError("identity automorphism missing")
    return result


def pair_catalogue(adj, *, budget=None):
    """Cover all labelled pairs; make no claim to have the full automorphism group."""
    budget = budget or Budget()
    maps = verified_affine_maps(adj, budget=budget)
    n = len(adj)
    all_pairs = set(itertools.combinations(range(n), 2))
    remaining, cases = set(all_pairs), []
    while remaining:
        representative = min(remaining)
        retained = [v for v in range(n) if v not in representative]
        graph = induced(adj, retained)
        members = {}
        for index, entry in enumerate(maps):
            budget.check()
            permutation = entry["permutation"]
            pair = tuple(sorted(permutation[v] for v in representative))
            if pair in members:
                continue
            target_retained = [v for v in range(n) if v not in pair]
            lookup = {v: i for i, v in enumerate(target_retained)}
            induced_map = [lookup[permutation[v]] for v in retained]
            if not is_isomorphism(graph, induced(adj, target_retained), induced_map):
                raise ValueError("induced orbit map failed")
            members[pair] = {"pair": list(pair), "automorphism_index": index,
                             "induced_permutation": induced_map}
        if not set(members) <= remaining:
            raise ValueError("affine orbits overlap")
        remaining -= set(members)
        cases.append({"index": len(cases), "representative_pair": list(representative),
                      "retained_vertices": retained, "adjacency": graph,
                      "adjacency_sha256": graph_digest(graph),
                      "edges": sum(row.bit_count() for row in graph) // 2,
                      "members": [members[pair] for pair in sorted(members)]})
    covered = [tuple(member["pair"]) for case in cases for member in case["members"]]
    if len(covered) != len(all_pairs) or set(covered) != all_pairs:
        raise ValueError("pair catalogue incomplete or duplicated")
    return {"schema_version": 1, "source_adjacency": adj,
            "source_adjacency_sha256": graph_digest(adj), "source_order": n,
            "scope": "induced graphs obtained by deleting exactly two source vertices",
            "is_complete_33_vertex_ramsey_catalogue": False,
            "automorphisms": maps, "labelled_pairs": len(all_pairs), "cases": cases}


def ramsey_catalogue(*, budget=None):
    budget = budget or Budget()
    graph = base_graph()
    published = [sum(1 << ((v + d) % 35) for d in PUBLISHED_DIFFERENCES)
                 for v in range(35)]
    if not is_isomorphism(graph, published, [22 * v % 35 for v in range(35)]):
        raise ValueError("published representative map failed")
    if (any(row.bit_count() != 8 for row in graph) or checker.triangle(graph) is not None
            or checker.independent_set(graph, 9, node_limit=1_000_000,
                                       deadline=budget.wall_start + budget.seconds) is not None):
        raise ValueError("35-vertex source failed independent graph checks")
    catalogue = pair_catalogue(graph, budget=budget)
    catalogue["source_evidence"] = {
        "reference": "Goedgebeur and Radziszowski, EJC 20(1), P30 (2013), Theorem 3",
        "url": "https://doi.org/10.37236/2824",
        "published_circulant_differences": list(PUBLISHED_DIFFERENCES),
        "local_circulant_differences": list(DIFFERENCES),
        "local_to_published_multiplier_mod35": 22,
        "triangle_free_checked": True, "independent_nine_set_absent_checked": True,
        "regular_degree": 8, "edges": 140,
    }
    budget.check()
    return catalogue
