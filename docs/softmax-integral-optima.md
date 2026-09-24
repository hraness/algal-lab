# When continuous softmax allocation has a discrete optimum

At every matched positive temperature, every optimal allocation gives each
agent's whole unit to one task. Continuous effort splitting adds no
maximizers. More generally, this holds throughout the region

\[
 \mathcal P=\{(t,\tau):t>0,\ \tau>0,\quad
                t\le2\ \text{or}\ \tau\ge t/4\}.
 \tag{1}
\]

Every optimum uses its full row budgets at **all** positive temperature
pairs, even outside this proved purity region. The
[support-structure sequel](softmax-support-structure.md) proves larger
sufficient regions and settles every two-task problem. Fractional optima
with three or more active tasks remain unresolved outside the enlarged
regions; the boundary in (1) is not claimed sharp.

This reduction turns the earlier pure-allocation results into global
continuous optima at matched temperature: two balanced groups near zero,
square-root groups at sufficiently large temperature for square populations,
and an exact three-agent solution for every positive temperature.

Use the [allocation model](softmax-task-allocation.md): a nonnegative
`N×M` matrix `A=(a_ij)` has row sums at most one, task scores
`S_j=B_t(A_j)` and reward `R=B_τ(S)`, where `A_j` denotes a column and

\[
 B_c(x)=\frac{\sum_i x_i e^{c x_i}}{\sum_i e^{c x_i}}.
\]

Dimensions are positive integers and temperatures finite. Pure full-budget
allocations have exactly one entry equal to one in each row. All conclusions
below concern every global maximizer, including equality cases.

## Derivative identities

For a single Boltzmann mean, write `p_i=e^{c x_i}/Σe^{c x_i}`,
`b=B_c(x)` and `ū=Σp_i u_i`. Direct differentiation gives

\[
 \partial_i B_c=p_i[1+c(x_i-b)],\qquad
 D^2B_c(x)[u,u]
 =c\sum_i p_i[2+c(x_i-b)](u_i-\bar u)^2.
 \tag{2}
\]

Expanding the centered square yields the useful equivalent expression

\[
 D^2B_c(x)[u,u]
 =c\sum_i p_i[2+c(x_i-b)]u_i^2
       -2c\bar u\,DB_c(x)[u].
 \tag{3}
\]

For the nested problem set

\[
 p_{ij}=\frac{e^{t a_{ij}}}{\sum_l e^{t a_{lj}}},
 \quad h_{ij}=1+t(a_{ij}-S_j),\qquad
 P_j=\frac{e^{\tau S_j}}{\sum_l e^{\tau S_l}},
 \quad g_j=1+\tau(S_j-R),\quad W_j=P_jg_j.
\]

Then `∂_ij R=W_j p_ij h_ij`, and the inner coordinate's second derivative is

\[
 \partial_{ij}^2S_j=t p_{ij}[1+h_{ij}-2p_{ij}h_{ij}].
 \tag{4}
\]

These derivative identities are elementary ingredients, not separate
originality claims. In particular, a scalar coordinate slice at positive
temperature has strictly positive second derivative `c p_i` whenever its
first derivative vanishes. Such a stationary point is a strict minimum.

## Every positive-temperature optimum uses full budgets

A global maximum exists by compactness. First, every positive-score column
of a maximizing matrix must have `W_j>0`. To see this, scale its nonnegative,
nonzero column `x` by `c`. Its score is `c B_(ct)(x)`, with derivative

\[
 \frac{d}{dc}\{cB_{ct}(x)\}
 =B_{ct}(x)+ct\,\operatorname{Var}_{ct}(x)>0\qquad(c>0).
\]

Decreasing `c` slightly below one is feasible and decreases only that
score. If `W_j<0`, this raises the outer reward. If `W_j=0`, the outer
coordinate slice is at a strict minimum by (4)'s scalar analogue, so the
same decrease again raises the reward. Both contradict maximality.

Next, every positive entry of a maximizing matrix has `h_ij>0`. If its
inner derivative were negative, decreasing that entry would raise its
column score and hence the reward, since `W_j>0`. At zero inner derivative,
(4) gives `t p_ij>0`, so a sufficiently small decrease again raises the
score. Such decreases preserve the row constraints.

A nonzero row with unused budget could now be improved by increasing a
positive entry, because both its inner and outer derivatives are positive.
It remains to exclude a completely zero row. Choose a column of maximal
score, and let `C` and `T` be the exponential-weight sum and weighted-input
sum of its other entries. Thus `0≤T≤C`. With `E=e^t`, replacing the zero
entry by one changes the score by

\[
 \frac{E+T}{E+C}-\frac{T}{1+C}
 =\frac{E(1+C-T)+T}{(E+C)(1+C)}>0.
\]

This is an endpoint comparison; monotonicity along intermediate effort
values is unnecessary. The raised score remains maximal. The outer
derivative in a maximal score is `P_j[1+τ(S_j-R)]≥P_j>0`, so the finite
increase raises the reward. The new row is feasible. No zero row can
maximize, and every row budget is exhausted for all `t,τ>0`.

## Why a fractional row cannot maximize in the proved region

Suppose a maximizing full-budget row has two positive entries, in columns
`j,k`. A sufficiently small transfer `+z,−z` between them is feasible in
both directions. Stationarity implies their allocation derivatives agree:

\[
 W_jp_{ij}h_{ij}=W_kp_{ik}h_{ik}=\lambda>0.
\]

The strict positivity follows from the preceding argument. Suppress the
row index on `p,h`. The task-score directional derivatives are
`v_j=p_jh_j`, `v_k=−p_kh_k`, with all other components zero.
Since `DR=DB_τ(S)[v]=0`, the last term of (3) vanishes.

Combining (3), (4) and the chain rule gives the exact transfer curvature

\[
 \frac{d^2R}{dz^2}
 =\lambda\sum_{l\in\{j,k\}}
 \left[t\left(1+\frac1{h_l}-2p_l\right)
       +\tau p_lh_l\left(1+\frac1{g_l}\right)\right].
 \tag{5}
\]

For `β=τ/t≥1/4`, each bracket divided by `t` is strictly positive:
its portion excluding `βph/g>0` is

\[
 1+\frac1h-2p+\beta ph
 =(1-p)\left(1+\frac1h\right)
       +p\left(-1+\frac1h+\beta h\right)\ge0.
\]

Here `0<p≤1`, `h,g>0`, and AM–GM gives
`1/h+βh≥2√β≥1`. Strictness includes `β=1/4` because the omitted term
is positive. Therefore (5) is positive, contradicting maximality along
the feasible two-sided transfer.

There is a second sufficient condition. For `0<t≤2` the inner Hessians
are positive semidefinite on the unit cube by (2). Their coefficients
`2+t(a_ij-S_j)` are strictly positive, including at `t=2`: equality would
require an entry zero and its positive-weight column mean one, which is
impossible. The chain-rule second derivative is

\[
 D^2R=D^2B_\tau(S)[v,v]
        +\sum_l W_l D^2B_t(A_l)[U_l,U_l].
\]

Only the two active columns move, and their `W_l` are positive. The inner
terms are nonnegative. By stationarity, (3) makes the outer term
`τΣP_l(1+g_l)v_l²>0`. This again contradicts maximality, for every `τ>0`.

No fractional maximizing row exists under either condition in (1).
Together with budget exhaustion, all maximizers there are pure and full.
The argument also covers one agent; with one task, budget exhaustion
already settles the problem.

The proof uses derivative signs **at a maximum**, not global monotonicity
or convexity of the outer operator. The earlier sufficient rectangle
`0<t≤2,0<τ≤1` also has a convex-composition proof, but that global
convexity argument alone does not establish the larger region (1).

For general `N,M`, optimization in (1) reduces exactly to positive integer
task occupancies summing to `N`, using at most `M` tasks. Occupancy `m` has
score `m e^t/(m e^t+N-m)`; unoccupied tasks have score zero. No grid over
continuous efforts is needed to justify this reduction.

## Two balanced groups are globally optimal near zero

For `N=M=n≥3` and matched `t=τ`, the earlier
[pure-allocation expansion](softmax-specialization-boundaries.md#small-positive-temperature-selects-two-balanced-groups)
is

\[
 R_m(t)-\frac{e^t}{e^t+n-1}
 =\frac{t^2}{2n^4}\sum_jm_j(m_j-1)(n-m_j)+O_n(t^3).
 \tag{6}
\]

Its coefficient is uniquely maximized by `(⌈n/2⌉,⌊n/2⌋)`, up to task
labels. Finitely many partitions and their strict coefficient gap make
this pattern optimal among pure allocations throughout a sufficiently
small positive neighborhood. Purity holds at every matched positive
temperature, making these exactly the global maximizers over
continuous efforts, including allocations allowed to leave budgets unused.

For every fixed `n≥3`, there is therefore `ε_n>0` such that every optimum
for `0<t=τ<ε_n` assigns all agents to two tasks as evenly as possible.
No explicit or dimension-uniform `ε_n` is claimed.

## Square-root groups are globally optimal at large temperature

The earlier [large-temperature expansion](softmax-specialization-boundaries.md#large-temperature-selects-square-root-groups-for-square-populations)
gives, for each pure occupancy partition,

\[
 R_m(t)=1-A(m)e^{-t}+O_n(te^{-2t}),\qquad
 A(m)=\frac nk\left(1+\sum_j\frac1{m_j}\right)-2.
\]

For a square population `n=r²`, `r≥2`, its unique leading-coefficient
minimizer is `r` groups of `r`. Finiteness of the partitions makes this
the unique pure occupancy optimum for every sufficiently large matched
temperature. Purity throughout the matched line now makes it the exact
global continuous optimum, with all agent/task relabelings included.

In particular, nine agents have global optimal occupancies `(5,4)` near
zero and `(3,3,3)` for sufficiently large temperature. This proves a
change in optimal group count over continuous allocations. It does not
identify a transition temperature, assert a unique transition or classify
all intermediate-temperature partitions.

## Exact three-agent phases

For `N=M=3`, fix `t>0` and put

\[
 E=e^t,\qquad a=\frac{2E}{2E+1},\qquad b=\frac{E}{E+2}.
\]

Only three pure occupancy patterns exist:

| Occupancies | Allocation type | Reward |
|---|---|---|
| `(1,1,1)` | Each agent has its own task | `P=b` |
| `(2,1,0)` | Two agents share a task; the other uses a second | `Q(τ)=(a e^{τa}+b e^{τb})/(e^{τa}+e^{τb}+1)` |
| `(3,0,0)` | Everyone uses one task | `H(τ)=e^τ/(e^τ+2)` |

Thus, throughout the proved purity region `𝒫`,

\[
 R_{\rm het}=\max\{P,Q(\tau),H(\tau)\},\qquad R_{\rm hom}=H(\tau).
 \tag{7}
\]

There are two unique thresholds satisfying

\[
 0<\ell(t)<t<u(t),\qquad
 \ell(t)=\frac1a\log\frac{2E+1}{3}.
 \tag{8}
\]

Within `𝒫`, they classify all maximizers:

| Outer temperature | All maximizing occupancy patterns |
|---|---|
| `τ<ℓ(t)` | `(1,1,1)` |
| `τ=ℓ(t)` | `(1,1,1)` and `(2,1,0)` |
| `ℓ(t)<τ<u(t)` | `(2,1,0)` |
| `τ=u(t)` | `(2,1,0)` and `(3,0,0)` |
| `τ>u(t)` | `(3,0,0)` |

For `t≤2` this covers every positive outer temperature; for `t>2` it
covers `τ≥t/4`. All agent and task relabelings are included. Fractional
mixtures of tied maximizers are excluded by the purity theorem.

For the lower threshold, direct subtraction gives

\[
 Q(\tau)-b=
 \frac{(a-b)e^{\tau a}-b}{e^{\tau a}+e^{\tau b}+1},
 \qquad \frac{b}{a-b}=\frac{2E+1}{3}.
\]

Its numerator increases strictly and changes sign once, proving the
formula for `ℓ`. Since `E>1`, `ℓ>0`. The prior
[matched-temperature gain](softmax-task-allocation.md#every-intermediate-pure-allocation-improves-the-reward)
gives `Q(t)>b` and hence `ℓ(t)<t`.

For the upper threshold, put `F=e^τ`, `f(F)=F^a+F^b+1` and
`G(F)=(F+2)f′(F)−f(F)`. Then

\[
 Q-H=\frac{F G(F)}{f(F)(F+2)},\qquad
 G'(F)=-(F+2)\{a(1-a)F^{a-2}+b(1-b)F^{b-2}\}<0.
 \tag{9}
\]

Here `G(1)=3(a+b−1)>0` and `G(F)→−∞`. The unique root `F_*` defines
`u(t)=log F_*`; matched gain gives `u(t)>t`. At `F=4E=2a/(1−a)`,
the contribution from score `a` is zero and the other contributions
negative. Thus `t<u(t)<t+log4`.

Finally `P>H` precisely when `τ<t`. The three comparisons prove the
table, including all ties. The thresholds exist for every `t>0`, but
global optimality above is asserted only in (1).

The mechanism in (9) is elementary concavity: `f` is a sum of concave
powers and `G′=(F+2)f″<0`. It is used as a lemma, not as a claim to a
new general single-crossing principle. For any nonbinary fixed score
vector in `[0,1]^n`, `n≥2`, the same calculation replaces `2` by `n−1`.
A unique positive crossover against the unit-simplex vertex exists
exactly when the score sum exceeds one. Binary vectors require separate
handling.

### The three-agent witness is an exact global solution

At every matched `t=τ>0`, (8) places the problem strictly in the intermediate
phase, so

\[
 R_{\rm het}(t,t)=\frac{a E^a+b E^b}{E^a+E^b+1}.
 \tag{10}
\]

Exactly 18 labeled allocations maximize the reward: choose the majority
task, minority task and minority agent. At `t=τ=log2` the earlier
`(2,1,0)` witness is therefore globally optimal, with exact optimal gap

\[
 \Delta R=\frac{3\,2^{4/5}-5}{10(2^{4/5}+\sqrt2+1)}
 >\frac1{295}.
\]

This promotes a lower-bound example to an exact optimum. It does not
establish an optimum formula outside (1).

### Exact fixtures for all three phases

Keep `t=log2` and take `τ=10log q`. For each rational `q` below, all three
candidate rewards are rational: `e^{τa}=q^8`, `e^{τb}=q^5` and
`e^τ=q^10`. The checker compares the original quotients exactly.

| `q` | Unique optimal occupancy type |
|---|---|
| `21/20` | `(1,1,1)` |
| `15/14` | `(2,1,0)` |
| `11/10` | `(3,0,0)` |

All fixtures are inside (1), since `0<10log q<10(q−1)≤1`. The purity
proof supplies globality; the rational comparisons supply reproducible
values for the three regimes.

## Verification and originality scope

Two independent mathematical reviews checked the derivative identities,
positive-gradient conditions at maxima, budget exhaustion, stationary
transfer argument and grouping consequences. The three-agent thresholds
were also independently checked. The analytic proofs establish
the continuous statements; finite arithmetic checks only supplement them.

Run the credential-free standard-library checker:

```sh
python3 -m research.spikes.stochastic.softmax_integrality
```

It checks 4,860 directional first- and second-derivative identities by
independently dividing exact quadratic series, including curvature equality
and coordinate-derivative signs. The initial weights in these algebraic
checks are arbitrary positive rationals; they are not presented as exact
softmax weights at the sampled coordinates. It also checks 3,120 fixed-score
comparison cases, 297 stationary-transfer identities through independent
quadratic composition, 108 sampled curvature inequalities and 21
zero-row endpoint identities. It verifies the three phase fixtures,
all 27 pure three-agent assignments and the radical lower-gap certificate.
The combined stochastic
verifier includes these checks in CI. No finite grid establishes the
arbitrary-dimensional theorem or its continuous equality cases.

The result sharpens the lower-bound analysis in Amir, Bettini and Prorok's
[current paper](https://arxiv.org/html/2506.09434v4). Its original exactness
conjecture was present in [v1](https://arxiv.org/pdf/2506.09434v1) and omitted
from v2 onward. The current lower bounds remain valid. No inspected passage
supplies the stated purity region or exact three-agent classification;
this is a bounded source comparison, not first-discovery priority.

Second-order necessary conditions, AM–GM, Taylor expansion and
concave-quotient comparison are standard ingredients. The crossover
also follows from the classical bounded-variance inequality and exponential
tilting: `d B_τ(s)/dτ=Var_τ(s)<B_τ(s)(1−B_τ(s))` for nonbinary scores,
so `logit(B_τ(s))−τ` decreases. The inequality and its equality condition
are stated in the introduction, Equation (1.3), of
[Lim and McCann](https://arxiv.org/html/2001.11851v1), crediting Bhatia and
Davis. The single-crossing consequence here is our derivation from that
standard ingredient.

The older weighted-average wirelength literature studies the same
exponential weighted mean. The recovered [2013 original](https://cc.ee.ntu.edu.tw/~ywchang/Papers/tcad13-3D-placement.pdf),
printed pages 500–502, Section IV-A.2–3 and Theorems 1–2, identifies that
mean and its positive-minus-negative wirelength surrogate. Its inspected
mathematical results concern approximation error; they do not state the
bounded convexity condition or nested allocation result. Inspected passages in
[Liao's 2024 thesis](https://www.cse.cuhk.edu.hk/~byu/papers/PHD-thesis-2024-Peiyu-Liao.pdf),
Sections 3.1.2 and 3.1.4 and the comparison on printed page 20, discuss the
nonconvexity of the positive-minus-negative-temperature surrogate. They
do not state (1). The original 2011 paper remains unread, and broader
first priority for the curvature range is not established.
The [novelty ledger](novelty-ledger.md) records inspected sources and gaps.
No small-model origination, token-efficiency or learned-policy claim is made.
