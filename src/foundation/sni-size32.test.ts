import { createHash } from "node:crypto";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { expect, test } from "bun:test";
import { extractSize32, freezeSize32, runSize32, runSyntheticSize32, SIZE32, type Size32Ref } from "./sni-size32";
import { SNI } from "./sni-intake";

const privateBlob = Buffer.from(JSON.stringify({ Source: ["Synthetic"], Categories: [], "Instance License": ["CC BY 4.0"],
  Instances: [{ input: "PRIVATE TRAIN BODY", output: ["PRIVATE TRAIN LABEL"] }] }));
function ref(task: string, bytes = privateBlob): Size32Ref {
  return { split: "train", task, size: bytes.length,
    blobOid: createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex") };
}
const first = ref("task109_smsspamcollection_spamsmsdetection");
const second = ref("task1135_xcsr_en_commonsense_mc_classification");
// No auto-generated content-length: exercise the streamed, observed-byte path.
const body = (bytes: Uint8Array) => new Response(new ReadableStream<Uint8Array>({
  start(controller) { controller.enqueue(bytes); controller.close(); },
}));
const single = async () => body(privateBlob);
async function temporary<T>(fn: (directory: string) => Promise<T>): Promise<T> {
  const directory = await mkdtemp(join(tmpdir(), "algal-size32-synthetic-"));
  try { return await fn(directory); } finally { await rm(directory, { recursive: true, force: true }); }
}
async function file(directory: string, name: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(join(directory, name), "utf8")) as Record<string, unknown>;
}

test("unpinned preflight bytes and alternate empty output fail before any request", async () => {
  expect(() => freezeSize32(Buffer.from("{}"), Buffer.from(""), Buffer.from(""))).toThrow("preflight");
  await temporary(async directory => {
    let requested = 0;
    await expect(runSize32(directory, async () => { requested++; return body(privateBlob); })).rejects.toThrow("private-path-required");
    expect(requested).toBe(0);
  });
});

test("copied three-file preflight cannot acquire custody or fetch", async () => {
  // The actual campaign preflight is ignored by Git. Keep CI's path rejection
  // regression independent of private run files; local authentic-copy evidence
  // remains in docs/sni-size32-path-guard-receipt.md.
  const names = ["all-task-sizes.tsv", "plan.json", "selection.tsv"] as const;
  await temporary(async originalDirectory => {
    const originals = names.map(name => Buffer.from(`synthetic ${name}\n`));
    for (const [index, name] of names.entries()) await writeFile(join(originalDirectory, name), originals[index]!);
    await temporary(async directory => {
      for (const [index, name] of names.entries()) await writeFile(join(directory, name), await readFile(join(originalDirectory, name)));
      for (const [index, name] of names.entries()) expect((await readFile(join(directory, name))).equals(originals[index]!)).toBe(true);
      let fetched = 0;
      await expect(runSize32(directory, async () => {
        fetched++;
        return new Response(null, { status: 200 });
      })).rejects.toThrow("size32-private-path-required");
      expect(fetched).toBe(0);
      expect((await readdir(directory)).sort()).toEqual([...names]);
    });
    expect((await readdir(originalDirectory)).sort()).toEqual([...names]);
    for (const [index, name] of names.entries()) expect((await readFile(join(originalDirectory, name))).equals(originals[index]!)).toBe(true);
  });
});

test("size and Git blob OID are checked before UTF-8/JSON; sidecar remains closed", () => {
  expect(extractSize32(first, privateBlob)).toEqual({ blobOid: first.blobOid, task: first.task,
    Source: ["Synthetic"], Categories: [], "Instance License": ["CC BY 4.0"] });
  expect(JSON.stringify(extractSize32(first, privateBlob))).not.toContain("PRIVATE");
  expect(() => extractSize32({ ...first, size: first.size + 1 }, privateBlob)).toThrow("size-mismatch");
  const invalid = Buffer.from("not JSON");
  expect(() => extractSize32({ ...ref(first.task, invalid), blobOid: "0".repeat(40) }, invalid)).toThrow("blob-OID-mismatch");
  expect(() => extractSize32(ref(first.task, invalid), invalid)).toThrow("invalid-JSON");
  const utf8 = Buffer.from([0xff]);
  expect(() => extractSize32(ref(first.task, utf8), utf8)).toThrow("invalid-utf8");
  const badMetadata = Buffer.from(JSON.stringify({ Source: [], Categories: [], "Instance License": [] }));
  expect(() => extractSize32(ref(first.task, badMetadata), badMetadata)).toThrow("invalid-metadata");
});

test("fake transport emits only the closed sidecar and exact byte ledger in pinned order", async () => {
  await temporary(async directory => {
    const urls: string[] = [];
    const report = await runSyntheticSize32(directory, [first, second], async (url, init) => {
      urls.push(url);
      expect(init.redirect).toBe("error");
      expect(init.signal).toBeDefined();
      return body(privateBlob);
    });
    expect(urls).toEqual([first, second].map(row =>
      `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/tasks/${row.task}.json`));
    expect(report).toMatchObject({ statuses: { extracted: 2, failed: 0 }, observedResponseBytes: 2 * privateBlob.length, paidUsd: 0 });
    const stored = await file(directory, "01.sidecar.json");
    expect(stored).toEqual({ blobOid: first.blobOid, task: first.task, Source: ["Synthetic"], Categories: [],
      "Instance License": ["CC BY 4.0"], observedBytes: privateBlob.length });
    expect(JSON.stringify(stored)).not.toContain("PRIVATE");
    expect((await file(directory, "01.attempt.json")).status).toBe("started");
    expect((await readdir(directory)).sort()).toEqual([".size32-custody", "01.attempt.json", "01.sidecar.json", "02.attempt.json", "02.sidecar.json", "report.json"]);
  });
});

test("attempt-write failure prevents request; partial terminal sidecar write stops with no fallback or retry", async () => {
  await temporary(async directory => {
    let requests = 0;
    const writer: typeof writeFile = async (path, data, options) => {
      if (String(path).endsWith("01.attempt.json")) throw Error("injected partial pre-request write");
      await writeFile(path, data, options);
    };
    await expect(runSyntheticSize32(directory, [first, second], async () => { requests++; return single(); }, writer)).rejects.toThrow("unresolved-write");
    expect(requests).toBe(0);
  });
  await temporary(async directory => {
    let requests = 0;
    const writer: typeof writeFile = async (path, data, options) => {
      await writeFile(path, data, options);
      if (String(path).endsWith("01.sidecar.json")) throw Error("terminal write result uncertain");
    };
    await expect(runSyntheticSize32(directory, [first, second], async () => { requests++; return single(); }, writer)).rejects.toThrow("unresolved-write");
    expect(requests).toBe(1);
    expect((await readdir(directory)).sort()).toEqual([".size32-custody", "01.attempt.json", "01.sidecar.json"]);
    expect((await file(directory, "01.sidecar.json")).observedBytes).toBe(privateBlob.length);
  });
});

test("pre-existing files and uncertain failure writes stop without retry", async () => {
  await temporary(async directory => {
    await writeFile(join(directory, "01.failure.json"), "not our file");
    let requested = 0;
    await expect(runSyntheticSize32(directory, [first], async () => { requested++; return body(privateBlob); })).rejects.toThrow("directory-not-exclusive");
    expect(requested).toBe(0);
  });
  await temporary(async directory => {
    const writer: typeof writeFile = async (path, data, options) => {
      if (String(path).endsWith("01.failure.json")) throw Error("failure write uncertain");
      await writeFile(path, data, options);
    };
    await expect(runSyntheticSize32(directory, [first, second], async () => { throw Error("PRIVATE upstream body"); }, writer)).rejects.toThrow("unresolved-write");
    expect((await readdir(directory)).sort()).toEqual([".size32-custody", "01.attempt.json"]);
  });
});

test("errored stream cancellation is uncertain: keep safe bytes and stop without report", async () => {
  await temporary(async directory => {
    let requests = 0;
    const partial = new ReadableStream<Uint8Array>({
      pull(controller) {
        if (requests === 1) { requests++; controller.enqueue(Buffer.from("abc")); }
        else controller.error(new DOMException("PRIVATE upstream error", "TimeoutError"));
      },
    }, { highWaterMark: 0 });
    await expect(runSyntheticSize32(directory, [first, second], async () => { requests = 1; return new Response(partial); })).rejects.toThrow("cleanup-uncertain");
    expect(requests).toBe(2);
    expect((await file(directory, "01.failure.json")).observedBytes).toBe(3);
    expect((await file(directory, "01.failure.json")).code).toBe("cleanup-error");
    expect((await readdir(directory)).includes("02.attempt.json")).toBe(false);
    expect((await readdir(directory)).includes("report.json")).toBe(false);
    expect(JSON.stringify(await file(directory, "01.failure.json"))).not.toContain("PRIVATE");
  });
});

test("missing body, redirect/transport failure and no upstream error text are safe failures", async () => {
  await temporary(async directory => {
    let requests = 0;
    const report = await runSyntheticSize32(directory, [first, second], async () => {
      if (++requests === 1) return new Response(null, { status: 200 });
      throw Error("PRIVATE redirect target");
    });
    expect((await file(directory, "01.failure.json")).code).toBe("missing-body");
    expect((await file(directory, "02.failure.json")).code).toBe("fetch-or-redirect-error");
    expect(report.observedResponseBytes).toBe(0);
    expect(JSON.stringify(await file(directory, "02.failure.json"))).not.toContain("PRIVATE");
  });
});

test("content-length is only a bound; exactly-at-body-cap passes stream bound, over-cap chunk counted", async () => {
  await temporary(async directory => {
    const requests: string[] = [];
    const atLimit = Buffer.alloc(SIZE32.maxBlobBytes);
    const overLimit = Buffer.alloc(SIZE32.maxBlobBytes + 1);
    const report = await runSyntheticSize32(directory, [first, second, ref("task1146_country_capital")], async (url) => {
      requests.push(url);
      if (requests.length === 1) return new Response(body(privateBlob).body, { headers: { "content-length": String(SIZE32.maxBlobBytes + 1) } });
      if (requests.length === 2) return body(atLimit);
      return body(overLimit);
    });
    expect((await file(directory, "01.failure.json")).observedBytes).toBe(0);
    expect((await file(directory, "01.failure.json")).code).toBe("blob-too-large");
    expect((await file(directory, "02.failure.json")).code).toBe("size-mismatch");
    expect((await file(directory, "02.failure.json")).observedBytes).toBe(SIZE32.maxBlobBytes);
    expect((await file(directory, "03.failure.json")).observedBytes).toBe(SIZE32.maxBlobBytes + 1);
    expect(report.observedResponseBytes).toBe(2 * SIZE32.maxBlobBytes + 1);
  });
});

test("whole-chunk aggregate crossing is recorded, not silently truncated or retried", async () => {
  await temporary(async directory => {
    const refs = Array.from({ length: 32 }, (_, i) => ref(`task${String(i + 100).padStart(3, "0")}_synthetic`));
    const tooLarge = Buffer.alloc(SIZE32.maxBlobBytes + 1);
    const exact = Buffer.alloc(SIZE32.maxBlobBytes);
    let requests = 0;
    const report = await runSyntheticSize32(directory, refs, async () => body(++requests < 32 ? tooLarge : exact));
    expect(requests).toBe(32);
    expect((await file(directory, "32.failure.json")).code).toBe("aggregate-limit");
    expect((await file(directory, "32.failure.json")).observedBytes).toBe(SIZE32.maxBlobBytes);
    expect(report.observedResponseBytes).toBe(32 * SIZE32.maxBlobBytes + 31);
    expect(report.statuses).toEqual({ extracted: 0, failed: 32 });
  });
});
