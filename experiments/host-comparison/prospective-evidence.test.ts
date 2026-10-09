import { expect, test } from "bun:test";
import { mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { appendRawRss, reserveTestProbe, startTestProbe, type ProbePlan } from "./prospective";
import { auditProspectiveEvidence } from "./prospective-evidence";
import type { RawRssSample } from "./raw-rss";

const plan: ProbePlan = { attemptId: "evidence-probe", sourceSha: "7ce4b68a3ebeab9e9756a1ae0d3bcd1848682d8e",
  previousAttemptsCharged: 2, comparisonAttemptsReserved: 0, probeExecutionsReserved: 1, paidUsd: 0 };
const uncertain = { job: { id: "unknown", owner: "owner", delay_ms: 20, ttl_ms: 30000, fault: "after_effect" },
  status: "uncertain", reason: "host_restart" };
const sample: RawRssSample = { pid: 1234, index: 0, readings: [
  { source: "proc_pidinfo", atNs: "100", bytes: 1_048_576 },
  { source: "proc_pid_rusage", atNs: "101", bytes: 1_048_580 },
  { source: "proc_pidinfo", atNs: "102", bytes: 1_048_600 },
], measuredBytes: 1_048_600 };
const expected = { count: 1, baselineBytes: 1_048_600, peakBytes: 1_048_600 };

test("missing or corrupt effect evidence fails closed after an uncertain callback, without retry", async () => {
  const root = mkdtempSync(join(tmpdir(), "algal-evidence-"));
  try {
    const probe = join(root, "attempt"), effects = join(root, "effects.jsonl");
    const witness = reserveTestProbe(probe, plan);
    let callbacks = 0;
    await expect(startTestProbe(probe, witness, () => {
      callbacks++;
      appendRawRss(probe, witness, sample, 1234);
      throw new Error("uncertain fixture callback");
    })).rejects.toThrow("uncertain fixture callback");
    const audit = (file = effects) => auditProspectiveEvidence(probe, witness, 1234, file, [uncertain], expected);
    expect(audit).toThrow(); // No file: not equivalent to an empty effect log.
    writeFileSync(effects, "");
    expect(audit()).toEqual({ rss: expected, effects: { uncertainIds: ["unknown"], completeIds: [] } });
    const effectPresent = join(root, "present.jsonl");
    writeFileSync(effectPresent, '{"id":"unknown"}\n');
    expect(audit(effectPresent).effects).toEqual({ uncertainIds: ["unknown"], completeIds: [] });
    for (const [name, contents] of [
      ["partial", '{"id":"unknown"}'],
      ["duplicate", '{"id":"unknown"}\n{"id":"unknown"}\n'],
      ["foreign", '{"id":"foreign"}\n'],
    ] as const) {
      const file = join(root, name + ".jsonl");
      writeFileSync(file, contents);
      expect(() => audit(file)).toThrow();
    }
    const link = join(root, "linked.jsonl");
    symlinkSync(effectPresent, link);
    expect(() => audit(link)).toThrow();
    expect(() => auditProspectiveEvidence(probe, "a".repeat(64), 1234, effects, [uncertain], expected)).toThrow();
    await expect(startTestProbe(probe, witness, () => { callbacks++; })).rejects.toThrow("already started");
    expect(callbacks).toBe(1);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("missing, truncated, or foreign-PID raw evidence cannot be replayed", async () => {
  const root = mkdtempSync(join(tmpdir(), "algal-evidence-"));
  try {
    const probe = join(root, "attempt"), effects = join(root, "effects.jsonl");
    const witness = reserveTestProbe(probe, plan);
    await startTestProbe(probe, witness, () => { appendRawRss(probe, witness, sample, 1234); });
    writeFileSync(effects, "");
    const audit = (pid = 1234) => auditProspectiveEvidence(probe, witness, pid, effects, [uncertain], expected);
    expect(() => audit(1235)).toThrow();
    expect(() => auditProspectiveEvidence(probe, witness, 1234, effects, [uncertain], { ...expected, count: 2 })).toThrow();
    const trace = join(probe, "rss.jsonl");
    writeFileSync(trace, readFileSync(trace, "utf8").trimEnd());
    expect(audit).toThrow();
    rmSync(trace);
    expect(audit).toThrow();
  } finally { rmSync(root, { recursive: true, force: true }); }
});
