"""Bounded necessary-column search; a found cover is not a Ramsey witness.

All six columns are distinct by the private-vertex argument documented in
STRUCTURAL-NOTE.md. A pivot on an uncovered degree-eight vertex is used with
NO ascending-index restriction. Columns missing that whole vertex set are
handled by an explicit, general completion branch.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import time

from catalogue import ramsey_catalogue
from shared import Budget, DEPENDENCIES, HERE, SearchLimit, checker, digest, graph_digest

MAX_COLUMNS = 5000
MAX_NODES = 100000
MAX_RESULT_BYTES = 16 * 1024**2


def bits(mask):
    while mask:
        bit = mask & -mask
        mask ^= bit
        yield bit.bit_length() - 1


def maximal_independent_sets(adj, *, budget=None, node_limit=1000000):
    """Visit every independent set in increasing vertex order; retain maximal ones."""
    checker.validate_adjacency(adj)
    if not 1 <= len(adj) <= 35 or not 1 <= node_limit <= 1000000:
        raise ValueError("enumeration bounds")
    budget = budget or Budget(5)
    full, nodes, result = (1 << len(adj)) - 1, 0, []

    def visit(available, selected, dominated):
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise SearchLimit("maximal-set enumeration node limit")
        if nodes == 1 or nodes % 256 == 0:
            budget.check()
        if dominated == full:
            if available:
                raise AssertionError("a maximal independent set cannot be extended")
            result.append(selected)
            return
        while available:
            bit = available & -available
            available ^= bit
            vertex = bit.bit_length() - 1
            visit(available & ~adj[vertex], selected | bit,
                  dominated | bit | adj[vertex])

    visit(full, 0, 0)
    budget.check()
    return sorted(result), nodes


def column_problem(adj, *, budget=None):
    """Construct only mathematically necessary conditions for the covered target."""
    budget = budget or Budget(5)
    checker.validate_adjacency(adj)
    if (len(adj) != 33 or checker.triangle(adj) is not None
            or any(not 6 <= row.bit_count() <= 8 for row in adj)):
        raise ValueError("expected a triangle-free 33-vertex remainder of degrees 6..8")
    maximal, nodes = maximal_independent_sets(adj, budget=budget)
    if any(mask.bit_count() > 8 for mask in maximal):
        raise ValueError("remainder has an independent nine-set")
    required = sum(1 << v for v, row in enumerate(adj) if row.bit_count() == 8)
    columns = [mask for mask in maximal
               if 5 <= mask.bit_count() <= 8 and (mask & required).bit_count() <= 4]
    if len(columns) > MAX_COLUMNS:
        raise SearchLimit("column-count limit")
    eights = [mask for mask in maximal if mask.bit_count() == 8]
    # alpha(H)<=8 makes every independent eight-set maximal.
    misses = []
    for column in columns:
        budget.check()
        misses.append(sum(1 << i for i, mask in enumerate(eights) if not column & mask))
    compatible = [0] * len(columns)
    for i, column in enumerate(columns):
        if i % 16 == 0:
            budget.check()
        for j in range(i):
            if not column & columns[j] & required and not misses[i] & misses[j]:
                compatible[i] |= 1 << j
                compatible[j] |= 1 << i
    budget.check()
    return {
        "adjacency": adj, "adjacency_sha256": graph_digest(adj),
        "columns": columns, "independent_eight_sets": eights,
        "compatible": compatible, "row_caps": [9 - row.bit_count() for row in adj],
        "required_mask": required, "slots": 6, "private_cap": 4, "cover_all": True,
        "inventory": {
            "maximal_set_sizes": dict(sorted(Counter(m.bit_count() for m in maximal).items())),
            "eligible_column_sizes": dict(sorted(Counter(m.bit_count() for m in columns).items())),
            "required_vertex_count": required.bit_count(),
            "empty_required_columns": sum(not (m & required) for m in columns),
            "compatible_pairs": sum(mask.bit_count() for mask in compatible) // 2,
            "independent_set_enumeration_nodes": nodes,
        },
    }


def validate_cover_problem(problem):
    columns, compatible, caps = (problem[key] for key in ("columns", "compatible", "row_caps"))
    required, slots = problem["required_mask"], problem["slots"]
    private_cap, cover_all = problem["private_cap"], problem["cover_all"]
    if (not 1 <= len(caps) <= 35 or len(columns) > MAX_COLUMNS
            or len(columns) != len(compatible) or len(set(columns)) != len(columns)
            or type(slots) is not int or not 1 <= slots <= 6
            or type(required) is not int or not 0 <= required < 1 << len(caps)
            or any(type(cap) is not int or not 1 <= cap <= 6 for cap in caps)
            or any(type(mask) is not int or not 0 < mask < 1 << len(caps) for mask in columns)
            or type(cover_all) is not bool
            or (private_cap is not None and (type(private_cap) is not int or not 0 <= private_cap <= 35))
            or any(caps[v] != 1 for v in bits(required))):
        raise ValueError("invalid cover problem")
    for i, mask in enumerate(compatible):
        if (type(mask) is not int or not 0 <= mask < 1 << len(columns) or mask >> i & 1
                or any(not (compatible[j] >> i & 1) for j in bits(mask))):
            raise ValueError("compatibility must be a simple undirected graph")


def search_cover(problem, *, budget=None, node_limit=MAX_NODES):
    """Return an exhaustive branch tree or an explicit necessary-condition cover.

This routine also supports small abstract controls. In particular zero-required
columns are completed generally, rather than relying on the production bound
that permits at most one of them.
    """
    validate_cover_problem(problem)
    if not 1 <= node_limit <= MAX_NODES:
        raise ValueError("search node limit")
    budget = budget or Budget(5)
    columns, compatible, caps = (problem[key] for key in ("columns", "compatible", "row_caps"))
    required, slots = problem["required_mask"], problem["slots"]
    full, count = (1 << len(caps)) - 1, len(columns)
    support = [sum(1 << i for i, column in enumerate(columns) if column >> v & 1)
               for v in range(len(caps))]
    empty = sum(1 << i for i, column in enumerate(columns) if not column & required)
    max_required = max(((column & required).bit_count() for column in columns), default=0)
    trace, found = [], None

    def visit(candidates, selected, usage, covered):
        nonlocal found
        if len(trace) >= node_limit:
            raise SearchLimit("cover search node limit")
        if not trace or len(trace) % 128 == 0:
            budget.check()
        index = len(trace)
        node = {"selected": selected, "candidates_hex": hex(candidates)}
        trace.append(node)
        need, uncovered = slots - len(selected), required & ~covered
        if uncovered.bit_count() > max_required * need:
            node["status"] = "insufficient_required_capacity"
        elif candidates.bit_count() < need:
            node["status"] = "too_few_columns"
        elif not need:
            if problem["cover_all"] and covered != full:
                node["status"] = "uncovered_remainder"
            elif problem["private_cap"] is not None and any(
                    sum(usage[v] == 1 for v in bits(columns[i])) > problem["private_cap"]
                    for i in selected):
                node["status"] = "private_cap_exceeded"
            else:
                node["status"], found = "necessary_cover", selected
        else:
            if uncovered:
                pivot = min(bits(uncovered), key=lambda v: (candidates & support[v]).bit_count())
                options = candidates & support[pivot]
                node["pivot"] = pivot
            else:
                options, node["pivot"] = candidates & empty, None
            node.update(status="branch", options=list(bits(options)), children=[])
            for chosen in bits(options):
                column = columns[chosen]
                new_usage = [old + int(bool(column >> v & 1)) for v, old in enumerate(usage)]
                if any(value > cap for value, cap in zip(new_usage, caps)):
                    raise AssertionError("candidate has an already saturated row")
                remaining = candidates & compatible[chosen]
                for v, (old, new, cap) in enumerate(zip(usage, new_usage, caps)):
                    if old < cap == new:
                        remaining &= ~support[v]
                # There is deliberately no chosen-index ordering restriction.
                child = visit(remaining, selected + [chosen], new_usage, covered | column)
                node["children"].append(child)
                if found is not None:
                    break
        return index

    visit((1 << count) - 1, [], [0] * len(caps), 0)
    budget.check()
    return {"status": "necessary_cover_found" if found is not None else "no_necessary_cover",
            "found_columns": found, "search_nodes": len(trace), "tree": trace}


def replay_cover(problem, result, *, budget=None):
    """Replay a negative tree by recomputing eligibility from selected columns.

Each absent column is justified directly: already selected, pair-incompatible,
or would exceed a row capacity. No incremental candidate update is trusted.
The tree must contain every option at every pivot, and exactly one visit per node.
    """
    validate_cover_problem(problem)
    budget = budget or Budget(5)
    if result["status"] != "no_necessary_cover" or result["found_columns"] is not None:
        raise ValueError("only a negative exhaustive tree can be replayed")
    trace = result["tree"]
    if not trace or len(trace) != result["search_nodes"] or len(trace) > MAX_NODES:
        raise ValueError("invalid trace size")
    columns, compatible, caps = (problem[key] for key in ("columns", "compatible", "row_caps"))
    required, slots = problem["required_mask"], problem["slots"]
    max_required = max(((column & required).bit_count() for column in columns), default=0)
    full, seen = (1 << len(caps)) - 1, set()

    def visit(index, selected):
        budget.check()
        if type(index) is not int or not 0 <= index < len(trace) or index in seen:
            raise ValueError("missing, duplicated, or cyclic branch")
        seen.add(index)
        node = trace[index]
        if node["selected"] != selected or len(selected) != len(set(selected)):
            raise ValueError("selected path mismatch")
        usage = [sum(bool(columns[i] >> v & 1) for i in selected) for v in range(len(caps))]
        if any(value > cap for value, cap in zip(usage, caps)):
            raise ValueError("invalid selected row capacity")
        covered = sum(1 << v for v, value in enumerate(usage) if value)
        eligible = [i for i, column in enumerate(columns)
                    if i not in selected and all(compatible[i] >> j & 1 for j in selected)
                    and all(usage[v] < caps[v] for v in bits(column))]
        if node["candidates_hex"] != hex(sum(1 << i for i in eligible)):
            raise ValueError("candidate omission or unjustified candidate")
        need, uncovered = slots - len(selected), required & ~covered
        if uncovered.bit_count() > max_required * need:
            expected = "insufficient_required_capacity"
        elif len(eligible) < need:
            expected = "too_few_columns"
        elif not need:
            if problem["cover_all"] and covered != full:
                expected = "uncovered_remainder"
            elif problem["private_cap"] is not None and any(
                    sum(usage[v] == 1 for v in bits(columns[i])) > problem["private_cap"]
                    for i in selected):
                expected = "private_cap_exceeded"
            else:
                raise ValueError("negative certificate contains a valid necessary cover")
        else:
            expected = "branch"
            if uncovered:
                pivot = min(bits(uncovered), key=lambda v: sum(bool(columns[i] >> v & 1) for i in eligible))
                options = [i for i in eligible if columns[i] >> pivot & 1]
            else:
                pivot, options = None, [i for i in eligible if not columns[i] & required]
            if node.get("pivot") != pivot or node.get("options") != options:
                raise ValueError("pivot or exhaustive options mismatch")
            children = node.get("children")
            if not isinstance(children, list) or len(children) != len(options):
                raise ValueError("missing branch")
            for chosen, child in zip(options, children):
                visit(child, selected + [chosen])
        if node["status"] != expected:
            raise ValueError("unjustified branch termination")

    visit(0, [])
    if seen != set(range(len(trace))):
        raise ValueError("unreachable trace nodes")
    budget.check()
    return {"replayed": True, "nodes_checked": len(seen)}


def write_bounded(path, value):
    raw = (json.dumps(value, indent=2) + "\n").encode()
    if len(raw) > MAX_RESULT_BYTES:
        raise SearchLimit("result byte limit")
    path.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new ignored run directory")
    parser.add_argument("--case", type=int, choices=range(7), help="omit to check all seven inputs")
    parser.add_argument("--seconds", type=float, default=5, help="CPU budget per case, at most 30")
    args = parser.parse_args()
    if not 0 < args.seconds <= 30:
        parser.error("seconds must be in (0,30]")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    dependencies = ["fixed_remainder/column_cover.py", "fixed_remainder/catalogue.py",
                    "fixed_remainder/shared.py", *DEPENDENCIES]
    hashes = {relative: digest(HERE.parent / relative) for relative in dependencies}
    for relative in dependencies:
        destination = output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE.parent / relative, destination)
        if digest(destination) != hashes[relative]:
            raise ValueError("source changed during snapshot")
    catalogue = ramsey_catalogue(budget=Budget(5))
    write_bounded(output / "catalogue.json", catalogue)
    selected = catalogue["cases"] if args.case is None else [catalogue["cases"][args.case]]
    summary = {"schema_version": 1, "status": "incomplete", "source_sha256": hashes,
               "catalogue_sha256": digest(output / "catalogue.json"),
               "cpu_seconds_per_case": args.seconds, "memory_mib": 1024,
               "scope": "covered six-neighbour extensions of these seven pair-deletion inputs only",
               "external_ramsey_bound_claim_made": False, "cases": []}
    write_bounded(output / "summary.json", summary)
    for case in selected:
        budget, started = Budget(args.seconds), time.process_time()
        record = {"case": case["index"], "deleted_pair": case["representative_pair"]}
        try:
            problem = column_problem(case["adjacency"], budget=budget)
            result = search_cover(problem, budget=budget)
            if result["status"] == "no_necessary_cover":
                result["replay"] = replay_cover(problem, result, budget=budget)
            record.update(status=result["status"], inventory=problem["inventory"],
                          search_nodes=result["search_nodes"])
            artifact = output / f"case-{case['index']}.json"
            write_bounded(artifact, {"problem": problem, "result": result})
            budget.check()
            record.update(artifact=artifact.name, artifact_sha256=digest(artifact))
        except SearchLimit as error:
            record.update(status="unresolved", reason=str(error))
        record["cpu_seconds"] = time.process_time() - started
        summary["cases"].append(record)
        write_bounded(output / "summary.json", summary)
    if hashes != {relative: digest(HERE.parent / relative) for relative in dependencies}:
        raise ValueError("sources changed during run")
    summary["status"] = ("all_selected_cases_no_necessary_cover"
                         if all(case["status"] == "no_necessary_cover" for case in summary["cases"])
                         else "some_cases_unresolved_or_have_necessary_covers")
    write_bounded(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
