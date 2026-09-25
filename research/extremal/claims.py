"""Construction claims: exactly verified constructions that beat a registry snapshot.

A claims file records, per construction, the target it improves, the value
recorded in the registry when the claim was made, the claim date, how the
construction was derived, and the construction itself. ``check`` re-runs the
verifier and the novelty gate; nothing in the file is trusted.

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
FIELDS = {"target", "verifier", "parameters", "value", "recorded_best", "claimed", "derivation", "construction"}


@dataclass(frozen=True)
class Claim:
    target: str
    verifier: str
    parameters: dict
    value: Fraction
    recorded_best: Fraction
    claimed: str
    derivation: tuple
    construction: dict


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
                 claimed=raw["claimed"], derivation=tuple(steps), construction=raw["construction"])


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


def check(claim: Claim, targets: dict) -> dict:
    """Re-verify one claim; raise ValueError on any inconsistency, else return the novelty assessment."""
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
    return novelty.assess(target, value)


def main() -> int:
    targets = registry.load_registry()
    failures = 0
    for path in sorted(CLAIMS_DIR.glob("*.json")):
        for claim in load_claims(path):
            started = time.time()
            try:
                result = check(claim, targets)
                status = result["status"]
            except ValueError as error:
                status = f"REJECTED: {error}"
            failures += status != "improves-recorded-best"
            print(f"{path.name} {claim.target}: {claim.value} vs recorded {claim.recorded_best}: {status} ({time.time() - started:.1f}s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
