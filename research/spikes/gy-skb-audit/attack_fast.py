"""Fast admissible-instance attack using exact Fraction grid evaluation."""
import random, sys
from fractions import Fraction
import sympy as sp
from fast_eval import (gy_Cker_val, skb_Aker_val, skb_Bker_val, GRIDF)
from audit_mphr import in_Vn, apply_T

y = sp.Symbol("y", positive=True)


def F(*a):
    return Fraction(*a)


def p_violation(vals, want):
    """want='nonneg': violation iff any val < 0; 'nonpos': iff any > 0."""
    if want == "nonneg":
        return any(v < 0 for v in vals)
    return any(v > 0 for v in vals)


# ------------------------------------------------------------------ GY Thm 5/6
def gy_attack(n, ntrials, seed):
    rng = random.Random(seed)
    admissible = viol = 0
    tries = 0
    first = None
    while admissible < ntrials and tries < 60 * ntrials:
        tries += 1
        a = [Fraction(rng.randint(1, 12), rng.randint(1, 12)) for _ in range(n)]
        if not all(F(0) < ai <= 1 for ai in a):
            continue
        if len(set(a)) < 2:
            continue
        c = 1 / sum(1 / ai for ai in a)
        p = [c / ai for ai in a]
        if sum(p) != 1:
            continue
        i, j = sorted(rng.sample(range(n), 2))
        w = Fraction(rng.randint(1, 19), 20)
        q = list(p); b = list(a)
        q[i] = w * p[i] + (1 - w) * p[j]
        q[j] = w * p[j] + (1 - w) * p[i]
        b[i] = w * a[i] + (1 - w) * a[j]
        b[j] = w * a[j] + (1 - w) * a[i]
        if not all(F(0) < bi <= 1 for bi in b):
            continue
        admissible += 1
        vals = [gy_Cker_val(p, a, v) - gy_Cker_val(q, b, v) for v in GRIDF]
        if p_violation(vals, "nonneg"):
            viol += 1
            if first is None:
                first = (p, a, q, b, i, j, w, vals)
    print(f"GY Thm6 n={n}: admissible {admissible}, violations {viol}", flush=True)
    if first:
        p, a, q, b, i, j, w, vals = first
        print(f"  p={p}\n  a={a}\n  T({i},{j},w={w})\n  q={q}\n  b={b}")
        print("  diff signs:", [(str(v), (s > 0) - (s < 0)) for v, s in zip(GRIDF, vals) if s != 0 or True])
    return first


def gy_thm5_check(ntrials, seed):
    rng = random.Random(seed)
    admissible = viol = 0
    while admissible < ntrials:
        a1 = Fraction(rng.randint(1, 12), rng.randint(1, 12))
        a2 = Fraction(rng.randint(1, 12), rng.randint(1, 12))
        if not (F(0) < a1 <= 1 and F(0) < a2 <= 1) or a1 == a2:
            continue
        c = 1 / (1 / a1 + 1 / a2)
        p = [c / a1, c / a2]
        w = Fraction(rng.randint(1, 19), 20)
        q = [w * p[0] + (1 - w) * p[1], w * p[1] + (1 - w) * p[0]]
        b = [w * a1 + (1 - w) * a2, w * a2 + (1 - w) * a1]
        admissible += 1
        vals = [gy_Cker_val(p, [a1, a2], v) - gy_Cker_val(q, b, v) for v in GRIDF]
        if p_violation(vals, "nonneg"):
            viol += 1
    print(f"GY Thm5 n=2: admissible {admissible}, violations {viol}", flush=True)


# ---------------------------------------------------------------- SKB kernels
def skb_attack(n, ntrials, seed, kernel, a_pool, want, label):
    """kernel: 'A' or 'B'; V_n admissible; single T on random pair."""
    rng = random.Random(seed)
    fn = skb_Aker_val if kernel == "A" else skb_Bker_val
    admissible = viol = 0
    tries = 0
    first = None
    while admissible < ntrials and tries < 60 * ntrials:
        tries += 1
        th = [Fraction(rng.randint(1, 9), rng.randint(1, 4)) for _ in range(n)]
        pr = [rng.randint(1, 20) for _ in range(n)]
        tot = sum(pr)
        p = [Fraction(vv, tot) for vv in pr]
        if not in_Vn(p, th):
            continue
        a = rng.choice(a_pool)
        i, j = sorted(rng.sample(range(n), 2))
        w = Fraction(rng.randint(1, 19), 20)
        q = list(p); gm = list(th)
        q[i] = w * p[i] + (1 - w) * p[j]
        q[j] = w * p[j] + (1 - w) * p[i]
        gm[i] = w * th[i] + (1 - w) * th[j]
        gm[j] = w * th[j] + (1 - w) * th[i]
        admissible += 1
        vals = [fn(p, th, a, v) - fn(q, gm, a, v) for v in GRIDF]
        if p_violation(vals, want):
            viol += 1
            if first is None:
                first = (p, th, q, gm, a, i, j, w, vals)
    print(f"SKB {label} n={n}: admissible {admissible}, violations {viol}", flush=True)
    if first:
        p, th, q, gm, a, i, j, w, vals = first
        print(f"  p={p}\n  th={th}\n  a={a}\n  T({i},{j},w={w})\n  q={q}\n  gm={gm}")
        print("  diff signs:", [(str(v), (s > 0) - (s < 0)) for v, s in zip(GRIDF, vals)])
    return first


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "gy5":
        gy_thm5_check(800, 7)
    elif which == "gy6":
        gy_attack(3, 2500, 1)
        gy_attack(4, 1500, 2)
    elif which == "skbn2":
        skb_attack(2, 700, 11, "A", [-1, -2, -3], "nonneg", "Thm7 hr n=2")
        skb_attack(2, 700, 12, "B", [1, 2, 3, 5], "nonpos", "Thm10 rh n=2")
    elif which == "skb":
        skb_attack(3, 3000, 3, "A", [-1, -2, -3, -4], "nonneg", "Thm8/23 hr(Aker>=) a<0")
        skb_attack(3, 3000, 5, "B", [1, 2, 3, 4, 5], "nonpos", "Thm11/20 rh/hr(Bker<=) a>0")
        skb_attack(4, 1500, 4, "A", [-1, -2], "nonneg", "Thm8/23 n=4")
        skb_attack(4, 1500, 6, "B", [1, 2], "nonpos", "Thm11/20 n=4")
