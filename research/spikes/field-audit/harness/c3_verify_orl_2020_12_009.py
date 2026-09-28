"""Independent C3 verification for doi:10.1016/j.orl.2020.12.009
Counterexample 4.1 (both printed cases).

Printed model (verbatim):
  PO marginal cdf:  F_{a_i}(x) = F(x) / (1 - (1-a_i) Fbar(x))
                              = F(x) / (a_i + (1-a_i) F(x))
  Parallel cdf:     F_{X3:3}(x) = phi1( sum_i psi1(F_{a_i}(x)) ), psi=phi^{-1}
  baseline: F(x) = 1 - e^{-x^0.5}, x>=0
  alpha = (0.9, 1.45, 2.15)  >=^w  beta = (1.2, 1.95, 2.65)   [paper's Def:
    smallest-first partial sums of alpha <= beta's: 0.9<=1.2, 2.35<=3.15,
    4.5<=5.8 -- TRUE]

  case (a): phi1(t) = 0.9/log(t + e^{0.9})   -> psi1(u) = e^{0.9/u} - e^{0.9}
            phi2(t) = e^{1-(1+t)^{1/8}}      -> psi2(u) = (1-log u)^8 - 1
  case (b): phi1(t) = e^{(1-e^t)/0.9}        -> psi1(u) = log(1-0.9 log u)
            phi2(t) = (2/(e^t+1))^{5}        -> psi2(u) = log(2 u^{-0.2} - 1)

Printed conclusion: 'the stochastic ordering result in Theorem 4.1 is not
attained' (i.e. X_{3:3} <=st Y_{3:3} fails; figures show crossing).
"""
import json
import os
from mpmath import mp, mpf, exp, log

mp.dps = 120
HERE = os.path.dirname(os.path.abspath(__file__))


def F_base(x):
    return 1 - exp(-mpf(x) ** mpf("0.5"))


def F_po(x, a):
    F = F_base(x)
    return F / (mpf(a) + (1 - mpf(a)) * F)


def Fmax(x, alphas, phi, psi):
    s = mpf(0)
    for a in alphas:
        s += psi(F_po(x, a))
    return phi(s)


alpha = [mpf("0.9"), mpf("1.45"), mpf("2.15")]
beta = [mpf("1.2"), mpf("1.95"), mpf("2.65")]

# case (a) PRINTED generators
phi1a = lambda t: mpf("0.9") / log(t + exp(mpf("0.9")))
psi1a = lambda u: exp(mpf("0.9") / u) - exp(mpf("0.9"))
phi2a = lambda t: exp(1 - (1 + t) ** (mpf(1) / 8))
psi2a = lambda u: (1 - log(u)) ** 8 - 1

# case (a) EVAL's (wrong) generator for phi2: Gumbel-Barnett e^{(1-e^t)/8}
phi2a_eval = lambda t: exp((1 - exp(t)) / 8)
psi2a_eval = lambda u: log(1 - 8 * log(u))

# case (b) generators
phi1b = lambda t: exp((1 - exp(t)) / mpf("0.9"))
psi1b = lambda u: log(1 - mpf("0.9") * log(u))
phi2b = lambda t: (2 / (exp(t) + 1)) ** 5
psi2b = lambda u: log(2 * u ** (-mpf("0.2")) - 1)

xs = [mpf(i) / 100 for i in range(1, 600)] + [mpf(i) / 10 for i in range(60, 300)] + \
     [mpf(10) ** (k / 4) for k in range(-16, 9)]

report = {}

for tag, p1, s1, p2, s2 in [
        ("case (a) PRINTED", phi1a, psi1a, phi2a, psi2a),
        ("case (a) EVAL-gen", phi1a, psi1a, phi2a_eval, psi2a_eval),
        ("case (b) PRINTED", phi1b, psi1b, phi2b, psi2b)]:
    diffs = []
    for t in xs:
        try:
            FX = Fmax(t, alpha, p1, s1)
            FY = Fmax(t, beta, p2, s2)
            diffs.append((FX - FY, t))
        except Exception:
            pass
    pos = [d for d in diffs if d[0] > mpf(10) ** -60]
    neg = [d for d in diffs if d[0] < -mpf(10) ** -60]
    mn = min(diffs); mx = max(diffs)
    report[tag] = {
        "min(FX-FY)": str(mn[0]), "argmin": str(mn[1]),
        "max(FX-FY)": str(mx[0]), "argmax": str(mx[1]),
        "n_points": len(diffs),
        "n_pos": len(pos), "n_neg": len(neg),
        "printed_claim_fails": len(pos) > 0 and len(neg) > 0,
        "X_leqst_Y_fails": len(neg) > 0,   # need FX>=FY; FX-FY<0 violates
        "Y_leqst_X_fails": len(pos) > 0,
    }

print(json.dumps(report, indent=1))
with open(os.path.join(HERE, "c3_verify_orl_2020_12_009.out.json"), "w") as fh:
    json.dump(report, fh, indent=1)
