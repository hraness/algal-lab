import { expect, test } from "bun:test";
import { compileTask, digestCanonical, MemoryStore, type JsonValue, type TaskOptimizationReport } from "@hraness/algal";
import { runArm, scriptedExecutor, studyCases } from "./study";
import { buildKnowledge, FRESH_CORPUS, freshCases, guidanceTask, parseKnowledge, runRetention, selectRetention, verifyRetention, type Knowledge } from "./retention";

async function learned() {
  const source = await runArm("feedback", 11, new MemoryStore(), scriptedExecutor());
  const built = buildKnowledge(source.report, studyCases(11));
  if (!built.eligible) throw new Error(built.reason);
  return { source, knowledge: built.knowledge };
}
function rehash(value: Knowledge): Knowledge { const { digest: _digest, ...base } = value; return { ...base, digest: digestCanonical(base as unknown as JsonValue) }; }

test("retention chooses validation winner and real accepted feedback, while preserving authority and rollback", async () => {
  const { source, knowledge } = await learned();
  const report = source.report as TaskOptimizationReport;
  expect(compileTask(knowledge.retainedTask).manifestDigest).toBe(report.portfolio[0]!);
  expect(knowledge.lessons[0]!.text).toBe(report.candidates.find(row => row.stage === "feedback")!.task.instructions);
  expect(knowledge.originalLearningCost.attempts).toBeLessThan(knowledge.originalCampaignCost.attempts);
  expect(String(compileTask(knowledge.priorTask).taskDigest)).toBe(knowledge.parentTaskDigest);
  expect(guidanceTask(knowledge).examples).toEqual(knowledge.priorTask.examples);
  const changedAudit = structuredClone(report);
  changedAudit.result!.holdout.passed = 0;
  const { digest: _digest, ...body } = changedAudit;
  changedAudit.digest = digestCanonical(body as unknown as JsonValue);
  const second = buildKnowledge(changedAudit, studyCases(11));
  if (!second.eligible) throw new Error(second.reason);
  expect(second.knowledge.lessons).toEqual(knowledge.lessons);
  expect(second.knowledge.retainedTask).toEqual(knowledge.retainedTask);
});

test("knowledge refuses stale parents, extra authority, source leakage, and growth beyond budget", async () => {
  const { knowledge } = await learned();
  expect(() => parseKnowledge({ ...knowledge, runner: "sh" })).toThrow();
  expect(() => parseKnowledge(knowledge, "sha256:" + "0".repeat(64))).toThrow("stale");
  const authority = structuredClone(knowledge); authority.retainedTask.budgets.maxAgentCalls = 2;
  expect(() => parseKnowledge(rehash(authority))).toThrow("authority");
  const oversized = structuredClone(knowledge); oversized.lessons[0]!.text = "x".repeat(2049);
  expect(() => parseKnowledge(rehash(oversized))).toThrow("bound");
  const leak = structuredClone(knowledge); leak.lessons[0]!.sourceIds = ["not-training"];
  expect(() => parseKnowledge(rehash(leak))).toThrow("non-training");
  const corpus = [...structuredClone(FRESH_CORPUS)]; corpus[0] = { ...corpus[0]!, sourceId: knowledge.originalSourceIds[0]! };
  expect(() => freshCases(knowledge, corpus)).toThrow("overlaps");
});

test("no accepted revision is explicit ineligibility rather than invented knowledge", async () => {
  const { source } = await learned();
  const report = structuredClone(source.report) as TaskOptimizationReport;
  report.revisions = [];
  const { digest: _digest, ...body } = report; report.digest = digestCanonical(body as unknown as JsonValue);
  expect(buildKnowledge(report, studyCases(11)).eligible).toBe(false);
});

test("fresh validation freezes before audit and ties preserve a rollback program", async () => {
  const { knowledge } = await learned();
  let frozen = false, selected = false, sawAudit = false;
  const fixture = scriptedExecutor();
  const executor = { ...fixture, async execute(request: Parameters<typeof fixture.execute>[0], signal?: AbortSignal) {
    expect(frozen).toBe(true);
    const input = request.context.inputs as { message?: string };
    if (FRESH_CORPUS.some(row => row.split === "holdout" && row.message === input.message)) { expect(selected).toBe(true); sawAudit = true; }
    return fixture.execute(request, signal);
  } };
  const store = new MemoryStore();
  const result = await runRetention({ knowledge, store, executor,
    onFrozen: async () => { frozen = true; }, onSelected: async () => { selected = true; expect(sawAudit).toBe(false); } });
  expect(sawAudit).toBe(true);
  expect(result.selection.accepted).toBe(false);
  expect(result.selection.selected).toBe("fixed");
  expect(result.servingTask).toEqual(result.rollbackTask);
  expect(result.audits.map(row => row.metrics.cases)).toEqual([8, 8, 8]);
  expect(result.freshEvaluationCost.attempts).toBe(78);
  expect(selectRetention(result.validation)).toEqual(result.selection);
  expect((await verifyRetention(result, store)).ok).toBe(true);
  const tampered = structuredClone(result); tampered.audits[0]!.metrics = { ...tampered.audits[0]!.metrics, correct: 0 };
  const { digest: _digest, ...body } = tampered; tampered.digest = digestCanonical(body as unknown as JsonValue);
  await expect(verifyRetention(tampered, store)).rejects.toThrow("does not reproduce");
}, 20000);
