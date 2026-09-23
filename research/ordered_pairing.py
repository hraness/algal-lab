"""Probability-free optimal equal-value pairing under weighted deletions.

The objective is the expected COUNT of working pairs, not the largest connected
component. 'both' requires both members; 'either' needs at least one member.
The same pairing is optimal at each fixed survivor count.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def optimal_pairing(weights: object, objective: object) -> dict:
    if type(weights) is not list or not 2 <= len(weights) <= 128 or len(weights) % 2:
        raise ValueError("weights must contain an even number of 2..128 rates")
    if any(type(w) not in (int, float) or not 0 < w <= 1_000_000 or not math.isfinite(w)
           for w in weights):
        raise ValueError("rates must be finite positive numbers at most 1,000,000")
    if type(objective) is not str or objective not in ("both", "either"):
        raise ValueError("objective must be both or either")
    ordered = sorted(range(len(weights)), key=lambda i: (weights[i], i))
    if objective == "both":
        pairs = list(zip(ordered[::2], ordered[1::2]))
    else:
        pairs = list(zip(ordered[:len(ordered) // 2], reversed(ordered[len(ordered) // 2:])))
    return {
        "contract": "algal.lab.ordered-pairing.v1",
        "status": "structurally-optimal",
        "objective": objective,
        "service": "expected number of equal-value working pairs",
        "weights": weights.copy(),
        "pairs": sorted([sorted(pair) for pair in pairs]),
        "horizons": "every fixed survivor count under sequential rate-proportional deletion",
        "proof": "ordered joint-inclusion four-point inequalities and matching exchanges",
        "probabilityEvaluations": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    with args.input.open("rb") as f:
        raw = f.read(8193)
    if len(raw) > 8192:
        raise ValueError("input exceeds 8192 bytes")
    value = json.loads(raw)
    if type(value) is not dict or set(value) != {"weights", "objective"}:
        raise ValueError("input requires exactly weights and objective")
    print(json.dumps(optimal_pairing(value["weights"], value["objective"]), indent=2))


if __name__ == "__main__":
    main()
