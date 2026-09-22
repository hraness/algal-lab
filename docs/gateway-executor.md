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

The example limits a study to twelve proposal slots. Each request uses the fixed
Gateway origin, a selected model and provider, zero temperature, low reasoning
effort, a sixty-second deadline, an 8 KiB proposal limit, and no tools. The lab
wrapper supplies a full provider JSON schema while preserving the original VM
manifest and host graph admission. ALGAL's Gateway adapter wraps the proposal in
`value` on the wire and extracts it before measurement.

The configuration digest covers schema, provider selection, and request limits.
Every request remains stateless and receives only its bounded research context.
The wrapper performs no client retries or alternate-model fallback. A timeout
cannot establish that remote inference stopped, so uncertain transport completion
blocks later requests from that executor.

The outer archive retains `intent.json`, `executor.json`, and `gateway.json`, with
the study under `study/`. It keeps failures and cancellation observations even
when the study cannot finish. Gateway response metadata supplements ordinary
ALGAL effect receipts: observed generation IDs, model names, finish reasons,
token counts, and reported cost when supplied. Missing usage remains unknown.
Credentials and raw upstream error bodies are never retained in these files.

The inspector reconstructs the study offline, checks the exact frozen first-smoke
protocol, model, provider, and settings, matches transport observations to effect
receipts, and applies the same peer-inheritance acceptance as the XCB smoke.
Other models or protocols need their own declared acceptance plan. The metadata
is not independently authenticated, and
HTTP completion does not provide XCB's native process-custody evidence. A passing
smoke establishes operation and recorded artifact inheritance, not a sharing
advantage or scientific discovery.
