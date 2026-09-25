# Review notes: sharp softmax threshold manuscript

Manuscript: `papers/softmax-thresholds/main.tex` (compiled with `tectonic main.tex`;
bibliography `refs.bib`; generated fragments `constants.tex`, `hashes.tex`).
Verification scripts: `papers/softmax-thresholds/verify/` (run `sh verify/run_all.sh`
with `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`; Python 3.12.14,
SymPy 1.14.0, mpmath 1.3.0). The scripts import nothing from the repository.

Source notes re-verified: `docs/sharp-softmax-spread.md`, `docs/simplex-softmax-order.md`,
`docs/novelty-ledger.md` (rows on the softmax sources). The repository verifiers
`research/spikes/stochastic/softmax_spread.py` and `simplex_spread.py` were read but not
imported or reused.

## Claim-by-claim table

| # | Claim | Where proved in main.tex | How re-verified | Status |
|---|-------|--------------------------|-----------------|--------|
| 1 | Box, sufficiency: for n>=3 and \|tau\|(b-a) <= c_n, B_tau is strictly Schur-convex (tau>0) / strictly Schur-concave (tau<0) on [a,b]^n, including the equality case | Thm 3.1(i); Lemmas 2.2 (segment criterion), 3.2 (pair identity), 3.3 (factorization), 2.4(i),(ii) (elementary inequalities), 2.5 (constants) | Hand re-derivation of every line; `identities.py` checks the pair identity and factorization symbolically and at random rationals; `violations.py` samples the derivative inequality at and below c_n and random T-transforms at L=c_n | Proved |
| 2 | Box, necessity: for L>c_n explicit interior pairs violate the ordering | Thm 3.1(ii); Lemmas 3.4 (split at the vertex), 3.5 (sign bound), 2.4(iii) | Hand re-derivation; `identities.py` checks (eq:split), the eta identities and the z^2 expansion; `violations.py` evaluates the construction at 50 digits for many (n,L) and checks domain, majorization, sign and the bound chain | Proved |
| 3 | Above c_n, B_tau is neither Schur-convex nor Schur-concave on the box | end of proof of Thm 3.1(ii), Lemma 2.3(e) | equal-split formula checked in `identities.py` | Proved |
| 4 | c_n = 2 + W_0(4/((n-2)e^2)), strictly decreasing to 2; dimension-free constant 2 is sharp | Lemma 2.5, Cor 3.8 | Lambert form checked in `identities.py`; monotonicity of the certified enclosures in `roots.py`; sampling at tau(b-a)=2 in `violations.py` | Proved |
| 5 | n=2: ordering holds on all of R^2 for every tau | Prop 3.7 | closed form B_tau(c-z,c+z)=c+z tanh(tau z) checked in `identities.py` | Proved |
| 6 | Fu-Wang-Shi Thm 1.4(II) transfers to the nonstrict bound tau(b-a)<=2 and nothing sharper | Remark 3.9 | Lehmer identity and limit checked in `identities.py`; the theorem statement read in the publisher PDF | Verified (derivation ours; theorem cited) |
| 7 | Simplex, tau>0: strict Schur-convexity iff tau S <= d_n, (d_n-2)e^{d_n}=2(n-1); explicit interior violations above | Thm 4.1(i); Lemmas 4.2 (convexity bound), 4.3, 4.4 (split of equal coordinates), 2.4(iv) | Hand re-derivation (the proof of H<=2 uses a chord bound for the convex function (s-2)e^s, which is simpler than the route in the note and gives the same threshold); `identities.py` checks (eq:Hsplit), f', phi(K)-2; `violations.py` evaluates the construction and samples H<=2 and the derivative inequality at K=d_n | Proved |
| 8 | Simplex, tau<0: strict Schur-concavity iff \|tau\| S <= 2c_n; explicit interior violations above | Thm 4.1(ii) | same lemmas as claims 1 and 2 with c <= K/2; construction evaluated in `violations.py` | Proved |
| 9 | d_n strictly increasing to infinity; c_3 = d_3; d_n - 2c_n changes sign exactly once, between n=57 and n=58 | Prop 4.5 | monotonicity analytic (Lemma 2.5); the crossover uses the exact rational enclosures of `roots.py` (d_57 upper < 2 c_57 lower, d_58 lower > 2 c_58 upper); mpmath cross-check that the sign changes once for 3<=n<=400 | Proved (computer-assisted, exact arithmetic) |
| 10 | Rational counterexamples at tau = +-8 log 2: 88/91 vs 43/44, 3/91 vs 1/44, 49/69 vs 97/136, 17/296 vs 1/18 | Prop 5.1 | hand computation in the proof; `counterexamples.py` in exact rationals | Proved |
| 11 | ICLR 2026 Table 3 asserts unrestricted strict Schur-convexity/concavity of the softmax aggregator; the assertion is false | Section 5, Cor 5.2 | quotes taken from the author PDF (page 21 table, page 2 sentence, Appendix G.4 proof opening) and from arXiv v1 and v4 texts | Verified against the inspected files; identity with the OpenReview camera-ready not confirmed |
| 12 | Root enclosures in Table 1 contain the constants; e^{3/5} < 2 | Section 6 | `roots.py` (exact rationals, degree-30 Taylor with argument reduction and geometric tail; 32 bisection steps with certified endpoint signs) | Certified |

## Discrepancies with the source notes

None mathematical. Every threshold, formula and witness in the notes was reproduced.
Presentation differences introduced in the manuscript:

- The manuscript proves strict Schur monotonicity on the closed box and closed simplex
  through a "segment criterion" (Lemma 2.2, strict T-transform monotonicity from a pairwise
  derivative inequality on the open segment) instead of invoking the Schur-Ostrowski
  criterion on sets with empty interior or boundary.
- The simplex bound H <= 2 (Lemma 4.2) is proved by a chord inequality for the convex
  function (s-2)e^s; the note reaches the same d_n by a different route.
- Root enclosures are reported to ten decimals in Table 1 (outward rounding of exact
  rational bounds of width 2^-32, resp. 6 * 2^-32); the notes quote fewer digits.
- The manuscript records that c_3 = d_3 exactly (both solve (s-2)e^s = 4), which the
  notes state numerically.

## Sources: retrieved or not

Retrieved and read (files kept in the session scratchpad, not committed):

- Amir, Bettini, Prorok, ICLR 2026, author PDF (32 pages), SHA-256
  4473fb913f6cb4a64f6db5fa92ae35320598cc89d029f930c88e747c84ec0d2f. Table 3 (Appendix I,
  page 21) row "Softmax": "Strictly Schur-convex for t>0. Strictly Schur-concave for t<0."
  Also the page 2 sentence and the Figure 1 caption ("on nonnegative inputs"), and the
  Appendix G.4 proof of Theorem 3.4, which invokes the unrestricted Schur-concavity.
  The download URL of this exact file was not recorded in the session transcript and could
  not be re-located (the project page https://sites.google.com/view/hetenvdesign answers
  200 to curl but redirects a fetch to a Google login); the manuscript therefore reports
  the hash and says so.
- arXiv 2506.09434 v1 (SHA-256 14c3a02a...7fa82) and v4 (SHA-256 40003616...0fe3e): same
  Table 3 wording. OpenReview record: not retrievable (page returned no content).
- Fu, Wang, Shi 2016 (J. Inequal. Appl.), publisher PDF: Theorem 1.4(II) read and cited.
- Perla, Padmanabhan, Lokesha 2017 (Adv. Inequal. Appl.): PDF read; the DOI printed in the
  paper does not resolve at Crossref, so the entry cites the journal without a DOI.
- Witkowski 2011 (Aequationes Math.), Gerber 1981 (Insurance Math. Econom.),
  Asadi and Littman 2017 (PMLR 70), Shi, Jiang, Jiang 2009 (RGMIA preprint),
  Goovaerts, Kaas, Laeven, Tang 2004 (Tinbergen TI 2004-030/4): retrieved and read.
- Lehmer 1971, Bullen 2003, Corless et al. 1996, Marshall, Olkin, Arnold 2011,
  Buhlmann 1980, Zehnwirth 1981: bibliographic data verified through Crossref; the
  cited statements are classical and were checked against the texts available to us.

Metadata or abstract only (not read in full):

- van Heerwaarden, Kaas, Goovaerts 1989 (Insurance Math. Econom.): publisher abstract
  only (reports failures of the Esscher premium to respect orderings of risks).
- Wang and Zhang 2026 (Aequationes Math. 100(5)): Springer preview only; the article page
  redirected to an institutional login.
- Polson 2026 (SSRN 7272019): abstract only, through the Crossref record of the DOI; the
  SSRN page returned 403.

Bounded literature searches (about ten, Crossref, Semantic Scholar, OpenAlex, arXiv,
Google Scholar through WebSearch): no source stating either constant c_n or d_n, or the
crossover at n=58, was found. Hardy, Littlewood, Polya is not in Crossref and is cited
through Marshall, Olkin, Arnold instead.

## Blockers before submission

1. Author name and affiliation: `\author{[Owner name to be confirmed]}` must be replaced.
2. Repository location in Section 6 ("[repository location to be confirmed by the owner]").
3. Priority is unresolved: the thresholds were first disclosed publicly in hraness/algal-lab
   PR #21 (created 2026-09-24T00:32Z, merged 00:37:47Z); the manuscript says so and does
   not claim priority beyond that record. Wang and Zhang 2026 and Polson 2026 could not be
   read in full, so an overlap with either cannot be excluded.
4. The counterexample section quotes the author PDF by hash; if the owner wants a URL,
   the arXiv version (same wording) is the safe citation.
5. The ICLR paper's Theorem 3.4 is affected only through its proof (Appendix G.4) for the
   softmax aggregator; the manuscript says this and does not claim the theorem itself is
   false for other aggregators.

## Compile status

`tectonic main.tex` (Tectonic 0.17.0) compiles without errors and without overfull boxes;
the only warning is one underfull hbox (badness 1158) in the reproduction paragraph.
The PDF has 17 pages, within the 10 to 20 range required. The delivered copy is
`/Users/bg/Documents/algal-lab-delivery-20260925/softmax-sharp-thresholds.pdf` (SHA-256
fff656ea778ac37dc7be7c0ed2748e5c369d098afde4977d3577e4706dccf092).

## Suggested venue

Mathematical Inequalities and Applications, or Journal of Mathematical Analysis and
Applications (majorization and inequalities section). Post to arXiv math.CA with a cs.LG
cross-list so the correction to the ICLR 2026 table reaches its readers.
