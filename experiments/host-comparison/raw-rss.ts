import { dlopen, ptr } from "bun:ffi";
import { checkedRss } from "./rss";

// Test-only prospective instrumentation. Keep v1's sampler and frozen source
// untouched; this is not wired to the v1 comparison harness.
export type RawReading = { source: "proc_pidinfo" | "proc_pid_rusage"; atNs: string; bytes: number };
export type RawRssSample = { pid: number; index: number; readings: [RawReading, RawReading, RawReading]; measuredBytes: number };

const proc = process.platform === "darwin" ? dlopen("/usr/lib/libproc.dylib", {
  proc_pidinfo: { args: ["i32", "i32", "u64", "ptr", "i32"], returns: "i32" },
  proc_pid_rusage: { args: ["i32", "i32", "ptr"], returns: "i32" },
}) : undefined;

function resident(bytes: Uint8Array, offset: number): number {
  const value = new DataView(bytes.buffer).getBigUint64(offset, true);
  if (value <= 0n || value > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error("invalid OS RSS");
  return Number(value);
}

function task(pid: number): number {
  const bytes = new Uint8Array(96); // proc_taskinfo.pti_resident_size, Apple xnu proc_info.h
  const count = proc!.symbols.proc_pidinfo(pid, 4, 0, ptr(bytes), bytes.length);
  if (count !== bytes.length) throw new Error(`proc_pidinfo failed: ${count} bytes`);
  return resident(bytes, 8);
}

function rusage(pid: number): number {
  const bytes = new Uint8Array(96); // rusage_info_v0.ri_resident_size, Apple xnu resource.h
  if (proc!.symbols.proc_pid_rusage(pid, 0, ptr(bytes)) !== 0) throw new Error("proc_pid_rusage failed");
  return resident(bytes, 64);
}

export function captureRawHostRss(pid: number, index: number): RawRssSample {
  if (!proc) throw new Error("raw bracketing requires Darwin; no ps fallback");
  if (!Number.isSafeInteger(pid) || pid <= 0 || pid > 2147483647) throw new Error("invalid host PID");
  if (!Number.isSafeInteger(index) || index < 0 || index >= 4096) throw new Error("invalid RSS index");
  const first = task(pid);
  const firstAt = process.hrtime.bigint().toString();
  const reference = rusage(pid);
  const referenceAt = process.hrtime.bigint().toString();
  const last = task(pid);
  const lastAt = process.hrtime.bigint().toString();
  const measuredBytes = checkedRss(first, reference, last);
  return { pid, index, readings: [
    { source: "proc_pidinfo", atNs: firstAt, bytes: first },
    { source: "proc_pid_rusage", atNs: referenceAt, bytes: reference },
    { source: "proc_pidinfo", atNs: lastAt, bytes: last },
  ], measuredBytes };
}
