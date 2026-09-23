import { describe, expect, test } from "bun:test";
import type { Graph } from "./network";
import { exactRandomAuc, exactWeightedAuc, serviceAucCeiling, weightedServiceAucCeiling } from "./oracle";

function complete(nodes: number): Graph {
  const edges: [number, number][] = [];
  for (let a = 0; a < nodes; a++) for (let b = a + 1; b < nodes; b++) edges.push([a, b]);
  return { nodes, edges };
}

const path = (nodes: number): Graph => ({ nodes, edges: Array.from({ length: nodes - 1 }, (_, a) => [a, a + 1]) });
const star = (nodes: number): Graph => ({ nodes, edges: Array.from({ length: nodes - 1 }, (_, a) => [0, a + 1]) });

// A third algorithm for test evidence: Boolean transitive closure, independent
// of both the instrument's breadth-first search and the oracle's disjoint sets.
function largestByClosure(graph: Graph, removed: number[]): number {
  const active = Array.from({ length: graph.nodes }, (_, node) => node).filter((node) => !removed.includes(node));
  const reachable = Array.from({ length: graph.nodes }, (): boolean[] => Array<boolean>(graph.nodes).fill(false));
  for (const node of active) reachable[node]![node] = true;
  for (const [a, b] of graph.edges) if (active.includes(a) && active.includes(b)) {
    reachable[a]![b] = true;
    reachable[b]![a] = true;
  }
  for (const k of active) for (const i of active) for (const j of active) {
    reachable[i]![j] = reachable[i]![j]! || (reachable[i]![k]! && reachable[k]![j]!);
  }
  return Math.max(...active.map((node) => reachable[node]!.filter(Boolean).length));
}

function permutationExpectation(graph: Graph, steps: number): number {
  let weighted = 0;
  let orders = 0;
  const visit = (removed: number[], internalSum: number): void => {
    const current = largestByClosure(graph, removed);
    if (removed.length === steps) {
      weighted += graph.nodes + current + 2 * internalSum;
      orders++;
      return;
    }
    for (let node = 0; node < graph.nodes; node++) if (!removed.includes(node)) {
      visit([...removed, node], internalSum + (removed.length === 0 ? 0 : current));
    }
  };
  visit([], 0);
  return weighted / (2 * graph.nodes * steps * orders);
}

describe("independent random-failure oracle", () => {
  test("complete graphs attain the analytic horizon-specific ceiling", () => {
    for (const nodes of [4, 5, 8, 10]) for (let steps = 1; steps <= nodes - 2; steps++) {
      expect(exactRandomAuc(complete(nodes), steps)).toBeCloseTo(1 - steps / (2 * nodes), 14);
      expect(serviceAucCeiling(nodes, steps)).toBe(1 - steps / (2 * nodes));
    }
    expect(serviceAucCeiling(10, 8)).toBe(0.6);
  });

  test("paths and stars agree with analytical expectations", () => {
    expect(exactRandomAuc(path(4), 2)).toBe(21 / 32);
    expect(exactRandomAuc(path(5), 3)).toBe(43 / 75);
    expect(exactRandomAuc(star(5), 3)).toBe(44 / 75);
    expect(exactRandomAuc(star(6), 4)).toBe(13 / 24);
    // With k survivors in an n-star, expected LCC = 1 + (k*k-k)/n.
    for (const nodes of [4, 8, 10]) {
      const steps = nodes - 2;
      const services = Array.from({ length: steps + 1 }, (_, step) => {
        const survivors = nodes - step;
        return (1 + (survivors * survivors - survivors) / nodes) / nodes;
      });
      const integral = (services[0]! + services[steps]! + 2 * services.slice(1, steps).reduce((a, b) => a + b, 0)) / (2 * steps);
      expect(exactRandomAuc(star(nodes), steps)).toBeCloseTo(integral, 14);
    }
  });

  test("all connected n=4,5 graphs agree with every ordered failure permutation", () => {
    const counts: number[] = [];
    let horizons = 0;
    for (const nodes of [4, 5]) {
      const universe = complete(nodes).edges;
      let connected = 0;
      for (let mask = 0; mask < (1 << universe.length); mask++) {
        const graph = { nodes, edges: universe.filter((_edge, index) => mask & (1 << index)) };
        if (largestByClosure(graph, []) !== nodes) continue;
        connected++;
        for (let steps = 1; steps <= nodes - 2; steps++) {
          expect(exactRandomAuc(graph, steps)).toBeCloseTo(permutationExpectation(graph, steps), 14);
          horizons++;
        }
      }
      counts.push(connected);
    }
    expect(counts).toEqual([38, 728]);
    expect(horizons).toBe(2260);
  });

  test("expectation is invariant under relabeling and edge representation", () => {
    const original = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]] as [number, number][] };
    const labels = [3, 1, 5, 0, 4, 2];
    const relabeled = { nodes: 6, edges: original.edges.map(([a, b]) => [labels[b]!, labels[a]!] as [number, number]).reverse() };
    const before = JSON.stringify(relabeled);
    for (let steps = 1; steps <= 4; steps++) expect(exactRandomAuc(relabeled, steps)).toBe(exactRandomAuc(original, steps));
    expect(JSON.stringify(relabeled)).toBe(before);
  });

  test("admission independently rejects invalid or over-budget inputs", () => {
    for (const graph of [
      null, [], {}, { ...path(4), ignored: true }, path(3), path(11),
      { nodes: 4, edges: [[0, 1], [1, 0], [2, 3]] },
      { nodes: 4, edges: [[0, 0], [0, 1], [2, 3]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [2, 4]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [2, 3.5]] },
      { nodes: 4, edges: [[0, 1, 2], [1, 2], [2, 3]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [0, 2]] },
      { nodes: 4, edges: [[0, 1], [2, 3]] },
    ]) expect(() => exactRandomAuc(graph as Graph, 1)).toThrow();
    for (const steps of [0, 3, -1, 1.5, NaN, Infinity]) {
      expect(() => exactRandomAuc(path(4), steps)).toThrow();
      expect(() => serviceAucCeiling(4, steps)).toThrow();
    }
    for (const nodes of [3, 11, 4.5, NaN, Infinity]) expect(() => serviceAucCeiling(nodes, 1)).toThrow();
  });
});

function largestValueByClosure(graph: Graph, removed: number[], values: readonly number[]): number {
  const active = Array.from({ length: graph.nodes }, (_, node) => node).filter((node) => !removed.includes(node));
  const reachable = Array.from({ length: graph.nodes }, (): boolean[] => Array<boolean>(graph.nodes).fill(false));
  for (const node of active) reachable[node]![node] = true;
  for (const [a, b] of graph.edges) if (active.includes(a) && active.includes(b)) {
    reachable[a]![b] = true;
    reachable[b]![a] = true;
  }
  for (const k of active) for (const i of active) for (const j of active) {
    reachable[i]![j] = reachable[i]![j]! || (reachable[i]![k]! && reachable[k]![j]!);
  }
  const seen = new Set<number>();
  let best = 0;
  for (const node of active) {
    if (seen.has(node)) continue;
    let total = 0;
    for (const other of active) if (reachable[node]![other]) { seen.add(other); total += values[other]!; }
    best = Math.max(best, total);
  }
  return best;
}

/** Every weighted removal order, independently: P(order) multiplies w_i over
 * remaining weight; the expectation adds the trapezoid numerator per order. */
function weightedPermutationExpectation(graph: Graph, env: { weights: readonly number[]; values: readonly number[] }, steps: number): number {
  const V = env.values.reduce((a, b) => a + b, 0);
  const W = env.weights.reduce((a, b) => a + b, 0);
  let total = 0;
  const visit = (removed: number[], removedWeight: number, prob: number, partial: number): void => {
    const k = removed.length;
    const service = largestValueByClosure(graph, removed, env.values) / V;
    const coefficient = k === 0 || k === steps ? 0.5 : 1;
    if (k === steps) { total += prob * (partial + coefficient * service); return; }
    for (let node = 0; node < graph.nodes; node++) if (!removed.includes(node)) {
      visit([...removed, node], removedWeight + env.weights[node]!, prob * env.weights[node]! / (W - removedWeight), partial + coefficient * service);
    }
  };
  visit([], 0, 1, 0);
  return total / steps;
}

describe("heterogeneous-failure oracle", () => {
  const envs = [
    { weights: [1, 1, 1, 1], values: [1, 1, 1, 1] },
    { weights: [5, 1, 2, 3], values: [4, 1, 2, 1] },
    { weights: [1, 4, 1, 4], values: [3, 1, 3, 1] },
  ];
  const graphs = [path(4), star(4), complete(4)];

  test("flat environments reduce to the uniform-random oracle exactly", () => {
    const flat = (nodes: number) => ({ weights: Array(nodes).fill(1), values: Array(nodes).fill(1) });
    for (const graph of [path(4), star(4), complete(4), path(5), star(5)]) for (let steps = 1; steps <= graph.nodes - 2; steps++) {
      expect(exactWeightedAuc(graph, flat(graph.nodes), steps)).toBeCloseTo(exactRandomAuc(graph, steps), 15);
      expect(weightedServiceAucCeiling(flat(graph.nodes), graph.nodes, steps)).toBeCloseTo(serviceAucCeiling(graph.nodes, steps), 15);
    }
  });

  test("the subset DP matches exhaustive weighted-order enumeration", () => {
    for (const env of envs) for (const graph of graphs) for (let steps = 1; steps <= graph.nodes - 2; steps++) {
      expect(exactWeightedAuc(graph, env, steps)).toBeCloseTo(weightedPermutationExpectation(graph, env, steps), 12);
    }
  });

  test("the weighted ceiling bounds every graph's exact AUC and is reachable for the complete graph", () => {
    for (const env of envs) for (const graph of graphs) for (let steps = 1; steps <= graph.nodes - 2; steps++) {
      expect(exactWeightedAuc(graph, env, steps)).toBeLessThanOrEqual(weightedServiceAucCeiling(env, graph.nodes, steps) + 1e-12);
    }
    for (const env of envs) for (let steps = 1; steps <= 2; steps++) {
      expect(exactWeightedAuc(complete(4), env, steps)).toBeCloseTo(weightedServiceAucCeiling(env, 4, steps), 12);
    }
  });

  test("environment admission and graph bounds mirror the uniform oracle", () => {
    const env = { weights: [1, 2, 3, 4], values: [1, 2, 3, 4] };
    expect(() => exactWeightedAuc(path(11), { weights: Array(11).fill(1), values: Array(11).fill(1) }, 1)).toThrow();
    expect(() => exactWeightedAuc(path(4), { weights: [1, 1, 1], values: [1, 1, 1, 1] }, 1)).toThrow();
    expect(() => exactWeightedAuc(path(4), { weights: [1, 0, 1, 1], values: [1, 1, 1, 1] }, 1)).toThrow();
    expect(() => exactWeightedAuc(path(4), { weights: [1, 1, 1, 1], values: [1, 1.5, 1, 1] }, 1)).toThrow();
    expect(() => weightedServiceAucCeiling(env, 11, 1)).toThrow();
    expect(() => weightedServiceAucCeiling(env, 4, 0)).toThrow();
  });
});
