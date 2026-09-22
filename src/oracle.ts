import type { Graph } from "./network";

/** Qualification only: exact uniform-random failure expectation on small graphs.
 * This module imports no numerical implementation from the simulator. It uses
 * disjoint-set connectivity and integer-weighted integration of every live
 * subset, rather than a seeded trajectory. It is not a physical validity claim
 * or an exclusively held-out measurement: it includes the full distribution.
 */
export const EXACT_RANDOM_MAX_NODES = 10;

function bounds(nodes: number, steps: number): void {
  if (!Number.isInteger(nodes) || nodes < 4 || nodes > EXACT_RANDOM_MAX_NODES) {
    throw new Error(`oracle nodes must be an integer in 4..${EXACT_RANDOM_MAX_NODES}`);
  }
  if (!Number.isInteger(steps) || steps < 1 || steps > nodes - 2) {
    throw new Error("oracle steps must be an integer in 1..nodes-2");
  }
}

function largest(graph: Graph, active: number): number {
  const parent = Array.from({ length: graph.nodes }, (_, node) => node);
  const root = (initial: number): number => {
    let node = initial;
    while (parent[node] !== node) node = parent[node]!;
    return node;
  };
  for (const [a, b] of graph.edges) {
    if ((active & (1 << a)) !== 0 && (active & (1 << b)) !== 0) parent[root(b)] = root(a);
  }
  const sizes = Array<number>(graph.nodes).fill(0);
  for (let node = 0; node < graph.nodes; node++) {
    if ((active & (1 << node)) !== 0) sizes[root(node)]!++;
  }
  return Math.max(...sizes);
}

function admit(value: Graph, steps: number): Graph {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("oracle graph must be an object");
  const prototype: unknown = Object.getPrototypeOf(value);
  const keys = Reflect.ownKeys(value);
  if ((prototype !== Object.prototype && prototype !== null) || keys.length !== 2 || !keys.includes("nodes") || !keys.includes("edges")) {
    throw new Error("oracle graph requires exactly nodes and edges");
  }
  bounds(value.nodes, steps);
  const maximum = value.nodes * (value.nodes - 1) / 2;
  if (!Array.isArray(value.edges) || value.edges.length < value.nodes - 1 || value.edges.length > maximum) {
    throw new Error("oracle graph edge count is out of bounds");
  }
  const seen = new Set<string>();
  const edges: [number, number][] = [];
  for (const edge of value.edges) {
    if (!Array.isArray(edge) || edge.length !== 2 || !edge.every((node) => Number.isInteger(node) && node >= 0 && node < value.nodes)) {
      throw new Error("oracle graph edges must be pairs of admitted node IDs");
    }
    const [a, b] = edge;
    if (a === b) throw new Error("oracle graph cannot contain a self loop");
    const key = [a, b].sort((x, y) => x - y).join(":");
    if (seen.has(key)) throw new Error("oracle graph cannot contain duplicate edges");
    seen.add(key);
    edges.push([a, b]);
  }
  const graph = { nodes: value.nodes, edges };
  if (largest(graph, (1 << graph.nodes) - 1) !== graph.nodes) throw new Error("oracle graph must initially be connected");
  return graph;
}

function popcount(value: number): number {
  let remaining = value;
  let count = 0;
  while (remaining !== 0) { remaining &= remaining - 1; count++; }
  return count;
}

function gcd(left: number, right: number): number {
  let a = left;
  let b = right;
  while (b !== 0) [a, b] = [b, a % b];
  return a;
}

/** Exact expectation under uniform node removal without replacement.
 * At step t, every surviving subset of size n-t is equally likely. Linearity
 * lets us integrate their expected component sizes without enumerating all
 * removal orders. At the maximum n=10,h=8 this examines 1,013 subsets including
 * the intact state. All weighted sums are exact integers; only the final AUC
 * division uses floating point.
 */
export function exactRandomAuc(input: Graph, steps: number): number {
  const graph = admit(input, steps);
  const sums = Array<number>(steps + 1).fill(0);
  const counts = Array<number>(steps + 1).fill(0);
  for (let active = 1; active < (1 << graph.nodes); active++) {
    const step = graph.nodes - popcount(active);
    if (step > steps) continue;
    sums[step]! += largest(graph, active);
    counts[step]!++;
  }
  let common = 1;
  for (const count of counts) common = common * count / gcd(common, count);
  let weighted = 0;
  for (let step = 0; step <= steps; step++) {
    weighted += (step === 0 || step === steps ? 1 : 2) * sums[step]! * (common / counts[step]!);
  }
  return weighted / (2 * graph.nodes * steps * common);
}

/** Maximum possible AUC when every surviving graph remains connected. */
export function serviceAucCeiling(nodes: number, steps: number): number {
  bounds(nodes, steps);
  return 1 - steps / (2 * nodes);
}
