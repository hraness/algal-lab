#!/usr/bin/env python
"""Exact re-verification of the three-component example and the padded family.

Independent of the repository: only sympy is used.  Every check is exact:
rational arithmetic, polynomial identities in the symbols q = exp(-t) and m,
and exact real-root counting (Sturm sequences) for the crossing points.

Run:  /path/to/venv/python verify_core.py
Exit status 0 means every check passed.
"""
import sys

import sympy as sp

R = sp.Rational
q = sp.Symbol("q", positive=True)   # q = exp(-t), so 0 < q < 1 for t > 0
m = sp.Symbol("m", positive=True)   # number of common rate-one components

RESULTS = []


def check(name, condition):
    ok = bool(condition)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)


def survival(rates, weights):
    return sum(w * q**r for r, w in zip(rates, weights))


def hazard(rates, weights):
    """Hazard rate of the mixture, h(t) = -S'(t)/S(t), written in q = exp(-t)."""
    num = sum(w * r * q**r for r, w in zip(rates, weights))
    den = sum(w * q**r for r, w in zip(rates, weights))
    return num / den


def majorizes(x, y):
    """x majorizes y: decreasing partial sums of x dominate those of y, equal totals."""
    xs, ys = sorted(x, reverse=True), sorted(y, reverse=True)
    assert len(xs) == len(ys)
    px = py = 0
    for a, b in zip(xs, ys):
        px, py = px + a, py + b
        if px < py:
            return False
    return px == py


def bracket(mm):
    """B_m(q) = m (1 - 2 q) - q^3 (1 + q)."""
    return mm * (1 - 2 * q) - q**3 * (1 + q)


def target_difference(mm):
    """Claimed closed form of h_lambda - h_gamma for the padded family."""
    return 2 * q**2 * (1 - q) * bracket(mm) / ((mm + q**2 + q**4) * (mm + 2 * q**3))


def root_count(expr, lo, hi):
    """Exact number of real roots of the polynomial expr in the closed interval [lo, hi]."""
    return sp.Poly(sp.expand(expr), q).count_roots(lo, hi)


def isolate_single_root(expr, lo, hi, eps):
    """Rational isolating interval of width < eps for the unique root of expr in [lo, hi]."""
    poly = sp.Poly(sp.expand(expr), q)
    assert poly.count_roots(lo, hi) == 1
    intervals = poly.intervals(inf=lo, sup=hi, eps=eps)
    assert len(intervals) == 1
    (a, b), mult = intervals[0]
    assert mult == 1 and lo <= a < b <= hi
    return sp.Rational(a), sp.Rational(b)


# --------------------------------------------------------------------------
# A. The three-component example: rates (1,3,5) versus (1,4,4), weights 1/3.
# --------------------------------------------------------------------------
print("== A. three components ==")
lam3, gam3 = (1, 3, 5), (1, 4, 4)
u3 = (R(1, 3),) * 3
check("A1 (1,3,5) majorizes (1,4,4)", majorizes(lam3, gam3))
check("A2 (1,4,4) does not majorize (1,3,5)", not majorizes(gam3, lam3))
check("A3 equal sums and equal means", sum(lam3) == sum(gam3) == 9)

hl3, hg3 = hazard(lam3, u3), hazard(gam3, u3)
sl3, sg3 = survival(lam3, u3), survival(gam3, u3)

exact_values = {
    R(1, 2): (R(11, 7), R(8, 5), R(-1, 35)),      # t = log 2
    R(1, 4): (R(103, 91), R(12, 11), R(41, 1001)),  # t = log 4
}
for qq, (a, b, c) in exact_values.items():
    va, vb = sp.nsimplify(hl3.subs(q, qq)), sp.nsimplify(hg3.subs(q, qq))
    check(f"A4 h_lambda at q={qq} equals {a}", va == a)
    check(f"A5 h_gamma  at q={qq} equals {b}", vb == b)
    check(f"A6 difference at q={qq} equals {c}", va - vb == c)

check("A7 S_lambda - S_gamma = q^3 (1-q)^2 / 3 identically",
      sp.cancel(sl3 - sg3 - q**3 * (1 - q)**2 / 3) == 0)
check("A8 closed form of the hazard difference (m = 1)",
      sp.cancel(hl3 - hg3 - target_difference(1)) == 0)

B1 = bracket(1)
check("A9 dB_1/dq = -2 - 3 q^2 - 4 q^3 (negative on (0,1))",
      sp.expand(sp.diff(B1, q) + 2 + 3 * q**2 + 4 * q**3) == 0)
check("A10 B_1 has exactly one root in [0,1]", root_count(B1, 0, 1) == 1)
check("A11 B_1(1/4) = 123/256 > 0 and B_1(1/2) = -3/16 < 0",
      B1.subs(q, R(1, 4)) == R(123, 256) and B1.subs(q, R(1, 2)) == R(-3, 16))
check("A12 the root lies in (1/4, 1/2)", root_count(B1, R(1, 4), R(1, 2)) == 1)
for name, expr in (("1 + q^2 + q^4", 1 + q**2 + q**4), ("1 + 2 q^3", 1 + 2 * q**3)):
    check(f"A13 denominator factor {name} has no root in [0,1] and is positive",
          root_count(expr, 0, 1) == 0 and expr.subs(q, R(1, 2)) > 0)

lo, hi = isolate_single_root(B1, 0, 1, R(1, 10**40))
q_star_lo, q_star_hi = lo, hi
t_star_hi, t_star_lo = -sp.log(lo), -sp.log(hi)   # t = -log q reverses order
print(f"   q_* in ({sp.N(lo, 25)}, {sp.N(hi, 25)})")
print(f"   t_* in ({sp.N(t_star_lo, 25)}, {sp.N(t_star_hi, 25)})")
check("A14 q_* in (0.4390, 0.4392) and t_* in (0.823, 0.8235)",
      R(4390, 10**4) < lo and hi < R(4392, 10**4)
      and sp.N(t_star_lo, 30) > R(823, 1000) and sp.N(t_star_hi, 30) < R(8235, 10**4))
# Sign pattern: B_1 > 0 on [0, q_*) (large t) and < 0 on (q_*, 1] (small t).
check("A15 sign pattern: h_lambda < h_gamma for q > q_* (t < t_*), > for q < q_*",
      B1.subs(q, R(9, 10)) < 0 and B1.subs(q, R(1, 10)) > 0
      and (hl3 - hg3).subs(q, R(9, 10)) < 0 and (hl3 - hg3).subs(q, R(1, 10)) > 0)

check("A15b B_1 = 1 - 2q - q^3 - q^4 is irreducible over Q (q_* is algebraic of degree 4)",
      sp.Poly(B1, q).is_irreducible and sp.Poly(B1, q).degree() == 4)

# Local behaviour at t = 0: h(0) equals the mean rate, h'(0) = -Var(rate).
t = sp.Symbol("t", positive=True)
hl3_t, hg3_t = hl3.subs(q, sp.exp(-t)), hg3.subs(q, sp.exp(-t))
check("A16 h_lambda(0) = h_gamma(0) = 3",
      sp.limit(hl3_t, t, 0) == 3 and sp.limit(hg3_t, t, 0) == 3)
check("A17 h_lambda'(0) = -8/3 < -2 = h_gamma'(0)",
      sp.limit(sp.diff(hl3_t, t), t, 0) == R(-8, 3)
      and sp.limit(sp.diff(hg3_t, t), t, 0) == -2)
check("A18 both hazards tend to the common minimal rate 1",
      sp.limit(hl3_t, t, sp.oo) == 1 and sp.limit(hg3_t, t, sp.oo) == 1)

# --------------------------------------------------------------------------
# B. Padded family: rates (1,...,1,3,5) versus (1,...,1,4,4) with m ones.
#    Symbolic in m (positive real), then exact root isolation for m = 1..64.
# --------------------------------------------------------------------------
print("== B. padded family, symbolic m ==")
hl_m = (m * q + 3 * q**3 + 5 * q**5) / (m * q + q**3 + q**5)
hg_m = (m * q + 8 * q**4) / (m * q + 2 * q**4)
sl_m = (m * q + q**3 + q**5) / (m + 2)
sg_m = (m * q + 2 * q**4) / (m + 2)
check("B1 hazard difference identity, symbolic in m",
      sp.cancel(hl_m - hg_m - target_difference(m)) == 0)
check("B2 survival difference = q^3 (1-q)^2 / (m+2), symbolic in m",
      sp.cancel(sl_m - sg_m - q**3 * (1 - q)**2 / (m + 2)) == 0)
check("B3 dB_m/dq = -2m - 3q^2 - 4q^3",
      sp.expand(sp.diff(bracket(m), q) + 2 * m + 3 * q**2 + 4 * q**3) == 0)
check("B4 B_m(1/4) = m/2 - 5/256",
      sp.expand(bracket(m).subs(q, R(1, 4)) - (m / 2 - R(5, 256))) == 0)
check("B5 B_m(1/2) = -3/16", bracket(m).subs(q, R(1, 2)) == R(-3, 16))
check("B6 B_m(0) = m and B_m(1) = -m - 2",
      bracket(m).subs(q, 0) == m and sp.expand(bracket(m).subs(q, 1) + m + 2) == 0)
# Localisation q_* in (1/2 - 3/(16 m), 1/2): B_m(1/2 - 3/(16m)) = 3/8 - (1/2-e)^3 (3/2-e).
e = R(3, 16) / m
check("B7 B_m(1/2 - 3/(16 m)) = 3/8 - (1/2 - e)^3 (3/2 - e) with e = 3/(16 m)",
      sp.simplify(bracket(m).subs(q, R(1, 2) - e) - (R(3, 8) - (R(1, 2) - e)**3 * (R(3, 2) - e))) == 0)
check("B8 lower limit of h_lambda - h_gamma as q -> 0 (t -> oo) is 0 from above",
      sp.limit(target_difference(m), q, 0) == 0
      and sp.limit(target_difference(m) / q**2, q, 0) == 2 / m)

print("== B'. padded family, exact root isolation for m = 1..64 ==")
crossing_table = []
all_ok = True
for mm in range(1, 65):
    lam = (1,) * mm + (3, 5)
    gam = (1,) * mm + (4, 4)
    n = mm + 2
    u = (R(1, n),) * n
    ok = majorizes(lam, gam) and not majorizes(gam, lam)
    ok &= sp.cancel(hazard(lam, u) - hl_m.subs(m, mm)) == 0
    ok &= sp.cancel(hazard(gam, u) - hg_m.subs(m, mm)) == 0
    ok &= sp.cancel(survival(lam, u) - survival(gam, u) - q**3 * (1 - q)**2 / n) == 0
    Bm = bracket(mm)
    ok &= root_count(Bm, 0, 1) == 1
    ok &= root_count(Bm, R(1, 4), R(1, 2)) == 1
    a, b = isolate_single_root(Bm, R(1, 4), R(1, 2), R(1, 10**12))
    ok &= R(1, 2) - R(3, 16 * mm) < a and b < R(1, 2)
    crossing_table.append((n, a, b))
    all_ok &= bool(ok)
check("B9 for m = 1..64: majorization, direct-definition agreement, one root, localisation", all_ok)
for n, a, b in crossing_table[:6] + crossing_table[-2:]:
    print(f"   n={n:3d}: q_* in ({sp.N(a, 12)}, {sp.N(b, 12)}), "
          f"t_* in ({sp.N(-sp.log(b), 12)}, {sp.N(-sp.log(a), 12)})")

# m = 0 (two components, no padding): no crossing, hazard order holds.
print("== C. two components (m = 0): no crossing ==")
hl0, hg0 = hazard((3, 5), (R(1, 2),) * 2), hazard((4, 4), (R(1, 2),) * 2)
check("C1 (3,5) majorizes (4,4)", majorizes((3, 5), (4, 4)))
check("C2 h_(3,5) - h_(4,4) = (q^2 - 1)/(1 + q^2) < 0 on (0,1)",
      sp.cancel(hl0 - hg0 - (q**2 - 1) / (1 + q**2)) == 0)
check("C3 B_0 = -q^3 (1+q) has no root in (0,1]",
      sp.expand(bracket(0) + q**3 * (1 + q)) == 0 and root_count(bracket(0), R(1, 10**6), 1) == 0)

# --------------------------------------------------------------------------
# D. Classical facts that survive (checked on the examples).
# --------------------------------------------------------------------------
print("== D. what survives ==")
check("D1 S_lambda >= S_gamma on (0,1) for the padded family (numerator q^3(1-q)^2 > 0)",
      root_count(q**3 * (1 - q)**2, R(1, 10**6), R(1 - R(1, 10**6))) == 0)
# variance of the uniform rate law is strictly Schur-convex: (1,3,5) vs (1,4,4)
var = lambda v: R(sum(x * x for x in v), len(v)) - R(sum(v), len(v))**2
check("D2 Var(1,3,5) = 8/3 > 2 = Var(1,4,4)", var(lam3) == R(8, 3) and var(gam3) == 2)

# --------------------------------------------------------------------------
# E. Other majorized triples with uniform weights (the failure is not universal).
# --------------------------------------------------------------------------
print("== E. other majorized triples ==")
pairs = {
    # (lambda, gamma): expected sign pattern of h_lambda - h_gamma on (0,1) in q
    ((1, 1, 7), (1, 4, 4)): "negative",     # hazard order holds: X_lambda >=_hr X_gamma
    ((1, 2, 6), (1, 4, 4)): "crossing",
    ((1, 2, 6), (1, 3, 5)): "crossing",
}
for (lam, gam), expected in pairs.items():
    d = sp.cancel(sp.together(hazard(lam, u3) - hazard(gam, u3)))
    num, den = sp.fraction(d)
    inner = root_count(num, R(1, 10**9), 1 - R(1, 10**9))
    ok = majorizes(lam, gam) and root_count(den, 0, 1) == 0
    if expected == "negative":
        ok &= inner == 0 and d.subs(q, R(1, 2)) < 0
    else:
        ok &= inner == 1 and d.subs(q, R(99, 100)) < 0 and d.subs(q, R(1, 100)) > 0
    check(f"E1 {lam} majorizes {gam}: hazard difference is {expected} on (0,1)", ok)
check("E2 (1,1,7) vs (1,4,4): h_lambda - h_gamma = 6 q^3 (q-1)(q^3+2)(q^2+q+1) / ((2q^3+1)(q^6+2))",
      sp.cancel(hazard((1, 1, 7), u3) - hazard((1, 4, 4), u3)
                - 6 * q**3 * (q - 1) * (q**3 + 2) * (q**2 + q + 1) / ((2 * q**3 + 1) * (q**6 + 2))) == 0)

failed = [name for name, ok in RESULTS if not ok]
print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
