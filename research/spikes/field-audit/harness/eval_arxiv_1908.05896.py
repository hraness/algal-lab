"""Evaluate canonical claims of arxiv:1908.05896 (TL-G systems).

Topp-Leone generated family TL-G(a, th, xi):
    F(x; a, th, xi) = [G(x;xi)^th (2 - G(x;xi)^th)]^a,   S = 1 - F.
Baselines used: G1(x) = 1 - e^{-x} (printed examples) and G2(x) = 1 - e^{-x/2}
for the different-baseline theorems (G2 <= G1 pointwise, matching the paper's
baseline-ordering hypothesis).

Independent components.  X_{1:n} survival = prod S_i;
X_{n:n} survival = 1 - prod F_i.

Paper conventions (verified in canonical): X <=st Y iff S_Y >= S_X;
X <=hr Y iff r_X >= r_Y; X <=lr Y iff fY/fX increasing -- all standard.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_1908.05896.json")
OUT = os.path.join(HERE, "eval_arxiv_1908.05896.result.json")
R = sp.Rational


def F(tlg_a, th, G):
    # F = [G^th (2 - G^th)]^a  written through exp/log so that fractional
    # powers never introduce Abs/sign nodes under symbolic differentiation.
    Gt = sp.exp(th * sp.log(G))
    return sp.exp(tlg_a * sp.log(Gt * (2 - Gt)))

def series_sf(params, G):
    """P(min > x) = prod S_i."""
    s = sp.Integer(1)
    for (a, th) in params:
        s *= 1 - F(a, th, G)
    return s

def parallel_sf(params, G):
    """P(max > x) = 1 - prod F_i."""
    s = sp.Integer(1)
    for (a, th) in params:
        s *= F(a, th, G)
    return 1 - s

G1 = 1 - sp.exp(-x)        # standard exponential baseline
G2 = 1 - sp.exp(-x/2)      # G2 <= G1 pointwise (st-larger baseline)


def claim_instances(r):
    """Return list of (Xsurv, Ysurv) pairs admissible for the record."""
    claim = r["claim"]
    if claim in ("Example 3.1", "Counterexample 3.1"):
        a = [R(1), R(9)]; ast = [R(4), R(6)]; th = R(1, 2)
        X = series_sf([(ai, th) for ai in a], G1)
        Y = series_sf([(ai, th) for ai in ast], G1)
        return [(X, Y)]
    if claim in ("Example 3.2", "Counterexample 3.2"):
        th = [R(1,10), R(4,10)]; ths = [R(2,10), R(5,10)]; a = R(1,2)
        X = parallel_sf([(a, t) for t in th], G1)
        Y = parallel_sf([(a, t) for t in ths], G1)
        return [(X, Y)]
    if "Theorem 3.1" in claim:   # alpha* <^m alpha, series, hr
        out = []
        for (a, ast, th) in [([R(1),R(9)], [R(4),R(6)], R(1,2)),
                             ([R(1),R(8)], [R(3),R(6)], R(1)),
                             ([R(1),R(2),R(9)], [R(3),R(4),R(5)], R(2)),
                             ([R(1),R(1),R(10)], [R(4),R(4),R(4)], R(1))]:
            out.append((series_sf([(ai,th) for ai in a], G1),
                        series_sf([(ai,th) for ai in ast], G1)))
        return out
    if "Corollary 3.1" in claim or "Theorem 3.2" in claim:
        # parallel, st, theta <^m theta* (Cor) or weak submajorization (Thm)
        out = []
        for (th, ths, a) in [([R(1,10),R(4,10)], [R(2,10),R(5,10)], R(1,2)),
                             ([R(1),R(2)], [R(1),R(4)], R(1)),       # majorized equal-sum
                             ([R(1,2),R(1),R(2)], [R(1),R(2),R(3)], R(3))]:
            out.append((parallel_sf([(a,t) for t in th], G1),
                        parallel_sf([(a,t) for t in ths], G1)))
        return out
    if "Theorem 3.3" in claim:   # coordinatewise theta <= theta*
        # integer a keeps every power exact (no sqrt-of-square -> Abs)
        out = []
        for (th, ths, a) in [([R(1),R(2)], [R(2),R(3)], R(1)),
                             ([R(1,2),R(1),R(3,2)], [R(1),R(2),R(2)], R(2))]:
            out.append((parallel_sf([(a,t) for t in th], G1),
                        parallel_sf([(a,t) for t in ths], G1)))
        return out
    if "Theorem 3.4" in claim:   # lr iff sum a_i <= sum a*_i (parallel)
        out = []
        for (a, ast) in [([R(1),R(3)], [R(2),R(4)]),      # 4 <= 6
                         ([R(1),R(2)], [R(1),R(2)]),      # equal
                         ([R(2),R(3)], [R(1),R(9)])]:     # 5 <= 10
            out.append((parallel_sf([(ai,R(1)) for ai in a], G1),
                        parallel_sf([(ai,R(1)) for ai in ast], G1)))
        return out
    if "Theorem 3.5" in claim:   # series, different baselines, a* <^m a
        out = []
        for (a, ast, th) in [([R(1),R(5)], [R(2),R(4)], R(1)),
                             ([R(1),R(2),R(6)], [R(3),R(3),R(3)], R(1,2))]:
            out.append((series_sf([(ai,th) for ai in a], G1),
                        series_sf([(ai,th) for ai in ast], G2)))
        return out
    if "Theorem 3.6(i)" in claim:   # parallel, weak submajorized scales, baselines
        out = []
        for (th, ths, a) in [([R(1),R(2)], [R(1),R(4)], R(1)),
                             ([R(1,2),R(2),R(3)], [R(1),R(3),R(4)], R(2))]:
            out.append((parallel_sf([(a,t) for t in th], G1),
                        parallel_sf([(a,t) for t in ths], G2)))
        return out
    if "Theorem 3.6(ii)" in claim:  # coordinatewise
        out = []
        for (th, ths, a) in [([R(1),R(2)], [R(2),R(3)], R(1)),
                             ([R(1,2),R(1)], [R(1),R(2)], R(2))]:
            out.append((parallel_sf([(a,t) for t in th], G1),
                        parallel_sf([(a,t) for t in ths], G2)))
        return out
    return []


def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=claim, order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        inst = 0; wit = None; und = 0
        is_counter = "Counterexample" in claim
        allhold = True
        for (X, Y) in claim_instances(r):
            ok, w, u = cf.check(order, Closed(X), Closed(Y))
            inst += 1; und += u
            if not ok:
                allhold = False; wit = str(w)
            if is_counter:
                # 'no lr ordering' means the ratio is non-monotone: the reverse
                # direction must also fail for the claim to hold.
                ok2, w2, u2 = cf.check(order, Closed(Y), Closed(X))
                und += u2
                if ok2:
                    allhold = True   # reverse direction holds -> no crossing
        status = "holds" if allhold else "refuted"
        out.append(dict(claim=claim, order=order, status=status,
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])

if __name__ == "__main__":
    go()
