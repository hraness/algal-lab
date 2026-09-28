import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildEvaluationEvidence, type EvaluationEvidence, type EvaluationOutcome, type EvaluationOutcomeCase } from "@hraness/algal";
import { digest } from "./artifacts";
import {
  assessClaim, buildClaim, buildClaimsLedger, CLAIM_CATEGORIES, evidenceSufficiency, parseClaim,
  parseClaimsLedger, promotableTo, recordsEvidenceResolver, verifyClaimsLedger, verifyStudyClaims, writeStudyClaims,
  type Claim, type ClaimCategory, type ClaimCitation,
} from "./claims";
import { json } from "./contracts";
import { writeStudyEvidence } from "./evidence";
import { runStudy } from "./study";

function kase(id: string, outcome: EvaluationOutcomeCase["outcome"]): EvaluationOutcomeCase {
  return { id, group: "r1:isolated", outcome, passed: outcome === "complete", score: outcome === "complete" ? 0.8 : 0, receipt: null, feedback: null };
}
function outcomeOf(cases: EvaluationOutcomeCase[]): EvaluationOutcome {
  return { passed: cases.filter((c) => c.passed).length, total: cases.length, score: cases.length ? cases.reduce((sum, c) => sum + c.score, 0) / cases.length : 0, cases };
}
/** A minimal but fully valid `algal.evaluation-evidence.v1` record, varied by tag. */
function record(tag: string, claimCategory: ClaimCategory, holdout: EvaluationOutcomeCase[]): EvaluationEvidence {
  return buildEvaluationEvidence({
    contract: "algal.evaluation-evidence.v1",
    baseArtifact: digest({ base: tag }), candidateArtifact: digest({ candidate: tag }),
    dataset: { digest: digest({ dataset: tag }), groups: ["r1:isolated"], splitPolicy: "test", labelProvenance: "test", redactionPolicy: "test" },
    evaluator: { scorerDigest: digest({ scorer: tag }), runtimeDigest: digest({ runtime: tag }), routeDigest: null },
    usage: { modelCalls: 1, tokensIn: 0, tokensOut: 0, units: "test-agent-effects" },
    charges: { reserved: 10, settled: 4, unit: "algal-work-units" },
    outcomes: { train: outcomeOf([kase(`${tag}-t0`, "complete")]), validation: outcomeOf([]), holdout: outcomeOf(holdout) },
    independentReview: { status: "not-reviewed", reviewer: null, notes: null },
    claimCategory,
    limitations: ["a synthetic test record"],
  });
}
const sorted = (citations: ClaimCitation[]) => [...citations].sort((a, b) => (a.evidence < b.evidence ? -1 : 1));
/** The citation reference is the record's content address: digest of the whole
 * stored object, matching both `ArtifactStore` naming and `envelope.records`. */
const ref = (r: EvaluationEvidence) => digest(r);
const replaySufficient = () => record("a", "replay", [kase("a-h0", "complete"), kase("a-h1", "failed")]);

test("sufficient replay evidence supports a replay claim but cannot carry a stronger one", async () => {
  const evidence = replaySufficient();
  const resolve = recordsEvidenceResolver([evidence]);
  const replay = await buildClaim({ id: "replay-consistency", statement: "the archived run replays consistently", asked: "replay",
    citations: [{ evidence: ref(evidence), role: "support" }] }, resolve);
  expect(replay.outcome).toBe("supported");
  expect(replay.granted).toBe("replay");
  expect(promotableTo(replay, "replay")).toBe(true);
  expect(promotableTo(replay, "qualified-boundary")).toBe(false);
  expect(promotableTo(replay, "activation")).toBe(false);
  // Asking beyond what the evidence attests retains the claim as
  // insufficient-evidence with the partial grant recorded — never promoted.
  const reach = await buildClaim({ id: "effectiveness-claim", statement: "the approach is effective", asked: "effectiveness",
    citations: [{ evidence: ref(evidence), role: "support" }] }, resolve);
  expect(reach.outcome).toBe("insufficient-evidence");
  expect(reach.granted).toBe("replay");
  for (const category of CLAIM_CATEGORIES) expect(promotableTo(reach, category)).toBe(false);
});

test("uncertain, failed, missing, and contradicting evidence all retain first-class insufficient results", async () => {
  const uncertain = record("u", "replay", [kase("u-h0", "uncertain")]);
  const failed = record("f", "replay", [kase("f-h0", "failed")]);
  const empty = record("e", "replay", []);
  const support = replaySufficient();
  const contradict = record("c", "replay", [kase("c-h0", "complete")]);
  expect(evidenceSufficiency(uncertain)).toBe("uncertain");
  expect(evidenceSufficiency(failed)).toBe("insufficient");
  expect(evidenceSufficiency(empty)).toBe("insufficient");
  const resolve = recordsEvidenceResolver([uncertain, failed, empty, support, contradict]);
  const phantom = digest({ absent: true });
  const drafts = [
    { id: "uncertain-run", statement: "s", asked: "replay", citations: [{ evidence: ref(uncertain), role: "support" as const }] },
    { id: "failed-run", statement: "s", asked: "replay", citations: [{ evidence: ref(failed), role: "support" as const }] },
    { id: "empty-run", statement: "s", asked: "replay", citations: [{ evidence: ref(empty), role: "support" as const }] },
    { id: "missing-record", statement: "s", asked: "replay", citations: [{ evidence: phantom, role: "support" as const }] },
    { id: "unattested-uncited", statement: "s", asked: "replay", citations: [] },
  ];
  for (const draft of drafts) {
    const claim = await buildClaim(draft, resolve);
    expect(claim.outcome).toBe("insufficient-evidence");
    expect(claim.granted).toBeNull();
    expect(claim.citations).toEqual(draft.citations); // citations stay on the record even when they resolve to nothing
    for (const category of CLAIM_CATEGORIES) expect(promotableTo(claim, category)).toBe(false);
  }
  // One sufficient contradictory citation defeats the claim outright.
  const defeated = await buildClaim({ id: "defeated", statement: "s", asked: "replay",
    citations: sorted([{ evidence: ref(support), role: "support" }, { evidence: ref(contradict), role: "contradict" }]) }, resolve);
  expect(defeated.outcome).toBe("contradicted");
  expect(defeated.granted).toBeNull();
  for (const category of CLAIM_CATEGORIES) expect(promotableTo(defeated, category)).toBe(false);
  // A contradictory citation that resolves to nothing cannot contradict.
  const unresolvableContradict = await buildClaim({ id: "weak-contradict", statement: "s", asked: "replay",
    citations: sorted([{ evidence: ref(support), role: "support" }, { evidence: phantom, role: "contradict" }]) }, resolve);
  expect(unresolvableContradict.outcome).toBe("supported");
});

test("the granted ceiling is the strongest cited record and never exceeds the ask", async () => {
  const replayEvidence = replaySufficient();
  const mechanismEvidence = record("m", "mechanism", [kase("m-h0", "complete")]);
  const resolve = recordsEvidenceResolver([replayEvidence, mechanismEvidence]);
  const mechanism = await buildClaim({ id: "why-it-works", statement: "s", asked: "mechanism",
    citations: sorted([{ evidence: ref(replayEvidence), role: "support" }, { evidence: ref(mechanismEvidence), role: "support" }]) }, resolve);
  expect(mechanism.outcome).toBe("supported");
  expect(mechanism.granted).toBe("mechanism");
  // Stronger-category evidence can satisfy a weaker ask.
  const weak = await buildClaim({ id: "weak-ask", statement: "s", asked: "replay",
    citations: [{ evidence: ref(mechanismEvidence), role: "support" }] }, resolve);
  expect(weak.outcome).toBe("supported");
  expect(weak.granted).toBe("replay");
  // Asking past the ceiling retains the claim at the ceiling, still insufficient.
  const overreach = await buildClaim({ id: "activation-claim", statement: "s", asked: "activation",
    citations: [{ evidence: ref(mechanismEvidence), role: "support" }] }, resolve);
  expect(overreach.outcome).toBe("insufficient-evidence");
  expect(overreach.granted).toBe("mechanism");
  expect(promotableTo(overreach, "activation")).toBe(false);
  // assessClaim agrees with buildClaim's recorded outcome.
  expect(await assessClaim({ id: "x", statement: "s", asked: "activation", citations: overreach.citations }, resolve)).toEqual({ outcome: "insufficient-evidence", granted: "mechanism" });
});

test("a ledger round-trips byte-for-byte and verification re-derives every outcome", async () => {
  const support = replaySufficient();
  const mechanismEvidence = record("m", "mechanism", [kase("m-h0", "complete")]);
  const uncertain = record("u", "replay", [kase("u-h0", "uncertain")]);
  const resolve = recordsEvidenceResolver([support, mechanismEvidence, uncertain]);
  const claims = [
    await buildClaim({ id: "b-overreach", statement: "s", asked: "effectiveness", citations: [{ evidence: ref(support), role: "support" }] }, resolve),
    await buildClaim({ id: "a-supported", statement: "s", asked: "replay", citations: [{ evidence: ref(support), role: "support" }] }, resolve),
    await buildClaim({ id: "c-uncertain", statement: "s", asked: "replay", citations: [{ evidence: ref(uncertain), role: "support" }] }, resolve),
    await buildClaim({ id: "d-mechanism", statement: "s", asked: "mechanism", citations: [{ evidence: ref(mechanismEvidence), role: "support" }] }, resolve),
  ];
  const ledger = buildClaimsLedger(claims);
  expect(ledger.claims.map((claim) => claim.id)).toEqual(["a-supported", "b-overreach", "c-uncertain", "d-mechanism"]);
  const reparsed = parseClaimsLedger(JSON.parse(JSON.stringify(ledger)));
  expect(reparsed).toEqual(ledger);
  expect(await verifyClaimsLedger(json(ledger), resolve)).toEqual({ ok: true, claims: 4, insufficient: 2, contradicted: 0 });
  // Each claim also round-trips on its own.
  for (const claim of claims) expect(parseClaim(JSON.parse(JSON.stringify(claim)))).toEqual(claim);

  // Forge a promotion: re-digest an insufficient claim as supported. The ledger
  // still parses — but verification re-derives the outcome and refuses it.
  const overreach = claims[0]!;
  const forgedBody = { contract: overreach.contract, id: overreach.id, statement: overreach.statement, asked: overreach.asked,
    citations: overreach.citations, outcome: "supported" as const, granted: overreach.asked };
  const forged: Claim = { ...forgedBody, digest: digest(forgedBody) };
  const forgedLedger = buildClaimsLedger([forged]);
  expect(() => parseClaimsLedger(json(forgedLedger))).not.toThrow();
  await expect(verifyClaimsLedger(json(forgedLedger), resolve)).rejects.toThrow(/differs from the cited evidence/);

  // Mutating the body without recomputing the digest fails earlier, at parse.
  const mutated = { ...claims[1]!, outcome: "insufficient-evidence" as const, granted: null };
  expect(() => parseClaim(mutated)).toThrow(/digest/);
  // Verification is honest when evidence is absent too: a claim recorded as
  // insufficient stays insufficient under a resolver that knows nothing.
  expect(await verifyClaimsLedger(json(buildClaimsLedger([claims[2]!])), recordsEvidenceResolver([]))).toEqual({ ok: true, claims: 1, insufficient: 1, contradicted: 0 });
});

test("claims admission rejects unknown keys, bad identities, and unsorted citations", async () => {
  const evidence = replaySufficient();
  const draft = { id: "ok-claim", statement: "s", asked: "replay", citations: [{ evidence: ref(evidence), role: "support" }] };
  await expect(buildClaim({ ...draft, extra: 1 }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/unknown field/);
  await expect(buildClaim({ ...draft, id: "Bad_Id" }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/claim id/);
  await expect(buildClaim({ ...draft, statement: "x".repeat(2049) }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/statement/);
  await expect(buildClaim({ ...draft, asked: "truth" }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/category/);
  await expect(buildClaim({ ...draft, citations: [{ evidence: ref(evidence), role: "cites" }] }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/role/);
  await expect(buildClaim({ ...draft, citations: [{ evidence: ref(evidence), role: "support", note: "x" }] }, recordsEvidenceResolver([evidence]))).rejects.toThrow(/unknown field/);
  const other = record("z", "replay", [kase("z-h0", "complete")]);
  const reversed = [{ evidence: ref(other), role: "support" }, { evidence: ref(evidence), role: "support" }]
    .sort((a, b) => (a.evidence > b.evidence ? -1 : 1)); // descending on purpose
  await expect(buildClaim({ ...draft, citations: reversed }, recordsEvidenceResolver([evidence, other]))).rejects.toThrow(/sorted/);
  await expect(buildClaim({ ...draft, citations: [{ evidence: ref(evidence), role: "support" }, { evidence: ref(evidence), role: "support" }] },
    recordsEvidenceResolver([evidence]))).rejects.toThrow(/sorted|unique/);
  expect(() => parseClaim({ contract: "algal.lab.claim.v1", extra: 1 })).toThrow(/unknown field/);
  expect(() => parseClaimsLedger({ contract: "algal.lab.claims-ledger.v1", extra: 1 })).toThrow(/unknown field/);
  const claim = await buildClaim(draft, recordsEvidenceResolver([evidence]));
  expect(() => parseClaimsLedger({ contract: "algal.lab.claims-ledger.v1", claims: [json(claim), json(claim)], digest: "x" })).toThrow(/sorted|unique/);
  // Digest binding is real: a claim whose digest was taken from a different body fails.
  const foreign = await buildClaim({ ...draft, id: "other-claim" }, recordsEvidenceResolver([evidence]));
  expect(() => parseClaim({ ...claim, digest: foreign.digest })).toThrow(/digest/);
});

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });

test("a claims ledger over a real study cites archived evidence and retains the insufficient ask", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-claims-test-"));
  roots.push(root);
  const directory = join(root, "run");
  await runStudy({ contract: "algal.lab.study.v1", name: "claims", replicateSeeds: [7], researchers: 2, rounds: 2,
    nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101] }, directory);
  const envelope = await writeStudyEvidence(directory);
  const reference = envelope.records[0]!;
  const drafts = { drafts: [
    { id: "a-replay", statement: "the archived run's receipts and measurements replay consistently", asked: "replay",
      citations: [{ evidence: reference, role: "support" }] },
    { id: "b-effectiveness", statement: "shared artifacts improve resilience on real networks", asked: "effectiveness",
      citations: [{ evidence: reference, role: "support" }] },
    { id: "c-absent", statement: "backed by a record that is not in this archive", asked: "replay",
      citations: [{ evidence: digest({ absent: "citation" }), role: "support" }] },
  ]};
  const draftsFile = join(root, "drafts.json");
  await writeFile(draftsFile, JSON.stringify(drafts));
  const ledger = await writeStudyClaims(directory, draftsFile);
  const byId = new Map(ledger.claims.map((claim) => [claim.id, claim]));
  expect(byId.get("a-replay")).toMatchObject({ outcome: "supported", granted: "replay" });
  // Study evidence is replay-grade only: the effectiveness ask is retained as
  // insufficient-evidence with its replay-grade partial grant, not promoted.
  expect(byId.get("b-effectiveness")).toMatchObject({ outcome: "insufficient-evidence", granted: "replay" });
  expect(byId.get("c-absent")).toMatchObject({ outcome: "insufficient-evidence", granted: null });
  expect(await verifyStudyClaims(directory)).toEqual({ ok: true, claims: 3, insufficient: 2, contradicted: 0, claimsDigest: ledger.digest });
  await expect(writeStudyClaims(directory, draftsFile)).rejects.toThrow();
}, 30000);
