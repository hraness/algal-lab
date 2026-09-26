"""Thm 3.10 (ageing-faster / R-rh): certified audit.

Claim: for common alpha, ANY p,p*, R(X_{a,b};p) <=_{R-rh} R(X_{a,b*};p*)
provided max_{i!=j}|b_i - b_j| <= min_{i!=j}|b*_i - b*_j|.

Proof defect (certified symbolically): the quadruple-sum kernel
  Delta_{i,j,k,l} = a*u*[(b_i - b_j) + (b*_l - b*_k)],  u = y^a/(1-y^a) > 0,
is asserted "<= 0 for all i,j,k,l" (line 1925 of text, (A16)); under the
theorem's own hypothesis it takes positive values.

Then: is the theorem itself false? Test on admissible instances with
Sturm certificates on the rational function R(z) = r~_R/r~_R* in z = g^{1/L}.
"""
import sympy as sp
from ik_lib import (R, y, g, z, rh_ratio_g, sturm_roots_on_01, witnesses,
                    sign_at)
import itertools

a, bi, bj, bk, bl, u = sp.symbols("a bi bj bk bl u", positive=True)

# ---------- Part A: symbolic Delta ----------
Delta = a * u * ((bi - bj) + (bl - bk))
print("Delta_{i,j,k,l}/(a u) =", sp.expand(Delta / (a * u)),
      " ; >0 e.g. for (b_i-b_j, b*_l-b*_k) = (0.2, 1.5) on Example 3.6 params")
# Example 3.6: b=(0.1,0.2,0.3), b*=(0.5,1,2): pick i=3,j=1,k=1,l=3
val = Delta.subs({bi: R(3, 10), bj: R(1, 10), bk: R(1, 2), bl: R(2)})
print("  Example 3.6 quadruple (i,j,k,l)=(3,1,1,3): Delta =", sp.nsimplify(val),
      "> 0  => printed termwise bound FALSE under stated hypothesis")

# ---------- Part B: test the claim ----------
def ratio_in_z(betas, p, betas_s, p_s, L):
    """r~_R/r~_R* with g = z**L (L = lcm of beta denominators)."""
    Rg = rh_ratio_g(betas, p, betas_s, p_s)
    return sp.cancel(Rg.subs(g, z ** L))


def denom_lcm(betas, betas_s):
    L = 1
    for b in list(betas) + list(betas_s):
        L = sp.ilcm(L, sp.fraction(R(b))[1])
    return int(L)


def audit_instance(betas, p, betas_s, p_s, label, check_cond=True):
    L = denom_lcm(betas, betas_s)
    Rz = ratio_in_z(betas, p, betas_s, p_s, L)
    dRz = sp.diff(Rz, z)
    cert = sturm_roots_on_01(dRz, z)
    rng = max(abs(betas[i] - betas[j])
              for i in range(len(betas)) for j in range(len(betas)) if i != j)
    rng_s = min(abs(betas_s[i] - betas_s[j])
                for i in range(len(betas_s)) for j in range(len(betas_s))
                if i != j)
    pts = [R(1, 10), R(1, 4), R(1, 2), R(3, 4), R(9, 10), R(19, 20)]
    wits = [(pt, sp.sign(dRz.subs(z, pt))) for pt in pts]
    print(f"\n=== {label} ===")
    print(f"  b={betas} b*={betas_s} p={p} p*={p_s}")
    print(f"  max|b_i-b_j|={rng} ; min|b*_i-b*_j|={rng_s} ; admissible={rng <= rng_s}")
    print(f"  R(z) rat'l deg(num dRz)={cert['deg']}, roots in (0,1)={cert['roots_0_1']},"
          f" den roots={cert['den_roots']}")
    print(f"  sign of R'(z) at grid: {[(str(pt), int(sg)) for pt, sg in wits]}")
    return cert, wits


# Example 3.6 (paper's own): alpha=2 common; b tenths -> L=10
cert_ex, w_ex = audit_instance(
    [R(1, 10), R(1, 5), R(3, 10)], [R(1, 10), R(3, 10), R(6, 10)],
    [R(1, 2), R(1), R(2)], [R(1, 5), R(3, 10), R(1, 2)],
    "Example 3.6 (paper)")

# Integer admissible instances -> fully polynomial certificates
inst = [
    ([R(1), R(2), R(3)], [R(1, 3), R(1, 3), R(1, 3)],
     [R(5), R(10), R(15)], [R(1, 3), R(1, 3), R(1, 3)], "int A: spread 2 vs 5"),
    ([R(1), R(2), R(3)], [R(1, 2), R(1, 3), R(1, 6)],
     [R(5), R(10), R(15)], [R(2, 5), R(2, 5), R(1, 5)], "int B"),
    ([R(2), R(3)], [R(1, 2), R(1, 2)],
     [R(1), R(5)], [R(1, 2), R(1, 2)], "n=2: rng 1 vs 4"),
    ([R(1), R(2)], [R(3, 4), R(1, 4)],
     [R(1), R(6)], [R(1, 4), R(3, 4)], "n=2 asymmetric weights"),
    ([R(1), R(2), R(4)], [R(1, 4), R(1, 2), R(1, 4)],
     [R(3), R(10), R(11)], [R(1, 3), R(1, 3), R(1, 3)], "int C rng3 vs1? no"),
]
for b, p, bs, ps, lab in inst:
    audit_instance(b, p, bs, ps, lab)
