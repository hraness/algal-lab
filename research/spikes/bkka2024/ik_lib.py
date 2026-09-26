"""Exact-arithmetic audit library for BKKA2024 (Mathematics 12(6):852; arXiv:2311.17568).

Model: finite mixture with IK(alpha_i, beta_i) components.
    F_i(x)  = (1 - (1+x)^{-a_i})^{b_i}
    f_i(x)  = a_i b_i (1+x)^{-(a_i+1)} (1 - (1+x)^{-a_i})^{b_i - 1}
    Fbar_i  = 1 - F_i
    mixture cdf F_R = sum_i p_i F_i ; rh r~(x) = f_R/F_R.

Substitution: y = (1+x)^{-1} in (0,1), decreasing in x.
    F_i = (1 - y^{a_i})^{b_i};  f_i = a_i b_i y^{a_i+1} (1-y^{a_i})^{b_i-1}.
For integer a_i, b_i everything is polynomial/rational in y -> Sturm.

For common alpha (Thm 3.10): g = 1 - y^a in (0,1), increasing in x.
    F_i = g^{b_i}; f_i = a b_i y^{a+1} g^{b_i-1} (factor a y^{a+1} common).
For rational b_i = k/L substitute g = z^L, z in (0,1) increasing in x.

Monotonicity cheat-sheet (x increasing <-> y decreasing <-> z,g increasing):
  st:  R >=st R*  iff  Fbar_R(x) >= Fbar_R*(x) all x  iff  F_R <= F_R*  all y.
  rh:  R <=rh R*  iff  F_R*/F_R incr. in x  iff  d/dy[F_R*/F_R] <= 0 on (0,1).
  lr:  R >=lr R*  iff  f_R/f_R* incr. in x  iff  d/dy[f_R/f_R*] <= 0 on (0,1).
  R-rh (Thm 3.10): r~_R/r~_R* decr. in x; with g common-alpha variable,
       ratio is rat'l in g (or z), incr. in x iff incr. in g (or z).
"""
from fractions import Fraction
import itertools
import sympy as sp

R = sp.Rational
y = sp.Symbol("y", positive=True)   # y = (1+x)^{-1}
g = sp.Symbol("g", positive=True)   # g = 1-(1+x)^{-a}
z = sp.Symbol("z", positive=True)   # z = g^{1/L}


def Fy(alphas, betas, p):
    """Mixture cdf in y."""
    return sum(pi * (1 - y ** ai) ** bi for pi, ai, bi in zip(p, alphas, betas))


def fy(alphas, betas, p):
    """Mixture pdf in y (pdf w.r.t. x, evaluated at x=1/y-1)."""
    return sum(pi * ai * bi * y ** (ai + 1) * (1 - y ** ai) ** (bi - 1)
               for pi, ai, bi in zip(p, alphas, betas))


def Fg(betas, p):
    """Mixture cdf in g for common alpha."""
    return sum(pi * g ** bi for pi, bi in zip(p, betas))


def fg_core(betas, p):
    """Mixture pdf / (a*y^{a+1}) in g for common alpha: sum p_i b_i g^{b_i-1}."""
    return sum(pi * bi * g ** (bi - 1) for pi, bi in zip(p, betas))


def rh_ratio_g(betas, p, betas_s, p_s):
    """r~_R / r~_R* as a function of g (common alpha): [sum p b g^{b-1} * sum p* g^{b*}]
       / [sum p g^b * sum p* b* g^{b*-1}]."""
    return (fg_core(betas, p) * Fg(betas_s, p_s)) / \
           (Fg(betas, p) * fg_core(betas_s, p_s))


def sturm_roots_on_01(expr, var):
    """Cancel expr to num/den; Sturm-count roots of num on (0,1). Exact."""
    d = sp.cancel(sp.together(expr))
    num, den = sp.fraction(d)
    num = sp.expand(num)
    poly = sp.Poly(num, var)
    nroots = poly.count_roots(0, 1)
    denroots = 0
    if den.has(var):
        denroots = sp.Poly(sp.expand(den), var).count_roots(0, 1)
    return {"num": num, "deg": poly.degree(), "roots_0_1": nroots,
            "den_roots": denroots, "expr": d}


def witnesses(expr, var, pts):
    """Exact rational evaluations expr(var=pt)."""
    return [(pt, sp.sign(expr.subs(var, pt))) for pt in pts]


def sign_at(expr, var, pt):
    return sp.sign(sp.cancel(expr.subs(var, pt)))


# ----------------------------- admissibility -------------------------------
def in_Ln(row1, row2):
    """(row1,row2) in L_n: (r1_i - r1_j)(r2_i - r2_j) <= 0 for all i,j."""
    return all(sp.sign((row1[i] - row1[j]) * (row2[i] - row2[j])) <= 0
               for i in range(len(row1)) for j in range(len(row1)))


def weak_sub(x, yv):
    """x weakly submajorized by y: sums of k largest of x <= y's (Bkka's p* ~_w p)."""
    xs = sorted(x, reverse=True)
    ys = sorted(yv, reverse=True)
    return all(sum(xs[:k]) <= sum(ys[:k]) for k in range(1, len(xs) + 1))


def weak_super(x, yv):
    xs = sorted(x)
    ys = sorted(yv)
    return all(sum(xs[:k]) >= sum(ys[:k]) for k in range(1, len(xs) + 1))


def majorizes(x, yv):
    xs = sorted(x)
    ys = sorted(yv)
    if sum(xs) != sum(ys):
        return False
    return all(sum(xs[:k]) <= sum(ys[:k]) for k in range(1, len(xs)))


def t_pair(row, i, j, w):
    """Apply T = w I + (1-w) Pi_{ij} to a row (right action on 2xn matrix)."""
    out = list(row)
    out[i] = w * row[i] + (1 - w) * row[j]
    out[j] = (1 - w) * row[i] + w * row[j]
    return out


def chain_step(mat, i, j, w):
    return [t_pair(r, i, j, w) for r in mat]
