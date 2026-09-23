import { afterEach, expect, test } from "bun:test";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { commandExecutor, type Executor, type JsonValue } from "@hraness/algal";
import { ArtifactStore, digest, readJsonFile } from "./artifacts";
import { CONDITIONS, json, type ResearchContext } from "./contracts";
import { primedProposal, scriptedProposal } from "./researcher";
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
    const portfolio = await store.get(summary.portfolioDigest) as { members: string[]; champion: string };
    expect(portfolio.members).toHaveLength(summary.uniqueDesigns);
    expect(summary.validExperiments).toBe(6);
    expect(portfolio.champion).toBe(summary.selectedAttempt!);
    const champion = await store.get(portfolio.champion) as unknown as Attempt;
    expect(attempts.filter((a) => a.context.condition === summary.condition).every((a) => a.measurement!.score <= champion.measurement!.score)).toBe(true);
    expect(summary.selectedRandomAuc).toBeGreaterThan(0);
    expect(summary.selectedTargetedAuc).toBeGreaterThan(0);
  }
  const verified = await verifyStudy(directory);
  expect(verified.ok).toBe(true);
  expect(verified.experiments).toBe(18);
  expect(verified.reportDigest).toBe(digest(report));
  const second = await runStudy(protocol, await location());
  expect(second).toEqual(report);
});

test("random-search controls ignore visibility, and champion selection cannot depend on holdouts", async () => {
  const directory = await location();
  const random = await runStudy(protocol, directory, { policy: "random" });
  const store = new ArtifactStore(directory);
  const graphs = await Promise.all(random.attempts.map(async (id) => (await store.get(id) as unknown as Attempt).measurement!.proposal.graph));
  expect(graphs.slice(0, 6)).toEqual(graphs.slice(6, 12));
  expect(graphs.slice(0, 6)).toEqual(graphs.slice(12));
  expect(random.backend).toBe("random");
  expect((await verifyStudy(directory)).experiments).toBe(18);
  const other = await runStudy({ ...protocol, holdoutSeeds: [999, 777] }, await location(), { policy: "random" });
  expect(random.summaries.map((s) => s.selectedAttempt)).toEqual(other.summaries.map((s) => s.selectedAttempt));
  expect(random.summaries.map((s) => s.portfolioDigest)).toEqual(other.summaries.map((s) => s.portfolioDigest));
});

test("live researcher requests omit assignment labels and evaluation data while retaining prior evidence", async () => {
  let sawEvidence = false;
  const executor: Executor = { id: "blinding-check", execute: async (request) => {
    const context = (request.context.inputs as { context: unknown }).context as ResearchContext;
    expect(context).not.toHaveProperty("condition");
    expect(context).not.toHaveProperty("holdoutSeeds");
    sawEvidence ||= context.evidence.length > 0;
    return scriptedProposal(context);
  } };
  const directory = await location();
  const report = await runStudy({ ...protocol, rounds: 2 }, directory, { executor });
  expect(sawEvidence).toBe(true);
  expect(report.summaries.every((s) => s.validExperiments === 4)).toBe(true);
  expect((await verifyStudy(directory)).experiments).toBe(12);
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

const protocolV2 = {
  contract: "algal.lab.study.v2", name: "test-v2", replicateSeeds: [7, 23], researchers: 2, rounds: 2,
  nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101],
  primedDesigns: 2, counterbalance: true, transferRegimes: [{ nodes: 7, edges: 9, failureSteps: 2 }],
};

test("v2 protocols prime identical designs across conditions, rotate condition order, and run transfer budgets", async () => {
  const directory = await location();
  const report = await runStudy(protocolV2, directory);
  const store = new ArtifactStore(directory);
  const attempts = await Promise.all(report.attempts.map(async (id) => await store.get(id) as unknown as Attempt));
  // 2 seeds × 3 conditions × (2 researchers × 2 primed + 2 × 2 discovery + 2 × 1 transfer)
  expect(report.attempts).toHaveLength(2 * 3 * (4 + 4 + 2));
  expect(report.conditionOrders).toEqual([
    { replicate: 7, conditions: ["isolated", "shared-artifacts", "shared-artifacts-and-messages"] },
    { replicate: 23, conditions: ["shared-artifacts", "shared-artifacts-and-messages", "isolated"] },
  ]);
  const phase = (a: Attempt) => a.context.contract === "algal.lab.context.v2" ? a.context.phase : "discovery";
  for (const attempt of attempts) expect(attempt.context.contract).toBe("algal.lab.context.v2");
  const primed = attempts.filter((a) => phase(a) === "primed");
  expect(primed).toHaveLength(2 * 3 * 4);
  for (const attempt of primed) {
    expect(attempt.context.round).toBe(-1);
    expect(attempt.context.evidence).toEqual([]);
    expect(attempt.receipt.effects[0]?.executor).toBe("algal-lab:primed-design.v1");
    expect(attempt.measurement).not.toBeNull();
  }
  // Identical primed graphs per (replicate, researcher, index) in every condition.
  for (const replicate of [7, 23]) for (const condition of CONDITIONS) {
    const graphs = primed.filter((a) => a.context.replicate === replicate && a.context.condition === condition).map((a) => a.measurement!.proposal.graph);
    const reference = primed.filter((a) => a.context.replicate === replicate && a.context.condition === "isolated").map((a) => a.measurement!.proposal.graph);
    expect(graphs).toEqual(reference);
  }
  // Discovery round zero sees primed evidence; isolated researchers see only their own primed designs.
  for (const attempt of attempts.filter((a) => phase(a) === "discovery" && a.context.round === 0)) {
    expect(attempt.context.evidence.length).toBe(attempt.context.condition === "isolated" ? 2 : 4);
  }
  // Transfer contexts carry the transfer budget while evidence stays at the primary budget.
  const transfers = attempts.filter((a) => phase(a) === "transfer");
  expect(transfers).toHaveLength(2 * 3 * 2);
  for (const attempt of transfers) {
    expect(attempt.context.round).toBe(2);
    expect(attempt.context.nodes).toBe(7);
    expect(attempt.context.edges).toBe(9);
    expect(attempt.context.evidence.length).toBeGreaterThan(0);
    expect(attempt.context.evidence.every((e) => e.graph.nodes === 6)).toBe(true);
    expect(attempt.measurement?.proposal.graph.nodes).toBe(7);
    expect(attempt.measurement?.proposal.graph.edges).toHaveLength(9);
    expect(attempt.measurement?.proposal.parents).toEqual([]); // the scripted policy has no transferable rule
  }
  for (const summary of report.summaries) {
    expect(summary.primedDesigns).toBe(4);
    expect(summary.validExperiments).toBe(4);
    expect(summary.attempts).toBe(4);
    expect(summary.transfers).toHaveLength(1);
    expect(summary.transfers[0]!.validExperiments).toBe(2);
    expect(summary.transfers[0]!.regime).toEqual({ nodes: 7, edges: 9, failureSteps: 2 });
    const portfolio = await store.get(summary.portfolioDigest) as { members: string[] };
    // Primed designs join the primary portfolio; transfer designs never do.
    expect(portfolio.members.some((id) => primed.some((a) => report.attempts[attempts.indexOf(a)] === id))).toBe(true);
    for (const member of portfolio.members) expect(transfers.some((a) => report.attempts[attempts.indexOf(a)] === member)).toBe(false);
    const transferPortfolio = await store.get(summary.transfers[0]!.portfolioDigest) as { regime: unknown; members: string[] };
    expect(transferPortfolio.regime).toEqual({ nodes: 7, edges: 9, failureSteps: 2 });
    expect(transferPortfolio.members.length).toBe(summary.transfers[0]!.uniqueDesigns);
  }
  const verified = await verifyStudy(directory);
  expect(verified.attempts).toBe(60);
  expect(verified.experiments).toBe(6 * 4 + 6 * 2);
  expect(await runStudy(protocolV2, await location())).toEqual(report);
});

test("a tampered primed design fails reconstruction, and v2 protocol bounds hold", async () => {
  const directory = await location();
  const report = await runStudy({ ...protocolV2, replicateSeeds: [7], transferRegimes: [] }, directory);
  const store = new ArtifactStore(directory);
  const id = report.attempts[0]!;
  const attempt = await store.get(id) as unknown as Attempt;
  expect(attempt.context.round).toBe(-1);
  // Forge a different valid graph into the primed attempt's recorded effect and
  // measurement, then re-address the artifact and report so every digest matches.
  const forged = JSON.parse(JSON.stringify(attempt)) as Attempt;
  const graph = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5], [0, 3]] } as unknown as Attempt["context"]["evidence"][number]["graph"];
  (forged.receipt.effects[0] as unknown as { output: { graph: unknown } }).output.graph = graph;
  forged.measurement!.proposal.graph = graph;
  const forgedId = await new ArtifactStore(directory).put(forged);
  const rewritten = { ...report, attempts: report.attempts.map((item) => item === id ? forgedId : item) };
  await writeFile(join(directory, "study.json"), JSON.stringify({ report: rewritten, digest: digest(rewritten) }));
  // Verification regenerates primed attempts on the host instead of replaying
  // them, so the forged artifact can never be reproduced and the report fails.
  await expect(verifyStudy(directory)).rejects.toThrow("report differs from reproduced study");
  expect(forged.receipt.effects[0]?.executor).toBe("algal-lab:primed-design.v1");
  // A command archive relabelled as a scripted baseline is recomputed, not replayed.
  const relabel = await location();
  const hand = { id: "hand-picked", capabilities: { effects: ["agent"] }, cacheable: false, retryable: false,
    execute: async () => json({ ...primedProposal({ ...attempt.context, replicate: 99 }, 0), prediction: 0.7 }) } as Executor;
  const command = await runStudy({ ...protocolV2, replicateSeeds: [7], transferRegimes: [] }, relabel, { executor: hand });
  expect(command.backend).toBe("command");
  await expect(verifyStudy(relabel)).resolves.toMatchObject({ ok: true });
  const relabelled = { ...command, backend: "scripted" };
  await writeFile(join(relabel, "study.json"), JSON.stringify({ report: relabelled, digest: digest(relabelled) }));
  await expect(verifyStudy(relabel)).rejects.toThrow("report differs from reproduced study");
  // The reverse relabelling is caught by executor identity before replay.
  const scripted = await location();
  const baseline = await runStudy({ ...protocolV2, replicateSeeds: [7], transferRegimes: [] }, scripted);
  const asCommand = { ...baseline, backend: "command" };
  await writeFile(join(scripted, "study.json"), JSON.stringify({ report: asCommand, digest: digest(asCommand) }));
  await expect(verifyStudy(scripted)).rejects.toThrow("host policy executor");
  await expect(runStudy({ ...protocolV2, transferRegimes: [{ nodes: 6, edges: 7, failureSteps: 2 }] }, await location())).rejects.toThrow("must differ");
  await expect(runStudy({ ...protocolV2, primedDesigns: 5 }, await location())).rejects.toThrow("primedDesigns");
  await expect(runStudy({ ...protocolV2, counterbalance: "yes" }, await location())).rejects.toThrow("counterbalance");
  await expect(runStudy({ ...protocolV2, transferRegimes: [{ nodes: 7, edges: 9, failureSteps: 2 }, { nodes: 7, edges: 9, failureSteps: 2 }] }, await location())).rejects.toThrow("repeated");
  await expect(runStudy({ ...protocolV2, extra: 1 }, await location())).rejects.toThrow("unknown field");
});

test("v3 studies run the heterogeneous instrument per replicate and reproduce offline", async () => {
  const directory = await location();
  const protocolV3 = { contract: "algal.lab.study.v3", instrument: "network.v2", name: "v3-study", replicateSeeds: [7], researchers: 2, rounds: 1,
    nodes: 5, edges: 4, failureSteps: 2, discoverySeeds: [11], holdoutSeeds: [101], primedDesigns: 1, counterbalance: true, transferRegimes: [] };
  const report = await runStudy(protocolV3, directory);
  expect(report.attempts).toHaveLength(12);
  const store = new ArtifactStore(directory);
  const attempts = await Promise.all(report.attempts.map(async (id) => await store.get(id) as unknown as Attempt));
  for (const attempt of attempts) {
    expect(attempt.context.contract).toBe("algal.lab.context.v3");
    if (attempt.context.contract !== "algal.lab.context.v3") throw new Error("expected v3 context");
    expect(attempt.context.environment.weights).toHaveLength(5);
    expect(attempt.context.environment.values).toHaveLength(5);
    expect(attempt.measurement?.results.every((r) => r.contract === "algal.lab.network-result.v2" && r.instrument === "network.v2")).toBe(true);
  }
  const verified = await verifyStudy(directory);
  expect(verified.ok).toBe(true);
  expect(verified.attempts).toBe(12);
});
