/**
 * network.v1 is a deterministic, discrete node-failure instrument.
 * Service always uses the original node count as its denominator. It measures
 * connectivity under this model; it does not model capacity, flow, or repair.
 * Keep numerical behavior here so an instrument identity can bind this source.
 */
export type Graph = { nodes: number; edges: [number, number][] };

export type FailureSchedule = {
  kind: "random" | "targeted";
  seed: number;
  steps: number;
};

export type NetworkResult = {
  contract: "algal.lab.network-result.v1";
  instrument: "network.v1";
  graph: Graph;
  schedule: FailureSchedule;
  trajectory: {
    step: number;
    removed: number | null;
    active: number[];
    largestComponent: number;
    service: number;
  }[];
  metrics: { auc: number; finalService: number };
};

const MIN_NODES = 4;
const MAX_NODES = 24;
const MAX_EDGES = 96;
const UINT32_MAX = 0xffff_ffff;
const MUTATION_ATTEMPTS = 128;

function record(value: unknown, fields: readonly string[], label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${label} must be an object`);
  }
  const prototype: unknown = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    throw new Error(`${label} must be a plain object`);
  }
  const keys = Reflect.ownKeys(value);
  if (keys.length !== fields.length || keys.some((key) => typeof key !== "string" || !fields.includes(key))) {
    throw new Error(`${label} requires exactly ${fields.join(", ")}`);
  }
  return value as Record<string, unknown>;
}

function integer(value: unknown, min: number, max: number, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < min || value > max) {
    throw new Error(`${label} must be an integer in ${min}..${max}`);
  }
  // Normalize negative zero, which is numerically zero but has two encodings.
  return value === 0 ? 0 : value;
}

function nodeCount(value: unknown): number {
  return integer(value, MIN_NODES, MAX_NODES, "graph.nodes");
}

function maximumEdges(nodes: number): number {
  return Math.min(MAX_EDGES, (nodes * (nodes - 1)) / 2);
}

function compareEdges(a: [number, number], b: [number, number]): number {
  return a[0] - b[0] || a[1] - b[1];
}

function adjacency(graph: Graph): number[][] {
  const neighbors = Array.from({ length: graph.nodes }, (): number[] => []);
  for (const [a, b] of graph.edges) {
    neighbors[a]!.push(b);
    neighbors[b]!.push(a);
  }
  return neighbors;
}

function largestComponent(neighbors: number[][], active: readonly boolean[]): number {
  const seen = Array<boolean>(neighbors.length).fill(false);
  let largest = 0;
  for (let node = 0; node < neighbors.length; node++) {
    if (!active[node] || seen[node]) continue;
    const queue = [node];
    seen[node] = true;
    for (let cursor = 0; cursor < queue.length; cursor++) {
      for (const neighbor of neighbors[queue[cursor]!]!) {
        if (active[neighbor] && !seen[neighbor]) {
          seen[neighbor] = true;
          queue.push(neighbor);
        }
      }
    }
    largest = Math.max(largest, queue.length);
  }
  return largest;
}

function connected(graph: Graph): boolean {
  return largestComponent(adjacency(graph), Array<boolean>(graph.nodes).fill(true)) === graph.nodes;
}

/** Normalize edge orientation/order only; reject any change to the design. */
export function parseGraph(value: unknown): Graph {
  const raw = record(value, ["nodes", "edges"], "graph");
  const nodes = nodeCount(raw.nodes);
  if (!Array.isArray(raw.edges) || raw.edges.length < nodes - 1 || raw.edges.length > maximumEdges(nodes)) {
    throw new Error(`graph.edges must contain ${nodes - 1}..${maximumEdges(nodes)} edges`);
  }
  const edges: [number, number][] = [];
  const seen = new Set<number>();
  for (const edge of raw.edges) {
    if (!Array.isArray(edge) || edge.length !== 2) {
      throw new Error("each graph edge must be a pair of node IDs");
    }
    const a = integer(edge[0], 0, nodes - 1, "edge node");
    const b = integer(edge[1], 0, nodes - 1, "edge node");
    if (a === b) throw new Error("graph edges must not contain self loops");
    const normalized: [number, number] = a < b ? [a, b] : [b, a];
    const key = normalized[0] * nodes + normalized[1];
    if (seen.has(key)) throw new Error("graph edges must not contain duplicates");
    seen.add(key);
    edges.push(normalized);
  }
  edges.sort(compareEdges);
  const graph: Graph = { nodes, edges };
  if (!connected(graph)) throw new Error("graph must initially be connected");
  return graph;
}

export function parseSchedule(value: unknown, nodes: number): FailureSchedule {
  nodeCount(nodes);
  const raw = record(value, ["kind", "seed", "steps"], "schedule");
  if (raw.kind !== "random" && raw.kind !== "targeted") {
    throw new Error("schedule.kind must be random or targeted");
  }
  return {
    kind: raw.kind,
    seed: integer(raw.seed, 0, UINT32_MAX, "schedule.seed"),
    steps: integer(raw.steps, 1, nodes - 2, "schedule.steps"),
  };
}

/** Mulberry32; all state is the admitted uint32 seed, never ambient randomness. */
function random(seed: number): () => number {
  let state = integer(seed, 0, UINT32_MAX, "seed");
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(state ^ (state >>> 15), state | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 0x1_0000_0000;
  };
}

function shuffle<T>(values: T[], next: () => number): void {
  for (let index = values.length - 1; index > 0; index--) {
    const other = Math.floor(next() * (index + 1));
    const saved = values[index]!;
    values[index] = values[other]!;
    values[other] = saved;
  }
}

export function simulate(inputGraph: Graph, inputSchedule: FailureSchedule): NetworkResult {
  const graph = parseGraph(inputGraph);
  const schedule = parseSchedule(inputSchedule, graph.nodes);
  const neighbors = adjacency(graph);
  const live = Array<boolean>(graph.nodes).fill(true);
  const next = random(schedule.seed);
  const trajectory: NetworkResult["trajectory"] = [{
    step: 0,
    removed: null,
    active: Array.from({ length: graph.nodes }, (_, node) => node),
    largestComponent: graph.nodes,
    service: 1,
  }];
  let area = 0;
  for (let step = 1; step <= schedule.steps; step++) {
    const active = live.flatMap((present, node) => present ? [node] : []);
    let removed: number;
    if (schedule.kind === "random") {
      removed = active[Math.floor(next() * active.length)]!;
    } else {
      // Active IDs are ascending; strict improvement retains the lowest-ID tie.
      removed = active[0]!;
      let highestDegree = -1;
      for (const node of active) {
        const degree = neighbors[node]!.reduce((sum, neighbor) => sum + Number(live[neighbor]), 0);
        if (degree > highestDegree) {
          highestDegree = degree;
          removed = node;
        }
      }
    }
    live[removed] = false;
    const largest = largestComponent(neighbors, live);
    const service = largest / graph.nodes;
    area += (trajectory[step - 1]!.service + service) / 2;
    trajectory.push({
      step,
      removed,
      active: active.filter((node) => node !== removed),
      largestComponent: largest,
      service,
    });
  }
  return {
    contract: "algal.lab.network-result.v1",
    instrument: "network.v1",
    graph,
    schedule,
    trajectory,
    metrics: { auc: area / schedule.steps, finalService: trajectory.at(-1)!.service },
  };
}

/**
 * A shuffled random recursive spanning tree, plus shuffled absent edges.
 * This returns an exact connected design, not a uniform connected-graph sample.
 */
export function randomGraph(inputNodes: number, edgeCount: number, seed: number): Graph {
  const nodes = nodeCount(inputNodes);
  const count = integer(edgeCount, nodes - 1, maximumEdges(nodes), "edgeCount");
  const next = random(seed);
  const order = Array.from({ length: nodes }, (_, node) => node);
  shuffle(order, next);
  const edges: [number, number][] = [];
  const used = new Set<number>();
  for (let index = 1; index < nodes; index++) {
    const a = order[index]!;
    const b = order[Math.floor(next() * index)]!;
    const edge: [number, number] = a < b ? [a, b] : [b, a];
    edges.push(edge);
    used.add(edge[0] * nodes + edge[1]);
  }
  const absent: [number, number][] = [];
  for (let a = 0; a < nodes; a++) {
    for (let b = a + 1; b < nodes; b++) {
      if (!used.has(a * nodes + b)) absent.push([a, b]);
    }
  }
  shuffle(absent, next);
  edges.push(...absent.slice(0, count - edges.length));
  return parseGraph({ nodes, edges });
}

/** One connected edge replacement; unchanged output is an allowed failure. */
export function mutateGraph(inputGraph: Graph, seed: number): Graph {
  const graph = parseGraph(inputGraph);
  const next = random(seed);
  const used = new Set(graph.edges.map(([a, b]) => a * graph.nodes + b));
  const absent: [number, number][] = [];
  for (let a = 0; a < graph.nodes; a++) {
    for (let b = a + 1; b < graph.nodes; b++) {
      if (!used.has(a * graph.nodes + b)) absent.push([a, b]);
    }
  }
  if (absent.length === 0) return graph;
  for (let attempt = 0; attempt < MUTATION_ATTEMPTS; attempt++) {
    const removed = Math.floor(next() * graph.edges.length);
    const added = absent[Math.floor(next() * absent.length)]!;
    const candidate: Graph = {
      nodes: graph.nodes,
      edges: graph.edges.map((edge, index) => index === removed ? [...added] : [...edge]),
    };
    if (connected(candidate)) return parseGraph(candidate);
  }
  return graph;
}
