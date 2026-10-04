import { afterEach, expect, spyOn, test } from "bun:test";
import { cp, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import example from "../../examples/discovery-local.json";
import proposal from "../../examples/discovery-proposal.json";
import { main } from "../../scripts/discovery";
import { abandon, confirm, init, propose, seal, step } from "./loop";
import { load, save, withRun } from "./store";
import { verify } from "./verify";
import * as evaluator from "./evaluator";
import { hash } from "./contracts";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true }))); });
async function directory() { const root = await mkdtemp(join(tmpdir(), "algal-verify-test-")); roots.push(root); return join(root, "run"); }
async function run() { const out = await directory(); await init(example, out); for (let i = 0; i < 4; i++) await step(out); return out; }

test("offline verification reproduces observed decisions and never evaluates an unseen holdout", async () => {
  const out = await run();
  await propose(out, { ...proposal, command: "not executable" }, "baseline");
  const before = await readFile(join(out, "state.json"), "utf8");
  const result = await main(["verify", out]) as Awaited<ReturnType<typeof verify>>;
  expect(result.verified).toBe(true);
  expect(result.handoffReady).toBe(true);
  expect(result.confirmationReproduced).toBe(false);
  expect(result.retainedFailures).toBe(1);
  expect(result.reproducedEvaluations).toBeGreaterThan(1);
  expect(await readFile(join(out, "state.json"), "utf8")).toBe(before);
  await seal(out); await confirm(out);
  expect((await verify(out)).confirmationReproduced).toBe(true);
  const copied = await directory(); await cp(out, copied, { recursive: true });
  expect(await verify(copied)).toEqual(await verify(out));
  await expect(main(["verify", out, "--live"])).rejects.toThrow("unexpected");
});

test("a copied exploring run continues without resetting attempts or reservations", async () => {
  const original = await run();
  const snapshot = await verify(original);
  const copied = await directory(); await cp(original, copied, { recursive: true });
  expect(await verify(copied)).toEqual(snapshot);
  await step(copied);
  const resumed = await verify(copied);
  expect(resumed.runId).toBe(snapshot.runId);
  expect(resumed.reserved.attempts).toBe(snapshot.reserved.attempts + 1);
  expect(resumed.reserved.activeMs).toBe(snapshot.reserved.activeMs + example.evaluationTimeoutMs);
  expect(await verify(original)).toEqual(snapshot);
});

test("unobserved holdouts are not computed and verification uses its own finite time limit", async () => {
  const out = await run(); await seal(out);
  const holdout = spyOn(evaluator, "confirmGraph").mockImplementation(() => { throw new Error("unseen holdout"); });
  const evaluate = spyOn(evaluator, "evaluate");
  try {
    expect((await verify(out)).confirmationReproduced).toBe(false);
    expect(holdout).not.toHaveBeenCalled();
    expect(evaluate.mock.calls.every(([, config]) => config.evaluationTimeoutMs === 10000)).toBe(true);
  } finally { holdout.mockRestore(); evaluate.mockRestore(); }
});

test("rehashed numerical corruption and changed seal are rejected", async () => {
  const out = await run();
  const { state } = await load(out);
  state.baseline!.development = 0; await save(out, state);
  await expect(verify(out)).rejects.toThrow("baseline scores");
  const sealed = await run(); await seal(sealed);
  const saved = (await load(sealed)).state;
  saved.seal!.digest = "0".repeat(64); await save(sealed, saved);
  await expect(verify(sealed)).rejects.toThrow("seal");
});

test("altered decisions and missing evidence cannot pass by updating file hashes", async () => {
  for (const mutation of ["scores", "input", "selection", "reservation"] as const) {
    const out = await run(); const { state } = await load(out);
    const attempt = state.attempts.find(a => a.scores)!;
    if (mutation === "scores") attempt.scores!.development = 0;
    if (mutation === "input") attempt.input = JSON.stringify({ ...proposal, command: "no" });
    if (mutation === "selection") {
      attempt.status = attempt.status === "promoted" ? "rejected" : "promoted";
      state.incumbent = state.attempts.filter(a => a.status === "promoted").at(-1)?.id ?? "baseline";
    }
    if (mutation === "reservation") attempt.reservedMs = 0;
    await save(out, state);
    await expect(verify(out)).rejects.toThrow();
  }
});

test("verification accounts for the final confirmation reservation exactly once", async () => {
  const out = await run();
  const { config, state } = await load(out);
  config.budget.activeMs = 5000;
  state.configHash = hash(config);
  await writeFile(join(out, "config.json"), JSON.stringify(config)); await save(out, state);
  await expect(verify(out)).rejects.toThrow("final confirmation reservation");
  const complete = await directory();
  await init({ ...example, budget: { ...example.budget, activeMs: 3000 } }, complete);
  await seal(complete); await confirm(complete);
  expect((await verify(complete)).reserved.activeMs).toBe(3000);
});

test("parent references require an earlier realized proposal", async () => {
  const out = await directory(); await init(example, out);
  const invalid = await propose(out, { bad: true }, "baseline");
  await step(out);
  const { state } = await load(out);
  state.attempts[1]!.parent = invalid.id; await save(out, state);
  await expect(verify(out)).rejects.toThrow("parent");
});

test("confirmed scores are reproduced and a failed baseline is not marked ready", async () => {
  const out = await run(); await seal(out); await confirm(out);
  const { state } = await load(out);
  state.confirmation!.incumbent = 0; await save(out, state);
  await expect(verify(out)).rejects.toThrow("confirmation");
  const failed = await directory(); await init(example, failed);
  const saved = (await load(failed)).state;
  saved.phase = "initialization-failed"; saved.baseline = null; await save(failed, saved);
  const result = await verify(failed);
  expect(result.handoffReady).toBe(false);
  expect(result.reproducedEvaluations).toBe(0);
  expect(result.reserved.activeMs).toBe(example.evaluationTimeoutMs);
});

test("verification refuses another writer and flags interrupted evaluations without retrying", async () => {
  const out = await run();
  await withRun(out, async () => { await expect(verify(out)).rejects.toThrow("locked"); });
  await seal(out);
  const { state } = await load(out); state.phase = "confirming"; await save(out, state);
  const before = await readFile(join(out, "state.json"), "utf8");
  const result = await verify(out);
  expect(result.handoffReady).toBe(false);
  expect(result.confirmationReproduced).toBe(false);
  expect(await readFile(join(out, "state.json"), "utf8")).toBe(before);
});

test("abandoned captured output stays unevaluated and malformed completed output keeps failed slots", async () => {
  const provider = { kind: "xai", model: "fixture-model", concurrency: 1, proposalsPerCall: 1, maxInputTokens: 32000, maxOutputTokens: 1000, timeoutMs: 1000, reserveUsdPerCall: 0.01 };
  const budget = { ...example.budget, modelCalls: 1, tokens: 40000, usd: 0.01 };
  const out = await directory(); await init({ ...example, provider, budget }, out);
  await step(out, { live: true, transport: async () => ({ responseId: "truncated", text: JSON.stringify({ proposals: [proposal] }), usage: null, completionError: "incomplete fixture" }) });
  const pending = await verify(out);
  expect(pending.handoffReady).toBe(false);
  await abandon(out, (await load(out)).state.requests[0]!.id);
  const abandoned = await verify(out);
  expect(abandoned.handoffReady).toBe(true);
  expect(abandoned.reserved).toEqual(pending.reserved);
  expect((await load(out)).state.attempts).toHaveLength(0);
  const malformed = await directory(); await init({ ...example, provider, budget }, malformed);
  await step(malformed, { live: true, transport: async () => ({ responseId: "malformed", text: '{"proposals":[]}', usage: null }) });
  const result = await verify(malformed);
  expect(result.retainedFailures).toBe(1);
  expect(result.handoffReady).toBe(true);
  const { state } = await load(malformed);
  state.requests[0]!.usage = { inputTokens: 0, outputTokens: 1001 }; await save(malformed, state);
  await expect(verify(malformed)).rejects.toThrow("usage overage");
});

test("uncertain remote requests and captured unevaluated proposals block handoff without dispatch", async () => {
  const out = await directory();
  await init({ ...example, provider: { kind: "xai", model: "fixture-model", concurrency: 1, proposalsPerCall: 1, maxInputTokens: 32000, maxOutputTokens: 1000, timeoutMs: 1000, reserveUsdPerCall: 0.01 }, budget: { ...example.budget, modelCalls: 1, tokens: 40000, usd: 0.01 } }, out);
  await step(out, { live: true, transport: async () => { throw new Error("fixture failure"); } });
  expect((await verify(out)).handoffReady).toBe(false);
  const { state } = await load(out);
  state.requests[0]!.status = "completed";
  state.requests[0]!.response = JSON.stringify({ proposals: [proposal] });
  state.requests[0]!.error = null;
  await save(out, state);
  expect((await verify(out)).handoffReady).toBe(false);
  await step(out, { transport: async () => { throw new Error("must not dispatch"); } });
  expect((await verify(out)).handoffReady).toBe(true);
});
