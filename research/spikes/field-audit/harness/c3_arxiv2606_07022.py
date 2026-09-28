"""Independent C3: Remark 2(item 1) of arxiv:2606.07022.

Printed extension: gamma1:r <= beta1:q (r <= q, same common difference mu)
implies X_{q,beta} <=st X_{r,gamma}.

Counter-instance (satisfies all printed conditions):
  r=2, gamma arithmetic from 1, q=3, beta arithmetic from 2, mu=1
  on the standard uniform baseline (0,1).

Uniform m-GOS survival (mu=1):
  S_{r,g,1}(x) = M/(r-1)! * sum_k (-1)^k C(r-1,k) (1-x)^{g+k}/(g+k),
  M = prod_{i=1}^r (g + i - 1).

Findings (strict interval enclosures):
  * at x=1/10^12 : S_{X_{3,beta}} - S_{X_{2,gamma}} < 0  (<=st fails)
  * at x=41/120  : S_{X_{3,beta}} - S_{X_{2,gamma}} > 0  (>=st fails)
  i.e. the two distribution functions cross -- no stochastic order at all.
For r=q=3 (gamma1=1<beta1=2, mu=1) the printed direction does hold.
"""
import sympy as sp
from mpmath import iv

iv.dps = 150
t = sp.Symbol("t", positive=True)


def ie(e, x0):
    if e == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if e.is_Rational:
        return iv.mpf(int(e.p)) / iv.mpf(int(e.q))
    if e.is_Add:
        s = iv.mpf(0)
        for a in e.args:
            s += ie(a, x0)
        return s
    if e.is_Mul:
        p = iv.mpf(1)
        for a in e.args:
            p *= ie(a, x0)
        return p
    if e.is_Pow:
        b_, e_ = e.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_, x0)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_, x0) * iv.log(ie(b_, x0)))
    raise ValueError(type(e))


R = sp.Rational


def M(r, g, m):
    p = R(1)
    for i in range(r):
        p *= g + i * m
    return p


def S_unif(r, g, m):
    s = R(0)
    for k in range(r):
        s += (-1) ** k * sp.binomial(r - 1, k) * \
            (1 - t) ** (g + m * k) / (g + m * k)
    return M(r, g, m) / (sp.factorial(r - 1) * m ** (r - 1)) * s


S_r2_g1 = S_unif(2, R(1), R(1))       # X_{2, gamma=(1,2)}
S_q3_b2 = S_unif(3, R(2), R(1))       # X_{3, beta=(2,3,4)}
D = S_q3_b2 - S_r2_g1                 # X_{q,b} <=st X_{r,g} needs D >= 0

for pt in (R(1, 10 ** 12), R(19, 100), R(41, 120), R(1, 3)):
    v = ie(D, pt)
    print(f"x={pt}: S_qb - S_rg in [{v.a}, {v.b}]")
# D > 0 on (0, ~0.2) -- printed direction X_{q,b} <=st X_{r,g} fails there
# (interior witness x=19/100); D < 0 at x=41/120 -- reverse fails too.
assert ie(D, R(19, 100)).a > 0, "printed-direction violation missing"
assert ie(D, R(41, 120)).b < 0, "reverse-direction violation missing"
print("REMARK 2(1) REFUTED: r<q regime -- survival functions cross; "
      "neither direction is st-ordered")

# sanity: r=q case does hold the printed direction
S_r3_g1 = S_unif(3, R(1), R(1))
S_q3_b2b = S_unif(3, R(2), R(1))
D2 = S_q3_b2b - S_r3_g1          # printed direction needs D2 <= 0
pos = any(ie(D2, R(i, 40)).a > 0 for i in range(1, 40))
print("r=q sanity (X_3,b <=st X_3,g needs D2<=0): any positive:", pos)
assert not pos
