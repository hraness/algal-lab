"""Evaluator for doi:10.29252/jss.12.2.395 (thinned portfolio sums).

Aggregate S = sum_i I_{p_i} X_{lam_i}, I Bernoulli, X Exp(lam).
For n=2 the aggregate survival on x>0 is
  S_agg(x) = p1(1-p2) S_{l1}(x) + (1-p1) p2 S_{l2}(x)
             + p1 p2 S_{l1*l2}(x)
with S_{l1*l2} = (l2 e^{-l1 x} - l1 e^{-l2 x})/(l2 - l1) (hypoexponential),
exact in z = e^{-x} for rational l.  The same mixture applies to any
component survival family -- for PRHR (S=1-(1-e^{-x})^l) the two-point
survivals are exact in z but the convolution is numerical (mpmath quad).

h(p) = (1-p)/p is used for the h-transform of coverage probabilities.
Majorization of matrices is encoded via a doubly-stochastic T-transform
instance (chain majorization) per the paper's Un-cone definition.
"""
import json
import auditlib as A
import sympy as sp
from mpmath import mp, quad, findroot

x = A.x
e = A.e
mp.dps = 60


def exp_surv(l):
    return e ** (-A.R(l) * x)


def conv_exp_surv(l1, l2):
    l1, l2 = A.R(l1), A.R(l2)
    if l1 == l2:
        return (1 + l1 * x) * e ** (-l1 * x)
    return (l2 * e ** (-l1 * x) - l1 * e ** (-l2 * x)) / (l2 - l1)


def agg_exp(pairs):
    """pairs = [(p_i, lam_i), ...] for n=2."""
    (p1, l1), (p2, l2) = [(A.R(p), A.R(l)) for p, l in pairs]
    return (p1 * (1 - p2) * exp_surv(l1)
            + (1 - p1) * p2 * exp_surv(l2)
            + p1 * p2 * conv_exp_surv(l1, l2))


def prhr_S(l, t_):
    return 1 - (1 - mp.e ** (-t_)) ** l


def prhr_f(l, t_):
    return l * mp.e ** (-t_) * (1 - mp.e ** (-t_)) ** (l - 1)


def conv_prhr_S(l1, l2, xx):
    """S_{X1+X2}(x) numerically: 1 - F1*F2 cdf at xx."""
    if xx <= 0:
        return mp.mpf(1)
    F = lambda t: 1 - prhr_S(l1, t)
    Fc = quad(lambda t: F(xx - t) * prhr_f(l2, t), [0, xx])
    return 1 - Fc


def agg_prhr(pairs, xx):
    (p1, l1), (p2, l2) = pairs
    return (p1 * (1 - p2) * prhr_S(l1, xx)
            + (1 - p1) * p2 * prhr_S(l2, xx)
            + p1 * p2 * conv_prhr_S(l1, l2, xx))


def test(SA, SB):
    return A.check_dist("st", A.C(SA), A.C(SB))


def main():
    claims = json.load(open("../canonical/doi_10.29252_jss.12.2.395.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order != "st":
            add(recd, "unsupported order")
            continue

        if c.startswith("Theorem 2"):
            # lam desc (3,1); p=(1/3,1/2) asc->p_(1)=1/3 pairs lam_(2)=1,
            # p_(2)=1/2 pairs lam_(1)=3; q=(2/5,2/5).
            # h(u)=(1-u)/u: h(p_asc)=(2,1), h(q)=(3/2,3/2): tops 2>=1.5,3=3.
            PX = [(A.R(1, 3), 1), (A.R(1, 2), 3)]
            PY = [(A.R(2, 5), 1), (A.R(2, 5), 3)]
            SX, SY = agg_exp(PX), agg_exp(PY)
            # claim: p-portfolio >=st q-portfolio (conclusion 'the
            # p-portfolio aggregate stochastically larger')
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="h=(1-p)/p; h(p_(i))=(2,1) majorizes h(q)=(3/2,3/2). "
                     "E = S_p - S_q = -19e^{-x}/300 + 9e^{-3x}/100 "
                     "crosses at x~0.5: E<0 on (0.5,inf), witness "
                     "x=1 (E=-0.0188): printed direction fails.")

        elif c.startswith("Theorem 3"):
            # lam=(3,1) ~m mu=(2,2); same p=(1/2,1/2); mu-side >=st lam-side
            PX = [(A.R(1, 2), 2), (A.R(1, 2), 2)]
            PY = [(A.R(1, 2), 3), (A.R(1, 2), 1)]
            SX, SY = agg_exp(PX), agg_exp(PY)
            h, w, u = test(SY, SX)   # X(mu) >=st Y(lam)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="mu=(2,2) vs lam=(3,1), equal p=1/2: E = S_mu-S_lam < 0 "
                     "throughout (e.g. -0.067 at x=1): the MORE spread "
                     "lam vector gives the stochastically larger thinned "
                     "sum -- printed direction fails.")

        elif c.startswith("Theorem 4"):
            # augmented matrices in Un: A = [[3,1],[-1,-2]] vs
            # B = A*D, D=[[3/4,1/4],[1/4,3/4]] -> [[5/2,3/2],[-5/4,-7/4]]
            # pairs: (lam_i, -h_i); X: (3,-1),(1,-2); Y: (5/2,-5/4),(3/2,-7/4)
            # p: h=1,2 -> p=(1/2,1/3); q: h=5/4,7/4 -> q=(4/9,4/11).
            # claim: Sigma I_q X_mu >=st Sigma I_p X_lam
            PX = [(A.R(1, 2), 3), (A.R(1, 3), 1)]
            PY = [(A.R(4, 9), A.R(5, 2)), (A.R(4, 11), A.R(3, 2))]
            SX, SY = agg_exp(PX), agg_exp(PY)
            h, w, u = test(SX, SY)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="B=A*D with D=[[3/4,1/4],[1/4,3/4]] (matrix "
                     "majorization); E=S_qmu-S_plam < 0 at x->0+ since "
                     "p1+p2-p1p2=2/3 > 0.6465=q-sum: claim fails at "
                     "origin and interior.")

        elif c.startswith("Theorem 5"):
            # PRHR family; same augmented matrices, numerical convolution
            PX = [(mp.mpf(1) / 2, mp.mpf(3)), (mp.mpf(1) / 3, mp.mpf(1))]
            PY = [(mp.mpf(4) / 9, mp.mpf(5) / 2),
                  (mp.mpf(4) / 11, mp.mpf(3) / 2)]
            # claim: (mu,q)-side >=st (lam,p)-side, i.e. SY-SX >= 0
            viol = []
            for xx in [mp.mpf(k) / 10 for k in range(1, 60)] + \
                      [mp.mpf(k) for k in range(6, 16)]:
                d = agg_prhr(PY, xx) - agg_prhr(PX, xx)
                if d < -mp.mpf('1e-8'):
                    viol.append((xx, d))
            ok = not viol
            add(recd, "holds" if ok else "refuted", 1,
                f"grid min {'none' if ok else viol[:2]}",
                note="PRHR S=1-(1-e^{-x})^l; convolution by mpmath quad; "
                     "S_qmu-S_plam < 0 on x=0.1..15 grid (min ~-0.011): "
                     "printed direction fails (same cause: coverage sum "
                     "of the q side is smaller).")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.29252_jss.12.2.395.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
