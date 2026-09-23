"""Bounded, independent rational checks for the weighted-tree theorem.

Run with Python 3.10+ from any directory. No dependencies, inference, network,
or repository implementation imports. All deletion orders and labeled trees
are enumerated; exact arithmetic is used throughout. This finite audit supports
the separate general proof and does not establish novelty.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product
from json import dumps
from math import factorial, lcm


def prufer_tree(sequence):
    n = len(sequence) + 2
    degrees = [1] * n
    for vertex in sequence:
        degrees[vertex] += 1
    edges = []
    for vertex in sequence:
        leaf = next(i for i, degree in enumerate(degrees) if degree == 1)
        edges.append(tuple(sorted((leaf, vertex))))
        degrees[leaf] -= 1
        degrees[vertex] -= 1
    edges.append(tuple(i for i, degree in enumerate(degrees) if degree == 1))
    return tuple(sorted(edges))


def components(n, edges, mask):
    unseen = {i for i in range(n) if mask & (1 << i)}
    found = []
    while unseen:
        stack = [unseen.pop()]
        component = 0
        while stack:
            vertex = stack.pop()
            component |= 1 << vertex
            for a, b in edges:
                neighbor = b if a == vertex else a if b == vertex else -1
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        found.append(component)
    return tuple(found)


@lru_cache(maxsize=5)
def trees(n):
    assert 2 <= n <= 6
    found = tuple(prufer_tree(sequence) for sequence in product(range(n), repeat=n - 2))
    assert len(set(found)) == n ** (n - 2)
    return found


@lru_cache(maxsize=5)
def component_tables(n):
    return tuple(tuple(components(n, tree, mask) for mask in range(1 << n)) for tree in trees(n))


def diameter(n, edges):
    maximum = 0
    for root in range(n):
        distances = {root: 0}
        pending = [root]
        for vertex in pending:
            for a, b in edges:
                neighbor = b if a == vertex else a if b == vertex else -1
                if neighbor >= 0 and neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    pending.append(neighbor)
        maximum = max(maximum, max(distances.values()))
    return maximum


@lru_cache(maxsize=256)
def survival_probabilities(weights):
    n = len(weights)
    assert 2 <= n <= 6 and all(isinstance(w, int) and w > 0 for w in weights)
    probabilities = [[Fraction(0) for _ in range(1 << n)] for _ in range(n + 1)]
    order_count = 0
    for order in permutations(range(n)):
        chance = Fraction(1)
        remaining_weight = sum(weights)
        for vertex in order:
            chance *= Fraction(weights[vertex], remaining_weight)
            remaining_weight -= weights[vertex]
        mask = (1 << n) - 1
        probabilities[0][mask] += chance
        for removed, vertex in enumerate(order, 1):
            mask ^= 1 << vertex
            probabilities[removed][mask] += chance
        order_count += 1
    assert order_count == factorial(n)
    for removed, row in enumerate(probabilities):
        assert sum(row) == 1
        assert all((probability > 0) == (mask.bit_count() == n - removed) for mask, probability in enumerate(row))
    return tuple(tuple(row) for row in probabilities)


def integer_distribution(probabilities):
    rows = []
    for row in probabilities:
        denominator = lcm(*(probability.denominator for probability in row))
        entries = tuple((mask, int(probability * denominator)) for mask, probability in enumerate(row) if probability)
        rows.append((denominator, entries))
    return rows


def values_by_mask(values):
    return tuple(sum(value for i, value in enumerate(values) if mask & (1 << i)) for mask in range(1 << len(values)))


def tree_scores(n, values, distribution):
    totals = values_by_mask(values)
    result = []
    for table in component_tables(n):
        largest = [max((totals[part] for part in parts), default=0) for parts in table]
        result.append(tuple(Fraction(sum(chance * largest[mask] for mask, chance in entries), denominator)
                            for denominator, entries in distribution))
    return result


def star_index(n, center):
    star = tuple(sorted(tuple(sorted((center, vertex))) for vertex in range(n) if vertex != center))
    return trees(n).index(star)


def auc(trajectory, values, horizon):
    return (trajectory[0] + trajectory[horizon] + 2 * sum(trajectory[1:horizon])) / (2 * horizon * sum(values))


def check_pair_order(weights, probabilities):
    n = len(weights)
    count = 0
    for removed in range(1, n - 1):
        row = probabilities[removed]
        pairs = {(i, j): sum(probability for mask, probability in enumerate(row) if mask & (1 << i) and mask & (1 << j))
                 for i in range(n) for j in range(n) if i != j}
        for a, b, other in permutations(range(n), 3):
            if weights[a] <= weights[b]:
                assert pairs[a, other] >= pairs[b, other]
                assert (pairs[a, other] == pairs[b, other]) == (weights[a] == weights[b])
                count += 1
    return count


def profile_values(n, weights):
    if n <= 4:
        return tuple(product((1, 2), repeat=n))
    center = min(range(n), key=lambda i: weights[i])
    profiles = {(1,) * n}
    for seed in range(4):
        values = [1 + ((i + 1) * (seed + 3) + i * i) % 11 for i in range(n)]
        values[center] = max(values)
        profiles.add(tuple(values))
    return tuple(sorted(profiles))


def verify_theorem():
    total_profiles = 0
    total_tree_profiles = 0
    total_step_comparisons = 0
    total_pair_comparisons = 0
    rows = []
    for n in range(2, 7):
        profiles = 0
        all_trees = trees(n)
        diameters = [diameter(n, tree) for tree in all_trees]
        internal = [tuple(i for i in range(n) if sum(i in edge for edge in tree) >= 2) for tree in all_trees]
        for weights in product((1, 2), repeat=n):
            probabilities = survival_probabilities(weights)
            distribution = integer_distribution(probabilities)
            total_pair_comparisons += check_pair_order(weights, probabilities)
            for values in profile_values(n, weights):
                centers = [i for i in range(n) if weights[i] == min(weights) and values[i] == max(values)]
                if not centers:
                    continue
                center = centers[0]
                star = star_index(n, center)
                scores = tree_scores(n, values, distribution)
                unique_minimum = weights.count(min(weights)) == 1
                for index, trajectory in enumerate(scores):
                    centers_of_tree = internal[index]
                    top_two = sorted(values)[-2:]
                    all_horizon_equal = n == 2 or (
                        all(weights[i] == min(weights) for i in centers_of_tree)
                        and ((len(centers_of_tree) == 1 and values[centers_of_tree[0]] >= top_two[0])
                             or (len(centers_of_tree) == 2 and sorted(values[i] for i in centers_of_tree) == top_two))
                    )
                    assert (trajectory == scores[star]) == all_horizon_equal
                    for removed in range(n + 1):
                        assert trajectory[removed] <= scores[star][removed], (n, weights, values, all_trees[index], removed)
                        if unique_minimum and index != star and 1 <= removed <= n - 2:
                            assert trajectory[removed] < scores[star][removed]
                        if len(set(values)) == 1 and 1 <= removed <= n - 2:
                            expected_equal = all(weights[i] == min(weights) for i in internal[index]) and (n - removed <= 3 or diameters[index] <= 3)
                            assert (trajectory[removed] == scores[star][removed]) == expected_equal
                        total_step_comparisons += 1
                profiles += 1
                total_tree_profiles += len(all_trees)
        total_profiles += profiles
        rows.append({"nodes": n, "labeled_trees": len(all_trees), "profiles": profiles, "orders_per_weight_profile": factorial(n)})
    return {"passed": True, "profiles": total_profiles, "tree_profiles": total_tree_profiles,
            "step_comparisons": total_step_comparisons, "pair_order_comparisons": total_pair_comparisons, "bounds": rows}


def verify_counterexample():
    n = 4
    weights = (3, 3, 1, 1)
    values = (6, 6, 1, 1)
    path = ((0, 1), (0, 2), (2, 3))
    scores = tree_scores(n, values, integer_distribution(survival_probabilities(weights)))
    path_index = trees(n).index(path)
    path_auc = auc(scores[path_index], values, 2)
    star_aucs = [auc(scores[star_index(n, center)], values, 2) for center in range(n)]
    assert path_auc > max(star_aucs)
    assert path_auc == max(auc(trajectory, values, 2) for trajectory in scores)
    assert [path_auc - candidate for candidate in star_aucs] == [Fraction(1, 784), Fraction(1, 784), Fraction(3, 1960), Fraction(3, 1960)]
    return {"nodes": n, "weights": weights, "values": values, "edges": path, "horizon": 2,
            "trajectory": [str(value) for value in scores[path_index]], "auc": str(path_auc),
            "star_auc_by_center": [str(value) for value in star_aucs],
            "all_labeled_trees_checked": len(scores), "globally_optimal": True,
            "gap_over_best_star": str(path_auc - max(star_aucs))}


def verify_registered_domain_counterexample():
    n, weights, values = 4, (1, 1, 2, 5), (1, 1, 4, 4)
    path = ((0, 1), (0, 2), (2, 3))
    scores = tree_scores(n, values, integer_distribution(survival_probabilities(weights)))
    path_auc = auc(scores[trees(n).index(path)], values, 2)
    star_aucs = [auc(scores[star_index(n, center)], values, 2) for center in range(n)]
    assert path_auc == Fraction(12937, 20160)
    assert max(star_aucs) == Fraction(6467, 10080)
    assert path_auc - max(star_aucs) == Fraction(1, 6720)
    assert path_auc == max(auc(trajectory, values, 2) for trajectory in scores)
    return {"nodes": n, "weights": weights, "values": values, "edges": path, "horizon": 2,
            "auc": str(path_auc), "star_auc_by_center": [str(value) for value in star_aucs],
            "globally_optimal": True, "gap_over_best_star": str(path_auc - max(star_aucs))}


def verify_upper_bound():
    profile_count = 0
    comparisons = 0
    for n in range(2, 7):
        rate_profiles = tuple(product((1, 2), repeat=n)) if n <= 5 else tuple(
            tuple(1 + (i * i + seed * (i + 1)) % 5 for i in range(n)) for seed in range(5)
        )
        for weights in rate_profiles:
            distribution = integer_distribution(survival_probabilities(weights))
            value_profiles = tuple(product((1, 2), repeat=n)) if n <= 4 else tuple(
                tuple(1 + ((i + 1) * (seed + 3) + i * i) % 7 for i in range(n)) for seed in range(2)
            )
            for values in value_profiles:
                center = min(range(n), key=lambda i: (weights[i], -values[i]))
                totals = values_by_mask(values)
                maxima = [max((values[i] for i in range(n) if mask & (1 << i)), default=0) for mask in range(1 << n)]
                limits = []
                for denominator, entries in distribution:
                    total_limit = Fraction(sum(chance * totals[mask] for mask, chance in entries), denominator)
                    forest_limit = Fraction(sum(chance * (maxima[mask] + (totals[mask] - values[center] if mask & (1 << center) else 0))
                                                for mask, chance in entries), denominator)
                    limits.append(min(total_limit, forest_limit))
                for trajectory in tree_scores(n, values, distribution):
                    for actual, limit in zip(trajectory, limits):
                        assert actual <= limit
                        comparisons += 1
                profile_count += 1
    return {"passed": True, "profiles": profile_count, "exact_step_comparisons": comparisons}


if __name__ == "__main__":
    print(dumps({"theorem": verify_theorem(), "counterexample": verify_counterexample(),
                 "registered_domain_counterexample": verify_registered_domain_counterexample(),
                 "upper_bound": verify_upper_bound()}, indent=2))
