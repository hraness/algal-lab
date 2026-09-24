import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { pathToFileURL } from "node:url";
import type { Executor } from "@hraness/algal";
import fixture from "../../examples/observation-fixture.json";
import { ArtifactStore, digest, readJsonFile } from "../artifacts";
import { json } from "../contracts";
import { observationFixtureInstrument as instrument } from "./fixture";
import { bindSources, completeObservationAttempt, createObservationStudy, evaluateObservationStudy, freezeObservationStudy, parseObservation, parseObservationInput, recoverObservationStudyLock, registerObservationAttempt, verifyObservationStudy, type ObservationInstrument } from "./observation";

const cleanup: string[] = [];
afterEach(async () => { for (const path of cleanup.splice(0)) await rm(path, { recursive: true, force: true }); });
async function directory(): Promise<string> {
  const parent = await mkdtemp(join(tmpdir(), "algal-observation-test-"));
  cleanup.push(parent);
  return join(parent, "study");
}
const executor = (output: unknown = fixture.proposal): Executor => ({ id: "test:proposal", capabilities: { effects: ["agent"] }, execute: async () => json(output) });
async function registered(adapter = instrument, proposal: unknown = fixture.proposal) {
  const path = await directory();
  await createObservationStudy(fixture.protocol, path, adapter);
  const result = await registerObservationAttempt(path, adapter, { attemptId: "first", input: fixture.discoveryInput, context: {}, executor: executor(proposal) });
  return { path, result };
}
async function completed() {
  const { path, result } = await registered();
  const observed = await completeObservationAttempt(path, instrument, "first");
  return { path, result, observed };
}

describe("non-graph observation boundary", () => {
  test("real ALGAL receipts preserve prediction before measurement and freeze before evaluation", async () => {
    const { path, result } = await registered();
    expect(result.registration.receipt.work.agentCalls).toBe(1);
    expect(result.registration.proposal?.prediction).toEqual({ mean: 2, unit: "fixture-unit" });
    expect(await verifyObservationStudy(path, instrument)).toMatchObject({ pending: 1, observations: 0, freshComputation: "not-requested" });
    await expect(freezeObservationStudy(path, instrument, ["first"])).rejects.toThrow("pending");
    const joined = await completeObservationAttempt(path, instrument, "first");
    expect(joined.observation.registrationDigest).toBe(result.registrationDigest);
    expect(joined.observation.receipt.work.agentCalls).toBe(0);
    expect(joined.observation.receipt.effects[0]?.executor).toBe("tool:lab.observation.measure.v1");
    expect(joined.observation.observation?.measurements[0]?.value).toBe(2);
    expect(joined.observation.observation?.measurements[0]?.uncertainty.upper).toBeCloseTo(2 + Math.sqrt(1 / 3));
    await freezeObservationStudy(path, instrument, ["first"]);
    const evaluations = await evaluateObservationStudy(path, instrument, fixture.evaluationInput);
    const evaluated = await new ArtifactStore(path).get(evaluations[0]!);
    expect(evaluated).toMatchObject({ inputDigest: fixture.protocol.evaluation.inputDigest, observation: { measurements: [{ value: 4 }] } });
    expect(await verifyObservationStudy(path, instrument, { recompute: true })).toEqual({ ok: true, attempts: 1, pending: 0, rejected: 0, observations: 1, evaluated: 1, frozen: true, receiptReplay: true, freshComputation: "passed" });
  });

  test("a fresh process resumes a durable registration without any proposal executor", async () => {
    let calls = 0;
    const path = await directory();
    await createObservationStudy(fixture.protocol, path, instrument);
    await registerObservationAttempt(path, instrument, { attemptId: "first", input: fixture.discoveryInput, context: {}, executor: { ...executor(), execute: async () => { calls++; return json(fixture.proposal); } } });
    // This boundary is the crash point: a new process has only the durable archive.
    const script = `import {completeObservationAttempt} from ${JSON.stringify(new URL("./observation.ts", import.meta.url).pathname)}; import {observationFixtureInstrument} from ${JSON.stringify(new URL("./fixture/index.ts", import.meta.url).pathname)}; console.log(JSON.stringify(await completeObservationAttempt(${JSON.stringify(path)},observationFixtureInstrument,"first")));`;
    const child = Bun.spawn([process.execPath, "-e", script], { stdout: "pipe", stderr: "pipe" });
    const [stdout, stderr, code] = await Promise.all([new Response(child.stdout).text(), new Response(child.stderr).text(), child.exited]);
    expect(stderr).toBe("");
    expect(code).toBe(0);
    const output = JSON.parse(stdout);
    const again = await completeObservationAttempt(path, instrument, "first");
    expect(again.observationDigest).toBe(output.observationDigest);
    expect(calls).toBe(1);
    await expect(registerObservationAttempt(path, instrument, { attemptId: "first", input: fixture.discoveryInput, context: {}, executor: executor() })).rejects.toThrow();
    expect(await verifyObservationStudy(path, instrument)).toMatchObject({ observations: 1, pending: 0 });
  });

  test("receipt replay invokes no provider or measurement; recomputation is a separate request", async () => {
    let measurements = 0;
    const counted: ObservationInstrument = { ...instrument, measure: async (...args) => { measurements++; return instrument.measure!(...args); } };
    const { path } = await registered(counted);
    await completeObservationAttempt(path, counted, "first");
    expect(measurements).toBe(1);
    await verifyObservationStudy(path, counted);
    expect(measurements).toBe(1);
    await verifyObservationStudy(path, counted, { recompute: true });
    expect(measurements).toBe(2);
  });

  test("an attempt named input has a distinct evaluation result pointer", async () => {
    const path = await directory();
    await createObservationStudy(fixture.protocol, path, instrument);
    await registerObservationAttempt(path, instrument, { attemptId: "input", input: fixture.discoveryInput, context: {}, executor: executor() });
    await completeObservationAttempt(path, instrument, "input");
    await freezeObservationStudy(path, instrument, ["input"]);
    const evaluated = await evaluateObservationStudy(path, instrument, fixture.evaluationInput);
    expect(evaluated[0]).not.toBe(fixture.protocol.evaluation.inputDigest);
    expect(await verifyObservationStudy(path, instrument, { recompute: true })).toMatchObject({ observations: 1, evaluated: 1, freshComputation: "passed" });
  });

  test("attachment studies cannot claim fresh computation before an observation exists", async () => {
    const { measure: _measure, ...base } = instrument;
    const adapter: ObservationInstrument = { ...base, id: "attached-replicates.v1", execution: "attachment" };
    const { path } = await registered(adapter);
    await expect(verifyObservationStudy(path, adapter, { recompute: true })).rejects.toThrow("pure adapter");
  });

  test("hard process death during measurement retains registration and permits guarded recovery", async () => {
    const { path, result } = await registered();
    const script = `import {completeObservationAttempt} from ${JSON.stringify(new URL("./observation.ts", import.meta.url).pathname)}; import {observationFixtureInstrument as instrument} from ${JSON.stringify(new URL("./fixture/index.ts", import.meta.url).pathname)}; await completeObservationAttempt(${JSON.stringify(path)},{...instrument,measure:async()=>{process.kill(process.pid,"SIGKILL");throw new Error("unreachable");}},"first");`;
    const child = Bun.spawn([process.execPath, "-e", script], { stdout: "ignore", stderr: "pipe" });
    await Promise.all([new Response(child.stderr).text(), child.exited]);
    expect(child.signalCode).toBe("SIGKILL");
    expect(await readJsonFile(join(path, "attempts", "first", "registered.json"))).toEqual({ artifact: result.registrationDigest });
    await expect(completeObservationAttempt(path, instrument, "first")).rejects.toThrow("mutation owner");
    await recoverObservationStudyLock(path);
    const resultAfterRecovery = await completeObservationAttempt(path, instrument, "first");
    expect(resultAfterRecovery.observation.registrationDigest).toBe(result.registrationDigest);
    expect(await verifyObservationStudy(path, instrument, { recompute: true })).toMatchObject({ attempts: 1, observations: 1, pending: 0 });
  });

  test("failed and rejected attempts remain immutable and cannot enter selection", async () => {
    const { path, result } = await registered(instrument, { ...fixture.proposal, unexpected: true });
    expect(result.registration.rejection).not.toBeNull();
    expect(result.registration.proposal).toBeNull();
    await expect(completeObservationAttempt(path, instrument, "first")).rejects.toThrow("rejected");
    await registerObservationAttempt(path, instrument, { attemptId: "bad-measurement", input: fixture.discoveryInput, context: {}, executor: executor({ ...fixture.proposal, design: { scale: 100 } }) });
    const failed = await completeObservationAttempt(path, instrument, "bad-measurement");
    expect(failed.observation.receipt.outcome).toBe("failed");
    expect(failed.observation.observation).toBeNull();
    await expect(freezeObservationStudy(path, instrument, ["bad-measurement"])).rejects.toThrow("successful");
    await freezeObservationStudy(path, instrument, []);
    expect(await verifyObservationStudy(path, instrument)).toMatchObject({ attempts: 2, rejected: 1, observations: 1, frozen: true });
  });

  test("an ambiguous provider-call boundary blocks retries and subsequent proposals", async () => {
    const { path } = await registered();
    await rm(join(path, "attempts", "first", "registered.json"));
    let calls = 0;
    const retry = { ...executor(), execute: async () => { calls++; return json(fixture.proposal); } };
    await expect(registerObservationAttempt(path, instrument, { attemptId: "second", input: fixture.discoveryInput, context: {}, executor: retry })).rejects.toThrow("ambiguous");
    await expect(completeObservationAttempt(path, instrument, "first")).rejects.toThrow("ambiguous");
    await expect(verifyObservationStudy(path, instrument)).rejects.toThrow("ambiguous");
    expect(calls).toBe(0);
  });

  test("freeze rejects late selection and evaluation rejects the wrong input commitment", async () => {
    const { path } = await completed();
    await expect(evaluateObservationStudy(path, instrument, fixture.evaluationInput)).rejects.toThrow();
    await freezeObservationStudy(path, instrument, ["first"]);
    await expect(registerObservationAttempt(path, instrument, { attemptId: "late", input: fixture.discoveryInput, context: {}, executor: executor() })).rejects.toThrow("frozen");
    await expect(freezeObservationStudy(path, instrument, [])).rejects.toThrow("frozen");
    await expect(evaluateObservationStudy(path, instrument, fixture.discoveryInput)).rejects.toThrow("commitment");
    expect(await verifyObservationStudy(path, instrument)).toMatchObject({ evaluated: 0, frozen: true });
    const before = await evaluateObservationStudy(path, instrument, fixture.evaluationInput);
    expect(await evaluateObservationStudy(path, instrument, fixture.evaluationInput)).toEqual(before);
  });

  test("source binding covers nested helper bytes and verification refuses a changed environment", async () => {
    const path = await directory();
    const sourceRoot = join(dirname(path), "adapter");
    await mkdir(join(sourceRoot, "nested"), { recursive: true });
    await writeFile(join(sourceRoot, "adapter.ts"), 'export { statistic } from "./nested/statistics.ts";');
    await writeFile(join(sourceRoot, "nested", "statistics.ts"), "export const statistic = 2;");
    const adapter: ObservationInstrument = { ...instrument, sources: { trees: { ...instrument.sources.trees, dependency: pathToFileURL(sourceRoot + "/") }, files: {} } };
    await createObservationStudy(fixture.protocol, path, adapter);
    const before = await bindSources(adapter.sources);
    expect(Object.keys(before)).toContain("dependency/nested/statistics.ts");
    await writeFile(join(sourceRoot, "nested", "statistics.ts"), "export const statistic = 99;");
    await expect(verifyObservationStudy(path, adapter)).rejects.toThrow("source or instrument identity");
  });

  test("artifact mutation and wrong instrument identity fail verification", async () => {
    const { path, observed } = await completed();
    await expect(verifyObservationStudy(path, { ...instrument, id: "different.v1" })).rejects.toThrow("identity");
    const filename = join(path, "artifacts", `${observed.observationDigest.slice(7)}.json`);
    const altered = JSON.parse(await readFile(filename, "utf8"));
    altered.inputDigest = fixture.protocol.evaluation.inputDigest;
    await writeFile(filename, JSON.stringify(altered));
    await expect(verifyObservationStudy(path, instrument)).rejects.toThrow("digest mismatch");
    await expect(completeObservationAttempt(path, instrument, "first")).rejects.toThrow("digest mismatch");
  });

  test("an internally rehashed wrong input join still fails its registration binding", async () => {
    const { path, observed } = await completed();
    const store = new ArtifactStore(path);
    const changed = { ...observed.observation, inputDigest: digest(fixture.evaluationInput) };
    const changedId = await store.put(changed);
    await writeFile(join(path, "attempts", "first", "observed.json"), JSON.stringify({ artifact: changedId }));
    await expect(verifyObservationStudy(path, instrument)).rejects.toThrow("join identity");
    await expect(freezeObservationStudy(path, instrument, ["first"])).rejects.toThrow("join identity");
  });

  test("external outcomes attach once and never relaunch an external job", async () => {
    const { measure: _measure, ...base } = instrument;
    const adapter: ObservationInstrument = { ...base, id: "attached-replicates.v1", execution: "attachment" };
    const { path } = await registered(adapter);
    const observation = await instrument.measure!(parseObservationInput(fixture.discoveryInput), fixture.proposal);
    const first = await completeObservationAttempt(path, adapter, "first", observation);
    expect(first.observation.mode).toBe("attached");
    const second = await completeObservationAttempt(path, adapter, "first", { invalid: "a later result cannot replace the join" });
    expect(second.observationDigest).toBe(first.observationDigest);
    expect(await verifyObservationStudy(path, adapter)).toMatchObject({ observations: 1, freshComputation: "not-requested" });
    await expect(verifyObservationStudy(path, adapter, { recompute: true })).rejects.toThrow("pure adapter");
  });

  test("unknown fields, excessive payloads and invalid intervals are rejected", () => {
    expect(() => parseObservationInput({ ...fixture.discoveryInput, extra: 1 })).toThrow("unknown field");
    expect(() => parseObservationInput({ ...fixture.discoveryInput, data: "x".repeat(65537) })).toThrow("byte bound");
    expect(() => parseObservation({ contract: "test.v1", realizedDesign: {}, values: {}, artifacts: [], limitations: [], measurements: [{ name: "x", value: 1, unit: "unit", uncertainty: { method: "test", lower: 3, upper: 1, level: 0.95 } }] })).toThrow("invalid uncertainty");
  });

  test("lock recovery refuses a live process and does not remove any archive evidence", async () => {
    const { path } = await registered();
    await writeFile(join(path, ".observation-lock"), JSON.stringify({ pid: process.pid, nonce: "test" }));
    await expect(recoverObservationStudyLock(path)).rejects.toThrow("alive");
    await expect(completeObservationAttempt(path, instrument, "first")).rejects.toThrow("mutation owner");
    expect(await readJsonFile(join(path, "attempts", "first", "registered.json"))).toHaveProperty("artifact");
  });
});
