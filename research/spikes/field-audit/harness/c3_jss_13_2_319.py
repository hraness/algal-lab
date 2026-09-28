"""Independent C3 for doi:10.29252/jss.13.2.319 (GLFR parallel systems).

Refutes Example 1 / Theorem 7 (same instance) and the constructed
instances of Theorems 5 and 6: the claimed X_{n:n} >=st Y_{n:n} fails
throughout the interior.  GLFR F_i(x) = (1 - e^{-(a x + b x^2/2)})^l;
parallel-maximum cdf F = prod F_i.  E = F_Y - F_X must be >= 0 for the
printed claim; it is strictly negative at interior points.

Verified independently with mpmath interval arithmetic.
"""
from mpmath import iv, mpf, nstr

iv.dps = 80


def F_i(a, b, l, x):
    return (1 - iv.exp(-(a * x + b * x ** 2 / 2))) ** l


def Fmax(params, x):
    f = iv.mpf(1)
    for p in params:
        f *= F_i(*p, x)
    return f


def report(tag, PX, PY):
    E = lambda x: Fmax(PY, x) - Fmax(PX, x)
    print(tag)
    for t in ["0.1", "0.25", "0.5", "1", "2"]:
        d = E(iv.mpf(t))
        flag = "NEGATIVE (refutes)" if d.b < 0 else (
            "positive" if d.a > 0 else "undecided")
        print(f"  x={t:>5}: F_Y - F_X in [{nstr(d.a,6)},{nstr(d.b,6)}] {flag}")


# Example 1 / Theorem 7: X: alpha=(2,3,4) lam=(1,2,3); Y: nu=(1,2,5),
# gamma=(2,5/2,3/2); common beta=1.  Claim X_{3:3} >=st Y_{3:3}.
report("Ex1/Thm7", [(2, 1, 1), (3, 1, 2), (4, 1, 3)],
       [(1, 1, 2), (2, 1, mpf(5) / 2), (5, 1, mpf(3) / 2)])

# Thm 5 instance: alpha=(4,3,1) ~m nu=(3,3,2) on D+;
# lam=(1,3) ~m gamma=(3/2,5/2) on E+; common beta=1.
report("Thm5", [(4, 1, 1), (3, 1, 3)],
       [(3, 1, mpf(3) / 2), (3, 1, mpf(5) / 2)])

# Thm 6 instance: beta=(5,3,1) ~m mu=(4,3,2) on D+;
# lam=(1,3) ~m gamma=(3/2,5/2) on E+; common alpha=1.
report("Thm6", [(1, 5, 1), (1, 3, 3)],
       [(1, 4, mpf(3) / 2), (1, 3, mpf(5) / 2)])
