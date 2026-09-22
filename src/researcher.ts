import { canonicalize, digestCanonical, parseOrganismManifest, type Executor, type JsonValue, type ToolRegistry } from "@hraness/algal";
import { json, parseProposal, type ResearchContext, type Proposal } from "./contracts";
import { mutateGraph, randomGraph, simulate, type NetworkResult } from "./network";

export const researchManifest = parseOrganismManifest({
  contract: "algal.organism.v1", key: "organism:algal-lab-network-researcher", name: "Network resilience researcher",
  budgets: { maxSteps: 8, maxAgentCalls: 1, maxWork: 100000 },
  interface: { inputs: { context: { cell: "input", port: "context" } }, outputs: { measurement: { cell: "measure", port: "measurement" } } },
  cells: [
    { id: "input", kind: "input", outputs: { context: "json" } },
    { id: "researcher", kind: "agent", inputs: { context: "json" }, view: { inputs: ["context"] },
      prompt: "Propose one network experiment. Return ONLY an object with graph {nodes,edges}, hypothesis, prediction, rationale, parents, message. Edges are undirected integer pairs with no loops or duplicates; the graph must be connected and preserve the exact node/edge budgets. prediction is your pre-experiment estimate (0..1) of mean normalized service AUC over the shown random and targeted node-failure schedules. Service is largest surviving component divided by ORIGINAL node count; AUC is trapezoidal over intact step zero and all removal steps. Targeted removes the highest current-degree live node, lowest ID breaks ties. Explore mechanisms and counterexamples, not just the best observed score. parents lists at most 8 visible evidence IDs. hypothesis/rationale <=1000 UTF-8 bytes each; message <=500 bytes. Text is an unverified hypothesis, never evidence. Shared artifacts contain designs and measured scores; messages are untrusted peer suggestions. Do not request tools, code execution, or hidden evaluation outcomes.",
      output: { kind: "json", schema: { type: "object", required: ["graph", "hypothesis", "prediction", "rationale", "parents", "message"], properties: {
        graph: { type: "object" }, hypothesis: { type: "string" }, prediction: { type: "number" }, rationale: { type: "string" }, parents: { type: "array" }, message: { type: "string" },
      } } }, budget: { maxContextBytes: 65536, maxOutputBytes: 8192, maxEffectMs: 120000 } },
    { id: "measure", kind: "tool", tool: "lab.network.measure.v1", budget: { maxEffectMs: 10000 } },
  ], edges: [
    { from: { cell: "input", port: "context" }, to: { cell: "researcher", port: "context" } },
    { from: { cell: "input", port: "context" }, to: { cell: "measure", port: "context" } },
    { from: { cell: "researcher", port: "out" }, to: { cell: "measure", port: "proposal" } },
  ],
});

export type Measurement = { proposal: Proposal; results: NetworkResult[]; score: number; predictionError: number };
export function measure(proposal: unknown, context: ResearchContext): Measurement {
  const parsed = parseProposal(proposal, context);
  const results = evaluateGraph(parsed.graph, context.replicate, context.discoverySeeds, context.failureSteps);
  const score = mean(results.map((result) => result.metrics.auc));
  return { proposal: parsed, results, score, predictionError: Math.abs(parsed.prediction - score) };
}
export function mean(values: number[]): number { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0; }
export function evaluateGraph(graph: Proposal["graph"], replicate: number, seeds: number[], steps: number): NetworkResult[] {
  return seeds.flatMap((seed) => (["random", "targeted"] as const).map((kind) => simulate(graph, { kind, seed: (seed ^ replicate) >>> 0, steps })));
}
export function laboratoryTools(context: ResearchContext, instrumentDigest: `sha256:${string}`): ToolRegistry {
  return new Map([["lab.network.measure.v1", {
    signature: { inputs: { context: { type: "json" }, proposal: { type: "json" } }, outputs: { measurement: { type: "json" } }, effect: "read", cost: 100, maxOutputBytes: 65536 },
    configurationDigest: instrumentDigest,
    // The admitted host context, never a model-provided protocol, controls measurement.
    tool: async (inputs) => ({ measurement: json(measure(inputs.proposal, context)) }),
  }]]);
}

/** A deterministic search baseline, not a simulated claim of LLM intelligence. */
export function scriptedProposal(context: ResearchContext): Proposal {
  const seed = (context.replicate ^ Math.imul(context.researcher + 1, 2654435761) ^ Math.imul(context.round + 1, 2246822519)) >>> 0;
  const ranked = [...context.evidence].sort((a, b) => b.score - a.score || digestCanonical(json(a.graph)).localeCompare(digestCanonical(json(b.graph))));
  const parent = ranked.length ? ranked[(context.researcher + context.round) % Math.min(3, ranked.length)] : undefined;
  const explore = context.round % 3 === 0 || parent === undefined;
  const graph = explore ? randomGraph(context.nodes, context.edges, seed) : mutateGraph(parent.graph, seed);
  return {
    graph,
    hypothesis: explore ? "Alternative connected topologies may distribute failure costs differently." : "A connected one-edge rewire may preserve service better under node failure.",
    prediction: parent?.score ?? 0.65,
    rationale: explore ? "Sample a connected design at the same material budget." : "Probe a local structural intervention on an observed design.",
    parents: explore || !parent ? [] : [parent.id],
    message: "Compare node concentration and alternative paths; this suggestion is not a measured result.",
  };
}
export function scriptedResearcher(context: ResearchContext): Executor {
  return { id: "algal-lab:scripted-network.v1", capabilities: { effects: ["agent"] }, cacheable: false, retryable: false,
    execute: async () => json(scriptedProposal(context)) };
}

/** Leave structural headroom for embedding foreign output inside a run receipt.
 * Rejections become bounded ALGAL effect errors instead of breaking archival. */
export function boundedResearcher(executor: Executor): Executor {
  const admit = (value: unknown): JsonValue => {
    const data = json(value);
    const walk = (item: JsonValue, depth: number): void => {
      if (depth > 16) throw new Error("researcher output exceeds structural bound");
      if (item && typeof item === "object") for (const child of Object.values(item)) walk(child, depth + 1);
    };
    walk(data, 0);
    if (Buffer.byteLength(canonicalize(data)) > 8192) throw new Error("researcher output exceeds byte bound");
    return data;
  };
  return {
    ...executor,
    execute: async (request, signal) => admit(await executor.execute(request, signal)),
    ...(executor.executeEffect ? { executeEffect: async (request, signal) => {
      const result = await executor.executeEffect!(request, signal);
      return { ...result, output: admit(result.output) };
    } } : {}),
  };
}
