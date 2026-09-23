# Frozen policy-evolution experiment, 2026-09-23

**The registered success criterion failed.** A policy selected by 48 bounded
evolutionary proposals improved on random-start local search, but a simple
theorem-informed star seed followed by the same local search performed better.
The result does not establish an algorithmic discovery, an advantage of policy
evolution over good fixed heuristics, or token efficiency.

The policy and source hashes were frozen before measuring 32 heldout seeds in
each of four graph regimes. No policy or experimental source was changed after
selection. The primary comparison averages the two eight-node regimes within
each seed, giving 32 comparison units. All seven search arms receive exactly 64
objective evaluations per case, including initialization and repeated graphs.
The objective is exact expected weighted-random-failure AUC, evaluated using
floating point arithmetic over the finite distribution.

The selected policy, candidate 43, is:

```json
{"minValue":0,"maxValue":0.5,"risk":1,"noise":0.25,"degree":0,"restart":16}
```

Its edge-construction score is half the log of the larger endpoint value,
minus the endpoints' combined failure weight divided by mean failure weight,
plus seeded Gumbel noise of scale 0.25. It greedily constructs a spanning tree,
adds any extra edges, then performs improving single-edge mutations and
restarts every 16 evaluations. The best graph is retained across restarts.

## Heldout evidence

Mean AUC, with 32 prespecified environment seeds in each row:

| Regime | Selected | Random hill | Annealing | Star hill | Fixed reliable | Star without search |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| n=8, m=7, s=3 | 0.777009 | 0.769047 | 0.769754 | **0.780182** | 0.776279 | **0.780182** |
| n=8, m=8, s=3 | 0.790346 | 0.781039 | 0.782675 | **0.791306** | 0.790028 | 0.786381 |
| n=10, m=9, s=4 | 0.749436 | 0.732250 | 0.734374 | **0.759600** | 0.747358 | **0.759600** |
| n=10, m=11, s=4 | 0.772329 | 0.764724 | 0.764317 | **0.777143** | 0.772868 | 0.772460 |

Primary selected-minus-baseline differences:

| Baseline | Mean AUC difference | Paired bootstrap 95% interval | Wins / ties / losses |
| --- | ---: | --- | --- |
| Random search | +0.016434 | [0.013574, 0.019310] | 32 / 0 / 0 |
| Random hill | +0.008635 | [0.005788, 0.011728] | 29 / 0 / 3 |
| Star hill | **−0.002067** | [−0.002911, −0.001275] | 3 / 0 / 29 |
| Annealing | +0.007463 | [0.004865, 0.010281] | 28 / 0 / 4 |
| Fixed pair | +0.010511 | [0.007299, 0.014211] | 32 / 0 / 0 |
| Fixed reliable | +0.000524 | [−0.000217, 0.001233] | 13 / 10 / 9 |
| Selected without search | +0.016522 | [0.012764, 0.020632] | 32 / 0 / 0 |
| Star without search | +0.000396 | [−0.000621, 0.001397] | 17 / 0 / 15 |

The registered criterion required a mean gain above 0.005 over random hill,
a positive lower bootstrap endpoint, and a higher mean than each of
`star-hill`, `annealing`, `fixed-pair`, and `fixed-reliable`. Its last condition
failed. Only this full primary criterion was specified as the study's success
test. Secondary and per-regime intervals are descriptive and unadjusted.

The comparison with `fixed-reliable` gives no clear primary evidence that the
evolutionary selection itself helps. Its development mean rose from the best
initial policy's 0.787672 to 0.789288, but that training improvement is not a
heldout effect estimate. The no-search star matched star hill to numerical
tolerance on both tree regimes. This observation alone is not a proof of
global tree optimality for multiple heterogeneous failures.

An explicit failure case is `transfer-tree:41280`: the selected policy scores
0.709843, while the star scores 0.735509, a gap of 0.025666. The environment is
weights `[3,4,3,4,4,3,5,5,5,2]`, values `[5,2,3,2,5,2,4,2,2,2]`.
There were no construction or evaluation exceptions in the actual study.

## Resource and validation accounting

Development spent **49,152 objective evaluations**: 48 proposals, representing
42 distinct configurations, over 16 cases and 64 evaluations each. Every
proposal, including rejected and repeated configurations, is retained with
parents, scores, failures, graphs, duplicate counts, and best-so-far traces.
Development included 4,625 repeated graph proposals, all charged to budget.

Heldout search spent **57,344 objective evaluations**: seven arms, 128 cases,
64 evaluations each. The selected arm accounted for 8,192 evaluations, including
453 repeated graphs. Repeats were 0 for random search, 694 for random hill,
2,164 for star hill, 643 for annealing, 284 for fixed pair, and 421 for fixed
reliable. No edge-mutation call returned an unchanged graph. Annealing accepted
172 worsening moves; every arm retained its best graph.

No-search constructors use **zero objective evaluations for selection**; their
256 combined measurements are charged separately. The independent original
oracle checked all **896 search champions**, with maximum absolute discrepancy
`2.4424906541753444e-15`. Those checks are additional computation. Constructor
work, subset-probability compilation, and wall time are not equated to an
objective-evaluation budget. Training took about 0.71 seconds and heldout work
about 1.80 seconds on this host; these timings are not controlled performance
comparisons.

A fresh process reproduced all development candidates and all heldout arm
results, including graphs and best-by-evaluation traces, exactly. This replay
spent another 106,496 search evaluations, 256 no-search measurements, and 896
oracle checks, taking about 2.53 seconds. Validation work is additional to the
reported discovery and deployment costs. Reproduction proves consistency of
these retained computations, not novelty or scientific generality.

Commands executed successfully:

```sh
bun test research/spikes/evolution/policy.test.ts
./node_modules/.bin/tsc --noEmit --strict --target ES2022 --module ESNext --moduleResolution bundler --skipLibCheck --noUncheckedIndexedAccess --exactOptionalPropertyTypes --resolveJsonModule --types bun research/spikes/evolution/policy.ts research/spikes/evolution/experiment.ts research/spikes/evolution/policy.test.ts research/scorer.ts
bun research/spikes/evolution/experiment.ts train
bun research/spikes/evolution/experiment.ts evaluate
bun research/spikes/evolution/experiment.ts replay
```

Focused validation: five tests, 109 assertions, no failures; explicit strict
TypeScript checking passed. The repository integrator owns the aggregate gate.
Raw generated archives remain in ignored `runs/v1/` alongside this note.
The protocol SHA-256 is
`9a3965031226e49a91f1b964b55d310d83e12de5b5aa989da056b4a8aa4c92cd`;
the heldout archive SHA-256 is
`789d70d501e96905c8cbbe2d74dca50582598d51122844f282e0ceeacfc30109`.

## Scope and implication

These are small graphs from one frozen value/weight generator and one search
random stream per case. Random graph proposals use the repository's recursive
tree plus extra edges generator, not a uniform draw from connected graphs.
The annealing schedule was fixed before evaluation, not optimized. The star
baseline uses the one-deletion center formula, although scoring uses three or
four deletions. No inference calls, generated code, targeted attacks, global
multi-deletion optimality proofs, or amortized-token claims are involved.

Reusable learned network-robustness construction policies already exist; for
example [Zhu et al., Nature Communications (2026)](https://www.nature.com/articles/s41467-026-70745-0)
learn edge-addition policies using a different, targeted-attack objective.
The present result supports investing in structural mathematics and stronger
fixed baselines before scaling this particular evolutionary grammar. It does
not show that evolutionary research policies in general cannot help.
