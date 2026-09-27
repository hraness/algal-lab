import { afterEach, expect, test } from "bun:test";
import { type EffectRequest } from "@hraness/algal";
import { createLiveExecutor, MODEL } from "./live";

const originalFetch = globalThis.fetch;
const originalKey = process.env.AI_GATEWAY_API_KEY;
afterEach(() => {
  globalThis.fetch = originalFetch;
  if (originalKey === undefined) delete process.env.AI_GATEWAY_API_KEY;
  else process.env.AI_GATEWAY_API_KEY = originalKey;
});
const request: EffectRequest = { contract: "algal.effect.v1", kind: "agent", cellId: "task", prompt: "classify",
  context: { inputs: { message: "Butler: define entropy" } }, output: { kind: "choice", labels: ["respond", "silent"] },
  budget: { maxContextBytes: 32_768, maxOutputBytes: 8192 } };

test("Gateway wrapper pins origin/provider/model and enforces request limit before dispatch", async () => {
  process.env.AI_GATEWAY_API_KEY = "test-only-fake-gateway-key";
  let calls = 0;
  globalThis.fetch = (async (url, init) => {
    calls++;
    expect(String(url)).toBe("https://ai-gateway.vercel.sh/v1/chat/completions");
    const body = JSON.parse(String(init?.body));
    expect(body.providerOptions).toEqual({ gateway: { only: ["openai"] } });
    expect(body.model).toBe(MODEL);
    expect(body.max_tokens).toBe(1024);
    expect(body.store).toBe(false);
    return Response.json({ model: MODEL, choices: [{ finish_reason: "stop", message: { content: '{"value":"respond"}' } }],
      usage: { prompt_tokens: 100, completion_tokens: 8 } });
  }) as typeof fetch;
  const executor = createLiveExecutor({ maxCalls: 1, maxEstimatedUSD: 1 });
  expect(await executor.execute(request)).toBe("respond");
  await expect(executor.execute(request)).rejects.toThrow("budget exhausted");
  expect(calls).toBe(1);
  expect(executor.observations[0]?.inputTokens).toBe(100);
});

test("uncertain transport halts subsequent dispatch; preflight spend refusal sends nothing", async () => {
  process.env.AI_GATEWAY_API_KEY = "test-only-fake-gateway-key";
  let calls = 0;
  globalThis.fetch = Object.assign(async (): Promise<Response> => { calls++; throw new Error("connection lost"); }, { preconnect: originalFetch.preconnect });
  const executor = createLiveExecutor({ maxCalls: 10, maxEstimatedUSD: 1 });
  await expect(executor.execute(request)).rejects.toThrow();
  await expect(executor.execute(request)).rejects.toThrow("unavailable");
  expect(calls).toBe(1);
  expect(executor.observations[0]?.uncertain).toBe(true);
  const noSpend = createLiveExecutor({ maxCalls: 10, maxEstimatedUSD: 0.000000001 });
  await expect(noSpend.execute(request)).rejects.toThrow();
  expect(calls).toBe(1);
  expect(noSpend.observations[0]?.uncertain).toBe(false);
});
