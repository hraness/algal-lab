import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { FileStore, canonicalize, digestCanonical, type Executor, type JsonValue } from "@hraness/algal";
import { CORPUS } from "./corpus";
import { createLiveExecutor, type LiveObservation } from "./live";
import { ARMS, CONTEXT_ARM, CONTEXT_BUDGETS, LIMITS, runArm, scriptedExecutor, type ArmResult } from "./study";

const args = process.argv.slice(2);
const allowed = new Set(["--out", "--seeds", "--live", "--max-calls", "--max-usd", "--context-feedback"]);
const options = new Map<string, string>();
for (let i = 0; i < args.length; i++) {
  const key = args[i]!;
  if (!allowed.has(key) || options.has(key)) throw new Error("usage: bun experiments/task-optimization/run.ts --out NEW_DIRECTORY [--seeds 11,23,37] [--context-feedback] [--live --max-calls N --max-usd N]");
  if (key === "--live" || key === "--context-feedback") options.set(key, "true");
  else { const value = args[++i]; if (!value || value.startsWith("--")) throw new Error(`missing ${key}`); options.set(key, value); }
}
const directory = options.get("--out");
if (!directory) throw new Error("--out NEW_DIRECTORY is required");
const seedText = options.get("--seeds") ?? "11,23,37";
if (!/^[1-9][0-9]{0,5}(,[1-9][0-9]{0,5}){0,2}$/.test(seedText)) throw new Error("provide one to three distinct integer seeds");
const seeds = seedText.split(",").map(Number);
if (new Set(seeds).size !== seeds.length) throw new Error("duplicate seed");
const live = options.has("--live");
const arms = options.has("--context-feedback") ? [...ARMS, CONTEXT_ARM] : ARMS;
if (live && seeds.length !== 1) throw new Error("live mode requires exactly one explicit --seeds value; run each seed in a fresh archive");
if (live && (!options.has("--max-calls") || !options.has("--max-usd"))) throw new Error("live mode requires explicit request and estimated-dollar caps");
if (!live && (options.has("--max-calls") || options.has("--max-usd"))) throw new Error("live budgets require --live");
const provider = live ? createLiveExecutor({ maxCalls: Number(options.get("--max-calls")), maxEstimatedUSD: Number(options.get("--max-usd")) }) : undefined;
await mkdir(dirname(directory), { recursive: true });
await mkdir(directory); // Refuse an existing archive, including an interrupted one.
const save = (name: string, value: unknown) => writeFile(join(directory, name), canonicalize(value as JsonValue) + "\n", { flag: "wx", mode: 0o600 });
const lifetime = new AbortController();
const interrupt = () => { process.exitCode = 130; lifetime.abort(); };
const terminate = () => { process.exitCode = 143; lifetime.abort(); };
process.on("SIGINT", interrupt); process.on("SIGTERM", terminate);
const base = provider ?? scriptedExecutor();
const executor: Executor = { ...base,
  async execute(request, signal) { lifetime.signal.throwIfAborted(); return base.execute(request, AbortSignal.any([lifetime.signal, ...(signal ? [signal] : [])])); },
  ...(base.executeEffect ? { async executeEffect(request, signal) {
    lifetime.signal.throwIfAborted(); return base.executeEffect!(request, AbortSignal.any([lifetime.signal, ...(signal ? [signal] : [])]));
  } } satisfies Partial<Executor> : {}),
};
const results: ArmResult[] = [];
let completed = false;
await save("intent.json", { contract: "algal.lab.task-study.v1", mode: live ? "live" : "scripted", seeds, arms,
  corpus: CORPUS, corpusDigest: digestCanonical(CORPUS as unknown as JsonValue), limits: LIMITS,
  ...(options.has("--context-feedback") ? { contextReviserBudgets: CONTEXT_BUDGETS } : {}),
  source: "https://github.com/hraness/textbutler/blob/bd7765af541a24da4cdfaed3386735eee531c1a7/packages/textbutler/src/habitat-program.ts",
  qualification: "Public synthetic policy cases; no production conversations or messaging effects. Scripted runs are orchestration checks.",
  executor: provider?.configuration ?? { id: base.id, live: false } });
try {
  for (const seed of seeds) for (const arm of arms) {
    lifetime.signal.throwIfAborted();
    const name = `${seed}-${arm}`;
    const result = await runArm(arm, seed, new FileStore(join(directory, name, "store")), executor);
    results.push(result);
    await save(`${name}.json`, result);
    await save(`${name}-task.json`, result.frozenTask);
    console.error(JSON.stringify({ seed, arm, accuracy: result.metrics.accuracy, invalid: result.metrics.invalid, calls: result.calls }));
    if (provider?.observations.at(-1)?.status === "failed") throw new Error("live provider failed; campaign stopped without retry");
  }
  completed = true;
} finally {
  process.off("SIGINT", interrupt); process.off("SIGTERM", terminate);
  const observations: LiveObservation[] = provider?.observations ?? [];
  await save("transport.json", { observations, estimatedUSD: observations.reduce((n, row) => n + row.estimatedUSD, 0),
    pricing: "Standard uncached token estimate; not invoice reconciliation" });
  await save("summary.json", { complete: completed, mode: live ? "live" : "scripted", cancelled: lifetime.signal.aborted,
    results: results.map(({ report: _report, frozenTask: _task, ...summary }) => summary),
    limitation: "The corpus is small and synthetic. Seeds vary demonstration ordering. A scripted result does not measure LLM quality; a live result does not establish production user benefit." });
}
