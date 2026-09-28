"""Evaluate canonical claims of doi_10.19139/soic-2310-5070-863 (SSMSN/NMVM).

The family is defined by X|tau ~ SN_d(mu, a1(tau1) Sigma, a2(tau) alpha), a
scale-shape mixture of multivariate SKEW-NORMAL laws with arbitrary mixing
vector tau ~ H(.;eta).  Every marginal survival function requires the normal
cdf Phi (equivalently erf): the skew-normal law and its mixtures have no
closed form in the {+, x, Pow, exp, log} expression language implemented by
harness/closedform.py.  Hence no supported-order claim can be encoded without
loss of faithfulness: st records are 'out of harness scope'.

All other printed order types (concordance, cx, dcx, sm, uo, icx, integral)
are outside the supported order set and are marked 'unsupported order'.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.19139_soic-2310-5070-863.json")
OUT = os.path.join(HERE, "eval_doi_10.19139_soic-2310-5070-863.result.json")


def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        if order in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=r["claim"], order=order,
                            status="out of harness scope", instances=0,
                            witness=None, undecided_points=0,
                            note=("skew-normal (SN) margins need Phi/erf; "
                                  "harness language is {+,x,Pow,exp,log}")))
        else:
            out.append(dict(claim=r["claim"], order=order,
                            status="unsupported order", instances=0,
                            witness=None, undecided_points=0))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"])


if __name__ == "__main__":
    go()
