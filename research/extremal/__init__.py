"""Extremal-construction discovery loop with exact verifiers and a mechanical novelty gate.

Targets are problems whose best-known value is publicly recorded with a
citation.  A candidate is a bounded program that prints a construction; an
exact verifier scores it; the gate compares the exact score with the recorded
value.  "Novel" means strictly better than the recorded value, nothing weaker.
"""
