import { afterEach, expect, test } from "bun:test";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { checkProofs, proofFiles, proofPlan, PROOF_PINS, toolReadiness } from "./tools";
import { encode, sha256 } from "./datasets";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true }))); });

test("proof setup uses the CI source pins and exact local destinations", async () => {
  const workflow = await readFile(new URL("../../.github/workflows/check.yml", import.meta.url), "utf8");
  expect(workflow).toContain(PROOF_PINS.cadical);
  expect(workflow).toContain(PROOF_PINS.lrat);
  const plan = proofPlan("/tmp/foundation path", "/repo", 2, "darwin");
  expect(plan.steps.find(step => step.name === "cadical-source-identity")?.expected).toBe(PROOF_PINS.cadical);
  expect(plan.environment.CADICAL_LIBRARY).toBe("/tmp/foundation path/native/libcadical.dylib");
  expect(plan.steps.find(step => step.name === "cadical-build")?.argv).toEqual(["make", "-j2"]);
  expect(plan.steps.some(step => step.name === "native-controls")).toBe(true);
  expect(plan.steps.some(step => step.name === "proof-controls")).toBe(true);
  expect(() => proofPlan("/tmp/tools", "/repo", 1000, "linux")).toThrow("jobs");
  expect(() => proofPlan("/tmp/tools", "/repo", 2, "win32")).toThrow("Linux or macOS");
});

test("toolchain checking binds recorded files, environment, platform, and closed fields", async () => {
  const out = await mkdtemp(join(tmpdir(), "algal-toolchain-test-")); roots.push(out);
  const files: Record<string, string> = {};
  for (const name of proofFiles()) {
    await mkdir(dirname(join(out, name)), { recursive: true });
    await writeFile(join(out, name), "fixture only"); files[name] = sha256("fixture only");
  }
  const manifest = { contract: "algal.proof-tools.v1", pins: PROOF_PINS, platform: process.platform, architecture: process.arch, files, controls: ["native-controls", "proof-controls"], setupSource: "a".repeat(64) };
  const path = join(out, "toolchain.json");
  await writeFile(path, encode(manifest));
  expect((await checkProofs(out)).verified).toBe(true);
  await writeFile(join(out, "environment.json"), "tampered");
  await expect(checkProofs(out)).rejects.toThrow("environment.json");
  await writeFile(path, encode({ ...manifest, platform: "unknown" }));
  await expect(checkProofs(out)).rejects.toThrow("platform");
  await writeFile(path, encode({ ...manifest, command: "no" }));
  await expect(checkProofs(out)).rejects.toThrow("unknown field");
});

test("readiness distinguishes available tools from an unqualified optional profile", async () => {
  const report = await toolReadiness(() => null);
  expect(report.coreReady).toBe(false);
  expect(report.profiles.allocation).toBe(false);
  expect(report.profiles.nativeProofBuild).toBe(false);
  expect(report.profiles.otpComparison).toBe(false);
  expect(report.liveProviders).toBe("not checked or activated");
});
