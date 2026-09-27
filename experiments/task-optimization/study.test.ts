import { expect, test } from "bun:test";
import { MemoryStore, compileTask } from "@hraness/algal";
import { ARMS, definition, runArm, scriptedExecutor, studyCases } from "./study";

test("seed changes demonstration order without changing held-out inputs or labels", () => {
  const a = studyCases(11), b = studyCases(23);
  expect(a.filter(row => row.split === "holdout")).toEqual(b.filter(row => row.split === "holdout"));
  expect(a.filter(row => row.split === "train").map(row => row.id)).not.toEqual(b.filter(row => row.split === "train").map(row => row.id));
  expect(compileTask(definition()).manifest.cells.every(cell => ["input", "agent"].includes(cell.kind))).toBe(true);
});

test("four study arms freeze a deployable program and retain all receipts without paid calls", async () => {
  for (const arm of ARMS) {
    const store = new MemoryStore();
    const result = await runArm(arm, 11, store, scriptedExecutor());
    expect(result.metrics.cases).toBe(12);
    expect(result.metrics.invalid).toBe(0);
    expect(result.calls).toBeGreaterThan(0);
    expect(compileTask(result.frozenTask).manifestDigest).toBe(result.selectedManifest);
    const report = result.report;
    const budget = "status" in report ? report.budget : report.budget!;
    expect(budget.charged.attempts).toBe(result.calls);
    expect(budget.runs.length).toBe(result.calls);
  }
}, 20_000);
