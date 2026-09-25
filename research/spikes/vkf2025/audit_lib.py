"""Exact-arithmetic audit library for finite (generalized) alpha-mixture claims.

Models audited
--------------
SAF2022 (Shojaee-Asadi-Finkelstein): generalized finite alpha-mixture
    Sbar(t, abar) = [ sum_i p_i Fbar_i(t)^{alpha_i} ]^{1/abar},  abar = sum_i p_i alpha_i
    parametric family Fbar(t|lambda); W_n(p,lambda) denotes the mixture.
    Hazard rate: r(t,abar) = (1/abar) * sum_i alpha_i p_i r_i(t) Fbar_i(t)^{alpha_i}
                                   / sum_j p_j Fbar_j(t)^{alpha_j}.

SKF2026 (Sahoo-Kayal-Finkelstein): finite alpha-mixture, resilience-scaled
components (their eq (1.3)-(1.4)):
    Gbar_U(t) = [ sum_i p_i Gbar(t/theta_i)^{alpha gamma_i} ]^{1/alpha},  alpha != 0
    Gbar_U(t) = prod_i Gbar(t/theta_i)^{p_i gamma_i},                  alpha = 0
    Hazard rate: theta-scaled baseline h times
        htilde(y) = sum_i p_i gamma_i y_i / sum_i p_i y_i,  y_i = Gbar(t/theta_i)^alpha.

Everything is evaluated exactly: with the substitution s = exp(-t/N) (or a
rational t for rational-function baselines) all quantities are rational
functions/numbers. Sign certificates use Sturm root counts (Poly.count_roots)
plus exact rational witnesses, as in verify_core.py.
"""
from fractions import Fraction
import itertools
import sympy as sp

R = sp.Rational
s = sp.Symbol("s", positive=True)  # s = exp(-t/N) in (0,1)


# ---------------------------------------------------------------- utilities
def inc_order(v):
    return tuple(sorted(v))


def dec_order(v):
    return tuple(sorted(v, reverse=True))


def majorizes(x, y):
    """x majorizes y (x ≻ y): lower partial sums of x_(i) are <= y's, equal totals."""
    xs, ys = inc_order(x), inc_order(y)
    if sum(xs) != sum(ys):
        return False
    return all(sum(xs[:k]) <= sum(ys[:k]) for k in range(1, len(xs)))


def weak_super(x, y):
    """x is weakly supermajorized by y, x ≺^w y: sum of k smallest of x >= y's, all k."""
    xs, ys = inc_order(x), inc_order(y)
    return all(sum(xs[:k]) >= sum(ys[:k]) for k in range(1, len(xs) + 1))


def weak_sub(x, y):
    """x is weakly submajorized by y, x ≺_w y: sum of k largest of x <= y's, all k."""
    xs, ys = dec_order(x), dec_order(y)
    return all(sum(xs[:k]) <= sum(ys[:k]) for k in range(1, len(xs) + 1))


def p_larger(x, y):
    """x p-larger than y (Khaledi-Kochar): prod of k smallest of x >= y's? two readings."""
    xs, ys = inc_order(x), inc_order(y)
    return all(sp.prod(xs[:k]) >= sp.prod(ys[:k]) for k in range(1, len(xs) + 1))


def p_larger_dec(x, y):
    """Alternative p-larger convention: products of k LARGEST components."""
    xs, ys = dec_order(x), dec_order(y)
    return all(sp.prod(xs[:k]) >= sp.prod(ys[:k]) for k in range(1, len(xs) + 1))


def is_probability(p):
    return all(pi > 0 for pi in p) and sum(p) == 1


def monotone(v, direction):
    if direction == "inc":
        return all(v[i] <= v[i + 1] for i in range(len(v) - 1))
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1))


def in_Un(p, lam):
    """U_n: (p_i - p_j)(lam_i - lam_j) <= 0 for all i,j (weakly antiordered)."""
    return all((p[i] - p[j]) * (lam[i] - lam[j]) <= 0
               for i in range(len(p)) for j in range(len(p)))


def in_Vn(row1, row2):
    """V_n class of SKF: (y_i - y_j)(z_i - z_j) <= 0."""
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(len(row1)) for j in range(len(row1)))


def in_Wn(row1, row2):
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) >= 0
               for i in range(len(row1)) for j in range(len(row1)))


# ---------------------------------------------------------- SAF2022 model ---
def saf_survival_q(lam, p, alpha, N=1):
    """Fbar(t|lam)=e^{-lam t}: SAF generalized alpha-mixture SF in s = e^{-t/N}.

    lam, alpha rational; exponents alpha_i*lam_i*N must be integers.
    Returns the SF as an expression in s (raised to real power 1/abar only at
    the outer level -- for sign comparisons use saf_sf_pow which keeps the
    inner sum and the outer exponent symbolic).
    """
    terms = [pi * s ** sp.nsimplify(ai * li * N) for pi, ai, li in zip(p, alpha, lam)]
    return sum(terms)


def saf_hazard_q(lam, p, alpha, N=1):
    """Hazard rate of SAF alpha-mixture with exponential components, in s.

    r(t) = (1/abar) sum_i alpha_i p_i lam_i s^{N a_i l_i} / sum_j p_j s^{N a_j l_j}
    (this is r as a function of t, written in s; the outer power of the SF is
    absent because it cancels in f/Fbar)."""
    abar = sum(pi * ai for pi, ai in zip(p, alpha))
    num = sum(ai * pi * li * s ** sp.nsimplify(ai * li * N)
              for pi, ai, li in zip(p, alpha, lam))
    den = sum(pi * s ** sp.nsimplify(ai * li * N) for pi, ai, li in zip(p, alpha, lam))
    return sp.cancel(num / (abar * den))


# ---------------------------------------------------------- SKF2026 model ---
def skf_inner_q(gam, p, alpha, theta, N=1):
    """Inner sum sum_i p_i s^{alpha gam_i N / theta_i} for Gbar(t)=e^{-t}."""
    return sum(pi * s ** sp.nsimplify(alpha * gi * N / ti)
               for pi, gi, ti in zip(p, gam, theta))


def skf_survival_q(gam, p, alpha, theta, N=1):
    """Gbar_U in s for exponential baseline (alpha != 0). Outer power 1/alpha kept."""
    inner = skf_inner_q(gam, p, alpha, theta, N)
    return inner ** (1 / alpha)


def skf_hazard_q(gam, p, alpha, theta, N=1):
    """h_U(t) = (1/theta)*h(t/theta)*htilde(Gbar^alpha) for scalar theta.

    For exponential baseline h=1: h_U = (1/theta) * htilde where
    htilde = sum_i p_i gam_i s^{a g_i N/th} / sum_i p_i s^{a g_i N/th}."""
    th = theta[0] if isinstance(theta, (list, tuple)) else theta
    num = sum(pi * gi * s ** sp.nsimplify(alpha * gi * N / th)
              for pi, gi in zip(p, gam))
    den = sum(pi * s ** sp.nsimplify(alpha * gi * N / th)
              for pi, gi in zip(p, gam))
    return sp.cancel(num / (th * den))


def skf_rh_displayed_q(gam, p, alpha, theta, N=1):
    """The reversed hazard rate DISPLAYED in the proof of SKF Thm 3.11, for
    baseline G(t)=1-e^{-t} (r=g/G).  With x = 1 - s^N = G(t):
        r_U(t) = r(t)/theta * htilde_{p,gam}(G(t/theta)^alpha)
    for scalar theta.  htilde as a function of x in (0,1): we return the
    expression in x-symbol-free form as rational in s:
    htilde(G^alpha) = sum p_i g_i (1-s^N)^{a g_i} / sum p_i (1-s^N)^{a g_i},
    rational in s when a*g_i are integers.
    """
    th = theta if not isinstance(theta, (list, tuple)) else theta[0]
    x = 1 - s ** N
    num = sum(pi * gi * x ** sp.nsimplify(alpha * gi) for pi, gi in zip(p, gam))
    den = sum(pi * x ** sp.nsimplify(alpha * gi) for pi, gi in zip(p, gam))
    return sp.cancel(num / den)  # multiplied by r(t)/theta (positive factor)


def rh_exponential_q(rates, p, N=1):
    """True reversed hazard rate of ordinary exponential mixture (reading b):
    r(t) = sum p_i v_i s^{N v_i} / (1 - sum p_i s^{N v_i})."""
    num = sum(pi * vi * s ** sp.nsimplify(vi * N) for pi, vi in zip(rates, p))
    den = 1 - sum(pi * s ** sp.nsimplify(vi * N) for pi, vi in zip(rates, p))
    return sp.cancel(num / den)


# ------------------------------------------------- sign certification -----
def numerator_of(diff):
    d = sp.cancel(sp.together(diff))
    num, den = sp.fraction(d)
    return sp.expand(num), sp.expand(den), d


def certify_sign_change(diff, var, name=""):
    """diff: expression in var on (0,1), continuous (den checked separately).
    Returns dict with root count and rational witnesses for each interval."""
    num, den, d = numerator_of(diff)
    poly = sp.Poly(num, var)
    nroots = poly.count_roots(0, 1)
    denroots = sp.Poly(den, var).count_roots(0, 1) if den.has(var) else 0
    return {"num": poly, "roots_0_1": nroots, "den_roots": denroots, "expr": d}


def eval_q(expr, val):
    """Exact evaluation at rational s=val."""
    return sp.nsimplify(sp.cancel(expr.subs(s, val)))


def scan_sign(expr, var, grid):
    """Evaluate expr (in var) on a rational grid, return list of (q, sign)."""
    out = []
    for v in grid:
        val = expr.subs(var, v)
        out.append((v, sp.sign(val)))
    return out


def grid(lo_num=1, den=20):
    return [R(k, den) for k in range(lo_num, den)]


# ----------------------------------------------- generic instance check ---
def hr_sign_search(rates_a, rates_b, p, grid_pts):
    """Ordinary exponential mixtures, equal/unequal weights: sign of h_a - h_b."""
    ha = sum(pi * vi * s ** vi for pi, vi in zip(p, rates_a)) / \
        sum(pi * s ** vi for pi, vi in zip(p, rates_a))
    hb = sum(pi * vi * s ** vi for pi, vi in zip(p, rates_b)) / \
        sum(pi * s ** vi for pi, vi in zip(p, rates_b))
    d = sp.cancel(sp.together(ha - hb))
    return [(v, sp.sign(d.subs(s, v))) for v in grid_pts]
