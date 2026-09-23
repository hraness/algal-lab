# A frontier theorem for terminal network design

We derived and independently checked an exact tree optimizer for a deliberately
separate endpoint: **the expected value of the largest component when exactly
two vertices survive weighted sequential deletion**. Its structural theorem
reduces the design to a small reliability/value frontier. A second algorithm
uses sampled deletion sequences and returns a finite-sample regret certificate.

This is a proved result within the declared mathematical model. Literature
priority for the specific structural result and combined algorithm remains
unresolved. The sampling law, probability integral, integer-polynomial idea,
spanning-tree machinery, and concentration tools have established prior art.
The contribution being assessed is their model-specific structural reduction
and checked implementation, not the invention of those ingredients.

The [earlier AUC study](weighted-tree-discovery.md) is unchanged. Its evolved
policy failed to beat the strongest fixed baseline. The terminal endpoint was
specified afterward as a new research question; success here cannot rescue
that failed comparison or establish a solution of the general AUC problem.

The fresh hybrid experiment passed its fixed criterion on the specified
64-vertex panel: **5.73× median speedup over the included exact construction**,
mean measured normalized regret **0.0000399**, and maximum probabilistic regret
bound **0.00835**, at 2,048 samples. These are bounded local results; the
[full findings](../research/spikes/terminal/hybrid-findings.md) show slower
regimes, competitive star baselines, and the distinct probability assumptions.

## Exact result

Let vertex `i` have positive failure rate `w_i` and value `v_i`. Repeatedly
delete a vertex with probability proportional to its remaining rate. Write
`q_ij` for the probability that `i,j` are the final survivors, and `V=sum v_i`.
For any graph `G`, its expected normalized terminal service is

`sum_(i<j) q_ij max(v_i,v_j)/V + sum_(ij in G) q_ij min(v_i,v_j)/V`.

Thus the best tree is a maximum spanning tree with edge rewards
`q_ij min(v_i,v_j)`. More specifically:

1. Keep one representative of each nondominated rate/value point: lower failure
   rate and higher value are preferable. These vertices form a frontier `F`.
2. Some globally optimal tree makes every other vertex a leaf attached to its
   best neighbor anywhere on `F`.
3. Order the frontier by increasing rate. Its values then also increase.
   Each frontier vertex after the first attaches to the best earlier vertex.

The proof uses a clock-exchange inequality, a tree-edge replacement argument,
and the maximum spanning tree cut property. It proves the existence of an
optimum with this structure; it does not assert uniqueness or this structure
for every optimum. The full [proof](../research/spikes/terminal/tree-proof.md)
covers duplicate points, ties, and a counterexample to restricting leaf
attachments to their dominators. All pair probabilities use the original
population, including the vertices made leaves.

With integer rates, divide out their common gcd and put `W=sum w_i`. Form
`P(x)=product_i(1-x^w_i)`. Dividing out two factors and integrating gives

`q_ij=(w_i+w_j) integral_0^1 x^(w_i+w_j-1) P(x)/((1-x^w_i)(1-x^w_j)) dx`.

Polynomial division uses an integer coefficient recurrence. A common
denominator `lcm(1,...,W)` permits exact integration and comparisons without
floating-point cancellation. Equal rate pairs share a cached calculation.
For `d` rate classes, frontier size `p`, and `A<=dp` queried rate-pair classes,
tree construction takes `O((n+A)W+np+n log n)` integer arithmetic operations.
This is **pseudopolynomial**, not polynomial in the binary length of arbitrary
rates. The proof separately accounts for integer bit lengths and storage.

For rates in `1..5`, there are at most five frontier vertices and fifteen pair
classes, and this implementation uses `O(n²)` arithmetic operations. Full
reporting of expected service additionally evaluates all label pairs and may
integrate every rate class. The experiment times construction separately from
that shared exact evaluation.

A small strict witness is `w=(2,2,1,1), v=(3,3,1,1)`. The path with edges
`01,02,23` achieves terminal service `181/480`; the best star achieves
`89/240`. The exact improvement is **`1/160`**, verified against all sixteen
labeled trees. These are terminal scores, not trajectory AUCs.

## Randomized algorithm with a checked error bound

For a fixed number `N` of sampled weighted deletion sequences, count their
final survivor pairs. Either maximize the empirical edge rewards over all
trees, or restrict the design to the proved frontier family. Both algorithms
receive exactly the same histogram in the experiment.

The implementation samples weighted deletions with integer tickets and a
Fenwick tree. It avoids approximating exponential clocks with floating-point
logarithms. Under independent unbiased tickets, every pair count has a binomial
marginal. Simultaneous binomial KL confidence intervals cover all true pair
probabilities with probability at least `1-delta`, including unseen pairs.

For any selected tree, shared edges cancel when comparing it with a competing
tree. Put lower confidence weights on its edges and upper weights on other
edges; a maximum spanning tree then gives an upper bound on its regret.
The interval boundaries use outward Decimal logarithm enclosures and a dyadic
grid; the final spanning tree and regret calculation use exact integers and
rationals. The displayed float rounds upward.

The [sampling proof](../research/spikes/terminal/sampling-proof.md) states the
probability assumptions, numerical argument, and fixed-sample limitation.
Arbitrary supplied counts or a deterministic seed cannot establish the IID
premise. A zero confidence bound is a statement on the coverage event, unless
separate deterministic evidence also proves optimality. Optional stopping
requires a different bound or a preallocated failure budget.

The structural restriction also has an explicit sample-complexity consequence.
The ordered frontier family contains `(p-1)! p^(n-p)` trees, versus `n^(n-2)`
unrestricted labeled trees. Standard finite-family concentration therefore
gives a smaller worst-case sampling bound for the restricted optimizer. This
is a consequence of the structural theorem and established concentration
machinery; it is separate from measured performance.

The [hybrid refinement](../research/spikes/terminal/hybrid-proof.md) uses the
theorem in the certificate itself. A leaf's possible parents stop at the first
frontier vertex whose value reaches its own: later vertices have no better
edge reward. Parent decisions are independent and their edge sets are disjoint.
The certificate therefore sums only the uncertain alternatives within each
decision, with the selected edge cancelling exactly. Only these fixed relevant
pairs need probability intervals; their probabilities need not sum to one.

When every parent choice is forced, the hybrid returns a deterministic optimum
without sampling or computing a probability. Otherwise it samples and reports
a confidence bound. This explicitly combines a deterministic structural proof
with randomized estimation where the proof leaves a choice unresolved.

## Experimental protocol and evidence

The [frozen protocol](../research/spikes/terminal/protocol.json) compares six
regimes at 24 and 64 vertices: rates in `1..5`, rates in `1..99`, and a stress
family where every vertex lies on the frontier. Four environment seeds, two
sampling seeds, and budgets of 128, 512, 2,048, and 8,192 give 192 histograms and
384 algorithm certificates. All cases and arms are fixed before evaluation.
Both arms share each histogram; allocating the failure budget separately to
both arms is conservative. Seeded trials are numerical evidence rather than
a statistical proof of independent randomness.

References include the exact optimum, best star, a reliability-centered star,
and 32 seeded Prüfer trees per environment. An independent exact subset DP
checks pair probabilities at 8, 12, and 16 vertices. The protocol records a
three-part speed/error criterion before outcomes are observed; every result
is retained whether it meets that criterion or not.

The [findings](../research/spikes/terminal/findings.md) report outcomes and
source/archive hashes. Local timings compare the included Python
implementations; they are not claims of superiority over mature external
Wallenius or spanning-tree libraries. Exact evaluation is shared experimental
ground truth and is excluded from the construction timings of both approaches.

The first terminal comparison failed its registered conjunction: its worst
confidence bound was 0.0102046 against a 0.01 limit, despite passing the speed
and measured-regret thresholds. The subsequent
[hybrid comparison](../research/spikes/terminal/hybrid-findings.md) uses fresh
seeds and a [separate frozen protocol](../research/spikes/terminal/hybrid-protocol.json).
It retains the original sample budget, per-certificate failure allowance,
primary regimes, and three acceptance thresholds. The original sources and
failed archive remain unchanged.

The mathematical implementation is independently checked against exact
weighted-order enumeration, exhaustive Prüfer trees, and a separate generic
maximum spanning tree. The probability certificate is also checked by exact
finite histogram enumeration, including cases where it fails with nonzero
probability and the total failure probability remains below its bound.
These are ordinary mathematical proofs plus executable checks, not a
machine-checked proof in a theorem prover.

## Reproduce

The code requires Python's standard library, no credentials or paid inference.

```sh
python3 -m research.terminal_tree research/examples/terminal-candidate.json
python3 -m unittest research.test_terminal_tree research.test_terminal_sampling research.test_terminal_hybrid
python3 -m research.spikes.terminal.experiment run --out research/spikes/terminal/runs/new
python3 -m research.spikes.terminal.experiment replay --out research/spikes/terminal/runs/new
python3 -m research.spikes.terminal.hybrid_experiment run --out research/spikes/terminal/runs/new-hybrid
python3 -m research.spikes.terminal.hybrid_experiment replay --out research/spikes/terminal/runs/new-hybrid
```

The standalone solver admits 2–128 vertices and integer rates/values in
`1..1,000,000`, with a separate exact-work budget: gcd-reduced total rate at
most 8,192 and at most forty million projected coefficient operations.
It rejects inputs exceeding those bounds. These bounds do not modify the
`network.v2` instrument or its admitted inputs.

Sampling admits at most 32,768 trajectories, bounded by 4,194,304 node-samples.
The default library sampler uses `secrets.randbelow`; the experiment supplies
a seeded generator for numerical reproduction. All generated archives stay
under ignored `runs/` directories. Existing archives are never overwritten.

## Prior art and remaining scientific claims

[Wallenius Bayes](https://repository.uantwerpen.be/docman/irua/532293/149101_2019_02_23.pdf)
(2018, §4.1.2) already gives the relevant product integral, integer-weight
polynomial interpretation, and gcd reduction. [Fog's calculation methods](https://www.agner.org/random/theory/nchyp1.pdf)
discuss the distribution and cancellation in expansion formulas.
[Ng and Donadio](https://doi.org/10.1016/j.jspi.2005.03.010) study inclusion
probabilities for order sampling. The full latter paper and specialized
spanning-tree literature remain relevant review leads.

Our scoped candidate contribution is the terminal-design frontier theorem,
its exact implementation and explicit computational bound, and the sampled
design's numerically enclosed regret certificate. Missing search hits do not
establish novelty. External expert review is still needed before presenting
this as a literature-first result. Nothing here establishes an advantage for
LLM intelligence, automatic generator evolution, or token efficiency.
