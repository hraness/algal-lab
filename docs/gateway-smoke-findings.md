# First Gateway smoke findings, 2026-09-22

The live Gateway route worked, but the first researcher smoke **failed its
predeclared acceptance**: twelve generations completed and eleven proposals
passed host validation. One proposal contained eleven edges instead of ten. All
attempts, including that failure, remain in the archive. No replacement model
calls or prompt changes were used to obtain a passing result.

The [transport plan](gateway-smoke-plan.md) was committed as `baaf5e2` before
inference. The implementation and instrument were frozen at `811ba84`, using
the existing pinned ALGAL dependency. Independent source review and the aggregate
check passed before inference: 82 tests, 3,429 assertions, and type checking.

## Operational evidence

The run used `openai/gpt-6-luna`, restricted to provider `openai`, for the exact
twelve-slot protocol. Every HTTP generation completed with a distinct response
ID, the selected model, the recorded configuration, and matching receipt usage.
Offline reproduction passed for all twelve attempts, eleven measurements, and
28 artifacts. The smoke inspector returned `passed: false`; its only failed
control was `everyProposalMeasured`.

Three valid proposals cited earlier visible artifacts from another researcher
and changed the labeled graph. This demonstrates recorded peer citation with a
changed graph. It does not establish causal use, improvement, or a new topology.

Gateway reported 8,948 input tokens and 9,496 output tokens, including 6,427
reasoning tokens, for a reported cost of **$0.0056428**. The temporary key's
metered spend matched that value. These are provider accounting reports rather
than an independently audited bill. The $1, non-renewing, seven-day key was
revoked after the test, its absence was checked, and its local secret files were
removed. No credits were purchased or billing settings changed.

## Descriptive results

Each condition had four proposal slots. Champions were selected using discovery
scores before any holdout evaluation. All three conditions selected the same
labeled graph, so the selected-champion sharing and message contrasts are zero.
That champion was already the very first isolated proposal, before any artifact
sharing. Each researcher's initial request digest was identical across
conditions, but outputs differed and the messages condition began with different
graphs. Zero temperature did not give this run matched initial populations.

| Condition | Valid / slots | Distinct labeled graphs | Champion exact random AUC | Targeted AUC | Prediction MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolated | 4 / 4 | 3 | 0.794643 | 0.729167 | 0.038125 |
| Shared artifacts | 3 / 4 | 2 | 0.794643 | 0.729167 | 0.030694 |
| Shared artifacts and messages | 4 / 4 | 4 | 0.794643 | 0.729167 | 0.050208 |

Prediction MAE describes admitted proposals only; the invalid proposal remains
in the slot denominator. The three-seed sampled random holdout score was
0.812500 for this champion, while its exact expectation was 0.794643. This
difference illustrates why the small sampled holdout is insufficient for a
precise performance claim. The exact endpoint covers the entire uniform failure
distribution, including discovery states; it is not an exclusively held-out test.

For a descriptive comparison, the existing adaptive and random policies were
run with this same seed, graph budget, discovery schedules, and four-slot budget.
Both completed all slots, and each condition selected the same control graph.
These supplementary descriptive controls do not change the frozen acceptance.
The earlier qualification's eight-slot, sixteen-seed averages are
background rather than matched controls for this smoke.

| Researcher or fixed reference | Selected exact random AUC | Targeted AUC |
| --- | ---: | ---: |
| Luna, each information condition | 0.794643 | 0.729167 |
| Scripted adaptive, each condition | 0.744420 | 0.666667 |
| Random search, each condition | 0.744420 | 0.666667 |
| Predeclared ring/chord reference | 0.785714 | 0.666667 |

The AUC upper bound with no fragmentation over this horizon is 0.812500.
The Luna champion exceeded these controls in
this one small regime. One search replicate, fixed condition order, and a failed
validity gate do not establish general superiority, a sharing advantage, or a
transferable discovery. Targeted removal also depends on node labels when
degrees tie.

All three accepted peer-child changes were non-isomorphic to their cited peers.
Their exact random-AUC changes were -0.033110, +0.005208, and +0.004092. The last
child also cited its own earlier design and underperformed that parent by
0.011533. These mixed outcomes are why a peer citation should not be counted as
an improvement. Across the run, seven distinct valid labeled graphs represented
six topology classes.

## Implications for the next experiment

Keep ALGAL as the execution and receipt layer and keep scientific semantics in
Algal Lab. Its existing Gateway executor was sufficient; the additions were
bounded transport evidence and a lab-specific acceptance check. The host graph
validator caught a model's budget violation without allowing the proposal to
change the instrument.

The next operational experiment should test an explicitly versioned proposal
contract that encodes the exact node and edge counts, or a bounded edit grammar
whose operations preserve those invariants. Retain the original failed run and
declare new acceptance before testing that contract. Model instructions and
general JSON shape alone did not enforce the experimental budget.

For a scientific sharing claim, first freeze a replicated comparison with
matched initial populations, counterbalanced condition order, failure-inclusive
scoring, random and fixed controls, and uncertainty on the paired differences.
Track topology equivalence separately from labeled graph identity. A discovery
claim additionally needs a precise rule with predictions on fresh graph
configurations and explicit counterexamples.

## Evidence identities

Generated archives remain local under `runs/`. Reproduction uses the recorded
application source; it does not call a provider.

```sh
bun run lab verify runs/gateway-smoke/study
bun scripts/inspect-gateway-smoke.ts runs/gateway-smoke
# The inspector intentionally exits 1 for this failed acceptance result.
bun run lab verify runs/gateway-controls-adaptive
bun run lab verify runs/gateway-controls-random
```

| Artifact | SHA-256 digest |
| --- | --- |
| Live study report | `f6cf347149b1ffe23fdeac1bcbd12f8338670954855be70e8dd0c00e92ed54ff` |
| Gateway inspector source | `d23ee931bcdb3054e4538ed997f6dab37d8ddb965f8678ed5b7dd52f795611a1` |
| Selected Luna graph | `52603ebad005e8150d0408ddc13cd46db2018d90a42cdebde9aed00ca8288ccc` |
| Matched adaptive study | `76b41af91e8334ae3db103f4404e6bdabf2ead6885e1f251dd49002a10b9c0a0` |
| Matched random study | `3d2bcc7126a49c32cf45fbeed87deddb183fe40562900406db951275aa901856` |
