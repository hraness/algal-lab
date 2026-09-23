# Comparison plan, 2026-09-23

This plan is frozen before the first live-arm run. Its purpose is to decide
whether information sharing changes measured outcomes in Algal Lab's replicated
comparison, and whether a live model arm differs from the scripted controls
under an identical protocol. A positive effect of sharing is not a pass
condition. Do not tune this plan until sharing wins. Later experiments require
a new plan and fresh seeds.

The machine-readable plan is [examples/comparison-plan.json](../examples/comparison-plan.json)
(`algal.lab.comparison-plan.v1`). The scripted control run under the same plan
is a control measurement, not the subject of this registration.

## Design

Three arms run the same protocol v2 study:

- **adaptive**: the deterministic scripted policy; a control for the host
  machinery, not evidence of intelligence.
- **random**: independently sampled connected graphs in the same slots; a
  control for the value of search over priming and reuse.
- **live**: one model configuration through the pinned ALGAL Gateway executor
  (`examples/gateway-compare.ts`, the same `algal.lab.gateway-executor.v2`
  contract that passed the second smoke). `GATEWAY_MODEL`/`GATEWAY_PROVIDER`
  are selected from the current catalog at run time and recorded in
  `intent.json` next to the transport observations and reported usage; the
  exact selection for the first run is fixed before its first call. An
  operator-owned `--executor-command` wrapper remains the generic seam for
  other providers; a different executor, model, or settings requires a new
  registration. Credentials live in the operator environment, never in the
  plan, artifacts, or Git. The model gets no tools and no repository access,
  and condition names are omitted from model-visible context.

Each replicate primes every researcher with 1 host-seeded design, identical
across conditions and arms by construction. Condition order is counterbalanced
across replicates. Primary budget is 8 nodes / 10 edges / 3 failure steps; the
held-out transfer budget is 10 nodes / 14 edges / 4 steps, proposed once per
researcher after discovery from the same visible evidence.

## Seeds

Replicate seeds are the first eight primes greater than 5000, in ascending
order: 5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059. The plan parser rejects
any repeated effective seed (`seed XOR replicate seed`) across the discovery
and holdout phases of all replicates; this rule satisfies that contract while
keeping seeds arbitrary relative to the instrument.

Discovery schedules (41, 83, 167, 331) and holdout schedules (1009, 2017,
4027, 8053, 16111, 32213, 64433, 128879) are retained from the qualification
plan for continuity. The exact oracle is the primary measurement; schedules
only bound the discovery-time evidence researchers see.

## Endpoint

The endpoint is the discovery-selected champion's exact expected
random-failure AUC over the full uniform removal distribution, computed by the
oracle and invariant to node relabeling. Champions freeze before any holdout
measurement; a condition without a valid champion scores zero
(failure-inclusive). The fixed ring/chord reference and the ceiling are
predeclared and never selected from results.

## Contrasts and verdicts

Within each arm, paired by replicate seed: shared-artifacts minus isolated,
messages minus shared-artifacts, and messages minus isolated, at the primary
budget and each transfer budget. Across arms, paired by seed within each
condition: live-minus-random, live-minus-adaptive, and adaptive-minus-random.

Each contrast reports every paired difference, mean, a 95% percentile
bootstrap interval, exact two-sided sign-flip and Wilcoxon signed-rank
p-values, and wins/ties/losses against the preregistered practical margin of
0.01 AUC points. Verdicts follow [statistics.ts](../src/statistics.ts):
exceeds-margin requires the whole interval above 0.01; below-margin below
-0.01; within-margin entirely inside ±0.01; anything else is inconclusive.

## Live call budget

The live arm needs exactly 240 model calls: 8 replicate seeds × 3 conditions ×
10 proposal slots (2 researchers × (4 rounds + 1 transfer regime)). Priming
consumes no calls. The executor's configured limit must admit this exact
count; every call, valid or not, is retained in the archive with its receipt.
Invalid proposals consume slots.

## Controls and acceptance

A run is admitted only if every recorded control holds: all slots retained,
primed designs identical across conditions and across arms, the random arm
ignores sharing, the scripted arm ignores messages, condition order is
counterbalanced, transfer budgets are honored, and champions are selected
before holdout evaluation. A failed control invalidates the comparison rather
than adjusting it. Offline verification replays the archive and must
reproduce the published report byte-for-byte.

## Claims

A completed run supports these statements only: the measured contrasts under
this protocol, at these budgets, with these seeds. A live arm's result
describes one model configuration; it does not establish causal use of
messages, a transferable discovery beyond the tested budgets, an independently
audited provider bill, or recursive scientific intelligence. Any superiority
claim requires the verdicts above plus a fresh confirmatory plan.
