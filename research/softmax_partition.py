"""Certified pure-group optimization for nested Boltzmann task allocation.

Only the Python standard library is used. Exact rational Taylor enclosures,
outward dyadic rounding, and two exact-budget DPs certify additive regret.
The continuous-model conclusion requires the separately proved purity region.
Run ``python3 -m research.softmax_partition --help`` for the bounded CLI.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
import re

from research.softmax_partition_dp import maximize_partition


CONTRACT = "algal.lab.softmax-partition.v1"
MAX_DIMENSION = 128
MAX_TEMPERATURE = Q(32)
MIN_EPSILON = Q(1, 2**40)
MAX_TRANSITIONS = 8_000_000
PRECISIONS = (32, 64, 128, 256)


def _rational(value: object, low: Q, high: Q, name: str) -> Q:
    if type(value) not in (int, Q):
        raise ValueError(f"{name}: requires an exact int or Fraction")
    result = Q(value)
    if (result.numerator.bit_length() > 64
            or result.denominator.bit_length() > 64
            or not low <= result <= high):
        raise ValueError(f"{name}: out of range or exceeds 64-bit rational input cap")
    return result


def _down(x: Q, bits: int) -> Q:
    return Q((x.numerator << bits) // x.denominator, 1 << bits)


def _up(x: Q, bits: int) -> Q:
    return -_down(-x, bits)


def _exp_interval(x: Q, bits: int) -> tuple[Q, Q]:
    """Enclose exp(x), 0<=x<=32, with exact rational operations.

    Scale to y<=1. After degree k, the positive Taylor remainder is at
    most next_term/(1-y/(k+2)); subsequent term ratios only decrease.
    Square outward intervals to undo scaling. No floating-point exp is used.
    """
    if not 0 <= x <= MAX_TEMPERATURE:
        raise ValueError("internal exponential input outside 0..32")
    if x == 0:
        return Q(1), Q(1)
    y, squarings = x, 0
    while y > 1:
        y /= 2
        squarings += 1
    term = total = Q(1)
    target = Q(1, 1 << (bits + 8))
    for degree in range(1, 1025):
        term *= y / degree
        total += term
        next_term = term * y / (degree + 1)
        tail = next_term / (1 - y / (degree + 2))
        if tail <= target:
            lo, hi = _down(total, bits), _up(total + tail, bits)
            for _ in range(squarings):
                lo, hi = _down(lo * lo, bits), _up(hi * hi, bits)
            return lo, hi
    raise ArithmeticError("exponential series work cap reached")


def _item_intervals(agents: int, inner: Q, outer: Q, bits: int
                    ) -> tuple[tuple[Q, Q, Q, Q], ...]:
    """Bounds (a_lo,a_hi,b_lo,b_hi) for a=s*exp(tau*s), b=exp(tau*s)-1."""
    e_lo, e_hi = _exp_interval(inner, bits)
    items = []
    for size in range(1, agents + 1):
        s_lo = size * e_lo / (size * e_lo + agents - size)
        s_hi = size * e_hi / (size * e_hi + agents - size)
        w_lo, w_hi = _exp_interval(outer * s_lo, bits)
        if s_hi != s_lo:
            _, w_hi = _exp_interval(outer * s_hi, bits)
        items.append((_down(s_lo * w_lo, bits), _up(s_hi * w_hi, bits),
                      max(Q(0), w_lo - 1), w_hi - 1))
    return tuple(items)


def _reward_interval(groups: tuple[int, ...], tasks: int,
                     items: tuple[tuple[Q, Q, Q, Q], ...], bits: int
                     ) -> tuple[Q, Q]:
    a_lo = sum((items[m - 1][0] for m in groups), Q(0))
    a_hi = sum((items[m - 1][1] for m in groups), Q(0))
    b_lo = tasks + sum((items[m - 1][2] for m in groups), Q(0))
    b_hi = tasks + sum((items[m - 1][3] for m in groups), Q(0))
    return max(Q(0), _down(a_lo / b_hi, bits)), min(Q(1), _up(a_hi / b_lo, bits))


def optimize_partition(agents: int, tasks: int, inner: Q, outer: Q,
                       epsilon: Q = Q(1, 1_000_000)) -> dict[str, object]:
    """Return a pure grouping and a rigorous additive-regret enclosure.

    Counts are bounded explicit populations. Temperatures must be positive
    exact rationals <=32, with <=64-bit numerator/denominator. Epsilon is
    in [2^-40,1]. Work admission precedes exponential evaluation. Outside
    the proved purity region, the upper bound applies ONLY to pure optima.
    This endpoint does not identify all ties or promise an exact optimizer.
    """
    for name, value in (("agents", agents), ("tasks", tasks)):
        if type(value) is not int or not 1 <= value <= MAX_DIMENSION:
            raise ValueError(f"{name}: requires an integer in 1..{MAX_DIMENSION}")
    inner = _rational(inner, Q(0), MAX_TEMPERATURE, "inner")
    outer = _rational(outer, Q(0), MAX_TEMPERATURE, "outer")
    if inner == 0 or outer == 0:
        raise ValueError("temperatures must be strictly positive")
    epsilon = _rational(epsilon, MIN_EPSILON, Q(1), "epsilon")
    max_queries, width = 0, Q(1)
    while width > epsilon:
        max_queries += 1
        width /= 2
    cap = min(agents, tasks)
    per_dp_bound = agents * (agents + 1) // 2
    if cap < agents:
        per_dp_bound *= cap
    transition_bound = 2 * max_queries * per_dp_bound
    if transition_bound > MAX_TRANSITIONS:
        raise ValueError("requested dimensions and epsilon exceed DP work cap")

    # Uniform in every query rho in [0,1]: the two residual DPs differ
    # by at most cap*max_m(width(a_m)+width(b_m)). This permits safe
    # termination at an exact/near tie without deciding its sign.
    for bits in PRECISIONS:
        items = _item_intervals(agents, inner, outer, bits)
        residual_width_bound = cap * max(a_hi - a_lo + b_hi - b_lo
                                        for a_lo, a_hi, b_lo, b_hi in items)
        if residual_width_bound <= epsilon * tasks / 4:
            break
    else:
        raise ArithmeticError("coefficient precision cap reached; no certificate returned")

    best_groups = (agents,)
    lower, witness_upper = _reward_interval(best_groups, tasks, items, bits)
    upper = Q(1)
    queries = transitions = 0
    stop = "bracket"
    while upper - lower > epsilon:
        if queries >= max_queries:
            raise ArithmeticError("bisection invariant failed; no certificate returned")
        rho = (lower + upper) / 2
        low_profits = tuple(a_lo - rho * b_hi for a_lo, _, _, b_hi in items)
        high_profits = tuple(a_hi - rho * b_lo for _, a_hi, b_lo, _ in items)
        low_value, groups, work_lo = maximize_partition(low_profits, tasks)
        high_value, _, work_hi = maximize_partition(high_profits, tasks)
        queries += 1
        transitions += work_lo + work_hi
        residual_lo, residual_hi = low_value - tasks * rho, high_value - tasks * rho
        candidate_lower, candidate_upper = _reward_interval(groups, tasks, items, bits)

        if residual_lo <= 0 <= residual_hi:
            # The lower-DP path has true residual >=residual_lo. Every
            # denominator is >=tasks, giving these two reward bounds.
            candidate_lower = max(candidate_lower, rho + residual_lo / tasks)
            upper = min(upper, rho + residual_hi / tasks)
            stop = "small-residual"
        elif residual_lo > 0:
            candidate_lower = max(candidate_lower, rho)
        else:
            # residual_hi<0 certifies that every ratio is below rho.
            upper = min(upper, rho)
        if candidate_lower > lower:
            best_groups, lower, witness_upper = groups, candidate_lower, candidate_upper
        if stop == "small-residual":
            break

    if not (Q(0) <= lower <= upper <= 1
            and lower <= witness_upper <= 1
            and upper - lower <= epsilon
            and transitions <= transition_bound):
        raise ArithmeticError("certificate invariant failed; no certificate returned")
    continuous = inner <= 2 or 4 * outer >= inner
    return {
        "contract": CONTRACT,
        "agents": agents, "tasks": tasks,
        "inner": str(inner), "outer": str(outer), "epsilon": str(epsilon),
        "groups": list(best_groups),
        "optimumScope": "continuous" if continuous else "pure-only",
        "optimumInterval": [str(lower), str(upper)],
        "witnessRewardInterval": [str(lower), str(min(upper, witness_upper))],
        "additiveRegretBound": str(upper - lower),
        "precisionBits": bits, "thresholdQueries": queries,
        "dpTransitions": transitions, "admittedTransitionBound": transition_bound,
        "residualWidthBound": str(residual_width_bound), "stopReason": stop,
        "arithmetic": "exact rational Taylor enclosures and outward dyadic rounding",
    }


def _cli_rational(raw: str) -> Q:
    # Fraction accepts scientific notation with arbitrarily large exponents.
    # Bound the grammar before conversion, rather than after its allocation.
    if re.fullmatch(r"[+-]?[0-9]{1,20}(?:/[0-9]{1,20}|\.[0-9]{1,20})?", raw) is None:
        raise argparse.ArgumentTypeError("requires a bounded integer, fraction, or decimal; no exponent notation")
    try:
        return Q(raw)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError("requires a rational such as 3/2") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", required=True, type=int)
    parser.add_argument("--tasks", required=True, type=int)
    parser.add_argument("--inner", required=True, type=_cli_rational)
    parser.add_argument("--outer", required=True, type=_cli_rational)
    parser.add_argument("--epsilon", default=Q(1, 1_000_000), type=_cli_rational)
    args = parser.parse_args()
    try:
        result = optimize_partition(args.agents, args.tasks, args.inner, args.outer, args.epsilon)
    except (ValueError, ArithmeticError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
