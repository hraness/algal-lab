"""Evaluation of canonical claims for doi:10.1080/03610926.2023.2165407
(GLSE / GHSS portfolios).

All st-ordered records concern GLSE_1 / GHSS random variables
(Y = mu + beta(Z) delta + sigma Z with beta arbitrary): the densities are
not in the supported expression class (they generally involve Bessel /
hyperbolic functions), and the multivariate records are coupled vectors ->
out of harness scope.  icx/cx/dcx/ccx/uo/sm/cp/cop orders -> unsupported.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1080_03610926.2023.2165407.json")))
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        label = rec["claim"]
        if order in ("st", "hr", "rh", "lr"):
            status = "out of harness scope"
            note = ("GLSE/GHSS densities not encodable in the supported "
                    "expression class")
        else:
            status = "unsupported order"
            note = "order %s" % order[:30]
        results.append({"claim": label, "order": order, "status": status,
                        "instances": 0, "witness": None,
                        "undecided_points": 0, "note": note})
    dest = os.path.join(HERE,
                        "eval_doi_10.1080_03610926.2023.2165407.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
