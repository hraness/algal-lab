"""Run the fixed, credential-free certified occupancy study into a new directory."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
from time import perf_counter

from research.softmax_partition import _item_intervals, _reward_interval, optimize_partition


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = Path(__file__).with_name("protocol.json")


def _partitions(total: int, largest: int | None = None):
    if total == 0:
        yield ()
        return
    if largest is None:
        largest = total
    for first in range(min(total, largest), 0, -1):
        for suffix in _partitions(total - first, first):
            yield (first,) + suffix


def _enumeration_check(result: dict[str, object]) -> dict[str, object]:
    n, tasks = result["agents"], result["tasks"]
    items = _item_intervals(n, Q(result["inner"]), Q(result["outer"]), result["precisionBits"])
    selected = tuple(result["groups"])
    chosen_lower = Q(result["witnessRewardInterval"][0])
    claimed_upper = Q(result["optimumInterval"][1])
    other_upper = Q(-1)
    exhaustive_lower = Q(0)
    count = 0
    for groups in _partitions(n):
        if len(groups) > tasks:
            continue
        lower, upper = _reward_interval(groups, tasks, items, result["precisionBits"])
        exhaustive_lower = max(exhaustive_lower, lower)
        if groups != selected:
            other_upper = max(other_upper, upper)
        if lower > claimed_upper:
            raise ArithmeticError("exhaustive feasible lower bound exceeds solver upper bound")
        count += 1
    gap = None if other_upper < 0 else chosen_lower - other_upper
    return {"partitionsEnumerated": count,
            "uniqueOptimalOccupancyCertified": other_upper < chosen_lower,
            "runnerUpGapLowerBound": str(gap) if gap is not None and gap > 0 else None,
            "exhaustiveBestLowerBound": str(exhaustive_lower),
            "comparisonScope": "Exact outward interval enumeration; shares coefficient enclosure code, independent of DP."}


def run(output: Path) -> dict[str, object]:
    with PROTOCOL.open("rb") as stream:
        raw = stream.read(8193)
    if len(raw) > 8192:
        raise ValueError("study protocol exceeds its size cap")
    protocol = json.loads(raw)
    # The study accepts only its repository-owned literal design, not arbitrary
    # external JSON or generated code. Output never overwrites an earlier run.
    expected_keys = {"contract", "purpose", "epsilon", "squarePopulations",
                     "matchedTemperatures", "additionalCases", "exhaustivePopulationCap",
                     "externalModelCalls", "interpretation"}
    if (type(protocol) is not dict or set(protocol) != expected_keys
            or protocol["contract"] != "algal.lab.softmax-partition-study.v1"
            or type(protocol["externalModelCalls"]) is not int
            or protocol["externalModelCalls"] != 0
            or any(type(protocol[key]) is not str or len(protocol[key]) > 512
                   for key in ("purpose", "interpretation"))
            or protocol["squarePopulations"] != [3, 9, 16, 64]
            or protocol["matchedTemperatures"] != ["1/10", "1", "3", "8"]
            or protocol["epsilon"] != "1/100000000"
            or protocol["exhaustivePopulationCap"] != 16
            or protocol["additionalCases"] != [
                {"agents": 9, "tasks": 9, "inner": "8", "outer": "1/4"},
                {"agents": 9, "tasks": 3, "inner": "1", "outer": "1"},
                {"agents": 9, "tasks": 1, "inner": "1", "outer": "1"},
                {"agents": 4, "tasks": 8, "inner": "1", "outer": "1"}]):
        raise ValueError("fixed study design changed; review the protocol and driver together")
    paths = [PROTOCOL, Path(__file__).resolve(), ROOT / "research/softmax_partition.py",
             ROOT / "research/softmax_partition_dp.py"]
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in paths}
    cases = [{"agents": n, "tasks": n, "inner": t, "outer": t}
             for n in protocol["squarePopulations"] for t in protocol["matchedTemperatures"]]
    cases += protocol["additionalCases"]
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"contract": protocol["contract"], "protocol": protocol,
               "sourceSha256": sources, "python": platform.python_version(),
               "results": [], "status": "running"}
    try:
        for case in cases:
            started = perf_counter()
            result = optimize_partition(case["agents"], case["tasks"],
                                        Q(case["inner"]), Q(case["outer"]), Q(protocol["epsilon"]))
            result["observedSolverSeconds"] = perf_counter() - started
            if case["agents"] <= protocol["exhaustivePopulationCap"]:
                result["exhaustiveCheck"] = _enumeration_check(result)
            else:
                result["exhaustiveCheck"] = None
            receipt["results"].append(result)
        receipt["status"] = "passed"
    except Exception as exc:
        receipt["status"] = "failed"
        receipt["failure"] = {"type": type(exc).__name__, "message": str(exc),
                              "caseIndex": len(receipt["results"])}
        raise
    finally:
        (output / "run.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.out)
    print(json.dumps({"status": result["status"], "cases": len(result["results"]),
                      "externalModelCalls": 0}))


if __name__ == "__main__":
    main()
