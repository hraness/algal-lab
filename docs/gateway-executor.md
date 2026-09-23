# Vercel AI Gateway inference

The [Gateway entry point](../examples/gateway-study.ts) reuses
`vercelGatewayExecutor` from the existing pinned ALGAL dependency. XCB is not
involved in this route. The default demo, qualification, and CI remain offline
and require no provider credentials.

Select a model and inference provider from the current Gateway catalog:

```sh
vercel ai-gateway models list --scope YOUR_TEAM --json
vercel ai-gateway models endpoints MODEL_ID --scope YOUR_TEAM --json
```

Supply an authorized `AI_GATEWAY_API_KEY` or short-lived `VERCEL_OIDC_TOKEN` through
the operator environment. Do not put credentials in protocols, command arguments,
artifacts, or Git. The entry point does not create credentials, fetch project
environment variables, purchase credits, or change account settings. See Vercel's
[authentication documentation](https://vercel.com/docs/ai-gateway/authentication-and-byok).

For the [frozen first Gateway smoke](gateway-smoke-plan.md), select Luna explicitly
and use a fresh directory:

```sh
GATEWAY_MODEL=openai/gpt-6-luna GATEWAY_PROVIDER=openai \
  bun examples/gateway-study.ts --protocol examples/network-model-smoke.json --out runs/gateway-smoke
bun run lab verify runs/gateway-smoke/study
bun scripts/inspect-gateway-smoke.ts runs/gateway-smoke
```

The [first recorded run](gateway-smoke-findings.md) completed twelve generations
and eleven valid experiments; its strict acceptance correctly failed. The
[v2 plan](proposal-contract-v2-plan.md) froze the exact-budget contract and the
next smoke's acceptance before further inference; the
[second run](gateway-smoke-v2-findings.md) measured all twelve proposals and
passed.

Each request uses the fixed Gateway origin, a selected model and provider, zero
temperature, low reasoning effort, a sixty-second deadline, an 8 KiB proposal
limit, and no tools. The lab wrapper supplies a provider JSON schema while
preserving the original VM manifest and host graph admission. Under
`algal.lab.gateway-executor.v2` that schema is the versioned
`algal.lab.proposal.v2` contract built per request: it encodes the admitted
context's exact node and edge budgets and each transport observation records the
dispatched schema digest. ALGAL's Gateway adapter wraps the proposal in `value`
on the wire and extracts it before measurement.

The executor is transport, not a judge of proposals. Once a completed generation
yields syntactically valid JSON whose wrapper is exactly `{value}`, the bounded,
credential-free value is handed to the host unchanged, even when it ignores the
dispatched budget. Host `parseProposal` then rejects an over- or under-budget,
disconnected, or otherwise inadmissible design, and ALGAL records that design as
the effect `output` next to the measurement tool's error inside the attempt
receipt, exactly as the v1 executor did. Offline verification replays such
attempts and reproduces the same rejection. The transport observation for such a
call is `completed` with no failure code; the rejection lives in the verified
receipt, where the proposed design remains inspectable. (The
[v2 plan](proposal-contract-v2-plan.md) originally had the executor reject
budget deviations as `invalid_response`; that discarded the model's design and
was reversed. `everyProposalMeasured` still fails for such a run.)

The configuration digest covers the contract version, provider selection, and
request limits.
Every request remains stateless and receives only its bounded research context.
The wrapper performs no client retries or alternate-model fallback.

## Failure codes and retained values

Every failed observation carries exactly one `code` from `GATEWAY_FAILURE_CODES`.
The codes that describe a completed HTTP exchange are distinct so an analysis
can separate budget violations, malformed responses, and contract deviations:

- `invalid_response`: malformed transport or JSON with nothing admissible to
  retain: a non-JSON or non-object body, zero or several choices, a missing
  message, non-text content, content that is not finite bounded JSON, a wrapper
  that is not an object or lacks `value`, or a value that echoes the credential
  (an echo is never retained anywhere).
- `contract_violation`: a syntactically valid response whose wrapper broke the
  dispatched strict schema (extra keys beside `value`). The host cannot receive
  it, so the observation retains the wrapper's `value` as `rejected`: a
  credential-free copy bounded by the same output limit as admitted proposals,
  so at most 8 KiB canonical. Extra wrapper keys are never retained.
- `output_limit`, `input_limit`, `response_limit`, `call_budget_exhausted`:
  byte and call budgets. An over-limit value is not retained because it exceeds
  the retention bound; the code alone distinguishes it from a malformed response.
- `model_mismatch`, `incomplete_response`, `tool_calls_forbidden`,
  `redirect_forbidden`, `provider_error`: definite provider-side failures with
  the HTTP status and identifiers retained and the body withheld.

Malformed or missing usage never fails a completed generation. A `usage: null`
report, which providers emit for some billed generations, is treated as absent,
exactly like ALGAL's own adapter (`usage ?? {}`); the observation and receipt
then carry no token counts rather than a discarded generation.

## Uncertainty latch

A failure is uncertain only when the executor cannot know whether the provider
ran and billed the generation: a deadline, cancellation, or network error after
the request was dispatched and before a complete body arrived. The first such
outcome latches the executor. Every later call fails immediately with
`completion_uncertain`, never dispatches, and records `latchedBy`, the attempt
number whose outcome set the latch, so an analysis can separate inherited
failures from a call's own failure. `settle()` rejects while the latch is set.

Once an HTTP status has been received and the body is being read, exceeding
`maxResponseBytes` (by declared `content-length` or mid-stream) is a definite
`response_limit` failure of that call alone: the generation finished, the body
was withheld, and later calls dispatch normally.

## Call budget

`maxCalls` defaults to twelve, the frozen smoke, and may be raised explicitly to
at most 400 (`GATEWAY_MAX_CALLS`) for replicated comparisons. The
[Gateway entry point](../examples/gateway-study.ts) bounds the executor to the
study's exact proposal slot count and refuses a study whose slots exceed the
operator limit `ALGAL_LAB_GATEWAY_MAX_CALLS` (an integer 1..400; default 12).
When that variable is set, `executor.json` also records `maxCallsLimit`; when it
is unset the archive shape is unchanged, so the frozen smoke inspector, which
rejects unknown fields and studies above twelve calls, keeps qualifying the
frozen smoke exactly as before. Runs above twelve calls need their own declared
acceptance plan and inspector.

The outer archive retains `intent.json`, `executor.json`, and `gateway.json`, with
the study under `study/`. It keeps failures and cancellation observations even
when the study cannot finish. Gateway response metadata supplements ordinary
ALGAL effect receipts: observed generation IDs, model names, finish reasons,
token counts, and reported cost when supplied. Missing usage remains unknown.
Credentials and raw upstream error bodies are never retained in these files.

The inspector reconstructs the study offline, checks the exact frozen first-smoke
protocol, model, provider, and settings, matches transport observations to effect
receipts, and applies the same peer-inheritance acceptance as the XCB smoke. It
requires the v2 executor configuration and checks that every observation carried
the exact-budget schema digest (`exactBudgetContract`).
Other models or protocols need their own declared acceptance plan. The metadata
is not independently authenticated, and
HTTP completion does not provide XCB's native process-custody evidence. A passing
smoke establishes operation and recorded artifact inheritance, not a sharing
advantage or scientific discovery.

## Text bounds: schema characters versus host bytes

The provider JSON schema bounds `hypothesis` and `rationale` with
`maxLength: 1000` and `message` with `maxLength: 500`, and JSON Schema counts
those limits in characters. The host parser is authoritative and counts
UTF-8 bytes (1,000 and 500 bytes respectively). A proposal with multi-byte text
can therefore pass the provider schema and still fail host admission; it is
then a recorded failed slot, not a transport error.
