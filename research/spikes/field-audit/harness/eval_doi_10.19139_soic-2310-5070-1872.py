"""Evaluation of canonical claims for doi:10.19139/soic-2310-5070-1872
(TL-TIIEHL-MO-G family).

CDF (paper Eq. 7): with M(x) = delta*Gbar/(1 - delta_bar*Gbar) (MO-G survival),
  F(x; b, alpha, delta) = [1 - (M/(2 - M))^{2 alpha}]^b.
Baseline G arbitrary -> instantiated with exponential and Weibull Gbar.

Claim: b1 < b2 => (printed) X2 <lr X1 and X1 <st X2.
The printed lr direction is adjudicated as transposed: decreasing f1/f2
means X1 <=lr X2 under the paper's definition. We test the printed
directions; for the lr records the mathematically indicated direction
X1 <=lr X2 is also checked, and the printed-direction test result is
what is reported.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_family(b, alpha, delta, base):
    """base: Gbar(x) expression; S = 1 - F."""
    M = R(delta) * base / (1 - (1 - R(delta)) * base)
    h = (M / (2 - M)) ** (2 * R(alpha))
    return 1 - (1 - h) ** R(b)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


BASES = [sp.exp(-x), sp.exp(-x ** 2)]
CASES = [  # (b1, b2, alpha, delta), b1 < b2
    (R(1), R(2), R(1), R(1)),
    (R(1, 2), R(1), R(2), R(1, 3)),
    (R(2), R(3), R(1, 2), R(2)),
    (R(1), R(3, 2), R(3), R(3, 2)),
]


def run_lr_printed():
    """Printed: X2 <=lr X1 (expected to fail; direction transposed)."""
    n, wit, und = 0, None, 0
    for base in BASES:
        for b1, b2, a, d in CASES:
            X1 = Closed(S_family(b1, a, d, base))
            X2 = Closed(S_family(b2, a, d, base))
            h, w, u = cf.check("lr", X2, X1)     # decide X2 <=lr X1
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def run_lr_corrected():
    """Corrected direction: X1 <=lr X2."""
    n, wit, und = 0, None, 0
    for base in BASES:
        for b1, b2, a, d in CASES:
            X1 = Closed(S_family(b1, a, d, base))
            X2 = Closed(S_family(b2, a, d, base))
            h, w, u = cf.check("lr", X1, X2)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def run_st():
    """Printed: X1 <=st X2."""
    n, wit, und = 0, None, 0
    for base in BASES:
        for b1, b2, a, d in CASES:
            X1 = Closed(S_family(b1, a, d, base))
            X2 = Closed(S_family(b2, a, d, base))
            h, w, u = cf.check("st", X1, X2)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.19139_soic-2310-5070-1872.json")))
    results = []
    lr_done = None
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if "lr" in label and order == "lr":
            if lr_done is None:
                lr_done = run_lr_printed()
                # sanity: corrected direction should hold
                n2, w2, _ = run_lr_corrected()
                print("corrected-direction X1<=lr X2 check:", "holds" if w2 is None else ("refuted at " + str(w2)), "n =", n2)
            n_, w, u = lr_done
        elif "st" in label and order == "st":
            n_, w, u = run_st()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.19139_soic-2310-5070-1872.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
