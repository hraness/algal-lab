"""Independent C3 for arXiv:1804.04103 Theorem 3.1 (log-Lindley, shocks).

Model: X_i log-Lindley(s_i, l_i) with Bernoulli shock p_i:
  F_{X_i}(x) = 1 - p_i * (1 - x^{s_i} + s_i x^{s_i} log x / (1 + l_i^{s_i}))
on (0,1).  Parallel maximum cdf F_X = prod_i F_{X_i}.

Claim (i) (h increasing convex, h(p) weakly supermajorized by h(p*) in the
paper's notation): X >=st X* should hold; tested instance
p = (4/5, 1/5), p* = (3/4, 1/2) (identity h): smallest-sum condition
1/5 <= 1/2 and 1 <= 5/4 both hold, so the witness satisfies the printed
hypothesis; s=(2,1), l=(1,1) for both.

F* - F must be >= 0 on (0,1); it is strictly negative at every tested
interior point (the atom at 0, prod(1-p_i) = 4/25 vs 1/8, is not covered
by the majorization hypothesis).
"""
from mpmath import iv, nstr
ln = iv.ln

iv.dps = 80


def Fi(p, s, l, x):
    return 1 - p * (1 - x ** s + s * x ** s * ln(x) / (1 + l ** s))


def Fmax(ps, x):
    f = iv.mpf(1)
    for p, s, l in ps:
        f *= Fi(p, s, l, x)
    return f


PX = [(iv.mpf(4) / 5, 2, 1), (iv.mpf(1) / 5, 1, 1)]
PY = [(iv.mpf(3) / 4, 2, 1), (iv.mpf(1) / 2, 1, 1)]
for t in ["1e-9", "1e-3", "0.1", "0.5", "0.9"]:
    xx = iv.mpf(t)
    d = Fmax(PY, xx) - Fmax(PX, xx)
    print(f"x={t:>6}: F* - F in [{nstr(d.a,8)},{nstr(d.b,8)}]",
          "NEGATIVE (refutes)" if d.b < 0 else "ok")

# a second instance (p=(9/10,1/2,1/5) vs (4/5,3/5,1/2), s=1, lambda=(3,2,1))
PX2 = [(iv.mpf(9) / 10, 1, 3), (iv.mpf(1) / 2, 1, 2), (iv.mpf(1) / 5, 1, 1)]
PY2 = [(iv.mpf(4) / 5, 1, 3), (iv.mpf(3) / 5, 1, 2), (iv.mpf(1) / 2, 1, 1)]
print("instance 2:")
for t in ["1e-3", "0.1", "0.5"]:
    xx = iv.mpf(t)
    d = Fmax(PY2, xx) - Fmax(PX2, xx)
    print(f"x={t:>6}: F* - F in [{nstr(d.a,8)},{nstr(d.b,8)}]",
          "NEGATIVE (refutes)" if d.b < 0 else "ok")
