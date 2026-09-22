/** Offline consistency inspection. Provider metadata is retained evidence, not
 * independent authentication of an author, a charge, or scientific validity. */
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ArtifactStore, digest, digestString, readJsonFile } from "../src/artifacts";
import { CONDITIONS, equal, integer, object, parseProtocol, proposalContractSchema, text, PROPOSAL_CONTRACT } from "../src/contracts";
import { GATEWAY_FAILURE_CODES } from "../src/gateway-executor";
import { exactRandomAuc } from "../src/oracle";
import { verifyStudy, type Attempt, type StudyReport } from "../src/study";

// This inspector qualifies the frozen bounded Gateway smoke under its declared
// plans, not any twelve-call study. Keep the committed plan here rather than
// trusting a mutable input file.
const FROZEN_PROTOCOL = {
  contract: "algal.lab.study.v1", name: "network-model-smoke", replicateSeeds: [2903], researchers: 2, rounds: 2,
  nodes: 8, edges: 10, failureSteps: 3, discoverySeeds: [71, 139], holdoutSeeds: [2063, 4127, 8263],
} as const;
const FROZEN_SETTINGS = {
  model: "openai/gpt-6-luna", provider: "openai", timeoutMs: 60000, maxCalls: 12, maxOutputBytes: 8192,
  maxResponseBytes: 65536, maxInputBytes: 131072, maxTokens: 2048,
} as const;

const USAGE_KEYS = ["tokensIn", "tokensOut", "totalTokens", "reasoningTokens", "cachedTokens", "cost"] as const;
type UsageKey = typeof USAGE_KEYS[number];
type Usage = Partial<Record<UsageKey, number>>;
type Observation = {
  attempt: number; requestDigest: string; schemaDigest?: string; elapsedMs: number; status: "completed" | "failed";
  dispatched: boolean; uncertain: boolean; httpStatus?: number; requestId?: string; responseId?: string;
  model?: string; finishReason?: string; usage?: Usage; code?: string;
};

function optionalObject(value: unknown, required: string[], optional: readonly string[], label: string) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`${label}: expected object`);
  return object(value, [...required, ...optional.filter((key) => Object.hasOwn(value, key))], label);
}

function configuration(value: unknown) {
  const c = object(value, ["contract", "adapterVersion", "model", "provider", "baseUrl", "proposalContract",
    "timeoutMs", "maxCalls", "maxOutputBytes", "maxResponseBytes", "maxInputBytes", "maxTokens", "temperature", "reasoningEffort",
    "zeroTools", "noFallback", "responseModelForms"], "gateway configuration");
  if (c.contract !== "algal.lab.gateway-executor.v2" || c.adapterVersion !== 2 || c.baseUrl !== "https://ai-gateway.vercel.sh/v1" ||
      c.proposalContract !== PROPOSAL_CONTRACT || c.temperature !== 0 || c.reasoningEffort !== "low" || c.zeroTools !== true ||
      c.noFallback !== true || c.responseModelForms !== "canonical-or-direct-slug" || c.maxInputBytes !== 131072) throw new Error("invalid Gateway configuration");
  const model = text(c.model, 128, "model");
  const provider = text(c.provider, 64, "provider");
  if (!/^[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/.test(model) || !/^[a-z0-9][a-z0-9-]*$/.test(provider)) throw new Error("invalid Gateway selection");
  integer(c.timeoutMs, 1, 60000, "timeout"); integer(c.maxCalls, 1, 12, "call budget");
  const maxOutputBytes = integer(c.maxOutputBytes, 1, 8192, "output bytes");
  integer(c.maxResponseBytes, 1, 65536, "response bytes");
  if (c.maxTokens !== Math.ceil(maxOutputBytes / 4)) throw new Error("invalid Gateway token budget");
  return { value: c, model, provider, executor: `algal-lab:gateway.v2:${model}` };
}

function usage(value: unknown): Usage {
  const u = optionalObject(value, [], USAGE_KEYS, "gateway usage");
  const parsed: Usage = {};
  for (const key of USAGE_KEYS) {
    if (!Object.hasOwn(u, key)) continue;
    if (key === "cost") {
      if (typeof u.cost !== "number" || !Number.isFinite(u.cost) || u.cost < 0 || u.cost > 1000000) throw new Error("invalid Gateway cost");
      parsed.cost = u.cost;
    } else parsed[key] = integer(u[key], 0, 1000000000, key);
  }
  return parsed;
}

function observation(value: unknown): Observation {
  const o = optionalObject(value, ["attempt", "requestDigest", "elapsedMs", "status", "dispatched", "uncertain"],
    ["schemaDigest", "httpStatus", "requestId", "responseId", "model", "finishReason", "usage", "code"], "gateway observation");
  const attempt = integer(o.attempt, 1, 12, "observation attempt");
  const requestDigest = digestString(o.requestDigest);
  const elapsedMs = integer(o.elapsedMs, 0, Number.MAX_SAFE_INTEGER, "elapsed time");
  if ((o.status !== "completed" && o.status !== "failed") || typeof o.dispatched !== "boolean" || typeof o.uncertain !== "boolean") throw new Error("invalid Gateway observation");
  const parsed: Observation = { attempt, requestDigest, elapsedMs, status: o.status, dispatched: o.dispatched, uncertain: o.uncertain };
  if (Object.hasOwn(o, "schemaDigest")) parsed.schemaDigest = digestString(o.schemaDigest);
  if (Object.hasOwn(o, "httpStatus")) parsed.httpStatus = integer(o.httpStatus, 100, 599, "HTTP status");
  for (const key of ["requestId", "responseId"] as const) {
    if (!Object.hasOwn(o, key)) continue;
    const id = text(o[key], 128, key);
    if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(id)) throw new Error("invalid Gateway request identity");
    parsed[key] = id;
  }
  if (Object.hasOwn(o, "model")) parsed.model = text(o.model, 128, "observed model");
  if (Object.hasOwn(o, "finishReason")) {
    const reason = text(o.finishReason, 32, "finish reason");
    if (!["stop", "length", "tool_calls", "function_call", "content_filter"].includes(reason)) throw new Error("invalid Gateway finish reason");
    parsed.finishReason = reason;
  }
  if (Object.hasOwn(o, "usage")) parsed.usage = usage(o.usage);
  if (Object.hasOwn(o, "code")) {
    const code = text(o.code, 64, "failure code");
    if (!(GATEWAY_FAILURE_CODES as readonly string[]).includes(code)) throw new Error("invalid Gateway failure code");
    parsed.code = code;
  }
  if ((parsed.status === "completed" && parsed.code !== undefined) || (parsed.status === "failed" && parsed.code === undefined)) throw new Error("invalid Gateway observation outcome");
  return parsed;
}

export async function inspectGatewaySmoke(directory: string) {
  const study = join(directory, "study");
  const verification = await verifyStudy(study);
  const envelope = object(await readJsonFile(join(study, "study.json")), ["report", "digest"], "study envelope");
  if (digest(envelope.report) !== verification.reportDigest || envelope.digest !== verification.reportDigest) throw new Error("study changed after verification");
  const report = envelope.report as StudyReport;
  if (report.backend !== "command" || report.attempts.length > 12 || report.protocol.nodes > 10) throw new Error("not a bounded Gateway smoke study");
  const sidecar = object(await readJsonFile(join(directory, "gateway.json")), ["configuration", "configurationDigest", "observations", "cancelled"], "transport sidecar");
  const config = object(await readJsonFile(join(directory, "executor.json")), ["configuration", "configurationDigest"], "executor configuration");
  if (!equal(sidecar.configuration, config.configuration) || sidecar.configurationDigest !== config.configurationDigest || digest(config.configuration) !== config.configurationDigest) throw new Error("configuration identity mismatch");
  const selected = configuration(config.configuration);
  const intent = object(await readJsonFile(join(directory, "intent.json")), ["protocol", "model", "provider", "maxCalls"], "smoke intent");
  if (!equal(parseProtocol(intent.protocol), report.protocol) || intent.model !== selected.model || intent.provider !== selected.provider ||
      intent.maxCalls !== report.attempts.length || intent.maxCalls !== selected.value.maxCalls) throw new Error("frozen intent mismatch");
  if (!Array.isArray(sidecar.observations) || sidecar.observations.length > 12 || typeof sidecar.cancelled !== "boolean") throw new Error("invalid transport observations");
  const observations = sidecar.observations.map(observation);
  const store = new ArtifactStore(study);
  const attempts = new Map<string, Attempt>();
  for (const id of report.attempts) attempts.set(id, await store.get(id) as unknown as Attempt);
  const effects = [...attempts.values()].flatMap((attempt) => attempt.receipt.effects.filter((effect) => !effect.executor.startsWith("tool:")));
  const inherited: { child: string; parent: string; condition: string; researcher: number; parentResearcher: number; round: number }[] = [];
  for (const [childId, child] of attempts) {
    if (!child.measurement) continue;
    for (const parentId of child.measurement.proposal.parents) {
      const parent = attempts.get(parentId);
      if (parent?.measurement && parent.context.round < child.context.round && parent.context.researcher !== child.context.researcher &&
          child.context.evidence.some((evidence) => evidence.id === parentId) && digest(parent.measurement.proposal.graph) !== digest(child.measurement.proposal.graph)) {
        inherited.push({ child: childId, parent: parentId, condition: child.context.condition, researcher: child.context.researcher,
          parentResearcher: parent.context.researcher, round: child.context.round });
      }
    }
  }
  const shape = report.protocol.replicateSeeds.length === 1 && report.protocol.researchers === 2 && report.protocol.rounds === 2 && report.attempts.length === 12;
  const acceptedModel = (model: string | undefined) => model === selected.model || model === selected.model.split("/")[1];
  const transportMatches = effects.length === 12 && observations.length === effects.length && observations.every((o, index) =>
    o.attempt === index + 1 && o.requestDigest === effects[index]?.requestDigest && o.status === "completed" && o.dispatched && !o.uncertain &&
    o.httpStatus !== undefined && o.httpStatus >= 200 && o.httpStatus < 300 && o.finishReason === "stop" && o.responseId !== undefined && acceptedModel(o.model));
  const configurationMatches = effects.every((effect) => effect.configurationDigest === config.configurationDigest && effect.executor === selected.executor &&
    effect.retryable === false && effect.cached !== true && acceptedModel(effect.usage?.model));
  const usageMatches = observations.length === effects.length && observations.every((o, index) => {
    const recorded = effects[index]?.usage;
    return recorded?.model === o.model && recorded?.tokensIn === o.usage?.tokensIn && recorded?.tokensOut === o.usage?.tokensOut;
  });
  const generationIds = observations.filter((o) => o.status === "completed").map((o) => o.responseId);
  const frozenPlanMatches = equal(report.protocol, FROZEN_PROTOCOL) && Object.entries(FROZEN_SETTINGS).every(([key, value]) => selected.value[key] === value);
  const controls = { frozenPlanMatches, boundedTwelveCallStudy: shape, everyProposalMeasured: verification.experiments === 12,
    transportReportsCompleted: transportMatches, receiptConfigurationMatches: configurationMatches, receiptUsageMatches: usageMatches,
    distinctGenerationRequests: generationIds.every((id) => id !== undefined) && new Set(generationIds).size === generationIds.length,
    notCancelled: sidecar.cancelled === false, changedDesignFromVisiblePeer: inherited.length > 0,
    // v2 dispatches the exact-budget proposal contract for the run's protocol.
    exactBudgetContract: observations.length > 0 &&
      observations.every((o) => o.schemaDigest === digest(proposalContractSchema(report.protocol.nodes, report.protocol.edges))) };
  // Do not turn omitted provider usage or a partial/mismatched archive into zero.
  const completeAccounting = transportMatches && configurationMatches && usageMatches && controls.distinctGenerationRequests;
  const total = (key: UsageKey): number | null => completeAccounting && observations.every((o) => o.usage?.[key] !== undefined)
    ? observations.reduce((sum, o) => sum + o.usage![key]!, 0) : null;
  const source = await readFile(new URL(import.meta.url), "utf8");
  return {
    contract: "algal.lab.gateway-smoke-inspection.v1", reportDigest: verification.reportDigest,
    analysisDigest: `sha256:${createHash("sha256").update(source).digest("hex")}`,
    passed: Object.values(controls).every(Boolean), controls, configuration: config.configuration,
    models: [...new Set(effects.map((effect) => effect.usage?.model ?? "unreported"))],
    usage: { tokensIn: total("tokensIn"), tokensOut: total("tokensOut"), totalTokens: total("totalTokens"),
      reasoningTokens: total("reasoningTokens"), cachedTokens: total("cachedTokens"), cost: total("cost") },
    usageLimits: "Totals include only provider-reported values matched to every generation; null means at least one value is unavailable or transport/receipt matching failed. Cost is supplemental Gateway metadata, not an independently verified bill.",
    proposals: verification.experiments, attempts: report.attempts.length, inheritance: inherited,
    champions: CONDITIONS.map((condition) => {
      const summary = report.summaries.find((item) => item.condition === condition)!;
      const graph = summary.selectedAttempt ? attempts.get(summary.selectedAttempt)?.measurement?.proposal.graph : undefined;
      return { condition, graphDigest: graph ? digest(graph) : null, exactRandomAuc: graph ? exactRandomAuc(graph, report.protocol.failureSteps) : null, targetedAuc: summary.selectedTargetedAuc };
    }),
    limits: "This checks archived operational inheritance and internally consistent HTTP generation reports. It does not authenticate provider claims or establish a sharing advantage, causal influence, or a transferable discovery.",
  };
}

if (import.meta.main) {
  if (Bun.argv.length !== 3) throw new Error("usage: bun scripts/inspect-gateway-smoke.ts RUN_DIRECTORY");
  const result = await inspectGatewaySmoke(Bun.argv[2]!);
  console.log(JSON.stringify(result, null, 2));
  if (!result.passed) process.exitCode = 1;
}
