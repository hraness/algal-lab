import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import platform

from research.softmax_additive_flow import maximize_additive_softmax, verify_additive_softmax_certificate


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def draw(case, field, modulus):
    value = hashlib.sha256(f"algal-allocation-v1:{case}:{field}".encode()).digest()
    return int.from_bytes(value[:8], "big") % modulus


def generate():
    cases = []
    for case in range(24):
        n, m = 2 + case % 4, 2 + case % 2
        cases.append({
            "id": f"allocation-{case:02d}", "split": "development" if case < 16 else "regression",
            "n": n, "capacities": [draw(case, f"capacity-{j}", n + 1) for j in range(m)],
            "exponentials": [str(Fraction(3 + draw(case, f"exp-{j}", 5), 2)) for j in range(m)],
            "weights": [str(Fraction(1 + draw(case, f"weight-{j}", 5), 1 + j)) for j in range(m)],
            "edges": [[i, j, str(Fraction(draw(case, f"reward-{i}-{j}", 9) - 4, 2))]
                      for i in range(n) for j in range(m) if draw(case, f"eligible-{i}-{j}", 5) != 0],
        })
    cases[0]["edges"] = []
    cases[1]["capacities"] = [0] * len(cases[1]["capacities"])
    return {"contract": "algal.dataset.allocation.v1", "generator": "sha256-counter-v1",
            "license": "MIT", "cases": cases,
            "limits": "Synthetic model controls, not a workload trace, fresh holdout, new solver, or production scheduling evidence."}


def problem(row):
    return {"n": row["n"], "capacities": tuple(row["capacities"]),
            "exponentials": tuple(Fraction(x) for x in row["exponentials"]),
            "weights": tuple(Fraction(x) for x in row["weights"]),
            "edges": tuple((i, j, Fraction(reward)) for i, j, reward in row["edges"])}


def objective(p, assignment):
    value = Fraction(0)
    for j, weight in enumerate(p["weights"]):
        efforts = tuple(int(task == j) for task in assignment)
        factors = tuple(p["exponentials"][j] ** x for x in efforts)
        value += weight * sum((x * factor for x, factor in zip(efforts, factors)), Fraction(0)) / sum(factors)
    rewards = {(i, j): reward for i, j, reward in p["edges"]}
    return value + sum((rewards[i, j] for i, j in enumerate(assignment) if j is not None), Fraction(0))


def exhaustive(p):
    allowed = {(i, j) for i, j, _ in p["edges"]}
    choices = [(None,) + tuple(j for j in range(len(p["capacities"])) if (i, j) in allowed) for i in range(p["n"])]
    best, assignment, evaluated = None, None, 0
    for candidate in product(*choices):
        if any(candidate.count(j) > cap for j, cap in enumerate(p["capacities"])):
            continue
        value = objective(p, candidate)
        evaluated += 1
        if best is None or value > best:
            best, assignment = value, candidate
    return best, assignment, evaluated


def greedy(p):
    assignment = [None] * p["n"]
    allowed = {(i, j) for i, j, _ in p["edges"]}
    for i in range(p["n"]):
        best, task = objective(p, assignment), None
        for j, cap in enumerate(p["capacities"]):
            if (i, j) not in allowed or assignment.count(j) >= cap:
                continue
            candidate = list(assignment)
            candidate[i] = j
            value = objective(p, candidate)
            if value > best:
                best, task = value, j
        assignment[i] = task
    return tuple(assignment)


def benchmark(dataset):
    if encoded(dataset) != encoded(generate()):
        raise ValueError("dataset differs from the frozen bounded generator")
    results = []
    for row in dataset["cases"]:
        p = problem(row)
        solved = maximize_additive_softmax(**p)
        oracle, witness, count = exhaustive(p)
        mutated = deepcopy(solved)
        mutated["objective"] += 1
        valid = verify_additive_softmax_certificate(**p, report=solved)
        rejected = not verify_additive_softmax_certificate(**p, report=mutated)
        equal = solved["objective"] == oracle == objective(p, solved["assignment"])
        if not valid or not rejected or not equal:
            raise ValueError(f"exact control failed for {row['id']}")
        greedy_value = objective(p, greedy(p))
        results.append({"id": row["id"], "split": row["split"], "objective": str(oracle),
                        "assignment": list(solved["assignment"]), "oracleAssignment": list(witness),
                        "enumeratedAssignments": count, "certificateValid": valid,
                        "oracleEqual": equal, "mutatedCertificateRejected": rejected,
                        "greedyObjective": str(greedy_value), "greedyRegret": str(oracle - greedy_value)})
    return {"contract": "algal.baseline.allocation.v1", "scope": "synthetic-development-controls",
            "datasetDigest": digest(dataset), "modelCalls": 0, "results": results,
            "limits": "Exact finite checks within the existing additive-softmax model. No runtime ranking, new theorem, practical workload validation, or continuous-scope proof is established by this benchmark."}


def source_identity():
    root = Path(__file__).resolve().parent
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in ("foundation_allocation.py", "softmax_additive_flow.py")}


def run(out):
    out.mkdir(mode=0o700)
    dataset = generate()
    with (out / "dataset.json").open("xb") as file:
        file.write(encoded(dataset))
    identity = {"sources": source_identity(), "python": platform.python_version()}
    with (out / "environment.json").open("xb") as file:
        file.write(encoded(identity))
    report = benchmark(dataset)
    with (out / "report.json").open("xb") as file:
        file.write(encoded(report))
    return {"datasetDigest": digest(dataset), "reportDigest": digest(report), "cases": len(report["results"]), "modelCalls": 0}


def read_bounded(path):
    with path.open("rb") as file:
        data = file.read(1_000_001)
    if len(data) > 1_000_000:
        raise ValueError("benchmark file exceeds bound")
    return json.loads(data)


def verify(out):
    identity = read_bounded(out / "environment.json")
    if type(identity) is not dict or set(identity) != {"sources", "python"} or type(identity["python"]) is not str:
        raise ValueError("invalid benchmark environment fields")
    if identity["sources"] != source_identity():
        raise ValueError("benchmark source identity changed")
    dataset = read_bounded(out / "dataset.json")
    report = benchmark(dataset)
    if read_bounded(out / "report.json") != report:
        raise ValueError("benchmark reproduction mismatch")
    return {"verified": True, "reportDigest": digest(report), "recordedPython": identity.get("python"),
            "verificationPython": platform.python_version()}


def main():
    parser = argparse.ArgumentParser(description="Generate exact allocation development controls without dependencies or model calls.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.verify) if args.verify else run(args.out)))


if __name__ == "__main__":
    main()
