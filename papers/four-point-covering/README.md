# Reflected max-convolution inequalities for finite supports

[Read the paper](main.pdf).

For every finitely supported nonnegative kernel `k` on the integers, put
`K=‖k‖₁` and `M=‖k‖∞`. For arbitrary nonzero finitely supported
nonnegative inputs `f,g`, the paper proves

```text
‖f⋆(gk)̃‖₁ / ‖f⋆g‖₁ ≤ (√K+√M)²/4.
```

Here `⋆` is max-product convolution. The denominator retains all values
of `g`, including those outside the kernel support; values on the
support may vanish. The proof uses the mixed weighted form of the
classical equality of sum and difference representation energies.
A kernel-level version also retains the distribution of the kernel values.
Weighted winner allocations give another bound,
`max{K/2,(K+3M)/4}`, for every finite support.

For `k=1_F`, `|F|=n`, the resulting bound is
`C_n=(√n+1)²/4`, strict for each input pair when `n>1`.
If `K_n` is the supremum over all `n`-point integer supports and
nonzero finite inputs, then

```text
K_1 = 1,  K_2 = 5/4,  K_3 = 3/2,  K_4 = 7/4,
(n+3)/4 ≤ K_n ≤ (√n+1)²/4  (n≥2),
K_n/n → 1/4.
```

The exact two- and three-site bounds follow from allocation estimates.
The four-site upper bound uses an inequality for four events and finite
linear-programming duality. The lower bounds use a geometric product
and finite integer embeddings.
For each nonempty prescribed list of positive kernel values with sum `K`
and maximum `M`, the geometric construction gives ratios tending to
`(K+3M)/4`. The integer locations may vary with the truncation; this is
a supremum over supports. The coefficient is sharp whenever `K≤3M`,
regardless of support size. It is also sharp for every such list of at
most four values: the weighted upper bound follows by integrating
kernel level sets. Zero kernel values do not contribute to the support,
and the zero kernel has ratio zero.

Averaging the sharp four-site bound over four-subsets gives
`K_n≤7n/16` for every `n≥4`. In particular:

| Support size | Reflected ratio upper bound |
| --- | --- |
| 4 | `7/4` |
| 5 | `35/16` |
| 6 | `21/8` |

These non-strict bounds hold with the full denominator and arbitrary
nonnegative input weights. For constant kernels their fourth powers
give the strict fourfold inequality when the fourfold sumset has at
least 23 elements on five sites or 48 elements on six sites.
The six-point result does not cover every six-point support.

The paper proves the reflected fourfold inequality for arbitrary
nonnegative kernel weights on at most four points and on
`{0,2,7,8,11}`, and for constant kernels on every five-point support.
It also proves the constant-kernel result on every finite `B₄` set,
whose unordered four-term sums are distinct with repetitions allowed.
On `B₄` supports the weighted result holds when `K/M≥9`.
The unrestricted fourfold problem remains unresolved here.

The covering proof uses finite linear-programming duality, classifies
the five four-point collision patterns and determines their sharp
unweighted covering constants. That stronger covering bound fails on
`{0,2,7,8,11}` by `1/16`. The reflected inequality on this support
for arbitrary kernels follows from allocation estimates and 240 rational
coefficient certificates. All original certificates are retained.

For the constant-kernel five-point theorem, an elementary argument gives
`|4F|≥30` for Sidon supports; supports with pair-sum collisions use
separate covering estimates. The paper also retains the stronger sharp
Sidon bound `|4F|≥39`, whose proof uses Freiman's classical `3k−4`
theorem in the restatement on page 1 of Bollobás, Leader and Tiba,
[*A strengthening of Freiman's 3k−4 theorem*, arXiv:2204.09816v1](https://arxiv.org/abs/2204.09816v1).
That statement was checked on the original PDF page; Freiman's original
proofs were not read.

The geometric construction samples and truncates Colesanti's orthant
exponential from Theorems 1.1–1.2 of
[*Functional inequalities related to the Rogers–Shephard inequality*](https://arxiv.org/abs/math/0512098v1).
Related geometric sequences appear in Matolcsi, Ruzsa, Shakan and
Zhelezov's Example 11.2, and reflected product exponentials appear in
Madiman, Manui, Zawalski and Zvavitch's Lemma A.3.
The paper also retains the classical indicator-simplex lower example
with ratio `(n²−2)/(4n−6)`, credited to Glasscock's Lemma B.1,
pp. 37–38, and the simplex family of Hennecart, Robert and Yudin.
These indicator examples supply the limiting lower coefficient `1/4`.
Combined with the general upper bound, they give `K_n/n→1/4` for arbitrary
nonnegative finite inputs. Historical priority remains unestablished,
and the exact value of `K_n` remains unresolved here for `n≥5`.

The [three-point paper](../three-point-fourfold/main.pdf) gives a separate
direct proof using scalar inequalities and telescoping potentials.
The shared [literature comparison](../sumset-literature.md) records the
exact primary sources, the relation to prior max-convolution and entropy
results, and the limits of the priority assessment.

The arbitrary-weight five-point proof includes 240 rational certificates:
two comparisons for each of the 120 orders of the five kernel weights.
The standard-library checker reconstructs all fourfold fibers and
polynomial coefficients and verifies both comparisons on every order.
From this directory, run:

```sh
python3 -B verify_five_point.py
```

The checker needs the files in `five-point-certificates/` beside it. It
checks exact integer inequalities and corruption controls without a
numerical optimizer. The paper gives the hand argument connecting these
coefficient comparisons to the reflected inequality.

The LaTeX sources include the complete hand proofs and the precise
classical theorem used for the stronger Sidon cardinality bound.
To build from this directory with Tectonic:

```sh
tectonic --only-cached --untrusted --keep-logs main.tex
```

All referenced TeX files must be present. The cached-only command requires
the TeX packages to have been installed previously. The checked PDF is
included for readers who do not have that cache.

The proofs and presentation were developed and reviewed with AI assistance.
The [publication review](../PUBLICATION-REVIEW.md) records that review and
the PDF checks; it does not represent human peer review or journal acceptance.
