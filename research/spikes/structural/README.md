# Weighted tree resilience: exact structural results

These are mathematical results for the laboratory's random-failure objective,
not claims of resilience in a physical network or established literature novelty.
They were developed after inspecting the objective. The finite searches are
development data, not holdout evidence about a learned proposal policy.

Consider a labeled tree on `n` vertices with positive node values `v_i` and
failure weights `w_i`. At each step, remove a surviving vertex with probability
proportional to its weight. Service is the largest surviving component's value,
divided by initial total value `V`. Let `W` be total failure weight. Integrate
service using the existing trapezoidal AUC over `h` removals.

## One removal: a linear-time exact optimizer

For arbitrary positive values and failure weights, an optimal tree for one
removal is a star. An optimal hub minimizes

`w_c (V - v_c - max_{j != c} v_j)`.

Its exact expected AUC is

`1 - [sum_i w_i v_i + min_c w_c(V-v_c-max_{j != c} v_j)] / (2WV)`.

The two largest values suffice to evaluate every candidate hub in linear time.
This is a deterministic optimizer over all labeled trees, not a heuristic that
merely compares a selected sample of trees.

Proof. A positive-value tree has a value-weighted centroid `a`: each component
after removing `a` has value at most `V/2`. Root the tree at `a` and let `b` be
the child with largest subtree value. At every other vertex, the component
toward `a` has value at least `V/2`, while every component away from `a` has value
strictly below `V/2`. It is therefore the unique largest component.

Cut edge `ab`, producing two rooted trees with roots `a` and `b`. The unnormalized
expected fragmentation loss of the original tree is

`D(T) = sum_{j not in {a,b}} v_j sum_{i on the root-to-parent(j) path} w_i`.

This counts each vertex value whenever deleting one of its ancestors leaves it
outside the largest surviving component. In particular,

`D(T) >= min(w_a,w_b) (V-v_a-v_b)`.

Choose `c` as the lighter-weight member of `{a,b}`. The star centered at `c`
has loss `w_c(V-v_c-max_{j != c}v_j)`, which is at most this lower bound because
the maximum includes the other member of `{a,b}`. Thus some star dominates
every tree. The removed vertex's own value is graph-independent, yielding the
stated AUC formula.

## Every horizon: an aligned hub is optimal

If a vertex `c` has both minimum failure weight and maximum value, the star at
`c` maximizes expected service at every removal count, and hence every positive
linear combination of those counts, including the laboratory AUC. Ties are
allowed. If `c` has strictly smallest weight, this star is the unique optimum
for every permitted AUC horizon `1 <= h <= n-2`.

Proof. Root an arbitrary competing tree at `c`. For survivor set `A`, let
`M(A)` be its maximum individual value and let `L_T(A)` be its largest component
value. Every surviving component has a topological root; its other vertices
can each be charged to their live parent edge. Therefore

`L_T(A) <= M(A) + sum_{j != c} v_j 1[{parent(j),j} subset A]`.

Write `q_k(i,j)` for the probability that both vertices survive `k` removals.
Weighted sequential removal has an exponential-clock representation:
independent clocks of rates `w_i`, with the earliest clocks removed first.
The event that two selected vertices are among the last `n-k` clocks is
increasing in either selected clock and decreasing in an unselected clock.
Couple two systems by sharing unit-rate exponential draws and swapping the
weights of `c` and `parent(j)`. Lowering the selected vertex's weight lengthens
its clock; raising the unselected vertex's weight shortens its clock. Thus
`q_k(c,j) >= q_k(parent(j),j)`.

Taking expectations in the component bound gives

`E L_T <= E M + sum_{j != c} v_j q_k(parent(j),j)`

`        <= E M + sum_{j != c} v_j q_k(c,j) = E L_star(c)`.

The final equality holds pointwise: if `c` survives it is a maximum-value
vertex and connects every survivor; otherwise the star leaves only isolates.
At the first removal, `q_1(c,j)-q_1(i,j)=(w_i-w_c)/W`. If `c` is the unique
minimum-weight vertex, any non-star tree has an edge with parent other than
`c`, making the expectation comparison strict already at this step.

The same proof provides an exact nonnegative gap decomposition into the
expected slack of the component bound and
`sum_{j != c} v_j[q_k(c,j)-q_k(parent(j),j)]`.

Consequences include uniform failure with arbitrary values (use a maximum-value
hub), and uniform values with arbitrary failure weights (use a minimum-weight
hub). The condition concerns a common extremal vertex. Separate extrema do
not give the same conclusion.

## Two removals: stars can be strictly suboptimal

A smallest-size counterexample within the instrument's admitted node range is

```text
weights = [1, 1, 2, 5]
values  = [1, 1, 4, 4]
horizon = 2
edges   = [[0,1], [0,2], [2,3]]
```

All entries lie in the registered environment generator's `1..5` range, and
both profiles satisfy its spread guard. Exhausting all 16 labeled trees and
all weighted removal orders gives:

| Design | Exact expected AUC |
| --- | ---: |
| Shown path, globally optimal among trees | `12937/20160` |
| Best star, hub 2 | `6467/10080` |
| Strict improvement | `1/6720` |

There are exactly two optimal labeled trees, obtained by swapping the identical
vertices 0 and 1. The improvement is about `0.00014881` AUC. This is an exact
counterexample and small-domain optimum, not evidence of broad practical
superiority or that randomization improves a deterministic design optimizer.
Four is the smallest graph size admitted by the laboratory; no claim is made
about a new graph-theoretic notion of minimality.

## A complete four-vertex phase diagram

For the symmetric family `weights=(r,r,1,1)`, `values=(x,x,1,1)`, with real
`r>=1`, `x>=2`, and two removals, call the first two vertices H and the others L.
Let `q_HH`, `q_LL`, and `q_HL` be the survival probabilities of one particular
pair of each type:

```text
q_HH = 1 / [(r+1)(2r+1)]
q_LL = r^2 / [(r+1)(r+2)]
q_HL = 3r / [2(r+2)(2r+1)]
```

Define `C=4V(ceiling-AUC)`, where the ceiling is the graph-independent AUC if
every surviving vertex stayed connected. Exhausting the six tree classes
under interchange of like vertices gives the following costs:

| Tree class | Multiplicity | Cost |
| --- | ---: | --- |
| Star at H | 2 | `C_H=2r/(r+1)+2q_HL+q_LL` |
| Star at L | 2 | `C_L=(x+1)/(r+1)+x q_HH+2q_HL` |
| Path HHLL, in path order | 4 | `C_P=(2r+1)/(r+1)+3q_HL` |
| Path LHHL | 2 | `C_H` |
| Path HLLH | 2 | `C_L+(x-1)/(r+1)` |
| Path HLHL | 4 | `C_L+(r-1)/(r+1)+q_LL-q_HL` |

The last two rows are dominated by the L star: `x>=2`, `r>=1`, and
`q_LL>=q_HL`. Thus the global optimum is exactly `min(C_H,C_L,C_P)`.
The HHLL path beats every star exactly when

```text
r > (9 + sqrt(145))/8
x > r(2r+1)/(r+1) + 3r/[4(r+2)].
```

For integer parameters, these conditions simplify to `r>=3` and `x>=2r`.
The first member is `r=3,x=6`: the path AUC is `4941/7840`, the best-star AUC
is `4931/7840`, and the improvement is exactly `1/784`. This symmetric family
uses values outside the registered generator's `1..5` range but remains within
the instrument's allowed `1..99` range when its parameters obey those bounds.
The preceding asymmetric example establishes the failure within `1..5`.

## Reproduction and limits

Run `python3 research/spikes/structural/verify.py`. It uses only the Python
standard library, integer arithmetic, and exact rational arithmetic. It checks
the one-removal optimizer over all 6,561 profiles with four vertices and
entries in `1..3`; checks all 125 five-vertex trees for three aligned profiles
and three horizons; verifies 90 members of the phase-diagram family; and
cross-checks the subset calculation against an independently implemented
weighted-order enumeration on all 16 trees for four profiles and two horizons.

`tree_search.py` is the retained development search. The commands
`python3 research/spikes/structural/tree_search.py 4 3` and `... 5 3` found no
counterexample among 6,561 and 59,049 environments respectively. The command
`... 4 5` found the displayed asymmetric example after 11,260 environments,
then stopped; it did not exhaust the full `1..5` grid. Negative finite searches
are not proofs. The proofs above establish the stated general results.

No literature-priority claim, measured proposal-policy advantage, token-cost
advantage, or result outside the declared tree objective follows from these
certificates. These findings motivate using exact structural baselines to
avoid spending proposal budgets rediscovering solved subcases.
