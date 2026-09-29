# An explicit weighted digit construction for small sumsets and large difference sets

This manuscript gives a weighted digit construction for the two-set exponent
defined by `|E+F| <= K|E|` and `|E-F| >= c(K)|E+F|^theta`, for fixed `K>1`.
It proves `theta > 1.1855` using the alphabet `{0,3,4,6,7,...,16}` and geometric
weights `(16/19)^a`. A second explicit example, omitting only digit 1, proves
`theta > 1.1813`. The proof uses the strict finite-set transfer lemma in
Section 2 of Gyarmati-Hennecart-Ruzsa (2007). Dilating each encoded set by
two ensures the lemma's strict difference-count hypothesis; its constant
effect on the logarithmic diameter disappears in the limit.

The numerical claim is one integer inequality. It does not depend on running
an optimizer, generating the large finite sets, or estimating a logarithm.
The bound improves on Zheng's stated `1.173077` theorem. The manuscript
also distinguishes the two-set exponent from the one-set ratio settled
by Lin and Li (2026), resolving the apparent `1.21` comparison in the
recent Hill Sampling benchmark. This note makes no global-priority or
current-record claim.

From this directory, using Python 3.10 or later:

```sh
python3 -B verify.py
python3 -B -m unittest -v test_verify
```

The verifier computes every ordered-pair maximum, checks the displayed
polynomial identities, and proves `theta > 1.18` at `q=3/4`,
`theta > 1.1813` at `q=377/500`, and the main `theta > 1.1855` certificate
at `q=16/19`. The controls compare integer maxima with
independent rational grouping for 189 small alphabet/weight configurations,
reject an overstated threshold, and check input limits.

`main.tex` is the source of the article. Build with a standard LaTeX engine
or `tectonic main.tex`. No scientific search is performed by the manuscript
or its certificate verifier.
