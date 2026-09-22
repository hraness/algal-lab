import { AlgalError, canonicalize, digestCanonical, effectRequestDigest, vercelGatewayExecutor, VERCEL_AI_GATEWAY_BASE_URL, type EffectRequest, type Executor, type ExecutorMetadata, type ExecutorResult, type GatewayFetch, type JsonObject } from "@hraness/algal";
import { json } from "./contracts";

const MAX_INPUT_BYTES = 131072;
const TOKEN_LIMIT = 1_000_000_000;
const FINISH_REASONS = ["stop", "length", "tool_calls", "function_call", "content_filter"];

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object") {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}

/** Provider-side structural hints. Host parseProposal remains authoritative for
 * byte limits, connectedness, exact budgets, and visible parent references. This
 * lives outside the manifest because ALGAL deliberately limits schema depth. */
export const GATEWAY_PROPOSAL_SCHEMA: JsonObject = freeze({
  type: "object", additionalProperties: false,
  required: ["graph", "hypothesis", "prediction", "rationale", "parents", "message"],
  properties: {
    graph: {
      type: "object", additionalProperties: false, required: ["nodes", "edges"],
      properties: {
        nodes: { type: "integer", minimum: 4, maximum: 16 },
        edges: { type: "array", minItems: 3, maxItems: 48, items: { type: "array", minItems: 2, maxItems: 2, items: { type: "integer", minimum: 0, maximum: 15 } } },
      },
    },
    hypothesis: { type: "string", minLength: 1, maxLength: 1000 },
    prediction: { type: "number", minimum: 0, maximum: 1 },
    rationale: { type: "string", minLength: 1, maxLength: 1000 },
    parents: { type: "array", maxItems: 8, items: { type: "string", pattern: "^sha256:[a-f0-9]{64}$", maxLength: 71 } },
    message: { type: "string", minLength: 1, maxLength: 500 },
  },
});
export const GATEWAY_SCHEMA_DIGEST = digestCanonical(GATEWAY_PROPOSAL_SCHEMA);

export const GATEWAY_FAILURE_CODES = [
  "invalid_options", "invalid_selection", "unsupported_effect", "invalid_context", "input_limit", "output_limit", "response_limit", "invalid_response", "model_mismatch", "incomplete_response", "tool_calls_forbidden", "redirect_forbidden", "provider_error", "credential_unavailable", "transport_error", "cancelled", "deadline", "completion_uncertain", "call_budget_exhausted", "executor_busy",
] as const;
type FailureCode = typeof GATEWAY_FAILURE_CODES[number];

export type GatewayExecutorOptions = {
  /** Exact model and provider observed in the current Gateway catalog. */
  model: string;
  provider: string;
  credential?: string;
  fetch?: GatewayFetch;
  timeoutMs?: number;
  maxCalls?: number;
  maxOutputBytes?: number;
  maxResponseBytes?: number;
  signal?: AbortSignal;
};
export type GatewayConfiguration = Readonly<{
  contract: "algal.lab.gateway-executor.v1";
  adapterVersion: 1;
  model: string;
  provider: string;
  baseUrl: typeof VERCEL_AI_GATEWAY_BASE_URL;
  schemaDigest: `sha256:${string}`;
  timeoutMs: number;
  maxCalls: number;
  maxOutputBytes: number;
  maxResponseBytes: number;
  maxInputBytes: number;
  maxTokens: number;
  temperature: 0;
  reasoningEffort: "low";
  zeroTools: true;
  noFallback: true;
  responseModelForms: "canonical-or-direct-slug";
}>;
export type GatewayUsage = Readonly<{
  tokensIn?: number;
  tokensOut?: number;
  totalTokens?: number;
  reasoningTokens?: number;
  cachedTokens?: number;
  cost?: number;
}>;
/** Bounded transport evidence only; no prompts, credentials, or raw errors. */
export type GatewayObservation = Readonly<{
  attempt: number;
  requestDigest: `sha256:${string}`;
  elapsedMs: number;
  status: "completed" | "failed";
  dispatched: boolean;
  uncertain: boolean;
  httpStatus?: number;
  requestId?: string;
  responseId?: string;
  model?: string;
  finishReason?: string;
  usage?: GatewayUsage;
  code?: FailureCode;
}>;
export type GatewayExecutor = Executor & {
  readonly configuration: GatewayConfiguration;
  readonly configurationDigest: `sha256:${string}`;
  readonly observations: readonly GatewayObservation[];
  /** Wait for local cancellation handling. Uncertain external completion stays
   * uncertain and blocks every later dispatch from this executor. */
  settle(): Promise<void>;
};

class GatewayError extends AlgalError {
  constructor(readonly failureCode: FailureCode, uncertain = false) {
    super(["deadline", "cancelled", "call_budget_exhausted"].includes(failureCode) ? "BUDGET_EXHAUSTED" : "EFFECT_FAILED", `gateway application: ${failureCode}`, undefined, { uncertain });
  }
}
function record(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new GatewayError("invalid_response");
  return value as Record<string, unknown>;
}
function bound(value: unknown, max: number): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 1 || value > max) throw new GatewayError("invalid_options");
  return value;
}
function token(value: unknown): number | undefined {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0 && value <= TOKEN_LIMIT ? value : undefined;
}
function usage(value: unknown): GatewayUsage | undefined {
  if (value === undefined) return undefined;
  const raw = record(value);
  const details = (value: unknown): Record<string, unknown> => value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
  const output: Record<string, number> = {};
  for (const [name, value] of Object.entries({
    tokensIn: raw.prompt_tokens ?? raw.input_tokens,
    tokensOut: raw.completion_tokens ?? raw.output_tokens,
    totalTokens: raw.total_tokens,
    reasoningTokens: details(raw.completion_tokens_details ?? raw.output_tokens_details).reasoning_tokens,
    cachedTokens: details(raw.prompt_tokens_details ?? raw.input_tokens_details).cached_tokens,
  })) {
    const admitted = token(value);
    if (admitted !== undefined) output[name] = admitted;
  }
  const reported = raw.cost;
  const cost = typeof reported === "number" ? reported : typeof reported === "string" && /^(?:0|[1-9][0-9]{0,6})(?:\.[0-9]{1,18})?$/.test(reported) ? Number(reported) : undefined;
  if (cost !== undefined && Number.isFinite(cost) && cost >= 0 && cost <= 1_000_000) output.cost = cost;
  return Object.keys(output).length ? Object.freeze(output) : undefined;
}
function identifier(value: unknown, credential: string): string | undefined {
  return typeof value === "string" && /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(value) && !value.includes(credential) ? value : undefined;
}
function abortable<T>(work: Promise<T>, signal: AbortSignal, failure: () => GatewayError): Promise<T> {
  return new Promise((resolve, reject) => {
    const abort = () => reject(failure());
    signal.addEventListener("abort", abort, { once: true });
    // Attach handlers even if already aborted: late rejection must be observed.
    work.then(resolve, reject).finally(() => signal.removeEventListener("abort", abort));
    if (signal.aborted) abort();
  });
}
async function responseBytes(response: Response, limit: number, signal: AbortSignal, aborted: () => GatewayError): Promise<Uint8Array> {
  if (Number(response.headers.get("content-length")) > limit) {
    void response.body?.cancel().catch(() => {});
    throw new GatewayError("response_limit", true);
  }
  if (!response.body) return new Uint8Array();
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let length = 0;
  try {
    for (;;) {
      const part = await abortable(reader.read(), signal, aborted);
      if (part.done) break;
      length += part.value.byteLength;
      if (length > limit) throw new GatewayError("response_limit", true);
      chunks.push(part.value);
    }
  } catch (error) {
    void reader.cancel().catch(() => {});
    throw error instanceof GatewayError ? error : new GatewayError("transport_error", true);
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return bytes;
}

/** Reuse ALGAL's fixed-origin, zero-tool Chat Completions executor while adding
 * the laboratory's protocol bounds and sanitized transport observations. */
export function createGatewayExecutor(input: GatewayExecutorOptions): GatewayExecutor {
  const raw = record(input);
  if (Object.keys(raw).some((key) => !["model", "provider", "credential", "fetch", "timeoutMs", "maxCalls", "maxOutputBytes", "maxResponseBytes", "signal"].includes(key)) ||
      (raw.fetch !== undefined && typeof raw.fetch !== "function") || (raw.signal !== undefined && !(raw.signal instanceof AbortSignal)) ||
      (raw.credential !== undefined && typeof raw.credential !== "string")) throw new GatewayError("invalid_options");
  const { model, provider } = input;
  if (typeof model !== "string" || model.length > 128 || !/^[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/.test(model) ||
      typeof provider !== "string" || provider.length > 64 || !/^[a-z0-9][a-z0-9-]*$/.test(provider)) throw new GatewayError("invalid_selection");
  const maxOutputBytes = bound(input.maxOutputBytes ?? 8192, 8192);
  const configuration: GatewayConfiguration = Object.freeze({
    contract: "algal.lab.gateway-executor.v1", adapterVersion: 1, model, provider, baseUrl: VERCEL_AI_GATEWAY_BASE_URL, schemaDigest: GATEWAY_SCHEMA_DIGEST,
    timeoutMs: bound(input.timeoutMs ?? 60000, 60000), maxCalls: bound(input.maxCalls ?? 12, 12), maxOutputBytes,
    maxResponseBytes: bound(input.maxResponseBytes ?? 65536, 65536), maxInputBytes: MAX_INPUT_BYTES,
    maxTokens: Math.ceil(maxOutputBytes / 4), temperature: 0, reasoningEffort: "low", zeroTools: true, noFallback: true, responseModelForms: "canonical-or-direct-slug",
  });
  const configurationDigest = digestCanonical(json(configuration));
  const id = `algal-lab:gateway.v1:${model}`;
  const metadata: ExecutorMetadata = { executor: id, configurationDigest, retryable: false };
  const fetcher = input.fetch ?? globalThis.fetch;
  const observations: GatewayObservation[] = [];
  let attempts = 0;
  let uncertain = false;
  let active: Promise<ExecutorResult> | undefined;

  const perform = async (request: EffectRequest, signal?: AbortSignal): Promise<ExecutorResult> => {
    if (attempts >= configuration.maxCalls) throw new GatewayError("call_budget_exhausted");
    // Runtime requests already satisfy ALGAL's contract; this also bounds direct
    // callers before canonicalization and guarantees the original digest below.
    try { json(request); } catch { throw new GatewayError("invalid_context"); }
    const requestDigest = effectRequestDigest(request);
    const attempt = ++attempts;
    const started = performance.now();
    const observed: { -readonly [K in keyof GatewayObservation]: GatewayObservation[K] } = {
      attempt, requestDigest, elapsedMs: 0, status: "failed", dispatched: false, uncertain: false,
    };
    const controller = new AbortController();
    let expired = false;
    const aborted = () => new GatewayError(expired ? "deadline" : "cancelled", observed.dispatched);
    const cancel = () => controller.abort();
    input.signal?.addEventListener("abort", cancel, { once: true });
    signal?.addEventListener("abort", cancel, { once: true });
    if (input.signal?.aborted || signal?.aborted) cancel();
    const timer = setTimeout(() => { expired = true; cancel(); }, configuration.timeoutMs);
    let failure: GatewayError | undefined;
    try {
      if (uncertain) throw new GatewayError("completion_uncertain", true);
      if (controller.signal.aborted) throw aborted();
      if (request.contract !== "algal.effect.v1" || request.kind !== "agent" || request.output.kind !== "json") throw new GatewayError("unsupported_effect");
      const context = record(request.context.inputs);
      if (record(context.context).contract !== "algal.lab.context.v1") throw new GatewayError("invalid_context");
      if (typeof request.prompt !== "string" || Buffer.byteLength(request.prompt) > 8192 ||
          Buffer.byteLength(canonicalize(request.context)) > bound(request.budget.maxContextBytes, 65536)) throw new GatewayError("input_limit");
      const outputLimit = Math.min(maxOutputBytes, bound(request.budget.maxOutputBytes, 8192));
      const credential = input.credential ?? process.env.AI_GATEWAY_API_KEY ?? process.env.VERCEL_OIDC_TOKEN;
      if (typeof credential !== "string" || credential.length < 16 || credential.length > 8192 || /[\r\n]/.test(credential)) throw new GatewayError("credential_unavailable");
      const boundedFetch: GatewayFetch = async (url, init) => {
        try {
          if (url !== `${VERCEL_AI_GATEWAY_BASE_URL}/chat/completions` || init?.method !== "POST" || init.redirect !== "error" || typeof init.body !== "string") throw new GatewayError("invalid_response");
          const body = record(JSON.parse(init.body));
          if (Object.hasOwn(body, "tools") || Object.hasOwn(body, "functions")) throw new GatewayError("tool_calls_forbidden");
          body.providerOptions = { gateway: { only: [provider] } };
          body.reasoning_effort = "low";
          const encoded = canonicalize(json(body));
          if (Buffer.byteLength(encoded) > configuration.maxInputBytes) throw new GatewayError("input_limit");
          if (controller.signal.aborted) throw aborted();
          observed.dispatched = true;
          const response = await abortable(fetcher(url, { ...init, body: encoded, cache: "no-store", signal: controller.signal }), controller.signal, aborted);
          observed.httpStatus = response.status;
          const requestId = identifier(response.headers.get("x-request-id"), credential);
          if (requestId) observed.requestId = requestId;
          if (response.redirected || (response.status >= 300 && response.status < 400)) {
            void response.body?.cancel().catch(() => {});
            throw new GatewayError("redirect_forbidden");
          }
          const bytes = await responseBytes(response, configuration.maxResponseBytes, controller.signal, aborted);
          if (!response.ok) throw new GatewayError("provider_error");
          let raw: Record<string, unknown>;
          try { raw = record(json(JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)))); }
          catch { throw new GatewayError("invalid_response"); }
          const responseId = identifier(raw.id, credential);
          if (responseId) observed.responseId = responseId;
          const reportedUsage = usage(raw.usage);
          if (reportedUsage) observed.usage = reportedUsage;
          if (raw.model !== model && raw.model !== model.split("/")[1]) throw new GatewayError("model_mismatch");
          observed.model = raw.model as string;
          if (!Array.isArray(raw.choices) || raw.choices.length !== 1) throw new GatewayError("invalid_response");
          const choice = record(raw.choices[0]);
          if (typeof choice.finish_reason === "string" && FINISH_REASONS.includes(choice.finish_reason)) observed.finishReason = choice.finish_reason;
          const message = record(choice.message);
          if ((message.tool_calls !== undefined && (!Array.isArray(message.tool_calls) || message.tool_calls.length !== 0)) || message.function_call != null) throw new GatewayError("tool_calls_forbidden");
          if (choice.finish_reason !== "stop") throw new GatewayError("incomplete_response");
          if (typeof message.content !== "string") throw new GatewayError("invalid_response");
          let structured: Record<string, unknown>;
          try { structured = record(json(JSON.parse(message.content))); }
          catch { throw new GatewayError("invalid_response"); }
          if (Object.keys(structured).length !== 1 || !Object.hasOwn(structured, "value")) throw new GatewayError("invalid_response");
          const proposed = canonicalize(json(structured.value));
          // The provider sees the bearer credential at the transport boundary.
          // Never let an exact echo enter ALGAL's durable effect output, including
          // echoes in object keys or JSON-escaped text.
          if (proposed.includes(credential) || proposed.includes(JSON.stringify(credential).slice(1, -1))) throw new GatewayError("invalid_response");
          if (Buffer.byteLength(proposed) > outputLimit) throw new GatewayError("output_limit");
          // Preserve ALGAL's parser and executeEffect usage while admitting only
          // the bounded usage fields represented by the sidecar.
          raw.usage = { ...(reportedUsage?.tokensIn !== undefined ? { prompt_tokens: reportedUsage.tokensIn } : {}), ...(reportedUsage?.tokensOut !== undefined ? { completion_tokens: reportedUsage.tokensOut } : {}) };
          return Response.json(raw);
        } catch (error) {
          failure = error instanceof GatewayError ? error : controller.signal.aborted ? aborted() : new GatewayError("transport_error", observed.dispatched);
          throw failure;
        }
      };
      const inner = vercelGatewayExecutor({ model, credential, fetch: boundedFetch, maxResponseBytes: configuration.maxResponseBytes });
      const adapted: EffectRequest = { ...request, output: { kind: "json", schema: GATEWAY_PROPOSAL_SCHEMA }, budget: { ...request.budget, maxOutputBytes: outputLimit } };
      const result = await inner.executeEffect!(adapted, controller.signal);
      if (controller.signal.aborted) throw aborted();
      observed.status = "completed";
      return { output: result.output, metadata: { ...result.metadata, ...metadata } };
    } catch (error) {
      const safe = failure ?? (error instanceof GatewayError ? error : controller.signal.aborted ? aborted() : new GatewayError("invalid_response"));
      observed.code = safe.failureCode;
      observed.uncertain = safe.uncertain;
      if (safe.uncertain) uncertain = true;
      throw safe;
    } finally {
      clearTimeout(timer);
      input.signal?.removeEventListener("abort", cancel);
      signal?.removeEventListener("abort", cancel);
      observed.elapsedMs = Math.max(0, Math.round(performance.now() - started));
      observations.push(freeze(observed));
    }
  };
  const executeEffect = (request: EffectRequest, signal?: AbortSignal): Promise<ExecutorResult> => {
    if (active) return Promise.reject(new GatewayError("executor_busy"));
    active = perform(request, signal).finally(() => { active = undefined; });
    return active;
  };
  return {
    id, capabilities: { effects: ["agent"] }, cacheable: false, retryable: false,
    configuration, configurationDigest,
    get observations() { return Object.freeze([...observations]); },
    receiptFor: () => ({ ...metadata }),
    executeEffect,
    execute: async (request, signal) => (await executeEffect(request, signal)).output,
    settle: async () => { await active?.catch(() => {}); if (uncertain) throw new GatewayError("completion_uncertain", true); },
  };
}
