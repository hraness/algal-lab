# Small-support inequalities for reflected max-convolution

[Read the paper](main.pdf).

The paper proves a reflected fourfold max-convolution inequality for every
nonzero finitely supported nonnegative input `f` and nonzero nonnegative
weights `g` supported on a finite integer set `F`. It allows arbitrary
nonnegative kernel weights `k` on supports of at most four points, and
constant `k` on every five-point support. The inequality is strict for
positive `k` on four points and positive constant `k` on five.

The four-point proof identifies a universal translated-kernel covering
constant with an ordinary-autoconvolution optimization, classifies the five
four-point collision patterns, and determines their sharp unweighted
covering constants.

The stronger covering bound holds universally on supports of size at most
four. It fails on the five-point set `{0, 2, 7, 8, 11}` by exactly `1/16` at
the displayed feasible profile. This establishes a support-size boundary for
the covering bound. The five-point theorem proves that this support still
satisfies the reflected inequality for constant `k`, with arbitrary `f`
and `g` as above. The unrestricted fourfold problem remains unresolved
here, and the paper makes no priority claim.

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

The LaTeX sources give the case proofs and the precise classical theorem
used. No search program or numerical optimizer is needed. To build from
this directory with Tectonic:

```sh
tectonic --only-cached --untrusted --keep-logs main.tex
```

All referenced TeX files must be present. The cached-only command requires
the TeX packages to have been installed previously. The checked PDF is
included for readers who do not have that cache.

The proofs and presentation were developed and reviewed with AI assistance.
The [publication review](../PUBLICATION-REVIEW.md) records that review and
the PDF checks; it does not represent human peer review or journal acceptance.
