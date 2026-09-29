"""Reconstruct the fixed four-digit certificate using only Python 3.10+ stdlib."""

import json
from pathlib import Path
import sys


ALPHABET = (0, 3, 4, *range(6, 17))
UNREACHABLE = 255  # Every finite endpoint cost is at most 128.
MAX_BYTES = 16384
MAX_CELLS = 1082401
PARAMETERS = {
    "schema_version": 1,
    "alphabet": list(ALPHABET),
    "block_base": 32,
    "block_depth": 4,
    "radius": 541200,
    "outer_base": 1082401,
    "q": [16, 19],
    "maximum_cost": 128,
    "strict_bound": [23713, 20000],
}
HISTOGRAMS = ("sum_histogram", "difference_histogram")
TOTALS = ("sum_numerator", "difference_numerator", "common_denominator")


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def validate_certificate(value):
    """Validate the one public certificate before allocating either cost table."""
    if type(value) is not dict or set(value) != set(PARAMETERS) | set(HISTOGRAMS) | set(TOTALS):
        raise ValueError("certificate fields differ")
    for key, expected in PARAMETERS.items():
        item = value[key]
        if (type(item) is not type(expected) or item != expected
                or (type(item) is list and any(type(v) is not int for v in item))):
            raise ValueError("fixed parameter differs: " + key)
    for key in HISTOGRAMS:
        item = value[key]
        if (type(item) is not list or len(item) != 129
                or any(type(v) is not int or not 0 <= v <= MAX_CELLS for v in item)):
            raise ValueError("invalid cost histogram")
    for key in TOTALS:
        item = value[key]
        if (type(item) is not str or not 1 <= len(item) <= 256
                or item[0] == "0" or any(not "0" <= v <= "9" for v in item)):
            raise ValueError("expected a bounded positive decimal integer")
    return value


def read_certificate(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("certificate exceeds the file limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("invalid certificate JSON") from error
    return validate_certificate(value)


def _advance(previous, increments, place):
    """Add one high digit; merge every repeated integer output by minimum cost."""
    low, high = min(increments), max(increments)
    length = len(previous) + (high - low) * place
    if length > MAX_CELLS:
        raise ValueError("cost table exceeds the cell limit")
    following = bytearray([UNREACHABLE]) * length
    for digit, digit_cost in increments.items():
        shift = (digit - low) * place
        for index, old_cost in enumerate(previous):
            if old_cost != UNREACHABLE:
                cost = old_cost + digit_cost
                if cost < following[index + shift]:
                    following[index + shift] = cost
    return following


def cost_tables(alphabet, base, depth):
    """Return sum costs at z, difference costs at z+radius, and the radius.

    Small bounded inputs are accepted for independent endpoint-pair controls.
    The command-line verifier uses only ALPHABET, base 32 and depth 4.
    """
    if (type(alphabet) is not tuple or not 2 <= len(alphabet) <= 17
            or any(type(a) is not int or not 0 <= a <= 16 for a in alphabet)
            or alphabet != tuple(sorted(set(alphabet))) or alphabet[0] != 0
            or type(base) is not int or not alphabet[-1] < base <= 32
            or type(depth) is not int or not 1 <= depth <= 4):
        raise ValueError("invalid bounded block parameters")
    sums, differences = {}, {}
    for a in alphabet:
        for b in alphabet:
            cost = a + b
            sums[a + b] = min(sums.get(a + b, UNREACHABLE), cost)
            differences[a - b] = min(differences.get(a - b, UNREACHABLE), cost)
    sum_costs = difference_costs = bytearray([0])
    radius, place = 0, 1
    for _ in range(depth):
        sum_costs = _advance(sum_costs, sums, place)
        difference_costs = _advance(difference_costs, differences, place)
        radius += alphabet[-1] * place
        place *= base
    return sum_costs, difference_costs, radius


def _histogram(costs, maximum):
    counts = [0] * (maximum + 1)
    for cost in costs:
        if cost != UNREACHABLE:
            if cost > maximum:
                raise ValueError("finite cost exceeds the declared maximum")
            counts[cost] += 1
    return counts


def _integer_total(counts, p, h):
    degree = len(counts) - 1
    return sum(count * p**e * h**(degree - e) for e, count in enumerate(counts))


def strict_ratio_exceeds(nd, ns, radix, offset, denominator):
    """Test 1+log(nd/ns)/log(radix) > 1+offset/denominator exactly."""
    if (any(type(v) is not int for v in (nd, ns, radix, offset, denominator))
            or not 0 < nd or not 0 < ns or max(nd.bit_length(), ns.bit_length()) > 1024
            or not 1 < radix <= MAX_CELLS or not 0 < offset < denominator <= 20000):
        raise ValueError("integer comparison outside the stated bounds")
    return nd**denominator > radix**offset * ns**denominator


def verify_certificate(certificate):
    data = validate_certificate(certificate)
    sums, differences, radius = cost_tables(ALPHABET, data["block_base"], data["block_depth"])
    if radius != data["radius"] or 2 * radius + 1 != data["outer_base"]:
        raise ValueError("reconstructed radius differs")
    sum_histogram = _histogram(sums, data["maximum_cost"])
    difference_histogram = _histogram(differences, data["maximum_cost"])
    if sum_histogram != data["sum_histogram"]:
        raise ValueError("reconstructed sum histogram differs")
    if difference_histogram != data["difference_histogram"]:
        raise ValueError("reconstructed difference histogram differs")
    p, h = data["q"]
    ns = _integer_total(sum_histogram, p, h)
    nd = _integer_total(difference_histogram, p, h)
    common_denominator = h**data["maximum_cost"]
    if (str(ns) != data["sum_numerator"] or str(nd) != data["difference_numerator"]
            or str(common_denominator) != data["common_denominator"]):
        raise ValueError("reconstructed integer totals differ")
    numerator, denominator = data["strict_bound"]
    if not strict_ratio_exceeds(nd, ns, data["outer_base"], numerator - denominator, denominator):
        raise ValueError("the strict integer inequality failed")
    return {
        "status": "verified",
        "block_base": data["block_base"], "block_depth": data["block_depth"],
        "radius": radius, "outer_base": data["outer_base"], "q": data["q"],
        "sum_histogram_bins": len(sum_histogram),
        "difference_histogram_bins": len(difference_histogram),
        "sum_numerator": str(ns), "difference_numerator": str(nd),
        "common_denominator": str(common_denominator),
        "strict_bound": data["strict_bound"],
    }


def main():
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python3 -B carry_verify.py")
    certificate = read_certificate(Path(__file__).with_name("carry-certificate.json"))
    print(json.dumps(verify_certificate(certificate), indent=2))


if __name__ == "__main__":
    main()
