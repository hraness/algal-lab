import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { canonicalize } from "@hraness/algal";
import { ArtifactStore, digest, digestString, readJsonFile, sourceIdentities } from "./artifacts";
import { CONDITIONS, equal, integer, json, object, parseProtocol, text, type Condition, type Protocol } from "./contracts";
import { parseGraph, simulate, type Graph } from "./network";
import { exactRandomAuc, serviceAucCeiling } from "./oracle";
import { mean } from "./researcher";
import { runStudy, verifyStudy, type Attempt, type StudyReport } from "./study";

export type Regime = { name: string; nodes: number; edges: number; failureSteps: number };
export type QualificationPlan = {
  contract: "algal.lab.qualification-plan.v1"; name: string; replicateSeeds: number[];
  researchers: number; rounds: number; discoverySeeds: number[]; holdoutSeeds: number[]; regimes: Regime[];
};
export type QualificationRow = {
  regime: string; backend: "scripted" | "random"; replicate: number; condition: Condition;
  attempts: number; valid: number; unique: number; selectedAttempt: string | null; graphDigest: string | null;
  exactRandomAuc: number | null; targetedAuc: number | null; sequenceDigest: string;
};
export type PairedSummary = {
  regime: string; contrast: string; count: number; differences: number[]; mean: number;
  minimum: number; maximum: number; wins: number; ties: number; losses: number;
};
export type QualificationReport = {
  contract: "algal.lab.qualification.v1"; plan: QualificationPlan;
  instrumentDigest: string; applicationDigest: string;
  studies: { id: string; reportDigest: string }[];
  references: { regime: string; graph: Graph; exactRandomAuc: number; targetedAuc: number; ceiling: number }[];
  rows: QualificationRow[]; comparisons: PairedSummary[];
  controls: { allAttemptsValid: boolean; randomIgnoresSharing: boolean; scriptedIgnoresMessages: boolean };
};

function slug(value: unknown): string {
  const name = text(value, 40, "name");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error("name must be a lowercase slug");
  return name;
}
export function parseQualificationPlan(value: unknown): QualificationPlan {
  const p = object(value, ["contract", "name", "replicateSeeds", "researchers", "rounds", "discoverySeeds", "holdoutSeeds", "regimes"], "qualification plan");
  if (p.contract !== "algal.lab.qualification-plan.v1") throw new Error("unsupported qualification plan");
  if (!Array.isArray(p.replicateSeeds) || p.replicateSeeds.length < 2 || p.replicateSeeds.length > 16) throw new Error("qualification requires 2..16 seeds");
  const replicateSeeds = p.replicateSeeds.map((seed) => integer(seed, 0, 0xffffffff, "replicate seed"));
  if (new Set(replicateSeeds).size !== replicateSeeds.length) throw new Error("repeated replicate seed");
  const researchers = integer(p.researchers, 2, 3, "researchers");
  const rounds = integer(p.rounds, 2, 4, "rounds");
  if (!Array.isArray(p.regimes) || p.regimes.length < 1 || p.regimes.length > 3) throw new Error("qualification requires 1..3 regimes");
  const regimes = p.regimes.map((value) => {
    const r = object(value, ["name", "nodes", "edges", "failureSteps"], "regime");
    const protocol = parseProtocol({ contract: "algal.lab.study.v1", name: "admission", replicateSeeds: [0],
      researchers, rounds, nodes: integer(r.nodes, 4, 10, "nodes"), edges: r.edges, failureSteps: r.failureSteps,
      discoverySeeds: p.discoverySeeds, holdoutSeeds: p.holdoutSeeds });
    return { name: slug(r.name), nodes: protocol.nodes, edges: protocol.edges, failureSteps: protocol.failureSteps };
  });
  if (new Set(regimes.map((r) => r.name)).size !== regimes.length) throw new Error("repeated regime name");
  const first = regimes[0]!;
  const seedProtocol = parseProtocol({ contract: "algal.lab.study.v1", name: "seeds", replicateSeeds: [0], researchers, rounds,
    nodes: first.nodes, edges: first.edges, failureSteps: first.failureSteps, discoverySeeds: p.discoverySeeds, holdoutSeeds: p.holdoutSeeds });
  return { contract: "algal.lab.qualification-plan.v1", name: slug(p.name), replicateSeeds, researchers, rounds,
    discoverySeeds: seedProtocol.discoverySeeds, holdoutSeeds: seedProtocol.holdoutSeeds, regimes };
}

/** Fixed path, then closing ring edge, then longest cyclic chords in node order.
 * This is an a-priori topology reference, never selected from measured scores. */
export function referenceGraph(nodes: number, edges: number): Graph {
  integer(nodes, 4, 10, "nodes"); integer(edges, nodes - 1, nodes * (nodes - 1) / 2, "edges");
  const pairs: [number, number][] = [];
  const seen = new Set<string>();
  const add = (a: number, b: number) => {
    const edge: [number, number] = a < b ? [a, b] : [b, a];
    const key = edge.join(":");
    if (pairs.length < edges && !seen.has(key)) { seen.add(key); pairs.push(edge); }
  };
  for (let node = 0; node < nodes - 1; node++) add(node, node + 1);
  add(0, nodes - 1);
  for (let distance = Math.floor(nodes / 2); distance >= 2; distance--) {
    for (let node = 0; node < nodes; node++) add(node, (node + distance) % nodes);
  }
  return parseGraph({ nodes, edges: pairs });
}

type Descriptor = { id: string; regime: Regime; policy: "adaptive" | "random"; protocol: Protocol };
function descriptors(plan: QualificationPlan): Descriptor[] {
  const result: Descriptor[] = [];
  for (const regime of plan.regimes) for (const policy of ["adaptive", "random"] as const) {
    for (let offset = 0; offset < plan.replicateSeeds.length; offset += 8) {
      const id = `${regime.name}-${policy}-${offset / 8}`;
      result.push({ id, regime, policy, protocol: parseProtocol({
        contract: "algal.lab.study.v1", name: id, replicateSeeds: plan.replicateSeeds.slice(offset, offset + 8),
        researchers: plan.researchers, rounds: plan.rounds, nodes: regime.nodes, edges: regime.edges, failureSteps: regime.failureSteps,
        discoverySeeds: plan.discoverySeeds, holdoutSeeds: plan.holdoutSeeds,
      }) });
    }
  }
  return result;
}

export function pairedSummary(regime: string, contrast: string, differences: number[]): PairedSummary {
  if (!differences.length || differences.length > 16 || differences.some((v) => !Number.isFinite(v) || Math.abs(v) > 1)) throw new Error("invalid paired differences");
  const tolerance = 1e-12;
  return { regime, contrast, count: differences.length, differences, mean: mean(differences),
    minimum: Math.min(...differences), maximum: Math.max(...differences),
    wins: differences.filter((v) => v > tolerance).length, ties: differences.filter((v) => Math.abs(v) <= tolerance).length,
    losses: differences.filter((v) => v < -tolerance).length };
}

async function reconstruct(plan: QualificationPlan, directory: string): Promise<QualificationReport> {
  const identities = await sourceIdentities();
  const studies: QualificationReport["studies"] = [];
  const rows: QualificationRow[] = [];
  for (const descriptor of descriptors(plan)) {
    const path = join(directory, "studies", descriptor.id);
    const verification = await verifyStudy(path);
    // Verification reconstructs all fields before they are interpreted here.
    const envelope = object(await readJsonFile(join(path, "study.json")), ["report", "digest"], "study envelope");
    if (envelope.digest !== verification.reportDigest || digest(envelope.report) !== verification.reportDigest) throw new Error("study report changed after verification");
    const report = envelope.report as StudyReport;
    if (!equal(report.protocol, descriptor.protocol) || report.backend !== (descriptor.policy === "adaptive" ? "scripted" : "random")) throw new Error("qualification study does not match the frozen plan");
    studies.push({ id: descriptor.id, reportDigest: verification.reportDigest });
    const store = new ArtifactStore(path);
    const attempts = new Map<string, Attempt>();
    for (const id of report.attempts) attempts.set(id, await store.get(id) as unknown as Attempt);
    for (const summary of report.summaries) {
      const selected = summary.selectedAttempt ? attempts.get(summary.selectedAttempt) : undefined;
      const graph = selected?.measurement?.proposal.graph;
      const sequence = [...attempts.values()].filter((a) => a.context.replicate === summary.replicate && a.context.condition === summary.condition)
        .map((a) => a.measurement ? digest(a.measurement.proposal.graph) : null);
      rows.push({ regime: descriptor.regime.name, backend: report.backend as "scripted" | "random", replicate: summary.replicate, condition: summary.condition,
        attempts: summary.attempts, valid: summary.validExperiments, unique: summary.uniqueDesigns, selectedAttempt: summary.selectedAttempt,
        graphDigest: graph ? digest(graph) : null, exactRandomAuc: graph ? exactRandomAuc(graph, descriptor.regime.failureSteps) : null,
        targetedAuc: summary.selectedTargetedAuc, sequenceDigest: digest(sequence) });
    }
  }
  const find = (regime: string, replicate: number, backend: QualificationRow["backend"], condition: Condition): QualificationRow => {
    const row = rows.find((r) => r.regime === regime && r.replicate === replicate && r.backend === backend && r.condition === condition);
    if (!row) throw new Error("missing qualification row"); return row;
  };
  const comparisons: PairedSummary[] = [];
  let randomIgnoresSharing = true; let scriptedIgnoresMessages = true;
  for (const regime of plan.regimes) {
    const differences = [[], [], []] as [number[], number[], number[]];
    for (const seed of plan.replicateSeeds) {
      const isolated = find(regime.name, seed, "scripted", "isolated");
      const shared = find(regime.name, seed, "scripted", "shared-artifacts");
      const messages = find(regime.name, seed, "scripted", "shared-artifacts-and-messages");
      const random = find(regime.name, seed, "random", "isolated");
      const randomShared = find(regime.name, seed, "random", "shared-artifacts");
      // A condition with no valid graph gets zero utility; do not drop failures.
      differences[0].push((shared.exactRandomAuc ?? 0) - (isolated.exactRandomAuc ?? 0));
      differences[1].push((isolated.exactRandomAuc ?? 0) - (random.exactRandomAuc ?? 0));
      differences[2].push((shared.exactRandomAuc ?? 0) - (randomShared.exactRandomAuc ?? 0));
      const controlled = (a: QualificationRow, b: QualificationRow) => a.sequenceDigest === b.sequenceDigest && a.graphDigest === b.graphDigest && a.exactRandomAuc === b.exactRandomAuc;
      scriptedIgnoresMessages &&= controlled(shared, messages);
      randomIgnoresSharing &&= CONDITIONS.every((c) => controlled(random, find(regime.name, seed, "random", c)));
    }
    for (const [index, contrast] of ["shared-minus-isolated", "isolated-minus-random", "shared-minus-random"].entries()) {
      comparisons.push(pairedSummary(regime.name, contrast, differences[index]!));
    }
  }
  const references = plan.regimes.map((regime) => {
    const graph = referenceGraph(regime.nodes, regime.edges);
    return { regime: regime.name, graph, exactRandomAuc: exactRandomAuc(graph, regime.failureSteps),
      targetedAuc: simulate(graph, { kind: "targeted", seed: 0, steps: regime.failureSteps }).metrics.auc,
      ceiling: serviceAucCeiling(regime.nodes, regime.failureSteps) };
  });
  return { contract: "algal.lab.qualification.v1", plan, ...identities, studies, references, rows, comparisons,
    controls: { allAttemptsValid: rows.every((r) => r.valid === r.attempts), randomIgnoresSharing, scriptedIgnoresMessages } };
}

export async function runQualification(input: unknown, directory: string, progress?: (message: string) => void): Promise<QualificationReport> {
  const plan = parseQualificationPlan(input);
  await mkdir(dirname(directory), { recursive: true }); await mkdir(directory);
  await writeFile(join(directory, "plan.json"), canonicalize(json(plan)) + "\n", { flag: "wx", mode: 0o600 });
  for (const descriptor of descriptors(plan)) {
    progress?.(`qualification: ${descriptor.id}`);
    await runStudy(descriptor.protocol, join(directory, "studies", descriptor.id), { policy: descriptor.policy });
  }
  const report = await reconstruct(plan, directory);
  await writeFile(join(directory, "qualification.json"), canonicalize(json({ report, digest: digest(report) })) + "\n", { flag: "wx", mode: 0o600 });
  await writeFile(join(directory, "report.md"), renderQualification(report), { flag: "wx", mode: 0o600 });
  return report;
}

export async function verifyQualification(directory: string): Promise<{ ok: true; studies: number; attempts: number; reportDigest: string }> {
  const envelope = object(await readJsonFile(join(directory, "qualification.json")), ["report", "digest"], "qualification envelope");
  const expected = digestString(envelope.digest);
  if (digest(envelope.report) !== expected) throw new Error("qualification digest mismatch");
  const plan = parseQualificationPlan(await readJsonFile(join(directory, "plan.json")));
  const actual = await reconstruct(plan, directory);
  if (!equal(actual, envelope.report)) throw new Error("qualification differs from reproduced analysis");
  return { ok: true, studies: actual.studies.length, attempts: actual.rows.reduce((sum, row) => sum + row.attempts, 0), reportDigest: expected };
}

export function renderQualification(report: QualificationReport): string {
  return `# ${report.plan.name}\n\nExact population evaluation of discovery-selected champions. This is a scripted comparison, not live-model or transferable-discovery evidence. All candidates freeze before evaluation. The full random-failure distribution includes discovery states; it is not an exclusively held-out sample.\n\n` +
    `Paired differences use whole search replicates. Units are absolute AUC points; positive favors the first policy. Intervals below are observed minima/maxima, not confidence intervals. Empty selections receive zero utility rather than being omitted.\n\n` +
    `| Regime | Contrast | Seeds | Mean difference | Minimum | Maximum | Wins/ties/losses |\n| --- | --- | ---: | ---: | ---: | ---: | --- |\n` +
    report.comparisons.map((c) => `| ${c.regime} | ${c.contrast} | ${c.count} | ${c.mean.toFixed(6)} | ${c.minimum.toFixed(6)} | ${c.maximum.toFixed(6)} | ${c.wins}/${c.ties}/${c.losses} |`).join("\n") +
    `\n\nFixed ring/chord reference (not selected from results):\n\n| Regime | Exact random AUC | Targeted control | Service ceiling |\n| --- | ---: | ---: | ---: |\n` +
    report.references.map((r) => `| ${r.regime} | ${r.exactRandomAuc.toFixed(6)} | ${r.targetedAuc.toFixed(6)} | ${r.ceiling.toFixed(6)} |`).join("\n") +
    `\n\nControls: ${JSON.stringify(report.controls)}. All raw paired differences, failures, duplicate counts, chosen graph references, study digests, and source identities are in [qualification.json](qualification.json). The frozen input is [plan.json](plan.json).\n\nA null or negative sharing result does not fail this measurement system. No superiority or statistical-significance claim is made. Targeted ties depend on node labels; the exact random endpoint is invariant to relabeling.\n`;
}
