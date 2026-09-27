import { readFile, mkdir, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { canonicalize, FileStore, type Executor, type JsonValue } from "@hraness/algal";
import { createLiveExecutor } from "./live";
import { scriptedExecutor, studyCases } from "./study";
import { buildKnowledge, FRESH_CORPUS, RETENTION_BOUNDS, runRetention, verifyRetention } from "./retention";

const args = process.argv.slice(2), options = new Map<string, string>();
if (args[0] === "--inspect") {
  const directory = args[1];
  if (!directory || args.length !== 2) throw new Error("usage: retention-run.ts --inspect ARCHIVE");
  const inspection = await verifyRetention(JSON.parse(await boundedRead(join(directory, "result.json"))), new FileStore(join(directory, "store")));
  await writeFile(join(directory, "inspection.json"), canonicalize(inspection as unknown as JsonValue) + "\n", { flag: "wx", mode: 0o600 });
  console.log(JSON.stringify(inspection)); process.exit(0);
}
const allowed = ["--from", "--out", "--live", "--max-calls", "--max-usd"];
for (let index = 0; index < args.length; index++) {
  const key = args[index]!;
  if (!allowed.includes(key) || options.has(key)) throw new Error("usage: bun experiments/task-optimization/retention-run.ts --from FEEDBACK_ARM.json --out NEW_DIRECTORY [--live --max-calls N --max-usd N]");
  if (key === "--live") options.set(key, "true");
  else { const value = args[++index]; if (!value || value.startsWith("--")) throw new Error(`missing ${key}`); options.set(key, value); }
}
const from = options.get("--from"), directory = options.get("--out"), live = options.has("--live");
if (!from || !directory) throw new Error("--from and --out are required");
if (live !== (options.has("--max-calls") && options.has("--max-usd")) || (!live && (options.has("--max-calls") || options.has("--max-usd")))) throw new Error("live mode requires explicit request and estimated-dollar caps");
async function boundedRead(path: string): Promise<string> {
  const metadata = await stat(path);
  if (!metadata.isFile() || metadata.size > 2_097_152) throw new Error("source campaign exceeds read bound");
  const bytes = await readFile(path, "utf8");
  if (Buffer.byteLength(bytes) > 2_097_152) throw new Error("source campaign exceeds read bound");
  return bytes;
}
const sourceBytes = await boundedRead(from);
const source: unknown = JSON.parse(sourceBytes);
if (!source || typeof source !== "object" || Array.isArray(source) || !("arm" in source) || source.arm !== "feedback" || !("seed" in source) || typeof source.seed !== "number" || !("report" in source)) throw new Error("requires a feedback-arm result file");
const built = buildKnowledge(source.report, studyCases(source.seed));
await mkdir(dirname(directory), { recursive: true }); await mkdir(directory);
const save = (name: string, value: unknown) => writeFile(join(directory, name), canonicalize(value as JsonValue) + "\n", { flag: "wx", mode: 0o600 });
await save("intent.json", { contract: "algal.lab.retention-intent.v1", mode: live ? "live" : "scripted", sourceSeed: source.seed, freshCorpus: FRESH_CORPUS, bounds: RETENTION_BOUNDS,
  qualification: "Public synthetic transfer cases; no messages can be sent. Scripted runs test mechanics, not model efficacy." });
if (!built.eligible) { await save("ineligible.json", built); console.log(JSON.stringify(built)); process.exit(0); }
await save("knowledge.json", built.knowledge);
const provider = live ? createLiveExecutor({ maxCalls: Number(options.get("--max-calls")), maxEstimatedUSD: Number(options.get("--max-usd")) }) : undefined;
if (provider) {
  const original = JSON.parse(await boundedRead(join(dirname(from), "intent.json")));
  const configuration = provider.configuration as Record<string, JsonValue>;
  if (original.mode !== "live") throw new Error("live transfer requires an original live campaign");
  for (const field of ["model", "provider", "endpoint", "fallback", "reasoningEffort", "serviceTier", "maxCompletionTokens", "maxInputBytes"]) {
    if (canonicalize(original.executor[field]) !== canonicalize(configuration[field]!)) throw new Error(`original learning and fresh evaluation differ in ${field}`);
  }
}
const base = provider ?? scriptedExecutor(), lifetime = new AbortController();
const interrupt = () => { process.exitCode = 130; lifetime.abort(); };
const terminate = () => { process.exitCode = 143; lifetime.abort(); };
process.on("SIGINT", interrupt); process.on("SIGTERM", terminate);
const executor: Executor = { ...base,
  async execute(request, signal) { lifetime.signal.throwIfAborted(); return base.execute(request, AbortSignal.any([lifetime.signal, ...(signal ? [signal] : [])])); },
  ...(base.executeEffect ? { async executeEffect(request, signal) { lifetime.signal.throwIfAborted(); return base.executeEffect!(request, AbortSignal.any([lifetime.signal, ...(signal ? [signal] : [])])); } } satisfies Partial<Executor> : {}),
};
let complete = false;
try {
  const result = await runRetention({ knowledge: built.knowledge, store: new FileStore(join(directory, "store")), executor,
    onFrozen: frozen => save("frozen.json", frozen), onSelected: selected => save("selection-before-audit.json", selected) });
  if (provider?.observations.some(row => row.status === "failed")) throw new Error("provider failure; transfer is incomplete and no serving task was published");
  await save("result.json", result); await save("serving-task.json", result.servingTask); await save("rollback-task.json", result.rollbackTask);
  complete = true;
  console.log(JSON.stringify({ complete, selection: result.selection, originalLearningCost: result.originalLearningCost, freshEvaluationCost: result.freshEvaluationCost,
    audit: result.audits.map(({ arm, metrics }) => ({ arm, metrics })) }, null, 2));
} finally {
  process.off("SIGINT", interrupt); process.off("SIGTERM", terminate);
  await save("transport.json", { complete, cancelled: lifetime.signal.aborted, configuration: provider?.configuration ?? { id: base.id, live: false }, observations: provider?.observations ?? [],
    estimatedUSD: (provider?.observations ?? []).reduce((sum, row) => sum + row.estimatedUSD, 0), pricing: "Standard uncached estimate; not invoice reconciliation" });
}
