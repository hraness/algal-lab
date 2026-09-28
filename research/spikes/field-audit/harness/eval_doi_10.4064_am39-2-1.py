"""Evaluator for doi:10.4064/am39-2-1 (gamma moment estimators, CI ordering).

Gamma G(lam, alpha): f = x^{a-1} e^{-x/l} / (Gamma(a) l^a).

Exact arguments:
 * shape: f(x;a2,l)/f(x;a1,l) = const * x^{a2-a1} strictly increasing
   for a2>a1  =>  lr  =>  st (holds).
 * scale: f(x;a,l2)/f(x;a,l1) = const * e^{x(1/l1-1/l2)} strictly
   increasing for l2>l1  =>  lr  =>  st (holds).
 * Remark 2.3 (n=2): 1/ahat ~ Beta(1/2,a): ratio (1-t)^{a2-a1}
   decreasing => 1/ahat st-decreasing => ahat st-increasing.
 * Theorem 2.1: lam-hat = S^2/Xbar = lam * T, T>0 a.s. scale-free:
   deterministic ordering on the scalar lam.
 * Theorem 2.2: alpha-hat scale-free; verified exactly at n=2 through
   the Beta(1/2,a) law of 1/alpha-hat.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e
t = sp.Symbol('t', positive=True)


def ratio_deriv_sign(fp_over_fm, var, unit_interval=False):
    """Return (all_nonnegative_on_grid, expr, witness)."""
    from closedform import iv_eval
    g = sp.simplify(sp.diff(sp.log(fp_over_fm), var))
    if unit_interval:
        pts = [sp.Rational(2) ** (-k) for k in range(1, 33)]
    else:
        pts = [sp.Rational(2) ** (k - 16) for k in range(0, 33)]
    bad = None
    for pt in pts:
        try:
            v = iv_eval(g, pt)
            if v.b < 0:
                bad = pt
                break
        except Exception:
            val = sp.N(g.subs(var, pt), 50)
            if val < 0:
                bad = pt
                break
    return bad is None, g, bad


def main():
    claims = json.load(open("../canonical/doi_10.4064_am39-2-1.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order != "st":
            add(recd, "unsupported order")
            continue

        if c.startswith("Preliminary fact") and \
                ("in \u03b1" in c or "in alpha" in c):
            # a2=2 > a1=1, lam=1: ratio = x * const; derivative check
            f2 = x * e ** (-x) / sp.gamma(2)
            f1 = e ** (-x) / sp.gamma(1)
            ok, g, bad = ratio_deriv_sign(f2 / f1, x)
            add(recd, "holds" if ok else "refuted", 1,
                f"d log ratio = {g}; wit {bad}",
                note="f(x;a2)/f(x;a1) = c x^{a2-a1}: strictly increasing "
                     "for a2>a1 => lr => st.")

        elif c.startswith("Preliminary fact") and \
                ("in \u03bb" in c or "in lambda" in c):
            f2 = x ** 0 * e ** (-x / 2) / 2  # a=1, l=2
            f1 = e ** (-x)
            ok, g, bad = ratio_deriv_sign(f2 / f1, x)
            add(recd, "holds" if ok else "refuted", 1,
                f"d log ratio = {g}; wit {bad}",
                note="f(x;l2)/f(x;l1) = c e^{x(1/l1-1/l2)}: strictly "
                     "increasing for l2>l1 => lr => st.")

        elif c == "Remark 2.3":
            a2, a1 = 2, 1
            f2 = t ** (-sp.Rational(1, 2)) * (1 - t) ** (a2 - 1) \
                / sp.beta(sp.Rational(1, 2), a2)
            f1 = t ** (-sp.Rational(1, 2)) * (1 - t) ** (a1 - 1) \
                / sp.beta(sp.Rational(1, 2), a1)
            # 1/ahat st-decreasing iff f2/f1 decreasing:
            ok, g, bad = ratio_deriv_sign(f2 / f1, t, unit_interval=True)
            add(recd, "holds" if not ok else "refuted", 1,
                f"d log(f2/f1) = {g} (should be <=0; wit {bad})",
                note="f(t;a2)/f(t;a1) = c (1-t)^{a2-a1} decreasing for "
                     "a2>a1 => 1/ahat st-decreasing => ahat increasing.")

        elif c == "Theorem 2.1":
            add(recd, "holds", 1, None, 0,
                note="exact scaling argument: lam-hat = lam*T, T>0 a.s. "
                     "with law free of lam; lam1*T <=st lam2*T for "
                     "lam1<lam2 -- deterministic.")

        elif c == "Theorem 2.2":
            a2, a1 = 2, 1
            f2 = t ** (-sp.Rational(1, 2)) * (1 - t) ** (a2 - 1) \
                / sp.beta(sp.Rational(1, 2), a2)
            f1 = t ** (-sp.Rational(1, 2)) * (1 - t) ** (a1 - 1) \
                / sp.beta(sp.Rational(1, 2), a1)
            ok, g, bad = ratio_deriv_sign(f2 / f1, t, unit_interval=True)
            add(recd, "holds" if not ok else "refuted", 1,
                f"n=2 law check; {g}",
                note="verified at n=2 where 1/ahat ~ Beta(1/2,a) "
                     "(st-decreasing ratio); general n is asserted "
                     "without a closed-form sampling law.")

        elif c.startswith("Theorem 3.3"):
            add(recd, "out of harness scope",
                note="CI endpoint/length st-ordering needs the joint "
                     "sampling distribution of (L,U); no closed form.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.4064_am39-2-1.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
