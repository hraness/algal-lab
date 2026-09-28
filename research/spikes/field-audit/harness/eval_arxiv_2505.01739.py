"""Evaluation of canonical claims for arxiv:2505.01739.

Every claim concerns the (SD) property: stochastic ordering of weighted sums
sum_i theta_i X_i of iid random variables under majorization of the weight
vector.  The harness has no convolution operation on survivals (only series/
parallel/order-stat/mixture compositions), and the claims additionally carry
an unverifiable universal quantifier over all theta <=^m eta.  All records are
therefore out of harness scope.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_2505.01739.json")))
    results = []
    for rec in records:
        results.append({
            "claim": rec["claim"],
            "order": rec["conclusion"]["order"],
            "status": "out of harness scope",
            "instances": 0, "witness": None, "undecided_points": 0,
            "note": "weighted sums (convolutions) under a universal "
                    "majorization quantifier are not composable in the "
                    "harness"})
    dest = os.path.join(HERE, "eval_arxiv_2505.01739.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
