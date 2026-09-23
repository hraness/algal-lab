import { createHash } from "node:crypto";
import { mkdir, open, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { compileObjective, type CompiledObjective } from "../../scorer";
import { environmentFor, type FailureEnvironment } from "../../../src/heterogeneous";
import { mulberry32 } from "../../../src/network";
import { exactWeightedAuc } from "../../../src/oracle";
import {
  admitPolicy, choices, construct, fixedPairPolicy, fixedReliablePolicy, search,
  theoremStar, type Policy, type SearchKind, type SearchResult,
} from "./policy";
import protocol from "./protocol.json";

type Regime = typeof protocol.regimes[number];
type Case = { key: string; seed: number; regime: Regime; environment: FailureEnvironment; objective: CompiledObjective };
type Candidate = { index: number; generation: number; parent: number | null; policy: Policy; mean: number;
  cases: { case: string; result: SearchResult }[]; evaluations: number; failures: number };
type Training = { contract: string; protocolDigest: string; sourceDigests: Record<string, string>; candidates: Candidate[];
  selectedIndex: number; selectedPolicy: Policy; totalEvaluations: number; elapsedMs: number };
type Selection = { sourceDigests: Record<string, string>; selectedIndex: number; selectedPolicy: unknown; trainingDigest: string };
type ArmResult = { key: string; seed: number; regime: string; environment: FailureEnvironment; ceiling: number;
  arms: Record<string, { result: SearchResult; objectiveSelectionEvaluations: number; measurementEvaluations: number }> };

const directory = import.meta.dir;
const outputDirectory = join(directory, "runs", "v1");
const hash = (data: string): string => `sha256:${createHash("sha256").update(data).digest("hex")}`;
const average = (values: readonly number[]): number => values.reduce((a, b) => a + b, 0) / values.length;
const key = (policy: Policy): string => JSON.stringify(policy);
const rank = (a: Candidate, b: Candidate): number => b.mean - a.mean || (key(a.policy) < key(b.policy) ? -1 : key(a.policy) > key(b.policy) ? 1 : 0);
const modelSeed = (regime: Regime, seed: number): number => (seed ^ Math.imul(regime.edges, 0x85ebca77) ^ Math.imul(regime.nodes, 0x9e3779b1)) >>> 0;

async function identity(): Promise<{ protocolDigest: string; sourceDigests: Record<string, string> }> {
  const files = ["protocol.json", "policy.ts", "experiment.ts", "../../scorer.ts", "../../../src/network.ts", "../../../src/heterogeneous.ts", "../../../src/oracle.ts"];
  const sourceDigests: Record<string, string> = {};
  for (const file of files) sourceDigests[file] = hash(await readFile(join(directory, file), "utf8"));
  return { protocolDigest: sourceDigests["protocol.json"]!, sourceDigests };
}

async function save(name: string, data: unknown): Promise<void> {
  await mkdir(outputDirectory, { recursive: true });
  await writeFile(join(outputDirectory, name), `${JSON.stringify(data, null, 2)}\n`, { flag: "wx" });
}

function record(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`${label}: expected object`);
  return value as Record<string, unknown>;
}

function fields(value: Record<string, unknown>, expected: string[], label: string): void {
  const keys = Object.keys(value);
  if (keys.length !== expected.length || keys.some((key) => !expected.includes(key))) throw new Error(`${label}: unexpected fields`);
}

async function readBounded(name: string): Promise<{ text: string; value: Record<string, unknown> }> {
  const limit = 16 * 1024 * 1024;
  const file = await open(join(outputDirectory, name), "r");
  let text: string;
  try {
    const size = (await file.stat()).size;
    if (size > limit) throw new Error("archive exceeds 16 MiB");
    const buffer = Buffer.alloc(size + 1);
    const { bytesRead } = await file.read(buffer, 0, size + 1, 0);
    if (bytesRead !== size) throw new Error("archive changed or read was incomplete");
    text = buffer.subarray(0, bytesRead).toString("utf8");
  } finally { await file.close(); }
  const value: unknown = JSON.parse(text);
  let entries = 0;
  const inspect = (item: unknown, depth: number): void => {
    if (++entries > 250_000 || depth > 16) throw new Error("archive structure exceeds bounds");
    if (typeof item === "string" && item.length > 2048) throw new Error("archive string exceeds bounds");
    if (item && typeof item === "object") {
      const values = Object.values(item);
      if (values.length > 4096) throw new Error("archive collection exceeds bounds");
      for (const child of values) inspect(child, depth + 1);
    }
  };
  inspect(value, 0);
  return { text, value: record(value, name) };
}

function cases(seeds: number[], regimes: Regime[]): Case[] {
  return regimes.flatMap((regime) => seeds.map((seed) => {
    const environment = environmentFor(regime.nodes, seed);
    return { key: `${regime.key}:${seed}`, seed, regime, environment, objective: compileObjective(environment, regime.steps) };
  }));
}

function initialPolicies(next: () => number): Policy[] {
  const result: Policy[] = [
    fixedPairPolicy, fixedReliablePolicy,
    { minValue: 1, maxValue: 0, risk: 1, noise: 0.5, degree: 0, restart: 0 },
    { minValue: 1, maxValue: 0, risk: 1, noise: 0.5, degree: 1, restart: 16 },
    { minValue: 2, maxValue: 0, risk: 2, noise: 0.5, degree: 0.5, restart: 16 },
    { minValue: 1, maxValue: 1, risk: 2, noise: 1, degree: 0.5, restart: 8 },
  ];
  while (result.length < protocol.generationSize) {
    const policy = {} as Policy;
    for (const field of Object.keys(choices) as (keyof Policy)[]) policy[field] = choices[field][Math.floor(next() * choices[field].length)]!;
    result.push(policy);
  }
  return result;
}

function mutate(parent: Policy, next: () => number): Policy {
  const proposal = { ...parent };
  const fields = Object.keys(choices) as (keyof Policy)[];
  const mutations = next() < 0.5 ? 1 : 2;
  for (let count = 0; count < mutations; count++) {
    const field = fields[Math.floor(next() * fields.length)]!;
    const alternatives = choices[field].filter((value) => value !== proposal[field]);
    proposal[field] = alternatives[Math.floor(next() * alternatives.length)]!;
  }
  return admitPolicy(proposal);
}

function computeTraining(frozen: Awaited<ReturnType<typeof identity>>): Training {
  const started = performance.now();
  const development = cases(protocol.developmentSeeds, protocol.regimes.filter((regime) => regime.development));
  const next = mulberry32(protocol.evolutionSeed), candidates: Candidate[] = [];
  let proposals = initialPolicies(next).map((policy) => ({ policy, parent: null as number | null }));
  for (let generation = 0; candidates.length < protocol.policyCandidates; generation++) {
    for (const proposal of proposals) {
      const results = development.map((item) => ({ case: item.key,
        result: search("policy", proposal.policy, item.environment, item.regime.edges, modelSeed(item.regime, item.seed),
          protocol.deploymentEvaluations, item.objective.score) }));
      candidates.push({ index: candidates.length, generation, parent: proposal.parent, policy: proposal.policy,
        mean: average(results.map((item) => item.result.score)), cases: results,
        evaluations: results.reduce((sum, item) => sum + item.result.evaluations, 0),
        failures: results.reduce((sum, item) => sum + item.result.failures.length, 0) });
    }
    const elites = [...candidates].sort(rank).slice(0, protocol.eliteCount);
    console.log(JSON.stringify({ phase: "development", generation, policies: candidates.length, best: elites[0]!.mean, policy: elites[0]!.policy }));
    proposals = Array.from({ length: protocol.generationSize }, (_, index) => {
      const parent = elites[index % elites.length]!;
      return { policy: mutate(parent.policy, next), parent: parent.index };
    });
  }
  const selected = [...candidates].sort(rank)[0]!;
  return { contract: "algal.lab.policy-spike-training.v1", ...frozen, candidates,
    selectedIndex: selected.index, selectedPolicy: selected.policy,
    totalEvaluations: candidates.reduce((sum, candidate) => sum + candidate.evaluations, 0), elapsedMs: performance.now() - started };
}

async function train(): Promise<void> {
  const frozen = await identity();
  const training = computeTraining(frozen);
  const selected = training.candidates[training.selectedIndex]!;
  await save("training.json", training);
  await save("selection.json", { contract: "algal.lab.policy-spike-selection.v1", ...frozen,
    selectedIndex: selected.index, selectedPolicy: selected.policy, trainingDigest: hash(JSON.stringify(training)),
    totalDevelopmentEvaluations: training.totalEvaluations,
    statement: "Policy and source frozen after development, before heldout execution." });
  console.log(JSON.stringify({ phase: "selected", index: selected.index, policy: selected.policy, meanDevelopment: selected.mean,
    totalEvaluations: training.totalEvaluations, elapsedMs: training.elapsedMs }));
}

async function readSelection(frozen: Awaited<ReturnType<typeof identity>>): Promise<{ selectionText: string; policy: Policy; training: Training }> {
  const { text: selectionText, value: rawSelection } = await readBounded("selection.json");
  fields(rawSelection, ["contract", "protocolDigest", "sourceDigests", "selectedIndex", "selectedPolicy", "trainingDigest", "totalDevelopmentEvaluations", "statement"], "selection");
  if (rawSelection.contract !== "algal.lab.policy-spike-selection.v1" || rawSelection.protocolDigest !== frozen.protocolDigest
    || !Number.isInteger(rawSelection.selectedIndex) || typeof rawSelection.trainingDigest !== "string") throw new Error("invalid selection identity");
  const selection = rawSelection as unknown as Selection;
  if (JSON.stringify(selection.sourceDigests) !== JSON.stringify(frozen.sourceDigests)) throw new Error("sources changed after selection");
  const { value: rawTraining } = await readBounded("training.json");
  fields(rawTraining, ["contract", "protocolDigest", "sourceDigests", "candidates", "selectedIndex", "selectedPolicy", "totalEvaluations", "elapsedMs"], "training");
  if (rawTraining.contract !== "algal.lab.policy-spike-training.v1" || rawTraining.protocolDigest !== frozen.protocolDigest
    || JSON.stringify(rawTraining.sourceDigests) !== JSON.stringify(frozen.sourceDigests)
    || !Array.isArray(rawTraining.candidates) || rawTraining.candidates.length !== protocol.policyCandidates) throw new Error("invalid training identity");
  const caseCount = protocol.developmentSeeds.length * protocol.regimes.filter((regime) => regime.development).length;
  for (let index = 0; index < rawTraining.candidates.length; index++) {
    const candidate = record(rawTraining.candidates[index], "candidate");
    fields(candidate, ["index", "generation", "parent", "policy", "mean", "cases", "evaluations", "failures"], "candidate");
    if (candidate.index !== index || candidate.generation !== Math.floor(index / protocol.generationSize)
      || (candidate.parent !== null && (!Number.isInteger(candidate.parent) || (candidate.parent as number) < 0 || (candidate.parent as number) >= index))
      || typeof candidate.mean !== "number" || !Number.isFinite(candidate.mean) || candidate.mean < 0 || candidate.mean > 1
      || !Array.isArray(candidate.cases) || candidate.cases.length !== caseCount
      || candidate.evaluations !== caseCount * protocol.deploymentEvaluations
      || !Number.isInteger(candidate.failures) || (candidate.failures as number) < 0 || (candidate.failures as number) > (candidate.evaluations as number)) throw new Error("invalid training candidate");
    admitPolicy(candidate.policy);
  }
  const training = rawTraining as unknown as Training;
  if (hash(JSON.stringify(training)) !== selection.trainingDigest) throw new Error("training archive differs from selection");
  if (training.totalEvaluations !== protocol.policyCandidates * caseCount * protocol.deploymentEvaluations
    || rawSelection.totalDevelopmentEvaluations !== training.totalEvaluations) throw new Error("training evaluation count mismatch");
  const winner = [...training.candidates].sort(rank)[0]!;
  const policy = admitPolicy(selection.selectedPolicy);
  if (winner.index !== selection.selectedIndex || winner.index !== training.selectedIndex || key(winner.policy) !== key(policy)
    || key(training.selectedPolicy) !== key(policy)) throw new Error("selection does not match archived development winner");
  return { selectionText, policy, training };
}

function bootstrap(differences: number[]): { mean: number; interval95: [number, number]; wins: number; ties: number; losses: number; minimum: number; maximum: number } {
  const next = mulberry32(protocol.bootstrapSeed);
  const draws: number[] = [];
  for (let sample = 0; sample < protocol.bootstrapReplicates; sample++) {
    let total = 0;
    for (let index = 0; index < differences.length; index++) total += differences[Math.floor(next() * differences.length)]!;
    draws.push(total / differences.length);
  }
  draws.sort((a, b) => a - b);
  return { mean: average(differences), interval95: [draws[Math.floor(0.025 * draws.length)]!, draws[Math.floor(0.975 * draws.length)]!],
    wins: differences.filter((value) => value > 1e-12).length, ties: differences.filter((value) => Math.abs(value) <= 1e-12).length,
    losses: differences.filter((value) => value < -1e-12).length, minimum: Math.min(...differences), maximum: Math.max(...differences) };
}

function measureUnsearched(graph: ReturnType<typeof construct>, objective: CompiledObjective): SearchResult {
  const score = objective.score(graph);
  return { graph, score, evaluations: 1, duplicateProposals: 0, unchangedMutations: 0, acceptedImprovements: 0, acceptedWorse: 0,
    failures: [], initialScore: score, bestByEvaluation: [score] };
}

function runCase(item: Case, policy: Policy): { row: ArmResult; maxOracleDiscrepancy: number } {
  const arms: ArmResult["arms"] = {};
  let maxOracleDiscrepancy = 0;
  const definitions: { name: string; kind: SearchKind; policy: Policy }[] = [
    { name: "selected", kind: "policy", policy },
    { name: "random-search", kind: "random-search", policy: fixedPairPolicy },
    { name: "random-hill", kind: "random-hill", policy: fixedPairPolicy },
    { name: "star-hill", kind: "star-hill", policy: fixedPairPolicy },
    { name: "annealing", kind: "annealing", policy: fixedPairPolicy },
    { name: "fixed-pair", kind: "policy", policy: fixedPairPolicy },
    { name: "fixed-reliable", kind: "policy", policy: fixedReliablePolicy },
  ];
  for (const definition of definitions) {
    const result = search(definition.kind, definition.policy, item.environment, item.regime.edges,
      modelSeed(item.regime, item.seed), protocol.deploymentEvaluations, item.objective.score);
    arms[definition.name] = { result, objectiveSelectionEvaluations: result.evaluations, measurementEvaluations: 0 };
    // Independent original oracle checks each reported champion, including failures/repeats in search accounting.
    maxOracleDiscrepancy = Math.max(maxOracleDiscrepancy, Math.abs(result.score - exactWeightedAuc(result.graph, item.environment, item.regime.steps)));
  }
  arms["selected-zero-search"] = { result: measureUnsearched(construct(policy, item.environment, item.regime.edges,
    Math.floor(mulberry32(modelSeed(item.regime, item.seed))() * 0x1_0000_0000) >>> 0), item.objective), objectiveSelectionEvaluations: 0, measurementEvaluations: 1 };
  arms["star-zero-search"] = { result: measureUnsearched(theoremStar(item.environment, item.regime.edges), item.objective),
    objectiveSelectionEvaluations: 0, measurementEvaluations: 1 };
  return { row: { key: item.key, seed: item.seed, regime: item.regime.key, environment: item.environment, ceiling: item.objective.ceiling, arms }, maxOracleDiscrepancy };
}

async function evaluate(): Promise<void> {
  const started = performance.now();
  const frozen = await identity();
  const { selectionText, policy } = await readSelection(frozen);
  await save("heldout-start.json", { ...frozen, selectionDigest: hash(selectionText), statement: "Frozen pre-evaluation selection; no heldout-informed tuning permitted." });
  const heldout = cases(protocol.heldoutSeeds, protocol.regimes);
  const results: ArmResult[] = [];
  let maxOracleDiscrepancy = 0;
  for (const item of heldout) {
    const measured = runCase(item, policy);
    maxOracleDiscrepancy = Math.max(maxOracleDiscrepancy, measured.maxOracleDiscrepancy);
    results.push(measured.row);
    if (results.length % protocol.heldoutSeeds.length === 0) console.log(JSON.stringify({ phase: "heldout", regime: item.regime.key, cases: results.length }));
  }
  const armNames = Object.keys(results[0]!.arms);
  const summary = protocol.regimes.map((regime) => {
    const rows = results.filter((item) => item.regime === regime.key);
    return { regime: regime.key, environments: rows.length, means: Object.fromEntries(armNames.map((arm) => [arm, average(rows.map((row) => row.arms[arm]!.result.score))])),
      contrasts: Object.fromEntries(armNames.filter((arm) => arm !== "selected").map((arm) => [arm,
        bootstrap(rows.map((row) => row.arms.selected!.result.score - row.arms[arm]!.result.score))])) };
  });
  const primaryContrasts = Object.fromEntries(armNames.filter((arm) => arm !== "selected").map((arm) => [arm, bootstrap(protocol.heldoutSeeds.map((seed) => {
    const rows = results.filter((item) => item.seed === seed && item.regime.startsWith("primary-"));
    return average(rows.map((row) => row.arms.selected!.result.score - row.arms[arm]!.result.score));
  }))]));
  const primary = primaryContrasts["random-hill"]!;
  const fixedNames = ["star-hill", "annealing", "fixed-pair", "fixed-reliable"];
  const fixedMeanPass = fixedNames.every((name) => primaryContrasts[name]!.mean > 0);
  const report = { contract: "algal.lab.policy-spike-heldout.v1", ...frozen, selectionDigest: hash(selectionText), selectedPolicy: policy,
    success: primary.mean > protocol.practicalMargin && primary.interval95[0] > 0 && fixedMeanPass,
    primaryContrasts, summary, maxOracleDiscrepancy,
    objectiveSelectionEvaluations: results.reduce((sum, row) => sum + Object.values(row.arms).reduce((subtotal, arm) => subtotal + arm.objectiveSelectionEvaluations, 0), 0),
    outputMeasurementEvaluations: results.length * 2,
    independentChampionChecks: results.length * 7,
    elapsedMs: performance.now() - started, results,
    limits: ["Exact distribution expectation evaluated in IEEE-754, not rational arithmetic.", "32 prespecified environment seeds; correlated graph budgets averaged within seed for the primary endpoint.",
      "No model inference or token-efficiency comparison.", "Policy evolution cost is additional to every deployment budget.",
      "Baselines are scoped implementations; no universal or state-of-the-art superiority claim."] };
  if (maxOracleDiscrepancy > 2e-14) throw new Error(`champion oracle discrepancy ${maxOracleDiscrepancy}`);
  await save("heldout.json", report);
  console.log(JSON.stringify({ phase: "complete", success: report.success, policy, primaryContrasts, summary,
    maxOracleDiscrepancy, objectiveSelectionEvaluations: report.objectiveSelectionEvaluations, elapsedMs: report.elapsedMs }, null, 2));
}

async function replay(): Promise<void> {
  const started = performance.now();
  const frozen = await identity();
  const { selectionText, policy, training } = await readSelection(frozen);
  const rerunTraining = computeTraining(frozen);
  if (JSON.stringify({ ...training, elapsedMs: 0 }) !== JSON.stringify({ ...rerunTraining, elapsedMs: 0 })) throw new Error("development reproduction differs");
  const { text: heldoutText, value: rawHeldout } = await readBounded("heldout.json");
  if (rawHeldout.contract !== "algal.lab.policy-spike-heldout.v1" || !Array.isArray(rawHeldout.results)
    || rawHeldout.results.length !== protocol.heldoutSeeds.length * protocol.regimes.length) throw new Error("invalid heldout archive");
  const heldout = rawHeldout as unknown as { sourceDigests: Record<string, string>; selectionDigest: string; results: ArmResult[] };
  if (JSON.stringify(heldout.sourceDigests) !== JSON.stringify(frozen.sourceDigests) || heldout.selectionDigest !== hash(selectionText)) throw new Error("heldout archive identity differs");
  const reproduced: ArmResult[] = [];
  let maxOracleDiscrepancy = 0;
  for (const item of cases(protocol.heldoutSeeds, protocol.regimes)) {
    const measured = runCase(item, policy);
    reproduced.push(measured.row);
    maxOracleDiscrepancy = Math.max(maxOracleDiscrepancy, measured.maxOracleDiscrepancy);
  }
  if (JSON.stringify(reproduced) !== JSON.stringify(heldout.results)) throw new Error("heldout reproduction differs");
  if (maxOracleDiscrepancy > 2e-14) throw new Error("reproduction oracle discrepancy");
  const receipt = { contract: "algal.lab.policy-spike-reproduction.v1", ...frozen, selectionDigest: hash(selectionText),
    heldoutDigest: hash(heldoutText), trainingCandidates: rerunTraining.candidates.length, heldoutCases: reproduced.length,
    replaySelectionEvaluations: rerunTraining.totalEvaluations + reproduced.length * 7 * protocol.deploymentEvaluations,
    measurementEvaluations: reproduced.length * 2, independentChampionChecks: reproduced.length * 7,
    maxOracleDiscrepancy, elapsedMs: performance.now() - started,
    statement: "Fresh numerical reproduction matches every retained development and heldout arm result, including champions and best-by-evaluation traces; no new selection." };
  await save("reproduction.json", receipt);
  console.log(JSON.stringify(receipt, null, 2));
}

const command = process.argv[2];
const usage = "usage: bun research/spikes/evolution/experiment.ts train|evaluate|replay";
if (process.argv.length !== 3) throw new Error(usage);
if (command === "train") await train();
else if (command === "evaluate") await evaluate();
else if (command === "replay") await replay();
else throw new Error(usage);
