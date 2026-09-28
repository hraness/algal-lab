import { expect, test } from "bun:test";
import { MemoryStore, digestCanonical, parseTaskDefinition, runTask, type JsonValue } from "@hraness/algal";
import { annotationTemplate, freezeCorpus, importCapturedCorpus } from "./corpus";
import { compareTextbutlerTasks } from "./study";

async function syntheticCorpus(count = 3) {
  const task = parseTaskDefinition({ contract: "algal.task.v1", key: "organism:textbutler-respond", name: "Synthetic Textbutler fixture", inputs: { context: "json" },
    output: { name: "result", contract: { kind: "json", schema: { type: "object" } } }, instructions: "Synthetic decision task; not production Textbutler guidance.",
    budgets: { maxSteps: 4, maxAgentCalls: 1, maxWork: 200_000, maxContextBytes: 16_384, maxOutputBytes: 8192, maxDepth: 0 } });
  const groups = [], cases = [];
  for (let n = 0; n < count; n++) {
    const run = await runTask({ task, args: { context: { message: `Synthetic request ${n}` } }, store: new MemoryStore(), executors: [{ id: "synthetic", async execute() { return { respond: true, confidence: 1, actions: [] }; } }] });
    const sourceId = digestCanonical({ syntheticGroup: n }), observed = { manifest: run.compilation.manifest, receipt: run.receipt, output: run.outputs.result! };
    groups.push({ sourceId, revision: 0, stateDigest: digestCanonical({ synthetic: n }), baseTask: task });
    cases.push({ id: run.receipt.digest, sourceId, capturedAt: n, sourceDigest: digestCanonical(observed as unknown as JsonValue), observed });
  }
  const body = { contract: "textbutler.observed-task-cases.v1", origin: "private-local-journal", labels: "absent", groups, cases, omitted: 0 };
  return importCapturedCorpus({ ...body, digest: digestCanonical(body as unknown as JsonValue) });
}
test("capture replay, independent labels and group freezing remain distinct gates", async () => {
  const corpus = await syntheticCorpus(), annotations = annotationTemplate(corpus);
  const partitions = corpus.groups.map((g, i) => ({ sourceId: g.sourceId, split: ["train", "validation", "holdout"][i] }));
  expect(() => freezeCorpus(corpus, annotations, partitions)).toThrow("actual annotation source");
  annotations.reviewer = { kind: "independent-reviewer", reference: "synthetic-test-reviewer" };
  expect(() => freezeCorpus(corpus, annotations, partitions)).toThrow("three conversation groups");
  for (const label of annotations.cases) { label.decision = "respond"; label.rationale = "Synthetic explicit request"; }
  const frozen = freezeCorpus(corpus, annotations, partitions);
  expect(frozen.cases).toHaveLength(3); expect(frozen.excludedUnknown).toBe(0);
  const study = await compareTextbutlerTasks({ baseTask: corpus.groups[0]!.baseTask, frozen,
    executors: [{ id: "synthetic-only", async execute() { return { respond: true, confidence: 1, actions: [] }; } }] });
  expect(study.comparison.comparable).toBe(true); expect(study.artifact).not.toBeNull();
  expect(study.fixed.report.status).toBe("complete"); expect(study.labeled.report.status).toBe("complete");
  const changed = structuredClone(corpus); changed.cases[0]!.observed.output = { respond: false };
  const { digest: _old, ...body } = changed; changed.digest = digestCanonical(body as unknown as JsonValue);
  await expect(importCapturedCorpus(changed)).rejects.toThrow("record changed");
});
test("two groups and duplicate/cross-source annotation claims cannot fabricate a holdout", async () => {
  const corpus = await syntheticCorpus(2), annotations = annotationTemplate(corpus);
  annotations.reviewer = { kind: "owner", reference: "synthetic-owner" };
  for (const label of annotations.cases) { label.decision = "respond"; label.rationale = "Synthetic question"; }
  const partitions = corpus.groups.map((g, i) => ({ sourceId: g.sourceId, split: ["train", "holdout"][i] }));
  expect(() => freezeCorpus(corpus, annotations, partitions)).toThrow("three conversation groups");
  annotations.cases[1] = { ...annotations.cases[0]! };
  expect(() => freezeCorpus(corpus, annotations, partitions)).toThrow("annotation");
});
