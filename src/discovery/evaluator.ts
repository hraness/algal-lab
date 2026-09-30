import { simulate, type Graph, type NetworkResult } from "../network";
import type { Config, Scores } from "./contracts";

/** Independently replay removal choices and connectivity using disjoint sets.
 * This checker does not call the simulator, its PRNG, or its BFS implementation. */
export function checkTrajectory(result: NetworkResult): void {
  const { graph, schedule, trajectory } = result;
  const live = new Set(Array.from({ length: graph.nodes }, (_, i) => i));
  let randomState = schedule.seed;
  let area = 0;
  let previous = 1;
  if (trajectory.length !== schedule.steps + 1) throw new Error("trajectory length mismatch");
  for (let step = 0; step <= schedule.steps; step++) {
    let removed: number | null = null;
    if (step > 0) {
      const active = [...live];
      if (schedule.kind === "random") {
        randomState = (randomState + 0x6d2b79f5) >>> 0;
        let t = Math.imul(randomState ^ (randomState >>> 15), randomState | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        const draw = ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        removed = active[Math.floor(draw * active.length)]!;
      } else {
        const degrees = new Map(active.map(n => [n, 0]));
        for (const [a, b] of graph.edges) if (live.has(a) && live.has(b)) {
          degrees.set(a, degrees.get(a)! + 1); degrees.set(b, degrees.get(b)! + 1);
        }
        removed = active.sort((a, b) => degrees.get(b)! - degrees.get(a)! || a - b)[0]!;
      }
      live.delete(removed);
    }
    const parent = Array.from({ length: graph.nodes }, (_, i) => i);
    const find = (n: number): number => { while (parent[n] !== n) n = parent[n]!; return n; };
    for (const [a, b] of graph.edges) if (live.has(a) && live.has(b)) parent[find(a)] = find(b);
    const sizes = new Map<number, number>();
    for (const n of live) sizes.set(find(n), (sizes.get(find(n)) ?? 0) + 1);
    const largest = Math.max(0, ...sizes.values());
    const row = trajectory[step]!;
    const service = largest / graph.nodes;
    if (row.step !== step || row.removed !== removed || row.largestComponent !== largest || row.service !== service || JSON.stringify(row.active) !== JSON.stringify([...live])) throw new Error("independent trajectory mismatch");
    if (step > 0) area += (previous + service) / 2;
    previous = service;
  }
  if (result.metrics.auc !== area / schedule.steps || result.metrics.finalService !== previous) throw new Error("independent metric mismatch");
}

function measure(graph: Graph, seeds: number[], steps: number, deadline: number): number {
  let sum = 0;
  for (const seed of seeds) {
    if (performance.now() >= deadline) throw new Error("evaluation time limit reached");
    const result = simulate(graph, { kind: "random", seed, steps });
    checkTrajectory(result);
    sum += result.metrics.auc;
  }
  if (performance.now() >= deadline) throw new Error("evaluation time limit reached");
  return sum / seeds.length;
}
export function evaluate(graph: Graph, config: Config): Scores {
  const deadline = performance.now() + config.evaluationTimeoutMs;
  const development = measure(graph, config.discoverySeeds, config.steps, deadline);
  const regression = measure(graph, config.regressionSeeds, config.steps, deadline);
  const targeted = simulate(graph, { kind: "targeted", seed: 0, steps: config.steps });
  checkTrajectory(targeted);
  if (performance.now() >= deadline) throw new Error("evaluation time limit reached");
  return { development, regression, targeted: targeted.metrics.auc };
}
export function confirmGraph(graph: Graph, config: Config): number {
  return measure(graph, config.holdoutSeeds, config.steps, performance.now() + config.evaluationTimeoutMs);
}
