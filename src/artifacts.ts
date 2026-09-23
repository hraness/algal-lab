import { constants } from "node:fs";
import { lstat, mkdir, open, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { canonicalize, digestCanonical, type JsonValue } from "@hraness/algal";
import { json } from "./contracts";

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
export async function sourceIdentities(): Promise<{ instrumentDigest: `sha256:${string}`; applicationDigest: `sha256:${string}` }> {
  const names = ["network.ts", "contracts.ts", "researcher.ts", "study.ts", "artifacts.ts", "oracle.ts", "qualification.ts", "xcb-executor.ts", "gateway-executor.ts", "statistics.ts", "topology.ts", "comparison.ts", "../examples/xcb-study.ts", "../examples/gateway-study.ts", "../cli.ts", "../package.json", "../bun.lock"];
  const sources = await Promise.all(names.map(async (name) => [name, await readFile(new URL(name, import.meta.url), "utf8")] as const));
  return { instrumentDigest: digest({ source: sources[0]![1], version: "network.v1" }), applicationDigest: digest(Object.fromEntries(sources)) };
}
