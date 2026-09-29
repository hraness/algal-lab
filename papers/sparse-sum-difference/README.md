# An explicit weighted digit construction for small sumsets and large difference sets

This manuscript proves `theta > 1.18565` for the two-set exponent defined by
`|E+F| <= K|E|` and `|E-F| >= c(K)|E+F|^theta`, for every fixed `K>1`.
It improves on Zheng's published `1.173077` lower bound. The paper gives the
general weighted-digit theorem, a simpler `theta > 1.1855` construction and
the stronger four-digit construction. It makes no global-priority or
current-record claim.

The four-digit alphabet consists of the integers
`c = a0 + 32*a1 + 32^2*a2 + 32^3*a3`, with each `ai` in
`{0,3,4,6,7,...,16}`. Its block cost is `a0+a1+a2+a3`, and its weight is
`(16/19)` raised to that cost. The largest block is `541200`; the theorem
encodes vectors of blocks in outer radix `1082401`. Minimum-cost recurrences
combine all representations of the same sum or difference within each block.

The proof uses the strict finite-set transfer lemma in Section 2 of
Gyarmati-Hennecart-Ruzsa (2007). Dilating each encoded set by two ensures
the lemma's strict difference-count hypothesis. The constant effect on the
logarithmic diameter disappears in the limit. The paper also distinguishes
this two-set exponent from the one-set ratio settled by Lin and Li (2026).

## Reproduce the four-digit certificate

From this directory, using Python 3.10 or later:

```sh
python3 -B carry_verify.py
python3 -B -m unittest -v test_carry_verify
```

`carry-certificate.json` records the fixed parameters, two 129-entry cost
histograms and their integer totals `NS` and `ND`, with common denominator
`19^128`. The verifier reconstructs both cost tables, compares all histogram
entries and integer totals, then checks

```text
ND^20000 > 1082401^3713 * NS^20000.
```

This strict integer inequality certifies `theta > 23713/20000 = 1.18565`.
The verifier uses only the standard library and evaluates one fixed
construction. Its largest cost array has 1,082,401 entries. The controls
compare every cost against an independent endpoint-pair calculation for
24 small block configurations, reject a corrupted full histogram, and
check strict comparisons and malformed certificate inputs.

## Reproduce the smaller constructions

```sh
python3 -B verify.py
python3 -B -m unittest -v test_verify
```

This verifier constructs ordered-pair maxima directly and checks the
displayed polynomial formulas. It certifies `theta > 1.18` at `q=3/4`,
`theta > 1.1813` at `q=377/500`, and `theta > 1.1855` for the sparse alphabet
at `q=16/19`. Its controls compare integer maxima with independent rational
grouping for 189 small configurations and reject overstated thresholds.

`main.tex` is the article source. Build it with a standard LaTeX engine or
`tectonic main.tex`. The
[28 September 2026 version](https://github.com/hraness/algal-lab/releases/tag/sum-difference-bound-20260928)
contains the original manuscript and its `theta > 1.1855` certificate.
