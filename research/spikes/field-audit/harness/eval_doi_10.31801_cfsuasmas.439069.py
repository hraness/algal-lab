"""Evaluator for doi:10.31801/cfsuasmas.439069 (NLCH-G family).

Lemma 2.6: (i) if lambda > 1 then X_F <=hr X_G; (ii) if lambda < 1 then
X_G <=hr X_F.  Model: R(x; lam, theta) = exp(-(lam + H(x))^theta), parent G with
cumulative hazard H.

The OCR-dropped shape condition makes the hypotheses ambiguous: a lambda-inequality
alone does not determine the hr ordering for arbitrary theta.  Under the coherent
reading (theta <= 1 for part (i); theta >= 1 for part (ii)) the conclusions are
testable; under a literal reading with theta unrestricted they fail.  We report
ambiguous hypotheses and record the bounded-test outcomes for both readings.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
E = A.e


def nlch_surv(lam, theta, H):
    return E ** (-(lam + H) ** theta)


def run(order, lam, theta, H, which="i"):
    """which='i': X_F <=hr X_G ; 'ii': X_G <=hr X_F."""
    XF = A.C(nlch_surv(A.R(lam), A.R(theta), H))
    XG = A.C(E ** (-H))
    if which == "i":
        return A.check_dist("hr", XF, XG)
    return A.check_dist("hr", XG, XF)


def main():
    claims = json.load(open("../canonical/doi_10.31801_cfsuasmas.439069.json"))
    out = []
    H_exp = x                      # baseline G = Exp(1): H(x) = x
    for recd in claims:
        order = recd["conclusion"]["order"]
        which = "i" if "part (i)" in recd["claim"] else "ii"
        # coherent reading: (i) theta<=1, lam>1 ; (ii) theta>=1, lam<1
        coh = []
        wit_coh = None
        und_coh = 0
        if which == "i":
            insts = [(A.R(2), A.R(1, 2)), (A.R(3, 2), A.R(1, 3)), (A.R(2), A.R(1))]
        else:
            insts = [(A.R(1, 2), A.R(2)), (A.R(1, 4), A.R(3)), (A.R(1, 2), A.R(3, 2))]
        for lam, th in insts:
            h, w, u = run(order, lam, th, H_exp, which)
            coh.append(h)
            und_coh += u
            if not h and wit_coh is None:
                wit_coh = w
        # literal reading (theta unrestricted): check opposite-theta instances
        if which == "i":
            lit = [(A.R(2), A.R(2))]       # lam>1, theta>1
        else:
            lit = [(A.R(1, 2), A.R(1, 2))]  # lam<1, theta<1
        lit_bad = []
        for lam, th in lit:
            h, w, u = run(order, lam, th, H_exp, which)
            if not h:
                lit_bad.append(str(w))
        note = ("OCR-dropped parameter condition; under reading "
                + ("theta<=1" if which == "i" else "theta>=1")
                + f" the printed conclusion survived bounded testing ({len(coh)} instances, "
                + f"all holds={all(coh)}); under the opposite-theta reading it fails"
                + (f" (e.g. witness {lit_bad[0]})" if lit_bad else ""))
        out.append(A.rec(recd, "ambiguous hypotheses", instances=len(coh),
                         witness=None, undecided=und_coh, note=note))
    A.emit("eval_doi_10.31801_cfsuasmas.439069.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
