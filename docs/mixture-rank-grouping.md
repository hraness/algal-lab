# Optimal grouping along a line of mixture laws

Independent scores need not be stochastically ordered for a simple grouping
rule to be optimal. Suppose every score law is a mixture of the same two
arbitrary distributions. Sort the mixture weights, then take consecutive
equal-size groups. This partition maximizes every tail probability of the
number of intact groups at every fixed survivor count.

The two base CDFs may cross. Consequently all distinct score CDFs may cross,
so this is a different sufficient condition from the
[FOSD grouping theorem](stochastic-intact-groups.md). The proof identifies
a squared-CDF integral behind a quartet comparison. That full-line integral
is an established Cramér–von Mises discrepancy; its positivity is not claimed
as a new discovery. Literature priority of the grouping result remains
unresolved in the [novelty ledger](novelty-ledger.md).

## Theorem

Let \(n=mr\), and let the focal scores be independent with proper atomless
CDFs

\[
 F_i=(1-p_i)G+p_iH,\qquad 0\le p_1\le\cdots\le p_n\le1. \tag{1}
\]

Here \(G,H\) are any two proper atomless CDFs; neither must dominate the
other. Append any finite background vector jointly independent of the focal
scores. Its coordinates may depend on one another. Retain the largest \(k\)
scores for a fixed \(k\).

Let \(T\) group consecutive sets of \(r\) focal labels, and let \(N_P\)
count intact groups of a partition \(P\) into \(r\)-element groups. Then

\[
 \Pr(N_T\ge j)\ge\Pr(N_P\ge j)
 \quad\text{for every }P,\ k,\ \text{and integer }j. \tag{2}
\]

All groups have the same value and work exactly when every member is
retained. The conclusion concerns each fixed horizon, not an adaptive
stopping rule or pathwise domination on the same sampled scores. It does
not assert a rule for unequal group sizes. Partially working groups require
a separate argument; the pair corollary below covers the one-survivor case.

Arbitrary atomic \(G,H\) are also admitted when every label, including
background labels, has an independent identically distributed continuous
tie key independent of all scores. The displayed integral below is stated
for atomless bases; raw Stieltjes substitution at jumps needs corrections.

## Why a quartet factors

Write \(Y_i\) for a label's selected indicator. Fix four labels \(a,b,c,d\),
all outside laws, and any nonnegative function \(W\) of selected indicators
outside the quartet. The expectation

\[
 f(p_a,p_b,p_c,p_d)
 =E[W(Y_a-Y_b)(Y_c-Y_d)]
\]

is affine separately in each \(p_i\), by independence and the mixture
representation. Swapping \(a,b\), or \(c,d\), changes its sign. These
symmetries hold even with a background: selection is label-equivariant,
and \(W\) involves no quartet labels.

An affine polynomial in each of two variables that changes sign when they
are exchanged is a constant times their difference. Applying this twice
gives

\[
 f=K_W(p_a-p_b)(p_c-p_d), \tag{3}
\]

where \(K_W\) depends on the bases, outside law, horizon and \(W\), but on
none of the four mixture weights. Relabeling the quartet leaves this same
coefficient in all three comparisons. With

\[
 A=Y_aY_b+Y_cY_d,\quad
 C=Y_aY_c+Y_bY_d,\quad
 R=Y_aY_d+Y_bY_c,
\]

we therefore have

\[
\begin{aligned}
 E[W(A-C)]&=K_W(p_a-p_d)(p_b-p_c),\\
 E[W(A-R)]&=K_W(p_a-p_c)(p_b-p_d),\\
 E[W(C-R)]&=K_W(p_a-p_b)(p_c-p_d).
\end{aligned} \tag{4}
\]

It remains to prove \(K_W\ge0\). Independence is essential to the
multiaffinity argument; the theorem does not merely assume mixture
marginals for dependent scores.

## A squared-CDF certificate on every window

Evaluate (3) at \(p_a=p_c=1,\ p_b=p_d=0\). Two focal laws are \(H\),
two are \(G\), and the positively paired labels have identical laws.

First take absolutely continuous bases. Condition on all outside scores.
If exactly two quartet labels cannot be selected, the contrast vanishes.
Otherwise let \(L\le U\) be the two outside thresholds bracketing that
case, with infinite end thresholds allowed. When the contrast is nonzero,
the selected outside set is the fixed set of its largest \(k-2\) scores.
Thus \(W\) is one constant \(w\ge0\) there.

Set

\[
 \Delta=G-H,\qquad S=(G+H)/2.
\]

The [two-threshold identity](two-threshold-certificate.md) gives the
conditional unweighted coefficient as \(D(U)+\int_L^U C(t)\,dt\), where

\[
 D=\Delta^2,\qquad
 C=2(H'G-G'H)\Delta.
\]

Direct algebra yields

\[
 H'G-G'H=S'\Delta-S\Delta',\qquad
 C=3S'\Delta^2-(S\Delta^2)'.
\]

Consequently the conditional coefficient equals

\[
 K(L,U)
 =(1-S(U))\Delta(U)^2+S(L)\Delta(L)^2
   +3\int_L^U\Delta(t)^2\,dS(t)\ge0. \tag{5}
\]

Every term is nonnegative, regardless of how often \(G,H\) cross.
Proper CDFs give \(\Delta(\pm\infty)=0\). When \(L=U\), the expression
reduces to \(\Delta(U)^2\). Multiplying by \(w\) and averaging proves
\(K_W\ge0\).

Common convolution extends the inequalities to arbitrary atomless bases:
convolve both bases with the same small continuous noise. Every focal law
retains (1), the quartet bounds persist, and rankings stabilize almost
surely against the independent finite background as the noise vanishes.
For atomic bases, use the same positive small noise with independent
uniform keys on every label, including backgrounds. This proves the
tie-key extension. Arbitrary fixed label priorities would break the
relabeling argument and are not admitted.

With no background, four focal labels, \(k=2\), and \(W=1\),

\[
 K=3\int_{\mathbb R}(G-H)^2\,d((G+H)/2). \tag{6}
\]

This is three times the established population discrepancy in
[Curry, Dang and Sang, Theorem 2.1 and equation (7)](https://arxiv.org/pdf/1802.06332).
That source establishes the discrepancy and its positivity. Even (5) can
be expressed using that known discrepancy: replace each base's mass below
finite \(L\) by a common uniform lower buffer, retain its CDF on \([L,U]\),
and replace its mass above \(U\) by a common uniform upper buffer. The lower
buffer contributes \(S(L)\Delta(L)^2\) to three times the discrepancy,
the upper contributes \((1-S(U))\Delta(U)^2\), and the middle supplies
the integral. Thus window positivity is also a consequence of the known
distance after this modification. The remaining rank-window representation,
mixture factorization, outside factors and assembly comparison are separate
steps; this is not a new distance or a claim of priority clearance.

## From quartets to all group sizes

For ordered \(p_a\le p_b\le p_c\le p_d\), all products in (4) are
nonnegative. In particular the consecutive pairing dominates both
alternatives, even after multiplication by any nonnegative outside factor.

These are exactly the inequalities needed by the existing
[group-separation proof](stochastic-intact-groups.md#equal-size-grouping-by-product-factorization).
For clarity, its algebra does not require an order on the CDFs. If two
old groups have union split into its first and last \(r\) mixture weights,
their intact-count difference factors as

\[
 (Y_P-Y_B)(Y_A-Y_Q),
\]

where \(P,A\) partition the first \(r\) labels, \(Q,B\) partition the last,
and \(|P|=|B|,\ |A|=|Q|\). Here \(Y_S=\prod_{i\in S}Y_i\).
Telescope both product differences. Each resulting term is a quartet
contrast in (4) times a nonnegative outside monomial.

For the full count comparison, let \(J\) count intact groups outside
these two. Both old and new local counts have the same indicator of being
two, since that event is selection of their entire union. Therefore for
any nondecreasing function \(\phi\), their difference after applying
\(\phi(J+\cdot)\) is the intact-count difference multiplied by
\(\phi(J+1)-\phi(J)\ge0\). This is another admitted outside factor.
Repeatedly isolating the first group and continuing proves (2).

For pairs, (4) gives a second conclusion: pairing the smallest remaining
mixture weight with the largest, and repeating, stochastically **minimizes**
the intact-pair count and **maximizes** the number of pairs with at least
one selected member. To see this, take the two current pairs containing
the extreme labels. Replacing them by the nested pairing minimizes their
intact-count contrast in (4). The preceding argument with
\(\phi(J+1)-\phi(J)\) proves the intact-count minimum.

For the redundant count, a change can occur only when exactly two quartet
labels are selected. There the local redundant count is two minus the local
intact count. Its \(\phi\)-difference is the negative intact-count difference
times \(\phi(J+2)-\phi(J+1)\ge0\), where \(J\) counts redundant pairs
outside the quartet. This is again an admitted outside factor. Fix the
extreme pair and recurse. This proof also allows an independent background;
it does not condition on a random number of focal survivors. The executable
optimizer below constructs the intact-count maximum; this pair corollary is
a separate mathematical conclusion.

## Crossing example and a sharp histogram boundary

Take three common unit bins and normalized base masses

\[
 G=(2,1,2)/5,\qquad H=(1,3,1)/5.
\]

Their CDFs cross at \(t=3/2\); every two distinct mixtures in (1) also
cross there. Equation (6) gives \(K=1/25\). For four mixture weights
\(0,1/3,2/3,1\), the consecutive-minus-crossing, consecutive-minus-nested,
and crossing-minus-nested gaps at top two are respectively

\[
 1/75,\qquad 4/225,\qquad 1/225.
\]

Thus a common FOSD chain is unnecessary, and the last comparison has the
opposite sign from the earlier general-FOSD counterexample.

For nine clocks, take mixture weights \(p_i=i/8\), \(i=0,\ldots,8\).
Their integer histogram rows are \((16-i,8+2i,16-i)\), each totaling 40.
All 36 pairs of CDFs cross. At six survivors, exact enumeration gives:

| Partition into triples | At least one intact | At least two intact |
|---|---:|---:|
| Consecutive \(012/345/678\) | 68.972135% | 3.949655% |
| Interleaved \(036/147/258\) | 67.597193% | 3.485443% |

Percentages are rounded; the verifier retains the exact rational values.
It compares all 280 triple partitions at all ten horizons, with 14,000
tail comparisons. This fixture illustrates the theorem, not a typical
performance estimate.

More generally, any family of common two-bin histogram laws lies on a
mixture line between the two pure-bin laws. These disjoint ordered bases
have \(K=1\) at top two with no background. All three pairing comparisons
follow the order of their mixture weights. A FOSD crossing-versus-nested
reversal is therefore impossible with two common bins. The strictly
positive three-bin rows

\[
 (1,9,20),\ (10,1,19),\ (19,1,10),\ (20,9,1)
\]

normalized by 30 give that reversal, \(503/2025-506/2025=-1/675\).
Three is the minimum bin count for this reversal within the common-bin
uniform histogram model. No minimality across arbitrary distribution
representations is asserted.

## Exact executable certificate

The [mixture optimizer](../research/mixture_stochastic_groups.py) accepts
the same bounded independent common-bin histogram model as the
[FOSD optimizer](../research/stochastic_groups.py). It normalizes rows
exactly, finds two extreme observed rows in one varying mass coordinate,
and verifies that every normalized row is their convex combination at
**every** bin. It sorts those exact mixture weights and returns the groups.

The bases are a representation of the supplied histogram laws; they are
not an estimate of hidden populations. Failure of the affine-line check
means the input is uncertified by this method, not that its proposed
grouping would be suboptimal. All-identical rows are a degenerate admitted
case. Rational outputs use reduced fraction strings and preserve input
label indexing.

Construction needs \(O(nB+n\log n)\) rational operations and \(O(nB)\)
storage, with zero joint-probability evaluations. These are arithmetic
operation bounds, not bit-complexity or wall-clock speed claims.

```sh
python3 -m research.mixture_stochastic_groups examples/mixture-stochastic-groups.json
python3 -m unittest research.test_mixture_stochastic_groups
python3 -m research.spikes.stochastic.mixtures
```

The independent finite verifier checks the algebra and exact ranking
probabilities for crossing-base fixtures. Those calculations check
implementation and examples; equations (3)–(5) and the group-separation
argument prove the distributional theorem. No model-discovery or token
efficiency advantage is established.
