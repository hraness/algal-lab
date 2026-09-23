# Frozen replicated comparison: first live run under network.v2

`examples/comparison-plan-v2.json` is the frozen input for the first
replicated comparison under the heterogeneous-failure instrument. It
supersedes [`comparison-plan.json`](../examples/comparison-plan.json) for the
live arm: the v1 plan's scripted control ran and confirmed the saturated
objective the independent review predicted. The design here — sharing
contrasts, priming, counterbalancing, paired inference, margins — is carried
over unchanged from [comparison-plan.md](comparison-plan.md); only the
instrument, budgets, and replicate seeds differ. This file is the
preregistration: changing it after the live run would be tuning, so do not
tune this plan until sharing wins; later experiments require a new plan and
new search seeds.

## Why the instrument changed

The v1 instrument (uniform random failure, node-count service) is saturated:
an independent review found the ring/chord reference at the exact optimum at
8/12/3 and a frontier model's one-shot proposal already at optimum at
8/10/3. No sharing or search effect can appear inside a zero residual.

The headroom spike replaced the objective with heterogeneous failure: each
node has an integer failure weight and value, random failure removes
survivors with probability proportional to weight, and service is the most
valuable surviving component's share of total value. Exact evaluation uses a
subset dynamic program over removal-set probabilities, independently checked
against exhaustive weighted-order enumeration and Monte Carlo (see
`bun run qualify:instrument` and [headroom-v2.md](headroom-v2.md)).

At the registered v1 budgets the heterogeneous objective still saturates
(0.0016–0.017 mean reference regret), so the spike searched regimes. The
frozen budgets below are the ones that cleared the preregistered 0.03
headroom bar with margin:

| Regime | Mean ref regret | Best relabeled ref | Best label-aware heuristic | Best of 2,000 random | Scripted champion |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8n/8e/3s (primary) | 0.0463 | 0.0321 | 0.0074 | 0.0025 | 0.0548 |
| 10n/11e/4s (transfer) | 0.0535 | 0.0167 | 0.0107 | 0.0076 | 0.0633 |

Label-blind designs provably cannot compete (even the best relabeling of the
reference misses the optimum by >0.03 at the primary budget), while
label-aware heuristics and random search show the headroom is reachable —
exactly the gap a live arm is measured against.

## Fixed inputs

- Instrument: `network.v2` (weighted random removal, value-fraction service).
- Replicate seeds: `[6007, 6011, 6029, 6037, 6043, 6067, 6073, 6079]` — the
  first eight primes greater than 6000. A new experiment gets new seeds;
  these are fresh rather than the v1 set's >5000 primes.
- Environments: per replicate, derived deterministically as
  `environmentFor(nodes, replicateSeed)` — weights and values i.i.d. uniform
  on 1..5, redrawn with seed+1 until both spreads are ≥3, and seeded by the
  replicate seed mixed with the node count so different budgets draw
  independent environments. Each replicate is an independent problem;
  conditions within a replicate share one world. Researchers see the
  environment; it is the skill being measured.
- Researchers 2, rounds 4, host-primed designs 1 per researcher, identical
  across conditions and arms by construction.
- Primary budget: 8 nodes / 8 edges / 3 failure steps.
- Transfer regime: 10 nodes / 11 edges / 4 failure steps.
- Discovery seeds `[41, 83, 167, 331]`; holdout seeds
  `[1009, 2017, 4027, 8053, 16111, 32213, 64433, 128879]`. Disjoint by
  construction and collision-free under the v2/v3 effective-seed rule.
- Practical margin: 0.01 mean champion exact weighted-AUC.

## Arms and endpoint

Same as the v1 plan: scripted `adaptive` and `random` controls, plus the
`live` arm through the pinned ALGAL Gateway executor
(`examples/gateway-compare.ts`). The endpoint is the discovery-selected
champion's exact expected weighted-failure AUC under its replicate's
environment — label-dependent by construction, oracle-computed, evaluated
before any holdout measurement. A condition without a valid champion scores
zero.

## Model-call budget

`liveCallBudget` = 8 replicates × 3 conditions × 2 researchers × (4 rounds +
1 transfer) = 240 calls. The entry point refuses to dispatch above the plan's
slot count.

## Script

```sh
bun run compare:v2                                        # scripted control arms
bun run lab verify-comparison runs/comparison-v2          # reconstruction

ALGAL_LAB_GATEWAY_MAX_CALLS=240 GATEWAY_MODEL=<catalog-model> GATEWAY_PROVIDER=<provider> \
  bun examples/gateway-compare.ts --plan examples/comparison-plan-v2.json --out runs/live-comparison-v2
bun run lab verify-comparison runs/live-comparison-v2/comparison
```

## First live result

The first live run under this plan completed 2026-09-23
(`openai/gpt-6-luna` through Vercel AI Gateway, 240 calls): the live arm
landed mid-pack at the primary budget, sharing showed a small within-margin
positive trend at primary, and peer evidence measurably degraded held-out
transfer. Recorded in [live-comparison-v2-findings.md](live-comparison-v2-findings.md).

## Limits

Everything in the v1 plan's limits applies: the scripted arms remain
controls, not evidence of intelligence; source digests are provenance, not
empirical validity; the instrument is a discrete model, not a physical claim.
Under network.v2 the endpoint is label-dependent, so "matches reference
topology" is reported for context only — topology classes do not carry
environment labels.
