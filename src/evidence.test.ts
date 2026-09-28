import { afterEach, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseEvaluationEvidence, type EvaluationEvidence, type Executor } from "@hraness/algal";
import { ArtifactStore, digest, readJsonFile, sourceIdentities } from "./artifacts";
import { ALGAL_REVISION, CONDITIONS, json, object } from "./contracts";
import { admitStudyView, parseStudyEvidence, studyEvidence, verifyStudyEvidence, writeStudyEvidence } from "./evidence";
import { researchManifest } from "./researcher";
import { runStudy, type Attempt, type StudyReport } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });
async function location() {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-evidence-test-"));
  roots.push(root);
  return join(root, "run");
}
const protocol = {
  contract: "algal.lab.study.v1", name: "evidence", replicateSeeds: [7], researchers: 2, rounds: 3,
  nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101],
};
const protocolV2 = {
  contract: "algal.lab.study.v2", name: "evidence-v2", replicateSeeds: [7, 23], researchers: 2, rounds: 2,
  nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101],
  primedDesigns: 2, counterbalance: true, transferRegimes: [{ nodes: 7, edges: 9, failureSteps: 2 }],
};

async function recordOf(directory: string): Promise<{ record: EvaluationEvidence; envelopeDigest: string }> {
  const file = object(await readJsonFile(join(directory, "evidence.json")), ["envelope", "digest"], "evidence file");
  const envelope = parseStudyEvidence(file.envelope);
  expect(String(envelope.digest)).toBe(String(file.digest));
  const record = parseEvaluationEvidence(await new ArtifactStore(directory).get(envelope.records[0]!));
  return { record, envelopeDigest: String(envelope.digest) };
}

test("a completed study projects to an evaluation-evidence record that verifies against the shared contract", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const envelope = await writeStudyEvidence(directory);
  expect(envelope.records).toHaveLength(1);
  expect(envelope.reportDigest).toBe(digest(report));
  const { record } = await recordOf(directory);
  expect(record.contract).toBe("algal.evaluation-evidence.v1");
  expect(record.claimCategory).toBe("replay");
  expect(record.independentReview).toEqual({ status: "not-reviewed", reviewer: null, notes: null });
  // train = every discovery attempt; v1 has no validation split; holdout = frozen designs.
  expect(record.outcomes.train.total).toBe(18);
  expect(record.outcomes.train.cases.every((c) => c.outcome === "complete" && c.passed)).toBe(true);
  expect(record.outcomes.validation.total).toBe(0);
  expect(record.limitations.some((line) => line.includes("no validation split"))).toBe(true);
  // Holdout cases are exactly the designs the archived evaluation batches list.
  const store = new ArtifactStore(directory);
  const attempts = new Map(await Promise.all(report.attempts.map(async (id) => [id, await store.get(id) as Attempt] as const)));
  let designs = 0;
  for (const summary of report.summaries) {
    for (const reference of [summary.evaluation, ...summary.transfers.map((t) => t.evaluation)]) {
      const batch = object(await store.get(reference), ["contract", "instrumentDigest", "portfolioDigest", "holdoutSeeds", "designs"], "evaluation batch");
      designs += (batch.designs as unknown[]).length;
    }
  }
  expect(designs).toBeGreaterThan(0);
  expect(record.outcomes.holdout.total).toBe(designs);
  expect(record.outcomes.holdout.cases.every((c) => c.outcome === "complete")).toBe(true);
  // Groups are the replicate/condition cells, sorted and unique.
  expect(record.dataset.groups).toEqual(["r7:isolated", "r7:shared-artifacts", "r7:shared-artifacts-and-messages"]);
  expect(String(record.dataset.digest)).toBe(digest(report.protocol));
  expect(String(record.baseArtifact)).toBe(report.instrumentDigest);
  expect(String(record.evaluator.scorerDigest)).toBe(report.applicationDigest);
  expect(record.evaluator.routeDigest).toBeNull();
  expect(record.usage.units).toBe("scripted-agent-effects");
  expect(record.usage.modelCalls).toBe([...attempts.values()].reduce((sum, attempt) => sum + attempt.receipt.work.agentCalls, 0));
  expect(record.charges.unit).toBe("algal-work-units");
  expect(record.charges.reserved).toBe(18 * researchManifest.budgets.maxWork);
  expect(record.charges.settled).toBeGreaterThan(0);
  expect(record.charges.settled).toBeLessThanOrEqual(record.charges.reserved);
  // Every case receipt binds the attempt's actual run receipt.
  for (const testCase of record.outcomes.train.cases) {
    expect(testCase.receipt).toBe(attempts.get(testCase.id)!.receipt.digest);
    expect(CONDITIONS.some((name) => name === testCase.group.slice(testCase.group.indexOf(":") + 1))).toBe(true);
  }
  expect(await verifyStudyEvidence(directory)).toEqual({ ok: true, records: 1, cases: 18 + designs, evidenceDigest: envelope.digest });
  // A second projection is byte-identical, and the evidence file cannot be overwritten.
  await expect(writeStudyEvidence(directory)).rejects.toThrow();
}, 30000);

test("v2 studies map primed and discovery attempts to train and transfer proposals to validation", async () => {
  const directory = await location();
  const report = await runStudy(protocolV2, directory);
  await writeStudyEvidence(directory);
  const { record } = await recordOf(directory);
  // 2 replicates × 3 conditions × (4 primed + 4 discovery) train; 2 transfer slots per cell.
  expect(record.outcomes.train.total).toBe(48);
  expect(record.outcomes.validation.total).toBe(12);
  const transfers = report.summaries.reduce((sum, s) => sum + s.transfers.reduce((n, t) => n + t.uniqueDesigns, 0), 0);
  const primary = report.summaries.reduce((sum, s) => sum + s.uniqueDesigns, 0);
  expect(record.outcomes.holdout.total).toBe(primary + transfers);
  expect(record.outcomes.train.cases.filter((c) => c.feedback === "phase:primed")).toHaveLength(24);
  expect(record.outcomes.validation.cases.every((c) => c.feedback === "phase:transfer")).toBe(true);
  expect(record.outcomes.holdout.cases.filter((c) => c.feedback === "scope:transfer-0")).toHaveLength(transfers);
  expect(record.dataset.groups).toHaveLength(6);
  expect([...record.dataset.groups].sort()).toEqual(record.dataset.groups);
  expect(record.limitations.some((line) => line.includes("host-primed"))).toBe(true);
  expect(record.limitations.some((line) => line.includes("not an independently labeled validation"))).toBe(true);
  expect((await verifyStudyEvidence(directory)).ok).toBe(true);
}, 30000);

test("evidence digests bind record bytes: tampering, drift, and unknown keys all fail closed", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  await writeStudyEvidence(directory);
  const { record } = await recordOf(directory);
  const reparsed = parseEvaluationEvidence(JSON.parse(JSON.stringify(record)));
  expect(reparsed).toEqual(record);
  // A mutated field without a recomputed digest fails the signature check.
  const changed = json({ ...record, limitations: ["x"] });
  expect(() => parseEvaluationEvidence(changed)).toThrow(/digest/);
  // Even with an honestly recomputed digest, unknown keys and closed-schema drift reject.
  const withKey = { ...record, extra: 1, digest: digest({ ...record, extra: 1 }) };
  expect(() => parseEvaluationEvidence(withKey)).toThrow(/unknown/);
  const reordered = { ...record, limitations: [...record.limitations].reverse(), digest: digest({ ...record, limitations: [...record.limitations].reverse() }) };
  expect(() => parseEvaluationEvidence(reordered)).toThrow(/sorted|differ/);
  // Rewrite evidence.json with a forged envelope whose own digest is
  // consistent but whose report binding points elsewhere: verification must
  // catch that the envelope does not bind this archive's report.
  const file = object(await readJsonFile(join(directory, "evidence.json")), ["envelope", "digest"], "evidence file");
  const env = file.envelope as Record<string, unknown>;
  const forgedBody = { contract: env.contract, reportDigest: digest(report.protocol), backend: env.backend,
    instrumentDigest: env.instrumentDigest, applicationDigest: env.applicationDigest, records: env.records };
  const forged = { ...forgedBody, digest: digest(forgedBody) };
  await writeFile(join(directory, "evidence.json"), JSON.stringify({ envelope: forged, digest: forged.digest }));
  await expect(verifyStudyEvidence(directory)).rejects.toThrow(/binds a different report/);
});

test("failed attempts are retained as failed cases and stay verifiable", async () => {
  const directory = await location();
  const executor: Executor = { id: "failing-fixture", execute: async () => { throw new Error("provider down"); } };
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor });
  const envelope = await writeStudyEvidence(directory);
  const { record } = await recordOf(directory);
  expect(record.outcomes.train.total).toBe(6);
  expect(record.outcomes.train.cases.every((c) => c.outcome === "failed" && !c.passed && c.score === 0)).toBe(true);
  expect(record.outcomes.train.cases.every((c) => c.feedback!.includes("provider down"))).toBe(true);
  expect(record.outcomes.holdout.total).toBe(0);
  expect(record.limitations.some((line) => line.includes("empty portfolios"))).toBe(true);
  expect((await verifyStudyEvidence(directory)).cases).toBe(6);
  expect(envelope.reportDigest).toBe(digest(report));
});

test("admitStudyView rejects foreign and drifted reports before any projection", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const admitted = admitStudyView(json(report));
  expect(admitted.attempts).toHaveLength(18);
  expect(() => admitStudyView({ ...report, extra: 1 })).toThrow(/unknown field/);
  expect(() => admitStudyView({ ...report, contract: "algal.lab.report.v1" })).toThrow(/identity or revision/);
  const drifted = JSON.parse(JSON.stringify(report)) as StudyReport;
  drifted.summaries[0]!.portfolioDigest = "sha256:" + "0".repeat(64);
  // A drifted portfolio digest still admits structurally, but the projection then
  // fails because the evaluation batch does not bind that portfolio.
  const store = new ArtifactStore(directory);
  await expect(studyEvidence(drifted, store)).rejects.toThrow(/does not bind its portfolio/);
});

/** A synthetic report over the largest legal protocol: 8 replicate seeds times
 * 3 conditions times (1 primary + 2 transfer) portfolios = 72 distinct
 * portfolio digests, the count that overflowed the old fixed bound. */
async function maximalReport(store: ArtifactStore) {
  const maximal = {
    contract: "algal.lab.study.v2", name: "max", replicateSeeds: [0, 1, 2, 3, 4, 5, 6, 7], researchers: 2, rounds: 4,
    nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101],
    primedDesigns: 0, counterbalance: false,
    transferRegimes: [{ nodes: 7, edges: 9, failureSteps: 2 }, { nodes: 8, edges: 10, failureSteps: 2 }],
  };
  const identities = await sourceIdentities("network.v1");
  const scores = { attempts: 0, primedDesigns: 0, validExperiments: 0, uniqueDesigns: 0, predictionMae: null,
    meanHoldoutAuc: null, bestHoldoutAuc: null, coverageAt075: 0, selectedAttempt: null, selectedScore: null,
    selectedRandomAuc: null, selectedTargetedAuc: null };
  const summaries = [];
  for (const replicate of maximal.replicateSeeds) {
    for (const name of CONDITIONS) {
      const slot = async (tag: string) => {
        const portfolioDigest = digest({ portfolio: `${replicate}:${name}:${tag}` });
        const evaluation = await store.put({ contract: "algal.lab.evaluation.v1", instrumentDigest: identities.instrumentDigest,
          portfolioDigest, holdoutSeeds: maximal.holdoutSeeds, designs: [] });
        return { portfolioDigest, evaluation };
      };
      const [primary, t0, t1] = [await slot("primary"), await slot("t0"), await slot("t1")];
      summaries.push({ replicate, condition: name, ...scores, portfolioDigest: primary.portfolioDigest, evaluation: primary.evaluation,
        transfers: [t0, t1].map((t) => ({ regime: maximal.transferRegimes[0], attempts: 0, validExperiments: 0, uniqueDesigns: 0,
          predictionMae: null, selectedAttempt: null, selectedScore: null, selectedRandomAuc: null, selectedTargetedAuc: null,
          portfolioDigest: t.portfolioDigest, evaluation: t.evaluation })) });
    }
  }
  return { contract: "algal.lab.report.v3", algalRevision: ALGAL_REVISION, backend: "scripted", protocol: maximal, ...identities,
    researcherManifest: digest({ manifest: "synthetic" }), conditionOrders: [], attempts: [], summaries };
}

test("a maximal legal protocol's 72 distinct portfolio digests project within the derived bound", async () => {
  const directory = await location();
  await mkdir(directory);
  const store = new ArtifactStore(directory);
  await store.initialize();
  const report = await maximalReport(store);
  const admitted = admitStudyView(json(report));
  expect(admitted.summaries).toHaveLength(24); // 8 replicate seeds x 3 conditions
  const { records } = await studyEvidence(json(report), store);
  expect(records).toHaveLength(1);
  expect(records[0]!.dataset.groups).toHaveLength(24);
  // One summary or one transfer beyond the derived bounds refuses admission.
  expect(() => admitStudyView({ ...report, summaries: [...report.summaries, report.summaries[0]!] })).toThrow(/summaries/);
  const extraTransfer = report.summaries.map((s, i) => i === 0 ? { ...s, transfers: [...s.transfers, s.transfers[0]!] } : s);
  expect(() => admitStudyView({ ...report, summaries: extraTransfer })).toThrow(/transfers/);
});

test("an attempt receipt whose digest does not match its body is rejected", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const store = new ArtifactStore(directory);
  const attempt = (await store.get(report.attempts[0]!)) as Attempt;
  const tamperedId = await store.put({ ...attempt, receipt: { ...attempt.receipt, digest: digest({ tampered: true }) } });
  await expect(studyEvidence(json({ ...report, attempts: [tamperedId], summaries: [] }), store)).rejects.toThrow(/receipt body does not match its digest/);
});

test("a drifted projection install is disclosed in the record and refused at verification", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const store = new ArtifactStore(directory);
  // A report recorded under different source identities still projects: the
  // record discloses the drift rather than silently mixing install states.
  const drifted = { ...report, instrumentDigest: digest({ other: "instrument" }), applicationDigest: digest({ other: "application" }),
    attempts: [], summaries: [] };
  const { records } = await studyEvidence(json(drifted), store);
  expect(records[0]!.limitations.some((line) => line.includes("differ from the study's recorded"))).toBe(true);
  const clean = await studyEvidence(json({ ...report, attempts: [], summaries: [] }), store);
  expect(clean.records[0]!.limitations.some((line) => line.includes("differ from the study's recorded"))).toBe(false);
  // And an evidence envelope whose recorded identities do not match the
  // installed sources fails verification before any record is checked.
  await writeStudyEvidence(directory);
  const file = object(await readJsonFile(join(directory, "evidence.json")), ["envelope", "digest"], "evidence file");
  const env = file.envelope as Record<string, unknown>;
  const forgedBody = { contract: env.contract, reportDigest: env.reportDigest, backend: env.backend,
    instrumentDigest: digest({ other: "instrument" }), applicationDigest: env.applicationDigest, records: env.records };
  const forged = { ...forgedBody, digest: digest(forgedBody) };
  await writeFile(join(directory, "evidence.json"), JSON.stringify({ envelope: forged, digest: forged.digest }));
  await expect(verifyStudyEvidence(directory)).rejects.toThrow(/source identity changed/);
}, 30000);
