"""Exact finite checks for hazard reversal among uniform exponential mixtures.

This verifier checks a parent-supplied example and its mapping to the published
majorization framework. It uses rational q=e^-t values, exact polynomial
arithmetic, and no external inputs or optional dependencies. Finite checks
support the separate theorem mapping; they do not establish that theorem.
"""
from fractions import Fraction


_Poly = dict[tuple[int, int], Fraction]  # powers of (m, q)


def _add(*polys: _Poly) -> _Poly:
    result: _Poly = {}
    for poly in polys:
        for powers, coefficient in poly.items():
            result[powers] = result.get(powers, Fraction(0)) + coefficient
    return {powers: coefficient for powers, coefficient in result.items()
            if coefficient}


def _scale(poly: _Poly, factor: Fraction | int) -> _Poly:
    factor = Fraction(factor)
    return {powers: coefficient * factor
            for powers, coefficient in poly.items()
            if coefficient * factor}


def _multiply(left: _Poly, right: _Poly) -> _Poly:
    result: _Poly = {}
    for (m1, q1), a in left.items():
        for (m2, q2), b in right.items():
            key = (m1 + m2, q1 + q2)
            result[key] = result.get(key, Fraction(0)) + a * b
    return {powers: coefficient for powers, coefficient in result.items()
            if coefficient}


def _constant(value: int | Fraction) -> _Poly:
    value = Fraction(value)
    return {(0, 0): value} if value else {}


def _monomial(m_power: int, q_power: int,
              coefficient: int | Fraction = 1) -> _Poly:
    coefficient = Fraction(coefficient)
    return {(m_power, q_power): coefficient} if coefficient else {}


def _q_derivative(poly: _Poly) -> _Poly:
    result: _Poly = {}
    for (m_power, q_power), coefficient in poly.items():
        if q_power:
            key = (m_power, q_power - 1)
            result[key] = result.get(key, Fraction(0)) + coefficient * q_power
    return {powers: coefficient for powers, coefficient in result.items()
            if coefficient}


def _symbolic_checks() -> dict[str, int]:
    m = _monomial(1, 0)
    q = _monomial(0, 1)
    one = _constant(1)
    q2, q3, q4, q5 = (_multiply(q, q), _multiply(_multiply(q, q), q),
                       _multiply(_multiply(q, q), _multiply(q, q)),
                       _multiply(_multiply(q, q), _multiply(_multiply(q, q), q)))

    # The raw hazard cross product is checked independently against its
    # factored numerator, before any pointwise evaluation.
    numerator_l = _add(m, _scale(q2, 3), _scale(q4, 5))
    denominator_l = _add(m, q2, q4)
    numerator_g = _add(m, _scale(q3, 8))
    denominator_g = _add(m, _scale(q3, 2))
    raw_hazard_numerator = _add(
        _multiply(numerator_l, denominator_g),
        _scale(_multiply(numerator_g, denominator_l), -1))
    bracket = _add(m, _scale(_multiply(m, q), -2),
                   _scale(q3, -1), _scale(q4, -1))
    factored_hazard_numerator = _multiply(
        _scale(_multiply(_multiply(q2, _add(one, _scale(q, -1))), bracket), 2),
        one)
    assert raw_hazard_numerator == factored_hazard_numerator

    # Survival difference: sum(q**lambda)-sum(q**gamma), with the common
    # m copies of rate 1 cancelling exactly.
    raw_survival_numerator = _add(q3, q5, _scale(q4, -2))
    factored_survival_numerator = _multiply(
        _multiply(q3, _add(one, _scale(q, -1))),
        _add(one, _scale(q, -1)))
    assert raw_survival_numerator == factored_survival_numerator

    # Differentiate the formal bracket polynomial and check its coefficients.
    bracket_derivative = _q_derivative(bracket)
    assert bracket_derivative == {
        (1, 0): Fraction(-2), (0, 2): Fraction(-3), (0, 3): Fraction(-4)}
    return {"symbolicHazardNumeratorTerms": len(raw_hazard_numerator),
            "symbolicSurvivalNumeratorTerms": len(raw_survival_numerator),
            "symbolicBracketDerivativeTerms": len(bracket_derivative)}


def _hazard(rates: tuple[int, ...], q: Fraction) -> Fraction:
    return sum((rate * q ** rate for rate in rates), Fraction(0)) / sum(
        (q ** rate for rate in rates), Fraction(0))


def _survival(rates: tuple[int, ...], q: Fraction) -> Fraction:
    return sum((q ** rate for rate in rates), Fraction(0)) / len(rates)


def _framework_checks(m: int) -> tuple[int, int, int]:
    lam = (1,) * m + (3, 5)
    gamma = (1,) * m + (4, 4)
    n = m + 2
    assert len(lam) == len(gamma) == n
    assert sum(lam) == sum(gamma) == m + 8

    # The decreasingly sorted rate vector lambda majorizes gamma.
    sorted_lam = tuple(sorted(lam, reverse=True))
    sorted_gamma = tuple(sorted(gamma, reverse=True))
    prefix_cases = 0
    prefix_lam = prefix_gamma = 0
    for x, y in zip(sorted_lam, sorted_gamma):
        prefix_lam += x
        prefix_gamma += y
        assert prefix_lam >= prefix_gamma
        prefix_cases += 1
    assert prefix_lam == prefix_gamma

    # U_n premise: uniform positive p, alpha=1 and alpha_i*p_i constant;
    # every antiordering product vanishes exactly for both rate vectors.
    p = (Fraction(1, n),) * n
    alpha = Fraction(1)
    alpha_i = (Fraction(1),) * n
    assert all(weight > 0 for weight in p) and sum(p) == 1
    assert alpha == 1
    assert len({alpha_i[i] * p[i] for i in range(n)}) == 1
    antiordering_cases = 0
    for i in range(n):
        for j in range(n):
            assert (p[i] - p[j]) * (lam[i] - lam[j]) <= 0
            assert (p[i] - p[j]) * (gamma[i] - gamma[j]) <= 0
            assert (p[i] - p[j]) * (lam[i] - lam[j]) == 0
            assert (p[i] - p[j]) * (gamma[i] - gamma[j]) == 0
            antiordering_cases += 2

    # T averages the final two coordinates. It is doubly stochastic and maps
    # lambda to gamma by row-vector multiplication.
    matrix = tuple(tuple(
        (Fraction(1, 2) if i >= n - 2 and j >= n - 2 else
         Fraction(i == j)) for j in range(n)) for i in range(n))
    assert all(value >= 0 for row in matrix for value in row)
    assert all(sum(row) == 1 for row in matrix)
    assert all(sum(matrix[i][j] for i in range(n)) == 1 for j in range(n))
    mapped_weights = tuple(sum((p[i] * matrix[i][j] for i in range(n)),
                               Fraction(0)) for j in range(n))
    assert mapped_weights == p
    mapped = tuple(sum((Fraction(lam[i]) * matrix[i][j]
                        for i in range(n)), Fraction(0)) for j in range(n))
    assert mapped == tuple(map(Fraction, gamma))
    return prefix_cases, antiordering_cases, 1


def _point_checks() -> dict[str, int | str]:
    # Pin the three-label rational examples.
    lam3, gamma3 = (1, 3, 5), (1, 4, 4)
    assert _hazard(lam3, Fraction(1, 2)) == Fraction(11, 7)
    assert _hazard(gamma3, Fraction(1, 2)) == Fraction(8, 5)
    assert _hazard(lam3, Fraction(1, 2)) - _hazard(gamma3, Fraction(1, 2)) == Fraction(-1, 35)
    assert _hazard(lam3, Fraction(1, 4)) == Fraction(103, 91)
    assert _hazard(gamma3, Fraction(1, 4)) == Fraction(12, 11)
    assert _hazard(lam3, Fraction(1, 4)) - _hazard(gamma3, Fraction(1, 4)) == Fraction(41, 1001)

    q_points = tuple(Fraction(j, 16) for j in range(1, 16))
    hazard_cases = survival_cases = bracket_cases = 0
    prefix_total = antiordering_total = transition_total = 0
    for m in range(1, 31):
        lam = (1,) * m + (3, 5)
        gamma = (1,) * m + (4, 4)
        prefix, antiordering, transition = _framework_checks(m)
        prefix_total += prefix
        antiordering_total += antiordering
        transition_total += transition
        n = m + 2
        bracket_quarter = m * (1 - 2 * Fraction(1, 4)) - Fraction(1, 4) ** 3 * (1 + Fraction(1, 4))
        bracket_half = m * (1 - 2 * Fraction(1, 2)) - Fraction(1, 2) ** 3 * (1 + Fraction(1, 2))
        assert bracket_quarter == Fraction(m, 2) - Fraction(5, 256) > 0
        assert bracket_half == Fraction(-3, 16)
        for q in q_points:
            actual_hazard = _hazard(lam, q) - _hazard(gamma, q)
            expected_hazard = (2 * q ** 2 * (1 - q)
                               * (m * (1 - 2 * q) - q ** 3 * (1 + q))
                               / ((m + q ** 2 + q ** 4) * (m + 2 * q ** 3)))
            assert actual_hazard == expected_hazard
            hazard_cases += 1

            actual_survival = _survival(lam, q) - _survival(gamma, q)
            expected_survival = q ** 3 * (1 - q) ** 2 / n
            assert actual_survival == expected_survival
            survival_cases += 1

            bracket = m * (1 - 2 * q) - q ** 3 * (1 + q)
            assert bracket == Fraction(m) + Fraction(-2 * m) * q - q ** 3 - q ** 4
            assert -2 * m - 3 * q ** 2 - 4 * q ** 3 < 0
            bracket_cases += 1

    assert hazard_cases == survival_cases == bracket_cases == 450
    return {
        "hazardPointChecks": hazard_cases,
        "survivalPointChecks": survival_cases,
        "bracketDerivativePointChecks": bracket_cases,
        "mixtureSizes": 30,
        "qGridSize": len(q_points),
        "majorizationPrefixChecks": prefix_total,
        "antiorderingProductChecks": antiordering_total,
        "verifiedTTransforms": transition_total,
        "theoremMapping": "uniform U_n weights and rates related by doubly stochastic averaging; finite checks only, theorem mapping supplied externally",
        "hazardAtQHalfLambda": "11/7",
        "hazardAtQHalfGamma": "8/5",
        "hazardDifferenceAtQHalf": "-1/35",
        "hazardAtQQuarterLambda": "103/91",
        "hazardAtQQuarterGamma": "12/11",
        "hazardDifferenceAtQQuarter": "41/1001",
        "bracketAtQQuarter": "123/256",
        "bracketAtQHalf": "-3/16",
    }


def _strict_premise_checks() -> dict[str, int | str | tuple[str, ...]]:
    lam = (2, 6, 10)
    gamma = (2, 7, 9)
    p = (Fraction(2, 5), Fraction(1, 3), Fraction(4, 15))
    q = Fraction(1, 2)
    assert sum(p) == 1 and all(weight > 0 for weight in p)
    assert all(left > right for left, right in zip(p, p[1:]))
    assert all(left < right for left, right in zip(lam, lam[1:]))
    assert all(left < right for left, right in zip(gamma, gamma[1:]))

    # Strict antiordering for every distinct pair under both rate vectors.
    strict_products = 0
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            assert (p[i] - p[j]) * (lam[i] - lam[j]) < 0
            assert (p[i] - p[j]) * (gamma[i] - gamma[j]) < 0
            strict_products += 2

    # Equal totals and decreasingly sorted prefix majorization.
    assert sum(lam) == sum(gamma) == 18
    prefix_lam = prefix_gamma = 0
    prefix_cases = 0
    for left, right in zip(sorted(lam, reverse=True),
                           sorted(gamma, reverse=True)):
        prefix_lam += left
        prefix_gamma += right
        assert prefix_lam >= prefix_gamma
        prefix_cases += 1
    assert prefix_lam == prefix_gamma

    fixed_p_difference = (_weighted_hazard(lam, p, q)
                          - _weighted_hazard(gamma, p, q))
    assert fixed_p_difference == Fraction(248, 4455) > 0

    # T=(3/4)I+(1/4)swap(last two) maps rates lambda to gamma and p to p'.
    transition = (
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(3, 4), Fraction(1, 4)),
        (Fraction(0), Fraction(1, 4), Fraction(3, 4)),
    )
    assert all(value >= 0 for row in transition for value in row)
    assert all(sum(row) == 1 for row in transition)
    assert all(sum(transition[i][j] for i in range(3)) == 1
               for j in range(3))
    mapped_p = tuple(sum((p[i] * transition[i][j] for i in range(3)),
                         Fraction(0)) for j in range(3))
    mapped_lam = tuple(sum((Fraction(lam[i]) * transition[i][j]
                            for i in range(3)), Fraction(0)) for j in range(3))
    expected_p = (Fraction(2, 5), Fraction(19, 60), Fraction(17, 60))
    assert mapped_p == expected_p
    assert all(weight > 0 for weight in mapped_p)
    assert all(left > right for left, right in zip(mapped_p, mapped_p[1:]))
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            assert (mapped_p[i] - mapped_p[j]) * (gamma[i] - gamma[j]) < 0
    assert mapped_lam == tuple(map(Fraction, gamma))
    assert _weighted_hazard(lam, p, q) == Fraction(898, 405)
    assert _weighted_hazard(gamma, p, q) == Fraction(214, 99)
    assert _weighted_hazard(gamma, mapped_p, q) == Fraction(6829, 3165)
    transformed_difference = (_weighted_hazard(lam, p, q)
                              - _weighted_hazard(gamma, mapped_p, q))
    assert transformed_difference == Fraction(1019, 17091) > 0
    early_q = Fraction(3, 4)
    early_fixed_difference = (_weighted_hazard(lam, p, early_q)
                              - _weighted_hazard(gamma, p, early_q))
    early_transformed_difference = (_weighted_hazard(lam, p, early_q)
                                    - _weighted_hazard(gamma, mapped_p, early_q))
    assert early_fixed_difference == Fraction(-26862489, 459534895)
    assert early_transformed_difference == Fraction(-399285261, 7327839955)
    return {
        "strictPremiseAntiorderingProducts": strict_products,
        "strictPremiseMajorizationPrefixes": prefix_cases,
        "strictPremiseFixedWeightHazardDifference": "248/4455",
        "strictPremiseTransformedWeightHazardDifference": "1019/17091",
        "strictPremiseTransformedWeights": tuple(map(str, expected_p)),
        "strictPremiseLambdaHazardAtQHalf": "898/405",
        "strictPremiseGammaFixedWeightHazardAtQHalf": "214/99",
        "strictPremiseGammaTransformedWeightHazardAtQHalf": "6829/3165",
        "strictPremiseFixedWeightDifferenceAtQThreeQuarters": str(early_fixed_difference),
        "strictPremiseTransformedWeightDifferenceAtQThreeQuarters": str(early_transformed_difference),
    }


def _weighted_hazard(rates: tuple[int, ...], weights: tuple[Fraction, ...],
                     q: Fraction) -> Fraction:
    assert len(rates) == len(weights)
    numerator = sum((weights[i] * rates[i] * q ** rates[i]
                     for i in range(len(rates))), Fraction(0))
    denominator = sum((weights[i] * q ** rates[i]
                       for i in range(len(rates))), Fraction(0))
    return numerator / denominator


def verify() -> dict[str, int | str | tuple[str, ...]]:
    """Run fixed exact checks for the uniform hazard-mixture example."""
    return {**_symbolic_checks(), **_point_checks(), **_strict_premise_checks()}


if __name__ == "__main__":
    print("uniform hazard mixtures:", verify())
