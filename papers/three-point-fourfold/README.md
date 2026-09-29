# A fourfold max-convolution inequality on three-point integer supports

This note proves a strict weighted inequality for every support `F` of three
distinct integers. The weights `g` and `k` are positive on `F`; `f` is any
nonzero finitely supported nonnegative function on the integers.

For max-convolution `(f ⋆ g)(s) = max_{x+y=s} f(x)g(y)` and reflection
`h̃(x) = h(-x)`, the theorem is

```text
||f ⋆ reflection(gk)||₁⁴ < ||f ⋆ g||₁⁴ ||k ⋆ k ⋆ k ⋆ k||₁.
```

Here `gk` is the pointwise product, functions are zero outside their
specified supports, and each norm is the sum of the function's values.
There is no bound on the number of nonzero entries or the positive values
of `f`.

The [manuscript](main.pdf) ([LaTeX source](main.tex)) supplies the full proof. Non-arithmetic triples
use a uniform bound for the reflected quotient and a classification of
fourfold collisions. Arithmetic progressions use polynomial estimates and
piecewise-linear potentials whose differences cancel when summed over the
sequence. The proof includes every coefficient inequality and every vertex
needed to check those potentials. Strictness follows from a scalar margin
or the first nonzero entry of the sequence.

Taking `g = k = 1_F` and `f = 1_A` gives
`|A-F|⁴ < |A+F|⁴ |4F|` for every finite nonempty integer set `A` and every
three-element integer set `F`. The weighted theorem concerns exactly three
support points. The fourfold question for arbitrary finite supports and
the result's literature priority remain unresolved here. The
[literature comparison](../sumset-literature.md) gives the related sources
and the limits of the comparison.

From this directory, build the PDF with Tectonic:

```sh
tectonic main.tex
```

The mathematical argument is contained in the manuscript and requires no
accompanying search program or numerical certificate.
