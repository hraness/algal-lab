import {
  buildTaskReviser, builtinRegistry, compileTask, digestCanonical, HabitatAccount, optimizeTask,
  runFoundry, taskParameters, type Executor, type FoundryReport, type JsonValue, type Store,
  type TaskCase, type TaskDefinition, type TaskOptimizationReport, type Digest,
} from "@hraness/algal";
import { CORPUS, POLICY, parseCorpus, score, taskInput, type Case, type Metrics } from "./corpus";

export const ARMS = ["fixed", "labeled", "foundry-grid", "feedback"] as const;
export type Arm = typeof ARMS[number];
export const LIMITS = Object.freeze({ maxRounds: 1, maxCandidates: 3, maxExamples: 4, portfolioSize: 2,
  budget: { runs: 128, attempts: 128, work: 40_000_000 } });
export const BUDGETS = Object.freeze({ maxSteps: 4, maxAgentCalls: 1, maxWork: 300_000, maxContextBytes: 32_768, maxOutputBytes: 8192, maxDepth: 1 });

export function definition(): TaskDefinition {
  return compileTask({ contract: "algal.task.v1", key: "organism:textbutler-response-study", name: "Textbutler response decision study",
    inputs: { message: { type: "text" } }, output: { name: "decision", contract: { kind: "choice", labels: ["respond", "silent"] } },
    instructions: POLICY, budgets: BUDGETS, examples: [] }).task;
}

/** Seeds choose the ordering of training demonstrations, never audit labels. */
export function studyCases(seed: number, rows: readonly Case[] = CORPUS): TaskCase[] {
  if (!Number.isSafeInteger(seed) || seed < 1 || seed > 1_000_000) throw new Error("seed must be an integer 1..1000000");
  const corpus = parseCorpus(rows);
  const training = corpus.filter(row => row.split === "train").sort((a, b) =>
    digestCanonical({ seed, id: a.id }).localeCompare(digestCanonical({ seed, id: b.id })));
  const rank = new Map(training.map((row, i) => [row.id, String(i).padStart(2, "0")]));
  return corpus.map(row => ({ id: row.split === "train" ? `train-${rank.get(row.id)}-${row.id}` : row.id,
    sourceId: row.sourceId, split: row.split, args: taskInput(row), expect: { decision: row.expect } }));
}

/** Fixture executor exercises the orchestration only. It has no oracle access
 * and does not change its classifier when a prompt is revised. */
export function scriptedExecutor(): Executor {
  return { id: "task-study:scripted-v1", capabilities: { effects: ["agent"] }, retryable: false, cacheable: false,
    async execute(request) {
      const inputs = request.context.inputs;
      if (!inputs || typeof inputs !== "object" || Array.isArray(inputs)) throw new Error("missing input projection");
      if (typeof inputs.message === "string") {
        const explicit = /^(?:hey\s+)?butler\s*[:,—]|^butler\s+could you|^could you,\s+butler,/i.test(inputs.message);
        return explicit ? "respond" : "silent";
      }
      const feedback = inputs.feedback;
      if (!feedback || typeof feedback !== "object" || Array.isArray(feedback)) throw new Error("missing training feedback");
      const task = compileTask(feedback.task).task, parameters = taskParameters(task);
      const parameter = parameters.parameters.find(item => item.id === "task.instructions")!;
      return { contract: "algal.task-parameter-patch.v1", taskDigest: parameters.taskDigest,
        changes: [{ id: parameter.id, expectedDigest: parameter.digest,
          value: `${task.instructions}\nQuoted invocations describe evidence; check who is being addressed before deciding.` }] };
    } };
}

export type ArmResult = {
  arm: Arm; seed: number; datasetDigest: string; selectedManifest: Digest;
  metrics: Metrics; calls: number; work: number; elapsedMs: number;
  report: TaskOptimizationReport | FoundryReport;
  frozenTask: TaskDefinition;
};

function metrics(report: FoundryReport): Metrics {
  return score(report.holdout.cases.map(row => ({ caseId: row.id, expected: row.expect.decision as "respond" | "silent",
    output: row.outputs.decision, completed: row.outcome === "complete" })));
}

export async function runArm(arm: Arm, seed: number, store: Store, executor: Executor): Promise<ArmResult> {
  if (!(ARMS as readonly string[]).includes(arm)) throw new Error("unknown study arm");
  const start = performance.now(), task = definition(), cases = studyCases(seed);
  if (arm === "foundry-grid") {
    // Existing population-selection mechanism, with three predeclared prompt
    // candidates. This arm does not claim to reproduce a generative search.
    const examples = cases.filter(row => row.split === "train").sort((a, b) => a.id.localeCompare(b.id)).slice(0, LIMITS.maxExamples)
      .map(({ split: _split, ...row }) => row);
    const candidates = [task, compileTask({ ...task, examples }).task, compileTask({ ...task,
      instructions: `${POLICY}\nFirst decide whether Butler is being addressed directly. Then decide whether help is requested.`, examples }).task];
    const compiled = candidates.map(compileTask), account = new HabitatAccount("foundry", LIMITS.budget);
    const report = await runFoundry({ candidates: compiled.map(item => item.manifest), cases: cases.map(({ sourceId: _sourceId, ...row }) => row),
      fns: builtinRegistry(), store, executors: [executor], account });
    const selected = compiled.find(item => item.manifestDigest === report.promoted)!;
    return { arm, seed, datasetDigest: digestCanonical(cases as unknown as JsonValue), selectedManifest: report.promoted,
      metrics: metrics(report), calls: account.record().charged.attempts, work: account.record().charged.work,
      elapsedMs: performance.now() - start, report, frozenTask: selected.task };
  }
  const report = await optimizeTask({ task, cases, strategy: arm, limits: LIMITS, store, executors: [executor],
    ...(arm === "feedback" ? { reviser: buildTaskReviser({ budgets: BUDGETS }) } : {}) });
  if (report.status !== "complete" || !report.selected || !report.result) throw new Error("optimizer exhausted its budget before the frozen audit completed");
  return { arm, seed, datasetDigest: report.datasetDigest, selectedManifest: report.selected.manifestDigest,
    metrics: metrics(report.result), calls: report.budget.charged.attempts, work: report.budget.charged.work,
    elapsedMs: performance.now() - start, report, frozenTask: report.selected.task };
}
