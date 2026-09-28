"""Run and preserve a small, resource-limited degree-six SAT pilot."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from encoding import PROFILES, independent_clause, structural_formula
from native import digest
from search import peak_bytes, search


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def worker(args):
    # Leave time for shutdown and the supervisor's final formula reconstruction.
    reserve = min(10, args.seconds / 5)
    cpu_stop = args.seconds - reserve
    hard_cpu = max(1, math.ceil(args.seconds - reserve / 2))
    resource.setrlimit(resource.RLIMIT_CPU, (hard_cpu, hard_cpu))
    resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024**2, 256 * 1024**2))
    start = time.monotonic()
    reason = None

    def stop():
        nonlocal reason
        if time.process_time() >= cpu_stop:
            reason = "cpu_limit"
        elif time.monotonic() - start >= args.seconds + 30:
            reason = "wall_limit"
        elif peak_bytes() >= args.memory_mib * 1024**2:
            reason = "memory_threshold"
        return reason is not None

    formula, variable, metadata = structural_formula(profile=args.profile)
    source = Path(__file__).resolve().parent
    metadata.update({
        "solver_library_sha256": digest(args.library),
        "source_sha256": {path.name: digest(path) for path in sorted(source.glob("*.py"))},
        "graph_checker_sha256": digest(source.parent / "vertex_transitive/checker.py"),
        "cpu_seconds_budget": args.seconds, "cooperative_cpu_stop": cpu_stop,
        "worker_hard_cpu_limit": hard_cpu, "supervisor_wall_seconds": args.seconds + 60,
        "memory_threshold_mib": args.memory_mib, "memory_limit_is_cooperative": True,
        "maximum_cuts": args.cuts, "maximum_models": args.models,
        "batch_size": args.batch, "seed": args.seed,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    write_json(args.output / "instance.json", metadata)
    with (args.output / "cuts.jsonl").open("x") as cuts_file, (args.output / "progress.jsonl").open("x") as progress:
        def event(kind, value):
            if kind == "cuts":
                cuts_file.write(json.dumps(value, separators=(",", ":")) + "\n")
                cuts_file.flush()
            elif kind in ("model", "candidate"):
                write_json(args.output / ("candidate.json" if kind == "candidate" else "last-model.json"), value["adjacency"])
                value = {key: item for key, item in value.items() if key != "adjacency"}
            progress.write(json.dumps({"event": kind, "cpu_seconds": time.process_time(),
                                       "wall_seconds": time.monotonic() - start,
                                       "peak_bytes": peak_bytes(), **value}, separators=(",", ":")) + "\n")
            progress.flush()

        result = search(formula, variable, metadata, args.library, stop=stop,
                        cut_limit=args.cuts, model_limit=args.models,
                        batch_size=args.batch, seed=args.seed, event=event)
    result["cuts"] = len(result["cuts"])
    result.pop("last_graph")
    result.update({"stop_reason": reason, "cpu_seconds": time.process_time(),
                   "wall_seconds": time.monotonic() - start, "peak_bytes": peak_bytes()})
    write_json(args.output / "worker-result.json", result)


def recorded_cuts(path, maximum):
    cuts, seen = [], set()
    if not path.exists():
        return cuts, False
    raw = path.read_bytes()
    if len(raw) > 32 * 1024**2:
        raise ValueError("oversized cut log")
    partial = bool(raw and not raw.endswith(b"\n"))
    lines = raw.splitlines()
    if partial:
        lines.pop()
    for line in lines:
        entry = json.loads(line)
        if type(entry) is not dict or set(entry) != {"model", "graph_sha256", "masks"}:
            raise ValueError("invalid cut record")
        if type(entry["masks"]) is not list or not 1 <= len(entry["masks"]) <= 256:
            raise ValueError("invalid cut batch")
        for mask in entry["masks"]:
            if type(mask) is not int or not 0 < mask < 1 << 40 or mask.bit_count() != 10 or mask in seen:
                raise ValueError("invalid or duplicate recorded cut")
            seen.add(mask)
            cuts.append(mask)
            if len(cuts) > maximum:
                raise ValueError("cut limit exceeded")
    return cuts, partial


def terminate_owned_worker(process):
    """Collect only this supervisor's child, including interrupted waits."""
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def supervise(args):
    if args.output.exists():
        raise ValueError("output directory must be new")
    args.output.mkdir(parents=True)
    start = time.monotonic()
    own_cpu = time.process_time()
    initial_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    command = [sys.executable, str(Path(__file__).resolve()), "--worker",
               "--library", str(args.library), "--output", str(args.output),
               "--seconds", str(args.seconds), "--cuts", str(args.cuts),
               "--models", str(args.models), "--batch", str(args.batch),
               "--memory-mib", str(args.memory_mib), "--seed", str(args.seed),
               "--profile", args.profile]
    external_stop = None
    supervisor_signal = None
    watched_signals = (signal.SIGINT, signal.SIGTERM)
    previous_handlers = {sig: signal.getsignal(sig) for sig in watched_signals}

    def interrupted(signum, _frame):
        nonlocal supervisor_signal
        supervisor_signal = signum
        raise KeyboardInterrupt

    try:
        for sig in watched_signals:
            signal.signal(sig, interrupted)
        with (args.output / "worker.log").open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                process.wait(timeout=args.seconds + 60)
            except subprocess.TimeoutExpired:
                external_stop = "supervisor_wall_limit"
            except KeyboardInterrupt:
                external_stop = "supervisor_interrupted"
                supervisor_signal = supervisor_signal or int(signal.SIGINT)
            finally:
                # Repeated interrupts must not abandon the child while it is
                # being terminated and collected. The cleanup is bounded.
                for sig in watched_signals:
                    signal.signal(sig, signal.SIG_IGN)
                terminate_owned_worker(process)
    finally:
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
    receipt = args.output / "worker-result.json"
    if receipt.exists() and process.returncode == 0 and external_stop is None:
        result = json.loads(receipt.read_text())
    else:
        result = {"status": "interrupted_or_error", "unsat_verified": False,
                  "graph_checked_without_independent_target_set": False}
    cuts, incomplete_log_line = recorded_cuts(args.output / "cuts.jsonl", args.cuts)
    formula, variable, metadata = structural_formula(profile=args.profile)
    cnf = args.output / "final.cnf"
    with cnf.open("x") as output:
        output.write(f"p cnf {formula.variables} {len(formula.clauses) + len(cuts)}\n")
        for clause in formula.clauses:
            output.write(" ".join(map(str, clause)) + " 0\n")
        for mask in cuts:
            output.write(" ".join(map(str, independent_clause(mask, variable, 10))) + " 0\n")
    final_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    children_cpu = (final_children.ru_utime + final_children.ru_stime
                    - initial_children.ru_utime - initial_children.ru_stime)
    result.update({"recorded_cuts": len(cuts), "base_clauses": len(formula.clauses),
                   "final_clauses": len(formula.clauses) + len(cuts),
                   "cnf_sha256": digest(cnf), "cuts_sha256": digest(args.output / "cuts.jsonl")
                   if (args.output / "cuts.jsonl").exists() else None,
                   "incomplete_cut_log_line_discarded": incomplete_log_line,
                   "final_formula_includes_every_complete_recorded_cut": True,
                   "submission_of_final_batch_uncertain": process.returncode != 0,
                   "worker_returncode": process.returncode, "external_stop": external_stop,
                   "worker_pid": process.pid, "supervisor_signal": supervisor_signal,
                   "total_cpu_seconds": children_cpu + time.process_time() - own_cpu,
                   "total_wall_seconds": time.monotonic() - start,
                   "ramsey_bound_changed": False})
    write_json(args.output / "result.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seconds", type=float, default=600)
    parser.add_argument("--cuts", type=int, default=100_000)
    parser.add_argument("--models", type=int, default=20_000)
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--profile", choices=PROFILES, default="baseline")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not (1 <= args.seconds <= 600 and 1 <= args.cuts <= 100_000
            and 1 <= args.models <= 20_000 and 1 <= args.batch <= 256
            and 64 <= args.memory_mib <= 1024 and 0 <= args.seed <= 2**31 - 1):
        parser.error("resource setting outside supported bounds")
    args.library = args.library.resolve(strict=True)
    args.output = args.output.resolve()
    if args.worker:
        worker(args)
    else:
        result = supervise(args)
        print(json.dumps(result, indent=2))
        if result["supervisor_signal"] is not None:
            raise SystemExit(128 + result["supervisor_signal"])
