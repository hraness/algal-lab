"""Fast float scan for BKB2022-own counterexample candidates + exact recheck.

Conventions:
  R (rate row):  matrix [nu; p], T acts on nu, exponents = nu (BKB could
                 parametrize components by rate).
  S (scale row): matrix [lam; p], T acts on lam, exponents nu = 1/lam
                 (BKF2024 convention; scale is the LS parameter).
Under S, class membership of (lam;p) is checked in scale coordinates; T-image
is computed in scale coordinates then inverted to rates.

Rates (exponential baseline, s = e^{-t} in (0,1)):
  rh: r(s) = sum p_i nu_i s^{nu_i} / (1 - sum p_i s^{nu_i})
  hr: h(s) = sum p_i nu_i s^{nu_i} / sum p_i s^{nu_i}
Reversed hazard under inverted-exponential baseline F(t)=e^{-1/t} (t^2 f
increasing):  t^2 r(t) = sum p_i lam_i s^{lam_i}/sum p_i s^{lam_i}, s=e^{-1/t}
-- identical ratio to hr, so hr certificates transfer.
"""
import sys, random
from fractions import Fraction as F

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

random.seed(20250925)
SGRID = [k / 64 for k in range(1, 64)]          # float grid on (0,1)


def Tpair(v, j, k, om):
    v = list(v)
    vj = om * v[j] + (1 - om) * v[k]
    vk = (1 - om) * v[j] + om * v[k]
    v[j], v[k] = vj, vk
    return v


def rand_prob(n):
    xs = sorted(random.sample(range(1, 40), n - 1))
    cuts = [0] + xs + [40]
    return [F(cuts[i + 1] - cuts[i], 40) for i in range(n)]


def rate_diff(order, nu_a, pa, nu_b, pb):
    """signs of rate_A - rate_B over the float grid."""
    out = []
    for s in SGRID:
        if order == "rh":
            Na = sum(pi * vi * s ** vi for pi, vi in zip(pa, nu_a))
            Nb = sum(pi * vi * s ** vi for pi, vi in zip(pb, nu_b))
            Da = 1 - sum(pi * s ** vi for pi, vi in zip(pa, nu_a))
            Db = 1 - sum(pi * s ** vi for pi, vi in zip(pb, nu_b))
        else:
            Na = sum(pi * vi * s ** vi for pi, vi in zip(pa, nu_a))
            Nb = sum(pi * vi * s ** vi for pi, vi in zip(pb, nu_b))
            Da = sum(pi * s ** vi for pi, vi in zip(pa, nu_a))
            Db = sum(pi * s ** vi for pi, vi in zip(pb, nu_b))
        out.append(Na / Da - Nb / Db)
    return out


def scan(order, n, ndraws, conv):
    """conv 'R': T on rates;  conv 'S': T on scales. Returns stats+examples."""
    cnt = {"V": 0, "W": 0}
    viol = {"V_geq": 0, "V_leq": 0, "W_geq": 0, "W_leq": 0,
            "V_both": 0, "W_both": 0}
    ex = {k: None for k in viol}
    for _ in range(ndraws):
        nu = [F(random.randint(1, 24), random.randint(1, 6)) for _ in range(n)]
        p = rand_prob(n)
        j, k = sorted(random.sample(range(n), 2))
        om = F(random.randint(1, 19), 20)
        pB = Tpair(p, j, k, om)
        if conv == "R":
            rowA, rowB = nu, Tpair(nu, j, k, om)
            nuB = rowB
        else:  # S: parameter row is scale lam = 1/nu
            lam = [1 / x for x in nu]
            lamB = Tpair(lam, j, k, om)
            rowA, rowB = lam, lamB
            nuB = [1 / x for x in lamB]
        clsA = "V" if in_Vn(rowA, p) else ("W" if in_Wn(rowA, p) else None)
        clsB = "V" if in_Vn(rowB, pB) else ("W" if in_Wn(rowB, pB) else None)
        if not clsA or clsA != clsB:
            continue
        cnt[clsA] += 1
        fs = [float(x) for x in nu]
        fsB = [float(x) for x in nuB]
        fp = [float(x) for x in p]
        fpB = [float(x) for x in pB]
        sg = rate_diff(order, fs, fp, fsB, fpB)
        neg, pos = any(x < -1e-12 for x in sg), any(x > 1e-12 for x in sg)
        rec = (nu, p, nuB, pB, om, [round(x, 6) for x in sg])
        if neg:
            viol[clsA + "_geq"] += 1
            if ex[clsA + "_geq"] is None:
                ex[clsA + "_geq"] = rec
        if pos:
            viol[clsA + "_leq"] += 1
            if ex[clsA + "_leq"] is None:
                ex[clsA + "_leq"] = rec
        if neg and pos:
            viol[clsA + "_both"] += 1
            if ex[clsA + "_both"] is None:
                ex[clsA + "_both"] = rec
    print(f"-- {order} n={n} conv={conv}: admissible V={cnt['V']} W={cnt['W']}")
    for cls in ("V", "W"):
        c = cnt[cls]
        if c:
            print(f"   {cls}_{n}: A-B<0 {viol[cls+'_geq']}/{c}; "
                  f"A-B>0 {viol[cls+'_leq']}/{c}; both {viol[cls+'_both']}")
    for kk, vv in ex.items():
        if vv:
            nu, p, nuB, pB, om, sg = vv
            print(f"   e.g. {kk}: nu={tuple(str(x) for x in nu)} "
                  f"p={tuple(str(x) for x in p)} om={om}")
            print(f"        nuB={tuple(str(x) for x in nuB)} "
                  f"pB={tuple(str(x) for x in pB)}")
    return ex


if __name__ == "__main__":
    nd = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
    print("BKB2022-own admissible-instance scan (float, exact recheck later)")
    for conv in ("R", "S"):
        for n in (2, 3):
            for order in ("rh", "hr"):
                scan(order, n, nd, conv)
