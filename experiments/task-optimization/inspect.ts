import { readFile, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import {
  FileStore, MemoryStore, canonicalize, digestCanonical, parseHabitatBudget, parseRunReceipt, replayExecutor,
  type JsonValue,
} from "@hraness/algal";
import { ARMS, runArm, type Arm } from "./study";

async function readJson(path: string): Promise<unknown> {
  if ((await stat(path)).size > 4_194_304) throw new Error("study file exceeds 4 MiB");
  const bytes = await readFile(path);
  if (bytes.byteLength > 4_194_304) throw new Error("study file changed beyond limit");
  return JSON.parse(bytes.toString("utf8"));
}
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("expected study object");
  return value as Record<string, unknown>;
}

/** Rerun the complete search and its audits with captured effects. Recomputing
 * only the displayed percentages would not check candidate selection or cost. */
export async function inspectStudyArm(directory: string, seed: number, arm: Arm) {
  if (!Number.isSafeInteger(seed) || seed < 1 || seed > 999999 || !(ARMS as readonly string[]).includes(arm)) throw new Error("invalid study identity");
  const name = `${seed}-${arm}`, original = object(await readJson(join(directory, `${name}.json`)));
  const fields = ["arm", "seed", "datasetDigest", "selectedManifest", "metrics", "calls", "work", "elapsedMs", "report", "frozenTask"];
  if (Object.keys(original).length !== fields.length || fields.some(key => !Object.hasOwn(original, key))) throw new Error("unknown or missing study fields");
  if (original.arm !== arm || original.seed !== seed || typeof original.elapsedMs !== "number" || !Number.isFinite(original.elapsedMs) || original.elapsedMs < 0) throw new Error("invalid study identity or elapsed time");
  const budget = parseHabitatBudget(object(original.report).budget);
  if (budget.runs.length > 128) throw new Error("study run count exceeds declared limit");
  const store = new FileStore(join(directory, name, "store"));
  const effects = [];
  for (const row of budget.runs) {
    const raw = await store.getReceipt(row.receipt);
    if (!raw || digestCanonical(raw) !== row.receipt) throw new Error("missing or changed receipt");
    const receipt = parseRunReceipt(raw);
    if (receipt.manifestDigest !== row.manifest || receipt.work.agentCalls !== row.charged.attempts || receipt.work.units !== row.charged.work) throw new Error("budget does not match receipt");
    effects.push(...receipt.effects);
    if (effects.length > 128) throw new Error("study effect count exceeds limit");
  }
  const reproduced = await runArm(arm, seed, new MemoryStore(), replayExecutor(effects));
  const { elapsedMs: _oldTime, ...oldContent } = original;
  const { elapsedMs: _newTime, ...newContent } = reproduced;
  if (canonicalize(oldContent as JsonValue) !== canonicalize(newContent as unknown as JsonValue)) throw new Error("study does not reproduce from recorded effects");
  return { seed, arm, ok: true, receipts: budget.runs.length, attempts: budget.charged.attempts,
    reportDigest: reproduced.report.digest, metrics: reproduced.metrics };
}

if (import.meta.main) {
  const [directory, seedText] = process.argv.slice(2);
  if (!directory || !seedText || !/^[1-9][0-9]{0,5}$/.test(seedText) || process.argv.length !== 4) throw new Error("usage: bun experiments/task-optimization/inspect.ts ARCHIVE SEED");
  const results = [];
  for (const arm of ARMS) results.push(await inspectStudyArm(directory, Number(seedText), arm));
  const result = { contract: "algal.lab.task-study-inspection.v1", ok: true, results,
    limitation: "Offline reproduction checks recorded execution, selection, and scores. It does not authenticate a provider, verify an invoice, or establish production quality." };
  await writeFile(join(directory, "inspection.json"), canonicalize(result as unknown as JsonValue) + "\n", { flag: "wx", mode: 0o600 });
  console.log(JSON.stringify(result));
}
