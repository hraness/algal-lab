import { AlgalError, digestCanonical, vercelGatewayExecutor, type EffectRequest, type Executor, type ExecutorResult, type JsonValue } from "@hraness/algal";

/** Experimental, explicit opt-in transport. The normal public run has no network. */
export const MODEL = "openai/gpt-6-luna";
const PRICES = { input: 0.1 / 1e6, output: 0.5 / 1e6 };
export const PRICE_SOURCE = "https://ai-gateway.vercel.sh/v1/models";
export type LiveObservation = {
  ordinal: number; requestDigest: string; status: "completed" | "failed";
  inputTokens: number | null; outputTokens: number | null; elapsedMs: number;
  estimatedUSD: number; uncertain: boolean; generationId: string | null;
};
export type LiveBudget = { maxCalls: number; maxEstimatedUSD: number };

export function createLiveExecutor(budget: LiveBudget): Executor & { observations: LiveObservation[]; configuration: JsonValue } {
  if (!Number.isSafeInteger(budget.maxCalls) || budget.maxCalls < 1 || budget.maxCalls > 400 ||
      !Number.isFinite(budget.maxEstimatedUSD) || budget.maxEstimatedUSD <= 0 || budget.maxEstimatedUSD > 5) {
    throw new Error("live run permits 1..400 calls and at most $5 estimated spend");
  }
  if (!(process.env.AI_GATEWAY_API_KEY ?? process.env.VERCEL_OIDC_TOKEN)) throw new Error("AI_GATEWAY_API_KEY or VERCEL_OIDC_TOKEN is required for explicit live mode");
  const maxInputBytes = 32_768, maxCompletionTokens = 1024;
  const configuration: JsonValue = { model: MODEL, endpoint: "https://ai-gateway.vercel.sh/v1/chat/completions", maxInputBytes,
    maxCompletionTokens, provider: "openai", fallback: false, reasoningEffort: "none", serviceTier: "default", store: false, budget, priceSource: PRICE_SOURCE,
    priceDate: "2026-09-27", pricesUSDPerToken: PRICES, temperature: "provider default (omitted)", pricing: "standard uncached estimate; invoice may differ", retry: false };
  const configurationDigest = digestCanonical(configuration);
  const observations: LiveObservation[] = [];
  let charged = 0, calls = 0, busy = false, uncertain = false;
  let reservation = 0;
  let generationId: string | null = null;
  const inner = vercelGatewayExecutor({
    model: MODEL,
    maxResponseBytes: 131_072,
    observeGeneration: generation => { generationId = generation.generationId; },
    async fetch(input, init) {
      if (String(input) !== "https://ai-gateway.vercel.sh/v1/chat/completions" || init?.method !== "POST" || typeof init.body !== "string") {
        throw new Error("unexpected provider transport");
      }
      const body = JSON.parse(init.body) as Record<string, unknown>;
      body.max_tokens = maxCompletionTokens;
      delete body.temperature;
      body.providerOptions = { gateway: { only: ["openai"] } };
      body.reasoning_effort = "none";
      body.store = false;
      body.service_tier = "default";
      const serialized = JSON.stringify(body);
      const bytes = Buffer.byteLength(serialized);
      if (bytes > maxInputBytes) throw new Error("live input byte ceiling exceeded");
      // Byte count plus protocol allowance is deliberately conservative. This
      // is an estimate guard, not a provider billing guarantee.
      reservation = (bytes + 512) * PRICES.input + maxCompletionTokens * PRICES.output;
      if (charged + reservation > budget.maxEstimatedUSD) throw new Error("estimated spend ceiling reached");
      calls++;
      charged += reservation;
      return fetch(input, { ...init, redirect: "error", body: serialized });
    },
  });
  const executeEffect = async (request: EffectRequest, signal?: AbortSignal): Promise<ExecutorResult> => {
    if (busy || uncertain || calls >= budget.maxCalls || signal?.aborted) throw new AlgalError("BUDGET_EXHAUSTED", "live executor unavailable or budget exhausted");
    busy = true;
    reservation = 0;
    generationId = null;
    const before = calls, start = performance.now();
    try {
      const result = await inner.executeEffect!(request, signal);
      const usage = result.metadata?.usage;
      if (!usage || (usage.model !== MODEL && usage.model !== MODEL.split("/")[1])) throw new Error("provider model identity changed");
      const inputTokens = usage.tokensIn ?? null, outputTokens = usage.tokensOut ?? null;
      const estimate = inputTokens === null || outputTokens === null ? reservation : inputTokens * PRICES.input + outputTokens * PRICES.output;
      charged += estimate - reservation;
      observations.push({ ordinal: calls, requestDigest: digestCanonical(request as unknown as JsonValue), status: "completed",
        inputTokens, outputTokens, elapsedMs: performance.now() - start, estimatedUSD: estimate, uncertain: false, generationId });
      return { output: result.output, metadata: { ...result.metadata, executor: `task-study:${configurationDigest}`, configurationDigest, retryable: false } };
    } catch (error) {
      // No remote retries after any dispatched failure; a provider may have
      // completed work even when the client cannot retain the answer.
      uncertain = calls > before;
      observations.push({ ordinal: calls, requestDigest: digestCanonical(request as unknown as JsonValue), status: "failed",
        inputTokens: null, outputTokens: null, elapsedMs: performance.now() - start, estimatedUSD: reservation, uncertain, generationId });
      throw error instanceof AlgalError ? error : new AlgalError("EFFECT_FAILED", "live study request failed; inspect sanitized observations", undefined, { uncertain });
    } finally { busy = false; }
  };
  return { id: `task-study:${configurationDigest}`, capabilities: { effects: ["agent", "classifier"] }, cacheable: false,
    retryable: false, configuration, observations, executeEffect,
    execute: async (request, signal) => (await executeEffect(request, signal)).output,
    receiptFor: () => ({ executor: `task-study:${configurationDigest}`, configurationDigest, retryable: false }),
  };
}
