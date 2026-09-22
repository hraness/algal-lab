# Live application inference

This page covers XCB. [Vercel AI Gateway](gateway-executor.md) is a separate
optional route using ALGAL's existing HTTP executor and the same scientific
smoke acceptance.

The default demo and qualification commands never contact a model. The optional
[XCB entry point](../examples/xcb-study.ts) uses an already qualified local XCB
installation for bounded, ephemeral application inference. It does not use a
coding-agent session or give researchers tools or repository access.

Inspect your installed XCB documentation and `xcb --json generate --capabilities`.
Select an exact available account/model key from that response. A connected
account alone is insufficient: qualification must bind the current executable,
account generation, model observation, provider boundary evidence, and expiry.
Creating that evidence belongs to XCB's supported qualification workflow. This
application neither fabricates it nor changes global configuration or credentials.

Set `XCB_EXECUTABLE` to the absolute installed executable path, `XCB_ACCOUNT`
to the selected account ID, and `XCB_MODEL` to its exact observed key. Keep those
settings local. Then use a fresh run directory:

```sh
bun examples/xcb-study.ts --protocol examples/network-model-smoke.json --out runs/model-smoke
bun run lab verify runs/model-smoke/study
bun scripts/inspect-model-smoke.ts runs/model-smoke
```

The public smoke protocol permits twelve model calls: one replicate, two
researchers, two rounds, and three sharing conditions. The example refuses larger
studies. Inference allows 45 seconds and 8 KiB of output per call by default.
Each call must pass the capability/qualification preflight again. The adapter
uses a direct executable invocation, with no shell, retries, alternate account,
or fallback to another provider or scripted search.

The request contains the common research prompt and bounded context. The host
omits the assignment label and all evaluation results. A valid result must come
from the chosen account/model, report a completed terminal state, and prove
joined execution with no tool effects. Runtime drift, expiry, invalid output,
or an uncertain provider state fail closed. Cancellation signals only the owned
process and awaits its cleanup. If custody is unproven, the executor refuses
further inference and settlement fails; a timeout alone is never proof of cleanup.

ALGAL effect receipts retain the executor identity, model key, and configuration
digest. The example exclusively claims an outer run directory, writes intent and
readable executor configuration before inference, and keeps the study under
`study/`. It retains `xcb.json` transport observations even after a partial run.
CLI signals cancel the owned inference and await settlement before persisting
that evidence. The transport files contain no raw prompt or
provider diagnostics; graph proposals remain in the ordinary research archive.
The sidecar is supplemental, and the offline study verifier does not authenticate
or reproduce its wall-clock and transport claims. The inspected XCB generation
contract exposes no token counts, so usage is explicitly unavailable, never
reported as zero. Equal call budgets are not equal inference cost.

The smoke inspector verifies the child study offline, checks receipt/sidecar
consistency, and requires a measured changed graph citing an earlier visible
artifact from a different researcher. It exits unsuccessfully if that operational
acceptance is missing. A parent citation without a changed design does not pass.
Its transport consistency checks do not independently authenticate provider
claims, and its own analysis source digest is retained in the printed result.

Read [the qualification plan](qualification-plan.md) before interpreting a live
run. A twelve-call smoke can establish valid execution and inheritance of a
visible peer artifact. It cannot establish that sharing improves search, that
messages help, or that a general scientific rule has been discovered. Missing
provider qualification leaves this acceptance item pending even when synthetic
adapter tests pass.
