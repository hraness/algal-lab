import { createHash } from "node:crypto";
import { constants } from "node:fs";
import { lstat, mkdir, open, readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { canonicalize, digestCanonical, type JsonValue } from "@hraness/algal";
import { ALGAL_REVISION, json } from "./contracts";

export const MAX_ARTIFACT_BYTES = 4 * 1024 * 1024;
export function digest(value: unknown): `sha256:${string}` { return digestCanonical(json(value)); }
export function digestString(value: unknown): `sha256:${string}` {
  if (typeof value !== "string" || !/^sha256:[a-f0-9]{64}$/.test(value)) throw new Error("invalid artifact digest");
  return value as `sha256:${string}`;
}
export async function readJsonFile(path: string): Promise<JsonValue> {
  const handle = await open(path, constants.O_RDONLY | constants.O_NONBLOCK | constants.O_NOFOLLOW);
  try {
    const stat = await handle.stat();
    if (!stat.isFile() || stat.size > MAX_ARTIFACT_BYTES) throw new Error("artifact file type or size exceeds bounds");
    const buffer = Buffer.alloc(MAX_ARTIFACT_BYTES + 1);
    let length = 0;
    while (length < buffer.length) {
      const read = await handle.read(buffer, length, buffer.length - length, null);
      if (read.bytesRead === 0) break;
      length += read.bytesRead;
    }
    if (length > MAX_ARTIFACT_BYTES) throw new Error("artifact grew beyond byte bound");
    return json(JSON.parse(buffer.subarray(0, length).toString("utf8")));
  } finally { await handle.close(); }
}
export class ArtifactStore {
  constructor(readonly directory: string) {}
  async initialize(): Promise<void> { await mkdir(join(this.directory, "artifacts")); }
  async put(value: unknown): Promise<`sha256:${string}`> {
    const metadata = await lstat(join(this.directory, "artifacts"));
    if (!metadata.isDirectory() || metadata.isSymbolicLink()) throw new Error("invalid artifact directory");
    const data = json(value);
    const id = digest(data);
    const contents = canonicalize(data) + "\n";
    if (Buffer.byteLength(contents) > MAX_ARTIFACT_BYTES) throw new Error("artifact exceeds byte bound");
    const path = join(this.directory, "artifacts", id.slice(7) + ".json");
    try { await writeFile(path, contents, { flag: "wx", mode: 0o600 }); }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
      if (digest(await readJsonFile(path)) !== id) throw new Error("content-addressed artifact conflict");
    }
    return id;
  }
  async get(ref: unknown): Promise<JsonValue> {
    const id = digestString(ref);
    const metadata = await lstat(join(this.directory, "artifacts"));
    if (!metadata.isDirectory() || metadata.isSymbolicLink()) throw new Error("invalid artifact directory");
    const value = await readJsonFile(join(this.directory, "artifacts", id.slice(7) + ".json"));
    if (digest(value) !== id) throw new Error(`artifact digest mismatch: ${id}`);
    return value;
  }
}
export const RUNTIME_PACKAGE = "@hraness/algal";
/** The installed runtime that actually executes: the directory of the module
 * `@hraness/algal` resolves to, not a path assumed from the repository layout. */
export const RUNTIME_ROOT = new URL("./", import.meta.resolve(RUNTIME_PACKAGE));
const RUNTIME_SPEC = /github:hraness\/algal#([0-9a-f]{7,40})/g;

/** Digest of runtime source files as (path, content digest) pairs. Pure so the
 * binding can be tested with synthetic inputs instead of a mutated install. */
export function runtimeDigest(files: Iterable<readonly [path: string, contents: string]>): `sha256:${string}` {
  const manifest: Record<string, `sha256:${string}`> = {};
  for (const [path, contents] of files) {
    if (path.length === 0 || Object.hasOwn(manifest, path)) throw new Error(`invalid or repeated runtime source path: ${path}`);
    manifest[path] = `sha256:${createHash("sha256").update(contents).digest("hex")}`;
  }
  if (Object.keys(manifest).length === 0) throw new Error("no runtime sources to bind");
  return digest(manifest);
}
/** Every `github:hraness/algal#<sha>` in the lockfile and the package manifest
 * must name ALGAL_REVISION (bun.lock abbreviates the resolved entry to a prefix). */
export function assertRuntimePinned(lock: string, manifest: string, revision: string = ALGAL_REVISION): void {
  if (!/^[0-9a-f]{40}$/.test(revision)) throw new Error("ALGAL_REVISION must be a full commit sha");
  const pins = [lock, manifest].map((source) => [...source.matchAll(RUNTIME_SPEC)].map((match) => match[1]!));
  if (pins.some((found) => found.length === 0)) throw new Error(`bun.lock and package.json must both pin ${RUNTIME_PACKAGE} to github:hraness/algal#${revision}`);
  for (const pin of pins.flat()) {
    if (!revision.startsWith(pin)) throw new Error(`${RUNTIME_PACKAGE} is pinned to github:hraness/algal#${pin}, not ALGAL_REVISION ${revision}; realign contracts.ts, package.json, and bun.lock`);
  }
}
/** package.json, index.ts, and every TypeScript file under src/ of the installed runtime, sorted by path. */
export async function readRuntimeSources(root: URL = RUNTIME_ROOT): Promise<[string, string][]> {
  // The expression engine ships as a binary; it executes too, so it is bound by its hex digest.
  const sources = (await readdir(new URL("src/", root), { recursive: true })).filter((path) => path.endsWith(".ts") || path.endsWith(".wasm")).map((path) => `src/${path}`);
  const paths = ["package.json", "index.ts", ...sources].sort();
  return Promise.all(paths.map(async (path) => [path, path.endsWith(".wasm") ? createHash("sha256").update(await readFile(new URL(path, root))).digest("hex") : await readFile(new URL(path, root), "utf8")] as [string, string]));
}
/** Source identities recorded in every report. applicationDigest binds the
 * laboratory sources and the installed ALGAL runtime; the lockfile must pin that
 * runtime to ALGAL_REVISION so the recorded revision names the hashed code. */
export async function sourceIdentities(): Promise<{ instrumentDigest: `sha256:${string}`; applicationDigest: `sha256:${string}` }> {
  const names = ["network.ts", "contracts.ts", "researcher.ts", "study.ts", "artifacts.ts", "oracle.ts", "qualification.ts", "xcb-executor.ts", "gateway-executor.ts", "statistics.ts", "topology.ts", "comparison.ts", "../examples/xcb-study.ts", "../examples/gateway-study.ts", "../cli.ts", "../package.json", "../bun.lock"];
  const [sources, runtime] = await Promise.all([
    Promise.all(names.map(async (name) => [name, await readFile(new URL(name, import.meta.url), "utf8")] as const)),
    readRuntimeSources(),
  ]);
  const source = (name: string) => sources.find((entry) => entry[0] === name)![1];
  assertRuntimePinned(source("../bun.lock"), source("../package.json"));
  return { instrumentDigest: digest({ source: sources[0]![1], version: "network.v1" }),
    applicationDigest: digest({ ...Object.fromEntries(sources), [`node_modules/${RUNTIME_PACKAGE}`]: runtimeDigest(runtime) }) };
}
