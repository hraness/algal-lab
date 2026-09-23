import { expect, test } from "bun:test";
import { environmentFor } from "../src/heterogeneous";
import { exactWeightedAuc } from "../src/oracle";
import type { Graph } from "../src/network";
import { certifiedOptimalTree, optimalSingleFailureTree } from "./optimal-trees";

/** Prüfer decoding enumerates every labeled tree once, independently of solver. */
function trees(nodes: number): Graph[] {
  return Array.from({ length: nodes ** (nodes - 2) }, (_, code) => {
    let remaining = code;
    const sequence = Array.from({ length: nodes - 2 }, () => { const digit = remaining % nodes; remaining = Math.floor(remaining / nodes); return digit; });
    const degrees = Array<number>(nodes).fill(1);
    for (const node of sequence) degrees[node]!++;
    const edges: [number, number][] = [];
    for (const node of sequence) {
      const leaf = degrees.findIndex((degree) => degree === 1);
      edges.push([leaf, node]); degrees[leaf]!--; degrees[node]!--;
    }
    const ends = degrees.flatMap((degree, node) => degree === 1 ? [node] : []);
    edges.push([ends[0]!, ends[1]!]);
    return { nodes, edges };
  });
}

test("one-failure O(n) solver attains exhaustive tree optimum, including tied values", () => {
  for (const nodes of [4, 5, 6]) {
    const candidates = trees(nodes);
    for (let seed = 0; seed < 8; seed++) {
      const env = environmentFor(nodes, seed + 7001);
      const certified = optimalSingleFailureTree(env);
      const expected = certified.auc!.numerator / certified.auc!.denominator;
      expect(Math.abs(exactWeightedAuc(certified.graph, env, 1) - expected)).toBeLessThan(2e-14);
      for (const graph of candidates) expect(exactWeightedAuc(graph, env, 1)).toBeLessThanOrEqual(expected + 2e-14);
    }
  }
});

test("dominant hub is optimal at every admitted horizon on exhaustive six-node trees", () => {
  const env = { weights: [1, 2, 4, 3, 5, 2], values: [9, 2, 3, 4, 1, 2] };
  const candidates = trees(6);
  for (let steps = 1; steps <= 4; steps++) {
    const result = certifiedOptimalTree(env, steps)!;
    expect(result.center).toBe(0);
    const best = exactWeightedAuc(result.graph, env, steps);
    for (const candidate of candidates) expect(exactWeightedAuc(candidate, env, steps)).toBeLessThanOrEqual(best + 2e-14);
  }
});

test("opposed reliability and value leave the theorem guard unresolved, and all stars can lose", () => {
  const env = { weights: [3, 3, 1, 1], values: [6, 6, 1, 1] };
  expect(certifiedOptimalTree(env, 2)).toBeNull();
  const path: Graph = { nodes: 4, edges: [[0, 1], [0, 2], [2, 3]] };
  expect(exactWeightedAuc(path, env, 2)).toBeCloseTo(4941 / 7840, 14);
  let bestStar = 0;
  for (let center = 0; center < 4; center++) {
    const graph: Graph = { nodes: 4, edges: [0, 1, 2, 3].filter((i) => i !== center).map((i) => [center, i]) };
    bestStar = Math.max(bestStar, exactWeightedAuc(graph, env, 2));
  }
  expect(bestStar).toBeCloseTo(4931 / 7840, 14);
  expect(exactWeightedAuc(path, env, 2) - bestStar).toBeCloseTo(1 / 784, 14);
  expect(() => certifiedOptimalTree(env, 3)).toThrow();
});
