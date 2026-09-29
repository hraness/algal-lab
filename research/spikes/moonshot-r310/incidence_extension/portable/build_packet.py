"""Copy an explicit frozen-file allowlist into a deterministic public archive."""

import argparse
import gzip
import importlib.util
import io
import json
from pathlib import Path
import re
import tarfile

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("_portable_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def build(run_output, output):
    verify.require(not output.exists(), "output directory must be new")
    payload = {}
    for name, expected in verify.FROZEN.items():
        if name.startswith("source/"):
            source = run_output / name
        elif name == "data/input.json":
            source = run_output / "input.json"
        else:
            source = run_output / "round-007" / Path(name).name
        raw = verify.read_bytes(source)
        verify.require((len(raw), verify.identity(raw)["sha256"]) == expected,
                       "frozen source or artifact changed: " + name)
        payload[name] = raw
    payload.update({
        "verify.py": verify.read_bytes(HERE / "verify.py"),
        "test_verify.py": verify.read_bytes(HERE / "test_verify.py"),
        "README.md": verify.read_bytes(HERE.parent / "README.md"),
        "LICENSE": verify.read_bytes(HERE.parents[4] / "LICENSE"),
    })
    verify.require(set(payload) == verify.PAYLOAD, "builder allowlist differs")
    for name, raw in payload.items():
        verify.require(not re.search(rb"/(?:Users|home)/|/private/(?:tmp|var)/|[A-Za-z]:\\Users\\", raw),
                       "private absolute path in public file: " + name)
    manifest = verify.manifest_header()
    manifest["files"] = {name: verify.identity(raw) for name, raw in sorted(payload.items())}
    verify.check_manifest(manifest)
    payload["manifest.json"] = verify.canonical(manifest) + b"\n"
    verify.require(sum(map(len, payload.values())) <= verify.MAX_PACKET_BYTES, "packet byte limit")
    output.mkdir(parents=True)
    packet = output / verify.PACKET
    packet.mkdir()
    for name, raw in sorted(payload.items()):
        destination = packet / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    verify.validate_packet(packet)
    archive = output / (verify.PACKET + ".tar.gz")
    with archive.open("xb") as stream, gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            for name, raw in sorted(payload.items()):
                info = tarfile.TarInfo(verify.PACKET + "/" + name)
                info.size, info.mode, info.mtime = len(raw), 0o644, 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(raw))
    identities = {
        archive.name: verify.identity(archive.read_bytes()),
        verify.PACKET + "/manifest.json": verify.identity(payload["manifest.json"]),
    }
    (output / "SHA256SUMS").write_text("".join(
        metadata["sha256"] + "  " + name + "\n" for name, metadata in identities.items()))
    print(json.dumps({"packet": verify.PACKET, "archive_members": len(payload),
                      "uncompressed_file_bytes": sum(map(len, payload.values())),
                      "files": identities}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-output", type=Path, required=True,
                        help="retained pilot output directory (read only)")
    parser.add_argument("--output", type=Path, required=True,
                        help="new publication directory")
    args = parser.parse_args()
    build(args.run_output, args.output)


if __name__ == "__main__":
    main()
