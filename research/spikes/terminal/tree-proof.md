# Exact terminal tree optimization through a dominance frontier

This note concerns a **new terminal endpoint**: exactly two vertices remain
after sequential weighted vertex removal from a simple undirected graph, and
the objective is the expected value of the largest surviving component. Each
step removes one remaining vertex with probability proportional to its positive
failure weight. Removed vertices and their incident edges disappear; paths
through a removed vertex do not remain connected. It does not optimize network.v2's
trajectory AUC. It does not alter the frozen proposal-policy experiment.

There are `n>=2` labeled vertices with positive failure weights `w_i` and
positive values `v_i`. The structural results below hold for real weights and
values.
The exact polynomial probability algorithm additionally assumes positive
integer failure weights; its stated bit bound assumes positive integer values.
Rational values can also be handled using exact comparisons, accounting for
their denominators. No literature-priority claim is established.

## 1. Terminal expectation is an edge-additive objective

Let `q_ij` denote the probability that the final two survivors are exactly
`{i,j}`. For any simple undirected graph `G`, their largest component has value

`max(v_i,v_j) + 1[{i,j} is an edge] min(v_i,v_j)`.

Therefore

`E L(G) = sum_{i<j} q_ij max(v_i,v_j) + sum_{ij in E(G)} s_ij`,

where `s_ij = q_ij min(v_i,v_j) > 0`. The first term is graph-independent.
Among trees, a maximum spanning tree with edge weights `s_ij` is consequently
a global optimizer. Division by total initial value gives normalized terminal
service and does not change the optimum.

## 2. Exact pair probabilities

Represent the removal process by independent clocks `T_i ~ Exp(w_i)` and delete
in increasing clock order. The first-clock selection rule and memorylessness
give exactly proportional-to-remaining-weight sequential removal. Vertices
`i,j` are the final pair precisely when every other clock is smaller than
`min(T_i,T_j)`. That minimum has rate `r=w_i+w_j` and is independent of the
other clocks. Hence

`q_ij = r integral_0^infinity exp(-rt) product_{k notin {i,j}}(1-exp(-w_k t)) dt`

`     = r integral_0^1 x^(r-1) product_{k notin {i,j}}(1-x^w_k) dx`.

The change of variables is `x=exp(-t)`. This is a special case of the known
multivariate Wallenius/partitioned Plackett-Luce probability integral, not a
new probability identity.

For positive integer rates, divide every weight by their common gcd first.
This common scaling changes clock time units only and preserves every removal
order probability. From now on let `W` be the sum of these reduced rates.

Construct the integer polynomial `P(x)=product_k(1-x^w_k)` in `O(nW)` integer
additions. To obtain `P/(1-x^a)`, use the coefficient recurrence

`Q_d = P_d + Q_(d-a)`, with coefficients outside the range interpreted as zero.

Divide twice, with `a=w_i,b=w_j`, to obtain coefficients `c_d` of the product
over the other vertices. Set `L=lcm(1,...,W)` and precompute `L/t` for each
integer `1<=t<=W`. Then

`N_ij = (w_i+w_j) sum_d c_d [L/(w_i+w_j+d)]`

is an integer and `q_ij=N_ij/L`. All divisions in this expression are exact.
The common denominator lets edge comparisons use only the integers
`N_ij min(v_i,v_j)`. No alternating sum is evaluated in floating point.
The identities `N_ij>0` and `sum_{i<j}N_ij=L` supply useful exact checks.

For fixed full multiset of rates, `N_ij` depends on the unordered rate pair
`(w_i,w_j)`, not the two labels or their values. Cache one integration per
queried pair of rate classes. A repeated pair `(a,a)` is only queried when
at least two vertices have that rate. Rates `1..5` permit at most 15 such
classes, independent of the number of vertices.

## 3. Pair monotonicity and edge dominance

For distinct `a,b,j`, if `w_a<=w_b`, then `q_aj>=q_bj`.

Proof: swap clock values at `a,b`. This maps the event that `a,j` are the last
two clocks bijectively onto the event that `b,j` are the last two. On the
first event, `t_a>t_b`, and the ratio of the two exponential densities is

`exp((w_b-w_a)(t_a-t_b)) >= 1`.

Integrating proves the inequality. For `n>=3`, the event has positive measure,
so unequal rates give strict inequality. Equal rates give equality by label
symmetry. This is the same clock-exchange argument underlying the previously
derived general-horizon pair-survival ordering.

Say that vertex `a` weakly dominates vertex `b` if
`w_a<=w_b` and `v_a>=v_b`. For every third vertex `j`,

`s_aj = q_aj min(v_a,v_j) >= q_bj min(v_b,v_j) = s_bj`.

This compares edges to a common third vertex. It does **not** assert that
edge `ab` exceeds every edge incident to `b`.

## 4. Simultaneous leafification theorem

Collapse identical `(w,v)` points to one representative, chosen by lowest ID
for determinism. Let `F` contain one representative of each nondominated
point, using the usual weak inequalities with at least one strict coordinate
for dominance between different points. Every vertex outside `F` has a weak
dominator in `F`; duplicate points use their representative as dominator.

**Theorem:** Some globally optimal tree has the following form:

1. A maximum spanning tree on the vertices of `F` under weights `s_ij`.
2. Every vertex `b` outside `F` is a leaf attached to a vertex maximizing
   `s_bf` over **all** `f in F`.

Proof: begin with any tree and process the vertices outside `F`, maintaining
that already processed vertices are leaves adjacent only to `F`. To process
`b`, choose a frontier dominator `a` and root the current tree at `a`. Replace
each edge from `b` to one of its children `j` by edge `a-j`. The detached
child component does not contain `a`, so every replacement remains a tree.
Edge dominance makes every replacement nondecreasing in weight. Vertex `b`
now has a single neighbor `p`, its former parent.

If `p` is in `F`, its edge is already no better than the best frontier
attachment. If `p` is outside `F`, choose a frontier dominator `f` of `p`.
Since `b` is distinct from both `p` and `f`, edge dominance gives
`s_bf>=s_bp`. In either case, detach the leaf `b` and attach it to its best
frontier neighbor without reducing total weight.

An already processed nonfrontier leaf cannot be adjacent to `b`, because its
only neighbor lies in `F`. Thus this operation preserves all previous leaf
attachments. After every nonfrontier vertex is processed, the remaining
frontier edges form a spanning tree on `F`. Maximizing its weight and each
independent leaf attachment gives the stated construction. Applied to an
optimal starting tree, this proves global optimality of the construction.

This proves that **some** optimum has this shape, not that all optima do or
that it is unique. Frontier vertices themselves are allowed to be leaves.
When `|F|=1`, the construction is a star at a simultaneous minimum-rate,
maximum-value representative, matching the earlier sufficient star theorem.

Restricting a discarded vertex to its dominators would be incorrect. For

`w=(1,2,3,4), v=(1,3,2,1)`, the frontier is `{0,1}`. Vertex 1 dominates vertex
2, whereas vertex 0 does not. Nonetheless `s_02=7/30` exceeds `s_12=2/9` by
`1/90`. The optimal attachment for vertex 2 is to vertex 0. The algorithm
must search the whole relevant frontier, not only the dominators.

## 5. The frontier core has an ordered parent rule

Sort the frontier as `f_1,...,f_p` by increasing failure rate. Rates and values
both increase **strictly** in this sequence: equal rates would eliminate the
lower-valued point, equal values would eliminate the higher-rate point, and
duplicate points have already been collapsed.

For `i<j<k`,

`s_(f_i,f_j) = v_(f_i) q_(f_i,f_j) >= v_(f_i) q_(f_i,f_k) = s_(f_i,f_k)`.

Consequently Prim's maximum-tree algorithm can add frontier vertices in this
fixed order. At a stage whose selected set is `f_1,...,f_(j-1)`, every edge
from `f_i` to a later vertex `f_k`, `k>=j`, is bounded above by its edge to
`f_j`. Thus a maximum edge crossing the current cut is

`(f_j, argmax_{i<j} v_(f_i) q_(f_i,f_j))`.

Choose this edge and continue. The maximum cut property proves optimality.
Ties between parents can be resolved deterministically by vertex ID; no
uniqueness assertion follows. Only `p(p-1)/2` core edge weights and at most
`(n-p)p` leaf attachment weights are needed.

One may skip, for a nonfrontier vertex, frontier vertices after the first
frontier point with value at least its value: later points have the same
`min` value and no larger pair probability. This is an optional optimization,
not needed for correctness.

## 6. Complexity and numerical meaning

Let `p=|F|`, let `K` be the number of distinct reduced integer rates, and let
`A` be the number of unordered rate-pair classes queried during construction.
Then `p<=K`, `A<=Kp`, and always `A<=K(K+1)/2`. Probabilities retain the full
original population throughout; deleting dominated vertices from the
probability calculation would change the distribution and invalidate the rule.

The construction used in [terminal_tree.py](../../terminal_tree.py) consists
of `PairProbabilities(weights)` followed by `frontier_tree(environment, pairs)`.
After common-gcd normalization it takes

`O((n+A)W + np + n log n)`

integer arithmetic operations: full polynomial construction, division and
integration per queried rate class, frontier sorting, and all attachment
comparisons. Caching the quotient for each first rate adds at most `K` length
`W` divisions, already absorbed by the `nW` term. Precomputing the common
LCM and its reciprocal table is also bounded by this arithmetic count, if a
gcd is counted as an integer operation. Without either reduction, a full-pair
polynomial calculation followed by sorted-edge Kruskal takes
`O(n^2 W + n^2 log n)` arithmetic operations.

The public `optimize` function then computes exact expected service and
normalization by looping over every labeled pair. Its **complete report**
therefore also performs `Theta(n^2)` pair visits and may integrate every
possible rate-pair class. If `A_all` is the number of such classes, the report
cost is

`O((n+A_all)W + n^2 + n log n)`.

The returned counters distinguish `constructionPairIntegrations` from
`totalPairIntegrations`, and separately report construction edge evaluations.
The construction bound alone must not be attributed to complete reporting.
The frozen comparison experiment times construction on both sides; its later
exact quality evaluation and reference comparisons are outside those times.

These are **arithmetic-operation bounds**. They are not unit-cost
bit-complexity claims. Polynomial coefficients have magnitude at most `2^n`.
A conservative bound is `log_2 L <= log_2(W!) = O(W log W)`. If admitted values
have at most `b` bits, every integer in the polynomial and optimizer stage has

`B=O(W log W+n+b)`

bits, including partial sums in the alternating integration. Classical integer
multiplication, exact division, and gcd admit a conservative `O(B^2)` bit cost,
so the construction stage has the safe bit bound

`O(((n+A)W + np + n log n) B^2)`.

The analogous complete-report bound replaces `A` by `A_all` and `np` by `n^2`.
Reading and common-gcd normalization of the original rates additionally depend
on their encoded bit length; the bounds above concern the reduced-rate stage.

The production implementation caches **single-factor quotient arrays** as well
as integrated pair numerators. Its storage bound is

`O(KW + A + n)` integers, or `O((KW + A + n) B)` bits.

Use `A_all` for complete reporting. This bound includes polynomial scratch
arrays, the `L/t` table, quotient caches, rate-class metadata, and the returned
tree. An alternative implementation could discard single-factor quotient
arrays to reduce memory; that is not the current implementation.

These bounds are pseudopolynomial in binary-encoded rates, not strongly
polynomial. Common-gcd normalization can materially reduce `W`. With rates
restricted to `1..5`, `W<=5n`, `K<=5`, `p<=5`, and `A_all<=15`; construction
and complete reporting take `O(n^2)` arithmetic operations under this bound.
No step enumerates all removed subsets or failure orders.

## 7. Independent bounded verification

The public [test suite](../../test_terminal_tree.py) uses complete sequential
weighted-removal permutations with exact `Fraction` arithmetic as an
independent probability reference. Tree comparisons decode every labeled
Pruefer sequence and evaluate the actual terminal component values. The
larger-case maximum-tree reference uses explicit component sets, separate
from the production ordered-frontier construction.

Run from the repository root:

```sh
python3 -B -m unittest research.test_terminal_tree -v
```

The focused run passed all seven tests. Its exact checks comprise:

- 420 pair-probability comparisons over 60 profiles with `n=2..6`, covering
  equal rates, common-gcd rates, mixed extremes, and fixed-seed profiles.
- All 6,561 four-vertex environments with rates and values in `1..3`, compared
  with all 16 labeled trees: 104,976 exact tree comparisons.
- Eight fixed-seed environments at each of `n=5,6`, compared with all labeled
  trees: 11,368 additional exact tree comparisons.
- Independent full-graph Kruskal comparisons at `n=24,64,128`, gcd scaling,
  duplicate points, a full frontier, admitted-input boundaries, and CLI JSON
  rejection cases.

Thus the two exhaustive tree panels contain 116,344 comparisons. These finite
checks support implementation correctness; the unrestricted result follows
from the proof above, not from extrapolating the test panel.

A strict nonstar optimum is included as a regression witness. For
`w=(2,2,1,1)`, `v=(3,3,1,1)`, the path with edges `01,02,23` has normalized
terminal service `181/480`. The best star has service `89/240`, so the exact
gain is `1/160`. This is a terminal-endpoint result, separate from any earlier
trajectory-AUC counterexample. The suite also retains the nondominator
attachment example from Section 4.

The [fixed experiment protocol](protocol.json) and [runner](experiment.py)
provide a separate comparison with sampled proposals and their confidence
certificates. Timings and holdout outcomes are not needed to prove the exact
structural theorem and are not asserted by this proof document.

## 8. Prior art and appropriate claim

The probability integral is established. Fog's
[distribution note](https://www.agner.org/random/distrib.pdf) gives the
multivariate Wallenius integral and attributes the distribution to Chesson
(1976). Ma et al., AISTATS 2021, derive related partitioned Plackett-Luce
integrals in [Learning to Rank from Partitioned Preference](https://arxiv.org/pdf/2006.05067).

Integer-rate polynomial integration and common-gcd reduction are also known:
Junque de Fortuny, Martens, and Provost's
[Wallenius Bayes](https://repository.uantwerpen.be/docman/irua/532293/149101_2019_02_23.pdf),
Machine Learning 107 (2018), Section 4.1.2, Equation 12, explicitly describes
both. The exact integer coefficient implementation here is an implementation
choice, not evidence of priority for the underlying transformation. Maximum
spanning trees and their cut property are classical.

The scoped result developed here is the dominance-frontier leafification and
ordered-core characterization for this terminal graph objective, with an
exact optimizer assembled from established probability and spanning-tree
methods. Its literature priority remains unresolved. This is an ordinary
mathematical proof with independent exact-arithmetic checks, not a proof
assistant formalization. It establishes deterministic exact optimization for
the declared terminal endpoint; it does not establish a solution to the
full-AUC problem, superiority of randomized algorithms, or a recognized open
problem.
