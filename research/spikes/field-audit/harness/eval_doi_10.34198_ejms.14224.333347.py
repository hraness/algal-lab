"""Evaluation of canonical claims for doi:10.34198/ejms.14224.333347
(Remkan distribution properties).

The paper's math layer is entirely unmapped glyphs in every available text
rendering: the Remkan density's parameters and the hypotheses of Theorem 5
(which parameter relations are assumed between X and Y) are unreadable, as
adjudicated in the canonical records.  No concrete instance can be certified
to satisfy the printed hypotheses, so the lr/hr/st parts are recorded as
'ambiguous hypotheses'; the mrl part is an unsupported order.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.34198_ejms.14224.333347.json")))
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        status = ("unsupported order" if order not in ("st", "hr", "rh", "lr")
                  else "ambiguous hypotheses")
        results.append({
            "claim": rec["claim"], "order": order, "status": status,
            "instances": 0, "witness": None, "undecided_points": 0,
            "note": "parameter symbols and hypothesis relations unreadable "
                    "in the extracted text ([?] glyphs)"})
    dest = os.path.join(HERE, "eval_doi_10.34198_ejms.14224.333347.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
