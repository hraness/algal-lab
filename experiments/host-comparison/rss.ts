import { dlopen, ptr } from "bun:ffi";

// Darwin's proc_taskinfo.pti_resident_size and rusage_info_v0.ri_resident_size
// are current, single-PID OS RSS in bytes (not max RSS or physical footprint).
// Layouts: Apple xnu bsd/sys/proc_info.h and bsd/sys/resource.h.
const TASK_INFO = 4;
const TASK_INFO_BYTES = 96;
const RUSAGE_INFO_V0 = 0;
const RUSAGE_INFO_BYTES = 96;
const PARITY_TOLERANCE_BYTES = 65536; // Four 16-KiB Darwin pages between adjacent reads.

const libproc = process.platform === "darwin" ? dlopen("/usr/lib/libproc.dylib", {
  proc_pidinfo: { args: ["i32", "i32", "u64", "ptr", "i32"], returns: "i32" },
  proc_pid_rusage: { args: ["i32", "i32", "ptr"], returns: "i32" },
}) : undefined;

function resident(value: bigint): number {
  if (value <= 0n || value > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error("invalid OS RSS");
  return Number(value);
}

function taskRss(pid: number): number {
  const bytes = new Uint8Array(TASK_INFO_BYTES);
  const count = libproc!.symbols.proc_pidinfo(pid, TASK_INFO, 0, ptr(bytes), bytes.length);
  if (count !== TASK_INFO_BYTES) throw new Error(`proc_pidinfo failed: ${count} bytes`);
  return resident(new DataView(bytes.buffer).getBigUint64(8, true));
}

function rusageRss(pid: number): number {
  const bytes = new Uint8Array(RUSAGE_INFO_BYTES);
  const result = libproc!.symbols.proc_pid_rusage(pid, RUSAGE_INFO_V0, ptr(bytes));
  if (result !== 0) throw new Error(`proc_pid_rusage failed: ${result}`);
  return resident(new DataView(bytes.buffer).getBigUint64(64, true));
}

// The reference uses a different OS API. Bracketing tolerates host allocations
// between reads, but rejects disagreement outside the observed range + four pages.
export function checkedRss(first: number, reference: number, last: number): number {
  for (const value of [first, reference, last]) {
    if (!Number.isSafeInteger(value) || value <= 0) throw new Error("invalid OS RSS");
  }
  if (reference < Math.min(first, last) - PARITY_TOLERANCE_BYTES ||
      reference > Math.max(first, last) + PARITY_TOLERANCE_BYTES) {
    throw new Error("OS RSS samplers disagree");
  }
  return last;
}

export function parsePsRss(text: string): number {
  if (!/^\s*[1-9][0-9]*\s*$/.test(text)) throw new Error("invalid ps RSS");
  const kib = Number(text.trim());
  if (!Number.isSafeInteger(kib) || !Number.isSafeInteger(kib * 1024)) throw new Error("invalid ps RSS");
  return kib * 1024;
}

export async function hostRssBytes(pid: number): Promise<number> {
  if (!Number.isSafeInteger(pid) || pid <= 0) throw new Error("invalid host PID");
  if (libproc) return checkedRss(taskRss(pid), rusageRss(pid), taskRss(pid));
  // Preserve the original ps endpoint off Darwin, but never turn an empty or
  // failed subprocess into a made-up zero-byte sample.
  const process = Bun.spawn(["/bin/ps", "-o", "rss=", "-p", String(pid)], { stdout: "pipe", stderr: "pipe" });
  const [text, errors, exit] = await Promise.all([
    new Response(process.stdout).text(), new Response(process.stderr).text(), process.exited,
  ]);
  if (exit !== 0) throw new Error(`ps RSS failed: ${exit}: ${errors.trim().slice(0, 256)}`);
  return parsePsRss(text);
}
