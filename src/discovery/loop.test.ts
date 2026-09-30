import { afterEach, describe, expect, spyOn, test } from "bun:test";
import { readFileSync } from "node:fs";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import example from "../../examples/discovery-local.json";
import proposal from "../../examples/discovery-proposal.json";
import { parseConfig, type Config, type Provider } from "./contracts";
import { abandon, confirm, context, init, propose, seal, spent, step } from "./loop";
import { load, save, unlock, withRun } from "./store";
import { checkTrajectory } from "./evaluator";
import { simulate } from "../network";
import { decodeResponse, requestModel, type RemoteProvider } from "./providers";
import { main } from "../../scripts/discovery";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true }))); });
async function directory(): Promise<string> { const root = await mkdtemp(join(tmpdir(), "algal-discovery-test-")); roots.push(root); return join(root, "run"); }
function config(changes: Partial<Config> = {}): Config { return parseConfig({ ...example, ...changes }); }
const remote: RemoteProvider = { kind: "xai", model: "fixture-model", concurrency: 2, proposalsPerCall: 2, maxInputTokens: 32000, maxOutputTokens: 1000, timeoutMs: 1000, reserveUsdPerCall: 0.01 };
function remoteConfig(provider: Provider = remote): Config { return config({ provider, budget: { attempts: 8, activeMs: 20000, modelCalls: 4, tokens: 100000, usd: 0.04 } }); }
const goodOutput = JSON.stringify({ proposals: [proposal, proposal] });

describe("resumable finite discovery", () => {
  test("documented CLI commands produce and resume a finite run", async () => {
    const out = await directory();
    const configPath = new URL("../../examples/discovery-local.json", import.meta.url).pathname;
    await main(["init", "--config", configPath, "--out", out]);
    await main(["run", out, "--steps", "4"]);
    expect((await load(out)).state.attempts).toHaveLength(4);
    const stopped = await main(["run", out, "--steps", "9"]) as { stop: string };
    expect(stopped.stop).toContain("budget exhausted");
    expect((await load(out)).state.attempts).toHaveLength(12);
    await main(["seal", out]); await main(["confirm", out]);
    expect((await load(out)).state.phase).toBe("confirmed");
    await expect(main(["step", out, "--unbounded"])).rejects.toThrow("unknown");
  });
  test("retains attempts, parents and predictions; freezes selection before holdout", async () => {
    const out = await directory();
    await init(config(), out);
    await expect(confirm(out)).rejects.toThrow("seal");
    for (let n = 0; n < 12; n++) await step(out);
    const { config: c, state } = await load(out);
    expect(state.attempts).toHaveLength(12);
    expect(state.attempts.some(a => a.status === "promoted")).toBe(true);
    expect(state.attempts.some(a => a.status === "rejected" || a.status === "duplicate")).toBe(true);
    let score = state.baseline!.development;
    for (const a of state.attempts) if (a.status === "promoted") { expect(a.scores!.development).toBeGreaterThan(score); expect(a.independentCheck).toBe(true); score = a.scores!.development; }
    expect(spent(c, state)).toEqual({ attempts: 12, activeMs: 13000, modelCalls: 0, tokens: 0, usd: 0 });
    await expect(step(out)).rejects.toThrow("budget exhausted");
    const frozen = await seal(out);
    const confirmed = await confirm(out);
    expect(confirmed.incumbent).toBe(frozen.incumbent);
    expect(confirmed.confirmation?.independentCheck).toBe(true);
    const bytes = await readFile(join(out, "state.json"), "utf8");
    await confirm(out);
    expect(await readFile(join(out, "state.json"), "utf8")).toBe(bytes);
    await expect(step(out)).rejects.toThrow("sealed");
    expect(spent(c, confirmed).activeMs).toBe(15000);
    const contextJson = JSON.stringify(context(c, confirmed));
    expect(contextJson).not.toContain("holdout");
    expect(contextJson).not.toContain("confirmation");
    for (const seed of c.holdoutSeeds) expect(contextJson).not.toContain(String(seed));
  });
  test("invalid and duplicate proposals are preserved without executing model commands", async () => {
    const out = await directory(); await init(config(), out);
    const invalid = await propose(out, { ...proposal, command: "touch unsafe" }, "baseline");
    expect(invalid.status).toBe("invalid"); expect(invalid.input).toContain("touch unsafe");
    const duplicate = await propose(out, { ...proposal, graph: example.baseline }, "baseline");
    expect(duplicate.status).toBe("duplicate");
    await expect(propose(out, proposal, "nonexistent")).rejects.toThrow("unknown parent");
    const state = (await load(out)).state;
    expect(state.attempts).toHaveLength(2);
    expect(state.attempts[0]?.proposal).toBeNull();
  });
  test("input counts, unknown config fields and overlapping schedules fail closed", () => {
    expect(() => parseConfig({ ...example, command: "echo wrong" })).toThrow("unknown field");
    expect(() => config({ holdoutSeeds: [11] })).toThrow("disjoint");
    expect(() => config({ budget: { ...example.budget, activeMs: 2999 } })).toThrow("final confirmation");
  });
  test("baseline timeout retains its prior reservation and leaves an inspectable terminal run", async () => {
    const out = await directory(); const c = config();
    let tick = 0; let reservedBeforeEvaluation = false;
    const clock = spyOn(performance, "now").mockImplementation(() => {
      const envelope = JSON.parse(readFileSync(join(out, "state.json"), "utf8"));
      reservedBeforeEvaluation = envelope.state.phase === "initializing" && envelope.state.baseline === null && spent(c, envelope.state).activeMs === c.evaluationTimeoutMs;
      return ++tick * c.evaluationTimeoutMs * 2;
    });
    try { await expect(init(c, out)).rejects.toThrow("evaluation time limit"); }
    finally { clock.mockRestore(); }
    expect(reservedBeforeEvaluation).toBe(true);
    const { state } = await load(out);
    expect(state.phase).toBe("initialization-failed"); expect(state.baseline).toBeNull();
    const result = await main(["status", out]) as { incumbent: unknown; initialization: { status: string; reservedMs: number }; reserved: Config["budget"] };
    expect(result.incumbent).toBeNull(); expect(result.initialization.status).toBe("failed");
    expect(result.initialization.reservedMs).toBe(c.evaluationTimeoutMs);
    expect(result.reserved).toEqual({ attempts: 0, activeMs: c.evaluationTimeoutMs, modelCalls: 0, tokens: 0, usd: 0 });
    const bytes = await readFile(join(out, "state.json"), "utf8");
    await expect(step(out)).rejects.toThrow("baseline evaluation");
    await expect(propose(out, proposal, "baseline")).rejects.toThrow("baseline evaluation");
    await expect(seal(out)).rejects.toThrow("baseline evaluation");
    await expect(confirm(out)).rejects.toThrow("baseline evaluation");
    expect(await readFile(join(out, "state.json"), "utf8")).toBe(bytes);
    // A hard interruption preserves the earlier initializing record, never scores.
    state.phase = "initializing"; await save(out, state);
    expect((await main(["status", out]) as typeof result).initialization.status).toBe("in progress or interrupted");
    await expect(step(out)).rejects.toThrow("baseline evaluation");
    expect(spent(c, (await load(out)).state).activeMs).toBe(c.evaluationTimeoutMs);
  });
  test("changed config, state digest or implementation identity stops resumption", async () => {
    const out = await directory(); await init(config(), out);
    const { state } = await load(out);
    state.sourceHash = "0".repeat(64); await save(out, state);
    await expect(load(out)).rejects.toThrow("source");
    await writeFile(join(out, "state.json"), '{"digest":"wrong","state":{}}');
    await expect(load(out)).rejects.toThrow("digest mismatch");
  });
  test("independent trajectory checker catches altered removals and metrics", () => {
    const valid = simulate(example.baseline as Config["baseline"], { kind: "random", seed: 5, steps: 3 });
    checkTrajectory(valid);
    const wrong = structuredClone(valid); wrong.trajectory[1]!.largestComponent = 0;
    expect(() => checkTrajectory(wrong)).toThrow("mismatch");
    const metric = structuredClone(valid); metric.metrics.auc += 0.01;
    expect(() => checkTrajectory(metric)).toThrow("metric");
    checkTrajectory(simulate(example.baseline as Config["baseline"], { kind: "targeted", seed: 5, steps: 3 }));
  });
  test("live lock is neither stolen nor released by recovery", async () => {
    const out = await directory(); await init(config(), out);
    await withRun(out, async () => {
      await expect(step(out)).rejects.toThrow("locked");
      await expect(unlock(out)).rejects.toThrow("still present");
    });
    await step(out);
  });
  test("an interrupted local evaluation keeps its charge and cannot be replayed", async () => {
    const out = await directory(); await init(config(), out); await step(out);
    const { config: c, state } = await load(out);
    state.attempts[0]!.status = "evaluating"; state.incumbent = "baseline";
    await save(out, state); await step(out);
    const after = (await load(out)).state;
    expect(after.attempts[0]!.reason).toContain("interrupted");
    expect(spent(c, after).attempts).toBe(2);
    expect(spent(c, after).activeMs).toBe(3000);
  });
  test("interrupted final evaluation stays sealed and is not repeated", async () => {
    const out = await directory(); await init(config(), out); await seal(out);
    const { config: c, state } = await load(out); state.phase = "confirming"; await save(out, state);
    await expect(confirm(out)).rejects.toThrow("interrupted");
    await expect(step(out)).rejects.toThrow("sealed");
    expect(spent(c, state).activeMs).toBe(3000);
  });
});

describe("bounded provider dispatch (mock transport only)", () => {
  for (const kind of ["xai", "gemini"] as const) {
    const body = (truncated: boolean, outputTokens: number) => kind === "xai" ? {
      id: "retained-xai-response", model: "reported-fixture-model", choices: [{ finish_reason: truncated ? "length" : "stop", message: { content: goodOutput } }], usage: { prompt_tokens: 3, completion_tokens: outputTokens },
    } : {
      responseId: "retained-gemini-response", modelVersion: "reported-fixture-model", candidates: [{ finishReason: truncated ? "MAX_TOKENS" : "STOP", content: { parts: [{ text: goodOutput }] } }], usageMetadata: { promptTokenCount: 3, candidatesTokenCount: 1, thoughtsTokenCount: outputTokens - 1 },
    };
    test(`${kind} truncated overage retains known evidence and cannot be abandoned to resume spending`, async () => {
      const out = await directory(); const c = remoteConfig({ ...remote, kind, concurrency: 1 }); await init(c, out);
      let calls = 0;
      const transport: typeof requestModel = async (provider, id, prompt, options) => requestModel(provider, id, prompt, {
        ...options, env: { XAI_API_KEY: "fixture-only", GEMINI_API_KEY: "fixture-only" }, fetch: async () => { calls++; return new Response(JSON.stringify(body(true, 25_000_001)), { status: 200 }); },
      });
      await step(out, { live: true, transport });
      const state = (await load(out)).state; const request = state.requests[0]!;
      expect(request.status).toBe("uncertain"); expect(request.responseId).toBe(`retained-${kind}-response`);
      expect(request.reportedModel).toBe("reported-fixture-model"); expect(request.response).toBe(goodOutput);
      expect(request.usage).toEqual({ inputTokens: 3, outputTokens: 25_000_001 });
      expect(request.error).toContain("reported tokens exceeded"); expect(state.attempts).toHaveLength(0);
      await expect(abandon(out, request.id)).rejects.toThrow("exceeded");
      await expect(step(out, { live: true, transport })).rejects.toThrow("unresolved"); expect(calls).toBe(1);
    });
    test(`${kind} truncation within reservation retains evidence but requires abandonment before a new request`, async () => {
      const out = await directory(); const c = remoteConfig({ ...remote, kind, concurrency: 1 }); await init(c, out);
      let calls = 0;
      const transport: typeof requestModel = async (provider, id, prompt, options) => requestModel(provider, id, prompt, {
        ...options, env: { XAI_API_KEY: "fixture-only", GEMINI_API_KEY: "fixture-only" }, fetch: async () => { calls++; return new Response(JSON.stringify(body(calls === 1, 7)), { status: 200 }); },
      });
      const first = await step(out, { live: true, transport }); const request = first.requests[0]!;
      expect(request.status).toBe("uncertain"); expect(request.responseId).toBe(`retained-${kind}-response`);
      expect(request.reportedModel).toBe("reported-fixture-model"); expect(request.response).toBe(goodOutput);
      expect(request.usage).toEqual({ inputTokens: 3, outputTokens: 7 }); expect(request.error).toContain("did not finish normally");
      expect(first.attempts).toHaveLength(0);
      await expect(step(out, { live: true, transport })).rejects.toThrow("unresolved"); expect(calls).toBe(1);
      const charged = spent(c, first); await abandon(out, request.id);
      const abandoned = (await load(out)).state;
      expect(spent(c, abandoned)).toEqual(charged); expect(abandoned.requests[0]?.response).toBe(goodOutput);
      const second = await step(out, { live: true, transport }); expect(calls).toBe(2);
      expect(second.requests[0]?.status).toBe("abandoned"); expect(second.requests[1]?.id).not.toBe(request.id);
      expect(second.attempts).toHaveLength(2); expect(second.requests[1]?.status).toBe("completed");
    });
  }
  test("a fast response survives interruption while a sibling remains pending", async () => {
    const out = await directory(); const interrupted = await directory(); await init(remoteConfig(), out);
    let releaseSlow!: () => void;
    const stalled = new Promise<void>(resolve => { releaseSlow = resolve; });
    const running = step(out, { live: true, transport: async (_provider, id) => {
      if (id.endsWith("-2")) { await stalled; throw new Error("simulated interrupted sibling"); }
      return { responseId: "fast-response", text: goodOutput, usage: null };
    } });
    try {
      let snapshot = (await load(out)).state;
      const deadline = Date.now() + 2000;
      while (snapshot.requests[0]?.status !== "completed" && Date.now() < deadline) {
        await new Promise(resolve => setTimeout(resolve, 2)); snapshot = (await load(out)).state;
      }
      expect(snapshot.requests[0]?.responseId).toBe("fast-response");
      expect(snapshot.requests[1]?.status).toBe("pending");
      expect(snapshot.attempts).toHaveLength(0);
      // Reconstruct the exact durable files present at this interruption point.
      await mkdir(interrupted); await copyFile(join(out, "config.json"), join(interrupted, "config.json"));
      await copyFile(join(out, "state.json"), join(interrupted, "state.json"));
      let calls = 0;
      const noRedispatch: typeof requestModel = async () => { calls++; throw new Error("must not send"); };
      await expect(step(interrupted, { live: true, transport: noRedispatch })).rejects.toThrow("unresolved");
      await abandon(interrupted, snapshot.requests[1]!.id);
      const recovered = await step(interrupted, { transport: noRedispatch });
      expect(calls).toBe(0); expect(recovered.attempts).toHaveLength(2);
      expect(recovered.requests[0]?.responseId).toBe("fast-response");
      expect(spent(remoteConfig(), recovered).attempts).toBe(4);
    } finally { releaseSlow(); await running; }
  });
  test("requires live opt-in and reserves all parallel slots before the first request", async () => {
    const out = await directory(); await init(remoteConfig(), out);
    let calls = 0; let active = 0; let maxActive = 0;
    const transport: typeof requestModel = async (_p, id) => {
      calls++; active++; maxActive = Math.max(maxActive, active);
      const saved = (await load(out)).state;
      expect(saved.requests).toHaveLength(2);
      expect(saved.requests.every(r => r.status === "pending")).toBe(true);
      await new Promise(resolve => setTimeout(resolve, 10)); active--;
      return { responseId: `fixture-${id}`, text: goodOutput, usage: { inputTokens: 10, outputTokens: 20 } };
    };
    await expect(step(out, { transport })).rejects.toThrow("--live"); expect(calls).toBe(0);
    const state = await step(out, { live: true, transport });
    expect(calls).toBe(2); expect(maxActive).toBe(2); expect(state.attempts).toHaveLength(4);
    expect(state.requests.every(r => r.status === "completed")).toBe(true);
    expect(new Set(state.attempts.map(a => a.id)).size).toBe(4);
    expect(spent(remoteConfig(), state).usd).toBe(0.02);
    expect(state.attempts.every(a => a.parent === "baseline")).toBe(true);
  });
  test("timeouts remain uncertain, consume all reservations and are never retried", async () => {
    const out = await directory(); const c = remoteConfig({ ...remote, concurrency: 1 }); await init(c, out);
    let calls = 0;
    const transport: typeof requestModel = async () => { calls++; throw new Error("fixture timeout with secret-detail"); };
    const state = await step(out, { live: true, transport });
    expect(state.requests[0]!.status).toBe("uncertain");
    expect(JSON.stringify(state)).not.toContain("secret-detail");
    await expect(step(out, { live: true, transport })).rejects.toThrow("unresolved"); expect(calls).toBe(1);
    const charged = spent(c, state);
    await abandon(out, state.requests[0]!.id);
    expect(spent(c, (await load(out)).state)).toEqual(charged);
  });
  test("saved responses resume interpretation without another model call", async () => {
    const out = await directory(); const c = remoteConfig({ ...remote, concurrency: 1 }); await init(c, out);
    const state = await step(out, { live: true, transport: async () => ({ responseId: "fixture-r1", text: goodOutput, usage: null }) });
    state.attempts = []; state.incumbent = "baseline"; await save(out, state);
    let calls = 0;
    const resumed = await step(out, { transport: async () => { calls++; throw new Error("must not send"); } });
    expect(calls).toBe(0); expect(resumed.attempts).toHaveLength(2); expect(resumed.requests).toHaveLength(1);
    expect(spent(c, resumed).modelCalls).toBe(1);
  });
  test("zero money or insufficient token allowance prevents every request", async () => {
    for (const budget of [{ ...remoteConfig().budget, usd: 0 }, { ...remoteConfig().budget, tokens: 1 }]) {
      const out = await directory(); await init(config({ provider: remote, budget }), out);
      let calls = 0;
      await expect(step(out, { live: true, transport: async () => { calls++; throw new Error("must not send"); } })).rejects.toThrow("budget exhausted");
      expect(calls).toBe(0); expect((await load(out)).state.requests).toHaveLength(0);
    }
  });
  test("excess reported tokens stop this run rather than refunding or hiding them", async () => {
    const out = await directory(); await init(remoteConfig({ ...remote, concurrency: 1 }), out);
    const state = await step(out, { live: true, transport: async () => ({ responseId: "fixture-usage", text: goodOutput, usage: { inputTokens: 100000, outputTokens: 20 } }) });
    expect(state.requests[0]!.status).toBe("uncertain");
    await expect(abandon(out, state.requests[0]!.id)).rejects.toThrow("exceeded");
    await expect(step(out)).rejects.toThrow("unresolved");
  });
  test("malformed proposal bundle retains all failed planned slots", async () => {
    const out = await directory(); await init(remoteConfig({ ...remote, concurrency: 1 }), out);
    const state = await step(out, { live: true, transport: async () => ({ responseId: "fixture-bad", text: '{"command":"unsafe"}', usage: null }) });
    expect(state.attempts).toHaveLength(2);
    expect(state.attempts.every(a => a.status === "invalid")).toBe(true);
    expect(state.requests[0]?.response).toContain("unsafe");
  });
  test("xAI and Gemini wire adapters keep secrets in headers and reject tool output", async () => {
    const responses = [
      { provider: remote, body: { id: "xai-fixture", choices: [{ finish_reason: "stop", message: { content: goodOutput } }], usage: { prompt_tokens: 3, completion_tokens: 7 } }, key: "XAI_API_KEY", host: "api.x.ai" },
      { provider: { ...remote, kind: "gemini" as const }, body: { responseId: "gemini-fixture", candidates: [{ finishReason: "STOP", content: { parts: [{ text: goodOutput }] } }], usageMetadata: { promptTokenCount: 3, candidatesTokenCount: 5, thoughtsTokenCount: 2 } }, key: "GEMINI_API_KEY", host: "generativelanguage.googleapis.com" },
    ];
    for (const fixture of responses) {
      let calls = 0;
      const result = await requestModel(fixture.provider, "request-fixture", "proposal context", { live: true, env: { [fixture.key]: "fixture-secret" }, fetch: async (input, options) => {
        calls++; expect(new URL(String(input)).host).toBe(fixture.host); expect(options?.redirect).toBe("error");
        expect(String(options?.body)).not.toContain("fixture-secret");
        expect(JSON.stringify(options?.headers)).toContain("fixture-secret");
        return new Response(JSON.stringify(fixture.body), { status: 200 });
      } });
      expect(calls).toBe(1); expect(result.usage).toEqual({ inputTokens: 3, outputTokens: 7 });
    }
    expect(decodeResponse(remote, { id: "x", choices: [{ finish_reason: "stop", message: { content: goodOutput, tool_calls: [] } }] }).completionError).toContain("tool");
    await expect(requestModel(remote, "request-fixture", "context", { live: false, env: { XAI_API_KEY: "fixture" } })).rejects.toThrow("--live");
  });
});
