"""Independent C3 verification for arxiv:1905.00425 Theorem 3.4 (hr).

Printed: Xi ~ Gum(mu_i, sigma), F(x)=exp(-e^{-(x-mu)/sigma});
 mu >=^m mu* => X_{1:n} <=hr Y_{1:n} i.e. r_X(x) >= r_Y(x) for all x.

Series hazard = sum of component hazards (printed and standard):
  r_{X1:n}(x) = (1/sigma) * sum_i phi(t_i),  t_i = e^{(mu_i - x)/sigma},
  phi(t) = t/(e^t - 1).

Fresh mpmath implementation at 120 digits.
"""
import json
import os
from mpmath import mp, mpf, exp, expm1

mp.dps = 120
HERE = os.path.dirname(os.path.abspath(__file__))


def phi(t):
    # t/(e^t - 1), overflow-safe: for huge t returns ~0, for tiny t ~1
    if t > 700:
        return mpf(0)
    return t / expm1(t)


def r_min(x, mus, sigma):
    s = mpf(0)
    for m in mus:
        t = exp((mpf(m) - mpf(x)) / mpf(sigma))
        s += phi(t)
    return s / mpf(sigma)


insts = [([3, 1], [2, 2], mpf(1)),
         ([4, 2, 1], [3, 2, 2], mpf(2)),
         ([5, 3, 1], [3, 3, 3], mpf("0.5")),
         ([9, 5, 1], [7, 5, 3], mpf(2))]

def majorizes(a, b):
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return mpf(sum(A)) == mpf(sum(B)) and all(
        mpf(sum(A[:k])) >= mpf(sum(B[:k])) for k in range(1, len(A)))

results = []
xs = [mpf(-80) + mpf(i) / 5 for i in range(0, 1600)]  # -80 .. 240 step 0.2
xs += [mpf(10) ** (k / 4) for k in range(-40, 33)]
for mX, mY, sg in insts:
    assert majorizes(mX, mY)
    diffs = [(r_min(t, mX, sg) - r_min(t, mY, sg), t) for t in xs]
    mn = min(diffs)
    mx = max(diffs)
    # witness reported at x=8/5
    w = mpf(8) / 5
    results.append({
        "muX": mX, "muY": mY, "sigma": str(sg),
        "min(rX-rY)": str(mn[0]), "argmin": str(mn[1]),
        "max(rX-rY)": str(mx[0]), "argmax": str(mx[1]),
        "rX(8/5)-rY(8/5)": str(r_min(w, mX, sg) - r_min(w, mY, sg)),
        "printed_hr_holds": bool(mn[0] >= 0),
        "reversed_holds": bool(mx[0] <= 0),
    })
print(json.dumps(results, indent=1))
with open(os.path.join(HERE, "c3_verify_1905_00425.out.json"), "w") as fh:
    json.dump(results, fh, indent=1)
