import { afterEach, expect, test } from "bun:test";
import { chmod, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { type EffectRequest } from "@hraness/algal";
import { ArtifactStore } from "./artifacts";
import { runStudy, verifyStudy, type Attempt } from "./study";
import { createXcbExecutor } from "./xcb-executor";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true }))); });

const proposal = { graph: { nodes: 4, edges: [[0, 1], [1, 2], [2, 3], [0, 3]] }, hypothesis: "Redundant paths may retain service.", prediction: 0.6, rationale: "Test the same edge budget.", parents: [], message: "Compare degree concentration." };
const request: EffectRequest = {
  contract: "algal.effect.v1", kind: "agent", cellId: "researcher", prompt: "Return a bounded proposal JSON.", output: { kind: "json", schema: { type: "object" } },
  context: { inputs: { context: { contract: "algal.lab.context.v1", nodes: 4, edges: 4, evidence: [], messages: [] } } },
  budget: { maxContextBytes: 65536, maxOutputBytes: 8192 },
};

async function fixture(mode = "success") {
  const root = await mkdtemp(join(tmpdir(), "algal-lab-xcb-"));
  roots.push(root);
  const executable = join(root, "fake-xcb");
  const statePath = join(root, "state.json");
  const callsPath = join(root, "calls.jsonl");
  const state = { mode, observedAtMs: Date.now() - 1000, expiresAt: Date.now() + 600000 };
  await writeFile(statePath, JSON.stringify(state));
  // Deliberately a local executable fixture, never the real XCB or a provider.
  await writeFile(executable, `#!${process.execPath}
import { readFileSync, appendFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
const state = JSON.parse(readFileSync(${JSON.stringify(statePath)}, "utf8"));
const account = "a_fixture";
const model = "claude/sonnet/low";
const runtimeDigest = createHash("sha256").update(readFileSync(process.argv[1])).digest("hex");
if (process.argv.slice(2).join(" ") === "--json generate --capabilities") {
  const qualification = { runtimeVersion: "0.4.0", runtimeDigest: state.mode === "mismatch" ? "0".repeat(64) : runtimeDigest, evidenceDigest: "1".repeat(64), expiresAt: state.expiresAt };
  const row = { id: account, name: "fixture", provider: "claude", enabled: true, busy: false, connected: true, runtimeAdmitted: true, available: true, reason: null, models: [{ key: model, label: "fixture", observedAtMs: state.observedAtMs }], qualification };
  if (state.mode === "missing-qualification") delete row.qualification;
  if (state.mode === "missing-model") row.models = [];
  console.log(JSON.stringify({ version: 1, supported: state.mode !== "unqualified", zeroTools: state.mode !== "tools", zeroHooks: true, ephemeral: true, limits: { maxInputBytes: 1048576, maxOutputBytes: 262144, minTimeoutMs: 1000, maxTimeoutMs: 120000 }, accounts: [row] }));
  process.exit(0);
}
if (process.argv.slice(2).join(" ") !== "--json generate") process.exit(91);
const input = JSON.parse(await Bun.stdin.text());
appendFileSync(${JSON.stringify(callsPath)}, JSON.stringify(input) + "\\n");
if (state.mode === "archive-failure") mkdirSync(${JSON.stringify(join(root, "partial", "study", "study.json"))}, { recursive: true });
if (state.mode === "cancel") {
  process.on("SIGTERM", () => setTimeout(() => { console.log(JSON.stringify({ version: 1, status: "failed", code: "cancelled", requestId: "application_fixture", joined: true, effects: "none" })); process.exit(1); }, 100));
  setInterval(() => {}, 1000);
} else if (state.mode === "failed") {
  console.log(JSON.stringify({ version: 1, status: "failed", code: "provider_error", requestId: "application_fixture", joined: true, effects: "none" })); process.exit(1);
} else if (state.mode === "overflow") {
  console.log("x".repeat(70000));
} else {
  console.log(JSON.stringify({ version: 1, status: "completed", requestId: "application_fixture", account, model: state.mode === "wrong-model" ? "claude/other/low" : model, text: state.mode === "invalid-json" ? "private provider output" : JSON.stringify(${JSON.stringify(proposal)}), outcome: { terminal: "completed", joined: state.mode !== "unjoined", effects: "none" } }));
}
`);
  await chmod(executable, 0o700);
  return {
    root, executable, options: { executable, account: "a_fixture", model: "claude/sonnet/low" },
    change: async (next: Partial<typeof state>) => { Object.assign(state, next); await writeFile(statePath, JSON.stringify(state)); },
    calls: async () => { try { return (await readFile(callsPath, "utf8")).trim().split("\n").filter(Boolean).map((line) => JSON.parse(line) as Record<string, unknown>); } catch { return []; } },
  };
}

test("qualified exact execution retains metadata, uses a closed request, and enforces its call budget", async () => {
  const f = await fixture();
  const executor = await createXcbExecutor({ ...f.options, maxCalls: 1 });
  const result = await executor.executeEffect!(request);
  expect(result.output).toEqual(proposal);
  expect(result.metadata).toEqual({ executor: executor.id, usage: { model: f.options.model }, configurationDigest: executor.configurationDigest, retryable: false });
  expect(executor.configuration).toMatchObject({ provider: "claude", model: f.options.model, zeroTools: true, zeroHooks: true, ephemeral: true, tokenUsage: "unavailable" });
  expect(JSON.stringify(executor.configuration)).not.toContain(f.executable);
  expect(result.metadata?.usage).not.toHaveProperty("tokensIn");
  const [body] = await f.calls();
  expect(Object.keys(body!).sort()).toEqual(["version", "account", "model", "prompt", "timeoutMs", "maxOutputBytes"].sort());
  expect(body).toMatchObject({ version: 1, account: f.options.account, model: f.options.model, timeoutMs: 45000, maxOutputBytes: 8192 });
  expect(body!.prompt).toContain("algal.lab.context.v1");
  expect(executor.observations).toMatchObject([{ requestId: "application_fixture", status: "completed", joined: true, effects: "none" }]);
  await expect(executor.execute(request)).rejects.toThrow("call_budget_exhausted");
  expect(await f.calls()).toHaveLength(1);
  await executor.settle();
}, 30000);

test("missing, unsafe, stale and mismatched qualification fail before inference", async () => {
  for (const mode of ["unqualified", "tools", "missing-qualification", "missing-model", "mismatch"]) {
    const f = await fixture(mode);
    await expect(createXcbExecutor(f.options)).rejects.toThrow();
    expect(await f.calls()).toEqual([]);
  }
  const f = await fixture();
  await f.change({ expiresAt: Date.now() - 1 });
  await expect(createXcbExecutor(f.options)).rejects.toThrow("stale_qualification");
  await f.change({ expiresAt: Date.now() + 60000, observedAtMs: Date.now() - 86400001 });
  await expect(createXcbExecutor(f.options)).rejects.toThrow("stale_model");
  expect(await f.calls()).toEqual([]);
}, 30000);

test("rechecks qualification before each call and rejects runtime drift", async () => {
  const f = await fixture();
  const executor = await createXcbExecutor(f.options);
  await f.change({ mode: "unqualified" });
  await expect(executor.execute(request)).rejects.toThrow("application_not_qualified");
  expect(await f.calls()).toEqual([]);
  await f.change({ mode: "success" });
  await writeFile(f.executable, (await readFile(f.executable, "utf8")) + "\n// replacement\n");
  await expect(executor.execute(request)).rejects.toThrow("qualification_changed");
  expect(await f.calls()).toEqual([]);
}, 30000);

test("bounds input before inference and rejects response mismatch or private malformed text", async () => {
  const f = await fixture();
  const executor = await createXcbExecutor(f.options);
  await expect(executor.execute({ ...request, prompt: "x".repeat(8193) })).rejects.toThrow();
  expect(await f.calls()).toEqual([]);
  await f.change({ mode: "wrong-model" });
  await expect(executor.execute(request)).rejects.toThrow("invalid_response");
  await f.change({ mode: "invalid-json" });
  await expect(executor.execute(request)).rejects.toThrow("xcb application: invalid_response");
  expect(executor.observations.every((item) => item.joined && item.effects === "none" && item.status === "failed")).toBe(true);
  expect(JSON.stringify(executor.observations)).not.toContain("private provider output");
}, 30000);

test("settled provider failure is retained without retry, while unproven custody blocks further calls", async () => {
  const f = await fixture("failed");
  const executor = await createXcbExecutor(f.options);
  await expect(executor.execute(request)).rejects.toThrow("provider_error");
  expect(await f.calls()).toHaveLength(1);
  expect(executor.observations).toMatchObject([{ status: "failed", code: "provider_error", joined: true, effects: "none" }]);
  await executor.settle();
  await f.change({ mode: "unjoined" });
  await expect(executor.execute(request)).rejects.toThrow("invalid_response");
  await f.change({ mode: "success" });
  await expect(executor.execute(request)).rejects.toThrow("custody_unproven");
  expect(await f.calls()).toHaveLength(2);
  await expect(executor.settle()).rejects.toThrow("custody_unproven");
}, 30000);

test("oversized process output is rejected and cannot silently permit another call", async () => {
  const f = await fixture("overflow");
  const executor = await createXcbExecutor(f.options);
  await expect(executor.execute(request)).rejects.toThrow("output_limit");
  await expect(executor.execute(request)).rejects.toThrow("custody_unproven");
  expect(await f.calls()).toHaveLength(1);
}, 30000);

test("cancellation forwards SIGTERM and waits for the application joined response", async () => {
  const f = await fixture("cancel");
  const executor = await createXcbExecutor(f.options);
  const controller = new AbortController();
  // Attach a normal promise rejection handler before sending cancellation;
  // the matcher is evaluated only after the child has received the signal.
  const running = executor.execute(request, controller.signal).then(() => undefined, (error: unknown) => error);
  for (let i = 0; i < 1000 && !(await f.calls()).length; i++) await Bun.sleep(10);
  const calls = await f.calls();
  const started = performance.now();
  controller.abort(); // Always cancel, even if fixture startup exceeded the bound.
  const failure = await running;
  expect(failure).toBeInstanceOf(Error);
  expect((failure as Error).message).toContain("cancelled");
  expect(calls).toHaveLength(1);
  expect(performance.now() - started).toBeGreaterThanOrEqual(80);
  expect(executor.observations).toMatchObject([{ status: "failed", code: "cancelled", joined: true, effects: "none" }]);
  await executor.settle();
}, 30000);

test("full ALGAL receipts preserve XCB model and configuration and reproduce without provider calls", async () => {
  const f = await fixture();
  const executor = await createXcbExecutor({ ...f.options, maxCalls: 6 });
  const directory = join(f.root, "study");
  const report = await runStudy({ contract: "algal.lab.study.v1", name: "xcb-fixture", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }, directory, { executor });
  const attempt = await new ArtifactStore(directory).get(report.attempts[0]) as unknown as Attempt;
  expect(attempt.receipt.effects[0]).toMatchObject({ executor: executor.id, usage: { model: f.options.model }, configurationDigest: executor.configurationDigest });
  expect(attempt.receipt.effects[0]?.usage).not.toHaveProperty("tokensOut");
  expect((await verifyStudy(directory)).experiments).toBe(6);
  expect(await f.calls()).toHaveLength(6);
}, 30000);

test("the optional example never appends a sidecar to an existing output directory", async () => {
  const f = await fixture();
  const protocolPath = join(f.root, "protocol.json");
  await writeFile(protocolPath, JSON.stringify({ contract: "algal.lab.study.v1", name: "xcb-fixture", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }));
  const directory = join(f.root, "existing");
  await mkdir(directory);
  await writeFile(join(directory, "owner.txt"), "existing run");
  const child = Bun.spawn([process.execPath, "examples/xcb-study.ts", "--protocol", protocolPath, "--out", directory], {
    env: { ...process.env, XCB_EXECUTABLE: f.executable, XCB_ACCOUNT: f.options.account, XCB_MODEL: f.options.model },
    stdout: "ignore", stderr: "ignore",
  });
  expect(await child.exited).not.toBe(0);
  expect(await readdir(directory)).toEqual(["owner.txt"]);
  expect(await f.calls()).toEqual([]);
});

test("the optional example forwards CLI cancellation, settles, and retains owned transport evidence", async () => {
  const f = await fixture("cancel");
  const protocolPath = join(f.root, "protocol.json");
  await writeFile(protocolPath, JSON.stringify({ contract: "algal.lab.study.v1", name: "xcb-fixture", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }));
  const directory = join(f.root, "cancelled");
  const child = Bun.spawn([process.execPath, "examples/xcb-study.ts", "--protocol", protocolPath, "--out", directory], {
    env: { ...process.env, XCB_EXECUTABLE: f.executable, XCB_ACCOUNT: f.options.account, XCB_MODEL: f.options.model }, stdout: "ignore", stderr: "ignore",
  });
  for (let i = 0; i < 1000 && !(await f.calls()).length; i++) await Bun.sleep(10);
  child.kill("SIGINT");
  expect(await child.exited).toBe(130);
  expect(await f.calls()).toHaveLength(1);
  const sidecar = JSON.parse(await readFile(join(directory, "xcb.json"), "utf8"));
  expect(sidecar).toMatchObject({ cancelled: true, observations: [{ status: "failed", code: "cancelled", joined: true, effects: "none" }] });
  expect(sidecar.configurationDigest).toBe(JSON.parse(await readFile(join(directory, "executor.json"), "utf8")).configurationDigest);
}, 30000);

test("archival failure still preserves configuration and joined provider observations", async () => {
  const f = await fixture("archive-failure");
  const protocolPath = join(f.root, "protocol.json");
  await writeFile(protocolPath, JSON.stringify({ contract: "algal.lab.study.v1", name: "xcb-fixture", replicateSeeds: [7], researchers: 2, rounds: 1, nodes: 4, edges: 4, failureSteps: 1, discoverySeeds: [11], holdoutSeeds: [101] }));
  const directory = join(f.root, "partial");
  const child = Bun.spawn([process.execPath, "examples/xcb-study.ts", "--protocol", protocolPath, "--out", directory], {
    env: { ...process.env, XCB_EXECUTABLE: f.executable, XCB_ACCOUNT: f.options.account, XCB_MODEL: f.options.model }, stdout: "ignore", stderr: "ignore",
  });
  expect(await child.exited).not.toBe(0);
  const sidecar = JSON.parse(await readFile(join(directory, "xcb.json"), "utf8"));
  expect(sidecar.observations).toHaveLength(6);
  expect(sidecar.observations.every((o: { joined: boolean; effects: string }) => o.joined && o.effects === "none")).toBe(true);
  expect(JSON.parse(await readFile(join(directory, "executor.json"), "utf8")).configurationDigest).toBe(sidecar.configurationDigest);
  expect(JSON.parse(await readFile(join(directory, "intent.json"), "utf8")).maxCalls).toBe(6);
}, 30000);
