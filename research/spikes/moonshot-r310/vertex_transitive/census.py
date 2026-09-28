"""Check a local graph6 collection without assuming its catalogue is complete."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import time

from checker import SearchLimit, independent_set, triangle, verify_independent


def decode_graph6(record):
    if record.startswith(b">>graph6<<"):
        record = record[10:]
    if not record or record[0] not in range(64, 126):
        raise ValueError("expected short graph6 order 1..62")
    n = record[0] - 63
    bit_count = n * (n - 1) // 2
    if len(record) != 1 + (bit_count + 5) // 6 or any(v not in range(63, 127) for v in record[1:]):
        raise ValueError("invalid graph6 length or alphabet")
    padding = -bit_count % 6
    if padding and (record[-1] - 63) & ((1 << padding) - 1):
        raise ValueError("nonzero graph6 padding")
    adj = [0] * n
    bit = 0
    for v in range(1, n):
        for u in range(v):
            if (record[1 + bit // 6] - 63) >> (5 - bit % 6) & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
            bit += 1
    return adj


def scan(path, *, order=40, target=10, max_records=100_000, seconds=60, expected_count=None):
    if not 1 <= order <= 62 or not 1 <= target <= order:
        raise ValueError("invalid graph order or independence target")
    if not 1 <= max_records <= 100_000 or not 0 < seconds <= 300:
        raise ValueError("invalid record or time budget")
    with open(path, "rb") as source:
        snapshot = source.read(16 * 1024 * 1024 + 1)
    if len(snapshot) > 16 * 1024 * 1024:
        raise ValueError("input exceeds 16 MiB; supply a reviewed smaller collection")
    if expected_count is not None and not 1 <= expected_count <= max_records:
        raise ValueError("expected count outside record budget")
    source_digest = hashlib.sha256(snapshot).hexdigest()
    result = {"schema_version": 1, "source_sha256": source_digest, "order": order,
              "target": target, "checked": 0, "with_triangles": 0, "with_independent_set": 0,
              "degree_counts": [0] * order, "complete_file": False, "reason": "record_limit",
              "expected_count": expected_count, "candidate": None,
              "catalogue_completeness": "not established by this file scan"}
    started = time.monotonic()
    deadline = started + seconds
    seen = set()
    with io.BytesIO(snapshot) as source:
        for line_number, line in enumerate(source, 1):
            if len(line) > 1024:
                raise ValueError(f"oversized line {line_number}")
            record = line.rstrip(b"\r\n")
            if line_number == 1 and record == b">>graph6<<":
                continue
            if result["checked"] >= max_records:
                break
            if time.monotonic() >= deadline:
                result["reason"] = "time_limit"
                break
            if record in seen:
                raise ValueError(f"duplicate encoded graph at line {line_number}")
            seen.add(record)
            adj = decode_graph6(record)
            if len(adj) != order:
                raise ValueError(f"wrong graph order at line {line_number}")
            tri = triangle(adj)
            independent = None
            if tri is None:
                try:
                    independent = independent_set(adj, target, node_limit=5_000_000, deadline=deadline)
                except SearchLimit as limit:
                    result["reason"] = str(limit)
                    break
                if independent is not None and not verify_independent(adj, independent, target):
                    raise AssertionError("independence oracle returned an invalid witness")
            result["checked"] += 1
            result["degree_counts"][max(row.bit_count() for row in adj)] += 1
            if tri is not None:
                result["with_triangles"] += 1
            elif independent is not None:
                result["with_independent_set"] += 1
            else:
                result["candidate"] = {"line": line_number, "graph6": record.decode("ascii"),
                                       "adjacency": adj}
                result["reason"] = "candidate_found"
                break
        else:
            result["complete_file"] = True
            result["reason"] = "exhausted_file"
    result["expected_count_matched"] = expected_count is not None and result["checked"] == expected_count
    if result["complete_file"] and expected_count is not None and not result["expected_count_matched"]:
        raise ValueError("file ended without the declared number of graphs")
    result["wall_seconds"] = round(time.monotonic() - started, 6)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="new JSON result file")
    parser.add_argument("--order", type=int, default=40)
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--max-records", type=int, default=100_000)
    parser.add_argument("--expected-count", type=int)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    result = scan(args.input, order=args.order, target=args.target, seconds=args.seconds,
                  max_records=args.max_records, expected_count=args.expected_count)
    with open(args.output, "x") as target:
        json.dump(result, target, indent=2)
        target.write("\n")
    print(f"{result['reason']}: {result['checked']} graphs; source SHA256 {result['source_sha256']}")
    return 0 if result["complete_file"] or result["candidate"] is not None else 3


if __name__ == "__main__":
    raise SystemExit(main())
