# Literature comparison for the sumset manuscripts

Review date: 30 September 2026, with an addition on 1 October 2026 comparing
Tao's construction examples.

These manuscripts give explicit constructions,
exact certificates and reflected fourfold inequalities with arbitrary
nonnegative kernel weights on at most four integers and on
`{0,2,7,8,11}`, and with constant kernels on every five-point integer
support and on every finite nonempty `B₄` set, whose unordered four-term
sums, allowing repetition, are distinct. On `B₄` supports, it also permits
nonconstant kernels with `‖k‖₁/‖k‖∞≥9`. A general energy bound controls
the reflected ratio for every nonnegative finite kernel. The sharp
scalar support constants are `K_1=1`, `K_2=5/4`, `K_3=3/2` and `K_4=7/4`;
for nonnegative kernels with at most four positive sites, the weighted
bound is `(K+3M)/4`, where `K=‖k‖₁` and `M=‖k‖∞`. For each nonempty
prescribed list of at most four positive values, this is the exact
supremum over nonzero finite inputs and integer locations. The zero
kernel gives ratio zero. The manuscript also determines sharp
four-point covering constants. Its stronger covering bound
fails on the displayed five-point support, where the reflected inequality holds for arbitrary
nonnegative kernels.
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

The note also gives a finite construction using binary words in base nine,
in dimension 555,008. An asymptotic version follows from Lau and Nair's
[typical-set theorem, arXiv:2312.11017v3, Theorem 10](https://arxiv.org/abs/2312.11017v3),
with probability laws

```text
p = (144,64,32,16,8,4,2,1)/271 on {0,…,7},
q = (255,16)/271 on {0,1}.
```

A selected coupling gives a lower bound for the difference entropy.
Positive generating polynomials bound the sumset and the fivefold sum
of the same binary typical set. The strict entropy gap gives finite
integer counterexamples for all sufficiently large dimensions. The note's
exact-type argument supplies its stated finite dimension. This identifies
the application of the earlier theorem; an earlier printed occurrence of
these particular marginals or the resulting fivefold example remains
unestablished.

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

For a fixed integer `B≥2` and the full alphabet `A={0,…,B}`, optimizing
geometric weights gives
exactly the same asymptotic difference-to-sum rate as optimizing the radius
in Zheng's bounded-coordinate simplex family. To make the comparison
precise, put `W(m,L,B)={x∈{0,…,B}^m: Σxᵢ≤L}` and

```text
P_B(q)=Σ_{s=0}^{2B} q^s,       Q_B(q)=1+2Σ_{j=1}^B q^j.
```

For `L=⌊rm⌋`, the finite method of types gives the limiting logarithmic
sum and difference counts per coordinate as

```text
s_B(r)=inf_{0<q≤1} [log P_B(q)−2r log q],
d_B(r)=inf_{0<q≤1} [log Q_B(q)−2r log q].
```

The difference formula uses reflection to make the positive and negative
coordinate budgets equal. At `r=0` both rates are zero. For `r>0`,
choosing a minimizing parameter for `s_B` bounds `d_B−s_B` above by `max_q log(Q_B/P_B)`. Conversely, at
`r=qQ_B′(q)/(2Q_B(q))`, the difference Gibbs distribution attains `d_B`,
and the same parameter bounds `s_B` above. Hence
`sup_{r≥0}(d_B(r)−s_B(r))=max_{0≤q≤1} log(Q_B(q)/P_B(q))`, with quotient
one at both endpoints. This is our derivation of the relation between
the two constructions; it does not recheck Zheng's numerical optimization.
Sparse alphabets with holes, including the manuscript's carry-block
alphabet, change the family itself. That distinction does not establish
historical novelty.

The manuscript gives the weighted-digit implication above, as well as
its direct counting proof with explicit cost sublevel sets. The particular four-digit
alphabet, weights, and certificate for `θ>1.18565` are separate from the
general formula. Their occurrence in earlier literature remains
unestablished. A larger exponent for another normalization cannot replace
a comparison under the displayed quantifiers.

Tao's *Sum-difference exponents for boundedly many slopes, and rational
complexity*, [arXiv:2511.15135v1](https://arxiv.org/abs/2511.15135v1)
(19 November 2025), studies universal entropy bounds for linear projections.
Section 3 relates its projection exponent to an independent-variable constant
through controlled self-doubling. For its final configuration, our elementary
comparison gives an `O(δM)` gap between the conditionally independent output
entropy and the largest entropy over couplings of the same conditional
marginals, averaged over the conditioning variable. Here `M` is the entropy
scale and `δ` measures the deficit from exponent two. This connects the
reduction to the maximal-coupling entropies used in typical-set transfer.

<details>
<summary>The coupling comparison</summary>

Let `(U,V)` be any finite rational-valued coupling, let `a` be a nonzero
rational, and let `V′` be independent of the whole pair with the same law as
`V`. Then

```text
H(U+aV) <= H(U+aV′) + H(V−V′) − H(V).
```

To see this, put `A=U+aV′` and `C=U+aV`. Subadditivity gives
`H(A)+H(C−A) >= H(C)+H(A|C)`, and conditioning further on `(U,V)` shows
`H(A|C) >= H(V′)`. Also `H(C−A)=H(V−V′)`. The right side depends only on
the marginals, so maximize the left side over their couplings. Independent
coupling is one allowed choice, giving a gap between zero and the
self-distance `H(V−V′)−H(V)`. Apply this separately at each conditioning
value and average. Tao's Corollary 3.10 bounds that average self-distance
by `O(δM)` in the configuration used by Section 3.6.

</details>

After `n` tensor copies, the resulting small-sumset estimate permits a factor
`exp(O(nδM)+o(n))`, which need not stay bounded. It therefore does not by itself
give the fixed-`K` conclusion required for `θ`. The GHR transfer can provide
that conclusion from a suitable finite single set, but also requires a
favorable difference-to-sum ratio relative to its diameter. Section 3 can
preserve coordinate supports; its entropy estimates do not supply this
quantitative comparison or our numerical certificate. Theorem 1.3's
changing-slope asymptotics do not give a near-two limit for the fixed inputs
`{0,1,infinity}` and output `-1`.

The lower-bound constructions in Sections 4–5 also let the output slope vary.
For their interval and symmetric polynomial sets, reflection makes the sum
and difference counts equal at slopes `1` and `-1`. Rational slopes approaching
`-1` can have many distinct output values that coincide at the limiting slope.

<details>
<summary>The construction examples at the fixed difference slope</summary>

For `I_N={1,…,N}`, the sum and difference sets both have `2N−1` elements.
By contrast, if `N≥2`, `b≥10N` is an integer, and `s=−(b−1)/b`, the map
`(x,y)↦x+sy` is injective on `I_N×I_N`. Sending this output to an ordinary
difference by setting `E=bI_N` and `F=(b−1)I_N` gives

```text
|E−F| = |E+F| = N²,       |E| = N.
```

Indeed, a nontrivial collision in either signed sum forces the two coordinate
differences to be nonzero multiples of `b−1` and `b`, exceeding their possible
magnitudes.
The resulting sumset factor is `N`, so it does not stay bounded by a fixed `K`.
The small projection is `E+[b/(b−1)]F=b(I_N+I_N)`; its coefficient differs
from one. More generally, the rational projective maps preserving the input
set `{0,1,infinity}` can send only `s∈{−1,1/2,2}` to `−1`.

Section 4's polynomial set has symmetric coefficient bounds and hence is
equal to its negative. Its sum and difference sets coincide. Used directly
as a single digit set, either symmetric family therefore has a difference-to-sum
ratio of one in the GHR transfer. Nor does changing only the coupling help
the maximal-entropy comparison: if a marginal is invariant under `Y↦c−Y`,
this reflection pairs its couplings with the other marginal fixed and makes
the maximum sum and difference entropies equal.

Theorem 1.4 takes coprime `a,b` with `b→infinity` and `a/b→α`. Even when
`α=−1`, the output slope cannot remain exactly `−1`: a reduced fraction
equal to `−1` has denominator one. For each fixed compactly supported density,
Section 5's discretized integer variables lie in an interval of length `O(b)`.
Their ordinary difference consequently has entropy at most `log b+O(1)`.
Using the stated marginal growth `log b+O(1)`, its output-to-input entropy
ratio is at most `1+O(1/log b)`. This fixed-slope comparison does not verify
the numerical coefficient in the theorem's continuous-limit expansion.

</details>

This comparison covers the retained Section 3, its Section 2 prerequisites,
and the construction passages in Sections 4–5, using Section 1's definitions
and theorem statements. The HTML extraction is partial; this is not a
whole-paper review or a priority claim. These examples do not exclude other
constructions based on Tao's methods.

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

## Covering bounds and reflected inequalities

The [finite-support manuscript](four-point-covering/main.pdf) studies the norm

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
this same support for arbitrary nonnegative kernel weights. Its separate
constant-kernel theorems apply to every five-point integer support and
every finite nonempty `B₄` set. Its weighted energy theorem also proves
the reflected inequality on `B₄` supports when `‖k‖₁/‖k‖∞≥9`.
The unrestricted fourfold question remains outside these results.

The prior max-convolution framework of Matolcsi et al., Green et al.'s
weighted Prékopa–Leindler preprint, and the cube and mixed-alphabet theorems
compared above remain relevant here. Their cited statements do not directly
state this weighted ordinary-autoconvolution norm comparison. This
observation is not a proof that the comparison cannot be derived from them.
The printed five-author chapter and the identified journal versions remain
unread; possible revisions to the inspected preprints have not been assessed.

### Arbitrary kernels on `{0,2,7,8,11}`

For `F={0,2,7,8,11}`, every nonnegative kernel `k` supported within `F`,
and arbitrary nonnegative finitely supported functions `f,g` on the
integers, the manuscript proves

```text
‖f⋆(gk)̃‖₁⁴ ≤ T_F(k) ‖f⋆g‖₁⁴.
```

The inequality is strict when `k` is positive at all five points and
`f,g` are nonzero. Both input functions may have support outside `F`.
The non-strict statement includes zero kernel values; a complete equality
classification is not asserted.

The proof combines bounds for the reflected ratio with two rational
coefficient comparisons for each of the 120 orders of the five kernel
weights. The resulting 240 exact certificates prove polynomial
inequalities throughout each region of ordered weights, including ties.
The [certificate data](four-point-covering/five-point-certificates/certificates.ndjson)
and [exact arithmetic checker](four-point-covering/verify_five_point.py)
accompany the proof. The certificate comparisons and a separate analytic
estimate cover all branches of the bound for the reflected ratio.
This arbitrary-kernel result concerns the specified support. The results
below address constant kernels on all five-point supports and additional
classes of supports and kernel weights.

### Constant kernels on five points

For every five-element integer set `F` and every nonzero finitely
supported nonnegative `f,g`, the manuscript proves

```text
‖f⋆(g1_F)̃‖₁⁴ < |4F| ‖f⋆g‖₁⁴.
```

This is the reflected fourfold inequality with `k=1_F`; scaling gives the
same conclusion for every positive constant kernel on `F`. The weights
`g` need not be constant or positive everywhere, and all exterior values
remain in the denominator. For Sidon supports, the proof combines
`R_F(f,g)≤35/16`, whose fourth power is less than 23,
with the elementary estimate `|4F|≥30`. Indeed, `|2F|=15`, and equality
in `|2F+2F|≥29` would make `2F` an arithmetic progression. After
translation, `2F={0,d,…,14d}` would place `F` inside `{0,d,…,7d}`,
which has only seven possible positive differences instead of the ten
required by the Sidon property. The manuscript includes the elementary
equality characterization. For supports with a pair-sum collision, it
proves the strict sufficient covering bound directly.

When `g=1_F`, the elementary energy argument already gives the stronger
ratio bound `9/5`. Since `|4F| ≥ 17`, this proves the five-point indicator
corollary `|A−F|⁴ < |A+F|⁴ |4F|` for every finite nonempty integer set
`A`. The five-point theorem extends the conclusion to arbitrary nonnegative
weights `g`. Neither the five-point condition nor this indicator corollary
settles the unrestricted fourfold sumset question.

The manuscript also retains the stronger sharp Sidon bound `|4F|≥39`.
This refinement uses Freiman's classical integer `3k−4` theorem,
in the form recalled by Béla Bollobás, Imre Leader and Marius Tiba,
*A strengthening of Freiman's 3k−4 theorem*,
[arXiv:2204.09816v1](https://arxiv.org/abs/2204.09816v1)
(21 April 2022). The unnumbered statement on page 1 immediately after
Theorem 1 says that integer sets `A,B` with `|A|=|B|=m` and
`|A+B|=2m−1+r`, `r≤m−3`, lie in progressions of a common difference,
each with `m+r` elements. Taking the two sets equal gives the form used
for that refinement. For `B=2F`, `|B|=15` and a hypothetical `|B+B|≤38`,
the containing progression has at most 24 elements. After normalization its step is one,
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

### Weighted energy bounds and `B₄` supports

For every nonnegative finitely supported kernel `k` on the integers, let
`K=‖k‖₁` and `M=‖k‖∞`. For arbitrary nonzero finitely supported nonnegative `f,g`,
the manuscript proves

```text
‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁ ≤ (√K+√M)²/4.
```

The denominator includes the values of `g` outside the kernel support,
and values on the support may be zero. The zero kernel gives zero.
The proof uses the mixed weighted form of the classical equal-energy
mechanism. With positive kernel values `k_i`, put `t=K+√(KM)` and

```text
q(x) = t Σ k_i x_i² − (Σ k_i x_i)².
K max_i(k_i x_i²) ≤ q(x) ≤ (t²/4) max_i x_i².
```

Weighted Cauchy–Schwarz and a completed square give the lower bound;
`x_i² ≤ (max x_j)x_i` and a scalar quadratic maximum give the upper bound.
For `x_i±(s)=√(g(p_i)f(s∓p_i))`, the diagonal sums agree, and the mixed
ordinary-convolution identity with auxiliary kernel `w_i=k_i√g(p_i)`
gives equal total `q` on the two sides. Summing compares the reflected
numerator directly with the full original denominator.

Hennecart, Robert and Yudin, p. 174, equation (4), record the equality
of sum and difference representation energies for equal indicator inputs.
The manuscript writes out the mixed weighted identity and uses it in a
quadratic comparison. This is a direct application of that classical
method; no prior source for the exact weighted coefficient has been
identified in the sources read, and no priority claim is made.

Taking `k=1_F` gives, for every `n`-point integer set,

```text
R_F(f,g) = ‖f⋆(g1_F)̃‖₁ / ‖f⋆g‖₁ ≤ C_n,
C_n = (√n+1)²/4.
```

The inequality is strict for each nonzero input pair when `n>1`. At the
output `min supp(f) − max {p∈F:g(p)>0}`, exactly one active reflected
coordinate is positive, which makes the quadratic comparison strict
when there is more than one active point. Empty and singleton active
supports follow separately. The four-, five- and six-point estimates
are strengthened by the four-event argument and subset averaging below. The general
support bound alone does not prove the fourfold inequality for every
six-point support.

The weighted theorem also follows from this scalar theorem by applying
kernel level sets with `f,g` and the full denominator fixed. For nonzero
`k`, put `N(u)=#{p:k(p)>u}`. Subadditivity gives the more detailed bound

```text
‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁
  ≤ ∫₀ᴹ C_{N(u)} du
  = (K+M)/4 + (1/2)∫₀ᴹ √N(u) du
  ≤ (√K+√M)²/4.
```

The last step is Cauchy–Schwarz. This integrates the kernel values;
no interchange of maximum and integration as an equality is used.

Weighted winner allocations give a further universal bound. For the
actual maximizing sites of the weighted numerator, the assigned masses
satisfy `0≤a_i≤1` and `a_i a_j≤1/4`, while the ratio is
`Σk_i a_i`. If every allocation is at most one-half, this is at most
`K/2`. Otherwise, with `x=a_j>1/2`, it is at most
`k_j x+(K−k_j)/(4x)`. Convexity on `[1/2,1]` gives

```text
‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁ ≤ max{K/2,(K+3M)/4}.
```

The geometric lower example below matches this upper bound whenever
`K≤3M`, for each fixed list of positive kernel values with locations
allowed to vary. There is no support-size restriction on that sharpness
statement. In particular, `K_1=1`, `K_2=5/4` and `K_3=3/2`.
The proof uses the actual weighted winners and the same full denominator;
it does not identify them with unweighted winners.

For four sites the sharp scalar bound is `K_4=7/4`. Its upper
bound follows from the following inequality for four events. For any
random subset `J` with positive marginals, put

```text
m_i = Pr(i∈J),  c_ij = Pr(i,j∈J),
r_ij = min(m_i,m_j)/max(m_i,m_j).
Σ_i m_i − max_i Σ_{j≠i} r_ij c_ij ≤ 7/4.
```

The proof combines elementary event bounds with a Gram-matrix comparison,
a variance bound for the integer-valued variable `|J|`, and an explicit
positive polynomial expansion. In the max-convolution argument, mixtures
of four star graphs give lower bounds from paired minima. The upper
bound is a convex function's finite vertex test; its linear-programming
dual is the displayed event inequality. Equal weighted diagonal traces
and reflection invariance then compare the two max-convolution norms.
The proof retains the full denominator and treats zero profile values
by their smaller positive support.

For a kernel on at most four sites, integration over the kernel level
sets gives

```text
‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁ ≤ (K+3M)/4.
```

The profile and its full denominator stay fixed at every level.
The geometric construction gives the matching lower bound for each
prescribed list of at most four positive kernel values, when the
integer locations may vary. This does not assert attainment on every
fixed support.

For `n≥4`, summing the four-site estimate over the four-subsets
of an `n`-element support gives `R_H(f,g)≤7n/16`. At each output,
a maximizing site belongs to exactly `binomial(n−1,3)` of those subsets.
Thus `K_5≤35/16` and `K_6≤21/8`. These ratio bounds are non-strict;
their fourth powers are strictly below 23 and 48, respectively.
Consequently the constant-kernel fourfold inequality holds on five-site
supports with at least 23 fourfold sums and six-site supports with at
least 48. The six-site result does not cover every support or arbitrary
kernel weights. No computational cover is used, and sharpness of the
five- and six-site constants is not asserted.

The version 11 follow-up fixes the five selected input values of `g`
in the proportions `9:5:5:5:5`, with kernel weight one on five distinct
integer sites.
A comparison of translation defects gives the upper coefficient
`3143504/1566459`. Extreme points of finite translated level sets give
a strict, input-dependent correction. An explicit finite probability
law proves that the specified family of certificate combinations cannot
lower that uniform coefficient. This is optimality of the stated proof
family, not a determination of the true profile supremum or of `K_5`.
The formal probability law is not realized by any nonzero finite input;
whether it can be approached remains unresolved.

No fresh primary-literature search was completed for this particular
profile refinement. The retained source reading below supports the
attribution of earlier ingredients, not a historical-priority finding
for the new bound or its certificate-family barrier.

For `K_n = sup R_F(f,g)` over all `n`-point integer sets and all nonzero
finitely supported nonnegative `f,g`, the resulting bounds are

```text
K_1 = 1,  K_2 = 5/4,  K_3 = 3/2,  K_4 = 7/4,
(n+3)/4 ≤ K_n ≤ (√n+1)²/4  (n≥2),
K_n ≤ 7n/16  (n≥4),  K_5 ≤ 35/16,  K_6 ≤ 21/8,
K_n/n → 1/4.
```

The geometric lower example uses `f_N(x)=2^(−Σx_i)` on
`{0,…,N}^d`, with the second profile equal to one at zero and one-half
at the coordinate vertices. An earlier continuous template is Colesanti's
orthant exponential, Theorems 1.1–1.2 of
[arXiv:math/0512098v1](https://arxiv.org/abs/math/0512098v1)
(5 December 2005); its reflected ratio is derived below.
Geometric sequences also occur explicitly in Matolcsi, Ruzsa, Shakan
and Zhelezov, Example 11.2,
p. 19, of arXiv:2003.04075v1; their Theorems 10.1–10.2 develop product
and fibre methods. Related reflected product exponentials occur in
Madiman, Manui, Zawalski and Zvavitch, Lemma A.3, p. 34, of
arXiv:2608.10456v1. Those two original PDF pages were checked.

The adaptation here restricts the second profile to the simplex vertices
and counts the disjoint exterior faces. If its kernel values have
maximum `M` at zero and total `K`, and `S_N=2−2^(−N)`, the masses are

```text
P_N = S_N^d + d·2^(−N−1) S_N^(d−1),
Q_N = M S_N^d + (K−M) S_N^(d−1)/2.
```

Their quotient tends to `(K+3M)/4`, giving `(n+3)/4` for the
indicator kernel on `n=d+1` sites. A positional embedding with base
`2N+3` preserves all finite sums and differences. The integer support
may vary with `N`; this is a supremum over support locations, not a
limit on an arbitrary fixed support. The sequence family and product
method are prior ingredients. The exact coefficient's publication history
remains unresolved. The exact value of `K_n` remains unresolved here for `n≥5`;
this is a construction-level adaptation, without a historical-priority claim.

For indicator inputs, the retained classical simplex example is an exact
specialization of known counting. Daniel Glasscock's
[*Sumset Estimates in Abelian Groups*](https://sites.uml.edu/daniel-glasscock/files/2021/06/MSThesis.pdf),
CEU master's thesis dated 24 February 2012, Lemma B.1, pp. 37–38,
gives both counts for `A=V(n−1,n−2)` and `U=V(n−1,1)`:

```text
|A+U| = binomial(2n−2,n−1),
|A−U| = binomial(2n−3,n−1) + (n−1)binomial(2n−4,n−2).
```

Their ratio is `(n²−2)/(4n−6)`. The thesis develops the classical
simplex family of Hennecart, Robert and Yudin, whose paper also uses
integer encoding. The finite-support manuscript supplies a sufficient
base for the integer example; the family, counts, negative-coordinate
argument and positional encoding are prior techniques. These indicator
examples give the limiting lower coefficient `1/4`. The general upper
bound gives the matching coefficient for arbitrary nonnegative finite
inputs, so `K_n/n→1/4`. The exact support supremum `K_n` is determined
for `1≤n≤4`; its exact value remains unresolved here for `n≥5`.

A lossless reduction of arbitrary profile weights to indicator profiles
at the same support size would give an incorrect bound. For `F={0,1}`
and `f=g` with values `(2,1)`, the denominator is `4+2+1=7`, while the
reflected numerator is `2+4+2=8`. The ratio `8/7` exceeds the indicator
coefficient `e_2=1`. Integrating the profile `g` also gives indicator
denominators totaling `5+3=8`, above the actual denominator `7`.
The mixed-energy proof avoids this step, and the kernel-level argument
keeps the profile unchanged.

For a constant kernel `k=c1_F`, the support estimate proves the fourfold
inequality whenever `|4F| ≥ C_n⁴`. A `B₄` set has distinct unordered
four-term sums, with repetitions allowed, and therefore
`|4F| = binomial(n+3,4)`. This support condition appears at `h=4` in the
independent addition graph of Ruzsa's
[*Sumsets and structure*, Chapter 1, Section 5, pp. 11–12](https://tensen.net/research/static/gc-data/sumset/Additive-Combinatorics.pdf),
using the linked manuscript's pagination. For every `n>1`,

```text
C_n⁴ < binomial(n+3,4).
```

An exact polynomial factorization with `x=√n` proves this comparison;
the two sides agree when `n=1`.

Thus the constant-kernel inequality holds for every finite nonempty `B₄`
set. It is strict for `n>1`, `c>0` and nonzero `f,g`. The singleton case
uses `R_F≤1`; `c=0` gives equality at zero.

For a nonzero kernel on a `B₄` support, the fourfold max-convolution mass
is the complete homogeneous polynomial `h₄(k)`. The multinomial expansion
gives `K⁴≤24h₄(k)`. If `K/M≥9`, then

```text
(√K+√M)²/4 ≤ 4K/9 < K/24^(1/4) ≤ h₄(k)^(1/4),
```

which proves the strict reflected fourfold inequality in this nonconstant
weight regime. Both the `B₄` support condition and `K/M≥9` are required
for this corollary; arbitrary kernel weights on all `B₄` sets remain
outside the result.

Gyarmati, Hennecart and Ruzsa's Theorem 2 supplies a direct comparison
through its threefold factor. A `B₄` set also has distinct
unordered three-term sums: append the same fourth point to any proposed
equality. Thus `|3F| = binomial(n+2,3)`, and, for `n>1`,

```text
|3F|⁴ / |4F|³ = 32n(n+1)(n+2) / (3(n+3)³) > 1,
32n(n+1)(n+2) − 3(n+3)³ = (n−1)(29n²+98n+81) > 0.
```

Consequently that theorem's factor `|3F|^(1/3)` is larger than
`|4F|^(1/4)` throughout this class. The direct factor substitution does
not give the fourfold conclusion. Max-convolution, the functional
tripling parameters and their tensorization belong to the prior framework
credited above. The mixed-energy argument gives a direct classical route
to the displayed weighted bound. Whether the prior max-convolution
theorems also imply these bounds or the `B₄` conclusions remains
unestablished, as does priority in the wider literature.
A `B₄` support admits a Freiman-4-isomorphic lift to the free simplex
`{0,e₁,…,eₙ₋₁}` in a binary cube, but deriving the required reflected
inequality on that simplex from the inspected prior results remains
unestablished.

### Colesanti's continuous reflected ratio

Andrea Colesanti's
[*Functional inequalities related to the Rogers-Shephard inequality*,
arXiv:math/0512098v1](https://arxiv.org/abs/math/0512098v1)
(5 December 2005), Theorems 1.1–1.2, pp. 4 and 6–7, supplies an earlier
reflected ratio bound and its orthant-exponential example. The 22-page
preprint was read in full, including a visual check of every PDF page.
The journal body has not been checked.

For a nonnegative log-concave `u` on `R^d`, Definition 1.1, p. 3, and
Theorem 1.1 give

```text
Δu(z) = sup_{x−y=2z} √(u(x)u(y)),
∫Δu ≤ 2^d ∫u.
```

Use supremum-product convolution and Lebesgue `L¹` norms on `R^d`.
For a nonnegative log-concave `h` with `0<∫h²<∞`, put `h̃(x)=h(−x)`.
Then

```text
Δ(h²)(z) = sup_{x−y=2z} h(x)h(y) = (h⋆h̃)(2z),
(h⋆h)(s) = h(s/2)²,
∫Δ(h²) = 2^(−d) ‖h⋆h̃‖₁,
‖h⋆h‖₁ = 2^d ∫h²,
‖h⋆h̃‖₁ / ‖h⋆h‖₁ ≤ 2^d.
```

Log-concavity gives the upper bound in the second identity, and
`x=y=s/2` attains it. The next two identities are changes of variables;
the last line follows by applying Theorem 1.1 to `u=h²`.
Theorem 1.2 gives equality for
`h(x)=exp(−aΣx_i)` on the nonnegative orthant and zero elsewhere,
with `a>0`, after rescaling. Sampling at `a=log 2` and truncating gives
the geometric product used in the finite lower construction.

This implication concerns equal log-concave profiles on `R^d`.
The manuscript allows independent `f,g` and a separate multiplier `k`.
Small-cell thickening preserves a discrete quotient but can violate
log-concavity; a log-concave envelope changes both masses without an
established comparison of their quotient. Finite integer encoding
preserves the relevant sums and differences but does not supply
log-concavity or turn the factor `2^d` into the manuscript's support or
weight coefficient. The inspected routes do not settle that derivation
or the discrete coefficient's priority.

A separate endpoint caveat concerns the proof of Theorem 5.1, pp. 21–22,
of this v1:
at `α=−1`, the displayed equality profile is `1/x` on `(0,1)`, which
is not integrable. That example does not establish admissible equality
attainment at the endpoint. This caveat does not affect the log-concave
Theorems 1.1–1.2 above.

### Comparison with alpha-concave functions

Madiman, Manui, Zawalski and Zvavitch,
[*Integral inequalities for alpha-convolutions of alpha-concave functions*,
arXiv:2608.10456v1](https://arxiv.org/abs/2608.10456v1)
(11 August 2026), use the same sup-product convolution at `α=0`.
Their Theorem 5.2, equation (37), pp. 26–28, bounds the continuous reflected
ratio by `2^d` for normalized log-concave functions on `R^d`.
The parameter `d` is ambient dimension, not the number of support points.
The complete 37-page preprint was read, including both proofs of that
theorem and Section 6. Original PDF pages 2, 19–20, 25–29, 31–32 and 34 were
also visually checked; this is not an all-page image review.

The proof of Theorem 6.2, pp. 31–32, contains a step that transfers to
arbitrary nonnegative finitely supported functions on the integers:

```text
‖a⋆b̃‖₁ ‖a⋆c̃‖₁ ≥ ‖a‖₂² ‖b⋆c̃‖₁.
```

It follows by summing the pointwise product inequality before the proof
uses Lemma 6.1 and Theorem 3.8. Put `h=g1_F≠0`,
`P_F=‖f⋆h‖₁`, `Q_F=‖f⋆h̃‖₁`, and `m=|supp(h)|`.
Taking `a=h̃, b=f, c=h` gives

```text
P_F ‖h⋆h‖₁ ≥ ‖h‖₂² Q_F,
‖h⋆h‖₁ ≤ ((Σh)²+Σh²)/2,
Q_F/‖f⋆g‖₁ ≤ Q_F/P_F ≤ (m+1)/2.
```

The middle estimate counts unordered pairs, including diagonals; Cauchy
gives the last step, and the full denominator is at least `P_F`.
This coefficient exceeds `C_m=(√m+1)²/4` by
`(√m−1)²/4` for every `m>1`. This derivation does not recover the
target coefficient or its strictness. The zero restricted profile gives
zero separately.

Allowing every supported truncation and rescaling of the common profile
does not improve this particular route. Take `h=1_F` on a Sidon set `F`
of size `n`, with all unordered pair sums, including diagonals, distinct.
For any nonzero `a` supported on `−F`, normalize `max a=1` and sort
its values as `0≤a₁≤⋯≤aₙ=1`. The pointwise first-factor bound
`‖a⋆f̃‖₁≤P_F` gives the coefficient

```text
‖a⋆h̃‖₁/‖a‖₂² = (Σⱼ j aⱼ)/(Σⱼ aⱼ²) ≥ (n+1)/2.
```

The inequality follows from ordered Chebyshev and `aⱼ≥aⱼ²`;
all values one attain equality. This excludes only the triangle step
combined with that pointwise first-factor estimate. Sharper estimates
depending on `f`, other common profiles with a proved control, and other
uses of the source are not excluded by this test.

Theorem 5.2's proofs retain log-concavity or convex level sets and
Lebesgue-volume scaling; Lemma 5.1, pp. 24–26, does not transfer by replacing
volume with lattice cardinality. Thickening each integer by an interval
of radius `0<ε<1/4` preserves the discrete quotient exactly but can fail
even quasiconcavity.
The source's difference operator, defined on p. 19, satisfies
`Δ₀(u²)(x/2)=(u⋆ũ)(x)`, with the integral scaling derived in the
Colesanti comparison above. Equation (29), p. 20, requires log-concavity.
Positive powers preserve that concavity requirement and the support.
Nor does normalization alone supply Lemma 6.1's moment estimate:
a ten-point profile with values `1,1/4,…,1/4` has
`‖u‖₁=13/4>2‖u‖₂²=25/8`.

These tests identify the limits of the stated derivations. They neither
rule out every further argument from this source nor establish novelty,
historical priority or finite-`n` optimality.

### Comparison with continuous autoconvolution bounds

Two inspected primary sources concern ordinary autoconvolution with a
different input normalization:

| Primary source | Statement and reading scope |
| --- | --- |
| Alexander Cloninger and Stefan Steinerberger, *On suprema of autoconvolutions with an application to Sidon sets*, [arXiv:1403.7988v3](https://arxiv.org/abs/1403.7988v3) (22 April 2016); published in *Proceedings of the American Mathematical Society* 145(8), 3191–3200 (2017) | Section 1.2 maximizes continuous `L¹` mass under an ordinary-autoconvolution supremum constraint on a fixed interval. Section 3 discretizes interval masses on a simplex with `Σaᵢ=4n`. The eight-page extraction was read; it was marked partial and reported an omitted image. Original PDF pages 4–8 were visually checked. The large computation was not reproduced; the journal text was not read. |
| Paata Ivanisvili and Xinyuan Xie, *Grokability in five inequalities*, [arXiv:2605.05193v1](https://arxiv.org/abs/2605.05193v1) (6 May 2026) | Theorem 5 states `‖f*f‖∞ ≥ 1.2802(∫f)²` for nonnegative integrable `f` supported on `[-1/4,1/4]`. The theorem and its complete Section 2.4 proof were read, including visual checks of original PDF pages 5, 16 and 17. The proof refines an error estimate and relies on an earlier computation from Cloninger–Steinerberger. This is a report of the source's theorem; that numerical dependency was not reproduced or independently certified here. The unrelated proofs were not all reviewed. |

These continuous statements constrain `L¹` mass. The covering part of the
finite-support manuscript instead optimizes the weighted squared input mass
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

Ken Lau, Chandra Nair and Zhaobang Zhu's
[*A maximal-coupling information inequality of sums on finite subsets of
Abelian groups*](https://chandra.ie.cuhk.edu.hk/pub/papers/comb/MCIneq.pdf)
(author-hosted manuscript, 2026), Theorem 5, proves a fractional-partition
upper bound for maximal sum entropy. Write `E_S` for the maximum entropy
of `Σ_{i∈S} X_i` over joint laws with specified finite-support marginals.
For nonnegative weights on nonempty subsets of `{1,…,r}`, it states

```text
E_{1,…,r} ≤ Σ_S γ(S) E_S,
provided Σ_{S∋i} γ(S) = 1 for each i.
```

The theorem holds in arbitrary abelian groups. With a common marginal
`q`, write `E_j(q)` for the corresponding maximum with `j` summands.
The pair, triple and singleton substitutions give

```text
E_4(q) ≤ 2 E_2(q),
E_4(q) ≤ (4/3) E_3(q),
E_4(q) ≤ 4 H(q).
```

These direct substitutions upper-bound `E_4`. They do not establish
`4(E_−(p,q)−E_+(p,q)) ≤ E_4(q)`, which is sufficient for the weighted
reflected fourfold comparison. Whether a further argument from the full
framework proves that comparison remains unestablished.

The complete seven-page author-hosted manuscript and its original page
images were reviewed. The comparison concerns that text; a final
publisher edition was not reviewed. It contains no displayed occurrence
of the constructions or numerical two-set bound considered here. This
bounded observation supplies no priority conclusion.

Lau's [*Information Inequalities: Subadditivity & Relationships with
Additive Combinatorics*](https://chandra.ie.cuhk.edu.hk/group/thesis/ken_thesis.pdf),
a PhD thesis at the Chinese University of Hong Kong (July 2025), gives the
relevant typical-set theorem for arbitrary Abelian groups in Appendix B.2.
[Theorem B.2.4, printed pp. 130–131](https://chandra.ie.cuhk.edu.hk/group/thesis/ken_thesis.pdf#page=143)
(PDF pages 143–144) states the same maximal-coupling sum-image limit for
finite-support marginals on any Abelian group `G`, with the shrinking
tolerances specified above.
Apply the cardinal sum-triangle inequality
`|A||B+C| ≤ |A+B||A+C|` in each Cartesian power `G^n` to the three
marginal typical sets. Ruzsa's [*Sumsets and structure*, Theorem 8.7](https://tensen.net/research/static/gc-data/sumset/Additive-Combinatorics.pdf)
states this cardinal inequality in every commutative group. Taking
logarithms, dividing by `n` and using Theorem B.2.4 gives

```text
H(p) + E_+(q,r) ≤ E_+(p,q) + E_+(p,r).
```

For the singleton factor `|A_n|`, apply Theorem B.2.4 with a point mass at
zero as the second marginal. Thus the maximal sum-triangle inequality on
arbitrary Abelian groups follows from prior cardinality and typical-set
results, with each coupling optimized separately.
Lau's Corollary 4.2.7 states it for finitely generated
torsion-free groups; [Remark 4.2.8, printed p. 84](https://chandra.ie.cuhk.edu.hk/group/thesis/ken_thesis.pdf#page=97)
says a stand-alone information-theoretic proof was not known to the authors.
The later Lau–Nair–Zhu manuscript labels the arbitrary-group formulation a
conjecture on page 7. The derivation above uses a cardinality inequality
and does not supply such a stand-alone information-theoretic proof.

The thesis also proves a signed four-copy inequality in
[Theorem 4.2.33, printed pp. 95–98](https://chandra.ie.cuhk.edu.hk/group/thesis/ken_thesis.pdf#page=108)
(PDF pages 108–111). Write `S_4(q)` for the maximum of
`H(Y₁−Y₂−Y₃+Y₄)` when each `Yᵢ` has marginal `q`. For marginals `p,q`,
the theorem gives

```text
S_4(q) ≤ 4 E_+(p,q) + E_−(p,p) − 4 H(p).
```

This upper bound concerns a signed sum and contains an auxiliary optimized
difference entropy. Replacing `S_4(q)` with the all-plus maximum `E_4(q)`,
or deleting `E_−(p,p)`, requires an additional argument. The theorem and the
direct substitutions inspected do not supply the reflected comparison
`4(E_−(p,q)−E_+(p,q)) ≤ E_4(q)`.

Text was extracted from all 157 thesis pages. Detailed reading covered
Theorem 4.1.1 and its proof, Corollary 4.2.7 and Remark 4.2.8,
Theorem 4.2.33 and its proof, and Appendix B.2. The statements and complete
proofs of Theorems 4.2.33 and B.2.4 were also checked on original PDF
pages 108–111 and 143–144. This is not a claim to have read the entire thesis.

The logarithm of a sumset's size is its support entropy. It generally
differs from the Shannon entropy of a sum of independent uniform elements.
The two construction papers also give direct finite counting proofs, and
both fourfold manuscripts prove their weighted inequalities directly.
The entropy derivation maximizes over couplings with prescribed marginals;
it does not substitute the entropy of independent uniform inputs.

## A finite entropy test for the support bound

The support bound has an exact reformulation that retains its displayed
coefficient. Fix nonempty finite supports `A,F`, and use natural logarithms.
For a positive constant `C`, the comparison

```text
E_−(p,q) − E_+(p,q) ≤ log C  for every pair of marginals p on A, q on F
```

is equivalent to `‖f⋆g̃‖₁ ≤ C‖f⋆g‖₁` for every nonzero nonnegative
`f,g` supported on `A,F`. To see this, define

```text
L_±(u,v) = log Σ_{z∈A±F} exp(max_{x±y=z} (u_x+v_y))
         = max_{p,q} [E_±(p,q) + p·u + q·v].
```

The second equality is the finite Gibbs variational formula, with one
maximizing pair selected in each output fiber. The functions `E_±` are
concave and upper semicontinuous on the compact marginal simplices, so
convex conjugacy also gives the reverse implication. Positive profiles
are `f=exp(u), g=exp(v)`; zero values follow by continuity. Restricting
an arbitrary `g` to `g1_F` leaves `‖f⋆(g1_F)̃‖₁` unchanged and can only
decrease the denominator. This extends the bound to the full denominator
used in the manuscript. If `g1_F=0`, the numerator is zero.

For a nonzero kernel with positive support `F={y:k_y>0}`, replacing `v`
by `v+log k` in the numerator gives the corresponding numerical test,
again for every pair of marginals `p,q` on `A,F`:

```text
E_−(p,q) − E_+(p,q) + Σ_y q_y log k_y
  ≤ log((√K+√M)²/4),   K=Σ_y k_y, M=max_y k_y.
```

This is a finite derivation using established variational and convex-duality
tools. Liu, Courtade, Cuff and Verdú,
[*Information-Theoretic Perspectives on Brascamp-Lieb Inequality and Its
Reverse*, arXiv:1702.06260v3](https://arxiv.org/abs/1702.06260v3)
(3 December 2017), Theorem 4, provide the relevant general
forward-reverse entropy duality. The theorem was read and its finite
projection-map specialization was checked. The finite comparison above
is derived here from Gibbs variational duality and convex conjugacy;
the general duality statement alone does not evaluate the reflected
coefficient.

For example, the singleton-partition substitution in Lau–Nair–Zhu's
Theorem 5 gives `E_−(p,q) ≤ H(p)+H(q)`. An independent coupling gives
`E_+(p,q) ≥ max(H(p),H(q))`. Together these yield a gap at most
`min(H(p),H(q)) ≤ log n`, where `n=|F|`. This direct comparison falls
short of `log C_n`, because `C_n=(√n+1)²/4<n` for `n>1`.
The remaining literature question is whether a prior theorem or a further
argument supplies the displayed smaller coefficient for arbitrary
profiles. The reformulation and these direct substitutions do not settle
that historical question or establish finite-`n` optimality.

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
The publisher page for Matolcsi et al. returned an access challenge on
30 September 2026, without the journal article or a source link.

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
