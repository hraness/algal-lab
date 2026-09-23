# Second Gateway smoke findings, 2026-09-22

The second researcher smoke **passed its predeclared acceptance**: twelve
generations completed and all twelve proposals passed host validation. The
[contract v2 plan](proposal-contract-v2-plan.md) was committed as `28c62a1`
before inference; the implementation was merged as `0742398` under
`algal.lab.gateway-executor.v2` with the `algal.lab.proposal.v2` exact-budget
schema. The frozen protocol, instrument, VM manifest, and scripted baselines
did not change.

The first run's failure mode did not recur. Under the v1 generic schema, one
proposal emitted eleven edges instead of ten. Under v2, every dispatched
request carried the schema encoding exactly eight nodes and ten edges, and all
twelve proposals satisfied the budget. This demonstrates the contract's
mechanism in the passing direction; it does not prove the provider enforced the
schema rather than simply complying, since no violating output was attempted by
the model this time.

## Operational evidence

The run reused `openai/gpt-6-luna`, restricted to provider `openai`, for the
exact twelve-slot protocol. Every HTTP generation completed with a distinct
response ID, the selected model, the recorded configuration, and matching
receipt usage. Offline reproduction passed for all twelve attempts, twelve
measurements, and 28 artifacts. The smoke inspector returned `passed: true`,
including `everyProposalMeasured` and `exactBudgetContract`.

Four proposals cited earlier visible artifacts from another researcher and
changed the labeled graph: two in shared-artifacts and two in
shared-artifacts-and-messages. This again demonstrates recorded peer citation
with a changed graph, not causal use or improvement.

Gateway reported 8,989 input tokens and 9,904 output tokens, including 6,794
reasoning tokens, for a reported cost of **$0.0058509**. The temporary key's
metered spend matched at the displayed cent resolution. These are provider
accounting reports rather than an independently audited bill. The $1,
non-renewing, seven-day key (`algal-lab-v2-smoke`) was created for this test,
revoked afterward, and its absence was verified. No credits were purchased or
billing settings changed. The credential was supplied only through the operator
environment; no local secret files were written.

## Descriptive results

Each condition had four proposal slots. Champions were selected using discovery
scores before any holdout evaluation. All three conditions selected the same
labeled graph — `52603eba`, the same graph run one's Luna champion selected —
so the selected-champion sharing and message contrasts are again zero. Every
round-zero proposal in every condition was that same graph: temperature zero
converged both researchers and all conditions onto it, which incidentally
produced matched initial populations this run. That convergence is a model
behavior, not a harness guarantee; a replicated comparison must still inject
matched populations deliberately.

| Condition | Valid / slots | Distinct labeled graphs | Champion exact random AUC | Targeted AUC | Prediction MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolated | 4 / 4 | 3 | 0.794643 | 0.729167 | 0.107344 |
| Shared artifacts | 4 / 4 | 3 | 0.794643 | 0.729167 | 0.026927 |
| Shared artifacts and messages | 4 / 4 | 3 | 0.794643 | 0.729167 | 0.036771 |

The three-seed sampled random holdout score was 0.812500 for this champion,
while its exact expectation was 0.794643 — the same gap run one showed, and
the same reason the small sampled holdout is insufficient for a precise
performance claim.

For a descriptive comparison, the adaptive and random scripted policies were
re-run under the current source with this same seed, graph budget, discovery
schedules, and four-slot budget. Both completed all slots, and each condition
selected the same control graph as in run one. These supplementary controls do
not change the frozen acceptance.

| Researcher or fixed reference | Selected exact random AUC | Targeted AUC |
| --- | ---: | ---: |
| Luna, each information condition | 0.794643 | 0.729167 |
| Scripted adaptive, each condition | 0.744420 | 0.666667 |
| Random search, each condition | 0.744420 | 0.666667 |
| Predeclared ring/chord reference | 0.785714 | 0.666667 |

The AUC upper bound with no fragmentation over this horizon is 0.812500. The
Luna champion again exceeded these controls in this one small regime — the same
graph, in fact. One search replicate per run, fixed condition order, and
round-zero convergence still do not establish general superiority, a sharing
advantage, or a transferable discovery.

All four accepted peer-child changes were non-isomorphic to their cited peers
and all four underperformed their parents on exact random AUC: -0.032738,
-0.017113, -0.045759, and -0.037202. Unlike run one's mixed deltas, every
observed peer modification here made the design worse, consistent with the
parent already being the run's best found design. Across the run, six distinct
valid labeled graphs represented six topology classes.

## Implications for the next experiment

The exact-budget contract is now the admitted proposal transport. Keep ALGAL
as the execution and receipt layer and keep scientific semantics in Algal Lab.
Sharing again produced no champion gain; with temperature-zero round-zero
convergence, this harness configuration gives conditions nearly identical
starting material, so information-sharing has little room to act differently.

A sharing claim still requires the frozen replicated comparison described in
the v2 plan and roadmap: matched initial populations by construction rather
than by model convergence, counterbalanced condition order, failure-inclusive
scoring, random and fixed controls, and uncertainty on paired differences.
Tracking topology equivalence separately from labeled identity is now measured
mechanically for this run and should move into the analysis path for that plan.

## Evidence identities

Generated archives remain local under `runs/`. Reproduction uses the recorded
application source; it does not call a provider. Later commits change the
report contract and application identity, so check out the recorded revision
first:

```sh
git checkout 0742398 && bun install --frozen-lockfile
bun run lab verify runs/gateway-smoke-v2/study
bun scripts/inspect-gateway-smoke.ts runs/gateway-smoke-v2
bun run lab verify runs/gateway-v2-controls-adaptive
bun run lab verify runs/gateway-v2-controls-random
```

| Artifact | SHA-256 digest |
| --- | --- |
| Live study report | `2586e2939f32d42b647623631d3c740665e3bc7724c290a61b34c32aefb447b4` |
| Gateway inspector source | `e5164477399bb83e208ed50ee3501e4c5e9df0760c004c813b8cc0ebb03cbbe4` |
| Selected Luna graph | `52603ebad005e8150d0408ddc13cd46db2018d90a42cdebde9aed00ca8288ccc` |
| Matched adaptive study | `82242cc851e3454e562e65bda645cf0a69afc3d43a95801e92eefd1c023a107a` |
| Matched random study | `0643063d83dd53e5186783ae88f08243b53d34939370c668f0b2a66b67ce5a1e` |
