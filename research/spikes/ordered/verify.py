"""Independent exact checks; no frugal pilot panels or model calls are read."""
from fractions import Fraction
from itertools import combinations
from random import Random

from research.survivor_order import pair_inclusion_probabilities


def algebra_checks():
    rng = Random(1)
    count = 0
    for kind in (0, 1):
        terms = ([(0, 1, 1), (2, 3, 1), (0, 2, -1), (1, 3, -1)]
                 if kind == 0 else
                 [(0, 2, 1), (1, 3, 1), (0, 3, -1), (1, 2, -1)])
        i, j, k, l = ((0, 3, 1, 2) if kind == 0 else (0, 1, 2, 3))
        for _ in range(100):
            f = [Fraction(rng.randrange(1, 30), rng.randrange(1, 10)) for _ in range(4)]
            g = [Fraction(rng.randrange(1, 30), rng.randrange(1, 10)) for _ in range(4)]
            derivative = [-g[x] * (1 + f[x]) for x in range(4)]
            pair_term = lambda a, b: g[a] * f[b] + f[a] * g[b]
            t0 = sum(sign * pair_term(a, b) for a, b, sign in terms)
            t1 = sum(sign * pair_term(a, b) *
                     sum(f[x] for x in range(4) if x not in (a, b))
                     for a, b, sign in terms)
            t2 = sum(sign * pair_term(a, b) *
                     f[next(x for x in range(4) if x not in (a, b))] *
                     f[next(x for x in reversed(range(4)) if x not in (a, b))]
                     for a, b, sign in terms)
            F = (f[i] - f[j]) * (f[k] - f[l])
            Fprime = ((derivative[i] - derivative[j]) * (f[k] - f[l]) +
                      (f[i] - f[j]) * (derivative[k] - derivative[l]))
            assert t2 == 0
            assert t0 + t1 == -Fprime - sum(g) * F
            count += 1
    return count


def probability_checks():
    rng = Random(9023)
    checked = strict = boundary = 0
    for n in range(4, 10):
        for _ in range(20):
            weights = sorted(rng.randrange(1, 13) for _ in range(n))
            for survivors in range(2, n + 1):
                q = pair_inclusion_probabilities(weights, survivors)
                for a, b, c, d in combinations(range(n), 4):
                    adjacent = q[a, b] + q[c, d]
                    crossing = q[a, c] + q[b, d]
                    nested = q[a, d] + q[b, c]
                    assert adjacent >= crossing >= nested
                    checked += 1
                    if weights[a] < weights[b] < weights[c] < weights[d] and survivors <= n - 2:
                        assert adjacent > crossing > nested
                        strict += 1
                    if survivors >= n - 1:
                        assert adjacent == crossing == nested
                        boundary += 1
    return checked, strict, boundary


if __name__ == "__main__":
    print("algebra_substitutions", algebra_checks())
    print("probability_cases_strict_boundary", *probability_checks())
