"""Exact verifiers.  Each exposes ``verify(construction, parameters) -> Fraction`` and raises ValueError on invalid input."""

from importlib import import_module

VERIFIERS = {name: name for name in ("covering_design", "circle_packing", "isosceles_free", "no_five_on_sphere",
                                     "ring_loading", "sum_difference", "heilbronn_square")}


def load_verifier(name: str):
    if name not in VERIFIERS:
        raise ValueError(f"unknown verifier {name!r}")
    return import_module(f"research.extremal.verifiers.{VERIFIERS[name]}")
