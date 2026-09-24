# Certified optimization after the purity theorem

The [purity theorem](softmax-integral-optima.md) turns continuous nested
Boltzmann allocation into an integer grouping problem whenever `t≤2` or
`τ≥t/4`, with both temperatures positive. This includes the entire matched
positive line. We can therefore compute a grouping with a rigorous bound
on its distance from the global continuous optimum, without running a
continuous numerical optimizer or a language model.

The optimization mechanism is classical fractional programming and
exact-budget dynamic programming. The candidate mathematical contribution
is the structural reduction that makes those tools apply to this continuous
model. Neither the recurrence, bisection nor interval arithmetic is claimed
as a new general algorithm. Wider priority for the reduction remains open.

## Occupancy reduction and threshold oracle

There are `N` agents and `M` tasks. A pure full-budget allocation has positive
group sizes `π=(m₁,…,m_k)`, with `Σm_i=N` and `k≤K=min(N,M)`. Write

\[
 E=e^t,\quad s_m=\frac{mE}{mE+N-m},\quad
 w_m=e^{\tau s_m},\quad a_m=s_mw_m,\quad b_m=w_m-1.
\]

Each empty task contributes denominator weight one. Thus

\[
 R_\pi=\frac{A_\pi}{B_\pi},\qquad
 A_\pi=\sum_{m\in\pi}a_m,\qquad
 B_\pi=M+\sum_{m\in\pi}b_m\ge M>0.
 \tag{1}
\]

For a threshold `ρ`, use the item profit `f_m(ρ)=a_m−ρb_m`. Then

\[
 \Phi(\rho)=\max_\pi(A_\pi-\rho B_\pi)
           =\max_\pi\sum_{m\in\pi}f_m(\rho)-M\rho.
 \tag{2}
\]

The sign of `Φ(ρ)` is the sign of `R_*−ρ`, where `R_*` is the best pure
reward. Indeed every residual is `B_π(R_π−ρ)` and every denominator is
positive. The finite maximum `Φ` is continuous, strictly decreasing and
piecewise affine, with unique zero `R_*`. No concavity of the original
continuous objective is assumed.

If `M≥N`, the group cap is automatic. The exact-budget recurrence is

\[
 D[0]=0,\qquad D[b]=\max_{1\le m\le b}\{D[b-m]+f_m(\rho)\}.
 \tag{3}
\]

Then `Φ(ρ)=D[N]−Mρ`. The recurrence considers ordered compositions,
but their order does not affect profit, feasibility or reward. Backpointers
recover one grouping; arbitrary deterministic choices among exact ties are
valid. One query needs `O(N²)` additions/comparisons and `O(N)` storage.

If `M<N`, retain the number of groups:

\[
 D[0,0]=0,\qquad
 D[k,b]=\max_m\{D[k-1,b-m]+f_m(\rho)\},\qquad
 \Phi(\rho)=\max_{1\le k\le K}D[k,N]-M\rho.
 \tag{4}
\]

Only feasible exact-group predecessors participate. This costs
`O(KN²)` operations and `O(KN)` value/backpointer storage per query.
All agents must be assigned even if profits are negative; replacing an
infeasible state or a negative optimum by zero changes the problem.

## A certificate that retains a feasible witness

Start with the concentration grouping `(N)`, a certified lower bound `L`
on its reward, and `U=1`. At each midpoint `ρ=(L+U)/2`, use the threshold
oracle and evaluate the recovered grouping. Retain the grouping with the
best certified reward lower bound.

With exact supplied coefficients, a positive residual gives a feasible
reward above `ρ`, and a negative residual proves `R_*<ρ`. Each nonterminal
step halves the bracket. After at most `⌈log₂(1/ε)⌉` steps, `[L,U]`
has width at most `ε`. The retained grouping has reward at least `L`,
so its additive regret is at most `U−L`.

The last queried grouping need not have the best ratio: at an upper
threshold the residual oracle can prefer a worse ratio with a smaller
denominator. Keeping the best feasible witness is essential.

The resulting bounds, **after real coefficients are supplied**, are
`O(N² log(1/ε))` arithmetic/comparison operations for `M≥N` and
`O(KN² log(1/ε))` otherwise. These are not unconditional bit-complexity
bounds for arbitrary real temperatures or polynomial bounds in `log N`
when population size is a compressed binary multiplicity.

## Rigorous exponential and comparison bounds

The [implementation](../research/softmax_partition.py) accepts rational
positive temperatures. It uses no floating-point exponentials. For rational
`x≥0`, divide by a power of two until `y≤1`. If `T_d(y)` is the Taylor
sum through degree `d`, the positive remainder satisfies

\[
 0\le e^y-T_d(y)
 \le \frac{y^{d+1}/(d+1)!}{1-y/(d+2)}.
 \tag{5}
\]

The ratio of each subsequent term to its predecessor only decreases, so
the geometric tail bounds the entire remainder. All calculations use exact
fractions. Round the endpoints outward to dyadic rationals, then square
and round outward to undo the scaling. Monotonicity of the score in `E`
and of the exponential gives enclosing intervals for every `a_m,b_m`.

For `ρ∈[0,1]`, the lower item profit is `a_m^-−ρb_m^+` and the upper
profit is `a_m^+−ρb_m^-`. Run the exact DP separately on these endpoints,
obtaining residual bounds `δ^-≤Φ(ρ)≤δ^+`. The lower-DP path itself has
true residual at least `δ^-`, even when interval errors change the selected
path. The max operation is monotone, so rounded comparisons need not guess
the exact maximizing path.

Uniformly across all queries,

\[
 \delta^+-\delta^-
 \le \eta:=K\max_m\{(a_m^+-a_m^-)+(b_m^+-b_m^-)\}.
 \tag{6}
\]

This follows by bounding the interval width of every feasible path, which
has at most `K` items, then taking maxima. The implementation refines
coefficient precision until `η≤εM/4`.

If both residual endpoints have the same strict sign, the usual bisection
step is certified. If `δ^-≤0≤δ^+`, positivity of all denominators gives

\[
 R_*\le\rho+\delta^+/M,\qquad
 R_{\text{lower-DP path}}\ge\rho+\delta^-/M.
 \tag{7}
\]

Their gap is at most `η/M≤ε/4`, so the algorithm can stop with a certificate
even at an exact tie. It does not need to decide an arbitrary transcendental
equality. Direct outward evaluation of the witness and the previous bracket
can further tighten these bounds.

The executable admits dimensions `1…128`, temperatures at most `32`,
epsilon in `[2^-40,1]`, and temperature/epsilon numerators and denominators
of at most 64 bits. A conservative eight-million-transition cap is checked
before exponential work; some large rectangular requests are rejected.
Coefficient precision is bounded by 256 bits and each Taylor evaluation
by 1,024 terms. Reaching a cap raises an error without returning a certificate.
The unbounded analytic theorem and these deliberately bounded executable
limits are different statements.

Outside the proved purity region, the same algorithm still certifies the
best **pure** reward and returns a feasible continuous allocation. Its upper
bound then applies only to the pure class; the output says `pure-only`.
It does not imply an upper bound for fractional allocations there.

## Reproduction and finite results

From the repository root:

```sh
python3 -m research.softmax_partition --agents 16 --tasks 16 --inner 1 --outer 1 --epsilon 1/100000000
python3 -m unittest research.test_softmax_partition_dp research.test_softmax_partition
python3 -m research.spikes.softmax_partitions.experiment --out research/spikes/context/runs/softmax-partition-study
```

Choose a new output directory for every experiment. The fixed
[protocol](../research/spikes/softmax_partitions/protocol.json) and
[driver](../research/spikes/softmax_partitions/experiment.py) record exact
input rationals, source hashes, reward brackets, groupings, operation counts
and observed timings. A failed run preserves completed cases and its failure.
There are no external model calls or credentials.

The initial 20-case run passed with certified additive regret below `10^-8`
in every case. For populations through 16, an independent partition
enumeration compared all alternatives using the same coefficient enclosures.
All 16 such cases certified a unique optimal occupancy pattern within the
reported scope, over 1,104 enumerated partitions in total. “Unique” concerns
group sizes; label permutations remain equivalent. Larger cases have the
additive certificate and no uniqueness claim.

| Agents = tasks | Matched temperature | Returned grouping | Guarantee |
|---|---:|---|---|
| 9 | 1/10 and 1 | (5,4) | Unique globally optimal occupancy |
| 9 | 3 and 8 | (3,3,3) | Unique globally optimal occupancy |
| 16 | 1/10 | (8,8) | Unique globally optimal occupancy |
| 16 | 1 | (6,5,5) | Unique globally optimal occupancy |
| 16 | 3 and 8 | (4,4,4,4) | Unique globally optimal occupancy |
| 64 | 1/10 | (32,32) | Continuous regret < 10^-8 |
| 64 | 1 | (22,21,21) | Continuous regret < 10^-8 |
| 64 | 3 | (11,11,11,11,10,10) | Continuous regret < 10^-8 |
| 64 | 8 | Eight groups of eight | Continuous regret < 10^-8 |

In particular, the 16-agent computation certifies an intermediate three-group
regime between the small-temperature two-group and large-temperature
four-group regimes. At `t=τ=1`, its reward exceeds every different occupancy
pattern by at least `631069/4294967296 > 1/7000`, using outward rational
enclosures. It does not locate every transition or prove that group
count changes monotonically. The separate `N=M=9,t=8,τ=1/4` case certifies
the permutation grouping **only among pure allocations**. Rectangular and
one-task cases are also retained.

The 20 solver calls took about 3.14 seconds in one Python 3.14.6 run on the
investigator's machine. This excludes the exhaustive comparison phase and
is an observation, not a benchmark against another solver. The study uses
investigator-selected cases, no held-out selection and no inference calls.
Neither its runtime nor the bounded worker's implementation of supplied
formulas demonstrates cheap-model theorem origination or token efficiency.

Focused tests compare the core DP with 466 independent exhaustive rational
cases. The solver tests include 18 exact comparisons against an unscaled
Taylor enclosure, a separate high-precision Decimal exponential oracle,
exhaustive reward comparisons, the temperature/epsilon boundary, and
synthetic exact-zero and nonzero ambiguous-residual cases. The synthetic
fixtures exercise control flow and are not Boltzmann data. Initial worker
test failures, a repaired infeasible DP predecessor, and the CLI admission
issue found by independent review are retained in the local attempt records.

## Prior art and remaining priority

[Megiddo (1979), Section 2](https://theory.stanford.edu/~megiddo/pdf/rational.pdf)
already converts additive combinatorial optimization into optimization of a
positive-denominator affine ratio. Our occupancy counts satisfy its model.
The threshold transformation is therefore established prior art; this
implementation uses bisection rather than Megiddo's exact parametric search.
The publisher abstract for [Dinkelbach (1967)](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.13.7.492)
credits the underlying parametric equivalence to
[Jagannathan (1966)](https://pubsonline.informs.org/doi/10.1287/mnsc.12.7.609).
Those two original article bodies remain unread. No Dinkelbach-iteration
convergence claim is needed here.

The inspected softmax model, Theorems 3.1–3.4 and Appendix G.4 of
[Amir–Bettini–Prorok v4](https://arxiv.org/html/2506.09434v4)
give endpoint lower bounds without this purity reduction or occupancy solver.
This is a bounded source comparison. Broader nonlinear allocation and
group-formation literature, the exact-model citation neighborhood and the
purity theorem's global priority remain unresolved. The
[novelty ledger](novelty-ledger.md) preserves those distinctions.
