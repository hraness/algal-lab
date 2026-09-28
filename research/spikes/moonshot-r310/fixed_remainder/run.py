"""Construct and attempt ONE fixed-remainder case with separately bounded stages."""

import argparse
import json
from pathlib import Path
import shutil
import sys

from catalogue import ramsey_catalogue
from encode import extension, write_instance
from process import run_process
from proof import lines, verify
from shared import Budget, HERE, checker, digest, peak_bytes, source_hashes, sources, write_json


def parse_model(path, variables):
    values = {}
    for line in lines(path, 1024 * 1024):
        if not line.startswith("v "):
            continue
        for literal in map(int, line[2:].split()):
            if literal == 0:
                continue
            if not 1 <= abs(literal) <= variables:
                raise ValueError("model variable outside formula")
            variable, value = abs(literal), literal > 0
            if variable in values and values[variable] != value:
                raise ValueError("contradictory model values")
            values[variable] = value
    if len(values) != variables:
        raise ValueError("incomplete model")
    return values


def audit_model(output, metadata, budget):
    values = parse_model(output / "solver.log", metadata["variables"])
    count = 0
    for line in lines(output / "instance.cnf", 128 * 1024**2):
        if line.startswith("p "):
            continue
        literals = list(map(int, line.split()))
        if not literals or literals[-1] != 0 or 0 in literals[:-1]:
            raise ValueError("invalid archived CNF clause")
        if not any(values[abs(literal)] == (literal > 0) for literal in literals[:-1]):
            raise ValueError("model violates archived CNF")
        count += 1
        if count % 256 == 0:
            budget.check()
    if count != metadata["clauses"]:
        raise ValueError("CNF clause inventory mismatch")
    positive = {variable for variable, value in values.items()
                if value and variable <= metadata["attachment_variables"]}
    graph = extension(metadata["base_adjacency"], metadata["neighbour_count"], positive)
    checker.validate_adjacency(graph)
    n, neighbours = metadata["base_order"], metadata["neighbour_count"]
    if len(graph) != metadata["extension_order"] or checker.triangle(graph) is not None:
        raise ValueError("candidate has wrong order or a triangle")
    if any(not metadata["minimum_degree"] <= row.bit_count() <= metadata["maximum_degree"]
           for row in graph):
        raise ValueError("candidate violates degree bounds")
    if metadata["centre_coverage_required"] and any(
            not any(graph[v] >> (n + a) & 1 for a in range(neighbours)) for v in range(n)):
        raise ValueError("candidate violates centre coverage")
    witness = checker.independent_set(graph, metadata["independent_set_target"],
                                      node_limit=1_000_000,
                                      deadline=budget.wall_start + budget.seconds)
    if witness is not None:
        raise ValueError("candidate contains an independent target set")
    budget.check()
    write_json(output / "candidate.json", graph)
    return {"status": "candidate_found", "graph_checked_without_independent_target_set": True,
            "cnf_sha256": digest(output / "instance.cnf"),
            "candidate_sha256": digest(output / "candidate.json")}


def worker(output, stage):
    protocol = json.loads((output / "protocol.json").read_text())
    if source_hashes() != protocol["source_sha256"]:
        raise ValueError("source snapshot differs from protocol")
    budget = Budget(protocol["construction_seconds"] if stage == "construct"
                    else protocol["audit_seconds"], protocol["memory_mib"])
    if stage == "construct":
        control = protocol.get("small_control")
        if control is None:
            catalogue = ramsey_catalogue(budget=budget)
            cases = catalogue["cases"]
            if not 0 <= protocol["case_index"] < len(cases):
                raise ValueError("case index outside catalogue")
            selected = cases[protocol["case_index"]]
            write_json(output / "catalogue.json", catalogue)
            metadata = write_instance(output, selected["adjacency"], budget=budget)
            metadata.update({"case_index": selected["index"],
                             "representative_pair": selected["representative_pair"],
                             "catalogue_sha256": digest(output / "catalogue.json"),
                             "scope": catalogue["scope"]})
        else:
            parameters = {key: value for key, value in control.items() if key != "adjacency"}
            metadata = write_instance(output, control["adjacency"], budget=budget, **parameters)
            metadata["scope"] = "small mathematical control only"
        metadata["source_sha256"] = protocol["source_sha256"]
        write_json(output / "instance.json", metadata)
        result = {"status": "constructed", "cnf_sha256": metadata["cnf_sha256"],
                  "variables": metadata["variables"], "clauses": metadata["clauses"]}
    else:
        metadata = json.loads((output / "instance.json").read_text())
        if digest(output / "instance.cnf") != metadata["cnf_sha256"]:
            raise ValueError("CNF differs from construction receipt")
        solve = json.loads((output / "solve-stage.json").read_text())
        if solve["external_stop"] is not None:
            raise ValueError("interrupted solve cannot enter proof/model audit")
        if solve["returncode"] == 20:
            result = {"status": "unsat_rup_verified", "unsat_verified": True,
                      "proof_verification": verify(output / "instance.cnf", output / "proof.lrat",
                                                   budget=budget)}
        elif solve["returncode"] == 10:
            result = audit_model(output, metadata, budget)
        else:
            raise ValueError("solver did not return SAT or UNSAT")
    budget.check()
    result["peak_bytes"] = peak_bytes()
    write_json(output / f"{stage}-result.json", result)


def snapshot(output):
    hashes = source_hashes()
    for relative in sources():
        source, destination = HERE.parent / relative, output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if digest(source) != hashes[relative] or digest(destination) != hashes[relative]:
            raise ValueError("source changed while snapshotting")
    return hashes


def run_attempt(output, solver, *, case=0, construction_seconds=60, solve_seconds=300,
                audit_seconds=300, memory_mib=1024, small_control=None, construct_only=False):
    if (type(case) is not int or not 0 <= case < 595 or not 0 < construction_seconds <= 60
            or not 0 < solve_seconds <= 300 or not 0 < audit_seconds <= 300
            or not 64 <= memory_mib <= 1024):
        raise ValueError("resource setting outside supported bounds")
    output, solver = Path(output).resolve(), Path(solver).resolve(strict=True)
    output.mkdir(parents=True, exist_ok=False)
    protocol = {"schema_version": 1, "case_index": case, "construction_seconds": construction_seconds,
                "solve_seconds": solve_seconds, "audit_seconds": audit_seconds,
                "memory_mib": memory_mib, "source_sha256": snapshot(output),
                "solver_sha256": digest(solver), "small_control": small_control,
                "construct_only": construct_only, "cases_in_this_attempt": 1}
    write_json(output / "protocol.json", protocol)
    result = {"schema_version": 1, "status": "incomplete", "unsat_verified": False,
              "graph_checked_without_independent_target_set": False,
              "external_ramsey_bound_claim_made": False,
              "source_sha256": protocol["source_sha256"], "stages": {}, "supervisor_signal": None}
    result_path = output / "result.json"
    write_json(result_path, result)
    driver = output / "source" / "fixed_remainder" / "run.py"

    def stage(name, command, seconds, file_bytes=256 * 1024**2):
        report = run_process(command, output / f"{name if name != 'solve' else 'solver'}.log",
                             output / f"{name}-stage.json", cpu_seconds=seconds,
                             wall_seconds=seconds + 30, memory_mib=memory_mib, file_bytes=file_bytes)
        result["stages"][name] = report
        result["supervisor_signal"] = report["supervisor_signal"]
        write_json(result_path, result)
        return report

    construct = stage("construct", [sys.executable, driver, "--worker", "construct",
                                     "--output", output], construction_seconds)
    if construct["returncode"] != 0 or construct["external_stop"] is not None:
        result["status"] = "construction_incomplete"
    elif construct_only:
        result["status"] = "constructed_not_solved"
    else:
        version = stage("version", [solver, "--version"], 5, 1024 * 1024)
        if version["returncode"] != 0 or version["external_stop"] is not None:
            result["status"] = "solver_identity_incomplete"
        else:
            result["solver_version"] = (output / "version.log").read_text().strip()
            if len(result["solver_version"]) > 1000 or digest(solver) != protocol["solver_sha256"]:
                raise ValueError("solver identity changed or is invalid")
            solve = stage("solve", [solver, "--lrat", "--no-binary", "--no-factor", "-q", "-t",
                                    str(max(1, int(solve_seconds))), output / "instance.cnf",
                                    output / "proof.lrat"], solve_seconds)
            if solve["returncode"] in (10, 20) and solve["external_stop"] is None:
                result["status"] = "unsat_unverified" if solve["returncode"] == 20 else "sat_unverified"
                audit = stage("audit", [sys.executable, driver, "--worker", "audit",
                                         "--output", output], audit_seconds)
                if audit["returncode"] == 0 and audit["external_stop"] is None:
                    result.update(json.loads((output / "audit-result.json").read_text()))
            else:
                result["status"] = "solve_incomplete"
    for name in ("protocol.json", "instance.cnf", "instance.json", "catalogue.json", "proof.lrat",
                 "construct-result.json", "audit-result.json", "construct-stage.json",
                 "version-stage.json", "solve-stage.json", "audit-stage.json"):
        if (output / name).exists():
            result.setdefault("artifact_sha256", {})[name] = digest(output / name)
    write_json(result_path, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver", type=Path)
    parser.add_argument("--case", type=int, default=0)
    parser.add_argument("--construction-seconds", type=float, default=60)
    parser.add_argument("--solve-seconds", type=float, default=300)
    parser.add_argument("--audit-seconds", type=float, default=300)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--construct-only", action="store_true")
    parser.add_argument("--worker", choices=("construct", "audit"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker(args.output, args.worker)
    else:
        if args.solver is None:
            parser.error("--solver is required")
        report = run_attempt(args.output, args.solver, case=args.case,
                             construction_seconds=args.construction_seconds, solve_seconds=args.solve_seconds,
                             audit_seconds=args.audit_seconds, memory_mib=args.memory_mib,
                             construct_only=args.construct_only)
        print(json.dumps(report, indent=2))
        if report["supervisor_signal"] is not None:
            raise SystemExit(128 + report["supervisor_signal"])
