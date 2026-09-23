# Optimal intact groups under stochastic dominance

Consecutive equal-size groups maximize the probability of having at least
`j` fully surviving groups, for every `j` and every fixed survivor count,
under **ordinary stochastic order**. In particular, they maximize the expected
number of fully surviving groups. Independent atomless clocks suffice; a
corollary below permits atoms with specified tie-breaking. The earlier ordinary-hazard assumption
in the [all-horizon proof](intact-groups-all-horizons.md) can be removed.

The proof has two steps. A positive integral gives the required four-clock
comparison under a CDF cut. That comparison remains valid when multiplied
by any nonnegative function of the other selected labels. A product
factorization then reduces each larger regrouping to those four-clock terms.

The conditioning, product algebra and rearrangement steps have established
precedents. Priority of this precise random-rank application remains
unresolved; see the [novelty ledger](novelty-ledger.md). A proof of correctness
does not by itself establish literature priority.

## Model and result

Let `X_1,…,X_n` be mutually independent proper atomless real clocks, with

\[
 F_1(t)\le F_2(t)\le\cdots\le F_n(t)\quad\text{for every }t.
\]

Thus earlier labels are stochastically larger. Partition the labels into
groups of common size `r`, where `r` divides `n`. Optionally append a finite
background vector jointly independent of all these clocks; its coordinates
may depend on one another. Retain the `k` largest values overall. A group
works exactly when all its members are retained. Group assignment does not
change the clocks or the rank-selection rule.

**Theorem 1.** The consecutive groups
`{1,…,r},{r+1,…,2r},…` maximize `P(N_k≥j)` for every `j`, where `N_k`
is the number of working groups at survivor horizon `k`. This holds for every
fixed `k` and every such background law. Equivalently, their working-group
count dominates every other partition's count in the usual stochastic order.
Consequently they maximize the expectation of every nondecreasing function
of that count, including the count itself.

The objective is an unweighted count of equal-size intact groups. The theorem
does not concern unequal group sizes, arbitrary group values, or the largest
connected component. Nor does it extend to groups that work if *any* member
survives; the strict counterexample below explains that distinction.

## The positive quartet integral

First assume four clocks have absolutely continuous CDFs `a=F_a,b=F_b,
c=F_c,d=F_d`, with densities `f_a,…,f_d`. Define

\[
 D=(d-a)(c-b),\qquad
 C=(f_ad-f_da)(c-b)+(d-a)(f_bc-f_cb).
\]

The [two-threshold identity](two-threshold-certificate.md) gives the
conditional gap `q_ab+q_cd−q_ac−q_bd`, after fixing every background score,
as

\[
 B(L,U)=D(U)+\int_L^U C(t)\,dt,\qquad L\le U. \tag{1}
\]

The decisive algebraic identity is

\[
 C+(bD)'=(c-b)\big[(d-b)f_a+2(d-a)f_b+(b-a)f_d\big]. \tag{2}
\]

Under `a≤b≤min(c,d)`, every factor on the right is nonnegative.
Integrating (2) in (1) gives

\[
 B(L,U)=(1-b(U))D(U)+b(L)D(L)
 +\int_L^U(c-b)\big[(d-b)f_a+2(d-a)f_b+(b-a)f_d\big]dt\ge0. \tag{3}
\]

In particular, a fully FOSD-ordered quartet satisfies the first comparison.
The order between `c,d` is unnecessary, so swapping them also proves
`q_ab+q_cd≥q_ad+q_bc`. Adjacent pairing dominates both alternatives.
Stochastic order alone need not decide which alternative is smaller.

**Lemma 2 (cut-separated quartet).** More generally, both comparisons hold
under the pointwise cut

\[
 \max(F_a,F_b)\le\min(F_c,F_d), \tag{4}
\]

even if CDFs cross within either pair.

**Proof.** The companion identity is

\[
 C+(aD)'=(d-a)\big[2(c-b)f_a+(c-a)f_b+(a-b)f_c\big]. \tag{5}
\]

Put `M=max(a,b)`. Use (2) where `b≥a`, and (5) where `a≥b`.
The maximum of two absolutely continuous functions is absolutely continuous.
On their equality set their derivatives agree almost everywhere. Thus
`C+(MD)'=G≥0` almost everywhere, without any switching-boundary term.
The resulting formula is

\[
 B(L,U)=(1-M(U))D(U)+M(L)D(L)+\int_L^U G(t)dt\ge0. \tag{6}
\]

All terms are integrable because densities integrate to one and CDF factors
are bounded. Proper CDFs give `D(±∞)=0`, so infinite thresholds are covered.
For `L=U` the formula reduces to `D(U)`. Conditioning and averaging over
the background proves the claim at every horizon. ∎

The conclusion extends to atomless laws without densities. Add independent
identically distributed `Uniform[−ε,ε]` noises to the four clocks. Common
convolution preserves all CDF cut inequalities and gives densities. As
`ε→0`, comparisons involving focal scores stabilize almost surely: independent
atomless focal clocks have no ties with one another or with their independent
background. Bounded convergence passes the inequalities to the original law.
No claim is made here for an arbitrary tie rule on atomic focal clocks.

## Nonnegative outside factors can be retained

Write `Y_i=1` when label `i` is selected. For a cut-separated quartet define

\[
 h(Y)=(Y_a-Y_d)(Y_b-Y_c)
 =Y_aY_b+Y_cY_d-Y_aY_c-Y_bY_d.
\]

It vanishes unless exactly two quartet labels are selected.

**Lemma 3 (outside-factor lift).** If `W` is any nonnegative function of
the selected-label indicators **outside** this quartet, then

\[
 \mathbb E[W(Y_{\rm outside})h(Y)]\ge0. \tag{7}
\]

**Proof.** Condition on all outside scores. Whenever `h` is nonzero,
exactly `k−2` outside labels are selected: they are the largest `k−2`
outside scores, a fixed label set under this conditioning. Therefore `W`
is the same nonnegative constant on the entire event where `h` can matter.
On its complement the product is zero. If that outside count is impossible,
the product is identically zero. Otherwise the conditional expectation is
this constant times a nonnegative quartet gap from Lemma 2. Averaging proves
(7). We conditioned on scores, not on a selection event that could destroy
focal independence. ∎

In the group proof, `W` is just a product of outside selection indicators,
so it is bounded. The statement also holds for any finite-valued function
on the finite outside label set. Background ties may use any fixed priority;
no focal score ties with a background almost surely.

## Equal-size grouping by product factorization

Consider any two current groups of size `r`. Let `H` be the first `r`
labels of their union in the global CDF order and `L` the other `r`.
Every member of `H` dominates every member of `L`. Write the original
groups as `P∪Q` and `A∪B`, where `P,A` partition `H` and `Q,B`
partition `L`. Equal group sizes imply `|P|=|B|` and `|A|=|Q|`.
For any label set `S`, write `Y_S=∏_{i∈S}Y_i`, including `Y_∅=1`.
The improvement from separating the groups is exactly

\[
 Y_H+Y_L-Y_{P\cup Q}-Y_{A\cup B}
 =(Y_P-Y_B)(Y_A-Y_Q). \tag{8}
\]

If either difference is identically zero because its two sets are empty,
there is no change. Otherwise choose any bijections between `P,B` and
between `A,Q`. A product difference telescopes as

\[
 \prod_{j=1}^{m}u_j-\prod_{j=1}^{m}v_j
 =\sum_{j=1}^{m}(u_j-v_j)
       \prod_{i<j}u_i\prod_{i>j}v_i. \tag{9}
\]

Apply (9) to both factors in (8) and multiply the sums. Each term is a
nonnegative outside monomial times
`(Y_p−Y_b)(Y_a−Y_q)`, where `p,a` are distinct members of `H` and
`b,q` are distinct members of `L`. This is a cut-separated quartet contrast.
Its multiplier contains none of those four labels. Lemma 3 makes every
term's expectation nonnegative. Separating any two groups therefore cannot
decrease expected intact count, in the original full population and horizon.

To finish Theorem 1, start with the group containing label 1. If it lacks a
member of `{1,…,r}`, combine it with a group containing such a missing
member and separate their union into its first and last `r` labels. The
first resulting group retains every first-block label it already held and
gains at least one. After finitely many steps it is `{1,…,r}`. Fix it and
repeat with the remaining groups. All exchanges weakly improve the same
objective, so the final consecutive partition maximizes expected intact count.
The following argument strengthens each step to prove the full theorem.

The two-group comparison itself needs only the cut between `H,L`, not an
order within either group. The global sorting proof uses the full CDF order
to certify every intermediate union cut. This distinction matters for an
optimizer that admits CDF crossings.

For pairs, separated target blocks suffice even with internal crossings.
If the first desired pair is split across two current pairs, its two partners
are both in later blocks. The cut-separated quartet comparison joins the
desired pair without decreasing the objective. Fix it and repeat. A single
group is trivial, and exactly two groups are covered directly by (8)–(9).

## The whole count distribution improves

Let `Z` and `Z'` be the numbers of intact groups among the two groups before
and after an exchange, and let `J` count intact groups outside their union.
Each of `Z,Z'` takes values in `{0,1,2}`. The product of the two intact-group
indicators is the same under either partition: it is `Y_{H∪L}`, because both
groups work exactly when their whole union is selected.

For any function `φ` on group counts, its value at `J+Z` can be written as

\[
 \varphi(J+Z)=\varphi(J)+[\varphi(J+1)-\varphi(J)]Z
 +[\varphi(J+2)-2\varphi(J+1)+\varphi(J)]Y_{H\cup L}.
\]

Subtracting cancels the last term. Thus

\[
 \varphi(J+Z')-\varphi(J+Z)
 =[\varphi(J+1)-\varphi(J)](Z'-Z). \tag{10}
\]

If `φ` is nondecreasing, the bracket is nonnegative and depends only on
selected labels outside the exchanged union. Multiply every quartet term in
(8)–(9) by this bracket. Each multiplier remains a nonnegative function of
labels outside that quartet, so Lemma 3 applies to every term. Every exchange
therefore increases `E[φ(N_k)]`. The same finite sorting procedure proves
Theorem 1. In particular, for `φ(s)=1{s≥j}` the bracket is `1{J=j−1}`,
giving each claimed tail probability. ∎

This is a distributional comparison at each fixed horizon. It does not claim
a pathwise improvement under the original shared scores, or optimality at a
horizon chosen after observing the failures. The special cases with internal
CDF crossings above inherit the same count-distribution conclusion.

## Atoms and tie-breaking

**Corollary 4.** Theorem 1 also holds for arbitrary independent proper real
clocks in the same CDF order when ties are broken uniformly at random.
Assign every label, including backgrounds, an independent `Uniform[−1,1]`
key independent of all scores, and rank lexicographically by `(score,key)`.

**Proof.** Perturb each score by `ε` times its key, using the same keys for
all `ε`. Common convolution preserves the focal CDF order, gives absolutely
continuous laws and preserves independence from the perturbed background
vector. For each finite realized population, distinct score levels have a
positive minimum separation when any exist. For sufficiently small `ε`,
all unequal-score comparisons therefore stay fixed, and equal-score
comparisons are exactly the key order. Rankings converge almost surely at
every horizon. Bounded convergence passes each count-tail inequality to the
lexicographic model. ∎

A fixed priority aligned with the certified order `1,…,n` is also valid.
Give labels distinct bounded constants `a_i`, with `a_1>⋯>a_n` on the focal
labels and any consistent placement of background labels. Perturb by
`ε a_i+ε²U_i`. Ordered shifts and common noise preserve the focal CDF chain;
the limiting rank order breaks equal scores by the specified priority.

An arbitrary fixed priority is insufficient. Take four constant-zero clocks,
the valid CDF order `1,2,3,4`, and tie priority `1,3,2,4`. At top two,
consecutive pairs `12,34` have zero intact groups, while `13,24` have one.
Uniform random ties instead make every pairing equivalent for this fixture.

## A strict counterexample for redundant pairs

On three common unit bins give four independent clocks these masses, each
row totaling 30:

```text
a:  1 9 20
b: 10 1 19
c: 19 1 10
d: 20 9  1
```

Every bin density is positive. The CDF numerators at the two interior
endpoints are `(1,10,19,20)` and `(10,11,20,29)`, respectively.
Affine interpolation proves `F_a<F_b<F_c<F_d` throughout `(0,3)`.
With no backgrounds, retain exactly two clocks. Exact categorical integration
gives

| Pairing | Sum of pair-inclusion probabilities |
|---|---:|
| Adjacent: `ab,cd` | `1016/2025` |
| Crossing: `ac,bd` | `503/2025` |
| Nested: `ad,bc` | `506/2025` |

Adjacent pairing maximizes intact count, as proved. For redundant pairs,
expected working-pair count is the sum of singleton inclusions minus the
pair-inclusion sum. The singleton sum is fixed at two, so crossing beats
nested by `1/675`. Thus opposite-end pairing can be suboptimal under strict
FOSD and positive densities in the whole population. The earlier
reversed-hazard theorem still supplies the stronger crossing-versus-nested
comparison in its narrower class.

## Bounded histogram optimizer and verification

The [implementation](../research/stochastic_groups.py) accepts `2..128`
histogram clocks on `1..64` common unit bins, nonnegative integer masses at
most one million, and a positive total in every row. The integer group size
is between two and `n` and divides `n`. It normalizes exactly, sorts CDF
endpoint vectors lexicographically, and checks the required pointwise order
at every bin endpoint. Differences are affine inside bins, so endpoint
comparisons suffice. It performs no inclusion-probability evaluations.

The general certificate requires a full CDF chain. It also admits the proved
special cases of a single group, two cut-separated groups, and cut-separated
pairs with arbitrary within-pair crossings. With three or more groups of
size greater than two, between-block separation alone is not asserted
sufficient here; the full-chain check remains required. Rejection means
the proposed partition is uncertified by these conditions, not that it is
nonoptimal.

Construction uses `O(n b log n)` rational-arithmetic work and `O(n b)`
storage for `b` bins. These are arithmetic-operation bounds, not constant
bit-cost claims. The certificate's independence assumptions are model
requirements; they cannot be inferred from marginal histograms alone.

```sh
python3 -m research.stochastic_groups examples/stochastic-groups.json
python3 -m unittest research.test_stochastic_groups
python3 -m research.spikes.stochastic.verify
```

Focused checks compare every partition of bounded small populations against
independent categorical-rank probabilities, including triples and size-four
groups. The separate verifier checks both integral identities, positive
density coefficients, universal quartet comparisons and the strict redundant
counterexample. The [factorization checker](../research/spikes/stochastic/factorization.py)
also verifies 2,352 exact two-group polynomial identities for sizes two through
seven and 51,384 cases of the outside-selection argument, including tied
backgrounds. An independent exploratory spike tested 6,144 six-clock FOSD
profiles and 111,958 three-threshold contexts without finding a triple
counterexample; that negative search did not establish the theorem. The
factorization proof and a separate supermodular-cube derivation supplied
the general conclusion.

The independent [count-tail checker](../research/spikes/stochastic/tails.py)
compares all 105 pair partitions of eight clocks and all 280 triple partitions
of nine clocks at three horizons each. It checks 3,780 exact tail inequalities,
212,256 local threshold identities, and uniform ties against an independent
enumeration of global key permutations. It also reproduces the fixed-priority
counterexample. Integer numerators and rational arithmetic avoid Monte Carlo
uncertainty in these bounded examples.

For a concrete effect size, the nine-clock fixture uses three unit bins and
rows `(1,5,9),(2,4,9),(3,4,8),(4,3,8),(5,5,5),(6,4,5),(7,4,4),
(8,4,3),(9,4,2)`, each totaling 15. Retain six clocks with no background.
The exact tail probabilities, with percentages rounded for readability, are:

| Partition | At least one intact group | At least two intact groups |
|---|---:|---:|
| Consecutive `123/456/789` | `23630883121/29900390625` (79.0320%) | `2034303131/25628906250` (7.9375%) |
| Interleaved `147/258/369` | `3890830837/5980078125` (65.0632%) | `961781473/35880468750` (2.6805%) |

This fixture illustrates the theorem's distributional conclusion. It is not
a measured speedup or an estimate of typical gains across applications.

The positive quartet identity was derived independently in two worker lanes;
the lead investigator supplied the product-factorization route, and a third
reviewer checked its conditioning and scope. These are research provenance
statements, not evidence of a small-model or low-token discovery advantage.
