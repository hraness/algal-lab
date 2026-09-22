import { afterEach, expect, test } from "bun:test";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { commandExecutor, type Executor, type JsonValue } from "@hraness/algal";
import { ArtifactStore, digest, readJsonFile } from "./artifacts";
import { CONDITIONS, type ResearchContext } from "./contracts";
import { scriptedProposal } from "./researcher";
import { runStudy, verifyStudy, type Attempt } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });
async function location() {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-test-"));
  roots.push(root);
  return join(root, "run");
}
const protocol = {
  contract: "algal.lab.study.v1", name: "test", replicateSeeds: [7], researchers: 2, rounds: 3,
  nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101],
};

test("complete studies reproduce, retain portfolios, and separate visibility by completed rounds", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const store = new ArtifactStore(directory);
  const attempts = await Promise.all(report.attempts.map(async (id) => await store.get(id) as unknown as Attempt));
  expect(report.attempts).toHaveLength(18);
  expect(report.summaries).toHaveLength(3);
  for (const attempt of attempts) {
    expect(attempt.context).not.toHaveProperty("holdoutSeeds");
    for (const evidence of attempt.context.evidence) {
      const source = await store.get(evidence.id) as unknown as Attempt;
      expect(source.context.round).toBeLessThan(attempt.context.round);
      expect(source.context.condition).toBe(attempt.context.condition);
      if (attempt.context.condition === "isolated") expect(source.context.researcher).toBe(attempt.context.researcher);
    }
    if (attempt.context.condition !== "shared-artifacts-and-messages") expect(attempt.context.messages).toEqual([]);
    expect(attempt.measurement?.results).toHaveLength(2);
    expect(attempt.receipt.effects.map((effect) => effect.executor)).toEqual(["algal-lab:scripted-network.v1", "tool:lab.network.measure.v1"]);
  }
  expect(attempts.filter((a) => a.context.condition === CONDITIONS[2] && a.context.round > 0).every((a) => a.context.messages.length > 0)).toBe(true);
  for (const summary of report.summaries) {
    const portfolio = await store.get(summary.portfolioDigest) as { members: string[] };
    expect(portfolio.members).toHaveLength(summary.uniqueDesigns);
    expect(summary.validExperiments).toBe(6);
  }
  const verified = await verifyStudy(directory);
  expect(verified.ok).toBe(true);
  expect(verified.experiments).toBe(18);
  expect(verified.reportDigest).toBe(digest(report));
  const second = await runStudy(protocol, await location());
  expect(second).toEqual(report);
});

test("scripted sharing variants have identical graphs and scores; condition hashes cannot steer selection", async () => {
  const directory = await location();
  const report = await runStudy({ ...protocol, rounds: 6, researchers: 3 }, directory);
  const store = new ArtifactStore(directory);
  const attempts = await Promise.all(report.attempts.map(async (id) => await store.get(id) as unknown as Attempt));
  const values = (condition: string) => attempts.filter((a) => a.context.condition === condition).map((a) => ({ graph: a.measurement?.proposal.graph, score: a.measurement?.score }));
  expect(values(CONDITIONS[1])).toEqual(values(CONDITIONS[2]));
});

test("invalid model proposals consume slots, retain evidence, and remain verifiable without recontacting the executor", async () => {
  const directory = await location();
  let calls = 0;
  const executor: Executor = { id: "invalid-test", execute: async () => {
    calls++;
    return { graph: { nodes: 6, edges: [[0, 1]] }, hypothesis: "bad", prediction: 0.5, rationale: "invalid graph", parents: [], message: "bad" };
  } };
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor });
  expect(calls).toBe(6);
  expect(report.summaries.every((s) => s.validExperiments === 0 && s.uniqueDesigns === 0 && s.meanHoldoutAuc === null)).toBe(true);
  const saved = await new ArtifactStore(directory).get(report.attempts[0]) as unknown as Attempt;
  expect(saved.receipt.cells.researcher?.outputs?.out).toBeDefined();
  expect(saved.measurement).toBeNull();
  expect((await verifyStudy(directory)).experiments).toBe(0);
  expect(calls).toBe(6);
});

test("the operator command seam works end to end and its recorded effects verify offline", async () => {
  const directory = await location();
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor: commandExecutor("bun examples/scripted-executor.ts", { timeoutMs: 10000, maxStdoutBytes: 8192 }) });
  expect(report.summaries.reduce((n, s) => n + s.validExperiments, 0)).toBe(6);
  expect((await verifyStudy(directory)).experiments).toBe(6);
});

test("a forged report with a recomputed outer digest still fails numerical reconstruction", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  report.summaries[0]!.meanHoldoutAuc = 1;
  await writeFile(join(directory, "study.json"), JSON.stringify({ report, digest: digest(report) }));
  await expect(verifyStudy(directory)).rejects.toThrow("report differs");
});

test("tampered content and source drift fail closed, and an existing run cannot be overwritten", async () => {
  const directory = await location();
  const report = await runStudy(protocol, directory);
  const path = join(directory, "artifacts", report.attempts[0]!.slice(7) + ".json");
  const original = await readFile(path, "utf8");
  await writeFile(path, original.replace('"prediction":0.65', '"prediction":0.25'));
  await expect(verifyStudy(directory)).rejects.toThrow("digest mismatch");
  await writeFile(path, original);
  report.applicationDigest = "sha256:" + "0".repeat(64);
  await writeFile(join(directory, "study.json"), JSON.stringify({ report, digest: digest(report) }));
  await expect(verifyStudy(directory)).rejects.toThrow("source identity changed");
  const before = await readJsonFile(join(directory, "protocol.json"));
  await expect(runStudy(protocol, directory)).rejects.toThrow();
  expect(await readJsonFile(join(directory, "protocol.json"))).toEqual(before);
});

test("a failed provider call is recorded once and not retried during execution or verification", async () => {
  const directory = await location();
  let calls = 0;
  const executor: Executor = { id: "failed-provider", execute: async () => { calls++; throw new Error("provider unavailable"); } };
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor });
  expect(calls).toBe(6);
  expect(report.summaries.every((s) => s.validExperiments === 0)).toBe(true);
  expect((await verifyStudy(directory)).experiments).toBe(0);
  expect(calls).toBe(6);
});

test("a researcher cannot cite future or other-condition evidence as a parent", async () => {
  const directory = await location();
  const executor: Executor = { id: "bad-parent", execute: async (request) => {
    const context = (request.context.inputs as { context: unknown }).context as ResearchContext;
    return { ...scriptedProposal(context), parents: ["sha256:" + "a".repeat(64)] };
  } };
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor });
  expect(report.summaries.every((s) => s.validExperiments === 0)).toBe(true);
  expect((await verifyStudy(directory)).experiments).toBe(0);
});

test("deep malformed researcher output is a recorded failure rather than an archival crash", async () => {
  const directory = await location();
  let nested: JsonValue = "leaf";
  for (let i = 0; i < 60; i++) nested = { child: nested };
  const executor: Executor = { id: "deep-output", execute: async () => ({ extra: nested }) };
  const report = await runStudy({ ...protocol, rounds: 1 }, directory, { executor });
  expect(report.attempts).toHaveLength(6);
  expect(report.summaries.every((s) => s.validExperiments === 0)).toBe(true);
  expect((await verifyStudy(directory)).experiments).toBe(0);
});

test("the largest admitted portfolio completes and verifies with bounded per-design artifacts", async () => {
  const directory = await location();
  const report = await runStudy({ ...protocol, researchers: 8, rounds: 12, nodes: 16, edges: 48, failureSteps: 14,
    discoverySeeds: [11, 29, 31, 43], holdoutSeeds: [101, 103, 107, 109, 113, 127, 131, 137] }, directory);
  expect(report.attempts).toHaveLength(288);
  expect(report.summaries.every((s) => s.validExperiments === 96)).toBe(true);
  expect((await verifyStudy(directory)).experiments).toBe(288);
}, 30000);
