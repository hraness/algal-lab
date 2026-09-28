"""C3 second evaluations for eval_doi_10.1080_02331888.2025.2552185.py.

Each refuted claim is re-verified with closedform's mpmath interval-arithmetic
grid (an independent code path from ratdist's exact polynomial isolation).
Survivals are re-expressed in t via z = e^{-t}:  (1-G^a)^g with G = 1-e^{-cx}
becomes  (1 - e^{-c a t})^g.

Expected: every 'must_fail' check returns False (strict negative interval
enclosure = rigorous refutation), and the st-orientation sanity checks hold.
"""

import sympy as sp
import closedform as cf
from closedform import x as t

R = sp.Rational


def kwg_t(c, a, g):
    """Kw-G survival in t with baseline G(x) = 1 - e^{-cx}:
    S(x) = (1 - G(x)^a)^g = (1 - (1 - e^{-cx})^a)^g."""
    return (1 - (1 - sp.exp(-R(c) * t)) ** R(a)) ** R(g)


def mix_min_t(params, c, gam, pmf):
    tot = sp.Integer(0)
    n = len(params)
    for m, p in pmf.items():
        tot += R(p) * sp.prod([kwg_t(c, params[i], gam[i]) for i in range(m)])
    return sp.expand(tot)


def mix_max_t(params, c, gam, pmf):
    tot = sp.Integer(0)
    for m, p in pmf.items():
        tot += R(p) * sp.prod([1 - kwg_t(c, params[i], gam[i]) for i in range(m)])
    return sp.expand(1 - tot)


def C(e):
    return cf.Closed(sp.expand(e))


def chk(order, A, B):
    return cf.check(order, C(A), C(B))


if __name__ == "__main__":
    pmf = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    print("=== Thm 3.7: printed iff 'sum g <= sum d  <=>  X >=hr Y' ===")
    # necc-d: N == 1, gamma1=2 <= delta1=3 but totals 7 > 6.
    # conclusion X_1 >=hr Y_1  <=>  h_X <= h_Y  <=>  2 <= 3 : verified holds
    # while premise fails -> iff false.
    SX = sp.exp(-2 * t)
    SY = sp.exp(-3 * t)
    print("necc-d premise fails; hr(Y<=X) holds:",
          chk("hr", SY, SX))        # must hold -> iff refuted
    # litsuf-f: totals 9 <= 9 premise satisfied literally but prefix sums
    # violate; N = {1:.9, 2:.1}: refutation of sufficiency under literal read.
    pmf2 = {1: R(9, 10), 2: R(1, 10)}
    # alpha=1 -> S_i = z^{gamma_i} = e^{-gamma_i t}:  kwg_t(1, 1, gamma_i)
    SX = mix_min_t((1, 1), 1, (4, 5), pmf2)
    SY = mix_min_t((1, 1), 1, (1, 8), pmf2)
    print("litsuf-f hr(Y<=X) (printed sufficiency):", chk("hr", SY, SX))

    print("=== Thm 3.8: gamma ⪰^m delta (order-free premise) ===")
    # gamma=(4,1,1) listed descending, delta=(2,2,2): same multiset as the
    # surviving ascending instance; premise still satisfied, claim fails.
    K = kwg_t(1, 2, 1)         # a=2: S_i = 1-(1-e^{-t})^2 = 2e^{-t}-e^{-2t}
    Sx1 = (K ** 4 + K ** 5 + K ** 6) / 3          # gamma=(4,1,1) prefixes 4,5,6
    Sy1 = (K ** 2 + K ** 4 + K ** 6) / 3          # delta=(2,2,2) prefixes 2,4,6
    print("desc-listing hr(Y<=X):", chk("hr", Sy1, Sx1), "   [must fail]")
    print("asc-listing  hr(Y<=X):",
          chk("hr", (K**2 + K**4 + K**6)/3, (K + K**2 + K**6)/3),
          "   [survives]")

    print("=== Thm 3.9: printed X_{1:N} >=hr Y_{1:N}, i.e. hr(Y <=hr X) ===")
    # adj-a: alpha=(1,1,2), beta=(2,2,2), gamma=delta=1_n, G=H=Exp(1)
    SX = mix_min_t((1, 1, 2), 1, (1, 1, 1), pmf)
    SY = mix_min_t((2, 2, 2), 1, (1, 1, 1), pmf)
    print("adj-a  printed hr(Y<=X):", chk("hr", SY, SX), "   [must fail]")
    print("adj-a  reverse hr(X<=Y):", chk("hr", SX, SY), "   [also fails: crossing]")
    print("adj-a  sanity st(X<=Y):", chk("st", SX, SY), "   [should hold]")
    # alt-c: alpha=(2,3,3) (supermajorizes beta) vs beta=(2,2,2)
    SX = mix_min_t((2, 3, 3), 1, (1, 1, 1), pmf)
    SY = mix_min_t((2, 2, 2), 1, (1, 1, 1), pmf)
    print("alt-c  printed hr(Y<=X):", chk("hr", SY, SX), "   [must fail]")
    print("alt-c  sanity st(Y<=X):", chk("st", SY, SX), "   [should hold]")

    print("=== Thm 3.10: printed X_{1:N} <=hr Y_{1:N} ===")
    SX = mix_min_t((1, 1, 2), 1, (1, 1, 1), pmf)
    SY = mix_min_t((2, 2, 2), 1, (1, 1, 1), pmf)
    print("adj-a  printed hr(X<=Y):", chk("hr", SX, SY), "   [must fail]")
    # alt reading: alpha supermajorizes beta -> X bigger -> also fails
    SX = mix_min_t((2, 3, 3), 1, (1, 1, 1), pmf)
    SY = mix_min_t((2, 2, 2), 1, (1, 1, 1), pmf)
    print("alt    printed hr(X<=Y):", chk("hr", SX, SY), "   [must fail]")

    print("=== Thm 3.12: printed X_{N:N} >=rh Y_{N:N} (rh(Y,X)) ===")
    g = 2
    SX = mix_max_t((1, 1, 2), 1, (g,) * 3, pmf)
    SY = mix_max_t((2, 2, 2), 1, (g,) * 3, pmf)
    print("adj    printed rh(Y<=X):", chk("rh", SY, SX), "   [must fail]")
    print("adj    reverse rh(X<=Y):", chk("rh", SX, SY), "   [holds]")
    SX = mix_max_t((2, 3, 3), 1, (g,) * 3, pmf)
    SY = mix_max_t((2, 2, 2), 1, (g,) * 3, pmf)
    print("alt    printed rh(Y<=X):", chk("rh", SY, SX), "   [must fail]")
    print("alt    reverse rh(X<=Y):", chk("rh", SX, SY), "   [also fails]")

    print("=== Thm 3.18: printed X_{1:N} <=lr Y_{1:N} ===")
    pmf2 = {1: R(1, 2), 2: R(1, 2)}
    sxa1 = kwg_t(1, 3, 1); sxa2 = kwg_t(1, 2, 1); syb1 = kwg_t(1, 1, 1)
    SX = (sxa1 + sxa1 * sxa2) / 2
    SY = (syb1 + syb1 * sxa2) / 2
    print("printed lr(X<=Y):", chk("lr", SX, SY), "   [must fail]")
    print("reverse lr(Y<=X):", chk("lr", SY, SX), "   [holds]")
    print("sanity st(Y<=X):", chk("st", SY, SX), "   [should hold: X bigger]")
