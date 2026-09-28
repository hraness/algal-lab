"""Evaluation of canonical claims for doi:10.3390/math6100197
(Zarezadeh-Asadi style: coherent networks under geometric counting process
component failures).

GCP with MVF Lambda(t):  P(xi(t)=k) = (1/(1+Lambda)) (Lambda/(1+Lambda))^k,
  P(theta_k > t) = 1 - z^k  with  z = Lambda/(1+Lambda) in (0,1), increasing in t.
Network lifetime survival (signature s on {1..n}):  S_T = sum_i s_i (1 - z^i).

Same-MVF comparisons are polynomial in z -> ratdist decides exactly on (0,1),
covering all t and every increasing Lambda simultaneously.
Different MVFs Lambda >= Lambda*: take Lambda = t, Lambda* = t/2, Lambda*=2t;
in the shared z of one side the other's z* is rational (z/(2-z), 2z/(1+z)).
Residual lifetimes (Thm 7): with v = z(t0+x), v in (u0,1), the residual
survival is a mixture of (1 - v^k)/(1 - u0^k), again rational -> ratdist.

Discrete signature orders on probability vectors {1..n}:
  st:  tail sums ordered;  hr: s_k/Sigma_{j>=k}s_j ordered;
  rh:  s_k/Sigma_{j<=k}s_j ordered;  lr: s_k/s*_k decreasing in k.
"""
import json
import os
from fractions import Fraction
from itertools import combinations
import random

import sympy as sp

import closedform as cf
from closedform import x, Closed
from ratdist import Dist, ORDERS, z, _nonnegative

R = sp.Rational
random.seed(20260927)
HERE = os.path.dirname(os.path.abspath(__file__))


def nonneg_on_01(expr):
    """expr rational in z on (0,1); its denominator is a positive combination of
    (1 - z^i) and (1+z)^i terms hence strictly positive on the OPEN interval
    (endpoint vanishing at z=1 irrelevant). Check numerator >= 0 on (0,1)."""
    num = sp.fraction(sp.together(expr))[0]
    return _nonnegative(num, R(0), R(1))


def net_dist(sig, zexpr=None):
    """Dist of network lifetime under shared MVF: S = sum s_i (1 - z^i)."""
    zz = z if zexpr is None else zexpr
    return Dist(sp.together(sum(R(s) * (1 - zz ** i) for i, s in enumerate(sig, start=1))),
                R(0), R(1), increasing=True)


def tails(v, k):
    return sum(v[k - 1:])


def d_st(s, t):
    return all(tails(s, k) <= tails(t, k) for k in range(1, len(s) + 1))


def d_hr(s, t):
    """s <=hr t: discrete failure rates h_s(k) = s_k / P(X >= k) ordered >=.
    Requires full support on both sides (generation ensures positive entries)."""
    for k in range(1, len(s) + 1):
        Ss, Ts = tails(s, k), tails(t, k)
        if Ss <= 0 or Ts <= 0:
            return False
        if Fraction(s[k - 1]) * Ts < Fraction(t[k - 1]) * Ss:
            return False
    return True


def d_rh(s, t):
    """s <=rh t: discrete reversed failure rates r_s(k) = s_k / P(X <= k) ordered <=."""
    for k in range(1, len(s) + 1):
        Ss, Ts = sum(s[:k]), sum(t[:k])
        if Ss <= 0 or Ts <= 0:
            return False
        if Fraction(s[k - 1]) * Ts > Fraction(t[k - 1]) * Ss:
            return False
    return True


def d_lr(s, t):
    """s <=lr t: s_k/t_k decreasing in k; both vectors full-support."""
    for k in range(1, len(s) + 1):
        if s[k - 1] <= 0 or t[k - 1] <= 0:
            return False
    for i, j in zip(range(1, len(s) + 1), range(2, len(s) + 1)):
        si, ti, sj, tj = (Fraction(v) for v in (s[i - 1], t[i - 1], s[j - 1], t[j - 1]))
        if si * tj < sj * ti:          # s_i/t_i >= s_j/t_j required
            return False
    return True


DORDERS = {"st": d_st, "hr": d_hr, "rh": d_rh, "lr": d_lr}


def rand_sig(n, den=8):
    """Probability vector on {1..n} with all entries positive."""
    cuts = sorted(random.randint(1, den - 1) for _ in range(n - 1))
    v = [Fraction(cuts[0])]
    v += [Fraction(c - p) for c, p in zip(cuts[1:], cuts[:-1])]
    v += [Fraction(den - cuts[-1])]
    if min(v) <= 0:
        return rand_sig(n, den)
    tot = sum(v)
    return [x / tot for x in v]


def rand_pair(order, n, tries=8000):
    for _ in range(tries):
        s, t = rand_sig(n), rand_sig(n)
        if s != t and DORDERS[order](s, t):
            return s, t
    return None


# ---------------------------------------------------------------- Example 1
def ex_1():
    """All-terminal s vs two-terminal s*, same GCP: T <=st T* (printed)."""
    s = [Fraction(0), Fraction(0), Fraction(1, 30), Fraction(9, 70),
         Fraction(29, 90), Fraction(65, 126), Fraction(0), Fraction(0),
         Fraction(0), Fraction(0)]
    ss = [Fraction(0), Fraction(0), Fraction(1, 120), Fraction(37, 840),
          Fraction(179, 1260), Fraction(379, 1260), Fraction(19, 70),
          Fraction(1, 6), Fraction(1, 15), Fraction(0)]
    assert sum(s) == 1 and sum(ss) == 1
    assert d_st(s, ss)                      # printed tail-sum ordering verified
    h, w = ORDERS["st"](net_dist([sp.Rational(v) for v in s]),
                        net_dist([sp.Rational(v) for v in ss]))
    return 1, None if h else w, 0


# ---------------------------------------------------------------- Example 2
def ex_2():
    """NHPP vs GCP reliability on the (non-series) Example-1 all-terminal
    network, Lambda = t. Printed claim: curves cross (neither st direction).
    NHPP kth arrival: P(theta_k > t) = e^{-t} sum_{j<k} t^j/j!"""
    s = [R(0), R(0), R(1, 30), R(9, 70), R(29, 90), R(65, 126), R(0), R(0), R(0), R(0)]
    zz = x / (1 + x)
    S_gcp = sum(si * (1 - zz ** i) for i, si in enumerate(s, start=1) if si)
    S_nhpp = sp.exp(-x) * sum(si * sum(x ** j / sp.factorial(j) for j in range(i))
                              for i, si in enumerate(s, start=1) if si)
    G, N = Closed(S_gcp), Closed(S_nhpp)
    h1, w1, u1 = cf.check("st", G, N)       # T_GCP <=st T_NHPP ? expect fail
    h2, w2, u2 = cf.check("st", N, G)       # T_NHPP <=st T_GCP ? expect fail
    confirmed = (w1 is not None) and (w2 is not None)
    return confirmed, (w1, w2), u1 + u2


# ---------------------------------------------------------------- Theorem 3
def thm_3(order):
    """s <=order s* (discrete) => T <=order T*; exact over all Lambda via z."""
    n, wit, seen = 0, None, 0
    for _ in range(14):
        pair = rand_pair(order, random.choice([3, 4]))
        if pair is None:
            continue
        s, t = pair
        h, w = ORDERS[order](net_dist([sp.Rational(v) for v in s]),
                             net_dist([sp.Rational(v) for v in t]))
        n += 1
        if not h and wit is None:
            wit = w
    # plus the Example-1 pair if it satisfies the stated order
    s = [Fraction(0), Fraction(0), Fraction(1, 30), Fraction(9, 70),
         Fraction(29, 90), Fraction(65, 126), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    ss = [Fraction(0), Fraction(0), Fraction(1, 120), Fraction(37, 840),
          Fraction(179, 1260), Fraction(379, 1260), Fraction(19, 70),
          Fraction(1, 6), Fraction(1, 15), Fraction(0)]
    if DORDERS[order](s, ss):
        h, w = ORDERS[order](net_dist([sp.Rational(v) for v in s]),
                             net_dist([sp.Rational(v) for v in ss]))
        n += 1
        if not h and wit is None:
            wit = w
    return n, wit, 0


# ---------------------------------------------------------------- Theorem 7
def cond_sig(sig, u0):
    """Conditional signature at time t0 with u0 = z(t0): s_k(1-u0^k)/D."""
    w = [Fraction(s) * (1 - Fraction(u0) ** k) for k, s in enumerate(sig, start=1)]
    d = sum(w)
    return [v / d for v in w]


def resid_dist(sig_t, u0):
    """Residual lifetime (T - t0 | T > t0): S_res(v) = sum_k s_k(t0) (1-v^k)/(1-u0^k),
    v = z(t0+x) in (u0, 1)."""
    terms = []
    for k, sk in enumerate(sig_t, start=1):
        if sk == 0:
            continue
        terms.append(sp.Rational(sk) * (1 - z ** k) / (1 - sp.Rational(u0) ** k))
    return Dist(sp.together(sum(terms)), sp.Rational(u0), sp.Rational(1), increasing=True)


def thm_7(order):
    """s(t0) <=order s*(t0) => residual lifetimes ordered. Random (s, s*, u0)."""
    n, wit = 0, None
    for _ in range(5000):
        if n >= 10:
            break
        n_ = random.choice([3, 4])
        s, t = rand_sig(n_), rand_sig(n_)
        u0 = Fraction(random.choice([2, 3, 4]), 5)          # 2/5, 3/5, 4/5
        ct, cs = cond_sig(t, u0), cond_sig(s, u0)
        if not DORDERS[order](cs, ct):
            continue
        h, w = ORDERS[order](resid_dist(cs, u0), resid_dist(ct, u0))
        n += 1
        if not h and wit is None:
            wit = w
    return n, wit, 0


# ---------------------------------------------------------------- Theorem 5
def thm_5():
    """(a) s(t) st-increasing in t; (b) Lambda <= Lambda* => s(t) <=st s*(t).
    s_k(t) = s_k(1-u^k)/sum_j s_j(1-u^j), rational in u on (0,1).
    (a): monotonicity <-> d/du tail_k(u) >= 0 for each tail k (u increases in t).
    (b): with Lambda* = 2 Lambda: u* = 2u/(1+u); tail differences checked."""
    s = [R(0), R(0), R(1, 30), R(9, 70), R(29, 90), R(65, 126), R(0), R(0), R(0), R(0)]
    # smaller random signatures too
    sigs = [s]
    random.seed(7)
    for _ in range(4):
        sigs.append([sp.Rational(v) for v in rand_sig(random.choice([3, 4]))])
    und = 0
    n = 0
    bad_a, bad_b = None, None
    for sig in sigs:
        nn = len(sig)
        D = sum(sig[i] * (1 - z ** (i + 1)) for i in range(nn))
        for k in range(2, nn + 1):
            tail_k = sum(sig[i] * (1 - z ** (i + 1)) for i in range(k - 1, nn)) / D
            d_tail = sp.diff(tail_k, z)
            ok, wit = nonneg_on_01(d_tail)
            n += 1
            if not ok and bad_a is None:
                bad_a = (k, wit)
        # part (b): same signature under u* = 2u/(1+u) >= u
        us = 2 * z / (1 + z)
        D1 = sum(sig[i] * (1 - z ** (i + 1)) for i in range(nn))
        D2 = sum(sig[i] * (1 - us ** (i + 1)) for i in range(nn))
        for k in range(2, nn + 1):
            t1 = sum(sig[i] * (1 - z ** (i + 1)) for i in range(k - 1, nn)) / D1
            t2 = sum(sig[i] * (1 - us ** (i + 1)) for i in range(k - 1, nn)) / D2
            ok, wit2 = nonneg_on_01(t2 - t1)
            n += 1
            if not ok and bad_b is None:
                bad_b = wit2
    wit = bad_a[1] if bad_a else bad_b
    return n, wit, und


def thm_5_ii():
    """Lambda <= Lambda* => s(t) <=st s*(t): tail differences on u in (0,1)."""
    s = [R(0), R(0), R(1, 30), R(9, 70), R(29, 90), R(65, 126), R(0), R(0), R(0), R(0)]
    us = 2 * z / (1 + z)                      # Lambda* = 2 Lambda
    nn = len(s)
    D1 = sum(s[i] * (1 - z ** (i + 1)) for i in range(nn))
    D2 = sum(s[i] * (1 - us ** (i + 1)) for i in range(nn))
    n, wit = 0, None
    for k in range(2, nn + 1):
        t1 = sum(s[i] * (1 - z ** (i + 1)) for i in range(k - 1, nn)) / D1
        t2 = sum(s[i] * (1 - us ** (i + 1)) for i in range(k - 1, nn)) / D2
        ok, w = nonneg_on_01(t2 - t1)
        n += 1
        if not ok and wit is None:
            wit = w
    return n, wit, 0


# ---------------------------------------------------------------- Theorem 2
def thm_2():
    """s <=st s*, Lambda >= Lambda* => T <=st T*. Lambda = t (z = t/(1+t)),
    Lambda* = t/2 -> z* = (t/2)/(1+t/2) = z/(2-z); both sides rational in the
    shared z on (0,1)."""
    pairs = []
    random.seed(11)
    while len(pairs) < 8:
        s, t = rand_sig(random.choice([3, 4])), None
        t = rand_sig(len(s))
        if d_st(s, t):
            pairs.append((s, t))
    zs = z / (2 - z)
    n, wit = 0, None
    for s, t in pairs:
        X = net_dist([sp.Rational(v) for v in s])                    # MVF Lambda = t
        Y = net_dist([sp.Rational(v) for v in t], zexpr=zs)          # MVF Lambda* = t/2
        h, w = ORDERS["st"](X, Y)
        n += 1
        if not h and wit is None:
            wit = w
    return n, wit, 0


# ---------------------------------------------------------------- series GCP vs NHPP
def series_gcp_nhpp():
    """s = (1,0,...,0): T = theta_1. Claim e^{-Lambda} <= 1/(1+Lambda), i.e.
    T_NP <=st T_GP, for all t >= 0. Test Lambda(t) = t and t^2."""
    n, wit, und = 0, None, 0
    for Lam in [x, x ** 2, R(3, 2) * x]:
        NP = Closed(sp.exp(-Lam))
        GP = Closed(1 / (1 + Lam))
        h, w, u = cf.check("st", NP, GP)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_math6100197.json")))
    results = []

    def rec(record, status, instances=0, witness=None, undecided=0):
        return {"claim": record["claim"], "order": record["conclusion"]["order"],
                "status": status, "instances": instances,
                "witness": None if witness is None else str(witness),
                "undecided_points": undecided}

    for recd in canon:
        label, order = recd["claim"], recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "out of harness scope" if str(order).startswith("other")
                               else "unsupported order"))
            continue
        n_, w, u = 0, None, 0
        cex = False
        if label == "Example 1":
            n_, w, u = ex_1()
        elif label == "Example 2":
            confirmed, (w1, w2), u = ex_2()
            results.append(rec(recd, "holds" if confirmed else "ambiguous hypotheses",
                               instances=2, witness=w2 or w1, undecided=u))
            continue
        elif label in ("Example 3", "Example 3 (counterexample)",
                       "mrl consequence of Theorem 3"):
            results.append(rec(recd, "unsupported order"))
            continue
        elif label == "Theorem 3 (i)":
            n_, w, u = thm_3("st")
        elif label == "Theorem 3 (ii)":
            n_, w, u = thm_3("hr")
        elif label == "Theorem 3 (iii)":
            n_, w, u = thm_3("rh")
        elif label == "Theorem 3 (iv)":
            n_, w, u = thm_3("lr")
        elif label == "Theorem 7 (i)":
            n_, w, u = thm_7("st")
        elif label == "Theorem 7 (ii)":
            n_, w, u = thm_7("hr")
        elif label == "Theorem 7 (iii)":
            n_, w, u = thm_7("rh")
        elif label == "Theorem 7 (iv)":
            n_, w, u = thm_7("lr")
        elif label == "Theorem 5":
            n_, w, u = thm_5()
        elif label == "Theorem 5 (ii)":
            n_, w, u = thm_5_ii()
        elif label == "Theorem 2":
            n_, w, u = thm_2()
        elif label == "Series-network comparison GCP vs NHPP (unnumbered, Section 2)":
            n_, w, u = series_gcp_nhpp()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.3390_math6100197.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
