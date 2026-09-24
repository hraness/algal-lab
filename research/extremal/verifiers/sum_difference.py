"""Sum-difference exponent lower bounds (AlphaEvolve problem 42).

For a finite set A of integers with |A-A| > |A|, the ratio
log(|A+A|/|A|) / log(|A-A|/|A|) lower-bounds the least C with
|A+A|/|A| <= (|A-A|/|A|)^C. The verifier counts sums and differences exactly
and returns the ratio as a 40-digit decimal truncated toward zero (absolute
error below 1e-38), which is far inside the reporting precision of any
published value. Larger is better.
"""

from decimal import Decimal, localcontext
from fractions import Fraction

DESCRIPTION = (
    "Finite set A of distinct integers. Score = ln(|A+A|/|A|) / ln(|A-A|/|A|) where A+A and A-A are "
    "the sumset and difference set (counted exactly). Larger is better; you want many sums but few "
    "differences. |A-A| must exceed |A|. Output: {\"set\": [int, ...]} with at most 2000 plain ints "
    "of absolute value below 10^9."
)
MAX_SIZE = 2000
MAX_ABS = 10**9
DIGITS = 40


def verify(construction, parameters) -> Fraction:
    raw = construction.get("set") if isinstance(construction, dict) else None
    if not isinstance(raw, list) or not 2 <= len(raw) <= MAX_SIZE:
        raise ValueError("set must be a list of 2..%d integers" % MAX_SIZE)
    if any(isinstance(x, bool) or not isinstance(x, int) or abs(x) >= MAX_ABS for x in raw):
        raise ValueError("set entries must be plain ints below 10^9 in absolute value")
    a = sorted(set(raw))
    if len(a) != len(raw):
        raise ValueError("repeated element")
    n = len(a)
    sums = {x + y for x in a for y in a}
    diffs = {x - y for x in a for y in a}
    if len(diffs) <= n:
        raise ValueError("|A-A| must exceed |A|")
    with localcontext() as ctx:
        ctx.prec = DIGITS + 20
        ratio = (Decimal(len(sums)) / Decimal(n)).ln() / (Decimal(len(diffs)) / Decimal(n)).ln()
        quant = Decimal(1).scaleb(-DIGITS)
        truncated = ratio.quantize(quant, rounding="ROUND_DOWN")
    return Fraction(truncated)
