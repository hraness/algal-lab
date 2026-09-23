# Intact equal-size groups at every survivor horizon

This note extends the [two-failure intact-group result](rank-selection-and-triples.md)
to every fixed survivor count. It proves a sorting rule within an exact
independent-clock model and records bounded reproducible checks. It does not
establish literature priority; reliability rearrangement results may subsume
the statement or its proof method.

The [stochastic-order sequel](stochastic-intact-groups.md) now proves the
optimality conclusion for independent atomless clocks under ordinary
stochastic dominance alone, with arbitrary independent background scores.
The exponential uniqueness statement and the outside-failure proof below
remain useful special-case results.

## Model and theorem

Let `n=mr` with `m,r≥2`. Give component `i` an independent exponential clock
`X_i` of positive rate `w_i`; larger clocks survive longer. Partition the
components into `m` groups of size `r` with equal value. At horizon `k`, retain
the `k` largest clocks and count groups whose **every** member survives.
Write `A_k(P)` for the expected count under partition `P`.

**Theorem.** Sort rates as `w_1≤⋯≤w_n`. The consecutive groups
`{1,…,r}, {r+1,…,2r}, …` maximize `A_k(P)` for every fixed `k`.
They also maximize every predetermined nonnegative weighted sum of these
fixed-horizon scores. If rates are strictly increasing, this partition is
unique up to group names and within-group order for `r≤k≤n−2`. At `k<r`,
`k=n−1`, and `k=n`, every partition ties. Tied rates can create more optima.

The objective is expected intact-group **count**. The theorem does not address
majority or OR service, unequal group rewards, a horizon chosen after observing
failures, or largest-component network service. The earlier
[majority-triple hardness result](rank-selection-and-triples.md#4-majority-triples-are-strongly-np-complete-to-optimize-exactly)
remains a separate two-failure statement.

## The outside-failure identity

Put `d=n−k`, `W=Σ_i w_i`, and `u_i(t)=e^{w_i t}−1`. For a set `S`, let
`e_j(u_S)` be the degree-`j` elementary symmetric polynomial, taking value
zero when `j<0` or `j>|S|`. For `d≥1`, define

\[
 \Phi_d(S;t)=\sum_{j\in S}w_j e_{d-1}(u_{S\setminus\{j\}}(t)).
\]

If `q_G(k)` is the probability that all vertices in a size-`r` set `G` rank
among the top `k`, then

\[
 q_G(k)=\int_0^\infty e^{-Wt}\Phi_d([n]\setminus G;t)\,dt. \tag{1}
\]

Condition on the label and time `t` of the `d`th failure **outside** `G`.
Exactly `d−1` other outside clocks have failed by `t`, and every clock in `G`
is still alive. Clock `j` failing at `t` contributes
`w_j e^{-w_jt}`; a previously failed clock `i` contributes
`1−e^{-w_it}`; each still-alive clock contributes `e^{-w_it}`.
Factoring `e^{-Wt}` turns each previous-failure factor into `u_i(t)`.
Summing the possible previous-failure sets and the final label proves (1).
If `d>n−r`, both sides vanish. If `d=0`, `q_G(n)=1` separately.

## Why sorting improves every horizon

Fix `t>0`, `d≥1`, and a set `R` of vertices outside two candidate groups.
Treat `\Phi_d(R\cup Z;t)` as a symmetric function `f` of the `r` rates assigned
to `Z`. Each term is a nonnegative product of increasing one-variable factors:
a coordinate appears as its rate `w_i`, its odds `u_i(t)`, or not at all.
Consequently, increasing two distinct coordinates has a nonnegative
*rectangular cross-difference*. Terms involving only one coordinate cancel;
each term involving both contributes the product of two nonnegative increments.
Thus `f` is supermodular on the product order. When `2≤d≤n−r`, every pair of
coordinates appears together in a term, so the cross-difference is strictly
positive if both rates increase strictly.

Take any two groups `G,H`, sort `G` ascending and `H` descending, and pair
their positions. The coordinatewise minima are exactly the lower `r` rates of
`G∪H`; the maxima are the upper `r`. To see this, a pair cannot contain two
of the lower `r`: if its position is `j`, there would be at least `j` lower
members in the ascending group and at least `r−j+1` in the descending group,
exceeding `r` in total. Since there are `r` pairs and `r` lower members,
each pair has exactly one lower member. Call the resulting groups `L,U`.
The supermodular lattice inequality gives, pointwise in `t`,

\[
 \Phi_d(R\cup L;t)+\Phi_d(R\cup U;t)
 \ge \Phi_d(R\cup G;t)+\Phi_d(R\cup H;t). \tag{2}
\]

In (1), the contribution of intact group `G` has outside set `R∪H`, and the
contribution of `H` has outside set `R∪G`. Therefore (2), multiplied by the
common positive `e^{-Wt}` and integrated, shows that sorting their union into
`L,U` cannot lower their combined service. Every other group's term is
unchanged. With distinct rates, sorting interlaced groups strictly increases
the objective when `2≤d≤n−r`; a finite sequence ends at the consecutive
partition and proves uniqueness. With ties, perturb equal rates into the
chosen order, apply the distinct-rate result, and take a continuous limit.

For `d=1`, `\Phi_1(S;t)=Σ_{j∈S}w_j` is additive, so all partitions tie.
The `d=0` and `d>n−r` cases also tie. These are exactly the boundary
horizons in the theorem.

This proof needs the density of the `d`th outside failure. Conditioning on
the minimum clock *inside* a group gives a different integral whose sorting
difference can be negative at individual times, even in exponential examples.
The positive pointwise inequality is exposed by (1).

## Extension under ordinary hazard order

The same sorting argument applies to a larger independent-clock class. Let
`X_i` be independent, proper, absolutely continuous lifetimes on `[0,∞)`
with survival `S_i(t)>0` for every finite `t`, CDF `F_i`, density `f_i`,
ordinary hazard `h_i=f_i/S_i`, and failure odds `v_i=F_i/S_i`. Assume there is
one component order such that **both** `h_i(t)` and `v_i(t)` are nondecreasing
with the component index for almost every `t`. Then

\[
 q_G(k)=\int_0^\infty\left(\prod_iS_i(t)\right)
 \sum_{j\notin G}h_j(t)
 e_{d-1}(v_{([n]\setminus G)\setminus\{j\}}(t))\,dt. \tag{3}
\]

For fixed `t`, the integrand's sum is symmetric and supermodular in the
paired component values `(h_i(t),v_i(t))` along their common order: each
monomial uses one `h` factor and distinct `v` factors, all nonnegative and
nondecreasing. The same opposite-order pairing of two groups proves (2),
then integration proves consecutive grouping optimal at every horizon.
Pointwise ordinary-hazard order alone supplies the odds order when all
`S_i(0)=1`: integrating ordered hazards gives ordered cumulative hazards,
hence `S_1≥⋯≥S_n` and `v_1≤⋯≤v_n`.

For example, `S_i(t)=exp(−it−i²t²/2)` has hazard `i+i²t` for `t≥0`.
These hazards are ordered, but their ratios vary with time, so the example
is not a common time change of exponentials. Weak optimality follows from
the stated almost-everywhere order. A sufficient condition for uniqueness
at an interior horizon is a common interval of positive measure on which
all relevant hazard and odds comparisons between distinct components are
strict, all survivals are positive, and all odds are positive. We make no
unconditional strictness claim for disjoint or finite supports. Equation (3)
uses positive finite-time survivals to avoid undefined hazard/odds ratios;
extending it through zero-survival endpoints requires a separate limit or
denominator-clearing argument.

## Reproduction and limits

The [constructor and exact small-case oracle](../research/intact_groups.py)
accept integer rates in `1..10^18` and populations of `4..96`; the constructor
only sorts rates and works up to that cap. Exact inclusion calculations admit
at most 12 vertices. Inputs are type checked, so booleans and malformed
partitions are rejected. For example:

```sh
python3 -m unittest research.test_intact_groups
python3 -m research.spikes.intact.verify
```

The tests independently enumerate deletion orders at six vertices. The
verifier expands (1) by inclusion–exclusion and compares its exact rational
value with the source's deletion-state DP in 1,688 group/horizon cases. It
also optimizes all partitions at 25 horizons for `n=6,8,9,12` and `r=3,4`,
and checks 4,200 pointwise local exchanges exactly at `t=log 2`. These are
finite implementation checks; the theorem follows from the proof above.
No model calls, credentials, or paid inference are needed.

## Relationship to prior assembly theorems

The min/max exchange is established prior art. El-Neweihi, Proschan and
Sethuraman's [1986 technical report](https://archive.org/download/DTIC_ADA177151/DTIC_ADA177151.pdf),
Theorem 2.1 and Remark 2.2, gives consecutive assembly of independent series
systems and maximizes their expected working count. Its §3 extends this
across deterministic mission times; Theorem 4.1 applies a general monotone
supermodular reliability function. Derman, Lieberman and Ross's
[1971 report](https://archive.org/download/DTIC_AD0737618/DTIC_AD0737618.pdf)
already gives aligned assembly for a common joint-CDF reliability function.

Our horizon is an order statistic of the same component clocks being scored.
An inequality at every deterministic time cannot simply be evaluated at a
time dependent on those clocks. Equation (1), or (3), supplies the extra
representation needed to apply the established exchange to this rank
objective. The inspected prior theorems do not state that representation or
directly establish its required comparison. This is a specific distinction
from those statements, not a proof of literature priority. The
[novelty ledger](novelty-ledger.md) records source coverage and unresolved
comparisons.
