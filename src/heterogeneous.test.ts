import { describe, expect, test } from "bun:test";
import { environmentFor, parseEnvironment, simulateHeterogeneous, type FailureEnvironment } from "./heterogeneous";
import { simulate, type Graph } from "./network";

const flat: FailureEnvironment = { weights: [1, 1, 1, 1], values: [1, 1, 1, 1] };
const weighted: FailureEnvironment = { weights: [5, 1, 2, 1], values: [4, 1, 1, 1] };
const path: Graph = { nodes: 4, edges: [[0, 1], [1, 2], [2, 3]] };

describe("heterogeneous environment", () => {
  test("derives deterministically per (nodes, seed) with bounded, spread-guarded entries", () => {
    const env = environmentFor(8, 5003);
    expect(env).toEqual(environmentFor(8, 5003));
    expect(env.weights).toHaveLength(8);
    expect(env.values).toHaveLength(8);
    for (const entries of [env.weights, env.values]) {
      expect(entries.every((v) => Number.isInteger(v) && v >= 1 && v <= 5)).toBe(true);
      expect(Math.max(...entries) - Math.min(...entries)).toBeGreaterThanOrEqual(3);
    }
    expect(environmentFor(8, 5004)).not.toEqual(env);
    expect(environmentFor(10, 5003).weights).toHaveLength(10);
  });

  test("rejects malformed environments and out-of-range parameters", () => {
    expect(() => environmentFor(1, 0)).toThrow();
    expect(() => environmentFor(17, 0)).toThrow();
    expect(() => parseEnvironment({ weights: [1, 1], values: [1] }, 2)).toThrow();
    expect(() => parseEnvironment({ weights: [1, 1], values: [1, 1], extra: 0 }, 2)).toThrow();
    expect(() => parseEnvironment({ weights: [0, 1], values: [1, 1] }, 2)).toThrow();
    expect(() => parseEnvironment({ weights: [1.5, 1], values: [1, 1] }, 2)).toThrow();
    expect(() => parseEnvironment({ weights: [1, 1], values: [1, 1] }, 3)).toThrow();
  });
});

describe("heterogeneous simulator", () => {
  test("flat environment reduces to the v1 instrument trajectory exactly", () => {
    const graph: Graph = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5], [1, 3]] };
    const env: FailureEnvironment = { weights: [1, 1, 1, 1, 1, 1], values: [1, 1, 1, 1, 1, 1] };
    for (const seed of [0, 7, 0xffffffff]) {
      const v2 = simulateHeterogeneous(graph, env, { kind: "random", seed, steps: 4 });
      const v1 = simulate(graph, { kind: "random", seed, steps: 4 });
      expect(v2.trajectory.map((p) => p.removed)).toEqual(v1.trajectory.map((p) => p.removed));
      expect(v2.trajectory.map((p) => p.service)).toEqual(v1.trajectory.map((p) => p.service));
      expect(v2.metrics.auc).toBe(v1.metrics.auc);
      const t2 = simulateHeterogeneous(graph, env, { kind: "targeted", seed, steps: 4 });
      expect(t2.metrics.auc).toBe(simulate(graph, { kind: "targeted", seed, steps: 4 }).metrics.auc);
    }
  });

  test("weighted removal favors high failure weights and service tracks value", () => {
    // Node 0 is both the heaviest (w=5) and the most valuable (v=4 of 7 total).
    const result = simulateHeterogeneous(path, weighted, { kind: "random", seed: 3, steps: 2 });
    expect(result.contract).toBe("algal.lab.network-result.v2");
    expect(result.instrument).toBe("network.v2");
    expect(result.environment).toEqual(weighted);
    expect(result.trajectory[0]).toEqual({ step: 0, removed: null, active: [0, 1, 2, 3], bestComponentValue: 7, service: 1 });
    for (const [index, point] of result.trajectory.entries()) {
      expect(point.step).toBe(index);
      if (index > 0) {
        expect(result.trajectory.slice(0, index).every((p) => p.removed !== point.removed)).toBe(true);
        expect(point.removed).not.toBeNull();
      }
      expect(point.service).toBeCloseTo(point.bestComponentValue / 7, 14);
    }
    expect(result.metrics.auc).toBeGreaterThan(0);
    expect(result.metrics.auc).toBeLessThanOrEqual(1);
    expect(result.metrics.finalService).toBe(result.trajectory.at(-1)!.service);
  });

  test("targeted removal keeps the label-blind max-degree rule", () => {
    // Path 0-1-2-3: node 1 or 2 has max degree 2; lowest ID wins.
    const result = simulateHeterogeneous(path, weighted, { kind: "targeted", seed: 99, steps: 2 });
    expect(result.trajectory.map((p) => p.removed)).toEqual([null, 1, 2]);
    // Removing 1 splits into {0}(v4) and {2,3}(v2); removing 2 leaves {0}(v4).
    expect(result.trajectory.map((p) => p.service)).toEqual([1, 4 / 7, 4 / 7]);
  });

  test("the objective is label-dependent under heterogeneous profiles", () => {
    const cycle: Graph = { nodes: 6, edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]] };
    const env = environmentFor(6, 12345);
    const aucs = new Set<number>();
    // Relabeling permutes which graph nodes hold which weights/values.
    const perm = [2, 4, 0, 5, 1, 3];
    const relabeled: Graph = { nodes: 6, edges: cycle.edges.map(([a, b]) => [perm[a]!, perm[b]!] as [number, number]) };
    for (const seed of [1, 2, 3, 4, 5]) aucs.add(simulateHeterogeneous(cycle, env, { kind: "random", seed, steps: 4 }).metrics.auc);
    const base = [...aucs];
    for (const seed of [1, 2, 3, 4, 5]) aucs.add(simulateHeterogeneous(relabeled, env, { kind: "random", seed, steps: 4 }).metrics.auc);
    expect([...aucs].some((auc) => !base.includes(auc))).toBe(true);
  });

  test("bounds and validation", () => {
    expect(() => simulateHeterogeneous(path, weighted, { kind: "random", seed: 0, steps: 3 })).toThrow();
    expect(() => simulateHeterogeneous(path, weighted, { kind: "random", seed: 0, steps: 2, extra: 1 } as never)).toThrow();
    expect(() => simulateHeterogeneous(path, { weights: [1, 1, 1, 1], values: [1, 1, 1, 1, 1] }, { kind: "random", seed: 0, steps: 2 })).toThrow();
    const disconnected: Graph = { nodes: 4, edges: [[0, 1], [1, 2]] };
    expect(() => simulateHeterogeneous(disconnected, flat, { kind: "random", seed: 0, steps: 2 })).toThrow();
  });
});
