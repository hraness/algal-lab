"""Bounded orbital-union search. Generated evidence belongs in ignored runs/."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from actions import cayley_actions, nonregular_actions
from checker import SearchLimit, triangle, verify_candidate, verify_independent
from orbits import adjacency_from_selection, digest, edge_orbits


def input_text(action, orbits, minimum, maximum, target, node_limit, seconds):
    return "\n".join([
        f"{action['n']} {len(orbits)} {minimum} {maximum} {target} {node_limit} {seconds}",
        *(f"{orbit['degree']} " + " ".join(map(str, orbit["adjacency"])) for orbit in orbits),
    ]) + "\n"


def verify_certificates(path, orbits, n, minimum, maximum, target, expected_count, *, deadline=None):
    """Replay each rejection using direct adjacency checks, no MIS solver.

    This verifies the rejected graphs. Completeness additionally depends on
    the enumerator and on the declared group-action list being complete.
    """
    previous, count = -1, 0
    counts = [0] * n
    with open(path) as source:
        for line in source:
            if deadline is not None and time.monotonic() >= deadline:
                raise SearchLimit("overall wall limit during certificate replay")
            fields = line.split()
            if len(fields) != 2:
                raise ValueError("invalid certificate record")
            selection, independent = (int(value, 16) for value in fields)
            # DFS processes orbit 0 first; reverse the bit order to get its
            # traversal order and reject duplicates without a large set.
            if selection < 0 or selection >> len(orbits):
                raise ValueError("invalid certificate selection")
            order = int(f"{selection:0{len(orbits)}b}"[::-1], 2)
            if order <= previous:
                raise ValueError("repeated or out-of-order selection")
            previous = order
            adj = adjacency_from_selection(orbits, selection, n)
            degree = adj[0].bit_count()
            if not minimum <= degree <= maximum or triangle(adj) is not None:
                raise ValueError("certificate does not describe a searched graph")
            if not verify_independent(adj, independent, target):
                raise ValueError("invalid independent-set certificate")
            count += 1
            counts[degree] += 1
    if count != expected_count:
        raise ValueError("certificate count does not match search output")
    return counts


def search_action(binary, action, *, minimum=0, maximum=9, target=10,
                  node_limit=50_000_000, seconds=10, certificates=None, deadline=None):
    orbits = edge_orbits(action)
    data = input_text(action, orbits, minimum, maximum, target, node_limit, seconds)
    command = [str(binary)] + ([str(certificates)] if certificates is not None else [])
    wall_budget = seconds * 10 + 10
    if deadline is not None:
        wall_budget = min(wall_budget, deadline - time.monotonic())
        if wall_budget <= 0:
            raise SearchLimit("overall wall limit before action search")
    try:
        run = subprocess.run(command, input=data, capture_output=True, text=True,
                             timeout=wall_budget, check=False)
    except subprocess.TimeoutExpired as exc:
        # subprocess.run kills and reaps its own C child before raising.
        raise SearchLimit("action or overall wall limit") from exc
    if run.returncode not in (0, 3):
        raise RuntimeError(f"search rejected input: {run.stderr.strip()}")
    result = json.loads(run.stdout)
    if result["complete"] != (run.returncode == 0 and result["candidate"] is None):
        raise ValueError("inconsistent completeness status")
    result.update({"action": action["name"], "order": action["n"],
                   "action_sha256": digest(action), "orbits_sha256": digest(orbits),
                   "orbit_degrees": [orbit["degree"] for orbit in orbits]})
    if result["candidate"] is not None:
        reconstructed = adjacency_from_selection(orbits, result["candidate"]["selection"], action["n"])
        if reconstructed != result["candidate"]["adjacency"]:
            raise ValueError("candidate differs from declared orbit union")
        result["candidate"]["independent_verification"] = verify_candidate(reconstructed, target, action["n"])
        if not result["candidate"]["independent_verification"]["is_ramsey_witness"]:
            raise ValueError("candidate failed the independent checker")
    if certificates is not None:
        expected = result["candidate_count"] - (result["candidate"] is not None)
        counts = verify_certificates(certificates, orbits, action["n"], minimum, maximum, target, expected,
                                     deadline=deadline)
        expected_counts = result["degree_counts"][:]
        if result["candidate"] is not None:
            expected_counts[result["candidate"]["adjacency"][0].bit_count()] -= 1
        if counts != expected_counts:
            raise ValueError("certificate degree counts do not match")
        result["rejection_certificates_verified"] = expected
        result["certificate_sha256"] = hashlib.sha256(Path(certificates).read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--family", choices=["cayley", "nonregular"])
    source.add_argument("--manifest", type=Path,
                        help="JSON array of explicit name/n/generators actions; no coverage inference")
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new output directory")
    parser.add_argument("--seconds", type=float, default=10, help="CPU seconds per action, at most 300")
    parser.add_argument("--node-limit", type=int, default=50_000_000)
    parser.add_argument("--min-degree", type=int, default=0)
    parser.add_argument("--max-degree", type=int, default=9)
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--certificates", action="store_true", help="write and independently replay every rejection")
    parser.add_argument("--wall-seconds", type=float, default=300,
                        help="overall wall budget, including certificate replay; at most 2100")
    args = parser.parse_args()
    if (not 0 < args.seconds <= 300 or not 1 <= args.node_limit <= 1_000_000_000
            or not 0 < args.wall_seconds <= 2100):
        parser.error("invalid time or node budget")
    started = time.monotonic()
    deadline = started + args.wall_seconds
    if args.manifest:
        with open(args.manifest, "rb") as source:
            snapshot = source.read(16 * 1024 * 1024 + 1)
        if len(snapshot) > 16 * 1024 * 1024:
            parser.error("manifest exceeds 16 MiB")
        actions = json.loads(snapshot)
    else:
        actions = cayley_actions() if args.family == "cayley" else nonregular_actions()
    if not isinstance(actions, list) or not 1 <= len(actions) <= 4096:
        parser.error("expected 1..4096 explicit actions")
    if len({action["name"] for action in actions}) != len(actions):
        parser.error("action names must be unique")
    # Validate the entire batch before creating output or launching work.
    for action in actions:
        if time.monotonic() >= deadline:
            parser.error("overall wall limit during manifest validation; no search started")
        edge_orbits(action)
        if not 0 <= args.min_degree <= args.max_degree < action["n"] or not 1 <= args.target <= action["n"]:
            parser.error("degree or target bounds invalid for action")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "actions.json").write_text(json.dumps(actions, indent=2) + "\n")
    results = []
    summary = {"schema_version": 1, "family": args.family or "supplied-actions",
               "action_count": len(actions), "minimum_degree": args.min_degree,
               "actions_sha256": digest(actions), "overall_wall_seconds": args.wall_seconds,
               "maximum_degree": args.max_degree, "independent_set_target": args.target,
               "cpu_seconds_per_action": args.seconds, "node_limit_per_action": args.node_limit,
               "source_sha256": {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                   for file in sorted(Path(__file__).parent.iterdir()) if file.suffix in (".py", ".c")},
               "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
               "all_actions_exhausted": False, "results": results}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for index, action in enumerate(actions):
        cert = args.output / f"rejections-{index:03}.txt" if args.certificates else None
        try:
            result = search_action(args.binary.resolve(), action, minimum=args.min_degree,
                                   maximum=args.max_degree, target=args.target, node_limit=args.node_limit,
                                   seconds=args.seconds, certificates=cert, deadline=deadline)
        except SearchLimit as exc:
            summary["unfinished_action"] = action["name"]
            summary["stop_reason"] = str(exc)
            summary["wall_seconds"] = round(time.monotonic() - started, 6)
            (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(f"Incomplete batch: {exc}; {len(results)} actions recorded", flush=True)
            return 3
        results.append(result)
        summary["wall_seconds"] = round(time.monotonic() - started, 6)
        summary["all_actions_exhausted"] = len(results) == len(actions) and all(item["complete"] for item in results)
        (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(f"{action['name']}: {result['reason']}; {result['candidate_count']} triangle-free graphs; "
              f"{result['cpu_seconds']:.3f} CPU seconds", flush=True)
        if result["candidate"] is not None:
            print("Independently verified candidate. Inspect the exact adjacency in summary.json.")
            return 0
    print(f"All declared actions exhausted: {summary['all_actions_exhausted']}")
    return 0 if summary["all_actions_exhausted"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
