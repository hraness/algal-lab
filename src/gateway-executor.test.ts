import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { digestCanonical, effectRequestDigest, type EffectRequest, type GatewayFetch } from "@hraness/algal";
import { ArtifactStore } from "./artifacts";
import { json, proposalContractSchema, PROPOSAL_CONTRACT } from "./contracts";
import { createGatewayExecutor, GATEWAY_DEFAULT_MAX_CALLS, GATEWAY_MAX_CALLS } from "./gateway-executor";
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
  for (const change of [{ provider: "azure-openai" }, { model: "openai/catalog-fixture" }, { maxCalls: 1 }, { maxCalls: 400 }, { timeoutMs: 5000 }, { maxOutputBytes: 4096 }, { maxResponseBytes: 32768 }]) {
    expect(createGatewayExecutor({ ...selection, ...change }).configurationDigest).not.toBe(normal.configurationDigest);
  }
  for (const change of [{ maxCalls: 401 }, { maxCalls: 0 }, { timeoutMs: 60001 }, { maxOutputBytes: 8193 }, { maxResponseBytes: 65537 }, { maxCalls: NaN }, { maxCalls: 12.5 }, { model: "auto" }, { provider: "openai/other" }, { retries: 1 }, { signal: {} }, { fetch: "url" }]) {
    expect(() => createGatewayExecutor({ ...selection, ...change } as never)).toThrow();
  }
  expect(Object.isFrozen(schema)).toBe(true);
  expect(Object.isFrozen(normal.configuration)).toBe(true);
  expect(JSON.stringify(normal.configuration)).not.toContain(selection.credential);
});

test("the call budget defaults to the twelve-call smoke and is configurable only up to the replicated-comparison cap", async () => {
  expect(GATEWAY_DEFAULT_MAX_CALLS).toBe(12);
  expect(GATEWAY_MAX_CALLS).toBe(400);
  expect(createGatewayExecutor(selection).configuration.maxCalls).toBe(12);
  expect(createGatewayExecutor({ ...selection, maxCalls: 12 }).configurationDigest).toBe(createGatewayExecutor(selection).configurationDigest);
  let calls = 0;
  const wide = createGatewayExecutor({ ...selection, maxCalls: 400, fetch: async () => { calls++; return response({ id: `chatcmpl-${calls}` }); } });
  expect(wide.configuration.maxCalls).toBe(400);
  for (let index = 0; index < 14; index++) await expect(wide.execute({ ...request, cellId: `cell-${index}` })).resolves.toEqual(proposal);
  expect(calls).toBe(14);
  expect(wide.observations).toHaveLength(14);
  expect(wide.observations[13]).toMatchObject({ attempt: 14, status: "completed" });
  await wide.settle();
});

test("null usage in a completed generation is treated as absent and the billed generation is retained", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response({ usage: null }); } });
  const result = await executor.executeEffect!(request);
  expect(calls).toBe(1);
  expect(result.output).toEqual(proposal);
  expect(result.metadata?.usage).toEqual({ model: "gpt-6-luna" });
  expect(executor.observations[0]).toMatchObject({ status: "completed", dispatched: true, uncertain: false, httpStatus: 200, responseId: "chatcmpl-fixture", finishReason: "stop" });
  expect(executor.observations[0]).not.toHaveProperty("usage");
  expect(executor.observations[0]).not.toHaveProperty("code");
  // A malformed usage record is still not a usage record; usage stays absent without failing the generation.
  const malformed = createGatewayExecutor({ ...selection, fetch: async () => response({ usage: "unknown" }) });
  await expect(malformed.execute(request)).rejects.toThrow("invalid_response");
  await executor.settle();
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

const violations = [
  { ...proposal, graph: { nodes: 4, edges: [...proposal.graph.edges, [0, 2]] } },
  { ...proposal, graph: { nodes: 4, edges: proposal.graph.edges.slice(1) } },
  { ...proposal, graph: { nodes: 5, edges: proposal.graph.edges } },
  { ...proposal, graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 4]] } },
  { ...proposal, graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 3.5]] } },
  { ...proposal, graph: { nodes: 4 } },
  { ...proposal, graph: "connected" },
];

test("provider output outside the exact budget contract reaches host admission as data instead of being discarded", async () => {
  for (const bad of violations) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response({ choices: failureChoice({}, { content: JSON.stringify({ value: bad }) }) }); } });
    // The executor is transport: it hands over the bounded value and lets host parseProposal judge it.
    await expect(executor.execute(request)).resolves.toEqual(bad);
    expect(calls).toBe(1);
    expect(executor.observations[0]).toMatchObject({ status: "completed", dispatched: true, uncertain: false, schemaDigest: digestCanonical(schema) });
    expect(executor.observations[0]).not.toHaveProperty("code");
    expect(executor.observations[0]).not.toHaveProperty("rejected");
    await executor.settle();
  }
});

test("a rejected proposal stays inside the recorded effect receipt and the study still verifies offline", async () => {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-gateway-rejected-")); roots.push(root);
  const directory = join(root, "study");
  let calls = 0;
  const served: unknown[] = [];
  const executor = createGatewayExecutor({ ...selection, maxCalls: 6, fetch: async () => {
    const bad = violations[calls++ % 2]!; // over budget, then under budget
    served.push(bad);
    return response({ id: `chatcmpl-${calls}`, choices: failureChoice({}, { content: JSON.stringify({ value: bad }) }) });
  } });
  const report = await runStudy({ contract: "algal.lab.study.v1", name: "gateway-rejected", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }, directory, { executor });
  expect(calls).toBe(6);
  expect(report.summaries.every((summary) => summary.validExperiments === 0)).toBe(true);
  const store = new ArtifactStore(directory);
  for (const [index, reference] of report.attempts.entries()) {
    const attempt = await store.get(reference) as unknown as Attempt;
    expect(attempt.measurement).toBeNull();
    expect(attempt.receipt.outcome).not.toBe("complete");
    const effect = attempt.receipt.effects.find((item) => item.executor === executor.id)!;
    expect(effect.output).toEqual(served[index] as never);
    expect(effect).not.toHaveProperty("error");
    expect(effect.usage).toEqual({ model: "gpt-6-luna", tokensIn: 10, tokensOut: 20 });
    expect(JSON.stringify(attempt.receipt)).toContain("proposal must preserve protocol node and edge budgets");
  }
  expect(executor.observations.every((item) => item.status === "completed" && item.code === undefined)).toBe(true);
  expect(await verifyStudy(directory)).toMatchObject({ attempts: 6, experiments: 0 });
  expect(calls).toBe(6);
  await executor.settle();
});

test("a wrapper outside the strict schema is a contract violation whose bounded value is retained without wrapper chatter", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response({ choices: failureChoice({}, { content: JSON.stringify({ value: proposal, private: "wrapper chatter" }) }) }); } });
  await expect(executor.execute(request)).rejects.toThrow("gateway application: contract_violation");
  expect(calls).toBe(1);
  expect(executor.observations[0]).toMatchObject({ status: "failed", code: "contract_violation", dispatched: true, uncertain: false, httpStatus: 200, rejected: proposal });
  expect(Object.isFrozen(executor.observations[0]!.rejected)).toBe(true);
  expect(JSON.stringify(executor.observations)).not.toContain("wrapper chatter");
  expect(JSON.stringify(executor.observations)).not.toContain("private");
  // The retained value is bounded by the same byte limit as admitted output, so it never exceeds 8 KiB.
  const oversized = createGatewayExecutor({ ...selection, maxOutputBytes: 64, fetch: async () => response({ choices: failureChoice({}, { content: JSON.stringify({ value: proposal, private: "wrapper chatter" }) }) }) });
  await expect(oversized.execute(request)).rejects.toThrow("output_limit");
  expect(oversized.observations[0]).toMatchObject({ code: "output_limit" });
  expect(oversized.observations[0]).not.toHaveProperty("rejected");
  // A credential echo is never retained, whatever else is wrong with the response.
  const echoed = createGatewayExecutor({ ...selection, fetch: async () => response({ choices: failureChoice({}, { content: JSON.stringify({ value: { ...proposal, rationale: selection.credential }, private: "wrapper chatter" }) }) }) });
  await expect(echoed.execute(request)).rejects.toThrow("invalid_response");
  expect(echoed.observations[0]).not.toHaveProperty("rejected");
  expect(JSON.stringify(echoed.observations)).not.toContain(selection.credential);
  // Malformed transport that leaves nothing admissible stays invalid_response, distinct from a contract violation.
  const malformed = createGatewayExecutor({ ...selection, fetch: async () => response({ choices: failureChoice({}, { content: JSON.stringify({ result: proposal }) }) }) });
  await expect(malformed.execute(request)).rejects.toThrow("invalid_response");
  expect(malformed.observations[0]).not.toHaveProperty("rejected");
  await executor.settle();
});

test("contexts outside the protocol bounds reject before dispatch", async () => {
  let calls = 0;
  const executor = createGatewayExecutor({ ...selection, fetch: async () => { calls++; return response(); } });
  const base = (request.context.inputs as Record<string, unknown>).context as Record<string, unknown>;
  for (const patch of [{ nodes: 3 }, { nodes: 17 }, { edges: 2 }, { edges: 7 }, { nodes: "4" }, { edges: 4.5 }]) {
    const context = { ...base, ...patch };
    await expect(executor.execute({ ...request, context: { inputs: { context } } })).rejects.toThrow("invalid_context");
  }
  await expect(executor.execute({ ...request, context: { inputs: { context: null } } })).rejects.toThrow("invalid_context");
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
    [{ choices: failureChoice({}, { content: JSON.stringify({ value: proposal, private: "extra" }) }) }, "contract_violation"],
    [{ choices: failureChoice({}, { content: JSON.stringify({ private: "output" }) }) }, "invalid_response"],
    [{ choices: failureChoice({}, { content: JSON.stringify([proposal]) }) }, "invalid_response"],
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

test("interrupted transport after dispatch latches later calls, which record the latching attempt rather than their own failure", async () => {
  const fetchers: [GatewayFetch, string][] = [
    [async () => { throw new Error(`private transport ${selection.credential}`); }, "transport_error"],
    [async () => new Response(new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array([123])); controller.error(new Error(`private stream ${selection.credential}`)); } })), "transport_error"],
    [async () => new Promise<Response>(() => {}), "deadline"],
  ];
  for (const [fetch, code] of fetchers) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, maxResponseBytes: 1024, timeoutMs: 50, fetch: async (...args) => { calls++; return fetch(...args); } });
    await expect(executor.execute(request)).rejects.toThrow(code);
    await expect(executor.execute({ ...request, cellId: "next" })).rejects.toThrow("completion_uncertain");
    await expect(executor.execute({ ...request, cellId: "later" })).rejects.toThrow("completion_uncertain");
    expect(calls).toBe(1);
    expect(executor.observations).toHaveLength(3);
    expect(executor.observations[0]).toMatchObject({ attempt: 1, code, uncertain: true, dispatched: true, status: "failed" });
    expect(executor.observations[0]).not.toHaveProperty("latchedBy");
    expect(executor.observations[1]).toMatchObject({ attempt: 2, uncertain: true, dispatched: false, code: "completion_uncertain", latchedBy: 1 });
    expect(executor.observations[2]).toMatchObject({ attempt: 3, uncertain: true, dispatched: false, code: "completion_uncertain", latchedBy: 1 });
    expect(JSON.stringify(executor.observations)).not.toContain(selection.credential);
    await expect(executor.settle()).rejects.toThrow("completion_uncertain");
  }
});

test("an oversized response after a received status fails only its own call and does not latch later dispatch", async () => {
  const fetchers: GatewayFetch[] = [
    async () => new Response("x".repeat(1025), { headers: { "x-request-id": "req_overflow" } }),
    async () => new Response("small", { headers: { "content-length": "1025", "x-request-id": "req_overflow" } }),
    async () => new Response(new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array(600)); controller.enqueue(new Uint8Array(600)); controller.close(); } })),
  ];
  for (const fetch of fetchers) {
    let calls = 0;
    const executor = createGatewayExecutor({ ...selection, maxResponseBytes: 1024, fetch: async (...args) => calls++ === 0 ? fetch(...args) : response() });
    await expect(executor.execute(request)).rejects.toThrow("gateway application: response_limit");
    expect(executor.observations[0]).toMatchObject({ attempt: 1, code: "response_limit", uncertain: false, dispatched: true, status: "failed", httpStatus: 200 });
    expect(executor.observations[0]).not.toHaveProperty("latchedBy");
    await executor.settle();
    await expect(executor.execute({ ...request, cellId: "next" })).resolves.toEqual(proposal);
    expect(calls).toBe(2);
    expect(executor.observations[1]).toMatchObject({ attempt: 2, status: "completed", uncertain: false, dispatched: true });
    expect(executor.observations[1]).not.toHaveProperty("latchedBy");
    await executor.settle();
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
