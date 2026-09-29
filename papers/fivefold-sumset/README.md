# A counterexample to the fivefold sumset inequality

This note gives finite integer sets `A` and `B` for which

```text
|A-B|^5 > |A+B|^5 |5B|.
```

Here `5B` is the set of sums of five elements of `B`. The construction starts
with nonnegative integer vectors of dimension 128 whose coordinate sums are
at most 160 for `A` and 32 for `B`, then encodes them in base 193. Counting
positive and negative coordinates gives a short exact certificate.

Gyarmati, Hennecart and Ruzsa asked when the corresponding inequality holds
universally in [*Sums and differences of finite sets*](https://doi.org/10.7169/facm/1229618749),
equation (9), page 177. Their discussion on page 182 left the cases four
and five unresolved. This note supplies a
counterexample to the fivefold statement in that text; it makes no priority
or current-status claim. The construction uses unequal radii in the classical
lattice-simplex family used for their sixfold counterexample on page 182.

From this directory, using Python 3.10 or later:

```sh
python3 -B verify.py
python3 -B -m unittest -v test_verify
```

The verifier computes the three cardinalities twice: once with a single sum
of binomial coefficients and once with a factorial-based double sum over
positive and negative supports. It checks the recorded integers and the
strict inequality. The tests compare both formulas with four explicitly
enumerated tiny set pairs and reject inputs outside the fixed limits.
Neither command searches for parameters or constructs the large example.

`main.tex` contains the proof and a short standalone arithmetic check. Build
with a standard LaTeX engine or `tectonic main.tex`.
