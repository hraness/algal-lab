import { mulberry32, mutateGraph, parseGraph, randomGraph, type Graph } from "../../../src/network";
import { parseEnvironment, type FailureEnvironment } from "../../../src/heterogeneous";

/** All proposals are bounded data; these six fields never carry executable code. */
export type Policy = {
  minValue: number;
  maxValue: number;
  risk: number;
  noise: number;
  degree: number;
  restart: number;
};

export const choices: { [K in keyof Policy]: readonly number[] } = {
  minValue: [0, 0.5, 1, 2], maxValue: [-1, 0, 0.5, 1],
  risk: [0, 0.25, 0.5, 1, 2, 4], noise: [0, 0.25, 0.5, 1, 2],
  degree: [0, 0.5, 1, 2], restart: [0, 1, 8, 16, 32],
};

export function admitPolicy(input: unknown): Policy {
  if (!input || typeof input !== "object" || Object.getPrototypeOf(input) !== Object.prototype) throw new Error("policy must be a plain object");
  const raw = input as Record<string, unknown>;
  const keys = Object.keys(choices) as (keyof Policy)[];
  const ownKeys = Reflect.ownKeys(raw);
  if (ownKeys.length !== keys.length || ownKeys.some((key) => typeof key !== "string" || !keys.includes(key as keyof Policy))) throw new Error("unknown policy fields");
  const result = {} as Policy;
  for (const key of keys) {
    const descriptor = Object.getOwnPropertyDescriptor(raw, key);
    if (!descriptor || !("value" in descriptor)) throw new Error("policy fields must be data");
    const value: unknown = descriptor.value;
    if (typeof value !== "number" || !choices[key].includes(value)) throw new Error(`invalid policy ${key}`);
    result[key] = value;
  }
  return result;
}

export const fixedPairPolicy: Policy = { minValue: 1, maxValue: 0, risk: 1, noise: 0.5, degree: 0.5, restart: 16 };
export const fixedReliablePolicy: Policy = { minValue: 0, maxValue: 0, risk: 1, noise: 0.25, degree: 0, restart: 16 };

const canonical = (graph: Graph): string => JSON.stringify(graph.edges);
const uint = (next: () => number): number => Math.floor(next() * 0x1_0000_0000) >>> 0;

function constructionEnvironment(input: FailureEnvironment, edges: number): FailureEnvironment {
  const nodes = input?.weights?.length;
  const environment = parseEnvironment(input, nodes);
  if (nodes > 10 || !Number.isInteger(edges) || edges < nodes - 1 || edges > nodes * (nodes - 1) / 2) throw new Error("unsupported construction budget");
  return environment;
}

function checkSeed(seed: number): void {
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) throw new Error("seed must be uint32");
}

/** A random greedy spanning tree, then extra edges, scored without any objective
 * queries. Risk/value features come from the visible environment. Dynamic
 * degree penalty can trade concentrated hubs against alternative connections. */
export function construct(policyInput: Policy, inputEnvironment: FailureEnvironment, edges: number, seed: number): Graph {
  const policy = admitPolicy(policyInput);
  const environment = constructionEnvironment(inputEnvironment, edges);
  checkSeed(seed);
  const nodes = environment.weights.length;
  const next = mulberry32(seed);
  const averageWeight = environment.weights.reduce((a, b) => a + b, 0) / nodes;
  const pairs: { edge: [number, number]; score: number }[] = [];
  for (let a = 0; a < nodes; a++) for (let b = a + 1; b < nodes; b++) {
    const low = Math.min(environment.values[a]!, environment.values[b]!);
    const high = Math.max(environment.values[a]!, environment.values[b]!);
    const jitter = -Math.log(-Math.log(Math.max(1e-12, Math.min(1 - 1e-12, next()))));
    pairs.push({ edge: [a, b], score: policy.minValue * Math.log(low) + policy.maxValue * Math.log(high)
      - policy.risk * (environment.weights[a]! + environment.weights[b]!) / averageWeight + policy.noise * jitter });
  }
  const parent = Array.from({ length: nodes }, (_, node) => node);
  const degree = Array<number>(nodes).fill(0);
  const find = (node: number): number => { while (parent[node] !== node) node = parent[node]!; return node; };
  const selected: [number, number][] = [];
  const used = new Set<number>();
  while (selected.length < edges) {
    let best = -1, bestScore = -Infinity;
    for (let index = 0; index < pairs.length; index++) {
      if (used.has(index)) continue;
      const pair = pairs[index]!;
      const [a, b] = pair.edge;
      if (selected.length < nodes - 1 && find(a) === find(b)) continue;
      const score = pair.score - policy.degree * (degree[a]! + degree[b]!);
      if (score > bestScore) { best = index; bestScore = score; }
    }
    if (best < 0) throw new Error("construction exhausted admissible edges");
    used.add(best);
    const [a, b] = pairs[best]!.edge;
    parent[find(a)] = find(b);
    degree[a]!++; degree[b]!++;
    selected.push([a, b]);
  }
  return parseGraph({ nodes, edges: selected });
}

/** Exact one-deletion star center formula. Extra edges use a fixed, objective-
 * free value/failure score; this baseline is also permitted local search. */
export function theoremStar(inputEnvironment: FailureEnvironment, edges: number): Graph {
  const environment = constructionEnvironment(inputEnvironment, edges);
  const nodes = environment.weights.length;
  const total = environment.values.reduce((a, b) => a + b, 0);
  const costs = environment.weights.map((weight, node) => weight * (total - environment.values[node]!
    - Math.max(...environment.values.filter((_, other) => node !== other))));
  const center = costs.indexOf(Math.min(...costs));
  const result: [number, number][] = Array.from({ length: nodes }, (_, node) => node).filter((node) => node !== center)
    .map((node): [number, number] => [Math.min(node, center), Math.max(node, center)]);
  const extra: { edge: [number, number]; score: number }[] = [];
  for (let a = 0; a < nodes; a++) for (let b = a + 1; b < nodes; b++) if (a !== center && b !== center) {
    extra.push({ edge: [a, b], score: Math.min(environment.values[a]!, environment.values[b]!) / (environment.weights[a]! + environment.weights[b]!) });
  }
  extra.sort((a, b) => b.score - a.score || a.edge[0] - b.edge[0] || a.edge[1] - b.edge[1]);
  result.push(...extra.slice(0, edges - result.length).map((entry) => entry.edge));
  return parseGraph({ nodes, edges: result });
}

export type SearchKind = "policy" | "random-search" | "random-hill" | "star-hill" | "annealing";
export type SearchResult = {
  graph: Graph; score: number; evaluations: number; duplicateProposals: number;
  unchangedMutations: number; acceptedImprovements: number; acceptedWorse: number; failures: string[];
  initialScore: number | null; bestByEvaluation: number[];
};

export function search(kind: SearchKind, inputPolicy: Policy, inputEnvironment: FailureEnvironment, edges: number, seed: number,
  evaluations: number, objective: (graph: Graph) => number): SearchResult {
  if (!Number.isInteger(evaluations) || evaluations < 1 || evaluations > 256) throw new Error("evaluation budget must be 1..256");
  const environment = constructionEnvironment(inputEnvironment, edges);
  const policy = admitPolicy(inputPolicy);
  checkSeed(seed);
  const next = mulberry32(seed);
  const nodes = environment.weights.length;
  let best: Graph | undefined, current: Graph | undefined;
  let bestScore = -Infinity, currentScore = -Infinity;
  let initialScore: number | null = null;
  let duplicateProposals = 0, unchangedMutations = 0, acceptedImprovements = 0, acceptedWorse = 0;
  const seen = new Set<string>(), failures: string[] = [], bestByEvaluation: number[] = [];
  for (let index = 0; index < evaluations; index++) {
    const proposalSeed = uint(next);
    try {
      let proposal: Graph;
      const restart = kind === "random-search" || current === undefined || (kind === "policy" && policy.restart > 0 && index % policy.restart === 0);
      if (restart) {
        proposal = kind === "star-hill" ? theoremStar(environment, edges)
          : kind === "policy" ? construct(policy, environment, edges, proposalSeed) : randomGraph(nodes, edges, proposalSeed);
      } else {
        proposal = mutateGraph(current!, proposalSeed);
        if (canonical(proposal) === canonical(current!)) unchangedMutations++;
      }
      const key = canonical(proposal);
      if (seen.has(key)) duplicateProposals++;
      seen.add(key);
      const value = objective(proposal);
      if (!Number.isFinite(value) || value < 0 || value > 1) throw new Error("invalid objective output");
      if (index === 0) initialScore = value;
      const temperature = 0.005 * Math.pow(0.01, index / Math.max(1, evaluations - 1));
      const annealAccept = kind === "annealing" && next() < Math.exp((value - currentScore) / temperature);
      if (restart || value > currentScore || annealAccept) {
        if (!restart && value > currentScore) acceptedImprovements++;
        if (!restart && value < currentScore) acceptedWorse++;
        current = proposal; currentScore = value;
      }
      if (value > bestScore || (value === bestScore && key < canonical(best!))) { best = proposal; bestScore = value; }
    } catch (error) { failures.push(`evaluation ${index}: ${String(error)}`); }
    bestByEvaluation.push(best === undefined ? 0 : bestScore);
  }
  if (best === undefined) throw new Error(`all proposals failed: ${failures.join("; ")}`);
  return { graph: best, score: bestScore, evaluations, duplicateProposals, unchangedMutations, acceptedImprovements, acceptedWorse, failures, initialScore, bestByEvaluation };
}
