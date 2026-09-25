#!/usr/bin/env python
"""Exact verification of the strict-weight, distinct-rate variant.

Weights p = (2/5, 1/3, 4/15) strictly decreasing; rates lambda = (2, 6, 10) and
gamma = (2, 7, 9) strictly increasing; lambda majorizes gamma; antiordering
(p_i - p_j)(v_i - v_j) < 0 holds strictly for every pair i != j and both rate
vectors.  T = (3/4) I + (1/4) P_23 is doubly stochastic, p T = (2/5, 19/60, 17/60)
and lambda T = gamma.

Checked exactly: the rational hazard values at q = 1/2 and q = 3/4, and the
exact number of sign changes of each hazard difference on (0,1).
"""
import sys

import sympy as sp

R = sp.Rational
q = sp.Symbol("q", positive=True)
RESULTS = []


def check(name, condition):
    ok = bool(condition)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)


def hazard(rates, weights):
    num = sum(w * r * q**r for r, w in zip(rates, weights))
    den = sum(w * q**r for r, w in zip(rates, weights))
    return num / den


def majorizes(x, y):
    xs, ys = sorted(x, reverse=True), sorted(y, reverse=True)
    px = py = 0
    for u, v in zip(xs, ys):
        px, py = px + u, py + v
        if px < py:
            return False
    return px == py


def strictly_antiordered(p, v):
    return all((p[i] - p[j]) * (v[i] - v[j]) < 0
               for i in range(len(p)) for j in range(len(p)) if i != j)


def crossings_in_unit_interval(expr):
    """Exact number of sign changes of a rational function of q on (0,1).

    Returns (number of roots of the numerator in (0,1), list of isolating intervals).
    """
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    num_poly, den_poly = sp.Poly(num, q), sp.Poly(den, q)
    eps = R(1, 10**6)
    assert den_poly.count_roots(eps, 1 - eps) == 0          # no pole inside
    assert den_poly.eval(R(1, 2)) != 0
    # exclude the endpoints: h(0) is common (numerator vanishes at q = 1)
    ivs = [(sp.Rational(x), sp.Rational(y)) for (x, y), k in
           num_poly.intervals(inf=eps, sup=1 - eps, eps=R(1, 10**12))]
    roots = num_poly.count_roots(eps, 1 - eps)
    # verify that there are no roots in (0, eps] or [1 - eps, 1) either
    assert num_poly.count_roots(R(1, 10**30), eps) == 0
    assert num_poly.count_roots(1 - eps, 1 - R(1, 10**30)) == 0
    return roots, ivs


p = (R(2, 5), R(1, 3), R(4, 15))
lam, gam = (2, 6, 10), (2, 7, 9)
check("1 weights sum to one, positive, strictly decreasing",
      sum(p) == 1 and all(x > 0 for x in p) and p[0] > p[1] > p[2])
check("2 lambda majorizes gamma and not conversely",
      majorizes(lam, gam) and not majorizes(gam, lam))
check("3 strict antiordering for (p, lambda) and (p, gamma)",
      strictly_antiordered(p, lam) and strictly_antiordered(p, gam))

h_pl, h_pg = hazard(lam, p), hazard(gam, p)
check("4 fixed weights: h_{p,lambda}(log 2) - h_{p,gamma}(log 2) = 248/4455 > 0",
      sp.nsimplify((h_pl - h_pg).subs(q, R(1, 2))) == R(248, 4455))
check("4' fixed weights: values 898/405 and 214/99 at q = 1/2",
      sp.nsimplify(h_pl.subs(q, R(1, 2))) == R(898, 405)
      and sp.nsimplify(h_pg.subs(q, R(1, 2))) == R(214, 99))
check("5 fixed weights: difference at q = 3/4 (t = log(4/3)) is -26862489/459534895 < 0",
      sp.nsimplify((h_pl - h_pg).subs(q, R(3, 4))) == R(-26862489, 459534895))

T = sp.Matrix([[1, 0, 0], [0, R(3, 4), R(1, 4)], [0, R(1, 4), R(3, 4)]])
check("6 T is doubly stochastic",
      all(x >= 0 for x in T) and all(sum(T.row(i)) == 1 for i in range(3))
      and all(sum(T.col(j)) == 1 for j in range(3)))
pT = list(sp.Matrix([list(p)]) * T)
lamT = list(sp.Matrix([list(lam)]) * T)
check("7 p T = (2/5, 19/60, 17/60) and lambda T = gamma",
      pT == [R(2, 5), R(19, 60), R(17, 60)] and lamT == list(gam))
check("8 (pT, gamma) strictly antiordered, pT strictly decreasing",
      strictly_antiordered(pT, gam) and pT[0] > pT[1] > pT[2])
h_pTg = hazard(gam, pT)
check("9 transformed weights: h_{pT,gamma}(log 2) = 6829/3165, difference 1019/17091 > 0",
      sp.nsimplify(h_pTg.subs(q, R(1, 2))) == R(6829, 3165)
      and sp.nsimplify((h_pl - h_pTg).subs(q, R(1, 2))) == R(1019, 17091))
check("10 transformed weights: difference at q = 3/4 is -399285261/7327839955 < 0",
      sp.nsimplify((h_pl - h_pTg).subs(q, R(3, 4))) == R(-399285261, 7327839955))

# Exact crossing counts on (0,1) (equivalently on t > 0).
for label, diff in (("fixed weights", h_pl - h_pg), ("transformed weights", h_pl - h_pTg)):
    n_roots, ivs = crossings_in_unit_interval(diff)
    print(f"   {label}: {n_roots} sign change(s) of the hazard difference on (0,1)")
    for (x, y) in ivs:
        print(f"      q_* in ({sp.N(x, 12)}, {sp.N(y, 12)}), "
              f"t_* in ({sp.N(-sp.log(y), 12)}, {sp.N(-sp.log(x), 12)})")
    check(f"11 {label}: exactly one crossing on (0,1)", n_roots == 1)
    # sign: negative for q near 1 (small t), positive for q near 0 (large t)
    check(f"12 {label}: negative at q = 99/100, positive at q = 1/100",
          diff.subs(q, R(99, 100)) < 0 and diff.subs(q, R(1, 100)) > 0)

# Both mixtures with common weights are stochastically ordered: S_lambda >= S_gamma.
sdiff = sum(w * q**r for r, w in zip(lam, p)) - sum(w * q**r for r, w in zip(gam, p))
check("13 fixed weights: S_lambda - S_gamma = q^6 (1/3 - (1/3) q + (4/15) q^3 ... ) has no root in (0,1) and is positive",
      sp.Poly(sp.expand(sdiff), q).count_roots(R(1, 10**9), 1 - R(1, 10**9)) == 0
      and sdiff.subs(q, R(1, 2)) > 0)
print("   S_lambda - S_gamma =", sp.factor(sdiff))

failed = [name for name, ok in RESULTS if not ok]
print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
