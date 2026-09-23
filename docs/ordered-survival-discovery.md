# Ordered joint survival and probability-free pairing

We derived a four-point inequality for joint inclusion under successive
weighted sampling. It holds at **every fixed sample size**, not only the final
two-survivor endpoint. It yields an exact pairing algorithm that only sorts
failure rates: adjacent rates for pairs that require both members, and opposite
ends for redundant pairs that require either member. No inclusion probabilities
need to be calculated to choose either optimum.

The result below is proved within the model and independently checked. Its
literature priority remains unresolved. The narrow candidate contribution is
the four-point ordering for second-order inclusion probabilities of successive
sampling. The probability representation and the matching exchange argument
have established precedents.

## Model and theorem

There are `n` vertices with positive real rates `w_i`. At each deletion, choose
a remaining vertex with probability proportional to its rate. Let `q_ij(k)` be
the probability that both `i,j` remain when exactly `k` vertices survive.
Equivalently, assign independent exponential clocks of rates `w_i` and retain
the `k` largest clocks. All probabilities refer to the original population.

For any four distinct vertices with `w_a <= w_b <= w_c <= w_d`, and every fixed
`0 <= k <= n`,

\[
q_{ab}(k)+q_{cd}(k)\ \ge\ q_{ac}(k)+q_{bd}(k)\ \ge\ q_{ad}(k)+q_{bc}(k).
\]

Both inequalities are strict when the four rates are strictly ordered and
`2 <= k <= n-2`. At `k=0,1,n-1,n` both are equalities. Tied rates can create
additional equalities. This is an additive statement; multiplicative total
positivity does not follow.

## Proof

For `t>0`, define

\[
 f_i=\frac{1}{e^{w_i t}-1},\qquad g_i=w_i f_i,\qquad
 P=\prod_i(1-e^{-w_i t}).
\]

Both `f_i` and `g_i` decrease as `w_i` increases. For a set `A`, let `e_j(A)`
be the degree-`j` elementary symmetric polynomial in its `f_i`, and put
`E_r(A)=sum_{j=0}^r e_j(A)`. Use `e_0=1`, `e_j=0` outside `0..|A|`, and
`E_r=0` for `r<0`.

Write `m=k-2` for `k>=2`. Conditional on the smaller of clocks `i,j` being
`t`, both survive if at most `m` other clocks exceed `t`. Independence gives

\[
 q_{ij}(k)=\int_0^\infty P(t)
       (g_i f_j+f_i g_j)E_m([n]\setminus\{i,j\})\,dt. \tag{1}
\]

Fix the four vertices and let `R` contain all other vertices. For the first
four-point difference put `F=(f_a-f_d)(f_b-f_c)`; for the second put
`F=(f_a-f_b)(f_c-f_d)`. In either case, define `T_0` by replacing one `f`
difference at a time by its corresponding `g` difference and adding:

\[
\begin{aligned}
T_0^{(1)}&=(g_a-g_d)(f_b-f_c)+(f_a-f_d)(g_b-g_c),\\
T_0^{(2)}&=(g_a-g_b)(f_c-f_d)+(f_a-f_b)(g_c-g_d).
\end{aligned}
\]

Thus `F,T_0>=0`. Expand (1) over the complementary two members of the
quartet. In each complementary-pair term, the coefficient multiplying
`E_(m-2)(R)` is `(product_quartet f_i)(w_i+w_j)`. Its signed sum is zero
because every quartet rate occurs once on each side. The remaining integrand is

\[
 P\{T_0 E_m(R)+T_1 E_{m-1}(R)\}, \tag{2}
\]

where direct expansion, using `f_i'=-w_i f_i(1+f_i)`, gives

\[
 T_0+T_1=-F'-F\sum_{i\in\{a,b,c,d\}}g_i.
\]

Since `P'/P=sum_i g_i`, integrate (2) by parts and use
`E_m-E_(m-1)=e_m`. The four-point difference is exactly

\[
 \int_0^\infty P\left[
 T_0 e_m(R)+F\sum_{r\in R}g_r e_{m-1}(R\setminus\{r\})
 \right]dt. \tag{3}
\]

For completeness, the second term follows from

\[
 E_{m-1}'(R)+E_{m-1}(R)\sum_{r\in R}g_r
 =\sum_{r\in R}g_r e_{m-1}(R\setminus\{r\}).
\]

The boundary term `PF E_(m-1)(R)` vanishes: near zero it is
`O(t^(n-m-1))`, at least `O(t)` for `k<=n`, and at infinity it decays
exponentially. Every term in (3) is nonnegative. Strictly ordered rates make
`T_0>0`; for `2<=k<=n-2`, `0<=m<=|R|`, so `e_m(R)>0`. At `k=n-1,n` (3)
is zero; at `k=0,1` all pair probabilities are zero. This proves the theorem.

## Two exact algorithms

Partition an even population into equal-value pairs. The objective is the
**expected number of working pairs**, which is separate from largest-component
service in `network.v2` and the earlier tree studies.

For a pair that requires **both** members, expected service is
`sum_(ij in M) q_ij(k)`. Sort the vertices by rate and pair adjacent vertices.
If the two smallest rates currently have different partners, the four-point
inequalities allow exchanging those two pairs for the adjacent pair and the
pair of their former partners without reducing service. Induction proves
optimality.

For a pair that requires **either** member, expected service is
`sum_i Pr(i survives) - sum_(ij in M) q_ij(k)`. The first term is independent
of the pairing. Pair the smallest rate with the largest, then recurse. An
exchange using the same inequalities minimizes the pair-probability sum and
therefore maximizes redundant-pair service.

Both algorithms use `O(n log n)` comparisons, `O(n)` storage, and **zero
probability evaluations**. The same pairing is optimal at every fixed horizon,
so it also optimizes any predetermined nonnegative weighted sum of these
services, including a trajectory AUC. This does not cover a stopping rule
chosen after observing failures, unequal pair rewards, the original
largest-component AUC, or constraints that require a connected graph.

With strictly distinct rates and `2<=k<=n-2`, the respective optimal perfect
matchings are unique. A mixture of horizons is also strict if it puts positive
weight on such a horizon. At the four boundary horizons every matching ties.

The [implementation](../research/ordered_pairing.py) supports 2–128 vertices
and positive finite rates at most one million. It uses the structural theorem,
not simulation. For example:

```sh
python3 -m research.ordered_pairing research/examples/ordered-pairing.json
python3 -m unittest research.test_ordered_pairing research.test_survivor_order
```

## Limits of tempting extensions

Multiplicative inequalities can reverse. For rates `(1,2,3,4)`,
`q_02 q_13 - q_03 q_12 = -1/12600` at two survivors. For rates
`(1,2,3,4,5)`, the analogous difference on labels `(0,1,3,4)` is
`25/6342336 > 0`. Neither multiplicative orientation is universal.

Multiplying pair probabilities by heterogeneous `min(v_i,v_j)` also destroys
the additive law. Optimal earlier-parent indices in the original tree theorem
need not increase: rates `(1,2,3,4)` and values `(19,40,41,42)` select parent
`1` for vertex `2`, then parent `0` for vertex `3`. Thus the new law cannot
justify a monotone-parent shortcut for that weighted tree solver.

## Prior art and the exact novelty question

Let `pi_i,pi_ij` be first- and second-order inclusion in the first `n-k`
deleted vertices. Complementation gives
`q_ij(k)=1-pi_i-pi_j+pi_ij`. In each four-point difference, every marginal
appears once on each side and cancels. Our inequality is therefore **exactly
an inequality about second-order inclusion in successive weighted sampling**;
renaming deleted units as survivors does not create a novel result.

[Rudys (2012), §4, equation 7](https://www.statistikuasociacija.lv/workshop2012/papers/W2012_CP_RUDYS_TOMAS.pdf)
gives second-order inclusion integrals for order sampling, and
[Ng and Donadio (2006)](https://doi.org/10.1016/j.jspi.2005.03.010) study their
computation. These are prior art for the representation, not a new integral
invented here. [Kochar and Korwar (2001), theorem 2.2 and corollary 2.2](https://web.pdx.edu/~kochar/Papers/d_papers/AISM_2001.pdf)
give arrangement and common-endpoint ordering results. The latter alone
compares individual pair probabilities rather than differences of two such
comparisons.

The adjacent-versus-crossing half makes the cost matrix `-q` a Demidenko
matrix in rate order; see [Çela, Deineko and Woeginger (2023), definition 2.1](https://arxiv.org/abs/2302.05191).
The full chain has an additional orientation not supplied by that definition.
Matching exchanges and reliability rearrangements themselves are established
methods; see [Boland, Proschan and Tong (1989)](https://doi.org/10.1002/1520-6750(198912)36:6%3C807::AID-NAV3220360606%3E3.0.CO;2-I).

The bounded literature searches did not locate this exact inclusion-probability
chain. That is evidence of a candidate gap, not proof of priority. The full
Ng–Donadio paper and broader arrangement-order/reliability literature still
need specialist review before a literature-first claim is justified.

## Economical discovery experiment

The investigators derived the two-survivor law and the candidate extension
before any small-model call. A separate
[frozen pilot](../research/spikes/frugal/protocol.json) tests whether Qwen3-14B
can independently select such conjectures from a bounded formula grammar,
and whether exact counterexamples improve selection. It includes a zero-model
enumeration baseline. It cannot credit the model with originating the grammar,
these laws, or their proofs. Its findings will distinguish model inference
cost from the larger cost of creating and verifying the laboratory.
