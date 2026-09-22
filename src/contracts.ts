import { canonicalize, type JsonObject, type JsonValue } from "@hraness/algal";
import { parseGraph, type Graph } from "./network";

export const CONDITIONS = ["isolated", "shared-artifacts", "shared-artifacts-and-messages"] as const;
export type Condition = typeof CONDITIONS[number];
export const ALGAL_REVISION = "f899456e497656eb292d97d7c0aef5e06f1437dc";
export const MAX_ATTEMPTS = 288;
export const PROPOSAL_CONTRACT = "algal.lab.proposal.v2";

export function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object") {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}

export type Protocol = {
  contract: "algal.lab.study.v1";
  name: string;
  replicateSeeds: number[];
  researchers: number;
  rounds: number;
  nodes: number;
  edges: number;
  failureSteps: number;
  discoverySeeds: number[];
  holdoutSeeds: number[];
};

export function object(value: unknown, keys: readonly string[], label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error(`${label}: expected object`);
  const result = value as Record<string, unknown>;
  if (Object.keys(result).some((key) => !keys.includes(key))) throw new Error(`${label}: unknown field`);
  for (const key of keys) if (!Object.hasOwn(result, key)) throw new Error(`${label}: missing ${key}`);
  return result;
}

export function integer(value: unknown, min: number, max: number, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < min || value > max) throw new Error(`${label}: expected integer ${min}..${max}`);
  return value;
}

export function text(value: unknown, max: number, label: string): string {
  if (typeof value !== "string" || value.length === 0 || Buffer.byteLength(value) > max) throw new Error(`${label}: invalid text`);
  return value;
}

function seeds(value: unknown, max: number, label: string): number[] {
  if (!Array.isArray(value) || value.length === 0 || value.length > max) throw new Error(`${label}: invalid seed count`);
  const result = value.map((seed) => integer(seed, 0, 0xffffffff, label));
  if (new Set(result).size !== result.length) throw new Error(`${label}: repeated seed`);
  return result;
}

export function parseProtocol(value: unknown): Protocol {
  const p = object(value, ["contract", "name", "replicateSeeds", "researchers", "rounds", "nodes", "edges", "failureSteps", "discoverySeeds", "holdoutSeeds"], "protocol");
  if (p.contract !== "algal.lab.study.v1") throw new Error("unsupported protocol");
  const name = text(p.name, 64, "protocol.name");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error("protocol.name: use lowercase letters, digits, and hyphens");
  const nodes = integer(p.nodes, 4, 16, "nodes");
  const result: Protocol = {
    contract: "algal.lab.study.v1", name,
    replicateSeeds: seeds(p.replicateSeeds, 8, "replicateSeeds"),
    researchers: integer(p.researchers, 2, 8, "researchers"),
    rounds: integer(p.rounds, 1, 12, "rounds"),
    nodes, edges: integer(p.edges, nodes - 1, Math.min(48, nodes * (nodes - 1) / 2), "edges"),
    failureSteps: integer(p.failureSteps, 1, nodes - 2, "failureSteps"),
    discoverySeeds: seeds(p.discoverySeeds, 4, "discoverySeeds"),
    holdoutSeeds: seeds(p.holdoutSeeds, 8, "holdoutSeeds"),
  };
  if (result.discoverySeeds.some((seed) => result.holdoutSeeds.includes(seed))) throw new Error("discovery and holdout seeds must be disjoint");
  if (result.replicateSeeds.length * result.researchers * result.rounds * CONDITIONS.length > MAX_ATTEMPTS) throw new Error(`study exceeds ${MAX_ATTEMPTS} proposal slots`);
  return result;
}

export type EvidenceView = { id: string; graph: Graph; score: number };
export type ResearchContext = {
  contract: "algal.lab.context.v1";
  replicate: number;
  condition: Condition;
  round: number;
  researcher: number;
  nodes: number;
  edges: number;
  failureSteps: number;
  discoverySeeds: number[];
  evidence: EvidenceView[];
  messages: { id: string; text: string }[];
};
export type Proposal = {
  graph: Graph;
  hypothesis: string;
  prediction: number;
  rationale: string;
  parents: string[];
  message: string;
};

export function parseProposal(value: unknown, context: ResearchContext): Proposal {
  const p = object(value, ["graph", "hypothesis", "prediction", "rationale", "parents", "message"], "proposal");
  const graph = parseGraph(p.graph);
  if (graph.nodes !== context.nodes || graph.edges.length !== context.edges) throw new Error("proposal must preserve protocol node and edge budgets");
  if (typeof p.prediction !== "number" || !Number.isFinite(p.prediction) || p.prediction < 0 || p.prediction > 1) throw new Error("prediction must be a mean discovery AUC in [0,1]");
  if (!Array.isArray(p.parents) || p.parents.length > 8 || new Set(p.parents).size !== p.parents.length) throw new Error("invalid parent references");
  const parents = p.parents.map((id: unknown) => {
    if (typeof id !== "string" || !context.evidence.some((item) => item.id === id)) throw new Error("parent must reference visible prior evidence");
    return id;
  });
  return { graph, hypothesis: text(p.hypothesis, 1000, "hypothesis"), prediction: p.prediction,
    rationale: text(p.rationale, 1000, "rationale"), parents, message: text(p.message, 500, "message") };
}

/** Provider-facing proposal schema for structured-output routes. Unlike the
 * retired generic v1 schema, it encodes the exact node and edge budgets from the
 * admitted context, so an over- or under-budget graph cannot be expressed. Host
 * parseProposal remains authoritative for every admission rule. */
export function proposalContractSchema(nodes: number, edges: number): JsonObject {
  integer(nodes, 4, 16, "contract.nodes");
  integer(edges, nodes - 1, Math.min(48, nodes * (nodes - 1) / 2), "contract.edges");
  return freeze({
    type: "object", additionalProperties: false,
    required: ["graph", "hypothesis", "prediction", "rationale", "parents", "message"],
    properties: {
      graph: {
        type: "object", additionalProperties: false, required: ["nodes", "edges"],
        properties: {
          nodes: { type: "integer", minimum: nodes, maximum: nodes },
          edges: { type: "array", minItems: edges, maxItems: edges,
            items: { type: "array", minItems: 2, maxItems: 2, items: { type: "integer", minimum: 0, maximum: nodes - 1 } } },
        },
      },
      hypothesis: { type: "string", minLength: 1, maxLength: 1000 },
      prediction: { type: "number", minimum: 0, maximum: 1 },
      rationale: { type: "string", minLength: 1, maxLength: 1000 },
      parents: { type: "array", maxItems: 8, items: { type: "string", pattern: "^sha256:[a-f0-9]{64}$", maxLength: 71 } },
      message: { type: "string", minLength: 1, maxLength: 500 },
    },
  }) as JsonObject;
}

/** Bound foreign JSON before hashing, traversing, or passing to ALGAL. */
export function json(value: unknown): JsonValue {
  let count = 0;
  const walk = (item: unknown, depth: number): void => {
    if (++count > 100_000 || depth > 48) throw new Error("JSON structure exceeds bounds");
    if (item === null || typeof item === "string" || typeof item === "boolean") return;
    if (typeof item === "number" && Number.isFinite(item)) return;
    if (Array.isArray(item)) { for (const child of item) walk(child, depth + 1); return; }
    if (typeof item === "object" && (Object.getPrototypeOf(item) === Object.prototype || Object.getPrototypeOf(item) === null)) {
      for (const child of Object.values(item as object)) walk(child, depth + 1);
      return;
    }
    throw new Error("expected finite JSON data");
  };
  walk(value, 0);
  return value as JsonValue;
}

export function equal(a: unknown, b: unknown): boolean { return canonicalize(json(a)) === canonicalize(json(b)); }
