"""Brute-force controls for the independent cover reproduction."""

import itertools
import random
import unittest

from independent_cover import Budget, LimitExceeded, exact_cover, maximal_independent_sets


class IndependentEnumerationControls(unittest.TestCase):
    def test_maximal_sets_of_every_four_vertex_graph(self):
        edges = list(itertools.combinations(range(4), 2))
        for pattern in range(1 << len(edges)):
            adjacency = [0] * 4
            for bit, (u, v) in enumerate(edges):
                if pattern >> bit & 1:
                    adjacency[u] |= 1 << v
                    adjacency[v] |= 1 << u
            independent = {mask for mask in range(16)
                           if all(not (adjacency[v] & mask)
                                  for v in range(4) if mask >> v & 1)}
            expected = {mask for mask in independent
                        if all((mask | 1 << v) not in independent
                               for v in range(4) if not (mask >> v & 1))}
            actual, _ = maximal_independent_sets(adjacency, Budget())
            self.assertEqual(set(actual), expected)


class IndependentCoverControls(unittest.TestCase):
    def test_dynamic_pivot_may_need_a_decreasing_column_index(self):
        # The first pivot is row0, whose only column is index1. Row1 then
        # requires index0; a global increasing-index restriction loses it.
        answer, _ = exact_cover([2, 1], 3, [1, 1], [{1}, {0}], 2, Budget())
        self.assertEqual(answer, [1, 0])

    def test_zero_required_row_columns_complete_a_cover(self):
        compatible = [set(range(3)) - {i} for i in range(3)]
        answer, _ = exact_cover([1, 2, 4], 1, [1, 1, 1], compatible, 3, Budget())
        self.assertEqual(set(answer), {0, 1, 2})

    def test_bounded_search_never_returns_an_exclusion(self):
        with self.assertRaises(LimitExceeded):
            exact_cover([1], 1, [1], [set()], 1, Budget(nodes=0))
        with self.assertRaises(LimitExceeded):
            maximal_independent_sets([0], Budget(nodes=0))

    def test_random_small_covers_against_all_subsets(self):
        randomizer = random.Random(310)
        satisfiable = 0
        for _ in range(160):
            columns = randomizer.sample(range(32), 8)
            required = randomizer.randrange(32)
            capacities = [1 if required >> v & 1 else randomizer.choice((1, 2, 3))
                          for v in range(5)]
            compatible = [set() for _ in columns]
            for i, j in itertools.combinations(range(len(columns)), 2):
                if randomizer.randrange(5):
                    compatible[i].add(j)
                    compatible[j].add(i)
            goal = randomizer.choice((1, 2, 3, 4))

            def valid(chosen):
                counts = [sum(columns[i] >> v & 1 for i in chosen) for v in range(5)]
                return (all(counts[v] <= capacities[v] for v in range(5))
                        and all(counts[v] == 1 for v in range(5) if required >> v & 1)
                        and all(j in compatible[i] for i, j in itertools.combinations(chosen, 2)))

            expected = {chosen for chosen in itertools.combinations(range(8), goal)
                        if valid(chosen)}
            answer, _ = exact_cover(columns, required, capacities, compatible, goal, Budget())
            self.assertEqual(answer is not None, bool(expected), (columns, required, goal))
            if answer is not None:
                self.assertEqual(len(answer), len(set(answer)))
                self.assertIn(tuple(sorted(answer)), expected)
                satisfiable += 1
        self.assertGreater(satisfiable, 0)


if __name__ == "__main__":
    unittest.main()
