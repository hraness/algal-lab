import { readFile } from "node:fs/promises";
import { hash, object, parseProposal, type Config, type State } from "./contracts";
import { confirmGraph, evaluate } from "./evaluator";
import { incumbent, spent } from "./loop";
import { withRun } from "./store";

function equal(actual: unknown, expected: unknown, label: string): void {
  if (hash(actual) !== hash(expected)) throw new Error(`verification mismatch: ${label}`);
}
function responseInputs(response: string, count: number): unknown[] {
  try {
    const raw = object(JSON.parse(response) as unknown, ["proposals"], "response");
    if (!Array.isArray(raw.proposals) || raw.proposals.length !== count) throw new Error("count");
    return raw.proposals.map(value => Buffer.byteLength(JSON.stringify(value)) <= 20000 ? value : { invalidModelResponse: true, responseHash: hash(response) });
  } catch { return Array.from({ length: count }, () => ({ invalidModelResponse: true, responseHash: hash(response) })); }
}
function checkRequests(config: Config, state: State): string[] {
  const outstanding: string[] = [];
  const remoteAttempts = new Set<string>();
  for (const [index, request] of state.requests.entries()) {
    if (request.parent !== "baseline" && !state.attempts.some(attempt => attempt.id === request.parent && attempt.proposal !== null)) throw new Error("request parent lacks a proposal");
    const provider = config.provider;
    if (provider.kind === "control") throw new Error("control run contains model requests");
    equal(request.id, `${state.runId}-request-${index + 1}`, "request identity");
    equal(request.inputTokens, Buffer.byteLength(request.prompt) + 512, "input token reservation");
    equal(request.outputTokens, provider.maxOutputTokens, "output token reservation");
    equal(request.reservedUsd, provider.reserveUsdPerCall, "dollar reservation");
    equal(request.reservedMs, provider.timeoutMs + request.count * config.evaluationTimeoutMs, "request time reservation");
    if (request.inputTokens > provider.maxInputTokens || request.count > provider.proposalsPerCall) throw new Error("request exceeds provider limits");
    if (request.usage && (request.usage.inputTokens > request.inputTokens || request.usage.outputTokens > request.outputTokens) && request.status !== "uncertain") throw new Error("usage overage is not unresolved");
    if (["pending", "uncertain"].includes(request.status)) outstanding.push(request.id);
    if (request.status === "completed" && request.response === null) throw new Error("completed request lacks its response");
    const inputs = request.status === "completed" && request.response ? responseInputs(request.response, request.count) : [];
    for (let i = 0; i < request.count; i++) {
      const id = `${request.id}-${i + 1}`;
      remoteAttempts.add(id);
      const attempt = state.attempts.find(attempt => attempt.id === id);
      if (!attempt) { if (request.status === "completed") outstanding.push(id); continue; }
      if (request.status !== "completed") throw new Error("unresolved or abandoned response was evaluated");
      equal(attempt.proposer, request.id, "request proposer");
      equal(attempt.parent, request.parent, "request parent");
      equal(attempt.input, JSON.stringify(inputs[i]), "captured proposal");
      equal(attempt.reservedMs, 0, "bundled evaluation reservation");
    }
  }
  for (const attempt of state.attempts) if (!remoteAttempts.has(attempt.id)) {
    if (!["outer-agent", "deterministic-control"].includes(attempt.proposer)) throw new Error("attempt has no recorded request");
    equal(attempt.reservedMs, config.evaluationTimeoutMs, "local evaluation reservation");
  }
  return outstanding;
}
function reproduce(config: Config, state: State) {
  const outstanding = checkRequests(config, state);
  const reserved = spent(config, state);
  for (const key of Object.keys(reserved) as (keyof typeof reserved)[]) {
    if (reserved[key] > config.budget[key] + 1e-10) throw new Error(`recorded ${key} exceeds budget`);
  }
  const remainingConfirmation = ["confirming", "confirmed"].includes(state.phase) ? 0 : config.evaluationTimeoutMs * 2;
  if (reserved.activeMs + remainingConfirmation > config.budget.activeMs) throw new Error("final confirmation reservation is missing");
  let reproducedEvaluations = 0;
  let retainedFailures = 0;
  let selected = "baseline";
  let scores = state.baseline;
  const replayConfig = { ...config, evaluationTimeoutMs: 10000 };
  if (scores) { equal(scores, evaluate(config.baseline, replayConfig), "baseline scores"); reproducedEvaluations++; }
  const graphs = new Set([hash(config.baseline)]);
  const parents = new Set(["baseline"]);
  for (const attempt of state.attempts) {
    if (!parents.has(attempt.parent)) throw new Error("attempt parent lacks an earlier proposal");
    if (attempt.proposal) parents.add(attempt.id);
    let proposal = null;
    try { proposal = parseProposal(JSON.parse(attempt.input) as unknown, config); } catch {}
    if (attempt.status === "evaluating") {
      if (attempt.proposal || attempt.scores || attempt.independentCheck) throw new Error("unfinished attempt contains uncommitted observations");
      outstanding.push(attempt.id); retainedFailures++; continue;
    }
    if (attempt.status === "rejected" && attempt.proposal === null && attempt.scores === null && !attempt.independentCheck && attempt.reason === "evaluation interrupted; reservation retained and this attempt is not retried") { retainedFailures++; continue; }
    equal(attempt.proposal, proposal, "original proposal");
    if (!proposal) {
      if (attempt.status !== "invalid" || attempt.scores || attempt.independentCheck) throw new Error("invalid proposal has measured evidence");
      retainedFailures++; continue;
    }
    const duplicate = graphs.has(hash(proposal.graph));
    graphs.add(hash(proposal.graph));
    if (duplicate) {
      if (attempt.status !== "duplicate" || attempt.scores || attempt.independentCheck) throw new Error("duplicate decision mismatch");
      continue;
    }
    if (attempt.scores === null) {
      if (attempt.status !== "invalid" || attempt.independentCheck) throw new Error("missing measurement for completed decision");
      retainedFailures++; continue;
    }
    if (!scores || !attempt.independentCheck) throw new Error("measurement lacks checked baseline");
    equal(attempt.scores, evaluate(proposal.graph, replayConfig), "attempt scores");
    reproducedEvaluations++;
    const measured = attempt.scores;
    const promote = measured.development > scores.development + config.minimumImprovement + 1e-12 && measured.regression + config.maxRegressionLoss + 1e-12 >= scores.regression && measured.targeted + config.maxRegressionLoss + 1e-12 >= scores.targeted;
    equal(attempt.status, promote ? "promoted" : "rejected", "selection decision");
    if (promote) { selected = attempt.id; scores = measured; }
  }
  equal(state.incumbent, selected, "incumbent");
  if (state.seal) {
    if (outstanding.length) throw new Error("sealed run has unfinished work");
    equal(state.seal.incumbent, selected, "sealed incumbent");
    equal(state.seal.digest, hash({ config: state.configHash, source: state.sourceHash, incumbent: incumbent(config, state), attempts: state.attempts, requests: state.requests }), "selection seal");
  }
  if (state.confirmation) {
    equal(state.confirmation.baseline, confirmGraph(config.baseline, replayConfig), "baseline confirmation");
    equal(state.confirmation.incumbent, confirmGraph(incumbent(config, state).graph, replayConfig), "incumbent confirmation");
    reproducedEvaluations += 2;
  }
  return { reproducedEvaluations, retainedFailures, outstanding, reserved, confirmationReproduced: state.confirmation !== null, handoffReady: outstanding.length === 0 && ["exploring", "sealed", "confirmed"].includes(state.phase) };
}
export async function verify(out: string) {
  return withRun(out, async (config, state) => ({
    verified: true,
    runId: state.runId,
    phase: state.phase,
    stateDigest: hash(state),
    configHash: state.configHash,
    sourceHash: state.sourceHash,
    verifierHash: hash(await readFile(new URL("./verify.ts", import.meta.url), "utf8")),
    bun: Bun.version,
    ...reproduce(config, state),
    limits: "Reproduces recorded numerical observations and selection, not provider authenticity, failed-operation outcomes, scientific validity, novelty, or practical utility. Handoff readiness describes this snapshot, not distributed ownership.",
  }));
}
