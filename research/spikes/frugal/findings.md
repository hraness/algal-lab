# Qwen3-14B conjecture-selection pilot, 2026-09-23

The six-call pilot completed with **2,454 input tokens and 350 output tokens**
(2,804 total), at **$0.00037848** reported Gateway cost. It found no improvement
from one round of exact counterexample feedback. Both model arms retained one
correct additive law; the zero-model enumeration control retained both.

This is a negative result for the proposed feedback benefit in this small
grammar. It does not establish a general limitation of small models or
counterexample-guided research. It also does not establish cheap autonomous
discovery: investigators had already derived the additive laws and their proof
before inference, and supplied the formula grammar. The model independently
selected hypotheses without seeing their directions or proof.

## Frozen design and attribution

The [protocol](protocol.json), [runner](experiment.py), and
[exact judge](../../survivor_order.py) were frozen in commit
`e7295faabcd636cc052b7726748d718baac80900` before any model call. The route was
`alibaba/qwen-3-14b`, restricted to `deepinfra`, with reasoning disabled,
temperature 0.7, 1,024 maximum output tokens, and no application retries or
model/provider fallbacks. The gateway may internally retry within the selected
provider. A public endpoint preflight checked model, provider, price, and limits.

There were two replicates, each with one initial call shared by both arms and
one final call per arm. Arm order was reversed in the second replicate. Both
arms saw the initial claims; only the feedback arm saw exact development
judgments and first counterexamples. All four final portfolios froze before
holdout evaluation. No replacement calls or changes were made after outcomes.

The admitted grammar has 24 claims: four fixed additive/product comparisons,
two directions, and three horizon scopes. The primary count collapses nested
horizon variants into a single expression/direction law, requires an all/interior
scope, and requires nonvacuous passes on both panels. Development contained 32
environments at 4–7 nodes and rates 1–6; holdout contained 60 environments at
5–9 nodes and rates 1–12, generated from a separate frozen seed. The judge used
exact rational subset DP, every eligible horizon, and every ordered quadruple.

The enumeration control tested all 24 claims on development and froze the six
passing scope variants before holdout. It has a larger candidate/evaluator
budget than a three-claim model portfolio; this is a practical exhaustive
alternative for the small grammar, not an equal-oracle-budget causal comparison.
Its inference-token cost is zero, but computation and investigator work are not.

## Outcomes

| Method | Replicate 1: correct broad laws | Replicate 2: correct broad laws |
|---|---:|---:|
| Qwen3-14B, no feedback | 1 | 1 |
| Qwen3-14B, development feedback | 1 | 1 |
| Exhaustive admitted-grammar control | 2 | Same deterministic control |

All six HTTP generations completed, used distinct response IDs, and produced
three admitted claims. Read-only generation lookups independently confirmed
the recorded model, DeepInfra provider, token counts, and cost for all six.
All reported reasoning and cached token counts were zero. These are provider
accounting reports, not an independently audited invoice.

Every final model portfolio retained
`q_ab+q_cd >= q_ac+q_bd` for all admitted horizons. This passed 1,568 development
and 15,612 holdout quadruple/horizon comparisons. The model chose the wrong
direction for the second additive inequality. After receiving a two-survivor
counterexample, both feedback calls restricted that wrong direction to
`k>=3`; a three-survivor counterexample still refuted it. The product claims
also failed. Those outputs and counterexamples remain in the archive.

The enumeration control retained both additive directions proved in the
[ordered-survival theorem](../../../docs/ordered-survival-discovery.md), in all
three scopes. Every retained variant passed holdout. No product orientation
survived this development panel. Finite passes alone are not proofs; the
separate mathematical derivation supplies the universal result.

The primary feedback contrast is zero in both replicates. Two replicates,
largely repeated outputs, and one feedback step do not support significance,
a learning curve, or generalization across model families. The investigator
chose the grammar, judged scientific usefulness, supplied the proofs, and
performed the literature review. None of that work is included in the small
model's 2,804 tokens or billed cost.

## Cost and implications

The full-context reservation for all six calls was $0.03096576, below the frozen
$0.05 ceiling. Actual reported and token-price-computed costs matched at
$0.00037848. Shared initial calls are counted once in actual totals and fully
in each standalone arm: each two-call no-feedback arm cost $0.00010584; each
two-call feedback arm cost $0.00013188.

Within a small typed grammar, exhaustive search plus an exact judge is the
stronger economical choice demonstrated here. A better role to test for models
is proposing useful new expressions or proof steps outside an easily exhausted
grammar. That is a proposed follow-up, not a capability established by this run.
There is no evidence here for evolved generators, autonomous novelty, or an
advantage over the current frontier research assistant.

## Reproduction and evidence

The full fresh replay reconstructed all requests, development feedback,
selection, freeze, exact judgments, costs, and results without another model
call. It matched. It does not reproduce model stochasticity or authenticate
external timestamps, authorship, or literature priority.

```sh
python3 -m unittest research.test_survivor_order research.test_frugal_experiment
# A new live run requires an operator-provided AI_GATEWAY_API_KEY and fresh path:
python3 -m research.spikes.frugal.experiment run --out research/spikes/frugal/runs/new
python3 -m research.spikes.frugal.experiment replay --out research/spikes/frugal/runs/new
```

Generated archives stay ignored. Public source and protocol suffice for fresh
inference; exact responses from this particular run are retained locally.

| Artifact | SHA-256 |
|---|---|
| Manifest | `fc3ec7c58e1dc47faf2d4f4b7c0f415b52bd9e0fbb6eec0d8b9f561fb9fc2f42` |
| Frozen portfolios | `924c19070727e8c4c3ebfec5b7d84792b3bc6741c0b9b3b488b64615b948aa8f` |
| Results | `c78619dd8390ad2ccb206b4f616cee7cc1c59201cb0d0c83a38b5d926709d2ff` |
| Fresh reproduction | `2a8f160926f7142a2d9d2473f70bae071d5895ff27c234420e8402d89e9270b2` |
| Runner | `934d12c8bdfb1295a7ee94a53c74c40964d05be3e7b8a383dbe02b3efcd6e224` |
| Protocol | `4df2a0434dbde767970c5cfc55ee7a44e87dd461b66ba5b6bcff383c7cf560d3` |
| Judge | `9316bbefeffee0b55479c73740091f13a5fee2f30aa22ff09d116ed9d03edef1` |
