"""Pilot tests for doi:10.2991/jsta.2018.17.3.8 (Frechet and scale-family extremes).

Frechet corollaries reduce to closed-form sums (the maximum of independent
Frechet variables with common shape a is Frechet with parameter sum lam_i^a),
so they are checked by exact comparison of those sums. Generalized-exponential
series systems GE(a, lam): survival prod_i [1 - (1 - e^{-lam_i x})^{a_i}] are
decided exactly with integer shapes (polynomials in s = e^{-x/D}); non-integer
shapes use the closed-form interval checker. Printed Example 3.1 is checked in
both directions.
"""
import json
import random

import sympy as sp

import closedform as cf
from ratdist import Dist, hr, st, z

random.seed(99)
R = sp.Rational
D = 4


def weak_sub(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def weak_super(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def ge_series_int(shapes, rates):
    S = sp.Mul(*[1 - (1 - z ** int(R(r) * D)) ** int(a) for a, r in zip(shapes, rates)])
    return Dist(sp.expand(S), sp.Integer(0), sp.Integer(1), increasing=False)


def ge_series_closed(shapes, rates):
    x = cf.x
    return cf.Closed(sp.Mul(*[1 - (1 - sp.exp(-R(r) * x)) ** R(a) for a, r in zip(shapes, rates)]))


def search(gen, decide, trials=30):
    tested, refuted = 0, None
    for _ in range(trials * 60):
        if tested >= trials:
            break
        inst = gen()
        if inst is None:
            continue
        holds, witness = decide(inst)
        tested += 1
        if not holds and refuted is None:
            refuted = {k: [str(v) for v in val] if isinstance(val, list) else str(val) for k, val in inst.items()}
            refuted["witness"] = str(witness)
    return {"tested": tested, "refuted_example": refuted}


out = {}

# Frechet corollaries: X*_{n:n} <=rh X_{n:n} iff sum lam*^a <= sum lam^a (common mu, a).
def frechet_gen(rule, a_rule):
    def gen():
        lam, lam_s = [R(random.randint(1, 16), 4) for _ in range(3)], [R(random.randint(1, 16), 4) for _ in range(3)]
        r = R(random.randint(1, 8), 4)
        a = r + R(random.randint(0, 8), 4) if a_rule == "ge" else r * R(random.randint(1, 4), 4)
        return {"lam": lam, "lam_star": lam_s, "r": r, "a": a} if rule(lam, lam_s, r) else None
    return gen


def lam_pow_sum(v, a):
    return sum(sp.nsimplify(x) ** a for x in v)


out["Corollary 3.1 (1/lam* weakly supermajorized by 1/lam => X* <=rh X)"] = search(
    frechet_gen(lambda l, ls, r: weak_super([1 / x for x in ls], [1 / x for x in l]), "ge"),
    lambda i: (sp.N(lam_pow_sum(i["lam_star"], i["a"]) - lam_pow_sum(i["lam"], i["a"]), 50) <= 0, None))
out["Corollary 3.2(i) (a >= r, lam*^r weakly submajorized by lam^r => X* <=rh X)"] = search(
    frechet_gen(lambda l, ls, r: weak_sub([x ** r for x in ls], [x ** r for x in l]), "ge"),
    lambda i: (sp.N(lam_pow_sum(i["lam_star"], i["a"]) - lam_pow_sum(i["lam"], i["a"]), 50) <= 0, None))
out["Corollary 3.2(ii) (a <= r, lam*^r weakly supermajorized by lam^r => X <=rh X*)"] = search(
    frechet_gen(lambda l, ls, r: weak_super([x ** r for x in ls], [x ** r for x in l]), "le"),
    lambda i: (sp.N(lam_pow_sum(i["lam"], i["a"]) - lam_pow_sum(i["lam_star"], i["a"]), 50) <= 0, None))


# Corollary 3.4: GE series, common rate, alpha* weakly supermajorized by alpha => X <=hr X*.
def gen_c34():
    a, a_s = [random.randint(1, 5) for _ in range(3)], [random.randint(1, 5) for _ in range(3)]
    return {"alpha": a, "alpha_star": a_s} if weak_super(a_s, a) else None


out["Corollary 3.4 (GE series, alpha* weakly supermajorized by alpha => X <=hr X*)"] = search(
    gen_c34, lambda i: hr(ge_series_int(i["alpha"], [1] * 3), ge_series_int(i["alpha_star"], [1] * 3)))


# Corollary 3.5 reading B: a >= 1 (a = 2), lam* weakly submajorized by lam => X <=st X*.
def gen_c35(rule):
    def gen():
        l, ls = [R(random.randint(1, 12), D) for _ in range(3)], [R(random.randint(1, 12), D) for _ in range(3)]
        return {"lam": l, "lam_star": ls} if rule(ls, l) else None
    return gen


out["Corollary 3.5 reading B (a = 2, lam* weakly submajorized by lam => X <=st X*)"] = search(
    gen_c35(weak_sub), lambda i: st(ge_series_int([2] * 3, i["lam"]), ge_series_int([2] * 3, i["lam_star"])))
out["Corollary 3.5 reading A (a = 1/2, lam* weakly supermajorized by lam => X* <=st X)"] = search(
    gen_c35(weak_super), lambda i: cf.check("st", ge_series_closed([R(1, 2)] * 3, i["lam_star"]), ge_series_closed([R(1, 2)] * 3, i["lam"]))[:2], trials=15)

# Printed Example 3.1.
def both(X, Y):
    a, _, _ = cf.check("st", X, Y)
    b, _, _ = cf.check("st", Y, X)
    return {"X_le_st_Xstar": a, "Xstar_le_st_X": b}


out["Example 3.1(i) a = 2, lam = (4, 1/2), lam* = (2, 3) (printed: not ordered)"] = both(
    ge_series_closed([2, 2], [4, R(1, 2)]), ge_series_closed([2, 2], [2, 3]))
out["Example 3.1(ii) case 1, a = 0.6, lam = (1, 5.5), lam* = (2, 3) (printed: X <=st X*)"] = both(
    ge_series_closed([R(3, 5)] * 2, [1, R(11, 2)]), ge_series_closed([R(3, 5)] * 2, [2, 3]))
out["Example 3.1(ii) case 2, a = 0.6, lam = (1, 2.25), lam* = (1.1, 2.14) (printed: X* <=st X)"] = both(
    ge_series_closed([R(3, 5)] * 2, [1, R(9, 4)]), ge_series_closed([R(3, 5)] * 2, [R(11, 10), R(107, 50)]))
print(json.dumps(out, indent=1, default=str))
