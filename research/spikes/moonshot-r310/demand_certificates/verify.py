"""Verify the nine finite demand-subset certificates using only Python's stdlib."""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time

KIND = "fixed-remainder-demand-subsets-v1"
MAX_INPUT_BYTES = 1024 * 1024
MAX_SUBSETS = 200_000


class InvalidCertificate(ValueError):
    pass


class VerificationLimit(RuntimeError):
    pass


class Budget:
    def __init__(self, subsets=MAX_SUBSETS, seconds=10):
        if (type(subsets) is not int or not 1 <= subsets <= MAX_SUBSETS
                or type(seconds) not in (int, float) or not 0 < seconds <= 10):
            raise ValueError("unsupported verification allowance")
        self.start = time.process_time()
        self.seconds, self.limit, self.reserved, self.checked = seconds, subsets, 0, 0

    def reserve(self, subsets):
        self.check()
        if self.reserved + subsets > self.limit:
            raise VerificationLimit("demand-subset allowance exceeded")
        self.reserved += subsets

    def check(self):
        if time.process_time() - self.start >= self.seconds:
            raise VerificationLimit("verification CPU allowance exceeded")


def adjacency_digest(adjacency):
    return hashlib.sha256(json.dumps(adjacency, separators=(",", ":")).encode()).hexdigest()


def valid_digest(value):
    return type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def graph_ok(adjacency):
    if type(adjacency) is not list or not 1 <= len(adjacency) <= 33:
        raise InvalidCertificate("expected one to 33 adjacency masks")
    n = len(adjacency)
    if any(type(row) is not int or not 0 <= row < 1 << n for row in adjacency):
        raise InvalidCertificate("invalid adjacency mask")
    for u in range(n):
        if adjacency[u] >> u & 1:
            raise InvalidCertificate("graph has a loop")
        for v in range(u + 1, n):
            edge = adjacency[u] >> v & 1
            if edge != (adjacency[v] >> u & 1):
                raise InvalidCertificate("adjacency is not symmetric")
            if edge and adjacency[u] & adjacency[v]:
                raise InvalidCertificate("graph contains a triangle")


def demands_ok(adjacency, pairs):
    if type(pairs) is not list or not 1 <= len(pairs) <= 64:
        raise InvalidCertificate("expected one to 64 selected demands")
    seen = set()
    for pair in pairs:
        if (type(pair) is not list or len(pair) != 2 or any(type(v) is not int for v in pair)
                or not 0 <= pair[0] < pair[1] < len(adjacency)):
            raise InvalidCertificate("invalid demand pair")
        u, v = pair
        if (u, v) in seen:
            raise InvalidCertificate("duplicate demand")
        seen.add((u, v))
        if adjacency[u] >> v & 1:
            raise InvalidCertificate("a selected demand is an H edge")
        if adjacency[u] & adjacency[v]:
            raise InvalidCertificate("a selected demand has a common H-neighbour")


def contains_edge(adjacency, vertices):
    while vertices:
        bit = vertices & -vertices
        vertices ^= bit
        if adjacency[bit.bit_length() - 1] & vertices:
            return True
    return False


def capacity_bound(adjacency, pairs, capacity, budget):
    """Return a counterexample or prove every independent set contains <=M pairs.

    Validated pairs are distinct. An independent set containing M+1 demands
    would contain the independent endpoint union of that demand subset.
    """
    if type(capacity) is not int or not 0 <= capacity <= len(pairs):
        raise InvalidCertificate("invalid attachment capacity")
    total = math.comb(len(pairs), capacity + 1)
    budget.reserve(total)
    masks = [(1 << u) | (1 << v) for u, v in pairs]
    for selected in itertools.combinations(range(len(pairs)), capacity + 1):
        vertices = 0
        for index in selected:
            vertices |= masks[index]
        budget.checked += 1
        if budget.checked % 1024 == 0:
            budget.check()
        if not contains_edge(adjacency, vertices):
            return {"demand_indices": list(selected), "independent_endpoint_mask": vertices}
    budget.check()
    return None


def verify_claim(adjacency, pairs, capacity, centre_degree, budget):
    graph_ok(adjacency)
    demands_ok(adjacency, pairs)
    if type(capacity) is not int or not 0 <= capacity < len(pairs):
        raise InvalidCertificate("invalid attachment capacity")
    if type(centre_degree) is not int or not 1 <= centre_degree <= 9:
        raise InvalidCertificate("invalid centre degree")
    if len(pairs) <= centre_degree * capacity:
        raise InvalidCertificate("the strict covering inequality does not hold")
    before = budget.checked
    counterexample = capacity_bound(adjacency, pairs, capacity, budget)
    if counterexample is not None:
        raise InvalidCertificate("attachment capacity is false: " + json.dumps(counterexample))
    return {"vertices_in_h": len(adjacency), "centre_degree": centre_degree,
            "edges_in_h": sum(row.bit_count() for row in adjacency) // 2,
            "selected_demands": len(pairs), "capacity_bound": capacity,
            "attachment_capacity": centre_degree * capacity,
            "demand_subsets_checked": budget.checked - before,
            "maximal_extension_excluded": True}


def verify_case(case, centre_degree, budget):
    expected = {"class", "adjacency", "adjacency_sha256", "demands", "capacity_bound", "source"}
    if type(case) is not dict or set(case) != expected:
        raise InvalidCertificate("unexpected certificate fields")
    if type(case["class"]) is not int or not 0 <= case["class"] <= 8:
        raise InvalidCertificate("invalid local class label")
    if case["source"] not in ("unit_census", "weighted_proposals"):
        raise InvalidCertificate("unknown provenance source")
    adjacency = case["adjacency"]
    if type(adjacency) is not list or len(adjacency) != 33:
        raise InvalidCertificate("this bundle requires order 33")
    if not valid_digest(case["adjacency_sha256"]) or adjacency_digest(adjacency) != case["adjacency_sha256"]:
        raise InvalidCertificate("labelled adjacency digest differs")
    result = verify_claim(adjacency, case["demands"], case["capacity_bound"], centre_degree, budget)
    result.update({"class": case["class"], "adjacency_sha256": case["adjacency_sha256"]})
    return result


def verify_bundle(bundle, budget=None):
    if type(bundle) is not dict or set(bundle) != {"schema_version", "kind", "centre_degree", "sources", "cases"}:
        raise InvalidCertificate("unexpected bundle fields")
    if (type(bundle["schema_version"]) is not int or bundle["schema_version"] != 1 or bundle["kind"] != KIND
            or type(bundle["centre_degree"]) is not int or bundle["centre_degree"] != 6):
        raise InvalidCertificate("unsupported certificate format")
    sources = bundle["sources"]
    if (type(sources) is not dict or set(sources) != {"unit_census", "weighted_proposals"}
            or any(not valid_digest(value) for value in sources.values())):
        raise InvalidCertificate("invalid source identifiers")
    cases = bundle["cases"]
    if type(cases) is not list or len(cases) != 9:
        raise InvalidCertificate("expected the nine specified finite certificates")
    budget = budget or Budget()
    results, seen = [], set()
    for case in cases:
        result = verify_case(case, 6, budget)
        if result["class"] in seen:
            raise InvalidCertificate("duplicate local class label")
        seen.add(result["class"])
        results.append(result)
    if seen != set(range(9)):
        raise InvalidCertificate("local class labels differ")
    budget.check()
    return {"kind": KIND, "status": "verified", "scope":
            "The nine exact H instances cannot be G minus N[c] for a maximal triangle-free G with degree(c)=6.",
            "global_ramsey_bound_claim_made": False, "cases": results,
            "demand_subsets_checked": budget.checked, "cpu_seconds": time.process_time() - budget.start}


def unique_fields(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise InvalidCertificate("duplicate JSON object field")
        result[name] = value
    return result


def reject_constant(value):
    raise InvalidCertificate("nonfinite JSON number: " + value)


def read_bundle(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise InvalidCertificate("certificate file exceeds its size limit")
    return json.loads(raw, object_pairs_hook=unique_fields, parse_constant=reject_constant), hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path(__file__).with_name("certificates.json"))
    args = parser.parse_args()
    try:
        bundle, file_hash = read_bundle(args.input)
        result = verify_bundle(bundle)
        result["input_sha256"] = file_hash
        print(json.dumps(result, indent=2, allow_nan=False))
    except VerificationLimit as error:
        print(json.dumps({"status": "unknown", "reason": str(error)}))
        sys.exit(2)
    except (ValueError, OSError, TypeError) as error:
        print(json.dumps({"status": "rejected", "reason": str(error)}))
        sys.exit(1)
