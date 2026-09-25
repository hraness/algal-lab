"""n=2 base-case probes + st-order control, exact arithmetic."""
import sys
import sympy as sp

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

s = sp.Symbol("s", positive=True)
z = sp.Symbol("z", positive=True)


def cls_tag(row, p):
    return "V" if in_Vn(row, p) else ("W" if in_Wn(row, p) else "-")


def certify(order, nu, p, nuB, pB, label, L=1):
    """nu may be rational; exponents cleared by z=s^{1/L}."""
    print(f"--- {label}")
    print(f"  A : row={[str(x) for x in nu]} p={[str(x) for x in p]} -> "
          f"{cls_tag(nu, p)}")
    print(f"  B : row={[str(x) for x in nuB]} p={[str(x) for x in pB]} -> "
          f"{cls_tag(nuB, pB)}")
    exA = [int(sp.Rational(vi) * L) for vi in nu]
    exB = [int(sp.Rational(vi) * L) for vi in nuB]
    Na = sum(pi * vi * z ** e for pi, vi, e in zip(p, nu, exA))
    Nb = sum(pi * vi * z ** e for pi, vi, e in zip(pB, nuB, exB))
    Da = sum(pi * z ** e for pi, e in zip(p, exA))
    Db = sum(pi * z ** e for pi, e in zip(pB, exB))
    if order == "rh":
        Da = 1 - Da
        Db = 1 - Db
    num = sp.Poly(sp.expand(Na * Db - Nb * Da), z)
    nroots = num.count_roots(0, 1)
    print(f"  L={L}, deg={num.degree()}, Sturm roots in (0,1): {nroots}")
    grid = [sp.Rational(k, 32) for k in range(1, 32)] + \
           [sp.Rational(m, 1024) for m in range(960, 1024, 8)]
    vals = [(q, sp.sign(num.as_expr().subs(z, q))) for q in grid]
    neg = [(q, num.as_expr().subs(z, q)) for q, sv in vals if sv < 0]
    pos = [(q, num.as_expr().subs(z, q)) for q, sv in vals if sv > 0]
    print("  sign pattern:",
          "".join("-" if sv < 0 else ("+" if sv > 0 else "0")
                  for _, sv in vals))
    if neg and pos:
        print(f"  CROSSING: num({neg[0][0]})={neg[0][1]}<0 ; "
              f"num({pos[0][0]})={pos[0][1]}>0")


H = sp.Rational

# n=2, rh, V_2 both sides (rate row), omega=1/2
certify("rh", [H(12, 5), H(1, 2)], [H(1, 4), H(3, 4)],
        [H(29, 20), H(29, 20)], [H(1, 2), H(1, 2)],
        "rh n=2 V_2 -> V_2, omega=1/2 (scan candidate)", L=20)

# n=2, rh, W_2 both sides, omega=1/4
certify("rh", [H(23), H(3, 2)], [H(5, 8), H(3, 8)],
        [H(55, 8), H(141, 8)], [H(7, 16), H(9, 16)],
        "rh n=2 W_2 -> W_2, omega=1/4 (scan candidate)", L=8)

# st-order control: separable sum, T on [nu;p]; check Fbar_A - Fbar_B sign
def st_control():
    import random
    from fractions import Fraction as F
    random.seed(3)
    bad = {"V": 0, "W": 0}
    cnt = {"V": 0, "W": 0}
    for _ in range(4000):
        nu = [F(random.randint(1, 20), random.randint(1, 6)) for _ in range(3)]
        xs = sorted(random.sample(range(1, 40), 2))
        cuts = [0] + xs + [40]
        p = [F(cuts[i + 1] - cuts[i], 40) for i in range(3)]
        cls = "V" if in_Vn(nu, p) else ("W" if in_Wn(nu, p) else None)
        if not cls:
            continue
        j, k = sorted(random.sample(range(3), 2))
        om = F(random.randint(1, 19), 20)
        nuB = list(nu)
        nuB[j] = om * nu[j] + (1 - om) * nu[k]
        nuB[k] = (1 - om) * nu[j] + om * nu[k]
        pB = list(p)
        pB[j] = om * p[j] + (1 - om) * p[k]
        pB[k] = (1 - om) * p[j] + om * p[k]
        clsB = "V" if in_Vn(nuB, pB) else ("W" if in_Wn(nuB, pB) else None)
        if clsB != cls:
            continue
        cnt[cls] += 1
        # SF difference on a float s-grid; a genuine st failure = both signs
        sg = []
        for sv in [k / 32 for k in range(1, 32)]:
            d = sum(float(pi) * sv ** vi for pi, vi in zip(p, nu)) - \
                sum(float(pi) * sv ** vi for pi, vi in zip(pB, nuB))
            sg.append(d)
        if any(x < -1e-12 for x in sg) and any(x > 1e-12 for x in sg):
            bad[cls] += 1
    print(f"st control (SF difference sign change): V3 {bad['V']}/{cnt['V']}, "
          f"W3 {bad['W']}/{cnt['W']} -- expect ~0 (separable lift is valid)")


st_control()
