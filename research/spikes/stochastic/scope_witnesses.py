"""Exact witnesses for prior theorem hypotheses and static-to-rank transfer.

Fixed fixtures only. The subset law enumerates common-bin assignments and
uniform cutoff subsets independently of the grouping optimizer and quartet
formula. These checks refute specific hypothesis implications; they neither
refute the cited theorems nor establish literature priority.
"""
from fractions import Fraction
from itertools import combinations, product
from math import comb


def _subset_law(rows: tuple[tuple[int, ...], ...], survivors: int
                ) -> dict[tuple[int, ...], Fraction]:
    population = len(rows)
    assert 1 <= survivors <= population <= 4
    bins = len(rows[0])
    assert 1 <= bins <= 3
    assert all(len(row) == bins and all(mass > 0 for mass in row) for row in rows)
    result = {chosen: Fraction(0)
              for chosen in combinations(range(population), survivors)}
    for cells in product(range(bins), repeat=population):
        probability = Fraction(1)
        for label, cell in enumerate(cells):
            probability *= Fraction(rows[label][cell], sum(rows[label]))
        cutoff = sorted(cells, reverse=True)[survivors - 1]
        above = tuple(i for i, cell in enumerate(cells) if cell > cutoff)
        tied = tuple(i for i, cell in enumerate(cells) if cell == cutoff)
        slots = survivors - len(above)
        for choice in combinations(tied, slots):
            chosen = tuple(sorted(above + choice))
            result[chosen] += probability / comb(len(tied), slots)
    assert sum(result.values()) == 1
    return result


def verify() -> dict[str, int | tuple[str, ...]]:
    # D'Abadie--Proschan (1983), equation (4.4): given increasing
    # parameter labels (weak, strong), aligned order must have >= weight.
    weak, strong = (2, 4, 9), (1, 5, 9)
    assert sum(weak) == sum(strong) == 15
    assert all(sum(strong[:end]) <= sum(weak[:end]) for end in range(4))
    aligned = Fraction(weak[1] * strong[2],
                       weak[1] * strong[2] + weak[2] * strong[1])
    assert aligned == Fraction(4, 9) < 1 - aligned
    first_aligned = Fraction(weak[0] * strong[1],
                             weak[0] * strong[1] + weak[1] * strong[0])
    assert first_aligned == Fraction(5, 7)
    # Two independent copies conditioned on separate ordered-score pairs.
    psa = (2 * first_aligned - 1) * (2 * aligned - 1)
    assert psa == -Fraction(1, 21)
    raw_psa = Fraction((10 - 4) * (36 - 45), 15 ** 4)
    assert raw_psa == -Fraction(2, 1875)

    # Marichal--Mathonet--Spizzichino (2014 preprint), Definition 8.
    # Positive densities and strictly ordered CDFs throughout (0,2).
    rows = ((1, 4), (2, 3), (3, 2), (4, 1))
    assert all(sum(row) == 5 for row in rows)
    assert all(rows[i][0] < rows[i + 1][0] for i in range(3))
    q = _subset_law(rows, 2)
    left, right = _subset_law(rows[:2], 1), _subset_law(rows[2:], 1)
    assert q == {
        (0, 1): Fraction(48, 125), (0, 2): Fraction(88, 375),
        (0, 3): Fraction(2, 15), (1, 2): Fraction(2, 15),
        (1, 3): Fraction(9, 125), (2, 3): Fraction(16, 375),
    }
    assert left == right == {(0,): Fraction(3, 5), (1,): Fraction(2, 5)}
    ratios = tuple(q[a, b] / (left[a,] * right[b - 2,])
                   for a, b in ((0, 2), (0, 3), (1, 2), (1, 3)))
    assert ratios == (Fraction(88, 135), Fraction(5, 9),
                      Fraction(5, 9), Fraction(9, 20))
    assert len(set(ratios)) > 1

    # Fixed-time reliability ordering need not imply rank ordering, even
    # for independent clocks with positive densities and a strict FOSD chain.
    rows = ((1, 9, 20), (10, 1, 19), (19, 1, 10), (20, 9, 1))
    rank = {size: _subset_law(rows, size) for size in (1, 2, 3)}
    rank[0], rank[4] = {(): Fraction(1)}, {tuple(range(4)): Fraction(1)}
    cdfs = tuple(Fraction(2 * row[0] + row[1], 60) for row in rows)
    states = {}
    for chosen in (subset for size in range(5)
                   for subset in combinations(range(4), size)):
        probability = Fraction(1)
        for i, value in enumerate(cdfs):
            probability *= 1 - value if i in chosen else value
        states[chosen] = probability
    assert sum(states.values()) == 1
    size_law = {size: sum(p for chosen, p in states.items() if len(chosen) == size)
                for size in range(5)}
    assert rank[2][0, 1] == Fraction(989, 2025)
    assert states[0, 1] / size_law[2] == Fraction(31213, 49838)
    assert states[0, 1] / size_law[2] != rank[2][0, 1]

    partitions = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    actuals, top_two = [], []
    for groups in partitions:
        def works(chosen: tuple[int, ...]) -> bool:
            return any(all(i in chosen for i in group) for group in groups)

        tails = [sum(p for chosen, p in rank[size].items() if works(chosen))
                 for size in range(5)]
        signature = [tails[5 - i] - tails[4 - i] for i in range(1, 5)]
        assert sum(signature) == 1 and all(p >= 0 for p in signature)
        actual = sum(p for chosen, p in states.items() if works(chosen))
        mixture = sum(signature[i - 1] * sum(size_law[k] for k in range(5 - i, 5))
                      for i in range(1, 5))
        actuals.append(actual)
        top_two.append(tails[2])
        if groups == partitions[0]:
            assert signature == [0, Fraction(1009, 2025), Fraction(1016, 2025), 0]
            assert actual == Fraction(807751, 1440000)
            assert mixture == Fraction(1460267629, 2916000000)
            assert actual - mixture == Fraction(87714073, 1458000000)
    # Static reliability difference is (p_a-p_b)(p_c-p_d), where p_i
    # is the survival probability. It is >= 0 at every deterministic time
    # under FOSD. At t=3/2 it is positive, but top-two selection reverses it.
    assert actuals[1] - actuals[2] == (cdfs[1] - cdfs[0]) * (cdfs[3] - cdfs[2])
    assert actuals[1] - actuals[2] == Fraction(1, 36)
    assert top_two == [Fraction(x, 2025) for x in (1016, 503, 506)]
    assert top_two[1] - top_two[2] == -Fraction(1, 675)
    return {"conditionalAiCounterexamples": 1,
            "conditionalPsaCounterexamples": 1,
            "signatureDecompositionCounterexamples": 1,
            "signatureSubsetAssignments": 24,
            "staticToRankCounterexamples": 1,
            "signatureMixtureCounterexamples": 1,
            "signatureMixtureRankSets": sum(len(law) for law in rank.values()),
            "incompatibleOccupancyCoefficients": tuple(map(str, ratios))}


if __name__ == "__main__":
    print("prior theorem hypotheses:", verify())
