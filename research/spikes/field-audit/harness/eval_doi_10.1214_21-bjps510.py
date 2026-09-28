"""Evaluate canonical claims of doi_10.1214/21-BJPS510 (shifted orders).

All 17 records concern SHIFTED stochastic orders (lr-up/down, hr-up/down,
rh-up/down): X <=_{ord up/down} Y defined through shifts x+D vs x.  These
orders are outside the supported set {st, hr, rh, lr} -- a shift-order
assertion is not equivalent to any unshifted supported order -- so every
record is 'unsupported order'.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1214_21-bjps510.json")
OUT = os.path.join(HERE, "eval_doi_10.1214_21-bjps510.result.json")


def go():
    recs = json.load(open(CANON))
    out = [dict(claim=r["claim"], order=(r.get("conclusion") or {}).get("order"),
                status="unsupported order", instances=0, witness=None,
                undecided_points=0,
                note="shifted order (lr/hr/rh up or down), not in {st,hr,rh,lr}")
           for r in recs]
    json.dump(out, open(OUT, "w"), indent=1)
    print(len(out), "records -> unsupported order")


if __name__ == "__main__":
    go()
