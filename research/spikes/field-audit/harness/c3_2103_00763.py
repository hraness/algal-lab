"""C3 for arxiv:2103.00763 counterexamples 3.2 and 3.3.

Independent machinery: sympy exact rational + 200-digit numerical eval
(no interval arithmetic).

3.3 (geometric max, reversed hazard rh(u) = [F(u)-F(u-1)]/F(u)):
    F(u) = prod_i (1 - q_i^{u+1}); q in Q -> everything rational, decided
    EXACTLY by rational arithmetic.

3.2 (Poisson min, hazard h(u) = [S(u)-S(u+1)]/S(u)):
    S(u) = 1 - e^{-mu} sum mu^r/r!; evaluated by sympy at 300 digits and by
    the tail-sum representation with an a priori remainder bound.
"""
import sympy as sp
from mpmath import mp, mpf, factorial, exp, power

mp.dps = 300

# ---------------- Counterexample 3.3: exact rational ------------------------
q = [sp.Rational(99, 100), sp.Rational(96, 100), sp.Rational(57, 100)]
qs = [sp.Rational(9, 10), sp.Rational(78, 100), sp.Rational(57, 100)]


def Fmax_geo(ps, u):
    return sp.prod([1 - p ** (u + 1) for p in ps])


def rh_geo(ps, u):
    Fu, Fum = Fmax_geo(ps, u), Fmax_geo(ps, u - 1)
    return sp.simplify((Fu - Fum) / Fu)


print("== 3.3 geometric (exact) ==")
for u in [1, 2, 4, 8, 20]:
    d = sp.nsimplify(rh_geo(q, u) - rh_geo(qs, u))
    print("u=%d:  h~X - h~Y = %s = %s" % (u, d, sp.N(d, 12)))
# printed claim: -0.0010584 @ u=1 ; +0.00628996 @ u=4  -> sign change alleged.

# ---------------- Counterexample 3.2: Poisson min hazard --------------------
def pois_S_tail(mu, u, prec_terms=400):
    """P(Poisson(mu) > u) by direct tail sum with bound:
    sum_{r>u} mu^r/r! computed upward until terms stop mattering at 300dps."""
    s = mpf(0)
    r = u + 1
    term = power(mu, r) / factorial(r)
    while term > mpf(10) ** (-250) and r < u + prec_terms:
        s += term
        r += 1
        term *= mu / r
    return exp(-mu) * s


def hz_min(mus, u):
    Su = mpf(1)
    Su1 = mpf(1)
    for m in mus:
        Su *= pois_S_tail(mpf(m), u)
        Su1 *= pois_S_tail(mpf(m), u + 1)
    return (Su - Su1) / Su


print("== 3.2 Poisson (300-digit tail sums) ==")
mu = (mpf(28), mpf("0.8"), mpf("0.1"))
mus = (mpf(27), mpf(1), mpf("0.9"))
for u in [6, 16]:
    print("u=%d: hX - hY = %s" % (u, mp.nstr(hz_min(mu, u) - hz_min(mus, u), 15)))
neg = None
for u in range(1, 60):
    d = hz_min(mu, u) - hz_min(mus, u)
    if d < 0:
        neg = u
        print("first negative diff at u=%d: %s" % (u, mp.nstr(d, 15)))
        break
print("no negative diff found" if neg is None else "sign change found")
