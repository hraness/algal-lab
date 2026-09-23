import { createHash } from "node:crypto";
import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, readdir, rename, rm, stat, symlink, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { ALGAL_REVISION } from "./contracts";
import { ArtifactStore, MAX_ARTIFACT_BYTES, RUNTIME_ROOT, assertRuntimePinned, digest, digestString, readJsonFile, readRuntimeSources, runtimeDigest, sourceIdentities } from "./artifacts";

const ownedDirectories: string[] = [];

async function temporaryDirectory(): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), "algal-lab-artifacts-test-"));
  ownedDirectories.push(directory);
  return directory;
}

afterEach(async () => {
  await Promise.all(ownedDirectories.splice(0).map((directory) => rm(directory, { recursive: true, force: true })));
});

describe("artifact file admission", () => {
  test("rejects a regular file above the byte ceiling before parsing it", async () => {
    const directory = await temporaryDirectory();
    const path = join(directory, "oversized.json");
    await writeFile(path, Buffer.alloc(MAX_ARTIFACT_BYTES + 1, 0x20));
    expect((await stat(path)).isFile()).toBe(true);
    await expect(readJsonFile(path)).rejects.toThrow(/size exceeds bounds/);
  });

  test("rejects a symbolic-link leaf without reading its target", async () => {
    const directory = await temporaryDirectory();
    const target = join(directory, "target.json");
    const link = join(directory, "linked.json");
    await writeFile(target, '{"value":"target"}\n');
    await symlink(target, link);
    await expect(readJsonFile(link)).rejects.toThrow();
    expect(await readJsonFile(target)).toEqual({ value: "target" });
  });

  test("rejects a FIFO immediately with no writer present", async () => {
    const directory = await temporaryDirectory();
    const fifo = join(directory, "no-writer.fifo");
    const created = Bun.spawnSync(["mkfifo", fifo], { stdout: "pipe", stderr: "pipe" });
    expect(created.exitCode).toBe(0);
    // No process opens the write end. Without O_NONBLOCK, opening this FIFO
    // would stall until the test timeout rather than reach file admission.
    await expect(readJsonFile(fifo)).rejects.toThrow(/file type or size/);
  }, 5_000);

  test("rejects directories as artifact files", async () => {
    const directory = await temporaryDirectory();
    const child = join(directory, "directory.json");
    await mkdir(child);
    await expect(readJsonFile(child)).rejects.toThrow(/file type or size/);
  });
});

describe("content-addressed artifact store", () => {
  test("duplicate equivalent content writes are idempotent", async () => {
    const directory = await temporaryDirectory();
    const store = new ArtifactStore(directory);
    await store.initialize();
    const first = await store.put({ z: 2, a: 1 });
    const path = join(directory, "artifacts", `${first.slice(7)}.json`);
    const before = await stat(path);
    const bytes = await readFile(path, "utf8");
    const second = await store.put({ a: 1, z: 2 });
    expect(second).toBe(first);
    expect(first).toBe(digest({ a: 1, z: 2 }));
    expect(await store.get(second)).toEqual({ a: 1, z: 2 });
    expect(await readdir(join(directory, "artifacts"))).toEqual([`${first.slice(7)}.json`]);
    expect((await stat(path)).ino).toBe(before.ino);
    expect(await readFile(path, "utf8")).toBe(bytes);
  });

  test("malformed digest references reject before any path lookup", async () => {
    const directory = await temporaryDirectory();
    // An uninitialized store ensures invalid references fail as digests,
    // rather than accidentally becoming filesystem requests.
    const store = new ArtifactStore(directory);
    for (const reference of [
      "../outside.json", `sha256:${"a".repeat(61)}../`, `sha256:${"A".repeat(64)}`,
      `sha256:${"a".repeat(63)}`, `sha256:${"a".repeat(65)}`, `${"a".repeat(64)}`,
      `sha256:${"a".repeat(64)}/../../outside`, null, 42, {},
    ]) {
      expect(() => digestString(reference)).toThrow(/invalid artifact digest/);
      await expect(store.get(reference)).rejects.toThrow(/invalid artifact digest/);
    }
  });

  test("digest tampering rejects reads and conflicting duplicate writes", async () => {
    const directory = await temporaryDirectory();
    const store = new ArtifactStore(directory);
    await store.initialize();
    const id = await store.put({ observed: 0.5 });
    const path = join(directory, "artifacts", `${id.slice(7)}.json`);
    await writeFile(path, '{"observed":0.9}\n');
    await expect(store.get(id)).rejects.toThrow(/digest mismatch/);
    await expect(store.put({ observed: 0.5 })).rejects.toThrow(/artifact conflict/);
    expect(await readFile(path, "utf8")).toBe('{"observed":0.9}\n');
  });

  test("store reads and duplicate writes reject a symlink artifact leaf", async () => {
    const directory = await temporaryDirectory();
    const store = new ArtifactStore(directory);
    await store.initialize();
    const value = { evidence: "retained" };
    const id = await store.put(value);
    const artifact = join(directory, "artifacts", `${id.slice(7)}.json`);
    const target = join(directory, "target.json");
    await writeFile(target, JSON.stringify(value));
    await unlink(artifact);
    await symlink(target, artifact);
    await expect(store.get(id)).rejects.toThrow();
    await expect(store.put(value)).rejects.toThrow();
    expect(await readJsonFile(target)).toEqual(value);
  });

  test("store reads and writes reject a replaced symlink artifacts directory", async () => {
    const directory = await temporaryDirectory();
    const store = new ArtifactStore(directory);
    await store.initialize();
    const id = await store.put({ retained: true });
    const artifacts = join(directory, "artifacts");
    const retained = join(directory, "retained-directory");
    await rename(artifacts, retained);
    await symlink(retained, artifacts, "dir");
    await expect(store.get(id)).rejects.toThrow(/artifact directory/);
    await expect(store.put({ newWrite: true })).rejects.toThrow(/artifact directory/);
    expect(await readdir(retained)).toEqual([`${id.slice(7)}.json`]);
  });
});

describe("source identity binds the installed runtime", () => {
  const files: [string, string][] = [["index.ts", "export * from './src/a';\n"], ["package.json", '{"name":"@hraness/algal"}'], ["src/a.ts", "export const a = 1;\n"]];

  test("runtime digest changes with any file content, path, or membership and is order-independent", () => {
    const baseline = runtimeDigest(files);
    expect(baseline).toMatch(/^sha256:[a-f0-9]{64}$/);
    expect(runtimeDigest([...files].reverse())).toBe(baseline);
    expect(runtimeDigest(files.map(([path, contents]) => path === "src/a.ts" ? [path, "export const a = 2;\n"] : [path, contents]))).not.toBe(baseline);
    expect(runtimeDigest(files.map(([path, contents]) => path === "src/a.ts" ? ["src/b.ts", contents] : [path, contents]))).not.toBe(baseline);
    expect(runtimeDigest([...files, ["src/extra.ts", ""]])).not.toBe(baseline);
    expect(runtimeDigest(files.slice(0, 2))).not.toBe(baseline);
    expect(() => runtimeDigest([...files, ["src/a.ts", "duplicate"]])).toThrow(/repeated runtime source path/);
    expect(() => runtimeDigest([["", "unnamed"]])).toThrow(/runtime source path/);
    expect(() => runtimeDigest([])).toThrow(/no runtime sources/);
  });

  test("lockfile and package manifest must pin the runtime to ALGAL_REVISION", async () => {
    const lock = await readFile(new URL("../bun.lock", import.meta.url), "utf8");
    const manifest = await readFile(new URL("../package.json", import.meta.url), "utf8");
    expect(() => assertRuntimePinned(lock, manifest)).not.toThrow();
    expect(lock).toContain(`github:hraness/algal#${ALGAL_REVISION}`);
    const other = "0123456789abcdef0123456789abcdef01234567";
    expect(() => assertRuntimePinned(lock, manifest, other)).toThrow(/not ALGAL_REVISION/);
    expect(() => assertRuntimePinned(lock.replaceAll(ALGAL_REVISION, other), manifest)).toThrow(/pinned to github:hraness\/algal#0123456789abcdef0123456789abcdef01234567, not ALGAL_REVISION/);
    // bun.lock abbreviates the resolved entry; an abbreviated pin must still be a prefix of the revision.
    const abbreviated = `algal#${ALGAL_REVISION.slice(0, 7)}"`;
    expect(lock).toContain(abbreviated);
    expect(() => assertRuntimePinned(lock.replace(abbreviated, `algal#${other.slice(0, 7)}"`), manifest)).toThrow(/pinned to github:hraness\/algal#0123456, not/);
    expect(() => assertRuntimePinned(lock, manifest.replace(ALGAL_REVISION, other))).toThrow(/not ALGAL_REVISION/);
    expect(() => assertRuntimePinned(lock.replaceAll(/github:hraness\/algal#[0-9a-f]+/g, "npm:@hraness/algal@0.1.0"), manifest)).toThrow(/must both pin/);
    expect(() => assertRuntimePinned("{}", "{}")).toThrow(/must both pin/);
    expect(() => assertRuntimePinned(lock, "{}")).toThrow(/must both pin/);
    expect(() => assertRuntimePinned(lock, manifest, ALGAL_REVISION.slice(0, 7))).toThrow(/full commit sha/);
  });

  test("runtime sources are the manifest, entrypoint, and every TypeScript file under src, sorted", async () => {
    const directory = await temporaryDirectory();
    await mkdir(join(directory, "src", "nested"), { recursive: true });
    await writeFile(join(directory, "package.json"), '{"name":"fixture"}');
    await writeFile(join(directory, "index.ts"), "export {};\n");
    await writeFile(join(directory, "src", "z.ts"), "z");
    await writeFile(join(directory, "src", "a.ts"), "a");
    await writeFile(join(directory, "src", "nested", "n.ts"), "n");
    await writeFile(join(directory, "src", "algal_expr.wasm"), "binary");
    await writeFile(join(directory, "cli.ts"), "cli");
    const sources = await readRuntimeSources(pathToFileURL(`${directory}/`));
    // Binaries are bound by their hex digest, not their bytes.
    expect(sources).toEqual([["index.ts", "export {};\n"], ["package.json", '{"name":"fixture"}'], ["src/a.ts", "a"], ["src/algal_expr.wasm", createHash("sha256").update("binary").digest("hex")], ["src/nested/n.ts", "n"], ["src/z.ts", "z"]]);
    await writeFile(join(directory, "src", "a.ts"), "changed");
    expect(runtimeDigest(await readRuntimeSources(pathToFileURL(`${directory}/`)))).not.toBe(runtimeDigest(sources));
    await rm(join(directory, "index.ts"));
    await expect(readRuntimeSources(pathToFileURL(`${directory}/`))).rejects.toThrow();
  });

  test("the installed runtime is resolved from the module graph and folded into the application digest", async () => {
    expect(RUNTIME_ROOT.pathname.endsWith("/node_modules/@hraness/algal/")).toBe(true);
    const sources = await readRuntimeSources();
    const paths = sources.map(([path]) => path);
    expect(paths.slice(0, 2)).toEqual(["index.ts", "package.json"]);
    expect(paths.slice(2).every((path) => path.startsWith("src/") && (path.endsWith(".ts") || path.endsWith(".wasm")))).toBe(true);
    expect(paths).toContain("src/algal_expr.wasm");
    expect(paths).toContain("src/digest.ts");
    expect(paths).toEqual([...paths].sort());
    expect(JSON.parse(sources[1]![1]).name).toBe("@hraness/algal");
    const first = await sourceIdentities();
    expect(await sourceIdentities()).toEqual(first);
    expect(Object.keys(first).sort()).toEqual(["applicationDigest", "instrumentDigest"]);
  });
});
