"""Proposal operators: a credential-free scripted mutator and a stateless command wrapper."""

from __future__ import annotations

import ast
import json
import random
import re
import subprocess
from dataclasses import dataclass

from .sandbox import MAX_PROGRAM_BYTES

PARAMS_PATTERN = re.compile(r"^PARAMS[ \t]*=[ \t]*(\{.*\})[ \t]*$", re.MULTILINE)
CODE_BLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
MAX_COMMAND_OUTPUT = 256 * 1024
REQUEST_CONTRACT = "algal.lab.extremal-request.v1"


@dataclass(frozen=True)
class Parent:
    program: str
    score: str | None
    error: str


def read_params(program: str) -> dict | None:
    match = PARAMS_PATTERN.search(program)
    if not match:
        return None
    try:
        value = ast.literal_eval(match.group(1))
    except (ValueError, SyntaxError):
        return None
    return value if isinstance(value, dict) else None


def write_params(program: str, params: dict) -> str:
    return PARAMS_PATTERN.sub("PARAMS = " + json.dumps(params), program, count=1)


def scripted_mutate(program: str, rng: random.Random) -> str:
    """Perturb numeric entries of the program's PARAMS literal; code is never edited."""
    params = read_params(program)
    if not params:
        return program
    keys = [k for k, v in params.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not keys:
        return program
    for key in rng.sample(keys, k=max(1, min(len(keys), rng.choice((1, 1, 2))))):
        value = params[key]
        if isinstance(value, int):
            params[key] = value + rng.choice((-2, -1, 1, 2))
        else:
            params[key] = round(value * (1 + rng.gauss(0, 0.25)) + rng.gauss(0, 0.05), 6)
    return write_params(program, params)


def build_request(target, parents: list[Parent], seed: int, description: str) -> dict:
    return {
        "contract": REQUEST_CONTRACT,
        "target": {
            "id": target.id,
            "title": target.title,
            "objective": target.objective,
            "parameters": target.parameters,
            "verifier_description": description,
            "recorded_best": str(target.best_known),
        },
        "parents": [{"program": p.program, "score": p.score, "error": p.error} for p in parents],
        "limits": {"max_program_bytes": MAX_PROGRAM_BYTES, "interface": "define construct(parameters, seed) -> dict; standard library only"},
        "seed": seed,
    }


def extract_program(text: str) -> str | None:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and isinstance(obj.get("program"), str):
            return obj["program"]
    except json.JSONDecodeError:
        pass
    blocks = CODE_BLOCK.findall(text)
    if blocks:
        return blocks[-1]
    return text if "def construct" in text else None


def command_propose(command: list[str], request: dict, timeout: float = 600.0) -> tuple[str | None, str]:
    """Run a stateless wrapper: request JSON on stdin, program on stdout."""
    try:
        proc = subprocess.run(command, input=json.dumps(request).encode(), capture_output=True, timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return None, f"command failed: {exc}"
    if proc.returncode != 0:
        return None, f"command exit {proc.returncode}: {proc.stderr[-600:].decode(errors='replace')}"
    out = proc.stdout[:MAX_COMMAND_OUTPUT].decode(errors="replace")
    program = extract_program(out)
    if program is None:
        return None, "command output contained no program"
    if len(program.encode()) > MAX_PROGRAM_BYTES:
        return None, "proposed program too large"
    return program, ""
