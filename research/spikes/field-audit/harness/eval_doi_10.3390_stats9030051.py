"""Evaluation of canonical claims for doi:10.3390/stats9030051 (GMOTL-G family).

GMOTL-G(delta, rho, omega) survival (paper Eq. (4)):
  S(t) = [ rho * A(t) / (1 - rho_bar * A(t)) ]^delta,
  A(t) = 1 - (1 - Gbar(t)^2)^omega,  rho_bar = 1 - rho.

Baseline G arbitrary -> we instantiate exponential Gbar = exp(-lam t)
and Weibull Gbar = exp(-t^2) baselines. Claim: rho1 < rho2 => T <=lr Y
(and hence hr, rh, st as consequences). rho > 1 is allowed
(Marshall-Olkin tilt), making rho_bar negative; covered in instances.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_gmotlg(delta, rho, omega, base):
    """base: Gbar expression in x."""
    A = 1 - (1 - base ** 2) ** R(omega)
    return (R(rho) * A / (1 - (1 - R(rho)) * A)) ** R(delta)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def theorem_1():
    """rho1 < rho2 => GMOTL-G(delta,rho1,omega) <=lr GMOTL-G(delta,rho2,omega)."""
    n, wit, und = 0, None, 0
    bases = [sp.exp(-x), sp.exp(-x ** 2)]
    cases = [
        # (delta, rho1, rho2, omega)
        (R(1), R(1, 2), R(2), R(1)),        # rho2 > 1
        (R(2), R(1, 3), R(1, 2), R(3, 2)),
        (R(1, 2), R(1), R(2), R(1, 3)),
        (R(3), R(1, 4), R(3, 4), R(2)),
        (R(1), R(3, 2), R(2), R(1)),        # both rho > 1
    ]
    for base in bases:
        for d, r1, r2, om in cases:
            T = Closed(S_gmotlg(d, r1, om, base))
            Y = Closed(S_gmotlg(d, r2, om, base))
            h, w, u = cf.check("lr", T, Y)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
            # consequences
            for order in ("hr", "rh", "st"):
                h, w, u = cf.check(order, T, Y)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_stats9030051.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if recd["claim"] == "Theorem 1":
            n_, w, u = theorem_1()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
        else:
            results.append(rec(recd, "out of harness scope"))
    out = os.path.join(HERE, "eval_doi_10.3390_stats9030051.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
