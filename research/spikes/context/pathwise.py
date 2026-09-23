"""Bounded rank-event checks for rewards supported on one focal cardinality.

These compare the selected label sets directly. They use neither probabilities
nor the independent-clock CDF identity. All enumeration bounds are fixed here.
"""
from itertools import combinations, permutations, product
from math import inf


def selected_focal(scores: list[int | float], focal: int, survivors: int) -> frozenset[int]:
    # The same focal-label tie order is preserved after background reduction.
    ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return frozenset(i for i in ranked[:survivors] if i < focal)


def check_case(scores: list[int | float], focal: int) -> int:
    assert not set(scores[:focal]) & set(scores[focal:])
    background = sorted(scores[focal:], reverse=True)
    comparisons = 0
    for cardinality in range(1, focal):
        for survivors in range(len(scores) + 1):
            original = selected_focal(scores, focal, survivors)
            m = survivors - cardinality
            if not 0 <= m <= len(background):
                assert len(original) != cardinality
                continue
            upper = inf if m == 0 else background[m - 1]
            lower = -inf if m == len(background) else background[m]
            reduced = selected_focal(scores[:focal] + [lower, upper], focal, cardinality + 1)
            original_event = original if len(original) == cardinality else None
            reduced_event = reduced if len(reduced) == cardinality else None
            assert original_event == reduced_event, (scores, focal, cardinality, survivors)
            comparisons += 1
    return comparisons


def verify() -> dict[str, int]:
    distinct = 0
    for focal in range(2, 6):
        for background in range(min(3, 7 - focal) + 1):
            for scores in permutations(range(focal + background)):
                distinct += check_case(list(scores), focal)
    background_ties = sum(check_case([1, 3, 5, 7] + list(bg), 4)
                          for bg in product((-2, 0, 2, 4, 6, 8), repeat=3))
    focal_ties = 0
    for focal in range(2, 5):
        for values in product((-1, 1, 3), repeat=focal):
            for count in range(3):
                for bg in product((-2, 0, 2, 4), repeat=count):
                    focal_ties += check_case(list(values + bg), focal)
    support_checks = 0
    for coefficients in ({(0, 1): 1, (2, 3): 1, (0, 2): -1, (1, 3): -1},
                         {(0, 2): 1, (1, 3): 1, (0, 3): -1, (1, 2): -1}):
        for size in (0, 1, 3, 4):
            for selected in combinations(range(4), size):
                assert sum(coefficients.get(pair, 0) for pair in combinations(selected, 2)) == 0
                support_checks += 1
    return {"distinctScoreComparisons": distinct, "tiedBackgroundComparisons": background_ties,
            "focalTieComparisons": focal_ties, "quartetSupportChecks": support_checks}


if __name__ == "__main__":
    print("pathwise context reduction:", verify())
