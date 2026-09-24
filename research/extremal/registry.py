"""Target registry: recorded best-known values with citations and retrieval dates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

REGISTRY_PATH = Path(__file__).with_name("registry.json")
MAX_REGISTRY_BYTES = 256 * 1024
OBJECTIVES = ("maximize", "minimize")


@dataclass(frozen=True)
class Target:
    id: str
    title: str
    objective: str
    verifier: str
    parameters: dict
    best_known: Fraction
    best_known_kind: str
    source: str
    url: str
    retrieved: str
    notes: str

    def improves(self, value: Fraction) -> bool:
        return self.margin(value) > self.reporting_precision()

    def margin(self, value: Fraction) -> Fraction:
        """Signed improvement over the recorded best (positive is better)."""
        sign = 1 if self.objective == "maximize" else -1
        return (value - self.best_known) * sign

    def reporting_precision(self) -> Fraction:
        """Half a unit in the last reported decimal place; zero for exact values.

        A value reported as 2.635 may stand for anything in [2.6345, 2.6355], so
        a verified value only beats it definitively when the margin exceeds 5e-4.
        """
        if self.best_known_kind != "reported-decimal":
            return Fraction(0)
        unit = Fraction(1)
        while (self.best_known / unit).denominator != 1:
            unit /= 10
        return unit / 2


def parse_value(text) -> Fraction:
    if isinstance(text, bool) or not isinstance(text, (int, str)):
        raise ValueError("values must be integers or rational strings")
    return Fraction(text)


def _require(obj: dict, key: str, kind):
    if key not in obj or not isinstance(obj[key], kind) or isinstance(obj[key], bool):
        raise ValueError(f"registry entry needs {key!r} of type {kind.__name__}")
    return obj[key]


def parse_target(raw) -> Target:
    if not isinstance(raw, dict):
        raise ValueError("registry entry must be an object")
    allowed = {"id", "title", "objective", "verifier", "parameters", "best_known", "source", "url", "retrieved", "notes"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown registry fields: {sorted(unknown)}")
    objective = _require(raw, "objective", str)
    if objective not in OBJECTIVES:
        raise ValueError(f"objective must be one of {OBJECTIVES}")
    best = _require(raw, "best_known", dict)
    kind = _require(best, "kind", str)
    if kind not in ("exact", "reported-decimal"):
        raise ValueError("best_known.kind must be 'exact' or 'reported-decimal'")
    parameters = _require(raw, "parameters", dict)
    value = parse_value(_require(best, "value", (int, str)))
    if kind == "reported-decimal":
        denominator = value.denominator
        for prime in (2, 5):
            while denominator % prime == 0:
                denominator //= prime
        if denominator != 1:
            raise ValueError("reported-decimal values must be terminating decimals")
    return Target(
        id=_require(raw, "id", str),
        title=_require(raw, "title", str),
        objective=objective,
        verifier=_require(raw, "verifier", str),
        parameters=parameters,
        best_known=value,
        best_known_kind=kind,
        source=_require(best, "source", str),
        url=_require(best, "url", str),
        retrieved=_require(best, "retrieved", str),
        notes=str(raw.get("notes", "")),
    )


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Target]:
    data = path.read_bytes()
    if len(data) > MAX_REGISTRY_BYTES:
        raise ValueError("registry file too large")
    raw = json.loads(data)
    if not isinstance(raw, dict) or not isinstance(raw.get("targets"), list):
        raise ValueError("registry must be an object with a 'targets' list")
    targets = {}
    for entry in raw["targets"]:
        target = parse_target(entry)
        if target.id in targets:
            raise ValueError(f"duplicate target id {target.id}")
        targets[target.id] = target
    return targets
