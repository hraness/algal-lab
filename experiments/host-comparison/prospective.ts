import { createHash } from "node:crypto";
import { closeSync, existsSync, fsyncSync, lstatSync, mkdirSync, openSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { parseEffectLog } from "./effect-log";
import { parseRecord } from "./protocol";
import { checkedRss } from "./rss";
import type { RawRssSample } from "./raw-rss";

// This module is a test probe, NOT an authorized comparison runner. In particular
// it cannot grant an attempt to the exhausted v1 campaign or launch either host.
const SHA = /^[a-f0-9]{64}$/;
const NS = /^[1-9][0-9]{0,19}$/;
const MAX_NS = (1n << 64n) - 1n;
const MAX_TRACE_BYTES = 1024 * 1024;
const MAX_SAMPLES = 4096;
const MAX_SPAN_NS = 500_000_000n;
const RESERVATION = "reservation.json";
const START = "start.json";
const TRACE = "rss.jsonl";
export type ProbePlan = { attemptId: string; sourceSha: string; previousAttemptsCharged: number; comparisonAttemptsReserved: 0; probeExecutionsReserved: 1; paidUsd: 0 };

function object(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("invalid evidence object");
  const v = value as Record<string, unknown>;
  if (Object.keys(v).length !== keys.length || Object.keys(v).some((key) => !keys.includes(key)) || keys.some((key) => !Object.hasOwn(v, key))) throw new Error("missing or extra evidence field");
  return v;
}
function ns(value: unknown): bigint {
  if (typeof value !== "string" || !NS.test(value)) throw new Error("invalid monotonic timestamp");
  const result = BigInt(value);
  if (result > MAX_NS) throw new Error("monotonic timestamp overflow");
  return result;
}
function positiveBytes(value: unknown): number {
  if (!Number.isSafeInteger(value) || (value as number) <= 0) throw new Error("invalid resident bytes");
  return value as number;
}
function pidNumber(value: unknown): number {
  if (!Number.isSafeInteger(value) || (value as number) <= 0 || (value as number) > 2147483647) throw new Error("invalid host PID");
  return value as number;
}
function canonical(value: unknown): string { return JSON.stringify(value) + "\n"; }
function digest(text: string): string { return createHash("sha256").update(text).digest("hex"); }
function readBounded(path: string, max: number): string {
  const stat = lstatSync(path);
  if (!stat.isFile() || stat.size > max || stat.size === 0) throw new Error("missing, unsafe, or oversized evidence");
  return readFileSync(path, "utf8");
}
function readJson(path: string): Record<string, unknown> {
  const text = readBounded(path, 4096);
  const value: unknown = JSON.parse(text);
  if (canonical(value) !== text) throw new Error("noncanonical evidence");
  return value as Record<string, unknown>;
}
function syncFile(path: string, content: string): void {
  const fd = openSync(path, "wx", 0o600);
  try { writeFileSync(fd, content); fsyncSync(fd); } finally { closeSync(fd); }
}
function syncDir(path: string): void {
  const fd = openSync(path, "r");
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
function checkPlan(value: unknown): ProbePlan {
  const v = object(value, ["attemptId", "sourceSha", "previousAttemptsCharged", "comparisonAttemptsReserved", "probeExecutionsReserved", "paidUsd"]);
  if (typeof v.attemptId !== "string" || !/^[a-z0-9][a-z0-9-]{0,63}$/.test(v.attemptId) ||
      typeof v.sourceSha !== "string" || !/^[a-f0-9]{40}$/.test(v.sourceSha) ||
      v.previousAttemptsCharged !== 2 ||
      v.comparisonAttemptsReserved !== 0 || v.probeExecutionsReserved !== 1 || v.paidUsd !== 0) throw new Error("invalid test-only allowance");
  return v as ProbePlan;
}
function reservationAt(dir: string): { hash: string; time: bigint } {
  const path = join(dir, RESERVATION);
  const text = readBounded(path, 4096);
  const row = object(JSON.parse(text), ["contract", "plan", "reservedAtUtc", "reservedAtNs"]);
  if (canonical(row) !== text || row.contract !== "algal.lab.test-probe-reservation.v2" ||
      typeof row.reservedAtUtc !== "string" || !Number.isFinite(Date.parse(row.reservedAtUtc))) throw new Error("invalid reservation");
  checkPlan(row.plan);
  return { hash: digest(text), time: ns(row.reservedAtNs) };
}

/** Exclusive, durable reservation before any callback. A test probe consumes no comparison attempt. */
export function reserveTestProbe(dir: string, plan: ProbePlan): string {
  checkPlan(plan);
  mkdirSync(dir, { mode: 0o700 }); // Must not already exist, even after a failure.
  const text = canonical({ contract: "algal.lab.test-probe-reservation.v2", plan,
    reservedAtUtc: new Date().toISOString(), reservedAtNs: process.hrtime.bigint().toString() });
  syncFile(join(dir, RESERVATION), text);
  syncDir(dir);
  syncDir(dirname(dir)); // Persist the new directory entry, not just its contents.
  syncFile(join(dir, TRACE), "");
  syncDir(dir);
  return digest(text); // An independent observer must retain this before start.
}

/** Reject altered evidence or a second start. The witness must be held outside this writer. */
export async function startTestProbe<T>(dir: string, witnessedDigest: string, execute: () => Promise<T> | T): Promise<T> {
  if (!SHA.test(witnessedDigest)) throw new Error("missing independent reservation witness");
  const reservation = reservationAt(dir);
  if (reservation.hash !== witnessedDigest) throw new Error("reservation witness mismatch");
  if (existsSync(join(dir, START))) throw new Error("probe already started; never retry an uncertain callback");
  const trace = join(dir, TRACE);
  if (!lstatSync(trace).isFile() || lstatSync(trace).size !== 0) throw new Error("probe trace is not empty");
  const startedAtNs = process.hrtime.bigint();
  if (startedAtNs <= reservation.time) throw new Error("non-monotonic reservation/start");
  syncFile(join(dir, START), canonical({ contract: "algal.lab.test-probe-start.v2", reservationSha256: reservation.hash,
    startedAtUtc: new Date().toISOString(), startedAtNs: startedAtNs.toString() }));
  syncDir(dir);
  auditProbe(dir, witnessedDigest); // Read back durable evidence before execution.
  return await execute(); // Error/uncertainty is retained; no second invocation.
}

export function auditProbe(dir: string, witnessedDigest: string): void {
  if (!SHA.test(witnessedDigest)) throw new Error("missing independent reservation witness");
  const reservation = reservationAt(dir);
  if (reservation.hash !== witnessedDigest) throw new Error("reservation witness mismatch");
  const marker = object(readJson(join(dir, START)), ["contract", "reservationSha256", "startedAtUtc", "startedAtNs"]);
  if (marker.contract !== "algal.lab.test-probe-start.v2" || marker.reservationSha256 !== reservation.hash ||
      typeof marker.startedAtUtc !== "string" || !Number.isFinite(Date.parse(marker.startedAtUtc)) ||
      ns(marker.startedAtNs) <= reservation.time) throw new Error("invalid start marker");
}

/** Pure replay: expectedPid is the separately recorded child spawn PID, never read from trace. */
export function auditRawRss(text: string, expectedPid: number, expected?: { count: number; baselineBytes: number; peakBytes: number }): { count: number; baselineBytes: number; peakBytes: number } {
  pidNumber(expectedPid);
  if (Buffer.byteLength(text) > MAX_TRACE_BYTES) throw new Error("oversized RSS trace");
  if (text && !text.endsWith("\n")) throw new Error("truncated RSS trace");
  const lines = text ? text.slice(0, -1).split("\n") : [];
  if (lines.length === 0) throw new Error("missing RSS sample");
  if (lines.length > MAX_SAMPLES) throw new Error("too many RSS samples");
  let first = 0, peak = 0, prior = 0n;
  for (const [index, line] of lines.entries()) {
    const row = object(JSON.parse(line), ["pid", "index", "readings", "measuredBytes"]);
    if (JSON.stringify(row) !== line || pidNumber(row.pid) !== expectedPid || row.index !== index || !Array.isArray(row.readings) || row.readings.length !== 3) throw new Error("invalid or foreign RSS sample");
    const stamps: bigint[] = [], bytes: number[] = [];
    for (const [position, raw] of row.readings.entries()) {
      const r = object(raw, ["source", "atNs", "bytes"]);
      if (r.source !== (position === 1 ? "proc_pid_rusage" : "proc_pidinfo")) throw new Error("wrong RSS sampler order");
      stamps.push(ns(r.atNs)); bytes.push(positiveBytes(r.bytes));
    }
    if (stamps[0]! <= prior || stamps[0]! >= stamps[1]! || stamps[1]! >= stamps[2]! || stamps[2]! - stamps[0]! > MAX_SPAN_NS) throw new Error("stale or unordered RSS sample");
    prior = stamps[2]!;
    const measured = checkedRss(bytes[0]!, bytes[1]!, bytes[2]!);
    if (row.measuredBytes !== measured) throw new Error("RSS result does not replay");
    if (index === 0) first = measured;
    peak = Math.max(peak, measured);
  }
  const result = { count: lines.length, baselineBytes: first, peakBytes: peak };
  if (expected && (expected.count !== result.count || expected.baselineBytes !== first || expected.peakBytes !== peak)) throw new Error("RSS aggregate mismatch");
  return result;
}

/** Append one synced sample; never repair a malformed/uncertain trace in place. */
export function appendRawRss(dir: string, witnessedDigest: string, sample: RawRssSample, expectedPid: number): void {
  auditProbe(dir, witnessedDigest);
  const path = join(dir, TRACE);
  const old = lstatSync(path);
  if (!old.isFile() || old.size > MAX_TRACE_BYTES) throw new Error("invalid RSS trace file");
  const prior = readFileSync(path, "utf8");
  const next = prior + canonical(sample);
  auditRawRss(next, expectedPid);
  const fd = openSync(path, "a");
  try { writeFileSync(fd, canonical(sample)); fsyncSync(fd); } finally { closeSync(fd); }
}

/** Fixture-only independent join: uncertainty is not success, even with an effect. */
export function auditFixtureEffects(effectText: string, journalTerminals: readonly unknown[]): { uncertainIds: string[]; completeIds: string[] } {
  if (journalTerminals.length > 512) throw new Error("too many terminal jobs");
  const states = new Map<string, string>();
  for (const value of journalTerminals) {
    const row = parseRecord(value);
    if (!["complete", "uncertain", "cancelled", "expired"].includes(row.status) || states.has(row.job.id)) throw new Error("invalid or duplicate terminal job");
    states.set(row.job.id, row.status);
  }
  const log = parseEffectLog(effectText, new Set(states.keys()));
  const effects = new Set(log.ids);
  for (const [id, status] of states) {
    if (status === "complete" && !effects.has(id)) throw new Error("fabricated complete without fixture effect");
    if ((status === "cancelled" || status === "expired") && effects.has(id)) throw new Error("effect on non-dispatched job");
  }
  return { uncertainIds: [...states].filter(([, state]) => state === "uncertain").map(([id]) => id).sort(),
    completeIds: [...states].filter(([, state]) => state === "complete").map(([id]) => id).sort() };
}
