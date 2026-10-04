import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { doctor } from "../discovery/agenda";
import { object } from "../contracts";
import { boundedFile, encode, requireNewDirectory, sha256 } from "./datasets";

export const PROOF_PINS = { cadical: "c60730422e758ef1cebe7aeddf2dda31c996bf04", lrat: "b30f400f4ee5c32b77ee566a7c006081b521534f" } as const;
export const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const SPECS = [
  { id: "python", argv: ["python3", "--version"], neededFor: "allocation and proof controls" },
  { id: "git", argv: ["git", "--version"], neededFor: "source checkouts" },
  { id: "gh", argv: ["gh", "--version"], neededFor: "optional pinned proof source download" },
  { id: "cc", argv: ["cc", "--version"], neededFor: "optional proof checker build" },
  { id: "cxx", argv: ["c++", "--version"], neededFor: "optional SAT solver build" },
  { id: "make", argv: ["make", "--version"], neededFor: "optional SAT solver build" },
  { id: "elixir", argv: ["elixir", "--version"], neededFor: "optional OTP host comparison (1.18+)" },
];
function probe(argv: string[]): string | null {
  const result = spawnSync(argv[0]!, argv.slice(1), { encoding: "utf8", timeout: 10000, maxBuffer: 8192 });
  return result.status === 0 ? `${result.stdout}${result.stderr}`.trim().slice(0, 1000) : null;
}
export async function toolReadiness(inspect: (argv: string[]) => string | null = probe) {
  const core = await doctor();
  const tools = SPECS.map(tool => ({ ...tool, version: inspect(tool.argv) }));
  const has = (id: string) => tools.some(tool => tool.id === id && tool.version !== null);
  const python = tools.find(tool => tool.id === "python")!.version?.match(/Python (\d+)\.(\d+)/);
  const pythonReady = Boolean(python && (Number(python[1]) > 3 || Number(python[1]) === 3 && Number(python[2]) >= 10));
  const elixir = tools.find(tool => tool.id === "elixir")!.version?.match(/Elixir (\d+)\.(\d+)/);
  const elixirReady = Boolean(elixir && (Number(elixir[1]) > 1 || Number(elixir[1]) === 1 && Number(elixir[2]) >= 18));
  return { contract: "algal.foundation.readiness.v1", coreReady: core.ready && pythonReady, bun: core.bun, tools,
    profiles: { publicIntentData: core.ready, allocation: pythonReady, nativeProofBuild: pythonReady && ["git", "gh", "cc", "cxx", "make"].every(has), otpComparison: elixirReady },
    liveProviders: "not checked or activated", limits: "Tool availability is not scientific qualification. Native tools require setup plus check-proofs; Elixir availability does not qualify the OTP experiment. Lean and extra Python packages are not required by these profiles." };
}
type Step = { name: string; argv: string[]; cwd: string; expected?: string };
export function proofPlan(out: string, root: string, jobs: number, platform = process.platform) {
  if (!Number.isInteger(jobs) || jobs < 1 || jobs > 4) throw new Error("jobs must be 1..4");
  if (platform !== "darwin" && platform !== "linux") throw new Error("proof setup supports Linux or macOS");
  const cadical = join(out, "cadical-source"), lrat = join(out, "lrat-source");
  const environment = { CADICAL_LIBRARY: join(out, "native", platform === "darwin" ? "libcadical.dylib" : "libcadical.so"), CADICAL_BINARY: join(cadical, "build", "cadical"), LRAT_TRIM: join(out, "lrat-trim"), SELECTOR_INDEPENDENT_CENSUS: join(out, "independent-census.json") };
  const degree = "research/spikes/moonshot-r310/degree_six", fixed = "research/spikes/moonshot-r310/fixed_remainder";
  const steps: Step[] = [
    { name: "cadical-download", argv: ["gh", "repo", "clone", "arminbiere/cadical", cadical, "--", "--no-checkout"], cwd: out },
    { name: "cadical-checkout", argv: ["git", "checkout", "--detach", PROOF_PINS.cadical], cwd: cadical },
    { name: "cadical-source-identity", argv: ["git", "rev-parse", "HEAD"], cwd: cadical, expected: PROOF_PINS.cadical },
    { name: "cadical-configure", argv: ["./configure", "-fPIC"], cwd: cadical },
    { name: "cadical-build", argv: ["make", `-j${jobs}`], cwd: cadical },
    { name: "cadical-version", argv: [environment.CADICAL_BINARY, "--version"], cwd: out, expected: "3.0.1" },
    { name: "cadical-link", argv: ["python3", join(root, degree, "native.py"), join(cadical, "build", "libcadical.a"), join(out, "native")], cwd: root },
    { name: "lrat-download", argv: ["gh", "repo", "clone", "arminbiere/lrat-trim", lrat, "--", "--no-checkout"], cwd: out },
    { name: "lrat-checkout", argv: ["git", "checkout", "--detach", PROOF_PINS.lrat], cwd: lrat },
    { name: "lrat-source-identity", argv: ["git", "rev-parse", "HEAD"], cwd: lrat, expected: PROOF_PINS.lrat },
    { name: "lrat-build", argv: ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", join(lrat, "lrat-trim.c"), "-o", environment.LRAT_TRIM], cwd: out },
    { name: "independent-census", argv: ["python3", join(root, fixed, "independent_cover.py"), "--output", environment.SELECTOR_INDEPENDENT_CENSUS], cwd: root },
    { name: "native-controls", argv: ["python3", "-m", "unittest", "discover", "-s", degree, "-p", "test_*.py", "-v"], cwd: root },
    { name: "proof-controls", argv: ["python3", "-m", "unittest", "discover", "-s", fixed, "-p", "test_*.py", "-v"], cwd: root },
  ];
  return { environment, steps };
}
async function command(step: Step, environment: Record<string, string>) {
  return new Promise<{ code: number; output: string; failure: string | null }>(resolve => {
    const child = spawn(step.argv[0]!, step.argv.slice(1), { cwd: step.cwd, env: { ...process.env, ...environment, GIT_TERMINAL_PROMPT: "0", GH_PROMPT_DISABLED: "1" }, detached: true, stdio: ["ignore", "pipe", "pipe"] });
    const chunks: Buffer[] = [];
    let size = 0, failure: string | null = null;
    const stop = (reason: string) => {
      failure = reason;
      if (child.pid) { try { process.kill(-child.pid, "SIGKILL"); } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ESRCH") failure = "owned process cleanup failed"; } }
    };
    const timer = setTimeout(() => stop("command exceeded ten-minute limit"), 600000);
    const interrupt = () => stop("setup interrupted; partial outputs retained");
    process.once("SIGINT", interrupt); process.once("SIGTERM", interrupt);
    const collect = (chunk: Buffer) => { size += chunk.length; if (size > 4_000_000) stop("command output exceeded bound"); else chunks.push(chunk); };
    child.stdout.on("data", collect); child.stderr.on("data", collect);
    child.on("error", () => { failure = "could not start required tool"; });
    child.on("close", code => {
      clearTimeout(timer); process.removeListener("SIGINT", interrupt); process.removeListener("SIGTERM", interrupt);
      resolve({ code: code ?? 1, output: Buffer.concat(chunks).toString("utf8"), failure });
    });
  });
}
export async function setupProofs(output: string, jobs: number) {
  const out = resolve(output), plan = proofPlan(out, ROOT, jobs);
  const setupSource = sha256(await readFile(new URL("./tools.ts", import.meta.url)));
  await requireNewDirectory(out);
  const readiness = await toolReadiness();
  if (!readiness.profiles.nativeProofBuild) throw new Error("proof build prerequisites missing; run foundation doctor");
  await mkdir(out, { mode: 0o700 });
  await writeFile(join(out, "intent.json"), encode({ contract: "algal.proof-tools.intent.v1", pins: PROOF_PINS, plan, tools: readiness.tools }), { flag: "wx", mode: 0o600 });
  for (const step of plan.steps) {
    console.error(`proof tools: ${step.name}`);
    const result = await command(step, plan.environment);
    await writeFile(join(out, `${step.name}.log`), result.output, { flag: "wx", mode: 0o600 });
    if (result.code !== 0 || result.failure || step.expected !== undefined && result.output.trim() !== step.expected) throw new Error(`${step.name} failed; inspect its retained log in the output directory`);
    if (["native-controls", "proof-controls"].includes(step.name) && /skipped[=\s]/i.test(result.output)) throw new Error(`${step.name} skipped controls; setup is not qualified`);
  }
  await writeFile(join(out, "environment.json"), encode(plan.environment), { flag: "wx", mode: 0o600 });
  const files: Record<string, string> = {};
  for (const file of proofFiles()) files[file] = sha256(await boundedFile(join(out, file), 128_000_000));
  if (sha256(await readFile(new URL("./tools.ts", import.meta.url))) !== setupSource) throw new Error("setup source changed during build; preserve the partial output");
  const body = { contract: "algal.proof-tools.v1", pins: PROOF_PINS, platform: process.platform, architecture: process.arch, files, controls: ["native-controls", "proof-controls"], setupSource };
  await writeFile(join(out, "toolchain.json"), encode(body), { flag: "wx", mode: 0o600 });
  return { ready: true, digest: sha256(encode(body)), environment: plan.environment, limits: "Locally built and control-tested tools, not a new research run or a proof of any new claim." };
}
export function proofFiles(): string[] {
  return ["cadical-source/build/cadical", "cadical-source/build/libcadical.a", process.platform === "darwin" ? "native/libcadical.dylib" : "native/libcadical.so", "lrat-trim", "independent-census.json", "intent.json", "environment.json", "native-controls.log", "proof-controls.log"];
}
export async function checkProofs(output: string) {
  const out = resolve(output);
  const manifest = object(JSON.parse((await boundedFile(join(out, "toolchain.json"), 10000)).toString("utf8")) as unknown, ["contract", "pins", "platform", "architecture", "files", "controls", "setupSource"], "toolchain");
  if (manifest.contract !== "algal.proof-tools.v1" || encode(manifest.pins) !== encode(PROOF_PINS) || manifest.platform !== process.platform || manifest.architecture !== process.arch || typeof manifest.setupSource !== "string" || !/^[a-f0-9]{64}$/.test(manifest.setupSource) || encode(manifest.controls) !== encode(["native-controls", "proof-controls"])) throw new Error("proof toolchain identity or platform mismatch");
  const expected = proofFiles();
  const files = object(manifest.files, expected, "toolchain files");
  for (const file of expected) if (sha256(await boundedFile(join(out, file), 128_000_000)) !== files[file]) throw new Error(`toolchain file changed: ${file}`);
  return { verified: true, digest: sha256(encode(manifest)), environment: proofPlan(out, ROOT, 1).environment, limits: "Checks recorded local build identities, not independent binary provenance or a new execution of the control tests." };
}
