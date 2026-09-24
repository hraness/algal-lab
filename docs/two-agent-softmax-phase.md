# Exact softmax allocation with two agents and any number of tasks

Two agents never need to split their effort at a positive-temperature
optimum, regardless of the number of available tasks. Every maximizing
allocation assigns each agent's full unit to one task. The exact continuous
optimum is therefore the larger of two explicit rewards: concentrating
both agents or assigning them different tasks.

There is one transition between these choices. With two tasks it occurs
at equal inner and outer temperatures. With more tasks it occurs strictly
above the matched-temperature line. Consequently, two agents and three
tasks already have a positive matched-temperature heterogeneity gain;
`1/150` is an exact rational lower bound for one example.

All temperatures in this note are **finite and strictly positive**. The
proof uses the [budget and derivative-sign lemmas](softmax-integral-optima.md)
and [support-structure theorems](softmax-support-structure.md). It extends
the earlier [two-agent square classification](softmax-specialization-boundaries.md)
to arbitrary task counts. Wider literature priority remains open.

## Model and exact classification

A feasible allocation is a nonnegative `2×M` matrix `A=(a_ij)` with each
row sum at most one, where `M≥1`. Let

\[
 B_c(x)=\frac{\sum_i x_i e^{cx_i}}{\sum_i e^{cx_i}},\qquad
 S_j=B_t(A_{:j}),\qquad R(A)=B_\tau(S),\qquad t,\tau>0.
\]

Write `R_het` for the maximum over all feasible matrices and `R_hom` for
the maximum over matrices with identical rows. A pure allocation has
exactly one unit entry in each row.

For `M=1`, the unique maximizing allocation gives both units to the only
task, and `R_het=R_hom=1`. For `M≥2`, put

\[
 E=e^t,\qquad b=\frac{E}{E+1},\qquad
 H=\frac{e^\tau}{e^\tau+M-1},\qquad
 D=\frac{2b e^{\tau b}}{2e^{\tau b}+M-2}.
 \tag{1}
\]

**Theorem.** Every global maximizer is pure, and

\[
 R_{\rm het}=\max\{H,D\},\qquad R_{\rm hom}=H,
 \qquad\Delta R=\max\{0,D-H\}.
 \tag{2}
\]

For fixed `t>0` and `M≥2`, there is a unique crossover `τ_*(t,M)>0`.
It equals `t` when `M=2`. When `M>2`,

\[
 t<\tau_*(t,M)<t+\log(M-1).
 \tag{3}
\]

Every equality case is included in the following classification. Counts
refer to labeled agents and tasks.

| Outer temperature | All maximizing allocations | Count |
|---|---|---:|
| `0<τ<τ_*` | The agents use different tasks | `M(M−1)` |
| `τ=τ_*` | Either separation or concentration | `M²` |
| `τ>τ_*` | Both agents use the same task | `M` |

No fractional allocation is optimal at the crossover.

## The only remaining fractional support

The linked positive-temperature lemmas establish, at every global maximum:
full row budgets, positive outer derivatives on active tasks, and positive
inner derivatives at positive allocation entries. Write these derivatives
as

\[
 \partial_j B_\tau(S)=W_j=P_jg_j>0,\qquad
 g_j=1+\tau(S_j-R),
\]

where `P_j=e^(τS_j)/Σ_l e^(τS_l)` includes **all** `M` tasks. The support
theorems also show that its bipartite graph is a forest, no row owns two
private tasks, at most `2N−1` tasks are active, and every maximum with at
most two active tasks is pure. A private task has only one positive entry.

Here `N=2`, so at most three tasks can be active. If three are active,
the support must be connected: otherwise each component has one row and
can contain only one task without violating the private-task restriction.
A connected forest on two row and three task vertices has four edges.
Neither row can have degree one, since the other would then own two
private tasks. Both have degree two. Up to task labels, the only possible
fractional support is thus

\[
 A=\begin{pmatrix}
 \alpha&1-\alpha&0&0&\cdots\\
 0&1-\beta&\beta&0&\cdots
 \end{pmatrix},\qquad 0<\alpha,\beta<1.
 \tag{4}
\]

The middle task is shared. The other `M−3` tasks retain score zero and
weight one in the outer denominator. We will rule out a maximum of (4)
by showing that its Hessian in the feasible local coordinates
`(α,β)` has positive trace.

For any single Boltzmann mean, put `p_i=e^(cx_i)/Σ_l e^(cx_l)` and
`h_i=1+c(x_i−B_c(x))`. Direct differentiation gives

\[
 D^2B_c(x)[v,v]
 =c\sum_i p_i(1+h_i)v_i^2
  -2c\left(\sum_i p_iv_i\right)DB_c(x)[v],\qquad
 \partial_i^2B_c=cp_i[1+h_i-2p_ih_i].
 \tag{5}
\]

Translation equivariance of the two-input mean implies that its first
partials sum to one and its Hessian is
`κ [[1,−1],[−1,1]]`, with the same `κ` on both diagonal entries.

## Two curvature bounds

A private task with effort `u` has score

\[
 q(u)=\frac{u e^{tu}}{1+e^{tu}}.
\]

With `z=tu≥0`, `p=e^z/(1+e^z)` and `h=1+z/(1+e^z)`, we have
`q′=ph>0` and, by (5),

\[
 L(u):=\frac{q''(u)}{q'(u)}
 =t\left(1+\frac1h-2p\right)>-\frac t4.
 \tag{6}
\]

To prove the last inequality, observe

\[
 1+e^z-3z\ge2-2z+\frac{z^2}{2}
              =\frac{(z-2)^2}{2}.
\]

The left side is strictly positive: the square is positive away from
`z=2`, and the exponential Taylor inequality is strict there. Hence
`z/(1+e^z)<1/3`, so `h<4/3` and `1/h>3/4`. Combining this with `p<1`
proves (6). Private scores can have negative curvature; this argument
bounds it without assuming convexity.

For the shared task, let `u=1−α`, `v=1−β`, let `p≤1/2` be its smaller
softmax weight, and put

\[
 \delta=t|u-v|=\log\frac{1-p}{p}.
\]

The derivative factor at the smaller entry is
`h_small=1−δ(1−p)>0`. It forces `p>1/5`: otherwise

\[
 \delta(1-p)\ge\frac45\log4>\frac{16}{15}>1,
\]

using `log 2>2/3`, which follows from the strict midpoint integral bound
for the convex function `1/x` on `[1,2]`. Formula (5) therefore gives

\[
 \kappa=tp[1+(1-2p)h_{\rm small}]
         \ge tp>\frac t5.
 \tag{7}
\]

Equal shared entries are included: then `p=1/2` and `κ=t/2`.
The constants in (6) and (7) are coarse sufficient bounds, not claimed
optimal constants.

## Positive trace excludes the fractional path

Let `c,d>0` be the first partial derivatives of the shared two-input mean,
so `c+d=1`. Denote the outer derivatives at the left private, shared and
right private tasks by `W_1,W_s,W_2>0`. At a maximum of (4), stationarity
in the two independent coordinates gives

\[
 W_1q'(\alpha)=W_sc,\qquad W_2q'(\beta)=W_sd.
 \tag{8}
\]

The inner part of the Hessian trace is consequently

\[
 \begin{aligned}
 W_1q''(\alpha)+W_2q''(\beta)+2W_s\kappa
 &=W_s[cL(\alpha)+dL(\beta)+2\kappa]\\
 &>\frac3{20}tW_s>0,
 \end{aligned}
 \tag{9}
\]

by (6), (7) and `c+d=1`.

The score-direction vectors for the two coordinate directions are

\[
 v^{(\alpha)}=(q'(\alpha),-c,0,0,\ldots),\qquad
 v^{(\beta)}=(0,-d,q'(\beta),0,\ldots).
\]

Equation (8) makes `DB_τ(S)[v]=0` for each vector. Thus (5) reduces each
outer Hessian contribution to

\[
 \tau\sum_j P_j(1+g_j)v_j^2>0.
 \tag{10}
\]

Every moved task is active and has `g_j>0`. Unused tasks have zero score
variation, although their weights remain in `P_j` and their scores in
`R`. Both direction vectors are nonzero.

Equations (9) and (10) make the full trace strictly positive. Both
coordinate perturbations are feasible with either sign near (4), whereas
a maximum requires both diagonal second derivatives, and hence their sum,
to be nonpositive. This contradiction eliminates the only remaining
fractional support. Every two-agent maximum is pure for every `M`.

## Evaluating the pure allocations

For `M≥2`, the only pure score patterns are `(1,0,…,0)` and
`(b,b,0,…,0)`, giving exactly `H` and `D` in (1). All empty-task weights
are retained. Purity therefore proves the unrestricted upper bound and
all equality cases in (2).

For a homogeneous allocation, each score equals its common row entry
`r_j`. Each outer weight is at most
`σ(τ,M)=e^τ/(e^τ+M−1)`, because `r_j≤1` and every other entry is
nonnegative. Hence

\[
 B_\tau(r)\le\sigma(\tau,M)\sum_jr_j
             \le\sigma(\tau,M)=H.
\]

Concentration attains the bound. For `M≥2`, equality forces a unit row,
as equality in the weight bound at any positive entry requires that entry
to equal one and every other entry to vanish. For `M=1`, full budgets
give the unique all-one column and reward one.

## One crossover, with exact bounds

Fix `t>0` and `M≥2`. Set `F=e^τ`, `f(F)=2F^b+M−2` and

\[
 G(F)=(F+M-1)f'(F)-f(F).
\]

Then

\[
 D-H=\frac{FG(F)}{f(F)(F+M-1)},\qquad
 G'(F)=2b(b-1)(F+M-1)F^{b-2}<0.
 \tag{11}
\]

Since `G(1)=M(2b−1)>0` and `G(F)→−∞`, there is a unique root
`F_*>1`. Define `τ_*=log F_*`. This proves the strict comparisons on
either side and the tie at the threshold.

For its location, use

\[
 G(F)=2F^{b-1}[b(M-1)-(1-b)F]-(M-2).
 \tag{12}
\]

When `M=2`, this vanishes exactly at `F=b/(1−b)=E`, so `τ_*=t`.
For `M>2`,

\[
 G(E)=(M-2)\left[\frac{2E^b}{E+1}-1\right]>0.
\]

The strict sign follows by differentiating

\[
 J(E)=\frac{E\log E}{E+1}-\log\frac{E+1}{2}:
 \qquad J(1)=0,\qquad J'(E)=\frac{\log E}{(E+1)^2}>0.
\]

Thus `E^b>(E+1)/2`. At `F=E(M−1)`, the bracket in (12) is zero,
giving `G=−(M−2)<0`. Strict monotonicity proves (3). The counts in the
classification table now follow from the `M` concentration assignments
and `M(M−1)` assignments to different tasks. Their union has `M²`
elements at the tie, and purity excludes any fractional equality case.

## An exact rectangular gain

Take `M=3`, `t=τ=log 2`, and assign the two agents different tasks.
Then `b=2/3`, `r=2^(2/3)`, and the exact optimum and gain are

\[
 R_{\rm het}=\frac{4r}{3(2r+1)},\qquad R_{\rm hom}=\frac12,
 \qquad\Delta R=\frac{2r-3}{6(2r+1)}.
\]

The integer comparison `19³=6859<6912=4·12³` gives `r>19/12`.
The gain expression increases strictly with `r`, since its derivative
is `4/[3(2r+1)²]`. Substitution yields

\[
 \boxed{\Delta R>\frac1{150}}.
\]

With one agent the homogeneous and unrestricted classes coincide. For
two agents, one task offers no choice, and the two-task matched gain is
zero. Three tasks are therefore the first task count with a positive
matched gain for this two-agent family. The previous three-agent
minimality result concerned square `N=M` instances and remains unchanged.

## Algorithmic consequence and evidence scope

For two agents and `M≥2`, only the two rewards in (1) need comparison.
After the required real score and exponential weights are supplied, this
requires `O(1)` arithmetic and comparison operations. The unique `M=1`
case is immediate. Writing a dense `2×M` allocation still takes output
space proportional to `M`; the optimizing occupancy pattern itself has
constant size.

This is not a general bit-complexity bound for arbitrary real temperatures.
Contract `algal.lab.softmax-partition.v3` of the
[certified solver](certified-softmax-partitions.md) evaluates outward
intervals for both rewards, retains the feasible witness with greatest
lower endpoint, and uses the largest upper endpoint as its optimum bound.
Their difference certifies additive regret without requiring an exact
decision at arbitrary transcendental ties. For `M>2`, this path reports
`two-agent-enumeration` and `purityCertificate.basis="universal-positive-temperature"`;
it makes no DP or threshold queries. Each of at most four precision passes
checks exactly two occupancies, so the executable makes at most eight
occupancy evaluations. The existing two-task scan covers `M=2`; `M=1`
is independently pure. No runtime benchmark or speedup is claimed.
Enumeration of two alternatives is classical.

The bounded [finite checker](../research/spikes/stochastic/softmax_small.py)
compares the formulas with independently evaluated nested means at
100-digit Decimal precision. It checks 40 pure-pattern comparisons and
5,900 full-budget quarter-grid matrices for two agents and two through
four tasks. All 73 numerically identified grid maximizers are pure.
Its exact integer check gives the displayed radical bound. The finite
grid does not establish continuous purity or the universal phase diagram.

```sh
python3 -m research.spikes.stochastic.softmax_small
python3 -m unittest research.test_softmax_partition
python3 -m research.softmax_partition --agents 2 --tasks 128 --inner 4 --outer 1/100 --epsilon 1/100000000
```

The proof is analytic and does not infer purity from numerical absence of
counterexamples. Reasoning agents developed and reviewed the argument;
no external-inference experiment or measured model/token-efficiency
comparison accompanies these results.

## Source comparison and remaining priority

The exact model is the nested-softmax allocation setting of
[Amir, Bettini and Prorok, v4](https://arxiv.org/html/2506.09434v4).
The bounded source audit inspected §2 and §3, including Theorems 3.1–3.4,
the softmax specialization, Appendix I Table 3, and Appendix J.2–J.4.
Theorem 3.4 assumes `N=M≥2` and gives heterogeneity-gain lower bounds.
The inspected experiments include square sizes `2,4,8` and a discrete
`N=11,M=2` comparison. Those passages do not state the exact two-agent,
arbitrary-task optimum, all-maximizer purity or the unique crossover
proved here.

The author publication records were checked for authorship, venue and
links. The linked OpenReview page presented a browser verification
challenge, so inaccessible review content supplies no evidence here.
Four targeted searches identified no follow-up proving this precise
classification; that outcome is not a literature-wide absence or
first-priority claim.

The support arguments rely on the classical ingredients credited in the
[support note](softmax-support-structure.md). The new exclusion above
combines elementary second-order necessary conditions with bounds on
private and shared curvatures. The crossover uses the standard concavity
comparison already discussed in the
[continuous-allocation note](softmax-integral-optima.md). Neither the
Hessian identity, positive-trace contradiction, two-option enumeration
nor the general one-crossing mechanism is presented as a new principle.

The candidate contribution is the exact model-specific rectangular
classification and its consequences. The later [universal purity theorem](softmax-universal-purity.md)
settles fractional support trees with any number of active tasks. Wider
nonlinear-allocation, small-population integrality and citation-neighborhood
comparisons remain open. The [dominance theorem](softmax-dominance.md) settles
three tasks for arbitrary populations, using the total-two-agent result here.
The [novelty ledger](novelty-ledger.md) tracks the broader source gaps; this
result does not close them.
