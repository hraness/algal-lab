import { afterEach, expect, test } from "bun:test";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Executor } from "@hraness/algal";
import { digest, readJsonFile } from "./artifacts";
import { json } from "./contracts";
import { comparisonStudies, liveCallBudget, parseComparisonPlan, runComparison, verifyComparison, type ComparisonReport } from "./comparison";
import { primedProposal } from "./researcher";

const directories: string[] = [];
afterEach(async () => { for (const directory of directories.splice(0)) await rm(directory, { recursive: true, force: true }); });
async function location(): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), "algal-lab-comparison-"));
  directories.push(directory);
  return join(directory, "run");
}

const plan = {
  contract: "algal.lab.comparison-plan.v1", name: "small-comparison", replicateSeeds: [7, 23, 41, 59], researchers: 2, rounds: 2, primedDesigns: 1,
  primary: { nodes: 6, edges: 7, failureSteps: 2 }, transferRegimes: [{ nodes: 7, edges: 9, failureSteps: 2 }],
  discoverySeeds: [1, 2], holdoutSeeds: [3, 4], margin: 0.02,
};

test("plan admission bounds seeds, oracle budgets, margins, and chunking", () => {
  const parsed = parseComparisonPlan(plan);
  expect(parsed.name).toBe("small-comparison");
  expect(comparisonStudies(parsed, ["adaptive", "random"]).map((d) => d.id)).toEqual(["adaptive-0", "random-0"]);
  expect(liveCallBudget(parsed)).toBe(4 * 3 * 2 * (2 + 1));
  const sixteen = { ...plan, replicateSeeds: Array.from({ length: 16 }, (_, i) => 100 + i) };
  expect(comparisonStudies(parseComparisonPlan(sixteen), ["adaptive", "random", "live"]).map((d) => d.id)).toEqual(["adaptive-0", "adaptive-1", "random-0", "random-1", "live-0", "live-1"]);
  expect(() => parseComparisonPlan({ ...plan, replicateSeeds: [1, 2, 3] })).toThrow("4..16");
  expect(() => parseComparisonPlan({ ...plan, replicateSeeds: [1, 2, 3, 3] })).toThrow("repeated");
  expect(() => parseComparisonPlan({ ...plan, primary: { nodes: 11, edges: 12, failureSteps: 2 } })).toThrow("ten nodes");
  expect(() => parseComparisonPlan({ ...plan, margin: 0 })).toThrow("margin");
  expect(() => parseComparisonPlan({ ...plan, primedDesigns: 0 })).toThrow("primedDesigns");
  expect(() => parseComparisonPlan({ ...plan, name: "Bad Name" })).toThrow("slug");
  expect(() => parseComparisonPlan({ ...plan, transferRegimes: [plan.primary] })).toThrow("must differ");
});

test("scripted comparison runs both control arms, verifies offline, and reports paired contrasts", async () => {
  const directory = await location();
  const report = await runComparison(plan, directory);
  expect(report.arms).toEqual(["adaptive", "random"]);
  expect(report.rows).toHaveLength(2 * 4 * 3);
  expect(report.controls).toEqual({ allSlotsRetained: true, primedIdenticalAcrossConditions: true, primedIdenticalAcrossArms: true, randomIgnoresSharing: true,
    scriptedIgnoresMessages: true, counterbalanced: true, transferBudgetsHonored: true, championsSelectedBeforeHoldout: true });
  expect(report.contrasts).toHaveLength(2 * 2 * 3);
  expect(report.armContrasts).toHaveLength(2 * 3 * 1);
  expect(report.armContrasts.every((c) => c.contrast === "adaptive-minus-random")).toBe(true);
  for (const contrast of report.contrasts) {
    expect(contrast.inference.count).toBe(4);
    expect(contrast.inference.bootstrap.lower).toBeLessThanOrEqual(contrast.inference.mean);
    expect(contrast.inference.bootstrap.upper).toBeGreaterThanOrEqual(contrast.inference.mean);
  }
  // Random search ignores sharing: its sharing contrasts are exactly zero everywhere.
  for (const contrast of report.contrasts.filter((c) => c.arm === "random")) {
    expect(contrast.inference.mean).toBe(0);
    expect(contrast.inference.verdict).toBe("within-margin");
  }
  for (const row of report.rows) {
    expect(row.bestPrimedExactAuc).toBeGreaterThan(0);
    // Champions are selected on the discovery mean (random and targeted), so the exact random AUC may fall below the primed design's.
    if (row.championExactAuc !== null) expect(row.improvementOverPrimed).toBe(row.championExactAuc - row.bestPrimedExactAuc);
    expect(row.transfers).toHaveLength(1);
    expect(row.transfers[0]!.regime).toEqual(plan.transferRegimes[0]!);
  }
  const primedPerSeed = new Map<number, number>();
  for (const row of report.rows) primedPerSeed.set(row.replicate, row.bestPrimedExactAuc);
  expect(report.rows.every((row) => primedPerSeed.get(row.replicate) === row.bestPrimedExactAuc)).toBe(true);
  expect(report.references).toHaveLength(2);
  expect(report.references[0]!.exactRandomAuc).toBeLessThanOrEqual(report.references[0]!.ceiling);
  const rendered = await readFile(join(directory, "report.md"), "utf8");
  expect(rendered).toContain("# small-comparison");
  expect(rendered).toContain("not model evidence");
  expect(rendered).toContain("## Transfer");
  const verified = await verifyComparison(directory);
  expect(verified).toMatchObject({ ok: true, studies: 2, rows: 24 });
  const envelope = await readJsonFile(join(directory, "comparison.json")) as { report: ComparisonReport; digest: string };
  expect(String(envelope.digest)).toBe(String(verified.reportDigest));
  expect(digest(envelope.report)).toBe(verified.reportDigest);
  expect(envelope.report.plan).toEqual(parseComparisonPlan(plan));
  // Tampering with a verdict or an underlying study is detected.
  const tampered = json({ ...envelope.report, controls: { ...envelope.report.controls, randomIgnoresSharing: false } });
  await writeFile(join(directory, "comparison.json"), JSON.stringify({ report: tampered, digest: digest(tampered) }));
  await expect(verifyComparison(directory)).rejects.toThrow("differs from reproduced analysis");
  await writeFile(join(directory, "comparison.json"), JSON.stringify({ report: envelope.report, digest: envelope.digest }));
  const frozen = await readJsonFile(join(directory, "plan.json")) as { plan: unknown; arms: string[] };
  await writeFile(join(directory, "plan.json"), JSON.stringify({ ...frozen, arms: ["adaptive", "random", "live"] }));
  await expect(verifyComparison(directory)).rejects.toThrow();
}, 120000);

test("a live arm is paired against both controls and a hand-picked executor cannot pose as a control", async () => {
  const directory = await location();
  const fixed: Executor = { id: "fixed-design", capabilities: { effects: ["agent"] }, cacheable: false, retryable: false,
    execute: async (request) => {
      const context = ((request.context as { inputs: { context: unknown } }).inputs).context as { replicate: number; researcher: number; nodes: number; edges: number };
      return json(primedProposal({ ...context, replicate: context.replicate + 1000 } as never, 0));
    } };
  const report = await runComparison({ ...plan, transferRegimes: [] }, directory, { executor: fixed });
  expect(report.arms).toEqual(["adaptive", "random", "live"]);
  expect(report.rows.filter((r) => r.arm === "live")).toHaveLength(12);
  expect(report.armContrasts.map((c) => c.contrast).sort()).toEqual([...Array(3).fill("adaptive-minus-random"), ...Array(3).fill("live-minus-adaptive"), ...Array(3).fill("live-minus-random")].sort());
  expect(report.controls.primedIdenticalAcrossArms).toBe(true);
  await expect(verifyComparison(directory)).resolves.toMatchObject({ ok: true, studies: 3 });
  // Relabel the live study as the adaptive control: verification recomputes the scripted policy and rejects it.
  const live = await readJsonFile(join(directory, "studies", "live-0", "study.json")) as { report: Record<string, unknown> };
  const forged = json({ ...live.report, backend: "scripted", protocol: { ...(live.report.protocol as object), name: "adaptive-0" } });
  await writeFile(join(directory, "studies", "adaptive-0", "study.json"), JSON.stringify({ report: forged, digest: digest(forged) }));
  await expect(verifyComparison(directory)).rejects.toThrow();
}, 120000);
