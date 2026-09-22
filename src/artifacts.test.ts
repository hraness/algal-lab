import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, readdir, rename, rm, stat, symlink, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { ArtifactStore, MAX_ARTIFACT_BYTES, digest, digestString, readJsonFile } from "./artifacts";

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
