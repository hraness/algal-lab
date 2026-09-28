"""Independent finite-family reproduction, without imports from the search code.

This uses Bron--Kerbosch on the complement and a set-based exact-cover search.
It is a necessary-condition exclusion, not a general R(3,10) computation.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import resource
import sys
import time


class LimitExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, seconds=25, nodes=1_000_000):
        self.start = time.process_time()
        self.wall_start = time.monotonic()
        self.seconds, self.nodes = seconds, nodes

    def check(self, nodes=0):
        if (time.process_time() - self.start >= self.seconds
                or time.monotonic() - self.wall_start >= self.seconds + 15
                or nodes > self.nodes):
            raise LimitExceeded("independent reproduction limit")


def published_graph_in_local_labels():
    """Transport the published edge matrix, rather than use local differences."""
    differences = (1, 7, 11, 16, 19, 24, 28, 34)
    published = [{(v + d) % 35 for d in differences} for v in range(35)]
    return [{w for w in range(35) if (22 * w) % 35 in published[(22 * v) % 35]}
            for v in range(35)]


def remainder(removed):
    source = published_graph_in_local_labels()
    kept = [v for v in range(35) if v not in (0, removed)]
    return [sum(1 << j for j, v in enumerate(kept) if v in source[u]) for u in kept]


def maximal_independent_sets(adj, budget):
    """Enumerate every maximal clique in the complement using pivoted BK."""
    n = len(adj)
    full = (1 << n) - 1
    complement = [full ^ (row | 1 << v) for v, row in enumerate(adj)]
    result, nodes = [], 0

    def visit(chosen, possible, excluded):
        nonlocal nodes
        nodes += 1
        if nodes % 256 == 1:
            budget.check(nodes)
        if not possible and not excluded:
            result.append(chosen)
            return
        pool = possible | excluded
        pivot = max((v for v in range(n) if pool >> v & 1),
                    key=lambda v: (possible & complement[v]).bit_count())
        branch = possible & ~complement[pivot]
        while branch:
            bit = branch & -branch
            v = bit.bit_length() - 1
            branch -= bit
            visit(chosen | bit, possible & complement[v], excluded & complement[v])
            possible -= bit
            excluded |= bit

    visit(0, full, 0)
    if len(result) != len(set(result)):
        raise ValueError("duplicate maximal set")
    budget.check(nodes)
    return sorted(result), nodes


def exact_cover(columns, required, capacities, compatible, goal, budget):
    """Select exactly goal distinct columns, covering required rows once.

    Other rows have upper capacities only. Compatible is a symmetric graph
    on column indices. Zero-required-row columns can be delayed until the
    required rows are covered; they are then enumerated in index order.
    There is no index ordering while a dynamic required-row pivot is active.
    """
    members = [[v for v in range(len(capacities)) if mask >> v & 1]
               for mask in columns]
    required_parts = [mask & required for mask in columns]
    nodes = 0

    def visit(chosen, available, uncovered, used):
        nonlocal nodes
        nodes += 1
        budget.check(nodes)
        slots = goal - len(chosen)
        if slots == 0:
            return chosen if not uncovered else None
        eligible = [i for i in sorted(available)
                    if not (required_parts[i] & ~uncovered)
                    and all(used[v] < capacities[v] for v in members[i])]
        if len(eligible) < slots:
            return None
        if uncovered:
            choices = [[i for i in eligible if required_parts[i] >> v & 1]
                       for v in range(len(capacities)) if uncovered >> v & 1]
            options = min(choices, key=len)
            if not options:
                return None
            if sum(sorted((required_parts[i].bit_count() for i in eligible),
                          reverse=True)[:slots]) < uncovered.bit_count():
                return None
        else:
            options = eligible
        for i in options:
            next_used = used[:]
            for v in members[i]:
                next_used[v] += 1
            next_available = available & compatible[i]
            if not uncovered:
                next_available = {j for j in next_available if j > i}
            found = visit(chosen + [i], next_available,
                          uncovered & ~required_parts[i], next_used)
            if found is not None:
                return found
        return None

    answer = visit([], set(range(len(columns))), required, [0] * len(capacities))
    return answer, nodes


def array_hash(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def check_case(removed, budget):
    adj = remainder(removed)
    maximal, enumeration_nodes = maximal_independent_sets(adj, budget)
    if any(mask.bit_count() not in (7, 8) for mask in maximal):
        raise ValueError("unexpected maximal-independent-set size")
    degree_eight = sum(1 << v for v, row in enumerate(adj) if row.bit_count() == 8)
    capacities = [9 - row.bit_count() for row in adj]
    columns = [mask for mask in maximal if (mask & degree_eight).bit_count() <= 4]
    independent_eight_sets = [mask for mask in maximal if mask.bit_count() == 8]
    misses = []
    for mask in columns:
        budget.check()
        misses.append(sum(1 << j for j, eight in enumerate(independent_eight_sets)
                          if not (mask & eight)))
    required_parts = [mask & degree_eight for mask in columns]
    compatible = []
    for i in range(len(columns)):
        budget.check()
        compatible.append({j for j in range(len(columns))
                           if j != i and not (misses[i] & misses[j])
                           and not (required_parts[i] & required_parts[j])})
    answer, nodes = exact_cover(columns, degree_eight, capacities, compatible, 6, budget)
    return {
        "deleted_local_pair": [0, removed],
        "deleted_published_pair": sorted((0, 22 * removed % 35)),
        "base_adjacency_sha256": array_hash(adj),
        "edges": sum(row.bit_count() for row in adj) // 2,
        "degree_eight_vertices": degree_eight.bit_count(),
        "maximal_set_counts": {str(k): sum(mask.bit_count() == k for mask in maximal)
                               for k in (7, 8)},
        "maximal_set_inventory_sha256": array_hash(maximal),
        "eligible_columns": len(columns),
        "eligible_column_inventory_sha256": array_hash(columns),
        "zero_degree_eight_columns": sum(not part for part in required_parts),
        "bron_kerbosch_nodes": enumeration_nodes,
        "cover_nodes": nodes,
        "six_column_cover": None if answer is None else [columns[i] for i in answer],
    }


def reproduce():
    budget = Budget()
    reports = [check_case(removed, budget) for removed in (1, 2, 4, 5, 7, 8, 14)]
    budget.check()
    return {
        "schema_version": 1,
        "scope": "seven pair-deletion remainders; centre-covered degree-six extensions",
        "method": "independent complement Bron-Kerbosch and set-based exact cover",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "cooperative_cpu_limit_seconds": 25,
        "cooperative_wall_limit_seconds": 40,
        "node_limit_per_enumeration_or_cover": 1_000_000,
        "cases": reports,
        "all_seven_have_no_necessary_column_cover": all(
            item["six_column_cover"] is None for item in reports),
        "cpu_seconds": time.process_time() - budget.start,
        "wall_seconds": time.monotonic() - budget.wall_start,
        "ramsey_bound_claim_made": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be new")
    resource.setrlimit(resource.RLIMIT_CPU, (29, 30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (4 * 1024**2, 4 * 1024**2))
    report = reproduce()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as destination:
        json.dump(report, destination, indent=2)
        destination.write("\n")
    print(json.dumps({"output": str(args.output), "cpu_seconds": report["cpu_seconds"],
                      "all_seven_have_no_necessary_column_cover":
                      report["all_seven_have_no_necessary_column_cover"]}))
