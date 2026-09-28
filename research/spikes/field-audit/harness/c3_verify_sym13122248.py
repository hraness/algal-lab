"""Independent C3 verification for doi:10.3390/sym13122248.

Printed model:
  MOTL-G marginal survival: zeta(a,b,G) = a(1-T^b)/(a+(1-a)T^b),
      T = 1-(1-G)^2  [printed cdf eq (1): T^b/(a+ (1-a) T^b)]
  shocked series: S_Y1:n(x) = (prod p_i) * psi(sum_i phi(zeta_i(x))),
      psi = Archimedean generator, phi = psi^{-1}
  paper's weak supermajorization Def 2(ii): x >=^w y iff
      sum_{i<=j} x_(i) <= sum y_(i) (smallest-first partial sums).

Records: Example 1 (st), Example 3 (hr, no-order counterexample),
         Example 4 (hr, no-order counterexample), Theorem 5 (hr).
"""
import json
import os
from mpmath import mp, mpf, exp, log

mp.dps = 120
HERE = os.path.dirname(os.path.abspath(__file__))


def T_of_G(G):
    return 1 - (1 - G) ** 2


def zeta(a, b, G):
    T = T_of_G(G)
    return mpf(a) * (1 - T ** mpf(b)) / (mpf(a) + (1 - mpf(a)) * T ** mpf(b))


def series_S(x, albetas, Gfun, psi, phi, ps):
    s = mpf(0)
    for a, b in albetas:
        s += phi(zeta(a, b, Gfun(x)))
    prodp = mpf(1)
    for p in ps:
        prodp *= p
    return prodp * psi(s)


# generators
def clayton(theta):
    return (lambda t: (theta * t + 1) ** (-1 / mpf(theta)),
            lambda u: (u ** (-mpf(theta)) - 1) / mpf(theta))


def amh():
    return (lambda t: 2 / (1 + exp(t)),
            lambda u: log(2 / u - 1))


def indep():
    return (lambda t: exp(-t), lambda u: -log(u))


def gumbel(theta):
    return (lambda t: exp(-t ** (1 / mpf(theta))),
            lambda u: (-log(u)) ** mpf(theta))


GLom = lambda x: 1 - 1 / (1 + x)
GExp = lambda x: 1 - exp(-x)
GU = lambda x: x

report = {}

# ---------- Example 1: Y1:3 <=st Y1:3* claimed ----------
psi2, phi2 = clayton(2)
psi4, phi4 = clayton(4)
alb = [(mpf("1.1"), mpf(2)), (mpf(4), mpf(5)), (mpf("6.5"), mpf(6))]
gde = [(mpf("3.5"), mpf("4.5")), (mpf(4), mpf(5)), (mpf("6.3"), mpf("5.8"))]
pu = [mpf("0.05"), mpf("0.08"), mpf("0.22")]
pus = [mpf("0.01"), mpf("0.21"), mpf("0.03")]
ps = [exp(-u) for u in pu]
pss = [exp(-u) for u in pus]
xs = [mpf(i) / 100 for i in range(1, 400)] + [mpf(i) / 10 for i in range(40, 300)] + \
     [mpf("64") / 15] + [mpf(10) ** (-k) for k in range(1, 13)] + \
     [mpf(10) ** (k / 4) for k in range(-12, 9)]
xs = sorted(set(xs))
diffs = [(series_S(t, alb, GLom, psi2, phi2, ps)
          - series_S(t, gde, GExp, psi4, phi4, pss), t) for t in xs]
mn, mx = min(diffs), max(diffs)
report["Example 1"] = {
    "min(S_Y - S_Y*)": str(mn[0]), "argmin": str(mn[1]),
    "max(S_Y - S_Y*)": str(mx[0]), "argmax": str(mx[1]),
    "printed_Y<=st_Y*": bool(mx[0] <= 0),
    "reversed_Y*<=st_Y": bool(mn[0] >= 0),
    "at_eval_witness_64/15": str(dict(diffs).get(mpf(64) / 15)),
}

# ---------- Example 3: survival ratio claimed NON-monotone ----------
psiA, phiA = amh()
ab3 = [(mpf(2), mpf(1)), (mpf(3), mpf(1))]
gd3 = [(mpf(4), mpf(1)), (mpf(6), mpf(1))]
ps3 = [mpf("0.5"), mpf("0.5")]       # product 1/4
pss3 = [mpf("0.3"), mpf("0.25")]     # product 3/40 -> ratio 0.3
xs3 = [mpf(i) / 1000 for i in range(1, 1000)]
SU3 = [series_S(t, ab3, GU, psiA, phiA, ps3) for t in xs3]
SV3 = [series_S(t, gd3, GU, psiA, phiA, pss3) for t in xs3]
rat = [v / u for u, v in zip(SU3, SV3)]  # S_Y*/S_Y; Y<=hrY* iff increasing
inc = all(rat[i + 1] >= rat[i] for i in range(len(rat) - 1))
dec = all(rat[i + 1] <= rat[i] for i in range(len(rat) - 1))
drat = [rat[i + 1] - rat[i] for i in range(len(rat) - 1)]
nup = sum(1 for d in drat if d > mpf(10) ** -40)
ndn = sum(1 for d in drat if d < -mpf(10) ** -40)
report["Example 3"] = {
    "ratio_monotone_increasing": bool(inc),
    "ratio_monotone_decreasing": bool(dec),
    "n_increases": nup, "n_decreases": ndn,
    "ratio_first": str(rat[0]), "ratio_min": str(min(rat)),
    "ratio_max": str(max(rat)), "ratio_last": str(rat[-1]),
    "argmin_x": str(xs3[rat.index(min(rat))]),
    "argmax_x": str(xs3[rat.index(max(rat))]),
    "printed_nonmonotone": nup > 0 and ndn > 0,
}

# ---------- Example 4: survival ratio claimed NON-monotone (indep) ----------
psiI, phiI = indep()
ab4 = [(mpf("1.2"), mpf(2)), (mpf("1.2"), mpf(7))]
gd4 = [(mpf("1.2"), mpf(6)), (mpf("1.2"), mpf(9))]
ps4 = [mpf("0.5"), mpf("0.5")]
pss4 = [mpf("0.75"), mpf(1)]        # product 3/4 vs 1/4 -> ratio 3
xs4 = xs3
SU4 = [series_S(t, ab4, GU, psiI, phiI, ps4) for t in xs4]
SV4 = [series_S(t, gd4, GU, psiI, phiI, pss4) for t in xs4]
rat4 = [v / u for u, v in zip(SU4, SV4)]
drat4 = [rat4[i + 1] - rat4[i] for i in range(len(rat4) - 1)]
nup4 = sum(1 for d in drat4 if d > mpf(10) ** -40)
ndn4 = sum(1 for d in drat4 if d < -mpf(10) ** -40)
report["Example 4"] = {
    "ratio_monotone_increasing": all(d >= -mpf(10) ** -40 for d in drat4),
    "ratio_monotone_decreasing": all(d <= mpf(10) ** -40 for d in drat4),
    "n_increases": nup4, "n_decreases": ndn4,
    "ratio_first": str(rat4[0]), "ratio_min": str(min(rat4)),
    "ratio_max": str(max(rat4)), "ratio_last": str(rat4[-1]),
    "argmin_x": str(xs4[rat4.index(min(rat4))]),
    "argmax_x": str(xs4[rat4.index(max(rat4))]),
    "printed_nonmonotone": nup4 > 0 and ndn4 > 0,
}

# ---------- Theorem 5: alpha ~w gamma -> Y <=hr Y* ----------
# eval instances: U alpha=(3,1) vs V alpha=(2,2), beta=2;
#                 U alpha=(4,2,1) vs V alpha=(3.5,2,1.5), beta=1
# shocks: prod p=(1/2)^n <= prod p*=(3/4)^n ; copula: Gumbel theta=2
# (log-convex — the proof's direction; printed 'log-concave' is a slip).
# baselines free in the printed statement: test both assignments.
def wsup_paper(a, b):
    aa, bb = sorted(a), sorted(b)
    return all(sum(aa[:k]) <= sum(bb[:k]) for k in range(1, len(aa) + 1))

psiG2, phiG2 = gumbel(2)
t5 = []
for U, V in [([(3, 2), (1, 2)], [(2, 2), (2, 2)]),
             ([(4, 1), (2, 1), (1, 1)], [(mpf("3.5"), 1), (2, 1), (mpf("1.5"), 1)])]:
    al = [a for a, _ in U]; ga = [a for a, _ in V]
    for GU_, GV_ in [(GLom, GExp), (GExp, GLom)]:
        n = len(U)
        pU = [mpf("0.5")] * n
        pV = [mpf("0.75")] * n
        xs5 = [mpf(i) / 100 for i in range(1, 400)] + \
              [mpf(i) / 10 for i in range(40, 200)] + \
              [mpf("64") / 15] + [mpf(10) ** (-k) for k in range(1, 13)]  # noqa
        xs5 = sorted(set(xs5))
        SU = [series_S(t, U, GU_, psiG2, phiG2, pU) for t in xs5]
        SV = [series_S(t, V, GV_, psiG2, phiG2, pV) for t in xs5]
        rat = [v / u for u, v in zip(SU, SV)]  # Y<=hrY* iff S_Y*/S_Y increasing
        dr = [rat[i + 1] - rat[i] for i in range(len(rat) - 1)]
        nup = sum(1 for d in dr if d > mpf(10) ** -40)
        ndn = sum(1 for d in dr if d < -mpf(10) ** -40)
        t5.append({"alphaU": [str(a) for a in al], "alphaV": [str(a) for a in ga],
                   "GU": "Lomax" if GU_ is GLom else "Exp",
                   "GV": "Lomax" if GV_ is GLom else "Exp",
                   "admissible_wsup": wsup_paper(al, ga),
                   "n_increases": nup, "n_decreases": ndn,
                   "ratio_min": str(min(rat)), "ratio_max": str(max(rat)),
                   "argmax_x": str(xs5[rat.index(max(rat))]),
                   "printed_incr": ndn == 0})
report["Theorem 5"] = t5

print(json.dumps(report, indent=1))
with open(os.path.join(HERE, "c3_verify_sym13122248.out.json"), "w") as fh:
    json.dump(report, fh, indent=1)
