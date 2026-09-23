# Weighted-tree discovery and proposal-policy experiment

2026-09-23. This continuation starts from the [first live network.v2 comparison](live-comparison-v2-findings.md),
whose live arm did not beat random search and whose shared messages hurt transfer.
The immediate research question is where the instrument admits a provable new
result within the project, and where genuine optimization difficulty remains.
We kept the failure instrument and its existing oracle unchanged.

## Results and their scope

Two exact design rules now remove whole families from the search problem:

- With one removal, an optimal tree is always a star. Its center minimizes
  `w_c (V - v_c - max_{j != c} v_j)`. The best tree and its exact rational AUC
  can be constructed in O(n) arithmetic operations, instead of searching
  the `n^(n-2)` labeled trees.
- At every removal horizon, a star is optimal if its center simultaneously
  has minimum failure weight and maximum value. The proof holds for arbitrary
  positive weights and values, not just a finite parameter grid. A strictly
  minimum failure weight makes that star the unique optimum for the lab's AUC.

The [full structural proof](../research/spikes/structural/README.md) includes a
complete phase diagram for a four-node, two-class family. An
[independent proof and verifier](../research/spikes/weighted-tree/README.md)
derive the same optimality bound using rooted components and exponential clocks.
[Executable linear-time solvers](../research/optimal-trees.ts) expose the two
sufficient cases. A `null` result means these sufficient conditions did not
certify an optimum; it does not prove that every star is suboptimal.

Conflicting reliability and value can require another shape. For four nodes,
weights `[1,1,2,5]`, values `[1,1,4,4]`, and two removals, the path with edges
`[[0,1],[0,2],[2,3]]` is globally optimal among all 16 labeled trees:

| Design | Exact expected AUC |
| --- | ---: |
| Path | `12937/20160` |
| Best star | `6467/10080` |
| Path advantage | `1/6720` |

All parameters lie in the existing environment generator's `1..5` range and
satisfy its spread guard. The gain is small (about 0.000149), but exact. It is
a counterexample to the unrestricted star conjecture, not a practical speedup
or a proof that randomization beats deterministic optimization.

## How the result was checked

The general statements have ordinary mathematical proofs with independent agent
review. They are not Lean/kernel-checked formalizations. Finite checks support
the implementations and examples; they do not replace those general proofs.

```sh
bun test research/scorer.test.ts research/optimal-trees.test.ts
python3 research/spikes/structural/verify.py
python3 research/spikes/weighted-tree/verify.py
```

The first Python checker uses exact integer/rational arithmetic for 104,976
one-failure tree/profile comparisons, 1,125 aligned-hub comparisons, 1,440
phase-family comparisons, and 128 independent removal-order cross-checks.
The second independently enumerates deletion permutations and every labeled
tree through six nodes on a bounded 752-profile panel: 438,186 tree/profile
pairs, 3,040,186 step comparisons, and 27,972 pair-survival order comparisons.
It imports neither the lab simulator nor its numerical oracle.

The [compiled evaluator](../research/scorer.ts) amortizes graph-independent
removal probabilities across candidate graphs. Bit-set flood fill independently
computes component values. It matches the original union-find oracle within
`2e-14` on all connected four/five-node graphs and all admitted horizons
(2,260 comparisons), plus larger bounded examples. Both TypeScript evaluators
use floating-point arithmetic for expectations; the Python certificates use
rational arithmetic.

## Randomized proposal, deterministic regret certificate

The same proof supplies an upper bound on the best possible tree even when no
node has both favorable extremes. At step k, choose a minimum-failure-weight
vertex c, with maximum value among ties, and bound expected component value by
the smaller of expected total surviving value and

`E[max surviving individual value] + sum_{j != c} v_j P(c and j survive k)`.

At the first failure, the exact optimum above tightens this bound. Integrating
these upper bounds gives an upper bound on the optimal tree AUC. Subtracting a
candidate's exact AUC yields a deterministic additive-regret certificate. The
bound can be loose: a positive gap does not prove that the candidate is
suboptimal. A zero gap does prove optimality within the declared tree problem.

The [exact certifier](../research/tree_certificate.py) accepts a JSON object
with `graph`, `environment`, and `steps`, using the existing shapes. It validates
connected trees with 4–10 nodes, positive integer weights/values at most 99,
and horizons 1 through n−2. It enumerates the complete failure distribution
using rational arithmetic; this verification remains exponential in node count.

```sh
python3 research/tree_certificate.py research/examples/aligned-candidate.json
python3 research/tree_certificate.py research/examples/path-candidate.json
python3 -m unittest research.test_tree_certificate
```

This permits uncertain or randomized proposal generation followed by an exact
check of the produced design and its regret bound. It does not make the
generator optimal, remove verification cost, or establish a new general
proposal-and-verification paradigm. The independent bound audit covers
160,016 comparisons across a bounded 410-profile panel and all trees through
six nodes.

After the frozen evolution experiment, we ran this exact check on all 64 of its
selected tree outputs. **Ten were certified globally optimal** (8/32 primary,
2/32 transfer). For the others, the checker returned upper bounds rather than
asserting optimality. Across all 64 outputs, the mean additive-regret bound was
0.020735 AUC and the maximum 0.073787. These are conservative bounds, **not
measured true regret**. The checks did not select or modify any design.

```sh
python3 research/certify_policy_results.py research/spikes/evolution/runs/v1/heldout.json
```

The [bounded report bridge](../research/certify_policy_results.py) emits all 64
complete certificates and binds the input archive and both verifier sources by
SHA-256. Its input archive digest for this run is
`789d70d501e96905c8cbbe2d74dca50582598d51122844f282e0ceeacfc30109`.

## Evolution experiment

The separate [frozen protocol](../research/spikes/evolution/protocol.json)
evolves bounded data parameters controlling graph construction and search.
Every search arm receives 64 candidate evaluations per deployment. Offline
policy selection has a separate cost; it cannot be counted as free deployment
performance. Policies freeze before fresh environment evaluation and transfer
to larger graphs. No paid inference or model token-efficiency claim belongs to
this experiment. See the [complete experiment report](../research/spikes/evolution/findings.md)
for regeneration commands and all baseline results.

**The registered success criterion failed.** Across the 32 prespecified seeds,
averaging the two primary budgets within seed, the selected policy improved on
random-start hill climbing by 0.00863 AUC (paired bootstrap 95% interval
`[0.00579, 0.01173]`). But it lost to theorem-star-seeded hill climbing by
0.00207 (`[-0.00291, -0.00127]` for selected minus star). The registered
criterion also required beating the stronger fixed baselines in mean.

| Budget: nodes/edges/removals | Evolved policy | Random-start hill climbing | Theorem-star-seeded hill climbing |
| --- | ---: | ---: | ---: |
| Primary tree: 8/7/3 | 0.77701 | 0.76905 | **0.78018** |
| Primary unicyclic: 8/8/3 | 0.79035 | 0.78104 | **0.79131** |
| Transfer tree: 10/9/4 | 0.74944 | 0.73225 | **0.75960** |
| Transfer bicyclic: 10/11/4 | 0.77233 | 0.76472 | **0.77714** |

The deterministic star construction alone matched star-seeded search in both
tree regimes. On these cases, its structural knowledge was more useful than
49,152 offline policy-training evaluations. The evolution experiment spent
57,344 additional heldout search evaluations, 256 output measurements for
zero-search controls, and 896 independent oracle checks. Maximum numerical
discrepancy was `2.45e-15`. Deployment budgets match objective evaluations,
not wall-clock time; all policy-selection cost remains additional.
Fresh numerical reproduction repeated 106,496 search evaluations, 256 control
measurements, and 896 oracle checks, reproducing all retained designs and traces.

Secondary intervals and individual-regime contrasts are descriptive and
unadjusted. This is one selected policy and one fixed stochastic stream per
case, not evidence about arbitrary reruns or model-token efficiency. The
negative result is retained; no policy was retuned on these outcomes.

## Prior art and novelty status

These are newly derived and verified results in this repository. Literature
priority is **unresolved**. A targeted primary-source review found related
results, and failure to find an identical statement is not proof of novelty.

[Goldschmidt, Jaillet and LaSota (1994)](https://web.mit.edu/~jaillet/www/general/networks-pj-94.pdf)
discuss classical optimal stars for residual node connectedness: the probability
that all survivors remain connected under homogeneous independent failure.
They cite Stivaros's 1990 dissertation for that result. We have inspected the
paper, not the dissertation. Our theorem concerns expected maximum surviving
component **value**, with heterogeneous sequential removal. That distinction
does not itself establish that our result is absent from older work.

[Zhu et al. (2026)](https://www.nature.com/articles/s41467-026-70745-0) already
learn reusable edge-addition policies to improve cumulative largest-component
robustness under targeted attack. [FunSearch](https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/)
already combines evolving program proposals with systematic evaluation.
The idea of evolution plus deterministic checking is established. A stronger
claim here needs a specific result and a comparison against relevant methods.

The [Vals shortest-path example](https://www.vals.ai/blogs/faster-shortest-path-algorithm)
motivated seeking a bounded theorem rather than merely more agent activity.
Its reported asymptotic improvement is separate from practical runtime gains.
Our result likewise does not imply a faster general shortest-path algorithm,
a physical-network discovery, or success on a longstanding open problem.

The structural rules provide exact controls and a way to avoid rediscovering
solved subcases. Antagonistic value/reliability profiles, extra-edge budgets,
and comparisons that charge offline policy selection remain the appropriate
places to test the evolutionary research mechanism.
