"""Evaluation of canonical claims for arxiv:2406.05834.

Every claim concerns systems whose components are coupled by Archimedean
(survival) copulas (AMH / Gumbel-Barnett / Gumbel-Hougaard) AND carry random
shocks.  Dependent components are out of harness scope per the evaluator spec
(the harness composes only independent survivals: series = product,
parallel = 1 - prod(1 - S)).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_2406.05834.json")))
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        results.append({
            "claim": rec["claim"], "order": order,
            "status": "out of harness scope",
            "instances": 0, "witness": None, "undecided_points": 0,
            "note": "Archimedean copula + random shocks (dependent "
                    "components)"})
    dest = os.path.join(HERE, "eval_arxiv_2406.05834.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
