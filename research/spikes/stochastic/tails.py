"""Exact, fixed-bound checks of stochastic optimality of intact-group counts.

The selection oracle enumerates categorical score assignments and chooses a
uniform subset of the labels tied at the cutoff. This is the exact selected-set
law both for atomic scores with iid continuous tie keys and for histograms
whose conditional distribution is uniform on each common score bin. It does
not use the optimizer, the quartet certificate, or a sorting-exchange proof.

All pair partitions of eight clocks and triple partitions of nine clocks are
compared at three fixed horizons each. A separate oracle enumerates global
key permutations to check the atomic interpretation, including all horizons
of four clocks. Fixed label priority is deliberately tested as a failure case.

These finite checks do not prove the general stochastic theorem. The local
threshold identity is checked separately to expose its algebraic premise.
All fixtures and bounds live here; verify() is the only public entry point.
There are no external inputs, repository imports, or optional dependencies.
"""
from collections.abc import Iterable, Iterator
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb, factorial, lcm, prod


def _mask(labels: Iterable[int]) -> int:
    return sum(1 << label for label in labels)


def _intact_count(selected: int, groups: tuple[int, ...]) -> int:
    return sum(selected & group == group for group in groups)


def _partitions(labels: tuple[int, ...], size: int
                ) -> Iterator[tuple[int, ...]]:
    """Enumerate each unlabeled partition once by fixing its least label."""
    if not labels:
        yield ()
        return
    for rest in combinations(labels[1:], size - 1):
        group = (labels[0], *rest)
        remaining = tuple(label for label in labels if label not in group)
        for tail in _partitions(remaining, size):
            yield (_mask(group), *tail)


def _selection_laws(rows: tuple[tuple[int, ...], ...],
                    horizons: tuple[int, ...]
                    ) -> tuple[dict[int, dict[int, int]], int, int, int]:
    """Integer numerators for the exact uniform-cutoff selected-set laws.

    With common row total M, each bin assignment has probability weight/M**n.
    A cutoff tie of t labels with s slots gives each s-subset probability
    1/choose(t,s). One fixed lcm makes all contributions integer numerators.
    """
    population = len(rows)
    bins = len(rows[0])
    total = sum(rows[0])
    assert all(len(row) == bins and sum(row) == total for row in rows)
    assert all(mass > 0 for row in rows for mass in row)
    assert all(0 <= horizon <= population for horizon in horizons)
    scale = lcm(*(comb(tied, slots) for tied in range(population + 1)
                  for slots in range(tied + 1)))
    denominator = scale * total ** population
    laws: dict[int, dict[int, int]] = {horizon: {} for horizon in horizons}
    cutoff_cache: dict[tuple[int, int], tuple[int, ...]] = {}
    assignments = outcomes = 0
    for values in product(range(bins), repeat=population):
        weight = prod(rows[label][value] for label, value in enumerate(values))
        buckets = [0] * bins
        for label, value in enumerate(values):
            buckets[value] |= 1 << label
        for horizon, law in laws.items():
            above = 0
            remaining = horizon
            for tied in reversed(buckets):
                count = tied.bit_count()
                if remaining > count:
                    above |= tied
                    remaining -= count
                    continue
                key = (tied, remaining)
                if key not in cutoff_cache:
                    labels = tuple(label for label in range(population)
                                   if tied & (1 << label))
                    cutoff_cache[key] = tuple(_mask(subset) for subset in
                                              combinations(labels, remaining))
                choices = cutoff_cache[key]
                assert len(choices) == comb(count, remaining)
                contribution = weight * (scale // len(choices))
                for choice in choices:
                    selected = above | choice
                    assert selected.bit_count() == horizon
                    law[selected] = law.get(selected, 0) + contribution
                    outcomes += 1
                break
            else:
                raise AssertionError("fixed fixture has no cutoff bin")
        assignments += 1
    assert assignments == bins ** population
    for horizon, law in laws.items():
        assert sum(law.values()) == denominator
        assert len(law) == comb(population, horizon)
    return laws, denominator, assignments, outcomes


def _tails(law: dict[int, int], groups: tuple[int, ...]) -> tuple[int, ...]:
    distribution = [0] * (len(groups) + 1)
    for selected, weight in law.items():
        distribution[_intact_count(selected, groups)] += weight
    return tuple(sum(distribution[threshold:])
                 for threshold in range(1, len(groups) + 1))


def _local_identity_checks() -> int:
    cases = 0
    for size in range(2, 5):
        full = (1 << (2 * size)) - 1
        high = (1 << size) - 1
        new = (high, full ^ high)
        for old in _partitions(tuple(range(2 * size)), size):
            for selected in range(full + 1):
                before = _intact_count(selected, old)
                after = _intact_count(selected, new)
                assert (before == 2) == (after == 2)
                for outside_count in range(4):
                    for threshold in range(outside_count + 4):
                        difference = (int(outside_count + after >= threshold)
                                      - int(outside_count + before >= threshold))
                        increment = (int(outside_count + 1 >= threshold)
                                     - int(outside_count >= threshold))
                        assert increment == int(outside_count == threshold - 1)
                        assert difference == increment * (after - before)
                        cases += 1
    assert cases == 212256
    return cases


def _partition_tail_checks() -> dict[str, int | tuple[str, ...]]:
    # Bin indices increase with the score. Earlier rows have lower CDFs and
    # hence stronger scores. The triple fixture needs only CDF order, not
    # stronger hazard or reversed-hazard ordering.
    pair_rows = tuple((10 - rate, rate) for rate in range(8, 0, -1))
    triple_rows = ((1, 5, 9), (2, 4, 9), (3, 4, 8),
                   (4, 3, 8), (5, 5, 5), (6, 4, 5),
                   (7, 4, 4), (8, 4, 3), (9, 4, 2))
    cases = strict = assignments = outcomes = 0
    illustration: dict[str, int | tuple[str, ...]] = {}
    for rows, size, horizons, expected_partitions in (
        (pair_rows, 2, (3, 4, 6), 105),
        (triple_rows, 3, (4, 6, 7), 280),
    ):
        for earlier, later in zip(rows, rows[1:]):
            assert all(sum(earlier[:cut]) <= sum(later[:cut])
                       for cut in range(1, len(earlier) + 1))
        population = len(rows)
        laws, denominator, assignment_count, outcome_count = _selection_laws(
            rows, horizons)
        assignments += assignment_count
        outcomes += outcome_count
        candidates = tuple(_partitions(tuple(range(population)), size))
        assert len(candidates) == expected_partitions
        assert len(set(candidates)) == expected_partitions
        target = tuple(_mask(range(first, first + size))
                       for first in range(0, population, size))
        for horizon, law in laws.items():
            best = _tails(law, target)
            for groups in candidates:
                actual = _tails(law, groups)
                for threshold, (optimal, other) in enumerate(zip(best, actual), 1):
                    assert optimal >= other, (size, horizon, groups, threshold,
                                              optimal, other, denominator)
                    cases += 1
                    strict += optimal > other
            if size == 2 and horizon == 4:
                assert tuple(Fraction(value, denominator) for value in best[:2]) == (
                    Fraction(4555499, 5250000), Fraction(781867, 5250000))
            if size == 3 and horizon == 6:
                # In one-based notation: 123/456/789 versus 147/258/369.
                interleaved = tuple(_mask(range(first, population, size))
                                    for first in range(size))
                illustration["tripleK6ConsecutiveTails"] = tuple(
                    str(Fraction(value, denominator)) for value in best[:2])
                illustration["tripleK6InterleavedTails"] = tuple(
                    str(Fraction(value, denominator))
                    for value in _tails(law, interleaved)[:2])
    assert cases == 3780 and assignments == 19939
    return {"pairPartitions": 105, "triplePartitions": 280,
            "categoricalAssignments": assignments, "cutoffSubsetOutcomes": outcomes,
            "groupTailComparisons": cases, "strictTailComparisons": strict,
            **illustration}


def _key_permutation_laws(rows: tuple[tuple[int, ...], ...]
                         ) -> tuple[dict[int, dict[int, int]], int, int]:
    """Independent oracle: rank each assignment under every global key order.

    The same key permutation is reused at every horizon. Stable sorting by
    score retains that permutation within tied blocks, matching iid keys.
    """
    population = len(rows)
    laws: dict[int, dict[int, int]] = {horizon: {} for horizon in range(population + 1)}
    denominator = sum(rows[0]) ** population * factorial(population)
    cases = 0
    for values in product(range(len(rows[0])), repeat=population):
        weight = prod(rows[label][value] for label, value in enumerate(values))
        for priority in permutations(range(population)):
            ordered = sorted(priority, key=lambda label: values[label], reverse=True)
            selected = 0
            for horizon, law in laws.items():
                if horizon:
                    selected |= 1 << ordered[horizon - 1]
                law[selected] = law.get(selected, 0) + weight
            cases += 1
    assert all(sum(law.values()) == denominator for law in laws.values())
    return laws, denominator, cases


def _atomic_tie_checks() -> dict[str, int]:
    rank_cases = subset_cases = 0
    for rows in (((2, 8), (3, 7), (4, 6), (5, 5)), ((1,),) * 4):
        categorical, cutoff_denominator, _, _ = _selection_laws(rows, tuple(range(5)))
        keyed, key_denominator, cases = _key_permutation_laws(rows)
        rank_cases += cases
        for horizon in range(5):
            assert set(categorical[horizon]) == set(keyed[horizon])
            for selected, numerator in categorical[horizon].items():
                assert numerator * key_denominator == (
                    keyed[horizon][selected] * cutoff_denominator)
                subset_cases += 1
        if len(rows[0]) == 1:
            # With four equal constants, every pair partition has intact-count
            # tail 1/3 under uniform ties. Fixed priority 1>3>2>4 instead selects
            # {1,3}, making the consecutive pairing strictly worse.
            for groups in _partitions(tuple(range(4)), 2):
                assert Fraction(_tails(keyed[2], groups)[0], key_denominator) == Fraction(1, 3)
            priority = (0, 2, 1, 3)
            selected = _mask(priority[:2])
            consecutive = (_mask((0, 1)), _mask((2, 3)))
            competitor = (_mask((0, 2)), _mask((1, 3)))
            assert _intact_count(selected, consecutive) == 0
            assert _intact_count(selected, competitor) == 1
            assert (_intact_count(selected, consecutive)
                    - _intact_count(selected, competitor)) == -1
    assert rank_cases == 408 and subset_cases == 32
    return {"uniformKeyRankings": rank_cases, "uniformKeySubsetComparisons": subset_cases,
            "adversarialPriorityCounterexamples": 1}


def verify() -> dict[str, int | tuple[str, ...]]:
    """Run the fixed exact checks; return counts and two illustrative tail pairs."""
    result: dict[str, int | tuple[str, ...]] = {
        "localThresholdIdentities": _local_identity_checks()}
    result.update(_partition_tail_checks())
    result.update(_atomic_tie_checks())
    return result


if __name__ == "__main__":
    print("stochastic intact-count tails:", verify())
