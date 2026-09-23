"""Fixed-bound checks of intact-group factorization and outside-pattern lifting.

For every two-group partition at sizes r=2..7, expand the proposed sorting
gain into integer squarefree monomials and compare every coefficient. Each
term must be a cut-separated quartet contrast times a disjoint nonnegative
monomial. This is an algebra check; the stochastic sign follows from the
separate quartet theorem under its distributional assumptions.

The lifting check sorts complete populations independently. Whenever exactly
two quartet labels are selected, it checks that the outside selected pattern
is fixed by the outside scores and horizon. This implies constancy of every
outside-pattern multiplier on a nonzero quartet contrast.

All fixtures and loop bounds are fixed here. There are no external inputs,
repository imports, optional dependencies, or general theorem claims based
on finite enumeration. verify() is the only public entry point.
"""
from collections.abc import Iterable
from itertools import combinations, permutations, product


def _mask(labels: Iterable[int]) -> int:
    return sum(1 << label for label in labels)


def _polynomial(terms: Iterable[tuple[int, int]]) -> dict[int, int]:
    """Collect exact coefficients, with bitmasks representing monomials."""
    result: dict[int, int] = {}
    for monomial, coefficient in terms:
        result[monomial] = result.get(monomial, 0) + coefficient
    return {monomial: coefficient for monomial, coefficient in result.items()
            if coefficient}


def _telescoping_terms(high: tuple[int, ...], low: tuple[int, ...]
                       ) -> list[tuple[int, int, int]]:
    """Terms in product(high)-product(low), retaining each outside monomial."""
    assert len(high) == len(low)
    return [(high[j], low[j], _mask(high[:j] + low[j + 1:]))
            for j in range(len(high))]


def _symbolic_checks() -> dict[str, int]:
    cases = terms = 0
    by_size = []
    for size in range(2, 8):
        high = tuple(range(size))
        low = tuple(range(size, 2 * size))
        full = (1 << (2 * size)) - 1
        count = 0
        # Require label zero in the first group to enumerate each unordered
        # partition once. The other group is its complement in the 2r labels.
        for rest in combinations(range(1, 2 * size), size - 1):
            original = (0, *rest)
            other = tuple(i for i in range(2 * size) if i not in original)
            p_set = tuple(i for i in original if i < size)
            q_set = tuple(i for i in original if i >= size)
            a_set = tuple(i for i in other if i < size)
            b_set = tuple(i for i in other if i >= size)
            target = _polynomial(((_mask(high), 1), (_mask(low), 1),
                                  (_mask(original), -1), (_mask(other), -1)))

            # (Pi_P-Pi_B)(Pi_A-Pi_Q) is the sorting gain. Expanding its
            # telescoping factors gives the required quartet decomposition.
            expansion = []
            for p, b, left in _telescoping_terms(p_set, b_set):
                for a, q, right in _telescoping_terms(a_set, q_set):
                    quartet = _mask((p, b, a, q))
                    multiplier = left | right
                    assert quartet.bit_count() == 4
                    assert left & right == 0 and multiplier & quartet == 0
                    assert multiplier.bit_count() == size - 2
                    assert max(p, a) < min(b, q)
                    expansion.extend((
                        (multiplier | _mask((p, a)), 1),
                        (multiplier | _mask((b, q)), 1),
                        (multiplier | _mask((p, q)), -1),
                        (multiplier | _mask((b, a)), -1),
                    ))
                    terms += 1
            actual = _polynomial(expansion)
            assert actual == target, (size, original, target, actual)
            assert _mask(original) ^ _mask(other) == full
            cases += 1
            count += 1
        by_size.append(count)
    assert by_size == [3, 10, 35, 126, 462, 1716]
    return {"symbolicPartitionIdentities": cases, "quartetTerms": terms}


def _selected_mask(scores: tuple[int, ...], survivors: int) -> int:
    ordered = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return _mask(ordered[:survivors])


def _lifting_checks() -> dict[str, int]:
    cases = cardinality_two = 0

    def check(scores: tuple[int, ...]) -> None:
        nonlocal cases, cardinality_two
        population = len(scores)
        outside_count = population - 4
        outside = sorted(range(4, population), key=lambda i: (-scores[i], i))
        for survivors in range(population + 1):
            actual = _selected_mask(scores, survivors)
            if (actual & 15).bit_count() == 2:
                selected_outside = survivors - 2
                assert 0 <= selected_outside <= outside_count
                assert actual & ~15 == _mask(outside[:selected_outside])
                cardinality_two += 1
            cases += 1

    # All distinct-score rankings of four focal labels plus zero to three
    # outside labels, with every horizon. Labels 0..3 are always the quartet.
    for outside_count in range(4):
        for scores in permutations(range(4 + outside_count)):
            check(scores)
    tied_cases = 0
    # These fixed grids permit outside ties but exclude focal/outside ties.
    for focal in permutations((1, 3, 5, 7)):
        for outside in product((-2, 0, 2), repeat=3):
            before = cases
            check(focal + outside)
            tied_cases += cases - before
    return {"outsideSelectionCases": cases, "quartetCardinalityTwoCases": cardinality_two,
            "tiedBackgroundCases": tied_cases}


def verify() -> dict[str, int]:
    """Run the fixed integer-algebra and direct-rank checks, with compact output."""
    result = _symbolic_checks()
    result.update(_lifting_checks())
    assert result == {
        "symbolicPartitionIdentities": 2352,
        "quartetTerms": 24024,
        "outsideSelectionCases": 51384,
        "quartetCardinalityTwoCases": 9888,
        "tiedBackgroundCases": 5184,
    }
    return result


if __name__ == "__main__":
    print("stochastic group factorization:", verify())
