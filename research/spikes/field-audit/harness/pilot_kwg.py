"""Pilot tests for doi:10.1080/02331888.2025.2552185 (Kumaraswamy-G random extremes).

Standing assumptions of Section 3.2 (text before Theorem 3.5): independent
components (psi = e^{-x}) and a common random sample size N. With alpha = beta = 1
the Kw-G survival is Gbar^gamma, so the random minimum has survival
  P(X_{1:N} > x) = sum_m P(N = m) Gbar(x)^{gamma_1 + ... + gamma_m},
a mixture over partial sums in index order. Exponential baseline G = H
(r_g = r_h, allowed by r_g <= r_h), s = e^{-x}; exponents are made integral by
s = w^2. Decided exactly by ratdist.
  Theorem 3.7: sum gamma <= sum delta  iff  X_{1:N} >=hr Y_{1:N}.
  Theorem 3.8: delta majorized by gamma (equal sums)  =>  X_{1:N} >=hr Y_{1:N}.
"""
import json
from fractions import Fraction as Fr

import sympy as sp

from ratdist import Dist, hr, st, z

R = sp.Rational


def random_minimum(gammas, pmf, scale=2):
    """pmf: {m: P(N = m)}; survival in w with s = w^scale."""
    total = 0
    for m, p in pmf.items():
        exponent = sum(R(g) for g in gammas[:m]) * scale
        assert exponent.q == 1
        total += R(p) * z ** int(exponent)
    return Dist(sp.expand(total), sp.Integer(0), sp.Integer(1), increasing=False)


def majorized(a, b):
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(sum(A[:k]) <= sum(B[:k]) for k in range(1, len(A)))


pmf = {2: R(1, 2), 3: R(1, 2)}
out = {}

g7, d7 = [2, 2, R(1, 2)], [1, 1, 3]
X, Y = random_minimum(g7, pmf), random_minimum(d7, pmf)
holds, w = hr(Y, X)                                   # claim: Y <=hr X
out["Theorem 3.7, gamma = (2, 2, 1/2), delta = (1, 1, 3), N uniform on {2, 3}"] = {
    "sum_gamma_le_sum_delta": sum(R(v) for v in g7) <= sum(R(v) for v in d7),
    "claim_X_ge_hr_Y_holds": holds, "witness_w": None if holds else str(w)}

g8, d8 = [3, 2, 1], [2, 2, 2]
X, Y = random_minimum(g8, pmf), random_minimum(d8, pmf)
holds, w = hr(Y, X)
st_holds, w_st = st(Y, X)
out["Theorem 3.8, gamma = (3, 2, 1), delta = (2, 2, 2), N uniform on {2, 3}"] = {
    "delta_majorized_by_gamma": majorized(d8, g8),
    "claim_X_ge_hr_Y_holds": holds, "witness_w": None if holds else str(w),
    "even_X_ge_st_Y_holds": st_holds, "st_witness_w": None if st_holds else str(w_st)}

# Reading R2 of Theorem 3.7: the sum condition holds for every sample size m that N
# can take (partial sums gamma_1..m <= delta_1..m), not only for the maximal n.
g7b, d7b = [1, 1, 1], [1, 1, 18]
X, Y = random_minimum(g7b, pmf), random_minimum(d7b, pmf)
holds, w = hr(Y, X)
out["Theorem 3.7 under reading R2, gamma = (1, 1, 1), delta = (1, 1, 18), N uniform on {2, 3}"] = {
    "partial_sums_ok_for_m_2_3": all(sum(R(v) for v in g7b[:m]) <= sum(R(v) for v in d7b[:m]) for m in (2, 3)),
    "claim_X_ge_hr_Y_holds": holds, "witness_w": None if holds else str(w)}

# C3: direct evaluation of the survival functions at x = 1 (s = e^{-1}), exact in s.
s = sp.exp(-1)
out["C3 Theorem 3.8 survivals at x = 1: (S_X, S_Y); claim needs S_X >= S_Y"] = [
    str(sp.N((s ** 5 + s ** 6) / 2, 12)), str(sp.N((s ** 4 + s ** 6) / 2, 12))]
print(json.dumps(out, indent=1, default=str))
