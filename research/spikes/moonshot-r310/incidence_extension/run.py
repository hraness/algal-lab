"""One reviewed 60-CPU-second pilot, with controls before any real-case search."""

import argparse
import math
import os
from pathlib import Path
import resource
import sys
import time
import unittest

from audit import audit, check_graph, checked_subset
from encode import graph, validate_cut, write_instance
from proof import check_model, verify
from support import (Budget, INDEPENDENT_NODES, MAX_CNF_BYTES, MAX_CUTS, MAX_PROOF_BYTES,
                     MAX_ROUNDS, MAX_RUN_BYTES, PROFILE, SearchLimit, checker, digest,
                     disk_bytes, object_digest, process, read_json, require, snapshot,
                     source_hashes, total_cpu, write_json)

SELECTED = [19, 22, 25, 31, 43, 52, 57, 72, 92, 98, 100, 103, 106, 108, 119]
LIMITS = {"aggregate_cpu_seconds": 60, "wall_seconds": 80, "child_memory_mib": 896,
          "driver_memory_mib": 96, "memory_overhead_reserve_mib": 32,
          "disk_bytes": MAX_RUN_BYTES, "proof_bytes": MAX_PROOF_BYTES,
          "cnf_bytes": MAX_CNF_BYTES, "rounds": MAX_ROUNDS, "cuts": MAX_CUTS,
          "independent_search_nodes_per_call": INDEPENDENT_NODES, "pilot_cases": 1}


def review_ok(review, hashes, manifest_hash):
    require(type(review) is dict and set(review) == {"schema_version", "profile", "source_sha256",
            "manifest_sha256", "approved_for_pilot", "reviewer"}, "review schema")
    require(type(review["schema_version"]) is int and review["schema_version"] == 1
            and review["profile"] == PROFILE and review["source_sha256"] == hashes
            and review["manifest_sha256"] == manifest_hash and review["approved_for_pilot"] is True
            and type(review["reviewer"]) is str and review["reviewer"].strip(), "unbound independent review")


def negative_checked(audited, trim_returncode, trim_lines, cnf_hash, proof_hash, expected_cnf_hash):
    flags = ("independent_encoding_verified", "independent_cuts_verified",
             "H_triangle_free_and_alpha_at_most_eight_verified", "python_rup_verified")
    replay = audited.get("proof_replay", {})
    return (all(audited.get(key) is True for key in flags) and type(replay) is dict
            and replay.get("python_rup_verified") is True and trim_returncode == 20
            and "s VERIFIED" in trim_lines
            and audited.get("cnf_sha256") == replay.get("cnf_sha256") == cnf_hash == expected_cnf_hash
            and audited.get("proof_sha256") == replay.get("proof_sha256") == proof_hash)


def load_manifest(path, review_path):
    manifest, reviewed = read_json(path), read_json(review_path)
    hashes = source_hashes()
    require(type(manifest) is dict and set(manifest) == {"schema_version", "profile", "source_sha256",
            "inputs", "tools", "selected_indices", "pilot_index", "adjacency_sha256", "limits"}, "manifest fields")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1
            and manifest["profile"] == PROFILE and manifest["source_sha256"] == hashes
            and manifest["selected_indices"] == SELECTED and type(manifest["pilot_index"]) is int
            and manifest["pilot_index"] == 19 and manifest["limits"] == LIMITS, "pilot identity")
    review_ok(reviewed, hashes, digest(path))
    require(set(manifest["inputs"]) == {"admission_receipt", "admission_result", "coloring_acceptance"}, "input roles")
    inputs = {}
    for role, entry in manifest["inputs"].items():
        require(type(entry) is dict and set(entry) == {"path", "sha256"}, "input descriptor")
        require(digest(entry["path"]) == entry["sha256"], "input changed: " + role)
        inputs[role] = read_json(entry["path"])
        require(digest(entry["path"]) == entry["sha256"], "input changed during read")
    receipt, admitted, frontier = (inputs[role] for role in ("admission_receipt", "admission_result", "coloring_acceptance"))
    expected = manifest["inputs"]["admission_result"]["sha256"]
    require(receipt["status"] == "admitted_exact_128_candidate_sample" and receipt["candidate_count"] == 128
            and receipt["artifacts_sha256"]["result.json"] == expected and receipt["owned_child_collected"] is True
            and receipt["process_returncode"] == 0, "raw input admission")
    require(admitted["status"] == "all_128_candidates_independently_verified" and len(admitted["candidates"]) == 128,
            "admitted sample identity")
    require(frontier["status"] == "independent_review_passed" and frontier["remaining_indices"] == SELECTED
            and frontier["colorable_indices"] == SELECTED and frontier["new_excluded_indices"] == []
            and frontier["input_sha256"]["admission_result"] == expected, "accepted fifteen-input frontier")
    selected = [case for case in admitted["candidates"] if case["index"] == 19]
    require(len(selected) == 1 and selected[0]["order"] == 33, "one pilot graph")
    raw = selected[0]["adjacency"]
    require(len(raw) == 33 and object_digest(raw) == selected[0]["adjacency_sha256"] == manifest["adjacency_sha256"],
            "exact pilot adjacency")
    require(set(manifest["tools"]) == {"python", "solver", "lrat_trim"}, "tool roles")
    for role, entry in manifest["tools"].items():
        fields = {"path", "sha256", "version"} if role == "python" else {"path", "sha256"}
        require(type(entry) is dict and set(entry) == fields and digest(entry["path"]) == entry["sha256"], "tool identity")
    python = manifest["tools"]["python"]
    require(str(Path(sys.executable).resolve()) == python["path"] and sys.version == python["version"], "Python runtime")
    return manifest, reviewed, raw


def worker(output, task, index, seconds):
    protocol = read_json(output / "protocol.json")
    require(protocol["profile"] == PROFILE and protocol["source_sha256"] == source_hashes(), "snapshot identity")
    require(digest(output / "input.json") == protocol["input_sha256"], "input snapshot changed")
    raw = read_json(output / "input.json")
    budget = Budget(seconds)
    current = output / f"round-{index:03d}"
    if task == "controls":
        import test_focused
        test_focused.BUDGET = budget
        controls = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_focused))
        require(controls.testsRun == 7 and controls.wasSuccessful(), "focused controls failed")
        result = {"status": "passed", "tests": controls.testsRun, "source_sha256": source_hashes()}
        budget.check()
        write_json(output / "controls" / "result.json", result)
        return
    if task == "construct":
        require(checker.independent_set(raw, 9, node_limit=INDEPENDENT_NODES, deadline=budget.deadline) is None,
                "admitted H has an independent nine-set")
        metadata = write_instance(current, raw, [], budget)
        result = {"status": "constructed_and_independently_rebuilt", **metadata, **audit(current, raw, budget)}
    else:
        metadata = read_json(current / "instance.json")
        proof_stage = task == "proof"
        name = "proof-solve" if proof_stage else "solve"
        receipt = read_json(current / (name + ".json"))
        require(receipt["external_stop"] is None and receipt["owned_child_collected"] is True
                and receipt["returncode"] == (10 if task == "refine" else 20)
                and receipt["executable_sha256"] == protocol["tools"]["solver"]["sha256"]
                and receipt["log_sha256"] == digest(current / (name + ".log"))
                and digest(current / "instance.cnf") == metadata["cnf_sha256"], "solver/CNF identity")
        if task == "audit":
            result = {"status": "independently_rebuilt_before_proof_replay", **audit(current, raw, budget)}
        elif task == "proof":
            before = read_json(current / "audit-result.json")
            require(before["status"] == "independently_rebuilt_before_proof_replay"
                    and before["cnf_sha256"] == metadata["cnf_sha256"], "unmatched proof replay")
            reconstructed = audit(current, raw, budget)
            replay = verify(current / "instance.cnf", current / "proof.lrat", budget)
            require(reconstructed["cnf_sha256"] == replay["cnf_sha256"] == metadata["cnf_sha256"],
                    "reconstruction/proof replay changed the original CNF")
            result = {"status": "independently_rebuilt_and_RUP_verified", **reconstructed,
                      "python_rup_verified": replay["python_rup_verified"],
                      "proof_sha256": replay["proof_sha256"], "proof_replay": replay}
        elif task == "refine":
            model = check_model(current / "instance.cnf", current / "solve.log", budget)
            masks = [sum(1 << v for v in range(33) if model[1 + a * 33 + v]) for a in range(6)]
            candidate = graph(raw, masks)
            witness = check_graph(raw, masks, candidate, budget)
            write_json(current / "candidate.json", candidate)
            if witness is None:
                result = {"status": "locally_checked_candidate", "columns": masks,
                          "candidate_sha256": digest(current / "candidate.json"), **audit(current, raw, budget)}
            else:
                cut = {"subset": witness >> 7, "witness": witness, "columns": masks, "candidate": candidate}
                validate_cut(raw, cut)
                checked_subset(raw, cut, 6, 9)
                write_json(current / "new-cut.json", cut)
                cuts = read_json(current / "cuts.json")
                require(all(previous["subset"] != cut["subset"] for previous in cuts), "model violates a previous cut")
                if len(cuts) >= MAX_CUTS or index + 1 >= MAX_ROUNDS:
                    raise SearchLimit("cut/iteration bound; rejected candidate retained")
                cuts.append(cut)
                following = write_instance(output / f"round-{index + 1:03d}", raw, cuts, budget)
                result = {"status": "refined", "columns": masks, "independent_witness": witness,
                          "subset": cut["subset"], "next_round": index + 1, "next_instance": following}
        else:
            raise ValueError("unknown worker task")
    budget.check()
    write_json(current / (task + "-result.json"), result)


def run_attempt(output, manifest_path, review_path):
    budget = Budget(60, 96)
    require(not any(key.startswith("CADICAL_") for key in os.environ), "unrecorded solver environment options")
    manifest, reviewed, raw = load_manifest(manifest_path, review_path)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    hashes = snapshot(output)
    require(hashes == manifest["source_sha256"], "snapshot changed after review")
    write_json(output / "input.json", raw)
    (output / "inputs").mkdir()
    for role, entry in manifest["inputs"].items():
        data = Path(entry["path"]).read_bytes()
        destination = output / "inputs" / (role + ".json")
        destination.write_bytes(data)
        require(digest(destination) == entry["sha256"], "input snapshot mismatch")
    (output / "manifest.json").write_bytes(Path(manifest_path).read_bytes())
    (output / "source-review.json").write_bytes(Path(review_path).read_bytes())
    protocol = {"schema_version": 1, "profile": PROFILE, "source_sha256": hashes, "tools": manifest["tools"],
                "manifest_sha256": digest(manifest_path), "source_review_sha256": digest(review_path),
                "input_sha256": digest(output / "input.json"), "input_adjacency_sha256": object_digest(raw),
                "pilot_index": 19, "frontier_indices": SELECTED, "limits": LIMITS,
                "solver_environment_options": {}, "python_version": sys.version}
    write_json(output / "protocol.json", protocol)
    result = {"schema_version": 1, "profile": PROFILE, "status": "unknown", "pilot_index": 19,
              "fixed_input_excluded": False, "ramsey_graph_found": False, "new_ramsey_bound_claim": False,
              "locally_checked_exclusion": False, "locally_checked_candidate": False,
              "exploration_unsat_seen": False, "stages": [], "rounds": []}
    write_json(output / "result.json", result)
    driver = output / "source" / "incidence_extension" / "run.py"
    solver, trim_tool = (Path(manifest["tools"][role]["path"]) for role in ("solver", "lrat_trim"))

    def stage(name, directory, command, requested):
        budget.check()
        available = math.floor(60 - (total_cpu() - budget.start) - 5)
        allowance = min(available, math.floor(requested))
        wall = min(allowance + 10, budget.deadline - time.monotonic())
        remaining_disk = MAX_RUN_BYTES - disk_bytes(output) - 2 * 1024**2
        file_cap = min(MAX_PROOF_BYTES, remaining_disk // 2)
        if allowance < 1 or wall <= 0 or file_cap < MAX_CNF_BYTES:
            raise SearchLimit("insufficient shared CPU, wall or disk allowance")
        for role in ("python", "solver", "lrat_trim"):
            entry = manifest["tools"][role]
            require(digest(entry["path"]) == entry["sha256"], "tool changed")
        directory.mkdir(parents=True, exist_ok=True)
        report = process.run_process(command(allowance), directory / (name + ".log"), directory / (name + ".json"),
                                     cpu_seconds=allowance, wall_seconds=wall, memory_mib=896, file_bytes=file_cap)
        result["stages"].append({"name": name, "directory": directory.name, **report})
        write_json(output / "result.json", result)
        budget.check()
        if disk_bytes(output) > MAX_RUN_BYTES or report["external_stop"] is not None or not report["owned_child_collected"]:
            raise SearchLimit("stage collection or resource limit")
        return report

    def work(task, index, allowance):
        return [sys.executable, "-B", driver, "--worker", task, "--output", output,
                "--round", str(index), "--seconds", str(allowance)]

    def solve_command(current, allowance, with_proof=False):
        command = [solver, "--seed=0", "-q", "-t", str(allowance), current / "instance.cnf"]
        if with_proof:
            command[1:1] = ["--lrat", "--no-binary", "--no-factor"]
            command.append(current / "proof.lrat")
        return command

    try:
        controls = stage("controls", output / "controls", lambda allowance: work("controls", 0, allowance), 10)
        require(controls["returncode"] == 0, "focused controls did not pass")
        checked_controls = read_json(output / "controls" / "result.json")
        require(checked_controls == {"status": "passed", "tests": 7, "source_sha256": hashes}, "controls identity")
        result["focused_controls"] = checked_controls
        construct = stage("construct", output, lambda allowance: work("construct", 0, allowance), 10)
        require(construct["returncode"] == 0, "construction/reconstruction did not complete")
        for index in range(MAX_ROUNDS):
            current = output / f"round-{index:03d}"
            metadata = read_json(current / "instance.json")
            require(digest(current / "instance.cnf") == metadata["cnf_sha256"], "CNF changed before exploration")
            requested = 60 - (total_cpu() - budget.start) - 17
            solve = stage("solve", current, lambda allowance: solve_command(current, allowance), requested)
            result["rounds"].append({"round": index, "solver_returncode": solve["returncode"], **metadata})
            if solve["returncode"] == 10:
                refined = stage("refine", current, lambda allowance: work("refine", index, allowance), 10)
                require(refined["returncode"] == 0, "model/graph/refinement check did not complete")
                checked = read_json(current / "refine-result.json")
                if checked["status"] == "locally_checked_candidate":
                    budget.check()
                    result.update(status="candidate_pending_independent_result_review", locally_checked_candidate=True,
                                  candidate=str((current / "candidate.json").relative_to(output)), independent_audit=checked)
                    break
                require(checked["status"] == "refined" and checked["next_round"] == index + 1, "invalid refinement")
            elif solve["returncode"] == 20:
                result.update(exploration_unsat_seen=True, final_round=index, final_cnf_sha256=metadata["cnf_sha256"])
                write_json(output / "result.json", result)
                rebuilt = stage("audit", current, lambda allowance: work("audit", index, allowance), 10)
                require(rebuilt["returncode"] == 0, "independent final-CNF reconstruction failed")
                before = read_json(current / "audit-result.json")
                require(before["status"] == "independently_rebuilt_before_proof_replay"
                        and before["cnf_sha256"] == digest(current / "instance.cnf"), "final-CNF mismatch")
                requested = 60 - (total_cpu() - budget.start) - 12
                replay = stage("proof-solve", current, lambda allowance: solve_command(current, allowance, True), requested)
                require(replay["returncode"] == 20 and digest(current / "instance.cnf") == before["cnf_sha256"],
                        "exact final-CNF proof run did not complete UNSAT")
                proof_check = stage("proof", current, lambda allowance: work("proof", index, allowance),
                                    max(1, (60 - (total_cpu() - budget.start) - 5) // 2))
                require(proof_check["returncode"] == 0, "independent RUP replay did not complete")
                audited = read_json(current / "proof-result.json")
                trimmed = stage("lrat-trim", current, lambda allowance: [trim_tool, "--no-trim",
                                current / "instance.cnf", current / "proof.lrat"], 60)
                require(negative_checked(audited, trimmed["returncode"], (current / "lrat-trim.log").read_text().splitlines(),
                                         digest(current / "instance.cnf"), digest(current / "proof.lrat"),
                                         result["final_cnf_sha256"]),
                        "second proof replay or artifact identity failed")
                budget.check()
                result.update(status="exclusion_pending_independent_result_review", locally_checked_exclusion=True,
                              independent_audit=audited, lrat_trim_verified=True)
                break
            else:
                raise SearchLimit("exploration returned no completed SAT/UNSAT decision")
        else:
            raise SearchLimit("iteration bound")
    except (SearchLimit, ValueError, OSError, KeyError, TypeError) as error:
        result.update(status="unknown", reason=type(error).__name__ + ": " + str(error),
                      locally_checked_exclusion=False, locally_checked_candidate=False)
    peak_driver = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_driver *= 1 if sys.platform == "darwin" else 1024
    result.update(aggregate_cpu_seconds=total_cpu() - budget.start, wall_seconds=time.monotonic() - budget.wall_start,
                  disk_bytes=disk_bytes(output), driver_peak_rss_bytes=peak_driver,
                  maximum_sampled_child_rss_bytes=max((s["maximum_sampled_rss_bytes"] for s in result["stages"]), default=0),
                  all_owned_children_collected=all(s["owned_child_collected"] for s in result["stages"]))
    if result["aggregate_cpu_seconds"] >= 60 or result["wall_seconds"] >= 80 or result["disk_bytes"] > MAX_RUN_BYTES:
        result.update(status="unknown", reason="final shared resource bound", locally_checked_exclusion=False,
                      locally_checked_candidate=False)
    write_json(output / "result.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--worker", choices=("controls", "construct", "refine", "audit", "proof"))
    parser.add_argument("--round", type=int, default=0)
    parser.add_argument("--seconds", type=int, default=60)
    args = parser.parse_args()
    if args.worker:
        require(0 <= args.round < MAX_ROUNDS, "worker round bound")
        worker(args.output, args.worker, args.round, args.seconds)
    else:
        require(args.manifest is not None and args.review is not None, "manifest and review required")
        print(run_attempt(args.output, args.manifest, args.review))
