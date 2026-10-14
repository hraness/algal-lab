import { createHash } from "node:crypto";
import { mkdtemp, readFile, readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { expect, test } from "bun:test";
import { runSyntheticSize32, type Size32Ref } from "./sni-size32";

// Frozen v4 no-network control: a fulfilled reader.cancel() is not a server-close receipt.
const payload = Buffer.from("v4-only-data");
const ref = (task: string): Size32Ref => ({ split: "train", task, size: payload.length,
  blobOid: createHash("sha1").update(`blob ${payload.length}\0`).update(payload).digest("hex") });
const refs = [ref("task102_synthetic"), ref("task103_synthetic")];

test("fulfilled cancellation of an incomplete oversized body fails before a second attempt", async () => {
  const directory = await mkdtemp(join(tmpdir(), "algal-size32-v4-injected-"));
  try {
    let fetches = 0, cancels = 0, signal: AbortSignal | undefined;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) { controller.enqueue(Buffer.alloc(1_000_001, 66)); },
      cancel() { cancels++; },
    }, { highWaterMark: 0 });
    await expect(runSyntheticSize32(directory, refs, async (_url, init) => {
      fetches++;
      signal = init.signal as AbortSignal;
      if (fetches !== 1) throw Error("unexpected second injected fetch");
      return new Response(stream);
    }, undefined, 750)).rejects.toThrow("size32-cleanup-uncertain");
    expect(fetches).toBe(1);
    expect(cancels).toBe(1);
    expect(signal?.aborted).toBe(true);
    expect((await readdir(directory)).sort()).toEqual([".size32-custody", "01.attempt.json", "01.failure.json"]);
    const attempt: unknown = JSON.parse(await readFile(join(directory, "01.attempt.json"), "utf8"));
    expect(attempt).toEqual({ task: refs[0]!.task, blobOid: refs[0]!.blobOid, status: "started" });
    const failure: unknown = JSON.parse(await readFile(join(directory, "01.failure.json"), "utf8"));
    expect(failure).toEqual({ task: refs[0]!.task, blobOid: refs[0]!.blobOid,
      code: "blob-too-large", observedBytes: 1_000_001, disposition: "failed; no retry or corpus admission" });
  } finally { await rm(directory, { recursive: true, force: true }); }
});
