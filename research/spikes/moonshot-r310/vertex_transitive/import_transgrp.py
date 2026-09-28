"""Read pinned TransGrp permutation literals as data; never evaluate GAP code.

Obtain the original archive separately. The archive and derived manifests are
research inputs, not vendored source. This parser intentionally supports only
the observed, explicit disjoint-cycle format, and refuses general GAP syntax.
"""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

from orbits import digest, validate_action


ARCHIVE_URL = "https://www.math.colostate.edu/~hulpke/transgrp/transgrp3.6.5.tar.gz"
ARCHIVE_SHA256 = "6f2ec142a004f9d5e3b28bfa03246472fee93ceb12837206960bcb560eb72376"
EXPECTED_MINIMAL_COUNTS = {39: 4, 40: 1963}
EXPECTED_GROUP_COUNTS = {39: 306, 40: 315842}


def parse_minimals(text, degree):
    match = re.fullmatch(r"\s*TRANSMINIMALS\{\[32\.\.47\]\}\s*:=\s*([\[\]\d,\s]+);\s*", text)
    if match is None:
        raise ValueError("unsupported minimal-index assignment")
    lists = json.loads(match.group(1))
    if not isinstance(lists, list) or len(lists) != 16:
        raise ValueError("wrong minimal-index degree range")
    if degree not in EXPECTED_MINIMAL_COUNTS:
        raise ValueError("supported degrees are 39 and 40")
    ids = lists[degree - 32]
    if (not isinstance(ids, list) or len(ids) != EXPECTED_MINIMAL_COUNTS[degree]
            or any(type(value) is not int or not 1 <= value <= 315842 for value in ids)
            or sorted(set(ids)) != ids):
        raise ValueError("unexpected, repeated, or unsorted minimal-action IDs")
    return ids


def parse_generators(text, n):
    if re.search(r"[^0-9(),\s]|\d\s+\d", text):
        raise ValueError("generator is not literal disjoint-cycle data")
    compact = re.sub(r"\s", "", text)
    pieces = re.findall(r"(?:\([^()]*\))+", compact)
    if ",".join(pieces) != compact or not 1 <= len(pieces) <= 128:
        raise ValueError("unsupported generator list")
    generators = []
    for piece in pieces:
        perm = list(range(n))
        seen = set()
        cycles = re.findall(r"\(([^()]*)\)", piece)
        for literal in cycles:
            if not literal:
                if len(cycles) != 1:
                    raise ValueError("identity mixed with nonidentity cycles")
                continue
            if not re.fullmatch(r"[1-9]\d*(?:,[1-9]\d*)*", literal):
                raise ValueError("invalid cycle literal")
            cycle = [int(value) - 1 for value in literal.split(",")]
            if (len(cycle) < 2 or len(set(cycle)) != len(cycle)
                    or seen.intersection(cycle) or any(not 0 <= v < n for v in cycle)):
                raise ValueError("cycles must be disjoint and use in-range distinct points")
            seen.update(cycle)
            for u, v in zip(cycle, cycle[1:] + cycle[:1]):
                perm[u] = v
        generators.append(perm)
    return generators


def parse_chunk(text, n, wanted):
    if len(re.findall(rf"(?m)^TRANSGRP\[{n}\]", text)) != 1:
        raise ValueError("expected exactly one generator assignment per chunk")
    marker = re.search(rf"(?m)^TRANSGRP\[{n}\]\{{\[(\d+)\.\.(\d+)\]\}}\s*:=\s*", text)
    if marker is None:
        raise ValueError("missing literal generator assignment")
    prefix = re.sub(r"(?m)#.*$", "", text[:marker.start()]).strip()
    if prefix:
        raise ValueError("unexpected content before generator assignment")
    first, last = map(int, marker.groups())
    if not 1 <= first <= last <= 315842 or last - first >= 5000:
        raise ValueError("unsupported assignment range")
    remainder = text[marker.end():]
    end = re.search(r"\]\s*;", remainder)
    if end is None:
        raise ValueError("unterminated generator assignment")
    outer = remainder[:end.start() + 1]
    if not outer.startswith("[") or not outer.endswith("]"):
        raise ValueError("expected an outer generator list")
    body = outer[1:-1]
    chunks = list(re.finditer(r"\[([^\[\]]*)\]", body))
    if len(chunks) != last - first + 1:
        raise ValueError("generator count does not match assignment range")
    expected_separator = ""
    previous = 0
    result = {}
    for index, chunk in enumerate(chunks, first):
        if body[previous:chunk.start()].strip() != expected_separator:
            raise ValueError("unsupported data between groups")
        previous = chunk.end()
        expected_separator = ","
        if index in wanted:
            literal = chunk.group(1)
            # Some degree files append a group-name string. TransGrp's loader
            # treats it as metadata, not a generator; accept only its exact ID.
            name = re.search(r',\s*"t(\d+)n(\d+)"\s*$', literal)
            if name is not None:
                if tuple(map(int, name.groups())) != (n, index):
                    raise ValueError("group-name metadata disagrees with its index")
                literal = literal[:name.start()]
            action = {"name": f"TransGrp3.6.5-{n}T{index}", "n": n,
                      "generators": parse_generators(literal, n)}
            validate_action(action)
            result[index] = action
    if body[previous:].strip():
        raise ValueError("unsupported trailing generator data")
    return first, last, result


def member_bytes(archive, member, *, compressed=False):
    if not member.isfile() or member.size > 8 * 1024 * 1024:
        raise ValueError("unexpected archive member type or size")
    with archive.extractfile(member) as source:
        data = source.read(8 * 1024 * 1024 + 1)
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as source:
            data = source.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("member exceeds the decompression limit")
    return data


def import_archive(path, degree=40):
    with open(path, "rb") as source:
        snapshot = source.read(80_000_001)
    if len(snapshot) > 80_000_000 or hashlib.sha256(snapshot).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("archive bytes do not match the pinned research input")
    provenance = {"archive_url": ARCHIVE_URL, "archive_sha256": ARCHIVE_SHA256,
                  "archive_bytes": len(snapshot), "package_version": "3.6.5", "degree": degree,
                  "completeness_basis": "TransGrp MinimalTransitiveIndices, checked against Holt/Royle Table 2",
                  "data_files": {}}
    with tarfile.open(fileobj=io.BytesIO(snapshot), mode="r:gz") as archive:
        members = archive.getmembers()
        if len(members) > 1000 or len({m.name for m in members}) != len(members):
            raise ValueError("unexpected or repeated archive members")
        lookup = {m.name: m for m in members}
        name = "transgrp/data/transminimals.grp.gz"
        data = member_bytes(archive, lookup[name], compressed=True)
        ids = parse_minimals(data.decode("ascii"), degree)
        provenance["data_files"][name] = hashlib.sha256(data).hexdigest()
        provenance["minimal_indices"] = ids
        provenance["minimal_indices_sha256"] = digest(ids)
        provenance["license_text"] = member_bytes(archive, lookup["transgrp/LICENSE"]).decode("ascii")
        actions = {}
        covered_ranges = []
        # Archive order avoids repeatedly seeking backwards through the outer gzip.
        for member in members:
            if not re.fullmatch(rf"transgrp/data/trans{degree}[a-z]+\.grp\.gz", member.name):
                continue
            data = member_bytes(archive, member, compressed=True)
            first, last, selected = parse_chunk(data.decode("ascii"), degree, set(ids))
            if actions.keys() & selected.keys():
                raise ValueError("repeated minimal-action ID across chunks")
            actions.update(selected)
            covered_ranges.append((first, last))
            if selected:
                provenance["data_files"][member.name] = hashlib.sha256(data).hexdigest()
        if sorted(actions) != ids:
            raise ValueError("missing minimal-action generators")
        ranges = sorted(covered_ranges)
        if (not ranges or ranges[0][0] != 1 or ranges[-1][1] != EXPECTED_GROUP_COUNTS[degree]
                or any(a[1] + 1 != b[0] for a, b in zip(ranges, ranges[1:]))):
            raise ValueError("generator chunks have overlapping or missing index ranges")
        ordered = [actions[index] for index in ids]
        provenance["action_count"] = len(ordered)
        provenance["actions_sha256"] = digest(ordered)
        provenance["parsed_group_range"] = [ranges[0][0], ranges[-1][1]]
    return ordered, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--degree", type=int, choices=sorted(EXPECTED_MINIMAL_COUNTS), default=40)
    parser.add_argument("--output", type=Path, required=True, help="new directory for ignored research data")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    actions, provenance = import_archive(args.archive, args.degree)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "actions.json").write_text(json.dumps(actions, indent=2) + "\n")
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Imported {len(actions)} actions of degree {args.degree}; SHA256 {provenance['actions_sha256']}")


if __name__ == "__main__":
    main()
