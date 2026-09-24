"""Bounded exact checks for softmax curvature and fixed-score identities.

These finite rational checks supplement analytic arguments. The derivative
cases use arbitrary positive starting weights as algebraic checks; those
weights are not asserted to be exact softmax values at the sampled scores.
"""
from fractions import Fraction as Q
from itertools import product


def _divide_quadratic_series(n, d):
    """Divide coefficient triples (constant, z, z^2) exactly."""
    n0, n1, n2 = n
    d0, d1, d2 = d
    q0 = n0 / d0
    q1 = (n1 - q0 * d1) / d0
    q2 = (n2 - q1 * d1 - q0 * d2) / d0
    return q0, q1, q2


def _softmax_derivatives():
    values = (Q(0), Q(1, 2), Q(1))
    directions = (-1, 0, 1)
    temperatures = (Q(1, 2), Q(1), Q(2))
    checked = curvature_equalities = gradient_checks = 0
    for d in (2, 3):
        weight_sets = (tuple(Q(1) for _ in range(d)),
                       tuple(Q(i) for i in range(1, d + 1)))
        for x, u, weights, c in product(product(values, repeat=d),
                                         product(directions, repeat=d),
                                         weight_sets, temperatures):
            total = sum(weights)
            p = tuple(w / total for w in weights)
            mean_u = sum((pi * ui for pi, ui in zip(p, u)), Q(0))
            b = sum((pi * xi for pi, xi in zip(p, x)), Q(0))
            second = sum((c * pi * (2 + c * (xi - b)) * (ui - mean_u) ** 2
                          for pi, xi, ui in zip(p, x, u)), Q(0))

            # Expand sum w_i (x_i+z u_i)e^(c z u_i) and sum w_i e^(c z u_i)
            # through z^2, then divide the two truncated series exactly.
            d0 = total
            d1 = sum((w * c * ui for w, ui in zip(weights, u)), Q(0))
            d2 = sum((w * c * c * ui * ui / 2 for w, ui in zip(weights, u)), Q(0))
            n0 = sum((w * xi for w, xi in zip(weights, x)), Q(0))
            n1 = sum((w * (ui + c * xi * ui) for w, xi, ui in zip(weights, x, u)), Q(0))
            n2 = sum((w * (c * ui * ui + c * c * xi * ui * ui / 2)
                      for w, xi, ui in zip(weights, x, u)), Q(0))
            ratio_z1 = (n1 - n0 * d1 / d0) / d0
            ratio_z2 = (n2 - n1 * d1 / d0 + n0 * (d1 * d1 / (d0 * d0) - d2 / d0)) / d0
            gradient_dot = sum((pi * (1 + c * (xi - b)) * ui
                                for pi, xi, ui in zip(p, x, u)), Q(0))
            assert ratio_z1 == gradient_dot
            assert 2 * ratio_z2 == second
            assert second >= 0
            assert (second == 0) == (len(set(u)) == 1)
            curvature_equalities += int(second == 0)

            if c <= 1:
                for pi, xi in zip(p, x):
                    grad = pi * (1 + c * (xi - b))
                    assert grad > 0
                    gradient_checks += 1
            checked += 1
    return {"softmaxDerivativeCases": checked,
            "softmaxGradientSeriesChecks": checked,
            "softmaxCurvatureEqualityCases": curvature_equalities,
            "softmaxGradientComponentChecks": gradient_checks,
            "softmaxDerivativeScope": "Exact z and z^2 series-division checks for finite x,u,c and arbitrary positive initial weights."}


def _stationary_transfer_checks():
    xs = ((Q(1, 2),), (Q(1, 2), Q(0)),
          (Q(1, 2), Q(1, 4), Q(0)),
          (Q(1, 2), Q(1, 2), Q(1, 4)),
          (Q(1, 2), Q(1, 2), Q(1, 2)))
    cases = 0
    for x in xs:
        d = len(x)
        weights = tuple(dict.fromkeys((tuple(Q(1) for _ in range(d)),
                                       tuple(Q(i) for i in range(1, d + 1)))))
        for w, v, t in product(weights, (Q(1), Q(2), Q(8)),
                               (Q(1, 2), Q(2), Q(8))):
            betas = (Q(1, 4), Q(1), Q(2))
            if t <= 2:
                betas += (Q(1, 16),)
            for beta in betas:
                tau = beta * t
                # Inner score S(z) is obtained by expanding its numerator and
                # denominator independently for u=(1,0,...).
                d0 = sum(w, Q(0))
                d1 = t * w[0]
                d2 = t * t * w[0] / 2
                n0 = sum((wi * xi for wi, xi in zip(w, x)), Q(0))
                n1 = w[0] * (1 + t * x[0])
                n2 = w[0] * (t + t * t * x[0] / 2)
                s0, s1, s2 = _divide_quadratic_series((n0, n1, n2),
                                                       (d0, d1, d2))
                p = w[0] / d0
                h = 1 + t * (x[0] - s0)
                P = Q(1, 2 + v)
                # The initial outer mean of the three scores is 2*s0/(2+v).
                r0 = 2 * s0 / (2 + v)
                g = 1 + tau * (s0 - r0)
                assert h > 0 and g > 0

                jet = (1, tau * s1, tau * s2 + tau * tau * s1 * s1 / 2)
                neg_jet = (1, -tau * s1,
                           tau * s2 + tau * tau * s1 * s1 / 2)
                score_jets = ((s0, s1, s2), (s0, -s1, s2),
                              (Q(0), Q(0), Q(0)))
                outer_weights = (Q(1), Q(1), v)
                numerator = [Q(0), Q(0), Q(0)]
                denominator = [Q(0), Q(0), Q(0)]
                for weight, ejet, score in zip(outer_weights,
                                               (jet, neg_jet, (Q(1), Q(0), Q(0))),
                                               score_jets):
                    for k in range(3):
                        denominator[k] += weight * ejet[k]
                    numerator[0] += weight * score[0] * ejet[0]
                    numerator[1] += weight * (score[0] * ejet[1] + score[1] * ejet[0])
                    numerator[2] += weight * (score[0] * ejet[2]
                                               + score[1] * ejet[1]
                                               + score[2] * ejet[0])
                _, r1, r2 = _divide_quadratic_series(tuple(numerator),
                                                      tuple(denominator))
                lam = P * g * p * h
                expected = 2 * lam * (t * (1 + 1 / h - 2 * p)
                                       + tau * p * h * (1 + 1 / g))
                assert r1 == 0
                assert 2 * r2 == expected
                assert 2 * r2 > 0
                cases += 1
    return {"stationaryTransferCases": cases,
            "stationaryTransferScope": "Exact quadratic series composition with arbitrary positive rational starting weights; algebraic prior-weight checks, not exact unweighted softmax values."}


def _positivity_and_endpoint_checks():
    positivity_cases = 0
    for p, h, g, beta in product((Q(1, 10), Q(1, 2), Q(1)),
                                  (Q(1, 4), Q(1), Q(2), Q(8)),
                                  (Q(1, 4), Q(1), Q(8)),
                                  (Q(1, 4), Q(1), Q(2))):
        A = 1 + 1 / h - 2 * p + beta * p * h
        decomposed = (1 - p) * (1 + 1 / h) + p * (-1 + 1 / h + beta * h)
        assert A == decomposed
        assert A >= 0
        assert A + beta * p * h / g > 0
        positivity_cases += 1

    endpoint_cases = 0
    for E, C in product((Q(3, 2), Q(2), Q(4)), (Q(0), Q(1), Q(3))):
        for T in set((Q(0), C / 2, C)):
            left = (E + T) / (E + C) - T / (1 + C)
            right = (E * (1 + C - T) + T) / ((E + C) * (1 + C))
            assert left == right
            assert right > 0
            endpoint_cases += 1
    return {"sampledPositivityCases": positivity_cases,
            "zeroRowEndpointCases": endpoint_cases,
            "zeroRowEndpointScope": "Exact finite endpoint comparisons; this does not assert monotonicity of intermediate effort."}


def _fixed_score_identities():
    grid = tuple(Q(j, 4) for j in range(5))
    bases = (Q(1, 2), Q(1), Q(3, 2), Q(2))
    vectors = cases = binary_cases = nonbinary_cases = strict_decreases = 0
    for n in range(1, 5):
        for scores in product(grid, repeat=n):
            vectors += 1
            binary = all(s in (0, 1) for s in scores)
            interior = any(0 < s < 1 for s in scores)
            prior_g = None
            for a in bases:
                F = a**4
                # Use a's integer powers so every operation remains rational.
                f = sum((a**int(4 * s) for s in scores), Q(0))
                fp = sum((s * a**int(4 * s - 4) for s in scores), Q(0))
                fpp = sum((s * (s - 1) * a**int(4 * s - 8) for s in scores), Q(0))
                R = sum((s * a**int(4 * s) for s in scores), Q(0)) / f
                H = F / (F + n - 1)
                G = (F + n - 1) * fp - f
                assert R == F * fp / f
                assert R - H == F * G / (f * (F + n - 1))
                if n == 1:
                    assert R == scores[0]
                    assert H == 1
                # Differentiate G termwise, independently of the f'' identity.
                gprime = sum(((n - 1) * s * (s - 1) * a**int(4 * s - 8)
                              - s * (1 - s) * a**int(4 * s - 4)
                              for s in scores), Q(0))
                assert gprime == (F + n - 1) * fpp
                assert (gprime < 0) == interior
                if F == 1:
                    assert G == n * (sum(scores) - 1)
                if F > 1 and not binary and sum(scores) <= 1:
                    assert R < H
                if binary:
                    ones = sum(scores)
                    assert G == n * (ones - 1)
                    binary_cases += 1
                else:
                    nonbinary_cases += 1
                if prior_g is not None:
                    assert (G < prior_g) if interior else (G == prior_g)
                    strict_decreases += int(interior)
                prior_g = G
                cases += 1
    return {"fixedScoreVectors": vectors,
            "fixedScoreIdentityCases": cases,
            "fixedScoreBinaryCases": binary_cases,
            "fixedScoreNonbinaryCases": nonbinary_cases,
            "fixedScoreStrictDecreaseComparisons": strict_decreases,
            **_global_phase_fixtures(),
            "fixedScoreScope": "Quarter-grid vectors through dimension four; n=1 has H=1 and no meaningful crossover classification."}


def _global_phase_fixtures():
    a, b = Q(4, 5), Q(1, 2)
    assert b / (a - b) == Q(5, 3)
    outcomes = []
    for q, expected in ((Q(21, 20), "P"),
                        (Q(15, 14), "Q"),
                        (Q(11, 10), "H")):
        # q <= 11/10, so log(q) < q-1 <= 1/10 and 10 log(q) < 1.
        assert 1 < q <= Q(11, 10)
        F = q**10
        P = Q(1, 2)
        Q_candidate = (a * q**8 + b * q**5) / (q**8 + q**5 + 1)
        H = F / (F + 2)
        candidates = {"P": P, "Q": Q_candidate, "H": H}
        assert max(candidates.values()) == candidates[expected]
        assert sum(v == candidates[expected] for v in candidates.values()) == 1
        outcomes.append((str(q), expected))
    return {"globalPhaseFixtureCount": len(outcomes),
            "globalPhaseFixtureWinners": tuple(outcomes),
            "lowerThresholdRatio": "5/3",
            "globalPhaseFixtureScope": "Three exact pure-candidate comparisons; analytic proof supplies globality. q values avoid floating logarithms."}


def _pure_assignments_and_certificates():
    concentration = permutation = intermediate = 0
    for assignment in product(range(3), repeat=3):
        counts = tuple(assignment.count(i) for i in range(3))
        kind = tuple(sorted((v for v in counts if v), reverse=True))
        if kind == (3,):
            concentration += 1
        elif kind == (1, 1, 1):
            permutation += 1
        else:
            assert kind == (2, 1)
            intermediate += 1
    assert (concentration, permutation, intermediate) == (3, 6, 18)
    assert 12**5 < 16 * 7**5
    assert Q(2) < Q(3, 2)**2
    r, q = Q(12, 7), Q(3, 2)
    # The fifth-power bound gives 2^(4/5)>r; q bounds sqrt(2) from above.
    # Since gap(r,q) increases in r and decreases in q on this positive range,
    # this is an exact lower certificate for the corresponding radical gap.
    gap = (3 * r - 5) / (10 * (r + q + 1))
    assert gap == Q(1, 295)
    return {"pureThreeByThreeAssignments": concentration + permutation + intermediate,
            "pureThreeByThreeConcentration": concentration,
            "pureThreeByThreePermutation": permutation,
            "pureThreeByThreeIntermediate": intermediate,
            "radicalCertificateChecks": 3,
            "pureAssignmentScope": "All 3^3 deterministic full assignments; radical comparisons use exact integers/rationals."}


def verify():
    return {**_softmax_derivatives(), **_fixed_score_identities(),
            **_pure_assignments_and_certificates(), **_stationary_transfer_checks(),
            **_positivity_and_endpoint_checks()}


if __name__ == "__main__":
    print("softmax integrality:", verify())
