"""Evaluator for arXiv:2002.12474 (GM and W-G systems under matrix majorization).

Gompertz-Makeham GM(a,b,l): F = 1 - exp(-l x - (a/b)(e^{b x} - 1));
  hazard r = l + a e^{b x}; series hazard = sum of component hazards.
W-G(a,b,g): H = 1 - exp(-a (w(g x))^b); exponential baseline F=1-e^{-g x}
  uses w(u) = e^{g x} - 1 evaluated at u = gamma x.

T-transform convention (Example 1/2): starred matrix row m* maps to
m = (d m1* + (1-d) m2*, (1-d) m1* + d m2*) with d = 0.45.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def gm_hazard(a, b, l):
    return A.R(l) + A.R(a) * e ** (A.R(b) * x)


def gm_surv(a, b, l):
    return e ** (-A.R(l) * x - (A.R(a) / A.R(b)) * (e ** (A.R(b) * x) - 1))


def wg_surv(a, b, g):
    """W-G with exponential baseline F(u)=1-e^{-u}: w(u) = e^u - 1."""
    return e ** (-A.R(a) * (e ** (A.R(g) * x) - 1) ** A.R(b))


def wg_hazard(a, b, g):
    S = wg_surv(a, b, g)
    return -sp.diff(S, x) / S


def series_hazard(params, fam="gm"):
    if fam == "gm":
        return sum(gm_hazard(*p) for p in params)
    return sum(wg_hazard(*p) for p in params)


def t_transform(row, d):
    r1, r2 = [A.R(v) for v in row]
    return [d * r1 + (1 - d) * r2, (1 - d) * r1 + d * r2]


def run_diff(expr):
    """check expr >= 0 on (0,oo) via interval evaluation of a 0-survival trick:
    encode as st check of Closed(expr) is wrong; evaluate sign directly."""
    import closedform as cf
    from mpmath import iv
    und = 0
    for pt in cf.grid(0, sp.oo, (expr,)):
        decided = False
        for dps in (60, 150, 400):
            iv.dps = dps
            v = cf.iv_eval(expr, pt)
            if v.b < 0:
                return False, pt, und
            if v.a >= 0:
                decided = True
                break
        und += not decided
    return True, None, und


def run_order_on_systems(order, survX, survY):
    return A.check_dist(order, A.C(survX), A.C(survY))


def main():
    claims = json.load(open("../canonical/arxiv_2002.12474.json"))
    out = []

    # Example 1 / Theorem 6 matrices (printed T-transform link, d=0.45)
    Mstar = [[A.R(48, 10), A.R(34, 10)], [A.R(25, 10), A.R(16, 10)]]
    d = A.R(45, 100)
    M = [t_transform(Mstar[0], d), t_transform(Mstar[1], d)]
    # check printed values
    assert M[0] == [A.R(403, 100), A.R(417, 100)]
    assert M[1] == [A.R(401, 200), A.R(419, 200)]

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c in ("Example 1", "Theorem 1"):
            # W-Exp series hazard with beta=3: r_i = 3 a_i (e^{g_i x}-1)^2 e^{g_i x} g_i
            rX = series_hazard([(M[0][0], 3, M[1][0]), (M[0][1], 3, M[1][1])], "wg")
            rY = series_hazard([(Mstar[0][0], 3, Mstar[1][0]),
                                (Mstar[0][1], 3, Mstar[1][1])], "wg")
            h, w, u = run_diff(rY - rX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="W-Exp baseline w=e^{gx}-1, beta=3; printed T-transform "
                     "matrices; claim X1:2 >=hr Y1:2 <=> rX <= rY.")

        elif c == "Theorem 2" or c == "Theorem 3":
            # n-component single/product of T-transforms; use n=2 with two
            # chained transforms for Thm 3 and one for Thm 2 (W-G, beta>=2)
            pairs = []
            if c == "Theorem 2":
                pairs = [(M, Mstar)]
            else:
                mid = [t_transform(row, A.R(1, 2)) for row in Mstar]
                pairs = [(M2 := [t_transform(row, A.R(2, 5)) for row in mid], mid)]
            n = und = 0
            wit = None
            for MX, MY in pairs:
                rX = series_hazard([(MX[0][i], 3, MX[1][i]) for i in range(2)], "wg")
                rY = series_hazard([(MY[0][i], 3, MY[1][i]) for i in range(2)], "wg")
                h, w, u = run_diff(rY - rX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        elif c == "Theorem 4":  # rh maxima, alpha ~_w alpha* (weak submaj)
            n = und = 0
            wit = None
            for aX, aY in [([A.R(1), A.R(2)], [A.R(2), A.R(3)]),
                           ([A.R(1), A.R(2), A.R(3)], [A.R(2), A.R(3), A.R(4)])]:
                assert A.weak_sub(aX, aY)
                # common beta=gamma=1: W-Exp surv = e^{-a(e^x - 1)^b}
                FX = sp.prod([1 - wg_surv(ai, 1, 1) for ai in aX])
                FY = sp.prod([1 - wg_surv(ai, 1, 1) for ai in aY])
                SX_, SY_ = 1 - FX, 1 - FY
                h, w, u = run_order_on_systems("rh", SX_, SY_)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und,
                note="alpha majorizes alpha*; W-Exp baseline beta=gamma=1.")

        elif c in ("Example 2", "Theorem 6"):
            # GM series hazard: r = n*lam + sum a_i e^{b_i x}; common lam
            rX = 2 * 1 + M[0][0] * e ** (M[1][0] * x) + M[0][1] * e ** (M[1][1] * x)
            rY = 2 * 1 + Mstar[0][0] * e ** (Mstar[1][0] * x) + \
                Mstar[0][1] * e ** (Mstar[1][1] * x)
            h, w, u = run_diff(rY - rX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u, note="common lambda=1.")

        elif c == "Theorem 7":
            # single T-transform between (alpha;beta) matrices, n=2
            rX = M[0][0] * e ** (M[1][0] * x) + M[0][1] * e ** (M[1][1] * x)
            rY = Mstar[0][0] * e ** (Mstar[1][0] * x) + \
                Mstar[0][1] * e ** (Mstar[1][1] * x)
            h, w, u = run_diff(rY - rX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="the printed (alpha;beta) matrix pair of Example 2.")

        elif c == "Theorem 8":
            # product of two T-transforms on 2x3 matrix
            Mstar3 = [[A.R(5), A.R(3), A.R(4)], [A.R(3), A.R(1), A.R(2)]]
            mid = [list(t_transform([row[0], row[1]], A.R(1, 2))) + [row[2]]
                   for row in Mstar3]
            # T-transforms on cols (1,2) then (2,3)
            final = [[row[0]] + t_transform([row[1], row[2]], A.R(1, 3))
                     for row in mid]
            rX = sum(final[0][i] * e ** (final[1][i] * x) for i in range(3))
            rY = sum(Mstar3[0][i] * e ** (Mstar3[1][i] * x) for i in range(3))
            h, w, u = run_diff(rY - rX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="n=3, two chained T-transforms; common lambda.")

        elif c == "Theorem 9":
            # printed '=st' under weak majorization: equality needs equal sums.
            # instance satisfying weak supermajorization but different sums.
            SX = sp.prod([gm_surv(2, 1, l) for l in [1, 4]])
            SY = sp.prod([gm_surv(2, 1, l) for l in [3, 3]])
            h, w, u = A.check_dist("st", A.C(SX), A.C(SY))
            h2, w2, u2 = A.check_dist("st", A.C(SY), A.C(SX))
            if not h or not h2:
                add(recd, "refuted", 1,
                    f"lambda=(1,4) ~w lambda*=(3,3) but survivals differ at "
                    f"x={w or w2}",
                    note="as printed, weak majorization alone does not force "
                         "equality; equality requires equal sums.")
            else:
                add(recd, "holds", 1)

        elif c == "Theorem 10":  # st maxima, weak submajorization on alpha
            n = und = 0
            wit = None
            for aX, aY in [([1, 2], [2, 3]), ([1, 2, 3], [2, 3, 4])]:
                assert A.weak_sub(aX, aY)
                FX = sp.prod([1 - gm_surv(ai, 1, 1) for ai in aX])
                FY = sp.prod([1 - gm_surv(ai, 1, 1) for ai in aY])
                h, w, u = run_order_on_systems("st", 1 - FX, 1 - FY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        elif c == "Theorem 5":  # W-Exp gamma vectors weak submaj, st maxima
            n = und = 0
            wit = None
            for gX, gY in [([1, 2], [2, 3]), ([1, 2, 3], [2, 3, 4])]:
                assert A.weak_sub(gX, gY)
                FX = sp.prod([1 - wg_surv(1, 2, gi) for gi in gX])
                FY = sp.prod([1 - wg_surv(1, 2, gi) for gi in gY])
                h, w, u = run_order_on_systems("st", 1 - FX, 1 - FY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_2002.12474.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
