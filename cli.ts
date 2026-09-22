#!/usr/bin/env bun
import { commandExecutor } from "@hraness/algal";
import { readJsonFile } from "./src/artifacts";
import { runStudy, verifyStudy } from "./src/study";

const HELP = `algal-lab — bounded research on ALGAL

bun run lab study --protocol <file.json> --out <new-directory>
  [--executor-command <operator-owned-command>]
bun run lab verify <run-directory>

Without --executor-command, study uses a deterministic no-key search baseline.
A command executor reads one ALGAL EffectRequest JSON on stdin and emits one
proposal JSON on stdout. It is trusted host code; keep auth inside the wrapper.
Verify is offline and never runs a provider command. Existing runs are not overwritten.
`;

export async function main(args: string[]): Promise<void> {
  const [command, ...rest] = args;
  if (!command || command === "--help" || command === "help") { console.log(HELP); return; }
  if (command === "verify") {
    if (rest.length !== 1 || rest[0]!.startsWith("--")) throw new Error("verify requires exactly one run directory");
    console.log(JSON.stringify(await verifyStudy(rest[0]!))); return;
  }
  if (command !== "study") throw new Error(`unknown command: ${command}`);
  const options = new Map<string, string>();
  for (let i = 0; i < rest.length; i += 2) {
    const key = rest[i]!;
    const value = rest[i + 1];
    if (!["--protocol", "--out", "--executor-command"].includes(key) || !value || value.startsWith("--") || options.has(key)) throw new Error(`invalid or duplicate option: ${key}`);
    options.set(key, value);
  }
  if (!options.has("--protocol") || !options.has("--out")) throw new Error("study requires --protocol and --out");
  const commandLine = options.get("--executor-command");
  if (commandLine && Buffer.byteLength(commandLine) > 4096) throw new Error("executor command exceeds bound");
  const report = await runStudy(await readJsonFile(options.get("--protocol")!), options.get("--out")!, {
    ...(commandLine ? { executor: commandExecutor(commandLine, { timeoutMs: 120000, maxStdoutBytes: 8192 }) } : {}),
    progress: (message) => console.error(message),
  });
  console.log(JSON.stringify({ report: `${options.get("--out")}/report.md`, attempts: report.attempts.length, validExperiments: report.summaries.reduce((n, s) => n + s.validExperiments, 0), backend: report.backend }));
}
if (import.meta.main) main(Bun.argv.slice(2)).catch((error: unknown) => { console.error(error instanceof Error ? error.message : "lab failed"); process.exitCode = 1; });
