import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { digestCanonical, effectRequestDigest, type EffectRequest, type GatewayFetch } from "@hraness/algal";
import { ArtifactStore } from "./artifacts";
import { json, proposalContractSchema, PROPOSAL_CONTRACT } from "./contracts";
import { createGatewayExecutor } from "./gateway-executor";
import { runStudy, verifyStudy, type Attempt } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true }))); });
const selection = { model: "openai/gpt-6-luna", provider: "openai", credential: "fixture-credential-only" };
const proposal = { graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 3]] }, hypothesis: "Redundant paths may retain service.", prediction: 0.6, rationale: "Compare designs at the same edge budget.", parents: [], message: "Compare degree concentration." };
const request: EffectRequest = {
  contract: "algal.effect.v1", kind: "agent", cellId: "researcher", prompt: "Return a bounded proposal JSON.",
  output: { kind: "json", schema: { type: "object" } },
  context: { inputs: { context: { contract: "algal.lab.context.v1", nodes: 4, edges: 4, evidence: [], messages: [] } } },
  budget: { maxContextBytes: 65536, maxOutputBytes: 8192 },
};
const schema = proposalContractSchema(4, 4);
function response(overrides: Record<string, unknown> = {}, headers: Record<string, string> = {}): Response {
  return Response.json({
    id: "chatcmpl-fixture", model: "gpt-6-luna",
    choices: [{ finish_reason: "stop", message: { role: "assistant", content: JSON.stringify({ value: proposal }) } }],
    usage: { prompt_tokens: 10, completion_tokens: 20, total_tokens: 30, completion_tokens_details: { reasoning_tokens: 2 }, prompt_tokens_details: { cached_tokens: 3 }, cost: "0.001" },
    ...overrides,
  }, { headers: { "x-request-id": "req_fixture", ...headers } });
}
function failureChoice(fields: Record<string, unknown> = {}, message: Record<string, unknown> = {}) {
  return [{ finish_reason: "stop", message: { content: JSON.stringify({ value: proposal }), ...message }, ...fields }];
}

test("native ALGAL Gateway execution sends the full bounded schema and retains original request identity and usage", async () => {
  const before = structuredClone(request);
  let calls = 0;
  const fetch: GatewayFetch = async (url, init) => {
    calls++;
    expect(url).toBe("https://ai-gateway.vercel.sh/v1/chat/completions");
    expect(init?.method).toBe("POST");
    expect(init?.redirect).toBe("error");
    expect(init?.cache).toBe("no-store");
    expect(new Headers(init?.headers).get("authorization")).toBe(`Bearer ${selection.credential}`);
    const body = JSON.parse(init!.body as string);
    expect(Object.keys(body).sort()).toEqual(["max_tokens", "messages", "model", "providerOptions", "reasoning_effort", "response_format", "temperature"]);
    expect(body).toMatchObject({ model: selection.model, max_tokens: 2048, temperature: 0, reasoning_effort: "low", providerOptions: { gateway: { only: [selection.provider] } } });
    expect(body.response_format).toEqual({ type: "json_schema", json_schema: { name: "algal_cell_output", strict: true, schema: { type: "object", additionalProperties: false, required: ["value"], properties: { value: schema } } } });
    const context = JSON.parse(body.messages[1].content);
    expect(context.context).toEqual(request.context);
    expect(context.output.schema).toEqual(schema);
    return response();
  };
  const executor = createGatewayExecutor({ ...selection, fetch, maxCalls: 1 });
  const result = await executor.executeEffect!(request);
  expect(result.output).toEqual(proposal);
  expect(result.metadata).toEqual({ executor: executor.id, configurationDigest: executor.configurationDigest, retryable: false, usage: { model: "gpt-6-luna", tokensIn: 10, tokensOut: 20 } });
  expect(executor.id).toBe(`algal-lab:gateway.v2:${selection.model}`);
  expect(executor.cacheable).toBe(false);
  expect(executor.retryable).toBe(false);
  expect(request).toEqual(before);
  expect(executor.configuration.proposalContract).toBe(PROPOSAL_CONTRACT);
  expect(executor.configurationDigest).toBe(digestCanonical(json(executor.configuration)));
  expect(executor.observations).toHaveLength(1);
  expect(executor.observations[0]).toMatchObject({ attempt: 1, requestDigest: effectRequestDigest(request), schemaDigest: digestCanonical(schema), status: "completed", dispatched: true, uncertain: false, httpStatus: 200, requestId: "req_fixture", responseId: "chatcmpl-fixture", model: "gpt-6-luna", finishReason: "stop", usage: { tokensIn: 10, tokensOut: 20, totalTokens: 30, reasoningTokens: 2, cachedTokens: 3, cost: 0.001 } });
  expect(executor.observations[0]).not.toHaveProperty("code");
  expect(JSON.stringify(executor.observations)).not.toContain(selection.credential);
  await expect(executor.execute(request)).rejects.toThrow("call_budget_exhausted");
  expect(calls).toBe(1);
  await executor.settle();
});

test("configuration identity changes for relevant bounds and selection but excludes credentials", () => {
  const normal = createGatewayExecutor(selection);
  expect(createGatewayExecutor({ ...selection, credential: "different-fixture-secret" }).configurationDigest).toBe(normal.configurationDigest);
  for (const change of [{ provider: "azure-openai" }, { model: "openai/catalog-fixture" }, { maxCalls: 1 }, { timeoutMs: 5000 }, { maxOutputBytes: 4096 }, { maxResponseBytes: 32768 }]) {
    expect(createGatewayExecutor({ ...selection, ...change }).configurationDigest).not.toBe(normal.configurationDigest);
  }
  for (const change of [{ maxCalls: 13 }, { maxCalls: 0 }, { timeoutMs: 60001 }, { maxOutputBytes: 8193 }, { maxResponseBytes: 65537 }, { maxCalls: NaN }, { model: "auto" }, { provider: "openai/other" }, { retries: 1 }, { signal: {} }, { fetch: "url" }]) {
    expect(() => createGatewayExecutor({ ...selection, ...change } as never)).toThrow();
  }
  expect(Object.isFrozen(schema)).toBe(true);
  expect(Object.isFrozen(normal.configuration)).toBe(true);
  expect(JSON.stringify(normal.configuration)).not.toContain(selection.credential);
});

test("missing token usage stays absent and unsupported numeric/identifier metadata never leaks", async () => {
  const executor = createGatewayExecutor({ ...selection, fetch: async () => response({
    id: selection.credential, model: selection.model,
    usage: { prompt_tokens: -1, completion_tokens: 1_000_000_001, total_tokens: 1.5, completion_tokens_details: { reasoning_tokens: "4" }, cost: "private-error" },
  }, { "x-request-id": `echo-${selection.credential}` }) });
  const result = await executor.executeEffect!(request);
  expect(result.metadata?.usage).toEqual({ model: selection.model });
  expect(executor.observations[0]).not.toHaveProperty("usage");
  expect(executor.observations[0]).not.toHaveProperty("requestId");
  expect(executor.observations[0]).not.toHaveProperty("responseId");
  expect(JSON.stringify(executor.observations)).not.toContain("private-error");
  expect(JSON.stringify(executor.observations)).not.toContain(selection.credential);
});

test("credential echoes in proposal text or keys are rejected before durable ALGAL receipts", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-gateway-redaction-")); roots.push(root);
  const directory = join(root, "study");
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, maxCalls: 6, fetch: async () => {
    const echoed = ++calls % 2 ? { ...proposal, rationale: `echo ${selection.credential}` } : { ...proposal, [selection.credential]: "key echo" };
    return response({ choices: failureChoice({}, { content: JSON.stringify({ value: echoed }) }) });
  } });
  const report = await runStudy({ contract: "algal.lab.study.v1", name: "gateway-redaction", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }, directory, { executor });
  expect(calls).toBe(6);
  const store = new ArtifactStore(directory);
  for (const reference of report.attempts) {
    const attempt = await store.get(reference) as unknown as Attempt;
    expect(attempt.measurement).toBeNull();
    expect(attempt.receipt.effects[0]?.error?.message).toBe("gateway application: invalid_response");
    expect(attempt.receipt.effects[0]).not.toHaveProperty("output");
    expect(JSON.stringify(attempt)).not.toContain(selection.credential);
  }
  expect(JSON.stringify(executor.observations)).not.toContain(selection.credential);
  expect(executor.observations.every((item) => item.code === "invalid_response" && !item.uncertain)).toBe(true);
  expect(await verifyStudy(directory)).toMatchObject({ attempts: 6, experiments: 0 });
  const escapedCredential = 'fixture-credential-"escaped';
  const escaped = createGatewayExecutor({ ...selection, credential: escapedCredential, fetch: async () => response({ choices: failureChoice({}, { content: JSON.stringify({ value: { ...proposal, rationale: escapedCredential } }) }) }) });
  await expect(escaped.execute(request)).rejects.toThrow("invalid_response");
  expect(JSON.stringify(escaped.observations)).not.toContain(escapedCredential);
});

test("provider output outside the exact budget contract is rejected before the host sees it", async () => {
  const violations = [
    { ...proposal, graph: { nodes: 4, edges: [...proposal.graph.edges, [0, 2]] } },
    { ...proposal, graph: { nodes: 4, edges: proposal.graph.edges.slice(1) } },
    { ...proposal, graph: { nodes: 5, edges: proposal.graph.edges } },
    { ...proposal, graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 4]] } },
    { ...proposal, graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 3.5]] } },
    { ...proposal, graph: { nodes: 4 } },
    { ...proposal, graph: "connected" },
  ];
  for (const bad of violations) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response({ choices: failureChoice({}, { content: JSON.stringify({ value: bad }) }) }); } });
    await expect(executor.execute(request)).rejects.toThrow("invalid_response");
    expect(calls).toBe(1);
    expect(executor.observations[0]).toMatchObject({ status: "failed", code: "invalid_response", dispatched: true, schemaDigest: digestCanonical(schema) });
    await executor.settle();
  }
});

test("contexts outside the protocol bounds reject before dispatch", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response(); } });
  const base = (request.context.inputs as Record<string, unknown>).context as Record<string, unknown>;
  for (const patch of [{ nodes: 3 }, { nodes: 17 }, { edges: 2 }, { edges: 7 }, { nodes: "4" }, { edges: 4.5 }]) {
    const context = { ...base, ...patch };
    await expect(executor.execute({ ...request, context: { inputs: { context } } })).rejects.toThrow("invalid_context");
  }
  expect(calls).toBe(0);
  expect(executor.observations.every((item) => item.dispatched === false && item.code === "invalid_context")).toBe(true);
  expect(executor.observations.every((item) => item.schemaDigest === undefined)).toBe(true);
});

test("completed provider failures are retained without retry, fallback, or raw error text", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async () => {
    calls++;
    return calls === 1 ? new Response(`private-provider-error:${selection.credential}`, { status: 429, headers: { "x-request-id": "req_rate_limit" } }) : response();
  } });
  await expect(executor.execute(request)).rejects.toThrow("provider_error");
  expect(calls).toBe(1);
  expect(executor.observations[0]).toMatchObject({ attempt: 1, status: "failed", code: "provider_error", httpStatus: 429, requestId: "req_rate_limit", dispatched: true, uncertain: false });
  expect(JSON.stringify(executor.observations)).not.toContain("private-provider-error");
  await executor.settle();
  await expect(executor.execute({ ...request, cellId: "next" })).resolves.toEqual(proposal);
  expect(calls).toBe(2);
});

test("requires one complete response from the explicitly selected model without tool calls", async () => {
  const cases: [Record<string, unknown>, string][] = [
    [{ model: "openai/other" }, "model_mismatch"],
    [{ model: undefined }, "model_mismatch"],
    [{ choices: [] }, "invalid_response"],
    [{ choices: [...failureChoice(), ...failureChoice()] }, "invalid_response"],
    [{ choices: failureChoice({ finish_reason: "length" }) }, "incomplete_response"],
    [{ choices: failureChoice({}, { tool_calls: [{ id: "unexpected", type: "function" }] }) }, "tool_calls_forbidden"],
    [{ choices: failureChoice({}, { function_call: { name: "unexpected" } }) }, "tool_calls_forbidden"],
    [{ choices: failureChoice({}, { content: JSON.stringify({ value: proposal, private: "extra" }) }) }, "invalid_response"],
    [{ choices: failureChoice({}, { content: "not valid JSON: private output" }) }, "invalid_response"],
    [{ choices: failureChoice({}, { content: '{"value":1e999}' }) }, "invalid_response"],
  ];
  for (const [overrides, code] of cases) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response(overrides); } });
    await expect(executor.execute(request)).rejects.toThrow(code);
    expect(calls).toBe(1);
    expect(executor.observations[0]).toMatchObject({ status: "failed", code, dispatched: true, uncertain: false });
    expect(JSON.stringify(executor.observations)).not.toContain("private output");
    await executor.settle();
  }
});

test("redirects are rejected without following a changed origin", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async (_url, init) => {
    calls++;
    expect(init?.redirect).toBe("error");
    return new Response("", { status: 307, headers: { location: "https://untrusted.invalid" } });
  } });
  await expect(executor.execute(request)).rejects.toThrow("redirect_forbidden");
  expect(calls).toBe(1);
  expect(executor.observations[0]).toMatchObject({ httpStatus: 307, code: "redirect_forbidden", uncertain: false });
});

test("response overflow and interrupted transport block all later dispatch and retain original failures", async () => {
  const fetchers: GatewayFetch[] = [
    async () => { throw new Error(`private transport ${selection.credential}`); },
    async () => new Response("x".repeat(1025)),
    async () => new Response("small", { headers: { "content-length": "1025" } }),
  ];
  for (const fetch of fetchers) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, maxResponseBytes: 1024, fetch: async (...args) => { calls++; return fetch(...args); } });
    await expect(executor.execute(request)).rejects.toThrow(/transport_error|response_limit/);
    await expect(executor.execute({ ...request, cellId: "next" })).rejects.toThrow("completion_uncertain");
    expect(calls).toBe(1);
    expect(executor.observations).toHaveLength(2);
    expect(executor.observations[0]).toMatchObject({ uncertain: true, dispatched: true, status: "failed" });
    expect(executor.observations[1]).toMatchObject({ attempt: 2, uncertain: true, dispatched: false, code: "completion_uncertain" });
    expect(JSON.stringify(executor.observations)).not.toContain(selection.credential);
    await expect(executor.settle()).rejects.toThrow("completion_uncertain");
  }
});

test("deadline bounds an uncooperative fetch and an unending response stream", async () => {
  const fetchers: GatewayFetch[] = [
    async () => new Promise<Response>(() => {}),
    async () => new Response(new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array([123])); } })),
  ];
  for (const fetch of fetchers) {
    const executor = createGatewayExecutor({ ...selection, timeoutMs: 10, fetch });
    const started = performance.now();
    await expect(executor.execute(request)).rejects.toThrow("deadline");
    expect(performance.now() - started).toBeLessThan(1000);
    expect(executor.observations[0]).toMatchObject({ status: "failed", code: "deadline", uncertain: true });
    await expect(executor.settle()).rejects.toThrow("completion_uncertain");
  }
});

test("cancellation before dispatch and during dispatch have distinct uncertainty, and concurrent calls do not dispatch", async () => {
  const before = new AbortController(); before.abort();
  let calls = 0;
  const inactive = createGatewayExecutor({ ...selection, signal: before.signal, fetch: async () => { calls++; return response(); } });
  await expect(inactive.execute(request)).rejects.toThrow("cancelled");
  expect(calls).toBe(0);
  expect(inactive.observations[0]).toMatchObject({ code: "cancelled", dispatched: false, uncertain: false });
  await inactive.settle();
  const during = new AbortController();
  let dispatched!: () => void;
  const entered = new Promise<void>((resolve) => { dispatched = resolve; });
  const active = createGatewayExecutor({ ...selection, timeoutMs: 100, fetch: async () => { calls++; dispatched(); return new Promise<Response>(() => {}); } });
  const pending = active.execute(request, during.signal);
  await entered;
  await expect(active.execute(request)).rejects.toThrow("executor_busy");
  during.abort();
  await expect(pending).rejects.toThrow("cancelled");
  expect(calls).toBe(1);
  expect(active.observations[0]).toMatchObject({ code: "cancelled", dispatched: true, uncertain: true });
  await expect(active.settle()).rejects.toThrow("completion_uncertain");
});

test("oversized proposal and invalid preflight requests cannot bypass local bounds", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, maxOutputBytes: 64, fetch: async () => { calls++; return response(); } });
  await expect(executor.execute(request)).rejects.toThrow("output_limit");
  expect(executor.observations[0]).toMatchObject({ code: "output_limit", dispatched: true, uncertain: false });
  const invalid = createGatewayExecutor({ ...selection, credential: "", fetch: async () => { calls++; return response(); } });
  await expect(invalid.execute(request)).rejects.toThrow("credential_unavailable");
  await expect(invalid.execute({ ...request, kind: "classifier" })).rejects.toThrow("unsupported_effect");
  await expect(invalid.execute({ ...request, prompt: "x".repeat(8193) })).rejects.toThrow("input_limit");
  expect(calls).toBe(1);
  expect(invalid.observations.every((item) => item.dispatched === false)).toBe(true);
});

test("native Gateway receipts reproduce a complete study offline without additional HTTP calls", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-gateway-")); roots.push(root);
  const directory = join(root, "study");
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, maxCalls: 6, fetch: async () => response({ id: `chatcmpl-${++calls}` }) });
  const report = await runStudy({ contract: "algal.lab.study.v1", name: "gateway-fixture", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }, directory, { executor });
  expect(calls).toBe(6);
  expect(report.attempts).toHaveLength(6);
  expect(executor.observations.every((item) => item.status === "completed")).toBe(true);
  const attempt = await new ArtifactStore(directory).get(report.attempts[0]!) as unknown as Attempt;
  expect(attempt.receipt.effects[0]).toMatchObject({ executor: executor.id, configurationDigest: executor.configurationDigest, retryable: false, usage: { model: "gpt-6-luna", tokensIn: 10, tokensOut: 20 }, requestDigest: executor.observations[0]!.requestDigest });
  const verified = await verifyStudy(directory);
  expect(verified).toMatchObject({ attempts: 6 });
  expect(calls).toBe(6);
  await executor.settle();
});
