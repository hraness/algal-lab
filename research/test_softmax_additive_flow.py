"""Independent assignment, fractional-grid, and residual-certificate checks."""

from copy import deepcopy
from fractions import Fraction
from itertools import product
import unittest

from research.softmax_additive_flow import (
    maximize_additive_softmax,
    verify_additive_softmax_certificate,
)


def _column_mean(column, exponential):
    # Raw definition sum(x_i E^x_i) / sum(E^x_i) over all n binary efforts,
    # evaluated without the solver's closed form.
    weights = [Fraction(exponential) ** x for x in column]
    return sum((x * w for x, w in zip(column, weights)), Fraction(0)) / sum(weights)


def _objective(n, exponentials, weights, rewards, assignment):
    score = Fraction(0)
    for j, weight in enumerate(weights):
        column = tuple(int(assignment[i] == j) for i in range(n))
        score += Fraction(weight) * _column_mean(column, exponentials[j])
    return score + sum((rewards[i, j] for i, j in enumerate(assignment)
                        if j is not None), Fraction(0))


def _exhaustive(n, capacities, exponentials, weights, edges):
    rewards = {(i, j): Fraction(reward) for i, j, reward in edges}
    choices = tuple((None,) + tuple(j for j in range(len(capacities))
                                   if (i, j) in rewards) for i in range(n))
    best, witnesses = None, []
    for assignment in product(*choices):
        if any(assignment.count(j) > cap for j, cap in enumerate(capacities)):
            continue
        value = _objective(n, exponentials, weights, rewards, assignment)
        if best is None or value > best:
            best, witnesses = value, [assignment]
        elif value == best:
            witnesses.append(assignment)
    return best, witnesses


class AdditiveSoftmaxFlowTests(unittest.TestCase):
    def check_certificate_independently(self, problem, report):
        n = problem["n"]
        capacities, exponentials, weights, edges = (
            problem[key] for key in ("capacities", "exponentials", "weights", "edges")
        )
        m, sink = len(capacities), n + len(capacities) + 1
        assignment = report["assignment"]
        rewards = {(i, j): Fraction(reward) for i, j, reward in edges}
        self.assertEqual(len(assignment), n)
        counts = tuple(assignment.count(j) for j in range(m))
        self.assertEqual(report["counts"], counts)
        for j, count in enumerate(counts):
            self.assertLessEqual(count, capacities[j])
        for i, j in enumerate(assignment):
            if j is not None:
                self.assertIn((i, j), rewards)
        self.assertEqual(report["objective"],
                         _objective(n, exponentials, weights, rewards, assignment))

        # Reconstruct each original unit arc without importing implementation
        # helpers.  The canonical flow fills each task's first count slots.
        arcs = [(0, i + 1, Fraction(0), 1) for i in range(n)]
        arcs += [(i + 1, n + j + 1, -Fraction(reward), int(assignment[i] == j))
                 for i, j, reward in edges]
        arcs += [(i + 1, sink, Fraction(0), int(assignment[i] is None))
                 for i in range(n)]
        for j, cap in enumerate(capacities):
            e, w = Fraction(exponentials[j]), Fraction(weights[j])
            for k in range(1, cap + 1):
                # Closed-form difference, independent of the optimizer's
                # subtraction of consecutive binary-column scores.
                marginal = w * n * e / ((n + k * (e - 1))
                                         * (n + (k - 1) * (e - 1)))
                arcs.append((n + j + 1, sink, -marginal, int(k <= counts[j])))
        balances = [0] * (sink + 1)
        cost = Fraction(0)
        potentials = report["certificate"]["potentials"]
        self.assertEqual(len(potentials), sink + 1)
        for u, v, arc_cost, flow in arcs:
            balances[u] -= flow
            balances[v] += flow
            cost += arc_cost * flow
            reduced = arc_cost + potentials[u] - potentials[v]
            self.assertGreaterEqual(reduced if flow == 0 else -reduced, 0,
                                    (u, v, arc_cost, flow, reduced))
        self.assertEqual(balances, [-n] + [0] * (n + m) + [n])
        self.assertEqual(cost, -report["objective"])
        self.assertEqual(report["certificate"]["cost"], cost)
        self.assertEqual(report["certificate"]["flowValue"], n)

    def check_exhaustive(self, problem):
        report = maximize_additive_softmax(**problem)
        expected, witnesses = _exhaustive(**problem)
        self.assertEqual(report["objective"], expected, (problem, report, witnesses))
        self.assertIn(report["assignment"], witnesses)
        self.assertEqual(report["optimumScope"], "continuous")
        self.assertEqual(report["allMaximizersBinaryGuaranteed"], problem["n"] >= 2)
        self.assertTrue(verify_additive_softmax_certificate(**problem, report=report))
        self.check_certificate_independently(problem, report)
        return report

    def test_small_profiles_match_exhaustive_assignments(self):
        for n in range(1, 6):
            for m in range(1, 5):
                for profile in range(4):
                    problem = {
                        "n": n,
                        "capacities": tuple((n + j + profile) % (n + 1)
                                            for j in range(m)),
                        "exponentials": tuple(Fraction(2 + j + profile, 1 + j)
                                              for j in range(m)),
                        "weights": tuple(Fraction(1 + (j + profile) % 4, 1 + j)
                                         for j in range(m)),
                        "edges": tuple((i, j, Fraction((5 * i + 3 * j + profile) % 9 - 4,
                                                      1 + (i + j) % 3))
                                       for i in range(n) for j in range(m)
                                       if (i + 2 * j + profile) % 5 != 0),
                    }
                    with self.subTest(n=n, m=m, profile=profile):
                        self.check_exhaustive(problem)

    def test_residual_reverse_arc_reassigns_an_earlier_agent(self):
        # The first augmentation strictly prefers agent 0 to task 0 (path cost
        # -8/3 versus -5/3); the second must reverse that arc to reach 23/6.
        problem = {"n": 2, "capacities": (1, 1), "exponentials": (2, 2),
                   "weights": (1, 1),
                   "edges": ((0, 0, 2), (0, 1, 1), (1, 0, Fraction(3, 2)))}
        report = self.check_exhaustive(problem)
        self.assertEqual(report["assignment"], (1, 0))
        self.assertEqual(report["objective"], Fraction(23, 6))

    def test_abstention_empty_eligibility_and_zero_capacity(self):
        base = {"n": 3, "capacities": (3, 3), "exponentials": (2, 3),
                "weights": (1, 2)}
        for edges, capacities in (((), (3, 3)),
                                  (tuple((i, j, -10) for i in range(3)
                                         for j in range(2)), (3, 3)),
                                  (tuple((i, j, 10) for i in range(3)
                                         for j in range(2)), (0, 0))):
            problem = dict(base, edges=edges, capacities=capacities)
            with self.subTest(edges=edges, capacities=capacities):
                report = self.check_exhaustive(problem)
                self.assertEqual(report["assignment"], (None, None, None))
                self.assertEqual(report["objective"], 0)

    def test_one_agent_guarantee_distinguishes_witness_from_all_maximizers(self):
        problem = {"n": 1, "capacities": (1, 1), "exponentials": (2, 3),
                   "weights": (2, 1), "edges": ((0, 0, -1), (0, 1, 0))}
        report = self.check_exhaustive(problem)
        self.assertEqual(report["objective"], 1)
        self.assertEqual(report["integralityScope"], "optimal-witness")
        self.assertFalse(report["allMaximizersBinaryGuaranteed"])
        # For N=1, each column score is x itself, so this fractional assignment
        # has the same exact value as both integral witnesses.
        self.assertEqual((2 - 1) * Fraction(2, 5) + (1 + 0) * Fraction(3, 5),
                         report["objective"])
        unique = dict(problem, edges=((0, 0, 0), (0, 1, 0)))
        unique_report = self.check_exhaustive(unique)
        self.assertEqual(unique_report["assignment"], (0,))
        self.assertFalse(unique_report["allMaximizersBinaryGuaranteed"])

    def test_exact_half_grid_continuous_values_are_strictly_below_optimum(self):
        row_options = tuple((a, b) for a in range(3) for b in range(3) if a + b <= 2)
        for n in range(2, 5):
            problem = {"n": n, "capacities": ((n + 1) // 2, n - 1),
                       "exponentials": (4, 9), "weights": (Fraction(3, 2), Fraction(2, 3)),
                       "edges": tuple((i, j, Fraction((i + j) % 3 - 1, 3))
                                      for i in range(n) for j in range(2)
                                      if (i, j) != (1, 0))}
            report = self.check_exhaustive(problem)
            rewards = {(i, j): reward for i, j, reward in problem["edges"]}
            fractional_cases = 0
            for rows in product(row_options, repeat=n):
                if any(rows[i][j] and (i, j) not in rewards
                       for i in range(n) for j in range(2)):
                    continue
                if any(sum(row[j] for row in rows) > 2 * cap
                       for j, cap in enumerate(problem["capacities"])):
                    continue
                value = Fraction(0)
                for j, root_e in enumerate((2, 3)):
                    numerator = sum((Fraction(row[j], 2) * root_e ** row[j]
                                     for row in rows), Fraction(0))
                    denominator = sum(root_e ** row[j] for row in rows)
                    value += problem["weights"][j] * numerator / denominator
                value += sum((reward * Fraction(rows[i][j], 2)
                              for (i, j), reward in rewards.items()), Fraction(0))
                self.assertLessEqual(value, report["objective"], (n, rows))
                if any(1 in row for row in rows):
                    fractional_cases += 1
                    self.assertLess(value, report["objective"], (n, rows))
            self.assertGreater(fractional_cases, 0)

    def test_largest_network_and_sixteen_bit_rationals(self):
        e = Fraction(65535, 65534)
        problem = {"n": 24, "capacities": (24,) * 24, "exponentials": (e,) * 24,
                   "weights": (e,) * 24,
                   "edges": tuple((i, j, 0) for i in range(24) for j in range(24))}
        report = maximize_additive_softmax(**problem)
        self.assertEqual(report["counts"], (1,) * 24)
        self.assertEqual(report["objective"], 24 * e * e / (23 + e))
        self.check_certificate_independently(problem, report)
        self.assertTrue(verify_additive_softmax_certificate(**problem, report=report))
        boundary = {"n": 2, "capacities": (2,), "exponentials": (65535,),
                    "weights": (Fraction(1, 65535),),
                    "edges": ((0, 0, 65535), (1, 0, -65535))}
        self.check_exhaustive(boundary)

    def test_equivalent_edge_orders_have_identical_deterministic_reports(self):
        problem = {"n": 3, "capacities": (2, 2), "exponentials": (2, 2),
                   "weights": (1, 1),
                   "edges": tuple((i, j, 0) for i in range(3) for j in range(2))}
        forward = maximize_additive_softmax(**problem)
        reverse = maximize_additive_softmax(**dict(problem, edges=problem["edges"][::-1]))
        self.assertEqual(forward, reverse)

    def test_verifier_rejects_tampered_or_malformed_reports(self):
        problem = {"n": 2, "capacities": (2, 2), "exponentials": (2, 2),
                   "weights": (1, 1),
                   "edges": tuple((i, j, 0) for i in range(2) for j in range(2))}
        original = maximize_additive_softmax(**problem)
        self.assertTrue(verify_additive_softmax_certificate(**problem, report=original))
        changes = (("objective", True), ("objective", 1.0), ("objective", Fraction(0)),
                   ("objective", 1 << 8192), ("assignment", [0, 1]),
                   ("assignment", (True, 1)), ("assignment", (2, 1)),
                   ("counts", (2, 0)), ("counts", (True, 1)),
                   ("allMaximizersBinaryGuaranteed", 1),
                   ("allMaximizersBinaryGuaranteed", False),
                   ("integralityScope", "optimal-witness"),
                   ("optimumScope", "integral"), ("continuousScopeBasis", "unknown"))
        for key, value in changes:
            report = deepcopy(original)
            report[key] = value
            with self.subTest(key=key, value=value):
                self.assertFalse(verify_additive_softmax_certificate(**problem, report=report))
        certificate_changes = (("potentials", (0,) * 6), ("potentials", (0,) * 5),
                               ("potentials", [0] * 6), ("potentials", (True,) * 6),
                               ("potentials", (1 << 8192,) * 6),
                               ("flowValue", True), ("flowValue", 1),
                               ("cost", 0), ("kind", "unknown"))
        for key, value in certificate_changes:
            report = deepcopy(original)
            report["certificate"][key] = value
            with self.subTest(certificate_key=key, value=value):
                self.assertFalse(verify_additive_softmax_certificate(**problem, report=report))
        suboptimal = deepcopy(original)
        suboptimal.update(assignment=(None, None), counts=(0, 0), objective=Fraction(0))
        suboptimal["certificate"]["cost"] = Fraction(0)
        self.assertFalse(verify_additive_softmax_certificate(**problem, report=suboptimal))
        for malformed in (None, [], {}, dict(original, extra=0),
                          dict(original, certificate=None),
                          dict(original, certificate=dict(original["certificate"], extra=0))):
            self.assertFalse(verify_additive_softmax_certificate(**problem, report=malformed))

    def test_input_admission_rejects_inexact_unbounded_and_malformed_values(self):
        base = {"n": 2, "capacities": (2,), "exponentials": (2,), "weights": (1,),
                "edges": ((0, 0, 0), (1, 0, 0))}
        invalid = (
            ("n", True, TypeError), ("n", 2.0, TypeError),
            ("n", 0, ValueError), ("n", 25, ValueError),
            ("capacities", [2], TypeError), ("capacities", (), ValueError),
            ("capacities", (2,) * 25, ValueError), ("capacities", (True,), TypeError),
            ("capacities", (-1,), ValueError), ("capacities", (3,), ValueError),
            ("exponentials", [2], TypeError), ("exponentials", (), ValueError),
            ("exponentials", (1,), ValueError), ("exponentials", (-2,), ValueError),
            ("exponentials", (True,), TypeError), ("exponentials", (2.0,), TypeError),
            ("exponentials", (65536,), ValueError),
            ("exponentials", (Fraction(65537, 65536),), ValueError),
            ("weights", (0,), ValueError), ("weights", (-1,), ValueError),
            ("weights", (True,), TypeError), ("weights", (1.0,), TypeError),
            ("weights", (Fraction(1, 65536),), ValueError),
            ("weights", (1, 1), ValueError), ("edges", [], TypeError),
            ("edges", ((0, 0, 0),) * 3, ValueError),
            ("edges", ([0, 0, 0],), TypeError),
            ("edges", ((0, 0),), ValueError),
            ("edges", ((True, 0, 0),), TypeError),
            ("edges", ((0, True, 0),), TypeError),
            ("edges", ((-1, 0, 0),), ValueError),
            ("edges", ((2, 0, 0),), ValueError),
            ("edges", ((0, 1, 0),), ValueError),
            ("edges", ((0, 0, 0), (0, 0, 1)), ValueError),
            ("edges", ((0, 0, True),), TypeError),
            ("edges", ((0, 0, 0.5),), TypeError),
            ("edges", ((0, 0, "1/2"),), TypeError),
            ("edges", ((0, 0, -65536),), ValueError),
        )
        for key, value, error in invalid:
            problem = dict(base, **{key: value})
            with self.subTest(key=key, value=value):
                with self.assertRaises(error):
                    maximize_additive_softmax(**problem)
                with self.assertRaises(error):
                    verify_additive_softmax_certificate(**problem, report={})


if __name__ == "__main__":
    unittest.main()
