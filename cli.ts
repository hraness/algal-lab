#!/usr/bin/env bun
import { commandExecutor } from "@hraness/algal";
import { readJsonFile } from "./src/artifacts";
import { runStudy, verifyStudy } from "./src/study";
import { runQualification, verifyQualification } from "./src/qualification";
import { runComparison, verifyComparison } from "./src/comparison";

const HELP = `algal-lab — bounded research on ALGAL

bun run lab study --protocol <file.json> --out <new-directory>
  [--policy adaptive|random | --executor-command <operator-owned-command>]
bun run lab verify <run-directory>
bun run lab qualify --plan <plan.json> --out <new-directory>
bun run lab verify-qualification <qualification-directory>
bun run lab compare --plan <plan.json> --out <new-directory> [--executor-command <cmd>]
bun run lab verify-comparison <comparison-directory>

Without --executor-command, study uses a deterministic no-key search baseline.
A command executor reads one ALGAL EffectRequest JSON on stdin and emits one
proposal JSON on stdout. It is trusted host code; keep auth inside the wrapper.
Verify is offline and never runs a provider command. Existing runs are not overwritten.
`;

export async function main(args: string[]): Promise<void> {
  const [command, ...rest] = args;
  if (!command || command === "--help" || command === "help") { console.log(HELP); return; }
  if (command === "verify" || command === "verify-qualification" || command === "verify-comparison") {
    if (rest.length !== 1 || rest[0]!.startsWith("--")) throw new Error("verify requires exactly one run directory");
    const verifier = command === "verify" ? verifyStudy : command === "verify-qualification" ? verifyQualification : verifyComparison;
    console.log(JSON.stringify(await verifier(rest[0]!))); return;
  }
  if (command !== "study" && command !== "qualify" && command !== "compare") throw new Error(`unknown command: ${command}`);
  const allowed = command === "study" ? ["--protocol", "--out", "--executor-command", "--policy"] : command === "compare" ? ["--plan", "--out", "--executor-command"] : ["--plan", "--out"];
  const options = new Map<string, string>();
  for (let i = 0; i < rest.length; i += 2) {
    const key = rest[i]!;
    const value = rest[i + 1];
    if (!allowed.includes(key) || !value || value.startsWith("--") || options.has(key)) throw new Error(`invalid or duplicate option: ${key}`);
    options.set(key, value);
  }
  if (command === "qualify") {
    if (!options.has("--plan") || !options.has("--out")) throw new Error("qualify requires --plan and --out");
    const report = await runQualification(await readJsonFile(options.get("--plan")!), options.get("--out")!, (message) => console.error(message));
    console.log(JSON.stringify({ report: `${options.get("--out")}/report.md`, studies: report.studies.length, attempts: report.rows.reduce((sum, r) => sum + r.attempts, 0), controls: report.controls }));
    if (Object.values(report.controls).some((passed) => !passed)) throw new Error("qualification control failed; inspect retained report");
    return;
  }
  const commandLine = options.get("--executor-command");
  if (commandLine && Buffer.byteLength(commandLine) > 4096) throw new Error("executor command exceeds bound");
  if (command === "compare") {
    if (!options.has("--plan") || !options.has("--out")) throw new Error("compare requires --plan and --out");
    const report = await runComparison(await readJsonFile(options.get("--plan")!), options.get("--out")!, {
      ...(commandLine ? { executor: commandExecutor(commandLine, { timeoutMs: 120000, maxStdoutBytes: 8192 }) } : {}),
      progress: (message) => console.error(message),
    });
    console.log(JSON.stringify({ report: `${options.get("--out")}/report.md`, arms: report.arms, studies: report.studies.length, rows: report.rows.length, controls: report.controls }));
    if (Object.values(report.controls).some((passed) => !passed)) throw new Error("comparison control failed; inspect retained report");
    return;
  }
  if (!options.has("--protocol") || !options.has("--out")) throw new Error("study requires --protocol and --out");
  const policy = options.get("--policy");
  if (policy !== undefined && policy !== "adaptive" && policy !== "random") throw new Error("policy must be adaptive or random");
  if (commandLine && policy !== undefined) throw new Error("choose --policy or --executor-command");
  const report = await runStudy(await readJsonFile(options.get("--protocol")!), options.get("--out")!, {
    ...(commandLine ? { executor: commandExecutor(commandLine, { timeoutMs: 120000, maxStdoutBytes: 8192 }) } : {}),
    ...(policy ? { policy } : {}),
    progress: (message) => console.error(message),
  });
  console.log(JSON.stringify({ report: `${options.get("--out")}/report.md`, attempts: report.attempts.length, validExperiments: report.summaries.reduce((n, s) => n + s.validExperiments, 0), backend: report.backend }));
}
/** Translate filesystem failures at the CLI boundary only; library behavior is unchanged. */
function describeFailure(args: string[], error: unknown): string {
  if (!(error instanceof Error)) return "lab failed";
  const [command, ...rest] = args;
  const code = (error as NodeJS.ErrnoException).code;
  if (code === "EEXIST" && (command === "study" || command === "qualify" || command === "compare")) {
    const out = rest[rest.indexOf("--out") + 1];
    if (rest.includes("--out") && out) return `${out} already exists; choose a new --out (existing runs are never overwritten)`;
  }
  if (code === "ENOENT" && (command === "verify" || command === "verify-qualification" || command === "verify-comparison") && rest[0]) {
    return `${rest[0]} is not a run directory`;
  }
  return error.message;
}
if (import.meta.main) main(Bun.argv.slice(2)).catch((error: unknown) => { console.error(describeFailure(Bun.argv.slice(2), error)); process.exitCode = 1; });
