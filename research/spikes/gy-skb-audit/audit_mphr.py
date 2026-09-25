"""Exact audit kernels for MPHR/MPRHR alpha-mixture ordering claims (GY2024, SKB2026).

Models
------
GY2024 (Guo-Yan arXiv:2407.15638v2): ordinary finite mixture of MPHR components
    Fbar_C(x) = sum_i p_i * a_i*y/(1-(1-a_i)*y),   y = Fbar(x)^lam in (0,1)
    hazard  r_C(x) = lam*h(x) * Cker(y),  Cker(y) = [sum p_i a_i M_i^-2]/[sum p_i a_i M_i^-1]
    with M_i = 1 - (1-a_i) y.   Claimed (Thm 5/6): V >=_hr W  <=>  Cker_V >= Cker_W.

SKB2026 (Sahoo-Kayal-Balakrishnan, Mathematics 14:2557): alpha-mixture of MPHR
components, common mphr-parameter beta:
    Gbar_W = [sum p_i Gbar_i^a]^{1/a}, Gbar_i = th_i y/(1-(1-th_i)y), y = Gbar^beta
    hazard  h_W = beta*h(t) * Aker(y),
        Aker = [sum p_i th_i^a (1-thb_i y)^(-a-1)]/[sum p_i th_i^a (1-thb_i y)^(-a)]
    reversed hazard r_W = beta*y*h(t)/(1-y) * Bker(y),
        Bker = [sum p_i th_i (1-thb_i y)^(-a-1)]/[sum p_i (1-thb_i y)^(-a)]
MPRHR dual (u = G^xi in (0,1)):
    h_Wtilde = xi*u*r_b/(1-u) * Bker(u);   r_Wtilde = xi*r_b * Aker(u).

All kernels are rational functions of y for integer a. Sign certificates via
Sturm root counts on (0,1).
"""
from fractions import Fraction
import itertools
import sympy as sp

R = sp.Rational
y = sp.Symbol("y", positive=True)  # in (0,1)


def inc_order(v):
    return tuple(sorted(v))


def in_Vn(row1, row2):
    """V_n: rows weakly antiordered, (a_i-a_j)(b_i-b_j) <= 0."""
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(len(row1)) for j in range(len(row1)))


def in_Wn(row1, row2):
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) >= 0
               for i in range(len(row1)) for j in range(len(row1)))


def is_probability(p):
    return all(pi > 0 for pi in p) and sum(p) == 1


def t_transform_matrix(n, i, j, w):
    """T = w I + (1-w) P_{ij} acting on the RIGHT of row vectors (B = A T)."""
    M = sp.eye(n) * w
    M[i, i] = w
    M[j, j] = w
    M[i, j] = 1 - w
    M[j, i] = 1 - w
    return sp.Matrix(M)


def apply_T(row1, row2, n, i, j, w):
    """(q;gm) = (p;th) T : each row mixed on columns i,j with weight w."""
    r1 = list(row1)
    r2 = list(row2)
    q1 = list(r1)
    q2 = list(r2)
    q1[i] = w * r1[i] + (1 - w) * r1[j]
    q1[j] = w * r1[j] + (1 - w) * r1[i]
    q2[i] = w * r2[i] + (1 - w) * r2[j]
    q2[j] = w * r2[j] + (1 - w) * r2[i]
    return tuple(q1), tuple(q2)


# ------------------------------------------------------------- GY2024 kernel
def gy_Cker(p, a):
    """Mixture-hazard kernel for ordinary MPHR mixture (p_i, a_i) columns."""
    terms_num = [pi * ai / (1 - (1 - ai) * y) ** 2 for pi, ai in zip(p, a)]
    terms_den = [pi * ai / (1 - (1 - ai) * y) for pi, ai in zip(p, a)]
    return sp.cancel(sum(terms_num) / sum(terms_den))


def gy_sf(p, a):
    return sum(pi * ai * y / (1 - (1 - ai) * y) for pi, ai in zip(p, a))


# ------------------------------------------------------------- SKB2026 kernels
def skb_Aker(p, th, a):
    """MPHR mixture hazard kernel (and MPRHR reversed-hazard kernel)."""
    num = sum(pi * thi ** a * (1 - (1 - thi) * y) ** (-a - 1)
              for pi, thi in zip(p, th))
    den = sum(pi * thi ** a * (1 - (1 - thi) * y) ** (-a)
              for pi, thi in zip(p, th))
    return sp.cancel(num / den)


def skb_Bker(p, th, a):
    """MPHR mixture reversed-hazard kernel (and MPRHR hazard kernel)."""
    num = sum(pi * thi * (1 - (1 - thi) * y) ** (-a - 1)
              for pi, thi in zip(p, th))
    den = sum(pi * (1 - (1 - thi) * y) ** (-a)
              for pi, thi in zip(p, th))
    return sp.cancel(num / den)


def skb_sf_inner(p, th, a, beta=1):
    """Inner sum sum p_i Gbar_i^a for MPHR components, y = Gbar^beta."""
    return sum(pi * (thi * y / (1 - (1 - thi) * y)) ** a
               for pi, thi in zip(p, th))


def skb_cdf_inner(p, th, a):
    """Inner sum sum p_i G_i^a, G_i = (1-y)/(1-(1-th_i)y)."""
    return sum(pi * ((1 - y) / (1 - (1 - thi) * y)) ** a
               for pi, thi in zip(p, th))


def mprhr_sf_inner(p, th, a):
    """MPRHR SF inner sum: SF_i = (1-u)/(1-(1-th_i)u), u = G^xi."""
    return skb_cdf_inner(p, th, a)


def mprhr_cdf_inner(p, th, a):
    """MPRHR CDF inner sum: G_i = th_i u/(1-(1-th_i)u)."""
    return skb_sf_inner(p, th, a)


# --------------------------------------------------------- sign certification
def numerator_of(diff, var=y):
    d = sp.cancel(sp.together(diff))
    num, den = sp.fraction(d)
    return sp.expand(num), sp.expand(den), d


def certify(diff, var=y, name=""):
    num, den, d = numerator_of(diff, var)
    poly = sp.Poly(num, var)
    nroots = poly.count_roots(0, 1)
    den_roots = sp.Poly(den, var).count_roots(0, 1) if den.has(var) else 0
    return {"num": poly, "roots": nroots, "den_roots": den_roots, "expr": d}


def sign_at(expr, v, var=y):
    return sp.sign(sp.cancel(expr.subs(var, v)))


GRID = [R(1, 16), R(1, 8), R(1, 5), R(1, 4), R(1, 3), R(2, 5), R(1, 2),
        R(3, 5), R(2, 3), R(3, 4), R(4, 5), R(7, 8), R(9, 10), R(15, 16),
        R(19, 20), R(39, 40), R(99, 100)]
