"""Evaluator for arXiv:1804.04103 (log-Lindley parallel systems with shocks).

LL(s, l): F(x) = x^s [1+s(l - log x)]/(1+ls), 0<x<1.  Shocked component
Xi = Ii Ti, Ii ~ Bernoulli(pi):  F_Xi(x) = 1 - p_i S_Ti(x), where
  S_Ti(x) = 1 - x^s + s x^s log x / (1 + l_i s).
Parallel system cdf: prod F_Xi.  The paper reparametrizes u_i = h(p_i)
(so p_i = h^{-1}(u_i)) and v_i = 1/(1+lam_i^s).

All claims are st on the max.  Domain (0,1).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def shocked_cdf(p, s, lam):
    return 1 - p * (1 - x ** A.R(s)
                    + A.R(s) * x ** A.R(s) * sp.log(x)
                    / (1 + A.R(lam) * A.R(s)))


def max_surv(params):
    """params: list of (p_i, sigma_i, lambda_i)."""
    return 1 - sp.prod([shocked_cdf(*q) for q in params])


def test(SX, SY):
    return A.check_dist("st", A.C(SX, 0, 1), A.C(SY, 0, 1))


def lam_from_v(v, s):
    """v = 1/(1+lam^s) -> lam = (1/v - 1)^{1/s}."""
    return (1 / A.R(v) - 1) ** (1 / A.R(s))


def main():
    claims = json.load(open("../canonical/arxiv_1804.04103.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c.startswith("Counterexample 3.1"):
            # positive illustration of Thm 3.3: sigma=0.5,
            # v=(0.4,0.4,0.1), v*=(0.5,0.4,0.2); h=-log u,
            # h(p)=(2,2,1), h(p*)=(3,2,1) -> p=e^{-u}
            s = A.R(1, 2)
            lamX = [lam_from_v(v, s) for v in (A.R(2, 5), A.R(2, 5), A.R(1, 10))]
            lamY = [lam_from_v(v, s) for v in (A.R(1, 2), A.R(2, 5), A.R(1, 5))]
            PX = [(e ** (-u), s, l) for u, l in zip((2, 2, 1), lamX)]
            PY = [(e ** (-u), s, l) for u, l in zip((3, 2, 1), lamY)]
            SX, SY = max_surv(PX), max_surv(PY)
            # claim X3:3 >=st Y3:3  <=>  Y <=st X
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="printed v, h(p) vectors; p=e^{-u}, lam=(1/v-1)^{2}.")

        elif c == "Counterexample 3.2":
            # shape-vector majorization fails to give st ordering:
            # case (a): sigma=(3,2,1), sigma*=(2,2,2), h(p)=(1,2,3)
            # case (b): sigma*=(2.6,2.4,1), h(p)=(0.03,0.02,0.01)
            # common lambda unspecified in canonical; lambda=1, h=-log u
            res = []
            for sX, sY, uX, uY in [
                    ([3, 2, 1], [2, 2, 2], [1, 2, 3], [1, 2, 3]),
                    ([3, 2, 1], [A.R(13, 5), A.R(12, 5), 1],
                     [1, 2, 3], [A.R(3, 100), A.R(1, 50), A.R(1, 100)])]:
                PX = [(e ** (-u), s, 1) for u, s in zip(uX, sX)]
                PY = [(e ** (-u), s, 1) for u, s in zip(uY, sY)]
                SX, SY = max_surv(PX), max_surv(PY)
                h1, w1, u1 = test(SX, SY)
                h2, w2, u2 = test(SY, SX)
                res.append(((not h1) or (not h2), w1, w2))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"fwd w={r[1]} rev w={r[2]}" for r in res),
                note="common lambda=1 assumed (canonical does not pin it); "
                     "h=-log u; checks that at least one st direction fails.")

        elif c == "Theorem 3.1":
            res = []
            # this paper's ~w (ii): smallest-j sums of h(p) <= h(p*)'s.
            # (i): h increasing convex -> h(u)=u; h(p)=(1,4) ~w (2,3):
            # 1<=2, 5<=5. lam in D+: (2,1).
            for uX, uY, lam in [([A.R(4, 5), A.R(1, 5)], [A.R(3, 4), A.R(1, 2)],
                                 [2, 1]),
                                ([A.R(9, 10), A.R(1, 2), A.R(1, 5)],
                                 [A.R(4, 5), A.R(3, 5), A.R(1, 2)], [3, 2, 1])]:
                # u in D+ descending, lam in D+; u ~w u* (smallest sums u<=u*)
                PX = [(A.R(u), A.R(1), l) for u, l in zip(uX, lam)]
                PY = [(A.R(u), A.R(1), l) for u, l in zip(uY, lam)]
                SX, SY = max_surv(PX), max_surv(PY)
                h, w, uu = test(SY, SX)   # claim X >=st Y
                res.append(("i", h, w))
            # (ii): h decreasing convex: h=-log u; lam in D+, h(p) in E+:
            # u=(1,4) asc, u*=(2,3) asc; smallest sums 1<=2,5<=5.
            uX, uY, lam = [1, 4], [2, 3], [2, 1]
            PX = [(e ** (-u), A.R(1), l) for u, l in zip(uX, lam)]
            PY = [(e ** (-u), A.R(1), l) for u, l in zip(uY, lam)]
            SX, SY = max_surv(PX), max_surv(PY)
            h, w, uu = test(SY, SX)
            res.append(("ii", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res))

        elif c == "Theorem 3.2":
            # v ~w v*: smallest-j sums of v <= v*'s; sigma common=1
            res = []
            for vX, vY in [([A.R(2, 5), A.R(2, 5), A.R(1, 10)],
                            [A.R(1, 2), A.R(2, 5), A.R(1, 5)]),
                           ([A.R(2, 5), A.R(9, 10), A.R(1, 10)],
                            [A.R(1, 2), A.R(3, 5), A.R(1, 2)])]:
                # verify: smallest-j sums of vX <= vY
                ax, ay = A.asc(vX), A.asc(vY)
                assert all(sum(ax[:j]) <= sum(ay[:j])
                           for j in range(1, len(ax) + 1))
                lamX = [lam_from_v(v, 1) for v in vX]
                lamY = [lam_from_v(v, 1) for v in vY]
                PX = [(A.R(1, 2), 1, l) for l in lamX]
                PY = [(A.R(1, 2), 1, l) for l in lamY]
                SX, SY = max_surv(PX), max_surv(PY)
                h, w, uu = test(SY, SX)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="v ~^w v* per printed weak-majorization; common sigma=1, "
                     "common shocks p=1/2.")

        elif c == "Theorem 3.3":
            # matrix weak majorization, h=-log u
            s = A.R(1, 2)
            lamX = [lam_from_v(v, s) for v in (A.R(2, 5), A.R(2, 5), A.R(1, 10))]
            lamY = [lam_from_v(v, s) for v in (A.R(1, 2), A.R(2, 5), A.R(1, 5))]
            PX = [(e ** (-u), s, l) for u, l in zip((2, 2, 1), lamX)]
            PY = [(e ** (-u), s, l) for u, l in zip((3, 2, 1), lamY)]
            SX, SY = max_surv(PX), max_surv(PY)
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u)

        elif c == "Theorem 3.4":
            # strict/chain matrix majorization: same instance as 3.3
            s = A.R(1, 2)
            lamX = [lam_from_v(v, s) for v in (A.R(2, 5), A.R(2, 5), A.R(1, 10))]
            lamY = [lam_from_v(v, s) for v in (A.R(1, 2), A.R(2, 5), A.R(1, 5))]
            PX = [(e ** (-u), s, l) for u, l in zip((2, 2, 1), lamX)]
            PY = [(e ** (-u), s, l) for u, l in zip((3, 2, 1), lamY)]
            SX, SY = max_surv(PX), max_surv(PY)
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="same instance as Counterexample 3.1 satisfies the "
                     "matrix-majorization hypothesis.")

        elif c == "Theorem 3.5":
            # heterogeneous shape, common lambda; h=-log u
            res = []
            # ii): sigma in D+, h(p) in E+, h decreasing
            for sX, uX, uY, lam in [([3, 2, 1], [1, 2, 3], [1, 2, 4], [1, 1, 1]),
                                    ([4, 3, 2], [1, 3, 5], [2, 3, 5], [2, 2, 2])]:
                PX = [(e ** (-u), s, l) for u, s, l in zip(uX, sX, lam)]
                PY = [(e ** (-u), s, l) for u, s, l in zip(uY, sX, lam)]
                SX, SY = max_surv(PX), max_surv(PY)
                h, w, uu = test(SY, SX)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="case ii: sigma desc, h(p) asc, h=-log u, common lambda.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_1804.04103.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
