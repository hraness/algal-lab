"""Incremental search with an exact, separately implemented graph checker."""

import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

from encoding import independent_clause
from native import Solver

_checker_spec = importlib.util.spec_from_file_location(
    "_r310_degree_six_checker", Path(__file__).resolve().parents[1] / "vertex_transitive/checker.py")
_checker = importlib.util.module_from_spec(_checker_spec)
sys.modules[_checker_spec.name] = _checker
_checker_spec.loader.exec_module(_checker)
SearchLimit = _checker.SearchLimit
independent_set = _checker.independent_set
triangle = _checker.triangle
validate_adjacency = _checker.validate_adjacency
verify_independent = _checker.verify_independent


def peak_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def validate_structure(adj, metadata):
    validate_adjacency(adj)
    n, degree = metadata["order"], metadata["centre_degree"]
    if len(adj) != n or triangle(adj) is not None:
        raise ValueError("model is not a triangle-free graph of the required order")
    if adj[0] != sum(1 << v for v in range(1, degree + 1)):
        raise ValueError("model has the wrong fixed neighborhood")
    if any(not metadata["minimum_degree"] <= row.bit_count() <= metadata["maximum_degree"]
           for row in adj):
        raise ValueError("model violates a degree bound")
    if metadata["centre_coverage_required"] and any(
            not row & adj[0] for row in adj[degree + 1:]):
        raise ValueError("model violates neighborhood coverage")
    if "strengthening" in metadata:
        check_strengthening(adj, degree, metadata["strengthening"])


def check_strengthening(adj, centre, bounds):
    """Recount profile constraints from graph edges, independently of CNF cells."""
    a = list(range(1, centre + 1))
    h = list(range(centre + 1, len(adj)))
    h_mask = sum(1 << v for v in h)
    h_edges = sum((adj[v] & h_mask).bit_count() for v in h) // 2
    signatures = [tuple(bool(adj[v] >> u & 1) for u in a) for v in h]
    cross_edges = sum(sum(row) for row in signatures)
    if h_edges < bounds["anti_neighborhood_minimum_edges"]:
        raise ValueError("model violates anti-neighborhood edge bound")
    if cross_edges < bounds["neighborhood_cross_minimum_edges"]:
        raise ValueError("model violates cross-edge bound")
    if signatures != sorted(signatures):
        raise ValueError("model violates signature order")
    for u in range(centre):
        if sum(row[u] and sum(row) == 1 for row in signatures) > bounds["private_neighbor_maximum"]:
            raise ValueError("model violates private-neighbor bound")
    if sum(row.bit_count() for row in adj) // 2 < bounds["implied_global_minimum_edges"]:
        raise ValueError("model violates implied global edge bound")


def graph_digest(adj):
    return hashlib.sha256(json.dumps(adj, separators=(",", ":")).encode()).hexdigest()


def additional_independent_sets(adj, target, first, limit, stop):
    """List a bounded number of real counterexamples; never certify absence."""
    found, nodes, halted = [first], 0, False

    def visit(available, chosen):
        nonlocal nodes, halted
        nodes += 1
        if nodes % 256 == 0 and stop():
            halted = True
        if halted or len(found) >= limit or nodes > 100_000:
            return
        need = target - chosen.bit_count()
        if not need:
            if chosen != first:
                found.append(chosen)
            return
        while available.bit_count() >= need and len(found) < limit:
            bit = available & -available
            available ^= bit
            vertex = bit.bit_length() - 1
            visit(available & ~adj[vertex], chosen | bit)
            if halted or nodes > 100_000:
                return

    if limit > 1:
        visit((1 << len(adj)) - 1, 0)
    return found


def search(formula, variable, metadata, library, *, stop, cut_limit=100_000,
           model_limit=20_000, batch_size=256, seed=0, event=None, fixed_graph=None):
    if not (1 <= cut_limit <= 100_000 and 1 <= model_limit <= 20_000
            and 1 <= batch_size <= 256):
        raise ValueError("search limit outside supported bounds")
    target, n = metadata["independent_set_target"], metadata["order"]
    event = event or (lambda *_: None)
    cuts, seen, models, last_graph = [], set(), 0, None
    with Solver(library, formula.variables, seed=seed, terminate=stop,
                freeze=variable.values()) as solver:
        for clause in formula.clauses:
            solver.add(clause)
        if fixed_graph is not None:
            # Used only by controls. These extra constraints are saved too.
            validate_structure(fixed_graph, metadata)
            for (u, v), literal in variable.items():
                clause = (literal if fixed_graph[u] >> v & 1 else -literal,)
                formula.clauses.append(clause)
                solver.add(clause)
        while True:
            if stop():
                status = "resource_limit"
                break
            if models >= model_limit:
                status = "model_limit"
                break
            event("before_solve", {"models": models, "cuts": len(cuts)})
            result = solver.solve()
            if result == 0:
                status = "solver_interrupted"
                break
            if result == 20:
                status = "unverified_unsat"
                break
            models += 1
            adj = [0] * n
            for (u, v), literal in variable.items():
                if solver.value(literal):
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
            validate_structure(adj, metadata)
            last_graph = adj
            event("model", {"number": models, "adjacency": adj, "sha256": graph_digest(adj)})
            try:
                first = independent_set(adj, target, node_limit=1_000_000,
                                        deadline=time.monotonic() + 2)
            except SearchLimit as error:
                status = "graph_check_limit"
                event("checker_limit", {"reason": str(error)})
                break
            if first is None:
                # This conclusion comes from the separate graph checker,
                # never from satisfaction of the current partial SAT formula.
                status = "candidate_found"
                event("candidate", {"adjacency": adj, "sha256": graph_digest(adj)})
                break
            if len(cuts) >= cut_limit:
                status = "cut_limit"
                break
            batch = additional_independent_sets(
                adj, target, first, min(batch_size, cut_limit - len(cuts)), stop)
            if len(batch) != len(set(batch)):
                raise RuntimeError("duplicate cut within a generated batch")
            for mask in batch:
                if not verify_independent(adj, mask, target) or mask.bit_count() != target:
                    raise RuntimeError("counterexample checker rejected a generated cut")
                if mask in seen:
                    raise RuntimeError("solver model violates a previously added cut")
            # Persist the complete batch before submitting it. If an external
            # kill interrupts submission, replay may include extra valid cuts.
            event("cuts", {"model": models, "graph_sha256": graph_digest(adj), "masks": batch})
            for mask in batch:
                clause = independent_clause(mask, variable, target)
                solver.add(clause)
                seen.add(mask)
                cuts.append(mask)
        return {"status": status, "models": models, "cuts": cuts,
                "last_graph": last_graph, "solver_signature": solver.signature,
                "unsat_verified": False,
                "graph_checked_without_independent_target_set": status == "candidate_found"}
