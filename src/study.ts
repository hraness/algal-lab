import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { MemoryStore, builtinRegistry, canonicalize, manifestToJson, parseRunReceipt, replayExecutor, runOrganism, type Executor, type RunReceipt } from "@hraness/algal";
import { ArtifactStore, digest, readJsonFile, sourceIdentities, digestString } from "./artifacts";
import { ALGAL_REVISION, CONDITIONS, conditionOrder, contextPhase, equal, instrumentOf, json, object, parseProtocol, proposalSlots, protocolSettings, type Budget, type Condition, type Phase, type Protocol, type ResearchContext } from "./contracts";
import { environmentFor, type FailureEnvironment } from "./heterogeneous";
import { boundedResearcher, evaluateGraph, laboratoryTools, mean, measure, primedProposal, primedResearcher, randomResearcher, researcherView, researchManifest, researchManifestV2, scriptedResearcher, type Measurement } from "./researcher";

export type Attempt = {
  contract: "algal.lab.attempt.v1";
  context: ResearchContext;
  instrumentDigest: string;
  receipt: RunReceipt;
  measurement: Measurement | null;
};
type Observed = { id: string; researcher: number; round: number; phase: Phase; measurement: Measurement };
/** Transfer results per held-out budget. Transfer designs never join the primary
 * portfolio; each regime freezes its own portfolio and champion before holdout. */
export type TransferSummary = {
  regime: Budget; attempts: number; validExperiments: number; uniqueDesigns: number; predictionMae: number | null;
  selectedAttempt: string | null; selectedScore: number | null; selectedRandomAuc: number | null; selectedTargetedAuc: number | null;
  portfolioDigest: string; evaluation: string;
};
export type Summary = {
  replicate: number; condition: Condition; attempts: number; primedDesigns: number; validExperiments: number; uniqueDesigns: number;
  predictionMae: number | null; meanHoldoutAuc: number | null; bestHoldoutAuc: number | null; coverageAt075: number;
  selectedAttempt: string | null; selectedScore: number | null; selectedRandomAuc: number | null; selectedTargetedAuc: number | null;
  portfolioDigest: string; evaluation: string; transfers: TransferSummary[];
};
export type StudyReport = {
  contract: "algal.lab.report.v3";
  algalRevision: string;
  backend: "scripted" | "random" | "command";
  protocol: Protocol;
  instrumentDigest: string;
  applicationDigest: string;
  researcherManifest: string;
  conditionOrders: { replicate: number; conditions: Condition[] }[];
  attempts: string[];
  summaries: Summary[];
};
export type StudyOptions = { executor?: Executor; policy?: "adaptive" | "random"; progress?: (message: string) => void };
const HOST_EXECUTORS = new Set(["algal-lab:scripted-network.v1", "algal-lab:random-network.v1", "algal-lab:primed-design.v1"]);
type Engine = {
  put: (value: unknown) => Promise<string>;
  executor: (context: ResearchContext, index: number) => Promise<Executor>;
  progress?: (message: string) => void;
};

function contextFor(protocol: Protocol, replicate: number, condition: Condition, round: number, researcher: number, prior: Observed[], phase: Phase, budget: Budget): ResearchContext {
  const visible = prior.filter((item) => condition !== "isolated" || item.researcher === researcher).slice(-24);
  const base = {
    replicate, condition, round, researcher,
    nodes: budget.nodes, edges: budget.edges, failureSteps: budget.failureSteps, discoverySeeds: [...protocol.discoverySeeds],
    evidence: visible.map((item) => ({ id: item.id, graph: item.measurement.proposal.graph, score: item.measurement.score })),
    messages: condition === "shared-artifacts-and-messages" ? prior.slice(-12).map((item) => ({ id: item.id, text: item.measurement.proposal.message })) : [],
  };
  if (protocol.contract === "algal.lab.study.v3") return { contract: "algal.lab.context.v3", phase, environment: environmentFor(budget.nodes, replicate), ...base };
  return protocol.contract === "algal.lab.study.v2" ? { contract: "algal.lab.context.v2", phase, ...base } : { contract: "algal.lab.context.v1", ...base };
}

type Frozen = { members: Observed[]; portfolio: Observed[]; champion: Observed | null; portfolioDigest: string };
async function freezePortfolio(engine: Engine, replicate: number, condition: Condition, members: Observed[], regime: Budget | null): Promise<Frozen> {
  // Retain one representative per realized graph. All valid attempts remain in evidence.
  const designs = new Map<string, Observed>();
  for (const item of members) {
    const graphId = digest(item.measurement.proposal.graph);
    if (!designs.has(graphId)) designs.set(graphId, item);
  }
  const portfolio = [...designs.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([, item]) => item);
  const champion = [...portfolio].sort((a, b) => b.measurement.score - a.measurement.score || digest(a.measurement.proposal.graph).localeCompare(digest(b.measurement.proposal.graph)))[0] ?? null;
  const portfolioDigest = await engine.put({ contract: "algal.lab.portfolio.v3", replicate, condition, regime,
    members: portfolio.map((item) => item.id), champion: champion?.id ?? null });
  return { members, portfolio, champion, portfolioDigest };
}
async function evaluatePortfolio(engine: Engine, protocol: Protocol, instrumentDigest: `sha256:${string}`, replicate: number, frozen: Frozen, budget: Budget) {
  const designs: { evaluation: string; meanAuc: number; aucs: number[] }[] = [];
  let selectedRandomAuc: number | null = null;
  let selectedTargetedAuc: number | null = null;
  const environment: FailureEnvironment | undefined = instrumentOf(protocol) === "network.v2" ? environmentFor(budget.nodes, replicate) : undefined;
  for (const item of frozen.portfolio) {
    const results = evaluateGraph(item.measurement.proposal.graph, replicate, protocol.holdoutSeeds, budget.failureSteps, environment);
    const meanAuc = mean(results.map((r) => r.metrics.auc));
    if (item.id === frozen.champion?.id) {
      selectedRandomAuc = mean(results.filter((r) => r.schedule.kind === "random").map((r) => r.metrics.auc));
      selectedTargetedAuc = results.find((r) => r.schedule.kind === "targeted")!.metrics.auc;
    }
    const evaluation = await engine.put({ contract: "algal.lab.design-evaluation.v1", instrumentDigest,
      attempt: item.id, graphDigest: digest(item.measurement.proposal.graph), results, meanAuc });
    designs.push({ evaluation, meanAuc, aucs: results.map((result) => result.metrics.auc) });
  }
  const evaluation = await engine.put({ contract: "algal.lab.evaluation.v1", instrumentDigest,
    portfolioDigest: frozen.portfolioDigest, holdoutSeeds: protocol.holdoutSeeds, designs: designs.map((design) => design.evaluation) });
  return { designs, evaluation, selectedRandomAuc, selectedTargetedAuc };
}

async function core(protocol: Protocol, backend: StudyReport["backend"], engine: Engine): Promise<StudyReport> {
  const identities = await sourceIdentities(instrumentOf(protocol));
  const settings = protocolSettings(protocol);
  const manifest = manifestToJson(instrumentOf(protocol) === "network.v2" ? researchManifestV2 : researchManifest);
  const researcherManifest = await engine.put(manifest);
  const attempts: string[] = [];
  const conditionOrders: StudyReport["conditionOrders"] = [];
  const frozen: { replicate: number; condition: Condition; primed: number; observed: Observed[]; primary: Frozen; transfers: { regime: Budget; observed: Observed[]; frozen: Frozen }[] }[] = [];
  const budget: Budget = { nodes: protocol.nodes, edges: protocol.edges, failureSteps: protocol.failureSteps };
  const attempt = async (context: ResearchContext, executor: Executor, observed: Observed[], expected?: Measurement["proposal"]["graph"]): Promise<void> => {
    const receipt = await runOrganism({
      manifest: instrumentOf(protocol) === "network.v2" ? researchManifestV2 : researchManifest, args: { input: { context: json(researcherView(context)) } },
      fns: builtinRegistry(), store: new MemoryStore(), executors: [boundedResearcher(executor)],
      tools: laboratoryTools(context, identities.instrumentDigest),
    });
    let measurement: Measurement | null = null;
    if (receipt.outcome === "complete") {
      measurement = measure(receipt.cells.researcher?.outputs?.out, context);
      if (!equal(measurement, receipt.cells.measure?.outputs?.measurement)) throw new Error("instrument output does not match fresh measurement");
    }
    // A primed design is host work: it must be exactly the seeded design, even under replay.
    if (expected && (!measurement || !equal(measurement.proposal.graph, expected))) throw new Error("primed design does not match the protocol seed");
    const record: Attempt = { contract: "algal.lab.attempt.v1", context, instrumentDigest: identities.instrumentDigest, receipt, measurement };
    const id = await engine.put(record);
    attempts.push(id);
    if (measurement) observed.push({ id, researcher: context.researcher, round: context.round, phase: contextPhase(context), measurement });
  };
  for (const [replicateIndex, replicate] of protocol.replicateSeeds.entries()) {
    const conditions = conditionOrder(protocol, replicateIndex);
    conditionOrders.push({ replicate, conditions });
    for (const condition of conditions) {
      const observed: Observed[] = [];
      // Priming: identical seeded designs per researcher in every condition, measured through the instrument.
      for (let index = 0; index < settings.primedDesigns; index++) {
        for (let researcher = 0; researcher < protocol.researchers; researcher++) {
          const context = contextFor(protocol, replicate, condition, -1, researcher, [], "primed", budget);
          await attempt(context, primedResearcher(context, index), observed, primedProposal(context, index).graph);
        }
      }
      for (let round = 0; round < protocol.rounds; round++) {
        const prior = [...observed]; // Every researcher in a round sees the same completed-round boundary.
        for (let researcher = 0; researcher < protocol.researchers; researcher++) {
          const context = contextFor(protocol, replicate, condition, round, researcher, prior, "discovery", budget);
          await attempt(context, await engine.executor(context, attempts.length), observed);
        }
      }
      const primed = observed.filter((item) => item.phase === "primed").length;
      const primary = await freezePortfolio(engine, replicate, condition, observed, null);
      // Transfer: after discovery, each researcher proposes once per held-out budget from the same visible evidence.
      const transfers: { regime: Budget; observed: Observed[]; frozen: Frozen }[] = [];
      for (const regime of settings.transferRegimes) {
        const transferred: Observed[] = [];
        for (let researcher = 0; researcher < protocol.researchers; researcher++) {
          const context = contextFor(protocol, replicate, condition, protocol.rounds, researcher, observed, "transfer", regime);
          await attempt(context, await engine.executor(context, attempts.length), transferred);
        }
        transfers.push({ regime, observed: transferred, frozen: await freezePortfolio(engine, replicate, condition, transferred, regime) });
      }
      frozen.push({ replicate, condition, primed, observed, primary, transfers });
      engine.progress?.(`seed ${replicate}, ${condition}: ${observed.length - primed}/${protocol.researchers * protocol.rounds} valid experiments; ${primary.portfolio.length} designs frozen`);
    }
  }
  // No further model calls or selection after the first holdout measurement.
  const summaries: Summary[] = [];
  for (const batch of frozen) {
    const researched = batch.observed.filter((item) => item.phase !== "primed");
    const { designs, evaluation, selectedRandomAuc, selectedTargetedAuc } = await evaluatePortfolio(engine, protocol, identities.instrumentDigest, batch.replicate, batch.primary, budget);
    const coverage = Array.from({ length: protocol.holdoutSeeds.length * 2 }, (_, i) => designs.some((design) => design.aucs[i]! >= 0.75));
    const transfers: TransferSummary[] = [];
    for (const transfer of batch.transfers) {
      const evaluated = await evaluatePortfolio(engine, protocol, identities.instrumentDigest, batch.replicate, transfer.frozen, transfer.regime);
      transfers.push({ regime: transfer.regime, attempts: protocol.researchers, validExperiments: transfer.observed.length, uniqueDesigns: evaluated.designs.length,
        predictionMae: transfer.observed.length ? mean(transfer.observed.map((item) => item.measurement.predictionError)) : null,
        selectedAttempt: transfer.frozen.champion?.id ?? null, selectedScore: transfer.frozen.champion?.measurement.score ?? null,
        selectedRandomAuc: evaluated.selectedRandomAuc, selectedTargetedAuc: evaluated.selectedTargetedAuc,
        portfolioDigest: transfer.frozen.portfolioDigest, evaluation: evaluated.evaluation });
    }
    summaries.push({
      replicate: batch.replicate, condition: batch.condition, attempts: protocol.researchers * protocol.rounds, primedDesigns: batch.primed,
      validExperiments: researched.length, uniqueDesigns: designs.length,
      predictionMae: researched.length ? mean(researched.map((item) => item.measurement.predictionError)) : null,
      meanHoldoutAuc: designs.length ? mean(designs.map((design) => design.meanAuc)) : null,
      bestHoldoutAuc: designs.length ? Math.max(...designs.map((design) => design.meanAuc)) : null,
      coverageAt075: mean(coverage.map(Number)), portfolioDigest: batch.primary.portfolioDigest, evaluation,
      selectedAttempt: batch.primary.champion?.id ?? null, selectedScore: batch.primary.champion?.measurement.score ?? null, selectedRandomAuc, selectedTargetedAuc, transfers,
    });
  }
  return { contract: "algal.lab.report.v3", algalRevision: ALGAL_REVISION, backend, protocol, ...identities, researcherManifest, conditionOrders, attempts, summaries };
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
  const raw = object(envelope.report, ["contract", "algalRevision", "backend", "protocol", "instrumentDigest", "applicationDigest", "researcherManifest", "conditionOrders", "attempts", "summaries"], "report");
  if (raw.contract !== "algal.lab.report.v3" || raw.algalRevision !== ALGAL_REVISION || !["scripted", "random", "command"].includes(raw.backend as string)) throw new Error("unsupported report identity");
  const protocol = parseProtocol(raw.protocol);
  if (!equal(protocol, await readJsonFile(join(directory, "protocol.json")))) throw new Error("protocol intent mismatch");
  const identities = await sourceIdentities(instrumentOf(protocol));
  if (raw.instrumentDigest !== identities.instrumentDigest || raw.applicationDigest !== identities.applicationDigest) throw new Error("source identity changed; verify with the exact recorded source version");
  const total = protocol.replicateSeeds.length * CONDITIONS.length * (proposalSlots(protocol) + protocolSettings(protocol).primedDesigns * protocol.researchers);
  if (!Array.isArray(raw.attempts) || raw.attempts.length !== total) throw new Error("attempt count violates protocol");
  const references = raw.attempts.map(digestString);
  const store = new ArtifactStore(directory);
  const checked = new Set<string>();
  const regenerated = await core(protocol, raw.backend as StudyReport["backend"], {
    async put(value) {
      const id = digest(value);
      const stored = await store.get(id).catch(() => undefined);
      if (stored === undefined) throw new Error("archive lacks the reproduced artifact; report differs from reproduced study");
      if (!equal(value, stored)) throw new Error("artifact differs from reproduced value");
      checked.add(id);
      return id;
    },
    async executor(context, index) {
      const saved = object(await store.get(references[index]), ["contract", "context", "instrumentDigest", "receipt", "measurement"], "attempt");
      if (saved.contract !== "algal.lab.attempt.v1" || !equal(saved.context, context)) throw new Error("recorded researcher context violates visibility or protocol");
      // Scripted policies are pure functions of the reconstructed context, so they
      // are recomputed rather than replayed: a relabelled or hand-picked archive
      // cannot pass as a deterministic baseline. Only foreign command output replays.
      if (raw.backend === "scripted") return scriptedResearcher(context);
      if (raw.backend === "random") return randomResearcher(context);
      const receipt = parseRunReceipt(json(saved.receipt));
      for (const effect of receipt.effects) {
        if (HOST_EXECUTORS.has(effect.executor)) throw new Error("command archive records a host policy executor");
      }
      return replayExecutor(receipt.effects);
    },
  });
  if (!equal(regenerated, envelope.report)) throw new Error("report differs from reproduced study");
  return { ok: true, attempts: references.length, experiments: regenerated.summaries.reduce((n, s) => n + s.validExperiments + s.transfers.reduce((t, x) => t + x.validExperiments, 0), 0), artifacts: checked.size, reportDigest: expectedDigest };
}

export function renderReport(report: StudyReport): string {
  const number = (value: number | null) => value === null ? "—" : value.toFixed(4);
  const settings = protocolSettings(report.protocol);
  const budget = (b: Budget) => `${b.nodes}n/${b.edges}e/${b.failureSteps}s`;
  const transfers = settings.transferRegimes.length ? `\n\n## Transfer budgets\n\nAfter discovery, each researcher proposed once per held-out budget from the same visible evidence. Transfer designs never join the primary portfolio; scores use discovery schedules at the transfer budget, and the champion is selected before holdout evaluation.\n\n| Seed | Condition | Budget | Valid | Designs | Champion discovery AUC | Champion random AUC | Champion targeted AUC | Prediction MAE |\n| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |\n` +
    report.summaries.flatMap((s) => s.transfers.map((t) => `| ${s.replicate} | ${s.condition} | ${budget(t.regime)} | ${t.validExperiments}/${t.attempts} | ${t.uniqueDesigns} | ${number(t.selectedScore)} | ${number(t.selectedRandomAuc)} | ${number(t.selectedTargetedAuc)} | ${number(t.predictionMae)} |`)).join("\n") : "";
  return `# ${report.protocol.name}\n\nBackend: ${report.backend}. ${report.backend !== "command" ? "This is a deterministic search baseline, not evidence of LLM discovery." : "Model outputs are hypotheses; measurements come from the admitted simulator."}\n\n` +
    `All conditions receive ${report.protocol.researchers * report.protocol.rounds} proposal slots per seed${settings.primedDesigns ? ` after ${settings.primedDesigns} host-primed design(s) per researcher, identical across conditions` : ""}. Portfolios freeze before evaluation on held-out random schedules and a repeated targeted control. Context and token counts may differ.${settings.counterbalance ? " Condition order rotates by replicate: " + report.conditionOrders.map((o) => `${o.replicate}: ${o.conditions.join(" → ")}`).join("; ") + "." : ""}\n\n` +
    `One champion per condition is selected by discovery mean AUC before evaluation, with graph-digest tie breaking. Champion random AUC uses unseen schedules; champion targeted AUC repeats the deterministic control.\n\n` +
    `| Seed | Condition | Valid | Primed | Designs | Champion random AUC | Champion targeted AUC | Prediction MAE | Portfolio mean AUC | Post-hoc best AUC | Coverage ≥ 0.75 |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n` +
    report.summaries.map((s) => `| ${s.replicate} | ${s.condition} | ${s.validExperiments}/${s.attempts} | ${s.primedDesigns} | ${s.uniqueDesigns} | ${number(s.selectedRandomAuc)} | ${number(s.selectedTargetedAuc)} | ${number(s.predictionMae)} | ${number(s.meanHoldoutAuc)} | ${number(s.bestHoldoutAuc)} | ${number(s.coverageAt075)} |`).join("\n") +
    transfers +
    `\n\nMean AUC averages the frozen unique designs, including primed designs. Best is a descriptive post-hoc maximum, not a selected or deployed policy. Coverage is the fraction of held-out schedules for which at least one frozen design reaches 0.75; it does not model interacting networks. Isolated portfolios pool the independent researchers' designs only after discovery. Prediction MAE excludes host-primed designs.\n\nTargeted attack is deterministic and ignores its seed, so repeated targeted entries are not independent observations. Replicate-seed rows are the comparison unit; this small demo makes no significance claim. Numerical results describe this graph model only. Replay and reproduction establish consistency, not physical validity or source authenticity.\n\nEvidence: [study.json](study.json), [protocol.json](protocol.json), and content-addressed [artifacts](artifacts/).\n`;
}
