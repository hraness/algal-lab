"""Frozen development-only labelled certificate transfer; see runs/certificate-transfer-20261011/protocol.md.

No new source demands, weights or capacity bounds are selected here. Every
proposed exclusion still goes through the existing exact checker and a
separate maximal-independent-set oracle. Not a solver or speed comparison.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import verify
import verify_sample as sampled

HERE = Path(__file__).resolve().parent
SAMPLE_SHA256 = "3676626e8c70832cfa6b4e9f522e627e668f77b03ee0f23a517a5189e506e199"
NINE_SHA256 = "b04e152fe80f1f4e6cda1c76dd432506cc70d221794b0dc99c9f6d7ca85eaa45"
TARGETS = (19, 22, 25, 31, 43, 52, 57, 72, 92, 98, 100, 103, 106, 108, 119)


def fixture():
    for name, digest in (("sampled-certificates.json", SAMPLE_SHA256),
                         ("certificates.json", NINE_SHA256)):
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise verify.InvalidCertificate("frozen input identity differs: " + name)
    bundle, _ = verify.read_bundle(HERE / "sampled-certificates.json")
    baseline = sampled.verify_bundle(bundle)
    if (baseline["certified_exclusions"] != 113
            or tuple(baseline["remaining_indices"]) != TARGETS):
        raise verify.InvalidCertificate("baseline partition differs")
    return bundle, baseline


def edge_distance(left, right):
    """Number of undirected labelled edge edits, never a graph isomorphism."""
    return sum((a ^ b).bit_count() for a, b in zip(left, right)) // 2


def proposals(bundle):
    graphs = {entry["index"]: entry for entry in bundle["sample"]}
    cases = {entry["sample_index"]: entry for entry in bundle["certificates"]}
    if len(graphs) != 128 or len(cases) != 113 or tuple(bundle["remaining_indices"]) != TARGETS:
        raise verify.InvalidCertificate("source or target partition differs")
    for target_index in TARGETS:
        target = graphs[target_index]
        ordered = sorted(cases, key=lambda i: (edge_distance(graphs[i]["adjacency"],
                                                           target["adjacency"]), i))
        for source_index in ordered[:8]:
            source = cases[source_index]
            adjacency = target["adjacency"]
            retained = [(pair, weight) for pair, weight in zip(source["demands"], source["weights"])
                        if not (adjacency[pair[0]] & (1 << pair[1]))
                        and not (adjacency[pair[0]] & adjacency[pair[1]])]
            yield target, source, edge_distance(graphs[source_index]["adjacency"], adjacency), retained


class OracleLimit(RuntimeError):
    pass


def direct_maximum(adjacency, pairs, weights, quota):
    """Enumerate maximal independent vertex sets using complement-clique recursion.

    Nonnegative weights imply every independent set's demand weight is bounded
    by that of a maximal independent superset. This implementation does not
    import or call the subset/capacity checker.
    """
    full = (1 << len(adjacency)) - 1
    complement = [full ^ (1 << vertex) ^ row for vertex, row in enumerate(adjacency)]
    local_nodes = 0
    maximum = 0

    def visit(clique, possible, excluded):
        nonlocal local_nodes, maximum
        quota["nodes"] += 1
        local_nodes += 1
        if quota["nodes"] > 1_000_000 or time.process_time() - quota["start"] >= 5:
            raise OracleLimit("direct oracle allowance exceeded")
        if not possible and not excluded:
            maximum = max(maximum, sum(weight for (u, v), weight in zip(pairs, weights)
                                       if clique & (1 << u) and clique & (1 << v)))
            return
        pivot, best_score = -1, -1
        for vertex in range(len(adjacency)):
            if (possible | excluded) & (1 << vertex):
                score = (possible & complement[vertex]).bit_count()
                if score > best_score:
                    pivot, best_score = vertex, score
        candidates = possible & ~complement[pivot] if pivot != -1 else possible
        while candidates:
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            visit(clique | bit, possible & complement[vertex], excluded & complement[vertex])
            possible &= ~bit
            excluded |= bit
            candidates &= ~bit

    visit(0, full, 0)
    return maximum, local_nodes


def run(ledger):
    bundle, baseline = fixture()
    attempt_list = list(proposals(bundle))
    if len(attempt_list) != 120:
        raise verify.InvalidCertificate("unexpected proposal count")
    budget = sampled.Budget(combinations=500_000, seconds=10)
    oracle = {"start": time.process_time(), "nodes": 0}
    counts = {}
    with Path(ledger).open("x", encoding="utf-8") as output:
        def save(value):
            output.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
            output.flush()
        save({"kind": "header", "sample_sha256": SAMPLE_SHA256, "nine_sha256": NINE_SHA256,
              "original_exclusions": baseline["certified_exclusions"],
              "original_endpoint_unions": baseline["minimal_overweight_subsets_checked"],
              "original_combinations": baseline["demand_combinations_considered"],
              "baseline_cpu_seconds": baseline["cpu_seconds"],
              "proposals": len(attempt_list), "paid_usd": 0})
        for ordinal, (target, source, distance, retained) in enumerate(attempt_list):
            if time.process_time() - budget.start >= 10 or budget.reserved >= 500_000:
                save({"kind": "stop", "reason": "global transfer budget exhausted",
                      "unattempted": len(attempt_list) - ordinal})
                break
            pairs = [pair for pair, _ in retained]
            weights = [weight for _, weight in retained]
            record = {"kind": "attempt", "ordinal": ordinal, "source_index": source["sample_index"],
                      "target_index": target["index"], "source_sha256": next(
                          graph["adjacency_sha256"] for graph in bundle["sample"]
                          if graph["index"] == source["sample_index"]),
                      "target_sha256": target["adjacency_sha256"], "edge_distance": distance,
                      "retained_demands": len(pairs), "retained_weight": sum(weights),
                      "capacity": source["capacity_bound"]}
            before = budget.considered, budget.checked
            if sum(weights) <= 6 * source["capacity_bound"]:
                record["status"] = "insufficient_weight"
            else:
                try:
                    sampled.verify_claim(target["adjacency"], pairs, weights,
                                         source["capacity_bound"], 6, budget)
                    maximum, nodes = direct_maximum(target["adjacency"], pairs, weights, oracle)
                    record["direct_maximum"] = maximum
                    record["direct_nodes"] = nodes
                    if maximum > source["capacity_bound"]:
                        record["status"] = "oracle_disagreement"
                    else:
                        record["status"] = "candidate_pending_independent_review"
                        record["certificate"] = {"sample_index": target["index"],
                                                 "demands": pairs, "weights": weights,
                                                 "capacity_bound": source["capacity_bound"]}
                except verify.InvalidCertificate as error:
                    record["status"] = "invalid_certificate"
                    record["reason"] = str(error)
                except (verify.VerificationLimit, OracleLimit) as error:
                    record["status"] = "unknown_limit"
                    record["reason"] = str(error)
            record["combinations"] = budget.considered - before[0]
            record["endpoint_unions"] = budget.checked - before[1]
            record["transfer_cpu_seconds"] = time.process_time() - budget.start
            counts[record["status"]] = counts.get(record["status"], 0) + 1
            save(record)
            if record["status"] in ("unknown_limit", "oracle_disagreement"):
                save({"kind": "stop", "reason": record["status"],
                      "unattempted": len(attempt_list) - ordinal - 1})
                break
        save({"kind": "summary", "statuses": counts, "combinations": budget.considered,
              "endpoint_unions": budget.checked, "reserved_combinations": budget.reserved,
              "oracle_nodes": oracle["nodes"], "transfer_cpu_seconds": time.process_time() - budget.start,
              "paid_usd": 0})
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path,
                        help="new private JSONL file; existing files are never overwritten")
    args = parser.parse_args()
    print(json.dumps(run(args.ledger), sort_keys=True))
