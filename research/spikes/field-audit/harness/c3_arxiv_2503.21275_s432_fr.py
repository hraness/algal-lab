"""C3 second evaluation: arxiv_2503.21275, Section 4.3.2 FR error-sign rule.

Printed rule: E^r(t) = (r_D - r_I)/r_I is <= 0 iff (gamma>0 & n odd) or
(gamma<0 & n even), and >= 0 in the complementary cases, for all t > 0, where

    F̄_D^P(t) = theta + (-1)^{n-1} prod(S_i) * gamma * prod(1-S_i),
    F̄_I^P(t) = theta = 1 - prod(1 - S_i),    S_i = exp(-lam_i t^alpha_i).

Independent check: express everything as polynomials in z = exp(-t) and use
ratdist.hr (exact Sturm/Vincent root isolation, a different code path than
closedform's interval grid).  hr(X, Y) tests r_X >= r_Y i.e. E^r >= 0.

Result (eval_arxiv_2503.21275.py): REFUTED — E^r is not one-signed in t at
all; r_D - r_I crosses zero in every (n, gamma) case tested.
"""

import sympy as sp
import ratdist
from ratdist import z

R = sp.Rational


def fgmw_par_z(n, gam):
    """FGMW parallel survivals as polynomials in z = e^{-t} (lam_i=alpha_i=1)."""
    s = z                        # S_i = z for each component
    prodS = s ** n
    prodC = (1 - s) ** n
    theta = 1 - prodC
    SDp = sp.expand(theta + (-1) ** (n - 1) * prodS * R(gam) * prodC)
    return SDp, sp.expand(theta)


def dist(expr):
    return ratdist.Dist(expr, sp.Integer(0), sp.Integer(1), increasing=False)


if __name__ == "__main__":
    for n, gam in [(2, R(1, 2)), (2, R(-1, 2)), (3, R(1, 2)), (3, R(-1, 2))]:
        SDp, SIp = fgmw_par_z(n, gam)
        X, Y = dist(SDp), dist(SIp)
        # r_D >= r_I  <=>  hr(X, Y)   (E^r >= 0)
        h_geq = ratdist.hr(X, Y)
        # r_D <= r_I  <=>  hr(Y, X)   (E^r <= 0)
        h_leq = ratdist.hr(Y, X)
        pred_leq = ((gam > 0) and n % 2 == 1) or ((gam < 0) and n % 2 == 0)
        print(f"n={n} gamma={gam}: printed predicts E^r<=0 ? {pred_leq}")
        print(f"   E^r >= 0 everywhere? {h_geq}")
        print(f"   E^r <= 0 everywhere? {h_leq}")
        # spot witnesses: hazard-difference numerator at a few rational z
        fD = sp.diff(SDp, z)          # density prop to -dS/dt = dS/dz up to |dz/dt|
        fI = sp.diff(SIp, z)
        num = sp.expand(fD * SIp - fI * SDp)
        print("   sign poly values: z=1/2:", num.subs(z, R(1, 2)),
              " z=9/10:", num.subs(z, R(9, 10)),
              " z=99/100:", num.subs(z, R(99, 100)))
