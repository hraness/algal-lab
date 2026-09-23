# Research method

The first study asks whether researchers benefit from observing one another's
artifacts, and whether adding messages changes the resulting portfolio. It uses
a small deterministic graph instrument so the experiment and its evidence can
be inspected without credentials, a physics solver, or a hosted service.

This is a toy model of connectivity under node removal. Nodes have no traffic,
capacity, geometry, material properties, or failure probabilities inferred from
the real world. Results do not establish the resilience of infrastructure,
communications systems, or materials.

## Instrument and metrics

An admitted graph is initially connected, undirected, and simple: no self-loops
or duplicate edges, including a repeated edge with reversed endpoints.
It has 4–24 nodes and at most 96 edges, subject to the number of possible unique
edges. Study proposals must meet the protocol's exact node and edge budgets.
The study protocol is narrower than the instrument: 4–16 nodes, at most 48 edges,
and at least `nodes - 1` edges. Admission also checks connectivity; satisfying
those counts alone is insufficient.
The retained realized edge list is the object evaluated, even when a proposal
began as a named generator or mutation of a prior graph.

The [instrument](../src/network.ts) is `network.v1`; its result contract is
`algal.lab.network-result.v1`. It removes nodes under two failure rules. Random
failure uses deterministic Mulberry32 draws to select an index in the current
live-node list. Targeted failure recomputes live degree after every removal,
selects a maximum-degree node, and breaks ties by the lowest node ID. A targeted
trajectory therefore does not vary with seed. Repeated targeted schedules are
not independent observations.

It records the removal sequence and surviving connectivity
after each step, including the initial graph. Let `n` be the original node count
and `L_k` the largest surviving connected component after `k` removals. The
retained-connectivity measurement is `y_k = L_k / n`; the denominator does not
shrink as nodes disappear.

For `s` failure steps, normalized trajectory AUC is the trapezoidal sum
`sum((y_(k-1) + y_k) / 2, k=1..s) / s`. It summarizes retention across the requested
failure horizon. It complements the final connectivity measurement: two graphs can end
at the same value after losing function at different points. Always inspect the
trajectory, failure rule, seed, and horizon alongside the aggregate. The
instrument's exact tie-breaking and AUC implementation are part of its versioned
contract, not a choice made by the researcher.

The seeded connected-graph baseline starts from a random recursive spanning tree
on a shuffled vertex order, then adds edges. It is not a uniform sample of all
connected graphs with the specified counts. Generator bias limits which design
families the baseline explores.
The mutation helper attempts at most 128 one-edge replacements while preserving
connectivity and exact node/edge counts. If it finds none, it returns the original
graph. An attempted mutation is not evidence of novelty. Realized graph
normalization only sorts edge endpoints and the edge list; it does not repair an
invalid design into an admissible one.

## Matched study conditions

Every replicate runs the same three conditions:

| Condition | Evidence available at the start of a round |
| --- | --- |
| `isolated` | Up to the last 24 successful experiments by that researcher: graphs, mean discovery AUC scores, and references. |
| `shared-artifacts` | Up to the last 24 successful experiments across researchers: graphs, scores, and references, without their prose. |
| `shared-artifacts-and-messages` | The same artifact window plus up to the last 12 successful experiments' proposal messages. |

Researchers are logical participants in one local study. A round uses a fixed
snapshot, so execution order cannot give later participants access to new work
from that round. Window order follows completed-round and researcher order;
context is bounded recent history, not a search over the complete archive. All
conditions receive the same number of researchers, rounds, and proposal
opportunities. Every admitted proposal gets the same discovery schedule count,
with paired failure schedules. Context length differs when information is shared, so this is not a
claim of equal token usage, inference cost, or wall-clock time.

The scripted baseline uses visible graphs and scores but ignores message text.
Its two shared conditions therefore produce the same numerical results under
the same protocol; their contexts and evidence IDs still differ. This baseline
cannot measure a benefit from communication or establish an LLM's ability to
learn from it. Use an explicitly configured model executor for that question,
with recorded provider settings and additional independent replicates.

The public [protocol](../examples/network-study.json) uses the
`algal.lab.study.v1` contract. Its defaults are two replicate seeds (`7`, `23`),
three researchers, three rounds, eight nodes, ten edges, and three failure steps.
Discovery schedule seeds are `11` and `29`; holdout schedule seeds are `101`,
`203`, and `307`. Each schedule is applied to both failure rules. The effective
schedule seed combines its replicate seed with its schedule seed by XOR.
The mean gives equal total weight to random and targeted failure. Multiple
targeted seed entries retain this weighting but add no distinct trajectories
for a fixed graph.

The [protocol parser](../src/contracts.ts) bounds a study to eight replicate
seeds, two to eight researchers, one to twelve rounds, and at most 288 proposal
slots across all conditions. Discovery has at most four schedule seeds and
holdout at most eight; those seed lists must be disjoint. The failure horizon is
one through `nodes - 2` removals. These bounds constrain the initial application;
they are not measured capacity or statistical adequacy claims.

These produce 54 proposal opportunities across the full default study.
Proposals may repeat a design or fail admission; count them separately from
unique graphs and successful evaluations. Equal opportunity does not imply
equal portfolio size or equal successful work.

Within a replicate, researchers and conditions share the relevant environmental
seed structure. They are correlated observations, not independent experimental
replicates. The independent study seed is the unit for a future across-run
comparison. Two seeds and a tiny scripted demo do not justify significance,
generalization, or superiority claims. A live model can also vary despite the
same simulation seeds; preserve the executor receipt and report the model
configuration separately.

## Prediction, selection, and holdout

A researcher provides a bounded design, falsifiable hypothesis, quantitative
prediction, rationale, and parent experiment references before receiving that
design's new discovery measurements. Preserve contradictions and failed attempts;
do not retrospectively rewrite the prediction to match the result. A rationale
is the researcher's claim, not an independently verified mechanism.
The prediction is a mean discovery AUC in `[0,1]`. Hypothesis and rationale text
are each at most 1,000 UTF-8 bytes, the message is at most 500
bytes, and at most eight distinct parents must refer to visible prior evidence.
Every proposal includes its message field; only the message-enabled condition
exposes peers' message text in later context.

After discovery, each replicate/condition freezes all its valid unique designs as a
portfolio. The initial archive retains competing candidates instead of reducing
the study to one winner. Random and targeted failure can favor different graph
structures. This retention policy is not yet a quality-diversity search engine
or a proven Pareto-front algorithm.
Uniqueness means the exact normalized, labeled edge list. It does not collapse
isomorphic graphs or establish distinct mechanisms. Node labeling can also
affect targeted failure when degrees tie, so future robustness studies should
include relabeling or an independently specified tie policy.
For the isolated condition, candidates from all its researchers are pooled only
after their discovery work. The first successful attempt for each exact graph
represents that graph in the portfolio; every other attempt remains in evidence.

Discovery and evaluation are separate phases of the entire study: all
replicate/condition portfolios freeze before the first holdout measurement, and
no later model calls occur. Held-out outcomes are excluded from researcher
context and portfolio selection. Final evaluation combines unseen random
schedules with the repeated targeted control: targeted failure is seed-independent
and has already been measured during discovery. The final aggregate therefore
is not entirely out-of-sample. The same schedules within a replicate evaluate
every frozen portfolio; a favorable holdout result cannot admit a new
candidate or cause further search in that study. The protocol file is public:
this separation is a workflow boundary, not secrecy from the machine's operator.
Reusing those results to tune a later protocol turns them into development data;
choose a new holdout for that later study.

Before evaluation, each portfolio also selects one champion by highest discovery
score, breaking ties by canonical graph digest. This selection does not see
evaluation outcomes. The report separates the champion's sampled random AUC
from its deterministic targeted AUC; portfolio-wide aggregates remain
descriptive. Model requests omit condition labels while preserving the
treatment's information.

The discovery score is the mean AUC over the discovery schedules with equal
weight on random and targeted failure (50% each). Both champion selection and
the adaptive scripted policy's parent ranking use this discovery mean. The
primary qualification and comparison endpoint is different: the champion's
exact expected random-failure AUC only. Adaptive search therefore optimizes an
objective that differs from the one it is judged on, and a champion that wins
on the mixed score need not maximize the exact random endpoint. This mismatch
was pre-declared in the [qualification plan](qualification-plan.md) and has not
been changed since; changing the selection score or the endpoint would be a new
instrument or plan version, never a retrospective adjustment.

## Reading the report

The report presents descriptive statistics for each replicate/condition:

| Field | Definition |
| --- | --- |
| Valid experiments | Completed attempts, including repeated graphs. |
| Designs | Distinct normalized labeled graphs in the frozen portfolio. |
| Champion random AUC | Mean on the sampled unseen random schedules for the discovery-selected champion. |
| Champion targeted AUC | The champion's repeated, seed-independent targeted control. |
| Prediction MAE | Mean absolute difference between each successful proposal's prediction and its mean discovery AUC. Host-primed designs are excluded. |
| Portfolio mean AUC | Mean of the designs' final-evaluation mean AUC values, where each design's mean mixes the unseen random schedules and the repeated targeted control; each unique design receives equal weight. |
| Post-hoc best AUC | Largest final-evaluation mean AUC among frozen designs, reported after evaluation. It does not select or deploy a policy. |
| Coverage ≥ 0.75 | Fraction of final-evaluation schedule entries for which at least one frozen design has AUC at least 0.75. |

Portfolio mean AUC and post-hoc best AUC both mix random and targeted
trajectories, while champion random AUC uses the random schedules alone.
Post-hoc best AUC can therefore be lower than champion random AUC in the same
row; that is a difference in what is averaged, not an error.

Coverage describes alternatives in a portfolio, not interacting graphs or a
system that can choose the right design before a failure. Repeated targeted
entries count as schedule entries but remain the same observation. In the demo
this column is uninformative: it is 0.5 in every row because the three random
holdout schedules always reach the threshold and the three repeated targeted
entries never do, so it separates failure rules rather than portfolios. It is
not an acceptance criterion anywhere in the lab. An empty portfolio has zero
coverage and no mean/best AUC; prediction MAE is absent when there are no
successful attempts. The threshold is a fixed descriptive choice, not a
validated real-world service target.

Offline verification reproduces execution evidence and the instrument's
measurements. It neither repeats the model's stochastic thought process nor
validates this graph model against a real system. Broader claims need a declared
analysis plan, more independent replicates, suitable baselines, and external
domain validation. See the staged [roadmap](roadmap.md).

## Independent qualification

The [frozen qualification plan](qualification-plan.md) evaluates a different,
explicit endpoint: exact expected random-failure AUC of the discovery-selected
champion. At each removal count it enumerates every remaining-node subset and
averages service, then integrates those expectations. This removes finite
schedule sampling noise, but includes all states in the failure distribution,
including discovery states. It is not an exclusively held-out sample.

The oracle is bounded to ten nodes and independently implements admission and
disjoint-set connectivity. Analytical examples and complete removal-permutation
comparisons validate it. The standalone instrument probe checks all connected
labeled graphs with four, five, and six nodes against an independent reference,
and documents graph-generator bias and node-label sensitivity.

The qualification compares adaptive search and random search under matched
proposal seeds/budgets, reporting paired differences at whole-replicate level.
It evaluates a fixed ring/chord topology as an a-priori reference. Targeted scores
remain a separate control. All raw differences and failed selections remain in
the report; an empty selection receives zero comparison utility and is still
shown as absent, rather than being dropped. Observed minima/maxima are not
confidence intervals. No p-value or superiority claim is produced.

Each substudy freezes before its sampled holdouts. Exact population analysis
begins only after all substudies complete, with no feedback into generation.
The scripted message treatment and random-search treatments are null controls:
their numerical graph sequences must remain identical where the policy ignores
the changed information. Passing those controls qualifies the measurement path,
not an advantage for sharing or intelligence of the scripted researchers.
