"""Exact optimal trees when weighted deletion leaves exactly two vertices.

This is a separate terminal endpoint, not the laboratory's trajectory AUC.
Run ``python3 -m research.terminal_tree input.json``; input is exactly
{environment: {weights, values}} with an optional candidate edge list.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from functools import reduce
import json
from math import gcd, isfinite, lcm
from pathlib import Path
import sys


CONTRACT = "algal.lab.terminal-tree.v1"
MAX_INPUT_BYTES = 128 * 1024
MAX_TOTAL_WEIGHT = 8192
MAX_COEFFICIENT_WORK = 40_000_000


def _integer(value: object, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label}: requires an integer in {low}..{high}")
    return value


def admit_environment(value: object) -> dict:
    """Bound the standalone research endpoint; do not change network.v2."""
    if type(value) is not dict or set(value) != {"weights", "values"}:
        raise ValueError("environment: requires exactly weights and values")
    weights, values = value["weights"], value["values"]
    if type(weights) is not list or not 2 <= len(weights) <= 128:
        raise ValueError("weights: requires 2..128 entries")
    if type(values) is not list or len(values) != len(weights):
        raise ValueError("values: requires the same length as weights")
    return {field: [_integer(x, 1, 1_000_000, field) for x in entries]
            for field, entries in (("weights", weights), ("values", values))}


def admit_tree(value: object, nodes: int) -> list[tuple[int, int]]:
    if type(value) is not list or len(value) != nodes - 1:
        raise ValueError("candidate: requires exactly nodes-1 edges")
    parent = list(range(nodes))

    def find(i: int) -> int:
        while parent[i] != i:
            i = parent[i]
        return i

    edges = []
    for edge in value:
        if type(edge) not in (list, tuple) or len(edge) != 2:
            raise ValueError("candidate: each edge must have two vertices")
        a, b = sorted(_integer(i, 0, nodes - 1, "edge vertex") for i in edge)
        ra, rb = find(a), find(b)
        if ra == rb:
            raise ValueError("candidate: loops, duplicates, and cycles are forbidden")
        parent[ra] = rb
        edges.append((a, b))
    return sorted(edges)


def maximum_spanning_tree(nodes: int, edge_weights: dict) -> list[tuple[int, int]]:
    """Kruskal reference, also used by the sampling confidence certificate."""
    _integer(nodes, 2, 128, "nodes")
    if type(edge_weights) is not dict or len(edge_weights) != nodes * (nodes - 1) // 2:
        raise ValueError("edge weights must describe a complete graph")
    for edge, weight in edge_weights.items():
        if (type(edge) is not tuple or len(edge) != 2
                or any(type(i) is not int for i in edge)
                or not 0 <= edge[0] < edge[1] < nodes
                or type(weight) not in (int, float)
                or (type(weight) is float and not isfinite(weight))):
            raise ValueError("invalid weighted edge")
    parent = list(range(nodes))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    result = []
    for (a, b), _ in sorted(edge_weights.items(), key=lambda item: (-item[1], item[0])):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            result.append((a, b))
            if len(result) == nodes - 1:
                return sorted(result)
    raise ArithmeticError("complete graph unexpectedly disconnected")


def _divide_factor(polynomial: list[int], weight: int) -> list[int]:
    # Q_d = P_d + Q_(d-w), since P=(1-x^w)Q. All arithmetic is integer.
    result = [0] * (len(polynomial) - weight)
    for degree in range(len(result)):
        result[degree] = polynomial[degree]
        if degree >= weight:
            result[degree] += result[degree - weight]
    return result


class PairProbabilities:
    """Batched exact Wallenius pair probabilities, with common denominator.

    Let W=sum of gcd-reduced integer rates and D=lcm(1,...,W).
    q_ij=(wi+wj) integral x^(wi+wj-1) product_(k!=i,j)(1-x^wk) dx.
    Integrating coefficients uses only exact divisions D/(wi+wj+d).
    Cache by unordered rate pair; identical rates are exchangeable.
    """

    def __init__(self, weights: list[int]):
        # Reuse strict input admission even for direct library callers.
        if type(weights) is not list:
            raise ValueError("weights: requires a list")
        original = admit_environment({"weights": weights, "values": [1] * len(weights)})["weights"]
        self.gcd = reduce(gcd, original)
        self.weights = [w // self.gcd for w in original]
        self.total_weight = sum(self.weights)
        counts = Counter(self.weights)
        self.types = [(a, b) for a in sorted(counts) for b in sorted(counts)
                      if a < b or (a == b and counts[a] >= 2)]
        self.coefficient_work_bound = (len(weights) + len(counts) + 2 * len(self.types)) * self.total_weight
        if self.total_weight > MAX_TOTAL_WEIGHT or self.coefficient_work_bound > MAX_COEFFICIENT_WORK:
            raise ValueError("exact probability budget exceeded: reduced total weight <=8192 and coefficient work <=40000000 required")
        self.denominator = lcm(*range(1, self.total_weight + 1))
        self._reciprocals = [0] + [self.denominator // i for i in range(1, self.total_weight + 1)]
        polynomial = [1]
        for weight in self.weights:
            previous = len(polynomial)
            polynomial.extend([0] * weight)
            for degree in range(previous - 1, -1, -1):
                polynomial[degree + weight] -= polynomial[degree]
        self.max_coefficient_bits = max(abs(c).bit_length() for c in polynomial)
        self._polynomial = polynomial
        self._single_quotients: dict[int, list[int]] = {}
        self._numerators: dict[tuple[int, int], int] = {}

    def numerator(self, i: int, j: int) -> int:
        if type(i) is not int or type(j) is not int or not 0 <= i < len(self.weights) or not 0 <= j < len(self.weights) or i == j:
            raise ValueError("pair requires two distinct admitted vertex indices")
        a, b = sorted((self.weights[i], self.weights[j]))
        key = (a, b)
        if key not in self._numerators:
            if a not in self._single_quotients:
                self._single_quotients[a] = _divide_factor(self._polynomial, a)
            coefficients = _divide_factor(self._single_quotients[a], b)
            rate = a + b
            numerator = rate * sum(c * self._reciprocals[rate + degree]
                                   for degree, c in enumerate(coefficients) if c)
            if not 0 < numerator <= self.denominator:
                raise ArithmeticError("pair probability is outside (0,1]")
            self._numerators[key] = numerator
        return self._numerators[key]

    @property
    def integrations(self) -> int:
        return len(self._numerators)


def pareto_frontier(environment: dict) -> list[int]:
    """One representative per nondominated (low rate, high value) point."""
    weights, values = environment["weights"], environment["values"]
    frontier = []
    best_value = 0
    for i in sorted(range(len(weights)), key=lambda j: (weights[j], -values[j], j)):
        if values[i] > best_value:
            frontier.append(i)
            best_value = values[i]
    return frontier


def frontier_tree(environment: dict, probabilities: PairProbabilities) -> tuple[list[tuple[int, int]], list[int], int]:
    """Exact ordered-Prim core and best-frontier attachment of other nodes."""
    values = environment["values"]
    frontier = pareto_frontier(environment)
    frontier_set = set(frontier)
    edges = []
    comparisons = 0

    def attach(node: int, choices: list[int]) -> None:
        nonlocal comparisons
        # Canonical endpoint tie-breaking makes replay deterministic.
        parent = min(choices, key=lambda j: (-probabilities.numerator(node, j) * min(values[node], values[j]), j))
        comparisons += len(choices)
        edges.append(tuple(sorted((node, parent))))

    for position in range(1, len(frontier)):
        attach(frontier[position], frontier[:position])
    for node in range(len(values)):
        if node not in frontier_set:
            attach(node, frontier)
    return sorted(edges), frontier, comparisons


def optimize(environment: object, candidate: object | None = None) -> dict:
    """Return a provably optimal tree and optional exact candidate regret."""
    env = admit_environment(environment)
    nodes = len(env["weights"])
    admitted_candidate = admit_tree(candidate, nodes) if candidate is not None else None
    probabilities = PairProbabilities(env["weights"])
    edges, frontier, comparisons = frontier_tree(env, probabilities)
    construction_integrations = probabilities.integrations
    values = env["values"]
    total_value = sum(values)
    base = 0
    mass = 0
    for i in range(nodes):
        for j in range(i + 1, nodes):
            q = probabilities.numerator(i, j)
            mass += q
            base += q * max(values[i], values[j])
    if mass != probabilities.denominator:
        raise ArithmeticError("terminal pair probabilities failed exact normalization")

    def reward(tree: list[tuple[int, int]]) -> int:
        return sum(probabilities.numerator(i, j) * min(values[i], values[j]) for i, j in tree)

    benefit = reward(edges)
    denominator = probabilities.denominator * total_value
    result = {
        "contract": CONTRACT,
        "endpoint": "Expected maximum surviving component value / original total value, after n-2 weighted deletions; not AUC",
        "environment": env,
        "graph": {"nodes": nodes, "edges": [list(edge) for edge in edges]},
        "paretoFrontier": frontier,
        "status": "globally-optimal-tree",
        "expectedService": str(Fraction(base + benefit, denominator)),
        "graphIndependentService": str(Fraction(base, denominator)),
        "edgeBenefit": str(Fraction(benefit, denominator)),
        "proofMethod": "terminal pair decomposition; pair-rate monotonicity; dominance leafification; ordered Prim frontier core",
        "arithmetic": "exact integers and rational output; pseudo-polynomial in gcd-reduced total rate",
        "work": {
            "reducedTotalWeight": probabilities.total_weight,
            "rateGcd": probabilities.gcd,
            "rateClasses": len(set(probabilities.weights)),
            "possiblePairClasses": len(probabilities.types),
            "constructionPairIntegrations": construction_integrations,
            "totalPairIntegrations": probabilities.integrations,
            "constructionEdgeEvaluations": comparisons,
            "coefficientWorkBound": probabilities.coefficient_work_bound,
            "commonDenominatorBits": probabilities.denominator.bit_length(),
            "maximumPolynomialCoefficientBits": probabilities.max_coefficient_bits,
        },
    }
    if admitted_candidate is not None:
        candidate_benefit = reward(admitted_candidate)
        if candidate_benefit > benefit:
            raise ArithmeticError("candidate exceeds claimed optimum")
        gap = benefit - candidate_benefit
        result["candidate"] = {
            "edges": [list(edge) for edge in admitted_candidate],
            "expectedService": str(Fraction(base + candidate_benefit, denominator)),
            "exactRegret": str(Fraction(gap, denominator)),
            "status": "globally-optimal-tree" if gap == 0 else "suboptimal-tree",
        }
    return result


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON objects must not repeat a key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON number {value} is forbidden")


def read_input(path: str | Path) -> dict:
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 128 KiB")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except RecursionError:
        raise ValueError("JSON nesting exceeds the parser recursion limit") from None
    if type(value) is not dict or set(value) not in ({"environment"}, {"environment", "candidate"}):
        raise ValueError("input: requires environment and optional candidate")
    env = admit_environment(value["environment"])
    result = {"environment": env}
    if "candidate" in value:
        result["candidate"] = admit_tree(value["candidate"], len(env["weights"]))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON file, at most 128 KiB")
    args = parser.parse_args(argv)
    try:
        value = read_input(args.input)
        result = optimize(value["environment"], value.get("candidate"))
    except (ValueError, OSError, UnicodeError) as error:
        print(f"terminal tree: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
