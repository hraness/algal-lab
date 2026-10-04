#!/usr/bin/env bun
import { abandon, confirm, context, init, propose, seal, status, step } from "../src/discovery/loop";
import { load, readJson, unlock } from "../src/discovery/store";
import { doctor, loadAgenda } from "../src/discovery/agenda";
import { verify } from "../src/discovery/verify";

const HELP = `Resumable discovery experiments

bun run discovery doctor
bun run discovery agenda [track-id]
bun run discovery init --config <file.json> --out <new-directory>
bun run discovery step <run-directory> [--live]
bun run discovery run <run-directory> --steps <1..256> [--live]
bun run discovery propose <run-directory> --proposal <file.json> --parent <attempt-id>
bun run discovery context <run-directory>
bun run discovery status <run-directory>
bun run discovery verify <run-directory>
bun run discovery seal <run-directory>
bun run discovery confirm <run-directory>
bun run discovery abandon <run-directory> --request <request-id>
bun run discovery unlock <run-directory>

The default control runs locally without keys. xAI/Gemini require a configured
spending budget and --live. Completed or uncertain request IDs are never retried.
Seal freezes selection permanently before final holdout evaluation.
`;
function options(args: string[], allowed: string[]): Map<string, string> {
  const result = new Map<string, string>();
  for (let i = 0; i < args.length; i++) {
    const key = args[i]!;
    if (!allowed.includes(key) || result.has(key)) throw new Error(`unknown or duplicate option: ${key}`);
    if (key === "--live") { result.set(key, "true"); continue; }
    const value = args[++i];
    if (!value || value.startsWith("--")) throw new Error(`missing value: ${key}`);
    result.set(key, value);
  }
  return result;
}
function required(opts: Map<string, string>, key: string): string {
  const value = opts.get(key); if (!value) throw new Error(`required: ${key}`); return value;
}
export async function main(args: string[]): Promise<unknown> {
  const [command, directory, ...rest] = args;
  if (!command || ["help", "--help"].includes(command)) return HELP;
  if (command === "doctor") {
    if (directory || rest.length) throw new Error("unexpected arguments");
    return doctor();
  }
  if (command === "agenda") {
    if (rest.length) throw new Error("unexpected arguments");
    const agenda = await loadAgenda();
    if (!directory) return agenda;
    const track = agenda.tracks.find(track => track.id === directory);
    if (!track) throw new Error(`unknown research track: ${directory}`);
    return track;
  }
  if (command === "init") {
    const opts = options(args.slice(1), ["--config", "--out"]);
    const out = required(opts, "--out");
    await init(await readJson(required(opts, "--config"), 20000), out);
    return status(out);
  }
  if (!directory || directory.startsWith("--")) throw new Error("a run directory is required");
  if (["context", "status", "verify", "seal", "confirm", "unlock"].includes(command)) {
    if (rest.length) throw new Error("unexpected arguments");
    if (command === "verify") return verify(directory);
    if (command === "context") { const { config, state } = await load(directory); return context(config, state); }
    if (command === "seal") await seal(directory);
    if (command === "confirm") await confirm(directory);
    if (command === "unlock") { await unlock(directory); return { unlocked: true }; }
    return status(directory);
  }
  if (command === "propose") {
    const opts = options(rest, ["--proposal", "--parent"]);
    return propose(directory, await readJson(required(opts, "--proposal"), 20000), required(opts, "--parent"));
  }
  if (command === "abandon") {
    const opts = options(rest, ["--request"]); await abandon(directory, required(opts, "--request")); return status(directory);
  }
  if (command === "step" || command === "run") {
    const opts = options(rest, command === "run" ? ["--steps", "--live"] : ["--live"]);
    const count = command === "step" ? 1 : Number(required(opts, "--steps"));
    if (!Number.isInteger(count) || count < 1 || count > 256) throw new Error("steps must be 1..256");
    for (let i = 0; i < count; i++) {
      try { await step(directory, { live: opts.has("--live") }); }
      catch (error) {
        if (command === "run" && error instanceof Error && /budget exhausted$/.test(error.message)) return { stop: error.message, result: await status(directory) };
        throw error;
      }
    }
    return status(directory);
  }
  throw new Error(`unknown command: ${command}`);
}
if (import.meta.main) main(Bun.argv.slice(2)).then(result => console.log(typeof result === "string" ? result : JSON.stringify(result, null, 2))).catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : "discovery command failed"); process.exitCode = 1;
});
