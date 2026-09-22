import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { inspectGatewaySmoke } from "../scripts/inspect-gateway-smoke";
import { digest } from "./artifacts";
import { type ResearchContext } from "./contracts";
import { createGatewayExecutor, type GatewayExecutorOptions } from "./gateway-executor";
import { mutateGraph } from "./network";
import { scriptedProposal } from "./researcher";
import { runStudy } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });

const protocol = { contract: "algal.lab.study.v1", name: "network-model-smoke", replicateSeeds: [2903], researchers: 2, rounds: 2,
  nodes: 8, edges: 10, failureSteps: 3, discoverySeeds: [71, 139], holdoutSeeds: [2063, 4127, 8263] };
const fullUsage = { prompt_tokens: 10, completion_tokens: 20, total_tokens: 30,
  completion_tokens_details: { reasoning_tokens: 2 }, prompt_tokens_details: { cached_tokens: 5 }, cost: 0.001 };

type FixtureOptions = {
  usage?: (index: number) => unknown; changePeer?: boolean; responseModel?: string; protocol?: Partial<typeof protocol>;
  settings?: Partial<Pick<GatewayExecutorOptions, "model" | "provider" | "timeoutMs" | "maxOutputBytes" | "maxResponseBytes">>;
};
async function fixture(options: FixtureOptions = {}) {
  const root = await mkdtemp(join(tmpdir(), "algal-gateway-smoke-")); roots.push(root);
  const studyProtocol = { ...protocol, ...options.protocol };
  const model = options.settings?.model ?? "openai/gpt-6-luna";
  let calls = 0;
  // The real wrapper talks exclusively to this fake HTTP boundary. No credentials
  // are loaded and no external model, account, or network connection is used.
  const executor = createGatewayExecutor({ model, provider: "openai", maxCalls: 12, ...options.settings,
    credential: "fixture-credential-only", fetch: async (_input, init) => {
      const body = JSON.parse(String(init?.body)) as { messages: { role: string; content: string }[] };
      const message = body.messages.find((item) => item.role === "user");
      const request = JSON.parse(message!.content) as { context: { inputs: { context: ResearchContext } } };
      const context = request.context.inputs.context;
      const peer = context.evidence.length === 2 ? context.evidence[1 - context.researcher] : undefined;
      const base = scriptedProposal(context);
      const proposal = peer ? { ...base, graph: options.changePeer === false ? peer.graph : mutateGraph(peer.graph, context.researcher + 43), parents: [peer.id] } : base;
      const index = calls++;
      const usage = options.usage ? options.usage(index) : fullUsage;
      return Response.json({ id: `chatcmpl-fixture-${index}`, model: options.responseModel ?? model.split("/")[1],
        choices: [{ finish_reason: "stop", message: { role: "assistant", content: JSON.stringify({ value: proposal }) } }],
        ...(usage !== undefined ? { usage } : {}) }, { headers: { "x-request-id": `req_fixture_${index}` } });
    } });
  const intent = { protocol: studyProtocol, model: executor.configuration.model, provider: executor.configuration.provider, maxCalls: 12 };
  const configuration = { configuration: executor.configuration, configurationDigest: executor.configurationDigest };
  const writeIntent = (value: unknown = intent) => writeFile(join(root, "intent.json"), JSON.stringify(value));
  const writeConfiguration = (value: unknown = configuration) => writeFile(join(root, "executor.json"), JSON.stringify(value));
  const writeSidecar = (observations: unknown = executor.observations, extra: Record<string, unknown> = {}) =>
    writeFile(join(root, "gateway.json"), JSON.stringify({ ...configuration, observations, cancelled: false, ...extra }));
  await writeIntent(); await writeConfiguration();
  try { await runStudy(studyProtocol, join(root, "study"), { executor }); }
  finally { await executor.settle(); await writeSidecar(); }
  return { root, calls, executor, intent, configuration, writeIntent, writeConfiguration, writeSidecar };
}

test("Gateway smoke inspects real-wrapper fake-fetch receipts, inheritance, and reported usage", async () => {
  const f = await fixture();
  const result = await inspectGatewaySmoke(f.root);
  expect(f.calls).toBe(12);
  expect(result.passed).toBe(true);
  expect(result.controls.frozenPlanMatches).toBe(true);
  expect(result.controls.exactBudgetContract).toBe(true);
  expect(result.inheritance.length).toBeGreaterThan(0);
  expect(result.inheritance.every((item) => item.researcher !== item.parentResearcher && item.round > 0)).toBe(true);
  expect(result.champions).toHaveLength(3);
  expect(result.champions.every((item) => item.graphDigest !== null && item.exactRandomAuc !== null)).toBe(true);
  expect(result.models).toEqual(["gpt-6-luna"]);
  expect(result.usage).toMatchObject({ tokensIn: 120, tokensOut: 240, totalTokens: 360, reasoningTokens: 24, cachedTokens: 60 });
  expect(result.usage.cost).toBeCloseTo(0.012, 12);
  expect(result.analysisDigest).toMatch(/^sha256:[a-f0-9]{64}$/);
});

test("Gateway smoke does not qualify a valid archive with a different protocol, model, or settings", async () => {
  const alternatives: FixtureOptions[] = [
    { protocol: { name: "other-smoke", replicateSeeds: [2904], nodes: 6, edges: 7, failureSteps: 2, discoverySeeds: [73], holdoutSeeds: [2067] } },
    { settings: { timeoutMs: 59000, maxOutputBytes: 4096, maxResponseBytes: 32768 } },
    { settings: { model: "openai/fixture-other", provider: "fixture-provider" } },
  ];
  for (const options of alternatives) {
    const f = await fixture(options);
    const result = await inspectGatewaySmoke(f.root);
    expect(result.proposals).toBe(12);
    expect(Object.entries(result.controls).filter(([, value]) => !value)).toEqual([["frozenPlanMatches", false]]);
    expect(result.passed).toBe(false);
  }
});

test("Gateway smoke leaves each incompletely reported usage total unknown", async () => {
  const f = await fixture({ usage: (index) => index === 11 ? { prompt_tokens: 10, completion_tokens: 20 } : fullUsage,
    responseModel: "openai/gpt-6-luna" });
  const result = await inspectGatewaySmoke(f.root);
  expect(result.passed).toBe(true);
  expect(result.models).toEqual(["openai/gpt-6-luna"]);
  expect(result.usage).toEqual({ tokensIn: 120, tokensOut: 240, totalTokens: null, reasoningTokens: null, cachedTokens: null, cost: null });
  const absent = await fixture({ usage: () => undefined });
  const missing = await inspectGatewaySmoke(absent.root);
  expect(missing.passed).toBe(true);
  expect(missing.usage).toEqual({ tokensIn: null, tokensOut: null, totalTokens: null, reasoningTokens: null, cachedTokens: null, cost: null });
});

test("Gateway smoke rejects unknown metadata and mismatched intent, model, identity, order, or usage", async () => {
  const f = await fixture();
  const observations = f.executor.observations;
  await f.writeIntent({ ...f.intent, provider: "other" });
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("frozen intent mismatch");
  await f.writeIntent({ ...f.intent, model: "openai/other" });
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("frozen intent mismatch");
  await f.writeIntent();

  const unknown = { ...f.executor.configuration, extra: true };
  const unknownConfiguration = { configuration: unknown, configurationDigest: digest(unknown) };
  await f.writeConfiguration(unknownConfiguration); await f.writeSidecar(observations, unknownConfiguration);
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("unknown field");
  const other = { ...f.executor.configuration, model: "openai/other" };
  const otherConfiguration = { configuration: other, configurationDigest: digest(other) };
  await f.writeConfiguration(otherConfiguration); await f.writeSidecar(observations, otherConfiguration);
  await f.writeIntent({ ...f.intent, model: other.model });
  expect((await inspectGatewaySmoke(f.root)).controls.receiptConfigurationMatches).toBe(false);
  await f.writeConfiguration(); await f.writeIntent();

  await f.writeSidecar(observations.map((o, index) => index === 1 ? { ...o, responseId: observations[0]!.responseId } : o));
  const repeated = await inspectGatewaySmoke(f.root);
  expect(repeated.controls.distinctGenerationRequests).toBe(false);
  expect(repeated.usage.cost).toBeNull();
  await f.writeSidecar([observations[1], observations[0], ...observations.slice(2)]);
  expect((await inspectGatewaySmoke(f.root)).controls.transportReportsCompleted).toBe(false);
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, usage: { ...o.usage, tokensIn: 11 } } : o));
  expect((await inspectGatewaySmoke(f.root)).controls.receiptUsageMatches).toBe(false);
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, model: "other" } : o));
  expect((await inspectGatewaySmoke(f.root)).controls.transportReportsCompleted).toBe(false);
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, code: "provider_error" } : o));
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("invalid Gateway observation outcome");
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, usage: { ...o.usage, priceEstimate: 1 } } : o));
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("unknown field");
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, usage: { ...o.usage, cost: -1 } } : o));
  await expect(inspectGatewaySmoke(f.root)).rejects.toThrow("invalid Gateway cost");
  await f.writeSidecar(observations.slice(1));
  expect((await inspectGatewaySmoke(f.root)).controls.transportReportsCompleted).toBe(false);
  await f.writeSidecar(observations, { cancelled: true });
  expect((await inspectGatewaySmoke(f.root)).controls.notCancelled).toBe(false);
  await f.writeSidecar(observations.map((o, index) => index === 0 ? { ...o, schemaDigest: "sha256:" + "0".repeat(64) } : o));
  expect((await inspectGatewaySmoke(f.root)).controls.exactBudgetContract).toBe(false);
  await f.writeSidecar(observations.map(({ schemaDigest: _dropped, ...o }) => o));
  expect((await inspectGatewaySmoke(f.root)).controls.exactBudgetContract).toBe(false);
});

test("Gateway smoke requires a changed peer design, not an unchanged citation", async () => {
  const f = await fixture({ changePeer: false });
  const result = await inspectGatewaySmoke(f.root);
  expect(result.proposals).toBe(12);
  expect(result.controls.transportReportsCompleted).toBe(true);
  expect(result.controls.changedDesignFromVisiblePeer).toBe(false);
  expect(result.passed).toBe(false);
});
