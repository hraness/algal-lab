"""Bounded independent search for weighted-removal tree structure.

This is a development spike, not a registered holdout. No paid inference.
Only Python's standard library is required. Fraction mode certifies finalists.
"""
from itertools import product
from fractions import Fraction
import json
import sys


def trees(n):
    for code in product(range(n), repeat=n - 2):
        degree = [1] * n
        for node in code:
            degree[node] += 1
        edges = []
        for node in code:
            leaf = next(i for i in range(n) if degree[i] == 1)
            edges.append(tuple(sorted((leaf, node))))
            degree[leaf] -= 1
            degree[node] -= 1
        edges.append(tuple(i for i in range(n) if degree[i] == 1))
        yield tuple(sorted(edges))


def probabilities(weights, exact=False):
    n = len(weights)
    zero = Fraction(0) if exact else 0.0
    one = Fraction(1) if exact else 1.0
    p = [zero] * (1 << n)
    p[0] = one
    total = sum(weights)
    for mask in range(1, 1 << n):
        for i, w in enumerate(weights):
            if mask & (1 << i):
                prev = mask ^ (1 << i)
                remain = total - sum(weights[j] for j in range(n) if prev & (1 << j))
                p[mask] += p[prev] * w / remain
    return p


def deficits(edges, values):
    n = len(values)
    neighbors = [0] * n
    for a, b in edges:
        neighbors[a] |= 1 << b
        neighbors[b] |= 1 << a
    result = []
    for removed in range(1 << n):
        alive = ((1 << n) - 1) ^ removed
        unseen = alive
        best = 0
        while unseen:
            frontier = unseen & -unseen
            unseen ^= frontier
            value = 0
            while frontier:
                bit = frontier & -frontier
                frontier ^= bit
                node = bit.bit_length() - 1
                value += values[node]
                found = neighbors[node] & unseen
                unseen ^= found
                frontier |= found
            best = max(best, value)
        result.append(sum(values[i] for i in range(n) if alive & (1 << i)) - best)
    return result


def loss(d, p, horizon, total):
    return sum((1 if mask.bit_count() in (0, horizon) else 2) * p[mask] * delta
               for mask, delta in enumerate(d) if mask.bit_count() <= horizon) / (2 * horizon * total)


def search(n=4, bound=3):
    if type(n) is not int or type(bound) is not int or n not in (4, 5) or not 1 <= bound <= (5 if n == 4 else 3):
        raise ValueError("search bounds: n=4 with 1<=bound<=5, or n=5 with 1<=bound<=3")
    all_trees = list(trees(n))
    star_indices = [i for i, edges in enumerate(all_trees)
                    if any(sum(node in edge for edge in edges) == n - 1 for node in range(n))]
    profiles = list(product(range(1, bound + 1), repeat=n))
    probabilities_by_weight = [(w, probabilities(w)) for w in profiles]
    tested = 0
    for values in profiles:
        all_deficits = [deficits(edges, values) for edges in all_trees]
        for weights, p in probabilities_by_weight:
            tested += 1
            for horizon in range(1, n - 1):
                losses = [loss(d, p, horizon, sum(values)) for d in all_deficits]
                best_star = min(star_indices, key=lambda i: losses[i])
                best = min(range(len(all_trees)), key=lambda i: losses[i])
                if losses[best] < losses[best_star] - 1e-12:
                    exact_p = probabilities(weights, exact=True)
                    exact_losses = [loss(d, exact_p, horizon, sum(values)) for d in all_deficits]
                    best_star = min(star_indices, key=lambda i: exact_losses[i])
                    best = min(range(len(all_trees)), key=lambda i: exact_losses[i])
                    print(json.dumps({"kind": "counterexample", "nodes": n, "bound": bound,
                        "profiles_tested": tested, "horizon": horizon, "weights": weights, "values": values,
                        "tree": all_trees[best], "tree_loss": str(exact_losses[best]),
                        "best_star": all_trees[best_star], "star_loss": str(exact_losses[best_star]),
                        "gain": str(exact_losses[best_star] - exact_losses[best]),
                        "all_star_losses": [{"edges": all_trees[i], "loss": str(exact_losses[i])} for i in star_indices],
                        "minimizers": sum(v == exact_losses[best] for v in exact_losses)}, indent=2))
                    return
    print(json.dumps({"kind": "no_counterexample", "nodes": n, "bound": bound,
        "profiles_tested": tested, "trees_per_profile": len(all_trees), "horizons": list(range(1, n - 1))}, indent=2))


if __name__ == "__main__":
    try:
        if len(sys.argv) > 3:
            raise ValueError("usage: tree_search.py [nodes [bound]]")
        search(*(int(v) for v in sys.argv[1:]))
    except ValueError as error:
        raise SystemExit(str(error)) from None
