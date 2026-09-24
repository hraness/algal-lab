# Sparse support in continuous softmax allocation

Every positive-temperature optimum has an acyclic allocation support, and
no agent divides effort between two tasks that nobody else serves. These
restrictions bound the number of active tasks by `2N−1` and the number of
positive allocation entries by `3N−2`, independently of the number of
available tasks. Every optimum using at most two tasks is pure.

Two further arguments enlarge the [earlier purity region](softmax-integral-optima.md):
a dimension-dependent inner-temperature threshold and a purity certificate
obtained from any certified feasible reward. The [certified occupancy
solver](certified-softmax-partitions.md) now checks these conditions and
uses a direct interval scan for two tasks.

The conclusions below are analytic statements about **every global
maximizer**, at finite positive temperatures. The sufficient boundaries and
support bounds are not claimed sharp for actual optima. Fractional optima
with three or more active tasks remain unresolved outside the proved
regions. Classical ingredients and the limits of the literature comparison
are identified at the end.

## Model and maximum-point identities

There are positive integers `N` agents and `M` tasks. A feasible matrix
`A=(a_ij)` is nonnegative, with every row sum at most one. Define

\[
 B_c(x)=\frac{\sum_i x_i e^{cx_i}}{\sum_i e^{cx_i}},\qquad
 S_j=B_t(A_{:j}),\qquad R(A)=B_\tau(S),\qquad t,\tau>0.
\]

A pure allocation gives each row's whole unit to one task. A task is active
when its column has a positive entry, and private to a row when that entry
is its only positive one. All entries and task scores lie in `[0,1]`.

Use the notation

\[
 p_{ij}=\frac{e^{t a_{ij}}}{\sum_l e^{t a_{lj}}},\quad
 h_{ij}=1+t(a_{ij}-S_j),\qquad
 P_j=\frac{e^{\tau S_j}}{\sum_l e^{\tau S_l}},\quad
 g_j=1+\tau(S_j-R),\quad W_j=P_jg_j.
\]

The [budget and sign lemmas](softmax-integral-optima.md#every-positive-temperature-optimum-uses-full-budgets)
already establish, at every positive-temperature global maximum:

- Every row sums to one.
- Every active column has `W_j>0`, and every positive entry has `h_ij>0`.
- Within the positive support of each row,
  `∂_ij R=W_j p_ij h_ij=λ_i>0` is constant.

The last statement follows from feasible two-sided transfers; for a row
with one positive entry, define `λ_i` as that entry's positive derivative.
These signs hold at maxima, without assuming global monotonicity of either
Boltzmann operator.

For one Boltzmann mean, writing `h_i=1+c(x_i−B_c(x))`, differentiation gives

\[
 D^2B_c(x)[u,u]
 =c\sum_i p_i(1+h_i)u_i^2
   -2c\left(\sum_i p_i u_i\right)DB_c(x)[u],\qquad
 \partial_i^2B_c=cp_i[1+h_i-2p_ih_i].
 \tag{1}
\]

For a transfer between two positive entries `j,k` of a maximizing row,
let `v_j=p_ij h_ij`, `v_k=−p_ik h_ik`, and other `v_l=0`.
Stationarity gives `DB_τ(S)[v]=0`. Consequently the outer Hessian
contribution in the chain rule is

\[
 \tau\sum_{l\in\{j,k\}}P_l(1+g_l)v_l^2>0.
 \tag{2}
\]

Thus if both moved inner coordinates have nonnegative second derivatives,
the transfer has strictly positive second derivative and cannot pass
through a maximum. A useful equivalent form, suppressing the row index
and using the common derivative `λ>0`, is

\[
 R''=\lambda\sum_{l\in\{j,k\}}
 \left[t\left(1+\frac1{h_l}-2p_l\right)
       +\tau p_lh_l\left(1+\frac1{g_l}\right)\right].
 \tag{3}
\]

These are elementary derivative and second-order-condition ingredients.

The degenerate dimensions are settled throughout the positive quadrant.
For `M=1`, full budgets force the sole column to be all ones. For `N=1`,
task scores are the entries of its row. With
`σ(c,d)=e^c/(e^c+d−1)`, each outer weight satisfies
`P_j≤σ(τ,M)`, so

\[
 R\le\sigma(\tau,M)\sum_j a_{1j}\le\sigma(\tau,M).
\]

When `M≥2`, equality in a supported term's weight bound forces its entry
to equal one and every other entry to vanish. Unit row vectors attain
the bound. Thus these degenerate optima are pure independently of the
sufficient inequalities below.

## Every maximizing support is a forest

Form the bipartite support graph with all `N` row vertices, its `K` active
task vertices, and an edge `(i,j)` exactly when `a_ij>0`. Let `E` be its
number of edges and `C` its number of connected components. There are no
isolated row vertices, and inactive tasks are omitted.

**Theorem.** At every global maximum the support graph is a forest.

Suppose instead that a simple cycle exists. Put alternating `+1,−1` values
on its edges and zero elsewhere, obtaining an array `V` with zero row
and column sums. Set `U_ij=V_ij/λ_i`. Its row sums still vanish, and
`A+zU` is feasible for all sufficiently small `z` of either sign because
every moved entry is initially positive. At each active column,

\[
 DS_j[U_{:j}]
 =\sum_i p_{ij}h_{ij}\frac{V_{ij}}{\lambda_i}
 =\frac1{W_j}\sum_i V_{ij}=0.
\]

The outer Hessian contribution therefore vanishes. The last term of each
inner Hessian in (1) vanishes as well. What remains is

\[
 D^2R(A)[U,U]
 =t\sum_{j\ \mathrm{active}}W_j
       \sum_{i:\,a_{ij}>0}p_{ij}(1+h_{ij})U_{ij}^2>0.
\]

All nonzero summands have positive coefficients, and the cycle makes
`U` nonzero. This contradicts maximality on the two-sided feasible line.

A forest has `E=N+K−C`. If `F` is the number of fractional rows, full
budgets imply

\[
 \sum_i(\deg(i)-1)=K-C,\qquad
 F\le\min(N,K-C)\le\min(N,M-1).
 \tag{4}
\]

Forest structure alone does not force `F=0`.

## No row serves two private tasks

**Theorem.** No row of a global maximum has two private active tasks.

Suppose a row puts positive efforts `a,b` into two private tasks. Their
scores are `x=q_N(a)`, `y=q_N(b)`, where

\[
 q_N(u)=\frac{u e^{tu}}{e^{tu}+N-1}.
\]

Consolidating the efforts gives scores `(c,0)`, with `c=q_N(a+b)`.
This is feasible since `a+b≤1`, preserves the row total, and changes no
other score. For `N≥2`, the ratio `q_N(u)/u` strictly increases for positive
`u`, so `c>x+y`. For `N=1`, it is constant and `c=x+y`. Always `c≥x+y`.

Let `R` be the old reward, including the other unchanged tasks.
The positive outer derivative at `x` gives `R<x+1/τ`. First compare the
formal score replacement `(x,y)→(x+y,0)`. With `X=e^(τx)>1` and
`Y=e^(τy)>1`, its numerator and denominator changes are

\[
 \Delta N=xX(Y-1)+yY(X-1),\qquad
 \Delta D=(X-1)(Y-1)>0.
\]

The reward increases exactly when `ΔN−RΔD>0`. Dividing by `ΔD` gives

\[
 \frac{\Delta N}{\Delta D}
 =\frac{x}{1-e^{-\tau x}}+\frac{y}{1-e^{-\tau y}}
 >x+\frac1\tau>R,
\]

using `1−e^(−z)<z` for positive `z`. Hence this formal replacement
strictly improves the reward. It is an algebraic comparison point and need
not itself be realizable by an allocation.

To reach the actual score `c≥x+y`, compare the new numerator minus `R`
times its denominator while increasing the replacement coordinate `v`.
Its derivative is

\[
 \frac{d}{dv}\{(v-R)e^{\tau v}\}
 =e^{\tau v}[1+\tau(v-R)]>0\qquad(v\ge x+y).
\]

The sign follows from `v>x>R−1/τ`. The residual improvement therefore
persists at the actual feasible consolidation, contradicting maximality.
For `N=1` this final increase has zero length, but the preceding improvement
is already strict. The newly empty task remains in the outer denominator
with weight one throughout the comparison.

This proof uses the derivative sign at a maximum. It does not assert that
merging arbitrary small scores improves every Boltzmann mean.

## Support bounds independent of the number of tasks

Let `L` be the number of active task vertices of degree one. Their owners
are distinct by the private-task theorem, so `L≤N`. Counting task degrees
and using the forest identity gives

\[
 2K-L\le E=N+K-C,
 \qquad K\le N+L-C\le2N-C,
 \qquad E\le3N-2C.
\]

Since `C≥1`, every global maximum satisfies

\[
 \boxed{K\le\min(M,2N-1)},\qquad
 \boxed{E\le\min(N+M-1,3N-2)}.
 \tag{5}
\]

In a component containing `n` rows, `k` tasks and `l` task leaves, the same
argument gives `k≤n+l−1≤2n−1`. A component with one row is therefore just
an isolated row–task edge. Every fractional row has a shared neighboring
task; all its neighbors cannot be private.

A refinement tracks the actual fractional rows. Let `D` be the number of
isolated row–task edge components. A private task with a pure owner forms
exactly such a component; all other private tasks have distinct fractional
owners. Hence

\[
 L\le D+F,\qquad K\le N+F+D-C.
\]

If `F>0`, at least one component is not an isolated edge, giving
`K≤N+F−1`. If `F=0`, purity directly gives `K≤N`.

These restrictions still allow fractional support trees. For example,
start with a tree on `N≥2` row vertices, replace each edge by a shared task
of degree two, and attach one private task to every row. The resulting
bipartite tree has `K=2N−1`, `E=3N−2`, and no row owns two private tasks.
Positive allocations with full row sums can realize it. This demonstrates
that the graph restrictions alone cannot improve (5); it does not produce
a stationary point or an optimizing fractional allocation.

## At most two active tasks force purity

**Theorem.** Every global maximum having at most two active tasks is pure,
for arbitrary ambient `M`. In particular, if `M=2`, every maximum is pure
for every positive `t,τ` and every `N`.

One active task is settled by full budgets. For two, (4) leaves at most
one fractional row. Suppose it exists and `N≥2`; every other row is pure.
If both active columns contain pure rows, each fractional entry has a
smaller exponential weight than a unit entry in its column. Thus its
weight is `p<1/2`, and, since `h>0`, its scalar inner curvature is

\[
 tp[1+(1-2p)h]>0.
\]

Otherwise one active column contains only the fractional row's entry
`b∈(0,1)`, and all other `N−1` agents serve the other task. Write `z=tb`.
The fractional entry `1−b` in that other column has weight

\[
 q=\frac1{1+(N-1)e^z}<\frac12,
 \qquad S_{\rm other}=1-qb,
 \qquad h_{\rm other}=1-z(1-q)>0.
\]

Therefore `z<1/(1−q)<2`. In the private column,
`p=e^z/(e^z+N−1)` and `h=1+z(1−p)`, so its scalar curvature is

\[
 tp(1-p)[2-z(2p-1)]>0.
\]

The other column's curvature is positive because `q<1/2` and
`h_other>0`. In either case both inner curvatures are positive; (2)
then contradicts maximality along the row transfer. The one-agent case
was settled above. Inactive ambient columns have zero score variation
and do not affect the argument.

This result concerns the actual support of a global maximum. A pure solver
returning two groups does not establish that every competing continuous
maximum also uses at most two tasks. For `M=2`, this also yields a direct
algorithmic consequence.

**Corollary.** At every positive `t,τ`, the two-task continuous optimum is
the largest reward among the `⌊N/2⌋+1` unlabeled occupancies

\[
 (N),\qquad (N-m,m),\quad 1\le m\le\lfloor N/2\rfloor.
\]

Set `s_m=m e^t/(m e^t+N−m)` for `0≤m≤N`, so `s_0=0` and `s_N=1`.
The rewards are precisely

\[
 \frac{s_m e^{\tau s_m}+s_{N-m}e^{\tau s_{N-m}}}
      {e^{\tau s_m}+e^{\tau s_{N-m}}},
 \qquad 0\le m\le\lfloor N/2\rfloor.
 \tag{6}
\]

The `m=0` case includes the empty task's denominator weight and gives
concentration. Every pure assignment has one listed pair of occupancies,
and the purity theorem excludes any better fractional assignment, proving
the corollary. After the score/exponential weights are supplied, evaluating
this list and retaining its largest reward takes `O(N)` arithmetic and
comparison operations. This does not identify which pattern wins without
performing the comparisons, or give a bit-complexity bound for arbitrary
real temperatures. Finite enumeration is classical; the structural
reduction is the candidate model-specific contribution.

## A larger inner-temperature region

For `N≥2`, define `κ_N` as the unique root greater than two of

\[
 (\kappa_N-2)e^{\kappa_N}=(N-1)(\kappa_N+2).
 \tag{7}
\]

This symbol differs from the `c_n` used in the
[spread-order theorem](sharp-softmax-spread.md).

**Theorem.** Every global maximum is pure whenever `0<t≤κ_N`, for
arbitrary `M` and `τ>0`. The endpoint is included.

Consider a positive entry `a∈(0,1)` of a hypothetical fractional maximizing
row. If its weight satisfies `p≤1/2`, its positive `h` makes
`1+h−2ph>0`. If `p>1/2`, its value exceeds every other entry in the
column. Let `b` be the other entries' weighted mean and put `d=t(a−b)>0`.
Then

\[
 d\le ta,\qquad p\le\sigma(ta,N),\qquad
 h=1+(1-p)d,\qquad
 1+h-2ph=(1-p)[2-(2p-1)d].
\]

Define `ψ_N(z)=z[2σ(z,N)−1]`. It is nonpositive up to `log(N−1)` and
strictly increasing above it, since

\[
 \psi_N'(z)=2\sigma(z,N)-1
             +2z\sigma(z,N)[1-\sigma(z,N)]>0.
\]

It tends to infinity and has a unique level-two root, namely (7).
That root exceeds two because `σ(2,N)<1`. The majority-weight case
implies `ta>log(N−1)`. Since `a<1` and `t≤κ_N`,

\[
 (2p-1)d\le\psi_N(ta)<\psi_N(\kappa_N)=2.
\]

Thus every moved coordinate of the fractional row has strictly positive
inner curvature, including at `t=κ_N`. Equation (2) excludes the row.

This proof strengthens the earlier `t≤2` sufficient condition. It concerns
active entries at maxima, where `h>0`; it does not assert global coordinate
convexity of the Boltzmann mean on its whole input cube.

## A feasible reward can certify purity

Let `R_*` be the unrestricted continuous optimum. Suppose a certified
bound `r₀∈[0,1]` satisfies `r₀≤R_*`, for example because a feasible
allocation has certified reward at least `r₀`. Put

\[
 G=1+\tau(1-r_0).
\]

**Theorem.** Every global maximum is pure if

\[
 \boxed{t\le4\tau\left(1+\frac1G\right)}.
 \tag{8}
\]

Equality is included. The witness used for `r₀` need not be optimal or
pure, and its lower-bound status need not rely on any purity theorem.

For `N≥2`, suppose a fractional global maximum exists. Since `R≥r₀`
and every score is at most one, its active factors satisfy
`0<g_j≤G`. Let `β=(τ/t)(1+1/G)`. By (8), `β≥1/4`. Each bracket of
(3), divided by `t`, is at least

\[
 \begin{aligned}
 1+\frac1h-2p+\beta ph
 &=(1-p)\left(1+\frac1h\right)
   +p\left(-1+\frac1h+\beta h\right)>0.
 \end{aligned}
\]

The first term is strictly positive because `0<p<1` at finite temperature
when `N≥2`; the second is nonnegative by
`1/h+βh≥2√β≥1`. This contradicts (3), including at equality in (8).
The `N=1` and `M=1` cases are already pure without this condition.

Concentration is always feasible and gives `r₀=σ(τ,M)`. Therefore

\[
 t\le4\tau\left(1+
   \frac1{1+\tau[1-\sigma(\tau,M)]}\right)
 \tag{9}
\]

is an explicit sufficient condition. For fixed `M≥2`, its right side is
strictly below `8τ` at finite `τ` and its ratio to `τ` tends to eight as
`τ→∞`. Thus this boundary approaches `τ/t=1/8` from the sufficient side;
it does not include the finite line `τ=t/8` through this criterion.
For `M=1`, `σ=1` makes (9) exactly `t≤8τ`, but that case is independently
pure at every positive pair.

The weaker choice `r₀=0` already gives the dimension-independent condition

\[
 t\le\frac{4\tau(\tau+2)}{\tau+1},
 \qquad\text{equivalently}\qquad
 \tau\ge\frac{t-8+\sqrt{t^2+64}}8.
 \tag{10}
\]

Both (9) and (10) enlarge the previous `τ≥t/4` sufficient region.
Increasing any valid `r₀` strengthens (8). None is asserted to give the
sharp purity boundary.

### Implemented solver certificates

The [occupancy solver](certified-softmax-partitions.md) returns a certified
lower bound for a feasible pure witness, even when its optimum upper bound
is limited to the pure class. That lower bound is valid for `R_*` without
assuming purity. Contract `algal.lab.softmax-partition.v2` substitutes it
for `r₀` in (8). The rational comparison is equivalently

\[
 tG\le4\tau(G+1).
\]

If it succeeds, every continuous maximizer is pure, so the computed pure
optimum interval and witness regret bound apply to the continuous problem.
The output records `purityCertificate.basis="feasible-reward"`, the actual
certified witness lower bound, `G`, and the resulting certified inner limit.
Failure of this test establishes no difference between the two optima.

The dimension-dependent test uses an outward upper bound `E⁺≥e^t`.
For `t>2`, the exact rational inequality
`(t−2)E⁺≤(N−1)(t+2)` certifies `t≤κ_N`; an inconclusive enclosure supplies
no certificate. Degenerate dimensions, two tasks and the earlier region
have their own recorded reasons. If none succeeds, the upper bound remains
`pure-only`. Having a two-group witness when `M>2` is never used to infer
that all competitors use only two active tasks.

For exactly two tasks, the solver scans the list in (6). The largest
candidate upper endpoint bounds the global optimum. The candidate with
largest lower endpoint supplies a witness, and the difference certifies
its additive regret. Precision is refined until that gap is at most the
requested epsilon or a declared cap is reached. This path makes no DP
queries and reports how many occupancy evaluations it performed, including
repeated scans at finer precision. The implementation uses at most four
precision passes; each considers exactly `⌊N/2⌋+1` occupancies.

Version 2 adds the purity certificate and occupancy-evaluation fields and
extends the admitted continuous scope; earlier version-1 receipts retain
their original source identities. The input caps and the rule that a work
or precision failure returns no certificate remain in force. No benchmark
or new general enumeration algorithm is claimed.

## Reproduction and finite evidence

The bounded [support verifier](../research/spikes/stochastic/softmax_support.py)
uses exact fractions for its grid identities and high-precision Decimal
arithmetic for a separate cycle-curvature check:

```sh
python3 -m research.spikes.stochastic.softmax_support
python3 -m unittest research.test_softmax_partition
python3 -m research.softmax_partition --agents 128 --tasks 2 --inner 8 --outer 1/4 --epsilon 1/100000000
python3 -m research.softmax_partition --agents 8 --tasks 8 --inner 3 --outer 1/100 --epsilon 1/100000000
python3 -m research.softmax_partition --agents 9 --tasks 9 --inner 8 --outer 9/8 --epsilon 1/100000000
```

Three investigator-selected examples using contract v2 give the following
certificates. These are theorem demonstrations, with no model calls,
holdout selection, uniqueness claim or timing comparison.

| Agents, tasks | Inner, outer temperature | Returned occupancy | Continuous guarantee | Certified additive regret |
|---|---|---|---|---|
| 128, 2 | 8, 1/4 | (64,64) | Two-task purity; 65 occupancy evaluations, zero DP queries | `3/4294967296 < 10⁻⁸` |
| 8, 8 | 3, 1/100 | Eight singletons | Dimension-dependent inner threshold | `< 10⁻⁸` |
| 9, 9 | 8, 9/8 | Nine singletons | Feasible-witness reward criterion | `< 10⁻⁸` |

All three lie outside the earlier sufficient region `t≤2` or `τ≥t/4`.
The middle example also has a paired scope test: at `N=M=4` with the
same temperatures, none of the implemented sufficient tests succeeds, so
the solver correctly retains `pure-only` scope. This is an inconclusive
certificate, not evidence that a fractional allocation wins there.

The verifier checks 180 exact inner-consolidation cases, 110 outer
consolidations with certified active signs, 18 two-task fixtures with both
active inner factors positive, 75 bracket decompositions and nine feasible
reward boundary identities. It separately reports 76 outer cases and
144 two-task cases whose sign premises were not certified; no conclusion
is inferred for those excluded cases. Exact Taylor bounds prove the
logarithm enclosure used in the rational fixtures. Seventy-two actual
nested-Boltzmann cycle examples compare finite second differences with the
derived positive curvature at 85-digit precision. These finite checks
corroborate the analytic proofs and do not establish them universally.

The exploratory optimizer search retained 1,920 starts across 160 cases,
including one optimizer nonconvergence. It found no above-pure result
beyond numerical tolerance. That absence supplies no purity proof and is
not used by the executable's certificate. The preliminary all-temperature
coordinate-convexity idea failed even for two agents; the limited
maximum-point threshold (7) is the proved replacement.

## Classical ingredients and remaining priority

The graph argument uses a familiar cycle direction. In the standard
transportation polytope, with both row and column margins fixed, a matrix
is a vertex exactly when its bipartite support is a forest. The inspected
source is Jesús De Loera's author-hosted
[Transportation Polytopes: a Twenty Year Update](https://www.math.ucdavis.edu/~deloera/TALKS/20yearsafter.pdf),
particularly slides 4 and 13. These slides state the classical criterion;
they are not its original publication. Bolker's 1972 work was identified
bibliographically, but its original theorem passage was not retrieved.

That criterion does not itself prove the result here. Column sums are not
constraints of this allocation model, and the scaled direction
`U_ij=V_ij/λ_i` need not preserve them. The additional argument is the
maximum-point derivative factorization, cancellation of all first score
variations, and strictly positive second variation. The conclusion concerns
every nonlinear global maximizer, not merely vertices of a fixed-margin
polytope. No new general graph theorem is claimed.

Shapley–Folkman results provide another important comparison. The inspected
primary research source is Dubois-Taine and d'Aspremont,
[Frank-Wolfe meets Shapley-Folkman, v3](https://arxiv.org/html/2406.18282v3):
problem (P), Assumption 1.1, Theorem 2.4, Lemma 2.2, Theorem 2.5 and
Proposition 3.1 were examined. They treat a separable objective under affine
coupling and give representations with a dimension-bounded number of
convexified components, together with appropriate existence, reconstruction
or duality-gap conclusions. The algorithmic support bound in Proposition
3.1 concerns a constructed representation.

Our nested objective is not separable in the rows with affine coupling
alone; introducing task scores adds nonlinear score-link constraints.
The cited statements also do not assert a support forest for every global
maximizer. This explains why those formulations do not directly imply the
present result, while leaving possible other formulations and closer
nonlinear-allocation results open. The 1969 Starr original was
bibliographically identified, but its PDF/theorem proof was not fully read
in this audit; the precise Shapley–Folkman comparison uses the inspected
v3 research paper.

The general occupancy solver continues to use classical fractional
optimization; its two-task specialization uses direct finite enumeration. [Megiddo's 1979 original, Section 2](https://theory.stanford.edu/~megiddo/pdf/rational.pdf)
covers positive-denominator affine ratios optimized through additive
combinatorial oracles. The inspected scope included the abstract,
introduction, complete Section 2 theorem/proof, Sections 4–5 and references.
The publisher abstracts of Dinkelbach (1967) and Jagannathan (1966) were
also read, with Dinkelbach crediting the earlier parametric equivalence;
their article bodies remain unread. The
[solver note](certified-softmax-partitions.md#prior-art-and-remaining-priority)
records the links and algorithmic attribution. Neither a new fractional
optimization mechanism nor a new dynamic-programming recurrence is claimed.

For the exact allocation model, the inspected softmax model,
Theorems 3.1–3.4 and Appendix G.4 of
[Amir–Bettini–Prorok v4](https://arxiv.org/html/2506.09434v4)
supply endpoint lower bounds without these structural reductions. This is
a bounded comparison to those passages, not a literature-wide absence
claim. The [novelty ledger](novelty-ledger.md) retains broader priority gaps.
The complete private-task consolidation statement and the enlarged purity
conditions still need their own wider source comparisons.

All mathematical conclusions above follow from the displayed proofs and
the linked maximum-point lemmas. Finite optimizer searches, their absence
of counterexamples, model capability or token expenditure establish none
of these theorems and no first-priority claim. The remaining mathematical
question is whether a global maximizer with three or more active tasks
can have a fractional tree support outside the sufficient regions.
