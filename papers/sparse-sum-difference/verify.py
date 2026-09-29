"""Exact certificates for the manuscript; Python 3.10+, standard library only."""

from fractions import Fraction
from math import gcd
import json


CASES = (
    ("simple-rational-control", tuple([0, *range(2, 12)]), 3, 4, 59, 50),
    ("theta-above-1.1813", tuple([0, *range(2, 12)]), 377, 500, 11813, 10000),
    ("theta-above-1.1855", tuple([0, 3, 4, *range(6, 17)]), 16, 19, 2371, 2000),
)


def totals(alphabet, numerator, denominator):
    """Return integer maxima with common denominator h**(2*B).

    Here h is the denominator after reducing numerator/denominator.
    """
    if (type(alphabet) is not tuple or not 2 <= len(alphabet) <= 65
            or any(type(a) is not int or not 0 <= a <= 64 for a in alphabet)
            or alphabet != tuple(sorted(set(alphabet))) or alphabet[0] != 0):
        raise ValueError("expected distinct sorted digits in 0..64, including 0")
    if (type(numerator) is not int or type(denominator) is not int
            or not 0 < numerator < denominator <= 10**6):
        raise ValueError("expected 0 < numerator < denominator <= 10**6")
    q = Fraction(numerator, denominator)
    p, h, b = q.numerator, q.denominator, alphabet[-1]
    weights = {a: p**a * h**(b-a) for a in alphabet}
    sums, differences = {}, {}
    for a, wa in weights.items():
        for c, wc in weights.items():
            product = wa * wc
            sums[a+c] = max(sums.get(a+c, 0), product)
            differences[a-c] = max(differences.get(a-c, 0), product)
    return sums, differences, h**(2*b)


def verify_case(name, alphabet, p, h, bound_numerator, bound_denominator):
    if (type(bound_numerator) is not int or type(bound_denominator) is not int
            or not 1 <= bound_denominator <= 10000
            or not bound_denominator < bound_numerator <= 2*bound_denominator):
        raise ValueError("expected a threshold in (1,2] with denominator <= 10000")
    sums, differences, common_denominator = totals(alphabet, p, h)
    b, base = alphabet[-1], 2*alphabet[-1]+1
    ns, nd = sum(sums.values()), sum(differences.values())

    # Check every claimed coefficient of the displayed one-omitted-digit formula.
    if alphabet == tuple([0, *range(2, b+1)]) and b >= 3:
        q = Fraction(p, h)
        term = lambda j: q.numerator**j * q.denominator**(2*b-j)
        expected_sums = {j: term(j) for j in range(2*b+1) if j != 1}
        expected_differences = {
            d: term(5 if abs(d) == 1 else abs(d)) for d in range(-b, b+1)
        }
        if sums != expected_sums or differences != expected_differences:
            raise ValueError("pair maxima disagree with the polynomial formulas")

    if alphabet == tuple([0, 3, 4, *range(6, b+1)]) and b >= 8:
        q = Fraction(p, h)
        term = lambda j: q.numerator**j * q.denominator**(2*b-j)
        expected_sums = {j: term(j) for j in range(2*b+1) if j not in (1, 2, 5)}
        exceptional = {1: 7, 2: 10, 5: 11}
        expected_differences = {
            d: term(exceptional.get(abs(d), abs(d))) for d in range(-b, b+1)
        }
        if sums != expected_sums or differences != expected_differences:
            raise ValueError("pair maxima disagree with the three-hole formulas")

    divisor = gcd(ns, nd)
    left = (nd//divisor)**bound_denominator
    right = (ns//divisor)**bound_denominator * base**(bound_numerator-bound_denominator)
    if left <= right:
        raise ValueError("the integer inequality does not certify this strict bound")
    return {
        "name": name, "alphabet": list(alphabet), "q": [p, h], "base": base,
        "sum_numerator": str(ns), "difference_numerator": str(nd),
        "common_denominator": str(common_denominator),
        "strict_bound": [bound_numerator, bound_denominator],
        "left_bits": left.bit_length(), "right_bits": right.bit_length(),
        "verified": True,
    }


def main():
    results = [verify_case(*case) for case in CASES]
    print(json.dumps({"status": "verified", "certificates": results}, indent=2))


if __name__ == "__main__":
    main()
