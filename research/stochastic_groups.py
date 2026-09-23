"""Certify optimal intact groups from separated blocks of histogram CDFs.

Each independent clock chooses a common unit bin by its normalized row mass,
then is uniform inside that bin. Retain the largest scores. A group earns one
unit exactly when all its members are retained. The certified equal-size
partition maximizes every tail probability of intact-group count at every
fixed survivor count, and hence its expectation, including with any finite
background vector independent of the input clocks.

Across consecutive groups, every CDF in the earlier group must lie below every
CDF in the later group. CDFs may cross within a group when forming pairs, at
most two groups, or exactly three triples. The last case has a separate exact
finite proof. Otherwise all CDFs must form a componentwise ordered chain.
Exact endpoint checks suffice because CDF differences are affine within each
common unit bin.
Construction takes O(n B log n) rational operations and O(n B) storage, with
no joint-inclusion probability evaluations or fallback optimization.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path


MAX_CLOCKS = 128
MAX_BINS = 64
MAX_COUNT = 1_000_000
MAX_INPUT_BYTES = 131_072


def _admit_histograms(value: object) -> list[list[int]]:
    if type(value) is not list or not 2 <= len(value) <= MAX_CLOCKS:
        raise ValueError(f"histograms requires 2..{MAX_CLOCKS} rows")
    bins = len(value[0]) if type(value[0]) is list else 0
    if not 1 <= bins <= MAX_BINS:
        raise ValueError(f"histograms requires 1..{MAX_BINS} common unit bins")
    rows = []
    for row in value:
        if type(row) is not list or len(row) != bins:
            raise ValueError("histograms requires rows of equal length")
        if any(type(count) is not int or not 0 <= count <= MAX_COUNT for count in row):
            raise ValueError(f"histogram counts require integers in 0..{MAX_COUNT}")
        if sum(row) == 0:
            raise ValueError("each histogram requires positive total mass")
        rows.append(row.copy())
    return rows


def optimal_histogram_groups(histograms: object, group_size: object) -> dict:
    """Return a structural certificate, or reject an uncertified CDF order.

    Labels are zero-based input row indices. Returned groups follow ascending
    lexicographic CDF order, with original labels resolving identical CDFs.
    A certificate concerns partitions of these labels into groups of the
    requested size. Background scores may change membership in the retained
    set but are not assigned to groups.
    """
    rows = _admit_histograms(histograms)
    if type(group_size) is not int or not 2 <= group_size <= len(rows) or len(rows) % group_size:
        raise ValueError("group_size requires an integer in 2..n dividing the number of clocks")
    cdfs = []
    for row in rows:
        total = sum(row)
        cumulative = 0
        endpoints = [Fraction(0)]
        for count in row:
            cumulative += count
            endpoints.append(Fraction(cumulative, total))
        cdfs.append(tuple(endpoints))

    ordered = sorted(range(len(rows)), key=lambda label: (cdfs[label], label))
    groups = [ordered[i:i + group_size] for i in range(0, len(rows), group_size)]
    for cut, (left, right) in enumerate(zip(groups, groups[1:]), start=1):
        for endpoint in range(len(rows[0]) + 1):
            left_max = max(cdfs[label][endpoint] for label in left)
            right_min = min(cdfs[label][endpoint] for label in right)
            if left_max > right_min:
                raise ValueError(
                    f"cannot certify CDF block cut {cut} at bin endpoint {endpoint}"
                )

    crossings_allowed = (group_size == 2 or len(groups) <= 2
                         or (group_size == 3 and len(groups) == 3))
    if not crossings_allowed:
        for left, right in zip(ordered, ordered[1:]):
            if any(a > b for a, b in zip(cdfs[left], cdfs[right])):
                raise ValueError(
                    "this group configuration requires a componentwise ordered CDF chain; "
                    "within-group crossings are certified only for pairs, at most two "
                    "groups, or exactly three triples"
                )

    return {
        "contract": "algal.lab.stochastic-grouping.v1",
        "status": "structurally-optimal",
        "objective": "intact",
        "service": "number of equal-value intact groups",
        "optimality": "usual stochastic order of intact-group count at each fixed horizon",
        "histograms": rows,
        "groupSize": group_size,
        "groups": groups,
        "horizons": "every fixed survivor count when retaining the largest scores",
        "scope": "partitions of the input labels into groups of the requested equal size; "
        "background scores are not assigned to groups",
        "assumptions": [
            "Input clocks are mutually independent and uniform within each sampled unit bin.",
            "Bin j is [j,j+1), and each row is normalized by its own positive total.",
            "Each group earns the same reward exactly when all its members are retained.",
            "Any finite background vector is jointly independent of the input clocks; "
            "its entries may depend on each other.",
        ],
        "certificate": {
            "criterion": ("separated CDF blocks of equal size" if crossings_allowed else
                          "componentwise ordered CDF chain"),
            "clockCount": len(rows),
            "binCount": len(rows[0]),
            "endpointCount": len(rows[0]) + 1,
            "cutCount": len(groups) - 1,
            "endpointComparison": "max CDF in each group <= min CDF in the next group",
            "withinGroupCdfOrder": ("unrestricted" if crossings_allowed else
                                    "componentwise ordered"),
        },
        "probabilityEvaluations": 0,
    }


def _unique_object(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_json_number(value: str) -> None:
    raise ValueError(f"JSON histogram counts and groupSize require integers, received {value}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    with args.input.open("rb") as source:
        raw = source.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                       parse_float=_reject_json_number, parse_constant=_reject_json_number)
    if type(value) is not dict or set(value) != {"histograms", "groupSize"}:
        raise ValueError("input requires exactly histograms and groupSize")
    result = optimal_histogram_groups(value["histograms"], value["groupSize"])
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
