# Intact grouping with imperfect CDF order

The [stochastic grouping theorem](stochastic-intact-groups.md) gives an exact
answer when independent component scores have ordered CDFs. A small error in
that model gives a quantitative guarantee: if the sum of componentwise CDF
errors is `D`, the resulting grouping loses at most `2D` in expected intact
count or in any one count-tail probability. More strongly, its total positive
tail deficit against any single competitor is at most `2D`.

This is an elementary stability consequence of the rank-selection model.
The approximation step uses established isotonic regression. Neither is
presented as a literature-first algorithm; the precise grouping theorem's
priority remains under [review](novelty-ledger.md).

## A bound for the whole count law

Fix a partition `P` of `n` focal labels into `m` disjoint groups. Under two
models the mutually independent focal scores have CDFs `F_i` and `G_i`.
The same finite background vector is independent of the focal scores in
both models; its coordinates may depend on one another. Retain the largest
`k` scores for a fixed `k`. Let `N_P` count groups all of whose members are
retained, and put

\[
 \delta_i=\sup_t|F_i(t)-G_i(t)|,\qquad D=\sum_i\delta_i.
\]

**Stability theorem.** For this fixed partition,

\[
 \sum_{j=1}^m\left|P_F(N_P\ge j)-P_G(N_P\ge j)\right|\le D. \tag{1}
\]

In particular, its expected count and every tail probability change by at
most `D`. The left side is the Wasserstein-1 distance between the two
integer-valued count laws. No stochastic ordering of the reference CDFs is
needed for this stability statement, and group sizes may differ.

**Proof.** Replace one focal distribution at a time. Condition on all other
scores. Unless every label or no label is retained, there is one threshold:
the `k`th largest outside score. Moving the focal score above that threshold
replaces exactly one outside label in the selected set. Only the entering
label's group can become intact, and only the departing label's group can
cease to be intact. If they share a group, its intact status is unchanged.
The two possible counts therefore differ by at most one.

For every function `φ` with `|φ(s+1)−φ(s)|≤1`, the conditional reward is
a constant plus a threshold indicator with coefficient of magnitude at
most one. Changing the one marginal CDF changes its expectation by at most
`δ_i`. Independence permits this conditioning in each hybrid model.
Summing over coordinate replacements gives

\[
 |E_F\varphi(N_P)-E_G\varphi(N_P)|\le D.
\]

Choose `φ(0)=0` and its `j`th increment equal to the sign of
`P_F(N_P≥j)−P_G(N_P≥j)`. The discrete tail-sum identity gives (1). ∎

This proof uses CDF distance directly. It does not assume that two score
laws can be coupled with mismatch probability equal to their CDF distance.

Atoms are allowed if ties use the same fixed label priority, or the same
exogenous random priority independent of all scores. Condition on that
priority too. Inclusion is either `X_i>t` or `X_i≥t`; CDF distance controls
both the CDF and its left limit. The outside ordering must remain stable as
one focal score changes.

## Transferring an optimal grouping

Suppose a partition `P*` stochastically maximizes intact count under `G`.
For example, the consecutive equal-size grouping does so when the reference
scores are independent, atomless and CDF-ordered. For every competing
partition `Q`, reference dominance and (1) imply

\[
 \sum_{j=1}^m
 [P_F(N_Q\ge j)-P_F(N_{P^*}\ge j)]_+\le 2D. \tag{2}
\]

Each positive deficit is at most the sum of the corresponding absolute
reference errors for `Q` and `P*`; summing proves (2). Thus expected-count
regret is at most `min(m,2D)`, every individual tail regret at most
`min(1,2D)`, and the sum in (2) at most `min(m,2D)`.
Equation (2) uses one competitor at a time. It does not sum deficits from
a different best competitor for each tail.

Reference optimality is a separate premise. Arbitrary atomic CDFs with an
arbitrary fixed tie priority need not make consecutive groups optimal.
The [uniform and aligned tie corollaries](stochastic-intact-groups.md#atoms-and-tie-breaking)
give two sufficient conventions. The implementation below always constructs
atomless reference histogram laws.

The constants are sharp as linear bounds. For stability, keep one member
of a pair always selected and let its partner compete with a deterministic
background score `1/2`. Changing that partner from `Uniform[0,1]` to
`Uniform[δ,1+δ]`, with `0<δ≤1/2`, changes intact probability by exactly
`δ`, its CDF distance.

For regret, let the four reference scores be independent with laws
`Uniform[3,4]`, `Uniform[0,1]`, `Uniform[0,1]`, `Uniform[−2,−1]`, and
retain two. Consecutive pairing is reference-optimal. Change only the third
score: give it density one on `[δ,1]` and density `δ` on `[1,2]`.
Its CDF distance is `δ`. Pairing the first and third labels now has intact
probability `1/2+δ−δ²/2`, whereas the reference pairing has
`1/2−δ+δ²/2`. Exact regret is `2δ−δ²`, so the ratio to `D=δ`
approaches two. This shows sharpness of the transfer bound, not sharpness
of the particular projection algorithm's worst-case regret.

## An explicit approximation for histograms

Take common-unit-bin histogram CDFs `H_i`. Choose a label order, and at
each bin endpoint `t` set

\[
 A_i(t)=\max_{a\le i}H_a(t),\quad
 B_i(t)=\min_{b\ge i}H_b(t),\quad
 G_i(t)=\tfrac12[A_i(t)+B_i(t)]. \tag{3}
\]

Interpolate between endpoints. Both envelope arrays are nondecreasing in
label index and score, so `G` is an ordered family of proper atomless CDFs.
Let `V=max_{i<j,t}[H_i(t)−H_j(t)]_+`, evaluated at endpoints.
Because `B_i≤H_i≤A_i` and each one-sided discrepancy is at most `V`,
each midpoint differs from its input by at most `V/2`. Conversely, an
ordered approximation with maximum CDF error `ε` must have
`H_i(t)−H_j(t)≤2ε`. Therefore the exact best uniform radius for this
**fixed label order** is `V/2`, attained by (3). Linear interpolation makes
endpoint errors sufficient. The approximation minimizes the largest marginal
error; it need not minimize their sum or find the best label order.

Formula (3) is precisely the unweighted **Basic** isotonic regression in
§2.1.1 of [Stout, *Weighted L∞ isotonic regression* (2018)](https://web.eecs.umich.edu/~qstout/pap/LinfinityIsoReg.pdf).
That paper explicitly records its older origins. Our use of the formula
preserves CDF monotonicity across score endpoints and feeds the errors into
(2); the regression algorithm itself is established prior art.

The [bounded implementation](../research/robust_stochastic_groups.py) chooses
the lexicographic order of the original CDF endpoint vectors, resolving
identical vectors by input label. It groups consecutive labels after (3),
reports each exact CDF error, and applies (2). It evaluates no joint rank
probabilities. Construction uses `O(n B log n)` rational operations and
`O(n B)` storage for `n` labels and `B` bins.

```sh
python3 -m research.robust_stochastic_groups examples/robust-stochastic-groups.json
python3 -m unittest research.test_robust_stochastic_groups
```

The input is exactly `histograms` and `groupSize`, with the same bounds as
the [exact optimizer](stochastic-intact-groups.md#bounded-histogram-optimizer-and-verification).
The separate `algal.lab.robust-stochastic-grouping.v1` contract returns an
`approximation-certified` result and rational errors and bounds. These
bounds certify the supplied histogram laws. If they estimate population
CDFs, a separate error bound `η_i` for each population-to-histogram distance
must be added to `δ_i`. The deterministic projection provides no sampling
confidence by itself.

The public example has rows `(1,1,18),(2,8,10),(3,2,15),(4,7,9)`.
It returns pairs `01/23`, total CDF error `D=1/4`, and regret bounds `1/2`.
At survivor count two, pairs `02/13` actually improve the expected intact
count by `387/4000`. This exact example demonstrates a nonoptimal proposal
with a valid approximation certificate. The bound is a worst-case guarantee,
not an estimate of the actual loss.
