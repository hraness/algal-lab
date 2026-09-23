"""Fixed exact checks for intact groups from two common mixture bases.

The bases may have crossing CDFs.  A symbolic derivative identity and exact
histogram integrals check the nonnegative squared-CDF kernel.  An independent
categorical selection oracle then checks all three quartet factorizations,
including exact outside selection patterns, and every triple partition of
nine clocks at every horizon.  The oracle is independent of the structural
optimizer and of the quartet integral calculation.

The sixteen binary mixture corners determine each multiaffine quartet gap;
three interior profiles are also recomputed directly.  The nine-clock fixture
has positive masses in three common bins and every pair of its CDFs crosses.
Uniform sampling within each bin makes the cutoff subset uniform.  The same
oracle also describes atomic bins with global iid continuous tie keys; it
does not describe arbitrary fixed label priority.

All fixtures and bounds are fixed here.  There are no external inputs or
optional dependencies.  These checks support the separate mathematical
proof; finite enumeration alone is not a general optimality theorem.
"""
from fractions import Fraction
from itertools import combinations, product

from research.spikes.stochastic.tails import (
    _mask,
    _partitions,
    _selection_laws,
    _tails,
)


_G = (2, 1, 2)
_H = (1, 3, 1)
_TOTAL = 5
_Polynomial = dict[tuple[int, int, int, int], Fraction]


def _add(*polynomials: _Polynomial) -> _Polynomial:
    result: _Polynomial = {}
    for polynomial in polynomials:
        for powers, coefficient in polynomial.items():
            result[powers] = result.get(powers, Fraction(0)) + coefficient
    return {powers: coefficient for powers, coefficient in result.items()
            if coefficient}


def _scale(polynomial: _Polynomial, factor: Fraction) -> _Polynomial:
    return {powers: coefficient * factor for powers, coefficient in polynomial.items()
            if coefficient * factor}


def _multiply(left: _Polynomial, right: _Polynomial) -> _Polynomial:
    terms: list[_Polynomial] = []
    for a, first in left.items():
        for b, second in right.items():
            powers = tuple(a[i] + b[i] for i in range(4))
            terms.append({powers: first * second})
    return _add(*terms)


def _derivative(polynomial: _Polynomial) -> _Polynomial:
    """Differentiate in time with the four symbols S, Delta, S', Delta'."""
    terms: list[_Polynomial] = []
    for powers, coefficient in polynomial.items():
        for variable in (0, 1):
            if powers[variable]:
                changed = list(powers)
                changed[variable] -= 1
                changed[variable + 2] += 1
                terms.append({tuple(changed): coefficient * powers[variable]})
    return _add(*terms)


def _symbolic_identity() -> int:
    s, delta, ds, dd = ({tuple(int(i == j) for i in range(4)): Fraction(1)}
                        for j in range(4))
    g = _add(s, _scale(delta, Fraction(1, 2)))
    h = _add(s, _scale(delta, Fraction(-1, 2)))
    dg = _add(ds, _scale(dd, Fraction(1, 2)))
    dh = _add(ds, _scale(dd, Fraction(-1, 2)))
    difference = _add(g, _scale(h, Fraction(-1)))
    square = _multiply(delta, delta)
    assert _multiply(difference, difference) == square
    cross = _add(_multiply(dh, g), _scale(_multiply(dg, h), Fraction(-1)))
    original = _scale(_multiply(cross, delta), Fraction(2))
    positive_derivative = _add(
        _scale(_multiply(ds, square), Fraction(3)),
        _scale(_derivative(_multiply(s, square)), Fraction(-1)),
    )
    assert original == positive_derivative
    return 2


def _cdf(row: tuple[int, ...], value: Fraction) -> Fraction:
    interval = min(int(value), 2)
    return (Fraction(sum(row[:interval]), _TOTAL)
            + Fraction(row[interval], _TOTAL) * (value - interval))


def _threshold_checks() -> dict[str, int | str]:
    points = tuple(Fraction(i, 2) for i in range(7))
    cases = positive = 0
    for lower_index, lower in enumerate(points):
        for upper in points[lower_index:]:
            delta_lower = _cdf(_G, lower) - _cdf(_H, lower)
            delta_upper = _cdf(_G, upper) - _cdf(_H, upper)
            s_lower = (_cdf(_G, lower) + _cdf(_H, lower)) / 2
            s_upper = (_cdf(_G, upper) + _cdf(_H, upper)) / 2
            original_integral = square_integral = Fraction(0)
            for interval in range(3):
                left = max(lower, Fraction(interval)) - interval
                right = min(upper, Fraction(interval + 1)) - interval
                if left >= right:
                    continue
                g0 = Fraction(sum(_G[:interval]), _TOTAL)
                h0 = Fraction(sum(_H[:interval]), _TOTAL)
                dg = Fraction(_G[interval], _TOTAL)
                dh = Fraction(_H[interval], _TOTAL)
                delta0, delta_slope = g0 - h0, dg - dh
                original_integral += 2 * (dh * g0 - dg * h0) * (
                    delta0 * (right - left)
                    + delta_slope * (right ** 2 - left ** 2) / 2)
                square_integral += (dg + dh) / 2 * (
                    delta0 ** 2 * (right - left)
                    + delta0 * delta_slope * (right ** 2 - left ** 2)
                    + delta_slope ** 2 * (right ** 3 - left ** 3) / 3)
            direct = delta_upper ** 2 + original_integral
            positive_formula = ((1 - s_upper) * delta_upper ** 2
                                + s_lower * delta_lower ** 2
                                + 3 * square_integral)
            assert direct == positive_formula and direct >= 0
            if lower == 0 and upper == 3:
                assert direct == Fraction(1, 25)
            cases += 1
            positive += direct > 0
    return {"mixtureThresholdWindows": cases, "mixturePositiveWindows": positive,
            "mixtureCrossingKernel": "1/25"}


def _mixture_row(parameter: Fraction) -> tuple[int, ...]:
    masses = tuple(8 * ((1 - parameter) * g + parameter * h)
                   for g, h in zip(_G, _H))
    assert all(mass.denominator == 1 and mass > 0 for mass in masses)
    return tuple(int(mass) for mass in masses)


def _gap_table(rows: tuple[tuple[int, ...], ...]
               ) -> tuple[dict[tuple[int, int], tuple[Fraction, ...]], int, int]:
    population = len(rows)
    laws, denominator, assignments, outcomes = _selection_laws(
        rows, tuple(range(population + 1)))
    patterns = tuple(pattern << 4 for pattern in range(1 << (population - 4)))
    result = {}
    for horizon, law in laws.items():
        for pattern in patterns:
            numerators = [0, 0, 0]
            for selected, weight in law.items():
                if selected & ~15 != pattern:
                    continue
                a, b, c, d = (int(bool(selected & (1 << label))) for label in range(4))
                # Adjacent-crossing, crossing-nested, adjacent-nested.
                contrasts = ((a - d) * (b - c), (a - b) * (c - d),
                             (a - c) * (b - d))
                for index, contrast in enumerate(contrasts):
                    numerators[index] += weight * contrast
            result[horizon, pattern] = tuple(Fraction(value, denominator)
                                             for value in numerators)
    return result, assignments, outcomes


def _quartet_checks() -> dict[str, int]:
    corners = tuple(product((Fraction(0), Fraction(1)), repeat=4))
    interior = ((Fraction(0), Fraction(1, 4), Fraction(3, 4), Fraction(1)),
                (Fraction(1, 2), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)),
                (Fraction(3, 4), Fraction(1, 4), Fraction(1), Fraction(0)))
    cases = kernels = positive = profiles = assignments = outcomes = 0
    # The outside histograms are arbitrary positive laws, not mixture rows.
    for outside in ((), ((5, 10, 25), (15, 20, 5))):
        tables = {}
        for parameters in (*corners, *interior):
            rows = tuple(_mixture_row(p) for p in parameters) + outside
            table, assignment_count, outcome_count = _gap_table(rows)
            tables[parameters] = table
            assignments += assignment_count
            outcomes += outcome_count
            profiles += 1
        reference = tables[(Fraction(1), Fraction(1), Fraction(0), Fraction(0))]
        for key, gaps in reference.items():
            kernel = gaps[0]
            assert kernel >= 0
            if not outside and key == (2, 0):
                assert kernel == Fraction(1, 25)
            kernels += 1
            positive += kernel > 0
            for parameters, table in tables.items():
                a, b, c, d = parameters
                factors = ((a - d) * (b - c), (a - b) * (c - d),
                           (a - c) * (b - d))
                for gap, factor in zip(table[key], factors):
                    assert gap == kernel * factor, (outside, key, parameters, gap, factor)
                    cases += 1
    assert profiles == 38 and cases == 1881 and assignments == 15390
    return {"mixtureQuartetProfiles": profiles, "mixtureGapFactorizations": cases,
            "mixtureOutsideKernels": kernels, "mixturePositiveOutsideKernels": positive,
            "mixtureQuartetAssignments": assignments,
            "mixtureQuartetCutoffOutcomes": outcomes}


def _triple_checks() -> dict[str, int | tuple[str, ...]]:
    rows = tuple((16 - i, 8 + 2 * i, 16 - i) for i in range(9))
    for i, row in enumerate(rows):
        assert row == _mixture_row(Fraction(i, 8)) and sum(row) == 40
    crossings = 0
    for left, right in combinations(rows, 2):
        # Endpoint one decreases in p; endpoint two increases. Every pair
        # crosses, so there is no CDF chain or separated multi-group cut.
        assert left[0] > right[0] and sum(left[:2]) < sum(right[:2])
        crossings += 1
    target = tuple(_mask(range(first, first + 3)) for first in range(0, 9, 3))
    interleaved = tuple(_mask(range(first, 9, 3)) for first in range(3))
    candidates = tuple(_partitions(tuple(range(9)), 3))
    assert len(candidates) == len(set(candidates)) == 280
    laws, denominator, assignments, outcomes = _selection_laws(rows, tuple(range(10)))
    cases = strict = 0
    illustration: dict[str, int | tuple[str, ...]] = {}
    for horizon, law in laws.items():
        optimum = (denominator, *_tails(law, target), 0)
        for groups in candidates:
            actual = (denominator, *_tails(law, groups), 0)
            for threshold, (best, other) in enumerate(zip(optimum, actual)):
                assert best >= other, (horizon, threshold, groups, best, other)
                cases += 1
                strict += best > other
        if horizon == 6:
            illustration["mixtureTripleK6ConsecutiveTails"] = tuple(
                str(Fraction(value, denominator)) for value in optimum[1:3])
            illustration["mixtureTripleK6InterleavedTails"] = tuple(
                str(Fraction(value, denominator)) for value in _tails(law, interleaved)[:2])
    assert cases == 14000 and crossings == 36 and assignments == 19683
    return {"mixtureCrossingCdfPairs": crossings, "mixtureTriplePartitions": len(candidates),
            "mixtureTripleHorizons": len(laws), "mixtureTripleTailComparisons": cases,
            "mixtureStrictTripleTailComparisons": strict,
            "mixtureTripleAssignments": assignments, "mixtureTripleCutoffOutcomes": outcomes,
            **illustration}


def verify() -> dict[str, int | str | tuple[str, ...]]:
    """Run bounded exact algebra, integral, quartet, and grouping checks."""
    result: dict[str, int | str | tuple[str, ...]] = {
        "mixturePolynomialIdentities": _symbolic_identity()}
    result.update(_threshold_checks())
    result.update(_quartet_checks())
    result.update(_triple_checks())
    return result


if __name__ == "__main__":
    print("common mixture groups:", verify())
