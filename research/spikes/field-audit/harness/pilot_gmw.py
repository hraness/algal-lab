"""Pilot tests for doi:10.52547/jsri.16.1.101 (series and parallel systems of
generalized modified Weibull components), F(x) = (1 - exp(-a x^g e^{l x}))^b.

Admissible sub-cases: independent components (the independence copula, with
generator exp(-t), meets every Archimedean-copula condition the paper uses:
its superadditivity conditions hold with equality and log exp(-t) is both convex
and concave), g = 1, integer b. Where the theorem allows l = 0 (no range stated)
the model is exponential-type and decided exactly by ratdist; where it requires
l > 0 the closed-form interval checker is used with l = 1/2.
"""
import itertools
import json
import random

import sympy as sp

import closedform as cf
from ratdist import ORDERS, Dist, z

random.seed(1729)
R = sp.Rational
D = 4  # alpha values are multiples of 1/4
ONE, ZERO = sp.Integer(1), sp.Integer(0)


def rational_system(alphas, betas, kind):
    """l = 0, g = 1: F_i = (1 - s^{D a_i})^{b_i} with s = exp(-x/D)."""
    F = [(1 - z ** int(R(a) * D)) ** int(b) for a, b in zip(alphas, betas)]
    if kind == "parallel":
        S = 1 - sp.Mul(*F)
    else:
        S = sp.Mul(*[1 - f for f in F])
    return Dist(sp.expand(S), ZERO, ONE, increasing=False)


def closed_system(alphas, betas, lams, kind):
    x = cf.x
    F = [(1 - sp.exp(-R(a) * x * sp.exp(R(l) * x))) ** int(b) for a, b, l in zip(alphas, betas, lams)]
    S = 1 - sp.Mul(*F) if kind == "parallel" else sp.Mul(*[1 - f for f in F])
    return cf.Closed(S)


def decide(order, X, Y):
    if isinstance(X, cf.Closed):
        holds, w, _ = cf.check(order, X, Y)
        return holds, w
    return ORDERS[order](X, Y)


def inc(v):
    return sorted(v)


def weak_super(a, b):
    """a weakly supermajorized by b: partial sums of increasing arrangements of a dominate b's."""
    A, B = inc(a), inc(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def weak_sub(a, b):
    """a weakly submajorized by b: sums of the j largest of a are at most b's."""
    A, B = inc(a), inc(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def majorized(a, b):
    return sum(a) == sum(b) and weak_sub(a, b)


def alpha_vec(n=3):
    return [R(random.randint(1, 16), D) for _ in range(n)]


def beta_vec(n=3):
    return [random.randint(1, 4) for _ in range(n)]


def run(spec, trials=25):
    tested, refuted = 0, None
    for _ in range(trials * 40):
        if tested >= trials:
            break
        inst = spec["gen"]()
        if inst is None:
            continue
        X, Y = spec["build"](inst)
        holds, witness = decide(spec["order"], X, Y)
        tested += 1
        if not holds and refuted is None:
            refuted = {k: [str(v) for v in val] if isinstance(val, (list, tuple)) else str(val) for k, val in inst.items()}
            refuted["witness"] = str(witness)
    return {"tested": tested, "refuted_example": refuted}


def gen_thm1():
    a, b = alpha_vec(), alpha_vec()
    beta = random.randint(1, 3)
    return {"alpha": a, "alpha_star": b, "beta": beta} if weak_super(a, b) else None


def gen_thm2():
    a = alpha_vec()
    b = [ai + R(random.randint(0, 8), D) for ai in a]
    return {"alpha": a, "alpha_star": b, "beta": random.randint(1, 3)}


def gen_thm4():
    a = alpha_vec()
    a_s = [max(R(1, D), ai - R(random.randint(0, 6), D)) for ai in a]      # alpha_i >= alpha*_i
    b = beta_vec()
    b_s = [bi + random.randint(0, 2) for bi in b]                           # beta_i <= beta*_i
    return {"alpha": a, "alpha_star": a_s, "beta": b, "beta_star": b_s}


def gen_thm7(beta_rule):
    a, b = alpha_vec(), alpha_vec()
    beta = random.randint(1, 3) if beta_rule == "ge1" else R(1, random.randint(1, 3))
    if beta_rule == "ge1" and weak_sub(a, b):
        return {"alpha": a, "alpha_star": b, "beta": beta}
    if beta_rule == "le1" and weak_super(a, b):
        return {"alpha": a, "alpha_star": b, "beta": beta}
    return None


def gen_thm8():
    b, b_s = beta_vec(), beta_vec()
    return {"alpha": R(random.randint(1, 12), D), "beta": b, "beta_star": b_s} if weak_super(b_s, b) else None


def gen_thm9():
    l, l_s = [R(random.randint(1, 8), 4) for _ in range(3)], [R(random.randint(1, 8), 4) for _ in range(3)]
    return {"lam": l, "lam_star": l_s, "alpha": R(random.randint(1, 8), D), "beta": random.randint(1, 3)} if weak_super(l, l_s) else None


def gen_thm10():
    l, l_s = [R(random.randint(1, 8), 4) for _ in range(3)], [R(random.randint(1, 8), 4) for _ in range(3)]
    return {"lam": l, "lam_star": l_s, "alpha": R(random.randint(1, 8), D), "beta": random.randint(1, 3)} if weak_sub(l, l_s) else None


def gen_thm12():
    b, b_s = beta_vec(), beta_vec()
    return {"alpha": R(random.randint(1, 12), D), "beta": b, "beta_star": b_s} if weak_super(b_s, b) else None


def gen_thm11():
    a, a_s = alpha_vec(), alpha_vec()
    return {"alpha": a, "alpha_star": a_s} if weak_super(a_s, a) else None


def gen_thm15(which):
    a, a_s = alpha_vec(), alpha_vec()
    ok = weak_sub(a_s, a) if which == "i" else weak_super(a_s, a)
    return {"alpha": a, "alpha_star": a_s} if ok else None


def gen_thm16(which):
    b, b_s = beta_vec(), beta_vec()
    ok = weak_sub(b_s, b) if which == "i" else weak_super(b_s, b)
    return {"beta": b, "beta_star": b_s, "alpha": R(random.randint(1, 12), D)} if ok else None


HALF = R(1, 2)
SPECS = {
    "Theorem 1 (parallel, rh; alpha weakly supermajorized by alpha*; l = 0)": dict(order="rh", gen=gen_thm1,
        build=lambda i: (rational_system(i["alpha"], [i["beta"]] * 3, "parallel"), rational_system(i["alpha_star"], [i["beta"]] * 3, "parallel"))),
    "Theorem 2 (parallel, rh; alpha_i <= alpha*_i; l = 1/2)": dict(order="rh", gen=gen_thm2,
        build=lambda i: (closed_system(i["alpha_star"], [i["beta"]] * 3, [HALF] * 3, "parallel"), closed_system(i["alpha"], [i["beta"]] * 3, [HALF] * 3, "parallel"))),
    "Theorem 4 (parallel, rh; alpha_i >= alpha*_i, beta_i <= beta*_i; l = 1/2)": dict(order="rh", gen=gen_thm4,
        build=lambda i: (closed_system(i["alpha"], i["beta"], [HALF] * 3, "parallel"), closed_system(i["alpha_star"], i["beta_star"], [HALF] * 3, "parallel"))),
    "Theorem 7(i) (series, st; weak submajorization, beta >= 1; l = 0)": dict(order="st", gen=lambda: gen_thm7("ge1"),
        build=lambda i: (rational_system(i["alpha_star"], [i["beta"]] * 3, "series"), rational_system(i["alpha"], [i["beta"]] * 3, "series"))),
    "Theorem 8 (series, hr; beta* weakly supermajorized by beta; l = 0)": dict(order="hr", gen=gen_thm8,
        build=lambda i: (rational_system([i["alpha"]] * 3, i["beta"], "series"), rational_system([i["alpha"]] * 3, i["beta_star"], "series"))),
    "Theorem 9 (parallel, st; lam weakly supermajorized by lam*)": dict(order="st", gen=gen_thm9,
        build=lambda i: (closed_system([i["alpha"]] * 3, [i["beta"]] * 3, i["lam"], "parallel"), closed_system([i["alpha"]] * 3, [i["beta"]] * 3, i["lam_star"], "parallel"))),
    "Theorem 10 (series, st; lam weakly submajorized by lam*, beta >= 1)": dict(order="st", gen=gen_thm10,
        build=lambda i: (closed_system([i["alpha"]] * 3, [i["beta"]] * 3, i["lam_star"], "series"), closed_system([i["alpha"]] * 3, [i["beta"]] * 3, i["lam"], "series"))),
    "Theorem 11 (series, st; G exponential, alpha* weakly supermajorized by alpha; independence)": dict(order="st", gen=gen_thm11,
        build=lambda i: (rational_system([1] * 3, i["alpha"], "series") if all(R(v).q == 1 for v in i["alpha"]) else None, None) if False else (
            cf.Closed(sp.Mul(*[1 - (1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha"]])), cf.Closed(sp.Mul(*[1 - (1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha_star"]])))),
    "Theorem 12 (series, st; beta* weakly supermajorized by beta; independence; l = 0)": dict(order="st", gen=gen_thm12,
        build=lambda i: (rational_system([i["alpha"]] * 3, i["beta"], "series"), rational_system([i["alpha"]] * 3, i["beta_star"], "series"))),
    "Theorem 15(i) (parallel, st; alpha* weakly submajorized by alpha; independence)": dict(order="st", gen=lambda: gen_thm15("i"),
        build=lambda i: (cf.Closed(1 - sp.Mul(*[(1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha_star"]])), cf.Closed(1 - sp.Mul(*[(1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha"]])))),
    "Theorem 15(ii) (parallel, st; alpha* weakly supermajorized by alpha; independence)": dict(order="st", gen=lambda: gen_thm15("ii"),
        build=lambda i: (cf.Closed(1 - sp.Mul(*[(1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha"]])), cf.Closed(1 - sp.Mul(*[(1 - sp.exp(-cf.x)) ** R(v) for v in i["alpha_star"]])))),
    "Theorem 16(i) (parallel, st; beta* weakly submajorized by beta; independence; l = 0)": dict(order="st", gen=lambda: gen_thm16("i"),
        build=lambda i: (rational_system([i["alpha"]] * 3, i["beta_star"], "parallel"), rational_system([i["alpha"]] * 3, i["beta"], "parallel"))),
    "Theorem 16(ii) (parallel, st; beta* weakly supermajorized by beta; independence; l = 0)": dict(order="st", gen=lambda: gen_thm16("ii"),
        build=lambda i: (rational_system([i["alpha"]] * 3, i["beta"], "parallel"), rational_system([i["alpha"]] * 3, i["beta_star"], "parallel"))),
}

if __name__ == "__main__":
    out = {name: run(spec) for name, spec in SPECS.items()}
    print(json.dumps(out, indent=1))
