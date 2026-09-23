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

// ---------------- heterogeneous failure (network.v2) ----------------

export type WeightedEnvironment = { weights: readonly number[]; values: readonly number[] };

function admitEnvironment(value: WeightedEnvironment, nodes: number): WeightedEnvironment {
  const read = (input: readonly number[], label: string): number[] => {
    if (!Array.isArray(input) || input.length !== nodes) throw new Error(`oracle ${label}: expected ${nodes} entries`);
    return input.map((entry) => {
      if (typeof entry !== "number" || !Number.isInteger(entry) || entry < 1 || entry > 99) throw new Error(`oracle ${label}: expected integers in 1..99`);
      return entry;
    });
  };
  return { weights: read(value.weights, "weights"), values: read(value.values, "values") };
}

/** Value sum of the most valuable component among `active`, by union-find. */
function largestValue(graph: Graph, active: number, values: readonly number[]): number {
  const parent = Array.from({ length: graph.nodes }, (_, node) => node);
  const root = (initial: number): number => {
    let node = initial;
    while (parent[node] !== node) node = parent[node]!;
    return node;
  };
  for (const [a, b] of graph.edges) {
    if ((active & (1 << a)) !== 0 && (active & (1 << b)) !== 0) parent[root(b)] = root(a);
  }
  const sums = new Map<number, number>();
  for (let node = 0; node < graph.nodes; node++) {
    if ((active & (1 << node)) !== 0) sums.set(root(node), (sums.get(root(node)) ?? 0) + values[node]!);
  }
  return Math.max(0, ...sums.values());
}

/**
 * Exact expectation under weighted sequential removal without replacement.
 * f(S) = P(the removed set after |S| steps is exactly S), by subset DP:
 * f(S) = sum_{i in S} f(S\{i}) * w_i / (W - w(S\{i})). Expected service at
 * step k = sum_{|S|=k} f(S) * (best component value of V\S) / V_total,
 * integrated as a trapezoid over k = 0..steps.
 */
export function exactWeightedAuc(input: Graph, environment: WeightedEnvironment, steps: number): number {
  const graph = admit(input, steps);
  const env = admitEnvironment(environment, graph.nodes);
  const size = 1 << graph.nodes;
  const full = size - 1;
  const totalWeight = env.weights.reduce((a, b) => a + b, 0);
  const totalValue = env.values.reduce((a, b) => a + b, 0);
  // Removed-set probabilities, popcount order.
  const weightOf = new Float64Array(size);
  for (let mask = 1; mask < size; mask++) {
    const bit = mask & -mask;
    const node = 31 - Math.clz32(bit);
    weightOf[mask] = weightOf[mask & ~bit]! + env.weights[node]!;
  }
  const probability = new Float64Array(size);
  probability[0] = 1;
  for (let mask = 1; mask < size; mask++) {
    let acc = 0, rest = mask;
    while (rest) {
      const bit = rest & -rest;
      const node = 31 - Math.clz32(bit);
      const prev = mask & ~bit;
      acc += probability[prev]! * env.weights[node]! / (totalWeight - weightOf[prev]!);
      rest &= ~bit;
    }
    probability[mask] = acc;
  }
  let weighted = 0;
  for (let mask = 0; mask < size; mask++) {
    const removed = popcount(mask);
    if (removed > steps) continue;
    const service = largestValue(graph, full & ~mask, env.values) / totalValue;
    const coefficient = removed === 0 || removed === steps ? 1 : 2;
    weighted += coefficient * probability[mask]! * service;
  }
  return weighted / (2 * steps);
}

/** Maximum possible weighted AUC when every surviving graph stays connected:
 * service then equals the surviving value fraction. Tight upper bound. */
export function weightedServiceAucCeiling(environment: WeightedEnvironment, nodes: number, steps: number): number {
  bounds(nodes, steps);
  const env = admitEnvironment(environment, nodes);
  const size = 1 << nodes;
  const totalWeight = env.weights.reduce((a, b) => a + b, 0);
  const totalValue = env.values.reduce((a, b) => a + b, 0);
  const weightOf = new Float64Array(size);
  for (let mask = 1; mask < size; mask++) {
    const bit = mask & -mask;
    weightOf[mask] = weightOf[mask & ~bit]! + env.weights[31 - Math.clz32(bit)]!;
  }
  const valueOf = new Float64Array(size);
  for (let mask = 1; mask < size; mask++) {
    const bit = mask & -mask;
    valueOf[mask] = valueOf[mask & ~bit]! + env.values[31 - Math.clz32(bit)]!;
  }
  const probability = new Float64Array(size);
  probability[0] = 1;
  for (let mask = 1; mask < size; mask++) {
    let acc = 0, rest = mask;
    while (rest) {
      const bit = rest & -rest;
      const node = 31 - Math.clz32(bit);
      const prev = mask & ~bit;
      acc += probability[prev]! * env.weights[node]! / (totalWeight - weightOf[prev]!);
      rest &= ~bit;
    }
    probability[mask] = acc;
  }
  let weighted = 0;
  for (let mask = 0; mask < size; mask++) {
    const removed = popcount(mask);
    if (removed > steps) continue;
    const coefficient = removed === 0 || removed === steps ? 1 : 2;
    weighted += coefficient * probability[mask]! * (1 - valueOf[mask]! / totalValue);
  }
  return weighted / (2 * steps);
}
