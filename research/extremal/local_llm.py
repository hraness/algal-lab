"""Stateless local-model proposal wrapper for the command operator.

Reads one request (contract algal.lab.extremal-request.v1) on stdin, asks a
local mlx_lm model for an improved program, and prints the reply on stdout.
Each call loads nothing from previous calls; the seed in the request selects
the sampling seed, so a run is reproducible on the same machine and weights.

Run it through the interpreter that has mlx_lm installed, for example:
    /Users/bg/.local/share/uv/tools/mlx-lm/bin/python -m research.extremal.local_llm
Environment: EXTREMAL_MODEL (default mlx-community/Qwen3-8B-4bit),
EXTREMAL_MAX_TOKENS (default 2048), EXTREMAL_TEMPERATURE (default 0.7).
"""

from __future__ import annotations

import json
import os
import sys

DEFAULT_MODEL = "mlx-community/Qwen3-8B-4bit"
SYSTEM = (
    "You are improving a Python program for an extremal combinatorics search. "
    "Reply with exactly one ```python code block and nothing else. The program must define "
    "construct(parameters, seed) -> dict, use only the standard library, finish within a few "
    "seconds, and return a construction the verifier accepts. Keep a PARAMS = {...} literal on one "
    "line near the top so numeric knobs can be tuned later."
)


def build_prompt(request: dict) -> str:
    target = request["target"]
    lines = [
        f"Target: {target['title']} (objective: {target['objective']} the verified value).",
        f"Parameters: {json.dumps(target['parameters'])}",
        f"Recorded best-known value to beat: {target['recorded_best']}",
        "",
        "Verifier:",
        target["verifier_description"].strip(),
        "",
    ]
    repair = None
    for i, parent in enumerate(request["parents"]):
        if parent.get("score") is None:
            repair = parent
            continue
        lines.append(f"Parent program {i} (verified score {parent['score']}):")
        lines.append("```python")
        lines.append(parent["program"].rstrip())
        lines.append("```")
        lines.append("")
    if repair is not None:
        lines.append("A previous proposal failed. Its program:")
        lines.append("```python")
        lines.append(repair["program"].rstrip())
        lines.append("```")
        lines.append(f"Its error: {repair['error']}")
        lines.append("Fix that failure (or return to a working parent's structure) so the new program is accepted.")
        lines.append("")
    else:
        lines.append("Improve on the best parent: change the search strategy or construction idea, not only constants.")
    lines.append(
        f"Write the complete program (at most {request['limits']['max_program_bytes']} bytes). "
        f"Interface: {request['limits']['interface']}. Keep every construct() call under a few seconds. /no_think"
    )
    return "\n".join(lines)


def main() -> int:
    request = json.load(sys.stdin)
    if request.get("contract") != "algal.lab.extremal-request.v1":
        print("unexpected request contract", file=sys.stderr)
        return 2
    prompt = build_prompt(request)
    if os.environ.get("EXTREMAL_DRY_RUN"):
        print(prompt)
        return 0
    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    model, tokenizer = load(os.environ.get("EXTREMAL_MODEL", DEFAULT_MODEL))
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    mx.random.seed(int(request.get("seed", 0)))
    sampler = make_sampler(temp=float(os.environ.get("EXTREMAL_TEMPERATURE", "0.7")))
    reply = generate(model, tokenizer, prompt=text, max_tokens=int(os.environ.get("EXTREMAL_MAX_TOKENS", "2048")),
                     sampler=sampler, verbose=False)
    print(reply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
