# Dominance restrictions and exact small-task optima

At a positive-temperature optimum, a pure agent never shares a task with
an agent who splits effort. A stronger pairwise restriction proves this
separation and, together with the support-forest theorem, shows that every
optimum with at most three active tasks is pure. In particular, **three
tasks suffice for an exact integer reduction at every population size and
every positive temperature pair**.

A separate curvature argument rules out a fractional star spanning all
agents. Consequently, if a maximizing task receives positive effort from
every agent, all agents concentrate their whole budgets there.

These are analytic statements about every global maximizer. Temperatures
are finite and strictly positive throughout. The later [universal purity
theorem](softmax-universal-purity.md) settles the remaining fractional support
trees; the wider literature priority of these model-specific conclusions
remains open.

## Model and established premises

Let `A=(a_ij)` be a nonnegative `N×M` matrix, with each row sum at most
one, where `N,M≥1`. Define

\[
 B_c(x)=\frac{\sum_i x_i e^{cx_i}}{\sum_i e^{cx_i}},\qquad
 S_j=B_t(A_{:j}),\qquad R(A)=B_\tau(S),\qquad t,\tau>0.
\]

A pure row has one unit entry; every other full-budget row is fractional.
An active task has a positive entry, and a private task has exactly one.
The [budget and sign lemmas](softmax-integral-optima.md) establish, at every
maximum, full row budgets and positive derivatives at positive entries:

\[
 p_{ij}=\frac{e^{ta_{ij}}}{\sum_l e^{ta_{lj}}},\quad
 h_{ij}=1+t(a_{ij}-S_j)>0,\qquad
 W_j=P_jg_j>0,\quad g_j=1+\tau(S_j-R)
\]

on active tasks, where `P_j=e^(τS_j)/Σ_l e^(τS_l)`. All sums retain the
zero entries and inactive tasks. The [support results](softmax-support-structure.md)
also establish a forest and forbid a row from owning two private tasks.

For `N≥2`, a positive inner entry `x` with weight `p` and factor `h>0`
has scalar curvature

\[
 \partial_x^2 B_t=tp[1+(1-2p)h].
 \tag{1}
\]

This is strictly positive if `p≤1/2`. If `p>1/2`, its entry exceeds all
others in the column. Let `m` be their weighted mean and `d=t(x−m)>0`.
Nonnegativity gives `d≤tx`, and

\[
 h=1+(1-p)d,\qquad
 \partial_x^2 B_t=tp(1-p)[2-(2p-1)d].
 \tag{2}
\]

In this case `tx<2` suffices for positive curvature.

A two-sided transfer between positive entries of a maximizing row is
stationary. If `v` is its first task-score variation, the identity

\[
 D^2 B_c(x)[v,v]
 =c\sum_i p_i(1+h_i)v_i^2
  -2c\left(\sum_i p_iv_i\right)DB_c(x)[v]
 \tag{3}
\]

makes the outer Hessian contribution
`τΣ_j P_j(1+g_j)v_j²>0`: the mixed term vanishes by stationarity, and
only active tasks move. Thus two positive inner scalar curvatures on the
transferred pair contradict maximality.

The one-agent case is separate. Its task scores equal its row entries,
and each outer weight is at most `σ(τ,M)=e^τ/(e^τ+M−1)`. Therefore
`R≤σ(τ,M)Σ_j a_1j≤σ(τ,M)`, attained only by unit rows when `M≥2`.
For `M=1`, full budgets give the unique all-one column. Neither case uses
the other-coordinate mean or strict inner curvature in (2).

## A larger contribution cannot dominate a supported pair

**Theorem.** If a maximizing row has positive entries `a,b` in distinct
tasks, every other agent's contribution `c` to the first task satisfies

\[
 \boxed{c<a+b}.
 \tag{4}
\]

Suppose instead `c≥a+b`. In the first task, `c>a` makes the weight of
`a` less than `1/2`, so its scalar curvature is positive by (1).
Put `z=t(c−a)>0`. If `x_l` are that task's entries and `Z` its exponential
denominator, positivity of `h_a` gives

\[
 0<Zh_a=\sum_l e^{tx_l}[1+t(a-x_l)].
\]

For every real `x`, the exponential tangent inequality gives
`e^(tx)[1+t(a−x)]≤e^(ta)`. Separating the entry `c` and bounding the
other `N−1` terms yields

\[
 0<Zh_a\le e^{tc}(1-z)+(N-1)e^{ta},\qquad
 (z-1)e^z<N-1.
 \tag{5}
\]

Now consider `b` in the other task. If its weight is at most `1/2`, its
curvature is positive by (1). Otherwise its own exponential weight exceeds
the sum of all others, which is at least `N−1` because entries are
nonnegative. With `y=tb≤z`,

\[
 (z-1)e^z<N-1<e^y\le e^z.
\]

Hence `z<2` and `y<2`, making `b`'s curvature positive by (2). Both
inner curvatures are now positive, contradicting the stationary transfer
condition following (3). This also excludes equality `c=a+b`.

The inequality concerns maxima with the stated positive derivative signs.
It is not an assertion about every feasible allocation.

## Pure and fractional rows occupy separate components

If a fractional row shares a task with a pure row, let `a>0` be its effort
there and `b>0` any other effort. The pure row contributes `c=1`, whereas
`a+b≤1`, contradicting (4). Thus no active task contains both row types.
Every support component consequently has only pure rows or only fractional
rows. A pure component is a star around one task.

A fractional component has every row degree at least two. It cannot have
one row, since that row would own two private tasks. If it has `n≥2`
rows, `k` tasks and `e` edges, the forest identity gives

\[
 e=n+k-1\ge2n,\qquad k\ge n+1.
 \tag{6}
\]

For the whole support, let `F` be its number of fractional rows, `C_F`
their number of components, `K_F` their task count, and `K_P` the number
of pure tasks. Summing (6) gives

\[
 K=K_F+K_P\ge F+C_F+K_P.
 \tag{7}
\]

If `F>0`, then `C_F≥1` and `F≥2C_F`. If `0<F<N`, full budgets also
force `K_P≥1`. If `F=N`, `K_P=0`; if `F=0`, then `C_F=K_F=0` and
(7) is the identity `K=K_P`.

## Three active tasks force purity

**Theorem.** Every global maximum with at most three active tasks is pure,
for every population size and arbitrary ambient task count. In particular,
every problem with `M≤3` has only pure maxima throughout the positive
temperature quadrant.

For `N≥3`, suppose `F>0`. If `F=N`, (7) gives `K≥N+1≥4`. If `F<N`,
then `F≥2`, `C_F≥1` and `K_P≥1`, again giving `K≥4`. This excludes a
fractional maximum with `K≤3`. The one-agent case was handled above;
the [two-agent arbitrary-task theorem](two-agent-softmax-phase.md) handles
`N=2`.

The two-agent theorem is used only when the **total** population is two.
A two-row fractional component inside a larger population still has the
other agents' zero entries in its inner denominators. It is not an isolated
two-agent optimization problem.

Likewise, a pure solver returning three groups does not prove that every
continuous competitor uses at most three tasks. The unconditional task-count
guarantee is `M≤3`.

### The complete three-agent square phase diagram

For `N=M=3`, let

\[
 E=e^t,\quad a=\frac{2E}{2E+1},\quad b=\frac{E}{E+2},\qquad
 P=b,\quad Q=\frac{a e^{\tau a}+b e^{\tau b}}
                       {e^{\tau a}+e^{\tau b}+1},\quad
 H=\frac{e^\tau}{e^\tau+2}.
\]

The earlier [pure phase comparison](softmax-integral-optima.md#exact-three-agent-phases)
proves thresholds

\[
 \ell(t)=\frac1a\log\frac{2E+1}{3},\qquad
 0<\ell(t)<t<u(t)<t+\log4,
\]

where `u(t)` is the unique positive `Q=H` crossing above `t`. The new
purity theorem makes `R_het=max{P,Q,H}` the continuous optimum for **all**
`t,τ>0`, with these complete labeled maximizing sets:

| Outer temperature | Optimal occupancies | Number of allocations |
|---|---|---:|
| `0<τ<ℓ` | `(1,1,1)` | 6 |
| `τ=ℓ` | `(1,1,1)` or `(2,1,0)` | 24 |
| `ℓ<τ<u` | `(2,1,0)` | 18 |
| `τ=u` | `(2,1,0)` or `(3,0,0)` | 21 |
| `τ>u` | `(3,0,0)` | 3 |

Every equality case is pure. This extends the existing pure comparison to
the entire continuous positive quadrant; it does not claim a new general
single-crossing principle.

For arbitrary `N` with `M=3`, there are `O(N²)` integer occupancy patterns
with at most three parts. After their score and exponential weights are
supplied, classical enumeration needs `O(N²)` reward evaluations and
comparisons to select an optimum. This is not a bit-complexity bound for
arbitrary real temperatures. The version-3
[certified solver](certified-softmax-partitions.md) documents its bounded
small-dimension execution paths, interval certificates and scope metadata.

## A fractional star spanning every agent cannot maximize

Assume `N≥2`. Consider an entire-population star: row `i` puts `1−a_i`
into one common central task and `a_i` into its own private task, with
`0<a_i<1`. There are `N+1` active tasks; additional tasks remain in the
outer mean as zeros. Each private effort is an independent two-sided local
coordinate preserving its row budget.

**Theorem.** No such fractional star is a global maximum.

Let `w>0` solve `w e^w=(N−1)/e`, the principal real Lambert-W value, and
set `α=w/(1+w)>0`. We use only this exact defining equation. For `z≥0`,

\[
 f(z)=\frac{z(N-1)}{e^z+N-1}
\]

has derivative with the sign of `N−1−(z−1)e^z`. Its unique positive
stationary point is `z=1+w`, where its value is `w`; it increases before
that point and decreases after it to zero. Consequently

\[
 \max_{z\ge0}f(z)=w.
 \tag{8}
\]

A private score is `q_N(u)=u e^(tu)/(e^(tu)+N−1)`. With its weight
`p=e^(tu)/(e^(tu)+N−1)` and `h=1+tu(1−p)`, (8) gives `h≤1+w`.
Since `q_N′=ph>0` and `p<1` at finite temperature,

\[
 L(u):=\frac{q_N''(u)}{q_N'(u)}
 =t\left(1+\frac1h-2p\right)>-t\alpha.
 \tag{9}
\]

Strictness remains even when `h=1+w`.

### The central weight and trace bounds

All `N` central entries `x_i=1−a_i` are positive, so all their derivative
factors `h_i` are positive. For the central weight vector `p`, entropy
`\mathcal H(p)=−Σ_i p_i log p_i` gives the exact identity

\[
 h_i=1+\log p_i+\mathcal H(p).
\]

Put `P=max_i p_i`. The smallest weight is at most `(1−P)/(N−1)`, and
entropy with one fixed weight `P` is maximized when the rest are equal.
Therefore

\[
 0<h_{\min}
 \le1-P\log\frac{(N-1)P}{1-P}.
 \tag{10}
\]

The function `φ(P)=P log((N−1)P/(1−P))` strictly increases for
`P≥1/N`, since its derivative is
`log((N−1)P/(1−P))+1/(1−P)>0`. At `P_*=1/(1+w)`, the defining
identity for `w` gives `φ(P_*)=1`. Also `w<N−1`, so `P_*>1/N`.
Equation (10) thus implies

\[
 P<\frac1{1+w},\qquad 1-P>\alpha.
 \tag{11}
\]

Let `c_i=∂_i B_t(x)=p_i h_i>0`. Translation equivariance gives
`Σ_i c_i=1`. The central Hessian trace is

\[
 T=\sum_i\partial_i^2B_t(x)
   =2t\left(1-\sum_i p_i^2h_i\right)
   \ge2t(1-P)>2t\alpha.
 \tag{12}
\]

Here `Σ_i p_i²h_i=Σ_i p_i c_i≤P`. The first comparison can be equality
at uniform weights; the second is strict by (11). In particular, the equal
central entries case is included.

### Stationarity completes the contradiction

Let `W_c>0` be the central outer derivative and `W_i>0` the derivative at
private task `i`. Stationarity in each effort `a_i` gives
`W_i q_N′(a_i)=W_c c_i`. The inner-score contribution to the full Hessian
trace is therefore

\[
 \sum_i W_iq_N''(a_i)+W_cT
 =W_c\left[\sum_i c_iL(a_i)+T\right]
 >t\alpha W_c>0,
 \tag{13}
\]

by (9), (12) and `Σ_i c_i=1`.

Each coordinate's score variation moves only its private and central tasks,
with derivatives `q_N′(a_i)` and `−c_i`. Stationarity cancels the mixed
term of (3), leaving a strictly positive outer Hessian contribution because
both tasks have `g_j>0`. Thus the full trace is positive. A maximum on the
open private-effort coordinates requires all diagonal second derivatives
to be nonpositive, a contradiction.

This proof includes `N=2` and uniform central weights. It does not apply to
a smaller star embedded among external zero rows: the active central
partials then need not sum to one, the active-coordinate trace is not the
full trace in (12), and positivity of the minimum-weight factor is not
guaranteed. Removing those rows would change the objective.

## A universally served task forces concentration

**Corollary.** If one task receives positive effort from every row at a
global maximum, all agents concentrate their full units on it. Equivalently,
every nonconcentrated maximum has a zero entry in each task column.

If a row is pure in that central task, the no-mixing theorem forces every
row there to be pure, yielding concentration. Otherwise all rows are
fractional. Any other task shared by two rows would form a four-cycle with
the central task, contradicting the support forest. Every noncentral task
is therefore private. Each fractional row needs at least one such task,
and the private-task theorem permits at most one. This is exactly the
excluded all-agent star. The one-agent case is already pure separately.

For three agents, a nonconcentrated optimum can therefore have no task
served by all three. The remaining possible fractional supports use four
or five active tasks, including a two-row fractional component with a
separate pure row and connected trees with shared tasks of degree two.
These support graphs are not asserted to be stationary or maximizing.

## Attribution and evidence limits

The exponential tangent inequality, scalar Lambert-W maximization, entropy
bound, weighted-average trace comparison, graph counting and second-order
necessary conditions are classical ingredients. The
[support note](softmax-support-structure.md#classical-ingredients-and-remaining-priority)
records the inspected transportation-polytope and Shapley–Folkman
comparisons. Those sources do not directly imply the nonlinear
all-maximizer conclusions here; wider nonlinear-allocation comparisons
remain open.

One used identity has explicit prior attribution: Theorem 5 of
[Liao et al., DAC 2023](https://www.cse.cuhk.edu.hk/~byu/papers/C171-DAC2023-Meawilm.pdf)
states that the gradient components of the positive exponential weighted
mean sum to one. Its weighted-average wirelength combines this mean with
the corresponding negative-temperature mean. The inspected theorems concern
gradient identities or limits and Moreau approximation, rather than nested
allocation support. The identity `Σ_i c_i=1` above is established prior art;
the positive-trace exclusion requires the additional maximum-point bounds.

The candidate contributions are the model-specific dominance exclusion,
three-task continuous reduction and all-agent-star exclusion. No new
general optimization framework, entropy inequality, enumeration mechanism
or definitive literature priority is claimed. The
[novelty ledger](novelty-ledger.md) tracks the outstanding source comparisons.

The [finite checker](../research/spikes/stochastic/softmax_small.py) evaluates
13,500 three-agent, three-task full-budget quarter-grid matrices at four
positive temperature pairs using 100-digit Decimal arithmetic. It compares
them with independently evaluated pure representatives; all 45 numerically
identified grid maxima are pure. One tested pair, `t=4,τ=1/100`, is outside
the earlier sufficient region. This finite grid corroborates the formulas
and does not prove purity for all populations or continuous inputs.

```sh
python3 -m research.spikes.stochastic.softmax_small
```

Reasoning agents developed and reviewed the analytic arguments. No
external-inference experiment or measured model/token-efficiency comparison
accompanies these claims. Numerical absence of fractional counterexamples
is not used as proof; the linked universal path proof, rather than this
finite grid, settles the higher-dimensional trees.
