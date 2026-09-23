import { expect, test } from "bun:test";
import { environmentFor } from "../../../src/heterogeneous";
import { parseGraph } from "../../../src/network";
import { admitPolicy, construct, fixedPairPolicy, search, theoremStar } from "./policy";

test("constructor preserves exact connected budgets and reproduces its random stream", () => {
  for (const nodes of [4, 8, 10]) for (const seed of [3, 17, 211]) for (const surplus of [0, 1, 2]) {
    const environment = environmentFor(nodes, seed);
    const edges = Math.min(nodes - 1 + surplus, nodes * (nodes - 1) / 2);
    const graph = construct(fixedPairPolicy, environment, edges, seed);
    expect(parseGraph(graph)).toEqual(graph);
    expect(graph.edges.length).toBe(edges);
    expect(construct(fixedPairPolicy, environment, edges, seed)).toEqual(graph);
  }
});

test("best-so-far survives forced restarts and every duplicate consumes an evaluation", () => {
  const environment = environmentFor(4, 3);
  let calls = 0;
  const result = search("policy", { ...fixedPairPolicy, noise: 0, restart: 1 }, environment, 3, 19, 12, () => {
    calls++; return calls === 1 ? 0.9 : 0.4;
  });
  expect(calls).toBe(12);
  expect(result.evaluations).toBe(12);
  expect(result.duplicateProposals).toBe(11);
  expect(result.score).toBe(0.9);
  expect(result.bestByEvaluation).toEqual(Array(12).fill(0.9));
});

test("failure-inclusive accounting keeps failed objective slots", () => {
  let calls = 0;
  const result = search("random-search", fixedPairPolicy, environmentFor(4, 11), 3, 7, 8, () => {
    calls++;
    if (calls === 3) throw new Error("deliberate objective failure");
    return 0.6;
  });
  expect(calls).toBe(8);
  expect(result.evaluations).toBe(8);
  expect(result.failures).toHaveLength(1);
  expect(result.bestByEvaluation).toHaveLength(8);
});

test("policy admission rejects executable or out-of-grammar data; known one-deletion star center", () => {
  expect(() => admitPolicy({ ...fixedPairPolicy, run: "arbitrary code" })).toThrow();
  expect(() => admitPolicy({ ...fixedPairPolicy, risk: NaN })).toThrow();
  expect(() => admitPolicy(Object.assign(Object.create({ inherited: true }), fixedPairPolicy))).toThrow();
  expect(() => admitPolicy({ ...fixedPairPolicy, [Symbol("unknown")]: true })).toThrow();
  expect(() => admitPolicy({ ...fixedPairPolicy, get risk() { throw new Error("getter must not execute"); } })).toThrow("policy fields must be data");
  const graph = theoremStar({ weights: [10, 10, 1, 1], values: [99, 99, 1, 1] }, 3);
  expect(graph.edges).toEqual([[0, 1], [0, 2], [0, 3]]);
});

test("constructors reject invalid environment, edge count, and seed before construction", () => {
  const environment = environmentFor(4, 3);
  for (const edges of [NaN, Infinity, 2, 3.5, 7]) {
    expect(() => construct(fixedPairPolicy, environment, edges, 3)).toThrow();
    expect(() => theoremStar(environment, edges)).toThrow();
  }
  expect(() => construct(fixedPairPolicy, { weights: [1, 2, 0, 4], values: [1, 2, 3, 4] }, 3, 3)).toThrow();
  expect(() => theoremStar({ weights: [1, 2, 3, 4], values: [1, 2, NaN, 4] }, 3)).toThrow();
  expect(() => construct(fixedPairPolicy, environment, 3, 1.5)).toThrow();
});
