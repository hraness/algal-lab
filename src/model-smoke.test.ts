import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { effectRequestDigest, type Executor } from "@hraness/algal";
import { inspectModelSmoke } from "../scripts/inspect-model-smoke";
import { digest } from "./artifacts";
import { type ResearchContext } from "./contracts";
import { mutateGraph } from "./network";
import { scriptedProposal } from "./researcher";
import { runStudy } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });

test("smoke inspection requires changed peer designs and complete matched transport evidence", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-smoke-inspection-")); roots.push(root);
  // Valid-shaped synthetic transport evidence, never a real provider call.
  const configuration = { contract: "algal.lab.xcb-executor.v1", provider: "devin", model: "devin/swe-2-high",
    accountDigest: digest("a_fixture"), runtimeVersion: "fixture", runtimeDigest: digest("fixture runtime"), qualificationEvidenceDigest: digest("fixture evidence"),
    qualificationExpiresAt: Date.now() + 3600000, modelObservedAtMs: Date.now(), timeoutMs: 45000, maxOutputBytes: 8192, maxInputBytes: 131072, maxCalls: 12,
    zeroTools: true, zeroHooks: true, ephemeral: true, tokenUsage: "unavailable" };
  const configurationDigest = digest(configuration);
  const observations: { requestDigest: string; requestId: string; elapsedMs: number; status: string; joined: boolean; effects: string }[] = [];
  const id = `algal-lab:xcb.v1:${configuration.model}`;
  const executor: Executor = { id, execute: async () => null, executeEffect: async (request) => {
    const context = (request.context.inputs as { context: unknown }).context as ResearchContext;
    const peer = context.evidence.length === 2 ? context.evidence[1 - context.researcher] : undefined;
    const base = scriptedProposal(context);
    const proposal = peer ? { ...base, graph: mutateGraph(peer.graph, context.researcher + 43), parents: [peer.id] } : base;
    observations.push({ requestDigest: effectRequestDigest(request), requestId: `application_fixture_${observations.length}`, elapsedMs: 1, status: "completed", joined: true, effects: "none" });
    return { output: proposal, metadata: { executor: id, configurationDigest, usage: { model: configuration.model } } };
  } };
  const protocol = { contract: "algal.lab.study.v1", name: "fixture", replicateSeeds: [2903], researchers: 2, rounds: 2,
    nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [71], holdoutSeeds: [2063] };
  await runStudy(protocol, join(root, "study"), { executor });
  const intent = { protocol, model: configuration.model, accountDigest: configuration.accountDigest, maxCalls: 12 };
  await writeFile(join(root, "intent.json"), JSON.stringify(intent));
  await writeFile(join(root, "executor.json"), JSON.stringify({ configuration, configurationDigest }));
  const sidecar = { configuration, configurationDigest, observations, cancelled: false };
  await writeFile(join(root, "xcb.json"), JSON.stringify(sidecar));
  const result = await inspectModelSmoke(root);
  expect(result.passed).toBe(true);
  expect(result.inheritance.length).toBeGreaterThan(0);
  expect(result.inheritance.every((i) => i.researcher !== i.parentResearcher && i.round > 0)).toBe(true);
  expect(result.champions).toHaveLength(3);
  await writeFile(join(root, "intent.json"), JSON.stringify({ ...intent, model: "devin/other" }));
  await expect(inspectModelSmoke(root)).rejects.toThrow("frozen intent mismatch");
  await writeFile(join(root, "intent.json"), JSON.stringify(intent));
  observations[1]!.requestId = observations[0]!.requestId;
  await writeFile(join(root, "xcb.json"), JSON.stringify(sidecar));
  expect((await inspectModelSmoke(root)).controls.distinctTransportRequests).toBe(false);
  const different = { ...configuration, model: "devin/other" };
  const differentDigest = digest(different);
  await writeFile(join(root, "executor.json"), JSON.stringify({ configuration: different, configurationDigest: differentDigest }));
  await writeFile(join(root, "xcb.json"), JSON.stringify({ ...sidecar, configuration: different, configurationDigest: differentDigest }));
  await writeFile(join(root, "intent.json"), JSON.stringify({ ...intent, model: different.model }));
  expect((await inspectModelSmoke(root)).controls.receiptConfigurationMatches).toBe(false);
  await writeFile(join(root, "executor.json"), JSON.stringify({ configuration, configurationDigest }));
  await writeFile(join(root, "intent.json"), JSON.stringify(intent));
  await writeFile(join(root, "xcb.json"), JSON.stringify({ ...sidecar, observations: observations.map((o, index) => index === 0 ? { ...o, code: "provider_error" } : o) }));
  await expect(inspectModelSmoke(root)).rejects.toThrow("invalid completed observation");
  observations.pop();
  await writeFile(join(root, "xcb.json"), JSON.stringify(sidecar));
  expect((await inspectModelSmoke(root)).controls.transportReportsCompletedJoined).toBe(false);
  await writeFile(join(root, "xcb.json"), JSON.stringify({ ...sidecar, configuration: { model: "forged" } }));
  await expect(inspectModelSmoke(root)).rejects.toThrow("configuration identity mismatch");
});
