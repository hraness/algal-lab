"""Independent exact checks for the rank-selection four-point identity.

Histograms encode independent clocks that are uniform within common unit bins.
The CDF-integral verifier below is separate from rank_selection.pair_probabilities:
it integrates the claimed C,D,H formula directly with rational polynomials, then
cross-checks it against that pair-probability oracle.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations


def _rows(value: object) -> list[list[Fraction]]:
    if type(value) is not list or not 4 <= len(value) <= 9:
        raise ValueError("expected 4..9 histogram rows")
    bins = len(value[0]) if type(value[0]) is list else 0
    if not 1 <= bins <= 6:
        raise ValueError("expected 1..6 unit bins")
    result: list[list[Fraction]] = []
    for row in value:
        if (type(row) is not list or len(row) != bins
                or any(type(x) is not int or not 0 <= x <= 64 for x in row)
                or sum(row) == 0):
            raise ValueError("rows need equal lengths and positive integer masses in 0..64")
        total = sum(row)
        result.append([Fraction(x, total) for x in row])
    return result


def _add(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * max(len(a), len(b))
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    return out


def _neg(a: list[Fraction]) -> list[Fraction]:
    return [-x for x in a]


def _sub(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    return _add(a, _neg(b))


def _scale(a: list[Fraction], c: Fraction) -> list[Fraction]:
    return [c * x for x in a]


def _mul(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _constant(x: Fraction | int) -> list[Fraction]:
    return [Fraction(x)]


def _unit_integral(poly: list[Fraction]) -> Fraction:
    return sum((coef / (degree + 1) for degree, coef in enumerate(poly)), Fraction(0))


def _exact_exceedance_polynomials(cdfs: list[list[Fraction]]) -> list[list[Fraction]]:
    """Return H_j(x): probability exactly j clocks exceed x in this bin."""
    counts = [_constant(1)]
    for cdf in cdfs:
        survival = _sub(_constant(1), cdf)
        updated = [_constant(0) for _ in range(len(counts) + 1)]
        for j, probability in enumerate(counts):
            updated[j] = _add(updated[j], _mul(probability, cdf))
            updated[j + 1] = _add(updated[j + 1], _mul(probability, survival))
        counts = updated
    return counts


def _exact_count(cdfs: list[list[Fraction]], count: int) -> list[Fraction]:
    if count < 0 or count >= len(cdfs) + 1:
        return _constant(0)
    return _exact_exceedance_polynomials(cdfs)[count]


def cdf_gap_integral(
    histograms: object,
    survivors: int,
    quartet: tuple[int, int, int, int],
    gap: int,
) -> Fraction:
    """Integrate one claimed four-point gap using C,D and exact H counts.

    gap=1 means q_ab+q_cd-q_ac-q_bd; gap=2 means
    q_ac+q_bd-q_ad-q_bc. The quartet order is caller supplied.
    """
    rows = _rows(histograms)
    n = len(rows)
    if type(survivors) is not int or not 0 <= survivors <= n:
        raise ValueError("survivors must be in 0..n")
    if (type(quartet) is not tuple or len(quartet) != 4
            or any(type(i) is not int or not 0 <= i < n for i in quartet)
            or len(set(quartet)) != 4):
        raise ValueError("quartet must contain four distinct valid labels")
    if type(gap) is not int or gap not in (1, 2):
        raise ValueError("gap must be 1 or 2")
    if survivors < 2:
        return Fraction(0)

    a, b, c, d = quartet
    m = survivors - 2
    rest = [i for i in range(n) if i not in quartet]
    before = [Fraction(0)] * n
    total = Fraction(0)

    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        cdfs = [[before[i], density[i]] for i in range(n)]
        fa, fb, fc, fd = (cdfs[i] for i in quartet)
        if gap == 2:
            dpoly = _mul(_sub(fb, fa), _sub(fd, fc))
            cpoly = _add(
                _mul(_sub(_scale(fb, density[a]), _scale(fa, density[b])), _sub(fd, fc)),
                _mul(_sub(fb, fa), _sub(_scale(fd, density[c]), _scale(fc, density[d]))),
            )
        else:
            dpoly = _mul(_sub(fd, fa), _sub(fc, fb))
            cpoly = _add(
                _mul(_sub(_scale(fd, density[a]), _scale(fa, density[d])), _sub(fc, fb)),
                _mul(_sub(fd, fa), _sub(_scale(fc, density[b]), _scale(fb, density[c]))),
            )

        h_m = _exact_count([cdfs[i] for i in rest], m)
        integrand = _mul(cpoly, h_m)
        for r in rest:
            h_previous = _exact_count([cdfs[i] for i in rest if i != r], m - 1)
            integrand = _add(integrand, _scale(_mul(dpoly, h_previous), density[r]))
        total += _unit_integral(integrand)
        before = [before[i] + density[i] for i in range(n)]
    return total


def _cdf_ordered(rows: list[list[Fraction]]) -> bool:
    before = [Fraction(0)] * len(rows)
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        after = [before[i] + density[i] for i in range(len(rows))]
        if any(before[i] > before[i + 1] or after[i] > after[i + 1]
               for i in range(len(rows) - 1)):
            return False
        before = after
    return True


def _reverse_hazard_ordered(rows: list[list[Fraction]]) -> bool:
    before = [Fraction(0)] * len(rows)
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        for i in range(len(rows) - 1):
            if density[i] * before[i + 1] < density[i + 1] * before[i]:
                return False
        before = [before[i] + density[i] for i in range(len(rows))]
    return True


def _has_strict_pairwise_order(rows: list[list[Fraction]]) -> bool:
    """Each adjacent CDF and reverse-hazard comparison is strict somewhere."""
    if not (_cdf_ordered(rows) and _reverse_hazard_ordered(rows)):
        return False
    before = [Fraction(0)] * 4
    cdf_strict = [False] * 3
    hazard_strict = [False] * 3
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        for i in range(3):
            midpoint_i = before[i] + density[i] / 2
            midpoint_j = before[i + 1] + density[i + 1] / 2
            cdf_strict[i] |= midpoint_i < midpoint_j
            hazard_strict[i] |= density[i] * before[i + 1] > density[i + 1] * before[i]
        before = [before[i] + density[i] for i in range(4)]
    return all(cdf_strict) and all(hazard_strict)


def check_identity_profiles() -> dict[str, int]:
    from research.rank_selection import ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE, pair_probabilities

    extra_rows = [[5, 2, 7], [1, 6, 9], [4, 5, 3]]
    profiles: list[tuple[str, list[list[int]]]] = []
    for n in range(4, 8):
        profiles.append((f"ordered-{n}", ORDERED_EXAMPLE + extra_rows[:n - 4]))
        profiles.append((f"cdf-only-{n}", STOCHASTIC_ONLY_EXAMPLE + extra_rows[:n - 4]))

    identity_checks = 0
    ordered_checks = 0
    strict_checks = 0
    for name, histogram in profiles:
        rows = _rows(histogram)
        n = len(rows)
        quartet_conditions = rows[:4]
        if name.startswith("ordered-"):
            assert _cdf_ordered(quartet_conditions) and _reverse_hazard_ordered(quartet_conditions)
        else:
            assert _cdf_ordered(quartet_conditions) and not _reverse_hazard_ordered(quartet_conditions)
        quartet_sets = list(combinations(range(n), 4))
        for k in range(n + 1):
            q = pair_probabilities(histogram, k)
            for quartet in quartet_sets:
                a, b, c, d = quartet
                first = q[a, b] + q[c, d] - q[a, c] - q[b, d]
                second = q[a, c] + q[b, d] - q[a, d] - q[b, c]
                integrated_first = cdf_gap_integral(histogram, k, quartet, 1)
                integrated_second = cdf_gap_integral(histogram, k, quartet, 2)
                assert integrated_first == first, (name, k, quartet, "first", first, integrated_first)
                assert integrated_second == second, (name, k, quartet, "second", second, integrated_second)
                identity_checks += 2

                selected = [rows[i] for i in quartet]
                if _cdf_ordered(selected) and _reverse_hazard_ordered(selected):
                    assert first >= 0 and second >= 0, (name, k, quartet, first, second)
                    ordered_checks += 2
                # This named profile has strict quartet order and positive
                # mass in every bin for all appended R clocks, so overlap and
                # every required exact R-count event hold on an open interval.
                if (name.startswith("ordered-") and quartet == (0, 1, 2, 3)
                        and 2 <= k <= n - 2):
                    assert _has_strict_pairwise_order(selected)
                    assert first > 0 and second > 0, (name, k, quartet, first, second)
                    strict_checks += 2
    return {
        "profiles": len(profiles),
        "identityGapChecks": identity_checks,
        "orderedWeakGapChecks": ordered_checks,
        "strictGapChecks": strict_checks,
    }


def check_strictness_counterexample() -> dict[str, Fraction]:
    from research.rank_selection import pair_probabilities

    # The four strict-order clocks end at 3. The fifth clock begins at 3,
    # so for k=2 it is always a survivor and no quartet pair can survive.
    quartet = [[1, 3, 12, 0, 0, 0], [2, 6, 8, 0, 0, 0],
               [4, 8, 4, 0, 0, 0], [8, 6, 2, 0, 0, 0]]
    q = pair_probabilities(quartet + [[0, 0, 0, 1, 1, 1]], 2)
    assert all(q[pair] == 0 for pair in combinations(range(4), 2))
    assert _has_strict_pairwise_order(_rows(quartet))
    return {"allQuartetPairsAtK2": Fraction(0), "pairCount": 6}


def check_fosd_countermodel() -> dict[str, object]:
    from research.rank_selection import pair_probabilities

    rows = [[0, 1, 2], [1, 0, 2], [2, 0, 1], [2, 1, 0]]
    mixed = [[9 * count + 1 for count in row] for row in rows]
    for profile in (rows, mixed):
        assert _cdf_ordered(_rows(profile))
    assert not _reverse_hazard_ordered(_rows(rows))
    base = pair_probabilities(rows, 2)
    mixture = pair_probabilities(mixed, 2)
    base_gaps = (base[0, 1] + base[2, 3] - base[0, 2] - base[1, 3],
                 base[0, 2] + base[1, 3] - base[0, 3] - base[1, 2])
    mix_gaps = (mixture[0, 1] + mixture[2, 3] - mixture[0, 2] - mixture[1, 3],
                mixture[0, 2] + mixture[1, 3] - mixture[0, 3] - mixture[1, 2])
    assert base_gaps == (Fraction(8, 27), Fraction(-1, 54))
    assert mix_gaps == (Fraction(123, 500), Fraction(-3, 250))
    return {
        "basePairProbabilities": base,
        "baseGaps": base_gaps,
        "positiveUniformMixtureCounts": mixed,
        "mixturePairProbabilities": mixture,
        "mixtureGaps": mix_gaps,
    }


def check_ai_countermodel() -> dict[str, int | Fraction]:
    """Dependent AI law satisfying every improving same-size subset swap.

    This refutes inference from those conclusions alone, not a theorem with
    additional independence or conditional joint-order premises.
    """
    labels = range(4)
    subset_probability = {
        pair: (Fraction(1, 11) if pair == (2, 3) else Fraction(2, 11))
        for pair in combinations(labels, 2)
    }

    common_endpoint_checks = 0
    for fixed in labels:
        others = [j for j in labels if j != fixed]
        for better, worse in combinations(others, 2):
            assert subset_probability[tuple(sorted((fixed, better)))] >= subset_probability[
                tuple(sorted((fixed, worse)))]
            common_endpoint_checks += 1

    adjacent = subset_probability[(0, 1)] + subset_probability[(2, 3)]
    crossing = subset_probability[(0, 2)] + subset_probability[(1, 3)]
    nested = subset_probability[(0, 3)] + subset_probability[(1, 2)]
    assert adjacent == Fraction(3, 11) and crossing == Fraction(4, 11)
    assert adjacent < crossing

    def order_probability(order: tuple[int, ...]) -> Fraction:
        top = tuple(sorted(order[:2]))
        return subset_probability[top] / 4

    orders = list(permutations(labels))
    assert sum((order_probability(order) for order in orders), Fraction(0)) == 1
    subset_swaps = marginal_comparisons = 0
    for size in range(1, 4):
        law = {subset: Fraction(0) for subset in combinations(labels, size)}
        for order in orders:
            law[tuple(sorted(order[:size]))] += order_probability(order)
        assert sum(law.values(), Fraction(0)) == 1
        for better, worse in combinations(labels, 2):
            remaining = [label for label in labels if label not in (better, worse)]
            for common in combinations(remaining, size - 1):
                assert law[tuple(sorted((*common, better)))] >= law[
                    tuple(sorted((*common, worse)))]
                subset_swaps += 1
            assert sum(p for subset, p in law.items() if better in subset) >= sum(
                p for subset, p in law.items() if worse in subset)
            marginal_comparisons += 1
        if size == 2:
            assert law == subset_probability
    assert subset_swaps == 24 and marginal_comparisons == 18
    transpositions = 0
    for order in orders:
        for r, s in combinations(range(4), 2):
            if order[r] > order[s]:
                improved = list(order)
                improved[r], improved[s] = improved[s], improved[r]
                assert order_probability(tuple(improved)) >= order_probability(order)
                transpositions += 1
    assert sum(subset_probability.values(), Fraction(0)) == 1
    return {
        "commonEndpointChecks": common_endpoint_checks,
        "sameSizeSubsetSwaps": subset_swaps,
        "marginalComparisons": marginal_comparisons,
        "orders": len(orders),
        "transpositions": transpositions,
        "adjacent": adjacent,
        "crossing": crossing,
        "nested": nested,
    }


def main() -> None:
    identities = check_identity_profiles()
    strictness = check_strictness_counterexample()
    fosd = check_fosd_countermodel()
    ai = check_ai_countermodel()
    print("exact CDF-gap identities:", identities)
    print("strictness counterexample:", strictness)
    print("FOSD-only countermodel:", fosd)
    print("AI countermodel:", ai)


if __name__ == "__main__":
    main()
