# Frontier-prefix hybrid algorithm and regret guarantee

The [hybrid implementation](../../terminal_hybrid.py) uses the proved terminal
tree structure to remove unnecessary parent choices and probability estimates.
Its endpoint is expected largest surviving component value divided by original
total value after exactly two vertices remain. It does not optimize trajectory
AUC. The underlying structural results and their prior-art limits are in the
[exact tree proof](tree-proof.md).

This is a subsequent algorithm and experiment, not a revision of the completed
v1 result. The [v1 primary criterion failed](findings.md): its maximum bound was
approximately `0.01020463347`, above the registered `0.01` threshold. Its
numerical sources, archive, and failed criterion remain unchanged. The new
algorithm requires a separate frozen protocol and fresh evaluation seeds.

## The pruned family contains an optimum

Let `F=(f_0,...,f_(p-1))` be one representative of each nondominated
`(failure weight, value)` point, sorted by increasing failure weight. Both
weights and values strictly increase along this frontier. Let `q_ij` be the
probability that `{i,j}` are the final pair in the **original full population**,
and let `s_ij=q_ij min(v_i,v_j)`.

The exact tree theorem supplies a globally optimal tree with these choices:

- Each frontier vertex `f_j`, for `j>0`, chooses a parent in
  `f_0,...,f_(j-1)`.
- Each nonfrontier vertex `b` chooses a parent in `F`.

For a nonfrontier vertex `b`, let `r` be the first frontier position whose
value satisfies `v_(f_r)>=v_b`. Such a position exists because `b` has a
frontier dominator, including the representative of an identical point when
necessary. For every later frontier point `f_k`, `k>r`, both edges have the
same value multiplier `v_b`. Pair-rate monotonicity gives

`q_(b,f_r) >= q_(b,f_k)` and therefore `s_(b,f_r) >= s_(b,f_k)`.

Thus some best attachment for `b` lies in the prefix `f_0,...,f_r`. Replacing
a later attachment by this prefix endpoint cannot decrease the objective.
Applying this independently to every nonfrontier leaf preserves a global
optimum. No vertex is removed from the probability distribution; only edge
choices are pruned.

There is one parent-choice group for each vertex other than `f_0`. Any
combination of these choices is a tree: frontier edges point to strictly
earlier frontier positions, and nonfrontier vertices attach only to the
frontier. Consequently every vertex has a path to `f_0` and there are exactly
`n-1` edges. Choices in different groups are disjoint: a frontier edge belongs
to its later endpoint's group, and a nonfrontier edge belongs to its
nonfrontier endpoint's group.

Each group can therefore be optimized independently. This statement concerns
a family containing **some** true optimum, not all optimal trees or a unique
optimum. Nondominating frontier parents inside the prefix must remain
eligible; the example in the exact proof shows why restricting leaves to
their dominators is incorrect.

## Deterministic and sampled cases

A group with one parent is forced. Its only edge occurs in every tree in the
pruned family, so its contribution cancels in every comparison between a
candidate and the family's true optimum. It needs no probability estimate.

If every group is forced, the family contains just one tree. The structural
theorem proves this tree globally optimal without any random draw. The public
function returns `status="structurally-exact-tree"`, exact regret bound `0`,
zero actual samples, and zero draw operations. The requested sample budget is
still validated and recorded separately as `requestedSamples`. Empirical
connection benefit is `null` because no empirical distribution was obtained.
This deterministic case includes some environments with more than one
frontier vertex.

Otherwise, for a fixed requested `N`, the sampler obtains `N` terminal-pair
observations using the frozen integer weighted-deletion sampler. Within each
group, it selects a parent maximizing `count_ij min(v_i,v_j)`, resolving ties
by the canonical edge tuple. The implementation retains the complete
lexicographic pair histogram for replay. Only the edges in nonforced groups
receive confidence intervals.

## Simultaneous intervals on the relevant edge set

Let `E'` be the union of edges in groups with at least two choices and
`m'=|E'|`. This set is determined from the input environment before observing
counts. Under independent unbiased sampling, each count has marginal
`C_e ~ Binomial(N,q_e)`. For `p_e=C_e/N`, set

`I_e={q in [0,1]: N kl(p_e || q) <= log(2m'/delta)}`,

where

`kl(p || q)=p log(p/q)+(1-p) log((1-p)/(1-q))`.

For fixed true `q_e`, the two binomial Chernoff tails bound the probability
that `q_e` lies outside this set by `2 exp(-log(2m'/delta))`. A union bound
over `E'` gives simultaneous inclusion with probability at least `1-delta`.
Dependence among different pair counts does not invalidate this argument;
independence across trajectory replications is required.

The concentration argument is classical, using the exponential-moment method
associated with [Chernoff's original report](https://statistics.stanford.edu/technical-reports/measure-asymptotic-efficiency-tests-hypothesis-based-sum-observations).
The binomial moment-generating-function derivation is stated explicitly in the
[existing sampling proof](sampling-proof.md). Bernoulli KL confidence bounds
also have extensive prior use, including [Garivier and Cappe's KL-UCB paper](https://proceedings.mlr.press/v19/garivier11a/garivier11a.pdf).
No new concentration inequality is claimed here.

The implementation reuses the frozen outward-rounded interval engine. Its
integer endpoints `L_e,U_e` have denominator `D=2^40`, so on the coverage
event `L_e/D <= q_e <= U_e/D`. Directed Decimal logarithm enclosures ensure
rounding can only widen these intervals; the existing arithmetic tests verify
that implementation independently using integer likelihood comparisons.

There is **no** assertion that `sum_(e in E') q_e=1`: the relevant set may be
a strict subset of all terminal pairs. The hybrid does not apply the earlier
full-simplex interval tightening to this subset. Its union budget is valid
because `E'` is fixed by the environment, not selected after seeing counts.

## Separable regret certificate

Write `a_e=min(v_i,v_j)` for edge `e={i,j}`, and let `e_g` be the candidate
edge selected in uncertain group `g`. For any other edge `f` in that group,
on the simultaneous coverage event,

`a_f q_f - a_(e_g) q_(e_g) <= [a_f U_f - a_(e_g) L_(e_g)]/D`.

Selecting `e_g` itself contributes exactly zero. Its upper and lower bounds
must not be subtracted from each other: it is the same edge on both sides
and cancels. Since group choices are independent and the family contains a
global optimum, normalized regret is at most

`R_box = sum_g max(0, max_(f in g, f!=e_g) [a_f U_f-a_(e_g) L_(e_g)])/(V D)`,

where `V=sum_i v_i` and only uncertain groups occur in the sum. Forced edges
cancel identically. This is the exact worst-case regret over the rectangular
interval box: group alternatives are independent, their edge sets are
disjoint, and each chosen competitor can attain its upper endpoints while
the distinct selected edges attain their lower endpoints. A feasible full
probability distribution may not attain this relaxation; that can only make
the box certificate conservative.

For any terminal pair, the difference between two tree payoffs is at most
`min(v_i,v_j)`. It is therefore bounded by the second-largest vertex value.
The implementation returns

`R = min(R_box, second_largest(v)/V)`.

Integer endpoint calculations followed by `Fraction` division preserve the
enclosure. `confidenceRegretBoundExact` is the resulting rational string;
`confidenceRegretBound` is only a display float, rounded upward if necessary.
The graph-independent term of terminal service cancels from every regret
comparison and need not be estimated.

The same simultaneous event covers data-dependent choices made using that
histogram. It does not require a separate selection sample. A zero statistical
bound establishes optimality **on that coverage event**, not unconditional
deterministic optimality. Nonforced outputs retain
`status="confidence-bounded-tree"` even if their reported bound is zero.

## Sampling assumptions and bounded work

`sample_hybrid_tree` defaults to `secrets.randbelow` and accepts an injected
`randbelow` function for reproducible numerical studies. The integer sampler
implements exact weighted deletion given independent uniform integer tickets.
Neither a fixed pseudorandom seed nor range checks prove the IID premise.
`optimize_hybrid_counts` verifies the histogram's shape and bounds but cannot
establish its origin. Zero total counts are admitted only in the deterministic
all-forced case.

The guarantee is for one call at a fixed `N`. Repeated calls or checkpoints
require a declared failure-budget allocation. Reusing fixed-N intervals until
a desirable certificate appears is not justified by this theorem. The new
comparison must freeze its sources, panel, budgets, and summaries before
evaluation and retain all outcomes.

The public budgets remain `n=2..128`, integer weights and values in
`1..1,000,000`, `N=1..32,768`, `N*n<=4,194,304`, and
`delta in [0.000001,0.25]`. In nonforced cases the integer sampler uses
`N(n-2)` deletion draws and `O(N n log n)` integer work. Parent selection
visits only the pruned choices, and certificate arithmetic visits only their
uncertain-group edges. The KL engine caches interval calculations by observed
count. Complete histogram admission and output still take `Theta(n^2)` work;
pruning does not eliminate that interface cost.

## Focused validation

The public [hybrid test suite](../../test_terminal_hybrid.py) passed all six
tests with this command from the repository root:

```sh
python3 -B -m unittest research.test_terminal_hybrid -v
```

The focused run took approximately `0.941` seconds on the development host;
that duration is descriptive, not a performance result. Tests cover:

- All 6,561 four-vertex environments with weights and values in `1..3`, using
  exact weighted-permutation probabilities. Every pruned family contains a
  global optimum against all 16 labeled trees: 104,976 tree comparisons.
- Seventy-two interval-box comparisons across 24 fixed-seed environments with
  four to six vertices. An independent exhaustive family comparison agrees
  exactly with the separable formula, and the bound covers true family regret
  whenever the constructed intervals contain the true probabilities.
- The strict nonstar witness with optimum-versus-best-star gap `1/160`, and
  the example that requires retaining a nondominating parent in the prefix.
- Four forced cases, including a two-point frontier, with both the random
  callback and interval constructor forbidden. Every result is an exact
  optimum with zero draws and zero confidence computations.
- Reproduction of the frozen integer sampler's histogram from the same seed,
  deterministic histogram replay, and rejection of malformed environments,
  counts, budgets, deltas, and random callbacks.

These checks validate the bounded implementation; the general guarantee rests
on the proof and the stated sampling assumptions. Literature priority for the
combined structural method remains unresolved. No claim about a new
concentration theorem, the earlier AUC objective, LLM intelligence, or token
efficiency follows from this result.
