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

export type Budget = { nodes: number; edges: number; failureSteps: number };
export type ProtocolV1 = {
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
/** v2 adds the replicated-comparison controls: host-primed initial designs that
 * are identical across conditions by construction, counterbalanced condition
 * order, and held-out transfer budgets proposed after discovery. */
export type ProtocolV2 = Omit<ProtocolV1, "contract"> & {
  contract: "algal.lab.study.v2";
  primedDesigns: number;
  counterbalance: boolean;
  transferRegimes: Budget[];
};
export type Protocol = ProtocolV1 | ProtocolV2;
export const MAX_PRIMED_DESIGNS = 4;
export const MAX_TRANSFER_REGIMES = 2;
export type Phase = "primed" | "discovery" | "transfer";

/** Normalized v2 view of any protocol; v1 has no priming, transfer, or rotation. */
export function protocolSettings(protocol: Protocol): { primedDesigns: number; counterbalance: boolean; transferRegimes: Budget[] } {
  return protocol.contract === "algal.lab.study.v2"
    ? { primedDesigns: protocol.primedDesigns, counterbalance: protocol.counterbalance, transferRegimes: protocol.transferRegimes }
    : { primedDesigns: 0, counterbalance: false, transferRegimes: [] };
}
/** Condition execution order for a replicate. Counterbalancing rotates the
 * fixed order by replicate index so no condition always runs first. */
export function conditionOrder(protocol: Protocol, replicateIndex: number): Condition[] {
  const shift = protocolSettings(protocol).counterbalance ? replicateIndex % CONDITIONS.length : 0;
  return CONDITIONS.map((_, index) => CONDITIONS[(index + shift) % CONDITIONS.length]!);
}
/** Model-call slots per replicate/condition: discovery rounds plus one transfer
 * proposal per researcher per transfer regime. Priming is host work. */
export function proposalSlots(protocol: Protocol): number {
  return protocol.researchers * (protocol.rounds + protocolSettings(protocol).transferRegimes.length);
}

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

export type EffectiveSeed = { replicate: number; phase: "discovery" | "holdout"; seed: number; effective: number };
/** Schedule seeds as the instrument receives them: evaluateGraph runs every
 * discovery and holdout schedule under `seed ^ replicate`, so the seeds that
 * reach the simulator are these, not the raw protocol lists. */
export function effectiveSeeds(protocol: Pick<Protocol, "replicateSeeds" | "discoverySeeds" | "holdoutSeeds">): EffectiveSeed[] {
  return protocol.replicateSeeds.flatMap((replicate) => (["discovery", "holdout"] as const).flatMap((phase) =>
    protocol[`${phase}Seeds`].map((seed) => ({ replicate, phase, seed, effective: (seed ^ replicate) >>> 0 }))));
}
/** Pairs of schedules that would run the same simulation under different labels. */
export function effectiveSeedCollisions(protocol: Pick<Protocol, "replicateSeeds" | "discoverySeeds" | "holdoutSeeds">): [EffectiveSeed, EffectiveSeed][] {
  const seen = new Map<number, EffectiveSeed>();
  const collisions: [EffectiveSeed, EffectiveSeed][] = [];
  for (const item of effectiveSeeds(protocol)) {
    const prior = seen.get(item.effective);
    if (prior) collisions.push([prior, item]); else seen.set(item.effective, item);
  }
  return collisions;
}

export function parseBudget(value: unknown, label: string): Budget {
  const b = object(value, ["nodes", "edges", "failureSteps"], label);
  const nodes = integer(b.nodes, 4, 16, `${label}.nodes`);
  return { nodes, edges: integer(b.edges, nodes - 1, Math.min(48, nodes * (nodes - 1) / 2), `${label}.edges`),
    failureSteps: integer(b.failureSteps, 1, nodes - 2, `${label}.failureSteps`) };
}
export function parseProtocol(value: unknown): Protocol {
  const common = ["contract", "name", "replicateSeeds", "researchers", "rounds", "nodes", "edges", "failureSteps", "discoverySeeds", "holdoutSeeds"];
  const version = value !== null && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>).contract : undefined;
  if (version !== "algal.lab.study.v1" && version !== "algal.lab.study.v2") throw new Error("unsupported protocol");
  const p = object(value, version === "algal.lab.study.v2" ? [...common, "primedDesigns", "counterbalance", "transferRegimes"] : common, "protocol");
  const name = text(p.name, 64, "protocol.name");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error("protocol.name: use lowercase letters, digits, and hyphens");
  const budget = parseBudget({ nodes: p.nodes, edges: p.edges, failureSteps: p.failureSteps }, "protocol");
  const base: ProtocolV1 = {
    contract: "algal.lab.study.v1", name,
    replicateSeeds: seeds(p.replicateSeeds, 8, "replicateSeeds"),
    researchers: integer(p.researchers, 2, 8, "researchers"),
    rounds: integer(p.rounds, 1, 12, "rounds"),
    ...budget,
    discoverySeeds: seeds(p.discoverySeeds, 4, "discoverySeeds"),
    holdoutSeeds: seeds(p.holdoutSeeds, 8, "holdoutSeeds"),
  };
  if (base.discoverySeeds.some((seed) => base.holdoutSeeds.includes(seed))) throw new Error("discovery and holdout seeds must be disjoint");
  let result: Protocol = base;
  if (version === "algal.lab.study.v2") {
    if (typeof p.counterbalance !== "boolean") throw new Error("counterbalance must be a boolean");
    if (!Array.isArray(p.transferRegimes) || p.transferRegimes.length > MAX_TRANSFER_REGIMES) throw new Error(`transferRegimes must list at most ${MAX_TRANSFER_REGIMES} budgets`);
    const transferRegimes = p.transferRegimes.map((regime, index) => parseBudget(regime, `transferRegimes[${index}]`));
    const keys = transferRegimes.map((r) => `${r.nodes}:${r.edges}:${r.failureSteps}`);
    if (new Set(keys).size !== keys.length) throw new Error("repeated transfer regime");
    // Transfer tests generalization, so a transfer budget must differ from the primary budget.
    if (transferRegimes.some((r) => r.nodes === budget.nodes && r.edges === budget.edges)) throw new Error("transfer regime must differ from the primary node/edge budget");
    result = { ...base, contract: "algal.lab.study.v2", primedDesigns: integer(p.primedDesigns, 0, MAX_PRIMED_DESIGNS, "primedDesigns"),
      counterbalance: p.counterbalance, transferRegimes };
    // Raw disjointness is not enough: two replicates can XOR different raw seeds
    // onto the same effective schedule, so one holdout could be a peer's
    // discovery schedule. v1 protocols and their frozen archives keep the raw rule.
    const [collision] = effectiveSeedCollisions(result);
    if (collision) throw new Error(`effective seed ${collision[0].effective} repeats: ${collision[0].phase} seed ${collision[0].seed} of replicate ${collision[0].replicate}` +
      ` and ${collision[1].phase} seed ${collision[1].seed} of replicate ${collision[1].replicate}`);
  }
  if (result.replicateSeeds.length * proposalSlots(result) * CONDITIONS.length > MAX_ATTEMPTS) throw new Error(`study exceeds ${MAX_ATTEMPTS} proposal slots`);
  return result;
}

export type EvidenceView = { id: string; graph: Graph; score: number };
export type ResearchContextV1 = {
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
/** v2 contexts name the phase. Primed attempts use round -1 and are generated
 * by the host; transfer attempts use round = protocol.rounds and carry a
 * transfer budget while their evidence stays at the primary budget. */
export type ResearchContextV2 = Omit<ResearchContextV1, "contract"> & { contract: "algal.lab.context.v2"; phase: Phase };
export type ResearchContext = ResearchContextV1 | ResearchContextV2;
export const CONTEXT_CONTRACTS = ["algal.lab.context.v1", "algal.lab.context.v2"] as const;
export function contextPhase(context: ResearchContext): Phase { return context.contract === "algal.lab.context.v2" ? context.phase : "discovery"; }
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
