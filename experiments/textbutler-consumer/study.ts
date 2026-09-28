import { MemoryStore, digestCanonical, optimizeTask, type Executor, type JsonValue, type TaskDefinition } from "@hraness/algal";
import { buildEvaluatedTaskArtifact } from "@hraness/algal/task-artifact";
import { buildTaskWorkflowArchive, compareTaskWorkflows, parseTaskWorkflowConfig, verifyTaskWorkflowArchive } from "@hraness/algal/task-workflow";
import { RUBRIC, type freezeCorpus } from "./corpus";

/** Closed decision-only rubric. Reply semantics and personal preference need
 * independent review; neither output validity nor this scalar measures them. */
export const DECISION_SCORER = { contract: "algal.expr.v1" as const, program: ["and",
  ["eq", ["get", "outputs", "result", "respond"], ["get", "expect", "result", "respond"]],
  ["if", ["get", "expect", "result", "respond"], ["gte", ["get", "outputs", "result", "confidence"], 0.85],
    ["eq", ["get", "outputs", "result", "actions"], ["quote", []]]]] as JsonValue };

export async function compareTextbutlerTasks(options: { baseTask: TaskDefinition; frozen: ReturnType<typeof freezeCorpus>; executors: Executor[] }) {
  const { digest, ...body } = options.frozen;
  if (digest !== digestCanonical(body as unknown as JsonValue) || body.rubricDigest !== digestCanonical(RUBRIC)) throw Error("Frozen cases or rubric changed");
  const limits = { maxRounds: 0, maxCandidates: 2, maxExamples: 2, portfolioSize: 2, budget: { work: 10_000_000, runs: 32, attempts: 32 } };
  const cases = body.cases.map(row => ({ id: row.id, sourceId: row.sourceId, split: row.split, args: row.args,
    expect: { result: { respond: row.expected === "respond", confidence: row.expected === "respond" ? 1 : 0, actions: [] } } }));
  const run = async (strategy: "fixed" | "labeled") => {
    const config = parseTaskWorkflowConfig({ contract: "algal.task-workflow.v1", task: options.baseTask, strategy, cases, scorer: DECISION_SCORER, limits });
    const store = new MemoryStore(), report = await optimizeTask({ ...config, store, executors: options.executors });
    const archive = await buildTaskWorkflowArchive({ config, report, store });
    await verifyTaskWorkflowArchive(archive);
    return { archive, store, report };
  };
  // Fixed finite campaign ceilings cover both attempts; no automatic feedback
  // revisions, provider retries, dispatch or installation exists in this module.
  const fixed = await run("fixed"), labeled = await run("labeled"), comparison = compareTaskWorkflows(fixed.archive, labeled.archive);
  return { contract: "algal.lab.textbutler-comparison.v1", frozenDigest: digest, rubricDigest: body.rubricDigest, scorerDigest: digestCanonical(DECISION_SCORER),
    fixed: fixed.archive, labeled: labeled.archive, comparison,
    artifact: labeled.report.status === "complete" ? await buildEvaluatedTaskArtifact({ baseTask: options.baseTask, report: labeled.report, store: labeled.store }) : null,
    limitations: ["Decision score does not measure reply quality or satisfaction", "Labels remain claims by the named reviewer", "Conversation examples remain private and must not be installed across contacts", "No live sends or automatic adoption"] };
}
