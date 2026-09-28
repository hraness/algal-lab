"""Evaluation of canonical claims for doi:10.3390/sym15091796.

Sample range R(X,n) = X_{n:n} - X_{1:n} of independent Exp(theta_i).
Range cdf (argmin decomposition + memorylessness):
  P(R <= t) = (1/S) * sum_j theta_j prod_{i!=j} (1 - exp(-theta_i t)),
  S = sum theta_i.

Theorem 2: eta in Theta_n(theta): theta >=^p eta (p-majorization: partial
products of ascending order stats, equality of total product) and
theta_k >= eta_k for k = 2..n  =>  R(X,n) >=st R(Y,n).

Theorem 3: eta in Omega_n(theta): theta >=^w eta (weak: partial sums of
ascending order stats, all i) and theta_k >= eta_k for k = 2..n
=> R(X,n) >=rh R(Y,n).

Theorem 1 (mrl, MOE common-shock parallel systems): unsupported order.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_range(rates):
    """Survival of max-min for independent exponentials with given rates."""
    rates = [R(r) for r in rates]
    total = sum(rates)
    s = sp.Integer(0)
    for j, rj in enumerate(rates):
        prod = sp.Integer(1)
        for i, ri in enumerate(rates):
            if i != j:
                prod *= (1 - sp.exp(-ri * x))
        s += rj * prod
    return 1 - s / total


def sorted_asc(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1))


def p_majorized(th, et):
    """theta >=^p eta: partial products (ascending) theta <= eta, i<n; total =."""
    n = len(th)
    assert sorted_asc(th) and sorted_asc(et)
    for i in range(1, n):
        if sp.prod(th[:i]) > sp.prod(et[:i]):
            return False
    return sp.prod(th) == sp.prod(et)


def w_majorized(th, et):
    """theta >=^w eta: partial sums (ascending) theta <= eta, all i."""
    n = len(th)
    assert sorted_asc(th) and sorted_asc(et)
    return all(sum(th[:i]) <= sum(et[:i]) for i in range(1, n + 1))


def tail_dominated(th, et):
    return all(th[k] >= et[k] for k in range(1, len(th)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.3390_sym15091796.json")))
    # instances satisfying the respective hypothesis sets
    p_pairs = [   # (theta, eta) with theta >=^p eta, theta_k >= eta_k k>=2
        ([R(1), R(3), R(6)], [R(2), R(3), R(3)]),
        ([R(1), R(2), R(9)], [R(3, 2), R(2), R(6)]),
        ([R(1), R(2), R(8)], [R(2), R(2), R(4)]),
        ([R(1, 2), R(2), R(8)], [R(1), R(2), R(4)]),
        ([R(2), R(3), R(5)], [R(2), R(3), R(5)]),      # equality edge
    ]
    w_pairs = [   # (theta, eta) with theta >=^w eta, theta_k >= eta_k k>=2
        ([R(1), R(3), R(6)], [R(2), R(3), R(5)]),
        ([R(1), R(3), R(6)], [R(2), R(2), R(6)]),
        ([R(1), R(2), R(9)], [R(2), R(2), R(8)]),
        ([R(1), R(2), R(4)], [R(2), R(2), R(3)]),
        ([R(1), R(2), R(3)], [R(2), R(2), R(3)]),
    ]
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        out = {"claim": rec["claim"], "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order == "mrl":
            out["status"] = "unsupported order"
            results.append(out)
            continue
        pairs = p_pairs if order == "st" else w_pairs
        check_rel = p_majorized if order == "st" else w_majorized
        n, wit, und = 0, None, 0
        for th, et in pairs:
            assert check_rel(th, et) and tail_dominated(th, et), (th, et)
            RX = Closed(S_range(th))
            RY = Closed(S_range(et))
            # conclusion R(X) >=order R(Y)  <=>  RY <=order RX
            h, w, u = cf.check(order, RY, RX)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit),
                   status="holds" if wit is None else "refuted")
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.3390_sym15091796.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
