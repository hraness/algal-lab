"""Integer-rate admissible-instance search (small polys -> fast Sturm).

Rates nu_i positive integers; T-transform on the rate row with omega such that
nuB stays integer (omega in {k/10}, mixes same-parity pairs). Classes checked
on (nu;p).  Convention R only; scale-row cases are handled by interval cert.
"""
import sys, random
from fractions import Fraction as F

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

random.seed(7)
SGRID = [k / 128 for k in range(1, 128)]


def rand_prob(n):
    xs = sorted(random.sample(range(1, 40), n - 1))
    cuts = [0] + xs + [40]
    return [F(cuts[i + 1] - cuts[i], 40) for i in range(n)]


def diff_sg(order, nu, p, nuB, pB):
    sg = []
    for s in SGRID:
        Na = sum(float(pi) * vi * s ** vi for pi, vi in zip(p, nu))
        Nb = sum(float(pi) * vi * s ** vi for pi, vi in zip(pB, nuB))
        Da = sum(float(pi) * s ** vi for pi, vi in zip(p, nu))
        Db = sum(float(pi) * s ** vi for pi, vi in zip(pB, nuB))
        if order == "rh":
            Da = 1 - Da
            Db = 1 - Db
        sg.append(Na / Da - Nb / Db)
    return sg


def find(order, cls_want, need):
    found = []
    tries = 0
    while len(found) < need and tries < 200000:
        tries += 1
        n = 3
        nu = [random.randint(1, 20) for _ in range(n)]
        if len(set(nu)) < n:
            continue
        p = rand_prob(n)
        cls = "V" if in_Vn(nu, p) else ("W" if in_Wn(nu, p) else None)
        if cls != cls_want:
            continue
        j, k = sorted(random.sample(range(n), 2))
        if (nu[j] + nu[k]) % 2:
            continue                    # keep omega=1/2 image integral
        nuB = list(nu)
        nuB[j] = (nu[j] + nu[k]) // 2
        nuB[k] = nuB[j]
        pB = [F(0)] * n
        om = F(1, 2)
        pB[j] = om * p[j] + (1 - om) * p[k]
        pB[k] = (1 - om) * p[j] + om * p[k]
        for i in range(n):
            if i not in (j, k):
                pB[i] = p[i]
        clsB = "V" if in_Vn(nuB, pB) else ("W" if in_Wn(nuB, pB) else None)
        if clsB != cls:
            continue
        sg = diff_sg(order, nu, p, nuB, pB)
        if any(x < -1e-11 for x in sg) and any(x > 1e-11 for x in sg):
            found.append((nu, p, nuB, pB, om, (j, k)))
    print(f"{order} {cls_want}: {len(found)} sign-changing instances "
          f"in {tries} tries")
    for rec in found:
        print("   ", rec)
    return found


if __name__ == "__main__":
    for order in ("rh", "hr"):
        for cls in ("V", "W"):
            find(order, cls, 3)
