"""Admissible/violation sweep at claim shape for SMH2026, n=3 only.

Claim shapes (canonical for the HF2018/NT2020/BKZ2021 machinery SMH cites;
all audited "as claim shape" since the paper is closed access):
  A  hr of alpha-mixture SF: (p,lam),(p,gam) in U_3, lam >maj gam
     ==> h_a^lam <= h_a^gam for all t (equivalently all u=e^{-a t} in (0,1)).
  B  hr of alpha-mixture SF: [p;lam] in V_3 (resp. W_3), [q;gam]=[p;lam] M_T
     single T-transform ==> hr ordering in the literature's direction
     (V: h_p >= h_q; W: h_p <= h_q).
Counts are exact-rational evaluations on a 10-point grid in u.
Since the bracket is alpha-independent, each admissible/violation count
applies uniformly to every alpha>0.
"""
import sys, random
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/hf2018-nt2020")
import sympy as sp
from audit_lib import R, majorizes, in_Un, in_Vn, in_Wn
from audit_hf_nt import htilde, ttransform, report, GRID

s = sp.Symbol("s", positive=True)


def sweep_A(trials=8000, seed=41):
    rng = random.Random(seed)
    adm = vio = cross = 0; ex = None
    for _ in range(trials):
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(3)),
                         reverse=True))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 9) for _ in range(3)))
        gam = tuple(sorted(rng.randint(1, 9) for _ in range(3)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not majorizes(list(lam), list(gam)) or lam == gam:
            continue
        adm += 1
        d = sp.cancel(sp.together(htilde(p, lam, s) - htilde(p, gam, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        r = report(vals, -1)
        if r != "ok":
            vio += 1
            if r == "crossing":
                cross += 1
            ex = ex or (p, lam, gam, vals)
    return adm, vio, cross, ex


def sweep_B(cls="V", trials=8000, seed=43):
    rng = random.Random(seed)
    adm = vio = cross = 0; ex = None
    for _ in range(trials):
        p = tuple(R(rng.randint(1, 40), 40) for _ in range(3))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(rng.randint(1, 9) for _ in range(3))
        ok = in_Vn(list(p), list(lam)) if cls == "V" else in_Wn(list(p), list(lam))
        if not ok:
            continue
        i, j = sorted(rng.sample(range(3), 2))
        om = R(rng.randint(1, 19), 20)
        qg = ttransform([list(p), list(lam)], i, j, om)
        q, gam = qg[0], qg[1]
        adm += 1
        d = sp.cancel(sp.together(htilde(p, lam, s) - htilde(q, gam, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        exp = +1 if cls == "V" else -1
        r = report(vals, exp)
        if r != "ok":
            vio += 1
            if r == "crossing":
                cross += 1
            ex = ex or (p, lam, q, gam, i, j, om, vals)
    return adm, vio, cross, ex


if __name__ == "__main__":
    a, v, c, e = sweep_A()
    print(f"A n=3 U3+maj hr: admissible={a} violations={v} (crossings={c})")
    if e:
        print("   first violation:", e[0], e[1], e[2],
              [str(sg) for _, sg in e[3]])
    for cls in ("V", "W"):
        a, v, c, e = sweep_B(cls)
        print(f"B n=3 single-T cls={cls}: admissible={a} violations={v}"
              f" (crossings={c})")
        if e:
            print("   first violation:", e[0], e[1], "->", e[2], e[3],
                  "cols", e[4], e[5], "om", e[6])
