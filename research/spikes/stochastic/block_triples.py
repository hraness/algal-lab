"""Exact certificates for three ordered, internally unordered target triples.

Let nine independent proper atomless scores have target groups 012, 345, and
678, with every CDF in an earlier target group at most every CDF in a later
group. No order within a target group is assumed. Arbitrary proper scores are
also covered when every label, including backgrounds, has an iid continuous
tie key independent of all scores. These finite identities, together with the
cut-separated quartet theorem and its outside-pattern lift, prove that the
target partition stochastically maximizes intact-group count at every fixed
survivor horizon, even with an independent arbitrary background vector.

Each term is a nonnegative rational coefficient times a cut-separated quartet
contrast times an EXACT selected pattern of the other five focal labels. The
pattern includes exclusions: it is an indicator, not merely a product of the
selected labels. A contrast vanishes unless two quartet labels are selected,
so fixing that outside pattern restricts its nonzero values to one focal
cardinality layer. Summing the layer identities therefore gives an identity
on the entire Boolean cube. The lift applies to each term without conditioning
on focal cardinality or altering focal independence, at every global horizon.

The accompanying fixed JSON has ten partition orbits and six potentially
nonzero (cardinality, tail) cases per orbit. Its coefficients were discovered
with an exploratory LP. This verifier uses only integer arithmetic and trusts
neither a solver status nor floating-point values. It explicitly transports
the identities to all 280 partitions by permutations within target blocks,
then checks every one of 512 selected sets and all thresholds 0..4, including
the trivial layers and tails. This is a finite proof for n=9, r=3, not a claim
about general numbers or sizes of internally unordered blocks.

Term arrays have the fixed layout [numerator, denominator, a, b, c, d,
selectedOutsideMask, crossing]. The positive pairs are ab and cd; crossing 0
uses negative pairs ac,bd, while crossing 1 uses ad,bc. All bounds and data
paths are fixed. verify() is the only public entry point; there are no CLI
inputs, repository imports, or optional dependencies.
"""
from copy import deepcopy
from itertools import combinations
import json
from math import gcd
from pathlib import Path


_FULL = 511
_TARGET = (7, 56, 448)
_CASES = {(3, 1), (4, 1), (5, 1), (6, 1), (6, 2), (7, 2)}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(value: object, low: int, high: int) -> bool:
    return type(value) is int and low <= value <= high


def _keys(value: object, expected: set[str]) -> None:
    _require(type(value) is dict and set(value) == expected, "unexpected object fields")


def _mask(labels) -> int:
    return sum(1 << label for label in labels)


def _count(selected: int, groups: tuple[int, ...]) -> int:
    return sum(selected & group == group for group in groups)


def _signature(groups: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(tuple((group & block).bit_count() for block in _TARGET)
                        for group in groups))


def _partitions(labels: tuple[int, ...]):
    if not labels:
        yield ()
        return
    for rest in combinations(labels[1:], 2):
        group = (labels[0], *rest)
        remaining = tuple(label for label in labels if label not in group)
        for tail in _partitions(remaining):
            yield (_mask(group), *tail)


def _document_tables(document: object):
    """Validate the fixed schema and reconstruct every representative identity."""
    _keys(document, {"schema_version", "label_count", "group_size", "coefficient_scale",
                     "target_groups", "orbits"})
    for field, expected in (("schema_version", 1), ("label_count", 9),
                            ("group_size", 3), ("coefficient_scale", 6)):
        _require(type(document[field]) is int and document[field] == expected,
                 "unexpected fixed parameter")
    _require(document["target_groups"] == [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
             "unexpected target groups")
    orbits = document["orbits"]
    _require(type(orbits) is list and len(orbits) == 10, "expected ten orbit records")
    tables = {}
    certificate_count = term_count = 0
    for orbit in orbits:
        _keys(orbit, {"groups", "block_counts", "certificates"})
        groups = orbit["groups"]
        _require(type(groups) is list and len(groups) == 3, "expected three groups")
        _require(all(type(group) is list and len(group) == 3
                     and all(_integer(label, 0, 8) for label in group)
                     and group == sorted(set(group)) for group in groups),
                 "invalid representative group")
        _require(sorted(label for group in groups for label in group) == list(range(9)),
                 "groups must partition the nine labels")
        masks = tuple(_mask(group) for group in groups)
        signature = _signature(masks)
        _require(orbit["block_counts"] == [list(row) for row in signature],
                 "incorrect block-count signature")
        _require(signature not in tables, "duplicate partition orbit")
        certificates = orbit["certificates"]
        _require(type(certificates) is list and len(certificates) == 6,
                 "expected six cases per orbit")
        values = [[0] * 5 for _ in range(512)]
        seen_cases = set()
        for certificate in certificates:
            _keys(certificate, {"selected_count", "threshold", "terms"})
            cardinality, threshold = certificate["selected_count"], certificate["threshold"]
            _require(_integer(cardinality, 3, 7) and _integer(threshold, 1, 2),
                     "invalid certificate case")
            case = (cardinality, threshold)
            _require(case in _CASES and case not in seen_cases, "unexpected or repeated case")
            seen_cases.add(case)
            terms = certificate["terms"]
            _require(type(terms) is list and len(terms) <= 64, "too many terms")
            for term in terms:
                _require(type(term) is list and len(term) == 8
                         and all(type(value) is int for value in term), "invalid term shape")
                numerator, denominator, a, b, c, d, fixed, crossing = term
                _require(0 < numerator <= 6 and denominator in (1, 2, 3, 6)
                         and gcd(numerator, denominator) == 1, "invalid positive coefficient")
                _require(0 <= a < b < c < d <= 8, "quartet labels must be distinct")
                _require(b // 3 < c // 3, "quartet cut crosses an unordered target block")
                _require(0 <= fixed <= _FULL and crossing in (0, 1), "invalid term pattern")
                quartet = _mask((a, b, c, d))
                outside = _FULL ^ quartet
                _require(fixed & quartet == 0, "outside pattern intersects quartet")
                _require(fixed.bit_count() == cardinality - 2, "wrong outside cardinality")
                weight = numerator * (6 // denominator)
                for selected in range(512):
                    # Equality fixes BOTH selected and excluded outside labels.
                    # Using a subset test here would invalidate the proof.
                    if selected & outside != fixed:
                        continue
                    ya, yb, yc, yd = (int(bool(selected & (1 << label)))
                                     for label in (a, b, c, d))
                    contrast = ((ya - yd) * (yb - yc) if crossing == 0
                                else (ya - yc) * (yb - yd))
                    if contrast:
                        _require(selected.bit_count() == cardinality,
                                 "term leaked outside its cardinality layer")
                    values[selected][threshold] += weight * contrast
                term_count += 1
            certificate_count += 1
        _require(seen_cases == _CASES, "missing certificate case")
        # Representatives are checked before their explicit relabelings. This
        # also makes algebraic tampering fail without an expensive later pass.
        for selected in range(512):
            target_count, other_count = _count(selected, _TARGET), _count(selected, masks)
            for threshold in range(5):
                expected = 6 * (int(target_count >= threshold) - int(other_count >= threshold))
                _require(values[selected][threshold] == expected, "exact identity failed")
        tables[signature] = (masks, values)
    _require(certificate_count == 60 and term_count == 533, "unexpected certificate size")
    return tables


def _relabeling(representative: tuple[int, ...], candidate: tuple[int, ...]) -> tuple[int, ...]:
    """Construct a block-preserving bijection taking one partition to the other.

    Rows with the same intersection counts can be paired arbitrarily. Within
    each paired row/block cell, biject its labels. Disjoint cells cover all
    labels, proving that equal signatures suffice for orbit membership.
    """
    unused = list(candidate)
    mapping = [-1] * 9
    for old_group in representative:
        counts = tuple((old_group & block).bit_count() for block in _TARGET)
        new_group = next(group for group in unused
                         if tuple((group & block).bit_count() for block in _TARGET) == counts)
        unused.remove(new_group)
        for block in _TARGET:
            old_labels = [i for i in range(9) if old_group & block & (1 << i)]
            new_labels = [i for i in range(9) if new_group & block & (1 << i)]
            _require(len(old_labels) == len(new_labels), "different orbit cells")
            for old, new in zip(old_labels, new_labels):
                mapping[old] = new
    _require(not unused and sorted(mapping) == list(range(9)), "not a bijection")
    _require(all(old // 3 == new // 3 for old, new in enumerate(mapping)),
             "relabeling leaves a target block")
    return tuple(mapping)


def _map_mask(mask: int, mapping: tuple[int, ...]) -> int:
    return _mask(mapping[i] for i in range(9) if mask & (1 << i))


def _all_partition_checks(tables) -> int:
    candidates = tuple(_partitions(tuple(range(9))))
    _require(len(candidates) == len(set(candidates)) == 280, "partition enumeration failed")
    reached = set()
    cases = 0
    for candidate in candidates:
        signature = _signature(candidate)
        _require(signature in tables, "missing partition orbit")
        reached.add(signature)
        representative, values = tables[signature]
        mapping = _relabeling(representative, candidate)
        _require({_map_mask(group, mapping) for group in representative} == set(candidate),
                 "relabeling does not give the candidate")
        _require(tuple(_map_mask(block, mapping) for block in _TARGET) == _TARGET,
                 "relabeling changed target partition")
        mapped_sets = set()
        for selected in range(512):
            mapped = _map_mask(selected, mapping)
            mapped_sets.add(mapped)
            target_count, other_count = _count(mapped, _TARGET), _count(mapped, candidate)
            for threshold in range(5):
                expected = 6 * (int(target_count >= threshold) - int(other_count >= threshold))
                _require(values[selected][threshold] == expected,
                         "relabeled exact identity failed")
                cases += 1
        _require(len(mapped_sets) == 512, "selection-set coverage failed")
    _require(reached == set(tables), "unused or missing orbit")
    _require(cases == 716800, "state-tail coverage failed")
    return cases


def _tamper_checks(document) -> int:
    first = next((i, j, k) for i, orbit in enumerate(document["orbits"])
                 for j, case in enumerate(orbit["certificates"])
                 for k, _ in enumerate(case["terms"]))
    rejected = 0
    for alteration in range(7):
        changed = deepcopy(document)
        i, j, k = first
        term = changed["orbits"][i]["certificates"][j]["terms"][k]
        if alteration == 0:
            term[0] = -1
        elif alteration == 1:
            term[1] = 0
        elif alteration == 2:
            term[3] = term[2]
        elif alteration == 3:
            term[2:6] = [0, 3, 4, 6]  # middle labels cross inside target block 1
        elif alteration == 4:
            term[6] |= 1 << term[2]
        elif alteration == 5:
            term[0] += term[1]  # positive, well-formed, but algebraically false
        else:
            changed["orbits"][i]["certificates"].pop()
        try:
            _document_tables(changed)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("tampered certificate was accepted")
    return rejected


def verify() -> dict[str, int]:
    """Verify the bounded checked-in certificate and return compact coverage."""
    raw = Path(__file__).with_name("block_triples_certificate.json").read_bytes()
    _require(len(raw) <= 262144, "certificate exceeds its fixed size bound")
    document = json.loads(raw)
    tables = _document_tables(document)
    cases = _all_partition_checks(tables)
    rejected = _tamper_checks(document)
    return {"blockTriplePartitions": 280, "blockTripleOrbits": len(tables),
            "blockTripleCertificates": 60, "blockTripleTerms": 533,
            "blockTripleStateTailChecks": cases, "blockTripleTamperRejections": rejected}


if __name__ == "__main__":
    print("block-separated triples:", verify())
