/** Fixed, bounded numerical qualification; prints compact JSON evidence.
 * Run with `bun scripts/qualify-instrument.ts`. No provider, credentials, or
 * generated fixture corpus is needed. The subject instrument remains unchanged.
 */
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { simulate, randomGraph, mutateGraph, type Graph } from "../src/network";
import { exactRandomAuc } from "../src/oracle";

if (process.argv.length !== 2) throw new Error("qualification takes no arguments; exhaustive scope is fixed at n=4,5,6");
const sha = (source: string): string => createHash("sha256").update(source).digest("hex");
const sources = {
  instrument: await readFile(new URL("../src/network.ts", import.meta.url), "utf8"),
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
require(sources.oracle === await readFile(new URL("../src/oracle.ts", import.meta.url), "utf8"), "oracle changed during qualification");
console.log(JSON.stringify({
  contract: "algal.lab.network-qualification.v1", runtime: { bun: Bun.version },
  sourceSha256: Object.fromEntries(Object.entries(sources).map(([name, source]) => [name, sha(source)])),
  connectedGraphs: counts, totalGraphs: Object.values(counts).reduce((a, b) => a + b, 0), trajectoryComparisons: comparisons,
  maxAucError, maxServiceError, randomSeeds,
  scope: "Independent union-find validates all targeted horizons and five random trajectories per connected labeled n=4..6 graph. Random removal validity and numerical consequences are checked; its PRNG sequence is not independently derived.",
  smallGraphOptima: [...budgets.values()].filter((row) => row.nodes >= 5 && row.edges <= row.nodes + 1).map(({ signatures: _omit, ...row }) => row),
  sixCycleLabelSensitivity: labelSensitivity, sampling,
  limits: "Discrete-model numerical consistency, not physical validity. Uniform-random optima use the independently tested full-distribution oracle, not finite discovery seeds. Construction frequencies assume independent uniform choices; empirical frequencies use the listed deterministic seed range. Degree-distribution distance is not a complete topology-distribution distance.",
}, null, 2));
