import { describe, expect, test } from "bun:test";
import type { JsonValue } from "@hraness/algal";
import {
  CONDITIONS,
  MAX_ATTEMPTS,
  equal,
  json,
  parseProposal,
  parseProtocol,
  proposalContractSchema,
  PROPOSAL_CONTRACT,
  type Protocol,
  type Proposal,
  type ResearchContext,
} from "./contracts";

const protocol: Protocol = {
  contract: "algal.lab.study.v1",
  name: "bounded-network-study",
  replicateSeeds: [17],
  researchers: 2,
  rounds: 3,
  nodes: 4,
  edges: 3,
  failureSteps: 2,
  discoverySeeds: [101, 102],
  holdoutSeeds: [201, 202],
};

const graph = { nodes: 4, edges: [[0, 1], [1, 2], [2, 3]] as [number, number][] };

const context: ResearchContext = {
  contract: "algal.lab.context.v1",
  replicate: 17,
  condition: "shared-artifacts",
  round: 1,
  researcher: 0,
  nodes: 4,
  edges: 3,
  failureSteps: 2,
  discoverySeeds: [101, 102],
  evidence: [{ id: "visible-prior", graph, score: 0.6 }],
  messages: [],
};

const proposal: Proposal = {
  graph,
  hypothesis: "Distributing degree can preserve connectivity under targeted removal.",
  prediction: 0.6,
  rationale: "Compare the realized design on the fixed discovery schedule.",
  parents: ["visible-prior"],
  message: "This proposal requires measurement before the hypothesis is retained.",
};

describe("study protocol admission", () => {
  test("valid protocol retains exact budgets and seeds", () => {
    expect(parseProtocol(protocol)).toEqual(protocol);
  });

  test("unknown and missing fields cannot silently change a protocol", () => {
    expect(() => parseProtocol({ ...protocol, simulator: "different" })).toThrow(/unknown field/);
    const { failureSteps: _missing, ...withoutSteps } = protocol;
    expect(() => parseProtocol(withoutSteps)).toThrow(/missing failureSteps/);
    expect(() => parseProtocol({ ...protocol, contract: "algal.lab.study.v2" })).toThrow();
    expect(() => parseProtocol({ ...protocol, name: "Different Study" })).toThrow();
    expect(() => parseProtocol({ ...protocol, name: "a".repeat(65) })).toThrow();
  });

  test("holdout/discovery seed overlap and repeated seeds reject", () => {
    expect(() => parseProtocol({ ...protocol, holdoutSeeds: [101, 202] })).toThrow(/disjoint/);
    for (const field of ["replicateSeeds", "discoverySeeds", "holdoutSeeds"] as const) {
      expect(() => parseProtocol({ ...protocol, [field]: [5, 5] })).toThrow(/repeated seed/);
      expect(() => parseProtocol({ ...protocol, [field]: [] })).toThrow();
      expect(() => parseProtocol({ ...protocol, [field]: [-1] })).toThrow();
      expect(() => parseProtocol({ ...protocol, [field]: [2 ** 32] })).toThrow();
      expect(() => parseProtocol({ ...protocol, [field]: [1.5] })).toThrow();
    }
    expect(() => parseProtocol({ ...protocol, discoverySeeds: [1, 2, 3, 4, 5] })).toThrow();
    expect(() => parseProtocol({ ...protocol, holdoutSeeds: Array.from({ length: 9 }, (_, i) => 300 + i) })).toThrow();
  });

  test("the combined proposal allowance counts every condition and replicate", () => {
    const atLimit = parseProtocol({ ...protocol, researchers: 8, rounds: 12 });
    expect(atLimit.replicateSeeds.length * atLimit.researchers * atLimit.rounds * CONDITIONS.length).toBe(MAX_ATTEMPTS);
    // Each individual field remains admissible; their joint workload is not.
    expect(() => parseProtocol({ ...atLimit, replicateSeeds: [17, 18] })).toThrow(/proposal slots/);
  });

  test("impossible graph and failure budgets reject before execution", () => {
    for (const patch of [
      { nodes: 3 }, { nodes: 17 }, { nodes: 4.5 }, { edges: 2 }, { edges: 7 },
      { nodes: 16, edges: 49 }, { failureSteps: 0 }, { failureSteps: 3 },
      { researchers: 1 }, { researchers: 9 }, { rounds: 0 }, { rounds: 13 },
    ]) expect(() => parseProtocol({ ...protocol, ...patch })).toThrow();
    expect(parseProtocol({ ...protocol, nodes: 16, edges: 48, failureSteps: 14 }).edges).toBe(48);
  });
});

describe("research proposal admission", () => {
  test("parents must be visible prior artifacts, with no duplicates", () => {
    expect(parseProposal(proposal, context).parents).toEqual(["visible-prior"]);
    expect(parseProposal({ ...proposal, parents: [] }, context).parents).toEqual([]);
    // The parser's authority is the supplied view, not knowledge of global IDs.
    const hiddenContext = { ...context, evidence: [] };
    expect(() => parseProposal(proposal, hiddenContext)).toThrow(/visible prior evidence/);
    expect(() => parseProposal({ ...proposal, parents: ["nonexistent"] }, context)).toThrow(/visible prior evidence/);
    expect(() => parseProposal({ ...proposal, parents: ["visible-prior", "visible-prior"] }, context)).toThrow(/parent references/);
    expect(() => parseProposal({ ...proposal, parents: [1] }, context)).toThrow();
    expect(() => parseProposal({ ...proposal, parents: "visible-prior" }, context)).toThrow();
    const many = Array.from({ length: 9 }, (_, i) => ({ id: `prior-${i}`, graph, score: 0.5 }));
    expect(() => parseProposal({ ...proposal, parents: many.map((item) => item.id) }, { ...context, evidence: many })).toThrow();
  });

  test("candidate node/edge budgets are exact, even for otherwise valid graphs", () => {
    const extraEdge = { nodes: 4, edges: [...graph.edges, [0, 3]] };
    const extraNode = { nodes: 5, edges: [...graph.edges, [3, 4]] };
    expect(() => parseProposal({ ...proposal, graph: extraEdge }, context)).toThrow(/node and edge budgets/);
    expect(() => parseProposal({ ...proposal, graph: extraNode }, { ...context, edges: 4 })).toThrow(/node and edge budgets/);
    expect(() => parseProposal({ ...proposal, extra: true }, context)).toThrow(/unknown field/);
  });

  test("equivalent undirected designs normalize without changing the proposal", () => {
    const reordered = { nodes: 4, edges: [[3, 2], [1, 0], [2, 1]] };
    const parsed = parseProposal({ ...proposal, graph: reordered }, context);
    expect(parsed).toEqual(proposal);
    expect(equal(parsed, proposal)).toBe(true);
    expect(reordered.edges).toEqual([[3, 2], [1, 0], [2, 1]]);
  });

  test("prose limits count UTF-8 bytes, not code units", () => {
    const boundary = {
      ...proposal,
      hypothesis: "🧪".repeat(250),
      rationale: "é".repeat(500),
      message: "🧪".repeat(125),
    };
    expect(parseProposal(boundary, context)).toEqual(boundary);
    for (const field of ["hypothesis", "rationale", "message"] as const) {
      expect(() => parseProposal({ ...boundary, [field]: `${boundary[field]}x` }, context)).toThrow(/invalid text/);
      expect(() => parseProposal({ ...proposal, [field]: "" }, context)).toThrow();
      expect(() => parseProposal({ ...proposal, [field]: null }, context)).toThrow();
    }
  });

  test("predictions are finite AUC values in the closed unit interval", () => {
    for (const prediction of [0, 0.5, 1]) {
      expect(parseProposal({ ...proposal, prediction }, context).prediction).toBe(prediction);
    }
    for (const prediction of [NaN, Infinity, -Infinity, -0.01, 1.01, "0.5", null]) {
      expect(() => parseProposal({ ...proposal, prediction }, context)).toThrow(/prediction/);
    }
  });
});

describe("versioned proposal contract schema", () => {
  test("encodes the exact admitted node and edge budgets", () => {
    const schema = proposalContractSchema(8, 10);
    const view = JSON.parse(JSON.stringify(schema)) as {
      properties: { graph: { properties: { nodes: { type: string; minimum: number; maximum: number };
        edges: { minItems: number; maxItems: number; items: { items: { type: string; minimum: number; maximum: number } } } } } } };
    expect(PROPOSAL_CONTRACT).toBe("algal.lab.proposal.v2");
    expect(view.properties.graph.properties.nodes).toEqual({ type: "integer", minimum: 8, maximum: 8 });
    expect(view.properties.graph.properties.edges.minItems).toBe(10);
    expect(view.properties.graph.properties.edges.maxItems).toBe(10);
    expect(view.properties.graph.properties.edges.items.items).toEqual({ type: "integer", minimum: 0, maximum: 7 });
    expect(proposalContractSchema(8, 10)).toEqual(schema);
    expect(proposalContractSchema(8, 10)).not.toEqual(proposalContractSchema(8, 11));
    expect(proposalContractSchema(8, 10)).not.toEqual(proposalContractSchema(9, 10));
    const edges = ((schema.properties as Record<string, JsonValue>).graph as Record<string, JsonValue>).properties as Record<string, JsonValue>;
    expect(Object.isFrozen(edges.edges)).toBe(true);
  });

  test("rejects budgets outside protocol bounds", () => {
    for (const [nodes, edges] of [[3, 2], [17, 16], [8, 6], [8, 29], [8, 10.5], [8, -1]] as const) {
      expect(() => proposalContractSchema(nodes, edges)).toThrow();
    }
    expect(() => proposalContractSchema("8" as unknown as number, 10)).toThrow();
    proposalContractSchema(4, 3);
    proposalContractSchema(16, 48);
  });
});

describe("foreign JSON admission", () => {
  test("finite JSON is retained while non-JSON values and nonfinite numbers reject", () => {
    const value = { nested: [null, false, "text", 0, -1.25], empty: {} };
    expect(json(value)).toEqual(value);
    const nullPrototype = Object.assign(Object.create(null) as object, { supported: true });
    expect(json(nullPrototype)).toEqual({ supported: true });
    for (const bad of [undefined, NaN, Infinity, -Infinity, 1n, Symbol("bad"), () => 1, new Date(0), new Map(), new Set()]) {
      expect(() => json(bad)).toThrow(/finite JSON/);
      expect(() => json({ nested: [bad] })).toThrow(/finite JSON/);
    }
    expect(() => equal({ value: NaN }, { value: null })).toThrow();
  });

  test("depth and node limits fail closed, including cyclic values", () => {
    const nested = (depth: number): JsonValue => {
      let value: JsonValue = null;
      for (let level = 0; level < depth; level++) value = [value];
      return value;
    };
    expect(json(nested(48))).toEqual(nested(48));
    expect(() => json(nested(49))).toThrow(/structure exceeds bounds/);
    expect(json(Array<null>(99_999).fill(null))).toHaveLength(99_999);
    expect(() => json(Array<null>(100_000).fill(null))).toThrow(/structure exceeds bounds/);
    const cycle: unknown[] = [];
    cycle.push(cycle);
    expect(() => json(cycle)).toThrow(/structure exceeds bounds/);
  });
});
