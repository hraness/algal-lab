"""Independent C3 verification for arxiv:2002.12474 refuted records.

Printed models (verbatim):
  W-G(a,b,g): H(x) = 1 - exp(-a * (F(gx)/(1-F(gx)))^b); with exponential
    baseline F(u) = 1 - e^{-u}:  S(x) = exp(-a*(e^{g x}-1)^b).
  GM(a,b,l):  F(x) = 1 - exp(-l x - (a/b)(e^{b x}-1)), x>0.

Weak-majorization glyph "a <w b" is not resolvable in the text layer:
  Def (4) submajorization: largest-first partial sums of a <= b's.
  Def (5) supermajorization: smallest-first partial sums of a >= b's.
Both readings are tested; the eval used Def (4) instances.
"""
import json
import os
from mpmath import mp, mpf, exp

mp.dps = 120
HERE = os.path.dirname(os.path.abspath(__file__))


def S_wg(x, a, b, g):
    return exp(-mpf(a) * (exp(mpf(g) * x) - 1) ** mpf(b))


def S_gm(x, a, b, l):
    return exp(-mpf(l) * x - (mpf(a) / mpf(b)) * (exp(mpf(b) * x) - 1))


def F_max(x, survs):
    p = mpf(1)
    for s in survs:
        p *= 1 - s(x)
    return p


def rhr_wg_exp(x, a, b, g):
    """Reversed hazard f/F of W-Exp: F=1-e^{-a v}, v=(e^{gx}-1)^b,
    f = a v' e^{-a v}, v' = b g e^{gx}(e^{gx}-1)^{b-1}.
    r~ = a v'/(e^{a v}-1)."""
    v = (exp(mpf(g) * x) - 1) ** mpf(b)
    vp = mpf(b) * mpf(g) * exp(mpf(g) * x) * (exp(mpf(g) * x) - 1) ** (mpf(b) - 1)
    return mpf(a) * vp / (exp(mpf(a) * v) - 1)


def weak_sub(a, b):
    da, db = sorted(a, reverse=True), sorted(b, reverse=True)
    return all(sum(da[:k]) <= sum(db[:k]) for k in range(1, len(da) + 1))


def weak_sup_paper(a, b):
    """a <^w b per printed Def (5): smallest-first partial sums of a >= b's."""
    aa, ab = sorted(a), sorted(b)
    return all(sum(aa[:k]) >= sum(ab[:k]) for k in range(1, len(aa) + 1))


xs = [mpf(10) ** (k / 4) for k in range(-40, 9)]
xs += [mpf(i) / 20 for i in range(1, 400)]

report = {}

# ---------- Theorem 4: alpha <w alpha* => Xn:n <=rh Yn:n (W-Exp, b=g=1)
# rhr of parallel system = sum of component reversed hazards
t4 = []
# eval instances: submajorization reading
for aX, aY in [([1, 2], [2, 3]), ([1, 2, 3], [2, 3, 4])]:
    assert weak_sub(aX, aY)
    assert not weak_sup_paper(aX, aY)
    diffs = [(sum(rhr_wg_exp(t, a, 1, 1) for a in aX)
              - sum(rhr_wg_exp(t, a, 1, 1) for a in aY), t) for t in xs]
    mn, mx = min(diffs), max(diffs)
    t4.append({"alphaX": aX, "alphaY": aY, "reading": "submajorization",
               "min(rX~-rY~)": str(mn[0]), "argmin": str(mn[1]),
               "max(rX~-rY~)": str(mx[0]), "argmax": str(mx[1]),
               "printed_X<=rh_Y": bool(mx[0] <= 0),
               "reversed_Y<=rh_X": bool(mn[0] >= 0)})
# supermajorization reading instances
for aX, aY in [([2, 3], [1, 4]), ([2, 4], [1, 5]), ([3, 4], [1, 3, 5])]:
    ok = weak_sup_paper(aX, aY)
    diffs = [(sum(rhr_wg_exp(t, a, 1, 1) for a in aX)
              - sum(rhr_wg_exp(t, a, 1, 1) for a in aY), t) for t in xs]
    mn, mx = min(diffs), max(diffs)
    t4.append({"alphaX": aX, "alphaY": aY, "reading": "supermajorization",
               "admissible": ok,
               "min(rX~-rY~)": str(mn[0]), "argmin": str(mn[1]),
               "max(rX~-rY~)": str(mx[0]), "argmax": str(mx[1]),
               "printed_X<=rh_Y": bool(mx[0] <= 0),
               "reversed_Y<=rh_X": bool(mn[0] >= 0)})
report["Theorem 4"] = t4

# ---------- Theorem 5: gamma <w gamma* => Xn:n <=st Yn:n (W-Exp a=1,b=2)
t5 = []
for gX, gY in [([1, 2], [2, 3]), ([1, 2, 3], [2, 3, 4])]:
    assert weak_sub(gX, gY)
    diffs = [(F_max(t, [lambda u, g=g: S_wg(u, 1, 2, g) for g in gX])
              - F_max(t, [lambda u, g=g: S_wg(u, 1, 2, g) for g in gY]), t)
             for t in xs]
    mn, mx = min(diffs), max(diffs)
    # printed X<=st Y <=> F_X >= F_Y
    t5.append({"gX": gX, "gY": gY, "reading": "submajorization",
               "min(FX-FY)": str(mn[0]), "argmin": str(mn[1]),
               "max(FX-FY)": str(mx[0]), "argmax": str(mx[1]),
               "printed_X<=st_Y": bool(mn[0] >= 0),
               "reversed_Y<=st_X": bool(mx[0] <= 0)})
for gX, gY in [([2, 3], [1, 4]), ([2, 4], [1, 5]), ([3, 4], [1, 3, 5])]:
    ok = weak_sup_paper(gX, gY)
    diffs = [(F_max(t, [lambda u, g=g: S_wg(u, 1, 2, g) for g in gX])
              - F_max(t, [lambda u, g=g: S_wg(u, 1, 2, g) for g in gY]), t)
             for t in xs]
    mn, mx = min(diffs), max(diffs)
    t5.append({"gX": gX, "gY": gY, "reading": "supermajorization",
               "admissible": ok,
               "min(FX-FY)": str(mn[0]), "argmin": str(mn[1]),
               "max(FX-FY)": str(mx[0]), "argmax": str(mx[1]),
               "printed_X<=st_Y": bool(mn[0] >= 0),
               "reversed_Y<=st_X": bool(mx[0] <= 0)})
report["Theorem 5"] = t5

# ---------- Theorem 9: lambda <w lambda* => X1:n =st Y1:n (GM a,b common)
t9 = []
# eval instance: lambda=(1,4), lambda*=(3,3), a=2,b=1
for lX, lY in [([1, 4], [3, 3]), ([1, 2], [2, 3]), ([3, 4], [1, 4])]:
    n, a, b = len(lX), 2, 1
    SX = lambda t: exp(-mpf(sum(lX)) * t - (n * a / b) * (exp(b * t) - 1))
    SY = lambda t: exp(-mpf(sum(lY)) * t - (n * a / b) * (exp(b * t) - 1))
    same = all(abs(SX(t) - SY(t)) < mpf(10) ** -60 for t in xs[:40])
    t9.append({"lX": lX, "lY": lY,
               "weak_sub": weak_sub(lX, lY),
               "weak_sup_paper": weak_sup_paper(lX, lY),
               "sums": [sum(lX), sum(lY)],
               "survivals_equal": bool(same)})
report["Theorem 9"] = t9

# ---------- Theorem 10: alpha <w alpha* => Xn:n <=st Yn:n (GM b=l=1)
t10 = []
for aX, aY in [([1, 2], [2, 3]), ([1, 2, 3], [2, 3, 4])]:
    assert weak_sub(aX, aY)
    diffs = [(F_max(t, [lambda u, a=a: S_gm(u, a, 1, 1) for a in aX])
              - F_max(t, [lambda u, a=a: S_gm(u, a, 1, 1) for a in aY]), t)
             for t in xs]
    mn, mx = min(diffs), max(diffs)
    t10.append({"aX": aX, "aY": aY, "reading": "submajorization",
                "min(FX-FY)": str(mn[0]), "argmin": str(mn[1]),
                "max(FX-FY)": str(mx[0]), "argmax": str(mx[1]),
                "printed_X<=st_Y": bool(mn[0] >= 0),
                "reversed_Y<=st_X": bool(mx[0] <= 0)})
for aX, aY in [([2, 3], [1, 4]), ([2, 4], [1, 5]), ([3, 4], [1, 3, 5])]:
    ok = weak_sup_paper(aX, aY)
    diffs = [(F_max(t, [lambda u, a=a: S_gm(u, a, 1, 1) for a in aX])
              - F_max(t, [lambda u, a=a: S_gm(u, a, 1, 1) for a in aY]), t)
             for t in xs]
    mn, mx = min(diffs), max(diffs)
    t10.append({"aX": aX, "aY": aY, "reading": "supermajorization",
                "admissible": ok,
                "min(FX-FY)": str(mn[0]), "argmin": str(mn[1]),
                "max(FX-FY)": str(mx[0]), "argmax": str(mx[1]),
                "printed_X<=st_Y": bool(mn[0] >= 0),
                "reversed_Y<=st_X": bool(mx[0] <= 0)})
report["Theorem 10"] = t10

print(json.dumps(report, indent=1))
with open(os.path.join(HERE, "c3_verify_2002_12474.out.json"), "w") as fh:
    json.dump(report, fh, indent=1)
