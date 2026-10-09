import { expect, test } from "bun:test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { appendRawRss, auditFixtureEffects, auditProbe, auditRawRss, reserveTestProbe, startTestProbe, type ProbePlan } from "./prospective";
import { captureRawHostRss, type RawRssSample } from "./raw-rss";

const plan: ProbePlan = { attemptId: "probe-1", sourceSha: "7ce4b68a3ebeab9e9756a1ae0d3bcd1848682d8e", previousAttemptsCharged: 2,
  comparisonAttemptsReserved: 0, probeExecutionsReserved: 1, paidUsd: 0 };
function sample(index = 0, pid = 1234, base = 100): RawRssSample {
  const at = base + index * 1000;
  return { pid, index, readings: [
    { source: "proc_pidinfo", atNs: String(at), bytes: 1_048_576 },
    { source: "proc_pid_rusage", atNs: String(at + 1), bytes: 1_048_580 },
    { source: "proc_pidinfo", atNs: String(at + 2), bytes: 1_048_600 + index * 4096 },
  ], measuredBytes: 1_048_600 + index * 4096 };
}
function lines(...samples: RawRssSample[]): string { return samples.map((row) => JSON.stringify(row) + "\n").join(""); }

test("reservation and witnessed marker are synced before a test callback; one start only", async () => {
  const root = mkdtempSync(join(tmpdir(), "algal-probe-"));
  const dir = join(root, "one");
  try {
    const witness = reserveTestProbe(dir, plan);
    expect(() => reserveTestProbe(dir, plan)).toThrow();
    expect(readFileSync(join(dir, "reservation.json"), "utf8")).toContain("test-probe-reservation.v2");
    expect(() => appendRawRss(dir, witness, sample(), 1234)).toThrow();
    let executions = 0;
    await startTestProbe(dir, witness, () => {
      executions++;
      auditProbe(dir, witness); // Disk read inside execution, after the synced reservation and marker.
      expect(readFileSync(join(dir, "rss.jsonl"), "utf8")).toBe("");
      appendRawRss(dir, witness, sample(), 1234);
      appendRawRss(dir, witness, sample(1), 1234);
    });
    expect(executions).toBe(1);
    expect(auditRawRss(readFileSync(join(dir, "rss.jsonl"), "utf8"), 1234,
      { count: 2, baselineBytes: 1_048_600, peakBytes: 1_052_696 })).toEqual({ count: 2, baselineBytes: 1_048_600, peakBytes: 1_052_696 });
    await expect(startTestProbe(dir, witness, () => { executions++; })).rejects.toThrow();
    expect(executions).toBe(1);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("missing witness, changed reservation, corrupted marker, and uncertain execution fail closed", async () => {
  const root = mkdtempSync(join(tmpdir(), "algal-probe-"));
  try {
    const dir = join(root, "one"), witness = reserveTestProbe(dir, plan);
    let called = false;
    await expect(startTestProbe(dir, "", () => { called = true; })).rejects.toThrow();
    await expect(startTestProbe(dir, "a".repeat(64), () => { called = true; })).rejects.toThrow();
    expect(called).toBe(false);
    const file = join(dir, "reservation.json"), old = readFileSync(file, "utf8");
    writeFileSync(file, old.replace('"previousAttemptsCharged":2', '"previousAttemptsCharged":3'));
    await expect(startTestProbe(dir, witness, () => { called = true; })).rejects.toThrow();
    expect(called).toBe(false);
    writeFileSync(file, old); // Test-owned fixture only; never repair an actual run.
    await expect(startTestProbe(dir, witness, () => { called = true; throw new Error("uncertain fixture effect"); })).rejects.toThrow("uncertain fixture effect");
    expect(called).toBe(true);
    await expect(startTestProbe(dir, witness, () => { throw new Error("retried"); })).rejects.toThrow("already started");
    const marker = join(dir, "start.json");
    writeFileSync(marker, readFileSync(marker, "utf8").replace(witness, "a".repeat(64)));
    expect(() => auditProbe(dir, witness)).toThrow();
    expect(() => appendRawRss(dir, witness, sample(), 1234)).toThrow();
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("raw PID and three ordered readings replay; every corruption or aggregate lie fails", () => {
  const valid = sample();
  expect(auditRawRss(lines(valid), 1234)).toEqual({ count: 1, baselineBytes: 1_048_600, peakBytes: 1_048_600 });
  expect(() => auditRawRss("", 1234)).toThrow("missing RSS sample");
  expect(() => auditRawRss("", 1234, { count: 0, baselineBytes: 0, peakBytes: 0 })).toThrow("missing RSS sample");
  const cases: string[] = [
    lines({ ...valid, pid: 1235 }), lines({ ...valid, index: 1 }), lines(valid, valid),
    lines({ ...valid, measuredBytes: 123 }), lines({ ...valid, unexpected: true } as RawRssSample),
    lines({ ...valid, readings: [{ ...valid.readings[0], bytes: 0 }, valid.readings[1], valid.readings[2]] }),
    lines({ ...valid, readings: [valid.readings[0], { ...valid.readings[1], bytes: 1_200_000 }, valid.readings[2]] }),
    lines({ ...valid, readings: [valid.readings[1], valid.readings[0], valid.readings[2]] }),
    lines({ ...valid, readings: [valid.readings[0], { ...valid.readings[1], atNs: "100" }, valid.readings[2]] }),
    lines({ ...valid, readings: [valid.readings[0], valid.readings[1], { ...valid.readings[2], atNs: "500000103" }] }),
    lines(valid).trimEnd(), lines(valid) + "\n", lines(valid).replace("\"bytes\"", "\"extra\":true,\"bytes\""),
  ];
  for (const corrupted of cases) expect(() => auditRawRss(corrupted, 1234)).toThrow();
  expect(() => auditRawRss(lines(valid), 1235)).toThrow();
  expect(() => auditRawRss(lines(valid), 1234, { count: 2, baselineBytes: valid.measuredBytes, peakBytes: valid.measuredBytes })).toThrow();
  expect(() => auditRawRss(lines(valid), 1234, { count: 1, baselineBytes: valid.measuredBytes, peakBytes: 7 })).toThrow();
});

test("an interrupted RSS append cannot be extended or silently repaired", async () => {
  const root = mkdtempSync(join(tmpdir(), "algal-probe-"));
  try {
    const dir = join(root, "one"), witness = reserveTestProbe(dir, plan);
    await startTestProbe(dir, witness, () => { appendRawRss(dir, witness, sample(), 1234); });
    const trace = join(dir, "rss.jsonl");
    writeFileSync(trace, readFileSync(trace, "utf8") + '{"pid":');
    expect(() => appendRawRss(dir, witness, sample(1), 1234)).toThrow();
    expect(readFileSync(trace, "utf8")).toContain('{"pid":');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("uncertain fixture effects remain uncertain; forged success, duplicates and foreign effects fail", () => {
  const job = { id: "unknown", owner: "owner", delay_ms: 20, ttl_ms: 30000, fault: "after_effect" } as const;
  const uncertain = { job, status: "uncertain", reason: "host_restart" };
  expect(auditFixtureEffects('', [uncertain])).toEqual({ uncertainIds: ["unknown"], completeIds: [] });
  expect(auditFixtureEffects('{"id":"unknown"}\n', [uncertain])).toEqual({ uncertainIds: ["unknown"], completeIds: [] });
  for (const [effects, rows] of [
    ['', [{ ...uncertain, status: "complete", digest: `sha256:${"a".repeat(64)}` }]],
    ['{"id":"unknown"}\n', [{ ...uncertain, status: "cancelled" }]],
    ['{"id":"unknown"}\n{"id":"unknown"}\n', [uncertain]],
    ['{"id":"foreign"}\n', [uncertain]],
    ['{"id":"unknown"}', [uncertain]],
    ['', [uncertain, uncertain]],
    ['', [{ ...uncertain, status: "running" }]],
    ['', [{ ...uncertain, status: "complete" }]],
  ] as const) expect(() => auditFixtureEffects(effects, rows)).toThrow();
});

(process.platform === "darwin" ? test : test.skip)("test-only Darwin sampler retains actual child PID and raw bracketing readings", async () => {
  const child = Bun.spawn([process.execPath, "-e", "console.log('ready'); await Bun.sleep(10000)"], { stdout: "pipe", stderr: "pipe" });
  try {
    const reader = child.stdout.getReader();
    const ready = await Promise.race([reader.read(), Bun.sleep(5000).then(() => { throw new Error("idle host timeout"); })]);
    if (ready.done || !new TextDecoder().decode(ready.value).includes("ready")) throw new Error("idle host not ready");
    reader.releaseLock();
    const measured = captureRawHostRss(child.pid, 0);
    expect(measured.pid).toBe(child.pid);
    expect(auditRawRss(lines(measured), child.pid, { count: 1, baselineBytes: measured.measuredBytes, peakBytes: measured.measuredBytes }).count).toBe(1);
    expect(() => auditRawRss(lines(measured), process.pid)).toThrow();
  } finally {
    if (child.exitCode === null && child.signalCode === null) child.kill();
    await child.exited;
  }
}, 12000);
