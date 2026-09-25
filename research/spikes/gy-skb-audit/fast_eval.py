"""Fast exact-Fraction evaluators for the kernels (grid screening only).

All arithmetic is exact (Fraction); symbolic Sturm certification happens
only for flagged instances via audit_mphr.certify.
"""
from fractions import Fraction


def fr(x):
    if isinstance(x, Fraction):
        return x
    return Fraction(x.numerator, x.denominator) if hasattr(x, "numerator") else Fraction(x)


# ---- GY2024 kernel: Cker = [sum p_i a_i (1-(1-a_i)y)^-2]/[sum p_i a_i (1-(1-a_i)y)^-1]
def gy_Cker_val(p, a, v):
    v = fr(v)
    num = sum(fr(pi) * fr(ai) / (1 - (1 - fr(ai)) * v) ** 2 for pi, ai in zip(p, a))
    den = sum(fr(pi) * fr(ai) / (1 - (1 - fr(ai)) * v) for pi, ai in zip(p, a))
    return num / den


def gy_sf_val(p, a, v):
    v = fr(v)
    return sum(fr(pi) * fr(ai) * v / (1 - (1 - fr(ai)) * v) for pi, ai in zip(p, a))


# ---- SKB Aker = [sum p_i th_i^a (1-thb_i y)^(-a-1)]/[sum p_i th_i^a (1-thb_i y)^(-a)]
def skb_Aker_val(p, th, a, v):
    v = fr(v)
    num = den = Fraction(0)
    for pi, ti in zip(p, th):
        pi, ti = fr(pi), fr(ti)
        base = 1 - (1 - ti) * v
        num += pi * ti ** a * base ** (-a - 1)
        den += pi * ti ** a * base ** (-a)
    return num / den


# ---- SKB Bker = [sum p_i th_i (1-thb_i y)^(-a-1)]/[sum p_i (1-thb_i y)^(-a)]
def skb_Bker_val(p, th, a, v):
    v = fr(v)
    num = den = Fraction(0)
    for pi, ti in zip(p, th):
        pi, ti = fr(pi), fr(ti)
        base = 1 - (1 - ti) * v
        num += pi * ti * base ** (-a - 1)
        den += pi * base ** (-a)
    return num / den


# ---- SKB alpha-mixture SF inner sums
def skb_sf_inner_val(p, th, a, v):
    """sum p_i [th_i v/(1-(1-th_i)v)]^a -- integer a only."""
    v = fr(v)
    return sum(fr(pi) * (fr(ti) * v / (1 - (1 - fr(ti)) * v)) ** a
               for pi, ti in zip(p, th))


def skb_cdf_inner_val(p, th, a, v):
    """sum p_i [(1-v)/(1-(1-th_i)v)]^a."""
    v = fr(v)
    return sum(fr(pi) * ((1 - v) / (1 - (1 - fr(ti)) * v)) ** a
               for pi, ti in zip(p, th))


GRIDF = [Fraction(1, 16), Fraction(1, 8), Fraction(1, 5), Fraction(1, 4),
         Fraction(1, 3), Fraction(2, 5), Fraction(1, 2), Fraction(3, 5),
         Fraction(2, 3), Fraction(3, 4), Fraction(4, 5), Fraction(7, 8),
         Fraction(9, 10), Fraction(15, 16), Fraction(19, 20), Fraction(39, 40),
         Fraction(49, 50), Fraction(99, 100), Fraction(1, 100), Fraction(1, 1000)]
