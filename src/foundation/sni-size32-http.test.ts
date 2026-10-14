import { createHash } from "node:crypto";
import { mkdir, mkdtemp, open, readdir } from "node:fs/promises";
import { join } from "node:path";
import { expect, test } from "bun:test";
import { runSyntheticSize32, type Size32Ref } from "./sni-size32";
import { SNI } from "./sni-intake";

// Protocol and pre-execution addenda: ignored runs/sni-size32-http-ci-v3-*.md.
// This is synthetic-only. Local runners that cannot bind must not claim qualification;
// GitHub Actions must execute every case and fail, rather than skip, on bind errors.
const qualification = process.env.GITHUB_ACTIONS === "true" ? test : test.skip;
const payload = Buffer.from("synthetic-only");
const ref = (task: string): Size32Ref => ({
  split: "train", task, size: payload.length,
  blobOid: createHash("sha1").update(`blob ${payload.length}\0`).update(payload).digest("hex"),
});
const refs = [ref("task100_synthetic"), ref("task101_synthetic")];
const expectedInputs = refs.map(row =>
  `https://raw.githubusercontent.com/allenai/natural-instructions/${SNI.commit}/tasks/${row.task}.json`);
const syntheticSelectionSha256 = createHash("sha256").update(`${JSON.stringify(refs, null, 2)}\n`).digest("hex");
const failedDisposition = "failed; no retry or corpus admission";
const reportDisposition = "metadata only; instance rights, families, and holdout require independent review";
type Case = "cancel" | "body" | "headers";
type Event = { kind: "stream-cancel" | "request-abort"; ms: number };
type RecordValue = Record<string, unknown>;
type Observation = {
  case: Case; bun: string; boundPort: number | null; routes: string[]; hits: number;
  firstEvents: Event[]; closeConfirmedBeforeSecond: boolean; closeWaitMs: number | null;
  clientAborted: boolean[]; clientAbortMs: (number | null)[]; fetchInputs: number; lateHeaderResponses: number;
  taskState: "not-started" | "pending" | "settled"; result: string;
  files: string[]; firstAttempt: RecordValue | null; secondAttempt: RecordValue | null;
  first: RecordValue | null; second: RecordValue | null; report: RecordValue | null;
  serverStop: "not-started" | "settled" | "uncertain"; diagnosticError: string | null; pass: boolean;
};
const pause = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));
// An exception's `code` is untrusted too: an uppercase token might be a credential.
// Print only known OS codes and internally constructed sentinels, never arbitrary text.
const safeCodes = new Set(["EACCES", "EADDRINUSE", "ECONNREFUSED", "EEXIST", "EIO",
  "EISDIR", "EMFILE", "ENFILE", "ENOENT", "ENOTDIR", "EPERM", "ETIMEDOUT"]);
const safeDescriptions = new Set(["Error:unknown", "Error:unexpected", "Error:size32-cleanup-uncertain",
  "Error:diagnostic-deadline", "Error:server-stop-deadline", ...[...safeCodes].map(code => `Error:${code}`)]);
const describe = (error: unknown) => {
  if (!(error instanceof Error)) return "Error:unknown";
  if (["size32-cleanup-uncertain", "diagnostic-deadline", "server-stop-deadline"].includes(error.message))
    return `Error:${error.message}`;
  const code = "code" in error ? (error as { code: unknown }).code : null;
  return typeof code === "string" && safeCodes.has(code) ? `Error:${code}` : "Error:unexpected";
};
const equalFiles = (actual: string[], wanted: string[]) => actual.join("\n") === wanted.sort().join("\n");
const exactKeys = (row: RecordValue, expected: string[]) =>
  Object.keys(row).sort().join("\n") === expected.sort().join("\n");
const exactAttempt = (row: RecordValue | null, selected: Size32Ref) => row !== null &&
  exactKeys(row, ["task", "blobOid", "status"]) && row.task === selected.task &&
  row.blobOid === selected.blobOid && row.status === "started";
const exactFailure = (row: RecordValue | null, selected: Size32Ref, codes: readonly string[], bytes: number) =>
  row !== null && exactKeys(row, ["task", "blobOid", "code", "observedBytes", "disposition"]) &&
  row.task === selected.task && row.blobOid === selected.blobOid &&
  typeof row.code === "string" && codes.includes(row.code) && row.observedBytes === bytes &&
  row.disposition === failedDisposition;
const exactReport = (row: RecordValue | null) => {
  if (row === null || !exactKeys(row, ["contract", "commit", "selectionSha256", "statuses",
    "observedResponseBytes", "paidUsd", "disposition"])) return false;
  const statuses = row.statuses;
  return statuses !== null && typeof statuses === "object" && !Array.isArray(statuses) &&
    exactKeys(statuses as RecordValue, ["extracted", "failed"]) &&
    (statuses as RecordValue).extracted === 0 && (statuses as RecordValue).failed === 2 &&
    row.contract === "algal.sni.size32.synthetic.v1" && row.commit === SNI.commit &&
    row.selectionSha256 === syntheticSelectionSha256 &&
    row.observedResponseBytes === 1_000_015 && row.paidUsd === 0 &&
    row.disposition === reportDisposition;
};

// A ledger value is never copied into a log, including when an exact-field check fails.
// Read at most 4097 bytes to detect over-limit data, even if a file grows during reading.
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

// Only exact, closed synthetic fields reach CI output; a mismatch becomes a fixed
// sentinel. No fields callback runs on a missing or invalid record.
const projectRecord = <T>(row: RecordValue | null, valid: boolean, fields: () => T): T | "missing" | "invalid" =>
  row === null ? "missing" : valid ? fields() : "invalid";
function safeLog(o: Observation) {
  const knownRoutes = ["/cancel", "/complete", "/body", "/headers"];
  const knownFiles = [".size32-custody", "01.attempt.json", "01.failure.json",
    "02.attempt.json", "02.failure.json", "report.json"];
  const boundedTime = (value: number | null) =>
    value !== null && Number.isFinite(value) && value >= 0 ? value : null;
  const safeError = (value: string | null) => {
    if (value === null) return null;
    if (safeDescriptions.has(value)) return value;
    for (const prefix of ["bind:", "setup:", "records:", "server-stop:"])
      if (value.startsWith(prefix) && safeDescriptions.has(value.slice(prefix.length))) return value;
    return "Error:unexpected";
  };
  const firstCodes = o.case === "cancel" ? ["blob-too-large"] : o.case === "body" ? ["timeout", "cleanup-error"] : ["timeout"];
  const firstBytes = o.case === "cancel" ? 1_000_001 : o.case === "body" ? 3 : 0;
  return {
    case: o.case, bun: /^\d{1,4}\.\d{1,4}\.\d{1,4}(?:[-+][0-9A-Za-z.-]{1,32})?$/.test(o.bun) ? o.bun : "unknown",
    boundPort: o.boundPort !== null && Number.isInteger(o.boundPort) && o.boundPort > 0 && o.boundPort <= 65535 ? o.boundPort : null,
    routes: o.routes.slice(0, 3).map(route => knownRoutes.includes(route) ? route : "unexpected-route"),
    routesTruncated: o.routes.length > 3, hits: o.hits,
    firstEvents: o.firstEvents.slice(0, 4).map(event => ({
      kind: event.kind === "stream-cancel" || event.kind === "request-abort" ? event.kind : "unexpected-event",
      ms: boundedTime(event.ms),
    })), eventsTruncated: o.firstEvents.length > 4,
    closeConfirmedBeforeSecond: o.closeConfirmedBeforeSecond, closeWaitMs: boundedTime(o.closeWaitMs),
    clientAborted: o.clientAborted.slice(0, 3),
    clientAbortMs: o.clientAbortMs.slice(0, 3).map(boundedTime),
    inputsTruncated: o.clientAborted.length > 3 || o.clientAbortMs.length > 3,
    fetchInputs: o.fetchInputs, lateHeaderResponses: o.lateHeaderResponses,
    taskState: o.taskState,
    result: o.result === "resolved" || o.result === "not-started" ? o.result : safeError(o.result),
    files: o.files.slice(0, 8).map(file => knownFiles.includes(file) ? file : "unexpected-file"),
    filesTruncated: o.files.length > 8,
    firstAttempt: projectRecord(o.firstAttempt, exactAttempt(o.firstAttempt, refs[0]!), () =>
      ({ task: refs[0]!.task, blobOid: refs[0]!.blobOid, status: "started" })),
    secondAttempt: projectRecord(o.secondAttempt, exactAttempt(o.secondAttempt, refs[1]!), () =>
      ({ task: refs[1]!.task, blobOid: refs[1]!.blobOid, status: "started" })),
    first: projectRecord(o.first, exactFailure(o.first, refs[0]!, firstCodes, firstBytes), () =>
      ({ task: refs[0]!.task, blobOid: refs[0]!.blobOid, code: o.first!.code,
        observedBytes: firstBytes, disposition: failedDisposition })),
    second: projectRecord(o.second, o.case === "cancel" && exactFailure(o.second, refs[1]!, ["invalid-JSON"], 14), () =>
      ({ task: refs[1]!.task, blobOid: refs[1]!.blobOid, code: "invalid-JSON",
        observedBytes: 14, disposition: failedDisposition })),
    report: projectRecord(o.report, exactReport(o.report), () =>
      ({ contract: "algal.sni.size32.synthetic.v1", commit: SNI.commit,
        selectionSha256: syntheticSelectionSha256, statuses: { extracted: 0, failed: 2 },
        observedResponseBytes: 1_000_015, paidUsd: 0, disposition: reportDisposition })),
    serverStop: o.serverStop, diagnosticError: safeError(o.diagnosticError), pass: o.pass,
  };
}

// Pure regression: no loopback server, selected fetch, or one-use HTTP fixture.
test("synthetic HTTP diagnostic log rejects arbitrary codes and record/route/path data", () => {
  const marker = "SYNTHETIC_SECRET_123";
  expect(describe(Object.assign(new Error("failed"), { code: marker }))).toBe("Error:unexpected");
  expect(describe(Object.assign(new Error("failed"), { code: "ENOENT" }))).toBe("Error:ENOENT");
  const observation: Observation = {
    case: "body", bun: Bun.version, boundPort: null, routes: [`/private/${marker}`], hits: 0,
    firstEvents: [], closeConfirmedBeforeSecond: false, closeWaitMs: null,
    clientAborted: [], clientAbortMs: [], fetchInputs: 0, lateHeaderResponses: 0,
    taskState: "not-started", result: `Error:${marker}`,
    files: [`/private/${marker}`], firstAttempt: { task: refs[0]!.task, blobOid: refs[0]!.blobOid,
      status: "started", extra: marker }, secondAttempt: null,
    first: { task: refs[0]!.task, blobOid: refs[0]!.blobOid, code: marker,
      observedBytes: 3, disposition: failedDisposition }, second: null, report: null,
    serverStop: "not-started", diagnosticError: `records:Error:${marker}`, pass: false,
  };
  const projected = safeLog(observation);
  expect(JSON.stringify(projected)).not.toContain(marker);
  expect(projected.firstAttempt).toBe("invalid");
  expect(projected.first).toBe("invalid");
  expect(projected.routes).toEqual(["unexpected-route"]);
  expect(projected.files).toEqual(["unexpected-file"]);
  expect(projected.diagnosticError).toBe("Error:unexpected");
});

async function one(which: Case): Promise<Observation> {
  const o: Observation = {
    case: which, bun: Bun.version, boundPort: null, routes: [], hits: 0, firstEvents: [],
    closeConfirmedBeforeSecond: false, closeWaitMs: null, clientAborted: [], clientAbortMs: [], fetchInputs: 0,
    lateHeaderResponses: 0, taskState: "not-started", result: "not-started", files: [],
    firstAttempt: null, secondAttempt: null, first: null, second: null, report: null,
    serverStop: "not-started", diagnosticError: null, pass: false,
  };
  let server: ReturnType<typeof Bun.serve> | undefined;
  let directory: string | undefined;
  let headerTimer: ReturnType<typeof setTimeout> | undefined;
  let taskTimer: ReturnType<typeof setTimeout> | undefined;
  const firstEvents: Event[] = [];
  let serverEventsBeforeStop: Event[] = [];
  let settledMs: number | null = null;
  const start = performance.now();
  try {
    // Fresh names on every execution; never reuse a failed case or touch the private size32 preflight.
    await mkdir("runs", { recursive: true });
    directory = await mkdtemp(join("runs", "sni-size32-http-ci-v3-"));
    try {
      server = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch(request) {
        const path = new URL(request.url).pathname;
        o.hits++;
        o.routes.push(path);
        const first = which === "cancel" && path === "/cancel" ||
          which === "body" && path === "/body" || which === "headers" && path === "/headers";
        if (first) request.signal.addEventListener("abort", () => {
          firstEvents.push({ kind: "request-abort", ms: performance.now() - start });
        }, { once: true });
        if (which === "cancel" && path === "/complete") return new Response(payload);
        if (which === "headers" && path === "/headers") return new Promise<Response>(resolve => {
          headerTimer = setTimeout(() => {
            o.lateHeaderResponses++;
            resolve(new Response(payload));
          }, 450);
        });
        if (which === "cancel" && path === "/cancel" || which === "body" && path === "/body") {
          const bytes = which === "cancel" ? Buffer.alloc(1_000_001, 65) : Buffer.from("abc");
          return new Response(new ReadableStream<Uint8Array>({
            start(controller) { controller.enqueue(bytes); },
            cancel() { firstEvents.push({ kind: "stream-cancel", ms: performance.now() - start }); },
          }, { highWaterMark: 0 }), { headers: { "content-type": "application/octet-stream" } });
        }
        return new Response("unexpected-route", { status: 404 });
      } });
      const port = server.port;
      o.boundPort = port ?? null;
      if (typeof port !== "number" || !Number.isInteger(port) || port <= 0) throw Error("no-positive-bound-port");
    } catch (error) { o.result = `bind:${describe(error)}`; return o; }
    const base = `http://127.0.0.1:${server.port}`;
    const fetcher = async (input: string, init: RequestInit): Promise<Response> => {
      const index = o.fetchInputs++;
      if (index > 1 || input !== expectedInputs[index] || init.redirect !== "error" || !init.signal)
        throw Error("synthetic-fetch-input-mismatch");
      const signal = init.signal as AbortSignal;
      if (which === "cancel" && index === 1) {
        const waitStart = performance.now();
        const deadline = waitStart + 500;
        while (!firstEvents.length && performance.now() < deadline) await pause(10);
        const waitEnd = performance.now();
        o.closeWaitMs = waitEnd - waitStart;
        // A poll waking after the deadline cannot turn a late server event into confirmation.
        o.closeConfirmedBeforeSecond = waitEnd <= deadline &&
          firstEvents.some(event => event.ms <= deadline - start);
        if (!o.closeConfirmedBeforeSecond) throw Error("first-server-close-unconfirmed");
      }
      const signalIndex = o.clientAborted.push(signal.aborted) - 1;
      o.clientAbortMs.push(signal.aborted ? performance.now() - start : null);
      signal.addEventListener("abort", () => {
        o.clientAborted[signalIndex] = true;
        o.clientAbortMs[signalIndex] ??= performance.now() - start;
      }, { once: true });
      const route = which === "cancel" ? index === 0 ? "/cancel" : "/complete" : `/${which}`;
      // The nominal URL is NEVER passed to global fetch; redirects and signal are preserved.
      return fetch(base + route, { ...init, redirect: "error", signal });
    };
    o.taskState = "pending";
    const task = runSyntheticSize32(directory, refs, fetcher, undefined, which === "cancel" ? 750 : 120);
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
    if (o.taskState === "settled") {
      settledMs = performance.now() - start;
      if (which !== "cancel") await pause(500);
    }
  } catch (error) {
    o.diagnosticError = describe(error);
    if (directory === undefined) o.result = `setup:${o.diagnosticError}`;
  } finally {
    // Only pre-teardown events count as transport evidence; stop(true) may itself abort a request.
    serverEventsBeforeStop = [...firstEvents];
    if (headerTimer) clearTimeout(headerTimer);
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
      if (o.files.includes("01.attempt.json")) o.firstAttempt = await readObject(directory, "01.attempt.json");
      if (o.files.includes("02.attempt.json")) o.secondAttempt = await readObject(directory, "02.attempt.json");
      if (o.files.includes("01.failure.json")) o.first = await readObject(directory, "01.failure.json");
      if (o.files.includes("02.failure.json")) o.second = await readObject(directory, "02.failure.json");
      if (o.files.includes("report.json")) o.report = await readObject(directory, "report.json");
    } catch (error) { o.diagnosticError = `records:${describe(error)}`; }
  }
  // Never classify a server event caused by listener teardown as transport cleanup.
  o.firstEvents = serverEventsBeforeStop;
  const base = o.boundPort !== null && o.boundPort > 0 && o.taskState === "settled" &&
    o.serverStop === "settled" && o.diagnosticError === null && exactAttempt(o.firstAttempt, refs[0]!);
  const abortedAt = o.clientAbortMs[0];
  if (which === "cancel") o.pass = base && o.result === "resolved" &&
    o.closeConfirmedBeforeSecond && o.closeWaitMs !== null && o.closeWaitMs <= 500 &&
    o.firstEvents.length > 0 && o.clientAborted[0] === false && o.fetchInputs === 2 &&
    o.hits === 2 && o.routes.join(",") === "/cancel,/complete" &&
    exactFailure(o.first, refs[0]!, ["blob-too-large"], 1_000_001) &&
    exactAttempt(o.secondAttempt, refs[1]!) && exactFailure(o.second, refs[1]!, ["invalid-JSON"], 14) &&
    equalFiles(o.files, [".size32-custody", "01.attempt.json", "01.failure.json", "02.attempt.json", "02.failure.json", "report.json"]) &&
    exactReport(o.report);
  else o.pass = base && o.result === "Error:size32-cleanup-uncertain" &&
    o.fetchInputs === 1 && o.hits === 1 && o.routes[0] === `/${which}` &&
    exactFailure(o.first, refs[0]!, which === "body" ? ["timeout", "cleanup-error"] : ["timeout"], which === "body" ? 3 : 0) &&
    o.clientAborted[0] === true && abortedAt !== null && abortedAt !== undefined &&
    serverEventsBeforeStop.some(event => settledMs !== null &&
      event.ms >= abortedAt && event.ms <= settledMs + 500) &&
    equalFiles(o.files, [".size32-custody", "01.attempt.json", "01.failure.json"]);
  return o;
}

qualification("synthetic Bun HTTP cancellation and abort fail-stop in GitHub Actions only", async () => {
  const observations: Observation[] = [];
  for (const which of ["cancel", "body", "headers"] as const) {
    const observation = await one(which);
    observations.push(observation);
    // Print a closed, capped projection, never the parsed ledger or raw route/file names.
    console.log(`SNI_SIZE32_HTTP_V3 ${JSON.stringify(safeLog(observation))}`);
    if (observation.boundPort === null || observation.taskState !== "settled" || observation.serverStop !== "settled") break;
  }
  expect(observations.map(observation => `${observation.case}:${observation.pass}`)).toEqual([
    "cancel:true", "body:true", "headers:true",
  ]);
}, 15_000);
