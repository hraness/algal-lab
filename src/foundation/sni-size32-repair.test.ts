import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, readdir, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { expect, test } from "bun:test";
import { runSyntheticSize32, SIZE32, type Size32Ref } from "./sni-size32";

function ref(task: string): Size32Ref {
  const bytes = Buffer.from("synthetic-only");
  return { split: "train", task, size: bytes.length,
    blobOid: createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex") };
}
const refs = [ref("task100_synthetic"), ref("task101_synthetic")];
const body = (bytes: Uint8Array) => new Response(new ReadableStream<Uint8Array>({
  start(controller) { controller.enqueue(bytes); controller.close(); },
}));
async function temporary(fn: (directory: string) => Promise<void>) {
  const directory = await mkdtemp(join(tmpdir(), "algal-size32-repair-"));
  try { await fn(directory); } finally { await rm(directory, { recursive: true, force: true }); }
}
async function failure(directory: string) {
  return JSON.parse(await readFile(join(directory, "01.failure.json"), "utf8")) as Record<string, unknown>;
}

test("exclusive custody is acquired before any attempt, remains after completion, and cannot be renewed", async () => {
  await temporary(async directory => {
    await mkdir(join(directory, ".size32-custody"));
    let calls = 0;
    await expect(runSyntheticSize32(directory, refs, async () => { calls++; return body(Buffer.from("x")); })).rejects.toThrow("directory-not-exclusive");
    expect(calls).toBe(0);
  });
  await temporary(async directory => {
    let calls = 0;
    await runSyntheticSize32(directory, refs.slice(0, 1), async () => { calls++; return body(Buffer.from("x")); });
    await expect(runSyntheticSize32(directory, refs.slice(0, 1), async () => { calls++; return body(Buffer.from("x")); })).rejects.toThrow("directory-not-exclusive");
    expect(calls).toBe(1);
    expect((await readdir(directory)).includes(".size32-custody")).toBe(true);
  });
});

test("a trailing slash cannot hide a symlink to an otherwise empty output directory", async () => {
  await temporary(async root => {
    const target = join(root, "target"), link = join(root, "link");
    await mkdir(target);
    await symlink(target, link, "dir");
    let calls = 0;
    await expect(runSyntheticSize32(`${link}/`, refs.slice(0, 1), async () => {
      calls++;
      return new Response(null, { status: 200 });
    })).rejects.toThrow("directory-not-exclusive");
    expect(calls).toBe(0);
    expect(await readdir(target)).toEqual([]);
  });
});

test("uncooperative fetch is aborted at deadline and never requests another row", async () => {
  await temporary(async directory => {
    let calls = 0, signal: AbortSignal | undefined;
    const start = performance.now();
    await expect(runSyntheticSize32(directory, refs, async (_url, init) => {
      calls++;
      signal = init.signal as AbortSignal;
      return new Promise<Response>(() => {});
    }, writeFile, 60)).rejects.toThrow("cleanup-uncertain");
    expect(performance.now() - start).toBeLessThan(2000);
    expect(signal?.aborted).toBe(true);
    expect(calls).toBe(1);
    expect(await failure(directory)).toMatchObject({ code: "timeout", observedBytes: 0 });
    expect((await readdir(directory)).includes("02.attempt.json")).toBe(false);
    expect((await readdir(directory)).includes("report.json")).toBe(false);
  });
});

test("hung body read records partial bytes, times out, and stops after cancellation uncertainty", async () => {
  await temporary(async directory => {
    let calls = 0;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) { controller.enqueue(Buffer.from("abc")); },
      cancel() { return new Promise<void>(() => {}); },
    }, { highWaterMark: 0 });
    await expect(runSyntheticSize32(directory, refs, async () => { calls++; return new Response(stream); }, writeFile, 60)).rejects.toThrow("cleanup-uncertain");
    expect(calls).toBe(1);
    expect(await failure(directory)).toMatchObject({ code: "cleanup-error", observedBytes: 3 });
    expect((await readdir(directory)).includes("report.json")).toBe(false);
  });
});

test("cancellation rejection overrides prior safe failure and stops the run", async () => {
  await temporary(async directory => {
    let calls = 0;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) { controller.enqueue(Buffer.alloc(SIZE32.maxBlobBytes + 1)); },
      cancel() { throw Error("PRIVATE cancellation body"); },
    }, { highWaterMark: 0 });
    await expect(runSyntheticSize32(directory, refs, async () => { calls++; return new Response(stream); })).rejects.toThrow("cleanup-uncertain");
    expect(calls).toBe(1);
    expect(await failure(directory)).toMatchObject({ code: "cleanup-error", observedBytes: SIZE32.maxBlobBytes + 1 });
    expect(JSON.stringify(await failure(directory))).not.toContain("PRIVATE");
  });
});

test("aggregate exhaustion before a remaining row writes no next attempt or report", async () => {
  await temporary(async directory => {
    let calls = 0;
    await expect(runSyntheticSize32(directory, refs, async () => {
      calls++;
      return body(Buffer.alloc(SIZE32.maxAggregateBytes));
    })).rejects.toThrow("aggregate-exhausted-unresolved");
    expect(calls).toBe(1);
    expect(await failure(directory)).toMatchObject({ code: "blob-too-large", observedBytes: SIZE32.maxAggregateBytes });
    expect((await readdir(directory)).includes("02.attempt.json")).toBe(false);
    expect((await readdir(directory)).includes("report.json")).toBe(false);
  });
});

test("report refuses a changed terminal record instead of trusting in-memory counters", async () => {
  await temporary(async directory => {
    const writer: typeof writeFile = async (path, data, options) => {
      await writeFile(path, data, options);
      if (String(path).endsWith("02.failure.json")) await writeFile(join(directory, "01.failure.json"), "{}", { mode: 0o600 });
    };
    await expect(runSyntheticSize32(directory, refs, async () => body(Buffer.from("x")), writer)).rejects.toThrow("ledger-changed-unresolved");
    expect((await readdir(directory)).includes("report.json")).toBe(false);
  });
});

test("all parser-admitted metadata fits the bounded terminal report reader", async () => {
  await temporary(async directory => {
    const large = Buffer.from(JSON.stringify({ Source: Array(12).fill("S".repeat(256)),
      Categories: Array(12).fill("C".repeat(256)), "Instance License": ["CC BY 4.0"],
      Instances: [{ input: "PRIVATE EXAMPLE" }] }));
    const selected: Size32Ref = { ...ref("task102_synthetic"), size: large.length,
      blobOid: createHash("sha1").update(`blob ${large.length}\0`).update(large).digest("hex") };
    const report = await runSyntheticSize32(directory, [selected], async () => body(large));
    const sidecar = await readFile(join(directory, "01.sidecar.json"), "utf8");
    expect(Buffer.byteLength(sidecar)).toBeGreaterThan(4096);
    expect(sidecar).not.toContain("PRIVATE EXAMPLE");
    expect(report.statuses).toEqual({ extracted: 1, failed: 0 });
    expect(report.observedResponseBytes).toBe(large.length);
  });
});
