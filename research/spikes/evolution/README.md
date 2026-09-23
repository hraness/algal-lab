# Reusable policy evolution spike

This bounded, credential-free experiment evolves six numeric fields describing
a graph constructor and restart schedule. It does not evolve executable code or
the evaluator. Its objective is the unchanged exact expected `network.v2`
weighted-random-failure AUC; all discovery and deployment evaluations use that
same objective.

The [completed findings](findings.md) report a failed success criterion: the
evolved policy beat ordinary local search but lost to the theorem-based seed.

The constructor builds a spanning tree by repeatedly choosing a maximum-scoring
edge between components, then fills the extra-edge budget. Edge scores combine
log minimum/maximum endpoint value, endpoint failure weight, seeded Gumbel
noise, and a degree penalty. Deployment spends at most 64 objective evaluations
on this constructor, one-edge mutations, and periodic restarts. Greedy acceptance
keeps only strict local improvements; the best graph survives every restart.
These are standard ingredients. This experiment tests a narrow combination and
does not assert algorithmic novelty.

The frozen [protocol](protocol.json) specifies training and heldout seeds,
budgets, policy count, selection, baselines, and a practical success margin.
Development uses 48 policy proposals, including repeated proposals, over 16
cases: **49,152 exact objective evaluations** in addition to deployment costs.
All proposals, parents, selection scores, failures, duplicate counts, and
best-so-far traces are retained. The stochastic stream permits regeneration of
every proposed graph. No inference is performed; token efficiency is untested.

The prespecified environment seed is the comparison unit. Primary tree and
unicyclic results are averaged within each seed before primary inference. Each
transfer regime is reported separately. Bootstrap intervals describe this
environment distribution and one fixed random stream per case, not arbitrary
graphs or independent reruns of policy search.

The one registered primary criterion is confirmatory for this bounded study;
per-regime and secondary intervals are descriptive and unadjusted. The stronger
baseline comparisons name `star-hill`, `annealing`, `fixed-pair`, and
`fixed-reliable` separately.

The training and evaluation commands are separate so that the selected data policy and source
hashes are written before any heldout evaluation. Existing output files are
never overwritten. A changed source fails evaluation admission.

```sh
bun test research/spikes/evolution/policy.test.ts
bun research/spikes/evolution/experiment.ts train
bun research/spikes/evolution/experiment.ts evaluate
bun research/spikes/evolution/experiment.ts replay
```

Archives are written to ignored `runs/v1/` inside this directory. Each reported
search champion is also checked with the original, independent union-find
oracle. The compiled scorer uses IEEE-754 arithmetic over the full finite
distribution; “exact” does not mean rational arithmetic.

`replay` regenerates the full development candidate sequence and every heldout
arm in a fresh process, then requires byte-identical retained data after removing
the training runtime. Evaluation verifies that the selected policy is the
archived development winner before any heldout work. Archive reads have file
size and JSON structure bounds. Replay establishes numerical reproduction, not
scientific validity or a general-purpose adversarial archive certification.
