"""Mechanical novelty gate against the registry's recorded best-known value."""

from __future__ import annotations

from fractions import Fraction

from .registry import Target


def reporting_precision(target: Target) -> Fraction:
    """Half a unit in the last reported decimal place; zero for exact values."""
    return target.reporting_precision()


def assess(target: Target, value: Fraction) -> dict:
    """Compare an exactly verified value with the recorded best.

    The result is a statement about the registry entry on its retrieval date,
    never a worldwide priority claim.
    """
    sign = 1 if target.objective == "maximize" else -1
    margin = (value - target.best_known) * sign
    precision = reporting_precision(target)
    if margin > precision:
        status = "improves-recorded-best"
    elif margin > 0:
        status = "within-reporting-precision"
    elif margin == 0:
        status = "matches-recorded-best"
    else:
        status = "below-recorded-best"
    return {
        "target": target.id,
        "status": status,
        "verified_value": str(value),
        "recorded_value": str(target.best_known),
        "recorded_kind": target.best_known_kind,
        "margin": str(margin),
        "reporting_precision": str(precision),
        "source": target.source,
        "url": target.url,
        "retrieved": target.retrieved,
        "claim_rule": (
            "A status of improves-recorded-best means the exact verified value beats the value "
            "recorded from the cited source on the retrieval date by more than its reporting "
            "precision. Before any claim, re-read the source on the claim date and search for "
            "later improvements; record both in the novelty ledger."
        ),
    }
