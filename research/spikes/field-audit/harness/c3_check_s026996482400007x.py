"""Independent check: doi:10.1017/s026996482400007x Theorem 3.7.

EW(a, lam, k): S(x) = a e^{-(lam x)^k} / (1 - (1-a) e^{-(lam x)^k}).
Independent series system: h_{X1:n}(x) = sum_i h_i(x), where
  h_i(x) = k lam_i^k x^{k-1} / (1 - (1-a) e^{-(lam_i x)^k}).
Claim: lam >=m mu (equal sums, lam more spread) => X1:n <=hr Y1:n,
i.e. h_X(x) >= h_Y(x) for all x.
"""
import mpmath as mp
import sympy as sp

mp.mp.dps = 100


def h_comp(lam, x, a, k):
    lam, x, a, k = mp.mpf(lam), mp.mpf(x), mp.mpf(a), mp.mpf(k)
    e = mp.exp(-(lam * x) ** k)
    return k * lam**k * x ** (k - 1) / (1 - (1 - a) * e)


def H(lams, x, a, k):
    return sum(h_comp(li, x, a, k) for li in lams)


# eval cases: (alpha, k, lam, mu); premise lam >=m mu: equal sums,
# mu's ascending partial sums >= lam's (mu more balanced).
cases = [
    ("1/2", 2, (3, 2, 1), ("3.5", "3.5", "0")),
    ]
cases = [
    (mp.mpf('0.5'), 2, (3, 2, 1), (2, 2, 2)),
    (mp.mpf('1'),   1, (4, 1, 1), (2, 2, 2)),
    (mp.mpf(1) / 3, mp.mpf('1.5'), (5, 2), (mp.mpf('3.5'), mp.mpf('3.5'))),
    (mp.mpf('0.8'), 3, (5, 3, 1), (3, 3, 3)),
]
for a, k, lam, mu in cases:
    # premise verify: sorted asc partial sums
    sa, sb = sorted(map(mp.mpf, lam)), sorted(map(mp.mpf, mu))
    ok = abs(sum(sa) - sum(sb)) < mp.mpf('1e-30') and all(
        sum(sb[:l]) >= sum(sa[:l]) - mp.mpf('1e-30') for l in range(1, len(sa)))
    print(f"a={mp.nstr(a,6)} k={k} lam={lam} mu={mu}  premise lam>=m mu: {ok}")
    # scan x dense
    fails = []
    for i in range(1, 3000):
        x = mp.mpf(i) / 300          # x in (0,10)
        d = H(lam, x, a, k) - H(mu, x, a, k)
        if d < -mp.mpf('1e-50'):
            fails.append((x, d))
    if fails:
        print("   h_X - h_Y < 0 at", len(fails), "points; first:", mp.nstr(fails[0][0], 6),
              "min:", mp.nstr(min(d for _, d in fails), 8),
              "at x=", mp.nstr(min(fails, key=lambda p: p[1])[0], 6))
    else:
        print("   holds on grid")

# Focus on the eval witness: a=1/3, k=3/2, lam=(5,2), mu=(3.5,3.5), x=0.1
a, k = mp.mpf(1) / 3, mp.mpf('1.5')
lam, mu = (5, 2), (mp.mpf('3.5'), mp.mpf('3.5'))
for xs in ('0.1', '0.05', '0.2', '0.5', '1', '2', '5'):
    x = mp.mpf(xs)
    print(f"x={xs}: h_X={mp.nstr(H(lam,x,a,k),20)}  h_Y={mp.nstr(H(mu,x,a,k),20)}  diff={mp.nstr(H(lam,x,a,k)-H(mu,x,a,k),10)}")

# Exact confirmation at x=1/10 with sympy rationals + exp
t = sp.Symbol('t', positive=True)
lam5 = sp.Rational(5); lam2 = sp.Rational(2); mu7 = sp.Rational(7, 2)
a = sp.Rational(1, 3); k = sp.Rational(3, 2); x0 = sp.Rational(1, 10)
def hs(lam):
    return k * lam**k * x0**(k-1) / (1 - (1 - a) * sp.exp(-(lam*x0)**k))
d = sp.N(hs(lam5) + hs(lam2) - 2*hs(mu7), 60)
print("exact-ish sympy check at x=1/10: h_X-h_Y =", d)

# also verify the Schur-convexity failure directly: g''(lam) sign
l_, x_ = sp.symbols('l_ x_', positive=True)
g = k * l_**k * x_**(k-1) / (1 - (1-a)*sp.exp(-(l_*x_)**k))
gpp = sp.diff(g, l_, 2)
for lv in ('2','5','3.5'):
    print(f"g''(lam={lv}) at x=1/10:", sp.N(gpp.subs({l_: sp.Rational(lv), x_: x0}), 20))
