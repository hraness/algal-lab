# Literature comparison for the sumset manuscripts

Review date: 29 September 2026. The two manuscripts give explicit constructions
and exact certificates. The comparison below credits their known ingredients
and distinguishes their conclusions from related sumset problems. It supports
the stated mathematical claims and the comparison with Zheng's theorem;
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
| Gyarmati, Hennecart and Ruzsa, *Sums and differences of finite sets* (2007), [DOI 10.7169/facm/1229618749](https://doi.org/10.7169/facm/1229618749) | Equation (9), p. 177 asks when `|A−B| ≤ |A+B| |hB|^(1/h)` holds universally. Page 182 gives a sixfold simplex counterexample and leaves four and five unresolved. The present construction contradicts the fivefold statement in that historical text. |
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
| Gyarmati, Hennecart and Ruzsa (2007), Section 2 | Their finite-set transfer gives `θ ≥ 1 + log(|U−U|/|U+U|)/log(2 max U+1)` under its strict difference-count hypothesis. The manuscript uses this existing lemma and enforces the hypothesis by dilation. |
| F. Zheng, *Sums and differences of sets: a further improvement over AlphaEvolve*, [arXiv:2506.01896v1](https://arxiv.org/abs/2506.01896v1) (2025) | Theorem 1, PDF p. 5, gives `1.173077` for the same two-set problem using bounded-coordinate integer vectors and large-deviation estimates. The current identifiable preprint is v1; its objective, theorem and numerical table were checked on the PDF pages. The manuscript's exact certificate improves this specifically checked bound. |
| Matolcsi, Ruzsa, Shakan and Zhelezov, *An analytic approach to cardinalities of sumsets*, [arXiv:2003.04075v1](https://arxiv.org/abs/2003.04075v1) (2020) | Definition 8.1 defines `(f⋆g)(z)=max_{x+y=z} f(x)g(y)`. The manuscript's `P` and `Q` are exactly `‖w⋆w‖₁` and `‖w⋆w̃‖₁`. Theorem 8.6 equates weighted and set versions of an induced tripling parameter. This establishes prior max-convolution machinery; that theorem does not supply the reflected quotient and encoding-diameter bound used here. |
| Becker, Ivanisvili, Krachun and Madrid, *Discrete Brunn–Minkowski inequality for subsets of the cube*, [arXiv:2404.04486v2](https://arxiv.org/abs/2404.04486v2) (2024) | Theorem 1.3 settles the two-point norm conjecture stated after Theorem 11.1 of the preceding preprint. It gives a lower bound for a triple max-convolution using independent norm factors. That conclusion does not itself give an upper bound for a quotient of linked ordinary and reflected convolutions. |
| Hosle and Ivanisvili, *Geometric Block Exponents and a Uniform Mixed-Alphabet Sumset Inequality*, [arXiv:2606.25350v1](https://arxiv.org/abs/2606.25350v1) (2026) | Theorem 1.5 treats a two-term first sequence and a nonincreasing second sequence. Proposition 7.3 and Corollary 1.7 give a sumset lower bound with exponent `log 4/log 6` for a binary first alphabet. The sparse fourteen-digit support used here is outside that hypothesis; the conclusion concerns sumset expansion, rather than a reflected quotient. |
| Lin and Li, *Settling the optimal exponent relating sumsets and difference sets*, [arXiv:2607.27199v1](https://arxiv.org/abs/2607.27199v1) (2026) | Proves a supremum of two for `C(A)=log(|A+A|/|A|)/log(|A−A|/|A|)`. This one-set normalization differs from `θ`. Its Section 3 identifies the reported search value `1.21` with `C(A)`. |

The max-convolution operation, weighted sumsets and tensorization therefore
require prior attribution. The weighted-digit paper records a particular
reflected comparison, explicit integer encoding and certified parameters.
A larger exponent for another normalization cannot replace a comparison
under the displayed quantifiers.

## Entropy translations

Lau and Nair's *Information inequalities via ideas from additive
combinatorics*, [arXiv:2312.11017v3](https://arxiv.org/abs/2312.11017v3)
(5 February 2025),
Theorem 1 and its proof translate a class of cardinality inequalities into
entropy inequalities with prescribed marginals and separate optimization
over couplings. The proof uses type classes and integer encoding. These
are established methods relevant to further weighted formulations of the
fourfold and fivefold question.

Theorem 1 is unchanged from v2. Version 3 adds Appendix B and Theorem 10,
which states a typical-set sum-image limit in terms of the maximum entropy
over couplings. The main equivalence theorem and the added displayed limit
were read in the current HTML. Parts of the appendix extraction are malformed,
so this comparison does not claim a complete verification of its proof.

The logarithm of a sumset's size is its support entropy. It generally
differs from the Shannon entropy of a sum of independent uniform elements.
The coupling requirements and repeated-set constraints must be preserved
when applying a translation theorem. The two manuscripts' present proofs
use direct finite counting and do not depend on replacing support entropy
by Shannon entropy.

## Scope of this review

The review followed the historical question, its simplex antecedents,
forward citations, weighted and entropy formulations, and related 2025–2026
preprints. The decisive simplex formulas and thesis attribution were checked
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
The manuscripts
therefore make no global-priority, optimality or current-record assertion.
Their exact certificates establish the displayed inequalities independently
of that unresolved historical assessment.
