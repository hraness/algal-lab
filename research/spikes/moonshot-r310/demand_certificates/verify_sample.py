"""Verify integer demand certificates for 113 of 128 specified remainders."""

import argparse
import itertools
import json
import math
from pathlib import Path
import sys
import time

import verify

KIND = "sampled-fixed-remainder-weighted-demands-v1"
MAX_COMBINATIONS = 500_000
SOURCES = {"sample", "unit_screen", "unit_review", "original_nine",
           "original_nine_review", "weighted_screen", "weighted_review"}
PROOF_SOURCES = {"unit_screen", "original_nine", "weighted_screen"}


class Budget:
    """One shared allowance for every certificate in the sample."""

    def __init__(self, combinations=MAX_COMBINATIONS, seconds=10):
        if (type(combinations) is not int or not 1 <= combinations <= MAX_COMBINATIONS
                or type(seconds) not in (int, float) or not 0 < seconds <= 10):
            raise ValueError("unsupported verification allowance")
        self.start = time.process_time()
        self.seconds, self.limit = seconds, combinations
        self.reserved = self.considered = self.checked = 0

    def check(self):
        if time.process_time() - self.start >= self.seconds:
            raise verify.VerificationLimit("verification CPU allowance exceeded")

    def reserve(self, count):
        self.check()
        if self.reserved + count > self.limit:
            raise verify.VerificationLimit("demand-combination allowance exceeded")
        self.reserved += count


def weights_ok(pairs, weights):
    if (type(pairs) is not list or len(pairs) > 64
            or type(weights) is not list or len(weights) != len(pairs)
            or any(type(weight) is not int or not 0 <= weight <= 3 for weight in weights)):
        raise verify.InvalidCertificate("expected one integer weight from zero to three per demand")


def weighted_capacity_bound(adjacency, pairs, weights, capacity, budget):
    """Check every inclusion-minimal positive-demand subset of weight > M.

    Such a subset has at most M+1 demands. Its minimality is equivalent to
    total weight minus its smallest weight being <= M. An independent set
    whose demand weight exceeds M would contain one of these subsets.
    """
    weights_ok(pairs, weights)
    if type(capacity) is not int or not 0 <= capacity <= sum(weights):
        raise verify.InvalidCertificate("invalid weighted attachment capacity")
    positive = [i for i, weight in enumerate(weights) if weight > 0]
    unit_weights = all(weights[i] == 1 for i in positive)
    sizes = ((capacity + 1,) if unit_weights
             else range(1, min(capacity + 1, len(positive)) + 1))
    budget.reserve(sum(math.comb(len(positive), size) for size in sizes))
    masks = [(1 << u) | (1 << v) for u, v in pairs]
    for size in sizes:
        for selected in itertools.combinations(positive, size):
            budget.considered += 1
            if budget.considered % 1024 == 0:
                budget.check()
            total = sum(weights[i] for i in selected)
            if total <= capacity or total - min(weights[i] for i in selected) > capacity:
                continue
            vertices = 0
            for index in selected:
                vertices |= masks[index]
            budget.checked += 1
            if not verify.contains_edge(adjacency, vertices):
                return {"demand_indices": list(selected), "total_weight": total,
                        "independent_endpoint_mask": vertices}
    budget.check()
    return None


def verify_claim(adjacency, pairs, weights, capacity, centre_degree, budget):
    verify.graph_ok(adjacency)
    verify.demands_ok(adjacency, pairs)
    weights_ok(pairs, weights)
    total = sum(weights)
    if type(capacity) is not int or not 0 <= capacity < total:
        raise verify.InvalidCertificate("invalid weighted attachment capacity")
    if type(centre_degree) is not int or not 1 <= centre_degree <= 9:
        raise verify.InvalidCertificate("invalid centre degree")
    if total <= centre_degree * capacity:
        raise verify.InvalidCertificate("the strict weighted covering inequality does not hold")
    before_checked, before_considered = budget.checked, budget.considered
    counterexample = weighted_capacity_bound(adjacency, pairs, weights, capacity, budget)
    if counterexample is not None:
        raise verify.InvalidCertificate("weighted capacity is false: " + json.dumps(counterexample))
    return {"vertices_in_h": len(adjacency), "centre_degree": centre_degree,
            "edges_in_h": sum(row.bit_count() for row in adjacency) // 2,
            "selected_demands": sum(weight > 0 for weight in weights),
            "total_demand_weight": total, "capacity_bound": capacity,
            "attachment_capacity": centre_degree * capacity,
            "demand_combinations_considered": budget.considered - before_considered,
            "minimal_overweight_subsets_checked": budget.checked - before_checked,
            "maximal_extension_excluded": True}


def verify_case(case, sample, budget):
    if (type(case) is not dict or set(case) !=
            {"sample_index", "demands", "weights", "capacity_bound", "source"}):
        raise verify.InvalidCertificate("unexpected weighted certificate fields")
    index = case["sample_index"]
    if type(index) is not int or index not in sample:
        raise verify.InvalidCertificate("unknown sample index")
    if type(case["source"]) is not str or case["source"] not in PROOF_SOURCES:
        raise verify.InvalidCertificate("unknown certificate source")
    weights_ok(case["demands"], case["weights"])
    if any(weight == 0 for weight in case["weights"]):
        raise verify.InvalidCertificate("the compact certificate must omit zero-weight demands")
    result = verify_claim(sample[index]["adjacency"], case["demands"], case["weights"],
                          case["capacity_bound"], 6, budget)
    result.update({"sample_index": index, "adjacency_sha256": sample[index]["adjacency_sha256"]})
    return result


def sample_graphs(value, budget):
    if type(value) is not list or len(value) != 128:
        raise verify.InvalidCertificate("expected the exact 128-graph sample")
    indexed, seen_bytes = {}, set()
    for row in value:
        budget.check()
        if type(row) is not dict or set(row) != {"index", "adjacency", "adjacency_sha256"}:
            raise verify.InvalidCertificate("unexpected sample graph fields")
        index = row["index"]
        if type(index) is not int or not 0 <= index < 128 or index in indexed:
            raise verify.InvalidCertificate("invalid or duplicate sample index")
        adjacency = row["adjacency"]
        if type(adjacency) is not list or len(adjacency) != 33:
            raise verify.InvalidCertificate("this sample requires order 33")
        verify.graph_ok(adjacency)
        if (not verify.valid_digest(row["adjacency_sha256"])
                or verify.adjacency_digest(adjacency) != row["adjacency_sha256"]):
            raise verify.InvalidCertificate("labelled adjacency digest differs")
        raw = json.dumps(adjacency, separators=(",", ":")).encode()
        if raw in seen_bytes:
            raise verify.InvalidCertificate("duplicate labelled graph bytes")
        seen_bytes.add(raw)
        indexed[index] = row
    return indexed


def verify_bundle(bundle, budget=None):
    expected = {"schema_version", "kind", "centre_degree", "sources", "sample",
                "certificates", "remaining_indices"}
    if type(bundle) is not dict or set(bundle) != expected:
        raise verify.InvalidCertificate("unexpected sampled-bundle fields")
    if (type(bundle["schema_version"]) is not int or bundle["schema_version"] != 1
            or bundle["kind"] != KIND or type(bundle["centre_degree"]) is not int
            or bundle["centre_degree"] != 6):
        raise verify.InvalidCertificate("unsupported sampled-certificate format")
    sources = bundle["sources"]
    if (type(sources) is not dict or set(sources) != SOURCES
            or any(not verify.valid_digest(value) for value in sources.values())):
        raise verify.InvalidCertificate("invalid sampled-source identifiers")
    certificates, remaining = bundle["certificates"], bundle["remaining_indices"]
    if type(certificates) is not list or len(certificates) != 113:
        raise verify.InvalidCertificate("expected the 113 sampled certificates")
    if (type(remaining) is not list or len(remaining) != 15
            or any(type(index) is not int or not 0 <= index < 128 for index in remaining)
            or remaining != sorted(set(remaining))):
        raise verify.InvalidCertificate("invalid remaining sample indices")
    budget = budget or Budget()
    sample = sample_graphs(bundle["sample"], budget)
    claimed_indices = []
    for case in certificates:
        if type(case) is not dict or type(case.get("sample_index")) is not int:
            raise verify.InvalidCertificate("invalid certificate sample index")
        claimed_indices.append(case["sample_index"])
    if (len(set(claimed_indices)) != 113
            or sorted(claimed_indices + remaining) != list(range(128))):
        raise verify.InvalidCertificate("certified and remaining indices do not partition the sample")
    results = [verify_case(case, sample, budget)
               for case in sorted(certificates, key=lambda case: case["sample_index"])]
    budget.check()
    return {"kind": KIND, "status": "verified", "scope":
            "The 113 listed H instances cannot be G minus N[c] for a maximal triangle-free G with degree(c)=6.",
            "sample_size": 128, "certified_exclusions": 113,
            "remaining_indices": remaining,
            "remaining_scope": "These 15 inputs have no certificate in this bundle; their extensions are not established.",
            "nonmaximal_extensions_excluded": False,
            "complete_catalogue_claim_made": False,
            "global_ramsey_bound_claim_made": False,
            "cases": results, "demand_combinations_considered": budget.considered,
            "minimal_overweight_subsets_checked": budget.checked,
            "cpu_seconds": time.process_time() - budget.start}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path,
                        default=Path(__file__).with_name("sampled-certificates.json"))
    args = parser.parse_args()
    try:
        bundle, file_hash = verify.read_bundle(args.input)
        result = verify_bundle(bundle)
        result["input_sha256"] = file_hash
        print(json.dumps(result, indent=2, allow_nan=False))
    except verify.VerificationLimit as error:
        print(json.dumps({"status": "unknown", "reason": str(error)}))
        sys.exit(2)
    except (ValueError, OSError, TypeError, KeyError, OverflowError) as error:
        print(json.dumps({"status": "rejected", "reason": str(error)}))
        sys.exit(1)
