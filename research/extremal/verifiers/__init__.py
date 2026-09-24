"""Exact verifiers.  Each exposes ``verify(construction, parameters) -> Fraction`` and raises ValueError on invalid input."""

from importlib import import_module

VERIFIERS = {"covering_design": "covering_design", "circle_packing": "circle_packing"}


def load_verifier(name: str):
    if name not in VERIFIERS:
        raise ValueError(f"unknown verifier {name!r}")
    return import_module(f"research.extremal.verifiers.{VERIFIERS[name]}")
