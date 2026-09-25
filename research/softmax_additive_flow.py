"""Exact, bounded flow optimization for additive softmax task allocation.

This uses the classical successive shortest augmenting path algorithm, with
Bellman--Ford and exact rational arithmetic.  It is not a new flow algorithm.
The continuous-scope claim relies on the positive-weight additive softmax
envelope theorem; the residual certificate establishes the flow optimum.

For a column x, the continuous score is
``sum(x_i * E**x_i) / sum(E**x_i)``, including all N agents.  Task j contributes
its positive weight times that score, plus the sum of eligible-edge rewards
times allocations.  Agents may abstain; task capacities are integer upper
bounds on column mass.  Inputs specify E = exp(t) exactly, rather than t.
"""

from dataclasses import dataclass
from fractions import Fraction


_BASIS = "positive-weight-additive-softmax-envelope"
_CERTIFICATE_KIND = "unit-capacity-min-cost-flow-potentials-v1"
_REPORT_KEYS = frozenset({
    "assignment", "counts", "objective", "optimumScope", "continuousScopeBasis",
    "allMaximizersBinaryGuaranteed", "integralityScope", "certificate",
})
_CERTIFICATE_KEYS = frozenset({"kind", "flowValue", "cost", "potentials"})


def _integer(value: object, name: str, lower: int, upper: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")
    if not lower <= value <= upper:
        raise ValueError(f"{name} must be between {lower} and {upper}")
    return value


def _rational(value: object, name: str) -> Fraction:
    if type(value) is not int and type(value) is not Fraction:
        raise TypeError(f"{name} must be an exact int or Fraction")
    exact = Fraction(value)
    if exact.numerator.bit_length() > 16 or exact.denominator.bit_length() > 16:
        raise ValueError(f"{name} numerator and denominator are limited to 16 bits")
    return exact


def _tuple(value: object, name: str, length: int | None = None) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be a tuple")
    if length is not None and len(value) != length:
        raise ValueError(f"{name} must contain exactly {length} values")
    return value


@dataclass(frozen=True)
class _Problem:
    n: int
    capacities: tuple[int, ...]
    exponentials: tuple[Fraction, ...]
    weights: tuple[Fraction, ...]
    edges: tuple[tuple[int, int, Fraction], ...]


def _admit(n, capacities, exponentials, weights, edges) -> _Problem:
    n = _integer(n, "n", 1, 24)
    capacities = _tuple(capacities, "capacities")
    m = len(capacities)
    if not 1 <= m <= 24:
        raise ValueError("capacities must contain between 1 and 24 tasks")
    admitted_capacities = tuple(
        _integer(value, "capacity", 0, n) for value in capacities
    )
    exponentials = _tuple(exponentials, "exponentials", m)
    weights = _tuple(weights, "weights", m)
    admitted_exponentials = tuple(_rational(value, "exponential")
                                  for value in exponentials)
    admitted_weights = tuple(_rational(value, "weight") for value in weights)
    if any(value <= 1 for value in admitted_exponentials):
        raise ValueError("every exponential must be strictly greater than one")
    if any(value <= 0 for value in admitted_weights):
        raise ValueError("every task weight must be strictly positive")
    edges = _tuple(edges, "edges")
    if len(edges) > n * m:
        raise ValueError("there can be at most n times m eligible edges")
    admitted_edges = []
    seen = set()
    for edge in edges:
        i, j, reward = _tuple(edge, "edge", 3)
        i = _integer(i, "agent index", 0, n - 1)
        j = _integer(j, "task index", 0, m - 1)
        reward = _rational(reward, "edge reward")
        if (i, j) in seen:
            raise ValueError("eligible agent-task edges must be unique")
        seen.add((i, j))
        admitted_edges.append((i, j, reward))
    return _Problem(n, admitted_capacities, admitted_exponentials,
                    admitted_weights, tuple(sorted(admitted_edges)))


def _score(n: int, exponential: Fraction, count: int) -> Fraction:
    return count * exponential / (n + count * (exponential - 1))


@dataclass(frozen=True)
class _Arc:
    tail: int
    head: int
    cost: Fraction


@dataclass(frozen=True)
class _Network:
    nodes: int
    sink: int
    arcs: tuple[_Arc, ...]
    assignments: tuple[tuple[int, int, int], ...]
    abstentions: tuple[int, ...]
    slots: tuple[tuple[int, ...], ...]


def _network(problem: _Problem) -> _Network:
    n, m = problem.n, len(problem.capacities)
    sink = n + m + 1
    # Node order is source, N agents, M tasks, sink.  All arcs have capacity 1.
    arcs = [_Arc(0, 1 + i, Fraction(0)) for i in range(n)]
    assignments = []
    for i, j, reward in problem.edges:
        assignments.append((i, j, len(arcs)))
        arcs.append(_Arc(1 + i, 1 + n + j, -reward))
    abstentions = []
    for i in range(n):
        abstentions.append(len(arcs))
        arcs.append(_Arc(1 + i, sink, Fraction(0)))
    slots = []
    for j, cap in enumerate(problem.capacities):
        task_slots = []
        previous = Fraction(0)
        for k in range(1, cap + 1):
            score = _score(n, problem.exponentials[j], k)
            task_slots.append(len(arcs))
            arcs.append(_Arc(1 + n + j, sink,
                             -problem.weights[j] * (score - previous)))
            previous = score
        slots.append(tuple(task_slots))
    return _Network(sink + 1, sink, tuple(arcs), tuple(assignments),
                    tuple(abstentions), tuple(slots))


def _residual(network: _Network, flow: list[int]):
    for index, arc in enumerate(network.arcs):
        if flow[index]:
            yield arc.head, arc.tail, -arc.cost, index, -1
        else:
            yield arc.tail, arc.head, arc.cost, index, 1


def _shortest_paths(network: _Network, flow: list[int], source: int | None):
    # source=None means a virtual source with zero-cost arcs to every node.
    distances = [Fraction(0) if source is None else None
                 for _ in range(network.nodes)]
    predecessors = [None] * network.nodes
    if source is not None:
        distances[source] = Fraction(0)
    for _ in range(network.nodes - 1):
        changed = False
        for u, v, cost, index, direction in _residual(network, flow):
            if distances[u] is None:
                continue
            candidate = distances[u] + cost
            if distances[v] is None or candidate < distances[v]:
                distances[v] = candidate
                predecessors[v] = (u, index, direction)
                changed = True
        if not changed:
            return distances, predecessors
    for u, v, cost, _, _ in _residual(network, flow):
        if distances[u] is not None and (
            distances[v] is None or distances[u] + cost < distances[v]
        ):
            raise RuntimeError("unexpected negative residual cycle")
    return distances, predecessors


def _witness_flow(network: _Network, assignment: tuple, counts: tuple) -> list[int]:
    n = len(assignment)
    flow = [0] * len(network.arcs)
    flow[:n] = [1] * n
    for i, j, index in network.assignments:
        flow[index] = int(assignment[i] == j)
    for i, index in enumerate(network.abstentions):
        flow[index] = int(assignment[i] is None)
    for j, slots in enumerate(network.slots):
        for k, index in enumerate(slots):
            flow[index] = int(k < counts[j])
    return flow


def maximize_additive_softmax(
    n: int,
    capacities: tuple[int, ...],
    exponentials: tuple[Fraction, ...],
    weights: tuple[Fraction, ...],
    edges: tuple[tuple[int, int, Fraction], ...],
) -> dict:
    """Return an exact optimal assignment and residual-potential certificate.

    ``n`` and task count are in 1..24.  Each capacity is an integer in 0..n;
    each E is greater than 1 and each weight is positive.  Edges are unique
    ``(agent_index, task_index, reward)`` tuples with zero-based indices.
    Rational inputs must be exact int/Fraction values whose numerator magnitude
    and denominator fit in 16 bits; bool and float are rejected.  All containers
    must be tuples.  Absence of an edge forbids that allocation.

    ``assignment[i]`` is a task index or None (abstention).  The objective is the
    weighted *sum*, without division by the task count, plus linear rewards.
    The theorem guarantees all maximizers binary for n>=2; for n=1 it guarantees
    an integral witness without claiming whether any fractional ties exist.

    Bellman--Ford sends exactly n unit flows.  There are at most 50 nodes and
    1200 original arcs; each search takes at most 49 relaxation sweeps and one
    cycle check.  Ties use the fixed, sorted network order.  The final potential
    at each node is its shortest distance from a virtual zero-cost source.
    For every residual arc u->v with cost c, c+p[u]-p[v] is nonnegative.
    """
    problem = _admit(n, capacities, exponentials, weights, edges)
    network = _network(problem)
    flow = [0] * len(network.arcs)
    for _ in range(problem.n):
        distances, predecessors = _shortest_paths(network, flow, 0)
        if distances[network.sink] is None:
            raise RuntimeError("abstention should make every unit flow feasible")
        v = network.sink
        for _ in range(network.nodes - 1):
            predecessor = predecessors[v]
            if predecessor is None:
                raise RuntimeError("missing augmenting-path predecessor")
            u, index, direction = predecessor
            flow[index] += direction
            v = u
            if v == 0:
                break
        if v != 0:
            raise RuntimeError("augmenting path exceeded the node bound")
    assignment = [None] * problem.n
    counts = [0] * len(problem.capacities)
    for i, j, index in network.assignments:
        if flow[index]:
            assignment[i] = j
            counts[j] += 1
    assignment, counts = tuple(assignment), tuple(counts)
    # Strictly decreasing positive marginal rewards force prefix slot usage.
    if flow != _witness_flow(network, assignment, counts):
        raise RuntimeError("flow does not match the canonical assignment witness")
    potentials, _ = _shortest_paths(network, flow, None)
    cost = sum((arc.cost * amount for arc, amount in zip(network.arcs, flow)),
               Fraction(0))
    return {
        "assignment": assignment,
        "counts": counts,
        "objective": -cost,
        "optimumScope": "continuous",
        "continuousScopeBasis": _BASIS,
        "allMaximizersBinaryGuaranteed": problem.n >= 2,
        "integralityScope": "all-maximizers" if problem.n >= 2 else "optimal-witness",
        "certificate": {
            "kind": _CERTIFICATE_KIND,
            "flowValue": problem.n,
            "cost": cost,
            "potentials": tuple(potentials),
        },
    }


def _certificate_rational(value: object) -> bool:
    # Costs on a simple residual path have fewer than 64 bits per arc before
    # summation and at most 49 arcs.  8192 bits generously bounds exact output
    # while rejecting unbounded integers in an externally supplied certificate.
    return (type(value) in (int, Fraction)
            and Fraction(value).numerator.bit_length() <= 8192
            and Fraction(value).denominator.bit_length() <= 8192)


def verify_additive_softmax_certificate(
    n: int,
    capacities: tuple[int, ...],
    exponentials: tuple[Fraction, ...],
    weights: tuple[Fraction, ...],
    edges: tuple[tuple[int, int, Fraction], ...],
    report: object,
) -> bool:
    """Check a report without optimization; malformed reports return False.

    Invalid problem inputs raise the same admission errors as the optimizer.
    The verifier reconstructs the unit-capacity network and canonical flow from
    the assignment, checks feasibility and cost, then checks every residual
    reduced cost.  These inequalities certify absence of a negative residual
    cycle and hence flow optimality.  The continuous claim additionally uses
    the analytic envelope theorem, not the certificate alone.
    """
    problem = _admit(n, capacities, exponentials, weights, edges)
    if type(report) is not dict or report.keys() != _REPORT_KEYS:
        return False
    assignment, counts = report["assignment"], report["counts"]
    m = len(problem.capacities)
    if type(assignment) is not tuple or len(assignment) != problem.n:
        return False
    if any(j is not None and (type(j) is not int or not 0 <= j < m)
           for j in assignment):
        return False
    if (type(counts) is not tuple or len(counts) != m
            or any(type(k) is not int for k in counts)):
        return False
    actual_counts = tuple(sum(j == task for j in assignment) for task in range(m))
    if counts != actual_counts or any(k > cap for k, cap in
                                      zip(counts, problem.capacities)):
        return False
    rewards = {(i, j): reward for i, j, reward in problem.edges}
    if any(j is not None and (i, j) not in rewards for i, j in enumerate(assignment)):
        return False
    objective = sum((problem.weights[j] * _score(problem.n,
                     problem.exponentials[j], k) for j, k in enumerate(counts)),
                    Fraction(0))
    objective += sum((rewards[i, j] for i, j in enumerate(assignment)
                      if j is not None), Fraction(0))
    if not _certificate_rational(report["objective"]) or report["objective"] != objective:
        return False
    if (report["optimumScope"] != "continuous"
            or report["continuousScopeBasis"] != _BASIS
            or report["allMaximizersBinaryGuaranteed"] is not (problem.n >= 2)
            or report["integralityScope"] != (
                "all-maximizers" if problem.n >= 2 else "optimal-witness")):
        return False
    certificate = report["certificate"]
    if type(certificate) is not dict or certificate.keys() != _CERTIFICATE_KEYS:
        return False
    if (certificate["kind"] != _CERTIFICATE_KIND
            or type(certificate["flowValue"]) is not int
            or certificate["flowValue"] != problem.n
            or not _certificate_rational(certificate["cost"])
            or certificate["cost"] != -objective):
        return False
    network = _network(problem)
    potentials = certificate["potentials"]
    if (type(potentials) is not tuple or len(potentials) != network.nodes
            or any(not _certificate_rational(value) for value in potentials)):
        return False
    flow = _witness_flow(network, assignment, counts)
    balances = [0] * network.nodes
    for arc, amount in zip(network.arcs, flow):
        balances[arc.tail] -= amount
        balances[arc.head] += amount
    if balances != [-problem.n] + [0] * (network.nodes - 2) + [problem.n]:
        return False
    if sum((arc.cost * amount for arc, amount in zip(network.arcs, flow)),
           Fraction(0)) != -objective:
        return False
    return all(cost + potentials[u] - potentials[v] >= 0
               for u, v, cost, _, _ in _residual(network, flow))
