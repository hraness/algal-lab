"""C3 for the CLFRD Theorem 3.2 refutation: independent evaluator.

Density typed directly from the paper's equation (3), no symbolic
differentiation: g(x) = (a + b x)(1 + l e^{-a x - b x^2/2}) / exp(a x + b x^2/2 + l - l e^{-a x - b x^2/2}).
Claim (joint reading, both readings covered): a1 <= a2, b1 <= b2, l1 <= l2 implies
X >=lr Y, i.e. g_X / g_Y nondecreasing. Instance: X = (1, 1, 1), Y = (1, 2, 1).
"""
from mpmath import mp, mpf, exp, iv

def g(a, b, l, t, lib=mp):
    e = lib.exp(-a * t - b * t * t / 2)
    return (a + b * t) * (1 + l * e) / lib.exp(a * t + b * t * t / 2 + l - l * e)

mp.dps = 60
pts = [mpf(k) / 10 ** 4 for k in range(1, 6)]
ratios = [g(1, 1, 1, t) / g(1, 2, 1, t) for t in pts]
print("g_X/g_Y at t = 1e-4 .. 5e-4:", [mp.nstr(r, 20) for r in ratios])
print("strictly decreasing there:", all(r1 > r2 for r1, r2 in zip(ratios, ratios[1:])))

iv.dps = 60
t1, t2 = iv.mpf(1) / 10 ** 4, iv.mpf(2) / 10 ** 4
r1 = g(1, 1, 1, t1, iv) / g(1, 2, 1, t1, iv)
r2 = g(1, 1, 1, t2, iv) / g(1, 2, 1, t2, iv)
print("rigorous: ratio(1e-4) - ratio(2e-4) in", r1 - r2, "-> positive:", (r1 - r2).a > 0)
