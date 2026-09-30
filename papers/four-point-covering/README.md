# Small-support inequalities for reflected max-convolution

[Read the paper](main.pdf).

The paper proves a reflected fourfold max-convolution inequality for every
nonzero finitely supported nonnegative input `f` and nonzero nonnegative
weights `g` supported on a finite integer set `F`. It allows arbitrary
nonnegative kernel weights `k` on supports of at most four points, and
constant `k` on every five-point support. On the specific support
`{0, 2, 7, 8, 11}`, it also allows arbitrary nonnegative `k`. The inequality
is strict for positive `k` on four points, positive constant `k` on five,
and positive `k` on this specific five-point support.

The four-point proof identifies a universal translated-kernel covering
constant with an ordinary-autoconvolution optimization, classifies the five
four-point collision patterns, and determines their sharp unweighted
covering constants.

The stronger covering bound holds universally on supports of size at most
four. It fails on the five-point set `{0, 2, 7, 8, 11}` by exactly `1/16` at
the displayed feasible profile. This establishes a support-size boundary for
the covering bound. A sharper estimate using a common input `f,g`, together
with rational coefficient certificates, proves the reflected inequality
on this support for every `k`. The unrestricted fourfold problem remains
unresolved here, and the paper makes no priority claim.

For five-point `F` and `k=1_F`, an elementary energy estimate already bounds
the reflected ratio by `9/5` when `g` is constant; this also proves the
indicator-set corollary. The theorem extends the conclusion to arbitrary
nonnegative `g`. Its Sidon case uses Freiman's classical `3k−4` theorem,
as restated on page 1 of Bollobás, Leader and Tiba,
[*A strengthening of Freiman's 3k−4 theorem*, arXiv:2204.09816v1](https://arxiv.org/abs/2204.09816v1)
(21 April 2022). That exact restatement was checked on the original PDF
page; Freiman's original proofs were not read.

The [three-point paper](../three-point-fourfold/main.pdf) gives a separate
direct proof using scalar inequalities and telescoping potentials.
The shared [literature comparison](../sumset-literature.md) credits the prior
max-convolution results, including Green et al.'s weighted Prékopa–Leindler
preprint, and records which editions were read and the limits of the
priority assessment.

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

The LaTeX sources include the remaining case proofs and the precise
classical theorem used. To build from this directory with Tectonic:

```sh
tectonic --only-cached --untrusted --keep-logs main.tex
```

All referenced TeX files must be present. The cached-only command requires
the TeX packages to have been installed previously. The checked PDF is
included for readers who do not have that cache.

The proofs and presentation were developed and reviewed with AI assistance.
The [publication review](../PUBLICATION-REVIEW.md) records that review and
the PDF checks; it does not represent human peer review or journal acceptance.
