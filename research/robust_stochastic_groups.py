"""Certify bounded regret for intact groups of independent histogram clocks.

Sort exact CDF endpoint vectors lexicographically, then use standard Basic
L-infinity isotonic regression: the midpoint of prefix maxima and suffix
minima. Linear interpolation gives ordered reference CDFs. Their consecutive
equal-size groups are optimal for intact-group count under the reference laws.
Kolmogorov perturbation bounds certify regret under the original histograms.

The projection minimizes the largest CDF error for this fixed label order;
it does not minimize the sum of errors or optimize the choice of label order.
Construction uses O(n B log n) rational operations and O(n B) storage, with
zero joint-probability evaluations. This certificate concerns histogram laws,
not unknown populations from which histogram counts may have been sampled.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from research.stochastic_groups import (
    MAX_INPUT_BYTES,
    _admit_histograms,
    _reject_json_number,
    _unique_object,
)


def robust_histogram_groups(histograms: object, group_size: object) -> dict:
    """Return an exact approximation certificate for every fixed horizon.

    Labels are zero-based input indices. CDF and error rows retain input order;
    ``labels`` and ``groups`` report the lexicographic ordering used for the
    projection. Every rational output is a reduced Fraction string.
    """
    rows = _admit_histograms(histograms)
    n = len(rows)
    if type(group_size) is not int or not 2 <= group_size <= n or n % group_size:
        raise ValueError("group_size requires an integer in 2..n dividing the number of clocks")
    bins = len(rows[0])
    cdfs = []
    for row in rows:
        total = sum(row)
        cumulative = 0
        endpoints = [Fraction(0)]
        for count in row:
            cumulative += count
            endpoints.append(Fraction(cumulative, total))
        cdfs.append(tuple(endpoints))
    ordered = sorted(range(n), key=lambda label: (cdfs[label], label))

    # Retain a violating pair to certify the minimax lower bound. Tracking
    # the prefix maximizer avoids enumerating all pairs of rows.
    maxima = [Fraction(0)] * (bins + 1)
    maximizers = [ordered[0]] * (bins + 1)
    prefixes = [[] for _ in rows]
    violation = Fraction(0)
    witness = None
    for label in ordered:
        for endpoint, value in enumerate(cdfs[label]):
            difference = maxima[endpoint] - value
            if difference > violation:
                violation = difference
                witness = {
                    "earlierLabel": maximizers[endpoint],
                    "laterLabel": label,
                    "endpoint": endpoint,
                    "violation": str(difference),
                }
            if value > maxima[endpoint]:
                maxima[endpoint] = value
                maximizers[endpoint] = label
        prefixes[label] = maxima.copy()

    minima = [Fraction(1)] * (bins + 1)
    projected = [[] for _ in rows]
    errors = [Fraction(0)] * n
    for label in reversed(ordered):
        for endpoint, value in enumerate(cdfs[label]):
            minima[endpoint] = min(minima[endpoint], value)
        projected[label] = [(upper + lower) / 2
                            for upper, lower in zip(prefixes[label], minima)]
        errors[label] = max(abs(original - reference)
                            for original, reference in zip(cdfs[label], projected[label]))

    groups = [ordered[start:start + group_size] for start in range(0, n, group_size)]
    total_error = sum(errors, Fraction(0))
    count_bound = min(Fraction(len(groups)), 2 * total_error)
    return {
        "contract": "algal.lab.robust-stochastic-grouping.v1",
        "status": "approximation-certified",
        "objective": "intact",
        "service": "number of equal-value intact groups",
        "histograms": rows,
        "groupSize": group_size,
        "labels": ordered,
        "groups": groups,
        "projectedCdfEndpoints": [[str(value) for value in row] for row in projected],
        "kolmogorovErrors": [str(error) for error in errors],
        "minimaxUniformRadius": str(violation / 2),
        "totalKolmogorovError": str(total_error),
        "regretBounds": {
            "mean": str(count_bound),
            "eachTail": str(min(Fraction(1), 2 * total_error)),
            "summedPositiveTailShortfall": str(count_bound),
        },
        "horizons": "every fixed survivor count when retaining the largest scores",
        "scope": "partitions of the input labels into groups of the requested equal size "
        "under the supplied histogram laws; background scores are not assigned to groups",
        "assumptions": [
            "Input clocks are mutually independent and uniform within each sampled unit bin.",
            "Bin j is [j,j+1), and each row is normalized by its own positive total.",
            "Each group earns the same reward exactly when all its members are retained.",
            "Any finite background vector is jointly independent of the input clocks; "
            "its entries may depend on each other.",
        ],
        "certificate": {
            "method": "standard Basic L-infinity isotonic regression of CDF endpoints",
            "ordering": "lexicographic exact CDF endpoints, then original label",
            "clockCount": n,
            "binCount": bins,
            "endpointCount": bins + 1,
            "endpointCoordinates": "integers from zero through binCount",
            "rowIndexing": "original input labels",
            "rationalEncoding": "reduced integer or numerator/denominator strings",
            "interpolation": "linear within each common unit bin",
            "largestOrderViolation": str(violation),
            "minimaxWitness": witness,
            "minimaxScope": "smallest maximum per-label Kolmogorov error among all "
            "CDF chains in the reported fixed label order",
            "referenceOptimality": "usual stochastic order of intact-group count "
            "at each fixed horizon under the projected independent laws",
            "regretComparison": "each bound compares the reported groups with every "
            "equal-size partition under the original histogram laws at a fixed horizon; "
            "summed positive-tail shortfall uses one competing partition for all tails",
            "limitations": [
                "No minimum sum of errors or best choice of label order is claimed.",
                "No population or sampling-confidence guarantee is inferred from counts.",
            ],
        },
        "probabilityEvaluations": 0,
    }


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
    result = robust_histogram_groups(value["histograms"], value["groupSize"])
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
