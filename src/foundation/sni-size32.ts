import { createHash } from "node:crypto";
import { lstat, mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { encode, sha256 } from "./datasets";
import { parseTaskMetadata, SNI, type TaskMetadata } from "./sni-intake";

// No live CLI: independent exact-byte review of this offline executor is still pending.
// The existing private intake is the only authorized live output, not a new run.
export const SIZE32 = {
  planSha256: "4e47e5875c5c89b8b876e8fe2b358c6243057497608bf136a316ecd95d3d3e42",
  selectionSha256: "6ea37fc2bff821ed5cbd5f10352c98b451442f29ee5dbf6bc2029c340c069388",
  sizesSha256: "951646cf44809e2b27216ead0c91a94f8d0deb42666a99e39ea09c4ef0b37531",
  indexSha256: "2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38",
  previousSelectionSha256: "97cb7f38b55869de58e4667f28458d2c1d15799211bfdb9e25d795b9444f0728",
  testNamesSha256: "5f65a29afa7b0c4bbb3b6c4c2b885e03d3c72adb182e67d06f9d91cb87d1d1c0",
  count: 32, maxBlobBytes: 1_000_000, maxAggregateBytes: 32_000_000, timeoutMs: 30_000,
} as const;
export type Size32Ref = Readonly<{ split: "train"; task: string; blobOid: string; size: number }>;
type Fetcher = (input: string, init: RequestInit) => Promise<Response>;
type Writer = typeof writeFile;
type FailureCode = "blob-too-large" | "aggregate-limit" | "size-mismatch" | "blob-OID-mismatch" |
  "invalid-utf8" | "invalid-JSON" | "invalid-metadata" | "http-status" | "missing-body" |
  "timeout" | "fetch-or-redirect-error" | "cleanup-error";
const failureCodes: readonly FailureCode[] = ["blob-too-large", "aggregate-limit", "size-mismatch", "blob-OID-mismatch",
  "invalid-utf8", "invalid-JSON", "invalid-metadata", "http-status", "missing-body", "timeout", "fetch-or-redirect-error", "cleanup-error"];
class IntakeFailure extends Error {
  constructor(readonly code: FailureCode) { super(code); }
}
const fail = (code: FailureCode): never => { throw new IntakeFailure(code); };
const rowPattern = /^(train|test|excluded)\t(task[0-9]{3,4}_[a-zA-Z0-9_.-]+)\t([0-9a-f]{40})\t(0|[1-9][0-9]*)$/;
const taskPattern = /^task[0-9]{3,4}_[a-zA-Z0-9_.-]+$/;
const byteOrder = (a: string, b: string) => Buffer.compare(Buffer.from(a), Buffer.from(b));
const custodyName = ".size32-custody";
// Module-root-relative, not caller-configurable: copying the preflight cannot renew the live intake.
const privateDirectory = resolve(fileURLToPath(new URL("../../runs/sni-size32-20261013-01/", import.meta.url)));
const disposition = "failed; no retry or corpus admission";

/** Only metadata enters; authenticate the entire selection and its size manifest first. */
export function freezeSize32(planBytes: Uint8Array, selectionBytes: Uint8Array, sizesBytes: Uint8Array): readonly Size32Ref[] {
  if (sha256(planBytes) !== SIZE32.planSha256 || sha256(selectionBytes) !== SIZE32.selectionSha256 || sha256(sizesBytes) !== SIZE32.sizesSha256) throw Error("size32-preflight-mismatch");
  // Exact plan bytes pin every field, including the $0/zero-attempt ledger and source identity.
  const plan: unknown = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(planBytes));
  if (!plan || typeof plan !== "object" || Array.isArray(plan) || (plan as Record<string, unknown>).commit !== SNI.commit) throw Error("size32-plan-mismatch");
  const text = new TextDecoder("utf-8", { fatal: true });
  const lines = (bytes: Uint8Array): string[] => {
    const rows = text.decode(bytes).split("\n");
    if (rows.pop() !== "" || !rows.length) throw Error("size32-invalid-tsv");
    return rows;
  };
  const counts = { train: 0, test: 0, excluded: 0 };
  const seen = new Set<string>(), manifest: { split: keyof typeof counts; task: string; blobOid: string; size: number }[] = [];
  for (const line of lines(sizesBytes)) {
    const match = rowPattern.exec(line);
    if (!match || seen.has(match[2]!)) throw Error("size32-invalid-manifest");
    const split = match[1]! as keyof typeof counts, task = match[2]!, blobOid = match[3]!, size = Number(match[4]);
    if (!Number.isSafeInteger(size) || size < 0) throw Error("size32-invalid-size");
    seen.add(task); counts[split]++; manifest.push({ split, task, blobOid, size });
  }
  if (Object.keys(counts).some(split => counts[split as keyof typeof counts] !== SNI.splits[split as keyof typeof counts].count)) throw Error("size32-split-count");
  const index = manifest.map(row => `${row.split}\t${row.task}\t${row.blobOid}\n`).join("");
  if (sha256(index) !== SIZE32.indexSha256) throw Error("size32-index-mismatch");
  const train = manifest.filter((row): row is Size32Ref => row.split === "train").sort((a, b) => byteOrder(a.task, b.task));
  const previous = train.slice(0, 64);
  if (sha256(previous.map(row => `${row.split}\t${row.task}\t${row.blobOid}\n`).join("")) !== SIZE32.previousSelectionSha256) throw Error("size32-previous-mismatch");
  const testNames = manifest.filter(row => row.split === "test").map(row => row.task).sort(byteOrder);
  if (sha256(testNames.join("\n") + "\n") !== SIZE32.testNamesSha256) throw Error("size32-test-names-mismatch");
  const previousIds = new Set(previous.map(row => row.task));
  const available = train.filter(row => !previousIds.has(row.task) && row.size <= SIZE32.maxBlobBytes);
  const selected = available.slice(0, SIZE32.count);
  const canonical = selected.map(row => `${row.split}\t${row.task}\t${row.blobOid}\t${row.size}\n`).join("");
  if (available.length !== 351 || selected.length !== SIZE32.count || selected.reduce((n, row) => n + row.size, 0) !== 4_016_222 ||
    !Buffer.from(selectionBytes).equals(Buffer.from(canonical))) throw Error("size32-selection-mismatch");
  // Neither test nor excluded blob bodies are constructed or requested.
  return selected;
}

/** Pure, synthetic-testable boundary: size and Git blob identity precede decoding. */
export function extractSize32(ref: Size32Ref, bytes: Uint8Array): TaskMetadata & { blobOid: string } {
  if (bytes.length > SIZE32.maxBlobBytes) fail("blob-too-large");
  if (bytes.length !== ref.size) fail("size-mismatch");
  if (createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex") !== ref.blobOid) fail("blob-OID-mismatch");
  let decoded: string;
  try { decoded = new TextDecoder("utf-8", { fatal: true }).decode(bytes); } catch { return fail("invalid-utf8"); }
  let value: unknown;
  try { value = JSON.parse(decoded) as unknown; } catch { return fail("invalid-JSON"); }
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("invalid-metadata");
  const row = value as Record<string, unknown>;
  try {
    const metadata = parseTaskMetadata({ task: ref.task, Source: row.Source, Categories: row.Categories, "Instance License": row["Instance License"] });
    return { blobOid: ref.blobOid, ...metadata };
  } catch { return fail("invalid-metadata"); }
}
function code(error: unknown): FailureCode {
  if (error instanceof IntakeFailure) return error.code;
  if (error instanceof Error && (error.name === "TimeoutError" || error.name === "AbortError")) return "timeout";
  return "fetch-or-redirect-error"; // No upstream exception, URL, body or local path is serialized.
}

type Outcome = { observedBytes: number; metadata?: TaskMetadata & { blobOid: string }; code?: FailureCode; uncertain: boolean };
async function fetchOne(ref: Size32Ref, used: number, fetcher: Fetcher, timeoutMs: number): Promise<Outcome> {
  let observedBytes = 0, reader: ReadableStreamDefaultReader<Uint8Array> | undefined, response: Response | undefined;
  let result: { metadata?: TaskMetadata & { blobOid: string }; code?: FailureCode } = {};
  let uncertain = false, completed = false;
  const controller = new AbortController();
  const deadline = performance.now() + timeoutMs;
  // Every await shares the same monotonic deadline; losing promises have rejection handlers.
  const within = <T>(promise: Promise<T>): Promise<T> => new Promise((resolve, reject) => {
    const remaining = deadline - performance.now();
    if (remaining <= 0) {
      controller.abort(); uncertain = true;
      void promise.catch(() => {});
      reject(new IntakeFailure("timeout"));
      return;
    }
    const timer = setTimeout(() => {
      uncertain = true;
      controller.abort();
      reject(new IntakeFailure("timeout"));
    }, remaining);
    void promise.then(value => {
      clearTimeout(timer);
      if (performance.now() >= deadline) { uncertain = true; controller.abort(); reject(new IntakeFailure("timeout")); }
      else resolve(value);
    }, error => {
      clearTimeout(timer);
      if (performance.now() >= deadline) { uncertain = true; controller.abort(); reject(new IntakeFailure("timeout")); }
      else reject(error);
    });
  });
  try {
    const url = `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/tasks/${ref.task}.json`;
    const fetched = await within(Promise.resolve().then(() => {
      if (controller.signal.aborted) fail("timeout");
      return fetcher(url, { redirect: "error", headers: { "User-Agent": "algal-sni-size32" }, signal: controller.signal });
    }));
    response = fetched;
    if (fetched.status !== 200) fail("http-status");
    const body = fetched.body;
    if (body === null) throw new IntakeFailure("missing-body");
    const header = fetched.headers.get("content-length");
    if (header !== null && /^[0-9]+$/.test(header)) {
      const length = Number(header);
      if (length > SIZE32.maxBlobBytes) fail("blob-too-large");
      if (length > SIZE32.maxAggregateBytes - used) fail("aggregate-limit");
    }
    reader = body.getReader();
    const chunks: Uint8Array[] = [];
    let accepted = 0;
    for (;;) {
      const next = await within(reader.read());
      if (next.done) { completed = true; break; }
      observedBytes += next.value.byteLength; // Count whole emitted chunk even if discarded.
      if (accepted + next.value.byteLength > SIZE32.maxBlobBytes) fail("blob-too-large");
      if (used + observedBytes > SIZE32.maxAggregateBytes) fail("aggregate-limit");
      accepted += next.value.byteLength;
      chunks.push(next.value);
    }
    if (performance.now() > deadline) fail("timeout");
    result.metadata = extractSize32(ref, Buffer.concat(chunks, accepted));
  } catch (error) { result = { code: code(error) }; }
  // A fulfilled cancel is not evidence that an incomplete remote body has stopped.
  const incompleteBody = !completed && (reader !== undefined || response?.body != null);
  try {
    if (reader) {
      if (!completed) await within(reader.cancel());
      reader.releaseLock();
    } else if (response?.body) await within(response.body.cancel());
  } catch { uncertain = true; result = { code: "cleanup-error" }; }
  if (incompleteBody) uncertain = true;
  if (uncertain) { controller.abort(); result = { code: result.code ?? "timeout" }; }
  return { ...result, observedBytes, uncertain };
}

async function attemptAll(directory: string, selected: readonly Size32Ref[], preflight: readonly string[], selectionSha256: string,
  fetcher: Fetcher, writer: Writer, synthetic: boolean, timeoutMs: number) {
  // Strip trailing separators before lstat: lstat("symlink/") follows the link on Bun/Darwin.
  directory = resolve(directory);
  const lockPath = join(directory, custodyName);
  const inspect = async (expected: readonly string[], custody?: { dev: number; ino: number }) => {
    if (!(await lstat(directory)).isDirectory()) throw Error("size32-directory-not-exclusive");
    const entries = await readdir(directory, { withFileTypes: true });
    if (entries.length !== expected.length + (custody ? 1 : 0) || entries.some(entry =>
      entry.name === custodyName ? !custody || !entry.isDirectory() : !expected.includes(entry.name) || !entry.isFile())) throw Error("size32-directory-not-exclusive");
    if (custody) {
      const lock = await lstat(lockPath);
      if (!lock.isDirectory() || lock.dev !== custody.dev || lock.ino !== custody.ino || (await readdir(lockPath)).length) throw Error("size32-custody-lost-unresolved");
    }
  };
  await inspect(preflight);
  // Atomic acquisition; never release or renew a consumed run, including synthetic tests.
  try { await mkdir(lockPath, { mode: 0o700 }); } catch { throw Error("size32-custody-unavailable"); }
  const lock = await lstat(lockPath);
  const custody = { dev: lock.dev, ino: lock.ino };
  const written = new Map<string, string>();
  const check = () => inspect([...preflight, ...written.keys()], custody);
  await check();
  const exclusive = async (name: string, value: unknown) => {
    await check();
    const bytes = encode(value);
    try {
      await writer(join(directory, name), bytes, { flag: "wx", mode: 0o600 });
      if (!(await readFile(join(directory, name))).equals(Buffer.from(bytes))) throw Error("partial write");
    } catch { throw Error("size32-unresolved-write"); }
    written.set(name, bytes);
    await check();
  };
  let used = 0;
  for (const [index, ref] of selected.entries()) {
    await check();
    if (used >= SIZE32.maxAggregateBytes) throw Error("size32-aggregate-exhausted-unresolved");
    const id = String(index + 1).padStart(2, "0");
    await exclusive(`${id}.attempt.json`, { task: ref.task, blobOid: ref.blobOid, status: "started" });
    const outcome = await fetchOne(ref, used, fetcher, timeoutMs);
    used += outcome.observedBytes;
    await check();
    if (outcome.metadata) {
      await exclusive(`${id}.sidecar.json`, { ...outcome.metadata, observedBytes: outcome.observedBytes });
    } else {
      await exclusive(`${id}.failure.json`, { task: ref.task, blobOid: ref.blobOid, code: outcome.code!, observedBytes: outcome.observedBytes,
        disposition });
    }
    // Even a terminal safe failure cannot justify another request after uncertain cleanup.
    if (outcome.uncertain) throw Error("size32-cleanup-uncertain");
  }
  await check();
  // Re-read bounded, exact terminal records. Mutable counters are not a report source.
  const record = async (name: string): Promise<Record<string, unknown>> => {
    const path = join(directory, name);
    const info = await lstat(path);
    // 36 parser-admitted metadata strings can each hold 256 bytes; JSON escaping
    // can expand a control byte sixfold, so 4 KiB would reject valid sidecars.
    if (!info.isFile() || info.size > 65_536 || info.size < 2) throw Error("size32-ledger-changed-unresolved");
    const bytes = await readFile(path);
    if (!bytes.equals(Buffer.from(written.get(name) ?? ""))) throw Error("size32-ledger-changed-unresolved");
    const value: unknown = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
    if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("size32-ledger-changed-unresolved");
    return value as Record<string, unknown>;
  };
  const keys = (row: Record<string, unknown>, expected: readonly string[]) =>
    Object.keys(row).length === expected.length && expected.every(key => Object.hasOwn(row, key));
  let extracted = 0, failed = 0, observedResponseBytes = 0;
  try {
    for (const [index, ref] of selected.entries()) {
      const id = String(index + 1).padStart(2, "0");
      const attempt = await record(`${id}.attempt.json`);
      if (!keys(attempt, ["task", "blobOid", "status"]) || attempt.task !== ref.task || attempt.blobOid !== ref.blobOid || attempt.status !== "started") throw Error("invalid attempt");
      const sidecar = `${id}.sidecar.json`, failure = `${id}.failure.json`;
      const name = written.has(sidecar) ? sidecar : failure;
      if (!written.has(name) || (await readdir(directory)).includes(name === sidecar ? failure : sidecar)) throw Error("missing or duplicate terminal");
      const row = await record(name);
      if (row.task !== ref.task || row.blobOid !== ref.blobOid || !Number.isSafeInteger(row.observedBytes) || (row.observedBytes as number) < 0) throw Error("invalid terminal");
      observedResponseBytes += row.observedBytes as number;
      if (name === sidecar) {
        if (!keys(row, ["blobOid", "task", "Source", "Categories", "Instance License", "observedBytes"])) throw Error("invalid sidecar");
        parseTaskMetadata({ task: row.task, Source: row.Source, Categories: row.Categories, "Instance License": row["Instance License"] });
        extracted++;
      } else {
        if (!keys(row, ["task", "blobOid", "code", "observedBytes", "disposition"]) ||
          !failureCodes.includes(row.code as FailureCode) || row.disposition !== disposition) throw Error("invalid failure");
        failed++;
      }
    }
  } catch { throw Error("size32-ledger-changed-unresolved"); }
  if (observedResponseBytes !== used || extracted + failed !== selected.length) throw Error("size32-ledger-changed-unresolved");
  await check();
  const report = { contract: synthetic ? "algal.sni.size32.synthetic.v1" : "algal.sni.size32.attempts.v1",
    commit: SNI.commit, selectionSha256, statuses: { extracted, failed }, observedResponseBytes, paidUsd: 0,
    disposition: "metadata only; instance rights, families, and holdout require independent review" };
  await exclusive("report.json", report);
  return report;
}

/** Offline test seam only: injected transport; no production CLI or default network fetch. */
export async function runSize32(directory: string, fetcher: Fetcher, writer: Writer = writeFile) {
  // Fail before trusting copied preflight bytes or creating a second custody record.
  if (resolve(directory) !== privateDirectory) throw Error("size32-private-path-required");
  // All subsequent accesses use the anchored path; lstat must not follow a trailing slash.
  directory = privateDirectory;
  if (!(await lstat(directory)).isDirectory()) throw Error("size32-directory-not-exclusive");
  const preflight = ["all-task-sizes.tsv", "plan.json", "selection.tsv"];
  const entries = await readdir(directory, { withFileTypes: true });
  if (entries.length !== preflight.length || entries.some(entry => !entry.isFile() || !preflight.includes(entry.name))) throw Error("size32-directory-not-exclusive");
  const selected = freezeSize32(await readFile(join(directory, "plan.json")), await readFile(join(directory, "selection.tsv")), await readFile(join(directory, "all-task-sizes.tsv")));
  return attemptAll(directory, selected, preflight, SIZE32.selectionSha256, fetcher, writer, false, SIZE32.timeoutMs);
}

/** Synthetic transport/write fault tests share the exact loop; never use as live entry. */
export async function runSyntheticSize32(directory: string, selected: readonly Size32Ref[], fetcher: Fetcher, writer: Writer = writeFile,
  testTimeoutMs: number = SIZE32.timeoutMs) {
  if (!selected.length || selected.length > SIZE32.count || new Set(selected.map(ref => ref.task)).size !== selected.length ||
    selected.some(ref => ref.split !== "train" || !taskPattern.test(ref.task) || !/^[0-9a-f]{40}$/.test(ref.blobOid) ||
      !Number.isSafeInteger(ref.size) || ref.size < 0 || ref.size > SIZE32.maxBlobBytes) ||
    !Number.isSafeInteger(testTimeoutMs) || testTimeoutMs < 1 || testTimeoutMs > SIZE32.timeoutMs) throw Error("invalid-synthetic-selection");
  return attemptAll(directory, selected, [], sha256(encode(selected)), fetcher, writer, true, testTimeoutMs);
}
