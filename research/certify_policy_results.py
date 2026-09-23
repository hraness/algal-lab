"""Certify the 64 selected tree outputs in a frozen policy-spike heldout report.

Usage: python3 research/certify_policy_results.py heldout.json
Read-only, bounded to 16 MiB; emits one JSON certificate bundle to stdout.
This checks selected tree inputs and scores, not other arms or policy provenance.
"""
from fractions import Fraction
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import sys

if __package__:
    from . import tree_certificate as certifier
else:
    import tree_certificate as certifier

MAX_BYTES = 16 * 1024 * 1024
REGIMES = {"primary-tree": (8, 3), "primary-unicyclic": None, "transfer-tree": (10, 4), "transfer-bicyclic": None}
REPORT_FIELDS = set("contract protocolDigest sourceDigests selectionDigest selectedPolicy success primaryContrasts summary maxOracleDiscrepancy objectiveSelectionEvaluations outputMeasurementEvaluations independentChampionChecks elapsedMs results limits".split())
ROW_FIELDS = set("key seed regime environment ceiling arms".split())
RESULT_FIELDS = set("graph score evaluations duplicateProposals unchangedMutations acceptedImprovements acceptedWorse failures initialScore bestByEvaluation".split())
ARM_NAMES = set("selected random-search random-hill star-hill annealing fixed-pair fixed-reliable selected-zero-search star-zero-search".split())


def _selected_rows(value):
    report = certifier._object(value, REPORT_FIELDS, "heldout report")
    if report["contract"] != "algal.lab.policy-spike-heldout.v1":
        raise ValueError("unsupported heldout report contract")
    rows = report["results"]
    if type(rows) is not list or len(rows) != 128:
        raise ValueError("heldout report requires exactly 128 rows")
    seeds = {regime: set() for regime in REGIMES}
    selected = []
    for value in rows:
        row = certifier._object(value, ROW_FIELDS, "heldout row")
        regime = row["regime"]
        if type(regime) is not str or regime not in REGIMES:
            raise ValueError("unknown heldout regime")
        seed = certifier._integer(row["seed"], 0, 0xffffffff, "heldout seed")
        if row["key"] != f"{regime}:{seed}" or seed in seeds[regime]:
            raise ValueError("noncanonical or duplicate heldout key/seed")
        seeds[regime].add(seed)
        if REGIMES[regime] is not None:
            selected.append(row)
    reference = seeds["primary-tree"]
    if len(reference) != 32 or any(entries != reference for entries in seeds.values()):
        raise ValueError("each regime requires the same 32 unique environment seeds")
    return sorted(selected, key=lambda row: (row["regime"], row["seed"]))


def _certify_row(row):
    nodes, steps = REGIMES[row["regime"]]
    arms = certifier._object(row["arms"], ARM_NAMES, "heldout arms")
    arm = certifier._object(arms["selected"], {"result", "objectiveSelectionEvaluations", "measurementEvaluations"}, "selected arm")
    result = certifier._object(arm["result"], RESULT_FIELDS, "selected result")
    score = result["score"]
    if type(score) not in (int, float) or not 0 <= score <= 1 or not math.isfinite(score):
        raise ValueError("selected score must be finite and in [0,1]")
    certificate = certifier.certify({"graph": result["graph"], "environment": row["environment"], "steps": steps})
    if certificate["input"]["graph"]["nodes"] != nodes:
        raise ValueError("tree graph node budget differs from its declared regime")
    if abs(float(Fraction(certificate["candidateAuc"])) - score) > 2e-14:
        raise ValueError("stored selected score differs from the exact candidate AUC")
    return {"key": row["key"], "seed": row["seed"], "regime": row["regime"],
            "storedScoreDescriptive": score, "certificate": certificate}


def certify_report(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("heldout input exceeds 16 MiB")
    try:
        report = json.loads(raw.decode("utf-8"), object_pairs_hook=certifier._unique_object, parse_constant=certifier._reject_constant)
    except RecursionError:
        raise ValueError("heldout JSON nesting exceeds the parser limit") from None
    rows = [_certify_row(row) for row in _selected_rows(report)]
    if len(rows) != 64:
        raise ArithmeticError("selected tree panel must contain exactly 64 certificates")
    regrets = [Fraction(row["certificate"]["additiveRegretUpperBound"]) for row in rows]
    summarize = lambda value: {"exactFraction": str(value), "descriptiveApproximation": float(value)}
    digest = lambda data: "sha256:" + sha256(data).hexdigest()
    return {"contract": "algal.lab.policy-tree-certificates.v1",
            "sourceDigests": {"rawHeldoutInput": digest(raw), "treeCertifier": digest(Path(certifier.__file__).read_bytes()), "reportCertifier": digest(Path(__file__).read_bytes())},
            "certificates": len(rows), "certifiedOptimal": sum(row["certificate"]["status"] == "optimal" for row in rows),
            "meanAdditiveRegretUpperBound": summarize(sum(regrets) / len(regrets)),
            "maximumAdditiveRegretUpperBound": summarize(max(regrets)), "rows": rows,
            "scope": "Only the selected policy's primary-tree and transfer-tree outputs are certified. Other arms, summary metadata, seed-to-environment generation, and policy provenance are not verified by this command.",
            "interpretation": "Positive regret bounds do not prove suboptimality. Approximate numbers are descriptive only. This post-selection certification performs no proposal generation or tuning."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("heldout", help="Frozen heldout.json report, at most 16 MiB")
    args = parser.parse_args()
    try:
        result = certify_report(args.heldout)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"policy tree certificates: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
