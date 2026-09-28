"""Evaluator for doi:10.17713/ajs.v50i3.1025 (Burr/Harris claim portfolios).

Model: Yi = I_{p_i} Xi (Bernoulli occurrence).  Y_{1:n} has survival
P(Y_{1:n} > x) = prod p_i S_i(x) (all claims occurred and all exceed x).
Hazard rate on x>0: r_Y(x) = sum_i r_{X_i}(x)  -- the prod p_i factor is
constant and cancels in f/S, so the hr ordering reduces to comparing sums
of component hazards.

Burr XII: S(x) = (1 + (b x)^l)^{-a}; r(x) = a l (b x)^l / (x(1+(b x)^l)).
Harris: S(x) = [b F^a(x) / (1 - (1-b) F^a(x))]^{1/a}, baseline F.
Claim: Y_{1:n}* <=hr Y_{1:n}  <=>  sum r_i* >= sum r_i.
"""
import json
import auditlib as A
import sympy as sp
from mpmath import iv, mp

x = A.x
e = A.e

mp.dps = 100
iv.dps = 100


def burr_hazard(a, b, l):
    a, b, l = A.R(a), A.R(b), A.R(l)
    u = (b * x) ** l
    return a * l * u / (x * (1 + u))


def burr_S(a, b, l):
    return (1 + (A.R(b) * x) ** A.R(l)) ** (-A.R(a))


def harris_S(a, b, F):
    """S_Harris = [b F^a / (1 - (1-b) F^a)]^{1/a}."""
    Fa = F ** A.R(a)
    return (A.R(b) * Fa / (1 - (1 - A.R(b)) * Fa)) ** (1 / A.R(a))


def r_of(S):
    return -sp.diff(S, x) / S


def check_hr_sum(rXs, rYs):
    """Return (holds, witness): sum r*_i >= sum r_i on (0, oo)?"""
    E = sum(rYs) - sum(rXs)
    import closedform as cf
    lo, hi = 0, None
    # scan a rational grid; interval evaluate
    pts = []
    for k in range(-12, 14):
        pts.append(sp.Rational(2) ** k)
    for pt in pts:
        try:
            v = cf.iv_eval(E, pt)
        except Exception:
            return None, pt
        if v.b < 0:
            return False, pt
    return True, None


def check_sign_change(E, pts):
    """Find a positive and a negative interval point."""
    import closedform as cf
    pos = neg = None
    for pt in pts:
        try:
            v = cf.iv_eval(E, pt)
        except Exception:
            continue
        if v.a > 0:
            pos = pt
        if v.b < 0:
            neg = pt
        if pos and neg:
            break
    return pos, neg


def grid():
    return [sp.Rational(2) ** k for k in range(-14, 15)] + \
           [sp.Rational(k, 10) for k in range(1, 40)]


def main():
    claims = json.load(open("../canonical/doi_10.17713_ajs.v50i3.1025.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    ex1 = dict(aX=[4, A.R(7, 10), A.R(1, 5)], aY=[A.R(21, 5), A.R(3, 5), A.R(3, 10)],
               bX=[5, A.R(7, 2), A.R(6, 5)], l=2)
    ex3 = dict(aX=[A.R(11, 10), A.R(8, 5), A.R(5, 2)],
               aY=[1, A.R(17, 10), A.R(23, 10)],
               bX=[A.R(1, 10), A.R(3, 10), A.R(3, 5)])

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c == "Example 1":
            # Burr l=2; claim r_Y1:n* >= r_Y1:n
            rX = [burr_hazard(a, b, ex1['l']) for a, b in zip(ex1['aX'], ex1['bX'])]
            rY = [burr_hazard(a, ex1['bX'][i], ex1['l']) for i, a in enumerate(ex1['aY'])]
            h, w = check_hr_sum(rX, rY)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, 0,
                note="printed vectors; Pi p* = .021875 <= .024 = Pi p.")

        elif c == "Example 2":
            # discordant alpha* -> counterexample: sign change expected
            aY = [A.R(21, 5), A.R(3, 10), A.R(3, 5)]
            rX = [burr_hazard(a, b, 2) for a, b in zip(ex1['aX'], ex1['bX'])]
            rY = [burr_hazard(aY[i], ex1['bX'][i], 2) for i in range(3)]
            E = sum(rY) - sum(rX)
            pos, neg = check_sign_change(E, grid())
            ok = pos is not None and neg is not None
            add(recd, "holds" if ok else "refuted", 1,
                f"pos={pos} neg={neg}",
                note="counterexample verified iff E takes both signs.")

        elif c == "Example 3":
            # Harris severities, baseline Fbar = Gamma(2,1): S0=e^{-x}(1+x)
            S0 = e ** (-x) * (1 + x)
            SX = [harris_S(a, b, S0) for a, b in zip(ex3['aX'], ex3['bX'])]
            SY = [harris_S(a, ex3['bX'][i], S0) for i, a in enumerate(ex3['aY'])]
            rX = [r_of(s) for s in SX]
            rY = [r_of(s) for s in SY]
            h, w = check_hr_sum(rX, rY)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, 0,
                note="Pi p*=.0005 <= .00075=Pi p; alpha ~^w alpha* "
                     "(lower partial sums 1.1,2.7,5.2 >= 1,2.7,5.0).")

        elif c == "Theorem 1":
            # general model -- test both printed variants on Burr l=2:
            # (i) r increasing+convex in a (Burr r is linear in a), Sn-
            #     (oppositely ordered a,b), a ~_w a* (top sums a <= a*).
            # (ii) bracketed: Sn+ with weak supermajorization.
            res = []
            # variant (i): a desc, b asc (Sn-): aX=(3,2,1) b=(1,2,3)
            for aX, aY, bX, sgn in [
                    ([3, 2, 1], [4, 3, 1], [1, 2, 3], "Sn- submaj"),
                    ]:
                assert A.weak_sub(aX, aY)
                rX = [burr_hazard(a, b, 2) for a, b in zip(aX, bX)]
                rY = [burr_hazard(aY[i], bX[i], 2) for i in range(len(aX))]
                h, w = check_hr_sum(rX, rY)
                res.append((sgn, h, w))
            # variant (ii): Sn+ a,b both asc; weak supermaj:
            # a's smallest-j sums >= a*'s (i.e. weak_super(a*, a))
            aX, aY, bX = [1, 3, 3], [1, 2, 4], [1, 2, 3]
            assert A.weak_super(aY, aX)  # a*'s smallest sums <= a's
            rX = [burr_hazard(a, b, 2) for a, b in zip(aX, bX)]
            rY = [burr_hazard(aY[i], bX[i], 2) for i in range(len(aX))]
            h, w = check_hr_sum(rX, rY)
            res.append(("Sn+ supermaj", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res))

        elif c == "Theorem 2":
            # exponentiated scale S = [F(bx)]^a, F = Weibull(2): F=e^{-x^2}
            # xr(x) = 2x^2 increasing; a ~_w a* (top sums a <= a*); Sn+/Sn-
            res = []
            F = e ** (-(x) ** 2)
            for aX, aY, bX in [([1, 2, 4], [2, 3, 4], [1, 2, 3]),
                               ([1, 2], [A.R(3, 2), A.R(5, 2)], [1, 2])]:
                assert A.weak_sub(aX, aY)
                SX = [F.subs(x, A.R(b) * x) ** A.R(a) for a, b in zip(aX, bX)]
                SY = [F.subs(x, A.R(bX[i]) * x) ** A.R(aY[i])
                      for i in range(len(aX))]
                rX = [r_of(s) for s in SX]
                rY = [r_of(s) for s in SY]
                h, w = check_hr_sum(rX, rY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="ES model with Weibull(1,2) baseline; a ~_w a*; "
                     "a,b similarly ordered.")

        elif c == "Theorem 3":
            res = []
            F = e ** (-(x) ** 2)
            for aX, bX, bY in [(2, [1, 2, 4], [2, 3, 4]),
                               (A.R(3, 2), [1, 3], [2, 3])]:
                assert A.weak_sub(bX, bY)
                SX = [F.subs(x, A.R(b) * x) ** A.R(aX) for b in bX]
                SY = [F.subs(x, A.R(b) * x) ** A.R(aX) for b in bY]
                rX = [r_of(s) for s in SX]
                rY = [r_of(s) for s in SY]
                h, w = check_hr_sum(rX, rY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="beta ~_w beta*, common alpha; Weibull baseline "
                     "(xr=2x^2 increasing convex).")

        elif c == "Theorem 4":
            # row weak submajorization of both rows of [a;b]
            res = []
            F = e ** (-(x) ** 2)
            for aX, aY, bX, bY in [([1, 2, 4], [2, 3, 4],
                                    [1, 2, 4], [2, 3, 4]),
                                   ([1, 3], [2, 4],
                                    [1, 3], [2, 4])]:
                assert A.weak_sub(aX, aY) and A.weak_sub(bX, bY)
                SX = [F.subs(x, A.R(b) * x) ** A.R(a) for a, b in zip(aX, bX)]
                SY = [F.subs(x, A.R(b) * x) ** A.R(a) for a, b in zip(aY, bY)]
                rX = [r_of(s) for s in SX]
                rY = [r_of(s) for s in SY]
                h, w = check_hr_sum(rX, rY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="both rows ~_w; Weibull baseline.")

        elif c == "Theorem 5":
            # Burr, Example-1 numbers satisfy the printed hypotheses
            rX = [burr_hazard(a, b, 2) for a, b in zip(ex1['aX'], ex1['bX'])]
            rY = [burr_hazard(a, ex1['bX'][i], 2) for i, a in enumerate(ex1['aY'])]
            h1, w1 = check_hr_sum(rX, rY)
            # second instance l=3, Sn+ similar ordering
            aX = [1, 2, 4]; aY = [2, 3, 4]; bX = [1, 2, 3]
            assert A.weak_sub(aX, aY)
            rX2 = [burr_hazard(a, b, 3) for a, b in zip(aX, bX)]
            rY2 = [burr_hazard(aY[i], bX[i], 3) for i in range(3)]
            h2, w2 = check_hr_sum(rX2, rY2)
            ok = h1 and h2
            add(recd, "holds" if ok else "refuted", 2,
                f"{w1 or 'ok'}; {w2 or 'ok'}",
                note="Ex1 numbers + constructed l=3 instance; "
                     "alpha ~_w alpha* (top sums alpha <= alpha*).")

        elif c == "Theorem 6":
            # Harris severities; alpha ~^w alpha* (smallest sums a* >= a? or
            # a >= a*: superscript w = weak supermajorization).  Ex3:
            # lower partial sums of alpha >= alpha*'s.
            S0 = e ** (-x) * (1 + x)
            res = []
            for aX, aY, bX in [
                    (ex3['aX'], ex3['aY'], ex3['bX']),
                    ([A.R(3, 2), 2, 3], [1, 2, 3], [A.R(1, 5), A.R(2, 5), A.R(3, 5)])]:
                SX = [harris_S(a, b, S0) for a, b in zip(aX, bX)]
                SY = [harris_S(aY[i], bX[i], S0) for i in range(len(aX))]
                rX = [r_of(s) for s in SX]
                rY = [r_of(s) for s in SY]
                h, w = check_hr_sum(rX, rY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="Harris over Gamma(2,1); Ex3 numbers + constructed; "
                     "alpha ~^w alpha* in the printed weak-super sense "
                     "(smallest sums of alpha >= alpha*'s).")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.17713_ajs.v50i3.1025.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
