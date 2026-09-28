"""Evaluate canonical claims of doi_10.1080/10920277.2019.1671203 (TG portfolio).

X_{lambda_i} ~ TG(lambda_i), baseline F:  Fbar_X(x) = Fbar(x)(1 - lambda F(x)),
lambda in [-1,1].  Y_i = I_{p_i} X_{lambda_i}, independent Bernoulli shocks;
components independent.  Thus
    cdf(Y_{n:n}) = prod_i (1 - p_i Fbar_i(x)),   surv(Y_{1:n}) = prod_i p_i Fbar_i(x).

Matrix majorization [lambda*; h(p*)] = [lambda; h(p)] T_omega,
T_omega = [[1-w, w],[w, 1-w]] acts on adjacent coordinates; starred entries
are convex mixtures (less spread).  Printed h:  log(2+p) and (5p+2)/(p+1).

Directions are encoded exactly as the canonical records print them; several
records disagree about which side is starred -- each is tested separately.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1080_10920277.2019.1671203.json")
OUT = os.path.join(HERE, "eval_doi_10.1080_10920277.2019.1671203.result.json")
R = sp.Rational


def hval(p, h):
    return sp.log(2 + p) if h == "log" else (5 * p + 2) / (p + 1)


def h_inv(u, h):
    return sp.exp(u) - 2 if h == "log" else (u - 2) / (5 - u)


def tg_sf(lam, Fbar):
    F = 1 - Fbar
    return sp.expand(Fbar * (1 - lam * F))


def max_sf(ps, ls, Fbar):
    g = sp.Integer(1)
    for p, l in zip(ps, ls):
        g *= 1 - p * tg_sf(l, Fbar)
    return 1 - g


def min_sf(ps, ls, Fbar):
    g = sp.Integer(1)
    for p, l in zip(ps, ls):
        g *= p * tg_sf(l, Fbar)
    return g


def T_apply(vec, i, j, om):
    """Robin-Hood transfer on coordinates i,j: v'_i=(1-w)v_i+w v_j,
    v'_j=w v_i+(1-w)v_j."""
    v = list(vec)
    vi, vj = v[i], v[j]
    v[i] = (1 - om) * vi + om * vj
    v[j] = om * vi + (1 - om) * vj
    return v


EXP = sp.exp(-x)
WBL = sp.exp(-x**2)

# generic instance pools
def maxstar_cases():
    """(ls, ps_raw: list of (u from h), h, Fb) -> (S_unstarred, S_starred)."""
    out = []
    for (ls, ps, oms, Fb, h) in [
            ([R(1,5), R(4,5)], [R(3,10), R(9,10)], [(0, 1, R(1,5))], EXP, "log"),
            ([R(1,5), R(4,5)], [R(3,10), R(9,10)], [(0, 1, R(2,5))], WBL, "ratio"),
            ([R(1,10), R(3,5), R(9,10)], [R(1,5), R(1,2), R(4,5)],
             [(0, 1, R(1,5)), (1, 2, R(2,5))], EXP, "log"),
            ([R(1,10), R(3,5), R(9,10)], [R(1,5), R(1,2), R(4,5)],
             [(0, 1, R(1,3)), (1, 2, R(1,4))], WBL, "ratio")]:
        u = [hval(p, h) for p in ps]
        l2, u2 = list(ls), list(u)
        for (i, j, om) in oms:
            l2 = T_apply(l2, i, j, om)
            u2 = T_apply(u2, i, j, om)
        pstar = [h_inv(ui, h) for ui in u2]
        out.append((max_sf(ps, ls, Fb), max_sf(pstar, l2, Fb)))
    return out


def minstar_cases():
    """min system; hypothesis prod p* <= prod p and lambda ~<_w lambda*;
    claim Y* <=st Y.  -> (S_starred, S_unstarred)."""
    out = []
    for (ls, lss, ps, pss, Fb) in [
            # lambda ~<_w lambda* : desc sums l <= l*
            ([R(3,10), R(7,10)], [R(1,5), R(4,5)],
             [R(4,5), R(9,10)], [R(1,2), R(3,5)], EXP),
            ([R(3,10), R(7,10)], [R(1,5), R(4,5)],
             [R(4,5), R(9,10)], [R(1,2), R(3,5)], WBL),
            ([R(3,10), R(2,5), R(1,2)], [R(1,5), R(2,5), R(4,5)],
             [R(3,5), R(4,5), R(9,10)], [R(1,2), R(3,5), R(4,5)], EXP),
            ([R(3,10), R(2,5), R(1,2)], [R(1,5), R(2,5), R(4,5)],
             [R(3,5), R(4,5), R(9,10)], [R(1,2), R(3,5), R(4,5)], WBL)]:
        out.append((min_sf(pss, lss, Fb), min_sf(ps, ls, Fb)))
    return out


def instances(claim, direction):
    """Return list of (S_left, S_right) per the printed left <=order right."""
    if claim.startswith("Corollary 3.1"):
        # Y2:2 >=st mean-homogeneous counterpart -> right = homogeneous
        out = []
        for (ls, ps, Fb, h) in [([R(1,5), R(4,5)], [R(3,10), R(9,10)], EXP, "log"),
                                ([R(1,5), R(4,5)], [R(3,10), R(9,10)], WBL, "ratio")]:
            n = 2
            lb = (ls[0] + ls[1]) / 2
            ub = (hval(ps[0], h) + hval(ps[1], h)) / 2
            pb = h_inv(ub, h)
            Shom = max_sf([pb] * n, [lb] * n, Fb)
            out.append((Shom, max_sf(ps, ls, Fb)))   # hom <=st Y
        return out
    if claim.startswith("Corollary 4.1"):
        out = []
        for (ls, ps, Fb) in [([R(1,5), R(4,5)], [R(4,5), R(9,10)], EXP),
                             ([R(1,5), R(4,5)], [R(4,5), R(9,10)], WBL)]:
            n = len(ls)
            lh = [(1 + l) / 2 for l in ls]
            ph = [sp.sqrt(ps[0] * ps[1]) for _ in range(n)]
            out.append((min_sf(ph, lh, Fb), min_sf(ps, ls, Fb)))
        return out
    # PDF-verified direction for ALL max claims: Y*_{n:n} <=st/rh Y_{n:n}
    # (starred = T-transformed, less spread).  Canonical direction strings
    # flipped the stars on some records; we test the printed direction.
    if claim.startswith(("Theorem 3.3", "Theorem 3.1", "Theorem 3.2",
                         "Corollary 3.2", "Corollary 3.3")) or \
            ("Corollary 3.3" in claim) or claim.startswith("Application") or \
            claim.startswith("Section 5"):
        if "Theorem 4.1" in claim or "second bullet" in claim:
            return minstar_cases()      # (Sst, Sun): claim Y* <=st Y
        return [tuple(reversed(p)) for p in maxstar_cases()]  # (Sst, Sun)
    if claim.startswith(("Theorem 4.1", "Theorem 4.2")):
        return minstar_cases()          # claim Y* <=order Y
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
        pairs = instances(claim, c.get("direction"))
        # direction: resolve from the canonical direction string
        d = str(c.get("direction") or "")
        inst = 0; wit = None; und = 0; allhold = True
        for item in pairs:
            A, B = item              # all records now (left,right) as printed
            ok, w, u = cf.check(order, Closed(A), Closed(B))
            inst += 1; und += u
            if not ok:
                allhold = False; wit = str(w)
        out.append(dict(claim=claim, order=order,
                        status="holds" if allhold else "refuted",
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
