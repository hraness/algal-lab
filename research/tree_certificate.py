"""Exact regret certificates for weighted random failures of a candidate tree.

Run ``python3 research/tree_certificate.py input.json``. The admitted JSON shape
is exactly {graph: {nodes, edges}, environment: {weights, values}, steps}.
This certifies the laboratory's tree objective, not arbitrary graph budgets.
No inference, network access, third-party modules, or output files are used.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys


MAX_INPUT_BYTES = 128 * 1024
CONTRACT = "algal.lab.tree-certificate.v1"
BOUND_METHOD = "rooted-forest-pair-survival; surviving-value ceiling; exact one-failure optimum"


def _object(value: object, keys: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != keys:
        raise ValueError(f"{label}: requires exactly {', '.join(sorted(keys))}")
    return value


def _integer(value: object, minimum: int, maximum: int, label: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{label}: requires an integer in {minimum}..{maximum}")
    return value


def admit(value: object) -> dict:
    """Validate all external fields and copy to a canonical, bounded input."""
    top = _object(value, {"graph", "environment", "steps"}, "input")
    graph = _object(top["graph"], {"nodes", "edges"}, "graph")
    nodes = _integer(graph["nodes"], 4, 10, "graph.nodes")
    steps = _integer(top["steps"], 1, nodes - 2, "steps")
    if type(graph["edges"]) is not list or len(graph["edges"]) != nodes - 1:
        raise ValueError("graph.edges: requires exactly nodes-1 edges")
    edges = []
    seen = set()
    neighbors = [set() for _ in range(nodes)]
    for edge in graph["edges"]:
        if type(edge) is not list or len(edge) != 2:
            raise ValueError("graph.edges: each edge must be a two-entry array")
        a, b = sorted(_integer(node, 0, nodes - 1, "graph edge vertex") for node in edge)
        if a == b or (a, b) in seen:
            raise ValueError("graph.edges: self-loops and duplicate undirected edges are forbidden")
        seen.add((a, b))
        edges.append([a, b])
        neighbors[a].add(b)
        neighbors[b].add(a)
    reached = {0}
    pending = [0]
    while pending:
        node = pending.pop()
        for neighbor in neighbors[node] - reached:
            reached.add(neighbor)
            pending.append(neighbor)
    if len(reached) != nodes:
        raise ValueError("graph: must be connected (with nodes-1 edges, hence a tree)")
    env = _object(top["environment"], {"weights", "values"}, "environment")
    admitted_env = {}
    for field in ("weights", "values"):
        entries = env[field]
        if type(entries) is not list or len(entries) != nodes:
            raise ValueError(f"environment.{field}: requires exactly {nodes} entries")
        admitted_env[field] = [_integer(entry, 1, 99, f"environment.{field}") for entry in entries]
    return {"graph": {"nodes": nodes, "edges": sorted(edges)}, "environment": admitted_env, "steps": steps}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON objects must not repeat a key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"JSON non-finite number {value} is forbidden")


def read_input(path: str | Path) -> dict:
    """Read at most 128 KiB of UTF-8 JSON, rejecting duplicate object fields."""
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError("input file exceeds 128 KiB")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except RecursionError:
        raise ValueError("JSON nesting exceeds the parser's bounded recursion limit") from None
    return admit(value)


def _largest_value(active: int, neighbors: list[list[int]], values: list[int]) -> int:
    unseen = {node for node in range(len(values)) if active & (1 << node)}
    best = 0
    while unseen:
        pending = [unseen.pop()]
        component_value = 0
        while pending:
            node = pending.pop()
            component_value += values[node]
            for neighbor in neighbors[node]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    pending.append(neighbor)
        best = max(best, component_value)
    return best


def _integral(trajectory: list[Fraction]) -> Fraction:
    steps = len(trajectory) - 1
    return (trajectory[0] + trajectory[-1] + 2 * sum(trajectory[1:-1])) / (2 * steps)


def certify(value: object) -> dict:
    """Return an exact upper bound on global tree regret, never a sampled claim.

    For any tree rooted at a minimum-failure-weight c and each survivor set A,
    L(A) <= max_{i in A} v_i + sum_{j!=c} v_j 1[parent(j),j in A]. Pair-survival
    monotonicity bounds each parent term by q(c,j). This gives the returned
    rooted-forest upper bound, whether or not c is a maximum-value vertex.
    The graph-independent surviving-value ceiling and exact one-failure tree
    optimum provide additional valid bounds. Integrating per-step bounds with
    nonnegative trapezoid coefficients bounds the optimum of the complete AUC.
    """
    admitted = admit(value)
    graph = admitted["graph"]
    nodes = graph["nodes"]
    steps = admitted["steps"]
    weights = admitted["environment"]["weights"]
    values = admitted["environment"]["values"]
    total_weight = sum(weights)
    total_value = sum(values)
    root = min(range(nodes), key=lambda i: (weights[i], -values[i], i))
    neighbors = [[] for _ in range(nodes)]
    for a, b in graph["edges"]:
        neighbors[a].append(b)
        neighbors[b].append(a)

    size = 1 << nodes
    full = size - 1
    removed_weights = [0] * size
    mask_values = [0] * size
    probability = [Fraction(0)] * size
    probability[0] = Fraction(1)
    for mask in range(1, size):
        bit = mask & -mask
        node = bit.bit_length() - 1
        prior = mask ^ bit
        removed_weights[mask] = removed_weights[prior] + weights[node]
        mask_values[mask] = mask_values[prior] + values[node]
        if mask.bit_count() > steps:
            continue
        remaining = mask
        while remaining:
            removed_bit = remaining & -remaining
            removed_node = removed_bit.bit_length() - 1
            previous = mask ^ removed_bit
            probability[mask] += probability[previous] * Fraction(weights[removed_node], total_weight - removed_weights[previous])
            remaining ^= removed_bit

    candidate = [Fraction(0)] * (steps + 1)
    ceiling = [Fraction(0)] * (steps + 1)
    forest = [Fraction(0)] * (steps + 1)
    mass = [Fraction(0)] * (steps + 1)
    for removed in range(size):
        count = removed.bit_count()
        if count > steps:
            continue
        active = full ^ removed
        p = probability[removed]
        surviving_value = mask_values[active]
        maximum = max(values[i] for i in range(nodes) if active & (1 << i))
        forest_value = maximum + (surviving_value - values[root] if active & (1 << root) else 0)
        candidate[count] += p * Fraction(_largest_value(active, neighbors, values), total_value)
        ceiling[count] += p * Fraction(surviving_value, total_value)
        forest[count] += p * Fraction(forest_value, total_value)
        mass[count] += p
    if any(value != 1 for value in mass):
        raise ArithmeticError("removed-set probabilities failed exact normalization")

    best_fragmentation = min(weights[c] * (total_value - values[c] - max(values[j] for j in range(nodes) if j != c))
                             for c in range(nodes))
    removed_value = sum(weight * value for weight, value in zip(weights, values))
    first_optimum = 1 - Fraction(removed_value + best_fragmentation, total_weight * total_value)
    upper = [min(a, b) for a, b in zip(ceiling, forest)]
    upper[0] = Fraction(1)
    upper[1] = min(upper[1], first_optimum)
    if any(candidate[k] > upper[k] for k in range(steps + 1)):
        raise ArithmeticError("candidate exceeds a claimed exact upper bound")
    candidate_auc = _integral(candidate)
    optimum_bound = _integral(upper)
    regret_bound = optimum_bound - candidate_auc
    trajectory = []
    for step in range(steps + 1):
        row = {
            "step": step,
            "candidateExpectedService": str(candidate[step]),
            "survivingValueCeiling": str(ceiling[step]),
            "rootedForestUpperBound": str(forest[step]),
            "treeOptimumServiceUpperBound": str(upper[step]),
        }
        if step == 1:
            row["exactOneFailureOptimumService"] = str(first_optimum)
        trajectory.append(row)
    return {
        "contract": CONTRACT,
        "scope": "Connected labeled trees; network.v2 weighted random removal; normalized trapezoidal AUC",
        "arithmetic": "exact rational; rational fields are canonical Fraction strings",
        "input": admitted,
        "boundMethod": BOUND_METHOD,
        "boundRoot": root,
        "status": "optimal" if regret_bound == 0 else "bounded",
        "candidateAuc": str(candidate_auc),
        "treeOptimumUpperBound": str(optimum_bound),
        "additiveRegretUpperBound": str(regret_bound),
        "trajectory": trajectory,
        "interpretation": "The true best-tree AUC minus candidate AUC is between zero and additiveRegretUpperBound. A positive bound does not prove suboptimality.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to a JSON input file of at most 128 KiB")
    args = parser.parse_args(argv)
    try:
        result = certify(read_input(args.input))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"tree certificate: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
