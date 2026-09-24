"""Exact checks for stochastic-order groups and their hypothesis boundary.

The optimizer constructs no inclusion probabilities. This separate verifier
checks the integral identities, universal quartet gaps and a redundancy
counterexample using independent finite probability calculations.
"""
from fractions import Fraction
from itertools import product

from research.context_certificate import (
    ORDERED_TWO_BACKGROUND_NECESSARY,
    STRICT_ORDERED_TWO_BACKGROUND_NECESSARY,
    universal_gap_minima,
)
from research.rank_selection import ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE
from research.spikes.context.verify import slow_minima
from research.spikes.stochastic.factorization import verify as verify_factorization
from research.spikes.stochastic.tails import verify as verify_tails
from research.spikes.stochastic.block_triples import verify as verify_block_triples
from research.spikes.stochastic.scope_witnesses import verify as verify_scope_witnesses
from research.spikes.stochastic.mixtures import verify as verify_mixtures
from research.spikes.stochastic.hazard_mixtures import verify as verify_hazard_mixtures
from research.spikes.stochastic.softmax_spread import verify as verify_softmax_spread
from research.spikes.stochastic.simplex_spread import verify as verify_simplex_spread
from research.spikes.stochastic.softmax_allocation import verify as verify_softmax_allocation
from research.stochastic_groups import optimal_histogram_groups
from research.test_rank_selection import categorical_oracle


STRICT_REDUNDANT_COUNTEREXAMPLE = [
    [1, 9, 20], [10, 1, 19], [19, 1, 10], [20, 9, 1],
]
WITHIN_PAIR_CROSSINGS = [
    [0, 2, 0, 4], [1, 0, 2, 3], [3, 3, 0, 0], [4, 0, 2, 0],
]


def verify() -> dict[str, object]:
    identities = 0
    positive_coefficients = 0
    for values in product(range(4), repeat=4):
        a, b, c, d = (Fraction(value, 3) for value in values)
        for active in range(4):
            fa, fb, fc, fd = (Fraction(i == active) for i in range(4))
            gap = (d - a) * (c - b)
            derivative = (fd - fa) * (c - b) + (d - a) * (fc - fb)
            integrand = (fa * d - fd * a) * (c - b) + (d - a) * (fb * c - fc * b)
            rhs_b = (c - b) * ((d - b) * fa + 2 * (d - a) * fb + (b - a) * fd)
            rhs_a = (d - a) * (2 * (c - b) * fa + (c - a) * fb + (a - b) * fc)
            assert integrand + fb * gap + b * derivative == rhs_b
            assert integrand + fa * gap + a * derivative == rhs_a
            identities += 2
            if max(a, b) <= min(c, d):
                assert gap >= 0
                assert (rhs_b if b >= a else rhs_a) >= 0
                positive_coefficients += 1

    fixtures = (ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE,
                STRICT_REDUNDANT_COUNTEREXAMPLE, WITHIN_PAIR_CROSSINGS,
                ORDERED_TWO_BACKGROUND_NECESSARY, STRICT_ORDERED_TWO_BACKGROUND_NECESSARY)
    for rows in fixtures:
        certificate = optimal_histogram_groups(rows, 2)
        assert certificate["probabilityEvaluations"] == 0
        order = [label for group in certificate["groups"] for label in group]
        ordered = [rows[label] for label in order]
        # First compares adjacent to crossing; swapping the final two labels
        # compares the same adjacent sum to nested instead.
        assert universal_gap_minima(ordered)[0].value == 0
        assert universal_gap_minima([ordered[i] for i in (0, 1, 3, 2)])[0].value == 0
    for rows in (WITHIN_PAIR_CROSSINGS, STRICT_REDUNDANT_COUNTEREXAMPLE):
        assert slow_minima(rows)[0] == 0
        assert slow_minima([rows[i] for i in (0, 1, 3, 2)])[0] == 0

    rows = STRICT_REDUNDANT_COUNTEREXAMPLE
    assert all(mass > 0 for row in rows for mass in row)
    assert [sum(row) for row in rows] == [30] * 4
    for endpoint in (1, 2):
        numerators = [sum(row[:endpoint]) for row in rows]
        assert all(a < b for a, b in zip(numerators, numerators[1:]))
    q = categorical_oracle(rows, 2)
    pair_sums = (q[0, 1] + q[2, 3], q[0, 2] + q[1, 3], q[0, 3] + q[1, 2])
    assert pair_sums == tuple(Fraction(x, 2025) for x in (1016, 503, 506))
    # Singleton marginals sum to two at top-two selection, so expected
    # working redundant-pair count is 2 minus the matching's pair sum.
    assert (2 - pair_sums[1]) - (2 - pair_sums[2]) == Fraction(1, 675)

    return {**verify_factorization(), **verify_tails(), **verify_block_triples(),
            **verify_scope_witnesses(), **verify_mixtures(), **verify_hazard_mixtures(),
            **verify_softmax_spread(),
            **verify_simplex_spread(),
            **verify_softmax_allocation(),
            "polynomialIdentityCases": identities,
            "nonnegativeDensityCoefficients": positive_coefficients,
            "universalQuartetComparisons": 2 * len(fixtures),
            "independentSlowMinima": 4, "strictRedundancyCounterexamples": 1}


if __name__ == "__main__":
    print("stochastic groups:", verify())
