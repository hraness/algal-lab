# When softmax specialization changes

The two-agent allocation problem has an exact solution at every pair of
inner and outer temperatures. In particular, matched positive temperatures
produce no heterogeneity gain with two agents, while every square dimension
from three onward has a positive gain. Three is therefore the sharp minimum
dimension over continuous allocations, including those that leave effort
unused.

A different boundary appears when selecting among pure allocations. At small
positive matched temperature, two groups as equal as possible are optimal.
At sufficiently large temperature, a square population of `r²` agents instead
optimally forms `r` groups of `r`. For nine agents this proves a change from
occupancies `(5,4)` to `(3,3,3)`. These statements concern eventual regimes;
no numerical transition temperature is asserted. The
[continuous-allocation sequel](softmax-integral-optima.md) proves that both
optima hold over fractional allocations, because every matched positive
temperature has only pure maximizers.

Use the [nested allocation model](softmax-task-allocation.md): nonnegative
`N×M` effort matrices with row sums at most one, task scores obtained with
`B_t`, and outer reward `B_τ`, where

\[
 B_a(x)=\frac{\sum_i x_i e^{a x_i}}{\sum_i e^{a x_i}},\qquad
 \sigma(a,n)=\frac{e^a}{e^a+n-1}.
\]

The two-agent theorem permits arbitrary continuous efforts. The later
asymptotic theorems use pure allocations with full budgets: each agent assigns
one unit to exactly one task. All temperatures below are finite real numbers.

## Exact two-agent solution

For `N=M=2` and every pair `(t,τ)`,

\[
 R_{\rm het}=\sigma(\max\{t,\tau,0\},2),\qquad
 R_{\rm hom}=\sigma(\max\{\tau,0\},2).
 \tag{1}
\]

Their difference is the exact heterogeneity gain. Thus every branch of the
lower bound in Theorem 3.4 of Amir, Bettini and Prorok is exact for two agents.
For `t,τ>0`, all maximizing allocations are:

| Parameters | Maximizers |
|---|---|
| `t>τ` | The two permutation matrices. |
| `τ>t` | The two complete-concentration matrices. |
| `t=τ` | Both endpoint types: exactly four matrices. |

Here a concentration matrix assigns both agents to the same task. Every
maximizer in this positive quadrant uses both budgets fully, even at
parameters where coordinatewise monotonicity of the Boltzmann mean fails.

### Full-budget calculation

Write the rows as `(a,1−a)` and `(b,1−b)`. Put

\[
 u=(a+b-1)/2,\quad d=(a-b)/2,\quad g_c(z)=z\tanh(cz).
\]

The task scores are `1/2+u+g_t(d)` and `1/2−u+g_t(d)`, so

\[
 R=\frac12+g_t(d)+g_\tau(u),\qquad |u|+|d|\le\frac12.
 \tag{2}
\]

Suppose `t,τ>0` and let `α=max(t,τ)`. The function `g_c` is even and
increases strictly with positive `c` at any fixed nonzero argument. For
`x,y≥0`, monotonicity of `tanh` gives

\[
 g_\alpha(x)+g_\alpha(y)\le g_\alpha(x+y),
\]

strictly if both arguments are positive. Also `g_α` increases strictly on
the positive half-line. Applying these facts to (2),

\[
 R\le\frac12+g_\alpha(|d|)+g_\alpha(|u|)
 \le\frac12+g_\alpha(1/2)=\sigma(\alpha,2).
\]

Both endpoints are feasible, so this upper bound is attained. Equality forces
`u=0, |d|=1/2` if `t>τ`, and `d=0, |u|=1/2` if `τ>t`. If the temperatures
are equal either choice is possible, and strictness excludes all others.

### Unused budgets cannot improve the optimum

The preceding calculation does not assume away the possibility of unused
effort. To handle it, take a global maximizer, which exists by compactness,
and choose a column of maximal task score `X`. For the outer mean,

\[
 \partial_X B_\tau(X,Y)=P_X[1+\tau(X-B_\tau(X,Y))]>0
 \quad\text{when }X\ge Y,\ \tau>0.
\]

For fixed other entry `c`, the inner slice `f(a)=B_t(a,c)` has derivative

\[
 f'(a)=\frac{e^v(1+e^v+v)}{(1+e^v)^2},\qquad v=t(a-c).
\]

The factor `1+e^v+v` is strictly increasing. Hence the slice has a single
strict minimum and no interior local maximum. If a row had unused budget
and a positive entry in the chosen column, an arbitrarily small feasible
increase or decrease of that entry would raise `X`, and then raise the outer
reward. This contradicts maximality, including when the two task scores tie.

Any slack row must therefore have a zero in this column. With only two
agents its score is `X=B_t(0,c)=cσ(tc,2)≤σ(t,2)`, since this expression is
strictly increasing in `0≤c≤1`. The outer reward is at most its maximal
score. If `τ>t`, concentration already attains the strictly larger
`σ(τ,2)`. If `τ≤t`, a permutation attains `σ(t,2)`, so equality would be
necessary. Equality forces both task scores to be `σ(t,2)` and `c=1`.
The other entry in that agent's row is then zero; the other task can reach
`σ(t,2)` only if the supposedly slack agent assigns it one unit. This is
again a contradiction. Thus all positive-quadrant maximizers use full budgets,
and the calculation above applies to the original feasible set.

For `t≤0`, the prior [score-set theorem](softmax-task-allocation.md#nonpositive-inner-temperature-the-entire-attainable-region)
gives `R_het=R_hom=σ(max(τ,0),2)`. For `t>0,τ≤0`, the prior exact optimum
is `σ(t,2)`, with homogeneous reward `1/2`. These two branches complete (1).

At matched positive temperatures, (1) gives `ΔR=0`. The prior pure-allocation
theorem gives `ΔR>0` for every `n≥3`; a single agent is trivially homogeneous.
Thus `n=3` is the sharp smallest square dimension for positive matched gain
over all continuous allocations with budgets at most one.

## Small positive temperature selects two balanced groups

Let `N=M=n≥3`, `t=τ>0`, and let positive integers `m_1,…,m_k` be the task
occupancies of a pure full-budget allocation, with `∑m_j=n`. Write its reward
as `R_m(t)` and the homogeneous optimum as `h(t)=σ(t,n)`. Then, as `t↓0`,

\[
 R_m(t)-h(t)=\frac{t^2}{2n^4}
 \sum_{j=1}^k m_j(m_j-1)(n-m_j)+O(t^3).
 \tag{3}
\]

Among these allocations the coefficient is uniquely maximized, up to task
permutation, by `(⌈n/2⌉,⌊n/2⌋)`. Consequently this occupancy pattern uniquely
maximizes the pure reward for all sufficiently small positive `t`, for each
fixed `n`. Agent relabeling does not affect the reward.

To prove the expansion, put `E=e^t`, `p=m/n`, `D=1−p+pE`, and `s=pE/D`.
Differentiation at zero gives

\[
 \log(E^s/D)=\tfrac12p(1-p)t^2+O(t^3).
\]

The exact gap identity in the [preceding proof](softmax-task-allocation.md#every-intermediate-pure-allocation-improves-the-reward)
is

\[
 R_m-h=\frac{h}{Z}\sum_j(m_j-1)(E^{s_{m_j}}/D_{m_j}-1),
 \quad Z=\sum_jE^{s_{m_j}}+n-k.
\]

Since `h/Z=1/n²+O(t)`, substitution proves (3).

For the optimization, set `f(m)=m(m−1)(n−m)`. Merging groups of sizes `a,b`
changes their total score by

\[
 f(a+b)-f(a)-f(b)=ab[2(n+1)-3(a+b)].
\]

If there are at least three groups, the two smallest obey `a+b≤2n/3`, so
merging them strictly increases the coefficient. A single group has zero
coefficient. For two groups the score is `(n−2)a(n−a)`, uniquely maximized
at the two closest integers to `n/2`. The maximum coefficient in (3) is

\[
 \frac{(n-2)\lfloor n^2/4\rfloor}{2n^4}.
\]

There are finitely many integer occupancy partitions at each fixed `n`.
The strictly positive coefficient gap to every competitor, together with
(3), gives one positive neighborhood where this pattern beats all competitors.
This is an eventual-optimality proof, not a computed uniform temperature bound
as `n` varies.

## Large temperature selects square-root groups for square populations

For a fixed occupancy partition, as `t→∞`,

\[
 R_m(t)=1-A(m)e^{-t}+O(te^{-2t}),\qquad
 A(m)=\frac nk\left(1+\sum_{j=1}^k\frac1{m_j}\right)-2.
 \tag{4}
\]

If `n=r²`, the unique coefficient minimizer is `k=r` and every `m_j=r`.
For each fixed square `n≥4`, this pattern therefore uniquely maximizes the
pure reward for all sufficiently large `t`.

For the expansion, write `c_m=n/m−1`. Then

\[
 s_m=1-c_m/E+O(E^{-2}),\qquad
 E^{s_m}=E-c_m\log E+O((\log E)^2/E).
\]

Using `Z=ΣE^{s_m}+n−k` and the exact deficit identity,

\[
 1-R_m=\frac{n-k+\sum_j(1-s_{m_j})E^{s_{m_j}}}{Z},
\]

we have `(1−s_m)E^{s_m}=c_m+O((log E)/E)` and `Z=kE+O(log E)`.
Their ratio gives (4), including its remainder order.

The elementary reciprocal-sum and arithmetic–geometric mean inequalities give

\[
 \sum_j\frac1{m_j}\ge\frac{k^2}{n},\qquad
 A(m)\ge k+n/k-2\ge2\sqrt n-2.
\]

For square `n=r²`, simultaneous equality requires `k=r` and all occupancies
`r`. Finiteness of the partition set again turns the strict coefficient gap
into eventual optimality. These standard inequalities are ingredients of the
allocation result, not separate novelty claims.

For `n=9`, the two regimes disagree:

| Occupancies | Small-temperature gain coefficient | Large-temperature deficit coefficient |
|---|---:|---:|
| `(5,4)` | `70/6561` | `181/40` |
| `(3,3,3)` | `54/6561` | `4` |

The first coefficient is maximized and the second minimized. Thus the optimal
number of occupied tasks changes between these regimes. This does not assert
one transition, a specific transition temperature, or the absence of other
optimal patterns at intermediate temperatures.

## Evidence and source scope

These proofs were independently checked. They sharpen the previous
[source-relative allocation results](softmax-task-allocation.md#source-comparison-and-priority).
In [arXiv v1](https://arxiv.org/pdf/2506.09434v1), Theorem 3.4's exactness
conjecture applied to every `N=M≥2`. The two-agent formula proves that special
case; the three-agent witness disproves the general conjecture. The conjecture
was omitted from [v2 onward](https://arxiv.org/html/2506.09434v2).

Figure 2 in the inspected [ICLR author PDF](https://matteobettini.com/publication/hetenvdesign/HetEnvDesign.pdf)
explicitly uses `N=M=2` and labels its gain values approximate. Its visible
positive-quadrant pattern is consistent with (1); the proof establishes the
formula rather than contradicting the figure or independently verifying its
numerical data. The current theorem states lower bounds. No inspected passage
supplied the unused-budget proof or the asymptotic pure-group selection
results. An audit of all committed program/configuration text in the authors'
[official code](https://github.com/proroklab/HetEnvDesign/tree/18521b698a5ce10f31fc5222cc4f0a3e637c4c28)
also found no matching result or identified Figure 2 heatmap method. Its
plotting paths produce training curves, CSV summaries or aggregator-input
surfaces. All 39 blobs were enumerated and hash-verified at commit
`18521b698a5ce10f31fc5222cc4f0a3e637c4c28`; all source/configuration bodies
were read, while the license received a partial text review. External
simulator and learning dependencies were not read. The wider literature
and inaccessible discussion remain gaps,
so first-discovery priority is not asserted. See the [novelty ledger](novelty-ledger.md).

Run the exact, credential-free standard-library checker:

```sh
python3 -m research.spikes.stochastic.softmax_boundaries
```

It directly evaluates 625 full-budget two-agent allocations at 25 pairs of
integer multiples of `log 2`, with exact rational weights after cancelling a
common exponential factor. It checks optimum values and the positive-quadrant
maximizers. It also checks the cubic coefficient optimization on 2,710
partitions through `n=20`, 2,593 strict merge identities, and the large-
temperature coefficient on 2,224 partitions for `n∈{4,9,16,25}`. The combined
stochastic verifier includes these checks in CI.

The arbitrary-budget two-agent statement, asymptotic remainders and eventual
optimality rest on the analytic proofs. Separate exploratory numerical checks
found no counterexample; one optimization search missed known endpoint optima
at several large temperatures. Those unsuccessful searches are retained and
are not optimum certificates. No learned-policy, small-model origination,
token-efficiency or runtime-performance claim is made.
