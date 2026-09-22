/** Optional live inference through ALGAL's pinned Vercel AI Gateway executor.
 * Credentials stay in the operator environment; every run owns a fresh archive. */
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { canonicalize } from "@hraness/algal";
import { readJsonFile } from "../src/artifacts";
import { json, parseProtocol } from "../src/contracts";
import { createGatewayExecutor, type GatewayExecutor } from "../src/gateway-executor";
import { runStudy } from "../src/study";

const args = process.argv.slice(2);
if (args.length !== 4 || args[0] !== "--protocol" || args[2] !== "--out") throw new Error("usage: bun examples/gateway-study.ts --protocol PATH --out NEW_DIRECTORY");
function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required; select an observed Gateway model and provider explicitly`);
  return value;
}
const protocol = parseProtocol(await readJsonFile(args[1]!));
const maxCalls = protocol.replicateSeeds.length * 3 * protocol.researchers * protocol.rounds;
if (maxCalls > 12) throw new Error("this smoke entry point permits at most 12 model calls");
const model = required("GATEWAY_MODEL");
const provider = required("GATEWAY_PROVIDER");
const directory = args[3]!;
await mkdir(dirname(directory), { recursive: true });
await mkdir(directory);
const save = async (name: string, value: unknown) => writeFile(join(directory, name), canonicalize(json(value)) + "\n", { flag: "wx", mode: 0o600 });
await save("intent.json", { protocol, model, provider, maxCalls });
const lifetime = new AbortController();
const stop = (code: number) => { if (!lifetime.signal.aborted) { process.exitCode = code; lifetime.abort(); } };
const interrupt = () => stop(130);
const terminate = () => stop(143);
process.on("SIGINT", interrupt); process.on("SIGTERM", terminate);
let executor: GatewayExecutor | undefined;
try {
  executor = createGatewayExecutor({ model, provider, maxCalls, signal: lifetime.signal });
  await save("executor.json", { configuration: executor.configuration, configurationDigest: executor.configurationDigest });
  const report = await runStudy(protocol, join(directory, "study"), { executor, progress: (message) => console.error(message) });
  console.log(JSON.stringify({ study: `${directory}/study`, attempts: report.attempts.length, summaries: report.summaries }));
} finally {
  try { await executor?.settle(); }
  finally {
    await save("gateway.json", { configuration: executor?.configuration ?? null, configurationDigest: executor?.configurationDigest ?? null,
      observations: executor?.observations ?? [], cancelled: lifetime.signal.aborted });
    process.off("SIGINT", interrupt); process.off("SIGTERM", terminate);
  }
}
