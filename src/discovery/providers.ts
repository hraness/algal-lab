import { integer, text, type Provider } from "./contracts";

export type RemoteProvider = Exclude<Provider, { kind: "control" }>;
export type ProviderResult = { responseId: string | null; reportedModel?: string; text: string | null; usage: { inputTokens: number; outputTokens: number } | null; completionError?: string };
type Fetch = (input: string | URL | Request, init?: RequestInit) => Promise<Response>;
function record(value: unknown, label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new Error(`invalid ${label}`);
  return value as Record<string, unknown>;
}
function optionalText(value: unknown, max: number): string | null {
  return typeof value === "string" && value.length > 0 && Buffer.byteLength(value) <= max ? value : null;
}
function tokenCount(value: unknown, label: string): number {
  return integer(value, 0, Number.MAX_SAFE_INTEGER, label);
}
/** Capture safe metadata and usage before classifying candidate completion.
 * Nonfinal replies are evidence, but their candidate text is never evaluated. */
export function decodeResponse(provider: RemoteProvider, raw: unknown): ProviderResult {
  const root = record(raw, "provider response");
  const usage = root[provider.kind === "xai" ? "usage" : "usageMetadata"];
  const counts = usage === undefined ? null : record(usage, "usage");
  const inputTokens = counts === null ? null : tokenCount(provider.kind === "xai" ? counts.prompt_tokens : counts.promptTokenCount, "input tokens");
  const outputTokens = counts === null ? null : provider.kind === "xai" ? tokenCount(counts.completion_tokens, "output tokens")
    : tokenCount(tokenCount(counts.candidatesTokenCount ?? 0, "candidatesTokenCount") + tokenCount(counts.thoughtsTokenCount ?? 0, "thoughtsTokenCount"), "output tokens");
  const reportedModel = optionalText(provider.kind === "xai" ? root.model : root.modelVersion, 300);
  const result: ProviderResult = {
    responseId: optionalText(provider.kind === "xai" ? root.id : root.responseId, 300),
    ...(reportedModel === null ? {} : { reportedModel }), text: null,
    usage: inputTokens === null || outputTokens === null ? null : { inputTokens, outputTokens },
  };
  // Malformed candidate content must not discard already reported billing usage.
  try {
    if (provider.kind === "xai") {
      const choices = root.choices;
      if (!Array.isArray(choices) || choices.length !== 1) throw new Error("expected one xAI response choice");
      const choice = record(choices[0], "choice");
      if (choice.finish_reason !== "stop") result.completionError = "xAI response did not finish normally";
      const message = record(choice.message, "message");
      result.text = message.content === null || message.content === undefined || message.content === "" ? null : text(message.content, 100000, "response text");
      if (message.tool_calls !== undefined) result.completionError = "model tool requests are not supported";
    } else {
      const candidates = root.candidates;
      if (!Array.isArray(candidates) || candidates.length !== 1) throw new Error("expected one Gemini response candidate");
      const candidate = record(candidates[0], "candidate");
      if (candidate.finishReason !== "STOP") result.completionError = "Gemini response did not finish normally";
      if (candidate.content !== undefined) {
        const content = record(candidate.content, "content");
        if (!Array.isArray(content.parts) || content.parts.length < 1 || content.parts.length > 32) throw new Error("invalid Gemini parts");
        const parts = content.parts.map(part => record(part, "part"));
        const output = parts.filter(part => part.thought !== true && part.text !== undefined).map(part => part.text === "" ? "" : text(part.text, 100000, "part text")).join("");
        result.text = output === "" ? null : text(output, 100000, "response text");
        if (parts.some(part => part.functionCall !== undefined || part.executableCode !== undefined)) result.completionError = "model tool requests are not supported";
      }
    }
    if (result.text === null && result.completionError === undefined) result.completionError = "provider returned no candidate text";
  } catch {
    result.completionError = "provider candidate content did not pass response checks";
  }
  return result;
}

/** Fixed HTTPS hosts, no redirects, tools, SDK retry behavior, shell, or endpoint override. */
export async function requestModel(provider: RemoteProvider, requestId: string, prompt: string, options: { live: boolean; fetch?: Fetch; env?: Record<string, string | undefined> }): Promise<ProviderResult> {
  if (!options.live) throw new Error("live inference requires --live");
  const env = options.env ?? process.env;
  const key = env[provider.kind === "xai" ? "XAI_API_KEY" : "GEMINI_API_KEY"];
  if (!key) throw new Error(`missing ${provider.kind === "xai" ? "XAI_API_KEY" : "GEMINI_API_KEY"}`);
  const common = { method: "POST", redirect: "error" as const, signal: AbortSignal.timeout(provider.timeoutMs) };
  const request = provider.kind === "xai" ? {
    url: "https://api.x.ai/v1/chat/completions", options: { ...common, headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}`, "X-Client-Request-Id": requestId }, body: JSON.stringify({ model: provider.model, messages: [{ role: "user", content: prompt }], max_tokens: provider.maxOutputTokens, response_format: { type: "json_object" }, stream: false }) },
  } : {
    url: `https://generativelanguage.googleapis.com/v1beta/models/${provider.model}:generateContent`, options: { ...common, headers: { "Content-Type": "application/json", "x-goog-api-key": key }, body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: provider.maxOutputTokens, responseMimeType: "application/json", candidateCount: 1 } }) },
  };
  // Errors omit response bodies and headers, which can contain provider account details.
  const response = await (options.fetch ?? fetch)(request.url, request.options);
  if (!response.ok) throw new Error(`provider returned HTTP ${response.status}`);
  if (Number(response.headers.get("content-length") ?? 0) > 200000) throw new Error("provider response exceeds limit");
  if (!response.body) throw new Error("provider returned no body");
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let bytes = 0;
  try {
    for (;;) {
      const chunk = await reader.read();
      if (chunk.done) break;
      bytes += chunk.value.byteLength;
      if (bytes > 200000) throw new Error("provider response exceeds limit");
      chunks.push(chunk.value);
    }
  } finally { await reader.cancel(); }
  return decodeResponse(provider, JSON.parse(Buffer.concat(chunks).toString("utf8")) as unknown);
}
