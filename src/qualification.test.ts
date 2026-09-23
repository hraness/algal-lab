import { afterEach, expect, test } from "bun:test";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { digest } from "./artifacts";
import { exactRandomAuc } from "./oracle";
import { pairedSummary, parseQualificationPlan, referenceGraph, runQualification, verifyQualification } from "./qualification";

const roots: string[] = [];
afterEach(async () => { await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true }))); });
async function location() { const root = await mkdtemp(join(tmpdir(), "algal-qualification-test-")); roots.push(root); return join(root, "run"); }
const plan = { contract: "algal.lab.qualification-plan.v1" as const, name: "test", replicateSeeds: [107, 223], researchers: 2, rounds: 2,
  discoverySeeds: [41], holdoutSeeds: [1009], regimes: [{ name: "small", nodes: 5, edges: 5, failureSteps: 2 }] };

test("qualification bounds work and reject ambiguous or unbounded plans before writing", async () => {
  expect(parseQualificationPlan(plan)).toEqual(plan);
  for (const invalid of [
    { ...plan, unknown: true }, { ...plan, replicateSeeds: [1, 1] }, { ...plan, replicateSeeds: Array.from({ length: 17 }, (_, i) => i) },
    { ...plan, regimes: [{ ...plan.regimes[0], nodes: 11 }] }, { ...plan, rounds: 5 },
    { ...plan, regimes: [plan.regimes[0], plan.regimes[0]] }, { ...plan, discoverySeeds: [1009] },
    { ...plan, regimes: [{ ...plan.regimes[0], name: "../outside" }] },
  ]) expect(() => parseQualificationPlan(invalid)).toThrow();
  await expect(runQualification({ ...plan, researchers: 999 }, await location())).rejects.toThrow();
});

test("fixed references realize exact budgets and include a known optimal five-cycle", () => {
  const cycle = referenceGraph(5, 5);
  expect(exactRandomAuc(cycle, 3)).toBeCloseTo(0.65, 14);
  for (let nodes = 4; nodes <= 10; nodes++) for (let edges = nodes - 1; edges <= nodes * (nodes - 1) / 2; edges++) {
    const graph = referenceGraph(nodes, edges);
    expect(graph.edges).toHaveLength(edges);
  }
});

test("paired descriptions preserve null and negative outcomes without significance claims", () => {
  const result = pairedSummary("small", "a-minus-b", [-0.1, 0, 0.2, -0.3]);
  expect(result.count).toBe(4);
  expect(result.mean).toBeCloseTo(-0.05);
  expect([result.wins, result.ties, result.losses]).toEqual([1, 1, 2]);
  expect(result.differences).toEqual([-0.1, 0, 0.2, -0.3]);
  expect(() => pairedSummary("x", "y", [NaN])).toThrow();
});

test("qualification freezes inputs, compares matched controls, and independently reconstructs analysis", async () => {
  const directory = await location();
  const report = await runQualification(plan, directory);
  expect(report.studies).toHaveLength(2);
  expect(report.rows).toHaveLength(12);
  expect(report.controls).toEqual({ allAttemptsValid: true, randomIgnoresSharing: true, scriptedIgnoresMessages: true });
  expect(report.comparisons).toHaveLength(3);
  expect(report.rows.every((r) => r.attempts === 4 && r.selectedAttempt && r.exactRandomAuc! > 0)).toBe(true);
  expect(await verifyQualification(directory)).toMatchObject({ ok: true, studies: 2, attempts: 48, reportDigest: digest(report) });
  const before = await readFile(join(directory, "plan.json"), "utf8");
  await expect(runQualification(plan, directory)).rejects.toThrow();
  expect(await readFile(join(directory, "plan.json"), "utf8")).toBe(before);
  report.comparisons[0]!.mean = 0.123;
  await writeFile(join(directory, "qualification.json"), JSON.stringify({ report, digest: digest(report) }));
  await expect(verifyQualification(directory)).rejects.toThrow("differs from reproduced analysis");
}, 60000); // twelve scripted studies plus a full offline reconstruction; keep headroom for loaded CI hosts
