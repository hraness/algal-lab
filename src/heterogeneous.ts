/** network.v2: heterogeneous node failure. Each node carries an integer failure
 * weight and an integer value, fixed by a seeded environment. Random failure
 * removes survivors without replacement with probability proportional to
 * weight; service is the most valuable surviving component's share of total
 * value. Targeted failure stays label-blind (max live degree, lowest id tie).
 * The environment derives deterministically from the replicate seed, so a
 * recorded protocol reproduces it exactly. */
import { mulberry32, parseGraph, type FailureSchedule, type Graph } from "./network";

export type FailureEnvironment = { weights: number[]; values: number[] };
export type HeterogeneousResult = {
  contract: "algal.lab.network-result.v2";
  instrument: "network.v2";
  environment: FailureEnvironment;
  graph: Graph;
  schedule: FailureSchedule;
  trajectory: { step: number; removed: number | null; active: number[]; bestComponentValue: number; service: number }[];
  metrics: { auc: number; finalService: number };
};

function count(value: unknown, min: number, max: number, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < min || value > max) throw new Error(`${label}: expected integer ${min}..${max}`);
  return value;
}

export function parseEnvironment(value: unknown, nodes: number): FailureEnvironment {
  const nodesBound = count(nodes, 2, 16, "environment.nodes");
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error("environment: expected object");
  const keys = Object.keys(value as object).sort();
  if (keys.length !== 2 || keys[0] !== "values" || keys[1] !== "weights") throw new Error("environment: requires exactly weights and values");
  const env = value as { weights: unknown; values: unknown };
  const read = (input: unknown, label: string): number[] => {
    if (!Array.isArray(input) || input.length !== nodesBound) throw new Error(`${label}: expected ${nodesBound} entries`);
    return input.map((entry) => count(entry, 1, 99, label));
  };
  return { weights: read(env.weights, "environment.weights"), values: read(env.values, "environment.values") };
}

const spread = (entries: number[]): number => Math.max(...entries) - Math.min(...entries);

/** The registered generator: weights and values i.i.d. uniform on 1..5, redrawn
 * with seed+1 until both spreads are at least 3, so every admitted environment
 * is non-degenerate. Deterministic per (nodes, seed). */
export function environmentFor(nodes: number, seed: number): FailureEnvironment {
  count(nodes, 2, 16, "environment.nodes");
  count(seed, 0, 0xffffffff, "environment.seed");
  for (let candidate = seed >>> 0; ; candidate = (candidate + 1) >>> 0) {
    const next = mulberry32(candidate);
    const weights = Array.from({ length: nodes }, () => 1 + Math.floor(next() * 5));
    const values = Array.from({ length: nodes }, () => 1 + Math.floor(next() * 5));
    if (spread(weights) >= 3 && spread(values) >= 3) return { weights, values };
  }
}

function adjacency(graph: Graph): number[][] {
  const neighbors = Array.from({ length: graph.nodes }, (): number[] => []);
  for (const [a, b] of graph.edges) { neighbors[a]!.push(b); neighbors[b]!.push(a); }
  return neighbors;
}

/** Value sum of the most valuable component among live nodes. */
function bestComponent(neighbors: number[][], live: readonly boolean[], values: readonly number[]): number {
  const seen = Array<boolean>(neighbors.length).fill(false);
  let best = 0;
  for (let start = 0; start < neighbors.length; start++) {
    if (!live[start] || seen[start]) continue;
    let total = 0;
    const stack = [start];
    seen[start] = true;
    while (stack.length) {
      const node = stack.pop()!;
      total += values[node]!;
      for (const neighbor of neighbors[node]!) if (live[neighbor] && !seen[neighbor]) { seen[neighbor] = true; stack.push(neighbor); }
    }
    if (total > best) best = total;
  }
  return best;
}

export function simulateHeterogeneous(inputGraph: Graph, inputEnvironment: FailureEnvironment, inputSchedule: FailureSchedule): HeterogeneousResult {
  const graph = parseGraph(inputGraph);
  const environment = parseEnvironment(inputEnvironment, graph.nodes);
  if (inputSchedule === null || typeof inputSchedule !== "object" || Array.isArray(inputSchedule)) throw new Error("schedule: expected object");
  const keys = Object.keys(inputSchedule as object).sort();
  if (keys.length !== 3 || keys[0] !== "kind" || keys[1] !== "seed" || keys[2] !== "steps") throw new Error("schedule: requires exactly kind, seed, and steps");
  const kind = (inputSchedule as { kind?: unknown }).kind;
  if (kind !== "random" && kind !== "targeted") throw new Error("schedule.kind: expected random or targeted");
  const seed = count((inputSchedule as { seed?: unknown }).seed, 0, 0xffffffff, "schedule.seed");
  const steps = count((inputSchedule as { steps?: unknown }).steps, 1, graph.nodes - 2, "schedule.steps");
  const schedule: FailureSchedule = { kind, seed, steps };
  const neighbors = adjacency(graph);
  const totalValue = environment.values.reduce((a, b) => a + b, 0);
  const live = Array<boolean>(graph.nodes).fill(true);
  const next = mulberry32(schedule.seed);
  const trajectory: HeterogeneousResult["trajectory"] = [{
    step: 0, removed: null, active: Array.from({ length: graph.nodes }, (_, node) => node),
    bestComponentValue: totalValue, service: 1,
  }];
  let area = 0;
  for (let step = 1; step <= schedule.steps; step++) {
    const active = live.flatMap((present, node) => present ? [node] : []);
    let removed: number;
    if (schedule.kind === "random") {
      const weight = active.reduce((sum, node) => sum + environment.weights[node]!, 0);
      let draw = next() * weight;
      removed = active[active.length - 1]!;
      for (const node of active) { draw -= environment.weights[node]!; if (draw < 0) { removed = node; break; } }
    } else {
      // Active IDs are ascending; strict improvement retains the lowest-ID tie.
      removed = active[0]!;
      let highestDegree = -1;
      for (const node of active) {
        const degree = neighbors[node]!.reduce((sum, neighbor) => sum + Number(live[neighbor]), 0);
        if (degree > highestDegree) { highestDegree = degree; removed = node; }
      }
    }
    live[removed] = false;
    const componentValue = bestComponent(neighbors, live, environment.values);
    const current = componentValue / totalValue;
    area += (trajectory[step - 1]!.service + current) / 2;
    trajectory.push({ step, removed, active: active.filter((node) => node !== removed), bestComponentValue: componentValue, service: current });
  }
  return { contract: "algal.lab.network-result.v2", instrument: "network.v2", environment, graph, schedule, trajectory,
    metrics: { auc: area / schedule.steps, finalService: trajectory.at(-1)!.service } };
}
