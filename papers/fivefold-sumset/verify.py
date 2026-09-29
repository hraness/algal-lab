"""Verify the fixed fivefold counterexample using two integer count formulas.

Python 3.10 or later; standard library only. No search or set materialization.
The helper input limits include the fixed example and the tiny test cases.
"""
from math import comb


EXPECTED = (
    26803978088637482320924005417351807094920729834065401687980641043635930530641397394413149542136919433471609550,
    154579661067052985891396746515532070244562006281032655462415619710257876956423657730117453330,
    3958413820136803962031338590521923319120722874548443129616912163401921356829633686382,
)


def validate(m, a, b):
    for value, lower, upper in ((m, 1, 128), (a, 0, 160), (b, 0, 32)):
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError('parameters exceed the certificate limits')


def single_sum(m, a, b):
    """Return (|A-B|, |A+B|, |5B|), grouping by negative support."""
    validate(m, a, b)
    difference = sum(comb(m, j) * comb(b, j) * comb(m - j + a, m - j)
                     for j in range(min(m, b) + 1))
    return difference, comb(m + a + b, m), comb(m + 5 * b, m)


def double_sum(m, a, b):
    """Reconstruct the three counts from factorials and both signed supports."""
    validate(m, a, b)
    factorial = [1]
    for number in range(1, max(m + a + b, m + 5 * b) + 1):
        factorial.append(factorial[-1] * number)

    def choose(n, k):
        return factorial[n] // (factorial[k] * factorial[n - k])

    difference = 0
    for positive in range(min(m, a) + 1):
        for negative in range(min(m - positive, b) + 1):
            difference += (choose(m, positive) * choose(m - positive, negative)
                           * choose(a, positive) * choose(b, negative))
    return (difference, choose(m + a + b, a + b),
            choose(m + 5 * b, 5 * b))


def verify_certificate():
    primary = single_sum(128, 160, 32)
    independent = double_sum(128, 160, 32)
    if primary != independent or primary != EXPECTED:
        raise ArithmeticError('the two counts or recorded integers disagree')
    difference, sums, fivefold = primary
    if difference ** 5 <= sums ** 5 * fivefold:
        raise ArithmeticError('the strict fivefold inequality does not fail')
    return primary


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 1:
        raise SystemExit('usage: python3 -B verify.py')
    verify_certificate()
    print('PASS: both integer counts agree and D^5 > S^5 F.')
