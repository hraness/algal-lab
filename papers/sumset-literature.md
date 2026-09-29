# Literature comparison for the sumset manuscripts

Review date: 29 September 2026. These manuscripts give explicit constructions,
exact certificates and reflected fourfold inequalities with arbitrary
nonnegative kernel weights on at most four integers and constant kernels
on five. The small-support manuscript also determines sharp four-point
covering constants and proves that its stronger covering bound fails on a
five-point support, even though the reflected inequality holds there for
constant kernels.
The comparison below credits their known ingredients and distinguishes
their conclusions from related sumset problems. It supports the stated
mathematical claims and the comparison with Zheng's theorem;
priority in the full literature remains unestablished. Source reading and
mathematical review were performed by AI agents.

## The fivefold counterexample

The [fivefold note](fivefold-sumset/main.pdf) gives finite integer sets with
`|A−B|^5 > |A+B|^5 |5B|`. Here `5B` is a repeated sumset. With
`V(m,r) = {x ∈ Z≥0^m : Σxᵢ ≤ r}`, the sets are base-193 encodings of
`V(128,160)` and `V(128,32)`.

| Primary source | Statement and relation to the note |
| --- | --- |
| Hennecart, Robert and Yudin, *On the number of sums and differences*, Astérisque 258 (1999), [pp. 173–178](https://www.numdam.org/item/AST_1999__258__173_0/) | Section 3, Lemma 2 gives the equal-radius simplex difference count. Pages 175–177 use integer encoding, Cartesian powers and the family `V(2m,m)` for a one-set logarithmic ratio. The simplex family and these techniques are prior work. |
| Gyarmati, Hennecart and Ruzsa, *Sums and differences of finite sets* (2007), [DOI 10.7169/facm/1229618749](https://doi.org/10.7169/facm/1229618749) | Equation (9), p. 177 asks when `\|A−B\| ≤ \|A+B\| \|hB\|^(1/h)` holds universally. Page 182 gives a sixfold simplex counterexample and leaves four and five unresolved. The present construction contradicts the fivefold statement in that historical text. |
| Daniel Glasscock, *Sumset Estimates in Abelian Groups*, master's thesis, Central European University, [24 February 2012](https://sites.uml.edu/daniel-glasscock/files/2021/06/MSThesis.pdf) | Lemma B.1, pp. 37–38 gives the **same unequal-radius count and negative-support proof** used in the note. Question 8, p. 28 still asks about four and five; Theorem B.3, p. 39 establishes six using equal radii. The title page identifies Glasscock as sole author and Gergely Harcos as adviser. |

In particular, Glasscock's lemma already gives

```text
|V(m,a)−V(m,b)| = Σⱼ binom(m,j) binom(b,j) binom(m−j+a,m−j),
```

where `0 ≤ j ≤ min(m,b)`. The substitution `(m,a,b)=(128,160,32)` supplies
the note's difference count directly. The sumset counts also follow from
that lemma. The contribution recorded by the note is the explicit choice of
parameters, the strict integer comparison and the resulting fivefold
counterexample. The counting formula and its proof are known.

Glasscock's explicit simplex applications use equal radii: `(m,r)=(2k,k)`,
`(k,k²)` and `(3k,k)`. Their stated conclusions concern the sixfold case or
other sum–difference ratios. They do not state the unequal-radius fivefold
specialization. This observation about those texts does not establish that
no later source made it.

## The two-set exponent

The [weighted-digit manuscript](sparse-sum-difference/main.pdf) defines `θ`
as the supremum of exponents `t` such that, for every fixed `K>1`, arbitrarily
large finite integer sets satisfy

```text
|E+F| ≤ K|E|,       |E−F| ≥ c(K)|E+F|^t,
```

with `c(K)>0`, also allowed to depend on the fixed `t`. Its four-digit
construction proves `θ > 23713/20000 = 1.18565`.

| Primary source | Statement and relation to the manuscript |
| --- | --- |
| Gyarmati, Hennecart and Ruzsa (2007), Section 2 | Their finite-set transfer gives `θ ≥ 1 + log(\|U−U\|/\|U+U\|)/log(2 max U+1)` under its strict difference-count hypothesis. The manuscript uses this existing lemma and enforces the hypothesis by dilation. |
| Chin Wa (Ken) Lau and Chandra Nair, *Information inequalities via ideas from additive combinatorics*, [arXiv:2312.11017v3](https://arxiv.org/abs/2312.11017v3) (5 February 2025), Theorem 10 | The typical-set sum-image limit, applied also after reflection, combines with a symmetric Gibbs coupling and the GHR transfer to imply the manuscript's general weighted-digit formula. Appendix A of the manuscript gives the derivation, including the encoding diameter and fixed-`K` quantifiers. |
| F. Zheng, *Sums and differences of sets: a further improvement over AlphaEvolve*, [arXiv:2506.01896v1](https://arxiv.org/abs/2506.01896v1) (2025) | Theorem 1, PDF p. 5, gives `1.173077` for the same two-set problem using bounded-coordinate integer vectors and large-deviation estimates. The current identifiable preprint is v1; its objective, theorem and numerical table were checked on the PDF pages. The manuscript's exact certificate improves this specifically checked bound. |
| Georgiev, Gómez-Serrano, Tao and Wagner, *Mathematical exploration and discovery at scale*, [arXiv:2511.02864v3](https://arxiv.org/abs/2511.02864v3) (22 December 2025) | Problem 6.44 formulates the two-set problem using `\|A+B\|≲\|A\|` and reports the later bounds `1.173050` and `1.173077` of Gerbicz and Zheng. The current version record matches the retained v3 HTML; the relevant passage was read, not the whole survey. |
| Matolcsi, Ruzsa, Shakan and Zhelezov, *An analytic approach to cardinalities of sumsets*, [arXiv:2003.04075v1](https://arxiv.org/abs/2003.04075v1) (2020) | Definition 8.1 defines `(f⋆g)(z)=max_{x+y=z} f(x)g(y)`. The manuscript's `P` and `Q` are exactly `‖w⋆w‖₁` and `‖w⋆w̃‖₁`. Theorem 8.6 equates weighted and set versions of an induced tripling parameter, providing prior weighted-to-set machinery. |
| Becker, Ivanisvili, Krachun and Madrid, *Discrete Brunn–Minkowski inequality for subsets of the cube*, [arXiv:2404.04486v2](https://arxiv.org/abs/2404.04486v2) (2024) | Theorem 1.3 settles the two-point norm conjecture stated after Theorem 11.1 of the preceding preprint. It gives a lower bound for a triple max-convolution using independent norm factors. That conclusion does not itself give an upper bound for a quotient of linked ordinary and reflected convolutions. |
| Hosle and Ivanisvili, *Geometric Block Exponents and a Uniform Mixed-Alphabet Sumset Inequality*, [arXiv:2606.25350v1](https://arxiv.org/abs/2606.25350v1) (2026) | Theorem 1.5 treats a two-term first sequence and a nonincreasing second sequence. Proposition 7.3 and Corollary 1.7 give a sumset lower bound with exponent `log 4/log 6` for a binary first alphabet. The support used here has more than two points and is outside that hypothesis; the conclusion concerns sumset expansion, rather than a reflected quotient. |
| Lin and Li, *Settling the optimal exponent relating sumsets and difference sets*, [arXiv:2607.27199v1](https://arxiv.org/abs/2607.27199v1) (2026) | Proves a supremum of two for `C(A)=log(\|A+A\|/\|A\|)/log(\|A−A\|/\|A\|)`. This one-set normalization differs from `θ`. Its Section 3 identifies the reported search value `1.21` with `C(A)`. |

For positive weights `w` on a finite alphabet `A ⊆ {0,…,B}`, the general
weighted-digit formula is

```text
D_d = max_{a−b=d} w_a w_b,       Q = Σ_d D_d,
P = Σ_s max_{a+b=s} w_a w_b,
θ ≥ 1 + log(Q/P)/log(2B+1),       when Q>P.
```

This statement follows from the Lau–Nair and GHR results above.
Choose pairs maximizing the weighted differences, with opposite
differences represented by reversed pairs, and give them probabilities
`D_d/Q`. Their joint distribution has equal marginals `p`. Gibbs'
inequality bounds the maximum sum entropy at those marginals, while the
chosen difference distribution gives a lower bound. The entropy gap is
at least `log(Q/P)`. Lau–Nair's theorem realizes both entropies on the
same typical sets; base-`2B+1` encoding and a dilation supply the diameter
and strict hypothesis for the GHR lemma.

The manuscript gives this implication as well as its direct counting
proof with explicit cost sublevel sets. The particular four-digit
alphabet, weights, and certificate for `θ>1.18565` are separate from the
general formula. Their occurrence in earlier literature remains
unestablished. A larger exponent for another normalization cannot replace
a comparison under the displayed quantifiers.

Tao's *Sum-difference exponents for boundedly many slopes, and rational
complexity*, [arXiv:2511.15135v1](https://arxiv.org/abs/2511.15135v1)
(19 November 2025), studies universal entropy bounds over specified linear
projections of jointly distributed variables. Section 1.1 and Theorem 1.3
were compared with the fixed-`K` existence problem above. Universal projection
bounds specialize to Cartesian sets and can give upper bounds for `θ`;
a lower bound from a general restricted planar set need not provide a
Cartesian pair with the required small sumset. The inspected statements
do not give a competing numerical lower bound for `θ`. The retained HTML
was partial; this comparison does not claim a complete reading of that paper.

## The fourfold inequality on three points

The [three-point note](three-point-fourfold/main.pdf) proves

```text
‖f⋆(gk)̃‖₁⁴ < ‖f⋆g‖₁⁴ ‖k⋆k⋆k⋆k‖₁
```

when `g` and `k` are positive on the same three distinct integers and zero
elsewhere, and `f` is a nonzero finitely supported nonnegative function.
Here the tilde denotes reflection and `gk` is the pointwise product.
This uses the max-convolution operation already defined by Matolcsi et al.,
Definition 8.1. It is a theorem about three-point kernels; it does not settle
the unrestricted fourfold set question of Gyarmati, Hennecart and Ruzsa.

The inspected two-point norm and mixed-alphabet expansion theorems in the
table do not directly state this reflected comparison with linked weights.
That difference in statements is not a proof of novelty or of non-implication.
The argument in the note is self-contained, and no priority claim is made.
The five-author preprint by Ben Green, Dávid Matolcsi, Imre Ruzsa,
George Shakan and Dmitrii Zhelezov,
*A weighted Prékopa–Leindler inequality and sumsets with quasicubes*,
[arXiv:2003.04077v1](https://arxiv.org/abs/2003.04077v1)
(9 March 2020), gives a relevant prior weighted inequality.
For nonnegative finitely supported `a,b` on the integers and `p∈[0,1]`,
Proposition 2.1 states

```text
Σₙ max(p(a⋆b)(n), (1−p)(a⋆b)(n−1)) ≥ ‖a‖₂ ‖b‖₂.
```

After normalizing the two-point kernel, this is equivalent to the
`p=q=2` case of Theorem 11.1 of Matolcsi et al.
Its proof embeds the sequences as piecewise exponential functions and
applies the continuous one-dimensional Prékopa–Leindler inequality.
Theorem 1.1 then proves `|A+B+U| ≥ √(|A||B|) |U|` for finite integer
lattice sets when `U` is contained in a quasicube. The proof uses induction
on coordinate fibres and a decomposition into residue classes. The complete
five-page preprint, including both proofs, was read and all five original
PDF pages were visually checked; the extraction had been marked partial.
These stated conclusions are max-convolution and triple-sum lower bounds.
They do not directly state the linked reflected ratio considered here;
this comparison does not establish that such a ratio cannot be derived
from them.

Green's
[January 2025 publication list](https://people.maths.ox.ac.uk/greenbj/papers/publist.pdf),
item 82, identifies the same five-author title as a chapter in *Analysis
at Large* (Springer, 2022), pp. 125–129. The printed chapter was not read
or compared with the inspected 2020 preprint; the two texts are not assumed
to be identical.

The four-author companion, Matolcsi, Ruzsa, Shakan and Zhelezov's
[*An analytic approach to cardinalities of sumsets*, arXiv:2003.04075v1](https://arxiv.org/abs/2003.04075v1),
defines the functional tripling invariant (Definition 8.4)

```text
γₚ(h) = inf ‖h⋆a⋆b‖₁ / (‖a‖ₚ ‖b‖q),
```

where `a,b` range over nonzero finitely supported nonnegative functions,
`1<p,q<∞` and `1/p+1/q=1`. These are norm exponents, distinct from the
mixture weight in the preceding proposition. Theorem 8.6 identifies
`γₚ(1_F)=βₚ(F)` with the corresponding set-tripling parameter.
Taking a two-point subset for the lower bound and long auxiliary intervals
for the upper bound gives

```text
γₚ(1_F) = p^(1/p) q^(1/q)
```

for every finite integer set `F` with at least two points. The lower bound
uses Theorems 9.1 and 11.1; the interval lengths approach the ratio `q:p`.
Thus these indicator invariants alone do not determine the supremum of the
reflected quotient for fixed `g`: `g=1_{0,1,2}` gives quotient one for
every input, whereas `f=g=1_{0,1,3}` gives `7/6`. Those two indicators
also have the same ordinary function norms. The value `7/6` is an example,
not a claim about the exact supremum for that profile.

The companion's complete retained extraction was read, and original PDF
pages 15–24 were visually checked, including the definitions, equivalence,
tensorization, two-point statement and proof. Whether the full framework
implies the present small-support theorems remains unestablished in this
comparison; no priority claim follows from the invariant example.

## Covering bounds and the five-point reflected inequality

The [small-support manuscript](four-point-covering/main.pdf) studies the norm

```text
N_F(k) = max { Σₚ k(p)x(p)² : x ≥ 0, supp(x) ⊆ F, x*x ≤ 1 },
T_F(k) = ‖k⋆k⋆k⋆k‖₁.
```

Here `*` is ordinary convolution, `⋆` is max-convolution, the constraint is
coefficientwise, and `k` is a nonnegative kernel supported on the finite
nonempty set `F`. It proves `N_F(k)⁴ ≤ T_F(k)` whenever `|F| ≤ 4`, strictly
when `|F| = 4` and `k` is positive at all four points.

The norm has an exact interpretation as a universal translated-covering
constant. For a nonzero nonnegative `g` supported on `F`, let `L_F(g,k)` be
the least total weight `Σₜ λₜ` of a nonnegative cover satisfying

```text
Σ_{q∈F} g(q)λ_{p+q} ≥ g(p)k(p)     for each p∈F, with t∈F+F.
```

Finite linear-programming duality and coefficientwise AM–GM give
`sup_g L_F(g,k) = N_F(k)`. The same supremum results if `g` is required to
be positive throughout `F`. A cover bounds
`‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁` for every nonzero finite nonnegative `f`.
Consequently the manuscript proves the reflected fourfold inequality above
for every support of at most four points, with strictness for positive
four-point `k` even when some values of `g` are zero. This sharpness statement
concerns the universal covering constant; it does not identify the sharp
nonlinear max-convolution ratio for a fixed `g`.

The proof separates the five possible patterns of equalities between
unordered pair sums. It also accounts for additional fourfold-sum
collisions within each pattern. The sharp unweighted values are:

| Four-point support pattern | `N_F(1_F)` |
| --- | ---: |
| Sidon: every unordered pair sum is distinct | `2` |
| One three-term progression and no other pair-sum equality | `7/4` |
| Proper parallelogram: one pair-sum equality using four distinct points | `25/16` |
| Two three-term progressions, represented by `{0,1,2,4}` | `105/64` |
| Four-term arithmetic progression | `3/2` |

For the five-point Sidon set `F={0,2,7,8,11}`, the feasible constant input
`x=1_F/√2` instead gives

```text
N_F(1_F)⁴ ≥ (5/2)⁴ = 39 + 1/16 > 39 = T_F(1_F).
```

Thus four is the largest support size for the universal covering bound.
The manuscript proves that the reflected inequality nevertheless holds on
this support when the kernel is constant, as part of its theorem for every
five-point support below. The unrestricted fourfold question remains
outside these results.

The prior max-convolution framework of Matolcsi et al., Green et al.'s
weighted Prékopa–Leindler preprint, and the cube and mixed-alphabet theorems
compared above remain relevant here. Their cited statements do not directly
state this weighted ordinary-autoconvolution norm comparison. This
observation is not a proof that the comparison cannot be derived from them.
The printed five-author chapter and the identified journal versions remain
unread; possible revisions to the inspected preprints have not been assessed.

### Constant kernels on five points

For every five-element integer set `F`, every nonzero finitely supported
nonnegative `f`, and every nonzero nonnegative `g` supported on `F`, the
manuscript proves

```text
‖f⋆g̃‖₁⁴ < |4F| ‖f⋆g‖₁⁴.
```

This is the reflected fourfold inequality with `k=1_F`; scaling gives the
same conclusion for every positive constant kernel on `F`. The weights
`g` need not be constant or positive everywhere. For Sidon supports, the
proof combines the universal ratio bound `‖f⋆g̃‖₁/‖f⋆g‖₁ ≤ 62/25`
with `|4F| ≥ 39`. For supports with a pair-sum collision, it proves the
strict sufficient covering bound directly.

When `g=1_F`, the elementary energy argument already gives the stronger
ratio bound `9/5`. Since `|4F| ≥ 17`, this proves the five-point indicator
corollary `|A−F|⁴ < |A+F|⁴ |4F|` for every finite nonempty integer set
`A`. The five-point theorem extends the conclusion to arbitrary nonnegative
weights `g`. Neither the support restriction nor this indicator corollary
settles the unrestricted fourfold sumset question.

The external ingredient is Freiman's classical integer `3k−4` theorem,
in the form recalled by Béla Bollobás, Imre Leader and Marius Tiba,
*A strengthening of Freiman's 3k−4 theorem*,
[arXiv:2204.09816v1](https://arxiv.org/abs/2204.09816v1)
(21 April 2022). The unnumbered statement on page 1 immediately after
Theorem 1 says that integer sets `A,B` with `|A|=|B|=m` and
`|A+B|=2m−1+r`, `r≤m−3`, lie in progressions of a common difference,
each with `m+r` elements. Taking the two sets equal gives the form used
here. For `B=2F`, `|B|=15` and a hypothetical `|B+B|≤38`, the containing
progression has at most 24 elements. After normalization its step is one,
so `diam(F)≤11`. A hand classification of span-11 Sidon sets and exact
fourfold-sum counts then yield the sharp lower bound 39.

The source's introduction and background on pages 1–4, and final discussion
and references on pages 13–14, were read. The exact classical statement was
also checked on the original first page. The extraction was marked partial
because an image was omitted; the complete PDF was retained and that page
was visually inspected. Freiman's original proofs and the full technical
proof of the authors' bounded-summand strengthening were not read. This is
a verified restatement of the classical dependency, not a claim to have
reviewed those other proofs or established priority for the five-point result.

### Comparison with continuous autoconvolution bounds

Two inspected primary sources concern ordinary autoconvolution with a
different input normalization:

| Primary source | Statement and reading scope |
| --- | --- |
| Alexander Cloninger and Stefan Steinerberger, *On suprema of autoconvolutions with an application to Sidon sets*, [arXiv:1403.7988v3](https://arxiv.org/abs/1403.7988v3) (22 April 2016); published in *Proceedings of the American Mathematical Society* 145(8), 3191–3200 (2017) | Section 1.2 maximizes continuous `L¹` mass under an ordinary-autoconvolution supremum constraint on a fixed interval. Section 3 discretizes interval masses on a simplex with `Σaᵢ=4n`. The eight-page extraction was read; it was marked partial and reported an omitted image. Original PDF pages 4–8 were visually checked. The large computation was not reproduced; the journal text was not read. |
| Paata Ivanisvili and Xinyuan Xie, *Grokability in five inequalities*, [arXiv:2605.05193v1](https://arxiv.org/abs/2605.05193v1) (6 May 2026) | Theorem 5 states `‖f*f‖∞ ≥ 1.2802(∫f)²` for nonnegative integrable `f` supported on `[-1/4,1/4]`. The theorem and its complete Section 2.4 proof were read, including visual checks of original PDF pages 5, 16 and 17. The proof refines an error estimate and relies on an earlier computation from Cloninger–Steinerberger. This is a report of the source's theorem; that numerical dependency was not reproduced or independently certified here. The unrelated proofs were not all reviewed. |

These continuous statements constrain `L¹` mass. The covering part of the
small-support manuscript instead optimizes the weighted squared input mass
`Σk(p)x(p)²` on a fixed finite support and compares it with a fourfold
max-convolution total.
Different normalizations alone establish neither novelty nor
non-implication. An implication would need a justified embedding and
normalization that preserve the linked reflected weights.

## Entropy translations

Lau and Nair's *Information inequalities via ideas from additive
combinatorics*, [arXiv:2312.11017v3](https://arxiv.org/abs/2312.11017v3)
(5 February 2025),
Theorem 1 and its proof translate a class of cardinality inequalities into
entropy inequalities with prescribed marginals and separate optimization
over couplings. The proof uses type classes and integer encoding. These
are established methods relevant to further weighted formulations of the
fourfold and fivefold question.

Theorem 1 is unchanged from v2. Theorem 10 in Appendix C of v3 states the
typical-set limit used in the weighted-digit derivation. For probability
vectors `p,q` on finite integer supports, define

```text
E_±(p,q) = max { H(X±Y) : the joint law of (X,Y) has marginals p,q }.
```

If `A_n,B_n` are their relative strongly typical sets, then
`n⁻¹ log|A_n±B_n| → E_±(p,q)`; the difference statement follows by
reflection. The relative tolerances tend to zero with
`√n ω_n → ∞`. When `p=q`, both limits use `A_n=B_n`.
The coupling may depend on the sign; independence is not required.

The complete 21-page v3 preprint was read. Independent mathematical review
covered Theorem 10 and the supporting type argument in Appendices B and C,
including checks of original PDF pages 15–21. The manuscript's Appendix A
also gives a direct proof of the required limits by counting complete type
classes and rounding joint distributions into the prescribed marginal
windows.
The logarithms in the source use base two; multiplication by `log 2` gives
the natural-logarithm formulas here.

The integer encoding in these applications concerns finite integer supports.
Applications to a global fourfold statement must preserve all marginal and
repeated-set constraints across all finite supports. A set inequality known
only with one fixed `B=F` does not cover the correlated typical sets
`B_n ⊆ F^n`. These translations do not resolve the unrestricted fourfold
question or identify the covering constant `N_F(k)` with the sharp
reflected quotient.

An author survey also identifies the journal edition in
[*IEEE Transactions on Information Theory* 71(6), 4055–4068 (2025)](https://doi.org/10.1109/TIT.2025.3557796).
The journal text remains unread; the theorem and proof comparison here is
with the identified arXiv v3.

The logarithm of a sumset's size is its support entropy. It generally
differs from the Shannon entropy of a sum of independent uniform elements.
The two construction papers also give direct finite counting proofs, and
both fourfold manuscripts prove their weighted inequalities directly.
The entropy derivation maximizes over couplings with prescribed marginals;
it does not substitute the entropy of independent uniform inputs.

## Scope of this review

The review followed the historical question, its simplex antecedents,
forward citations, weighted and entropy formulations, continuous
autoconvolution bounds, and related 2025–2026 preprints. The decisive simplex
formulas and thesis attribution were checked
on the original PDF pages. Comparisons of the analytic and entropy work
use the versions linked above and the relevant definitions and proofs.

The version check also identified journal editions of Matolcsi et al.,
[*Combinatorica* (2022)](https://doi.org/10.1007/s00493-021-4547-0), and
Becker et al.,
[*Combinatorica* 45 (2025), Paper 48](https://doi.org/10.1007/s00493-025-00180-0),
from the bibliographies of later primary papers. Their journal texts remain
unread; the comparisons above concern the exact preprints linked in the table.

This is a dated comparison of identified sources. Search coverage, later
versions and unread texts limit any absence claim. In particular,
Ruzsa's 2007 chapter *Cardinality questions about sumsets* and Sárközy and
Sós's 2013 chapter *On Additive Representative Functions* were identified
but not read. The latter is [DOI 10.1007/978-1-4614-7258-2_16](https://doi.org/10.1007/978-1-4614-7258-2_16).
The manuscripts therefore make no global-priority or current-record
assertion. Their sharpness claims concern only the quantities and classes
for which proofs are given.
Their finite proofs and exact certificates establish the displayed
inequalities independently of that unresolved historical assessment.
