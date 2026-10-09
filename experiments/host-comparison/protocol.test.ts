import { expect, test } from "bun:test";
import { parseEffectLog } from "./effect-log";
import { parseCommand, parseRecord } from "./protocol";

const job = { id: "one", owner: "session", delay_ms: 20, ttl_ms: 30000, fault: "none" } as const;
test("the host protocol rejects executable authority, coercions, and unbounded inputs", () => {
  expect(parseCommand({ op: "submit", job })).toEqual({ op: "submit", job });
  for (const invalid of [
    { ...job, command: "echo unsafe" }, { ...job, id: "../escape" }, { ...job, owner: "x".repeat(65) },
    { ...job, delay_ms: "20" }, { ...job, delay_ms: -1 }, { ...job, ttl_ms: 30001 }, { ...job, fault: ["none"] },
  ]) expect(() => parseCommand({ op: "submit", job: invalid })).toThrow();
  expect(() => parseCommand({ op: "observe", command: "ignored?" })).toThrow();
});
test("recovery refuses malformed retained authority and incomplete success records", () => {
  const row = { job, status: "uncertain", reason: "host_restart" } as const;
  expect(parseRecord(row)).toEqual(row);
  for (const invalid of [{ ...row, status: "retry" }, { ...row, status: "complete" }, { ...row, digest: "fake" }, { ...row, job: { ...job, id: "../escape" } }, { ...row, queue_ms: Infinity }, { ...row, runner: "sh" }]) expect(() => parseRecord(invalid)).toThrow();
});
test("the effect oracle returns a deterministic submitted-ID set", () => {
  expect(parseEffectLog('{"id":"two"}\n{"id":"one"}\n', new Set(["one", "two"]))).toEqual({ ids: ["one", "two"], count: 2 });
  expect(parseEffectLog("", new Set(["one"]))).toEqual({ ids: [], count: 0 });
});
test("the effect oracle fails closed on incomplete, unknown, invalid, duplicate, and foreign records", () => {
  const submitted = new Set(["one"]);
  for (const invalid of [
    '{"id":"one"}',
    '{"id":"one","extra":true}\n',
    '{"id":"../escape"}\n',
    '{"id":"other"}\n',
    '{"id":"one"}\n{"id":"one"}\n',
    '{"id":"one"}\n\n',
    '{"id":"one"\n',
  ]) expect(() => parseEffectLog(invalid, submitted)).toThrow();
});
