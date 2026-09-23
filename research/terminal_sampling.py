"""Bounded terminal-pair sampling and a simultaneous finite-sample certificate.

For a fixed sample size N, each pair count has a Binomial(N, q_e) marginal.
With m pairs and L=ln(2m/delta), Chernoff's two tails and a union bound give
q_e in {q: N kl(count_e/N || q) <= L} for every pair with probability at
least 1-delta. Dependence between different pair counts is harmless.

The guarantee assumes independent unbiased integer draws. The default uses
secrets.randbelow; a supplied seeded generator supports numerical reproduction
but is not, by itself, evidence that the IID premise holds. This is a fixed-N
certificate, not an optional-stopping rule or a guarantee across many runs.

KL endpoints are rounded outward to a dyadic grid using directed Decimal
arithmetic. Decimal.ln is documented to be correctly rounded; its neighboring
representable values enclose the real logarithm. Integer MSTs and Fraction
arithmetic then preserve the enclosure through the regret calculation.
"""
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from itertools import combinations
import math
import secrets

from research.terminal_tree import admit_environment, maximum_spanning_tree, pareto_frontier


MAX_SAMPLES = 32768
MAX_NODE_SAMPLES = 4_194_304
DYADIC_BITS = 40
DYADIC_DENOMINATOR = 1 << DYADIC_BITS


class _KLDyadicIntervals:
    """Outward KL intervals, cached by count rather than by pair identity."""

    def __init__(self, samples, pairs, delta):
        self.samples = samples
        self.pairs = pairs
        self.delta = delta
        self.nearest = Context(prec=70, rounding=ROUND_HALF_EVEN)
        self.down = Context(prec=70, rounding=ROUND_FLOOR)
        self.up = Context(prec=70, rounding=ROUND_CEILING)
        self.logs = {1: (Decimal(0), Decimal(0))}
        self.cache = {}
        self.queries = 0

    def _log(self, integer):
        if integer not in self.logs:
            value = self.nearest.ln(Decimal(integer))
            self.logs[integer] = (self.nearest.next_minus(value), self.nearest.next_plus(value))
        return self.logs[integer]

    def _constant_lower(self, count):
        # N*kl(p || k/D)-ln(2m/delta), excluding the k-dependent terms.
        n = self.samples
        terms = [(count, count), (n-count, n-count), (-n, n),
                 (n, DYADIC_DENOMINATOR), (-1, 2*self.pairs),
                 (-1, self.delta.denominator), (1, self.delta.numerator)]
        result = Decimal(0)
        for coefficient, argument in terms:
            if not coefficient:
                continue
            lower, upper = self._log(argument)
            endpoint = lower if coefficient > 0 else upper
            result = self.down.add(result, self.down.multiply(Decimal(coefficient), endpoint))
        return result

    def _outside(self, count, numerator, constant):
        self.queries += 1
        if numerator == 0:
            return count > 0
        if numerator == DYADIC_DENOMINATOR:
            return count < self.samples
        lower = constant
        for coefficient, argument in ((count, numerator), (self.samples-count, DYADIC_DENOMINATOR-numerator)):
            if coefficient:
                upper_term = self.up.multiply(Decimal(coefficient), self._log(argument)[1])
                lower = self.down.subtract(lower, upper_term)
        # An inconclusive comparison keeps the point: rounding only widens.
        return lower > 0

    def bounds(self, count):
        if count in self.cache:
            return self.cache[count]
        n, denominator = self.samples, DYADIC_DENOMINATOR
        constant = self._constant_lower(count)
        if count == 0:
            lower = 0
        else:
            left, right = 0, (count*denominator+n-1)//n
            while right-left > 1:
                middle = (left+right)//2
                if self._outside(count, middle, constant):
                    left = middle
                else:
                    right = middle
            lower = left
        if count == n:
            upper = denominator
        else:
            left, right = count*denominator//n, denominator
            while right-left > 1:
                middle = (left+right)//2
                if self._outside(count, middle, constant):
                    right = middle
                else:
                    left = middle
            upper = right
        self.cache[count] = (lower, upper)
        return lower, upper


def _draw_pair_counts(weights, samples, randbelow):
    """Exact weighted deletion under unbiased draws; O(N n log n) integer work."""
    n = len(weights)
    template = [0] + list(weights)
    for index in range(1, n+1):
        parent = index + (index & -index)
        if parent <= n:
            template[parent] += template[index]
    original_total = sum(weights)
    counts = [0] * (n*(n-1)//2)
    search_steps = update_steps = draws = 0
    initial_bit = 1 << (n.bit_length()-1)
    for _ in range(samples):
        tree, total, alive = template[:], original_total, (1 << n)-1
        for _ in range(n-2):
            ticket = randbelow(total)
            if type(ticket) is not int or not 0 <= ticket < total:
                raise ValueError("randbelow must return an integer in [0, its argument)")
            draws += 1
            index, bit = 0, initial_bit
            while bit:
                search_steps += 1
                next_index = index+bit
                if next_index <= n and tree[next_index] <= ticket:
                    index = next_index
                    ticket -= tree[index]
                bit >>= 1
            weight = weights[index]
            total -= weight
            alive ^= 1 << index
            position = index+1
            while position <= n:
                update_steps += 1
                tree[position] -= weight
                position += position & -position
        first_bit = alive & -alive
        first = first_bit.bit_length()-1
        second = (alive ^ first_bit).bit_length()-1
        pair_index = first*(2*n-first-1)//2 + second-first-1
        counts[pair_index] += 1
    return counts, {"integerDraws": draws, "fenwickSearchSteps": search_steps,
                    "fenwickUpdateSteps": update_steps, "histogramUpdates": samples}


def _simplex_tighten(intervals):
    """Use the deterministic identity sum(q_e)=1 without spending more alpha."""
    total_lower = sum(lower for lower, _ in intervals)
    total_upper = sum(upper for _, upper in intervals)
    d = DYADIC_DENOMINATOR
    return [(max(lower, d-total_upper+upper), min(upper, d-total_lower+lower))
            for lower, upper in intervals]


def _regret_certificate(values, pairs, candidate, intervals):
    """Exact worst-case regret for a confidence box, capped by the payoff range.

For any competitor T, shared edges cancel in benefit(T)-benefit(candidate).
Put lower weights on candidate edges and upper weights on all other edges.
The maximum spanning tree under those weights maximizes the resulting upper
bound over T. The true pair vector lies in the box on the coverage event.
"""
    candidate = set(map(tuple, candidate))
    weights = {pair: min(values[pair[0]], values[pair[1]]) * (interval[0] if pair in candidate else interval[1])
               for pair, interval in zip(pairs, intervals)}
    optimistic = maximum_spanning_tree(len(values), weights)
    numerator = sum(weights[tuple(pair)] for pair in optimistic) - sum(weights[pair] for pair in candidate)
    if numerator < 0:
        raise ArithmeticError("optimistic tree cannot score below the feasible candidate")
    bound = Fraction(numerator, sum(values)*DYADIC_DENOMINATOR)
    payoff_range = Fraction(sorted(values)[-2], sum(values))
    return min(bound, payoff_range)


def _upward_float(value):
    result = float(value)
    return math.nextafter(result, math.inf) if Fraction.from_float(result) < value else result


def _admit_budget(n, samples, delta):
    if type(samples) is not int or not 1 <= samples <= MAX_SAMPLES or samples*n > MAX_NODE_SAMPLES:
        raise ValueError("samples must be an integer in [1,32768] with samples*nodes <=4194304")
    if type(delta) not in (int, float) or not 1e-6 <= delta <= .25 or not math.isfinite(delta):
        raise ValueError("delta must be finite and in [0.000001,0.25]")


def _candidate(environment, empirical_weights, method):
    n = len(environment["weights"])
    if method == "kruskal":
        return maximum_spanning_tree(n, empirical_weights), len(empirical_weights)
    frontier = pareto_frontier(environment)
    frontier_set = set(frontier)
    edges = []
    comparisons = 0

    def attach(node, choices):
        nonlocal comparisons
        comparisons += len(choices)
        edge = min((tuple(sorted((node, parent))) for parent in choices),
                   key=lambda pair: (-empirical_weights[pair], pair))
        edges.append(edge)

    for index, node in enumerate(frontier[1:], 1):
        attach(node, frontier[:index])
    for node in range(n):
        if node not in frontier_set:
            attach(node, frontier)
    return sorted(edges), comparisons


def optimize_counts(environment, counts, delta=.05, *, method="kruskal"):
    """Optimize one complete lexicographic pair histogram without resampling.

The frontier method maximizes the empirical objective within the ordered
frontier family from the exact solver. Both methods receive the same general
confidence certificate. Histogram admission cannot establish its IID origin.
"""
    environment = admit_environment(environment)
    values, n = environment["values"], len(environment["weights"])
    if type(counts) is not list or len(counts) != n*(n-1)//2:
        raise ValueError("counts must include every lexicographic pair")
    if any(type(count) is not int or not 0 <= count <= MAX_SAMPLES for count in counts):
        raise ValueError("each pair count must be an integer in [0,32768]")
    counts = counts[:]
    samples = sum(counts)
    _admit_budget(n, samples, delta)
    if type(method) is not str or method not in ("kruskal", "frontier"):
        raise ValueError("method must be kruskal or frontier")
    delta_fraction = Fraction(str(delta))
    pairs = list(combinations(range(n), 2))
    empirical_weights = {pair: min(values[pair[0]], values[pair[1]])*count
                         for pair, count in zip(pairs, counts)}
    candidate, comparisons = _candidate(environment, empirical_weights, method)
    interval_engine = _KLDyadicIntervals(samples, len(pairs), delta_fraction)
    intervals = _simplex_tighten([interval_engine.bounds(count) for count in counts])
    bound = _regret_certificate(values, pairs, candidate, intervals)
    benefit = Fraction(sum(empirical_weights[tuple(pair)] for pair in candidate), samples*sum(values))
    operations = {"candidateFamilyEdgeComparisons": comparisons, "certificateMstEdges": len(pairs),
                  "empiricalEdgeWeights": len(pairs), "distinctCountIntervals": len(interval_engine.cache),
                  "klBoundaryQueries": interval_engine.queries, "decimalLogEnclosures": len(interval_engine.logs)-1}
    return {
        "contract": "algal.lab.terminal-sampling.v1",
        "input": {"environment": environment, "samples": samples, "delta": delta,
                  "deltaExact": str(delta_fraction), "method": method},
        "graph": {"nodes": n, "edges": [list(pair) for pair in candidate]},
        "confidenceRegretBound": _upward_float(bound),
        "confidenceRegretBoundExact": str(bound),
        "empiricalConnectionBenefitExact": str(benefit),
        "pairCounts": counts,
        "pairCountOrder": "lexicographic pairs (i,j), i<j, including zero counts",
        "operations": operations,
        "confidence": {"method": "simultaneous binomial KL intervals; simplex tightening; optimistic MST",
                       "dyadicBits": DYADIC_BITS, "decimalPrecision": interval_engine.nearest.prec,
                       "coverage": "At least 1-delta for this fixed sample size under independent unbiased integer draws.",
                       "source": "externally supplied counts; IID origin is not verified",
                       "limitations": "A fixed seed is numerical reproduction, not proof of IID sampling. No optional-stopping or multiple-run coverage is claimed.",
                       "arithmetic": "Outward Decimal logarithm enclosures, dyadic endpoints, integer MST, rational regret; reported float rounds upward."},
    }


def sample_terminal_tree(environment, samples, delta=.05, *, randbelow=None, method="kruskal"):
    """Sample a tree and certify normalized endpoint regret at fixed N.

Environment admission is shared with the exact terminal solver. ``delta`` is
interpreted as its round-trip decimal string. An injected randbelow callback
is trusted to supply randomness; range checks cannot establish independence.
Use optimize_counts on the returned pairCounts to compare methods on one draw.
"""
    environment = admit_environment(environment)
    n = len(environment["weights"])
    _admit_budget(n, samples, delta)
    if type(method) is not str or method not in ("kruskal", "frontier"):
        raise ValueError("method must be kruskal or frontier")
    if randbelow is not None and not callable(randbelow):
        raise ValueError("randbelow must be callable")
    source = secrets.randbelow if randbelow is None else randbelow
    counts, operations = _draw_pair_counts(environment["weights"], samples, source)
    result = optimize_counts(environment, counts, delta, method=method)
    result["operations"].update(operations, trajectories=samples, nodesPerTrajectory=n)
    result["confidence"]["source"] = "secrets.randbelow" if randbelow is None else "caller-supplied randbelow"
    return result
