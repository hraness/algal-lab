"""Bounded evolutionary search over construction programs with a full archive.

Usage:
    python3 -m research.extremal.evolve --protocol PROTOCOL.json --out DIR

The output directory must not exist.  Every proposed program, its evaluations,
its parents, and the operator that produced it are retained.  Selection uses
the best exactly verified value over the protocol's construction seeds; the
best construction is stored with its verifier value and the novelty assessment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

from . import novelty, registry
from .operators import Parent, build_request, command_propose, scripted_mutate
from .sandbox import run_program
from .verifiers import load_verifier

PROTOCOL_CONTRACT = "algal.lab.extremal-protocol.v1"
MAX_EVALUATIONS = 4096
MAX_POPULATION = 64
MAX_CONSTRUCTION_SEEDS = 8
MAX_PARENTS_SHOWN = 4


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _int_field(obj, key, low, high):
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"protocol {key!r} must be an integer in [{low}, {high}]")
    return value


def parse_protocol(raw: dict, base: Path) -> dict:
    if not isinstance(raw, dict) or raw.get("contract") != PROTOCOL_CONTRACT:
        raise ValueError(f"protocol contract must be {PROTOCOL_CONTRACT}")
    allowed = {"contract", "target", "seed", "evaluations", "population", "elites", "operator", "command",
               "constructionSeeds", "programTimeout", "commandTimeout", "seedProgram", "note"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown protocol fields: {sorted(unknown)}")
    proto = {
        "target": raw.get("target"),
        "seed": _int_field(raw, "seed", 0, 2**31 - 1),
        "evaluations": _int_field(raw, "evaluations", 1, MAX_EVALUATIONS),
        "population": _int_field(raw, "population", 1, MAX_POPULATION),
        "elites": _int_field(raw, "elites", 1, MAX_POPULATION),
        "operator": raw.get("operator"),
        "command": raw.get("command", []),
        "constructionSeeds": raw.get("constructionSeeds", [0]),
        "programTimeout": float(raw.get("programTimeout", 30)),
        "commandTimeout": float(raw.get("commandTimeout", 600)),
        "note": str(raw.get("note", "")),
    }
    if not isinstance(proto["target"], str):
        raise ValueError("protocol target must be a string id")
    if proto["operator"] not in ("scripted", "command"):
        raise ValueError("operator must be 'scripted' or 'command'")
    if proto["operator"] == "command" and (not isinstance(proto["command"], list) or not proto["command"]
                                            or not all(isinstance(c, str) for c in proto["command"])):
        raise ValueError("command operator needs a non-empty list of strings")
    seeds = proto["constructionSeeds"]
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= MAX_CONSTRUCTION_SEEDS or \
            any(isinstance(s, bool) or not isinstance(s, int) for s in seeds):
        raise ValueError("constructionSeeds must be 1..8 integers")
    if proto["elites"] > proto["population"]:
        raise ValueError("elites cannot exceed population")
    seed_program = raw.get("seedProgram")
    if not isinstance(seed_program, str):
        raise ValueError("seedProgram must be a path to the initial program")
    proto["seedProgram"] = str((base / seed_program).resolve())
    return proto


class Archive:
    def __init__(self, out: Path):
        self.out = out
        self.programs = out / "programs"
        self.programs.mkdir(parents=True)
        self.candidates = open(out / "candidates.jsonl", "a", encoding="utf-8")
        self.count = 0

    def record(self, entry: dict, program: str) -> None:
        path = self.programs / f"{entry['program_sha256']}.py"
        if not path.exists():
            path.write_text(program, encoding="utf-8")
        self.candidates.write(json.dumps(entry, separators=(",", ":")) + "\n")
        self.candidates.flush()
        self.count += 1

    def close(self):
        self.candidates.close()


def evaluate(program: str, target: registry.Target, verifier, seeds: list[int], timeout: float) -> tuple[list[dict], Fraction | None, object]:
    evaluations = []
    best_value = None
    best_construction = None
    sign = 1 if target.objective == "maximize" else -1
    for seed in seeds:
        run = run_program(program, target.parameters, seed, timeout=timeout)
        record = {"seed": seed, "ok": run.ok, "seconds": round(run.seconds, 3), "error": run.error, "value": None}
        if run.ok:
            try:
                value = verifier.verify(run.construction, target.parameters)
                record["value"] = str(value)
                if best_value is None or value * sign > best_value * sign:
                    best_value, best_construction = value, run.construction
            except (ValueError, TypeError, KeyError, OverflowError) as exc:
                record["ok"] = False
                record["error"] = f"verifier rejected: {exc}"[:600]
        evaluations.append(record)
    return evaluations, best_value, best_construction


def run(protocol_path: Path, out: Path) -> dict:
    if out.exists():
        raise SystemExit(f"output directory {out} already exists; choose a new one")
    raw = json.loads(protocol_path.read_text())
    proto = parse_protocol(raw, protocol_path.parent)
    targets = registry.load_registry()
    if proto["target"] not in targets:
        raise SystemExit(f"unknown target {proto['target']!r}")
    target = targets[proto["target"]]
    verifier = load_verifier(target.verifier)
    seed_program = Path(proto["seedProgram"]).read_text(encoding="utf-8")
    rng = random.Random(proto["seed"])
    archive = Archive(out)
    sign = 1 if target.objective == "maximize" else -1
    population: list[dict] = []  # entries with program and selection value
    best = None  # (value, construction, entry index)
    last_failure = None  # (index, program, error) of the latest failed command proposal, offered for repair
    started = time.time()

    def submit(program: str, parents: list[int], operator: str, note: str = "") -> dict:
        nonlocal best, last_failure
        evaluations, value, construction = evaluate(program, target, verifier, proto["constructionSeeds"], proto["programTimeout"])
        entry = {
            "index": archive.count,
            "program_sha256": sha256(program),
            "parents": parents,
            "operator": operator,
            "note": note,
            "evaluations": evaluations,
            "selection_value": None if value is None else str(value),
        }
        archive.record(entry, program)
        if value is not None:
            population.append({"program": program, "value": value, "index": entry["index"], "sha": entry["program_sha256"]})
            if best is None or value * sign > best[0] * sign:
                best = (value, construction, entry["index"])
        else:
            errors = [e["error"] for e in evaluations if e["error"]]
            if operator == "command":
                last_failure = (entry["index"], program, errors[0] if errors else "no evaluable construction")
        return entry

    submit(seed_program, [], "seed")
    while archive.count < proto["evaluations"]:
        if not population:
            raise SystemExit("no evaluable program in the population; fix the seed program")
        population.sort(key=lambda e: (e["value"] * sign, -e["index"]), reverse=True)
        del population[proto["population"]:]
        elites = population[: proto["elites"]]
        if proto["operator"] == "scripted":
            parent = rng.choice(elites)
            child = scripted_mutate(parent["program"], rng)
            submit(child, [parent["index"]], "scripted")
        else:
            shown = elites[:MAX_PARENTS_SHOWN - 1] if last_failure else elites[:MAX_PARENTS_SHOWN]
            parents = [Parent(p["program"], str(p["value"]), "") for p in shown]
            parent_indices = [p["index"] for p in shown]
            note = ""
            if last_failure is not None:
                # Repair turn: show the failed proposal with its error alongside the elites.
                parents.append(Parent(last_failure[1], None, last_failure[2]))
                parent_indices.append(last_failure[0])
                note = "repair"
                last_failure = None
            request = build_request(target, parents, rng.randrange(2**31), verifier.DESCRIPTION)
            program, error = command_propose(proto["command"], request, timeout=proto["commandTimeout"])
            if program is None:
                entry = {"index": archive.count, "program_sha256": sha256(""), "parents": parent_indices,
                         "operator": "command", "note": error, "evaluations": [], "selection_value": None}
                archive.record(entry, "")
                continue
            submit(program, parent_indices, "command", note)
    archive.close()
    result = {
        "contract": "algal.lab.extremal-run.v1",
        "protocol": raw,
        "protocol_sha256": sha256(protocol_path.read_text()),
        "target": target.id,
        "registry_entry": {"best_known": str(target.best_known), "kind": target.best_known_kind, "source": target.source,
                           "url": target.url, "retrieved": target.retrieved},
        "sources": {name: sha256(Path(__file__).with_name(name).read_text()) for name in ("evolve.py", "sandbox.py", "operators.py", "novelty.py", "registry.py")},
        "verifier_sha256": sha256(Path(verifier.__file__).read_text()),
        "python": sys.version.split()[0],
        "candidates": archive.count,
        "evaluable": sum(1 for _ in open(out / "candidates.jsonl") ),
        "seconds": round(time.time() - started, 1),
        "best": None,
    }
    if best is not None:
        value, construction, index = best
        (out / "best-construction.json").write_text(json.dumps(construction, separators=(",", ":")))
        result["best"] = {"value": str(value), "candidate_index": index,
                          "construction_sha256": sha256((out / "best-construction.json").read_text()),
                          "novelty": novelty.assess(target, value)}
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    result = run(args.protocol, args.out)
    best = result["best"]
    if best is None:
        print("no evaluable candidate")
    else:
        print(f"best {best['value']} (candidate {best['candidate_index']}): {best['novelty']['status']} vs recorded {result['registry_entry']['best_known']}")


if __name__ == "__main__":
    main()
