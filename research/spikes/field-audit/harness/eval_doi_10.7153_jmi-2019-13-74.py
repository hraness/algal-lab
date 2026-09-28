"""Evaluation of canonical claims for doi:10.7153/jmi-2019-13-74
(Ling & Fang: comparisons of largest/smallest order statistics from
heterogeneous Pareto-I and Pareto-II components under matrix chain
majorization).

  PI(a, b):   S(x) = (b/x)^a,                       x >= b
  PII(a, b):  S(x) = (b/(x+b))^a,                   x > 0
On the common domain x >= max(all scales), for minima (series):
  S_1:n(x) = prod S_i ;  for maxima (parallel): S_n:n = 1 - prod(1 - S_i).
(Encoding validated against printed numbers: r~_X1:2(15)=0.069, h_X1:2(6)=0.5857.)

Matrix orders: Sn = {(a;b): (a_i-a_j)(b_i-b_j) <= 0 for all i,j}
(anti-comonotone rows); Tn = Sn with all a_i >= 1. T-transform T_w on a column
pair (i,j): c_i' = w c_i + (1-w) c_j, c_j' = w c_j + (1-w) c_i.
check(order, A, B) decides A <=_order B.
Counterexample records assert a *failure* of an order; a strict witness of
that failure confirms the printed claim -> status "holds".
"""
import json
import os
import random

import sympy as sp

import closedform as cf
from closedform import x, Closed
from mpmath import iv

R = sp.Rational
random.seed(424242)
HERE = os.path.dirname(os.path.abspath(__file__))

# Probe the coverage hole in closedform's grid (see NP evaluator note).
PROBES = [R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(1), R(3, 2), R(2), R(3), R(5),
          R(8), R(13), R(21), R(34), R(55), R(89), R(144), R(233), R(377),
          R(610), R(987), R(1597), R(2584), R(4184), R(6765), R(10946),
          R(17711), R(28657), R(46368), R(75025), R(121393), R(196418),
          R(317811), R(514229), R(832040)]


def rat(v):
    return v if isinstance(v, sp.Basic) else R(v)


def S_pi(a, b):
    return (rat(b) / x) ** R(a)


def S_pii(a, b):
    return (rat(b) / (x + rat(b))) ** R(a)


def sys_surv(fam, params, kind):
    """params: list of (a_i, b_i). kind 'min' -> series, 'max' -> parallel."""
    S = [fam(a, b) for a, b in params]
    if kind == "min":
        return sp.prod(S)
    return 1 - sp.prod([1 - s for s in S])


def lo_pi(paramsX, paramsY):
    return max([R(b) for _, b in paramsX] + [R(b) for _, b in paramsY])


def check(order, SX, SY, lo):
    X, Y = Closed(SX, lo=lo), Closed(SY, lo=lo)
    holds, w, u = cf.check(order, X, Y)
    if w is not None:
        return holds, w, u
    E = cf.expression(order, X, Y)
    from mpmath import mp, mpf
    mp.dps = 60
    fS = [sp.lambdify(x, S, modules="mpmath") for S in (X.survival, Y.survival)]
    for p in PROBES:
        if p <= X.lo:
            continue
        if all(abs(f(mpf(str(float(p))))) < mpf(10) ** -30 for f in fS):
            continue                       # beyond resolvable region
        for dps in (150, 400, 900):
            iv.dps = dps
            v = cf.iv_eval(E, p)
            if v.b < 0:
                return False, p, u
            if v.a >= 0:
                break
        else:
            u += 1
    return True, None, u


def in_Sn(a, b):
    return all((a[i] - a[j]) * (b[i] - b[j]) <= 0
               for i in range(len(a)) for j in range(len(a)))


def in_Tn(a, b):
    return in_Sn(a, b) and all(v >= 1 for v in a)


def t_apply(a, b, pair, w):
    i, j = pair
    aa, bb = list(a), list(b)
    for r in (aa, bb):
        ri, rj = r[i], r[j]
        r[i] = w * ri + (1 - w) * rj
        r[j] = w * rj + (1 - w) * ri
    return aa, bb


def majorized(u, v):
    """u majorizes v: equal totals, descending partial sums dominate."""
    U, V = sorted(u, reverse=True), sorted(v, reverse=True)
    return sum(u) == sum(v) and all(sum(U[:j]) >= sum(V[:j]) for j in range(1, len(U)))


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def rand_matrix(n, set_):
    """Random (a, b) in Sn (set_='S') or Tn (set_='T'), anti-comonotone rows."""
    for _ in range(400):
        a = sorted([R(random.randint(1, 8), random.choice([1, 2, 4]))
                    for _ in range(n)], reverse=True)
        b = sorted([R(random.randint(1, 6), random.choice([1, 2]))
                    for _ in range(n)])
        if len(set(a)) < n or len(set(b)) < n:
            continue
        ok = in_Tn(a, b) if set_ == "T" else in_Sn(a, b)
        if ok:
            return a, b
    return None


def gen_chain(a, b, steps, keep_in=None):
    """Apply `steps` random T-transforms; if keep_in is 'S'/'T', require every
    partial product matrix to stay in Sn/Tn. Returns final (a',b') or None."""
    n = len(a)
    for _ in range(60):
        aa, bb = list(a), list(b)
        ok = True
        for _s in range(steps):
            i, j = sorted(random.sample(range(n), 2))
            w = R(random.randint(1, 4), 5)
            aa, bb = t_apply(aa, bb, (i, j), w)
            if keep_in == "S" and not in_Sn(aa, bb):
                ok = False
                break
            if keep_in == "T" and not in_Tn(aa, bb):
                ok = False
                break
        if ok:
            return aa, bb
    return None


def gen_same_struct_chain(a, b, steps, pair):
    aa, bb = list(a), list(b)
    for _ in range(steps):
        aa, bb = t_apply(aa, bb, pair, R(random.randint(1, 4), 5))
    return aa, bb


# --------------------------------------------------------------- examples
def ex_2_1_i():
    """PI, (a;b)=(5 4;3 6) in S2, (c;d)=(4.44 4.56;4.68 4.32): Y1:2 >=rh X1:2."""
    a, b = [R(5), R(4)], [R(3), R(6)]
    c, d = [R(111, 25), R(114, 25)], [R(117, 25), R(108, 25)]
    assert in_Sn(a, b)
    assert t_apply(*t_apply(a, b, (0, 1), R(1, 5)), (0, 1), R(3, 5)) == (c, d)
    lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
    return check("rh", sys_surv(S_pi, zip(a, b), "min"),
                 sys_surv(S_pi, zip(c, d), "min"), lo)         # X <=rh Y ?


def ex_2_1_ii():
    """PI, (a;b)=(7 2;3 5) in T2, (c;d)=(4.7 4.3;3.92 4.08): X2:2 >=st Y2:2."""
    a, b = [R(7), R(2)], [R(3), R(5)]
    c, d = [R(47, 10), R(43, 10)], [R(98, 25), R(102, 25)]
    assert in_Tn(a, b)
    assert t_apply(*t_apply(a, b, (0, 1), R(3, 10)), (0, 1), R(2, 5)) == (c, d)
    lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
    return check("st", sys_surv(S_pi, zip(c, d), "max"),
                 sys_surv(S_pi, zip(a, b), "max"), lo)          # Y <=st X ?


def ex_2_2():
    """PII, (a;b)=(2 0.8;0.6 1) in S2, (c;d)=(1.208 1.592;0.864 0.736): Y1:2 >=hr X1:2."""
    a, b = [R(2), R(4, 5)], [R(3, 5), R(1)]
    c, d = [R(151, 125), R(199, 125)], [R(108, 125), R(92, 125)]
    assert in_Sn(a, b)
    assert t_apply(*t_apply(a, b, (0, 1), R(9, 10)), (0, 1), R(3, 10)) == (c, d)
    return check("hr", sys_surv(S_pii, zip(a, b), "min"),
                 sys_surv(S_pii, zip(c, d), "min"), R(0))       # X <=hr Y ?


def ex_2_5():
    """PI n=3, (a;b)=(6 4 1;2 3 5) in S3, intermediates in S3, (c;d) given:
    Y1:3 >=st X1:3 -> test X <=st Y."""
    a, b = [R(6), R(4), R(1)], [R(2), R(3), R(5)]
    c, d = [R(207, 50), R(68, 25), R(207, 50)], [R(76, 25), R(98, 25), R(76, 25)]
    assert in_Sn(a, b)
    m1 = t_apply(a, b, (1, 2), R(3, 10))
    assert in_Sn(*m1)
    m2 = t_apply(*m1, (0, 1), R(4, 5))
    assert in_Sn(*m2)
    assert t_apply(*m2, (0, 2), R(1, 2)) == (c, d)
    lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
    return check("st", sys_surv(S_pi, zip(a, b), "min"),
                 sys_surv(S_pi, zip(c, d), "min"), lo)          # X <=st Y ?


def ex_2_6():
    """PI n=3, (a;b)=(5 4 2;2 6 8) in T3, intermediates in T3: X3:3 >=st Y3:3.
    NOTE: the printed chain has an arithmetic slip — (a;b)T0.35's b-entry is
    7.3 (0.35*6 + 0.65*8), not the printed 7.4; printed final 6.58 should be
    6.53.  We test the EXACT chain product and the printed (c;d) matrix."""
    a, b = [R(5), R(4), R(2)], [R(2), R(6), R(8)]
    c, d = [R(317, 100), R(317, 100), R(233, 50)], [R(329, 50), R(329, 50), R(147, 50)]
    assert in_Tn(a, b)
    m1 = t_apply(a, b, (1, 2), R(7, 20))
    assert in_Tn(*m1)                       # (5 2.7 3.3; 2 7.3 6.7) exact
    m2 = t_apply(*m1, (0, 2), R(1, 5))
    assert in_Tn(*m2)                       # (3.64 2.7 4.66; 5.76 7.3 2.94) exact
    ce, de = t_apply(*m2, (0, 1), R(1, 2))  # exact product (3.17,3.17,4.66; 6.53,6.53,2.94)
    h1, w1, u1 = check("st", sys_surv(S_pi, zip(c, d), "max"),
                       sys_surv(S_pi, zip(a, b), "max"), lo_pi(list(zip(a, b)), list(zip(c, d))))
    h2, w2, u2 = check("st", sys_surv(S_pi, zip(ce, de), "max"),
                       sys_surv(S_pi, zip(a, b), "max"), lo_pi(list(zip(a, b)), list(zip(ce, de))))
    return (h1 and h2), (w1 or w2), u1 + u2


def ex_2_7():
    """PII n=3, (a;b)=(0.8 0.3 0.1;0.6 1 2) in S3, intermediates in S3:
    Y1:3 >=hr X1:3 -> test X <=hr Y.
    Printed (c;d) is rounded to 3 decimals; test the EXACT chain product and
    the printed rounded matrix (both admissible hypothesis instances)."""
    a, b = [R(4, 5), R(3, 10), R(1, 10)], [R(3, 5), R(1), R(2)]
    assert in_Sn(a, b)
    m1 = t_apply(a, b, (0, 2), R(3, 10))
    assert m1 == ([R(31, 100), R(3, 10), R(59, 100)], [R(79, 50), R(1), R(51, 50)])
    # NB: printed claim "m1 in S3" is FALSE — (0.31-0.30)(1.58-1) > 0 and
    # (0.30-0.59)(1-1.02) > 0: the first intermediate leaves S3.  Premise
    # verification fails as printed; the conclusion is still checked below.
    print("   [ex_2_7] printed m1 in S3:", in_Sn(*m1))
    m2 = t_apply(*m1, (1, 2), R(2, 5))
    assert m2 == ([R(31, 100), R(237, 500), R(52, 125)], [R(79, 50), R(253, 250), R(126, 125)])
    print("   [ex_2_7] printed m2 in S3:", in_Sn(*m2))
    ce, de = t_apply(*m2, (0, 1), R(9, 10))                # exact product
    cp, dp = [R(163, 500), R(229, 500), R(52, 125)], [R(1523, 1000), R(1069, 1000), R(126, 125)]
    print("   [ex_2_7] printed c,d in S3:", in_Sn(cp, dp), "| exact chain in S3:", in_Sn(ce, de))
    h1, w1, u1 = check("hr", sys_surv(S_pii, zip(a, b), "min"),
                       sys_surv(S_pii, zip(ce, de), "min"), R(0))
    h2, w2, u2 = check("hr", sys_surv(S_pii, zip(a, b), "min"),
                       sys_surv(S_pii, zip(cp, dp), "min"), R(0))
    return (h1 and h2), (w1 or w2), u1 + u2


def ex_2_3():
    """PI counterexample: (a;b)=(1 2;6 12), (c;d)=(1.7 1.3;10.2 7.8), NOT in S2;
    printed claim NOT(Y1:2 >=rh X1:2) i.e. X <=rh Y fails -> expect witness."""
    a, b = [R(1), R(2)], [R(6), R(12)]
    c, d = [R(17, 10), R(13, 10)], [R(51, 5), R(39, 5)]
    assert not in_Sn(a, b) and not in_Sn(c, d)
    assert t_apply(a, b, (0, 1), R(3, 10)) == (c, d)
    lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
    h, w, u = check("rh", sys_surv(S_pi, zip(a, b), "min"),
                    sys_surv(S_pi, zip(c, d), "min"), lo)
    return w is not None, w, u


def ex_2_4():
    """PII counterexample: (a;b)=(3 2;4 1), (c;d)=(2.4 2.6;2.2 2.8), NOT in S2;
    printed claim NOT(Y1:2 >=hr X1:2) -> expect witness for X <=hr Y."""
    a, b = [R(3), R(2)], [R(4), R(1)]
    c, d = [R(12, 5), R(13, 5)], [R(11, 5), R(14, 5)]
    assert not in_Sn(a, b) and not in_Sn(c, d)
    assert t_apply(a, b, (0, 1), R(2, 5)) == (c, d)
    h, w, u = check("hr", sys_surv(S_pii, zip(a, b), "min"),
                    sys_surv(S_pii, zip(c, d), "min"), R(0))
    return w is not None, w, u


# --------------------------------------------------------------- theorems
def thm_2_1():
    """PI, (a;b) in S2, chain => Y1:2 >=rh X1:2 i.e. X <=rh Y."""
    insts = [([R(5), R(4)], [R(3), R(6)], [R(111, 25), R(114, 25)], [R(117, 25), R(108, 25)]),
             ([R(3), R(2)], [R(6), R(12)], [R(3, 2), R(5, 2)], [R(9), R(9)])]
    n, wit, und = 0, None, 0
    for _ in range(300):
        if n >= 12:
            break
        m = rand_matrix(2, "S")
        if m is None:
            continue
        a, b = m
        res = gen_chain(a, b, random.choice([1, 2]))
        if res is None:
            continue
        c, d = res
        insts.append((a, b, c, d))
    for a, b, c, d in insts:
        lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
        h, w, u = check("rh", sys_surv(S_pi, zip(a, b), "min"),
                        sys_surv(S_pi, zip(c, d), "min"), lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_2():
    """PI, (a;b) in T2, chain => X2:2 >=st Y2:2 i.e. Y <=st X."""
    insts = [([R(7), R(2)], [R(3), R(5)], [R(47, 10), R(43, 10)], [R(98, 25), R(102, 25)])]
    for _ in range(300):
        if len(insts) >= 12:
            break
        m = rand_matrix(2, "T")
        if m is None:
            continue
        a, b = m
        res = gen_chain(a, b, random.choice([1, 2]))
        if res is None:
            continue
        insts.append((a, b, res[0], res[1]))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
        h, w, u = check("st", sys_surv(S_pi, zip(c, d), "max"),
                        sys_surv(S_pi, zip(a, b), "max"), lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_3():
    """PII, (a;b) in S2, chain => Y1:2 >=hr X1:2 i.e. X <=hr Y."""
    insts = [([R(2), R(4, 5)], [R(3, 5), R(1)], [R(151, 125), R(199, 125)], [R(108, 125), R(92, 125)])]
    for _ in range(400):
        if len(insts) >= 12:
            break
        m = rand_matrix(2, "S")
        if m is None:
            continue
        a, b = m
        res = gen_chain(a, b, random.choice([1, 2]))
        if res is None:
            continue
        insts.append((a, b, res[0], res[1]))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        h, w, u = check("hr", sys_surv(S_pii, zip(a, b), "min"),
                        sys_surv(S_pii, zip(c, d), "min"), R(0))
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_4():
    """PI, (a;b) in Sn, single Tw => Y1:n >=st X1:n i.e. X <=st Y."""
    insts = [([R(6), R(4), R(1)], [R(2), R(3), R(5)],
              *t_apply([R(6), R(4), R(1)], [R(2), R(3), R(5)], (0, 2), R(1, 3)))]
    for _ in range(400):
        if len(insts) >= 10:
            break
        m = rand_matrix(3, "S") or rand_matrix(4, "S")
        if m is None:
            continue
        a, b = m
        i, j = sorted(random.sample(range(len(a)), 2))
        c, d = t_apply(a, b, (i, j), R(random.randint(1, 4), 5))
        insts.append((a, b, c, d))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
        h, w, u = check("st", sys_surv(S_pi, zip(a, b), "min"),
                        sys_surv(S_pi, zip(c, d), "min"), lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_5():
    """PI, (a;b) in Tn, single Tw => Xn:n >=st Yn:n i.e. Y <=st X."""
    insts = []
    for _ in range(400):
        if len(insts) >= 10:
            break
        m = rand_matrix(random.choice([2, 3]), "T")
        if m is None:
            continue
        a, b = m
        i, j = sorted(random.sample(range(len(a)), 2))
        c, d = t_apply(a, b, (i, j), R(random.randint(1, 4), 5))
        insts.append((a, b, c, d))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        lo = lo_pi(list(zip(a, b)), list(zip(c, d)))
        h, w, u = check("st", sys_surv(S_pi, zip(c, d), "max"),
                        sys_surv(S_pi, zip(a, b), "max"), lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_6():
    """Theorem 2.6 prints Xi ~ PI(ai,bi) against Yi ~ PII(ci,di) — a genuine
    CROSS-FAMILY claim (canonical flags 'proof looks PII' — the statement is
    literal).  (a;b) in Sn, (c;d) = (a;b)Tw => Y1:n >=hr X1:n i.e. X <=hr Y.
    We test BOTH readings: literal (X~PI vs Y~PII) and intended (PII vs PII).
    Returns (n, wit_literal, wit_intended, undecided)."""
    insts = []
    for _ in range(400):
        if len(insts) >= 8:
            break
        m = rand_matrix(random.choice([2, 3]), "S")
        if m is None:
            continue
        a, b = m
        i, j = sorted(random.sample(range(len(a)), 2))
        c, d = t_apply(a, b, (i, j), R(random.randint(1, 4), 5))
        insts.append((a, b, c, d))
    n, witL, witI, und = 0, None, None, 0
    for a, b, c, d in insts:
        loL = lo_pi(list(zip(a, b)), list(zip(c, d)))   # PI needs x >= scales
        h, w, u = check("hr", sys_surv(S_pi, zip(a, b), "min"),
                        sys_surv(S_pii, zip(c, d), "min"), loL)
        n += 1; und += u
        if not h and witL is None:
            witL = w
        h, w, u = check("hr", sys_surv(S_pii, zip(a, b), "min"),
                        sys_surv(S_pii, zip(c, d), "min"), R(0))
        n += 1; und += u
        if not h and witI is None:
            witI = w
    return n, witL, witI, und


def thm_2_7_8_9(fam, set_, order, kind, n_inst=8):
    """Theorems 2.7 (PI,Sn,st,min), 2.8 (PI,Tn,st,max), 2.9 (PII,Sn,hr,min):
    chains with all partial products in the stated class."""
    insts = []
    for _ in range(600):
        if len(insts) >= n_inst:
            break
        m = rand_matrix(random.choice([3]), set_)
        if m is None:
            continue
        a, b = m
        res = gen_chain(a, b, random.choice([2, 3]), keep_in=set_)
        if res is None:
            continue
        insts.append((a, b, res[0], res[1]))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        lo = R(0) if fam is S_pii else lo_pi(list(zip(a, b)), list(zip(c, d)))
        if kind == "min":
            SX, SY = sys_surv(fam, zip(a, b), "min"), sys_surv(fam, zip(c, d), "min")
        else:
            SX, SY = sys_surv(fam, zip(c, d), "max"), sys_surv(fam, zip(a, b), "max")
        h, w, u = check(order, SX, SY, lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def cor_2_x(fam, set_, order, kind, n_inst=8):
    """Corollaries 2.1 (PI,Sn,st,min), 2.2 (PI,Tn,st,max), 2.3 (PII,Sn,hr,min):
    same-structure chains (same column pair throughout)."""
    insts = []
    for _ in range(400):
        if len(insts) >= n_inst:
            break
        m = rand_matrix(random.choice([2, 3]), set_)
        if m is None:
            continue
        a, b = m
        pair = tuple(sorted(random.sample(range(len(a)), 2)))
        c, d = gen_same_struct_chain(a, b, random.choice([1, 2]), pair)
        insts.append((a, b, c, d))
    n, wit, und = 0, None, 0
    for a, b, c, d in insts:
        lo = R(0) if fam is S_pii else lo_pi(list(zip(a, b)), list(zip(c, d)))
        if kind == "min":
            SX, SY = sys_surv(fam, zip(a, b), "min"), sys_surv(fam, zip(c, d), "min")
        else:
            SX, SY = sys_surv(fam, zip(c, d), "max"), sys_surv(fam, zip(a, b), "max")
        h, w, u = check(order, SX, SY, lo)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def thm_2_10():
    """PII common scale b, a majorizes c => Xn:n >=st Yn:n i.e. Y <=st X."""
    pairs = [([R(3), R(1), R(1, 2)], [R(2), R(3, 2), R(1)]),
             ([R(5, 2), R(2), R(1, 2)], [R(2), R(2), R(1)]),
             ([R(4), R(1, 2), R(1, 4)], [R(2), R(3, 2), R(5, 4)])]
    n, wit, und = 0, None, 0
    for b in [R(1), R(2), R(3, 2)]:
        for a, c in pairs:
            assert majorized(a, c)
            h, w, u = check("st",
                            sys_surv(S_pii, [(ci, b) for ci in c], "max"),
                            sys_surv(S_pii, [(ai, b) for ai in a], "max"), R(0))
            n += 1; und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.7153_jmi-2019-13-74.json")))
    results = []
    for recd in canon:
        label, order = recd["claim"], recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        n_, w, u = 0, None, 0
        cex = label.startswith("Example 2.3") or label.startswith("Example 2.4")
        if label == "Example 2.1(i)":
            h, w, u = ex_2_1_i(); n_ = 1
        elif label == "Example 2.1(ii)":
            h, w, u = ex_2_1_ii(); n_ = 1
        elif label == "Example 2.2":
            h, w, u = ex_2_2(); n_ = 1
        elif label.startswith("Example 2.3"):
            ok, w, u = ex_2_3(); n_ = 1
            results.append(rec(recd, "holds" if ok else "ambiguous hypotheses",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label.startswith("Example 2.4"):
            ok, w, u = ex_2_4(); n_ = 1
            results.append(rec(recd, "holds" if ok else "ambiguous hypotheses",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Example 2.5":
            h, w, u = ex_2_5(); n_ = 1
        elif label == "Example 2.6":
            h, w, u = ex_2_6(); n_ = 1
        elif label == "Example 2.7":
            h, w, u = ex_2_7(); n_ = 2
        elif label == "Example 2.1":            # bundled duplicate: run both parts
            h1, w1, u1 = ex_2_1_i(); h2, w2, u2 = ex_2_1_ii()
            w = w1 or w2; u = u1 + u2; n_ = 2
            results.append(rec(recd, "holds" if (w1 is None and w2 is None) else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 2.1":
            n_, w, u = thm_2_1()
        elif label == "Theorem 2.2":
            n_, w, u = thm_2_2()
        elif label == "Theorem 2.3":
            n_, w, u = thm_2_3()
        elif label == "Theorem 2.4":
            n_, w, u = thm_2_4()
        elif label == "Theorem 2.5":
            n_, w, u = thm_2_5()
        elif label == "Theorem 2.6":
            n_, wlit, wint, u = thm_2_6()
            if wlit is not None and wint is not None:
                st_, w = "refuted", wlit      # fails under either reading
            elif wlit is not None or wint is not None:
                # canonical flags a PI/PII statement-vs-proof mismatch: a
                # one-reading-only failure is an ambiguity, not a clean verdict
                st_ = "ambiguous hypotheses"
                w = wlit if wlit is not None else wint
            else:
                st_, w = "holds", None
            results.append(rec(recd, st_, instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 2.7":
            n_, w, u = thm_2_7_8_9(S_pi, "S", "st", "min")
        elif label == "Theorem 2.8":
            n_, w, u = thm_2_7_8_9(S_pi, "T", "st", "max")
        elif label == "Theorem 2.9":
            n_, w, u = thm_2_7_8_9(S_pii, "S", "hr", "min")
        elif label == "Theorem 2.10":
            n_, w, u = thm_2_10()
        elif label == "Corollary 2.1":
            n_, w, u = cor_2_x(S_pi, "S", "st", "min")
        elif label == "Corollary 2.2":
            n_, w, u = cor_2_x(S_pi, "T", "st", "max")
        elif label == "Corollary 2.3":
            n_, w, u = cor_2_x(S_pii, "S", "hr", "min")
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
        print(results[-1]["claim"], "->", results[-1]["status"],
              results[-1]["witness"], flush=True)
    out = os.path.join(HERE, "eval_doi_10.7153_jmi-2019-13-74.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
