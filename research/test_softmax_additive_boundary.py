"""Independent finite checks for the zero-outer-temperature theorem.

The oracle uses Decimal arithmetic and does not import the certified solver or
its interval helpers.  These checks support the analytic price/envelope proof;
they do not replace it.
"""

from decimal import Decimal, localcontext
from itertools import product
import unittest


def _scores(n: int, t: Decimal) -> tuple[Decimal, ...]:
    """Return the binary-column values s_0,...,s_n."""
    e = t.exp()
    return tuple(
        Decimal(k) * e / (Decimal(k) * e + Decimal(n - k))
        if k else Decimal(0)
        for k in range(n + 1)
    )


def _column_score(x: tuple[Decimal, ...],
                  weights: dict[Decimal, Decimal]) -> Decimal:
    numerator = sum((value * weights[value] for value in x), Decimal(0))
    denominator = sum((weights[value] for value in x), Decimal(0))
    return numerator / denominator


def _envelope(mass: Decimal, values: tuple[Decimal, ...]) -> Decimal:
    n = len(values) - 1
    if mass == Decimal(n):
        return values[n]
    k = int(mass)
    remainder = mass - Decimal(k)
    return values[k] + remainder * (values[k + 1] - values[k])


def _partitions(total: int, largest: int | None = None):
    if total == 0:
        yield ()
        return
    if largest is None:
        largest = total
    for first in range(min(total, largest), 0, -1):
        for suffix in _partitions(total - first, first):
            yield (first,) + suffix


class AdditiveBoundaryTests(unittest.TestCase):
    def test_binary_values_have_strictly_decreasing_slopes(self):
        with localcontext() as context:
            context.prec = 90
            for n in range(2, 13):
                for raw_t in ("0.01", "0.1", "1", "3", "8", "32"):
                    values = _scores(n, Decimal(raw_t))
                    slopes = tuple(values[k + 1] - values[k] for k in range(n))
                    for left, right in zip(slopes, slopes[1:]):
                        self.assertGreater(left, right,
                                           (n, raw_t, left, right))

    def test_pointwise_envelope_on_deterministic_fractional_grid(self):
        # The grid is small enough to be exhaustive through dimension five,
        # while covering both nearly linear and highly concentrated regimes.
        with localcontext() as context:
            context.prec = 90
            grid = tuple(Decimal(k) / Decimal(10) for k in range(11))
            for n in range(2, 6):
                for raw_t in ("0.1", "1", "3", "8"):
                    t = Decimal(raw_t)
                    values = _scores(n, t)
                    weights = {value: (t * value).exp() for value in grid}
                    for point in product(grid, repeat=n):
                        mass = sum(point, Decimal(0))
                        score = _column_score(point, weights)
                        upper = _envelope(mass, values)
                        self.assertLessEqual(score, upper,
                                             (n, raw_t, point, score, upper))
                        if any(value not in (Decimal(0), Decimal(1))
                               for value in point):
                            self.assertLess(score, upper,
                                            (n, raw_t, point, score, upper))

    def test_balanced_integer_occupancies_are_the_additive_optimum(self):
        with localcontext() as context:
            context.prec = 90
            for n in range(2, 13):
                for m in range(1, 8):
                    q, remainder = divmod(n, m)
                    expected = tuple(sorted(
                        (q + 1,) * remainder + (q,) * (m - remainder),
                        reverse=True,
                    ))
                    expected = tuple(size for size in expected if size > 0)
                    for raw_t in ("0.1", "1", "8"):
                        values = _scores(n, Decimal(raw_t))
                        expected_value = sum(
                            (values[size] for size in expected), Decimal(0)
                        ) / Decimal(m)
                        best = None
                        best_groups = []
                        for groups in _partitions(n):
                            if len(groups) > m:
                                continue
                            value = sum(
                                (values[size] for size in groups), Decimal(0)
                            ) / Decimal(m)
                            if best is None or value > best:
                                best, best_groups = value, [groups]
                            elif value == best:
                                best_groups.append(groups)
                        self.assertEqual(best_groups, [expected],
                                         (n, m, raw_t, best_groups))
                        self.assertEqual(best, expected_value,
                                         (n, m, raw_t, best, expected_value))

    def test_one_agent_has_fractional_full_budget_ties(self):
        with localcontext() as context:
            context.prec = 90
            for allocation in (("1", "0", "0"), ("0.2", "0.3", "0.5"),
                               ("0.2", "0.3", "0")):
                row = tuple(map(Decimal, allocation))
                for raw_t in ("0.01", "1", "32"):
                    t = Decimal(raw_t)
                    weights = {value: (t * value).exp() for value in row}
                    reward = sum((_column_score((value,), weights) for value in row),
                                 Decimal(0)) / Decimal(len(row))
                    expected = sum(row, Decimal(0)) / Decimal(len(row))
                    self.assertLess(abs(reward - expected), Decimal("1e-85"))
                    if sum(row, Decimal(0)) < 1:
                        self.assertLess(reward, Decimal(1) / Decimal(len(row)))

    def test_zero_inner_temperature_returns_linear_budget_value(self):
        with localcontext() as context:
            context.prec = 90
            # A genuinely rectangular fixture distinguishes 1/M from 1/N.
            for raw_matrix in ((("1", "0", "0"), ("0", "1", "0")),
                               (("0.2", "0.3", "0.5"), ("0.4", "0.1", "0.5")),
                               (("0.2", "0.3", "0"), ("0.4", "0.1", "0"))):
                matrix = tuple(tuple(map(Decimal, row)) for row in raw_matrix)
                weights = {value: Decimal(1) for row in matrix for value in row}
                reward = sum((_column_score(column, weights)
                              for column in zip(*matrix)), Decimal(0)) / Decimal(3)
                total = sum((sum(row, Decimal(0)) for row in matrix), Decimal(0))
                self.assertEqual(reward, total / Decimal(6))


if __name__ == "__main__":
    unittest.main()
