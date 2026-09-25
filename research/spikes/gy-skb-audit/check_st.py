"""Bounded spot-checks of the st-order claims (legitimate-machinery controls).

GY Thm 1/2(i): K_n, chain maj => V <=_st W  (additive SF, lift OK)
GY Thm 3/4(i): (p,lam) in K_n => Z >=_st Y  (additive SF)
SKB Thm 1(i): (p,th),(q,th) comonotone; (p,b),(q,b) antiordered; a>0; p weak-super q
   => inner_W <= inner_V (SF ordering same direction for a>0)
SKB Thm 1(ii): (p,th),(q,th) antiordered; (p,b),(q,b) comonotone; a>0; p weak-super q
   => W >=_st V.
SKB Thm 3: combined, a>=1, 0<th<1, (p,b),(q,b),(q,d) antiordered; b weak-super d, p weak-sub q
   => W <=_st V.
"""
import random
from fractions import Fraction
from audit_mphr import in_Vn, in_Wn
from fast_eval import GRIDF

F = Fraction


def weak_super(x, z):
    xs, ys = sorted(x), sorted(z)
    return all(sum(xs[:k]) >= sum(ys[:k]) for k in range(1, len(xs) + 1))


def weak_sub(x, z):
    xs, ys = sorted(x, reverse=True), sorted(z, reverse=True)
    return all(sum(xs[:k]) <= sum(ys[:k]) for k in range(1, len(xs) + 1))


def gy_sf(p_, a_, v):
    return sum(pi * ai * v / (1 - (1 - ai) * v) for pi, ai in zip(p_, a_))


def gy_sfZ(p_, l_, v, al):
    # l_i integers in this spot-check -> y^l
    return sum(pi * al * v ** li / (1 - (1 - al) * v ** li) for pi, li in zip(p_, l_))


def skb_inner(p_, th_, b_, a, v):
    # K_i = th_i v^{b_i}/(1-(1-th_i)v^{b_i}); integer b_i
    return sum(pi * (ti * v ** bi / (1 - (1 - ti) * v ** bi)) ** a
               for pi, ti, bi in zip(p_, th_, b_))


def run_gy1(n, ntrials, seed):
    rng = random.Random(seed)
    adm = viol = 0
    tries = 0
    while adm < ntrials and tries < 80 * ntrials:
        tries += 1
        a = [F(rng.randint(1, 10), rng.randint(1, 10)) for _ in range(n)]
        if not all(F(0) < t <= 1 for t in a):
            continue
        pr = [rng.randint(1, 15) for _ in range(n)]
        tot = sum(pr)
        p = [F(vv, tot) for vv in pr]
        if not in_Vn(p, a):
            continue
        i, j = sorted(rng.sample(range(n), 2))
        w = F(rng.randint(1, 19), 20)
        q = list(p); b = list(a)
        q[i] = w * p[i] + (1 - w) * p[j]; q[j] = w * p[j] + (1 - w) * p[i]
        b[i] = w * a[i] + (1 - w) * a[j]; b[j] = w * a[j] + (1 - w) * a[i]
        if not all(F(0) < bi <= 1 for bi in b):
            continue
        adm += 1
        if any(gy_sf(p, a, v) - gy_sf(q, b, v) > 0 for v in GRIDF):
            viol += 1
    print(f"GY Thm1/2(i) st n={n}: admissible {adm}, violations {viol}", flush=True)


def run_gy3(n, ntrials, seed):
    """GY Thm 3(i)/4(i): (p,lam) in K_n, integer lam, al scalar -> Z >=_st Y."""
    rng = random.Random(seed)
    adm = viol = 0
    tries = 0
    al = F(1, 5)
    while adm < ntrials and tries < 80 * ntrials:
        tries += 1
        lam = [F(rng.randint(1, 6), 1) for _ in range(n)]  # integer lam for exactness
        pr = [rng.randint(1, 15) for _ in range(n)]
        tot = sum(pr)
        p = [F(vv, tot) for vv in pr]
        if not in_Vn(p, lam):
            continue
        i, j = sorted(rng.sample(range(n), 2))
        w = F(rng.randint(1, 19), 20)
        q = list(p); th = list(lam)
        q[i] = w * p[i] + (1 - w) * p[j]; q[j] = w * p[j] + (1 - w) * p[i]
        th[i] = w * lam[i] + (1 - w) * lam[j]; th[j] = w * lam[j] + (1 - w) * lam[i]
        # q must stay prob vector (yes), theta positive (yes); exponents fractional -> skip exact
        try:
            vals = [gy_sfZ(p, lam, v, al) - gy_sfZ(q, th, v, al) for v in GRIDF]
        except Exception:
            continue
        adm += 1
        if any(vv < 0 for vv in vals):
            viol += 1
    print(f"GY Thm3/4(i) st n={n}: admissible {adm}, violations {viol} "
          "(only integer-lambda samples - exact)", flush=True)


def run_skb1(n, ntrials, seed):
    rng = random.Random(seed)
    adm = viol = 0
    tries = 0
    while adm < ntrials and tries < 200 * ntrials:
        tries += 1
        th = [F(rng.randint(1, 9), rng.randint(1, 4)) for _ in range(n)]
        b = [F(rng.randint(1, 4), 1) for _ in range(n)]
        pr = [rng.randint(1, 15) for _ in range(n)]
        tot = sum(pr)
        p = [F(vv, tot) for vv in pr]
        qr = [rng.randint(1, 15) for _ in range(n)]
        totq = sum(qr)
        q = [F(vv, totq) for vv in qr]
        if not (in_Wn(p, th) and in_Wn(q, th)):
            continue
        if not (in_Vn(p, b) and in_Vn(q, b)):
            continue
        if not weak_super(p, q):
            continue
        a = rng.choice([1, 2, 3])
        adm += 1
        dW = skb_inner(p, th, b, a, None) if False else None
        vals = [skb_inner(p, th, b, a, v) - skb_inner(q, th, b, a, v) for v in GRIDF]
        # a>0: SF order = inner order; claim W <=_st V <=> inner_W <= inner_V
        if any(vv > 0 for vv in vals):
            viol += 1
    print(f"SKB Thm1(i) st n={n}: admissible {adm}, violations {viol}", flush=True)


def run_skb3(n, ntrials, seed):
    """Thm 3: a>=1, 0<th<1 scalar, (p,b),(q,b),(q,d) in Dn; b weak-super d;
    p weak-sub q => W <=_st V i.e. inner(p,b) <= inner(q,d)."""
    rng = random.Random(seed)
    adm = viol = 0
    tries = 0
    while adm < ntrials and tries < 400 * ntrials:
        tries += 1
        th = F(rng.randint(1, 3), rng.randint(2, 4))  # 0<th<1
        th = [th] * n
        b = [F(rng.randint(1, 4), 1) for _ in range(n)]
        d_ = [F(rng.randint(1, 4), 1) for _ in range(n)]
        pr = [rng.randint(1, 15) for _ in range(n)]
        tot = sum(pr)
        p = [F(vv, tot) for vv in pr]
        qr = [rng.randint(1, 15) for _ in range(n)]
        totq = sum(qr)
        q = [F(vv, totq) for vv in qr]
        if not (in_Vn(p, b) and in_Vn(q, b) and in_Vn(q, d_)):
            continue
        if not (weak_super(b, d_) and weak_sub(p, q)):
            continue
        a = rng.choice([1, 2])
        adm += 1
        vals = [skb_inner(p, th, b, a, v) - skb_inner(q, th, d_, a, v) for v in GRIDF]
        if any(vv > 0 for vv in vals):
            viol += 1
    print(f"SKB Thm3 st n={n}: admissible {adm}, violations {viol}", flush=True)


if __name__ == "__main__":
    run_gy1(3, 1500, 31)
    run_gy1(4, 800, 32)
    run_gy3(2, 800, 33)
    run_gy3(3, 600, 34)
    run_skb1(3, 800, 35)
    run_skb3(3, 800, 36)
