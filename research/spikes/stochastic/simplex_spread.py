"""Exact bounded checker for supplied fixed-sum softmax thresholds.

All formulas and witnesses were supplied externally. This finite checker makes
no theorem-origin or literature-priority claim; the analytic theorem proof is
recorded separately. It writes no artifacts and accepts no external inputs.
"""
from fractions import Fraction as F

from research.spikes.stochastic.softmax_spread import (
    _exp_bounds,
    _softmax,
    _threshold_bounds,
)


_SIZES = (3, 4, 8, 32, 57, 58, 128)
_D_STEPS = 26
_C_STEPS = 24


def _positive_exp_bounds(x: F) -> tuple[F, F]:
    """Enclose exp(x) on [2,6] by squaring bounds for exp(x/2)."""
    assert 2 <= x <= 6
    lower, upper = _exp_bounds(x / 2)
    assert 1 <= x / 2 <= 3
    return lower * lower, upper * upper


def _d_bounds(n: int, x: F) -> tuple[F, F]:
    assert n >= 3 and 2 <= x <= 6
    exp_lower, exp_upper = _positive_exp_bounds(x)
    factor = x - 2
    return (factor * exp_lower - 2 * (n - 1),
            factor * exp_upper - 2 * (n - 1))


def _d_roots() -> tuple[dict[str, object], ...]:
    roots = []
    previous_upper = None
    for n in _SIZES:
        lo, hi = F(2), F(6)
        assert _d_bounds(n, lo)[1] < 0 < _d_bounds(n, hi)[0]
        # f'_n(x)=exp(x)(x-1)>0 throughout the bracket, so bisection is valid.
        assert lo - 1 > 0 and hi - 1 > 0
        for _ in range(_D_STEPS):
            mid = (lo + hi) / 2
            lower, upper = _d_bounds(n, mid)
            if upper < 0:
                lo = mid
            else:
                assert lower > 0, "positive-root enclosure left a bisection point unresolved"
                hi = mid
        assert hi - lo == F(1, 2 ** 24)
        assert _d_bounds(n, lo)[1] < 0 < _d_bounds(n, hi)[0]
        if previous_upper is not None:
            assert previous_upper < lo
        previous_upper = hi
        roots.append({"n": n, "lower": str(lo), "upper": str(hi)})
    return tuple(roots)


def _c_roots() -> tuple[dict[str, object], ...]:
    roots = []
    previous_lower = None
    for n in _SIZES:
        lo, hi = F(2), F(3)
        assert _threshold_bounds(n, lo)[1] < 0 < _threshold_bounds(n, hi)[0]
        # The imported oracle encloses (n-2)(x-2)exp(x)-4. Its derivative
        # (n-2)(x-1)exp(x) is strictly positive over [2,3].
        for _ in range(_C_STEPS):
            mid = (lo + hi) / 2
            lower, upper = _threshold_bounds(n, mid)
            if upper < 0:
                lo = mid
            else:
                assert lower > 0, "negative-root enclosure left a bisection point unresolved"
                hi = mid
        assert hi - lo == F(1, 2 ** 24)
        assert _threshold_bounds(n, lo)[1] < 0 < _threshold_bounds(n, hi)[0]
        if previous_lower is not None:
            assert hi < previous_lower
        previous_lower = lo
        roots.append({"n": n, "lower": str(lo), "upper": str(hi)})
    return tuple(roots)


def _threshold_comparisons(d_roots, c_roots):
    comparisons = []
    for d, c in zip(d_roots, c_roots):
        d_lo, d_hi = F(d["lower"]), F(d["upper"])
        c_lo, c_hi = F(c["lower"]), F(c["upper"])
        if d_hi < 2 * c_lo:
            relation = "d_n < 2 c_n"
        elif d_lo > 2 * c_hi:
            relation = "d_n > 2 c_n"
        else:
            relation = "not separated by certified intervals"
        comparisons.append({"n": d["n"], "relation": relation})
    return tuple(comparisons)


def _prefix_majorizes(left, right) -> int:
    assert len(left) == len(right) == 3
    assert sum(left) == sum(right) == 1
    cases = 0
    for k in range(1, 4):
        assert sum(sorted(left, reverse=True)[:k]) >= sum(
            sorted(right, reverse=True)[:k])
        cases += 1
    return cases


def _simplex_witnesses():
    positive_x = (F(3, 4), F(1, 4), F(0))
    positive_y = (F(3, 4), F(1, 8), F(1, 8))
    negative_u = (F(0), F(3, 8), F(5, 8))
    negative_v = (F(0), F(1, 2), F(1, 2))
    assert all(value >= 0 for vector in
               (positive_x, positive_y, negative_u, negative_v)
               for value in vector)
    prefixes = (_prefix_majorizes(positive_x, positive_y)
                + _prefix_majorizes(negative_u, negative_v))

    positive_x_value = _softmax(positive_x, 1)
    positive_y_value = _softmax(positive_y, 1)
    positive_difference = positive_x_value - positive_y_value
    assert positive_x_value == F(49, 69)
    assert positive_y_value == F(97, 136)
    assert positive_difference == F(-29, 9384) < 0

    negative_u_value = _softmax(negative_u, -1)
    negative_v_value = _softmax(negative_v, -1)
    negative_difference = negative_u_value - negative_v_value
    assert negative_u_value == F(17, 296)
    assert negative_v_value == F(1, 18)
    assert negative_difference == F(5, 2664) > 0
    return {
        "simplexMajorizationPrefixChecks": prefixes,
        "simplexPositiveTemperatureX": tuple(map(str, positive_x)),
        "simplexPositiveTemperatureY": tuple(map(str, positive_y)),
        "simplexPositiveTemperatureBx": str(positive_x_value),
        "simplexPositiveTemperatureBy": str(positive_y_value),
        "simplexPositiveTemperatureDifference": str(positive_difference),
        "simplexNegativeTemperatureU": tuple(map(str, negative_u)),
        "simplexNegativeTemperatureV": tuple(map(str, negative_v)),
        "simplexNegativeTemperatureBu": str(negative_u_value),
        "simplexNegativeTemperatureBv": str(negative_v_value),
        "simplexNegativeTemperatureDifference": str(negative_difference),
    }


def verify() -> dict[str, object]:
    """Run exact root-enclosure, threshold-comparison, and simplex checks."""
    d_roots = _d_roots()
    c_roots = _c_roots()
    negative_thresholds = tuple({
        "n": root["n"],
        "lower": str(2 * F(root["lower"])),
        "upper": str(2 * F(root["upper"])),
    } for root in c_roots)
    assert all(F(root["upper"]) - F(root["lower"]) == F(1, 2 ** 24)
               for root in c_roots)
    assert all(F(root["upper"]) - F(root["lower"]) == F(1, 2 ** 23)
               for root in negative_thresholds)
    comparisons = _threshold_comparisons(d_roots, c_roots)
    assert comparisons[4]["relation"] == "d_n < 2 c_n"
    assert comparisons[5]["relation"] == "d_n > 2 c_n"
    return {
        "simplexThresholdSizes": _SIZES,
        "simplexPositiveRootBisectionSteps": _D_STEPS,
        "simplexPositiveRootBracketWidth": "1/16777216",
        "simplexNegativeRootBisectionSteps": _C_STEPS,
        "simplexCRootBracketWidth": "1/16777216",
        "simplexNegativeThresholdBracketWidth": "1/8388608",
        "simplexPositiveThresholdBrackets": d_roots,
        "simplexCRootBrackets": c_roots,
        "simplexNegativeThresholdBrackets": negative_thresholds,
        "simplexThresholdComparisons": comparisons,
        **_simplex_witnesses(),
        "simplexLimitations": "Supplied theorem and formulas; finite exact checks only, no theorem proof or literature-priority claim.",
    }


if __name__ == "__main__":
    print("simplex softmax spread:", verify())
