import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { MemoryStore, builtinRegistry, canonicalize, manifestToJson, parseRunReceipt, replayExecutor, runOrganism, type Executor, type RunReceipt } from "@hraness/algal";
import { ArtifactStore, digest, readJsonFile, sourceIdentities, digestString } from "./artifacts";
import { ALGAL_REVISION, CONDITIONS, equal, json, object, parseProtocol, type Condition, type Protocol, type ResearchContext } from "./contracts";
import { boundedResearcher, evaluateGraph, laboratoryTools, mean, measure, randomResearcher, researcherView, researchManifest, scriptedResearcher, type Measurement } from "./researcher";

export type Attempt = {
  contract: "algal.lab.attempt.v1";
  context: ResearchContext;
  instrumentDigest: string;
  receipt: RunReceipt;
  measurement: Measurement | null;
};
type Observed = { id: string; researcher: number; round: number; measurement: Measurement };
export type Summary = {
  replicate: number; condition: Condition; attempts: number; validExperiments: number; uniqueDesigns: number;
  predictionMae: number | null; meanHoldoutAuc: number | null; bestHoldoutAuc: number | null; coverageAt075: number;
  selectedAttempt: string | null; selectedRandomAuc: number | null; selectedTargetedAuc: number | null;
  portfolioDigest: string; evaluation: string;
};
export type StudyReport = {
  contract: "algal.lab.report.v2";
  algalRevision: string;
  backend: "scripted" | "random" | "command";
  protocol: Protocol;
  instrumentDigest: string;
  applicationDigest: string;
  researcherManifest: string;
  attempts: string[];
  summaries: Summary[];
};
export type StudyOptions = { executor?: Executor; policy?: "adaptive" | "random"; progress?: (message: string) => void };
type Engine = {
  put: (value: unknown) => Promise<string>;
  executor: (context: ResearchContext, index: number) => Promise<Executor>;
  progress?: (message: string) => void;
};

function contextFor(protocol: Protocol, replicate: number, condition: Condition, round: number, researcher: number, prior: Observed[]): ResearchContext {
  const visible = prior.filter((item) => condition !== "isolated" || item.researcher === researcher).slice(-24);
  return {
    contract: "algal.lab.context.v1", replicate, condition, round, researcher,
    nodes: protocol.nodes, edges: protocol.edges, failureSteps: protocol.failureSteps, discoverySeeds: [...protocol.discoverySeeds],
    evidence: visible.map((item) => ({ id: item.id, graph: item.measurement.proposal.graph, score: item.measurement.score })),
    messages: condition === "shared-artifacts-and-messages" ? prior.slice(-12).map((item) => ({ id: item.id, text: item.measurement.proposal.message })) : [],
  };
}

async function core(protocol: Protocol, backend: StudyReport["backend"], engine: Engine): Promise<StudyReport> {
  const identities = await sourceIdentities();
  const manifest = manifestToJson(researchManifest);
  const researcherManifest = await engine.put(manifest);
  const attempts: string[] = [];
  const frozen: { replicate: number; condition: Condition; observed: Observed[]; portfolio: Observed[]; champion: Observed | null; portfolioDigest: string }[] = [];
  for (const replicate of protocol.replicateSeeds) {
    for (const condition of CONDITIONS) {
      const observed: Observed[] = [];
      for (let round = 0; round < protocol.rounds; round++) {
        const prior = [...observed]; // Every researcher in a round sees the same completed-round boundary.
        for (let researcher = 0; researcher < protocol.researchers; researcher++) {
          const context = contextFor(protocol, replicate, condition, round, researcher, prior);
          const receipt = await runOrganism({
            manifest: researchManifest, args: { input: { context: json(researcherView(context)) } },
            fns: builtinRegistry(), store: new MemoryStore(), executors: [boundedResearcher(await engine.executor(context, attempts.length))],
            tools: laboratoryTools(context, identities.instrumentDigest),
          });
          let measurement: Measurement | null = null;
          if (receipt.outcome === "complete") {
            measurement = measure(receipt.cells.researcher?.outputs?.out, context);
            if (!equal(measurement, receipt.cells.measure?.outputs?.measurement)) throw new Error("instrument output does not match fresh measurement");
          }
          const attempt: Attempt = { contract: "algal.lab.attempt.v1", context, instrumentDigest: identities.instrumentDigest, receipt, measurement };
          const id = await engine.put(attempt);
          attempts.push(id);
          if (measurement) observed.push({ id, researcher, round, measurement });
        }
      }
      // Retain one representative per realized graph. All valid attempts remain in evidence.
      const designs = new Map<string, Observed>();
      for (const item of observed) {
        const graphId = digest(item.measurement.proposal.graph);
        if (!designs.has(graphId)) designs.set(graphId, item);
      }
      const portfolio = [...designs.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([, item]) => item);
      const champion = [...portfolio].sort((a, b) => b.measurement.score - a.measurement.score || digest(a.measurement.proposal.graph).localeCompare(digest(b.measurement.proposal.graph)))[0] ?? null;
      const portfolioDigest = await engine.put({ contract: "algal.lab.portfolio.v2", replicate, condition,
        members: portfolio.map((item) => item.id), champion: champion?.id ?? null });
      frozen.push({ replicate, condition, observed, portfolio, champion, portfolioDigest });
      engine.progress?.(`seed ${replicate}, ${condition}: ${observed.length}/${protocol.researchers * protocol.rounds} valid experiments; ${portfolio.length} designs frozen`);
    }
  }
  // No further model calls or selection after the first holdout measurement.
  const summaries: Summary[] = [];
  for (const batch of frozen) {
    const designs: { evaluation: string; meanAuc: number; aucs: number[] }[] = [];
    let selectedRandomAuc: number | null = null;
    let selectedTargetedAuc: number | null = null;
    for (const item of batch.portfolio) {
      const results = evaluateGraph(item.measurement.proposal.graph, batch.replicate, protocol.holdoutSeeds, protocol.failureSteps);
      const meanAuc = mean(results.map((r) => r.metrics.auc));
      if (item.id === batch.champion?.id) {
        selectedRandomAuc = mean(results.filter((r) => r.schedule.kind === "random").map((r) => r.metrics.auc));
        selectedTargetedAuc = results.find((r) => r.schedule.kind === "targeted")!.metrics.auc;
      }
      const evaluation = await engine.put({ contract: "algal.lab.design-evaluation.v1", instrumentDigest: identities.instrumentDigest,
        attempt: item.id, graphDigest: digest(item.measurement.proposal.graph), results, meanAuc });
      designs.push({ evaluation, meanAuc, aucs: results.map((result) => result.metrics.auc) });
    }
    const coverage = Array.from({ length: protocol.holdoutSeeds.length * 2 }, (_, i) => designs.some((design) => design.aucs[i]! >= 0.75));
    const evaluation = await engine.put({ contract: "algal.lab.evaluation.v1", instrumentDigest: identities.instrumentDigest,
      portfolioDigest: batch.portfolioDigest, holdoutSeeds: protocol.holdoutSeeds, designs: designs.map((design) => design.evaluation) });
    summaries.push({
      replicate: batch.replicate, condition: batch.condition, attempts: protocol.researchers * protocol.rounds,
      validExperiments: batch.observed.length, uniqueDesigns: designs.length,
      predictionMae: batch.observed.length ? mean(batch.observed.map((item) => item.measurement.predictionError)) : null,
      meanHoldoutAuc: designs.length ? mean(designs.map((design) => design.meanAuc)) : null,
      bestHoldoutAuc: designs.length ? Math.max(...designs.map((design) => design.meanAuc)) : null,
      coverageAt075: mean(coverage.map(Number)), portfolioDigest: batch.portfolioDigest, evaluation,
      selectedAttempt: batch.champion?.id ?? null, selectedRandomAuc, selectedTargetedAuc,
    });
  }
  return { contract: "algal.lab.report.v2", algalRevision: ALGAL_REVISION, backend, protocol, ...identities, researcherManifest, attempts, summaries };
}

export async function runStudy(input: unknown, directory: string, options: StudyOptions = {}): Promise<StudyReport> {
  const protocol = parseProtocol(input);
  if (options.policy !== undefined && options.policy !== "adaptive" && options.policy !== "random") throw new Error("unknown search policy");
  if (options.executor && options.policy !== undefined) throw new Error("choose a scripted policy or an executor, not both");
  await mkdir(dirname(directory), { recursive: true });
  await mkdir(directory); // Never overwrite another run or an uncertain partial result.
  const store = new ArtifactStore(directory);
  await store.initialize();
  // Intent survives an interrupted run. There is deliberately no automatic retry/resume.
  await writeFile(join(directory, "protocol.json"), canonicalize(json(protocol)) + "\n", { flag: "wx", mode: 0o600 });
  const report = await core(protocol, options.executor ? "command" : options.policy === "random" ? "random" : "scripted", {
    put: (value) => store.put(value), executor: async (context) => options.executor ?? (options.policy === "random" ? randomResearcher(context) : scriptedResearcher(context)),
    ...(options.progress ? { progress: options.progress } : {}),
  });
  const envelope = { report, digest: digest(report) };
  await writeFile(join(directory, "study.json"), canonicalize(json(envelope)) + "\n", { flag: "wx", mode: 0o600 });
  await writeFile(join(directory, "report.md"), renderReport(report), { flag: "wx", mode: 0o600 });
  return report;
}

/** Reconstruct the entire protocol from recorded agent effects, but execute the
 * current admitted simulator afresh. Nothing from an archive can execute code. */
export async function verifyStudy(directory: string): Promise<{ ok: true; attempts: number; experiments: number; artifacts: number; reportDigest: string }> {
  const envelope = object(await readJsonFile(join(directory, "study.json")), ["report", "digest"], "study envelope");
  const expectedDigest = digestString(envelope.digest);
  if (digest(envelope.report) !== expectedDigest) throw new Error("report digest mismatch");
  const raw = object(envelope.report, ["contract", "algalRevision", "backend", "protocol", "instrumentDigest", "applicationDigest", "researcherManifest", "attempts", "summaries"], "report");
  if (raw.contract !== "algal.lab.report.v2" || raw.algalRevision !== ALGAL_REVISION || !["scripted", "random", "command"].includes(raw.backend as string)) throw new Error("unsupported report identity");
  const protocol = parseProtocol(raw.protocol);
  if (!equal(protocol, await readJsonFile(join(directory, "protocol.json")))) throw new Error("protocol intent mismatch");
  const identities = await sourceIdentities();
  if (raw.instrumentDigest !== identities.instrumentDigest || raw.applicationDigest !== identities.applicationDigest) throw new Error("source identity changed; verify with the exact recorded source version");
  const total = protocol.replicateSeeds.length * CONDITIONS.length * protocol.rounds * protocol.researchers;
  if (!Array.isArray(raw.attempts) || raw.attempts.length !== total) throw new Error("attempt count violates protocol");
  const references = raw.attempts.map(digestString);
  const store = new ArtifactStore(directory);
  const checked = new Set<string>();
  const regenerated = await core(protocol, raw.backend as StudyReport["backend"], {
    async put(value) {
      const id = digest(value);
      if (!equal(value, await store.get(id))) throw new Error("artifact differs from reproduced value");
      checked.add(id);
      return id;
    },
    async executor(context, index) {
      const saved = object(await store.get(references[index]), ["contract", "context", "instrumentDigest", "receipt", "measurement"], "attempt");
      if (saved.contract !== "algal.lab.attempt.v1" || !equal(saved.context, context)) throw new Error("recorded researcher context violates visibility or protocol");
      const receipt = parseRunReceipt(json(saved.receipt));
      return replayExecutor(receipt.effects);
    },
  });
  if (!equal(regenerated, envelope.report)) throw new Error("report differs from reproduced study");
  return { ok: true, attempts: references.length, experiments: regenerated.summaries.reduce((n, s) => n + s.validExperiments, 0), artifacts: checked.size, reportDigest: expectedDigest };
}

export function renderReport(report: StudyReport): string {
  const number = (value: number | null) => value === null ? "—" : value.toFixed(4);
  return `# ${report.protocol.name}\n\nBackend: ${report.backend}. ${report.backend !== "command" ? "This is a deterministic search baseline, not evidence of LLM discovery." : "Model outputs are hypotheses; measurements come from the admitted simulator."}\n\n` +
    `All conditions receive ${report.protocol.researchers * report.protocol.rounds} proposal slots per seed. Portfolios freeze before evaluation on held-out random schedules and a repeated targeted control. Context and token counts may differ.\n\n` +
    `One champion per condition is selected by discovery mean AUC before evaluation, with graph-digest tie breaking. Champion random AUC uses unseen schedules; champion targeted AUC repeats the deterministic control.\n\n` +
    `| Seed | Condition | Valid | Designs | Champion random AUC | Champion targeted AUC | Prediction MAE | Portfolio mean AUC | Post-hoc best AUC | Coverage ≥ 0.75 |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n` +
    report.summaries.map((s) => `| ${s.replicate} | ${s.condition} | ${s.validExperiments}/${s.attempts} | ${s.uniqueDesigns} | ${number(s.selectedRandomAuc)} | ${number(s.selectedTargetedAuc)} | ${number(s.predictionMae)} | ${number(s.meanHoldoutAuc)} | ${number(s.bestHoldoutAuc)} | ${number(s.coverageAt075)} |`).join("\n") +
    `\n\nMean AUC averages the frozen unique designs. Best is a descriptive post-hoc maximum, not a selected or deployed policy. Coverage is the fraction of held-out schedules for which at least one frozen design reaches 0.75; it does not model interacting networks. Isolated portfolios pool the independent researchers' designs only after discovery.\n\nTargeted attack is deterministic and ignores its seed, so repeated targeted entries are not independent observations. Replicate-seed rows are the comparison unit; this small demo makes no significance claim. Numerical results describe this graph model only. Replay and reproduction establish consistency, not physical validity or source authenticity.\n\nEvidence: [study.json](study.json), [protocol.json](protocol.json), and content-addressed [artifacts](artifacts/).\n`;
}
