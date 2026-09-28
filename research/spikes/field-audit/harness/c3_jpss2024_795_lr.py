"""Independent C3 check of the refutation in eval_doi_10.37119_jpss2024.v22i1.795.

Claim: eta < psi and beta < delta => MGGD(eta,beta) <=lr MGGD(psi,delta).
Refuting instance: (eta,beta,psi,delta) = (1/2,1/2,1,1), witness x = 1/10.
Hypotheses hold: 1/2 < 1 and 1/2 < 1.

Independent method: evaluate d/dx log(f_Y/f_X) directly at the witness with
high-precision interval arithmetic on a fresh encoding. lr order X<=lr Y
needs d/dx(f_Y/f_X) >= 0, equivalently f_Y' f_X - f_Y f_X' >= 0.
Also prints the raw density-ratio slope in plain mp (not iv) arithmetic.
"""
import sympy as sp
from mpmath import iv, mp, mpf

mp.dps = 80
iv.dps = 80

t = sp.Symbol("t", positive=True)


def S(e, b):
    e, b = sp.Rational(e), sp.Rational(b)
    gomp = sp.exp(-(e / b) * (sp.exp(b * t) - 1))
    gam = b * (1 + e * t + (e * t) ** 2 / 2) * sp.exp(-e * t)
    return (gomp + gam) / (1 + b)


eta, beta, psi, delta = sp.Rational(1, 2), sp.Rational(1, 2), sp.Rational(1), sp.Rational(1)
assert eta < psi and beta < delta, "printed hypotheses"

SX, SY = S(eta, beta), S(psi, delta)
fX, fY = -sp.diff(SX, t), -sp.diff(SY, t)
E = sp.diff(fY, t) * fX - fY * sp.diff(fX, t)   # sign of d/dx(f_Y/f_X) * f_X^2

# interval evaluation at the witness, independent hand-rolled tree walk
x0 = sp.Rational(1, 10)


def ie(expr):
    if expr == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if expr.is_Rational:
        return iv.mpf(int(expr.p)) / iv.mpf(int(expr.q))
    if expr.is_Add:
        s = iv.mpf(0)
        for a in expr.args:
            s += ie(a)
        return s
    if expr.is_Mul:
        p = iv.mpf(1)
        for a in expr.args:
            p *= ie(a)
        return p
    if expr.is_Pow:
        b_, e_ = expr.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_) * iv.log(ie(b_)))
    if isinstance(expr, sp.exp):
        return iv.exp(ie(expr.args[0]))
    raise ValueError(type(expr))


v = ie(E)
print("iv enclosure of E at x=1/10:", v)
assert v.b < 0, "expected strictly negative enclosure"
print("REFUTATION CONFIRMED: E < 0 at x = 1/10 under eta<psi, beta<delta")

# second, plain-mp sanity: numerical derivative of log(f_Y/f_X) near witness
fXl = sp.lambdify(t, sp.log(fX), "mpmath")
fYl = sp.lambdify(t, sp.log(fY), "mpmath")
eps = mpf(10) ** -20
slope = ((fYl(mpf("0.1") + eps) - fXl(mpf("0.1") + eps))
         - (fYl(mpf("0.1")) - fXl(mpf("0.1")))) / eps
print("d/dx log(fY/fX) at 0.1 (mp):", slope)
assert slope < 0
