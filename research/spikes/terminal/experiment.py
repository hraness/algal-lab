"""Frozen terminal-tree experiment; no inference, network access, or code search.

python3 -m research.spikes.terminal.experiment run --out research/spikes/terminal/runs/v1
python3 -m research.spikes.terminal.experiment replay --out research/spikes/terminal/runs/v1

New runs refuse existing directories. Replay repeats the seeded generation and
all numerical calculations, compares timing-free evidence, and writes one new
reproduction receipt. It does not establish the IID premise or prior-art novelty.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
from random import Random
from statistics import mean, median
import sys
from time import perf_counter

from research.terminal_sampling import _draw_pair_counts, optimize_counts
from research.terminal_tree import PairProbabilities, admit_environment, frontier_tree, maximum_spanning_tree


ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = Path(__file__).with_name("protocol.json")
SOURCES = ["research/terminal_tree.py", "research/terminal_sampling.py",
           "research/spikes/terminal/experiment.py", "research/spikes/terminal/protocol.json"]
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return sha256(_canonical(value).encode()).hexdigest()


def _identities():
    return {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES}


def _read_json(path, limit=MAX_ARCHIVE_BYTES):
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("archive exceeds bounded input size")

    def object_hook(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"nonfinite JSON number {value}")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=object_hook, parse_constant=invalid)
    except RecursionError:
        raise ValueError("JSON nesting exceeds parser limit") from None


def _plan():
    plan = _read_json(PLAN_PATH, 64 * 1024)
    # This is a single fixed instrument, not an arbitrary plan interpreter.
    expected = {
        "contract", "endpoint", "environmentSeeds", "sampleSeeds", "sampleBudgets", "methods",
        "familyDelta", "regimes", "exactTimingRepeats", "randomTreeReferences", "referenceNodes", "referenceSeeds",
        "referenceTimingRepeats", "primary", "interpretation",
    }
    if type(plan) is not dict or set(plan) != expected or plan["contract"] != "algal.lab.terminal-comparison-plan.v1":
        raise ValueError("unrecognized terminal experiment plan")
    for key, count in (("environmentSeeds", 4), ("sampleSeeds", 2), ("referenceSeeds", 2)):
        seeds = plan[key]
        if type(seeds) is not list or len(seeds) != count or any(type(x) is not int or not 0 <= x < 2**32 for x in seeds) or len(set(seeds)) != count:
            raise ValueError(f"invalid {key}")
    if (plan["sampleBudgets"] != [128, 512, 2048, 8192] or plan["methods"] != ["kruskal", "frontier"]
            or plan["familyDelta"] != .05 or plan["exactTimingRepeats"] != 3
            or plan["randomTreeReferences"] != 32
            or plan["referenceNodes"] != [8, 12, 16] or plan["referenceTimingRepeats"] != 2):
        raise ValueError("fixed experiment budgets changed; admit a new instrument version")
    expected_regimes = [
        {"name": f"{name}-{n}", "nodes": n, "rateCeiling": ceiling, "profile": profile}
        for name, ceiling, profile in (("small-rates", 5, "independent"), ("wide-rates", 99, "independent"),
                                       ("frontier", 99, "full-frontier")) for n in (24, 64)
    ]
    if plan["regimes"] != expected_regimes:
        raise ValueError("regimes differ from the bounded registered instrument")
    expected_primary = {"regimes": ["wide-rates-64", "frontier-64"], "method": "frontier", "samples": 2048,
                        "maximumMeanExactRegret": .001, "maximumEveryConfidenceBound": .01, "minimumMedianSpeedup": 2}
    if plan["primary"] != expected_primary:
        raise ValueError("primary acceptance criteria changed")
    return plan


def _seed(*parts):
    return int.from_bytes(sha256(_canonical(parts).encode()).digest(), "big")


def _environment(regime, seed):
    rng = Random(_seed("terminal-environment-v1", regime["name"], seed))
    n = regime["nodes"]
    if regime["profile"] == "independent":
        weights = [rng.randint(1, regime["rateCeiling"]) for _ in range(n)]
        values = [rng.randint(1, 99) for _ in range(n)]
    else:
        weights = sorted(rng.sample(range(1, regime["rateCeiling"] + 1), n))
        values = sorted(rng.sample(range(1, 257), n))
        labels = list(range(n))
        rng.shuffle(labels)
        weights, values = [weights[i] for i in labels], [values[i] for i in labels]
    return admit_environment({"weights": weights, "values": values})


def _subset_reference(weights):
    """Independent exact deletion-state DP; O(n 2^n), bounded to n<=16."""
    n = len(weights)
    if not 2 <= n <= 16:
        raise ValueError("reference DP requires 2..16 nodes")
    size, total = 1 << n, sum(weights)
    removed_weight = [0] * size
    probability = [Fraction(0) for _ in range(size)]
    probability[0] = Fraction(1)
    transitions = 0
    for removed in range(size):
        if removed:
            bit = removed & -removed
            removed_weight[removed] = removed_weight[removed ^ bit] + weights[bit.bit_length() - 1]
        if removed.bit_count() > n - 2:
            continue
        if removed:
            pending = removed
            while pending:
                bit = pending & -pending
                previous = removed ^ bit
                probability[removed] += probability[previous] * Fraction(weights[bit.bit_length() - 1], total - removed_weight[previous])
                transitions += 1
                pending ^= bit
    full = size - 1
    result = {(i, j): probability[full ^ (1 << i) ^ (1 << j)] for i, j in combinations(range(n), 2)}
    if sum(result.values()) != 1:
        raise ArithmeticError("independent DP failed normalization")
    return result, {"allocatedSubsetStates": size, "probabilityTransitions": transitions}


def _distribution(weights):
    probabilities = PairProbabilities(weights)
    result = {(i, j): Fraction(probabilities.numerator(i, j), probabilities.denominator)
              for i, j in combinations(range(len(weights)), 2)}
    return result, {"pairIntegrations": probabilities.integrations,
                    "coefficientWorkBound": probabilities.coefficient_work_bound}


def _prufer_tree(nodes, rng):
    code = [rng.randrange(nodes) for _ in range(nodes - 2)]
    degree = [1] * nodes
    for node in code:
        degree[node] += 1
    edges = []
    for node in code:
        leaf = next(i for i in range(nodes) if degree[i] == 1)
        edges.append(tuple(sorted((leaf, node))))
        degree[node] -= 1
        degree[leaf] -= 1
    edges.append(tuple(i for i in range(nodes) if degree[i] == 1))
    return sorted(edges)


def _reference_panel(plan):
    rows = []
    for n in plan["referenceNodes"]:
        for seed in plan["referenceSeeds"]:
            rng = Random(_seed("terminal-dp-reference-v1", n, seed))
            weights = [rng.randint(1, 5) for _ in range(n)]
            times = {"polynomial": [], "subset": []}
            outputs = {}
            for repeat in range(plan["referenceTimingRepeats"]):
                # Alternate order; no host isolation or library-superiority claim.
                order = ("polynomial", "subset") if repeat % 2 == 0 else ("subset", "polynomial")
                for method in order:
                    start = perf_counter()
                    outputs[method] = (_distribution if method == "polynomial" else _subset_reference)(weights)
                    times[method].append(perf_counter() - start)
            if outputs["polynomial"][0] != outputs["subset"][0]:
                raise ArithmeticError("polynomial and independent subset probabilities disagree")
            rows.append({"nodes": n, "seed": seed, "weights": weights,
                         "probabilityDigest": _digest([[i, j, str(q)] for (i, j), q in outputs["subset"][0].items()]),
                         "work": {key: value[1] for key, value in outputs.items()}, "timing": times})
    return rows


def _cases(plan):
    rows = []
    certificates = len(plan["regimes"]) * len(plan["environmentSeeds"]) * len(plan["sampleSeeds"]) * len(plan["sampleBudgets"]) * len(plan["methods"])
    delta = plan["familyDelta"] / certificates
    for regime in plan["regimes"]:
        for seed in plan["environmentSeeds"]:
            env = _environment(regime, seed)
            n, values = regime["nodes"], env["values"]
            exact_times = []
            for _ in range(plan["exactTimingRepeats"]):
                start = perf_counter()
                p = PairProbabilities(env["weights"])
                tree, frontier, comparisons = frontier_tree(env, p)
                exact_times.append(perf_counter() - start)
            construction_integrations = p.integrations
            pairs = list(combinations(range(n), 2))
            # Full exact numerical evaluation is deliberately outside timing of
            # BOTH algorithms' construction. It is shared experimental ground truth.
            numerators = {pair: p.numerator(*pair) for pair in pairs}
            if sum(numerators.values()) != p.denominator:
                raise ArithmeticError("exact pair mass failed normalization")
            edge_weights = {pair: q * min(values[pair[0]], values[pair[1]]) for pair, q in numerators.items()}
            optimum_benefit = sum(edge_weights[edge] for edge in tree)
            kruskal = maximum_spanning_tree(n, edge_weights)
            if sum(edge_weights[edge] for edge in kruskal) != optimum_benefit:
                raise ArithmeticError("frontier tree differs from generic exact Kruskal optimum")
            denominator = p.denominator * sum(values)
            base = sum(numerators[pair] * max(values[pair[0]], values[pair[1]]) for pair in pairs)
            stars = [sum(weight for pair, weight in edge_weights.items() if center in pair) for center in range(n)]
            reliable_center = min(range(n), key=lambda i: (env["weights"][i], -values[i], i))
            rng = Random(_seed("terminal-prufer-references-v1", regime["name"], seed))
            random_trees = [_prufer_tree(n, rng) for _ in range(plan["randomTreeReferences"])]
            row = {"regime": regime["name"], "environmentSeed": seed, "environment": env,
                   "exact": {"edges": tree, "frontier": frontier,
                             "expectedService": str(Fraction(base + optimum_benefit, denominator)),
                             "edgeBenefit": str(Fraction(optimum_benefit, denominator)),
                             "payoffRange": str(Fraction(sorted(values)[-2], sum(values))),
                             "bestStarRegret": str(Fraction(optimum_benefit - max(stars), denominator)),
                             "reliableStarCenter": reliable_center,
                             "reliableStarRegret": str(Fraction(optimum_benefit - stars[reliable_center], denominator)),
                             "constructionPairIntegrations": construction_integrations,
                             "fullEvaluationPairIntegrations": p.integrations,
                             "constructionEdgeEvaluations": comparisons,
                             "coefficientWorkBound": p.coefficient_work_bound},
                   "randomTreeReferences": [{"edges": graph,
                       "exactRegret": str(Fraction(optimum_benefit - sum(edge_weights[edge] for edge in graph), denominator))}
                       for graph in random_trees],
                   "timing": {"exactConstructionSeconds": exact_times}, "trials": []}
            for sample_seed in plan["sampleSeeds"]:
                for samples in plan["sampleBudgets"]:
                    rng = Random(_seed("terminal-histogram-v1", regime["name"], seed, sample_seed, samples))
                    start = perf_counter()
                    counts, operations = _draw_pair_counts(env["weights"], samples, rng.randrange)
                    draw_seconds = perf_counter() - start
                    methods = {}
                    # Alternate method order across sample seeds to reduce a fixed order effect.
                    order = plan["methods"] if sample_seed == plan["sampleSeeds"][0] else list(reversed(plan["methods"]))
                    for method in order:
                        start = perf_counter()
                        result = optimize_counts(env, counts, delta, method=method)
                        analysis_seconds = perf_counter() - start
                        selected_benefit = sum(edge_weights[tuple(edge)] for edge in result["graph"]["edges"])
                        regret = Fraction(optimum_benefit - selected_benefit, denominator)
                        if regret < 0:
                            raise ArithmeticError("sampled tree exceeds exact optimum")
                        methods[method] = {"result": result, "exactRegret": str(regret),
                                           "covered": regret <= Fraction(result["confidenceRegretBoundExact"]),
                                           "timing": {"selectionAndCertificateSeconds": analysis_seconds,
                                                      "totalAlgorithmSeconds": draw_seconds + analysis_seconds}}
                    row["trials"].append({"sampleSeed": sample_seed, "samples": samples,
                                          "counts": counts, "drawOperations": operations,
                                          "timing": {"drawSeconds": draw_seconds}, "methods": methods})
            rows.append(row)
            print(f"completed {regime['name']} environment {seed}", flush=True)
    return rows


def _summary(plan, cases, references):
    groups = []
    for regime in plan["regimes"]:
        rows = [row for row in cases if row["regime"] == regime["name"]]
        for samples in plan["sampleBudgets"]:
            for method in plan["methods"]:
                data = [(row, trial["methods"][method]) for row in rows for trial in row["trials"] if trial["samples"] == samples]
                groups.append({"regime": regime["name"], "samples": samples, "method": method, "trials": len(data),
                               "meanExactRegret": mean(float(Fraction(result["exactRegret"])) for _, result in data),
                               "meanRegretOverPayoffRange": mean(float(Fraction(result["exactRegret"]) / Fraction(row["exact"]["payoffRange"])) for row, result in data),
                               "maximumExactRegret": max(float(Fraction(result["exactRegret"])) for _, result in data),
                               "maximumConfidenceBound": max(result["result"]["confidenceRegretBound"] for _, result in data),
                               "coverageViolations": sum(not result["covered"] for _, result in data),
                               "exactOptima": sum(Fraction(result["exactRegret"]) == 0 for _, result in data),
                               "medianAlgorithmSeconds": median(result["timing"]["totalAlgorithmSeconds"] for _, result in data),
                               "medianSpeedup": median(median(row["timing"]["exactConstructionSeconds"]) / result["timing"]["totalAlgorithmSeconds"] for row, result in data)})
    primary = plan["primary"]
    data = [(row, trial["methods"][primary["method"]]) for row in cases if row["regime"] in primary["regimes"]
            for trial in row["trials"] if trial["samples"] == primary["samples"]]
    exact_mean_regret = mean(Fraction(result["exactRegret"]) for _, result in data)
    exact_maximum_bound = max(Fraction(result["result"]["confidenceRegretBoundExact"]) for _, result in data)
    primary_metrics = {
        "meanExactRegret": float(exact_mean_regret),
        "meanExactRegretExact": str(exact_mean_regret),
        "maximumConfidenceBound": max(result["result"]["confidenceRegretBound"] for _, result in data),
        "maximumConfidenceBoundExact": str(exact_maximum_bound),
        "medianSpeedup": median(median(row["timing"]["exactConstructionSeconds"]) / result["timing"]["totalAlgorithmSeconds"] for row, result in data),
    }
    primary_success = (exact_mean_regret <= Fraction(str(primary["maximumMeanExactRegret"]))
                       and exact_maximum_bound <= Fraction(str(primary["maximumEveryConfidenceBound"]))
                       and primary_metrics["medianSpeedup"] >= primary["minimumMedianSpeedup"])
    return {"primarySuccess": primary_success, "primaryMetrics": primary_metrics, "groups": groups,
            "referenceTimings": [{"nodes": row["nodes"], "seed": row["seed"],
                                   "polynomialSeconds": median(row["timing"]["polynomial"]),
                                   "subsetSeconds": median(row["timing"]["subset"]),
                                   "speedup": median(row["timing"]["subset"]) / median(row["timing"]["polynomial"])} for row in references],
            "interpretation": plan["interpretation"]}


def _without_timings(value):
    if type(value) is dict:
        return {key: _without_timings(item) for key, item in value.items() if key != "timing"}
    if type(value) in (list, tuple):
        return [_without_timings(item) for item in value]
    return value


def _calculate(plan):
    references = _reference_panel(plan)
    cases = _cases(plan)
    return {"references": references, "cases": cases, "summary": _summary(plan, cases, references)}


def _write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "replay"))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        plan, identities = _plan(), _identities()
        if args.mode == "run":
            args.out.mkdir(parents=True, exist_ok=False)
            manifest = {"contract": "algal.lab.terminal-comparison-run.v1", "protocol": plan,
                        "protocolDigest": _digest(plan), "sourceIdentities": identities,
                        "runtime": {"python": sys.version, "platform": platform.platform(), "machine": platform.machine()},
                        "randomness": "Python Random with SHA-256-derived fixed seeds; numerical replay, not proof of IID"}
            _write_new(args.out / "manifest.json", manifest)
            output = _calculate(plan)
            if _identities() != identities:
                raise ValueError("instrument changed while experiment ran")
            _write_new(args.out / "results.json", output)
            print(_canonical(output["summary"]))
        else:
            manifest = _read_json(args.out / "manifest.json")
            if type(manifest) is not dict or set(manifest) != {"contract", "protocol", "protocolDigest", "sourceIdentities", "runtime", "randomness"} or manifest["contract"] != "algal.lab.terminal-comparison-run.v1":
                raise ValueError("invalid run manifest")
            if manifest.get("sourceIdentities") != identities or manifest.get("protocol") != plan or manifest.get("protocolDigest") != _digest(plan):
                raise ValueError("replay source/protocol mismatch")
            recorded = _read_json(args.out / "results.json")
            if type(recorded) is not dict or set(recorded) != {"references", "cases", "summary"} or type(recorded["references"]) is not list or len(recorded["references"]) != 6 or type(recorded["cases"]) is not list or len(recorded["cases"]) != 24 or type(recorded["summary"]) is not dict:
                raise ValueError("invalid bounded result archive")
            reproduced = _calculate(plan)
            for field in ("references", "cases"):
                if _without_timings(recorded[field]) != _without_timings(reproduced[field]):
                    raise ValueError(f"fresh numerical reproduction mismatch in {field}")
            if _summary(plan, recorded["cases"], recorded["references"]) != recorded["summary"]:
                raise ValueError("recorded summary does not match its rows")
            if _identities() != identities:
                raise ValueError("instrument changed while replay ran")
            receipt = {"contract": "algal.lab.terminal-reproduction.v1", "status": "matched",
                       "sourceIdentities": identities, "recordedResultsSha256": sha256((args.out / "results.json").read_bytes()).hexdigest(),
                       "caseCount": len(recorded["cases"]), "referenceCount": len(recorded["references"]),
                       "timingsReproduced": False, "interpretation": "Fresh seeded sampling and exact calculations match; no IID, authorship, or novelty authentication."}
            _write_new(args.out / "reproduction.json", receipt)
            print(_canonical(receipt))
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as error:
        print(f"terminal experiment: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
