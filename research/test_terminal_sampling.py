"""Independent finite arithmetic checks for sampling and confidence certificates."""
from collections import defaultdict
from decimal import localcontext, ROUND_DOWN
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb, factorial
from random import Random
import unittest

from research import terminal_sampling as sampling


def all_trees(nodes):
    for edges in combinations(combinations(range(nodes), 2), nodes-1):
        reached = {0}
        while True:
            enlarged = reached | {b for a, b in edges if a in reached} | {a for a, b in edges if b in reached}
            if enlarged == reached:
                break
            reached = enlarged
        if len(reached) == nodes:
            yield edges


def exact_pairs(weights):
    probabilities = defaultdict(F)
    for order in permutations(range(len(weights)), len(weights)-2):
        remaining, probability = set(range(len(weights))), F(1)
        for node in order:
            probability *= F(weights[node], sum(weights[j] for j in remaining))
            remaining.remove(node)
        probabilities[tuple(sorted(remaining))] += probability
    return probabilities


def count_vectors(total, cells):
    if cells == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for rest in count_vectors(total-first, cells-1):
                yield (first,) + rest


class TerminalSamplingTests(unittest.TestCase):
    def test_integer_sampler_exact_distribution_by_ticket_enumeration(self):
        weights = [1, 2, 3, 4]
        pairs = list(combinations(range(4), 2))
        measured = defaultdict(F)
        for first in range(sum(weights)):
            remaining_ticket, removed = first, 0
            while remaining_ticket >= weights[removed]:
                remaining_ticket -= weights[removed]
                removed += 1
            next_total = sum(weights)-weights[removed]
            for second in range(next_total):
                tape = iter(((sum(weights), first), (next_total, second)))

                def draw(total):
                    expected, ticket = next(tape)
                    self.assertEqual(total, expected)
                    return ticket

                counts, operations = sampling._draw_pair_counts(weights, 1, draw)
                self.assertEqual(sum(counts), 1)
                self.assertEqual(operations["integerDraws"], 2)
                measured[pairs[counts.index(1)]] += F(1, sum(weights)*next_total)
        self.assertEqual(dict(measured), dict(exact_pairs(weights)))
        self.assertEqual(sum(measured.values()), 1)

    def test_kl_outward_endpoints_using_exact_integer_likelihoods(self):
        # No transcendental arithmetic in the reference comparison:
        # exp(N KL)>2m/delta iff this exact integer product is greater.
        d, m, delta = sampling.DYADIC_DENOMINATOR, 6, F(1, 20)
        for n in (1, 2, 8, 32):
            engine = sampling._KLDyadicIntervals(n, m, delta)
            for count in range(n+1):
                lower, upper = engine.bounds(count)

                def outside(k):
                    left = count**count * (n-count)**(n-count) * d**n * delta.numerator
                    right = n**n * k**count * (d-k)**(n-count) * 2*m*delta.denominator
                    return left > right

                self.assertLessEqual(F(lower, d), F(count, n))
                self.assertGreaterEqual(F(upper, d), F(count, n))
                if lower:
                    self.assertTrue(outside(lower))
                    self.assertFalse(outside(lower+1))
                if upper < d:
                    self.assertTrue(outside(upper))
                    self.assertFalse(outside(upper-1))
            self.assertGreater(engine.bounds(0)[1], 0, "unseen pairs retain positive upper probability")

    def test_exact_binomial_coverage_on_rational_grid(self):
        n, m, delta = 12, 6, F(1, 20)
        engine = sampling._KLDyadicIntervals(n, m, delta)
        intervals = [tuple(F(x, sampling.DYADIC_DENOMINATOR) for x in engine.bounds(c)) for c in range(n+1)]
        for numerator in range(1, 40):
            p = F(numerator, 40)
            failure = sum(F(comb(n, c))*p**c*(1-p)**(n-c)
                          for c, (lower, upper) in enumerate(intervals) if not lower <= p <= upper)
            self.assertLessEqual(failure, delta/m)

    def test_certificate_equals_exact_regret_when_box_is_a_point(self):
        values, pairs = [1, 1, 4, 4], list(combinations(range(4), 2))
        numerators = [6, 3, 1, 2, 1, 3]
        q = dict(zip(pairs, map(lambda x: F(x, 16), numerators)))
        score = lambda tree: sum(q[e]*min(values[e[0]], values[e[1]])/sum(values) for e in tree)
        trees = list(all_trees(4))
        optimum = max(map(score, trees))
        intervals = [(x*(sampling.DYADIC_DENOMINATOR//16),)*2 for x in numerators]
        for candidate in trees:
            self.assertEqual(sampling._regret_certificate(values, pairs, candidate, intervals), optimum-score(candidate))

    def test_exact_multinomial_adaptive_candidate_coverage(self):
        environment = {"weights": [1, 2, 3, 4], "values": [1, 1, 9, 9]}
        values, n, delta = environment["values"], 6, F(1, 4)
        pairs = list(combinations(range(4), 2))
        q = exact_pairs(environment["weights"])
        score = lambda tree: sum(q[e]*min(values[e[0]], values[e[1]])/sum(values) for e in tree)
        optimum = max(map(score, all_trees(4)))
        engine = sampling._KLDyadicIntervals(n, len(pairs), delta)
        failure = {"kruskal": F(0), "frontier": F(0)}
        total = F(0)
        for counts in count_vectors(n, len(pairs)):
            probability = F(factorial(n))
            for pair, count in zip(pairs, counts):
                probability *= q[pair]**count / factorial(count)
            total += probability
            weights = {pair: count*min(values[pair[0]], values[pair[1]]) for pair, count in zip(pairs, counts)}
            intervals = sampling._simplex_tighten([engine.bounds(c) for c in counts])
            for method in failure:
                candidate, _ = sampling._candidate(environment, weights, method)
                bound = sampling._regret_certificate(values, pairs, candidate, intervals)
                if optimum-score(candidate) > bound:
                    failure[method] += probability
        self.assertEqual(total, 1)
        self.assertTrue(all(mass <= delta for mass in failure.values()))

    def test_empirical_optima_and_frontier_family(self):
        environment = {"weights": [1, 2, 3, 4], "values": [1, 2, 3, 4]}
        pairs = list(combinations(range(4), 2))
        weights = dict(zip(pairs, (1, 5, 9, 2, 7, 4)))
        score = lambda tree: sum(weights[e] for e in tree)
        candidate, _ = sampling._candidate(environment, weights, "kruskal")
        self.assertEqual(score(candidate), max(map(score, all_trees(4))))
        candidate, _ = sampling._candidate(environment, weights, "frontier")
        restricted = [tuple((parent, child) for child, parent in enumerate(parents, 1))
                      for parents in product(range(1), range(2), range(3))]
        self.assertEqual(score(candidate), max(map(score, restricted)))

    def test_public_replay_context_isolation_and_upward_float(self):
        environment = {"weights": [1, 1, 2, 5], "values": [1, 1, 4, 4]}
        first = sampling.sample_terminal_tree(environment, 128, randbelow=Random(7).randrange)
        second = sampling.sample_terminal_tree(environment, 128, randbelow=Random(7).randrange)
        self.assertEqual(first, second)
        with localcontext() as context:
            context.prec = 3
            context.rounding = ROUND_DOWN
            replay = sampling.optimize_counts(environment, first["pairCounts"])
        ordinary = sampling.optimize_counts(environment, first["pairCounts"])
        self.assertEqual(replay, ordinary)
        self.assertEqual(replay["graph"], first["graph"])
        self.assertEqual(sum(first["pairCounts"]), 128)
        self.assertEqual(first["operations"]["integerDraws"], 256)
        self.assertGreaterEqual(F.from_float(first["confidenceRegretBound"]), F(first["confidenceRegretBoundExact"]))
        pair = sampling.sample_terminal_tree({"weights": [1, 1000000], "values": [3, 5]}, 1)
        self.assertEqual(pair["confidenceRegretBoundExact"], "0")
        self.assertEqual(pair["operations"]["integerDraws"], 0)

    def test_strict_budgets_histograms_methods_and_rng_admission(self):
        environment = {"weights": [1, 2, 3], "values": [1, 2, 3]}
        for samples in (0, -1, True, 32769, 1.5, "1"):
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                sampling.sample_terminal_tree(environment, samples)
        for delta in (None, 0, .3, float("nan"), float("inf"), True, ".05"):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                sampling.sample_terminal_tree(environment, 1, delta)
        for counts in ([1], (1, 0, 0), [0, 0, 0], [-1, 1, 1], [True, 0, 0], [32769, 0, 0], [32768, 1, 0]):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                sampling.optimize_counts(environment, counts)
        for method in (None, "other", 1):
            with self.subTest(method=method), self.assertRaises(ValueError):
                sampling.sample_terminal_tree(environment, 1, method=method)
        for output in (True, -1, 6, .5):
            with self.subTest(output=output), self.assertRaises(ValueError):
                sampling.sample_terminal_tree(environment, 1, randbelow=lambda _: output)
        with self.assertRaises(ValueError):
            sampling.sample_terminal_tree(environment, 1, randbelow="random")


if __name__ == "__main__":
    unittest.main()
