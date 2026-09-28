"""One bounded CaDiCaL attempt, with separate graph or LRAT verification."""

import argparse
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time

from encode import extension, write_instance
from lrat import read_cnf, verify
from checker import SearchLimit, independent_set, triangle


def digest(path):
    state = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(256 * 1024), b""):
            state.update(block)
    return state.hexdigest()


def parse_model(log, variables):
    model = {}
    for line in log.splitlines():
        if not line.startswith("v "):
            continue
        for literal in map(int, line[2:].split()):
            if literal == 0:
                continue
            if not 1 <= abs(literal) <= variables:
                raise ValueError("model variable outside formula")
            value = literal > 0
            if abs(literal) in model and model[abs(literal)] != value:
                raise ValueError("contradictory model values")
            model[abs(literal)] = value
    if len(model) != variables:
        raise ValueError("incomplete model")
    return {variable for variable, value in model.items() if value}


def solve(output, solver, *, seconds=60, checker_seconds=60, adj=None, target=10, neighbours=4):
    if not 1 <= seconds <= 300 or not 0 < checker_seconds <= 300:
        raise ValueError("invalid solver/checker time budget")
    solver = solver.resolve(strict=True)
    version = subprocess.run([str(solver), "--version"], check=True,
                             text=True, capture_output=True, timeout=5).stdout.strip()
    if len(version) > 1000:
        raise ValueError("unexpected solver version output")
    metadata = write_instance(output, adj=adj, target=target, neighbours=neighbours)
    cnf, proof = output / "instance.cnf", output / "proof.lrat"
    command = [str(solver), "--lrat", "--no-binary", "--no-factor", "-q", "-t", str(seconds),
               str(cnf.resolve()), str(proof.resolve())]
    report = {"schema_version": 1, "status": "not_started", "solver_version": version,
              "solver_sha256": digest(solver), "solver_argv": command,
              "cpu_limit_seconds": seconds, "wall_limit_seconds": seconds + 5,
              "output_file_limit_bytes": 256 * 1024 * 1024,
              "cnf_sha256": metadata["cnf_sha256"],
              "source_sha256": {name: digest(Path(__file__).parent / name)
                                for name in ("encode.py", "lrat.py", "solve.py")}}
    report_path = output / "result.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds + 2))
        resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024 * 1024, 256 * 1024 * 1024))

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    with (output / "solver.log").open("w") as log:
        try:
            process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                     check=False, timeout=seconds + 5, preexec_fn=limits)
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            # subprocess.run kills and reaps this exact child before raising.
            returncode = None
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    report.update({"returncode": returncode, "wall_seconds": round(time.monotonic() - started, 6),
                   "child_cpu_seconds": round(after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime, 6),
                   "status": "incomplete"})
    if proof.exists():
        report["proof_sha256"] = digest(proof)
        report["proof_bytes"] = proof.stat().st_size
    log_path = output / "solver.log"
    report["solver_log_sha256"] = digest(log_path)
    if log_path.stat().st_size > 1_000_000:
        report["verification_error"] = "unexpectedly large solver log"
    elif returncode == 20:
        report["status"] = "unsat_unverified"
        try:
            report["proof_verification"] = verify(cnf, proof, seconds=checker_seconds)
            report["status"] = "unsat_verified"
        except (ValueError, OSError) as exc:
            report["verification_error"] = str(exc)
    elif returncode == 10:
        report["status"] = "sat_unverified"
        try:
            variables, clauses = read_cnf(cnf)
            positive = parse_model(log_path.read_text(), variables)
            if not all(any(literal in positive if literal > 0 else -literal not in positive
                           for literal in clause) for clause in clauses.values()):
                raise ValueError("model fails an encoded clause")
            graph = extension(metadata["base_adjacency"], neighbours, positive)
            tri = triangle(graph)
            witness = independent_set(graph, target, node_limit=5_000_000,
                                      deadline=time.monotonic() + checker_seconds)
            if tri is not None or witness is not None:
                raise ValueError("model fails direct Ramsey-graph verification")
            (output / "candidate.json").write_text(json.dumps(graph) + "\n")
            report.update({"status": "sat_verified", "candidate_sha256": digest(output / "candidate.json")})
        except (ValueError, SearchLimit, OSError) as exc:
            report["verification_error"] = str(exc)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output directory")
    parser.add_argument("--solver", type=Path, default=shutil.which("cadical"))
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--checker-seconds", type=float, default=60)
    args = parser.parse_args()
    if args.solver is None:
        parser.error("CaDiCaL is not installed; provide an approved --solver path")
    result = solve(args.output, args.solver, seconds=args.seconds, checker_seconds=args.checker_seconds)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] in ("sat_verified", "unsat_verified") else 3)
