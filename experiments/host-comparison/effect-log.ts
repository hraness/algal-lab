import { readFileSync } from "node:fs";
import { idPattern } from "./protocol";

const maxLogBytes = 4_000_000;

export type EffectLog = { ids: string[]; count: number };

function parseEffectRecord(value: unknown): string {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("effect record must be an object");
  const record = value as Record<string, unknown>;
  if (Object.keys(record).length !== 1 || !("id" in record)) throw new Error("unexpected effect record field");
  if (typeof record.id !== "string" || !idPattern.test(record.id)) throw new Error("invalid effect identifier");
  return record.id;
}

/**
 * Parse the durable effect log without consulting host state or the event stream.
 * The sorted IDs make the oracle result deterministic; duplicate records fail closed.
 */
export function parseEffectLog(text: string, submittedJobIds: ReadonlySet<string>): EffectLog {
  if (Buffer.byteLength(text, "utf8") > maxLogBytes) throw new Error("effect log oversized");
  if (text === "") return { ids: [], count: 0 };
  if (!text.endsWith("\n")) throw new Error("effect log has an incomplete final line");
  const ids = new Set<string>();
  for (const line of text.slice(0, -1).split("\n")) {
    if (line.trim() === "") throw new Error("effect log has an empty line");
    let value: unknown;
    try { value = JSON.parse(line); } catch { throw new Error("effect log has invalid JSON"); }
    const id = parseEffectRecord(value);
    if (!submittedJobIds.has(id)) throw new Error("effect ID was not submitted");
    if (ids.has(id)) throw new Error("effect ID was recorded twice");
    ids.add(id);
  }
  const ordered = [...ids].sort();
  return { ids: ordered, count: ordered.length };
}

export function readEffectLog(path: string, submittedJobIds: ReadonlySet<string>): EffectLog {
  let text: string;
  try {
    text = readFileSync(path, "utf8");
  } catch (error: unknown) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") return parseEffectLog("", submittedJobIds);
    throw error;
  }
  return parseEffectLog(text, submittedJobIds);
}
