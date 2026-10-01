import { expect, test } from "bun:test";
import { AGENT_CONTEXT_SELECT_TOOL, MemoryStore, compileTask, type JsonValue } from "@hraness/algal";
import { ARMS, CONTEXT_ARM, definition, runArm, scriptedExecutor, studyCases } from "./study";

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

test("opt-in exact context remains training-only, records selection and charges both calls", async () => {
  const base = scriptedExecutor();
  const seen: JsonValue[] = [];
  const store = new MemoryStore();
  const result = await runArm(CONTEXT_ARM, 11, store, { ...base, async execute(request, signal) {
    const inputs = request.context.inputs;
    if (inputs && typeof inputs === "object" && !Array.isArray(inputs) && inputs.feedback) seen.push(inputs);
    return base.execute(request, signal);
  } });
  expect(ARMS).not.toContain(CONTEXT_ARM);
  expect(seen).toHaveLength(2);
  const all = JSON.stringify(seen);
  for (const row of studyCases(11).filter(row => row.split !== "train")) expect(all).not.toContain(row.sourceId);
  expect(all).toContain("task instructions");
  expect(all).toContain("history");
  if (!("revisions" in result.report)) throw new Error("missing optimizer report");
  expect(result.report.revisions).toHaveLength(1);
  const revision = await store.getReceipt(result.report.revisions[0]!.receiptDigest);
  expect(revision).toMatchObject({ outcome: "complete", work: { agentCalls: 2 } });
  expect(JSON.stringify(revision)).toContain(AGENT_CONTEXT_SELECT_TOOL);
  const baseline = await runArm("feedback", 11, new MemoryStore(), scriptedExecutor());
  expect(result.calls).toBe(baseline.calls + 1);
  expect(result.metrics).toEqual(baseline.metrics);
}, 20_000);
