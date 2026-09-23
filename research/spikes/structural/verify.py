"""Exact, bounded structural certificates; no model calls or third-party modules.

Run from the repository root:
    python3 research/spikes/structural/verify.py

The independent order enumerator uses ordinary set/queue connectivity and
Fraction arithmetic. It does not import the instrument or subset evaluator.
"""
from fractions import Fraction as Q
from itertools import permutations, product
import json

from tree_search import deficits, loss, probabilities, trees


def order_auc(edges, weights, values, horizon):
    n = len(values)
    total = sum(values)
    result = Q(0)
    for order in permutations(range(n), horizon):
        alive = set(range(n))
        likelihood = Q(1)
        previous = Q(1)
        area = Q(0)
        for removed in order:
            likelihood *= Q(weights[removed], sum(weights[i] for i in alive))
            alive.remove(removed)
            remaining = alive.copy()
            best = 0
            while remaining:
                queue = [remaining.pop()]
                value = 0
                while queue:
                    node = queue.pop()
                    value += values[node]
                    for a, b in edges:
                        neighbor = b if a == node else a if b == node else None
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            queue.append(neighbor)
                best = max(best, value)
            current = Q(best, total)
            area += (previous + current) / 2
            previous = current
        result += likelihood * area / horizon
    return result


def ceiling(values, p, horizon):
    n = len(values)
    return sum((1 if mask.bit_count() in (0, horizon) else 2) * p[mask]
               * sum(values[i] for i in range(n) if not (mask >> i & 1))
               for mask in range(1 << n) if mask.bit_count() <= horizon) / (2 * horizon * sum(values))


def star(n, hub):
    return tuple(sorted(tuple(sorted((hub, i))) for i in range(n) if i != hub))


def main():
    four_trees = list(trees(4))
    assert len(four_trees) == len(set(four_trees)) == 16
    profiles = list(product(range(1, 4), repeat=4))
    one_failure_comparisons = 0
    for values in profiles:
        all_deficits = [deficits(edges, values) for edges in four_trees]
        total = sum(values)
        for weights in profiles:
            predicted = min(weights[c] * (total - values[c] - max(values[j] for j in range(4) if j != c))
                            for c in range(4))
            actual = min(sum(weights[i] * d[1 << i] for i in range(4)) for d in all_deficits)
            assert actual == predicted
            one_failure_comparisons += len(four_trees)

    fixtures = [
        ((1, 1, 2, 5), (1, 1, 4, 4)),
        ((3, 3, 1, 1), (6, 6, 1, 1)),
        ((1, 2, 3, 4), (5, 4, 3, 2)),
        ((1, 1, 1, 1), (2, 3, 4, 5)),
    ]
    order_comparisons = 0
    counterexample = None
    for weights, values in fixtures:
        p = probabilities(weights, exact=True)
        all_deficits = {edges: deficits(edges, values) for edges in four_trees}
        for horizon in (1, 2):
            upper = ceiling(values, p, horizon)
            scores = {}
            for edges in four_trees:
                dp = upper - loss(all_deficits[edges], p, horizon, sum(values))
                enumerated = order_auc(edges, weights, values, horizon)
                assert dp == enumerated
                scores[edges] = dp
                order_comparisons += 1
            if weights == (1, 1, 2, 5) and horizon == 2:
                optimum = max(scores.values())
                best_star = max(scores[star(4, c)] for c in range(4))
                assert optimum == Q(12937, 20160)
                assert best_star == Q(6467, 10080)
                assert optimum - best_star == Q(1, 6720)
                counterexample = {
                    "weights": weights, "values": values, "horizon": horizon,
                    "optimum": str(optimum), "best_star": str(best_star),
                    "advantage": str(optimum - best_star),
                    "optimal_trees": [edges for edges, score in scores.items() if score == optimum],
                }

    five_trees = list(trees(5))
    assert len(five_trees) == len(set(five_trees)) == 125
    aligned_comparisons = 0
    for weights, values in [((1, 2, 3, 4, 5), (5, 4, 3, 2, 1)),
                            ((1, 1, 2, 2, 3), (5, 5, 3, 1, 2)),
                            ((1, 1, 1, 1, 1), (5, 2, 3, 4, 1))]:
        p = probabilities(weights, exact=True)
        all_deficits = [deficits(edges, values) for edges in five_trees]
        hub_index = five_trees.index(star(5, 0))
        for horizon in (1, 2, 3):
            losses = [loss(d, p, horizon, sum(values)) for d in all_deficits]
            assert losses[hub_index] == min(losses)
            if len(set(weights)) == 5:
                assert sum(d == min(losses) for d in losses) == 1
            aligned_comparisons += len(five_trees)

    family_comparisons = 0
    for r in range(1, 7):
        for x in range(2, 17):
            weights = (r, r, 1, 1)
            values = (x, x, 1, 1)
            p = probabilities(weights, exact=True)
            q_hh = Q(1, (r + 1) * (2 * r + 1))
            q_ll = Q(r * r, (r + 1) * (r + 2))
            q_hl = Q(3 * r, 2 * (r + 2) * (2 * r + 1))
            cost_h = Q(2 * r, r + 1) + 2 * q_hl + q_ll
            cost_l = Q(x + 1, r + 1) + x * q_hh + 2 * q_hl
            cost_p = Q(2 * r + 1, r + 1) + 3 * q_hl
            costs = [4 * sum(values) * loss(deficits(e, values), p, 2, sum(values)) for e in four_trees]
            assert min(costs) == min(cost_h, cost_l, cost_p)
            assert cost_h - cost_p == Q(4 * r * r - 9 * r - 4, 2 * (r + 2) * (2 * r + 1))
            assert (cost_p < cost_h and cost_p < cost_l) == (r >= 3 and x >= 2 * r)
            family_comparisons += len(four_trees)

    print(json.dumps({
        "status": "pass", "arithmetic": "exact rational/integer",
        "one_failure_tree_profile_comparisons": one_failure_comparisons,
        "independent_weighted_order_comparisons": order_comparisons,
        "aligned_hub_tree_horizon_comparisons": aligned_comparisons,
        "two_class_family_tree_comparisons": family_comparisons,
        "registered_domain_counterexample": counterexample,
    }, indent=2))


if __name__ == "__main__":
    main()
