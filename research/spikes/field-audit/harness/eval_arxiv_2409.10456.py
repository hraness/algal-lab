"""Evaluate canonical claims of arxiv_2409.10456 (MRLAI-type ageing classes).

Every record except Counterexample 4.5 is about MRLAI/DMRLAI/IMRLAI class
membership or the vrl order -- none are in {st,hr,rh,lr} -> unsupported.
Counterexample 4.5 contains a verifiable lr premise: X ~ Erlang(2,3),
Y ~ Erlang(2,2) with X <=lr Y (and hence X does NOT dominate Y in MRLAI).
The printed direction X <=lr Y is tested: survival of Erlang(2,mu) is
S(t) = e^{-mu t} (1 + mu t).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2409.10456.json")
OUT = os.path.join(HERE, "eval_arxiv_2409.10456.result.json")


def erlang2(mu):
    return sp.exp(-mu * x) * (1 + mu * x)


def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        if order != "lr":
            out.append(dict(claim=r["claim"], order=order,
                            status="unsupported order", instances=0,
                            witness=None, undecided_points=0))
            continue
        # Counterexample 4.5: printed X <=lr Y holds (f_Y/f_X ~ e^t incr).
        X = Closed(erlang2(sp.Rational(3)))
        Y = Closed(erlang2(sp.Rational(2)))
        ok, w, u = cf.check("lr", X, Y)
        out.append(dict(claim=r["claim"], order=order,
                        status="holds" if ok else "refuted",
                        instances=1, witness=str(w), undecided_points=u,
                        note=("record asserts X<=lr Y (verified) plus "
                              "MRLAI non-implication (MRLAI unsupported)")))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"])


if __name__ == "__main__":
    go()
