# Proposal contract v2 plan, 2026-09-22

This plan is frozen before any further Gateway inference. It responds to the
[first smoke failure](gateway-smoke-findings.md): eleven of twelve Luna
proposals passed admission, but one emitted eleven edges instead of ten. The
provider-facing schema bounded edges generically (3–48 items, 4–16 nodes)
instead of encoding the protocol's exact budget. Model instructions and general
JSON shape alone did not enforce the experimental budget. The original failed
run remains retained under `runs/gateway-smoke/`; this plan does not re-judge it.

## Changes in scope

- A versioned proposal contract, `algal.lab.proposal.v2`. The provider-facing
  schema is built per request from the admitted research context and encodes the
  exact node count and edge count: `nodes` is bounded to the protocol value,
  `edges` has equal `minItems`/`maxItems`, and endpoints are bounded to
  `[0, nodes - 1]`. Host `parseProposal` stays authoritative for connectedness,
  loops, duplicates, parent visibility, and byte limits; the schema is an
  additional admission bound, never a new judge.
- Executor contract `algal.lab.gateway-executor.v2` (`adapterVersion` 2). Each
  transport observation records the dispatched schema's digest, and a provider
  response outside the exact budget contract is rejected as `invalid_response`
  before it can become a failed measurement. A run whose provider ignored the
  schema therefore fails transport conformance rather than silently passing.
- The smoke inspector recognizes v2 configurations and adds an
  `exactBudgetContract` control: every observation must carry the schema digest
  for the frozen protocol's exact node and edge counts.
- The study protocol, VM manifest, instrument, scripted baselines, and archived
  v1 runs do not change. The proposal payload shape is unchanged. Existing
  archives still verify, but only at their recorded source revision (`811ba84`
  for the first smoke), because the application identity binds the changed
  executor and inspector sources; they do not verify at later commits.

## Frozen smoke settings

The next live smoke reuses `examples/network-model-smoke.json` unchanged: seed
2903, two researchers, two rounds, three information conditions, twelve proposal
slots, eight nodes, ten edges, three failure steps. Settings remain the observed
`openai/gpt-6-luna` restricted to provider `openai`, temperature zero, low
reasoning effort, a sixty-second deadline, an 8 KiB proposal bound, and no
tools, client retries, alternate models, or response memoization.

Credential rules are unchanged: existing authorized access or a separately
authorized temporary credential, no purchased credits or billing changes, no
credentials in Git or archives. Inference does not run until such authorization
exists; the first smoke's temporary key was already revoked.

## Declared acceptance for the next live smoke

- `everyProposalMeasured`: all twelve proposals are measured. This is the
  contract's purpose; a strict-acceptance failure is a result, not a defect to
  be edited away.
- `exactBudgetContract`: every dispatched request carried the v2 schema digest
  for exactly eight nodes and ten edges.
- `transportReportsCompleted`, `receiptConfigurationMatches`,
  `receiptUsageMatches`, `distinctGenerationRequests`, `notCancelled`,
  `frozenPlanMatches`, and `boundedTwelveCallStudy`: unchanged.
- `changedDesignFromVisiblePeer`: unchanged; at least one valid changed design
  citing an earlier visible peer artifact.

A passing smoke establishes that the exact-budget contract operated and that
recorded inheritance occurred. It cannot establish a sharing advantage, causal
influence of a message, a transferable discovery, or an independently
authenticated provider bill. Do not change this plan in response to a
disappointing scientific outcome.

## Follow-ups outside this scope

A scientific sharing claim still needs its own frozen plan: replicated
comparison with matched initial populations, counterbalanced condition order,
failure-inclusive scoring, random and fixed controls, and uncertainty on paired
differences. Topology equivalence must be tracked separately from labeled graph
identity. These are design requirements for that plan, not changes made here.
