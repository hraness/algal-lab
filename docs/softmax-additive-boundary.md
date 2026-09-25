# Exact concave envelope and additive Boltzmann allocation

The softmax-weighted mean has an explicit least concave majorant on the unit
cube. When there are at least two coordinates and the temperature is positive,
the majorant touches the smooth function only at binary vectors. This gives
the exact rectangular task-allocation optimum at zero outer temperature:
assign whole agents to tasks and balance their occupancies.

The same envelope supplies a stronger [flow reduction](softmax-additive-flow.md)
with task weights, task-specific temperatures, eligibility restrictions,
integer task capacities, and linear assignment rewards. The probability-ratio
bound, concave-cardinality closure, and flow machinery are established
ingredients. The candidate contribution is their exact application to this
nonlinear allocation objective, including all equality cases; worldwide
literature priority remains unresolved.

## One-column theorem

Fix an integer `N≥1` and a finite real `t>0`. For `x∈[0,1]^N`, define

\[
 f_t(x)=\frac{\sum_i x_i e^{t x_i}}{\sum_i e^{t x_i}},\qquad
 E=e^t,\qquad s_k=\frac{kE}{N+k(E-1)},\quad 0\le k\le N.
 \tag{1}
\]

Let `φ` be the polygonal interpolation of `(k,s_k)`. Its consecutive slopes

\[
 d_k=s_{k+1}-s_k=
 \frac{EN}{(N+k(E-1))(N+(k+1)(E-1))},\quad 0\le k<N,
 \tag{2}
\]

are positive and strictly decreasing when there is more than one slope.
Thus `φ` is increasing and concave.

**Envelope theorem.** The least concave majorant of `f_t` on the cube is

\[
 H_t(x)=\phi\left(\sum_i x_i\right).
 \tag{3}
\]

For `N≥2`, equality `f_t(x)=H_t(x)` holds exactly at binary vectors. For
`N=1`, both functions equal `x_1` everywhere.

### Subset-mass bound

Put `p_i=e^(t x_i)/Σ_l e^(t x_l)`. For a nonempty proper subset `L` of
size `k`, every cross ratio satisfies `p_i≤E p_j` for `i∈L,j∉L`.
Summing these inequalities gives

\[
 (N-k)P(L)\le kE(1-P(L)),\qquad P(L)\le s_k.
 \tag{4}
\]

Equality requires equality of every cross ratio. Within the unit cube,
`x_i-x_j=1` then forces `x=1_L`. In particular, every proper subset bound
in (4) is strict at every `x` other than `1_L`.

Order the coordinates so that `p_1≥⋯≥p_N`, let `P_k=Σ_{i≤k} p_i`, and
write `S=Σ_i x_i=k+r`, `0≤r<1`, for `S<N`. By (4), `P_k≤s_k` for
`1≤k≤N-1`. Maximizing a fixed linear form
`p·y` over `0≤y_i≤1,Σ_i y_i=S` fills the largest weights first. Therefore

\[
 f_t(x)=p\cdot x
 \le \sum_{i=1}^k p_i+r p_{k+1}
 =(1-r)P_k+rP_{k+1}
 \le (1-r)s_k+r s_{k+1}=\phi(S),
 \tag{5}
\]

where `P_0=s_0=0` and `P_N=s_N=1`. When `x` is nonbinary, `0<S<N`, and a
positive coefficient multiplies a proper subset bound in (5): if `k=0`,
then `r=S>0` multiplies `P_1≤s_1`, and `{1}` is proper because `N≥2`; if
`1≤k≤N-1`, then `1-r>0` multiplies `P_k≤s_k`. Either bound is strict by
(4), since a nonbinary `x` is not of the form `1_L`. Binary points give
equality. The endpoint `S=N`
is the all-one vector. This proves the upper bound and its exact contact set
without any convexity or coordinate-monotonicity assumption on `f_t`.

### Leastness of the majorant

Every vertex of the slab
`Q_k={x∈[0,1]^N:k≤Σ_i x_i≤k+1}` is binary. Two fractional coordinates
allow a small sum-preserving transfer. With exactly one fractional coordinate,
the sum cannot equal either integer boundary, so that coordinate can move in
both directions. Neither case is a vertex.

Consequently each `x∈Q_k` is a convex combination of binary vectors of
cardinality `k` or `k+1`. Any concave majorant `G` of `f_t` must satisfy

\[
 G(x)\ge\sum_v\alpha_v G(v)
 \ge\sum_v\alpha_v s_{|v|}=\phi(S)=H_t(x).
 \tag{6}
\]

The last equality uses `Σ_v α_v |v|=S` and linearity of `φ` on that slab.
Since (5) already proves that the concave `H_t` majorizes `f_t`, it is the
least such function.

### Arbitrary coordinate prices

For any real vector `λ`, not only a uniform nonnegative price,

\[
 \max_{x\in[0,1]^N}\{f_t(x)-\lambda\cdot x\}
 =\max_{L\subseteq\{1,\ldots,N\}}
   \left\{s_{|L|}-\sum_{i\in L}\lambda_i\right\}.
 \tag{7}
\]

Indeed, the slab decomposition makes `H_t(x)-λ·x` an average of binary
values. It cannot exceed their maximum; `f_t≤H_t` supplies the other step.
For `N≥2`, every maximizer of (7) is binary because (5) is strict otherwise.
This strengthens the earlier uniform-price derivation, but follows from the
same standard subset-probability geometry.

## Rectangular allocation at zero outer temperature

Let `A` be a nonnegative `N×M` matrix, with finite positive integers `N,M`
and row sums at most one. At outer temperature zero the reward is

\[
 R_0(A)=\frac1M\sum_j f_t(A_{:j}).
 \tag{8}
\]

Write `N=qM+r`, `0≤r<M`. If `N≥2`, every maximizer is pure, uses all
row budgets, and has occupancy `q+1` on `r` tasks and `q` on the others.
Its value is

\[
 \max_A R_0(A)=\frac{(M-r)s_q+r s_{q+1}}M.
 \tag{9}
\]

When `r=0`, the `s_(q+1)` term has coefficient zero; for `M=1` it is
undefined and omitted, giving the all-one column and value one.

For a proof, put `S_j=Σ_i a_ij`. The envelope, Jensen's inequality, and
the increasing property of `φ` give

\[
 R_0(A)\le\frac1M\sum_j\phi(S_j)
 \le\phi\left(\frac1M\sum_j S_j\right)
 \le\phi(N/M).
 \tag{10}
\]

A pure balanced assignment attains this value. Equality requires total effort
`N` and binary columns, so every row has one unit entry. If integer column
counts satisfy `n_a≤n_b-2`, moving one agent from `b` to `a` improves the
sum by `d_(n_a)-d_(n_b-1)>0`. Thus the balanced assignments are exactly
all maximizers.

For `N=1`, every full-budget row ties at `1/M`; fractional maximizers occur
when `M≥2`. For `t=0`, the objective is total effort divided by `NM`, so
every full-budget allocation ties at `1/M`. These exceptions explain why the
strict theorem requires both `N≥2` and `t>0`.

## A known extremal constant reappears

The elementary covariance identity gives `f_t(x)≥S/N`, with equality exactly
when all coordinates are equal. Consequently the exact envelope gap is

\[
 \max_x(H_t(x)-f_t(x))
 =\max_{0\le k\le N}\left(s_k-\frac{k}{N}\right).
 \tag{11}
\]

The covariance step gives `H_t(x)-f_t(x)≤φ(S)-S/N` for `S∈[0,N]`. Since
`φ(S)-S/N` is piecewise linear with integer breakpoints, its maximum over
`[0,N]` is attained at an integer. To see attainment, use a constant vector
of total mass `k` at a maximizing integer. All gap maximizers are constant vectors whose total mass maximizes
`φ(S)-S/N`; an adjacent integer tie gives the entire interval between them.

This constant is already a specialization of the fixed-base Hilbert-distance
bound of [Cohen and Fausti, Lemma 5.2, equation (41)](https://arxiv.org/html/2309.02413v2#S5.SS1).
With uniform base probabilities and exponential tilting, their subset masses
are `k/N`; half of their `ℓ¹` bound produces (11). Their Theorem 5.1 and
its proof give the ceiling
`tanh(t/4)` and maximizing continuous mass fraction `1/(1+e^(t/2))`.
Those constants are prior art. Here they also describe the smooth mean's
concavification gap through (3).

## Reproducible checks

```sh
python3 -m unittest research.test_softmax_additive_boundary
```

The independent Decimal checker imports no solver or interval helpers. It
checks strict pointwise gaps on a tenth grid for `N=2…5`, decreasing slopes,
balanced occupancies through `N=12,M=7`, and explicit `N=1` and `t=0`
boundaries. These finite checks support the analytic proof and do not replace
it. The flow sequel adds exact optimization and independent certificates.

## Prior art and claim boundary

[Amir, Bettini and Prorok, v4](https://arxiv.org/html/2506.09434v4), Section 3
and Appendix G.4, use this nested Boltzmann model and give square-population
lower bounds. The inspected passages do not give (3), its strict contact set,
or the rectangular equality classification (9). The older repository
[task-allocation note](softmax-task-allocation.md) already proves the square
`N=M,τ≤0` case.

The probability-ratio geometry is established: Cohen–Fausti Section 4
characterizes Hilbert balls by ratio constraints, and (4) follows directly by
summing those constraints. Cardinality concavity and concave closure are
standard; see [Shioura (2009)](https://www.dais.is.tohoku.ac.jp/~shioura/papers/dmaa09.pdf),
Example 2.8 and Theorems 2.10–2.11. Formula (6) gives the elementary slab
specialization. Neither that geometry, the price-value mechanism, integer
balancing, nor the constant (11) is advertised as new machinery.

The exact smooth-function envelope/contact identification and nonlinear
allocation application were not located in this bounded source packet. The
1989 Esscher-order original and broader allocation comparisons remain gaps;
no worldwide first-priority assertion follows. The envelope proof is also
independent of the [positive-outer-temperature purity theorem](softmax-universal-purity.md).
