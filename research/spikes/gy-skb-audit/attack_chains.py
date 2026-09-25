"""Two-step different-structure T-chains with intermediates in V_n/K_n.

GY Cor 6 (hr, different structures, intermediates in K_n):
  claim Cker(p,a) - Cker(q2,b2) >= 0.
SKB Thm 9/12/21/24 (hf Thm 3.4 route): intermediates (p;th)M_{T1..m} in V_n.
  Thm 9:  Aker(p) - Aker(q2) >= 0 (a<0)
  Thm 12/24: Bker(p) - Bker(q2) <= 0 (a>0) [MPHR rh]
"""
import random
from fractions import Fraction
from fast_eval import gy_Cker_val, skb_Aker_val, skb_Bker_val, GRIDF
from audit_mphr import in_Vn


def apply_T_frac(r1, r2, i, j, w):
    q1 = list(r1); q2 = list(r2)
    q1[i] = w * r1[i] + (1 - w) * r1[j]
    q1[j] = w * r1[j] + (1 - w) * r1[i]
    q2[i] = w * r2[i] + (1 - w) * r2[j]
    q2[j] = w * r2[j] + (1 - w) * r2[i]
    return q1, q2


def chain_attack(kernel, a_pool, want, n, ntrials, seed, label, eq_prod=False):
    fn = {"A": skb_Aker_val, "B": skb_Bker_val, "C": gy_Cker_val}[kernel]
    rng = random.Random(seed)
    admissible = viol = 0
    tries = 0
    first = None
    while admissible < ntrials and tries < 200 * ntrials:
        tries += 1
        th = [Fraction(rng.randint(1, 9), rng.randint(1, 4)) for _ in range(n)]
        if eq_prod:
            # GY-style: a_i in (0,1], p_i = c/a_i
            if not all(Fraction(0) < t <= 1 for t in th):
                continue
            if len(set(th)) < 2:
                continue
            c = 1 / sum(1 / t for t in th)
            p = [c / t for t in th]
            a = None
        else:
            pr = [rng.randint(1, 20) for _ in range(n)]
            tot = sum(pr)
            p = [Fraction(v, tot) for v in pr]
            a = rng.choice(a_pool)
            if not in_Vn(p, th):
                continue
        # two T-transforms on distinct pairs
        i1, j1 = sorted(rng.sample(range(n), 2))
        i2, j2 = sorted(rng.sample(range(n), 2))
        if (i1, j1) == (i2, j2):
            continue
        w1 = Fraction(rng.randint(1, 19), 20)
        w2 = Fraction(rng.randint(1, 19), 20)
        p1, th1 = apply_T_frac(p, th, i1, j1, w1)
        if not in_Vn(p1, th1):
            continue  # intermediate must stay in V_n
        p2, th2 = apply_T_frac(p1, th1, i2, j2, w2)
        admissible += 1
        if eq_prod:
            vals = [fn(p, th, v) - fn(p2, th2, v) for v in GRIDF]
        else:
            vals = [fn(p, th, a, v) - fn(p2, th2, a, v) for v in GRIDF]
        bad = (any(v < 0 for v in vals) if want == "nonneg"
               else any(v > 0 for v in vals))
        if bad:
            viol += 1
            if first is None:
                first = (p, th, p1, th1, p2, th2, a,
                         (i1, j1, w1), (i2, j2, w2), vals)
    print(f"{label} n={n}: admissible {admissible}, violations {viol}", flush=True)
    if first:
        p, th, p1, th1, p2, th2, a, t1, t2, vals = first
        print(f"  p={p}\n  th={th}\n  a={a}")
        print(f"  T1{t1}: p1={p1} th1={th1}")
        print(f"  T2{t2}: p2={p2} th2={th2}")
        print("  signs:", [(str(v), (s > 0) - (s < 0)) for v, s in zip(GRIDF, vals)])
    return first


if __name__ == "__main__":
    # SKB Thm 9 (hr, diff structures, a<0)
    chain_attack("A", [-1, -2, -3], "nonneg", 3, 1500, 21, "SKB Thm9 hr diff-T a<0")
    # SKB Thm 12/24 (rh, diff structures, a>0)
    chain_attack("B", [1, 2, 3], "nonpos", 3, 1500, 22, "SKB Thm12/24 rh diff-T a>0")
    # GY Cor 6 (hr, diff structures, intermediates in K_n == V_n here)
    chain_attack("C", None, "nonneg", 3, 1500, 23, "GY Cor6 hr diff-T", eq_prod=True)
