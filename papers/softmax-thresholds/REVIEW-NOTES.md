# Review notes: sharp softmax threshold manuscript

Manuscript: `papers/softmax-thresholds/main.tex` (compiled with `tectonic main.tex`;
bibliography `refs.bib`; generated fragments `constants.tex`, `hashes.tex`).
Verification scripts: `papers/softmax-thresholds/verify/` (run `sh verify/run_all.sh`
with a Python 3 interpreter that has SymPy and mpmath, `PYTHON=<interpreter> sh verify/run_all.sh`,
the default being `python3`; checked with Python 3.12.14,
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
| 11 | ICLR 2026 Table 3 asserts unrestricted strict Schur-convexity/concavity of the softmax aggregator; the assertion is false | Section 5, Cor 5.2 | quotes taken from arXiv v4 (Table 3 on page 21 of 32, page 2 sentence, Appendix G.4 proof on page 19, Figure 5(a) caption on page 9) and checked against v1 and the author-marked file | Verified against the inspected files; identity with the OpenReview camera-ready not confirmed |
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

- Amir, Bettini, Prorok, arXiv 2506.09434 v4 (1 March 2026, 32 pages by pdfinfo, SHA-256
  4000361622a21d9f829d1a7733f54a477345ecea90668c53ea410151bd40b3fe): the primary source of
  every quotation since the revision. Table 3 (Appendix I, page 21) row "Softmax": "Strictly
  Schur-convex for t>0. Strictly Schur-concave for t<0."; caption clause "(on nonnegative
  inputs)"; page 2 sentence; Appendix G.4 proof of Theorem 3.4 (page 19), which invokes the
  unrestricted property for T_j and for the outer aggregator U; Figure 5(a) caption (page 9).
  The referee report gives "24 pages, page 20" for the same hash; pdfinfo and pdftotext on
  the file give 32 pages with Table 3 on page 21, so the manuscript says page 21.
- arXiv v1 (11 June 2025, 25 pages, SHA-256 14c3a02a...b7fa82): same caption clause and row,
  Table 3 on page 20.
- Author-marked file "Published as a conference paper at ICLR 2026" (32 pages, SHA-256
  4473fb91...84ec0d2f): identical page layout and wording in every quoted passage; no public
  URL re-located, so it is now only mentioned in a footnote, without page numbers.
  OpenReview record: not retrievable (page returned no content).
- Fu, Wang, Shi 2016 (J. Nonlinear Sci. Appl. 9(6)), publisher PDF: Theorem 1.4(II) read and cited.
- Perla, Padmanabhan, Lokesha 2017 (Int. J. Curr. Adv. Res. 6(10)): PDF read earlier, but the
  printed DOI does not resolve and no working URL could be found (journal site probes 404/403,
  searches empty), so the citation and its single use were dropped in the revision.
- Laeven and Goovaerts, "Premium calculation and insurance pricing" (Encyclopedia of
  Quantitative Risk Analysis and Assessment, Wiley 2008, DOI verified at Crossref): the
  authors' 2011 preprint was read; it cites Gerber 1981 and the 1989 paper for the
  non-monotonicity of the Esscher premium. Added as a reference.
- Witkowski 2011 (Math. Inequal. Appl. 14(4)), Gerber 1981 (ASTIN Bulletin 12(2)),
  Asadi and Littman 2017 (PMLR 70), Shi, Jiang, Jiang 2009 (RGMIA preprint),
  Goovaerts, Kaas, Laeven, Tang 2004 (Tinbergen TI 2004-030/4): retrieved and read.
- Lehmer 1971, Bullen 2003, Corless et al. 1996, Marshall, Olkin, Arnold 2011,
  Buhlmann 1980, Zehnwirth 1981: bibliographic data verified through Crossref; the
  cited statements are classical and were checked against the texts available to us.

Metadata or abstract only (not read in full):

- van Heerwaarden, Kaas, Goovaerts 1989 (Insurance: Mathematics and Economics 8(4)):
  abstract only. Tried in the revision: ScienceDirect (403), Semantic Scholar and OpenAlex
  (abstract withheld, no open copy), Crossref (no abstract), Google Books (no snippets), the
  Cambridge Core review of van Heerwaarden's 1991 thesis (no Esscher content), citing texts
  (Laeven-Goovaerts survey; arXiv 2405.11248). The abstract's clause "higher premiums might
  be asked ... also for less variable risks" is the qualitative phenomenon of the negative
  half of the box theorem; the manuscript now says so and claims novelty only for the sharp
  constants, the strictness and the crossover.
- Wang and Zhang 2026 (Aequationes Math. 100, article 77): abstract and preview only; the
  article page and the content/pdf endpoint both bounce to an IdP page. B_tau is a
  Bajraktarevic mean (identity generator, weight e^{tau s}), so their sufficient conditions
  may apply; the manuscript says this and claims nothing about their content.
- Polson 2026 (SSRN 7272019): abstract only, through the Crossref record of the DOI; the
  SSRN page returns 403, and no arXiv or OpenAlex open copy exists. The manuscript now
  states only what the abstract says.

Bounded literature searches (about ten, Crossref, Semantic Scholar, OpenAlex, arXiv,
Google Scholar through WebSearch): no source stating either constant c_n or d_n, or the
crossover at n=58, was found. Hardy, Littlewood, Polya is not in Crossref and is cited
through Marshall, Olkin, Arnold instead.

## Blockers before submission

1. Author name and affiliation: `\author{[Owner name to be confirmed]}` must be replaced.
2. Priority is unresolved: the thresholds were first disclosed publicly in hraness/algal-lab
   PR #21 (created 2026-09-24T00:32Z, merged 00:37:47Z); the manuscript says so and does
   not claim priority beyond that record. The full text of van Heerwaarden, Kaas and
   Goovaerts 1989 (and the 1994 monograph "Ordering of actuarial risks") was not obtained;
   Wang and Zhang 2026 and Polson 2026 could not be read in full, so an overlap with any of
   them cannot be excluded. A library copy of the 1989 paper would settle the main point.
3. The repository is now cited as https://github.com/hraness/algal-lab (path
   papers/softmax-thresholds); the branch must be merged before the citation resolves.
4. The ICLR paper's Theorem 3.4 is affected only through its proof (Appendix G.4) for the
   softmax aggregator; the manuscript says this and does not claim the theorem itself is
   false for other aggregators.

## Compile status

`tectonic main.tex` (Tectonic 0.17.0) compiles without errors and without overfull boxes;
the only warning is one underfull hbox (badness 1158) in the reproduction paragraph.
The PDF has 18 pages, within the 10 to 20 range required. The delivered copy
`softmax-sharp-thresholds.pdf` in the delivery folder of 25 September 2026 has SHA-256
c42b3988f409180c554b2c9269d05691c010d1f3daec5acd04b89addb0fd3edc.

## Suggested venue

Mathematical Inequalities and Applications, or Journal of Mathematical Analysis and
Applications (majorization and inequalities section). Post to arXiv math.CA with a cs.LG
cross-list so the correction to the ICLR 2026 table reaches its readers.

## Revision after the referee report (commit 9f0bf82)

One line per item of the report and of the coordinator's list.

1. Lemma 2.2: the segment is now v(rho) = ((r+rho)/(2r)) v + ((r-rho)/(2r)) vQ, with the
   equivalent form (rho/r) v + (1 - rho/r) v(0); the computation vT = v(rho) for rho = (2 lambda - 1) r
   (lambda >= 1/2) and vT = v(rho) Q for rho = (1 - 2 lambda) r (lambda < 1/2) was re-checked by
   comparing coefficients.
2. Notation: Delta(c,z) is now J(c,z); the partition function of F is Sigma(u); the sum
   sum x_k e^{tau x_k} is M_tau(x); the sum over k not in {i,j} in the proof of Lemma 4.4 is V;
   the Taylor polynomial is p_30(y) with upper bound U(y); the vertex is v^*; the Lehmer mean
   is script L_p; the T-transform matrix T, the simplex Delta_S and Euler's e are unchanged.
   Every occurrence was updated and the old forms no longer appear.
3. Remark 4.8 now says both thresholds are at least c_n, with equality only when d_3 = c_3.
4. The rational-witness remark (Section 5, "A counterexample to an unrestricted claim") now says "witnesses with rational
   coordinates exist", and explains that the values of B_tau at such witnesses need not be rational.
5. Citations: arXiv 2506.09434 v4 (hash 40003616...bd40b3fe) is the primary citation, with
   Table 3 on page 21 of the 32-page file (pdfinfo and pdftotext; the report says page 20 of
   24 pages); the author-marked file is in a footnote without page numbers; refs.bib notes v4.
6. van Heerwaarden, Kaas, Goovaerts 1989: full text still unobtainable (see Sources); the
   manuscript quotes the abstract clause about less variable risks, cites Laeven and
   Goovaerts 2008 for the non-monotonicity attribution, credits the 1989 paper with the
   qualitative observation and claims novelty only for c_n, d_n, strictness and the n = 58
   crossover, without claiming priority over the 1989 paper.
7. Wang and Zhang 2026 and Polson 2026: sentences restricted to what the abstracts say,
   with the remark that B_tau is a Bajraktarevic mean; both marked as abstract-only.
8. Placeholders: author block kept as a marked placeholder; repository set to
   https://github.com/hraness/algal-lab, path papers/softmax-thresholds; verify/run_all.sh
   uses PY="${PYTHON:-python3}"; no machine-specific absolute path remains in the shipped files.
9. Perla 2017 dropped (citation and its one use); Gerber 1981 / De Vylder example kept,
   verified against the retrieved text and reworded to what the text says (negative
   derivative at z = 0 for large h).
10. MSC: primary 26B25, 26D15, 26E60; secondary 68T05, 91G05.
11. "Symmetric set" and "symmetric function" defined in Section 2.1.
12. Added, from the v4 text: the proof of Theorem 3.4 also invokes the unrestricted
    statement for the outer aggregator U, and the Figure 5(a) caption (page 9) states it.
13. This file: journal names of Fu-Wang-Shi, Perla, Witkowski and Zehnwirth corrected; v4
    hash tail corrected to bd40b3fe; interpreter and delivery paths made machine-independent.

Checks after the revision: verify/run_all.sh (with a SymPy-equipped interpreter) ends with
"FAILED: none" for both scripts and leaves constants.tex and hashes.tex unchanged; tectonic
compiles with the same single underfull box; no "??" in the PDF text; no em-dash in
main.tex, refs.bib or this file.
