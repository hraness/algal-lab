import { expect, test } from "bun:test";
import { checkedRss, hostRssBytes, parsePsRss } from "./rss";

test("RSS parsing rejects empty, malformed, zero, and overflowed ps output", () => {
  expect(parsePsRss(" 12345\n")).toBe(12345 * 1024);
  for (const bad of ["", " ", "0", "12\n34", "12.5", "-1", "Infinity", "9999999999999999999999"])
    expect(() => parsePsRss(bad)).toThrow();
});

test("independent sampler disagreement and invalid readings fail closed", () => {
  expect(checkedRss(1024 * 1024, 1024 * 1024, 1024 * 1024)).toBe(1024 * 1024);
  expect(checkedRss(1024 * 1024, 2 * 1024 * 1024, 2 * 1024 * 1024)).toBe(2 * 1024 * 1024);
  for (const bad of [0, -1, NaN, Infinity, 1.5, Number.MAX_SAFE_INTEGER + 1])
    expect(() => checkedRss(bad, 1024 * 1024, 1024 * 1024)).toThrow();
  expect(() => checkedRss(1024 * 1024, 1024 * 1024 + 65537, 1024 * 1024)).toThrow();
  expect(() => checkedRss(1024 * 1024, 1024 * 1024 - 65537, 1024 * 1024)).toThrow();
});

test("invalid or exited PID does not produce a synthetic reading", async () => {
  await expect(hostRssBytes(0)).rejects.toThrow();
  await expect(hostRssBytes(-1)).rejects.toThrow();
  if (process.platform === "darwin") await expect(hostRssBytes(2147483647)).rejects.toThrow();
});

const python = Bun.which("python3");
const elixir = Bun.which("elixir");
const live = process.platform === "darwin" && python !== null && elixir !== null;
(live ? test : test.skip)("Bun and OTP child host RSS agrees with independent OS rusage probe", async () => {
  // The Python binding reads rusage_info_v0.ri_resident_size (offset 64),
  // independent of the Bun FFI proc_pidinfo sampler and the host journal.
  const probe = `import ctypes,struct,sys
p=ctypes.CDLL('/usr/lib/libproc.dylib',use_errno=True)
b=ctypes.create_string_buffer(96)
if p.proc_pid_rusage(int(sys.argv[1]),0,b) != 0: raise RuntimeError('rusage failed')
print(struct.unpack_from('=Q',b,64)[0])`;
  const hosts = [
    [process.execPath, "-e", "console.log('ready'); await Bun.sleep(10000)"],
    [elixir!, "--erl", "+S 4:4", "-e", "IO.puts(\"ready\"); Process.sleep(10000)"],
  ];
  for (const command of hosts) {
    const child = Bun.spawn(command, { stdout: "pipe", stderr: "pipe" });
    try {
      const reader = child.stdout.getReader();
      const first = await Promise.race([reader.read(), Bun.sleep(5000).then(() => { throw new Error("host readiness timeout"); })]);
      if (first.done || !new TextDecoder().decode(first.value).includes("ready")) throw new Error("host not ready");
      reader.releaseLock();
      const measured = await hostRssBytes(child.pid);
      const independent = Bun.spawn([python!, "-c", probe, String(child.pid)], { stdout: "pipe", stderr: "pipe" });
      const [text, errors, exit] = await Promise.all([
        new Response(independent.stdout).text(), new Response(independent.stderr).text(), independent.exited,
      ]);
      if (exit !== 0 || !/^[1-9][0-9]*\n$/.test(text)) throw new Error(`independent probe failed: ${errors}`);
      const reference = Number(text.trim());
      expect(Number.isSafeInteger(reference)).toBe(true);
      expect(Math.abs(measured - reference)).toBeLessThanOrEqual(65536);
    } finally {
      if (child.exitCode === null && child.signalCode === null) child.kill();
      await child.exited;
    }
  }
}, 20000);
