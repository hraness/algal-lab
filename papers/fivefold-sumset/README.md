# A counterexample to the fivefold sumset inequality

This note gives finite integer sets `A` and `B` for which

```text
|A-B|^5 > |A+B|^5 |5B|.
```

Here `5B` is the set of sums of five elements of `B`. The main construction
starts with nonnegative integer vectors of dimension 128. Their coordinate
sums are at most 160 for `A` and 32 for `B`; the vectors are encoded in base
193. Counting positive and negative coordinates gives a short exact certificate.

An elementary companion construction uses `k=2048`, `n=271k=555008`
coordinates and base 9. The first set encodes digits from 0 through 7 with
total `247k`; the second encodes binary words with exactly `16k` ones.
Its complete finite proof uses type counting and generating polynomials.
Small rational comparisons and the binomial theorem establish strictness.

Gyarmati, Hennecart and Ruzsa asked when the corresponding inequality holds
universally in [*Sums and differences of finite sets*](https://doi.org/10.7169/facm/1229618749),
equation (9), page 177. Their discussion on page 182 left the cases four
and five unresolved. This note supplies a
counterexample to the fivefold statement in that text; it makes no priority
or current-status claim. The main construction uses unequal radii in the
classical lattice-simplex family used by Hennecart, Robert and Yudin (1999).
Glasscock's 2012 master's thesis, Lemma B.1, already gives the exact
unequal-radius count and its proof. The main example specializes that formula
to `(m,a,b)=(128,160,32)` and verifies the strict fivefold comparison. The
[literature comparison](../sumset-literature.md) records these attributions
and the scope of the later-source review.

An asymptotic version of the binary construction follows from
[Lau and Nair's typical-set theorem](https://arxiv.org/abs/2312.11017v3),
Theorem 10 in Appendix C, applied to the displayed marginals in the paper
with elementary generating-polynomial bounds. One binary typical set
supplies all five summands. The finite proof gives the stated dimension
555,008 directly. For the related weighted max-convolution framework, see
[Matolcsi, Ruzsa, Shakan and Zhelezov](https://arxiv.org/abs/2003.04075v1),
Section 8.

From this directory, using Python 3.10 or later:

```sh
python3 -B verify.py
python3 -B -m unittest -v test_verify
```

The verifier computes the simplex construction's three cardinalities twice:
once with a single sum of binomial coefficients and once with a double sum
over positive and negative supports using factorials. It checks the recorded
integers and the strict inequality. The tests compare both formulas with
four explicitly enumerated tiny set pairs and reject inputs outside the
fixed limits. Neither command searches for parameters or constructs the
large example.

`main.tex` contains both proofs and a short standalone arithmetic check for
the simplex construction. The companion proof requires no large-number
evaluation. Build with a standard LaTeX engine or `tectonic main.tex`.
