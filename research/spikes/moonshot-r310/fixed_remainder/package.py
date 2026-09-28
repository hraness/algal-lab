"""Package and independently replay the seven fixed-remainder certificates.

The builder consumes the retained 2026-09-28 records. The public verifier
uses their exact formulas and proofs; it never invokes a SAT solver.
"""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import resource
import stat
import sys
import tarfile

HERE = Path(__file__).resolve().parent
PROFILE = "fixed-h-column-selector-v1"
ARCHIVE_ROOT = "r310-fixed-remainder-proof"
MAX_MEMBER_BYTES = 256 * 1024**2
MAX_TOTAL_BYTES = 512 * 1024**2
MAX_MEMBERS = 200
CHECKER_COMMIT = "b30f400f4ee5c32b77ee566a7c006081b521534f"
CHECKER_SOURCE = "fdd3c1574ce2caef9e2ab2c08cd1919d7153f46682f9ed4c760706ab2bfc9944"
CHECKER_LICENSE = "fed6340aef9aca20fb84b0b1bba47dc3880660016a1b9b3b81b676ba0c9700f6"
FORMULA_AUDITOR = "da5cbcb19cfe5134e44530feed87abb4cd03f1a1c76c389f93c420b0f73916ca"
PAIRS = ((0, 1), (0, 2), (0, 4), (0, 5), (0, 7), (0, 8), (0, 14))
PRIVATE_PREFIXES = (b"/" + b"Users/", b"/" + b"private/tmp/", b"/" + b"home/")
SOURCE_NAMES = (
    "degree_four/lrat.py", "degree_six/encoding.py", "degree_six/native.py",
    "fixed_remainder/catalogue.py", "fixed_remainder/column_cover.py",
    "fixed_remainder/encode.py", "fixed_remainder/independent_cover.py",
    "fixed_remainder/process.py", "fixed_remainder/proof.py", "fixed_remainder/run.py",
    "fixed_remainder/selector.py", "fixed_remainder/selector_proof.py",
    "fixed_remainder/selector_run.py", "fixed_remainder/shared.py",
    "fixed_remainder/test_column_cover.py", "fixed_remainder/test_fixed.py",
    "fixed_remainder/test_independent_cover.py", "fixed_remainder/test_process.py",
    "fixed_remainder/test_selector.py", "vertex_transitive/checker.py",
)
STAGE_FIELDS = (
    "schema_version", "executable_sha256", "status", "cpu_limit_seconds",
    "wall_limit_seconds", "memory_threshold_mib", "rss_sampling_interval_seconds",
    "rss_sample_timeout_seconds", "memory_limit_is_cooperative", "linux_address_space_limit",
    "per_file_limit_bytes", "returncode", "external_stop", "supervisor_signal",
    "wall_seconds", "children_cpu_seconds_including_rss_sampler",
    "maximum_sampled_rss_bytes", "log_sha256", "owned_child_collected",
)
RESULT_FIELDS = (
    "schema_version", "profile", "status", "case_index", "necessary_selector_formula_unsat",
    "python_rup_verified", "lrat_trim_verified", "sat_is_only_a_cover", "ramsey_graph_found",
    "external_ramsey_bound_claim_made", "source_sha256", "solver-version", "lrat-trim-version",
    "proof_verification", "peak_bytes", "no_solver_rerun", "certificate_sha256",
    "all_owned_children_collected",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    require(isinstance(name, str) and 0 < len(name) <= 240, "invalid member name")
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in name.split("/"))
            and "\\" not in name and not any(ord(c) < 32 for c in name), "unsafe member name")
    return path


def bounded_bytes(path, limit=MAX_MEMBER_BYTES):
    require(not path.is_symlink(), "symbolic-link input is unsupported")
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_size <= limit, "input exceeds type or byte limit")
    with path.open("rb") as source:
        raw = source.read(limit + 1)
    require(len(raw) <= limit, "input grew beyond byte limit")
    return raw


def read_json(path):
    value = json.loads(bounded_bytes(path, 16 * 1024**2))
    require(isinstance(value, dict), "expected a JSON object")
    return value


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def public_record(record, original_digest):
    """Copy a declared set of scientific and execution fields, never argv/PIDs."""
    projected = {key: record[key] for key in RESULT_FIELDS if key in record}
    projected["stages"] = {
        name: {key: stage[key] for key in STAGE_FIELDS if key in stage}
        for name, stage in record.get("stages", {}).items()
    }
    projected["original_record_sha256"] = original_digest
    projected["projection_note"] = (
        "Original status and scientific fields are preserved. Local executable paths, "
        "command paths and process identifiers are omitted. The original record remains retained."
    )
    return projected


def check_stage(stage, code):
    require(stage.get("status") == "complete" and stage.get("returncode") == code
            and stage.get("owned_child_collected") is True
            and stage.get("external_stop") is None and stage.get("supervisor_signal") is None,
            "stage did not complete and collect successfully")


def check_run_files(directory, result):
    for name, expected in result["artifact_sha256"].items():
        require(len(safe_name(name).parts) == 1, "nested recorded artifact")
        require(sha(bounded_bytes(directory / name)) == expected, "recorded artifact hash mismatch")
    for name, stage in result["stages"].items():
        safe_name(name)
        log_name = "solver" if name == "solve" else name
        require(sha(bounded_bytes(directory / (log_name + ".log"))) == stage["log_sha256"],
                "recorded stage log mismatch")
        require(read_json(directory / (name + "-stage.json")) == stage,
                "stage and result records disagree")


def snapshot(directory, hashes):
    require(set(hashes) == set(SOURCE_NAMES), "unexpected source snapshot")
    result = {}
    for name in SOURCE_NAMES:
        raw = bounded_bytes(directory / name, 1024**2)
        require(sha(raw) == hashes[name], "source snapshot mismatch: " + name)
        result[name] = raw
    return result


def privacy_check(name, raw):
    require(not any(prefix in raw for prefix in PRIVATE_PREFIXES), "private path in member: " + name)
    if name.endswith(".json"):
        def visit(value):
            if isinstance(value, dict):
                require(not {"pid", "ppid", "argv"} & set(value), "private process field in member: " + name)
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        visit(json.loads(raw))


def build(runs, third_party, output, *, check_only=False):
    require(not output.exists() and not output.with_name(output.name + ".sha256").exists(),
            "archive and digest destinations must be new")
    members, total = {}, 0

    def add(name, raw):
        nonlocal total
        safe_name(name)
        require(name not in members and len(members) < MAX_MEMBERS, "duplicate or excess archive member")
        require(len(raw) <= MAX_MEMBER_BYTES, "archive member exceeds byte limit")
        total += len(raw)
        require(total <= MAX_TOTAL_BYTES, "archive exceeds total byte limit")
        privacy_check(name, raw)
        members[name] = raw

    def copy(name, path):
        add(name, bounded_bytes(path))

    first = runs / "fixed-remainder-selector-case0-20260928"
    repair = runs / "fixed-remainder-selector-case4-replay-20260928"
    old_hashes = read_json(first / "protocol.json")["source_sha256"]
    repair_protocol, repair_result = read_json(repair / "protocol.json"), read_json(repair / "result.json")
    new_hashes = repair_protocol["source_sha256"]
    require(repair_protocol["followup_kind"] == "existing_certificate_replay_only"
            and repair_protocol["no_solver_rerun"] is True and repair_result["no_solver_rerun"] is True,
            "repair must replay the existing certificate only")
    require(repair_result["source_sha256"] == new_hashes, "repair source declarations disagree")
    original_source = snapshot(first / "source", old_hashes)
    repaired_source = snapshot(repair / "source", new_hashes)
    require({name for name in old_hashes if old_hashes[name] != new_hashes[name]} == {
        "fixed_remainder/selector_proof.py", "fixed_remainder/test_selector.py"},
        "unexpected repair source change")
    for name in SOURCE_NAMES:
        require(sha(bounded_bytes(HERE.parent / name)) == new_hashes[name], "current reviewed source drift")
        add("original-source/" + name, original_source[name])
        add("source/" + name, repaired_source[name])
    copy("source/fixed_remainder/package.py", Path(__file__))
    copy("source/fixed_remainder/test_package.py", HERE / "test_package.py")
    for name in ("README.md", "SELECTOR-PROFILE.md", "STRUCTURAL-NOTE.md", "REVIEW.md"):
        copy("source/fixed_remainder/" + name, HERE / name)
    for name in ("ANALYTIC-NEXT.md", "NEXT-PROFILE.md"):
        copy("source/degree_six/" + name, HERE.parent / "degree_six" / name)
    license_path = next((parent / "LICENSE" for parent in HERE.parents if (parent / "LICENSE").is_file()), None)
    require(license_path is not None, "repository license missing")
    copy("LICENSE", license_path)
    auditor = runs / "independent-selector-formula-audit.py"
    require(file_sha(auditor) == FORMULA_AUDITOR, "formula auditor source drift")
    copy("auditors/independent-selector-formula-audit.py", auditor)
    copy("original-artifact-readback.json", runs / "independent-selector-artifact-readback-20260928.json")
    checker = read_json(runs / "degree-four-60s/lrat-trim-receipt.json")
    require(checker["source_commit"] == CHECKER_COMMIT and checker["source_sha256"] == CHECKER_SOURCE
            and checker["license_sha256"] == CHECKER_LICENSE, "checker provenance mismatch")
    require(file_sha(third_party / "lrat-trim.c") == CHECKER_SOURCE
            and file_sha(third_party / "LICENSE") == CHECKER_LICENSE
            and file_sha(third_party / "lrat-trim") == checker["binary_sha256"], "checker identity mismatch")
    for name in ("lrat-trim.c", "LICENSE"):
        copy("third-party/lrat-trim/" + name, third_party / name)
    check_run_files(repair, repair_result)
    records = []
    catalogue_raw = bounded_bytes(first / "catalogue.json")
    add("catalogue.json", catalogue_raw)
    for case in range(7):
        directory = runs / f"fixed-remainder-selector-case{case}-20260928"
        protocol, result = read_json(directory / "protocol.json"), read_json(directory / "result.json")
        metadata, columns = read_json(directory / "instance.json"), read_json(directory / "columns.json")
        require(protocol["case_index"] == case and protocol["profile"] == PROFILE
                and protocol["small_control"] is None and protocol["construct_only"] is False,
                "wrong selector case or profile")
        require(protocol["source_sha256"] == result["source_sha256"] == metadata["source_sha256"] == old_hashes,
                "original source declarations disagree")
        snapshot(directory / "source", old_hashes)
        check_run_files(directory, result)
        require(bounded_bytes(directory / "catalogue.json") == catalogue_raw, "catalogue drift between cases")
        require(tuple(columns["representative_pair"]) == PAIRS[case], "wrong deletion pair")
        check_stage(result["stages"]["solve"], 20)
        verified, verified_directory = (repair_result, repair) if case == 4 else (result, directory)
        require(verified["status"] == "selector_unsat_dual_verified"
                and verified["python_rup_verified"] is True and verified["lrat_trim_verified"] is True
                and verified["necessary_selector_formula_unsat"] is True
                and verified["ramsey_graph_found"] is False
                and verified["external_ramsey_bound_claim_made"] is False, "missing dual proof verification")
        check_stage(verified["stages"]["audit"], 0)
        check_stage(verified["stages"]["lrat-trim"], 20)
        require(verified["stages"]["lrat-trim"]["executable_sha256"] == checker["binary_sha256"],
                "different established checker binary")
        require("s VERIFIED" in (verified_directory / "lrat-trim.log").read_text().splitlines(),
                "established checker success marker missing")
        proof = verified["proof_verification"]
        require(proof["profile"] == PROFILE and proof["verified_unsatisfiable"] is True, "unverified proof result")
        prefix = f"selectors/case-{case}/"
        for name in ("instance.cnf", "proof.lrat", "instance.json", "columns.json", "protocol.json"):
            copy(prefix + name, directory / name)
        cnf_hash, proof_hash = sha(members[prefix + "instance.cnf"]), sha(members[prefix + "proof.lrat"])
        require(cnf_hash == metadata["cnf_sha256"] == proof["cnf_sha256"]
                and proof_hash == proof["proof_sha256"]
                and metadata["columns_sha256"] == sha(members[prefix + "columns.json"]), "certificate binding mismatch")
        if case == 4:
            require(result["status"] == "selector_unsat_unverified"
                    and repair_protocol["original_result_sha256"] == file_sha(directory / "result.json")
                    and repair_protocol["original_protocol_sha256"] == file_sha(directory / "protocol.json")
                    and repair_protocol["certificate_sha256"] == {"instance.cnf": cnf_hash, "proof.lrat": proof_hash},
                    "follow-up does not bind the unchanged original failed attempt")
            require(file_sha(repair / "instance.cnf") == cnf_hash and file_sha(repair / "proof.lrat") == proof_hash,
                    "repair certificate bytes differ")
        add(prefix + "original-run.json", json_bytes(public_record(result, file_sha(directory / "result.json"))))
        add(prefix + "verification.json", json_bytes(public_record(verified, file_sha(verified_directory / "result.json"))))
        records.append({"case": case, "deleted_pair": list(PAIRS[case]), "variables": metadata["variables"],
                        "clauses": metadata["clauses"], "cnf_sha256": cnf_hash, "proof_sha256": proof_hash,
                        "original_status": result["status"], "verification_source": "source" if case == 4 else "original-source",
                        "status": "selector_unsat_dual_verified"})
    copy("case-4-followup-protocol.json", repair / "protocol.json")
    cover = runs / "fixed-column-cover-20260928-r2/evidence"
    summary = read_json(cover / "summary.json")
    require(summary["status"] == "all_selected_cases_no_necessary_cover"
            and [item["case"] for item in summary["cases"]] == list(range(7)), "incomplete branch-tree evidence")
    require(all(old_hashes.get(name) == expected and file_sha(cover / "source" / name) == expected
                for name, expected in summary["source_sha256"].items()), "branch-tree source mismatch")
    require(file_sha(cover / "catalogue.json") == summary["catalogue_sha256"] == sha(catalogue_raw),
            "branch-tree catalogue mismatch")
    copy("branch-tree/summary.json", cover / "summary.json")
    for item in summary["cases"]:
        name = f"case-{item['case']}.json"
        require(item["artifact"] == name and item["status"] == "no_necessary_cover"
                and file_sha(cover / name) == item["artifact_sha256"], "branch-tree artifact mismatch")
        copy("branch-tree/" + name, cover / name)
    independent_path = runs / "fixed-remainder-independent-cover-20260928.json"
    independent = read_json(independent_path)
    require(independent["source_sha256"] == old_hashes["fixed_remainder/independent_cover.py"]
            and independent["all_seven_have_no_necessary_column_cover"] is True
            and len(independent["cases"]) == 7, "independent reproduction missing")
    copy("branch-tree/independent-result.json", independent_path)
    add("RESULT.json", json_bytes({
        "schema_version": 1, "profile": PROFILE, "cases": records,
        "claim": "No centre-covered triangle-free 40-vertex graph with independence number at most nine, "
                 "a degree-six centre, and remainder isomorphic to a two-vertex deletion of the stated 35-vertex graph exists.",
        "includes_maximal_triangle_free_graphs_with_this_centre_and_remainder": True,
        "all_33_vertex_ramsey_graphs_classified": False, "ramsey_number_settled": False,
        "novelty_claimed": False, "branch_tree_nodes": sum(item["search_nodes"] for item in summary["cases"]),
        "formula_reconstruction_evidence": "Independent review in source/fixed_remainder/REVIEW.md; "
            "the portable auditor independently regenerates every formula. original-artifact-readback.json is a hash/stage readback, not a formula execution record.",
        "source_snapshots": {"original-source": old_hashes, "source": new_hashes},
        "source_note": "The release attaches this fixed archive to its reviewed repository revision. "
                       "File hashes identify every included runtime and document; no prepublication Git commit is inferred.",
        "checker": {key: checker[key] for key in ("checker", "version", "source_repository", "source_commit",
                                                   "source_sha256", "license_sha256", "binary_sha256")},
        "algorithms": {"original_columns": "increasing-order independent-set enumeration",
                       "independent_columns": "pivoted Bron-Kerbosch on the complement",
                       "branch_tree": "dynamic required-row pivot with exhaustive children",
                       "selector_formula": "six distinct columns; row capacities and missed-eight-set pairs",
                       "proofs": "textual LRAT/RUP replay by Python and lrat-trim"},
    }))
    add("README.md", BUNDLE_README.encode())
    manifest = {"schema_version": 1, "archive_root": ARCHIVE_ROOT,
                "files": {name: sha(raw) for name, raw in sorted(members.items())},
                "file_bytes": {name: len(raw) for name, raw in sorted(members.items())}}
    add("MANIFEST.json", json_bytes(manifest))
    if check_only:
        return {"status": "admission_passed", "members": len(members),
                "uncompressed_member_bytes": total, "manifest_sha256": sha(members["MANIFEST.json"])}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        with gzip.GzipFile(fileobj=destination, filename="", mode="wb", mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, raw in sorted(members.items()):
                    entry = tarfile.TarInfo(ARCHIVE_ROOT + "/" + name)
                    entry.size, entry.mode, entry.mtime = len(raw), 0o644, 0
                    archive.addfile(entry, io.BytesIO(raw))
    digest = file_sha(output)
    with output.with_name(output.name + ".sha256").open("x") as destination:
        destination.write(digest + "  " + output.name + "\n")
    return {"archive": str(output), "sha256": digest, "bytes": output.stat().st_size,
            "members": len(members), "uncompressed_member_bytes": total,
            "current_source_sha256": {name: sha(raw) for name, raw in sorted(members.items())
                                      if name.startswith(("source/", "auditors/", "third-party/"))}}


def verify_manifest(bundle):
    manifest = read_json(bundle / "MANIFEST.json")
    require(set(manifest) == {"schema_version", "archive_root", "files", "file_bytes"}
            and manifest["schema_version"] == 1 and manifest["archive_root"] == ARCHIVE_ROOT, "unknown bundle manifest")
    files, sizes = manifest["files"], manifest["file_bytes"]
    require(isinstance(files, dict) and 0 < len(files) < MAX_MEMBERS and set(files) == set(sizes), "invalid file inventory")
    total = 0
    for name, expected in files.items():
        safe_name(name)
        require(isinstance(expected, str) and re.fullmatch("[0-9a-f]{64}", expected) is not None,
                "invalid file digest")
        path = bundle / name
        require(path.resolve().is_relative_to(bundle.resolve()), "member escapes bundle")
        raw = bounded_bytes(path)
        require(type(sizes[name]) is int and len(raw) == sizes[name] and sha(raw) == expected, "bundle file changed: " + name)
        privacy_check(name, raw)
        total += len(raw)
        require(total <= MAX_TOTAL_BYTES, "bundle exceeds total byte limit")
    actual = set()
    for path in bundle.rglob("*"):
        require(not path.is_symlink(), "symbolic link in extracted bundle")
        if path.is_file():
            actual.add(path.relative_to(bundle).as_posix())
            require(len(actual) <= MAX_MEMBERS, "too many extracted files")
    require(actual == set(files) | {"MANIFEST.json"}, "unlisted or missing extracted files")
    return {"files_checked": len(files), "bytes_checked": total, "manifest_sha256": file_sha(bundle / "MANIFEST.json")}


def proof_worker(cnf, proof, output):
    from selector_proof import verify as verify_proof
    result = verify_proof(cnf, proof, profile=PROFILE)
    with output.open("x") as destination:
        json.dump(result, destination, indent=2)
        destination.write("\n")


def tree_worker(bundle, output):
    sys.path.insert(0, str(bundle / "original-source/fixed_remainder"))
    from catalogue import ramsey_catalogue
    from column_cover import column_problem, replay_cover
    from independent_cover import reproduce
    from shared import Budget
    catalogue = read_json(bundle / "catalogue.json")
    require(ramsey_catalogue(budget=Budget(10)) == catalogue, "catalogue reconstruction mismatch")
    nodes = 0
    budget = Budget(30)
    for case in catalogue["cases"]:
        saved = read_json(bundle / f"branch-tree/case-{case['index']}.json")
        problem = column_problem(case["adjacency"], budget=budget)
        require(json.loads(json.dumps(problem)) == saved["problem"], "branch problem reconstruction mismatch")
        replay = replay_cover(problem, saved["result"], budget=budget)
        require(replay["replayed"] is True, "branch replay failed")
        nodes += replay["nodes_checked"]
    independent = reproduce()
    require(independent["all_seven_have_no_necessary_column_cover"] is True
            and independent["cases"] == read_json(bundle / "branch-tree/independent-result.json")["cases"],
            "independent enumeration or cover reproduction mismatch")
    result = {"catalogue_pair_maps_verified": catalogue["labelled_pairs"], "cases": len(catalogue["cases"]),
              "branch_nodes_checked": nodes, "independent_reproduction_matches": True}
    with output.open("x") as destination:
        json.dump(result, destination, indent=2)
        destination.write("\n")


def verify_bundle(bundle, output, lrat_trim):
    bundle, output = bundle.resolve(strict=True), output.resolve()
    require(Path(__file__).resolve() == bundle / "source/fixed_remainder/package.py",
            "run the verifier included in the extracted bundle")
    require(not output.is_relative_to(bundle), "verification output must be outside the input bundle")
    require(not output.exists(), "verification output directory must be new")
    checked = verify_manifest(bundle)
    from process import run_process
    checker = lrat_trim.resolve(strict=True)
    require(checker.is_file(), "lrat-trim executable is not a regular file")
    published = read_json(bundle / "RESULT.json")
    checker_digest = file_sha(checker)
    output.mkdir(parents=True, exist_ok=False)
    report = {"schema_version": 1, "status": "incomplete", "manifest": checked, "stages": {},
              "checker": {"sha256": checker_digest,
                          "requested_source_commit": published["checker"]["source_commit"],
                          "matches_original_recorded_binary": checker_digest == published["checker"]["binary_sha256"]}}

    def save():
        (output / "verification.json").write_bytes(json_bytes(report))

    def stage(name, argv, cpu, code, file_bytes=256 * 1024**2):
        record = run_process(argv, output / (name + ".log"), output / (name + "-stage.json"),
                             cpu_seconds=cpu, wall_seconds=cpu + 30, memory_mib=1024,
                             file_bytes=file_bytes)
        report["stages"][name] = record
        save()
        check_stage(record, code)

    save()
    stage("checker-version", [str(checker), "--version"], 5, 0)
    require((output / "checker-version.log").read_text().strip() == published["checker"]["version"]
            and report["stages"]["checker-version"]["executable_sha256"] == checker_digest,
            "checker version or binary identity mismatch")
    for case in range(7):
        directory = bundle / f"selectors/case-{case}"
        stage(f"case-{case}-formula", [sys.executable, "-B",
              str(bundle / "auditors/independent-selector-formula-audit.py"), str(directory),
              "--independent-source", str(bundle / "original-source/fixed_remainder/independent_cover.py")], 20, 0)
        formula = read_json(output / f"case-{case}-formula.log")
        require(formula["independent_formula_reconstruction_passed"] is True, "formula reconstruction failed")
        stage(f"case-{case}-python", [sys.executable, "-B", str(Path(__file__).resolve()), "_proof",
              str(directory / "instance.cnf"), str(directory / "proof.lrat"),
              str(output / f"case-{case}-python.json")], 90, 0)
        proof = read_json(output / f"case-{case}-python.json")
        require(proof["verified_unsatisfiable"] is True
                and proof["cnf_sha256"] == formula["cnf_sha256"] == published["cases"][case]["cnf_sha256"]
                and proof["proof_sha256"] == published["cases"][case]["proof_sha256"],
                "proof/formula replay mismatch")
        stage(f"case-{case}-lrat-trim", [str(checker), "--no-trim", str(directory / "instance.cnf"),
                                        str(directory / "proof.lrat")], 90, 20)
        require("s VERIFIED" in (output / f"case-{case}-lrat-trim.log").read_text().splitlines(),
                "established checker success marker missing")
        require(report["stages"][f"case-{case}-lrat-trim"]["executable_sha256"] == checker_digest,
                "checker binary changed during replay")
    stage("branch-evidence", [sys.executable, "-B", str(Path(__file__).resolve()), "_trees",
                              str(bundle), str(output / "branch-evidence.json")], 60, 0)
    report.update(status="all_seven_proofs_formulas_and_branch_evidence_replayed", solver_invoked=False,
                  cases_verified=7, branch_evidence=read_json(output / "branch-evidence.json"))
    save()
    return {"status": report["status"], "cases_verified": 7, "solver_invoked": False,
            "verification_sha256": file_sha(output / "verification.json"), "output": str(output)}


BUNDLE_README = r"""# Seven fixed-remainder exclusions for R(3,10)

Every triangle-free graph on 40 vertices with independence number at most
nine is excluded from the following finite family: a distinguished vertex
has six neighbours; each of the other 33 vertices has a neighbour among
those six; and the remaining 33-vertex graph is a two-vertex deletion of
the published 35-vertex circulant with differences ±{1,7,11,16}. This includes maximal
triangle-free graphs with that centre and remainder. It does not exclude
all degree-six cases, classify all 33-vertex Ramsey graphs, settle R(3,10),
or make a publication-priority claim.

The 595 deletion pairs are covered by seven representatives through
explicitly checked edge-and-nonedge preserving permutations. Each saved
CNF encodes necessary conditions on six attachment neighbourhoods. All
seven are UNSAT, with independent formula reconstruction, Python RUP
replay and lrat-trim verification. The separate branch trees contain
1,712 checked nodes. A second cover implementation uses Bron-Kerbosch on
the complement and shares no imports with the original search code.

The mathematical argument, references, exact limits and review are in
source/fixed_remainder/{README,STRUCTURAL-NOTE,SELECTOR-PROFILE,REVIEW}.md.
RESULT.json describes the scope and source identities. MANIFEST.json
hashes every other file. The archive has no original-machine executables,
absolute home-directory paths or process identifiers. Runtime sources,
CNFs, proofs, catalogue and branch records are exact copies. Public run
records omit local command paths and process identifiers; their original
digests are retained. The original private records were not changed.

Case four originally failed the one-million-character proof-line limit.
Its original-run.json preserves that unverified status. A reviewed change
allows selector deletion records up to 2 MiB, retaining all other limits
and proof semantics. The same certificate then passed both checkers.
case-4-followup-protocol.json binds that replay to the original bytes.
original-source/ contains the original runtime; source/ contains the
reviewed proof reader used by the portable command below. No solver rerun
was needed. The independent formula auditor is included as a separate
source file; the original artifact readback is not a formula-run record.

After checking the downloaded archive against its published SHA-256 and
extracting it, use Python 3.11 or newer on Linux or macOS, with a verified
build of the pinned lrat-trim source:

```sh
cd r310-fixed-remainder-proof
python3 -B source/fixed_remainder/package.py verify . \
  --lrat-trim /path/to/verified/lrat-trim --output ../r310-replay
```

The output directory must be new and outside the extracted bundle. The
command checks every file hash and the supplied checker's version and
binary identity, independently reconstructs all seven formulas,
replays each proof with both implementations, verifies all catalogue maps
and branch trees, and reruns the independent finite cover calculation.
It never calls a SAT solver. Every child has a CPU limit, a wall deadline,
a one-GiB memory threshold and a file-size limit; memory monitoring is
cooperative on macOS. Failed or interrupted checks remain incomplete.
Success is recorded in the new directory's verification.json as
`all_seven_proofs_formulas_and_branch_evidence_replayed`.

If a verified checker build is unavailable, first validate the extracted
files, then compile the included C11 source under the host's native-build
controls. Where direct compiler invocation is permitted, for example:

```sh
python3 -B source/fixed_remainder/package.py check-files .
mkdir ../r310-checker
cc -std=c11 -O2 -Wall -Wextra third-party/lrat-trim/lrat-trim.c \
  -o ../r310-checker/lrat-trim
```

Then pass `--lrat-trim ../r310-checker/lrat-trim` to the verifier. The build
is a separate host-managed operation: compiler subprocesses are outside
the verifier's direct-child supervision. The verifier never launches a
compiler. Its receipt records the invoked executable digest and whether
it matches the original recorded checker binary; a different compiler or
platform can produce different executable bytes from the pinned source.

The third-party checker is arminbiere/lrat-trim at commit
b30f400f4ee5c32b77ee566a7c006081b521534f, with its own included MIT license.
The laboratory source uses the repository's included MIT license. Its
recorded original executable digest is provenance. Verification trusts the
saved proof and the independently supplied checker, not the SAT solver.
"""


def apply_build_limits():
    for kind, requested in ((resource.RLIMIT_CPU, (59, 60)),
                            (resource.RLIMIT_FSIZE, (MAX_TOTAL_BYTES, MAX_TOTAL_BYTES))):
        inherited = resource.getrlimit(kind)
        limits = tuple(cap if value == resource.RLIM_INFINITY else min(value, cap)
                       for value, cap in zip(inherited, requested))
        resource.setrlimit(kind, limits)


def main():
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("build", help="build from the retained private experiment records")
    pack.add_argument("runs", type=Path)
    pack.add_argument("third_party", type=Path)
    pack.add_argument("output", type=Path)
    pack.add_argument("--check-only", action="store_true", help="validate all inputs without writing an archive")
    replay = commands.add_parser("verify", help="replay a public extracted archive without a solver")
    replay.add_argument("bundle", type=Path)
    replay.add_argument("--output", type=Path, required=True)
    replay.add_argument("--lrat-trim", type=Path, required=True)
    files = commands.add_parser("check-files", help="check only an extracted archive's manifest and file hashes")
    files.add_argument("bundle", type=Path)
    proof = commands.add_parser("_proof", help="internal bounded proof worker")
    proof.add_argument("cnf", type=Path)
    proof.add_argument("proof", type=Path)
    proof.add_argument("output", type=Path)
    trees = commands.add_parser("_trees", help="internal bounded branch-evidence worker")
    trees.add_argument("bundle", type=Path)
    trees.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        apply_build_limits()
        print(json.dumps(build(args.runs, args.third_party, args.output, check_only=args.check_only), indent=2))
    elif args.command == "verify":
        print(json.dumps(verify_bundle(args.bundle, args.output, args.lrat_trim), indent=2))
    elif args.command == "check-files":
        print(json.dumps(verify_manifest(args.bundle), indent=2))
    elif args.command == "_proof":
        proof_worker(args.cnf, args.proof, args.output)
    else:
        tree_worker(args.bundle, args.output)


if __name__ == "__main__":
    main()
