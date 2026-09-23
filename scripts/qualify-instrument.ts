/** Fixed, bounded numerical qualification; emits compact JSON evidence.
 * Run with `bun scripts/qualify-instrument.ts [output.json]`. With no argument the
 * evidence is printed to stdout; with a path it is written to a new file that is
 * never overwritten. No provider, credentials, or generated fixture corpus is
 * needed. The subject instrument remains unchanged.
 */
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import { simulate, randomGraph, mutateGraph, type Graph } from "../src/network";
import { environmentFor, simulateHeterogeneous, type FailureEnvironment } from "../src/heterogeneous";
import { exactRandomAuc, exactWeightedAuc, weightedServiceAucCeiling } from "../src/oracle";

if (process.argv.length > 3) throw new Error("qualification takes at most one output path; exhaustive scope is fixed at n=4,5,6");
const outputPath = process.argv[2];
if (outputPath !== undefined && (outputPath.length === 0 || outputPath.startsWith("--"))) throw new Error("output path must be a file path");
const sha = (source: string): string => createHash("sha256").update(source).digest("hex");
const sources = {
  instrument: await readFile(new URL("../src/network.ts", import.meta.url), "utf8"),
  heterogeneous: await readFile(new URL("../src/heterogeneous.ts", import.meta.url), "utf8"),
  oracle: await readFile(new URL("../src/oracle.ts", import.meta.url), "utf8"),
  probe: await readFile(new URL(import.meta.url), "utf8"),
};
function require(condition: boolean, message: string): void { if (!condition) throw new Error(message); }

function pairs(nodes: number): [number, number][] {
  const result: [number, number][] = [];
  for (let high = 1; high < nodes; high++) for (let low = 0; low < high; low++) result.push([low, high]);
  return result;
}

// Independent disjoint-set reference: the subject uses adjacency-list BFS.
// This does not call simulator parsing, adjacency, connectivity, or metrics.
function largest(graph: Graph, live: number): number {
  const parent = Array.from({ length: graph.nodes }, (_, id) => id);
  const root = (initial: number): number => {
    let node = initial;
    while (parent[node] !== node) node = parent[node]!;
    return node;
  };
  for (const [a, b] of graph.edges) if ((live & (1 << a)) && (live & (1 << b))) parent[root(b)] = root(a);
  const counts = new Map<number, number>();
  for (let id = 0; id < graph.nodes; id++) if (live & (1 << id)) counts.set(root(id), (counts.get(root(id)) ?? 0) + 1);
  return Math.max(0, ...counts.values());
}

function connected(graph: Graph): boolean { return largest(graph, (1 << graph.nodes) - 1) === graph.nodes; }

function targeted(graph: Graph): { removed: (null | number)[]; largest: number[] } {
  let live = (1 << graph.nodes) - 1;
  const removed: (null | number)[] = [null];
  const sizes = [graph.nodes];
  for (let step = 1; step <= graph.nodes - 2; step++) {
    const candidates = Array.from({ length: graph.nodes }, (_, node) => node)
      .filter((node) => (live & (1 << node)) !== 0)
      .map((node) => ({ node, degree: graph.edges.filter(([a, b]) =>
        (a === node && (live & (1 << b))) || (b === node && (live & (1 << a)))).length }))
      .sort((a, b) => b.degree - a.degree || a.node - b.node);
    const node = candidates[0]!.node;
    live &= ~(1 << node);
    removed.push(node);
    sizes.push(largest(graph, live));
  }
  return { removed, largest: sizes };
}

function aucNumerator(sizes: number[], steps: number): number {
  return sizes[0]! + sizes[steps]! + 2 * sizes.slice(1, steps).reduce((a, b) => a + b, 0);
}

function signature(graph: Graph): string {
  return Array.from({ length: graph.nodes }, (_, node) => graph.edges.filter(([a, b]) => a === node || b === node).length)
    .sort((a, b) => b - a).join(",");
}

const randomSeeds = [0, 1, 42, 0x80000000, 0xffffffff];
let comparisons = 0;
let maxAucError = 0;
let maxServiceError = 0;
function compare(graph: Graph, kind: "random" | "targeted", seed: number, steps: number): void {
  const actual = simulate(graph, { kind, seed, steps });
  const expected = kind === "targeted" ? targeted(graph) : undefined;
  require(actual.trajectory.length === steps + 1, "trajectory length mismatch");
  let live = (1 << graph.nodes) - 1;
  const sizes = [graph.nodes];
  for (let step = 0; step <= steps; step++) {
    const point = actual.trajectory[step]!;
    if (step === 0) require(point.removed === null, "intact step removal");
    else {
      require(Number.isInteger(point.removed) && point.removed! >= 0 && point.removed! < graph.nodes, "invalid removed node");
      require((live & (1 << point.removed!)) !== 0, "node removed twice");
      live &= ~(1 << point.removed!);
      sizes.push(largest(graph, live));
    }
    if (expected) require(point.removed === expected.removed[step], "targeted order mismatch");
    const active = Array.from({ length: graph.nodes }, (_, id) => id).filter((id) => live & (1 << id));
    require(JSON.stringify(active) === JSON.stringify(point.active), "active state mismatch");
    require(point.step === step && point.largestComponent === sizes[step], "component or step mismatch");
    const error = Math.abs(point.service - sizes[step]! / graph.nodes);
    maxServiceError = Math.max(maxServiceError, error);
    require(error <= 1e-14, "service mismatch");
  }
  const error = Math.abs(actual.metrics.auc - aucNumerator(sizes, steps) / (2 * graph.nodes * steps));
  maxAucError = Math.max(maxAucError, error);
  require(error <= 1e-14, "AUC mismatch");
  require(actual.metrics.finalService === sizes[steps]! / graph.nodes, "final service mismatch");
  comparisons++;
}

type Maximum = { auc: number; count: number };
type Budget = { nodes: number; edges: number; steps: number; graphs: number; targeted: Maximum; uniformRandom: Maximum; signatures: Record<string, number> };
const budgets = new Map<string, Budget>();
function observe(best: Maximum, auc: number): void {
  if (best.count === 0 || auc > best.auc) Object.assign(best, { auc, count: 1 });
  else if (auc === best.auc) best.count++;
}
const counts: Record<string, number> = {};
for (const nodes of [4, 5, 6]) {
  const universe = pairs(nodes);
  let total = 0;
  for (let mask = 0; mask < (1 << universe.length); mask++) {
    const graph = { nodes, edges: universe.filter((_edge, index) => mask & (1 << index)) };
    if (!connected(graph)) continue;
    total++;
    for (let steps = 1; steps <= nodes - 2; steps++) compare(graph, "targeted", 0, steps);
    for (const seed of randomSeeds) compare(graph, "random", seed, nodes - 2);
    const key = `${nodes}:${graph.edges.length}`;
    let budget = budgets.get(key);
    if (!budget) {
      budget = { nodes, edges: graph.edges.length, steps: nodes - 2, graphs: 0, targeted: { auc: -1, count: 0 }, uniformRandom: { auc: -1, count: 0 }, signatures: {} };
      budgets.set(key, budget);
    }
    budget.graphs++;
    const degrees = signature(graph);
    budget.signatures[degrees] = (budget.signatures[degrees] ?? 0) + 1;
    observe(budget.targeted, aucNumerator(targeted(graph).largest, nodes - 2) / (2 * nodes * (nodes - 2)));
    observe(budget.uniformRandom, exactRandomAuc(graph, nodes - 2));
  }
  counts[nodes] = total;
}
require(counts[4] === 38 && counts[5] === 728 && counts[6] === 26704, "connected graph enumeration sanity count");

// ---------------- network.v2: heterogeneous failure ----------------

// Value-weighted component on the same independent disjoint-set implementation.
function largestValue(graph: Graph, live: number, values: readonly number[]): number {
  const parent = Array.from({ length: graph.nodes }, (_, id) => id);
  const root = (initial: number): number => {
    let node = initial;
    while (parent[node] !== node) node = parent[node]!;
    return node;
  };
  for (const [a, b] of graph.edges) if ((live & (1 << a)) && (live & (1 << b))) parent[root(b)] = root(a);
  const sums = new Map<number, number>();
  for (let id = 0; id < graph.nodes; id++) if (live & (1 << id)) sums.set(root(id), (sums.get(root(id)) ?? 0) + values[id]!);
  return Math.max(0, ...sums.values());
}

/** Every weighted removal order independently: P(order) multiplies each
 * removed node's weight over the remaining total weight. */
function weightedOrderExpectation(graph: Graph, env: FailureEnvironment, steps: number): number {
  const totalValue = env.values.reduce((a, b) => a + b, 0);
  const totalWeight = env.weights.reduce((a, b) => a + b, 0);
  let total = 0;
  const visit = (removed: number[], removedWeight: number, probability: number, partial: number): void => {
    const k = removed.length;
    const live = ((1 << graph.nodes) - 1) & ~removed.reduce((mask, node) => mask | (1 << node), 0);
    const service = largestValue(graph, live, env.values) / totalValue;
    const coefficient = k === 0 || k === steps ? 0.5 : 1;
    if (k === steps) { total += probability * (partial + coefficient * service); return; }
    for (let node = 0; node < graph.nodes; node++) if (!removed.includes(node)) {
      visit([...removed, node], removedWeight + env.weights[node]!, probability * env.weights[node]! / (totalWeight - removedWeight), partial + coefficient * service);
    }
  };
  visit([], 0, 1, 0);
  return total / steps;
}

const heterogeneous = {
  graphsChecked: 0, flatReductions: 0, trajectoryChecks: 0, oracleComparisons: 0,
  maxReductionError: 0, maxServiceError: 0, maxAucError: 0, maxCeilingSlack: 0,
  environments: { seedsChecked: [7, 8], nodeCountsChecked: [4, 8, 10], spreadFloor: 3, sample: environmentFor(4, 7) },
};
for (const nodes of [4, 5]) {
  const flat: FailureEnvironment = { weights: Array(nodes).fill(1), values: Array(nodes).fill(1) };
  const env = environmentFor(nodes, 7);
  const universe = pairs(nodes);
  for (let mask = 0; mask < (1 << universe.length); mask++) {
    const graph = { nodes, edges: universe.filter((_edge, index) => mask & (1 << index)) };
    if (!connected(graph)) continue;
    heterogeneous.graphsChecked++;
    // Flat profiles must reproduce the v1 instrument exactly, at every horizon.
    for (const seed of randomSeeds) for (const kind of ["random", "targeted"] as const) {
      const v2 = simulateHeterogeneous(graph, flat, { kind, seed, steps: nodes - 2 });
      const v1 = simulate(graph, { kind, seed, steps: nodes - 2 });
      heterogeneous.maxReductionError = Math.max(heterogeneous.maxReductionError, Math.abs(v2.metrics.auc - v1.metrics.auc));
      require(JSON.stringify(v2.trajectory.map((p) => [p.removed, p.service])) === JSON.stringify(v1.trajectory.map((p) => [p.removed, p.service])), "flat reduction trajectory mismatch");
      heterogeneous.flatReductions++;
    }
    // Heterogeneous trajectories stay legal and track value-fraction service.
    const het = simulateHeterogeneous(graph, env, { kind: "random", seed: 11, steps: nodes - 2 });
    const totalValue = env.values.reduce((a, b) => a + b, 0);
    let live = (1 << nodes) - 1;
    for (const [index, point] of het.trajectory.entries()) {
      require(point.step === index, "v2 step mismatch");
      if (index > 0) require((live & (1 << point.removed!)) !== 0, "v2 node removed twice");
      if (index > 0) live &= ~(1 << point.removed!);
      const expected = largestValue(graph, live, env.values);
      const error = Math.abs(point.service - expected / totalValue);
      heterogeneous.maxServiceError = Math.max(heterogeneous.maxServiceError, error);
      require(error <= 1e-14, "v2 service mismatch");
      heterogeneous.trajectoryChecks++;
    }
    // The subset DP agrees with exhaustive weighted-order enumeration.
    for (let steps = 1; steps <= nodes - 2; steps++) {
      const error = Math.abs(exactWeightedAuc(graph, env, steps) - weightedOrderExpectation(graph, env, steps));
      heterogeneous.maxAucError = Math.max(heterogeneous.maxAucError, error);
      require(error <= 1e-12, "weighted oracle disagrees with order enumeration");
      heterogeneous.oracleComparisons++;
      heterogeneous.maxCeilingSlack = Math.max(heterogeneous.maxCeilingSlack, weightedServiceAucCeiling(env, nodes, steps) - exactWeightedAuc(graph, env, steps));
      require(exactWeightedAuc(graph, env, steps) <= weightedServiceAucCeiling(env, nodes, steps) + 1e-12, "weighted ceiling violated");
    }
  }
}
for (const seed of [7, 8]) for (const nodes of [4, 8, 10]) {
  const env = environmentFor(nodes, seed);
  require(env.weights.length === nodes && env.values.length === nodes, "environment size");
  for (const entries of [env.weights, env.values]) {
    require(entries.every((v) => Number.isInteger(v) && v >= 1 && v <= 5), "environment bounds");
    require(Math.max(...entries) - Math.min(...entries) >= 3, "environment spread guard");
  }
}
const envSample = environmentFor(6, 7);
require(JSON.stringify(envSample) === JSON.stringify(environmentFor(6, 7)), "environment derivation unstable");
require(JSON.stringify(envSample) !== JSON.stringify(environmentFor(6, 8)), "environment seed ignored");

function permutations(values: number[]): number[][] {
  if (values.length === 0) return [[]];
  return values.flatMap((value, index) => permutations(values.filter((_v, i) => i !== index)).map((tail) => [value, ...tail]));
}
const cycle: Graph = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]] };
const labelSensitivity = [1, 2, 3, 4].map((steps) => {
  const distribution: Record<string, number> = {};
  for (const labels of permutations([0, 1, 2, 3, 4, 5])) {
    const graph = { nodes: 6, edges: cycle.edges.map(([a, b]) => [labels[a]!, labels[b]!] as [number, number]) };
    const key = `${aucNumerator(targeted(graph).largest, steps)}/${12 * steps}`;
    distribution[key] = (distribution[key] ?? 0) + 1;
  }
  return { steps, labelings: 720, targetedAucDistribution: distribution };
});

function recursiveTrees(nodes: number): Graph[] {
  let trees: Graph[] = [{ nodes, edges: [] }];
  for (let node = 1; node < nodes; node++) trees = trees.flatMap((tree) => Array.from({ length: node }, (_, parent) => ({ nodes, edges: [...tree.edges, [parent, node] as [number, number]] })));
  return trees;
}
function choose<T>(values: T[], count: number): T[][] {
  if (count === 0) return [[]];
  if (count > values.length) return [];
  return values.flatMap((value, index) => choose(values.slice(index + 1), count - 1).map((tail) => [value, ...tail]));
}

const sampling = [];
const seedCount = 10000;
for (const [nodes, edges] of [[5, 4], [5, 6], [6, 5], [6, 7]] as const) {
  const budget = budgets.get(`${nodes}:${edges}`)!;
  const construction: Record<string, number> = {};
  let constructionCount = 0;
  for (const tree of recursiveTrees(nodes)) {
    const absent = pairs(nodes).filter(([a, b]) => !tree.edges.some(([x, y]) => a === x && b === y));
    for (const extra of choose(absent, edges - (nodes - 1))) {
      const degrees = signature({ nodes, edges: [...tree.edges, ...extra] });
      construction[degrees] = (construction[degrees] ?? 0) + 1;
      constructionCount++;
    }
  }
  const empirical: Record<string, number> = {};
  let mutationsUnchanged = 0;
  for (let seed = 0; seed < seedCount; seed++) {
    const graph = randomGraph(nodes, edges, seed);
    require(graph.nodes === nodes && graph.edges.length === edges && connected(graph), "generated invalid design");
    const degrees = signature(graph);
    empirical[degrees] = (empirical[degrees] ?? 0) + 1;
    const mutated = mutateGraph(graph, (seed ^ 0xa5a5a5a5) >>> 0);
    require(mutated.nodes === nodes && mutated.edges.length === edges && connected(mutated), "mutated invalid design");
    if (JSON.stringify(graph) === JSON.stringify(mutated)) mutationsUnchanged++;
    const from = new Set(graph.edges.map(([a, b]) => `${Math.min(a, b)}:${Math.max(a, b)}`));
    const to = new Set(mutated.edges.map(([a, b]) => `${Math.min(a, b)}:${Math.max(a, b)}`));
    require(to.size === edges, "mutated duplicate edges");
    require([...from].filter((edge) => !to.has(edge)).length <= 1 && [...to].filter((edge) => !from.has(edge)).length <= 1, "mutation changed more than one edge");
  }
  const frequencies = Object.keys(budget.signatures).map((degrees) => ({ degrees, uniform: budget.signatures[degrees]! / budget.graphs,
    construction: (construction[degrees] ?? 0) / constructionCount, empirical: (empirical[degrees] ?? 0) / seedCount }));
  sampling.push({ nodes, edges, uniformGraphCount: budget.graphs, constructionCount, seeds: { first: 0, last: seedCount - 1 }, mutationsUnchanged,
    degreeDistributionDistanceFromUniform: frequencies.reduce((sum, row) => sum + Math.abs(row.uniform - row.construction), 0) / 2,
    treePathAndStarFrequencies: edges === nodes - 1 ? frequencies.filter((row) => row.degrees.startsWith(`${nodes - 1},`) || row.degrees.startsWith("2,")) : [] });
}

require(sources.instrument === await readFile(new URL("../src/network.ts", import.meta.url), "utf8"), "instrument changed during qualification");
require(sources.heterogeneous === await readFile(new URL("../src/heterogeneous.ts", import.meta.url), "utf8"), "heterogeneous instrument changed during qualification");
require(sources.oracle === await readFile(new URL("../src/oracle.ts", import.meta.url), "utf8"), "oracle changed during qualification");
const evidence = JSON.stringify({
  contract: "algal.lab.network-qualification.v2", runtime: { bun: Bun.version },
  sourceSha256: Object.fromEntries(Object.entries(sources).map(([name, source]) => [name, sha(source)])),
  connectedGraphs: counts, totalGraphs: Object.values(counts).reduce((a, b) => a + b, 0), trajectoryComparisons: comparisons,
  maxAucError, maxServiceError, randomSeeds,
  heterogeneous,
  scope: "Independent union-find validates all targeted horizons and five random trajectories per connected labeled n=4..6 graph. Under network.v2, flat profiles reproduce v1 trajectories exhaustively at n=4,5; value-fraction service is checked against an independent value-weighted disjoint set; and the weighted subset-DP oracle agrees with exhaustive weighted removal-order enumeration at n=4,5. Random removal validity and numerical consequences are checked; its PRNG sequence is not independently derived.",
  smallGraphOptima: [...budgets.values()].filter((row) => row.nodes >= 5 && row.edges <= row.nodes + 1).map(({ signatures: _omit, ...row }) => row),
  sixCycleLabelSensitivity: labelSensitivity, sampling,
  limits: "Discrete-model numerical consistency, not physical validity. Uniform-random optima use the independently tested full-distribution oracle, not finite discovery seeds; weighted optima likewise use the independently enumerated subset DP. Construction frequencies assume independent uniform choices; empirical frequencies use the listed deterministic seed range. Degree-distribution distance is not a complete topology-distribution distance.",
}, null, 2) + "\n";
if (outputPath === undefined) process.stdout.write(evidence);
else {
  // Like run directories, evidence files are never overwritten: choose a new path to rerun.
  await mkdir(dirname(outputPath), { recursive: true });
  try { await writeFile(outputPath, evidence, { flag: "wx", mode: 0o600 }); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === "EEXIST") throw new Error(`${outputPath} already exists; choose a new output path (evidence files are never overwritten)`);
    throw error;
  }
  console.error(`instrument qualification written to ${outputPath}`);
}
