"""Finite corroboration for supplied positive-temperature support lemmas.

The exact checks use rational arithmetic on fixed grids. A separate bounded
Decimal calculation checks 72 cycle-curvature identities numerically. These
are corroborating checks, not proofs of the universal theorems or priority.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as Q
from itertools import product


def _exp_taylor_enclosure(x: Q, degree: int = 64) -> tuple[Q, Q]:
    """Exact positive Taylor sum and geometric remainder for 0<=x<1."""
    if not 0 <= x < 1:
        raise ValueError("this local exponential bound accepts 0 <= x < 1")
    term = total = Q(1)
    for k in range(1, degree + 1):
        term *= x / k
        total += term
    following = term * x / (degree + 1)
    ratio = x / (degree + 2)
    return total, total + following / (1 - ratio)


def _q_score(population: int, effort: Q, z: Q) -> Q:
    weight = z ** int(4 * effort)
    return effort * weight / (weight + population - 1)


def _inner_superadditivity() -> dict[str, int]:
    grid = (Q(1, 4), Q(1, 2), Q(3, 4))
    pairs = tuple((a, b) for a in grid for b in grid if a + b <= 1)
    equalities = strict = cases = 0
    for population in range(1, 11):
        for z in (Q(3, 2), Q(2), Q(3)):
            for a, b in pairs:
                combined = _q_score(population, a + b, z)
                separate = _q_score(population, a, z) + _q_score(population, b, z)
                assert combined >= separate
                if population == 1:
                    assert combined == separate
                    equalities += 1
                else:
                    assert combined > separate
                    strict += 1
                cases += 1
    assert cases == 180 and equalities == 18 and strict == 162
    return {"cases": cases, "N1Equalities": equalities,
            "N2To10Strict": strict}


def _outer_fixed_score_consolidation(tau_hi: Q) -> dict[str, int]:
    grid = tuple(Q(k, 4) for k in range(5))
    pairs = tuple((x, y) for x in grid[1:] for y in grid[1:] if x + y <= 1)
    cases = certified = excluded = 0
    for tasks in range(2, 5):
        for x, y in pairs:
            for background in product(grid, repeat=tasks - 2):
                scores = (x, y) + background
                weights = tuple(Q(2) ** int(4 * score) for score in scores)
                numerator = sum((score * weight for score, weight in zip(scores, weights)), Q(0))
                denominator = sum(weights, Q(0))
                reward = numerator / denominator

                def active_derivative_certified(score: Q) -> bool:
                    gap = score - reward
                    # If the gap is negative, tau<=tau_hi is the adverse end
                    # of the certified range for g=1+tau*(score-reward).
                    return gap >= 0 or 1 + tau_hi * gap > 0

                cases += 1
                if not (active_derivative_certified(x)
                        and active_derivative_certified(y)):
                    excluded += 1
                    continue
                certified += 1

                X, Y = Q(2) ** int(4 * x), Q(2) ** int(4 * y)
                delta_num_direct = (x + y) * X * Y - x * X - y * Y
                delta_den_direct = X * Y + 1 - X - Y
                delta_num = x * X * (Y - 1) + y * Y * (X - 1)
                delta_den = (X - 1) * (Y - 1)
                assert delta_num_direct == delta_num
                assert delta_den_direct == delta_den > 0
                T = x / (1 - 1 / X) + y / (1 - 1 / Y)
                assert T > reward
                assert delta_num - reward * delta_den == delta_den * (T - reward) > 0

                new_scores = (x + y, Q(0)) + background
                new_weights = tuple(Q(2) ** int(4 * score) for score in new_scores)
                new_reward = (
                    sum((s * w for s, w in zip(new_scores, new_weights)), Q(0))
                    / sum(new_weights, Q(0))
                )
                assert new_reward > reward
    assert cases == 186 and certified == 110 and excluded == 76
    return {"fixedScoreCases": cases, "bothActiveCertified": certified,
            "notCertifiedBothActiveExcluded": excluded}


def _two_task_curvature(tau_lo: Q, tau_hi: Q) -> dict[str, int]:
    quarter = (Q(1, 4), Q(1, 2), Q(3, 4))
    total = certified = excluded = endpoint_checks = 0
    for population in range(2, 11):
        for pure_left in range(population):
            for b in quarter:
                total += 1
                left_weight = Q(2) ** int(4 * b)
                right_weight = Q(2) ** int(4 * (1 - b))

                left_den = 16 * pure_left + left_weight + (population - pure_left - 1)
                left_score = (16 * pure_left + b * left_weight) / left_den
                p_left = left_weight / left_den
                h_left = (1 + tau_lo * (b - left_score),
                          1 + tau_hi * (b - left_score))

                pure_right = population - pure_left - 1
                right_den = 16 * pure_right + right_weight + pure_left
                right_score = (16 * pure_right + (1 - b) * right_weight) / right_den
                p_right = right_weight / right_den
                h_right = (1 + tau_lo * (1 - b - right_score),
                           1 + tau_hi * (1 - b - right_score))

                if min(h_left) <= 0 or min(h_right) <= 0:
                    excluded += 1
                    continue
                certified += 1
                for t in (tau_lo, tau_hi):
                    left_curvature_over_t = p_left * (
                        2 * (1 - p_left) + t * (b - left_score) * (1 - 2 * p_left)
                    )
                    right_curvature_over_t = p_right * (
                        2 * (1 - p_right)
                        + t * (1 - b - right_score) * (1 - 2 * p_right)
                    )
                    assert left_curvature_over_t > 0
                    assert right_curvature_over_t > 0
                    endpoint_checks += 2
    assert total == 162 and certified == 18 and excluded == 144
    assert endpoint_checks == 72
    return {"cases": total, "bothActiveHPositiveCertified": certified,
            "hNotCertifiedExcluded": excluded,
            "positiveCurvatureEndpointChecks": endpoint_checks}


def _feasible_reward_amgm() -> dict[str, int]:
    h_values = (Q(1, 4), Q(1, 2), Q(1), Q(2), Q(4))
    p_values = (Q(1, 4), Q(1, 2), Q(3, 4), Q(99, 100), Q(1023, 1024))
    roots = (Q(1, 2), Q(1), Q(3, 2))
    cases = boundary_cases = 0
    for root in roots:
        beta = root * root
        for p in p_values:
            assert 0 < p < 1
            for h in h_values:
                bracket = 1 + 1 / h - 2 * p + beta * p * h
                decomposed = (
                    (1 - p) * (1 + 1 / h)
                    + p * ((2 * root - 1) + (root * h - 1) ** 2 / h)
                )
                assert bracket == decomposed > 0
                assert 1 / h + beta * h >= 2 * root
                cases += 1
                if beta == Q(1, 4):
                    assert 1 / h + beta * h - 1 == (h - 2) ** 2 / (4 * h)
                    boundary_cases += 1

    feasible_boundary_cases = 0
    for t in (Q(4), Q(8), Q(16), Q(32)):
        for G in (Q(1), Q(2), Q(4)):
            tau = t / (4 * (1 + 1 / G))
            beta = tau / t * (1 + 1 / G)
            r0 = 1 - (G - 1) / tau
            if 0 <= r0 <= 1:
                assert beta == Q(1, 4)
                assert G == 1 + tau * (1 - r0)
                assert t == 4 * tau * (1 + 1 / G)
                feasible_boundary_cases += 1
    assert cases == 75 and boundary_cases == 25
    assert feasible_boundary_cases == 9
    return {"bracketIdentityCases": cases,
            "betaQuarterStrictCases": boundary_cases,
            "feasibleRewardBoundaryCases": feasible_boundary_cases}


def _boltzmann(values: list[Decimal], temperature: Decimal) -> Decimal:
    weights = [(temperature * value).exp() for value in values]
    return sum((value * weight for value, weight in zip(values, weights)), Decimal(0)) / sum(weights)


def _nested(allocation: list[list[Decimal]], inner: Decimal,
            outer: Decimal) -> Decimal:
    task_scores = [
        _boltzmann([row[column] for row in allocation], inner)
        for column in range(len(allocation[0]))
    ]
    return _boltzmann(task_scores, outer)


def _decimal_cycle_curvature() -> dict[str, object]:
    checks = 0
    maximum_abs_error = Decimal(0)
    with localcontext() as context:
        context.prec = 85
        step = Decimal("1e-17")
        inner_values = tuple(map(Decimal, ("0.5", "2", "8", "20")))
        outer_values = tuple(map(Decimal, ("0.01", "0.2", "3")))
        for population in range(3, 9):
            for inner in inner_values:
                for outer in outer_values:
                    allocation = [
                        [Decimal("0.5") if column in (row, (row + 1) % population)
                         else Decimal(0) for column in range(population)]
                        for row in range(population)
                    ]
                    direction = [
                        [Decimal(1) if column == row
                         else Decimal(-1) if column == (row + 1) % population
                         else Decimal(0) for column in range(population)]
                        for row in range(population)
                    ]
                    weight = (inner / 2).exp()
                    probability = weight / (2 * weight + population - 2)
                    score = probability
                    h = 1 + inner * (Decimal("0.5") - score)
                    predicted = 2 * inner * probability * (1 + h)
                    plus = [[a + step * v for a, v in zip(row, delta)]
                            for row, delta in zip(allocation, direction)]
                    minus = [[a - step * v for a, v in zip(row, delta)]
                             for row, delta in zip(allocation, direction)]
                    finite_difference = (
                        _nested(plus, inner, outer)
                        - 2 * _nested(allocation, inner, outer)
                        + _nested(minus, inner, outer)
                    ) / (step * step)
                    error = abs(finite_difference - predicted)
                    assert predicted > 0 and error < Decimal("1e-25")
                    maximum_abs_error = max(maximum_abs_error, error)
                    checks += 1
    assert checks == 72
    return {"decimalCycleChecks": checks,
            "maximumAbsoluteFiniteDifferenceError": str(maximum_abs_error),
            "scope": "finite Decimal corroboration only; universal forest claim rests on analytic proof"}


def verify() -> dict[str, object]:
    exp_069_lo, exp_069_hi = _exp_taylor_enclosure(Q(69, 100))
    exp_070_lo, exp_070_hi = _exp_taylor_enclosure(Q(7, 10))
    assert exp_069_hi < 2 < exp_070_lo
    ln2_bounds = (Q(69, 100), Q(7, 10))
    tau_lo, tau_hi = 4 * ln2_bounds[0], 4 * ln2_bounds[1]
    assert tau_lo == Q(69, 25) and tau_hi == Q(14, 5)

    summary = {
        "ln2ExpSeriesBoundCertified": True,
        "tauLower": str(tau_lo),
        "tauUpper": str(tau_hi),
        "innerSuperadditivity": _inner_superadditivity(),
        "outerConsolidation": _outer_fixed_score_consolidation(tau_hi),
        "twoTaskCurvature": _two_task_curvature(tau_lo, tau_hi),
        "feasibleRewardAmgm": _feasible_reward_amgm(),
        "cycleCurvature": _decimal_cycle_curvature(),
    }
    return {"softmaxSupport": summary}


if __name__ == "__main__":
    print("softmax support:", verify())
