import { afterEach, expect, test } from "bun:test";
import { access, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { verifyStudy } from "./study";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true }))); });
const project = fileURLToPath(new URL("../", import.meta.url));

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "algal-gateway-entrypoint-")); roots.push(root);
  const output = join(root, "archive");
  const run = async (model = "openai/gpt-6-luna", env: Record<string, string> = {}) => {
    // An explicit environment prevents local dotenv files or operator credentials
    // from turning these failure-path checks into paid model calls.
    const child = Bun.spawn([process.execPath, "--no-env-file", "examples/gateway-study.ts", "--protocol", "examples/network-model-smoke.json", "--out", output], {
      cwd: project, env: { PATH: process.env.PATH ?? "", GATEWAY_MODEL: model, GATEWAY_PROVIDER: "openai", ...env }, stdout: "pipe", stderr: "pipe",
    });
    const [exitCode, stdout, stderr] = await Promise.all([child.exited, new Response(child.stdout).text(), new Response(child.stderr).text()]);
    return { exitCode, stdout, stderr };
  };
  return { output, run };
}

test("Gateway entry point exclusively owns its archive and retains initialization failures", async () => {
  const existing = await fixture();
  await mkdir(existing.output);
  await writeFile(join(existing.output, "intent.json"), "previous evidence\n");
  expect((await existing.run()).exitCode).not.toBe(0);
  expect(await readFile(join(existing.output, "intent.json"), "utf8")).toBe("previous evidence\n");
  expect(await readdir(existing.output)).toEqual(["intent.json"]);

  const invalid = await fixture();
  expect((await invalid.run("invalid-selection")).exitCode).not.toBe(0);
  expect((await readdir(invalid.output)).sort()).toEqual(["gateway.json", "intent.json"]);
  expect(JSON.parse(await readFile(join(invalid.output, "gateway.json"), "utf8"))).toEqual({
    configuration: null, configurationDigest: null, observations: [], cancelled: false,
  });
});

test("Gateway entry point preserves all missing-credential failures with no dispatch", async () => {
  const f = await fixture();
  const result = await f.run();
  expect(result.exitCode).toBe(0); // The study archive records failed proposal slots.
  const transport = JSON.parse(await readFile(join(f.output, "gateway.json"), "utf8"));
  expect(transport.observations).toHaveLength(12);
  expect(transport.observations.every((o: { dispatched: boolean; status: string; code: string }) =>
    !o.dispatched && o.status === "failed" && o.code === "credential_unavailable")).toBe(true);
  const verified = await verifyStudy(join(f.output, "study"));
  expect(verified.experiments).toBe(0);
});

test("Gateway entry point keeps the twelve-call default and records an explicit call budget only when configured", async () => {
  const explicit = await fixture();
  const result = await explicit.run(undefined, { ALGAL_LAB_GATEWAY_MAX_CALLS: "24" });
  expect(result.exitCode).toBe(0);
  const configuration = JSON.parse(await readFile(join(explicit.output, "executor.json"), "utf8"));
  expect(Object.keys(configuration).sort()).toEqual(["configuration", "configurationDigest", "maxCallsLimit"]);
  expect(configuration.maxCallsLimit).toBe(24);
  // The executor budget stays the study's exact slot count; the limit only admits larger studies.
  expect(configuration.configuration.maxCalls).toBe(12);
  expect(JSON.parse(await readFile(join(explicit.output, "intent.json"), "utf8")).maxCalls).toBe(12);
  const transport = JSON.parse(await readFile(join(explicit.output, "gateway.json"), "utf8"));
  expect(Object.keys(transport).sort()).toEqual(["cancelled", "configuration", "configurationDigest", "observations"]);
  expect(transport.observations).toHaveLength(12);

  const implicit = await fixture();
  expect((await implicit.run()).exitCode).toBe(0);
  expect(Object.keys(JSON.parse(await readFile(join(implicit.output, "executor.json"), "utf8"))).sort()).toEqual(["configuration", "configurationDigest"]);

  // An unparseable, out-of-range, or too-small budget fails before any archive exists.
  for (const value of ["abc", "0", "401", "12.0", "6", " 12", ""]) {
    const rejected = await fixture();
    const outcome = await rejected.run(undefined, { ALGAL_LAB_GATEWAY_MAX_CALLS: value });
    expect(outcome.exitCode).not.toBe(0);
    expect(outcome.stderr).toContain("ALGAL_LAB_GATEWAY_MAX_CALLS");
    await expect(access(rejected.output)).rejects.toThrow();
  }
});
