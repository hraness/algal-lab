"""Construction claims: exactly verified constructions that beat a registry snapshot.

A claims file records, per construction, the target it improves, the value
recorded in the registry when the claim was made, the claim date, how the
construction was derived, an unseeded control run, and the construction
itself. ``check`` re-runs the verifier and the novelty gate and labels the
claim from its control; nothing in the file is trusted.

The control is the same search started from nothing (no public certificate,
no warm start) at a stated budget, which should be the seeded run's budget.
Its ``outcome`` compares the control's value with the claimed value in the
objective's direction: ``matched``, ``below`` (the control did not reach the
claimed value), ``above`` (it beat the claimed value), or ``not-run`` (no
control exists; ``value`` and ``command`` are then null and ``budget`` states
the budget a control must match). ``check`` adds a ``search_status``:
``under-searched`` when the control reached at least the recorded best, so
the public cell was beatable from nothing at that budget; ``control-missing``
when no control was run on a target that requires one; ``control-not-required``
when the target waives it; otherwise the novelty status
(``improves-recorded-best`` for a valid claim).

    python3 -m research.extremal.claims            # re-verify every claims file
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from . import novelty, registry
from .verifiers import load_verifier

CLAIMS_DIR = Path(__file__).with_name("claims")
CONTRACT = "algal.lab.extremal-claims.v1"
MAX_CLAIMS_BYTES = 1024 * 1024
MAX_DERIVATION_STEPS = 16
MAX_CONTROL_TEXT = 2000
FIELDS = {"target", "verifier", "parameters", "value", "recorded_best", "claimed", "derivation", "control", "construction"}
CONTROL_FIELDS = {"kind", "value", "budget", "command", "outcome"}
CONTROL_KIND = "unseeded"
CONTROL_OUTCOMES = ("matched", "below", "above", "not-run")


@dataclass(frozen=True)
class Control:
    kind: str
    value: Fraction | None
    budget: str
    command: str | None
    outcome: str


@dataclass(frozen=True)
class Claim:
    target: str
    verifier: str
    parameters: dict
    value: Fraction
    recorded_best: Fraction
    claimed: str
    derivation: tuple
    control: Control
    construction: dict


def _text(value, what: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_CONTROL_TEXT:
        raise ValueError(f"control {what} must be a non-empty string of at most {MAX_CONTROL_TEXT} characters")
    return value


def parse_control(raw) -> Control:
    if not isinstance(raw, dict):
        raise ValueError("control must be an object")
    unknown = set(raw) - CONTROL_FIELDS
    missing = CONTROL_FIELDS - set(raw)
    if unknown or missing:
        raise ValueError(f"control fields: unknown {sorted(unknown)}, missing {sorted(missing)}")
    if raw["kind"] != CONTROL_KIND:
        raise ValueError(f"control kind must be {CONTROL_KIND!r}")
    outcome = raw["outcome"]
    if not isinstance(outcome, str) or outcome not in CONTROL_OUTCOMES:
        raise ValueError(f"control outcome must be one of {CONTROL_OUTCOMES}")
    budget = _text(raw["budget"], "budget")
    if outcome == "not-run":
        if raw["value"] is not None or raw["command"] is not None:
            raise ValueError("a not-run control must have null value and command")
        return Control(kind=CONTROL_KIND, value=None, budget=budget, command=None, outcome=outcome)
    return Control(kind=CONTROL_KIND, value=registry.parse_value(raw["value"]), budget=budget,
                   command=_text(raw["command"], "command"), outcome=outcome)


def parse_claim(raw) -> Claim:
    if not isinstance(raw, dict):
        raise ValueError("claim must be an object")
    unknown = set(raw) - FIELDS
    missing = FIELDS - set(raw)
    if unknown or missing:
        raise ValueError(f"claim fields: unknown {sorted(unknown)}, missing {sorted(missing)}")
    for key in ("target", "verifier", "claimed"):
        if not isinstance(raw[key], str):
            raise ValueError(f"claim {key!r} must be a string")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw["claimed"]):
        raise ValueError("claim date must be YYYY-MM-DD")
    if not isinstance(raw["parameters"], dict) or not isinstance(raw["construction"], dict):
        raise ValueError("claim parameters and construction must be objects")
    steps = raw["derivation"]
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_DERIVATION_STEPS or not all(isinstance(s, str) for s in steps):
        raise ValueError(f"derivation must list 1..{MAX_DERIVATION_STEPS} strings")
    return Claim(target=raw["target"], verifier=raw["verifier"], parameters=raw["parameters"],
                 value=registry.parse_value(raw["value"]), recorded_best=registry.parse_value(raw["recorded_best"]),
                 claimed=raw["claimed"], derivation=tuple(steps), control=parse_control(raw["control"]),
                 construction=raw["construction"])


def load_claims(path: Path) -> list[Claim]:
    data = path.read_bytes()
    if len(data) > MAX_CLAIMS_BYTES:
        raise ValueError("claims file too large")
    raw = json.loads(data)
    if not isinstance(raw, dict) or set(raw) != {"contract", "note", "claims"} or raw["contract"] != CONTRACT:
        raise ValueError(f"claims file must be {{contract: {CONTRACT!r}, note, claims}}")
    if not isinstance(raw["claims"], list):
        raise ValueError("claims must be a list")
    return [parse_claim(entry) for entry in raw["claims"]]


def search_status(target: registry.Target, claim: Claim, novelty_status: str) -> str:
    """Label the claim from its unseeded control; raise ValueError when the outcome contradicts the values."""
    control = claim.control
    if control.outcome == "not-run":
        return "control-missing" if target.control_required else "control-not-required"
    sign = 1 if target.objective == "maximize" else -1
    diff = (control.value - claim.value) * sign
    expected = "matched" if diff == 0 else ("above" if diff > 0 else "below")
    if control.outcome != expected:
        raise ValueError(f"{claim.target}: control value {control.value} against the claimed {claim.value} is {expected!r}, "
                         f"but the control outcome says {control.outcome!r}")
    return "under-searched" if target.margin(control.value) >= 0 else novelty_status


def check(claim: Claim, targets: dict) -> dict:
    """Re-verify one claim; raise ValueError on any inconsistency, else return the novelty assessment with its search status."""
    target = targets.get(claim.target)
    if target is None:
        raise ValueError(f"unknown target {claim.target!r}")
    if target.verifier != claim.verifier or target.parameters != claim.parameters:
        raise ValueError(f"{claim.target}: verifier or parameters differ from the registry")
    if target.best_known != claim.recorded_best:
        raise ValueError(f"{claim.target}: claim recorded best {claim.recorded_best} but the registry holds {target.best_known}")
    value = load_verifier(claim.verifier).verify(claim.construction, claim.parameters)
    if value != claim.value:
        raise ValueError(f"{claim.target}: verifier returns {value}, claim states {claim.value}")
    result = novelty.assess(target, value)
    result["search_status"] = search_status(target, claim, result["status"])
    control = claim.control
    result["control"] = {"kind": control.kind, "value": None if control.value is None else str(control.value),
                         "budget": control.budget, "command": control.command, "outcome": control.outcome}
    result["search_rule"] = (
        "under-searched means the unseeded control reached at least the recorded best at its stated budget, so the "
        "public cell was beatable from nothing and the claim says more about the ledger than about the method; "
        "control-missing means no control was run and the gap is open."
    )
    return result


def describe(control: Control) -> str:
    return "not-run" if control.outcome == "not-run" else f"{control.value} ({control.outcome})"


def main() -> int:
    targets = registry.load_registry()
    failures = missing = 0
    for path in sorted(CLAIMS_DIR.glob("*.json")):
        for claim in load_claims(path):
            started = time.time()
            try:
                result = check(claim, targets)
                status, search = result["status"], result["search_status"]
            except ValueError as error:
                status, search = f"REJECTED: {error}", "not-checked"
            failures += status != "improves-recorded-best"
            missing += search == "control-missing"
            print(f"{path.name} {claim.target}: {claim.value} vs recorded {claim.recorded_best}: {status}; "
                  f"control {describe(claim.control)}: {search} ({time.time() - started:.1f}s)")
    if missing:
        print(f"{missing} claim(s) labelled control-missing: run the unseeded control at the seeded budget and record it")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
