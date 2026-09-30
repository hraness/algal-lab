import { createHash } from "node:crypto";
import { object, integer, text } from "../contracts";
import { parseGraph, type Graph } from "../network";

export { object, integer, text };
export const VERSION = "algal.discovery.v1";
export type Provider = { kind: "control" } | {
  kind: "xai" | "gemini"; model: string; concurrency: number; proposalsPerCall: number;
  maxOutputTokens: number; maxInputTokens: number; timeoutMs: number; reserveUsdPerCall: number;
};
export type Config = {
  contract: typeof VERSION; name: string; seed: number; instrument: "network.v1";
  strategy: { id: string; instructions: string };
  baseline: Graph; steps: number; discoverySeeds: number[]; regressionSeeds: number[]; holdoutSeeds: number[];
  minimumImprovement: number; maxRegressionLoss: number; evaluationTimeoutMs: number;
  budget: { attempts: number; activeMs: number; modelCalls: number; tokens: number; usd: number };
  provider: Provider;
};
export type Proposal = { graph: Graph; prediction: number; hypothesis: string; rationale: string };
export type Scores = { development: number; regression: number; targeted: number };
export type Attempt = {
  id: string; parent: string; proposer: string; input: string; proposal: Proposal | null;
  status: "evaluating" | "invalid" | "duplicate" | "rejected" | "promoted"; reason: string;
  scores: Scores | null; independentCheck: boolean; reservedMs: number;
};
export type RequestRecord = {
  id: string; parent: string; status: "pending" | "completed" | "uncertain" | "abandoned";
  prompt: string; promptHash: string; count: number; inputTokens: number; outputTokens: number;
  reservedUsd: number; reservedMs: number; responseId: string | null; reportedModel: string | null; response: string | null;
  usage: { inputTokens: number; outputTokens: number } | null; error: string | null;
};
export type State = {
  contract: typeof VERSION; runId: string; configHash: string; sourceHash: string; createdAt: string;
  phase: "initializing" | "initialization-failed" | "exploring" | "sealed" | "confirming" | "confirmed"; incumbent: string;
  baseline: Scores | null; attempts: Attempt[]; requests: RequestRecord[];
  seal: { incumbent: string; digest: string } | null;
  confirmation: { baseline: number; incumbent: number; independentCheck: true; reservedMs: number } | null;
};
export function hash(value: unknown): string {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex");
}
export function number(value: unknown, min: number, max: number, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) throw new Error(`${label}: expected number ${min}..${max}`);
  return value;
}
function seeds(value: unknown, label: string): number[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > 16) throw new Error(`${label}: expected 1..16 seeds`);
  const result = value.map(item => integer(item, 0, 0xffff_ffff, label));
  if (new Set(result).size !== result.length) throw new Error(`${label}: duplicate seeds`);
  return result;
}
export function parseConfig(value: unknown): Config {
  const raw = object(value, ["contract", "name", "seed", "instrument", "strategy", "baseline", "steps", "discoverySeeds", "regressionSeeds", "holdoutSeeds", "minimumImprovement", "maxRegressionLoss", "evaluationTimeoutMs", "budget", "provider"], "config");
  if (raw.contract !== VERSION || raw.instrument !== "network.v1") throw new Error("unsupported discovery config or instrument");
  const name = text(raw.name, 80, "name");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) throw new Error("name must use lowercase letters, digits and hyphens");
  const strategy = object(raw.strategy, ["id", "instructions"], "strategy");
  const baseline = parseGraph(raw.baseline);
  if (baseline.nodes > 12 || baseline.edges.length > 36) throw new Error("discovery evaluator supports at most 12 nodes and 36 edges");
  const discoverySeeds = seeds(raw.discoverySeeds, "discoverySeeds");
  const regressionSeeds = seeds(raw.regressionSeeds, "regressionSeeds");
  const holdoutSeeds = seeds(raw.holdoutSeeds, "holdoutSeeds");
  const all = [...discoverySeeds, ...regressionSeeds, ...holdoutSeeds];
  if (new Set(all).size !== all.length) throw new Error("development, regression and holdout seeds must be disjoint");
  const b = object(raw.budget, ["attempts", "activeMs", "modelCalls", "tokens", "usd"], "budget");
  const budget = { attempts: integer(b.attempts, 1, 256, "attempts"), activeMs: integer(b.activeMs, 300, 86_400_000, "activeMs"), modelCalls: integer(b.modelCalls, 0, 256, "modelCalls"), tokens: integer(b.tokens, 0, 20_000_000, "tokens"), usd: number(b.usd, 0, 100, "usd") };
  const evaluationTimeoutMs = integer(raw.evaluationTimeoutMs, 100, 10_000, "evaluationTimeoutMs");
  if (budget.activeMs < evaluationTimeoutMs * 3) throw new Error("time budget must cover baseline and final confirmation");
  let provider: Provider;
  if ((raw.provider as { kind?: unknown } | null)?.kind === "control") {
    object(raw.provider, ["kind"], "provider");
    provider = { kind: "control" };
  } else {
    const p = object(raw.provider, ["kind", "model", "concurrency", "proposalsPerCall", "maxOutputTokens", "maxInputTokens", "timeoutMs", "reserveUsdPerCall"], "provider");
    if (p.kind !== "xai" && p.kind !== "gemini") throw new Error("provider must be control, xai, or gemini");
    const model = text(p.model, 100, "model");
    if (!/^[a-zA-Z0-9._-]+$/.test(model)) throw new Error("model must be a provider model name without a URL or path");
    provider = { kind: p.kind, model, concurrency: integer(p.concurrency, 1, 4, "concurrency"), proposalsPerCall: integer(p.proposalsPerCall, 1, 4, "proposalsPerCall"), maxOutputTokens: integer(p.maxOutputTokens, 256, 8192, "maxOutputTokens"), maxInputTokens: integer(p.maxInputTokens, 1024, 65536, "maxInputTokens"), timeoutMs: integer(p.timeoutMs, 1000, 120_000, "timeoutMs"), reserveUsdPerCall: number(p.reserveUsdPerCall, 0.000001, 100, "reserveUsdPerCall") };
  }
  return { contract: VERSION, name, seed: integer(raw.seed, 0, 0xffff_ffff, "seed"), instrument: "network.v1", strategy: { id: text(strategy.id, 100, "strategy.id"), instructions: text(strategy.instructions, 3000, "strategy.instructions") }, baseline, steps: integer(raw.steps, 1, baseline.nodes - 2, "steps"), discoverySeeds, regressionSeeds, holdoutSeeds, minimumImprovement: number(raw.minimumImprovement, 0, 1, "minimumImprovement"), maxRegressionLoss: number(raw.maxRegressionLoss, 0, 1, "maxRegressionLoss"), evaluationTimeoutMs, budget, provider };
}
export function parseProposal(value: unknown, config: Config): Proposal {
  const p = object(value, ["graph", "prediction", "hypothesis", "rationale"], "proposal");
  const graph = parseGraph(p.graph);
  if (graph.nodes !== config.baseline.nodes || graph.edges.length !== config.baseline.edges.length) throw new Error("proposal must preserve the exact node and edge counts");
  return { graph, prediction: number(p.prediction, 0, 1, "prediction"), hypothesis: text(p.hypothesis, 1500, "hypothesis"), rationale: text(p.rationale, 1500, "rationale") };
}
function scores(value: unknown): Scores {
  const s = object(value, ["development", "regression", "targeted"], "scores");
  return { development: number(s.development, 0, 1, "development"), regression: number(s.regression, 0, 1, "regression"), targeted: number(s.targeted, 0, 1, "targeted") };
}
function nullableText(value: unknown, max: number, label: string): string | null { return value === null ? null : text(value, max, label); }
export function parseState(value: unknown, config: Config): State {
  const s = object(value, ["contract", "runId", "configHash", "sourceHash", "createdAt", "phase", "incumbent", "baseline", "attempts", "requests", "seal", "confirmation"], "state");
  if (s.contract !== VERSION || !["initializing", "initialization-failed", "exploring", "sealed", "confirming", "confirmed"].includes(String(s.phase))) throw new Error("invalid discovery state");
  if (!Array.isArray(s.attempts) || s.attempts.length > config.budget.attempts || !Array.isArray(s.requests) || s.requests.length > config.budget.modelCalls) throw new Error("state exceeds attempts or calls");
  const attempts: Attempt[] = s.attempts.map(value => {
    const a = object(value, ["id", "parent", "proposer", "input", "proposal", "status", "reason", "scores", "independentCheck", "reservedMs"], "attempt");
    if (!["evaluating", "invalid", "duplicate", "rejected", "promoted"].includes(String(a.status)) || typeof a.independentCheck !== "boolean") throw new Error("invalid attempt status");
    return { id: text(a.id, 80, "id"), parent: text(a.parent, 80, "parent"), proposer: text(a.proposer, 120, "proposer"), input: text(a.input, 20000, "input"), proposal: a.proposal === null ? null : parseProposal(a.proposal, config), status: a.status as Attempt["status"], reason: text(a.reason, 1000, "reason"), scores: a.scores === null ? null : scores(a.scores), independentCheck: a.independentCheck, reservedMs: integer(a.reservedMs, 0, config.evaluationTimeoutMs, "reservedMs") };
  });
  const requests: RequestRecord[] = s.requests.map(value => {
    const r = object(value, ["id", "parent", "status", "prompt", "promptHash", "count", "inputTokens", "outputTokens", "reservedUsd", "reservedMs", "responseId", "reportedModel", "response", "usage", "error"], "request");
    if (!["pending", "completed", "uncertain", "abandoned"].includes(String(r.status))) throw new Error("invalid request status");
    const u = r.usage === null ? null : object(r.usage, ["inputTokens", "outputTokens"], "usage");
    return { id: text(r.id, 100, "id"), parent: text(r.parent, 80, "parent"), status: r.status as RequestRecord["status"], prompt: text(r.prompt, 65000, "prompt"), promptHash: text(r.promptHash, 64, "promptHash"), count: integer(r.count, 1, 4, "count"), inputTokens: integer(r.inputTokens, 0, 65536, "inputTokens"), outputTokens: integer(r.outputTokens, 0, 8192, "outputTokens"), reservedUsd: number(r.reservedUsd, 0, 100, "reservedUsd"), reservedMs: integer(r.reservedMs, 1000, 160000, "reservedMs"), responseId: nullableText(r.responseId, 300, "responseId"), reportedModel: nullableText(r.reportedModel, 300, "reportedModel"), response: nullableText(r.response, 100000, "response"), usage: u === null ? null : { inputTokens: integer(u.inputTokens, 0, Number.MAX_SAFE_INTEGER, "inputTokens"), outputTokens: integer(u.outputTokens, 0, Number.MAX_SAFE_INTEGER, "outputTokens") }, error: nullableText(r.error, 1000, "error") };
  });
  const se = s.seal === null ? null : object(s.seal, ["incumbent", "digest"], "seal");
  const co = s.confirmation === null ? null : object(s.confirmation, ["baseline", "incumbent", "independentCheck", "reservedMs"], "confirmation");
  if (co !== null && co.independentCheck !== true) throw new Error("confirmation requires independent checking");
  const state: State = { contract: VERSION, runId: text(s.runId, 100, "runId"), configHash: text(s.configHash, 64, "configHash"), sourceHash: text(s.sourceHash, 64, "sourceHash"), createdAt: text(s.createdAt, 30, "createdAt"), phase: s.phase as State["phase"], incumbent: text(s.incumbent, 80, "incumbent"), baseline: s.baseline === null ? null : scores(s.baseline), attempts, requests, seal: se === null ? null : { incumbent: text(se.incumbent, 80, "incumbent"), digest: text(se.digest, 64, "digest") }, confirmation: co === null ? null : { baseline: number(co.baseline, 0, 1, "baseline"), incumbent: number(co.incumbent, 0, 1, "incumbent"), independentCheck: true, reservedMs: integer(co.reservedMs, config.evaluationTimeoutMs * 2, config.evaluationTimeoutMs * 2, "reservedMs") } };
  if (state.configHash !== hash(config)) throw new Error("config changed after initialization");
  const ids = new Set(["baseline"]);
  let incumbent = "baseline";
  for (const a of attempts) {
    if (ids.has(a.id) || !ids.has(a.parent)) throw new Error("invalid attempt identity or parent");
    ids.add(a.id);
    if (a.status === "promoted") {
      if (!a.proposal || !a.scores || !a.independentCheck) throw new Error("promotion lacks checked evidence");
      incumbent = a.id;
    }
  }
  if (incumbent !== state.incumbent || new Set(requests.map(r => r.id)).size !== requests.length || requests.some(r => !ids.has(r.parent) || r.promptHash !== hash(r.prompt))) throw new Error("state identity mismatch");
  const uninitialized = state.phase === "initializing" || state.phase === "initialization-failed";
  if (uninitialized !== (state.baseline === null) || (uninitialized && (attempts.length > 0 || requests.length > 0))) throw new Error("state baseline phase mismatch");
  if ((uninitialized || state.phase === "exploring") !== (state.seal === null) || (state.phase === "confirmed") !== (state.confirmation !== null)) throw new Error("state phase mismatch");
  return state;
}
