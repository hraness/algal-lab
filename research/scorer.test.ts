import { expect, test } from "bun:test";
import { environmentFor } from "../src/heterogeneous";
import { exactWeightedAuc, weightedServiceAucCeiling } from "../src/oracle";
import { parseGraph, randomGraph } from "../src/network";
import { compileObjective } from "./scorer";

test("compiled expectation agrees with independent union-find oracle on all small connected graphs", () => {
  let comparisons = 0;
  for (const nodes of [4, 5]) {
    const pairs: [number, number][] = [];
    for (let a = 0; a < nodes; a++) for (let b = a + 1; b < nodes; b++) pairs.push([a, b]);
    const environment = environmentFor(nodes, 1907);
    const objectives = Array.from({ length: nodes - 2 }, (_, i) => compileObjective(environment, i + 1));
    for (let mask = 0; mask < 1 << pairs.length; mask++) {
      let graph;
      try { graph = parseGraph({ nodes, edges: pairs.filter((_, i) => mask & (1 << i)) }); }
      catch { continue; }
      for (const objective of objectives) {
        expect(Math.abs(objective.score(graph) - exactWeightedAuc(graph, environment, objective.steps))).toBeLessThan(2e-14);
        comparisons++;
      }
    }
  }
  expect(comparisons).toBe(2260);
});

test("larger heterogeneous cases, near-terminal horizons, and captured environment remain valid", () => {
  for (const nodes of [8, 10]) {
    for (const steps of [1, 3, nodes - 2]) {
      const environment = environmentFor(nodes, 2909 + steps);
      const objective = compileObjective(environment, steps);
      expect(Math.abs(objective.ceiling - weightedServiceAucCeiling(environment, nodes, steps))).toBeLessThan(2e-14);
      for (let seed = 0; seed < 12; seed++) {
        const graph = randomGraph(nodes, nodes - 1 + seed % 4, seed + 3907);
        const expected = exactWeightedAuc(graph, environment, steps);
        expect(Math.abs(objective.score(graph) - expected)).toBeLessThan(2e-14);
      }
      const graph = randomGraph(nodes, nodes, 4903);
      const before = objective.score(graph);
      environment.values.fill(99);
      objective.environment.weights.fill(99);
      objective.environment.values.fill(99);
      expect(objective.score(graph)).toBe(before);
    }
  }
});

test("compiled evaluator rejects mismatched candidates and unbounded requests", () => {
  const environment = environmentFor(4, 12);
  expect(() => compileObjective(environment, 3)).toThrow();
  expect(() => compileObjective({ weights: [1], values: [1] }, 1)).toThrow();
  expect(() => compileObjective(environment, 1).score(randomGraph(5, 5, 0))).toThrow();
});
