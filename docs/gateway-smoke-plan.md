# Gateway smoke plan, 2026-09-22

This addendum is frozen before any Gateway inference. It changes the optional
transport to ALGAL's existing Vercel AI Gateway executor. The
[scientific smoke acceptance](qualification-plan.md#live-model-smoke), graph
instrument, and `examples/network-model-smoke.json` remain unchanged: seed 2903,
two researchers, two rounds, three information conditions, twelve proposal slots.
The earlier XCB attempt issued zero generation requests and remains archived.

Use the observed model `openai/gpt-6-luna` and restrict the inference provider to
`openai`. The Gateway catalog and provider endpoint were checked on 2026-09-22;
they advertise structured output, temperature, output-token limits, and low
reasoning effort. Fix temperature at zero, reasoning effort at low, a sixty-second
request deadline, an 8 KiB proposal bound, and a 2,048-token completion allowance.
No tools, client retries, alternate models, or response memoization are permitted.
These are call and output bounds, not a promise of equal token usage across
conditions or independent authentication of upstream service behavior.

Reuse the pinned ALGAL executor. A lab-owned wrapper refines the provider-facing
JSON schema without changing the VM manifest or host proposal admission. Bind
that schema, routing, and settings in configuration identity. Retain each original
effect-request digest, observed generation ID/model/finish reason, token usage,
reported cost when available, and failure status. Unknown usage or cost stays
unknown. A transport timeout may leave remote completion uncertain; block further
dispatch in that executor and preserve the partial evidence.

Use existing authorized Gateway access or a separately authorized temporary
credential. Do not purchase credits or change billing settings as part of this
smoke. Keep credentials and raw run archives outside Git. Before inference,
require focused fake-transport tests and independent source review. Afterward,
reproduce the study offline and run the Gateway smoke inspector.

Acceptance still requires twelve valid measured proposals and at least one
changed design citing an earlier visible peer artifact. Retain all failures.
The result can establish this research loop's operational behavior. It cannot
establish a benefit from sharing, causal influence of a message, a comparison
with Devin, or a transferable scientific discovery. Do not change this plan in
response to a disappointing scientific outcome.
