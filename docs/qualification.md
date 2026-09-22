# Initial qualification findings

The initial results support keeping ALGAL as the execution and receipt layer,
with the experimental method and instruments in Algal Lab. They do not establish
that sharing improves search. The [plan](qualification-plan.md) was committed
before observing the qualification outcomes, and null/negative results were
retained without tuning the search policy.

## Numerical agreement

The independent instrument probe enumerated 27,470 connected labeled graphs
with four through six nodes and checked 246,426 failure trajectories. Component
service agreed exactly with a union-find reference; the maximum AUC difference
was 1.11e-16. The probe also checked 40,000 generated/mutated design pairs for
connectivity, fixed edge budgets, and bounded one-edge mutation.

The separate exact random-failure oracle was checked against analytical graphs
and explicit removal permutations over all connected four- and five-node
graphs. It computes the full uniform failure distribution, not an exclusively
held-out sample or a physical infrastructure model.

Two measured limitations matter. On a six-cycle, the targeted score after three
removals is either 23/36 or 22/36 depending only on node labels, because the
instrument breaks degree ties by lowest ID. The graph generator also favors
some structures: for five-node trees its construction gives stars an 8.33%
share, compared with 4% under uniform labeled-tree sampling. These are documented
properties of the instrument and generator; they are not new topology discoveries.

## Matched search comparison

Twelve studies completed 2,304 valid proposals across three regimes and sixteen
search seeds per regime. Each condition received eight proposal slots. Its
champion was selected using discovery scores before evaluation. The primary
endpoint was that champion's exact expected random-failure AUC.

| Regime: nodes / edges / steps | Isolated adaptive | Shared adaptive | Random search | Fixed ring/chord reference |
| --- | ---: | ---: | ---: | ---: |
| 8 / 10 / 3 | 0.762347 | 0.761905 | 0.765578 | 0.785714 |
| 8 / 12 / 3 | 0.793713 | 0.792062 | 0.794201 | 0.809524 |
| 10 / 14 / 4 | 0.760166 | 0.759932 | 0.759498 | 0.782877 |

Search columns are means over the sixteen selected champions. The fixed
reference is one predeclared design at each budget, not a selected winner.
Shared-minus-isolated mean differences were -0.000442, -0.001651, and -0.000234
AUC points respectively. These are descriptive paired results, not confidence
intervals or evidence of statistically significant harm. They do not show a
reliable benefit from this scripted sharing policy. The fixed reference exceeds
the average selected candidate in every regime, so it is an important baseline
for any later model-driven search claim.

All proposals were measured. Random search produced identical graph sequences
across information conditions. The message-blind adaptive policy's two shared
conditions also matched exactly. Those controls support the comparison's
implementation; they say nothing about a model's ability to use messages.

Reproduce the evidence with:

```sh
bun run qualify:instrument
bun run qualify
bun run lab verify-qualification runs/qualification
```

The generated archive retains every substudy, complete receipt, frozen champion,
source identity, paired difference, and reference graph. Use a new output path
for another run. Generated archives remain local rather than being committed.

## Live model status

The user-selected next route is Devin SWE-2 through XCB, with Codex Luna as a
fallback. The adapter's synthetic tests cover provider admission, source drift,
budgets, metadata, offline replay, cancellation, and evidence retention. They
are not live-model evidence.

The first local preflight found the Devin route but no valid application
qualification for the installed XCB bytes. Independent native boundary tests
passed for an isolated helper, while a concurrent XCB deployment produced
different source/build/installed identities. That evidence cannot qualify a
different executable. Provider pins and account state were preserved. The XCB
owner subsequently deployed and qualified the matching runtime. The latest
preflight admits Devin SWE-2 but reports the account busy in another session;
the smoke remains pending until that session releases it. See
[the live executor procedure](live-executor.md).

## Architectural implications

Keep the present runtime/lab boundary. Exact evaluation, honest controls, and
discovery-only selection were the useful additions; another orchestration layer
would not have answered these questions. Preserve competing artifacts, but
measure whether researchers actually inherit and improve them. A growing archive
alone is not evidence of learning.

For the next scientific claim, qualify an actual researcher against random
search and the fixed reference. Then test typed hypotheses with counterexamples
and fresh graph configurations. A transferable rule requires predictions beyond
the designs used to invent it. Instrument evolution and federation remain later
experiments with their own admission and evaluation contracts.
