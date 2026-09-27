"""Pilot checks for arxiv:2407.18801 (second-order statistics, Archimedean copulas).

1. Remark 2 claims the scale (SC), PHR and location models satisfy condition (ii)
   of Theorem 3.1 (a -> Fbar(x; e^a) decreasing and log-convex) exactly when the
   baseline is DFR. Second derivatives in a, exact or rigorously enclosed:
     PHR  log Fbar(x)^{e^a} = e^a log Fbar(x), second derivative e^a log Fbar(x) < 0:
          strictly log-concave for every baseline, so (ii) never holds.
     SC   d2/da2 log Fbar(e^a x) = -u d/du[u h(u)] at u = e^a x, so (ii) holds iff
          u h(u) is decreasing (DPFR); a DFR baseline need not satisfy it. The
          paper's own example baseline, EW(0.9, 0.9), is checked at u = 1/100.
2. The ordering these models would inherit, theta p-larger than theta* implies
   X_{2:n} >=st Y_{2:n}: under independence (log-concave generator), SC with an
   exponential or Weibull baseline and PHR both reduce to exponential rates, so
   it is decided exactly on random instances with the rational harness.
"""
import itertools
import json
import random

import sympy as sp
from mpmath import iv

import closedform as cf
from ratdist import Dist, st, z

random.seed(4242)
R = sp.Rational
out = {}

# 1a. PHR: exact.
xs = sp.Symbol("xs", positive=True)
Fbar = sp.exp(-xs)  # any baseline; exponential for concreteness
a = sp.Symbol("a", real=True)
second = sp.diff(sp.log(Fbar ** sp.exp(a)), a, 2)
out["PHR second derivative in a (exponential baseline, x = 1, a = 0)"] = str(sp.simplify(second.subs({xs: 1, a: 0})))

# 1b. SC with EW(alpha = beta = 9/10): g''(a) = -u (u h(u))' at u = 1/100, rigorous enclosure.
u = cf.x
al = be = R(9, 10)
F = (1 - sp.exp(-u ** al)) ** be
Sbar = 1 - F
h = sp.diff(F, u) / Sbar
g2 = -u * sp.diff(u * h, u)
iv.dps = 60
out["SC with EW(0.9, 0.9): d2/da2 log Fbar(e^a x) at u = e^a x = 1/100 (enclosure)"] = str(cf.iv_eval(g2, R(1, 100)))


# 2. Inherited ordering, exponential rates, independence.
def second_smallest(rates, D):
    s = [z ** int(R(r) * D) for r in rates]
    n = len(s)
    total = sp.Mul(*s)                                   # none failed
    for i in range(n):                                   # exactly one failed
        total += (1 - s[i]) * sp.Mul(*[s[j] for j in range(n) if j != i])
    return Dist(sp.expand(total), sp.Integer(0), sp.Integer(1), increasing=False)


def p_larger(t, ts):
    """t p-larger than ts: partial products of increasing arrangements of t are at most ts's."""
    A, B = sorted(t), sorted(ts)
    pa = pb = 1
    for x, y in zip(A, B):
        pa, pb = pa * x, pb * y
        if pa > pb:
            return False
    return True


tested, refuted = 0, None
for _ in range(4000):
    if tested >= 40:
        break
    t = [R(random.randint(1, 12), 4) for _ in range(3)]
    ts = [R(random.randint(1, 12), 4) for _ in range(3)]
    if not p_larger(t, ts) or sorted(t) == sorted(ts):
        continue
    X, Y = second_smallest(t, 4), second_smallest(ts, 4)
    holds, witness = st(Y, X)                            # claim: Y_{2:n} <=st X_{2:n}
    tested += 1
    if not holds and refuted is None:
        refuted = {"theta": [str(v) for v in t], "theta_star": [str(v) for v in ts], "s0": str(witness)}
out["Inherited claim (exponential rates, n = 3): theta p-larger => X_{2:3} >=st Y_{2:3}"] = {"tested": tested, "refuted_example": refuted}
print(json.dumps(out, indent=1))
