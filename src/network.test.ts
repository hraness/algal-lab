import { describe, expect, test } from "bun:test";
import { mutateGraph, parseGraph, parseSchedule, randomGraph, simulate, type Graph } from "./network";

const path: Graph = { nodes: 4, edges: [[0, 1], [1, 2], [2, 3]] };
const complete: Graph = { nodes: 4, edges: [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]] };

describe("network instrument", () => {
  test("complete graph has analytic service and trapezoidal area", () => {
    const result = simulate(complete, { kind: "targeted", seed: 0, steps: 2 });
    expect(result.trajectory.map((point) => point.removed)).toEqual([null, 0, 1]);
    expect(result.trajectory.map((point) => point.service)).toEqual([1, 3 / 4, 1 / 2]);
    expect(result.metrics).toEqual({ auc: 3 / 4, finalService: 1 / 2 });
    expect(simulate(complete, { kind: "targeted", seed: 5, steps: 1 }).metrics.auc).toBe(7 / 8);
  });

  test("path attack recomputes live degrees and breaks ties by lowest ID", () => {
    const result = simulate(path, { kind: "targeted", seed: 99, steps: 2 });
    expect(result.trajectory).toEqual([
      { step: 0, removed: null, active: [0, 1, 2, 3], largestComponent: 4, service: 1 },
      { step: 1, removed: 1, active: [0, 2, 3], largestComponent: 2, service: 1 / 2 },
      { step: 2, removed: 2, active: [0, 3], largestComponent: 1, service: 1 / 4 },
    ]);
    expect(result.metrics.auc).toBe(9 / 16);
  });

  test("targeted hub failure disconnects a star while a cycle retains service", () => {
    const star: Graph = { nodes: 6, edges: [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]] };
    const cycle: Graph = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]] };
    const schedule = { kind: "targeted" as const, seed: 0, steps: 2 };
    const failedStar = simulate(star, schedule);
    const failedCycle = simulate(cycle, schedule);
    expect(failedStar.trajectory.map((point) => point.largestComponent)).toEqual([6, 1, 1]);
    expect(failedCycle.trajectory.map((point) => point.largestComponent)).toEqual([6, 5, 3]);
    expect(failedStar.metrics.auc).toBeCloseTo(3 / 8, 14);
    expect(failedCycle.metrics.auc).toBeCloseTo(19 / 24, 14);
  });

  test("random schedules are repeatable, bounded, and never remove a node twice", () => {
    const graph = randomGraph(12, 18, 47);
    const schedule = { kind: "random" as const, seed: 0xffff_ffff, steps: 10 };
    const before = JSON.stringify({ graph, schedule });
    const result = simulate(graph, schedule);
    expect(simulate(graph, schedule)).toEqual(result);
    expect(JSON.stringify({ graph, schedule })).toBe(before);
    expect(new Set(result.trajectory.slice(1).map((point) => point.removed)).size).toBe(10);
    for (const point of result.trajectory) {
      expect(point.active.length).toBe(graph.nodes - point.step);
      expect(point.service).toBe(point.largestComponent / graph.nodes);
      expect(point.largestComponent).toBeGreaterThanOrEqual(1);
      expect(point.largestComponent).toBeLessThanOrEqual(point.active.length);
    }
    expect(simulate(graph, { ...schedule, seed: 0 }).trajectory).not.toEqual(result.trajectory);
  });
});

describe("design admission and generation", () => {
  test("admission only normalizes edge orientation and ordering", () => {
    const reversed = { nodes: 4, edges: [[3, 2], [1, 0], [2, 1]] };
    expect(parseGraph(reversed)).toEqual(path);
    expect(reversed.edges).toEqual([[3, 2], [1, 0], [2, 1]]);
  });

  test("random designs preserve the exact edge budget and are repeatable", () => {
    for (const [nodes, edges] of [[4, 3], [4, 6], [12, 11], [12, 33], [24, 23], [24, 96]]) {
      for (const seed of [0, 1, 42, 0xffff_ffff]) {
        const graph = randomGraph(nodes!, edges!, seed);
        expect(graph.nodes).toBe(nodes!);
        expect(graph.edges.length).toBe(edges!);
        expect(parseGraph(graph)).toEqual(graph);
        expect(randomGraph(nodes!, edges!, seed)).toEqual(graph);
      }
    }
  });

  test("bounded mutation preserves connectivity and exact node/edge budgets", () => {
    for (const graph of [path, complete, randomGraph(12, 11, 1), randomGraph(24, 96, 2)]) {
      const before = JSON.stringify(graph);
      for (const seed of [0, 1, 42, 0xffff_ffff]) {
        const mutated = mutateGraph(graph, seed);
        expect(mutated.nodes).toBe(graph.nodes);
        expect(mutated.edges.length).toBe(graph.edges.length);
        expect(parseGraph(mutated)).toEqual(mutated);
        expect(mutateGraph(graph, seed)).toEqual(mutated);
      }
      expect(JSON.stringify(graph)).toBe(before);
    }
    // A complete graph has no admissible absent edge; failure is unchanged data.
    expect(mutateGraph(complete, 0)).toEqual(complete);
    expect(mutateGraph(path, 0)).not.toEqual(path);
  });

  test("malformed graphs reject without silently repairing the design", () => {
    const malformed: unknown[] = [
      null, [], {}, { ...path, extra: true }, { nodes: 3, edges: path.edges },
      { nodes: 25, edges: path.edges }, { nodes: 4.5, edges: path.edges },
      { nodes: 4, edges: [[0, 1], [1, 0], [2, 3]] },
      { nodes: 4, edges: [[0, 0], [0, 1], [2, 3]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [2, 4]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [2, -1]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [2, 3.5]] },
      { nodes: 4, edges: [[0, 1, 2], [1, 2], [2, 3]] },
      { nodes: 4, edges: [[0, 1], [1, 2]] },
      { nodes: 4, edges: [[0, 1], [1, 2], [0, 2]] },
      { nodes: 4, edges: "wrong" },
      { nodes: 24, edges: Array.from({ length: 97 }, () => [0, 1]) },
    ];
    for (const value of malformed) expect(() => parseGraph(value)).toThrow();
    expect(() => simulate(malformed[3] as Graph, { kind: "random", seed: 0, steps: 1 })).toThrow();
  });

  test("malformed schedules and generator bounds reject", () => {
    const valid = { kind: "random", seed: 0, steps: 1 };
    for (const schedule of [
      null, [], {}, { ...valid, extra: true }, { ...valid, kind: "random-ish" },
      { ...valid, seed: -1 }, { ...valid, seed: 2 ** 32 }, { ...valid, seed: 0.5 },
      { ...valid, seed: NaN }, { ...valid, steps: 0 }, { ...valid, steps: 3 },
      { ...valid, steps: 1.5 },
    ]) expect(() => parseSchedule(schedule, 4)).toThrow();
    expect(() => parseSchedule(valid, 3)).toThrow();
    expect(() => randomGraph(3, 3, 0)).toThrow();
    expect(() => randomGraph(4, 2, 0)).toThrow();
    expect(() => randomGraph(4, 7, 0)).toThrow();
    expect(() => randomGraph(24, 97, 0)).toThrow();
    expect(() => randomGraph(4, 3, -1)).toThrow();
    expect(() => mutateGraph(path, 2 ** 32)).toThrow();
  });
});
