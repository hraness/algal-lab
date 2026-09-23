# Rank selection beyond exponential clocks, and a boundary for redundant groups

Algal Lab research note, 23 September 2026. Draft for expert review.

## Abstract

The earlier [four-point inclusion inequality](ordered-survival-discovery.md)
extends from exponential clocks to independent continuous clocks ordered by
their CDFs and reversed hazards. We give an exact nonnegative integral for
each four-point difference, an example outside the common exponential
time-change model, and a continuous counterexample to replacing the hypotheses
by ordinary stochastic order for the full crossing-versus-nested chain. The
resulting optimal pairing rules still need only an ordering of components.

For larger groups we identify a separate tractability boundary. After exactly
two successive rate-proportional failures, sorting into consecutive equal-size
groups maximizes the expected number of completely intact groups. In contrast,
maximizing the expected number of working majority triples is strongly
NP-complete in its decision form, even for arbitrarily nearly equal positive
integer rates. The reduction includes a finite error bound and a rounded
threshold whose numerator and denominator are polynomially bounded. Near
equality also permits a small additive approximation bound: exact hardness
does not imply that useful approximate grouping is difficult.

These are mathematical results in specified models, supported by ordinary
proofs and exact executable checks. They are not formal theorem-prover proofs,
real-equipment measurements, or established claims of literature priority.

## 1. A rank-selection identity

Let independent, absolutely continuous real random variables `X_1,...,X_n`
have CDFs `F_i` and densities `d_i`. Retain the `k` largest variables, and write
`q_ij(k)` for the probability that both labels `i,j` are retained. For a set
`A`, define

\[
 H_j^A(t)=\Pr\{\#\{i\in A:X_i>t\}=j\},\qquad
 L_j^A(t)=\Pr\{\#\{i\in A:X_i>t\}\le j\}.
\]

Use `H_j=0` outside `0..|A|` and `L_j=0` for negative `j`.
Fix four different labels `a,b,c,d`; let `R` contain the other labels and
`m=k-2`. Put

\[
\begin{aligned}
D_1&=(F_d-F_a)(F_c-F_b),\\
C_1&=(d_aF_d-d_dF_a)(F_c-F_b)
       +(F_d-F_a)(d_bF_c-d_cF_b),\\
D_2&=(F_b-F_a)(F_d-F_c),\\
C_2&=(d_aF_b-d_bF_a)(F_d-F_c)
       +(F_b-F_a)(d_cF_d-d_dF_c).
\end{aligned}
\]

**Identity.** For `k>=2`, each of the two gaps

\[
 \Delta_1=q_{ab}+q_{cd}-q_{ac}-q_{bd},\qquad
 \Delta_2=q_{ac}+q_{bd}-q_{ad}-q_{bc}
\]

satisfies

\[
 \boxed{\displaystyle
 \Delta_\ell=\int_{\mathbb R}
 \left[C_\ell H_m^R+
 D_\ell\sum_{r\in R}d_rH_{m-1}^{R\setminus\{r\}}\right]dt.} \tag{1}
\]

No distributional ordering is needed for this identity.

**Proof.** Conditioning on the smaller of the two selected clocks gives

\[
 q_{ij}(k)=\int [d_i(1-F_j)+d_j(1-F_i)]
                 L_m^{[n]\setminus\{i,j\}}\,dt. \tag{2}
\]

Here the count is **at most** `m`; using exactly `m` would be incorrect.
For a complementary quartet pair `x,y`, expand this count probability as

\[
 F_xF_y L_m^R+
 [(1-F_x)F_y+F_x(1-F_y)]L_{m-1}^R+
 (1-F_x)(1-F_y)L_{m-2}^R.
\]

Substitution into either signed four-pair sum and collection of terms gives

\[
 \Delta_\ell=\int
       [C_\ell H_m^R-D_\ell' L_{m-1}^R]dt. \tag{3}
\]

This is a polynomial identity in the CDFs and densities. One way to verify
the collection is to set `u_i=(1-F_i)/F_i`, `h_i=d_i/F_i`, and `P=product F_i`
where all CDFs are positive. The coefficient of `L_(m-2)` in the equivalent
odds expansion cancels because each label contributes once with each sign;
`u_i'=-h_i(1+u_i)` gives the remaining derivative. Clearing denominators proves
(3) everywhere, including regions with zero CDFs.

Finally,

\[
 (L_{m-1}^R)'=\sum_{r\in R}d_r H_{m-1}^{R\setminus\{r\}}.
\]

Integration by parts in (3) proves (1). Its boundary term is
`D_l L_(m-1)^R`. Both CDF differences tend to zero at either end of the real
line and `0<=L<=1`, so it vanishes. All terms are integrable: bounded CDF
products multiply finite sums of probability densities. This also justifies
the proof for different supports, without division by a vanishing CDF.

## 2. Pairing beyond memoryless failures

**Theorem.** Suppose, for almost every `t`,

\[
 F_a\le F_b\le F_c\le F_d,\qquad
 d_iF_j\ge d_jF_i\quad(i<j\text{ in the quartet order}). \tag{4}
\]

Where CDFs are positive, the second condition is descending reversed-hazard
order `d_a/F_a >= d_b/F_b >= d_c/F_c >= d_d/F_d`. The cross-product condition
states the hypothesis without support ambiguities. Then, for every fixed `k`,

\[
 q_{ab}(k)+q_{cd}(k)\ge q_{ac}(k)+q_{bd}(k)
                      \ge q_{ad}(k)+q_{bc}(k). \tag{5}
\]

Every `C_l,D_l` in (1) is nonnegative, proving the claim. At `k=0,1,n-1,n`
the gaps are zero. A gap is strict precisely when its nonnegative integrand
is positive on a set of positive measure. Strict quartet order by itself
does not ensure this when the other clocks have arbitrary supports. For
example, if four clocks lie below 1 and the fifth above 2, retaining two
clocks cannot retain any pair from that quartet.

If an even population admits this common order, the usual four-point exchange
argument proves that adjacent pairs maximize expected intact-pair count and
opposite-end pairs maximize expected redundant-pair count. The same choices
optimize any predetermined nonnegative sum over fixed rank horizons. They use
`O(n log n)` comparisons, or linear work if the order is supplied. They do not
require evaluating `q_ij`, but obtaining a valid stochastic order can itself
require distributional knowledge. Adaptive stopping and arbitrary dependence
are outside the theorem.

For a concrete non-exponential example, let four independent clocks be uniform
within each of the unit intervals `(0,1),(1,2),(2,3)`, with interval masses
given by the following rows divided by 16:

\[
 \begin{pmatrix}1&3&12\\2&6&8\\4&8&4\\8&6&2\end{pmatrix}.
\]

CDFs are linear within each interval. Checking their values at the endpoints
establishes CDF order; `d_iF_j-d_jF_i` is constant within an interval, so its
sign can also be checked exactly. Both conditions (4) hold. At `n=4,k=2`,
the adjacent, crossing, and nested sums respectively are

\[
 731/1536,\qquad1781/6144,\qquad1439/6144.
\]

This is more than a common time change of independent exponentials. Such a
change would make ordinary hazard ratios constant. For the first two rows,
their ratio starts at `1/2` and approaches `7/15` at the left limit of 1.

**Stochastic order alone can fail the second gap.** Instead use interval masses

\[
 \frac13\begin{pmatrix}0&1&2\\1&0&2\\2&0&1\\2&1&0\end{pmatrix}.
\]

The CDFs still satisfy the same order everywhere, and the variables are
independent and continuous. At `k=2`, the three matching sums are
`85/162,37/162,40/162`; the second gap is `-1/54`. A common 10% uniform mixture
makes every interval mass positive and preserves a negative gap. Thus ordinary
stochastic dominance is insufficient for the full chain, even without atoms
or ties. The [stochastic-order group theorem](stochastic-intact-groups.md)
now proves that the first gap, and adjacent intact-pair optimality, hold under
ordinary stochastic order alone. It extends intact-group optimality to every
equal group size and every fixed survivor horizon.

## 3. Completely intact groups after two failures

Return to successive weighted deletion: select each next failed component
proportionally to its positive rate among those remaining. Partition `n=mr`
components into `m>=2` groups of size `r>=2`, and stop after exactly two
failures. Put

\[
 W=\sum_iw_i,\quad b_i=\frac{w_i}{W-w_i},\quad
 A_G=\sum_{i\in G}w_i,\quad B_G=\sum_{i\in G}b_i,\quad
 J=\sum_iw_i b_i.
\]

Summing the two possible failure orders gives unordered pair probability
`(w_i b_j+w_j b_i)/W`. Therefore

\[
 P_{\rm same}(\mathcal P)=\frac{\sum_{G\in\mathcal P}A_GB_G-J}{W},\quad
 E_{\rm all}=m-2+P_{\rm same},\quad
 E_{r-1}=m-P_{\rm same}. \tag{6}
\]

**Theorem.** Consecutive blocks of `r` sorted rates maximize `E_all` and
minimize `E_(r-1)`. With distinct rates the partition is unique, up to group
names and within-group order.

For the proof, take any two groups and sort their union into lower and upper
halves `L,H`. Since both `w_i` and `b_i` increase with the rate, this split
maximizes the absolute difference between the two group sums for **both**
quantities. For another split `X,Y` of that same union `U`, write
`delta_A=A_X-A_Y`, `delta_B=B_X-B_Y`. Then

\[
 A_XB_X+A_YB_Y=\frac{A_UB_U+\delta_A\delta_B}{2}
              \le A_LB_L+A_HB_H.
\]

For distinct rates this is strict unless the two groups are already separated
in rate order. Repeatedly separate interlaced groups. The objective strictly
increases on a finite set of partitions, so the process terminates at the
consecutive blocks. Tied rates follow by continuity, perturbing them in the
chosen sorted order. Equation (6) proves both objective statements.

This is an `O(n log n)` construction for the two-failure horizon. The subsequent
[outside-failure proof](intact-groups-all-horizons.md) extends the intact-count
result to every fixed survivor count; the majority objective remains separate.

## 4. Majority triples are strongly NP-complete to optimize exactly

Define the decision problem: given `n=3m` positive integer rates and a rational
threshold `tau`, does a partition into triples have expected working-group
count at least `tau` after two successive weighted failures, when a group
works if at least two members remain? Its objective is `E_2` in (6).

**Theorem.** This decision problem is strongly NP-complete. For every fixed
`epsilon>0`, hardness persists with `max(w)/min(w)<1+epsilon`.

**Proof.** Reduce from restricted 3-PARTITION: positive integers `a_1,...,a_n`
sum to `mB`, with `B/4<a_i<B/2`. Take `K=nB^3`, `w_i=K+a_i`, and `D=W-K`.
For a triple partition put

\[
 F(\mathcal P)=\sum_G A_GB_G,\qquad
 C=(3K+B)\sum_i b_i,\qquad u_G=\sum_{i\in G}a_i-B.
\]

The integers `u_G` sum to zero. Write `d=W/D^2`. The exact expansion

\[
 b_i=\frac KD+d a_i+d\frac{a_i^2}{D-a_i}
\]

implies

\[
 \frac{F(\mathcal P)-C}{d}=\sum_Gu_G^2+E,\qquad
 E=\sum_Gu_G\sum_{i\in G}\frac{a_i^2}{D-a_i}. \tag{7}
\]

Indeed the constant term cancels using `sum u_G=0`, and
`sum u_G sum_(i in G) a_i=sum u_G^2`. Also `|u_G|<B/2`,
`sum a_i^2<mB^2/2`, and `D-max a_i>K`, whence

\[
 |E|<\frac{(B/2)(mB^2/2)}K=\frac1{12}. \tag{8}
\]

A perfect 3-partition gives all `u_G=0` and hence `F=C`. For any other
partition, nonzero integers summing to zero have `sum u_G^2>=2`. Let
`R_0=m-(C-J)/W`. Equations (6)–(8) give

\[
 E_2(\mathcal P)=R_0-\frac{\sum_Gu_G^2+E}{D^2}.
\]

Thus YES instances attain `R_0`, whereas every NO partition has service
strictly below `R_0-1/D^2`. The exact rational `R_0` may have a large
denominator, so it must not simply be declared a polynomially bounded numeric
threshold. Instead set

\[
 Q=2D^2,\qquad \tau=\frac{\lfloor Q R_0\rfloor}{Q}. \tag{9}
\]

YES instances reach `tau`; NO instances cannot, since
`tau>R_0-1/Q>R_0-1/D^2`. On polynomially bounded 3-PARTITION instances the
rates, `Q`, and threshold numerator are all polynomially bounded. Computing
the floor in (9) uses polynomial-bit rational arithmetic. A proposed partition
can likewise be scored exactly in polynomial time, proving NP membership.

For any fixed `epsilon>0`, replace `K` by `c nB^3` for a sufficiently large
fixed integer `c`. The error bound decreases, all bounds stay polynomial, and
`max(w)/min(w)<1+epsilon`. This proves the additional restriction.

The reduction concerns a varying number of triples. It does not make the
bounded six- or nine-component example solver computationally hard, nor rule
out useful approximation or randomized heuristics.

## 5. Near equality limits the practical penalty

There is a simple quantitative complement to the hardness theorem. Write
`a=min(w)`, `M=max(w)`. For any two equal-size partitions, either objective
in (6) differs by at most

\[
 \boxed{\displaystyle
 \min\left\{1,\frac{nr(M-a)^2}{2(W-M)(W-a)}\right\}.} \tag{10}
\]

To see this, center the group sums in `F=sum A_GB_G` at `W/m` and
`sum b_i/m`. The `A_G` range is at most `r(M-a)` and the `B_G` range at most
`r(b_max-b_min)`. The variance bound for a variable in an interval and
Cauchy–Schwarz put the absolute centered product sum below
`m r^2 (M-a)(b_max-b_min)/4`. Two partitions differ by at most twice this.
Use `b_max-b_min=W(M-a)/[(W-M)(W-a)]` and divide by `W`. The cap of 1 follows
from (6), since a probability lies in `[0,1]`.

Consequently **any** proposed grouping has an additive regret certificate (10).
If `rho=M/a`, a simpler bound is `nr(rho-1)^2/[2(n-1)^2]`. It vanishes
quadratically with relative spread. This is an elementary range/covariance
corollary, not a claimed new approximation technique. It explains why the
near-uniform hardness construction should not be sold as a large practical
performance obstacle.

Even at modest sizes, rate magnitudes matter. The unique majority-triple
optimum for rates `(1,2,3,4,5,6)` is `((0,2,5),(1,3,4))`; changing only the
last rate to 9 changes the unique optimum to `((0,1,5),(2,3,4))`. Both stop
after two failures. Unlike the pair result, a rule using only sorted positions
cannot choose both optima.

## 6. Prior art and the remaining priority question

The earlier exponential-clock theorem is exactly a second-order inclusion
inequality for successive sampling: complementing the selected set cancels
all first-order marginals in the four-point differences. This prevents a
change of terminology from being mistaken for a discovery.

[Kochar and Korwar (2001), theorem 2.1, corollary 2.2 and theorem 2.2](https://www.ism.ac.jp/editsec/aism/pdf/053_3_0631.pdf)
establish neighboring sample, common-endpoint inclusion, and ordered-sample
arrangement comparisons. A concrete distinction is possible: assign a
four-label top-two set probability `2/11` to each pair except `{2,3}`, which
gets `1/11`, and divide each set's mass equally among its four complete
rankings. Every common-endpoint comparison and every rank transposition that
moves a better label above a worse one has the expected sign, but
`q_01+q_23=3/11<4/11=q_02+q_13`. Thus those monotonicity properties alone do
not imply the four-point law. The countermodel is dependent; it does not
exclude a derivation from stronger results using independence.

[Rudys (2012), equation 7](https://www.statistikuasociacija.lv/workshop2012/papers/W2012_CP_RUDYS_TOMAS.pdf)
and [Ng and Donadio (2006)](https://doi.org/10.1016/j.jspi.2005.03.010) are
prior art for order-sampling inclusion representations and computation.
[Boland, Proschan and Tong (1989)](https://doi.org/10.1002/1520-6750(198912)36:6%3C807::AID-NAV3220360606%3E3.0.CO;2-I)
provides prior art for reliability rearrangements. The exchange method and
the use of exponential rankings are not novelty claims here.

The hardness source problem is classical
[3-PARTITION, Garey and Johnson (1975)](https://doi.org/10.1137/0204035).
[Ng, Barketau, Cheng and Kovalyov (2010)](https://doi.org/10.1016/j.ejor.2010.05.034)
already establish strong hardness for Product Partition variants and a
series–parallel reliability-design problem. Likewise, reducing balanced
triple sums to a quadratic partition objective is standard. The narrower
candidate contribution here is the exact two-successive-failure majority
objective, its near-uniform restriction, and its finite-error reduction—not
generic hardness of reliability design.

The bounded primary-source search did not locate either the general identity
(1) or this restricted hardness theorem. Full theorem-level comparison with
some order-sampling and reliability sources remains incomplete. Search absence
is not proof of literature priority; broader sampling, stochastic-order and
reliability expertise could still identify an equivalent result. An expert
review should test both direct statements and reductions from more general
theorems before any “first discovery” announcement.

## 7. Executable evidence and discovery record

All checks use Python's standard library, rational arithmetic, and bounded
inputs. No credentials or paid inference are required:

```sh
python3 -m unittest research.test_rank_selection research.test_two_failure_groups
python3 -m research.spikes.rank.verify
python3 -m research.spikes.groups.verify
python3 -m research.rank_selection
```

The [rank oracle](../research/rank_selection.py) integrates polynomial CDF
expressions for 4–9 independent histogram clocks on at most six intervals.
Its independent categorical enumeration conditions on interval assignments and
uniform ranks within the cutoff interval. The separate verifier checks the
gap identity and the arrangement countermodel. These finite tests check the
implementation and examples; the proof establishes the unbounded theorem.

The [group oracle](../research/two_failure_groups.py) scores partitions up to
96 vertices with integer rates at most `10^18`, constructs the consecutive
ALL optimum, and exhausts the ten or 280 triple partitions at six or nine
vertices. Direct ordered-deletion enumeration independently checks 325
partition scores. Four bounded YES/NO reductions at target 16 exhaust 580
partitions. Executable caps are not restrictions in the complexity theorem.

This continuation followed the earlier result and its negative small-model
pilot. A bounded Sol worker found the two-deletion group formula and magnitude
counterexamples; the lead agent proposed the generalized rank identity, the
stochastic-order counterexample, the finite-offset hardness reduction and its
threshold repair. Luna workers audited the algebra and prior art, and the
group worker independently checked the reduction. No new external model API
experiment was run. That does **not** make the agent analysis free or establish
that a small model originated the full contribution. The earlier
[Qwen3-14B pilot](../research/spikes/frugal/findings.md) remains a negative
selection experiment, with its original cost and limits unchanged.

Exploratory failures are retained in the public examples above. Strict
full-chain inequalities for disjoint supports are not asserted. Subsequent
work proves an [all-horizon intact-group theorem](intact-groups-all-horizons.md),
strengthens it to [ordinary stochastic order](stochastic-intact-groups.md),
and gives a [complete two-threshold criterion](two-threshold-certificate.md) for
quartet inequalities against arbitrary independent backgrounds.
