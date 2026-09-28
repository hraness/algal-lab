"""Attempt one selector case with separately bounded solve and proof checks."""

import argparse
import json
from pathlib import Path
import sys

from catalogue import ramsey_catalogue
from process import run_process
from proof import lines
from run import parse_model, snapshot
from selector import PROFILE, catalogue_columns, check_cover, write_instance
from selector_proof import verify
from shared import Budget, digest, peak_bytes, source_hashes, write_json


def control_inventory(control):
    required = {"columns", "row_caps", "exact_rows", "missed_eight_set_bitsets", "choose"}
    if type(control) is not dict or set(control) != required:
        raise ValueError("unknown or missing small selector control field")
    return {**control, "scope": "small selector control only", "profile": PROFILE}


def audit_cover(output, metadata, inventory, budget):
    values = parse_model(output / "solver.log", metadata["variables"])
    count = 0
    for line in lines(output / "instance.cnf", 32 * 1024**2):
        if line.startswith("p "):
            continue
        literals = list(map(int, line.split()))
        if not literals or literals[-1] != 0 or 0 in literals[:-1]:
            raise ValueError("invalid selector archived CNF clause")
        if not any(values[abs(literal)] == (literal > 0) for literal in literals[:-1]):
            raise ValueError("selector model violates archived CNF")
        count += 1
        if count % 256 == 0:
            budget.check()
    if count != metadata["clauses"]:
        raise ValueError("selector CNF clause inventory mismatch")
    selected = [variable - 1 for variable in range(1, metadata["selector_variables"] + 1)
                if values[variable]]
    check_cover(inventory, selected)
    result = {"status": "necessary_cover_found", "selected_column_indices": selected,
              "selected_columns": [inventory["columns"][index] for index in selected],
              "sat_is_only_a_cover": True, "ramsey_graph_found": False}
    write_json(output / "cover.json", result)
    budget.check()
    return result


def worker(output, stage):
    protocol = json.loads((output / "protocol.json").read_text())
    if protocol["profile"] != PROFILE or source_hashes() != protocol["source_sha256"]:
        raise ValueError("selector profile or source snapshot differs from protocol")
    budget = Budget(protocol["construction_seconds"] if stage == "construct" else protocol["audit_seconds"],
                    protocol["memory_mib"])
    if stage == "construct":
        control = protocol["small_control"]
        if control is None:
            catalogue = ramsey_catalogue(budget=budget)
            if not 0 <= protocol["case_index"] < len(catalogue["cases"]):
                raise ValueError("selector case outside catalogue")
            selected = catalogue["cases"][protocol["case_index"]]
            inventory = catalogue_columns(selected["adjacency"], budget=budget)
            inventory.update({"case_index": selected["index"],
                              "representative_pair": selected["representative_pair"],
                              "pair_deletion_scope": catalogue["scope"]})
            write_json(output / "catalogue.json", catalogue)
        else:
            inventory = control_inventory(control)
        write_json(output / "columns.json", inventory)
        metadata = write_instance(output, inventory, budget=budget)
        metadata.update({"source_sha256": protocol["source_sha256"],
                         "columns_sha256": digest(output / "columns.json")})
        write_json(output / "instance.json", metadata)
        result = {"status": "constructed", "cnf_sha256": metadata["cnf_sha256"],
                  "variables": metadata["variables"], "clauses": metadata["clauses"],
                  "selector_variables": metadata["selector_variables"]}
    else:
        metadata = json.loads((output / "instance.json").read_text())
        if (metadata["profile"] != PROFILE or digest(output / "instance.cnf") != metadata["cnf_sha256"]
                or digest(output / "columns.json") != metadata["columns_sha256"]):
            raise ValueError("selector artifacts differ from construction record")
        solve = json.loads((output / "solve-stage.json").read_text())
        if solve["external_stop"] is not None:
            raise ValueError("interrupted selector solve cannot enter audit")
        if solve["returncode"] == 20:
            result = {"status": "selector_rup_verified", "python_rup_verified": True,
                      "proof_verification": verify(output / "instance.cnf", output / "proof.lrat",
                                                   profile=PROFILE, budget=budget)}
        elif solve["returncode"] == 10:
            result = audit_cover(output, metadata, json.loads((output / "columns.json").read_text()), budget)
        else:
            raise ValueError("selector solver did not return SAT or UNSAT")
    budget.check()
    result["peak_bytes"] = peak_bytes()
    write_json(output / f"{stage}-result.json", result)


def run_attempt(output, solver, lrat_trim, *, case=0, construction_seconds=60,
                solve_seconds=90, audit_seconds=90, memory_mib=1024,
                small_control=None, construct_only=False):
    if (type(case) is not int or not 0 <= case < 7 or not 0 < construction_seconds <= 60
            or not 0 < solve_seconds <= 90 or not 0 < audit_seconds <= 90
            or not 64 <= memory_mib <= 1024 or type(construct_only) is not bool):
        raise ValueError("selector resource setting outside supported bounds")
    if small_control is not None:
        control_inventory(small_control)
    output = Path(output).resolve()
    solver, lrat_trim = Path(solver).resolve(strict=True), Path(lrat_trim).resolve(strict=True)
    output.mkdir(parents=True, exist_ok=False)
    protocol = {"schema_version": 1, "profile": PROFILE, "case_index": case,
                "construction_seconds": construction_seconds, "solve_seconds": solve_seconds,
                "audit_seconds": audit_seconds, "memory_mib": memory_mib,
                "source_sha256": snapshot(output), "solver_sha256": digest(solver),
                "lrat_trim_sha256": digest(lrat_trim), "small_control": small_control,
                "construct_only": construct_only, "cases_in_this_attempt": 1}
    write_json(output / "protocol.json", protocol)
    result = {"schema_version": 1, "profile": PROFILE, "status": "incomplete",
              "necessary_selector_formula_unsat": False, "python_rup_verified": False,
              "lrat_trim_verified": False, "sat_is_only_a_cover": True,
              "ramsey_graph_found": False, "external_ramsey_bound_claim_made": False,
              "source_sha256": protocol["source_sha256"], "stages": {}, "supervisor_signal": None}
    result_path = output / "result.json"
    write_json(result_path, result)
    driver = output / "source" / "fixed_remainder" / "selector_run.py"

    def stage(name, command, seconds, file_bytes=256 * 1024**2):
        report = run_process(command, output / f"{name if name != 'solve' else 'solver'}.log",
                             output / f"{name}-stage.json", cpu_seconds=seconds,
                             wall_seconds=seconds + 30, memory_mib=memory_mib, file_bytes=file_bytes)
        result["stages"][name] = report
        result["supervisor_signal"] = report["supervisor_signal"]
        write_json(result_path, result)
        return report

    construct = stage("construct", [sys.executable, driver, "--worker", "construct", "--output", output],
                      construction_seconds, 32 * 1024**2)
    if construct["returncode"] != 0 or construct["external_stop"] is not None:
        result["status"] = "construction_incomplete"
    elif construct_only:
        result["status"] = "constructed_not_solved"
    else:
        identities = (("solver-version", solver, protocol["solver_sha256"]),
                      ("lrat-trim-version", lrat_trim, protocol["lrat_trim_sha256"]))
        identity_ok = True
        for name, binary, expected in identities:
            report = stage(name, [binary, "--version"], 5, 1024 * 1024)
            if report["returncode"] != 0 or report["external_stop"] is not None:
                identity_ok = False
                break
            version = (output / f"{name}.log").read_text().strip()
            if len(version) > 1000 or digest(binary) != expected:
                raise ValueError("selector tool identity changed or is invalid")
            result[name] = version
        if not identity_ok:
            result["status"] = "tool_identity_incomplete"
        else:
            solve = stage("solve", [solver, "--lrat", "--no-binary", "--no-factor", "-q", "-t",
                                    str(max(1, int(solve_seconds))), output / "instance.cnf",
                                    output / "proof.lrat"], solve_seconds)
            if solve["returncode"] in (10, 20) and solve["external_stop"] is None:
                result["status"] = "selector_unsat_unverified" if solve["returncode"] == 20 else "selector_sat_unverified"
                audit = stage("audit", [sys.executable, driver, "--worker", "audit", "--output", output], audit_seconds)
                if audit["returncode"] == 0 and audit["external_stop"] is None:
                    result.update(json.loads((output / "audit-result.json").read_text()))
                    if solve["returncode"] == 20:
                        if digest(lrat_trim) != protocol["lrat_trim_sha256"]:
                            raise ValueError("lrat-trim changed before verification")
                        trim = stage("lrat-trim", [lrat_trim, "--no-trim", output / "instance.cnf",
                                                   output / "proof.lrat"], audit_seconds)
                        verified = trim["returncode"] == 20 and trim["external_stop"] is None
                        if verified:
                            verified = "s VERIFIED" in (output / "lrat-trim.log").read_text().splitlines()
                        if verified:
                            result.update({"status": "selector_unsat_dual_verified",
                                           "necessary_selector_formula_unsat": True, "lrat_trim_verified": True})
                        else:
                            result["status"] = "selector_second_check_incomplete"
            else:
                result["status"] = "solve_incomplete"
    # Every stage's log hash is inside its receipt. Preserve the source,
    # premise, formula, proof, and all process/worker reports in one inventory.
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "result.json" and path.suffix in (".json", ".cnf", ".lrat"):
            result.setdefault("artifact_sha256", {})[path.name] = digest(path)
    write_json(result_path, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver", type=Path)
    parser.add_argument("--lrat-trim", type=Path)
    parser.add_argument("--case", type=int, default=0)
    parser.add_argument("--construction-seconds", type=float, default=60)
    parser.add_argument("--solve-seconds", type=float, default=90)
    parser.add_argument("--audit-seconds", type=float, default=90)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--construct-only", action="store_true")
    parser.add_argument("--worker", choices=("construct", "audit"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker(args.output, args.worker)
    else:
        if args.solver is None or args.lrat_trim is None:
            parser.error("--solver and --lrat-trim are required")
        report = run_attempt(args.output, args.solver, args.lrat_trim, case=args.case,
                             construction_seconds=args.construction_seconds, solve_seconds=args.solve_seconds,
                             audit_seconds=args.audit_seconds, memory_mib=args.memory_mib,
                             construct_only=args.construct_only)
        print(json.dumps(report, indent=2))
        if report["supervisor_signal"] is not None:
            raise SystemExit(128 + report["supervisor_signal"])
