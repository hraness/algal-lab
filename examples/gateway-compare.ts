/** Live replicated comparison through ALGAL's pinned Vercel AI Gateway executor.
 * The scripted control arms run offline in the same archive; the live arm's
 * model calls are exactly the plan's proposal slots. Credentials stay in the
 * operator environment; every run owns a fresh archive. */
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { canonicalize } from "@hraness/algal";
import { readJsonFile } from "../src/artifacts";
import { liveCallBudget, parseComparisonPlan, runComparison } from "../src/comparison";
import { json } from "../src/contracts";
import { createGatewayExecutor, GATEWAY_DEFAULT_MAX_CALLS, GATEWAY_MAX_CALLS, type GatewayExecutor } from "../src/gateway-executor";

const args = process.argv.slice(2);
if (args.length !== 4 || args[0] !== "--plan" || args[2] !== "--out") throw new Error("usage: bun examples/gateway-compare.ts --plan PATH --out NEW_DIRECTORY");
function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required; select an observed Gateway model and provider explicitly`);
  return value;
}
const input = await readJsonFile(args[1]!);
const plan = parseComparisonPlan(input);
/** Operator call budget. The default admits only the twelve-call smoke; the
 * replicated comparison must raise it explicitly, up to the executor's cap. */
const configuredLimit = process.env.ALGAL_LAB_GATEWAY_MAX_CALLS;
if (configuredLimit !== undefined && (!/^[1-9][0-9]{0,2}$/.test(configuredLimit) || Number(configuredLimit) > GATEWAY_MAX_CALLS)) {
  throw new Error(`ALGAL_LAB_GATEWAY_MAX_CALLS must be an integer 1..${GATEWAY_MAX_CALLS}`);
}
const maxCallsLimit = configuredLimit === undefined ? GATEWAY_DEFAULT_MAX_CALLS : Number(configuredLimit);
// The executor budget is the live arm's exact slot count, never the limit itself.
const maxCalls = liveCallBudget(plan);
if (maxCalls > maxCallsLimit) throw new Error(`this comparison needs ${maxCalls} model calls; ALGAL_LAB_GATEWAY_MAX_CALLS permits ${maxCallsLimit} (default ${GATEWAY_DEFAULT_MAX_CALLS}, maximum ${GATEWAY_MAX_CALLS})`);
const model = required("GATEWAY_MODEL");
const provider = required("GATEWAY_PROVIDER");
const directory = args[3]!;
await mkdir(dirname(directory), { recursive: true });
await mkdir(directory);
const save = async (name: string, value: unknown) => writeFile(join(directory, name), canonicalize(json(value)) + "\n", { flag: "wx", mode: 0o600 });
await save("intent.json", { plan, model, provider, maxCalls });
const lifetime = new AbortController();
const stop = (code: number) => { if (!lifetime.signal.aborted) { process.exitCode = code; lifetime.abort(); } };
const interrupt = () => stop(130);
const terminate = () => stop(143);
process.on("SIGINT", interrupt); process.on("SIGTERM", terminate);
let executor: GatewayExecutor | undefined;
try {
  executor = createGatewayExecutor({ model, provider, maxCalls, signal: lifetime.signal });
  // The explicit limit is recorded only when configured, so the control-run
  // archive shape stays comparable with scripted `bun run compare` output.
  await save("executor.json", { configuration: executor.configuration, configurationDigest: executor.configurationDigest,
    ...(configuredLimit !== undefined ? { maxCallsLimit } : {}) });
  const report = await runComparison(input, join(directory, "comparison"), { executor, progress: (message) => console.error(message) });
  console.log(JSON.stringify({ comparison: `${directory}/comparison`, arms: report.arms, studies: report.studies.length, rows: report.rows.length, controls: report.controls }));
} finally {
  try { await executor?.settle(); }
  finally {
    await save("gateway.json", { configuration: executor?.configuration ?? null, configurationDigest: executor?.configurationDigest ?? null,
      observations: executor?.observations ?? [], cancelled: lifetime.signal.aborted });
    process.off("SIGINT", interrupt); process.off("SIGTERM", terminate);
  }
}
