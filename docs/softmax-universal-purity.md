# Universal purity in nested Boltzmann allocation

For every finite positive inner and outer temperature, every globally
optimal allocation assigns each agent's entire unit of effort to one task.
This holds for every finite number of agents and tasks, including all ties.
The continuous optimization problem therefore reduces exactly to a finite
optimization over integer task occupancies.

The proof combines the established support and dominance lemmas with a
path between two private task leaves. A suitable transfer along that path
preserves every row budget and cancels every internal task's first score
variation. Its second reward derivative is strictly positive, excluding
the proposed fractional maximum. No temperature ratio or numerical search
enters the argument. Wider literature priority for the model-specific
conclusion remains open.

## Model and theorem

Let `N,M≥1` be integers and let `t,τ>0` be finite. A feasible allocation
is a nonnegative matrix `A=(a_ij)` with `Σ_j a_ij≤1` for each row. Define

\[
 B_c(x)=\frac{\sum_i x_i e^{cx_i}}{\sum_i e^{cx_i}},\qquad
 S_j=B_t(A_{:j}),\qquad R(A)=B_\tau(S).
 \tag{1}
\]

Every inner denominator includes all `N` rows, including zero entries.
The outer denominator includes all `M` tasks, including tasks with zero
score. A row is **pure** when it has exactly one unit entry; an allocation
is pure when all its rows are pure.

**Theorem.** Every global maximizer of (1) is pure. Equivalently,

\[
 A\in\operatorname*{arg\,max}_{\substack{a_{ij}\ge0\\
                                  \sum_j a_{ij}\le1}}R(A)
 \quad\Longrightarrow\quad
 a_{ij}\in\{0,1\},\qquad \sum_j a_{ij}=1\quad\text{for every }i.
 \tag{2}
\]

The feasible set is compact, and the finite-temperature objective is
smooth with strictly positive denominators, so a global maximum exists.
The assertion concerns every maximizer: a fractional allocation cannot
tie an optimal pure allocation.

## Dependency lemmas and their order

The following results were proved separately for all finite `t,τ>0`.
Their proofs do not assume (2).

| Result | Precise premise used here | Proof |
|---|---|---|
| Budget exhaustion and derivative signs | Every maximizing row sums to one; active outer derivatives and supported inner derivative factors are positive. | [Budget and sign lemmas](softmax-integral-optima.md#every-positive-temperature-optimum-uses-full-budgets) |
| Support forest | The bipartite graph of positive allocation entries has no cycle. | [Cycle perturbation](softmax-support-structure.md#every-maximizing-support-is-a-forest) |
| Private-task consolidation | A maximizing row cannot own two tasks that have no other positive contributor. | [Strict consolidation](softmax-support-structure.md#no-row-serves-two-private-tasks) |
| No mixing of row types | An active task cannot contain both a pure row and a fractional row. | [Dominance exclusion](softmax-dominance.md#a-larger-contribution-cannot-dominate-a-supported-pair) and its [component consequence](softmax-dominance.md#pure-and-fractional-rows-occupy-separate-components) |

The budget and sign proof uses feasible one-sided decreases and an endpoint
improvement for a zero row. Row stationarity then follows from two-sided
transfers between positive entries. The forest proof applies a separate
cycle direction. The private-task proof makes a strict finite consolidation.
The dominance proof uses the exponential tangent inequality and a
two-entry curvature contradiction; it needs no previously established
purity region.

Only these lemmas enter the path argument. The temperature-dependent
purity conditions, two-agent and three-task classifications, and all-agent
star exclusion are not prerequisites. This order prevents a circular
appeal to those consequences or to the universal conclusion.

## Derivatives at a proposed maximum

Fix a global maximizer `A`. Use the notation

\[
 p_{ij}=\frac{e^{ta_{ij}}}{\sum_l e^{ta_{lj}}},\qquad
 h_{ij}=1+t(a_{ij}-S_j),
\]
\[
 P_j=\frac{e^{\tau S_j}}{\sum_l e^{\tau S_l}},\qquad
 g_j=1+\tau(S_j-R),\qquad W_j=P_jg_j.
 \tag{3}
\]

The sign lemmas give `W_j>0` on every active task and `h_ij>0` at every
positive entry. For each row, equality of its positive-support allocation
derivatives gives a common multiplier

\[
 W_jp_{ij}h_{ij}=\lambda_i>0\qquad(a_{ij}>0).
 \tag{4}
\]

All multipliers below are fixed at this matrix when defining a direction.
No derivative sign at an allocation entry equal to zero is required.

For a single Boltzmann mean, put `p_i=e^(cx_i)/Σ_l e^(cx_l)` and
`h_i=1+c(x_i−B_c(x))`. The elementary
[derivative identities](softmax-integral-optima.md#derivative-identities)
give

\[
 D^2B_c(x)[u,u]
 =c\sum_i p_i(1+h_i)u_i^2
   -2c\left(\sum_i p_i u_i\right)DB_c(x)[u],
 \tag{5}
\]
\[
 \partial_i^2B_c=cp_i(1+h_i-2p_ih_i).
 \tag{6}
\]

These identities apply to the full vectors, including all zero entries.
In particular, cancelling a column's first score variation cancels the
entire mixed term in (5).

## A fractional component supplies a private-leaf path

Suppose some row of `A` is fractional. Full budgets make its support
degree at least two. The no-mixing lemma implies that its connected
support component contains only fractional rows, all of degree at least
two. The forest lemma makes this component a finite tree.

Every finite nontrivial tree has at least two leaves. None here can be a
row vertex, so choose two task leaves. A task leaf is private in the
original allocation, since its degree is one in the whole support graph.
Their owners are distinct by the private-task consolidation lemma.
Their unique path is therefore

\[
 j_0-i_1-j_1-i_2-\cdots-i_L-j_L,\qquad L\ge2.
 \tag{7}
\]

Internal tasks may have other positive contributors off this path, and
path rows may serve other tasks. All those entries will remain fixed.

For each `r=1,…,L`, define

\[
 U_{i_r,j_{r-1}}=\frac1{\lambda_{i_r}},\qquad
 U_{i_r,j_r}=-\frac1{\lambda_{i_r}},
 \tag{8}
\]

and set all other entries of `U` to zero. Every row sum of `U` vanishes.
Every changed entry of `A` is positive. Thus `A+sU` is feasible for both
signs of `s` whenever

\[
 |s|<\min_{(i,j):\,U_{ij}\ne0} a_{ij}\lambda_i.
 \tag{9}
\]

This is a two-sided feasible line in the original problem.

Let `v_j=DS_j[U_:j]`. At an internal task `j_r`, (4) gives

\[
 v_{j_r}
 =-\frac{p_{i_rj_r}h_{i_rj_r}}{\lambda_{i_r}}
   +\frac{p_{i_{r+1}j_r}h_{i_{r+1}j_r}}{\lambda_{i_{r+1}}}
 =-\frac1{W_{j_r}}+\frac1{W_{j_r}}=0.
 \tag{10}
\]

At the endpoints,

\[
 v_{j_0}=\frac1{W_{j_0}},\qquad
 v_{j_L}=-\frac1{W_{j_L}}.
 \tag{11}
\]

All other task variations vanish. Consequently

\[
 DR(A)[U]=DB_\tau(S)[v]=\sum_j W_jv_j=0.
 \tag{12}
\]

## Positive curvature after pairing contributions by row

For an internal task, (10) cancels the mixed term of its inner Hessian.
Its weighted contribution from (5) is exactly

\[
 W_jD^2S_j[U_{:j},U_{:j}]
 =t\sum_{i:\,U_{ij}\ne0}
       \lambda_i\left(1+\frac1{h_{ij}}\right)U_{ij}^2.
 \tag{13}
\]

Each term is strictly greater than `tλ_i U_ij²`. This decomposition is
made after cancelling the complete column mixed term; it does not discard
cross terms between its two moving entries.

At a private endpoint only its owner's entry varies. Equation (6) retains
that scalar curvature in full:

\[
 W_jD^2S_j[U_{:j},U_{:j}]
 =t\lambda_i\left(1+\frac1{h_{ij}}-2p_{ij}\right)U_{ij}^2
 >-t\lambda_i U_{ij}^2.
 \tag{14}
\]

Here `h_ij>0` and `p_ij<1`, since the hypothetical component has at least
two rows and the temperatures are finite. Private scores may have negative
curvature; (14) bounds its magnitude.

Now group (13) and (14) by row. Each endpoint owner has one private edge
and one internal-task edge along the path, with equal direction magnitude
`1/λ_i`. Their sum is

\[
 \frac{t}{\lambda_i}
 \left(2+\frac1{h_{i,\mathrm{private}}}
          +\frac1{h_{i,\mathrm{internal}}}
          -2p_{i,\mathrm{private}}\right)>0.
 \tag{15}
\]

Each intervening row has two internal-task edges, both contributing
positively. The private endpoints have different owners, so no row is
left with two private terms and no internal term. Therefore

\[
 \sum_j W_jD^2S_j[U_{:j},U_{:j}]>0.
 \tag{16}
\]

This pairing includes `L=2`: the single shared task supplies one positive
term to each of its two path rows, even when there are other agents whose
entries in these columns are zero.

The nested chain rule gives

\[
 D^2R(A)[U,U]
 =\sum_j W_jD^2S_j[U_{:j},U_{:j}]+D^2B_\tau(S)[v,v].
 \tag{17}
\]

Equation (12) cancels the outer mixed term in (5). Only the two active
endpoint scores move, and their factors `g_j` are positive, so

\[
 D^2B_\tau(S)[v,v]
 =\tau\sum_{j\in\{j_0,j_L\}}P_j(1+g_j)v_j^2>0.
 \tag{18}
\]

Equations (16)–(18) show `D²R(A)[U,U]>0`. A maximum on the feasible
two-sided line (9) requires a nonpositive second derivative. This
contradiction excludes the fractional component and proves (2).

For completeness, the boundary dimensions require no path. With `M=1`,
full budgets give the all-one column. With `N=1`, the scores are its row
entries. Each outer weight is at most
`σ(τ,M)=e^τ/(e^τ+M−1)`, whence
`R≤σ(τ,M)Σ_j a_1j≤σ(τ,M)`. For `M≥2`, equality requires one unit entry
and all others zero. Concentration attains this bound.

## Exact occupancy consequence

Let `π=(m₁,…,m_k)` be a partition of `N` into positive integer task
occupancies, with `k≤min(N,M)`. Put

\[
 s_m=\frac{m e^t}{m e^t+N-m}.
\]

A pure allocation with these occupancies has reward

\[
 R_\pi=
 \frac{\sum_{r=1}^k s_{m_r}e^{\tau s_{m_r}}}
      {M-k+\sum_{r=1}^k e^{\tau s_{m_r}}}.
 \tag{19}
\]

The theorem gives the unrestricted continuous optimum exactly:

\[
 \boxed{\max_A R(A)=\max_{\substack{\pi\vdash N\\
                                  |\pi|\le M}}R_\pi}.
 \tag{20}
\]

Every maximizing matrix is a labeled pure assignment realizing an optimal
occupancy partition, and every such assignment attains the maximum. This
describes all equality cases without asserting that the best partition
is unique.

The [certified occupancy solver](certified-softmax-partitions.md) uses
classical ratio-threshold optimization, exact-budget dynamic programming
and bounded direct enumeration. The universal theorem supplies the
continuous upper-bound justification throughout the positive-temperature
domain. Numerical work and precision caps still apply to the executable;
a finite additive-regret interval does not decide every exact tie between
transcendental rewards. No new enumeration, DP recurrence, interval method
or general bit-complexity result is claimed here.

## Scope and originality

The theorem covers every finite positive `t,τ` and every finite positive
`N,M` in the unit-budget model (1). It makes no assertion at zero, negative
or infinite temperatures, with unequal budgets, negative allocations or
different aggregation operators. It does not imply global convexity,
purity of all stationary points, optimality of every pure assignment or a
unique optimum.

The derivative identities, stationarity conditions, tree paths and
second-order necessary conditions are classical ingredients. The
model-specific contribution is the complete all-maximizer purity argument
and resulting continuous-to-occupancy reduction. The
[novelty ledger](novelty-ledger.md) records the inspected sources and
remaining priority comparisons; proof soundness alone does not establish
first priority.

The result has an analytic proof and independent mathematical review.
Finite numerical checks provide separate corroboration. No measured
model/token-efficiency comparison or cheap-model discovery experiment
accompanies it.

The independent review is retained at
`/private/tmp/algal-round21-universal-purity-review.md` (SHA-256
`d69f68b05126328e6b33bfa97ee174ea38416385ba96f61d16d334b183feabc5`) and
audits the proof source
`/private/tmp/algal-round21-embedded-pair.md` (SHA-256
`f7a8f515a5e4fe3150ebd1f9fe5dda56a45014f2df221cf6e807263b2b2fe91e`).
Those files are review evidence, not runtime inputs. The bounded source audit
and its access ledger remain in the local research archive; the ledger labels
the result as a candidate contribution rather than a priority claim.

## Appendix: why an embedded coordinate trace is insufficient

An embedded two-row component retains the other `N−2` zero entries in
each inner mean. If `c_i=p_i h_i` are its two active shared-task partials,
their sum need not equal one. The missing zero-entry partials still enter
the full translation identity. Consequently the trace proof for an
entire-population star cannot be transferred by deleting external rows.

For example, let `N=2^32+2`, `u=4(N−1)`, `v=2(N−2)` and
`t=log u+log v`. Give each of two rows private effort `a=log u/t` and
shared effort `x=log v/t=1−a`. The private weight is `4/5`, each active
shared weight is `2/5`, and

\[
 h_{\rm private}=1+\frac{\log u}{5},\qquad
 h_{\rm shared}=1+\frac{\log v}{5}.
\]

Set `c=(2/5)h_shared`, let `T_active` be the sum of the two active shared
scalar curvatures, and put `L_N(a)=q_N''(a)/q_N'(a)` for
`q_N(a)=a e^(ta)/(e^(ta)+N−1)`. The inner trace expression obtained by
formally substituting row stationarity is

\[
 \frac{T_{\rm active}+2cL_N(a)}{2ct}
 =-\frac25+\frac1{h_{\rm private}}+\frac1{h_{\rm shared}}
 <-\frac{382}{11205}<0.
\]

The bound uses `log 2>2/3`, giving `h_private>83/15` and
`h_shared>27/5`. This refutes positivity of that inner trace under only
the support, active-inner-sign and dominance premises. It is not an actual
maximizing stationary allocation: its private score is larger than its
shared score, while the positive-outer-derivative stationarity equations
would require the opposite derivative ordering. It supplies no fractional
optimum. The path proof instead uses the full-population derivatives and
an explicit direction with positive curvature.
