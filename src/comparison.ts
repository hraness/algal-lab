import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { canonicalize, type Executor } from "@hraness/algal";
import { ArtifactStore, digest, digestString, readJsonFile, sourceIdentities } from "./artifacts";
import { CONDITIONS, conditionOrder, contextPhase, effectiveSeedCollisions, equal, integer, json, object, parseBudget, parseProtocol, proposalSlots, protocolSettings, text, type Budget, type Condition, type Instrument, type Protocol } from "./contracts";
import { environmentFor, simulateHeterogeneous, type FailureEnvironment } from "./heterogeneous";
import { simulate, type Graph } from "./network";
import { exactRandomAuc, exactWeightedAuc, serviceAucCeiling, weightedServiceAucCeiling } from "./oracle";
import { referenceGraph } from "./qualification";
import { pairedInference, type PairedInference } from "./statistics";
import { runStudy, verifyStudy, type Attempt, type StudyReport, type Summary } from "./study";
import { topologyClasses, topologyDigest } from "./topology";

/**
 * A replicated comparison is the frozen confirmatory design the qualification
 * plan asked for: matched initial populations by construction (host priming),
 * counterbalanced condition order, failure-inclusive champion scoring against
 * the exact oracle, paired uncertainty across replicate seeds with a
 * preregistered practical margin, matched scripted controls, a fixed reference,
 * topology classes tracked separately from labeled identity, and held-out
 * transfer budgets that test whether anything learned generalizes.
 */
export const ARMS = ["adaptive", "random", "live"] as const;
export type Arm = typeof ARMS[number];
export const CONTRASTS = ["shared-minus-isolated", "messages-minus-shared", "messages-minus-isolated"] as const;
export type Contrast = typeof CONTRASTS[number];
export const ARM_CONTRASTS = ["live-minus-random", "live-minus-adaptive", "adaptive-minus-random"] as const;
export type ArmContrast = typeof ARM_CONTRASTS[number];

export type ComparisonPlan = {
  contract: "algal.lab.comparison-plan.v1" | "algal.lab.comparison-plan.v2"; name: string; instrument: Instrument;
  replicateSeeds: number[]; researchers: number; rounds: number;
  primedDesigns: number; primary: Budget; transferRegimes: Budget[]; discoverySeeds: number[]; holdoutSeeds: number[]; margin: number;
};
export type TransferRow = {
  regime: Budget; attempts: number; valid: number; uniqueDesigns: number; topologyClasses: number; citedParents: number;
  championAttempt: string | null; championGraphDigest: string | null; championTopologyDigest: string | null;
  championExactAuc: number | null; championTargetedAuc: number | null; matchesReferenceTopology: boolean;
};
export type ComparisonRow = {
  arm: Arm; replicate: number; condition: Condition; attempts: number; valid: number; primed: number; uniqueDesigns: number; topologyClasses: number;
  championAttempt: string | null; championGraphDigest: string | null; championTopologyDigest: string | null; championIsPrimed: boolean;
  championExactAuc: number | null; championTargetedAuc: number | null; bestPrimedExactAuc: number; improvementOverPrimed: number | null;
  matchesReferenceTopology: boolean; sequenceDigest: string; transfers: TransferRow[];
};
export type ContrastRow = { arm: Arm; scope: string; contrast: Contrast; inference: PairedInference };
export type ArmContrastRow = { scope: string; condition: Condition; contrast: ArmContrast; inference: PairedInference };
export type ComparisonReport = {
  contract: "algal.lab.comparison.v1"; plan: ComparisonPlan; arms: Arm[]; instrumentDigest: string; applicationDigest: string;
  studies: { id: string; arm: Arm; chunk: number; reportDigest: string }[];
  references: { scope: string; budget: Budget; graph: Graph; topologyDigest: string; exactRandomAuc: number; targetedAuc: number; ceiling: number;
    perReplicate: { replicate: number; exactRandomAuc: number; targetedAuc: number; ceiling: number }[] }[];
  rows: ComparisonRow[]; contrasts: ContrastRow[]; armContrasts: ArmContrastRow[];
  controls: { allSlotsRetained: boolean; primedIdenticalAcrossConditions: boolean; primedIdenticalAcrossArms: boolean; randomIgnoresSharing: boolean;
    scriptedIgnoresMessages: boolean; counterbalanced: boolean; transferBudgetsHonored: boolean; championsSelectedBeforeHoldout: true };
};

const CHUNK = 8;
function slug(value: unknown): string {
  const name = text(value, 40, "name");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error("name must be a lowercase slug");
  return name;
}
function oracleBudget(value: unknown, label: string): Budget {
  const budget = parseBudget(value, label);
  if (budget.nodes > 10) throw new Error(`${label}: exact evaluation is bounded to ten nodes`);
  return budget;
}
export function parseComparisonPlan(value: unknown): ComparisonPlan {
  const version = value !== null && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>).contract : undefined;
  if (version !== "algal.lab.comparison-plan.v1" && version !== "algal.lab.comparison-plan.v2") throw new Error("unsupported comparison plan");
  const keys = ["contract", "name", "replicateSeeds", "researchers", "rounds", "primedDesigns", "primary", "transferRegimes", "discoverySeeds", "holdoutSeeds", "margin"];
  // instrument defaults under the v1 contract; every other unknown field still rejects.
  const filled = value !== null && typeof value === "object" && !Array.isArray(value)
    ? { ...(value as Record<string, unknown>), instrument: (value as Record<string, unknown>).instrument ?? "network.v1" } : value;
  const p = object(filled, [...keys, "instrument"], "comparison plan");
  const expected = version === "algal.lab.comparison-plan.v2" ? "network.v2" : "network.v1";
  if (p.instrument !== expected) throw new Error(`instrument must be ${expected}`);
  const instrument = p.instrument as Instrument;
  if (!Array.isArray(p.replicateSeeds) || p.replicateSeeds.length < 4 || p.replicateSeeds.length > 16) throw new Error("comparison requires 4..16 replicate seeds");
  const replicateSeeds = p.replicateSeeds.map((seed) => integer(seed, 0, 0xffffffff, "replicate seed"));
  if (new Set(replicateSeeds).size !== replicateSeeds.length) throw new Error("repeated replicate seed");
  if (typeof p.margin !== "number" || !Number.isFinite(p.margin) || p.margin <= 0 || p.margin > 0.1) throw new Error("margin must be a practical AUC margin in (0, 0.1]");
  if (!Array.isArray(p.transferRegimes)) throw new Error("transferRegimes must be a list");
  const primary = oracleBudget(p.primary, "primary");
  // Chunks are separate protocols, so effective schedule seeds are checked across the whole plan here.
  const [collision] = effectiveSeedCollisions({ replicateSeeds, discoverySeeds: p.discoverySeeds as number[], holdoutSeeds: p.holdoutSeeds as number[] });
  if (collision) throw new Error(`effective seed ${collision[0].effective} repeats across the plan's replicates`);
  const transferRegimes = p.transferRegimes.map((regime, index) => oracleBudget(regime, `transferRegimes[${index}]`));
  // Every chunk must admit as a study protocol; the first chunk carries the shared seed bounds.
  const admission = { contract: instrument === "network.v2" ? "algal.lab.study.v3" : "algal.lab.study.v2", name: "admission", replicateSeeds: replicateSeeds.slice(0, CHUNK),
    researchers: integer(p.researchers, 2, 3, "researchers"), rounds: integer(p.rounds, 1, 6, "rounds"), ...primary,
    discoverySeeds: p.discoverySeeds, holdoutSeeds: p.holdoutSeeds, primedDesigns: integer(p.primedDesigns, 1, 4, "primedDesigns"),
    counterbalance: true, transferRegimes, ...(instrument === "network.v2" ? { instrument: "network.v2" } : {}) };
  const protocol = parseProtocol(admission);
  return { contract: version, name: slug(p.name), instrument, replicateSeeds, researchers: protocol.researchers, rounds: protocol.rounds,
    primedDesigns: protocolSettings(protocol).primedDesigns, primary, transferRegimes: protocolSettings(protocol).transferRegimes, discoverySeeds: protocol.discoverySeeds,
    holdoutSeeds: protocol.holdoutSeeds, margin: p.margin };
}

type Descriptor = { id: string; arm: Arm; chunk: number; protocol: Protocol };
export function comparisonStudies(plan: ComparisonPlan, arms: readonly Arm[]): Descriptor[] {
  const result: Descriptor[] = [];
  for (const arm of arms) {
    for (let offset = 0; offset < plan.replicateSeeds.length; offset += CHUNK) {
      const chunk = offset / CHUNK;
      const id = `${arm}-${chunk}`;
      result.push({ id, arm, chunk, protocol: parseProtocol({ contract: plan.instrument === "network.v2" ? "algal.lab.study.v3" : "algal.lab.study.v2", name: id, replicateSeeds: plan.replicateSeeds.slice(offset, offset + CHUNK),
        researchers: plan.researchers, rounds: plan.rounds, ...plan.primary, discoverySeeds: plan.discoverySeeds, holdoutSeeds: plan.holdoutSeeds,
        primedDesigns: plan.primedDesigns, counterbalance: true, transferRegimes: plan.transferRegimes,
        ...(plan.instrument === "network.v2" ? { instrument: "network.v2" as const } : {}) }) });
    }
  }
  return result;
}
/** Model calls a live arm needs: every discovery and transfer slot, no priming. */
export function liveCallBudget(plan: ComparisonPlan): number {
  return comparisonStudies(plan, ["live"]).reduce((sum, d) => sum + d.protocol.replicateSeeds.length * CONDITIONS.length * proposalSlots(d.protocol), 0);
}

function parseArms(value: unknown): Arm[] {
  if (!Array.isArray(value) || value.length < 2 || value.length > 3 || new Set(value).size !== value.length) throw new Error("invalid comparison arms");
  const arms = value.map((arm) => { if (!(ARMS as readonly unknown[]).includes(arm)) throw new Error("unknown comparison arm"); return arm as Arm; });
  if (!arms.includes("adaptive") || !arms.includes("random")) throw new Error("comparison requires the scripted control arms");
  return arms;
}
function targetedAuc(graph: Graph, steps: number): number { return simulate(graph, { kind: "targeted", seed: 0, steps }).metrics.auc; }
const scopeOf = (index: number) => index < 0 ? "primary" : `transfer-${index}`;

async function reconstruct(plan: ComparisonPlan, arms: Arm[], directory: string): Promise<ComparisonReport> {
  const identities = await sourceIdentities(plan.instrument);
  const budgets = [plan.primary, ...plan.transferRegimes];
  // Under network.v2 each replicate poses a different environment; fixed-design
  // references and every champion endpoint are evaluated per replicate.
  const env = (nodes: number, replicate: number): FailureEnvironment | undefined =>
    plan.instrument === "network.v2" ? environmentFor(nodes, replicate) : undefined;
  const exactAuc = (graph: Graph, replicate: number, steps: number): number => {
    const environment = env(graph.nodes, replicate);
    return environment === undefined ? exactRandomAuc(graph, steps) : exactWeightedAuc(graph, environment, steps);
  };
  const targetedOf = (graph: Graph, replicate: number, steps: number): number => {
    const environment = env(graph.nodes, replicate);
    return environment === undefined ? targetedAuc(graph, steps) : simulateHeterogeneous(graph, environment, { kind: "targeted", seed: 0, steps }).metrics.auc;
  };
  const ceilingOf = (nodes: number, replicate: number, steps: number): number => {
    const environment = env(nodes, replicate);
    return environment === undefined ? serviceAucCeiling(nodes, steps) : weightedServiceAucCeiling(environment, nodes, steps);
  };
  const meanOf = (values: number[]) => values.reduce((a, b) => a + b, 0) / values.length;
  const references = budgets.map((budget, index) => {
    const graph = referenceGraph(budget.nodes, budget.edges);
    const perReplicate = plan.replicateSeeds.map((replicate) => ({ replicate,
      exactRandomAuc: exactAuc(graph, replicate, budget.failureSteps),
      targetedAuc: targetedOf(graph, replicate, budget.failureSteps),
      ceiling: ceilingOf(budget.nodes, replicate, budget.failureSteps) }));
    return { scope: scopeOf(index - 1), budget, graph, topologyDigest: topologyDigest(graph),
      exactRandomAuc: meanOf(perReplicate.map((row) => row.exactRandomAuc)),
      targetedAuc: meanOf(perReplicate.map((row) => row.targetedAuc)),
      ceiling: meanOf(perReplicate.map((row) => row.ceiling)), perReplicate };
  });
  const referenceTopology = (scope: string) => references.find((r) => r.scope === scope)!.topologyDigest;
  const studies: ComparisonReport["studies"] = [];
  const rows: ComparisonRow[] = [];
  let counterbalanced = true; let transferBudgetsHonored = true; let primedIdenticalAcrossConditions = true;
  const primedByReplicate = new Map<number, string>();
  let primedIdenticalAcrossArms = true;
  for (const descriptor of comparisonStudies(plan, arms)) {
    const path = join(directory, "studies", descriptor.id);
    const verification = await verifyStudy(path);
    const envelope = object(await readJsonFile(join(path, "study.json")), ["report", "digest"], "study envelope");
    if (envelope.digest !== verification.reportDigest || digest(envelope.report) !== verification.reportDigest) throw new Error("study report changed after verification");
    const report = envelope.report as StudyReport;
    const expectedBackend = descriptor.arm === "adaptive" ? "scripted" : descriptor.arm === "random" ? "random" : "command";
    if (!equal(report.protocol, descriptor.protocol) || report.backend !== expectedBackend) throw new Error("comparison study does not match the frozen plan");
    studies.push({ id: descriptor.id, arm: descriptor.arm, chunk: descriptor.chunk, reportDigest: verification.reportDigest });
    counterbalanced &&= report.conditionOrders.every((order, index) => equal(order, { replicate: descriptor.protocol.replicateSeeds[index], conditions: conditionOrder(descriptor.protocol, index) }));
    const store = new ArtifactStore(path);
    const attempts = new Map<string, Attempt>();
    for (const id of report.attempts) attempts.set(id, await store.get(id) as unknown as Attempt);
    const portfolioOf = async (summary: Summary | Summary["transfers"][number]) => {
      const portfolio = object(await store.get(summary.portfolioDigest), ["contract", "replicate", "condition", "regime", "members", "champion"], "portfolio");
      if (!Array.isArray(portfolio.members) || portfolio.champion !== summary.selectedAttempt) throw new Error("portfolio does not match summary");
      return portfolio.members.map((id) => attempts.get(digestString(id))!);
    };
    for (const summary of report.summaries) {
      const own = [...attempts.values()].filter((a) => a.context.replicate === summary.replicate && a.context.condition === summary.condition);
      const primed = own.filter((a) => contextPhase(a.context) === "primed");
      const primedGraphs = digest(primed.map((a) => a.measurement?.proposal.graph ?? null));
      const seen = primedByReplicate.get(summary.replicate);
      if (seen === undefined) primedByReplicate.set(summary.replicate, primedGraphs);
      else if (seen !== primedGraphs) { if (descriptor.arm === rows.find((r) => r.replicate === summary.replicate)?.arm) primedIdenticalAcrossConditions = false; else primedIdenticalAcrossArms = false; }
      const bestPrimedExactAuc = Math.max(0, ...primed.flatMap((a) => a.measurement ? [exactAuc(a.measurement.proposal.graph, summary.replicate, plan.primary.failureSteps)] : []));
      const members = await portfolioOf(summary);
      const champion = summary.selectedAttempt ? attempts.get(summary.selectedAttempt) : undefined;
      const graph = champion?.measurement?.proposal.graph;
      const championExactAuc = graph ? exactAuc(graph, summary.replicate, plan.primary.failureSteps) : null;
      const sequence = own.filter((a) => contextPhase(a.context) !== "transfer").map((a) => a.measurement ? digest(a.measurement.proposal.graph) : null);
      const transfers: TransferRow[] = [];
      for (const [index, transfer] of summary.transfers.entries()) {
        const regime = plan.transferRegimes[index]!;
        const proposals = own.filter((a) => contextPhase(a.context) === "transfer" && a.context.nodes === regime.nodes && a.context.edges === regime.edges && a.context.failureSteps === regime.failureSteps);
        transferBudgetsHonored &&= equal(transfer.regime, regime) && proposals.length === plan.researchers &&
          proposals.every((a) => !a.measurement || (a.measurement.proposal.graph.nodes === regime.nodes && a.measurement.proposal.graph.edges.length === regime.edges));
        const transferMembers = await portfolioOf(transfer);
        const selected = transfer.selectedAttempt ? attempts.get(transfer.selectedAttempt)?.measurement?.proposal.graph : undefined;
        const classes = topologyClasses(transferMembers.map((a) => a.measurement!.proposal.graph)).length;
        transfers.push({ regime, attempts: transfer.attempts, valid: transfer.validExperiments, uniqueDesigns: transfer.uniqueDesigns, topologyClasses: classes,
          citedParents: proposals.filter((a) => (a.measurement?.proposal.parents.length ?? 0) > 0).length,
          championAttempt: transfer.selectedAttempt, championGraphDigest: selected ? digest(selected) : null, championTopologyDigest: selected ? topologyDigest(selected) : null,
          championExactAuc: selected ? exactAuc(selected, summary.replicate, regime.failureSteps) : null, championTargetedAuc: transfer.selectedTargetedAuc,
          matchesReferenceTopology: selected ? topologyDigest(selected) === referenceTopology(scopeOf(index)) : false });
      }
      rows.push({ arm: descriptor.arm, replicate: summary.replicate, condition: summary.condition, attempts: summary.attempts, valid: summary.validExperiments,
        primed: summary.primedDesigns, uniqueDesigns: summary.uniqueDesigns, topologyClasses: topologyClasses(members.map((a) => a.measurement!.proposal.graph)).length,
        championAttempt: summary.selectedAttempt, championGraphDigest: graph ? digest(graph) : null, championTopologyDigest: graph ? topologyDigest(graph) : null,
        championIsPrimed: champion ? contextPhase(champion.context) === "primed" : false, championExactAuc, championTargetedAuc: summary.selectedTargetedAuc,
        bestPrimedExactAuc, improvementOverPrimed: championExactAuc === null ? null : championExactAuc - bestPrimedExactAuc,
        matchesReferenceTopology: graph ? topologyDigest(graph) === referenceTopology("primary") : false, sequenceDigest: digest(sequence), transfers });
    }
  }
  const find = (arm: Arm, replicate: number, condition: Condition): ComparisonRow => {
    const row = rows.find((r) => r.arm === arm && r.replicate === replicate && r.condition === condition);
    if (!row) throw new Error("missing comparison row"); return row;
  };
  // Failure-inclusive utility: a condition that selected no champion scores zero rather than being dropped.
  const utility = (row: ComparisonRow, scope: number): number => scope < 0 ? row.championExactAuc ?? 0 : row.transfers[scope]?.championExactAuc ?? 0;
  const scopes = [-1, ...plan.transferRegimes.map((_, index) => index)];
  const contrasts: ContrastRow[] = [];
  for (const arm of arms) for (const scope of scopes) for (const contrast of CONTRASTS) {
    const [minuend, subtrahend]: [Condition, Condition] = contrast === "shared-minus-isolated" ? ["shared-artifacts", "isolated"]
      : contrast === "messages-minus-shared" ? ["shared-artifacts-and-messages", "shared-artifacts"] : ["shared-artifacts-and-messages", "isolated"];
    const differences = plan.replicateSeeds.map((seed) => utility(find(arm, seed, minuend), scope) - utility(find(arm, seed, subtrahend), scope));
    contrasts.push({ arm, scope: scopeOf(scope), contrast, inference: pairedInference(differences, plan.margin) });
  }
  const armContrasts: ArmContrastRow[] = [];
  for (const scope of scopes) for (const condition of CONDITIONS) for (const contrast of ARM_CONTRASTS) {
    const [minuend, subtrahend]: [Arm, Arm] = contrast === "live-minus-random" ? ["live", "random"] : contrast === "live-minus-adaptive" ? ["live", "adaptive"] : ["adaptive", "random"];
    if (!arms.includes(minuend) || !arms.includes(subtrahend)) continue;
    const differences = plan.replicateSeeds.map((seed) => utility(find(minuend, seed, condition), scope) - utility(find(subtrahend, seed, condition), scope));
    armContrasts.push({ scope: scopeOf(scope), condition, contrast, inference: pairedInference(differences, plan.margin) });
  }
  let randomIgnoresSharing = true; let scriptedIgnoresMessages = true;
  const controlled = (a: ComparisonRow, b: ComparisonRow) => a.sequenceDigest === b.sequenceDigest && a.championGraphDigest === b.championGraphDigest && a.championExactAuc === b.championExactAuc;
  for (const seed of plan.replicateSeeds) {
    randomIgnoresSharing &&= CONDITIONS.every((c) => controlled(find("random", seed, "isolated"), find("random", seed, c)));
    scriptedIgnoresMessages &&= controlled(find("adaptive", seed, "shared-artifacts"), find("adaptive", seed, "shared-artifacts-and-messages"));
  }
  const allSlotsRetained = rows.every((r) => r.attempts === plan.researchers * plan.rounds && r.primed === plan.researchers * plan.primedDesigns && r.transfers.every((t) => t.attempts === plan.researchers));
  return { contract: "algal.lab.comparison.v1", plan, arms, ...identities, studies, references, rows, contrasts, armContrasts,
    controls: { allSlotsRetained, primedIdenticalAcrossConditions, primedIdenticalAcrossArms, randomIgnoresSharing, scriptedIgnoresMessages, counterbalanced, transferBudgetsHonored, championsSelectedBeforeHoldout: true } };
}

export type ComparisonOptions = { executor?: Executor; progress?: (message: string) => void };
/** Run the scripted control arms and, when an executor is supplied, the live arm.
 * The analysis is written only after every study has completed and verified. */
export async function runComparison(input: unknown, directory: string, options: ComparisonOptions = {}): Promise<ComparisonReport> {
  const plan = parseComparisonPlan(input);
  const arms: Arm[] = options.executor ? ["adaptive", "random", "live"] : ["adaptive", "random"];
  await mkdir(dirname(directory), { recursive: true }); await mkdir(directory);
  await writeFile(join(directory, "plan.json"), canonicalize(json({ plan, arms })) + "\n", { flag: "wx", mode: 0o600 });
  for (const descriptor of comparisonStudies(plan, arms)) {
    options.progress?.(`comparison: ${descriptor.id}`);
    await runStudy(descriptor.protocol, join(directory, "studies", descriptor.id), {
      ...(descriptor.arm === "live" ? { executor: options.executor! } : { policy: descriptor.arm }),
      ...(options.progress ? { progress: options.progress } : {}) });
  }
  const report = await reconstruct(plan, arms, directory);
  await writeFile(join(directory, "comparison.json"), canonicalize(json({ report, digest: digest(report) })) + "\n", { flag: "wx", mode: 0o600 });
  await writeFile(join(directory, "report.md"), renderComparison(report), { flag: "wx", mode: 0o600 });
  return report;
}
export async function verifyComparison(directory: string): Promise<{ ok: true; studies: number; rows: number; reportDigest: string }> {
  const envelope = object(await readJsonFile(join(directory, "comparison.json")), ["report", "digest"], "comparison envelope");
  const expected = digestString(envelope.digest);
  if (digest(envelope.report) !== expected) throw new Error("comparison digest mismatch");
  const frozen = object(await readJsonFile(join(directory, "plan.json")), ["plan", "arms"], "comparison intent");
  const actual = await reconstruct(parseComparisonPlan(frozen.plan), parseArms(frozen.arms), directory);
  if (!equal(actual, envelope.report)) throw new Error("comparison differs from reproduced analysis");
  return { ok: true, studies: actual.studies.length, rows: actual.rows.length, reportDigest: expected };
}

export function renderComparison(report: ComparisonReport): string {
  const f = (value: number | null) => value === null ? "—" : value.toFixed(6);
  const budget = (b: Budget) => `${b.nodes} nodes / ${b.edges} edges / ${b.failureSteps} steps`;
  const inference = (i: PairedInference) => `${f(i.mean)} | [${f(i.bootstrap.lower)}, ${f(i.bootstrap.upper)}] | ${i.signFlip.pValue.toFixed(4)} | ${i.wilcoxon.pValue === null ? "—" : i.wilcoxon.pValue.toFixed(4)} | ${i.wins}/${i.ties}/${i.losses} | ${i.verdict}`;
  const armMean = (arm: Arm, condition: Condition, scope: number) => {
    const values = report.rows.filter((r) => r.arm === arm && r.condition === condition).map((r) => scope < 0 ? r.championExactAuc ?? 0 : r.transfers[scope]?.championExactAuc ?? 0);
    return values.reduce((a, b) => a + b, 0) / values.length;
  };
  const scopes = [-1, ...report.plan.transferRegimes.map((_, index) => index)];
  const live = report.arms.includes("live");
  return `# ${report.plan.name}\n\n` +
    `Replicated comparison under the frozen plan in [plan.json](plan.json): ${report.plan.replicateSeeds.length} replicate seeds, ${report.plan.researchers} researchers, ${report.plan.rounds} discovery rounds, ${report.plan.primedDesigns} host-primed design(s) per researcher (identical across conditions and arms by construction), counterbalanced condition order, primary budget ${budget(report.plan.primary)}${report.plan.transferRegimes.length ? `, transfer budgets ${report.plan.transferRegimes.map(budget).join(" and ")}` : ""}. Arms: ${report.arms.join(", ")}${live ? "" : " (no live arm: this is a scripted control run, not model evidence)"}.\n\n` +
    `The endpoint is the discovery-selected champion's exact expected random-failure AUC (${report.plan.instrument === "network.v2" ? "full weighted removal distribution under each replicate's seeded environment, oracle-computed, label-dependent; per-replicate values are reported per environment" : "full uniform removal distribution, oracle-computed, label-invariant"}). Champions are selected before any holdout measurement. A condition without a valid champion scores zero (failure-inclusive). Intervals are 95% percentile bootstrap intervals over paired replicate differences; p-values are exact two-sided sign-flip and Wilcoxon signed-rank tests. The preregistered practical margin is ${report.plan.margin} AUC points; a verdict of exceeds-margin requires the whole interval above it.\n\n` +
    `## Mean champion exact AUC by arm and condition\n\n| Scope | Arm | Isolated | Shared artifacts | Shared artifacts and messages | Fixed reference | Ceiling |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n` +
    scopes.flatMap((scope) => report.arms.map((arm) => { const ref = report.references[scope + 1]!; return `| ${scopeOf(scope)} | ${arm} | ${f(armMean(arm, "isolated", scope))} | ${f(armMean(arm, "shared-artifacts", scope))} | ${f(armMean(arm, "shared-artifacts-and-messages", scope))} | ${f(ref.exactRandomAuc)} | ${f(ref.ceiling)} |`; })).join("\n") +
    `\n\n## Information-sharing contrasts (paired by seed within an arm)\n\n| Scope | Arm | Contrast | Mean | 95% bootstrap | Sign-flip p | Wilcoxon p | W/T/L | Verdict |\n| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |\n` +
    report.contrasts.map((c) => `| ${c.scope} | ${c.arm} | ${c.contrast} | ${inference(c.inference)} |`).join("\n") +
    `\n\n## Arm contrasts (paired by seed within a condition)\n\n| Scope | Condition | Contrast | Mean | 95% bootstrap | Sign-flip p | Wilcoxon p | W/T/L | Verdict |\n| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |\n` +
    (report.armContrasts.map((c) => `| ${c.scope} | ${c.condition} | ${c.contrast} | ${inference(c.inference)} |`).join("\n") || "| — | — | — | — | — | — | — | — | — |") +
    `\n\n## Search versus priming\n\nEach row's improvement is the champion's exact AUC minus the best host-primed design's exact AUC for that seed; a champion that is itself a primed design shows zero improvement. Topology classes count isomorphism classes among frozen unique designs.\n\n| Arm | Condition | Seeds | Champion improved over priming | Champion is primed | Mean improvement | Mean designs | Mean topology classes | Champion matches reference topology |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n` +
    report.arms.flatMap((arm) => CONDITIONS.map((condition) => {
      const rows = report.rows.filter((r) => r.arm === arm && r.condition === condition);
      const improvements = rows.map((r) => r.improvementOverPrimed ?? 0);
      return `| ${arm} | ${condition} | ${rows.length} | ${rows.filter((r) => (r.improvementOverPrimed ?? 0) > 1e-12).length} | ${rows.filter((r) => r.championIsPrimed).length} | ${f(improvements.reduce((a, b) => a + b, 0) / rows.length)} | ${(rows.reduce((a, r) => a + r.uniqueDesigns, 0) / rows.length).toFixed(2)} | ${(rows.reduce((a, r) => a + r.topologyClasses, 0) / rows.length).toFixed(2)} | ${rows.filter((r) => r.matchesReferenceTopology).length} |`;
    })).join("\n") +
    (report.plan.transferRegimes.length ? `\n\n## Transfer\n\nAfter discovery, each researcher proposed once per held-out budget from the same visible evidence. Cited parents count transfer proposals that referenced visible primary-budget evidence.\n\n| Scope | Arm | Condition | Valid / slots | Cited parents | Champion matches reference topology |\n| --- | --- | --- | ---: | ---: | ---: |\n` +
      report.plan.transferRegimes.flatMap((_, index) => report.arms.flatMap((arm) => CONDITIONS.map((condition) => {
        const rows = report.rows.filter((r) => r.arm === arm && r.condition === condition).map((r) => r.transfers[index]!);
        return `| ${scopeOf(index)} | ${arm} | ${condition} | ${rows.reduce((a, t) => a + t.valid, 0)} / ${rows.reduce((a, t) => a + t.attempts, 0)} | ${rows.reduce((a, t) => a + t.citedParents, 0)} | ${rows.filter((t) => t.matchesReferenceTopology).length} |`;
      }))).join("\n") : "") +
    `\n\n## Controls\n\n${JSON.stringify(report.controls)}\n\nA failed control invalidates the comparison rather than adjusting it. The fixed ring/chord reference is predeclared, never selected from results. Every paired difference, champion identity, topology digest, and study digest is in [comparison.json](comparison.json).\n\n` +
    `## Limits\n\nThis is a small graph model with ${report.plan.replicateSeeds.length} independent replicate seeds; bootstrap intervals at this size are coarse and the sign-flip test's smallest attainable two-sided p is ${(2 / 2 ** report.plan.replicateSeeds.length).toExponential(2)}. Scripted arms are deterministic controls, not intelligence. A live arm's result describes one model configuration under this protocol; it does not establish causal use of messages, a transferable discovery beyond the tested budgets, or an independently audited provider bill. Verdicts follow the preregistered rule and are not to be reinterpreted after the fact.\n`;
}
