"""Structural terminal-tree proposals with a restricted-family regret bound.

The exact optimum has an ordered Pareto-frontier core and frontier-attached
leaves. A leaf only needs the frontier prefix through its first member whose
value reaches the leaf's value. Each remaining parent decision is independent
of the other decisions. Singleton decisions require no pair probabilities.

For fixed N, simultaneous binomial KL intervals cover only edges in decisions
with at least two alternatives. Shared selected edges cancel in the regret
comparison. No simplex constraint is imposed on this strict subset of pairs.
The probability guarantee requires IID unbiased integer draws; fixed seeds
provide numerical reproduction, not a proof of that premise.
"""

from fractions import Fraction
from itertools import combinations
import secrets

from research.terminal_sampling import (
    DYADIC_BITS, DYADIC_DENOMINATOR, MAX_SAMPLES, _KLDyadicIntervals,
    _admit_budget, _draw_pair_counts, _upward_float,
)
from research.terminal_tree import admit_environment, pareto_frontier


CONTRACT = "algal.lab.terminal-hybrid.v1"


def _choice_groups(environment):
    """Return the fixed environment-defined family, before observing counts."""
    values = environment["values"]
    frontier = pareto_frontier(environment)
    frontier_set = set(frontier)
    groups = [(node, frontier[:index]) for index, node in enumerate(frontier) if index]
    for node in range(len(values)):
        if node not in frontier_set:
            # Every nonfrontier point has a frontier dominator, so this exists.
            stop = next(index for index, parent in enumerate(frontier) if values[parent] >= values[node])
            groups.append((node, frontier[:stop + 1]))
    return frontier, groups


def _edge(node, parent):
    return (min(node, parent), max(node, parent))


def _group_regret_bound(values, groups, selected, intervals):
    """Exact confidence-box bound, with each selected edge cancelling itself."""
    numerator = 0
    for (node, parents), chosen in zip(groups, selected):
        if len(parents) == 1:
            continue
        lower = min(values[i] for i in chosen) * intervals[chosen][0]
        numerator += max([0] + [
            min(values[i] for i in edge) * intervals[edge][1] - lower
            for parent in parents if (edge := _edge(node, parent)) != chosen
        ])
    return min(Fraction(numerator, sum(values) * DYADIC_DENOMINATOR),
               Fraction(sorted(values)[-2], sum(values)))


def optimize_hybrid_counts(environment, counts, delta=.05):
    """Choose parents from one complete lexicographic terminal-pair histogram.

Zero samples are admitted only when every structural decision is forced. A
histogram cannot establish its IID origin. Delta uses its round-trip decimal
string, as in the frozen sampler.
"""
    environment = admit_environment(environment)
    values, n = environment["values"], len(environment["weights"])
    if type(counts) is not list or len(counts) != n * (n - 1) // 2:
        raise ValueError("counts must include every lexicographic pair")
    if any(type(count) is not int or not 0 <= count <= MAX_SAMPLES for count in counts):
        raise ValueError("each pair count must be an integer in [0,32768]")
    counts = counts[:]
    samples = sum(counts)
    frontier, groups = _choice_groups(environment)
    uncertain = [(node, parents) for node, parents in groups if len(parents) > 1]
    if samples == 0 and uncertain:
        raise ValueError("zero samples require all structural decisions to be forced")
    _admit_budget(n, samples if samples else 1, delta)
    delta_fraction = Fraction(str(delta))
    pairs = list(combinations(range(n), 2))
    histogram = dict(zip(pairs, counts))
    selected = [min((_edge(node, parent) for parent in parents),
                    key=lambda edge: (-histogram[edge] * min(values[i] for i in edge), edge))
                for node, parents in groups]
    relevant = sorted({_edge(node, parent) for node, parents in uncertain for parent in parents})
    engine = _KLDyadicIntervals(samples, len(relevant), delta_fraction) if relevant else None
    intervals = {edge: engine.bounds(histogram[edge]) for edge in relevant}
    bound = _group_regret_bound(values, groups, selected, intervals)
    benefit = (Fraction(sum(histogram[edge] * min(values[i] for i in edge) for edge in selected),
                        samples * sum(values)) if samples else None)
    exact = not uncertain
    return {
        "contract": CONTRACT,
        "input": {"environment": environment, "samples": samples, "requestedSamples": samples,
                  "delta": delta, "deltaExact": str(delta_fraction)},
        "status": "structurally-exact-tree" if exact else "confidence-bounded-tree",
        "graph": {"nodes": n, "edges": [list(edge) for edge in sorted(selected)]},
        "structure": {"paretoFrontier": frontier,
                      "choiceGroups": [{"child": node, "parents": parents} for node, parents in groups],
                      "forcedGroups": len(groups) - len(uncertain), "uncertainGroups": len(uncertain),
                      "relevantPairs": len(relevant)},
        "confidenceRegretBound": _upward_float(bound),
        "confidenceRegretBoundExact": str(bound),
        "empiricalConnectionBenefitExact": str(benefit) if benefit is not None else None,
        "pairCounts": counts,
        "pairCountOrder": "lexicographic pairs (i,j), i<j, including zero counts",
        "operations": {
            "candidateFamilyEdgeComparisons": sum(len(parents) for _, parents in uncertain),
            "forcedParentChoices": len(groups) - len(uncertain),
            "certificateRelevantPairs": len(relevant),
            "distinctCountIntervals": len(engine.cache) if engine else 0,
            "klBoundaryQueries": engine.queries if engine else 0,
            "decimalLogEnclosures": len(engine.logs) - 1 if engine else 0,
        },
        "confidence": {
            "method": "environment-defined frontier-prefix family; simultaneous binomial KL intervals; independent parent regret bounds",
            "dyadicBits": DYADIC_BITS, "decimalPrecision": engine.nearest.prec if engine else 70,
            "coverage": ("Deterministic global tree optimum: all structural choices are forced."
                         if exact else "At least 1-delta for this fixed sample size under independent unbiased integer draws."),
            "source": "no sampling required" if exact else "externally supplied counts; IID origin is not verified",
            "limitations": "A fixed seed is numerical reproduction, not proof of IID sampling. No optional-stopping or multiple-run coverage is claimed.",
            "arithmetic": "Outward Decimal logarithm enclosures, dyadic endpoints, rational group regret; reported float rounds upward. No subset simplex tightening.",
        },
    }


def sample_hybrid_tree(environment, samples, delta=.05, *, randbelow=None):
    """Sample only when the proven optimum family has a nonforced decision."""
    environment = admit_environment(environment)
    n = len(environment["weights"])
    _admit_budget(n, samples, delta)
    if randbelow is not None and not callable(randbelow):
        raise ValueError("randbelow must be callable")
    _, groups = _choice_groups(environment)
    if all(len(parents) == 1 for _, parents in groups):
        result = optimize_hybrid_counts(environment, [0] * (n * (n - 1) // 2), delta)
        operations = {"integerDraws": 0, "fenwickSearchSteps": 0,
                      "fenwickUpdateSteps": 0, "histogramUpdates": 0}
        trajectories = 0
    else:
        source = secrets.randbelow if randbelow is None else randbelow
        counts, operations = _draw_pair_counts(environment["weights"], samples, source)
        result = optimize_hybrid_counts(environment, counts, delta)
        result["confidence"]["source"] = "secrets.randbelow" if randbelow is None else "caller-supplied randbelow"
        trajectories = samples
    result["input"]["requestedSamples"] = samples
    result["operations"].update(operations, trajectories=trajectories, nodesPerTrajectory=n)
    return result
