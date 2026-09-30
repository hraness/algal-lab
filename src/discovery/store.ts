import { mkdir, open, readFile, rename, unlink, writeFile } from "node:fs/promises";
import { hostname } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { hash, object, parseConfig, parseState, type Config, type State } from "./contracts";

const SOURCE_FILES = ["contracts.ts", "evaluator.ts", "providers.ts", "store.ts", "loop.ts"];
export async function sourceHash(): Promise<string> {
  const files = await Promise.all(SOURCE_FILES.map(async name => [name, await readFile(new URL(name, import.meta.url), "utf8")]));
  files.push(["network.ts", await readFile(new URL("../network.ts", import.meta.url), "utf8")]);
  files.push(["contracts.ts (shared)", await readFile(new URL("../contracts.ts", import.meta.url), "utf8")]);
  files.push(["bun.lock", await readFile(new URL("../../bun.lock", import.meta.url), "utf8")]);
  return hash({ files, bun: Bun.version });
}
export async function readJson(path: string, maxBytes = 64_000_000): Promise<unknown> {
  const file = await open(path, "r");
  try {
    if ((await file.stat()).size > maxBytes) throw new Error("JSON file exceeds size limit");
    return JSON.parse(await file.readFile("utf8")) as unknown;
  } finally { await file.close(); }
}
export async function save(out: string, state: State): Promise<void> {
  const envelope = { digest: hash(state), state };
  const bytes = `${JSON.stringify(envelope, null, 2)}\n`;
  const temporary = join(out, `state-${randomUUID()}.tmp`);
  const file = await open(temporary, "wx", 0o600);
  try { await file.writeFile(bytes); await file.sync(); } finally { await file.close(); }
  // Record transitions without quadratically copying prompts and responses.
  // The atomic state preserves every request, response, prediction, and failure.
  await mkdir(join(out, "history"), { recursive: true, mode: 0o700 });
  const transition = { digest: envelope.digest, phase: state.phase, incumbent: state.incumbent, attempts: state.attempts.map(a => ({ id: a.id, status: a.status })), requests: state.requests.map(r => ({ id: r.id, status: r.status })) };
  try { await writeFile(join(out, "history", `${envelope.digest}.json`), `${JSON.stringify(transition)}\n`, { flag: "wx", mode: 0o600 }); }
  catch (error) { if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error; }
  await rename(temporary, join(out, "state.json"));
}
export async function load(out: string): Promise<{ config: Config; state: State }> {
  const config = parseConfig(await readJson(join(out, "config.json"), 20000));
  const envelope = object(await readJson(join(out, "state.json")), ["digest", "state"], "state file");
  if (envelope.digest !== hash(envelope.state)) throw new Error("state file digest mismatch");
  const state = parseState(envelope.state, config);
  if (state.sourceHash !== await sourceHash()) throw new Error("evaluator, loop source, or Bun version changed; preserve this run and start a new one");
  return { config, state };
}
export async function withRun<T>(out: string, action: (config: Config, state: State) => Promise<T>): Promise<T> {
  const path = join(out, ".lock");
  let lock;
  try { lock = await open(path, "wx", 0o600); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === "EEXIST") throw new Error("run is locked; after a crash use unlock on the same host (never remove a live owner's lock)");
    throw error;
  }
  try {
    await lock.writeFile(JSON.stringify({ pid: process.pid, host: hostname(), token: randomUUID() }));
    await lock.sync();
    const { config, state } = await load(out);
    return await action(config, state);
  } finally { await lock.close(); await unlink(path); }
}
export async function unlock(out: string): Promise<void> {
  const path = join(out, ".lock");
  const lock = object(await readJson(path, 1024), ["pid", "host", "token"], "lock");
  if (lock.host !== hostname() || typeof lock.pid !== "number" || !Number.isInteger(lock.pid) || lock.pid <= 0) throw new Error("cannot release a lock from another host or with an invalid owner");
  try { process.kill(lock.pid, 0); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ESRCH") { await unlink(path); return; }
    throw new Error("cannot establish that the lock owner is absent");
  }
  throw new Error("run owner is still present; lock preserved");
}
