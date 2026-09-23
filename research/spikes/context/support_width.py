"""Bounded independent checks of support-width rank-selection compression.

The oracle sorts whole populations; it imports no rank-selection implementation
or symbolic probability formula. All bounds and fixtures are fixed in this
module. The only public entry point, verify(), accepts no external inputs.

Coverage is finite, not a substitute for the mathematical proofs:

* For 1 <= d <= 6 and 0 <= s <= 6, test every background multiset on three
  levels, every horizon and support interval, and every focal gap pattern.
  One focal label order suffices here: relabeling preserves both selected
  prefixes, whose equality is checked whenever the support interval is hit.
* For d=3, test all 256 Boolean set rewards against all contexts with at most
  three backgrounds on five levels. Enumerating all focal label orders and
  gap patterns represents every comparison cell for these contexts. Search
  replacement contexts by their complete reward signatures, independently
  of the proposed active-rank minimum formula. This minimum search concerns
  the five-level family; arbitrary-real sharpness needs the theorem's proof.
* Check 20 specified homogeneous harmonic products and one mixed-degree
  counterexample. These are fixtures, not all harmonic polynomials.

Finite comparisons use integer scores. Background ties and infinite padding
are included; focal ties and focal/background ties are outside this checker.
"""
from collections.abc import Iterator, Sequence
from itertools import combinations_with_replacement, permutations
from math import inf


def _focal_patterns(focal: int, levels: tuple[int, ...],
                    labelled: bool = False) -> Iterator[tuple[int, ...]]:
    """Represent every strict focal order and gap placement, as requested.

    Comparisons to the background levels depend only on the gap containing
    each focal score. In sorted focal order these gap indices are weakly
    increasing, so combinations_with_replacement is exhaustive. Scale the
    levels by focal+1 and put score number j strictly inside its gap using
    integer offset j+1. Permuting labels covers all labeled order cells.
    """
    orders = list(permutations(range(focal))) if labelled else [tuple(range(focal))]
    for gaps in combinations_with_replacement(range(len(levels) + 1), focal):
        values = []
        for position, gap in enumerate(gaps):
            lower = levels[gap - 1] if gap else levels[0] - 1
            upper = levels[gap] if gap < len(levels) else levels[-1] + 1
            values.append(lower * (focal + 1) + (upper - lower) * (position + 1))
        for order in orders:
            scores = [0] * focal
            for label, value in zip(order, values):
                scores[label] = value
            yield tuple(scores)


def _selected_focal_mask(focal: tuple[int, ...], background: Sequence[int | float],
                         survivors: int) -> int:
    """Direct combined-population sorting, with distinct focal/background IDs."""
    population = [(value, label) for label, value in enumerate(focal)]
    population += [(value, -index - 1) for index, value in enumerate(background)]
    population.sort(reverse=True)
    return sum(1 << label for _, label in population[:survivors] if label >= 0)


def _order_statistic(ordered: tuple[int, ...], index: int) -> int | float:
    if index <= 0:
        return inf
    if index > len(ordered):
        return -inf
    return ordered[index - 1]


def _support_interval_checks() -> int:
    cases = 0
    levels = (0, 1, 2)
    for focal in range(1, 7):
        for count in range(7):
            for values in combinations_with_replacement(levels, count):
                background = tuple(value * (focal + 1) for value in reversed(values))
                for scores in _focal_patterns(focal, levels):
                    for survivors in range(focal + count + 1):
                        original = _selected_focal_mask(scores, background, survivors)
                        size = original.bit_count()
                        for lower in range(focal + 1):
                            for upper in range(lower, focal + 1):
                                retained = tuple(
                                    _order_statistic(background, index)
                                    for index in range(survivors - upper,
                                                       survivors - lower + 2)
                                )
                                reduced = _selected_focal_mask(scores, retained, upper + 1)
                                reduced_size = reduced.bit_count()
                                context = (focal, background, scores, survivors, lower, upper)
                                assert ((lower <= size <= upper)
                                        == (lower <= reduced_size <= upper)), context
                                if lower <= size <= upper:
                                    assert original == reduced, context

                                first = max(1, lower)
                                last = min(focal, upper + 1)
                                endpoint_retained = tuple(
                                    _order_statistic(background, index)
                                    for index in range(survivors - last + 1,
                                                       survivors - first + 2)
                                )
                                endpoint_reduced = _selected_focal_mask(
                                    scores, endpoint_retained, last)
                                endpoint_size = endpoint_reduced.bit_count()
                                assert endpoint_size == min(max(size, first - 1), last), context
                                assert ((lower <= size <= upper)
                                        == (lower <= endpoint_size <= upper)), context
                                if lower <= size <= upper:
                                    assert original == endpoint_reduced, context
                                cases += 1
    return cases


def _active_ranks(reward: Sequence[int], focal: int) -> set[int]:
    active = set()
    for selected in range(1 << focal):
        for label in range(focal):
            if (not (selected >> label) & 1
                    and reward[selected] != reward[selected | (1 << label)]):
                active.add(selected.bit_count() + 1)
    return active


def _minimum_background_checks() -> dict[str, int]:
    focal = 3
    levels = (0, 1, 2, 3, 4)
    score_vectors = list(_focal_patterns(focal, levels, labelled=True))
    contexts = []
    for count in range(4):
        for values in combinations_with_replacement(levels, count):
            background = tuple(value * (focal + 1) for value in reversed(values))
            for survivors in range(focal + count + 1):
                masks = tuple(_selected_focal_mask(scores, background, survivors)
                              for scores in score_vectors)
                contexts.append((count, survivors, background, masks))

    cases = 0
    reward_count = 1 << (1 << focal)
    for truth_table in range(reward_count):
        reward = tuple((truth_table >> selected) & 1 for selected in range(1 << focal))
        active = _active_ranks(reward, focal)
        signatures = []
        minimum: dict[bytes, int] = {}
        for count, _, _, masks in contexts:
            signature = bytes(reward[selected] for selected in masks)
            signatures.append(signature)
            # Contexts were generated in increasing background count, so this
            # finds the true minimum in the enumerated family without a formula.
            minimum.setdefault(signature, count)
        for (count, survivors, background, masks), signature in zip(contexts, signatures):
            feasible = range(max(1, survivors - count + 1), min(focal, survivors) + 1)
            relevant = active.intersection(feasible)
            predicted = max(relevant) - min(relevant) + 1 if relevant else 0
            assert minimum[signature] == predicted, (
                truth_table, background, survivors, predicted, minimum[signature])
            if relevant:
                first, last = min(relevant), max(relevant)
                retained = tuple(_order_statistic(background, index)
                                 for index in range(survivors - last + 1,
                                                    survivors - first + 2))
                assert all(reward[_selected_focal_mask(scores, retained, last)]
                           == reward[selected]
                           for scores, selected in zip(score_vectors, masks))
            else:
                horizon = max(0, survivors - count)
                assert all(reward[_selected_focal_mask(scores, (), horizon)]
                           == reward[selected]
                           for scores, selected in zip(score_vectors, masks))
            cases += 1
    return {"minimumFocalOrderCells": len(score_vectors), "minimumContexts": len(contexts),
            "booleanRewards": reward_count, "minimumRewardContextCases": cases}


def _harmonic_checks() -> dict[str, int]:
    tested = 0
    for focal in range(2, 10):
        for degree in range(1, focal // 2 + 1):
            reward = []
            for selected in range(1 << focal):
                value = 1
                # Each factor uses disjoint coordinates and its two partial
                # derivatives cancel. Their product is homogeneous harmonic.
                for pair in range(degree):
                    value *= (((selected >> (2 * pair)) & 1)
                              - ((selected >> (2 * pair + 1)) & 1))
                reward.append(value)
            support = sorted({selected.bit_count() for selected, value in enumerate(reward)
                              if value})
            active = sorted(_active_ranks(reward, focal))
            assert support == list(range(degree, focal - degree + 1))
            assert active[0] == degree and active[-1] == focal - degree + 1
            assert active[-1] - active[0] + 1 == focal - 2 * degree + 2
            tested += 1

    # (x1-x2)(1+x3-x4) is harmonic but has degrees one and two. Its
    # support/active span refutes using the highest harmonic degree alone.
    mixed = []
    for selected in range(16):
        x = [(selected >> label) & 1 for label in range(4)]
        mixed.append((x[0] - x[1]) * (1 + x[2] - x[3]))
    assert sorted({selected.bit_count() for selected, value in enumerate(mixed)
                   if value}) == [1, 2, 3]
    assert sorted(_active_ranks(mixed, 4)) == [1, 2, 3, 4]
    return {"homogeneousHarmonicProducts": tested, "mixedDegreeCounterexamples": 1}


def verify() -> dict[str, int]:
    """Run the fixed finite enumeration and return compact comparison counts."""
    results = {"supportIntervalCases": _support_interval_checks()}
    results.update(_minimum_background_checks())
    results.update(_harmonic_checks())
    assert results == {
        "supportIntervalCases": 3_915_366,
        "minimumFocalOrderCells": 336,
        "minimumContexts": 364,
        "booleanRewards": 256,
        "minimumRewardContextCases": 93_184,
        "homogeneousHarmonicProducts": 20,
        "mixedDegreeCounterexamples": 1,
    }
    return results


if __name__ == "__main__":
    print("support-width context reduction:", verify())
