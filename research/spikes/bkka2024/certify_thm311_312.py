"""Thm 3.11 (rh) and Thm 3.12 (lr) audit.

Thm 3.11: R <=rh R* provided max a* <= min a AND max{a_i b_i} <= min{a*_j b*_j}.
Thm 3.12: R >=lr R* provided max a <= min a* AND min{a_i b_i} >= max{a*_j b*_j}.

Both proofs are double-sum expansions xi(x) = sum_ij p_i p*_j [pos] * bracket_{ij}
with a termwise sign assertion. We (a) check the bracket termwise, (b) test the
aggregate claims with Sturm certificates on admissible instances and on the
paper's examples/counterexamples.

y = 1/(1+x) in (0,1), decreasing in x.
"""
import sympy as sp
from ik_lib import R, y, Fy, fy, sturm_roots_on_01, witnesses

v = sp.Symbol("v", positive=True)   # v = 1+x > 1


# ---------------- Thm 3.11 bracket -------------------------------------
# bracket_ij = a_i b_i v^{-(a_i+1)} (1-v^{-a*_j}) - a*_j b*_j v^{-(a*_j+1)}(1-v^{-a_i})
# claim: <= 0 whenever a*_j <= a_i and a_i b_i <= a*_j b*_j.
# ratio of the positive parts:
#   [a_i b_i v^{-(a_i+1)}(1-v^{-a*_j})] / [a*_j b*_j v^{-(a*_j+1)}(1-v^{-a_i})]
#   = (a_i b_i)/(a*_j b*_j) * v^{a*_j-a_i} * (1-v^{-a*_j})/(1-v^{-a_i})  <= 1
# product of three factors each in (0,1].
print("== Thm 3.11 bracket: numerical scan over admissible (a_i, a*_j, b_i, b*_j) ==")
bad = 0
tot = 0
for ai in [R(1, 2), R(1), R(3, 2), R(2), R(5), R(10)]:
    for aj in [R(1, 4), R(1, 2), R(1), R(2)]:
        if aj > ai:
            continue
        for bi in [R(1, 10), R(1, 2), R(1), R(3), R(20)]:
            for bj in [R(1, 10), R(1, 2), R(1), R(5), R(30)]:
                if ai * bi > aj * bj:
                    continue
                tot += 1
                for vv in [R(11, 10), R(3, 2), R(2), R(5), R(100)]:
                    lhs = ai * bi * vv ** (-(ai + 1)) * (1 - vv ** (-aj))
                    rhs = aj * bj * vv ** (-(aj + 1)) * (1 - vv ** (-ai))
                    if sp.sign(lhs - rhs) > 0:
                        bad += 1
                        print("  bracket>0 at", ai, aj, bi, bj, vv)
print(f"  admissible tuples scanned: {tot}, violations: {bad}")


# ---------------- Thm 3.12 bracket -------------------------------------
# bracket_ij = a_i(b_i-1) v^{-a_i} g*_j + (a*_j - a_i) g_i g*_j
#              - a*_j(b*_j-1) v^{-a*_j} g_i ,  g_k = 1 - v^{-a_k}
# claim (needed for xi' >= 0): >= 0 when a_i <= a*_j and a_i b_i >= a*_j b*_j.
print("\n== Thm 3.12 bracket scan ==")
bad12 = []
tot = 0
for ai in [R(1, 2), R(1), R(2), R(4), R(8), R(20)]:
    for aj in [R(1, 2), R(1), R(3), R(10), R(30)]:
        if aj < ai:
            continue
        for bi in [R(1, 10), R(1, 2), R(1), R(5), R(30)]:
            for bj in [R(1, 20), R(1, 4), R(1), R(10), R(40)]:
                if ai * bi < aj * bj:
                    continue
                tot += 1
                for vv in [R(101, 100), R(11, 10), R(3, 2), R(2), R(5), R(100)]:
                    gi = 1 - vv ** (-ai)
                    gj = 1 - vv ** (-aj)
                    B = (ai * (bi - 1) * vv ** (-ai) * gj
                         + (aj - ai) * gi * gj
                         - aj * (bj - 1) * vv ** (-aj) * gi)
                    if sp.sign(B) < 0:
                        bad12.append((ai, aj, bi, bj, vv))
print(f"  admissible tuples scanned: {tot}, violations: {len(bad12)}")
for t in bad12[:10]:
    print("   ", t)


# ---------------- aggregate tests on the paper's examples ---------------
def rh_order_cert(a1, b1, p1, a2, b2, p2, label):
    """Claim R1 <=rh R2: F2/F1 increasing in x <-> d/dy[F2/F1] <= 0 on (0,1)."""
    F1, F2 = Fy(a1, b1, p1), Fy(a2, b2, p2)
    d = sp.diff(F2 / F1, y)
    cert = sturm_roots_on_01(d, y)
    w = [(pt, sp.sign(d.subs(y, pt)))
         for pt in [R(1, 10), R(1, 4), R(1, 2), R(3, 4), R(9, 10)]]
    print(f"\n== rh cert {label}: roots(d/dy[F2/F1]) on (0,1) = {cert['roots_0_1']}"
          f" (want <=0: decr in y); signs: {[(str(p_), int(s_)) for p_, s_ in w]}")


def lr_order_cert(a1, b1, p1, a2, b2, p2, label):
    """Claim R1 >=lr R2: f1/f2 increasing in x <-> d/dy[f1/f2] <= 0 on (0,1)."""
    f1, f2 = fy(a1, b1, p1), fy(a2, b2, p2)
    d = sp.diff(f1 / f2, y)
    cert = sturm_roots_on_01(d, y)
    w = [(pt, sp.sign(d.subs(y, pt)))
         for pt in [R(1, 10), R(1, 4), R(1, 2), R(3, 4), R(9, 10)]]
    print(f"\n== lr cert {label}: roots(d/dy[f1/f2]) on (0,1) = {cert['roots_0_1']}"
          f"; signs: {[(str(p_), int(s_)) for p_, s_ in w]}")


# Example 3.7 (Thm 3.11, expects holds): p=(.1,.7,.2),p*=(.2,.5,.3),
# a=(5,8,6),b=(2,1,1), a*=(3,4,2),b*=(5,3,6)
rh_order_cert([R(5), R(8), R(6)], [R(2), R(1), R(1)], [R(1, 10), R(7, 10), R(1, 5)],
              [R(3), R(4), R(2)], [R(5), R(3), R(6)], [R(1, 5), R(1, 2), R(3, 10)],
              "Example 3.7 (Thm 3.11)")

# Counterexample 3.6 (Thm 3.11 violated hyp, expects nonmonotone):
# p=(.60,.25,.15),p*=(.45,.30,.25), a=(1,3,5),b=(3,6,9), a*=(2,4,6),b*=(25,30,35)
rh_order_cert([R(1), R(3), R(5)], [R(3), R(6), R(9)], [R(3, 5), R(1, 4), R(3, 20)],
              [R(2), R(4), R(6)], [R(25), R(30), R(35)], [R(9, 20), R(3, 10), R(1, 4)],
              "Counterexample 3.6")

# Example 3.8 (Thm 3.12, expects holds): p=(.2,.4,.4),p*=(.3,.5,.2),
# a=(2,4,6),b=(25,13,9), a*=(8,10,12),b*=(3,4,1)
lr_order_cert([R(2), R(4), R(6)], [R(25), R(13), R(9)], [R(1, 5), R(2, 5), R(2, 5)],
              [R(8), R(10), R(12)], [R(3), R(4), R(1)], [R(3, 10), R(1, 2), R(1, 5)],
              "Example 3.8 (Thm 3.12)")

# Counterexample 3.7 (Thm 3.12 violated hyp, expects nonmonotone):
# p=(.1,.2,.7),p*=(.6,.3,.1), a=(3,6,9),b=(14,15,11), a*=(5,8,12),b*=(4,2,3)
lr_order_cert([R(3), R(6), R(9)], [R(14), R(15), R(11)], [R(1, 10), R(1, 5), R(7, 10)],
              [R(5), R(8), R(12)], [R(4), R(2), R(3)], [R(3, 5), R(3, 10), R(1, 10)],
              "Counterexample 3.7")
