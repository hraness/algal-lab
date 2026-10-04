#!/usr/bin/env bun
import { prepareClinc, verifyDataset } from "../src/foundation/datasets";
import { runBaseline, verifyBaseline } from "../src/foundation/retrieval";
import { checkProofs, setupProofs, toolReadiness } from "../src/foundation/tools";

const HELP = `Research datasets and local toolchains

bun run foundation doctor
bun run foundation fetch clinc150 --out <new-directory>
bun run foundation import clinc150 --source <pinned-source-checkout> --out <new-directory>
bun run foundation verify-dataset <dataset-directory>
bun run foundation baseline <dataset-directory> --out <new-directory>
bun run foundation verify-baseline <dataset-directory> <baseline-directory>
bun run foundation setup-proofs --out <new-directory> [--jobs <1..4>]
bun run foundation check-proofs <toolchain-directory>
python3 -m research.foundation_allocation --out <new-directory>
python3 -m research.foundation_allocation --verify <benchmark-directory>

fetch explicitly downloads three hash-pinned public files. import is offline.
Baselines read training/validation only, make no model calls, and do not score test.
setup-proofs downloads and builds the CI-pinned sources with local controls;
it changes no global tool installation. Run builds through your host scheduler.
Every output directory must be new. No provider or private dataset is activated.
`;
function options(args: string[], keys: string[]): Map<string, string> {
  const result = new Map<string, string>();
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i]!, value = args[i + 1];
    if (!keys.includes(key) || !value || value.startsWith("--") || result.has(key)) throw new Error(`invalid or duplicate option: ${key}`);
    result.set(key, value);
  }
  return result;
}
function required(opts: Map<string, string>, key: string): string { const value = opts.get(key); if (!value) throw new Error(`required: ${key}`); return value; }
export async function main(args: string[]): Promise<unknown> {
  const [command, target, ...rest] = args;
  if (!command || command === "--help" || command === "help") return HELP;
  if (command === "doctor") { if (args.length !== 1) throw new Error("unexpected arguments"); return toolReadiness(); }
  if (command === "setup-proofs") { const opts = options(args.slice(1), ["--out", "--jobs"]); return setupProofs(required(opts, "--out"), Number(opts.get("--jobs") ?? 2)); }
  if (!target || target.startsWith("--")) throw new Error("a dataset or directory is required");
  if (command === "fetch" || command === "import") {
    if (target !== "clinc150") throw new Error("unknown dataset");
    const opts = options(rest, command === "fetch" ? ["--out"] : ["--source", "--out"]);
    return prepareClinc(required(opts, "--out"), command === "import" ? { source: required(opts, "--source") } : {});
  }
  if (command === "baseline") { const opts = options(rest, ["--out"]); return runBaseline(target, required(opts, "--out")); }
  if (command === "verify-baseline") { if (rest.length !== 1 || rest[0]!.startsWith("--")) throw new Error("requires dataset and baseline directories"); return verifyBaseline(target, rest[0]!); }
  if (rest.length) throw new Error("unexpected arguments");
  if (command === "verify-dataset") return verifyDataset(target);
  if (command === "check-proofs") return checkProofs(target);
  throw new Error(`unknown command: ${command}`);
}
if (import.meta.main) main(Bun.argv.slice(2)).then(result => console.log(typeof result === "string" ? result : JSON.stringify(result, null, 2))).catch((error: unknown) => { console.error(error instanceof Error ? error.message : "foundation command failed"); process.exitCode = 1; });
