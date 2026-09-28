"""Independent C3 verification for arxiv:1904.08730 refuted records.

Fresh model code (mpmath, 100+ digits). EG2(theta,phi,alpha) as printed:
  F(x) = 1 - (1 - exp(-theta * x^{-phi}))^alpha   x>0
  S(x) =     (1 - exp(-theta * x^{-phi}))^alpha
Series (min) of independent: S_min = prod S_i.
Parallel (max): F_max = prod F_i = prod (1 - S_i).

Checked claims:
  Example 3.3 : X_{1:2} <=st X*_{1:2} on printed numbers
                A=(a; t)=((0.54,0.66),(1.7,1.4)); B=((0.5,0.7),(1.8,1.3))
  Example 3.4 : X_{2:2} >=st X*_{2:2} on printed numbers
                A=((2.34,2.26),(1.32,1.38)); B=((2.1,2.5),(1.5,1.2))
  Theorem 3.10: sum a <= sum a* => X_{1:n} <=lr X*_{1:n}
"""
import json
import os
from fractions import Fraction

from mpmath import mp, mpf, exp, log, diff

mp.dps = 120

HERE = os.path.dirname(os.path.abspath(__file__))


def S(x, theta, phi, alpha):
    """Survival of EG2(theta,phi,alpha)."""
    u = 1 - exp(-mpf(theta) * mpf(x) ** (-mpf(phi)))
    return u ** mpf(alpha)


def f(x, theta, phi, alpha):
    """Density of EG2(theta,phi,alpha)."""
    u = 1 - exp(-mpf(theta) * mpf(x) ** (-mpf(phi)))
    # d/dx u = theta*phi*x^{-phi-1}*exp(-theta x^{-phi})
    du = mpf(theta) * mpf(phi) * mpf(x) ** (-mpf(phi) - 1) * exp(-mpf(theta) * mpf(x) ** (-mpf(phi)))
    return mpf(alpha) * u ** (mpf(alpha) - 1) * du


def S_min(x, params):
    out = mpf(1)
    for (th, ph, al) in params:
        out *= S(x, th, ph, al)
    return out


def S_max(x, params):
    out = mpf(1)
    for (th, ph, al) in params:
        out *= (1 - S(x, th, ph, al))
    return 1 - out


def Tmat(w):
    return [[mpf(w), 1 - mpf(w)], [1 - mpf(w), mpf(w)]]


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)]
            for i in range(2)]


def scan(sign_fn, grid):
    """Return (min value, argmin) over grid."""
    vals = [(sign_fn(t), t) for t in grid]
    return min(vals)


def grid_pts():
    pts = [mpf(10) ** k for k in range(-12, 7)]
    pts += [mpf(i) / 10 for i in range(1, 400)]
    pts += [mpf(i) for i in range(40, 200)]
    return pts


report = {}

# ---------------- Example 3.3 ----------------
# A=(alpha;theta)=((0.54,0.66),(1.7,1.4)); B=(alpha*;theta*)=((0.5,0.7),(1.8,1.3))
A33 = [[mpf("0.54"), mpf("0.66")], [mpf("1.7"), mpf("1.4")]]
B33 = [[mpf("0.5"), mpf("0.7")], [mpf("1.8"), mpf("1.3")]]
# printed equation A = B * T_0.8 ?
prod = matmul(B33, Tmat(mpf("0.8")))
eq_ok = all(abs(prod[i][j] - A33[i][j]) < mpf(10) ** -100 for i in range(2) for j in range(2))
# A >> B would need B = A*P, P doubly stochastic. Unique P = A^{-1}B.
detA = A33[0][0] * A33[1][1] - A33[0][1] * A33[1][0]
Ainv = [[A33[1][1] / detA, -A33[0][1] / detA], [-A33[1][0] / detA, A33[0][0] / detA]]
P = matmul(Ainv, B33)
chain_AB_possible = all(P[i][j] >= 0 for i in range(2) for j in range(2))

def SminA33(x, phi):
    return S_min(x, [(mpf("1.7"), phi, mpf("0.54")), (mpf("1.4"), phi, mpf("0.66"))])

def SminB33(x, phi):
    return S_min(x, [(mpf("1.8"), phi, mpf("0.5")), (mpf("1.3"), phi, mpf("0.7"))])

g = grid_pts()
ex33 = {"printed_eq_A_eq_BT0.8": eq_ok,
        "A_chain_maj_B_possible": chain_AB_possible,
        "AinvB": [[str(P[i][j]) for j in range(2)] for i in range(2)]}
for phi in ["0.5", "1", "2", "3"]:
    dvals = [(t, SminA33(t, mpf(phi)) - SminB33(t, mpf(phi))) for t in g]
    mn = min(v for _, v in dvals)  # printed claim needs S_A - S_B <= 0
    mx = max(v for _, v in dvals)  # reversed needs >= 0
    argmn = [t for t, v in dvals if v == mn][0]
    ex33["phi=%s" % phi] = {"min(SA-SB)": str(mn), "at": str(argmn),
                            "max(SA-SB)": str(mx),
                            "printed_holds": mn >= -mpf(10) ** -60,
                            "reversed_holds": mn >= 0}
report["Example 3.3"] = ex33

# ---------------- Example 3.4 ----------------
A34 = [[mpf("2.34"), mpf("2.26")], [mpf("1.32"), mpf("1.38")]]
B34 = [[mpf("2.1"), mpf("2.5")], [mpf("1.5"), mpf("1.2")]]
prod = matmul(B34, Tmat(mpf("0.4")))  # printed product uses T_0.4 = 0.4I+0.6Pi
eq_ok34 = all(abs(prod[i][j] - A34[i][j]) < mpf(10) ** -100 for i in range(2) for j in range(2))
detA = A34[0][0] * A34[1][1] - A34[0][1] * A34[1][0]
Ainv = [[A34[1][1] / detA, -A34[0][1] / detA], [-A34[1][0] / detA, A34[0][0] / detA]]
P34 = matmul(Ainv, B34)
chain34 = all(P34[i][j] >= 0 for i in range(2) for j in range(2))

def SmaxA34(x, phi):
    return S_max(x, [(mpf("1.32"), phi, mpf("2.34")), (mpf("1.38"), phi, mpf("2.26"))])

def SmaxB34(x, phi):
    return S_max(x, [(mpf("1.5"), phi, mpf("2.1")), (mpf("1.2"), phi, mpf("2.5"))])

ex34 = {"printed_eq_A_eq_BT0.4": eq_ok34,
        "A_chain_maj_B_possible": chain34,
        "AinvB": [[str(P34[i][j]) for j in range(2)] for i in range(2)]}
for phi in ["0.5", "1", "2", "3"]:
    dvals = [(t, SmaxA34(t, mpf(phi)) - SmaxB34(t, mpf(phi))) for t in g]
    mn = min(v for _, v in dvals)
    argmn = [t for t, v in dvals if v == mn][0]
    ex34["phi=%s" % phi] = {"min(SA-SB)": str(mn), "at": str(argmn),
                            "printed_holds": mn >= -mpf(10) ** -60,
                            "reversed_holds": mn >= 0}
report["Example 3.4"] = ex34

# ---------------- Theorem 3.10 ----------------
# X_{1:n} ~ EG2(theta,phi,Sa); X*_{1:n} ~ EG2(theta,phi,Sa*), Sa<=Sa*.
# claim: X <=lr X* i.e. g/f = f*/f non-decreasing in x.
th310 = []
insts = [([1, 1], [2, 2], 1, 1), ([1, 2], [2, 5], 1, 1),
         ([mpf("0.5"), mpf("0.5"), 1], [2, 1, 3], 1, 1),
         ([1, 1], [2, 2], 3, 2), ([1, 2], [2, 5], 3, 2),
         ([mpf("0.5"), mpf("0.5"), 1], [2, 1, 3], 3, 2)]
for aA, aB, th, ph in insts:
    Sa = sum(mpf(a) for a in aA)
    Sb = sum(mpf(b) for b in aB)
    assert Sa <= Sb
    ratio = lambda t: f(t, th, ph, Sb) / f(t, th, ph, Sa)
    # numerical derivative sign + endpoint comparison
    ts = [mpf(10) ** k for k in range(-6, 6)]
    dec_all = all(ratio(ts[i + 1]) < ratio(ts[i]) for i in range(len(ts) - 1))
    r_lo, r_hi = ratio(mpf("0.001")), ratio(mpf("100"))
    th310.append({"Sa": str(Sa), "Sb": str(Sb), "theta": th, "phi": ph,
                  "ratio_lo": str(r_lo), "ratio_hi": str(r_hi),
                  "strictly_decreasing_on_grid": bool(dec_all),
                  "printed_lr_direction_fails": bool(r_hi < r_lo)})
# analytic: d/dx log(f*/f) = (Sb-Sa) * d/dx log u, u=1-e^{-theta x^{-phi}} dec.
report["Theorem 3.10"] = {
    "instances": th310,
    "analytic": "log(f*/f)=const+(Sb-Sa)*log(u); u=1-exp(-theta*x^-phi) "
                "strictly decreasing in x (u->1 as x->0, u->0 as x->oo); "
                "exponent Sb-Sa>=0 => f*/f decreasing => X*_{1:n} <=lr X_{1:n} "
                "(reversed) is what holds"}
print(json.dumps(report, indent=1))
with open(os.path.join(HERE, "c3_verify_1904_08730.out.json"), "w") as fh:
    json.dump(report, fh, indent=1)
