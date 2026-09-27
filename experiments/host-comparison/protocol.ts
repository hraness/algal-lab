/** Operational protocol only: these timestamps never enter ALGAL receipts. */
export type Job = { id: string; owner: string; delay_ms: number; ttl_ms: number; fault: "none" | "before_dispatch" | "after_effect" | "hold_after_effect" };
export type Command = { op: "submit"; job: Job } | { op: "cancel"; id: string } | { op: "owner_down"; owner: string } | { op: "observe" } | { op: "stop" } | { op: "crash_owner" };
export type Status = "queued" | "running" | "complete" | "cancelled" | "expired" | "uncertain";
export type RecordRow = { job: Job; status: Status; reason: string; queue_ms?: number; digest?: string };
export const idPattern = /^[a-zA-Z0-9_-]{1,64}$/;
function object(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("expected object");
  return value as Record<string, unknown>;
}
function fields(value: Record<string, unknown>, keys: string[]): void {
  if (Object.keys(value).some((key) => !keys.includes(key)) || keys.some((key) => !(key in value))) throw new Error("unexpected or missing field");
}
function identifier(value: unknown): string {
  if (typeof value !== "string" || !idPattern.test(value)) throw new Error("invalid identifier");
  return value;
}
export function parseJob(value: unknown): Job {
  const v = object(value); fields(v, ["id", "owner", "delay_ms", "ttl_ms", "fault"]);
  for (const key of ["delay_ms", "ttl_ms"]) if (!Number.isInteger(v[key]) || Number(v[key]) < 0 || Number(v[key]) > 30_000) throw new Error("invalid duration");
  if (typeof v.fault !== "string" || !["none", "before_dispatch", "after_effect", "hold_after_effect"].includes(v.fault)) throw new Error("invalid fault");
  return { id: identifier(v.id), owner: identifier(v.owner), delay_ms: Number(v.delay_ms), ttl_ms: Number(v.ttl_ms), fault: v.fault as Job["fault"] };
}
export function parseRecord(value: unknown): RecordRow {
  const v = object(value);
  if (Object.keys(v).some((key) => !["job", "status", "reason", "queue_ms", "digest"].includes(key))) throw new Error("invalid journal field");
  if (typeof v.status !== "string" || !["queued", "running", "complete", "cancelled", "expired", "uncertain"].includes(v.status)) throw new Error("invalid journal status");
  if (typeof v.reason !== "string" || v.reason.length > 128) throw new Error("invalid journal reason");
  const row: RecordRow = { job: parseJob(v.job), status: v.status as Status, reason: v.reason };
  if (v.queue_ms !== undefined) { if (typeof v.queue_ms !== "number" || !Number.isFinite(v.queue_ms) || v.queue_ms < 0) throw new Error("invalid queue measurement"); row.queue_ms = v.queue_ms; }
  if (v.digest !== undefined) { if (typeof v.digest !== "string" || !/^sha256:[a-f0-9]{64}$/.test(v.digest)) throw new Error("invalid receipt digest"); row.digest = v.digest; }
  if (row.status === "complete" && !row.digest) throw new Error("complete record lacks receipt digest");
  return row;
}
export function parseCommand(value: unknown): Command {
  const v = object(value);
  if (v.op === "submit") { fields(v, ["op", "job"]); return { op: v.op, job: parseJob(v.job) }; }
  if (v.op === "cancel") { fields(v, ["op", "id"]); return { op: v.op, id: identifier(v.id) }; }
  if (v.op === "owner_down") { fields(v, ["op", "owner"]); return { op: v.op, owner: identifier(v.owner) }; }
  if (v.op === "observe" || v.op === "stop" || v.op === "crash_owner") { fields(v, ["op"]); return { op: v.op }; }
  throw new Error("invalid operation");
}
