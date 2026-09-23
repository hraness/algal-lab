# Weighted-tree spike: exact theorem, equality, and a sharp boundary

This is a proved, scoped mathematical result inside the lab's failure model.
Its novelty relative to the full literature remains unestablished. The proof
does not rely on numerical experiments. The accompanying independent exact
audit checks its implementation consequences and attempts to falsify it on
small cases.

## Model and theorem

Let `V` contain `n >= 2` labeled vertices. Vertex `i` has positive failure
weight `w_i` and positive service value `v_i`. Failures remove one remaining
vertex at a time with probability proportional to its failure weight, without
replacement. Write `S_k` for the survivors after `k` failures. The deletion
distribution is fixed independently of the proposed tree.

For a tree `T`, let `L_v(T[S])` be the largest total vertex value of any
component of its induced surviving forest, with value zero when `S` is empty.
Division by `sum_i v_i` gives the lab's normalized service.

**Theorem.** If a vertex `c` satisfies both

```text
w_c = min_i w_i,       v_c = max_i v_i,
```

then the star `K_c` centered at `c` maximizes `E[L_v(T[S_k])]` over every
labeled tree on `V`, simultaneously for all `k = 0,...,n`. It consequently
maximizes every nonnegative weighted sum of these expectations, including
each trapezoidal AUC horizon. An optimal tree in this subclass can therefore
be constructed in `O(n)` time, including writing its edges.

If `c` is the unique minimum-weight vertex and `n >= 3`, this star is the
unique optimum at every informative step `1 <= k <= n-2`. Positive values
are needed for this strictness assertion.

The equal-value conjecture is a direct corollary: every minimum-weight
center gives an optimal star. There is no claim here for degree-dependent
targeted deletion, graph-dependent failure probabilities, arbitrary values
without the joint extreme vertex, or edge budgets above `n-1`.

## Pair-survival lemma

For distinct `a,b,j`, define

```text
q_ij(k) = P(i and j both belong to S_k).
```

If `w_a <= w_b`, then `q_aj(k) >= q_bj(k)` for all `k`. For
`1 <= k <= n-2`, equality holds exactly when `w_a = w_b`.

**Proof.** Give vertex `i` an independent exponential clock of rate `w_i`.
Order the clocks increasingly and delete in that order. The next-clock
probability is `w_i / sum_remaining w`, and memorylessness reproduces the
whole sequential failure law. Survivors are the vertices with the largest
`n-k` clocks.

The shared event that `a,b,j` all survive cancels when subtracting the two
pair probabilities. Let `D` be the event that `a,j` survive and `b` does not.
Swapping the two clock values at `a,b` maps `D` bijectively to the opposite
event, without changing `j`'s survival. Every clock vector in `D` satisfies
`t_a > t_b`. With exponential densities `f_i(t) = w_i exp(-w_i t)`,

```text
f_a(t_a) f_b(t_b) / [f_a(t_b) f_b(t_a)]
    = exp((w_b - w_a)(t_a - t_b)) >= 1.
```

Integrating the paired density difference over `D` proves the inequality.
For `2 <= n-k <= n-1`, `D` contains an open set of clock configurations:
choose `a,j` and `n-k-2` others late, and choose `b` and the others early.
All densities are positive. The integral is therefore strictly positive
when `w_a < w_b`. Equal rates give equality by label symmetry. The endpoint
steps have pair probabilities all one or all zero. This proves the lemma.

This argument compares two vertices within the same complete failure law;
it does not incorrectly assume that survivor inclusion probabilities are
proportional to reciprocal failure weights.

## Rooted forest bound and proof of the theorem

Root an arbitrary candidate tree `T` at `c`; let `p(j)` be the parent of
each nonroot vertex. For every surviving set `S`, put

```text
M(S) = max_{i in S} v_i, with M(empty) = 0,
B_T(S) = M(S) + sum_{j != c} v_j 1{p(j),j in S} - L_v(T[S]).
```

Then `B_T(S) >= 0`. To see this, take a maximum-value component `C` of
`T[S]` and let `r` be its vertex closest to `c` in the original tree.
Every vertex of `C` except `r` has its parent in `C`, so

```text
value(C) = v_r + sum_{j in C, j != r} v_j.
```

The proposed bound replaces `v_r` by the no-smaller `M(S)` and adds
nonnegative contributions from all other surviving edges. This is valid
even if the largest component does not contain `c`.

The star `K_c` attains the bound for every `S`: when `c` survives, its
component contains all survivors and `M(S)=v_c`; otherwise the surviving
graph has no edges and its service is exactly `M(S)`. Consequently,

```text
E L_v(T[S_k])
  <= E M(S_k) + sum_{j != c} v_j q_{p(j),j}(k)
  <= E M(S_k) + sum_{j != c} v_j q_{c,j}(k)
   = E L_v(K_c[S_k]).
```

The second inequality applies the pair-survival lemma to each child `j`.
If `p(j)=c`, the terms are already identical. This proves the theorem.

For unique-minimum strictness, any tree other than `K_c` has a vertex `j`
with `p(j) != c`. Its parent has weight strictly greater than `w_c`, so
that edge's contribution is strictly smaller at every informative step.
All other differences and `B_T` are nonnegative.

## Equality conditions

The proof gives the exact gap identity

```text
E L_v(K_c[S_k]) - E L_v(T[S_k])
  = E B_T(S_k)
    + sum_{j != c} v_j [q_{c,j}(k) - q_{p(j),j}(k)].
```

For any informative step, equality holds if and only if both conditions
below hold:

1. Every internal vertex of `T` (degree at least two) has globally minimum
   failure weight.
2. `B_T(S)=0` for every surviving subset of size `n-k`.

All such subsets have positive probability, so an almost-sure equality is
equivalent to the second finite condition. For a largest-value component
`C` rooted at `r`, its slack is explicitly

```text
B_T(S) = M(S) - v_r
         + sum_{surviving edges outside C} v_child.
```

Thus condition 2 says that there is at most one component containing an
edge, and if there is one, its vertex closest to `c` has value `M(S)`.

For **equal values**, this simplifies completely. At a step with two or
three survivors, condition 2 always holds. At a step with at least four
survivors and at least one failure, it holds exactly for trees of diameter
at most three: stars and double-stars. A tree of diameter at least four
contains a five-vertex path `a-b-x-d-e`; deleting `x` and retaining
`a,b,d,e` leaves two components with edges. Extend this surviving subset
to any size from four to `n-1` without restoring `x`. Conversely, any
induced subgraph of a star or double-star has at most one nontrivial
component. In particular, under uniform failure weights all stars and
double-stars tie at every step; with at most three survivors all trees
tie. Stars are not generally unique.

For **arbitrary positive values under the theorem's joint-extreme
assumption**, the trees tying the optimal star at every step have a compact
description (`n >= 3`):

- A star whose center has minimum failure weight and value at least the
  second-largest vertex value; or
- A proper double-star whose two centers both have minimum failure weight
  and whose center values are the two largest vertex values, allowing ties.

Necessity already follows from equality after one failure. Two nontrivial
components would create positive slack, so the diameter is at most three.
For a star centered away from `c`, deleting `c` forces the center to have
the maximum remaining value. For a double-star with `c` a center, deleting
`c` forces the other center to have the maximum remaining value. If `c`
is a leaf attached to center `a`, deleting `a` forces center `b` to have
value `v_c`; deleting `c` then forces `v_a=v_b=v_c`. These are precisely
the listed cases. They are sufficient because, in every surviving subset,
the root of the sole nontrivial component has maximum surviving value.
The single two-vertex tree is the trivial additional case.

## A global upper bound when no joint-extreme vertex exists

The rooted forest inequality also gives a certificate without the theorem's
value assumption. Choose a minimum-failure-weight vertex `c`, breaking rate
ties in favor of largest value. For any tree and every step,

```text
E L_v(T[S_k]) <= U_k
U_k = min(E sum_{i in S_k} v_i,
          E M(S_k) + sum_{j != c} v_j q_{c,j}(k)).
```

The first bound is total surviving value. The second is the same rooted
forest bound followed by pair-survival ordering; the star need not attain
it when `c` is not a maximum-value vertex. Among minimum-rate choices,
largest value minimizes this second bound: for tied-rate vertices `c,d`,
the bounds differ by `(v_d-v_c) q_cd`, since `q_cj=q_dj` for every other
vertex `j`.

Apply the positive trapezoidal coefficients to `U_k` and divide by the
initial total value to get a global tree-optimum AUC upper bound `U`.
For a candidate with exactly evaluated AUC `C`, its regret is at most
`U-C`. If `U-C <= epsilon`, this certifies epsilon optimality regardless
of how the candidate was generated. This can support randomized search
with deterministic final error bounds. A loose bound certifies only a
loose result. No sampling estimate or observed best score can substitute
for exact evaluation of the bound. The additional verifier audit checks
this bound against all labeled trees in bounded aligned and misaligned
profiles; it does not tighten it using an unproved one-failure formula.

## Smallest counterexample to unrestricted star optimality

The theorem cannot omit the joint extreme condition and still assert that
some star is always optimal. Use four vertices with

```text
failure weights w = (3, 3, 1, 1)
service values  v = (6, 6, 1, 1)
path edges       = {(0,1), (0,2), (2,3)}
horizon          = 2 failures
```

The independently enumerated exact expected component values at steps
`0,1,2` are `14`, `67/8`, and `159/35`. Its normalized trapezoidal AUC is
`4941/7840`. Stars centered at vertices 0 or 1 attain `4931/7840`; stars
centered at 2 or 3 attain `4929/7840`. The path improves over every star,
with gap `1/784` over the best star. Exhausting all 16 labeled trees
confirms that this path is globally optimal for the stated instance.

Four vertices is minimal by vertex count, because every tree on at most
three vertices is itself a star. The instance also falls inside the lab's
`horizon <= nodes-2` bound. This is a mathematical boundary example, not
evidence that a model discovered a better general algorithm.

The narrower claim that a minimum-failure-weight center alone is optimal
already fails with three vertices: weights `(1,2,2)`, values `(1,3,3)`, one
failure. The expected unnormalized component-value deficit relative to
total surviving value is `3/5` for the minimum-weight center and `2/5` for
either other center. Division by the initial total value, seven, gives
normalized service deficits `3/35` and `2/35`.

An additional asymmetric instance stays inside the registered generator's
weight/value range: weights `(1,1,2,5)`, values `(1,1,4,4)`, the same path,
and horizon two. Its exact AUC is `12937/20160`, the best star attains
`6467/10080`, and the gap is `1/6720`. The verifier exhausts all 16 labeled
trees and confirms the path is globally optimal.

## Independent exact audit

Run from the repository root:

```sh
python3 research/spikes/weighted-tree/verify.py
```

The verifier imports no lab implementation and uses no floating point.
It enumerates every deletion permutation with its exact rational
Plackett-Luce probability and every labeled tree using Prüfer sequences.
This differs from the lab oracle's subset dynamic program. It checks
pair-survival monotonicity and strictness, all-step optimality, unique-minimum
strictness, the full equal-value equality characterization, the arbitrary-value
all-horizon equality characterization, and the boundary counterexample.

The fixed finite coverage is exhaustive over failure weights in `{1,2}`
for each `n=2,...,6`. At `n<=4`, it also exhausts values in `{1,2}` subject
to a joint-extreme vertex. At `n=5,6`, it uses equal values and four fixed
heterogeneous value profiles per weight vector, adjusted to contain a
joint-extreme vertex. It exhausts all trees for every profile, not all
positive real-valued profiles.

| n | Labeled trees | Admitted value/weight profiles | Orders per weight vector |
| --- | ---: | ---: | ---: |
| 2 | 1 | 14 | 2 |
| 3 | 3 | 52 | 6 |
| 4 | 16 | 206 | 24 |
| 5 | 125 | 160 | 120 |
| 6 | 1296 | 320 | 720 |

Recorded result: 752 profiles, 438,186 tree-profile pairs, 3,040,186 exact
step comparisons, and 27,972 strict/non-strict pair-order comparisons;
all passed. A general theorem follows from the proof above, not from this
finite sample.

## Bounded primary-source search and novelty status

Searches on 2026-09-23 covered combinations of weighted vertex failure,
expected largest component, star/double-star optimality, tree reliability,
Plackett-Luce sampling, and unequal-probability inclusion probabilities.
No directly matching joint-extreme theorem was identified in this bounded
search. That is insufficient to establish a new-to-literature theorem.

The exponential ordering construction is established prior art. Efraimidis
and Spirakis describe weighted sampling via independent random keys, and
the later treatment distinguishes different meanings of weighted sampling.
Our result uses the successive proportional-to-remaining-weight law only.
[Weighted Random Sampling over Data Streams](https://arxiv.org/abs/1012.0256),
[author's sampling project](https://utopia.duth.gr/~pefraimi/projects/WRS/index.html).

Unequal-probability sampling and inclusion probabilities are also established
topics; general sampling results do not make survivor marginals proportional
to raw weights. [Yu, On the inclusion probabilities in some unequal probability
sampling plans without replacement](https://arxiv.org/abs/1005.4107).

Related extremal tree reliability results require careful objective matching.
Aivaliotis, Gordon, and Graveman study independent **edge** failures and
greedoid rank, including a rooted reachable-component interpretation. The
unrooted rank in that paper uses subtree complements, rather than the largest
surviving vertex component considered here. It is related prior art, not an
identified proof or refutation of this theorem.
[When Bad Things Happen to Good Trees](https://webbox.lafayette.edu/~gordong/pubs/badthings.pdf).

The supported status is therefore: an independently checked theorem and
smallest boundary counterexample for this explicitly defined objective;
novelty unestablished; no claim to solve a recognized open problem. The
theorem is useful as an exact baseline and as a warning to keep easy aligned
environments separate from difficult misaligned environments in algorithm
discovery experiments.
