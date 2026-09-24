"""Fixed exact checks for sharp softmax-spread examples.

This module checks supplied rational examples and bounded root brackets. Its
Taylor bounds are exact rational enclosures, not floating-point evidence. The
unbounded analytic theorem and any literature assessment are outside this
verifier. There are no external inputs or optional dependencies.
"""
from fractions import Fraction


_ROOT_SIZES = (3, 4, 8, 32, 128)
_TAYLOR_DEGREE = 48
_BISECTION_STEPS = 24


def _exp_bounds(x: Fraction) -> tuple[Fraction, Fraction]:
    """Enclose exp(x) on [0,3] by a Taylor sum and geometric tail bound.

    The Taylor terms are positive. After degree 48, each successive term's
    ratio is x/(k+1) <= x/50 <= 3/50 < 1. Thus the omitted positive tail is
    bounded by its first term divided by 1-x/50.
    """
    assert 0 <= x <= 3
    term = Fraction(1)
    partial = term
    for k in range(1, _TAYLOR_DEGREE + 1):
        term *= x / k
        partial += term
    first_omitted = term * x / (_TAYLOR_DEGREE + 1)
    upper = partial + first_omitted / (1 - x / (_TAYLOR_DEGREE + 2))
    return partial, upper


def _threshold_bounds(n: int, x: Fraction
                      ) -> tuple[Fraction, Fraction]:
    """Enclose f_n(x)=(n-2)(x-2)exp(x)-4 for x in [2,3]."""
    assert n >= 3 and 2 <= x <= 3
    exp_lower, exp_upper = _exp_bounds(x)
    multiplier = (n - 2) * (x - 2)
    assert multiplier >= 0
    return multiplier * exp_lower - 4, multiplier * exp_upper - 4


def _threshold_checks() -> dict[str, int | tuple[int, ...] | tuple[tuple[str, str], ...]]:
    roots = []
    previous_lower = None
    monotone_checks = 0
    for n in _ROOT_SIZES:
        lower, upper = Fraction(2), Fraction(3)
        assert _threshold_bounds(n, lower)[1] < 0
        assert _threshold_bounds(n, upper)[0] > 0
        # f'_n(x)=(n-2)(x-1)exp(x)>0 for n>=3 and x in [2,3].
        assert (n - 2) * (lower - 1) > 0
        assert (n - 2) * (upper - 1) > 0
        for _ in range(_BISECTION_STEPS):
            middle = (lower + upper) / 2
            f_lower, f_upper = _threshold_bounds(n, middle)
            if f_upper < 0:
                lower = middle
            else:
                assert f_lower > 0, "Taylor enclosure did not classify bisection point"
                upper = middle
        assert upper - lower == Fraction(1, 2 ** _BISECTION_STEPS)
        assert _threshold_bounds(n, lower)[1] < 0
        assert _threshold_bounds(n, upper)[0] > 0
        if previous_lower is not None:
            # Increasing n raises f_n pointwise on x>2, so its unique root
            # moves left; these disjoint certified intervals check that order.
            assert upper < previous_lower
            monotone_checks += 1
        previous_lower = lower
        roots.append((str(lower), str(upper)))
    return {
        "softmaxTaylorDegree": _TAYLOR_DEGREE,
        "softmaxTaylorArgumentBound": 3,
        "softmaxBisectionStepsPerRoot": _BISECTION_STEPS,
        "softmaxThresholdRootCount": len(roots),
        "softmaxThresholdSizes": _ROOT_SIZES,
        "softmaxMonotoneRootOrderChecks": monotone_checks,
        "softmaxThresholdBrackets": tuple(roots),
    }


def _softmax(values: tuple[Fraction, ...], sign: int = 1) -> Fraction:
    """Compute B_{sign*8 log 2} exactly for eighth-grid values."""
    assert sign in (-1, 1)
    exponents = tuple(sign * 8 * value for value in values)
    assert all(exponent.denominator == 1 for exponent in exponents)
    weights = tuple(
        (Fraction(2 ** int(exponent)) if exponent >= 0
         else Fraction(1, 2 ** (-int(exponent))))
        for exponent in exponents)
    assert all(weight > 0 for weight in weights)
    return sum((value * weight for value, weight in zip(values, weights)),
               Fraction(0)) / sum(weights, Fraction(0))


def _allocation_rows(column: tuple[Fraction, ...],
                     add_zero_third: bool = False
                     ) -> tuple[tuple[Fraction, ...], ...]:
    """Append each agent's complement to make row budget exactly one."""
    assert len(column) == 3 and all(0 <= value <= 1 for value in column)
    rows = tuple((value, 1 - value) for value in column)
    if add_zero_third:
        rows = tuple((*row, Fraction(0)) for row in rows)
    assert all(sum(row) == 1 for row in rows)
    return rows


def _softmax_witness_checks() -> dict[str, int | str | tuple[str, ...] | tuple[tuple[str, ...], ...]]:
    x = (Fraction(1), Fraction(1, 2), Fraction(0))
    y = (Fraction(1), Fraction(1, 4), Fraction(1, 4))
    assert sum(x) == sum(y)
    for k in (1, 2, 3):
        assert sum(sorted(x, reverse=True)[:k]) >= sum(sorted(y, reverse=True)[:k])

    bx = _softmax(x)
    by = _softmax(y)
    difference = bx - by
    assert bx == Fraction(88, 91)
    assert by == Fraction(43, 44)
    assert difference == Fraction(-41, 4004)

    # Reflecting both vectors and reversing temperature gives the mirror
    # witness. The identity B_{-tau}(1-z)=1-B_tau(z) is checked exactly.
    reflected_x = tuple(1 - value for value in x)
    reflected_y = tuple(1 - value for value in y)
    assert sum(reflected_x) == sum(reflected_y)
    for k in (1, 2, 3):
        assert (sum(sorted(reflected_x, reverse=True)[:k])
                >= sum(sorted(reflected_y, reverse=True)[:k]))
    reflected_bx = _softmax(reflected_x, -1)
    reflected_by = _softmax(reflected_y, -1)
    reflected_difference = reflected_bx - reflected_by
    assert reflected_bx == 1 - bx
    assert reflected_by == 1 - by
    assert reflected_difference == Fraction(41, 4004) > 0

    allocations_x = _allocation_rows(x)
    allocations_y = _allocation_rows(y)
    allocations_x_zero = _allocation_rows(x, add_zero_third=True)
    allocations_y_zero = _allocation_rows(y, add_zero_third=True)
    assert all(len(row) == 2 for row in (*allocations_x, *allocations_y))
    assert all(len(row) == 3 for row in (*allocations_x_zero, *allocations_y_zero))
    assert all(row[2] == 0 for row in (*allocations_x_zero, *allocations_y_zero))
    return {
        "softmaxMajorizationPrefixChecks": 6,
        "softmaxAllocationRowBudgetChecks": 12,
        "softmaxAllocationZeroThirdColumnChecks": 6,
        "softmaxWitnessBx": str(bx),
        "softmaxWitnessBy": str(by),
        "softmaxWitnessDifferenceBxMinusBy": str(difference),
        "softmaxWitnessReflectedX": tuple(map(str, reflected_x)),
        "softmaxWitnessReflectedY": tuple(map(str, reflected_y)),
        "softmaxWitnessReflectedBxAtNegativeTemperature": str(reflected_bx),
        "softmaxWitnessReflectedByAtNegativeTemperature": str(reflected_by),
        "softmaxWitnessReflectedDifferenceAtNegativeTemperature": str(reflected_difference),
        "softmaxWitnessXTwoTaskRows": tuple(tuple(map(str, row))
                                             for row in allocations_x),
        "softmaxWitnessYTwoTaskRows": tuple(tuple(map(str, row))
                                             for row in allocations_y),
        "softmaxWitnessXWithZeroThirdTaskRows": tuple(tuple(map(str, row))
                                                       for row in allocations_x_zero),
        "softmaxWitnessYWithZeroThirdTaskRows": tuple(tuple(map(str, row))
                                                       for row in allocations_y_zero),
    }


def verify() -> dict[str, int | str | tuple[int, ...] | tuple[str, ...] | tuple[tuple[str, ...], ...]]:
    """Run fixed exact threshold and softmax-spread checks."""
    return {**_threshold_checks(), **_softmax_witness_checks()}


if __name__ == "__main__":
    print("softmax spread:", verify())
