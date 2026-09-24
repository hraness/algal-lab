"""Exact-budget partition dynamic programming over rational item profits.

This is a classical additive optimization primitive.  It makes no claim about
the origin or novelty of the recurrence.  Every returned witness consumes the
entire population budget, including when some or all item profits are
negative.
"""

from fractions import Fraction


def _admit(profits: tuple[Fraction, ...], max_groups: int) -> tuple[Fraction, ...]:
    if type(profits) is not tuple:
        raise TypeError("profits must be a tuple")
    if not 1 <= len(profits) <= 128:
        raise ValueError("profits must contain between 1 and 128 values")
    if type(max_groups) is not int:
        raise TypeError("max_groups must be an exact int")
    if not 1 <= max_groups <= 128:
        raise ValueError("max_groups must be between 1 and 128")

    admitted: list[Fraction] = []
    for value in profits:
        if type(value) is int:
            exact = Fraction(value)
        elif type(value) is Fraction:
            exact = value
        else:
            raise TypeError("each profit must be an exact int or Fraction")
        if exact.numerator.bit_length() > 4096 or exact.denominator.bit_length() > 4096:
            raise ValueError("profit numerator and denominator are limited to 4096 bits")
        admitted.append(exact)
    return tuple(admitted)


def maximize_partition(
    profits: tuple[Fraction, ...], max_groups: int
) -> tuple[Fraction, tuple[int, ...], int]:
    """Maximize exact additive profit using exactly ``len(profits)`` units.

    ``profits[m - 1]`` is the profit of a group of size ``m``.  The witness
    contains at most ``max_groups`` positive group sizes, sorted nonincreasingly.
    Ties are resolved deterministically by considering smaller final group
    sizes first; in the capped recurrence, the smallest feasible group count
    wins a tie between final states.  ``transitions`` counts every feasible
    predecessor candidate actually examined by the dynamic program.
    """
    items = _admit(profits, max_groups)
    population = len(items)
    cap = min(population, max_groups)
    transitions = 0

    if max_groups >= population:
        # Exact-budget composition DP.  Every positive composition of b uses
        # at most b groups, so the group cap is automatic in this branch.
        best: list[Fraction | None] = [None] * (population + 1)
        choice = [0] * (population + 1)
        best[0] = Fraction(0)
        for budget in range(1, population + 1):
            optimum: Fraction | None = None
            selected = 0
            for size in range(1, budget + 1):
                previous = best[budget - size]
                # All these predecessor budgets are feasible, including zero.
                assert previous is not None
                transitions += 1
                candidate = previous + items[size - 1]
                if optimum is None or candidate > optimum:
                    optimum = candidate
                    selected = size
            assert optimum is not None
            best[budget] = optimum
            choice[budget] = selected

        sizes: list[int] = []
        remaining = population
        while remaining:
            size = choice[remaining]
            assert 1 <= size <= remaining
            sizes.append(size)
            remaining -= size
        sizes.sort(reverse=True)
        result = best[population]
        assert result is not None
        return result, tuple(sizes), transitions

    # Capped exact-k DP.  None denotes an infeasible state; no state is
    # initialized to zero except the unique empty partition D[0, 0].
    values: list[list[Fraction | None]] = [
        [None] * (population + 1) for _ in range(cap + 1)
    ]
    choices = [[0] * (population + 1) for _ in range(cap + 1)]
    values[0][0] = Fraction(0)

    for groups in range(1, cap + 1):
        for budget in range(groups, population + 1):
            optimum = None
            selected = 0
            # A size m leaves a feasible exact (groups-1)-group partition of
            # budget-m.  Since all group sizes are positive, this range lists
            # precisely the feasible predecessor states.
            sizes_to_check = (
                (budget,)
                if groups == 1
                else range(1, budget - groups + 2)
            )
            for size in sizes_to_check:
                previous = values[groups - 1][budget - size]
                assert previous is not None
                transitions += 1
                candidate = previous + items[size - 1]
                if optimum is None or candidate > optimum:
                    optimum = candidate
                    selected = size
            assert optimum is not None
            values[groups][budget] = optimum
            choices[groups][budget] = selected

    winning_groups = 0
    result = None
    for groups in range(1, cap + 1):
        candidate = values[groups][population]
        if candidate is not None and (result is None or candidate > result):
            result = candidate
            winning_groups = groups
    assert result is not None and winning_groups > 0

    sizes = []
    remaining = population
    groups = winning_groups
    while groups:
        size = choices[groups][remaining]
        assert 1 <= size <= remaining
        sizes.append(size)
        remaining -= size
        groups -= 1
    assert remaining == 0
    sizes.sort(reverse=True)
    return result, tuple(sizes), transitions
