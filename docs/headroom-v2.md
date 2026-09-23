# Headroom study behind instrument v2

Evidence for adopting `network.v2` (heterogeneous failure) and for the budgets
frozen in [`comparison-plan-v2.json`](../examples/comparison-plan-v2.json).
This is a distilled record of a scratchpad spike; the production instrument
lives in [`src/heterogeneous.ts`](../src/heterogeneous.ts) and its oracle in
[`src/oracle.ts`](../src/oracle.ts).

## Instrument under test

Each node i has integer failure weight w_i ≥ 1 and value v_i ≥ 1, fixed by the
environment. Random failure removes survivors sequentially without
replacement, P(i) = w_i / Σ_survivors w. Service after each removal is the
most valuable connected component's share of Σv; trapezoid AUC over steps
0..s. Targeted control stays label-blind: max live degree, lowest id tie.

Exact oracle: subset DP, f(∅)=1; f(S) = Σ_{i∈S} f(S\{i}) · w_i / (W − w(S\{i}));
expected service at step k = Σ_{|S|=k} f(S)·service(V\S). O(2^n · n), exact.

## Verification

- Reduces to `exactRandomAuc` when w=v=1: max |Δ| ≤ 3.3e-16 across 150 graphs
  at six budgets; sampled simulator reproduces v1 `simulate` on 200 graphs
  with 0 mismatches.
- Monte Carlo in the spike at 200k sampled schedules per graph: |MC − exact|
  ≤ 0.0006, within ±2 standard errors on all five checked (graph, profile)
  pairs.
- Label dependence: over all 40,320 relabelings of a fixed 8-node profile and
  reference graph, 4,710 distinct AUC values in [0.7869, 0.8252]; every
  non-(w,v)-preserving permutation changes the AUC. Flat profile is invariant.
- Repo-side: `bun run qualify:instrument` re-checks flat reduction across all
  766 connected n=4,5 graphs (0 error) and the subset DP against exhaustive
  weighted-order enumeration (2,260 comparisons, ≤4.4e-16).

## Headroom at the registered v1 budgets

Mean optimum-minus-reference regret over a 16-environment panel (8 uniform,
8 two-class profiles) plus the flat control. Exact optima by exhaustive
enumeration where feasible; "ref relabeled" is the best of all 8! relabelings
of the fixed reference under each environment.

| Budget | Optimum bound | ref regret | relabeled | heur best | rand2k best | scripted |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 8/10/3 | exact, 10,230,360 graphs | 0.0167 | 0.0059 | 0.0097 | 0.0018 | 0.0265 |
| 8/12/3 | exact, 28,044,072 graphs | 0.0016 | 0.0007 | 0.0009 | 0.0004 | 0.0114 |
| 10/14/4 | 5,000 optimizer starts | 0.0131 | 0.0033 | 0.0046 | 0.0039 | 0.0322 |

Heterogeneity alone does not clear the preregistered 0.03 bar at these edge
densities — the budget, not the weights, is the binding constraint.

## Alternative regimes

| Regime | Optimum bound | ref regret | relabeled | heur best | rand2k best | scripted |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 8/10/3, mix objective | exact | 0.0265 | 0.0065 | 0.0215 | 0.0027 | 0.0349 |
| 8/12/3, mix objective | exact | 0.0028 | 0.0002 | 0.0024 | 0.0006 | 0.0117 |
| 10/14/4, mix objective | 1,800 starts | 0.0225 | 0.0020 | 0.0118 | 0.0060 | 0.0372 |
| **8/10/6 (deep failure)** | exact | **0.0310** | 0.0101 | 0.0085 | 0.0048 | 0.0386 |
| **8/8/3 (sparse)** | exact | **0.0463** | 0.0321 | 0.0074 | 0.0025 | 0.0548 |
| **10/11/4 (sparse)** | 1,800 starts | **0.0535** | 0.0167 | 0.0107 | 0.0076 | 0.0633 |

The sparse budgets are the adopted regimes: label-blind designs provably
cannot compete (best relabeling still ≥0.03 short at 8/8/3), while
label-aware heuristics (0.0074) and seeded random search (0.0025) show the
headroom is reachable rather than oracle-only. The flat control stays
near-optimal for the reference at 8/8/3 (0.0097), so heterogeneity — not
sparsity alone — creates the gap. The adversary mixture was rejected: pure
weighted random failure already clears the bar and keeps the instrument to
one objective.

## Environment rule

Per replicate: `environmentFor(nodes, replicateSeed)` — uniform 1..5 weights
and values, redrawn with seed+1 until both spreads ≥3. Each replicate poses
an independent problem while conditions share one world; per-replicate
regret ranges 0.021–0.064 at 8/8/3, so a single shared environment would
make the verdict profile-luck-sensitive. The environment is visible to
researchers — adapting a design to it is the measured skill.
