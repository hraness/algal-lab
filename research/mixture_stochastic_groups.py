"""Certify optimal intact groups for a common two-base histogram mixture.

The normalized histogram rows must lie on one affine line in the probability
simplex. Its two extreme input rows are common base distributions, and every
clock independently samples its own mixture of those bases. The bases may
have crossing CDFs. Sorting the mixture weights and grouping consecutively
maximizes every tail of intact-group count at each fixed survivor horizon,
including with any finite background vector independent of the input clocks.

Admission and the affine certificate use exact rational arithmetic. There
are O(n B + n log n) rational operations and O(n B) stored values, not a
bit-complexity claim. No joint probabilities or candidate partitions are
evaluated. The certificate concerns the supplied histogram laws, not unknown
populations from which counts may have been sampled.
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


def optimal_mixture_histogram_groups(histograms: object, group_size: object) -> dict:
    """Return an exact structural certificate, or reject noncollinear laws.

    Labels are zero-based input indices. The first differing normalized-mass
    coordinate determines the two bases, using its smallest and largest row
    values and original-label tie breaking. Mixture weights retain input
    order. Identical laws use label zero for both bases and all-zero weights.
    """
    rows = _admit_histograms(histograms)
    n = len(rows)
    if type(group_size) is not int or not 2 <= group_size <= n or n % group_size:
        raise ValueError("group_size requires an integer in 2..n dividing the number of clocks")
    bins = len(rows[0])
    masses = []
    for row in rows:
        total = sum(row)
        masses.append(tuple(Fraction(count, total) for count in row))

    differing_bin = next((index for index in range(bins)
                          if any(row[index] != masses[0][index] for row in masses[1:])), None)
    if differing_bin is None:
        base_labels = [0, 0]
        weights = [Fraction(0)] * n
    else:
        lower = min(range(n), key=lambda label: (masses[label][differing_bin], label))
        upper = min(range(n), key=lambda label: (-masses[label][differing_bin], label))
        base_labels = [lower, upper]
        span = masses[upper][differing_bin] - masses[lower][differing_bin]
        weights = [(row[differing_bin] - masses[lower][differing_bin]) / span
                   for row in masses]
        for label, weight in enumerate(weights):
            if not 0 <= weight <= 1:
                raise ValueError(f"cannot certify a common mixture weight for label {label}")
            for index in range(bins):
                expected = ((1 - weight) * masses[lower][index]
                            + weight * masses[upper][index])
                if masses[label][index] != expected:
                    raise ValueError(
                        f"cannot certify affine-collinear normalized histogram rows: "
                        f"label {label}, bin {index}"
                    )

    ordered = sorted(range(n), key=lambda label: (weights[label], label))
    groups = [ordered[start:start + group_size] for start in range(0, n, group_size)]
    return {
        "contract": "algal.lab.mixture-stochastic-grouping.v1",
        "status": "structurally-optimal",
        "objective": "intact",
        "service": "number of equal-value intact groups",
        "optimality": "usual stochastic order of intact-group count at each fixed horizon",
        "histograms": rows,
        "groupSize": group_size,
        "labels": ordered,
        "groups": groups,
        "baseLabels": base_labels,
        "baseMasses": [[str(value) for value in masses[label]] for label in base_labels],
        "mixingWeights": [str(weight) for weight in weights],
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
            "criterion": "affine-collinear normalized histogram mass rows",
            "affineDimension": int(differing_bin is not None),
            "differingBin": differing_bin,
            "clockCount": n,
            "binCount": bins,
            "baseSelection": "minimum and maximum mass in the first differing bin; "
            "lowest original label resolves ties; identical laws use label zero twice",
            "identity": "normalized row i = (1-mixingWeights[i])*baseMasses[0] "
            "+ mixingWeights[i]*baseMasses[1], verified in every bin",
            "ordering": "ascending exact mixture weight, then original label",
            "weightIndexing": "original input labels",
            "rationalEncoding": "reduced integer or numerator/denominator strings",
            "baseCdfOrder": "unrestricted; the two base CDFs may cross",
            "constructionCost": "O(n B + n log n) rational operations and O(n B) storage; "
            "no bit-complexity claim",
            "limitations": [
                "No population or sampling-confidence guarantee is inferred from counts.",
                "No certificate is returned for noncollinear normalized laws.",
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
    result = optimal_mixture_histogram_groups(value["histograms"], value["groupSize"])
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
