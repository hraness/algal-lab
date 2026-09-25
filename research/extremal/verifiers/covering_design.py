"""Covering design verifier: a list of k-subsets of {0..v-1} covering every t-subset."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations

MAX_V = 64
MAX_BLOCKS = 100_000

DESCRIPTION = (
    "A covering design C(v,k,t) is a family of k-element subsets (blocks) of {0,...,v-1} "
    "such that every t-element subset is contained in at least one block. The score is the "
    "number of blocks; fewer is better. A construction that leaves any t-subset uncovered is "
    "rejected outright, so return a complete covering. Output: {\"blocks\": [[int, ...], ...]} "
    "with plain Python ints, each block exactly k distinct points."
)


def verify(construction, parameters) -> Fraction:
    v, k, t = (int(parameters[key]) for key in ("v", "k", "t"))
    if not (1 <= t <= k <= v <= MAX_V):
        raise ValueError("need 1 <= t <= k <= v <= 64")
    if not isinstance(construction, dict) or "blocks" not in construction:
        raise ValueError("construction must be an object with 'blocks'")
    blocks = construction["blocks"]
    if not isinstance(blocks, list) or len(blocks) > MAX_BLOCKS:
        raise ValueError("blocks must be a list of at most 100000 blocks")
    seen = set()
    masks = []
    for block in blocks:
        if not isinstance(block, list) or len(block) != k:
            raise ValueError(f"every block must be a list of {k} points")
        if any(isinstance(p, bool) or not isinstance(p, int) or not 0 <= p < v for p in block):
            raise ValueError("block points must be integers in range")
        if len(set(block)) != k:
            raise ValueError("block points must be distinct")
        key = tuple(sorted(block))
        if key in seen:
            raise ValueError("duplicate block")
        seen.add(key)
        mask = 0
        for p in block:
            mask |= 1 << p
        masks.append(mask)
    for subset in combinations(range(v), t):
        mask = 0
        for p in subset:
            mask |= 1 << p
        if not any(mask & b == mask for b in masks):
            raise ValueError(f"uncovered {t}-subset {subset}")
    return Fraction(len(masks))
