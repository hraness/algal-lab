# Exact constrained Boltzmann allocation by minimum-cost flow

A nonconcave additive task-allocation objective has an exact flow formulation.
It permits different task weights and positive temperatures, agent–task
eligibility restrictions, integer task capacities, and arbitrary linear
assignment rewards. With at least two agents, every maximizing allocation is
binary: each agent either chooses one task or abstains. This follows from the
strict contact set of the [one-column concave envelope](softmax-additive-boundary.md),
not from convexity of the smooth objective.

The flow algorithm and integrality theorem are classical. The candidate
contribution is the exact reduction for this Boltzmann objective and the
exclusion of every fractional optimum. The inspected sources do not state
this application; worldwide priority remains unresolved.

## Model and result

Let `N,M≥1` be finite integers, `F` an arbitrary set of eligible agent–task
pairs, and `b_j∈{0,…,N}` the capacity of task `j`. A feasible matrix satisfies

\[
 a_{ij}\ge0,\quad a_{ij}=0\text{ for }(i,j)\notin F,\quad
 \sum_j a_{ij}\le1,\quad \sum_i a_{ij}\le b_j.
 \tag{1}
\]

Each task has finite real parameters `t_j>0,w_j>0`; each eligible pair has a
finite real reward `c_ij`, which may be negative. Maximize

\[
 J(A)=\sum_j w_j
 \frac{\sum_{i=1}^N a_{ij}e^{t_j a_{ij}}}
      {\sum_{i=1}^N e^{t_j a_{ij}}}
 +\sum_{(i,j)\in F}c_{ij}a_{ij}.
 \tag{2}
\]

Every denominator retains all `N` coordinates, including ineligible agents'
zero efforts. Removing those coordinates would change the model.

**Theorem.** The minimum cost of a value-`N` flow in the network below
equals `−max J`, and every integral minimum-cost flow projects to a
maximizer of (2). If `N≥2`, every maximizing matrix is binary,
including at ties. An optimal row can be all zero: arbitrary linear rewards
do not imply full budgets. If `N=1`, an integral optimum still exists, but
fractional optima may tie.

## Standard flow construction

Put `E_j=e^(t_j)` and

\[
 s_{j,k}=\frac{kE_j}{N+k(E_j-1)},\qquad
 m_{j,k}=w_j(s_{j,k}-s_{j,k-1})
 =\frac{w_jNE_j}
 {(N+(k-1)(E_j-1))(N+k(E_j-1))}.
 \tag{3}
\]

Use a source, one vertex per agent, one per task, and a sink. Send `N` units
of flow through these unit-capacity arcs:

| Arc | Cost | Purpose |
|---|---:|---|
| Source to agent `i` | `0` | Route each agent's unit |
| Agent `i` to sink | `0` | Allow abstention |
| Agent `i` to task `j`, for `(i,j)∈F` | `−c_ij` | Assign eligible effort |
| Task `j` to sink, one parallel arc for each `k=1,…,b_j` | `−m_(j,k)` | Reward successive occupied slots |

There are `N+M+2` vertices and `2N+|F|+Σ_j b_j` forward arcs. Task marginal
rewards strictly decrease, so their costs increase. The all-abstention flow
is always feasible, even if all task capacities are zero or some agents have
no eligible task.

### The network represents the concave upper bound

Let `φ_j` interpolate `(k,s_(j,k))`. The envelope theorem gives

\[
 J(A)\le\overline J(A)
 :=\sum_j w_j\phi_j\left(\sum_i a_{ij}\right)
   +\sum_{(i,j)\in F}c_{ij}a_{ij}.
 \tag{4}
\]

For `N≥2`, this inequality is strict at every nonbinary feasible `A`,
because the column holding a fractional entry has `w_j>0` and `t_j>0`.

Given any feasible `A`, route `a_ij` along its assignment arcs and route
`1−Σ_j a_ij` along the abstention arc. At task `j`, fill the first
`floor(S_j)` slot arcs and the fractional part of the next, where
`S_j=Σ_i a_ij`. This flow has cost `−overline J(A)` by telescoping (3).

Conversely, any flow of value `N` projects to a feasible `A`: its `N` unit
source arcs are all saturated, so conservation at agent `i` gives
`Σ_j a_ij≤1`. At fixed task outflow,
using the cheapest slot arcs first minimizes cost. This gives exactly
`−w_j φ_j(S_j)`; any other slot choice costs at least as much. Therefore

\[
 \min\{\text{network cost}\}=-\max_A\overline J(A).
 \tag{5}
\]

This is the standard parallel-arc representation of a separable piecewise
linear convex cost. It applies to fractional flows as well as integer flows.

### Exactness and all maximizers

The bounded flow polytope has an integral optimal vertex because its incidence
matrix is totally unimodular and its supplies and capacities are integral.
This vertex property does not require the objective coefficients to be
rational. Its projected assignment `A*` is binary, so the envelope and
original objective coincide there:

\[
 \max_A J(A)\le\max_A\overline J(A)
 =\overline J(A^*)=J(A^*)\le\max_A J(A).
 \tag{6}
\]

All terms are equal. If another maximizing `A` were fractional, strictness
in (4) would imply `overline J(A)>max overline J`, a contradiction.
This excludes every fractional optimum of the smooth problem. The network
relaxation itself can have fractional tied optima; the theorem does not say
otherwise.

## Exact rational implementation

The [bounded implementation](../research/softmax_additive_flow.py) accepts
`E_j=e^(t_j)>1` directly as exact rationals, along with rational weights and
edge rewards. Thus every slot cost and reported optimum is rational. For
example `E_j=2` means `t_j=log 2`; a rational temperature is generally a
different input model. No exact finite-bit claim for arbitrary real
temperatures follows from the structural theorem.

The API admits `1…24` agents and tasks, capacities `0…N`, and exact integers
or `Fraction` values with numerator magnitude and denominator at most 16 bits.
All input containers are tuples; eligible pairs must be unique. Floats and
booleans are rejected. It uses at most 50 vertices, 1,200 forward arcs and
24 unit augmentations. The certificate verifier bounds each rational output
at 8,192 bits and runs no optimization.

The implementation uses classical successive shortest augmenting paths and
returns an assignment plus residual vertex potentials. A potential `π` with
`cost(u,v)+π_u−π_v≥0` on every residual arc certifies optimality: every
residual cycle then has nonnegative cost, and the difference from any feasible
flow of the same value `N`, which is the maximum value, decomposes into such
cycles.
Feasibility, the exact original
objective, and the residual inequalities are checked separately from the
search. The theorem supplies the final continuous upper-bound justification.

```python
from fractions import Fraction as Q
from research.softmax_additive_flow import maximize_additive_softmax

result = maximize_additive_softmax(
    3,
    (1, 2),                         # task capacities
    (Q(2), Q(3)),                   # exp(inner temperature)
    (Q(1), Q(2)),                   # task weights
    ((0, 0, Q(0)), (0, 1, Q(-1, 5)),
     (1, 0, Q(1, 4)), (1, 1, Q(0)), (2, 1, Q(-3))),
)
print(result)
```

The unique assignment is agent `0` to task `1`, agent `1` to task `0`, and
agent `2` unassigned. Its exact value is `7/4`. The third agent's zero effort
still contributes one to both softmax denominators.

```sh
python3 -m unittest research.test_softmax_additive_boundary research.test_softmax_additive_flow
```

The envelope tests use independent Decimal evaluation. The flow tests compare
80 fixed small profiles against exhaustive eligible assignments, including
abstention, and independently inspect certificate inequalities. Additional
tests enumerate feasible half-step allocations with `E=4,9`, for which every
continuous reward is exactly rational, and check strict gaps at fractional
matrices. They also exercise residual reassignment, empty eligibility, zero
capacities, one-agent ties, malformed certificates, and the largest admitted
network. These finite checks
corroborate the proof and implementation; they establish no runtime or
model-efficiency advantage.

## Scope boundaries

Positive task weights and temperatures, at least two denominator coordinates,
and integer capacities support the all-maximizer statement. At `N=1`,
`t_j=0`, or zero task weight, the same flow construction can retain an
integral optimum while fractional ties return. The implementation admits
`N=1` with only an integral-witness guarantee; zero temperatures and weights
are outside its input contract.

Integer task capacities are material: with `N=2,M=1,b_1=1/2`, positive
weight and no linear reward, a fractional feasible allocation has positive
value while the only binary feasible allocation is zero. Negative task
weights, unequal agent budgets, and unrelated side constraints require
separate analysis. This flow formulation is for an additive outer reward,
not the positive-outer-temperature solver's nonlinear reward.

## Literature comparison

The classical parallel-arc expansion is stated explicitly in
[Ahuja, Hochbaum and Orlin (2003), Section 4](https://hochbaum.ieor.berkeley.edu/html/pub/AHO-MS2003.pdf).
The integral-flow existence result is standard; see the exposition in
[Goemans's network-flow notes, Theorem 1](https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2008/4064d889e5033a9915327a777d12b592_notes_flow.pdf).
The real-cost version used in the proof follows from the same integral
polytope. The shortest-path method and residual certificate are also
established tools, not algorithmic novelty claims.

[Amir, Bettini and Prorok, v4](https://arxiv.org/html/2506.09434v4), Sections
2–3, already allow task-specific aggregators and instantiate the nested
Boltzmann objective. Their inspected softmax theorem gives square-population
value lower bounds. It does not state this constrained exact-flow reduction
or all-maximizer result. Task-specific aggregators alone are therefore not a
new generalization. The [envelope note](softmax-additive-boundary.md#prior-art-and-claim-boundary)
credits the underlying probability geometry and known gap constants.

The specific smooth-to-flow application was not located in the bounded
primary-source packet. That supports a source-relative contribution, not a
claim that no equivalent theorem exists elsewhere. The
[novelty ledger](novelty-ledger.md) preserves this distinction.
