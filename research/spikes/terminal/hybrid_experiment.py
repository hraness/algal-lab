"""Fresh fixed-panel test of theorem-restricted terminal certificates.

python3 -m research.spikes.terminal.hybrid_experiment run --out research/spikes/terminal/runs/hybrid-v2
python3 -m research.spikes.terminal.hybrid_experiment replay --out research/spikes/terminal/runs/hybrid-v2
"""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import platform
from random import Random
from statistics import mean, median
import sys
from time import perf_counter

from research.terminal_hybrid import sample_hybrid_tree
from research.terminal_sampling import sample_terminal_tree
from research.terminal_tree import PairProbabilities, frontier_tree, maximum_spanning_tree
from research.spikes.terminal.experiment import (
    ROOT, SOURCES as V1_SOURCES, _canonical, _digest, _environment, _plan as _v1_plan,
    _read_json, _seed, _without_timings, _write_new,
)


PLAN_PATH = Path(__file__).with_name("hybrid-protocol.json")
SOURCES = V1_SOURCES + ["research/terminal_hybrid.py", "research/spikes/terminal/hybrid_experiment.py",
                        "research/spikes/terminal/hybrid-protocol.json"]


def _identities():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def _plan():
    plan = _read_json(PLAN_PATH, 64 * 1024)
    keys = {"contract", "endpoint", "environmentSeeds", "sampleSeeds", "samples", "methods", "familyDelta",
            "deltaAllocation", "exactTimingRepeats", "regimes", "primary", "interpretation"}
    if type(plan) is not dict or set(plan) != keys or plan["contract"] != "algal.lab.terminal-hybrid-plan.v1":
        raise ValueError("invalid hybrid plan")
    original = _v1_plan()
    for key, expected, excluded in (("environmentSeeds", 4, original["environmentSeeds"]),
                                    ("sampleSeeds", 2, original["sampleSeeds"])):
        values = plan[key]
        if (type(values) is not list or len(values) != expected or len(set(values)) != expected
                or any(type(x) is not int or not 0 <= x < 2**32 for x in values)
                or set(values) & set(excluded)):
            raise ValueError(f"invalid or reused {key}")
    if (plan["samples"] != 2048 or plan["methods"] != ["frontier-v1", "hybrid-v2"]
            or plan["familyDelta"] != .05 or plan["deltaAllocation"] != 384 or plan["exactTimingRepeats"] != 3
            or plan["regimes"] != original["regimes"]):
        raise ValueError("fixed hybrid instrument budgets changed")
    primary = {"regimes": ["wide-rates-64", "frontier-64"], "method": "hybrid-v2",
               "maximumMeanExactRegret": .001, "maximumEveryConfidenceBound": .01, "minimumMedianSpeedup": 2}
    if plan["primary"] != primary:
        raise ValueError("primary criterion changed")
    return plan


def _calculate(plan):
    cases = []
    delta = plan["familyDelta"] / plan["deltaAllocation"]
    for regime in plan["regimes"]:
        n = regime["nodes"]
        for environment_seed in plan["environmentSeeds"]:
            env = _environment(regime, environment_seed)
            values = env["values"]
            exact_times = []
            for _ in range(plan["exactTimingRepeats"]):
                start = perf_counter()
                probabilities = PairProbabilities(env["weights"])
                optimal, frontier, comparisons = frontier_tree(env, probabilities)
                exact_times.append(perf_counter() - start)
            construction_integrations = probabilities.integrations
            q = {(i, j): probabilities.numerator(i, j) for i in range(n) for j in range(i + 1, n)}
            if sum(q.values()) != probabilities.denominator:
                raise ArithmeticError("exact pair normalization failed")
            weights = {edge: chance * min(values[i] for i in edge) for edge, chance in q.items()}
            benefit = sum(weights[edge] for edge in optimal)
            if sum(weights[edge] for edge in maximum_spanning_tree(n, weights)) != benefit:
                raise ArithmeticError("structural and generic exact optimizers disagree")
            denominator = probabilities.denominator * sum(values)
            base = sum(chance * max(values[i] for i in edge) for edge, chance in q.items())
            stars = [sum(weight for edge, weight in weights.items() if center in edge) for center in range(n)]
            center = min(range(n), key=lambda i: (env["weights"][i], -values[i], i))
            case = {"regime": regime["name"], "environmentSeed": environment_seed, "environment": env,
                    "exact": {"edges": optimal, "frontier": frontier, "expectedService": str(Fraction(base + benefit, denominator)),
                              "edgeBenefit": str(Fraction(benefit, denominator)),
                              "payoffRange": str(Fraction(sorted(values)[-2], sum(values))),
                              "bestStarRegret": str(Fraction(benefit - max(stars), denominator)),
                              "reliableStarRegret": str(Fraction(benefit - stars[center], denominator)),
                              "constructionEdgeEvaluations": comparisons,
                              "constructionPairIntegrations": construction_integrations,
                              "fullEvaluationPairIntegrations": probabilities.integrations},
                    "timing": {"exactConstructionSeconds": exact_times}, "trials": []}
            for sample_seed in plan["sampleSeeds"]:
                order = plan["methods"] if sample_seed == plan["sampleSeeds"][0] else list(reversed(plan["methods"]))
                methods = {}
                for method in order:
                    rng = Random(_seed("terminal-hybrid-panel-v2", regime["name"], environment_seed, sample_seed))
                    start = perf_counter()
                    if method == "hybrid-v2":
                        result = sample_hybrid_tree(env, plan["samples"], delta, randbelow=rng.randrange)
                    else:
                        result = sample_terminal_tree(env, plan["samples"], delta, randbelow=rng.randrange, method="frontier")
                    seconds = perf_counter() - start
                    candidate_benefit = sum(weights[tuple(edge)] for edge in result["graph"]["edges"])
                    regret = Fraction(benefit - candidate_benefit, denominator)
                    if regret < 0:
                        raise ArithmeticError("candidate exceeds exact optimum")
                    if result.get("status") == "structurally-exact-tree" and regret != 0:
                        raise ArithmeticError("deterministic exact claim is false")
                    methods[method] = {"result": result, "exactRegret": str(regret),
                                       "covered": regret <= Fraction(result["confidenceRegretBoundExact"]),
                                       "timing": {"totalAlgorithmSeconds": seconds}}
                hybrid, baseline = methods["hybrid-v2"]["result"], methods["frontier-v1"]["result"]
                if hybrid["operations"]["trajectories"] and hybrid["pairCounts"] != baseline["pairCounts"]:
                    raise ArithmeticError("paired nonforced algorithms received different samples")
                case["trials"].append({"sampleSeed": sample_seed, "methods": methods})
            cases.append(case)
            print(f"completed hybrid {regime['name']} environment {environment_seed}", flush=True)
    return {"cases": cases, "summary": _summary(plan, cases)}


def _metrics(data):
    regret = mean(Fraction(result["exactRegret"]) for _, result in data)
    bound = max(Fraction(result["result"]["confidenceRegretBoundExact"]) for _, result in data)
    return {"trials": len(data), "meanExactRegret": float(regret), "meanExactRegretExact": str(regret),
            "meanRegretOverPayoffRange": mean(float(Fraction(result["exactRegret"]) / Fraction(row["exact"]["payoffRange"])) for row, result in data),
            "maximumConfidenceBound": max(result["result"]["confidenceRegretBound"] for _, result in data),
            "maximumConfidenceBoundExact": str(bound),
            "coverageViolations": sum(not result["covered"] for _, result in data),
            "deterministicExact": sum(result["result"].get("status") == "structurally-exact-tree" for _, result in data),
            "measuredExactOptima": sum(Fraction(result["exactRegret"]) == 0 for _, result in data),
            "trajectories": sum(result["result"]["operations"]["trajectories"] for _, result in data),
            "integerDraws": sum(result["result"]["operations"]["integerDraws"] for _, result in data),
            "medianAlgorithmSeconds": median(result["timing"]["totalAlgorithmSeconds"] for _, result in data),
            "medianSpeedup": median(median(row["timing"]["exactConstructionSeconds"]) / result["timing"]["totalAlgorithmSeconds"] for row, result in data)}


def _summary(plan, cases):
    groups = []
    for regime in plan["regimes"]:
        for method in plan["methods"]:
            data = [(row, trial["methods"][method]) for row in cases if row["regime"] == regime["name"] for trial in row["trials"]]
            groups.append({"regime": regime["name"], "method": method, **_metrics(data)})
    primary = plan["primary"]
    data = [(row, trial["methods"][primary["method"]]) for row in cases if row["regime"] in primary["regimes"] for trial in row["trials"]]
    metrics = _metrics(data)
    accepted = (Fraction(metrics["meanExactRegretExact"]) <= Fraction(str(primary["maximumMeanExactRegret"]))
                and Fraction(metrics["maximumConfidenceBoundExact"]) <= Fraction(str(primary["maximumEveryConfidenceBound"]))
                and metrics["medianSpeedup"] >= primary["minimumMedianSpeedup"])
    return {"primarySuccess": accepted, "primaryMetrics": metrics, "groups": groups, "interpretation": plan["interpretation"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "replay"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan, identities = _plan(), _identities()
        if args.mode == "run":
            args.out.mkdir(parents=True, exist_ok=False)
            manifest = {"contract": "algal.lab.terminal-hybrid-run.v1", "protocol": plan, "protocolDigest": _digest(plan),
                        "sourceIdentities": identities,
                        "runtime": {"python": sys.version, "platform": platform.platform(), "machine": platform.machine()},
                        "randomness": "Paired Python Random streams from fresh SHA-256-derived seeds; numerical reproduction, not IID proof"}
            _write_new(args.out / "manifest.json", manifest)
            result = _calculate(plan)
            if _identities() != identities:
                raise ValueError("instrument changed during run")
            _write_new(args.out / "results.json", result)
            print(_canonical(result["summary"]))
        else:
            manifest = _read_json(args.out / "manifest.json")
            if type(manifest) is not dict or set(manifest) != {"contract", "protocol", "protocolDigest", "sourceIdentities", "runtime", "randomness"} or manifest["contract"] != "algal.lab.terminal-hybrid-run.v1":
                raise ValueError("invalid hybrid manifest")
            if manifest["protocol"] != plan or manifest["protocolDigest"] != _digest(plan) or manifest["sourceIdentities"] != identities:
                raise ValueError("hybrid source/protocol mismatch")
            recorded = _read_json(args.out / "results.json")
            if type(recorded) is not dict or set(recorded) != {"cases", "summary"} or type(recorded["cases"]) is not list or len(recorded["cases"]) != 24 or type(recorded["summary"]) is not dict:
                raise ValueError("invalid hybrid result archive")
            reproduced = _calculate(plan)
            if _without_timings(recorded["cases"]) != _without_timings(reproduced["cases"]):
                raise ValueError("fresh hybrid numerical reproduction mismatch")
            if _summary(plan, recorded["cases"]) != recorded["summary"]:
                raise ValueError("hybrid summary mismatch")
            if _identities() != identities:
                raise ValueError("instrument changed during replay")
            receipt = {"contract": "algal.lab.terminal-hybrid-reproduction.v1", "status": "matched",
                       "caseCount": 24, "sourceIdentities": identities,
                       "recordedResultsSha256": sha256((args.out / "results.json").read_bytes()).hexdigest(),
                       "timingsReproduced": False,
                       "interpretation": "Fresh paired sampling and exact numerical outcomes match; not IID or novelty authentication."}
            _write_new(args.out / "reproduction.json", receipt)
            print(_canonical(receipt))
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as error:
        print(f"hybrid experiment: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
