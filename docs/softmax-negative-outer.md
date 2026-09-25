# Divisibility decides purity at negative outer temperature

At negative outer temperature, the nested Boltzmann allocation objective
weights the weakest tasks most. Whether whole-agent assignments remain
optimal then depends on an arithmetic fact, whether the number of tasks
divides the number of agents, together with the size of the inner
temperature.

When it does, every maximizer at every nonpositive outer temperature is a
balanced pure assignment, and the value is the same at every such
temperature. When it does not, and the inner temperature is not too large,
the bottleneck limit strictly prefers fractional allocations, so there is a
finite negative outer temperature below which no pure allocation is optimal.
For `N≥2` the zero-temperature optimum is pure in both cases by the
[rectangular theorem](softmax-additive-boundary.md), so the indivisible case
has a genuine transition on the negative half-line. The indivisible case at
large inner temperature is not settled here.

The inner temperature is finite and strictly positive throughout. The proofs
reuse the [concave envelope](softmax-additive-boundary.md) and elementary
inequalities for the outer softmax. The divisible statement is a corollary
of recorded results; the indivisible transition is the candidate
contribution. Literature priority is addressed in the last section.

## Model and notation

Let `N≥1` agents and `M≥1` tasks be finite integers. A feasible allocation
is a nonnegative `N×M` matrix `A` with row sums at most one. With `t>0`,
`E=e^t`, and

\[
 f_t(x)=\frac{\sum_i x_i e^{t x_i}}{\sum_i e^{t x_i}},\qquad
 s_k=\frac{kE}{N+k(E-1)},\qquad
 g_j(A)=f_t(A_{:j}),
 \tag{1}
\]

the reward at finite outer temperature `τ` and its bottleneck limit are

\[
 R_\tau(A)=\frac{\sum_j g_j e^{\tau g_j}}{\sum_j e^{\tau g_j}},\qquad
 R_{-\infty}(A)=\min_j g_j(A).
 \tag{2}
\]

Write `N=qM+r` with `0≤r<M`. A *pure* allocation is a binary matrix. A
*balanced pure* allocation is a binary matrix with exactly one unit entry
in every row, `q+1` unit entries in `r` columns and `q` in the others. Let
`φ` be the polygonal interpolation of `(k,s_k)`; the
[envelope theorem](softmax-additive-boundary.md) gives `f_t(x)≤φ(Σ_i x_i)`,
with equality exactly at binary `x` when `N≥2`, and `φ` is increasing and
concave with strictly decreasing slopes `d_k=s_(k+1)−s_k`.

## Two bounds on the outer softmax

**Lemma 1.** Let `g∈[0,1]^M`, `m=min_j g_j`, and `τ≤0`. Then

\[
 m\le R_\tau\le\frac1M\sum_j g_j,
 \tag{3}
\]

with equality on the right if and only if `τ=0` or all `g_j` are equal.
For `τ<0`,

\[
 R_\tau-m\le\frac{M-1}{e|\tau|}.
 \tag{4}
\]

*Proof.* `R_τ` is a weighted mean of the `g_j`, which gives the left bound.
The weights `w_j=e^{τg_j}` are nonincreasing in `g_j`, so Chebyshev's sum
inequality gives `Σ_j g_j w_j ≤ (Σ_j g_j)(Σ_j w_j)/M`, which is the right
bound; equality holds exactly when one of the two sequences is constant, and
`w` is constant precisely when `τ=0` or `g` is constant. For (4), write
`u_j=g_j−m≥0`. The denominator `Σ_j e^{τu_j}` is at least one because some
`u_j` vanishes, and each of the other `M−1` numerator terms
`u_j e^{−|τ|u_j}` is at most `1/(e|τ|)`; the common factor `e^{τm}`
cancels from numerator and denominator. ∎

The reward `R_τ` is not monotone in its scores: `∂R_τ/∂g_j` has the sign of
`1+τ(g_j−R_τ)`, so raising an already high score can lower `R_τ` when
`|τ|(g_j−R_τ)>1`. The arguments below therefore pass through the bottleneck
limit and the mean, never through monotonicity in individual scores.

## Corollary A: the divisible case is pure at every nonpositive temperature

**Corollary A.** Let `N≥2`, `t>0`, `τ≤0`, and suppose `M` divides `N`, so
`q=N/M` and `r=0`. Then

\[
 \max_A R_\tau(A)=s_q,
 \tag{5}
\]

and the maximizers are exactly the balanced pure allocations, independently
of `τ`.

*Proof.* Put `S_j=Σ_i a_ij`, so `Σ_j S_j≤N=qM`. By (3) and the envelope,

\[
 R_\tau(A)\le\frac1M\sum_j g_j(A)\le\frac1M\sum_j\phi(S_j).
 \tag{6}
\]

Concavity of `φ` gives `φ(S)≤s_q−d_(q−1)(q−S)` for `S≤q` and
`φ(S)≤s_q+d_q(S−q)` for `S≥q`; the first slope exists because `q≥1`, and
when `q=N` the second case is empty and we set `d_N=0` so that (7) reads
correctly. Summing over columns and using
`Σ_(S_j>q)(S_j−q)≤Σ_(S_j<q)(q−S_j)`,

\[
 \sum_j\phi(S_j)\le Ms_q-\bigl(d_{q-1}-d_q\bigr)\sum_{S_j<q}(q-S_j)\le Ms_q.
 \tag{7}
\]

Since `d_(q−1)>d_q`, equality in (7) forces no column sum below `q`, and
then the total budget forces every `S_j=q`. Equality in the envelope step of
(6) then forces every column to be a binary vector with exactly `q` unit
entries, because `N≥2`. These `qM=N` unit entries lie in distinct rows, so
`A` is balanced pure. Conversely, every balanced pure allocation has all
scores equal to `s_q`, so (3) holds with equality and `R_τ(A)=s_q`. ∎

For `q=1` this is the square theorem of the
[task-allocation note](softmax-task-allocation.md); for `τ=0` it is the
`r=0` case of the rectangular theorem. The statement is a corollary of those
recorded results and Chebyshev's inequality: the divisible optimum and its
maximizer set do not move anywhere on `τ≤0`. For `N=1` the
hypothesis forces `M=1` and the single entry `a=1` is the unique maximizer.

## Theorem B: the indivisible case turns fractional

Assume now `r≥1`, hence `M≥2` and `N≥q+1`. Every pure allocation has a
column with at most `q` unit entries, since `M(q+1)>N`, so its bottleneck
score is at most `s_q`; a balanced pure allocation attains `s_q`. Thus

\[
 \max_{A\text{ pure}}R_{-\infty}(A)=s_q.
 \tag{8}
\]

The question is whether a fractional allocation can lift every column above
`s_q`. Consider a column with `q` unit entries, one entry `y∈[0,1]`, and
zeros elsewhere. Clearing denominators,

\[
 f_t(1^q,y,0,\dots,0)>s_q
 \iff
 h(y):=y\,(qE+N-q)-qE\bigl(1-e^{-ty}\bigr)>0.
 \tag{9}
\]

The function `h` is convex on `[0,1]`, strictly so when `q≥1` and linear
`h(y)=Ny` when `q=0`, with `h(0)=0`, `h(1)=N>0`, and
`h'(0)=(qE+N−q)(1−t s_q)`. Define the *crumb threshold* `y*=y*(t,N,q)` as
`0` when `t s_q≤1` and as the unique root of `h` in `(0,1)` otherwise. Then
`h>0` exactly on `(y*,1]`. The sign of `h'(0)` is the sign of
`∂f_t/∂x_k=e^{tx_k}(1+tx_k−tf_t)/Σ_i e^{tx_i}` at an empty coordinate of
`1^q`: to first order, a crumb of effort helps a `q`-occupied task exactly
when `t s_q<1`, and at `t s_q=1` it still helps at second order.

**Spread construction.** Let `m=⌈M/r⌉≥2`. Partition the tasks into `r`
groups of sizes `⌊M/r⌋` or `⌈M/r⌉`. Assign `q` distinct agents fully to each
task, using `qM` agents. Give each of the remaining `r` agents one group,
and let it place `1/|G|` on every task of its group `G`. Every row sum is
one, and column `j` equals `(1^q,y_j,0,…)` up to order with
`y_j=1/|G|∈[1/m,1]`. Some group has at least two tasks, so the matrix `A*`
is fractional.

**Theorem B.** Let `t>0`, `r≥1`, and `y*(t)<1/⌈M/r⌉`. Then

\[
 R_{-\infty}(A^*)=\min_j f_t(1^q,y_j,0,\dots)>s_q
 =\max_{A\text{ pure}}R_{-\infty}(A),
 \tag{10}
\]

so no pure allocation is bottleneck-optimal. Moreover, with
`δ=R_(−∞)(A*)−s_q>0`, every maximizer of `R_τ` is fractional whenever

\[
 \tau<-\frac{2(M-1)}{e\,\delta}.
 \tag{11}
\]

The hypothesis holds whenever `t s_q≤1`, in particular whenever `N<M`.

*Proof.* Each `y_j≥1/m>y*`, so `h(y_j)>0` and (9) gives every column
score above `s_q`; (8) gives the rest of (10). For (11), let `A` be pure.
By (4) and (8), `R_τ(A)≤s_q+(M−1)/(e|τ|)<s_q+δ/2`. By (3),
`R_τ(A*)≥s_q+δ`. The feasible set is compact and `R_τ` is continuous, so a
maximizer exists and its value is at least `R_τ(A*)`, which every pure
allocation falls short of. ∎

Because the zero-temperature maximizers are pure for `N≥2`, the
indivisible case then changes maximizer type at least once on `(−∞,0)`.
Bound (11) is a sufficient condition, not a crossover estimate: for the
`N=3`, `M=2`, `E=4` witness below it gives `τ<−15.45`, while the actual
crossover for that witness lies between `−6` and `−5`. Whether a single
threshold separates the two regimes, and where it lies, is open.

A numerical spike (memo `algal-round24-bottleneck-numerics.md`, retained
locally with the audit memo) searched the bottleneck optimum for
`(N,M)∈{(3,2),(5,2),(4,3),(7,3),(5,3),(2,3)}` over `t∈[0.25,6]`. In every
case the pure balanced allocation stopped being bottleneck-optimal exactly
where the hypothesis of Theorem B starts to hold, to the search resolution:
for `r=1` at the root of `f_t(1^q,1/M,0,…)=s_q`, and for `(5,3)` at the root
of `f_t(1,1/2,0,0,0)=s_1`, `t≈2.3487`. The window between `t s_q=1` and
that root, where the spread allocation wins although a crumb loses to first
order, had width between `0.3` and `0.6` in `t`. Above the root the search
never beat the pure value; for divisible `(4,2)`, `(6,3)`, `(6,2)` it never
beat the balanced pure allocation at any `τ`. These are search results, not
proofs; they suggest that the spread construction is optimal among
fractional allocations in this regime, which is not proved here. The mechanism, a first-order
perturbation showing that a continuous max-min relaxation exceeds every
integral value, is classical; the model-specific threshold `t s_q≤1` and the
divisibility dichotomy are what this note adds.

## Reduction to one column

When the hypothesis of Theorem B fails, the following reduction bounds the
question from the other side.

**Proposition C.** If some feasible `A` has `R_(−∞)(A)>s_q`, then some
column `x=A_(:j)` satisfies `q<Σ_i x_i≤N/M` and `f_t(x)>s_q`. Consequently,
if `max{f_t(x):Σ_i x_i=S}≤s_q` for every `S∈(q,N/M]`, the balanced pure
allocations are bottleneck-optimal.

*Proof.* The column sums average at most `N/M`, so some column has
`S_j≤N/M`; its score exceeds `s_q`, while `φ(S)≤s_q` for `S≤q`. ∎

For `N<M` the window `(q,N/M]` is `(0,N/M]`, the balanced pure allocation
leaves tasks empty, and Theorem B applies with `s_0=0`. The one-column
maximum over a fixed sum is not characterized here; the
[flow note](softmax-additive-flow.md) treats additive objectives only.

## Exact witnesses

With `E=4` and entries in `{0,1/2,1}`, every quantity in (1) is rational
because `e^{t/2}=2`.

- `N=3`, `M=2`, `q=r=1`: `s_1=2/3` and `t s_1=(2/3)ln 4<1`. The spread
  allocation gives agent 3 half a unit on each task; both columns are
  `(1,0,1/2)` up to order with score `(4+1)/(4+1+2)=5/7`. So
  `δ=1/21` and (11) reads `τ<−42/e≈−15.45`. At `τ=0` the balanced pure
  allocation scores `(8/9+2/3)/2=7/9>5/7`, so the maximizer type changes
  between `0` and `−42/e`.
- `N=5`, `M=3`, `q=1`, `r=2`: `s_1=1/2`, groups of sizes two and one, columns
  `(1,1/2,0,0,0)` with score `5/9` and `(1,1,0,0,0)` with score `8/11`;
  `δ=1/18`.
- `N=2`, `M=3`, `q=0`: the balanced pure bottleneck is `s_0=0` and any
  allocation touching every task beats it.
- `E=64`, `N=3`, `M=2`: `t s_1=(32/33)ln 64>1`, and the spread column
  `(1,0,1/2)` scores `68/73<32/33=s_1`. The hypothesis of Theorem B fails
  and the construction does not beat the pure bottleneck, which is consistent
  with the large-`t` regime being open.

## Reproducible checks

```sh
python3 -m unittest research.test_softmax_negative_outer
```

The checks enumerate all allocations with half-unit entries for
`(N,M)∈{(4,2),(6,2),(3,3),(4,4)}` and confirm that the exact mean score is
maximized only by balanced pure allocations; verify (3) and (4), including the
strict case, in Decimal arithmetic at several negative `τ`; confirm that the
negative-`τ` grid maximizers for `(N,M)∈{(4,2),(3,3)}` are exactly the
balanced pure allocations;
verify the exact witnesses above, the pure bottleneck ceiling (8) over all
binary matrices for small sizes, and the finite-`τ` comparison at `τ=−16`
for `N=3`, `M=2` against every binary allocation; and record the `E=64`
boundary. Finite checks support the proofs and do not replace them.

## Prior art and claim boundary

[Amir, Bettini and Prorok](https://arxiv.org/abs/2506.09434), versions 1–4,
treat the softmax theory only for `N=M`. Theorem 3.4 there gives the lower
bound `σ(t,N)−1/N` for `t>0`, `τ≤0`, and Appendix G.4 obtains it from the
one-hot spread allocation together with Schur-concavity of the outer
aggregator for `τ≤0`. Version 1 conjectured that this bound is exact for
`N=M`; the [task-allocation note](softmax-task-allocation.md) proves it. No
version states a non-square softmax result, a fractional optimum, or a
bottleneck regime, so Theorem B was not located there. Their continuous
Table 1 entry for outer `min` and inner `max` implicitly assumes `N≥M`; the
discrete Table 2 carries the indicator. Corollary A is not new relative to
this lab's records: the `τ=0` case is the rectangular theorem with `r=0`,
the `N=M` case is recorded, and the remaining step is Chebyshev's sum
inequality (Hardy–Littlewood–Pólya, §2.17, cited from indexed descriptions,
not opened) plus the observation that a balanced pure allocation has equal
column scores. Balanced optima of
separable concave integer objectives go back to Gross (1956) and Fox (1966),
cited as standard references rather than inspected evidence, and the
cardinality closure is credited to Shioura in the envelope note.

The perturbation in Theorem B is standard first-order analysis, and the
phenomenon that a max-min relaxation strictly exceeds the best integral
value is the integrality-gap phenomenon of max-min fair allocation, seen by
indexed description only. Neither mechanism is claimed as new. The candidate
source-relative contribution is the proved mixed regime at sufficiently
negative outer temperature for indivisible populations under `t s_q≤1`,
contrasting the recorded purity for `τ≥0`, with the divisibility dichotomy
and the explicit threshold (11). Proposition C is a model-specific reduction
whose averaging step is elementary. Open access gaps: the OpenReview forum
for the paper, the Gross and Fox full texts, and the Hardy–Littlewood–Pólya
section; the large-`t` indivisible regime is an open question, where a
tenths-grid search at `E=64`, `N=3`, `M=2` found no allocation beating the
pure bottleneck. No worldwide first-priority assertion follows. The audit
memo `algal-round24-prior-art.md` (SHA-256
`74e5a4736448fd0acb787b3732d5eaefd7c69f3207443f5e69aba8a89774f60e`) and its
search protocol are retained locally under
`research/spikes/context/runs/round24-negative-outer/`.
