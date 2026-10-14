import { createHash } from "node:crypto";
import { mkdir, mkdtemp, open, readdir } from "node:fs/promises";
import { join } from "node:path";
import { expect, test } from "bun:test";
import { runSyntheticSize32, type Size32Ref } from "./sni-size32";
import { SNI } from "./sni-intake";

// Frozen ignored runs/sni-size32-http-ci-v4-fail-stop-protocol-20261014.md.
// V1/v2/v3 fixtures are spent. This single new case runs once on a PR Actions
// head, not again on the post-merge main push. A local skip, bind failure or red
// CI run is not a qualification pass.
const qualification = process.env.GITHUB_ACTIONS === "true" &&
  process.env.GITHUB_EVENT_NAME === "pull_request" ? test : test.skip;
const payload = Buffer.from("v4-only-data");
const ref = (task: string): Size32Ref => ({ split: "train", task, size: payload.length,
  blobOid: createHash("sha1").update(`blob ${payload.length}\0`).update(payload).digest("hex") });
const refs = [ref("task102_synthetic"), ref("task103_synthetic")];
const expectedInput = `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/tasks/${refs[0]!.task}.json`;
const disposition = "failed; no retry or corpus admission";
type Event = { kind: "stream-cancel" | "request-abort"; ms: number };
type RecordValue = Record<string, unknown>;
type Observation = {
  bun: string; boundPort: number | null; routes: string[]; hits: number;
  firstEvents: Event[]; fetchInputs: number; clientAborted: boolean; clientAbortMs: number | null;
  taskState: "not-started" | "pending" | "settled"; result: string;
  files: string[]; attempt: RecordValue | null; failure: RecordValue | null;
  serverStop: "not-started" | "settled" | "uncertain"; diagnosticError: string | null; pass: boolean;
};
const pause = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));
const safeCodes = new Set(["EACCES", "EADDRINUSE", "ECONNREFUSED", "EEXIST", "EIO",
  "EISDIR", "EMFILE", "ENFILE", "ENOENT", "ENOTDIR", "EPERM", "ETIMEDOUT"]);
const safeDescriptions = new Set(["Error:unknown", "Error:unexpected", "Error:size32-cleanup-uncertain",
  "Error:diagnostic-deadline", "Error:server-stop-deadline", ...[...safeCodes].map(code => `Error:${code}`)]);
function describe(error: unknown) {
  if (!(error instanceof Error)) return "Error:unknown";
  if (["size32-cleanup-uncertain", "diagnostic-deadline", "server-stop-deadline"].includes(error.message))
    return `Error:${error.message}`;
  const code = "code" in error ? (error as { code: unknown }).code : null;
  return typeof code === "string" && safeCodes.has(code) ? `Error:${code}` : "Error:unexpected";
}
const exactKeys = (row: RecordValue, expected: string[]) =>
  Object.keys(row).sort().join("\n") === expected.sort().join("\n");
const exactAttempt = (row: RecordValue | null) => row !== null &&
  exactKeys(row, ["task", "blobOid", "status"]) &&
  row.task === refs[0]!.task && row.blobOid === refs[0]!.blobOid && row.status === "started";
const exactFailure = (row: RecordValue | null) => row !== null &&
  exactKeys(row, ["task", "blobOid", "code", "observedBytes", "disposition"]) &&
  row.task === refs[0]!.task && row.blobOid === refs[0]!.blobOid &&
  row.code === "blob-too-large" && row.observedBytes === 1_000_001 && row.disposition === disposition;
const equalFiles = (actual: string[], wanted: string[]) => actual.join("\n") === wanted.sort().join("\n");

// Never print a parsed record, even on a failed assertion; cap the read to 4097
// bytes so an oversized or concurrently grown record fails closed.
async function readObject(directory: string, name: string): Promise<RecordValue> {
  const file = await open(join(directory, name), "r");
  try {
    const buffer = Buffer.alloc(4097);
    let length = 0;
    while (length < buffer.length) {
      const { bytesRead } = await file.read(buffer, length, buffer.length - length, length);
      if (bytesRead === 0) break;
      length += bytesRead;
    }
    if (length > 4096) throw Error("oversized-fixture-record");
    const value: unknown = JSON.parse(buffer.subarray(0, length).toString("utf8"));
    if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("invalid-fixture-record");
    return value as RecordValue;
  } finally { await file.close(); }
}

function safeLog(o: Observation) {
  const safeError = (value: string | null) => {
    if (value === null) return null;
    if (safeDescriptions.has(value)) return value;
    for (const prefix of ["bind:", "setup:", "records:", "server-stop:"])
      if (value.startsWith(prefix) && safeDescriptions.has(value.slice(prefix.length))) return value;
    return "Error:unexpected";
  };
  const boundedTime = (value: number | null) =>
    value !== null && Number.isFinite(value) && value >= 0 && value <= 100_000 ? value : null;
  const count = (value: number) => Number.isSafeInteger(value) && value >= 0 && value <= 100_000 ? value : null;
  const knownFiles = [".size32-custody", "01.attempt.json", "01.failure.json", "02.attempt.json", "02.failure.json", "report.json"];
  return {
    case: "oversize-stop-v4", bun: /^\d{1,4}\.\d{1,4}\.\d{1,4}(?:[-+][0-9A-Za-z.-]{1,32})?$/.test(o.bun) ? o.bun : "unknown",
    boundPort: o.boundPort !== null && Number.isInteger(o.boundPort) && o.boundPort > 0 && o.boundPort <= 65535 ? o.boundPort : null,
    routes: o.routes.slice(0, 3).map(route => route === "/oversize-stop-v4" ? route : "unexpected-route"),
    routesTruncated: o.routes.length > 3, hits: count(o.hits), fetchInputs: count(o.fetchInputs),
    firstEvents: o.firstEvents.slice(0, 4).map(event => ({
      kind: event.kind === "stream-cancel" || event.kind === "request-abort" ? event.kind : "unexpected-event",
      ms: boundedTime(event.ms),
    })), eventsTruncated: o.firstEvents.length > 4,
    clientAborted: o.clientAborted, clientAbortMs: boundedTime(o.clientAbortMs),
    taskState: o.taskState,
    result: o.result === "resolved" || o.result === "not-started" ? o.result : safeError(o.result),
    files: o.files.slice(0, 8).map(name => knownFiles.includes(name) ? name : "unexpected-file"),
    filesTruncated: o.files.length > 8,
    attempt: o.attempt === null ? "missing" : exactAttempt(o.attempt) ?
      { task: refs[0]!.task, blobOid: refs[0]!.blobOid, status: "started" } : "invalid",
    failure: o.failure === null ? "missing" : exactFailure(o.failure) ?
      { task: refs[0]!.task, blobOid: refs[0]!.blobOid, code: "blob-too-large",
        observedBytes: 1_000_001, disposition } : "invalid",
    serverStop: o.serverStop, diagnosticError: safeError(o.diagnosticError), pass: o.pass,
  };
}

// Pure no-HTTP log-regression; the one-use qualification remains skipped locally.
test("v4 diagnostic log rejects arbitrary codes, ledger fields, routes and paths", () => {
  const marker = "SYNTHETIC_SECRET_V4_123";
  expect(describe(Object.assign(new Error("failed"), { code: marker }))).toBe("Error:unexpected");
  const o: Observation = {
    bun: Bun.version, boundPort: null, routes: [`/private/${marker}`], hits: 0,
    firstEvents: [], fetchInputs: 0, clientAborted: false, clientAbortMs: null,
    taskState: "not-started", result: `Error:${marker}`,
    files: [`/private/${marker}`], attempt: { task: refs[0]!.task, blobOid: refs[0]!.blobOid,
      status: "started", extra: marker }, failure: { task: refs[0]!.task, blobOid: refs[0]!.blobOid,
      code: marker, observedBytes: 1_000_001, disposition },
    serverStop: "not-started", diagnosticError: `records:Error:${marker}`, pass: false,
  };
  const projected = safeLog(o);
  expect(JSON.stringify(projected)).not.toContain(marker);
  expect(projected.attempt).toBe("invalid");
  expect(projected.failure).toBe("invalid");
  expect(projected.routes).toEqual(["unexpected-route"]);
  expect(projected.files).toEqual(["unexpected-file"]);
  expect(projected.diagnosticError).toBe("Error:unexpected");
});

async function one(): Promise<Observation> {
  const o: Observation = {
    bun: Bun.version, boundPort: null, routes: [], hits: 0, firstEvents: [], fetchInputs: 0,
    clientAborted: false, clientAbortMs: null, taskState: "not-started", result: "not-started",
    files: [], attempt: null, failure: null, serverStop: "not-started", diagnosticError: null, pass: false,
  };
  let server: ReturnType<typeof Bun.serve> | undefined;
  let directory: string | undefined;
  let taskTimer: ReturnType<typeof setTimeout> | undefined;
  const firstEvents: Event[] = [];
  let beforeStop: Event[] = [];
  const start = performance.now();
  try {
    await mkdir("runs", { recursive: true });
    directory = await mkdtemp(join("runs", "sni-size32-http-ci-v4-"));
    try {
      server = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch(request) {
        const path = new URL(request.url).pathname;
        o.hits++;
        o.routes.push(path);
        if (path !== "/oversize-stop-v4") return new Response("unexpected-route", { status: 404 });
        request.signal.addEventListener("abort", () => {
          firstEvents.push({ kind: "request-abort", ms: performance.now() - start });
        }, { once: true });
        return new Response(new ReadableStream<Uint8Array>({
          start(controller) { controller.enqueue(Buffer.alloc(1_000_001, 66)); },
          cancel() { firstEvents.push({ kind: "stream-cancel", ms: performance.now() - start }); },
        }, { highWaterMark: 0 }), { headers: { "content-type": "application/octet-stream" } });
      } });
      const port = server.port;
      o.boundPort = port ?? null;
      if (typeof port !== "number" || !Number.isInteger(port) || port <= 0) throw Error("no-positive-bound-port");
    } catch (error) { o.result = `bind:${describe(error)}`; return o; }
    const base = `http://127.0.0.1:${server.port}`;
    const fetcher = async (input: string, init: RequestInit): Promise<Response> => {
      const index = o.fetchInputs++;
      if (index !== 0 || input !== expectedInput || init.redirect !== "error" || !init.signal)
        throw Error("synthetic-fetch-input-mismatch");
      const signal = init.signal as AbortSignal;
      o.clientAborted = signal.aborted;
      o.clientAbortMs = signal.aborted ? performance.now() - start : null;
      signal.addEventListener("abort", () => {
        o.clientAborted = true;
        o.clientAbortMs ??= performance.now() - start;
      }, { once: true });
      // A nominal upstream-shaped string is never passed to global fetch.
      return fetch(base + "/oversize-stop-v4", { ...init, redirect: "error", signal });
    };
    o.taskState = "pending";
    const task = runSyntheticSize32(directory, refs, fetcher, undefined, 750);
    try {
      await Promise.race([task, new Promise<never>((_, reject) => {
        taskTimer = setTimeout(() => reject(Error("diagnostic-deadline")), 3000);
      })]);
      o.result = "resolved";
      o.taskState = "settled";
    } catch (error) {
      o.result = describe(error);
      if (o.result !== "Error:diagnostic-deadline") o.taskState = "settled";
    }
    if (o.taskState === "settled") await pause(500);
  } catch (error) {
    o.diagnosticError = describe(error);
    if (directory === undefined) o.result = `setup:${o.diagnosticError}`;
  } finally {
    // Teardown itself may close a request; it must not be counted as transport evidence.
    beforeStop = [...firstEvents];
    if (taskTimer) clearTimeout(taskTimer);
    if (server) {
      let stopTimer: ReturnType<typeof setTimeout> | undefined;
      try {
        await Promise.race([Promise.resolve().then(() => server!.stop(true)), new Promise<never>((_, reject) => {
          stopTimer = setTimeout(() => reject(Error("server-stop-deadline")), 1000);
        })]);
        o.serverStop = "settled";
      } catch (error) {
        o.serverStop = "uncertain";
        o.diagnosticError = `server-stop:${describe(error)}`;
      } finally { if (stopTimer) clearTimeout(stopTimer); }
    }
    if (directory !== undefined) try {
      o.files = (await readdir(directory)).sort();
      if (o.files.includes("01.attempt.json")) o.attempt = await readObject(directory, "01.attempt.json");
      if (o.files.includes("01.failure.json")) o.failure = await readObject(directory, "01.failure.json");
    } catch (error) { o.diagnosticError = `records:${describe(error)}`; }
  }
  o.firstEvents = beforeStop;
  o.pass = o.boundPort !== null && o.boundPort > 0 && o.taskState === "settled" &&
    o.serverStop === "settled" && o.diagnosticError === null &&
    o.result === "Error:size32-cleanup-uncertain" && o.clientAborted && o.clientAbortMs !== null &&
    o.fetchInputs === 1 && o.hits === 1 && o.routes.join(",") === "/oversize-stop-v4" &&
    equalFiles(o.files, [".size32-custody", "01.attempt.json", "01.failure.json"]) &&
    exactAttempt(o.attempt) && exactFailure(o.failure);
  return o;
}

qualification("synthetic Bun HTTP v4 incomplete-body fail-stop in Actions only", async () => {
  const observation = await one();
  console.log(`SNI_SIZE32_HTTP_V4 ${JSON.stringify(safeLog(observation))}`);
  expect(observation.pass).toBe(true);
}, 8_000);
