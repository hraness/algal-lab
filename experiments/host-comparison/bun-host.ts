import { appendFileSync, closeSync, existsSync, fsyncSync, mkdirSync, openSync, readFileSync, rmdirSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { parseCommand, parseRecord, type Job, type RecordRow } from "./protocol";

const [directory, activeArg = "4", backlogArg = "32"] = process.argv.slice(2);
if (!directory) throw new Error("run directory required");
const limit = Number(activeArg), backlog = Number(backlogArg);
if (!Number.isInteger(limit) || limit < 1 || limit > 8 || !Number.isInteger(backlog) || backlog < 1 || backlog > 64) throw new Error("invalid limits");
mkdirSync(join(directory, "host.lock"));
writeFileSync(join(directory, "host.lock", "pid"), String(process.pid));
const journal = join(directory, "journal.jsonl");
const rows = new Map<string, RecordRow>();
const queued: { job: Job; received: number }[] = [];
const active = new Map<string, ReturnType<typeof Bun.spawn>>();
let stopping = false;
function emit(value: object): void { process.stdout.write(JSON.stringify(value) + "\n"); }
function persist(row: RecordRow): void {
  const fd = openSync(journal, "a", 0o600);
  try { appendFileSync(fd, JSON.stringify(row) + "\n"); fsyncSync(fd); } finally { closeSync(fd); }
  rows.set(row.job.id, row); emit({ event: "state", ...row });
}
if (existsSync(journal)) {
  const content = readFileSync(journal, "utf8");
  if (Buffer.byteLength(content) > 4_000_000 || (content && !content.endsWith("\n"))) throw new Error("journal incomplete or oversized; reconciliation required");
  for (const line of content.trim().split("\n").filter(Boolean)) { const row = parseRecord(JSON.parse(line)); rows.set(row.job.id, row); }
  if (rows.size > 512) throw new Error("journal job bound exceeded");
  for (const row of rows.values()) if (row.status === "queued" || row.status === "running") persist({ ...row, status: row.status === "queued" ? "cancelled" : "uncertain", reason: "host_restart" });
}
function cancel(id: string, reason: string): void {
  const row = rows.get(id);
  if (row?.status === "queued" || row?.status === "running") {
    persist({ ...row, status: row.status === "queued" ? "cancelled" : "uncertain", reason });
    active.get(id)?.kill();
  }
}
function finish(): void {
  if (stopping && active.size === 0) {
    clearInterval(ticker); unlinkSync(join(directory!, "host.lock", "pid")); rmdirSync(join(directory!, "host.lock")); process.exit(0);
  }
}
function pump(): void {
  for (let i = queued.length - 1; i >= 0; i--) {
    const q = queued[i]!;
    if (rows.get(q.job.id)?.status !== "queued") queued.splice(i, 1);
    else if (performance.now() - q.received >= q.job.ttl_ms) { persist({ job: q.job, status: "expired", reason: "deadline_before_dispatch" }); queued.splice(i, 1); }
  }
  while (!stopping && active.size < limit && queued.length) {
    const q = queued.shift()!;
    const running: RecordRow = { job: q.job, status: "running", reason: "dispatch_intent", queue_ms: performance.now() - q.received };
    // Sync intent precedes subprocess creation. Any crash afterward is uncertain.
    persist(running);
    try {
      const child = Bun.spawn([process.execPath, join(import.meta.dir, "worker.ts"), JSON.stringify(q.job), directory!], { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
      active.set(q.job.id, child); emit({ event: "spawn", id: q.job.id, pid: child.pid });
      const timeout = setTimeout(() => child.kill(), 31000);
      void (async () => {
        const [output, errors, code] = await Promise.all([new Response(child.stdout).text(), new Response(child.stderr).text(), child.exited]);
        clearTimeout(timeout);
        active.delete(q.job.id);
        const current = rows.get(q.job.id)!;
        if (current.status === "running") {
          let result: { digest?: string } | undefined;
          if (Buffer.byteLength(output) < 16384) for (const line of output.trim().split("\n").filter(Boolean)) { const v = JSON.parse(line); if (v.event === "result") result = v; }
          if (code === 0 && typeof result?.digest === "string") persist({ ...current, status: "complete", reason: "settled", digest: result.digest });
          else persist({ ...current, status: "uncertain", reason: `worker_exit_${code}` });
          if (errors) emit({ event: "worker_error", id: q.job.id, message: errors.slice(0, 1024) });
        }
        pump(); finish();
      })().catch((error: unknown) => { emit({ event: "fatal", message: String(error) }); process.exit(1); });
    } catch { persist({ ...running, status: "uncertain", reason: "spawn_failed" }); }
  }
  finish();
}
function stop(): void { stopping = true; for (const id of rows.keys()) cancel(id, "host_stop"); pump(); }
const ticker = setInterval(pump, 5);
process.on("SIGTERM", stop);
emit({ event: "ready", host: "bun", pid: process.pid, active_limit: limit, backlog_limit: backlog });
let buffer = "";
for await (const bytes of process.stdin) {
  buffer += Buffer.from(bytes).toString("utf8");
  if (Buffer.byteLength(buffer) > 16384) { emit({ event: "rejected", reason: "input_too_large" }); stop(); break; }
  let at: number;
  while ((at = buffer.indexOf("\n")) !== -1) {
    const line = buffer.slice(0, at); buffer = buffer.slice(at + 1);
    try {
      const cmd = parseCommand(JSON.parse(line));
      if (cmd.op === "submit") {
        pump();
        if (rows.has(cmd.job.id)) emit({ event: "duplicate", id: cmd.job.id, status: rows.get(cmd.job.id)!.status });
        else if (stopping || rows.size >= 512 || queued.length >= backlog) emit({ event: "rejected", id: cmd.job.id, reason: "capacity" });
        else { queued.push({ job: cmd.job, received: performance.now() }); persist({ job: cmd.job, status: "queued", reason: "accepted" }); pump(); }
      } else if (cmd.op === "cancel") { cancel(cmd.id, "cancelled_by_owner"); pump(); }
      else if (cmd.op === "owner_down") { for (const row of rows.values()) if (row.job.owner === cmd.owner) cancel(row.job.id, "owner_down"); pump(); }
      else if (cmd.op === "observe") emit({ event: "observation", active: active.size, queued: queued.length, retained: rows.size, rss_bytes: process.memoryUsage().rss });
      else if (cmd.op === "crash_owner") process.kill(process.pid, "SIGKILL");
      else stop();
    } catch { emit({ event: "rejected", reason: "invalid_command" }); }
  }
}
stop();
