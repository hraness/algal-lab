import { strict as assert } from "node:assert";
import { existsSync, mkdirSync, readFileSync, rmdirSync, unlinkSync, writeFileSync } from "node:fs";
import { cpus, platform, release, totalmem } from "node:os";
import { dirname, join, resolve } from "node:path";
import type { Command, Job } from "./protocol";

type Host = "bun" | "otp";
type Event = { event: string; at: number; id?: string; job?: Job; pid?: number; status?: string; reason?: string; digest?: string; queue_ms?: number; active?: number; queued?: number };
const terminal = new Set(["complete", "uncertain", "cancelled", "expired"]);
const elixir = process.env.ELIXIR ?? Bun.which("elixir") ?? "/opt/homebrew/bin/elixir";
const directory = resolve(process.argv[2] ?? "runs/host-comparison");
mkdirSync(dirname(directory), { recursive: true });
mkdirSync(directory); // A run never overwrites earlier evidence.
const transcript: { host: Host; scenario: string; event: Event }[] = [];
const live = new Set<Session>();
function alive(pid: number): boolean { try { process.kill(pid, 0); return true; } catch { return false; } }
async function until(condition: () => boolean | Promise<boolean>, label: string, timeout = 15000): Promise<void> {
  const started = performance.now();
  while (!await condition()) { if (performance.now() - started > timeout) throw new Error(`timeout: ${label}`); await Bun.sleep(5); }
}
class Session {
  readonly events: Event[] = [];
  readonly child: ReturnType<typeof Bun.spawn<"pipe", "pipe", "pipe">>;
  readonly errors: Promise<string>;
  readonly output: Promise<void>;
  readonly folder: string;
  constructor(readonly host: Host, readonly scenario: string, active = 4, backlog = 32, restart = false) {
    this.folder = join(directory, `${host}-${scenario}`);
    if (!restart) mkdirSync(this.folder);
    const command = host === "bun"
      ? [process.execPath, join(import.meta.dir, "bun-host.ts"), this.folder, String(active), String(backlog)]
      : [elixir, "--erl", "+S 4:4", join(import.meta.dir, "otp-host.exs"), this.folder, process.execPath, join(import.meta.dir, "worker.ts"), String(active), String(backlog)];
    const child = Bun.spawn(command, { stdin: "pipe", stdout: "pipe", stderr: "pipe" });
    this.child = child;
    live.add(this);
    this.errors = new Response(this.child.stderr).text();
    this.output = (async () => {
      let pending = "";
      for await (const chunk of child.stdout) {
        pending += Buffer.from(chunk).toString("utf8");
        let at: number;
        while ((at = pending.indexOf("\n")) >= 0) {
          const line = pending.slice(0, at); pending = pending.slice(at + 1);
          try {
            const event = { ...JSON.parse(line), at: performance.now() } as Event;
            this.events.push(event); transcript.push({ host, scenario, event });
          } catch { throw new Error(`non-JSON ${host} output: ${line.slice(0, 1000)}`); }
        }
      }
    })();
  }
  async ready(): Promise<void> {
    await until(async () => {
      if (this.child.exitCode !== null || this.child.signalCode !== null) throw new Error(`${this.host} exited: ${await this.errors}`);
      return this.events.some((e) => e.event === "ready");
    }, `${this.host} ready`);
  }
  send(cmd: Command | object): void { this.child.stdin.write(JSON.stringify(cmd) + "\n"); this.child.stdin.flush(); }
  state(id: string): Event | undefined { return [...this.events].reverse().find((e) => e.event === "state" && e.job?.id === id); }
  async settled(id: string): Promise<Event> { await until(() => terminal.has(this.state(id)?.status ?? ""), `${this.host} ${id} settled`); return this.state(id)!; }
  async spawned(id: string): Promise<number> { await until(() => this.events.some((e) => e.event === "spawn" && e.id === id), `${id} spawned`); return this.events.find((e) => e.event === "spawn" && e.id === id)!.pid!; }
  effects(): string[] { return existsSync(join(this.folder, "effects.jsonl")) ? readFileSync(join(this.folder, "effects.jsonl"), "utf8").trim().split("\n").filter(Boolean).map((s) => String(JSON.parse(s).id)) : []; }
  async close(kill = false): Promise<void> {
    if (this.child.exitCode === null && this.child.signalCode === null) { if (kill) this.child.kill("SIGKILL"); else this.send({ op: "stop" }); }
    await Promise.race([this.child.exited, Bun.sleep(10000).then(() => { throw new Error("host exit timeout"); })]);
    await this.output;
    const errors = await this.errors;
    if (!kill && this.child.exitCode !== 0) throw new Error(errors || `host exit ${this.child.exitCode}`);
    for (const event of this.events.filter((e) => e.event === "spawn")) await until(() => !alive(event.pid!), "worker owner lease closed", 5000);
    live.delete(this);
    if (kill) {
      // The harness owns this exact child and has observed both host and worker exits.
      // Recovery is deliberately explicit; hosts never remove a live owner's lock.
      const lock = join(this.folder, "host.lock");
      assert.equal(Number(readFileSync(join(lock, "pid"), "utf8")), this.child.pid);
      unlinkSync(join(lock, "pid")); rmdirSync(lock);
    }
  }
}
function job(id: string, options: Partial<Job> = {}): Job { return { id, owner: "owner", delay_ms: 20, ttl_ms: 30000, fault: "none", ...options }; }
function submit(session: Session, value: Job): void { session.send({ op: "submit", job: value }); }
function assertLimits(events: Event[], active: number, backlog: number): void {
  const states = new Map<string, string>();
  for (const event of events) if (event.event === "state") {
    states.set(event.job!.id, event.status!);
    assert.ok([...states.values()].filter((status) => status === "running").length <= active, "active bound");
    assert.ok([...states.values()].filter((status) => status === "queued").length <= backlog, "backlog bound");
  }
}
function quantile(values: number[], q: number): number { const sorted = [...values].sort((a, b) => a - b); return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * q))]!; }
async function rss(pid: number): Promise<number> {
  const process = Bun.spawn(["/bin/ps", "-o", "rss=", "-p", String(pid)], { stdout: "pipe", stderr: "pipe" });
  const text = await new Response(process.stdout).text(); await process.exited;
  return Number(text.trim()) * 1024;
}
const benchmarks: object[] = [];
const checks: object[] = [];
const digests = new Map<string, string>();
async function benchmark(host: Host, repeat: number): Promise<void> {
  const starting = performance.now();
  const s = new Session(host, `throughput-${repeat}`); await s.ready();
  const startupMs = performance.now() - starting;
  const baseline = await rss(s.child.pid), samples = [baseline];
  const start = performance.now();
  for (let i = 0; i < 24; i++) submit(s, job(`work-${i}`));
  while (s.events.filter((e) => e.event === "state" && terminal.has(e.status ?? "")).length < 24) { samples.push(await rss(s.child.pid)); await Bun.sleep(20); assert.ok(performance.now() - start < 15000); }
  const elapsed = performance.now() - start;
  for (let i = 0; i < 24; i++) {
    const row = s.state(`work-${i}`)!; assert.equal(row.status, "complete");
    const key = `work-${i}`; if (digests.has(key)) assert.equal(row.digest, digests.get(key), "identical canonical receipts across hosts/repeats"); else digests.set(key, row.digest!);
  }
  assert.equal(new Set(s.effects()).size, 24); assert.equal(s.effects().length, 24);
  assertLimits(s.events, 4, 32);
  const queues = s.events.filter((e) => e.status === "running").map((e) => e.queue_ms!);
  benchmarks.push({ host, repeat, jobs: 24, concurrency: 4, startup_ms: startupMs, elapsed_ms: elapsed, throughput_per_second: 24000 / elapsed, queue_p50_ms: quantile(queues, 0.5), queue_p95_ms: quantile(queues, 0.95), host_rss_baseline_bytes: baseline, host_rss_peak_sampled_bytes: Math.max(...samples) });
  await s.close();
}
async function failures(host: Host): Promise<void> {
  const s = new Session(host, "failures", 1, 2); await s.ready();
  submit(s, job("running", { delay_ms: 5000 })); const pid = await s.spawned("running");
  submit(s, job("expiry", { ttl_ms: 1000 })); submit(s, job("queued")); submit(s, job("overflow"));
  await until(() => s.events.some((e) => e.event === "rejected" && e.id === "overflow"), "bounded backlog");
  assert.equal((await s.settled("expiry")).status, "expired");
  s.send({ op: "cancel", id: "queued" }); assert.equal((await s.settled("queued")).status, "cancelled");
  const cancellation = performance.now(); s.send({ op: "cancel", id: "running" });
  assert.equal((await s.settled("running")).status, "uncertain"); await until(() => !alive(pid), "cancelled process exited");
  const cancellationMs = performance.now() - cancellation;
  for (const [id, fault] of [["worker-before", "before_dispatch"], ["worker-after", "after_effect"]] as const) {
    submit(s, job(id, { fault })); assert.equal((await s.settled(id)).status, "uncertain"); submit(s, job(id, { fault }));
  }
  submit(s, job("owner-active", { owner: "lost", delay_ms: 5000 })); await s.spawned("owner-active");
  submit(s, job("owner-queued", { owner: "lost" })); s.send({ op: "owner_down", owner: "lost" });
  assert.equal((await s.settled("owner-active")).status, "uncertain"); assert.equal((await s.settled("owner-queued")).status, "cancelled");
  submit(s, job("healthy")); assert.equal((await s.settled("healthy")).status, "complete");
  s.send({ op: "submit", job: { ...job("invalid"), command: "forbidden" } });
  await until(() => s.events.some((e) => e.event === "rejected" && e.reason === "invalid_command"), "unknown authority rejected");
  s.send({ op: "observe" }); await until(() => s.events.some((e) => e.event === "observation"), "observation");
  assert.deepEqual(s.effects().sort(), ["healthy", "worker-after"]);
  assert.equal(s.events.filter((e) => e.event === "duplicate").length, 2);
  assertLimits(s.events, 1, 2);
  await s.close();
  checks.push({ host, scenario: "admission_cancel_worker_owner", passed: true, cancellation_to_process_exit_ms: cancellationMs, effect_count: 2 });

  for (const phase of ["before-effect", "after-effect"] as const) {
    const name = `host-crash-${phase}`;
    const first = new Session(host, name, 1, 2); await first.ready();
    const j = job("inflight", phase === "before-effect" ? { delay_ms: 5000 } : { fault: "hold_after_effect" });
    submit(first, j); await first.spawned(j.id); submit(first, job("waiting"));
    await until(() => first.state("waiting")?.status === "queued", "waiting durable");
    if (phase === "after-effect") await until(() => first.effects().includes(j.id), "effect committed before host crash");
    if (phase === "before-effect") {
      // Kill the owning GenServer in OTP (event-loop owner in Bun), separately
      // from the OS-host SIGKILL tested after the effect.
      first.send({ op: "crash_owner" });
      await until(() => first.child.exitCode !== null || first.child.signalCode !== null, "owner crash terminates service");
    }
    await first.close(true);
    const second = new Session(host, name, 1, 2, true); await second.ready();
    assert.equal(second.state("inflight")?.status, "uncertain"); assert.equal(second.state("waiting")?.status, "cancelled");
    submit(second, j); submit(second, job("waiting"));
    await until(() => second.events.filter((e) => e.event === "duplicate").length === 2, "restart duplicate guard");
    submit(second, job("after-recovery")); assert.equal((await second.settled("after-recovery")).status, "complete");
    assert.deepEqual(second.effects().sort(), phase === "after-effect" ? ["after-recovery", "inflight"] : ["after-recovery"]);
    await second.close(); checks.push({ host, scenario: name, passed: true, recovered_inflight: "uncertain", recovered_waiting: "cancelled", duplicate_dispatches: 0 });
  }
}
try {
  // Alternate order to reduce simple order bias; still a single-machine smoke benchmark.
  for (let repeat = 0; repeat < 3; repeat++) for (const host of (repeat % 2 ? ["otp", "bun"] : ["bun", "otp"]) as Host[]) await benchmark(host, repeat);
  for (const host of ["bun", "otp"] as const) await failures(host);
  const version = Bun.spawn([elixir, "--version"], { stdout: "pipe", stderr: "pipe" });
  const elixirVersion = await new Response(version.stdout).text(); await version.exited;
  const dependency = JSON.parse(readFileSync(join(import.meta.dir, "../../package.json"), "utf8")).dependencies["@hraness/algal"];
  const result = { contract: "algal.lab.host-comparison.v1", environment: { bun: Bun.version, elixir: elixirVersion.trim(), beam_schedulers: 4, platform: platform(), release: release(), cpu: cpus()[0]?.model, logical_cpus: cpus().length, total_memory_bytes: totalmem(), algal: dependency }, workload: { jobs: 24, repeats: 3, concurrency: 4, backlog: 32, effect_delay_ms: 20, max_jobs_per_host: 512, provider_calls: 0 }, benchmarks, checks, canonical_receipts_equal: true, limits: ["One shared development machine; no statistical performance conclusion.", "Includes ALGAL import/subprocess launch, fsync and host protocol overhead; not a BEAM VM microbenchmark.", "RSS is sampled OS host-process RSS; excludes common ALGAL subprocesses and allocator figures are not compared.", "Deadline applies to admission; worker execution has a separate 31-second bound.", "Explicit single-writer recovery after observed owner exit; no distributed lease or remote provider reconciliation.", "Local append fixture demonstrates uncertainty; it does not validate a production provider."] };
  writeFileSync(join(directory, "report.json"), JSON.stringify(result, null, 2) + "\n");
  writeFileSync(join(directory, "events.jsonl"), transcript.map((row) => JSON.stringify(row)).join("\n") + "\n");
  console.log(JSON.stringify(result, null, 2));
} catch (error) {
  writeFileSync(join(directory, "failure.json"), JSON.stringify({ contract: "algal.lab.host-comparison-failure.v1", error: String(error), benchmarks, checks }, null, 2) + "\n");
  throw error;
} finally {
  for (const session of live) { try { await session.close(true); } catch (error) { console.error(String(error)); } }
  writeFileSync(join(directory, "events.jsonl"), transcript.map((row) => JSON.stringify(row)).join("\n") + "\n");
}
