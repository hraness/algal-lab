"""Pilot test for doi:10.37119/jpss2023.v21i1.637 (modified weighted uniform, MWU).

MWU(alpha, lam): survival (1 - lam x)^{alpha+1} on [0, 1/lam]. Theorem (1) as
printed (verified against the page image, since the text layer drops subscripts):
  (i)  alpha1 < alpha2, lam1 = lam2  =>  X <=lr Y, X <=hr Y, X <=st Y
  (ii) alpha1 = alpha2, lam2 > lam1  =>  X <=lr Y, X <=hr Y, X <=st Y
with X ~ MWU(alpha1, lam1), Y ~ MWU(alpha2, lam2). Survivals are polynomials in
x, so every order is decided exactly on the common support (0, min(1/lam)).
A second, direct evaluation at the witness is printed for C3.
"""
import json
from fractions import Fraction as Fr

import sympy as sp

from ratdist import ORDERS, Dist, z

R = sp.Rational


def mwu(alpha, lam, hi):
    return Dist((1 - R(lam) * z) ** (R(alpha) + 1), sp.Integer(0), R(hi), increasing=True)


def direct_survival(alpha, lam, x):
    return max(Fr(0), 1 - Fr(lam) * x) ** (alpha + 1)


out = {}
cases = {
    "Theorem (1)(i): alpha = (0, 1), lam = (1, 1)": ((0, 1), (1, 1)),
    "Theorem (1)(ii): alpha = (1, 1), lam = (1, 2)": ((1, 1), (1, 2)),
}
for name, ((a1, a2), (l1, l2)) in cases.items():
    hi = min(R(1, l1), R(1, l2))
    X, Y = mwu(a1, l1, hi), mwu(a2, l2, hi)
    row = {}
    for order in ("st", "hr", "rh", "lr"):
        holds, witness = ORDERS[order](X, Y)          # claim: X <=order Y
        reverse, _ = ORDERS[order](Y, X)
        row[order] = {"claim_X_le_Y_holds": holds, "witness_x": None if holds else str(witness), "reverse_Y_le_X_holds": reverse}
    x0 = Fr(1, 4)
    row["C3 direct survivals at x = 1/4 (S_X, S_Y); claim X <=st Y needs S_X <= S_Y"] = [
        str(direct_survival(a1, l1, x0)), str(direct_survival(a2, l2, x0))]
    out[name] = row
print(json.dumps(out, indent=1))
