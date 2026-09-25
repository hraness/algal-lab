# Independent referee report: "Sharp thresholds for the Schur ordering of the softmax-weighted mean"

Manuscript under review: `papers/softmax-thresholds/main.tex` at commit `a2febc9` (branch
`paper/softmax-thresholds`), 17-page PDF, with `refs.bib`, `constants.tex`, `hashes.tex`,
`verify/` and the author-agent notes `REVIEW-NOTES.md` (read last, after all checks below).
Referee: an independent AI agent (Claude), 25 September 2026. The referee did not read the
`verify/` scripts before finishing its own re-derivations; its own scripts are in the session
scratchpad (`/private/tmp/claude-501/-Users-bg-Documents/af6572bf-4735-4489-a5f4-322baab6d05b/scratchpad/`,
files `ref_identities.py`, `ref_identities2.py`, `ref_roots.py`, `ref_violations.py`,
`ref_counterex.py`) and are not committed.

## Verdict

**Minor revision.** The mathematics is correct. Every identity, both directions of the box
theorem and of the simplex theorem (both temperature signs), the segment criterion, the
constants and their Lambert-W forms, the crossover at n = 58, and the four rational
counterexamples were re-derived by hand and recomputed with fresh code; all agree with the
manuscript. The quotations from the ICLR 2026 paper and from Fu, Wang and Shi (2016) are
verbatim-correct, the softmax aggregator of the ICLR paper is exactly B_t, and the
counterexamples violate exactly the quoted claim on exactly the stated domain. The
verification suite passes, the script hashes match, and the generated tables regenerate
identically.

What must be fixed before submission: one wrong formula inside the proof of Lemma 2.2 (the
conclusion survives), several notation collisions, the reliance on an unobtainable
"author version" PDF for the quotations (the arXiv v4 file, whose hash the referee verified,
should carry them), one novelty caveat that needs a full-text check of a 7-page 1989 paper
that is an ordinary journal article, and the placeholders (author block, repository
location, a machine-specific path in `verify/run_all.sh`).

## Numbered problems

Severity scale: Major (affects correctness or the main claims), Moderate (affects
verifiability, attribution or novelty claims), Minor (presentation, notation, wording).

1. **Minor but mathematically wrong statement in a proof (Lemma 2.2, first paragraph).** The
   displayed convex combination `v(rho) = (rho/r) v + (1 - rho/r) vQ` is false: its i-th
   coordinate is `(rho/r)(c-r) + (1-rho/r)(c+r) = c + r - 2 rho`, not `c - rho` (checked
   symbolically; `ref_identities.py`, last block). The conclusion `v(rho) in D` still holds,
   because the correct representation is
   `v(rho) = ((r+rho)/(2r)) v + ((r-rho)/(2r)) vQ` (coefficients in [1/2, 1] for rho in [0, r]),
   or equivalently `v(rho) = (rho/r) v + (1 - rho/r) v(0)` with `v(0) = (v + vQ)/2 in D`. The
   subsequent "direct computation" (`vT = v(rho)` with `rho = (2 lambda - 1) r` for
   `lambda >= 1/2`) is consistent with the corrected formula, not with the printed one.
   **Fix:** replace the displayed formula by one of the two correct forms.

2. **Minor: notation collisions that hurt readability in exactly the places where care is
   needed.**
   - `Delta(c, z)` (Lemma 3.4, the two-point split difference) versus `Delta_S`, `Delta_K`
     (the simplex): both are used in the same proof (Theorem 4.1(ii), where `F(u) - F(u°) =
     Delta(C, z)` is asserted for vectors in `Delta_K`).
   - `S(u) = sum_k e^{-u_k}` (Section 2.2) versus `S` = simplex total: the proof of Theorem
     4.1(ii) uses `K = tS` and `S(u)^{-2}` two lines apart.
   - `T` = T-transform (Section 2.1), `T_tau(x) = sum x_k e^{tau x_k}` (proof of Lemma 2.3(d))
     and `T = sum_{k != i,j} w_k e^{w_k}` (proof of Lemma 4.4).
   - `P = P(x, y)` (Lemma 3.2) versus the Taylor polynomial `P(y)` (Section 6.1).
   - `e = (K, 0, ..., 0)` (proof of Theorem 4.1(i)) versus Euler's `e` in `e^K` in the same
     paragraph.
   - `L = |tau|(b-a)` (Theorem 3.1) versus the Lehmer mean `L_p` (Remark 3.6).
   **Fix:** rename the split difference (e.g. `D(c, z)` or `delta(c, z)`), write the partition
   function of `F` as `Z_{-1}(u)` or `Sigma(u)`, call the vertex `v^*` or `Ke_1`, and call the
   Taylor polynomial `p_{30}(y)`.

3. **Minor, wording (Remark 4.8).** "Both thresholds exceed the box threshold c_n, as they
   must" is false for n = 3, where `d_3 = c_3` (Lemma 2.5). **Fix:** "are at least c_n, with
   equality only for d_3 = c_3".

4. **Minor, wording (Section 5, paragraph after Proposition 5.1).** "Rational witnesses of the
   same kind exist for every n >= 3 and every temperature above the thresholds ... by the
   density of the rationals." For a general temperature the *values* `B_tau(x)` are not
   rational; what the theorems and density give is witnesses with rational *coordinates*
   (the strict inequality is an open condition and a rational T-transform keeps the
   majorization). Rational values, as in Proposition 5.1, need `tau x_i in (log 2) Z` or a
   similar grid. **Fix:** say "witnesses with rational coordinates".

5. **Moderate, verifiability of the quotations (Section 5, first paragraph).** The primary
   source for the quotations is an "author version" PDF identified only by a SHA-256 with no
   URL; the referee cannot verify it and no reader will be able to. The referee downloaded
   arXiv 2506.09434 **v4** (`https://arxiv.org/pdf/2506.09434v4`, 24 pages) and **v1**:
   the v4 SHA-256 is exactly the value printed in the manuscript
   (`40003616 22a21d9f ... bd40b3fe`), and in v4 Table 3 is in Appendix I on page 20, its
   caption reads "Illustrative families of parametric (and one nonparametric) aggregators
   f_t(x). Changing the real parameter t can switch between Schur-convex and Schur-concave
   behaviors (on nonnegative inputs), or control how strongly ...", the Softmax row reads
   `Softmax_t(x) = sum_i e^{t x_i}/sum_j e^{t x_j} x_i, t in R` with "Strictly Schur-convex
   for t > 0. Strictly Schur-concave for t < 0.", the page-2 sentence "the soft-max operator
   switches from Schur-concave to Schur-convex as its temperature increases" is verbatim, and
   the proof in Appendix G.4 opens exactly with "When t <= 0, T_j is Schur-concave, so
   Delta R = 0 by Thm. 3.2." v1 (SHA-256 `14c3a02a ... 7fa82`, 18 pages) carries the same
   caption clause and row. **Fix:** make arXiv v4 the primary citation for all quotations,
   with its appendix/table/page numbers; mention the unobtainable author file (if at all) in
   a footnote without page numbers; add the OpenReview/proceedings record when it becomes
   reachable (the referee's attempt through the OpenReview API also returned "search
   unavailable").

6. **Moderate, novelty claim (Sections 1 and 7, "Esscher premium").** The publisher abstract of
   van Heerwaarden, Kaas and Goovaerts (1989) says the paper studies "order preserving and
   order inducing properties" of the Esscher principle and that "higher premiums might be
   asked for smaller risks, and also for less variable risks". "Less variable risks" is the
   convex/variability order, i.e. exactly the phenomenon of the negative half of this
   manuscript (failure of Schur-convexity of the Esscher premium of an empirical law). This
   is a 7-page article in Insurance: Mathematics and Economics 8(4); "we could not retrieve
   the full text" is not an acceptable state for a submitted paper whose novelty statement
   hinges on it. **Fix:** obtain the article (any university library; also check the
   monograph Kaas, van Heerwaarden, Goovaerts, "Ordering of Actuarial Risks", 1994, which
   treats Esscher premiums and stop-loss order) and state precisely what it contains; quote
   the abstract phrase in Section 7 in the meantime. This does not affect correctness.

7. **Minor, placeholders and reproduction path.** `\author{[Owner name to be confirmed]}`,
   "[repository location to be confirmed by the owner]" (Section 6), and
   `verify/run_all.sh` defaults `PY` to `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`,
   a machine-specific path in a script the paper tells readers to run. **Fix:** default to
   `python3`; ship `verify/` as ancillary files or give the repository URL.

8. **Minor, bibliography.** All 13 DOIs in `refs.bib` resolve at Crossref and match
   author/title/journal/volume/issue/pages/year (Witkowski 2011: Crossref lacks the volume;
   14 is correct for MIA 14(4)). The Asadi and Littman entry matches the PMLR page
   (vol. 70, pp. 243-252, eds. Precup and Teh). The Perla, Padmanabhan and Lokesha DOI
   returns 404 at Crossref, as the bib note says; the referee could not verify this paper's
   content at all, and the manuscript only says it "states analogous results". **Fix:** give
   a URL for it or drop the citation. The Gerber 1981 description ("an example, credited
   there to De Vylder, of a uniform law on three points (0, z, 1) ...") could not be verified
   by the referee (only the Cambridge Core preview was reachable; it does not show the
   example); the example itself is mathematically right (by Lemma 2.3(d) the coordinate
   derivative is negative when `z < B - 1/h`), so only the attribution needs a second look.

9. **Minor, MSC.** 15A39 (linear inequalities of matrices) is an odd fit. Suggest primary
   26B25, 26D15, 26E60 (means); secondary 68T05, 91G05.

10. **Minor, definitions.** Section 2.1 defines a symmetric *set* but a symmetric *function*
    is only defined implicitly in the Introduction; add one sentence before Lemma 2.2.

11. **Minor, optional strengthening of Section 5.** The unrestricted claim is also used for
    the outer aggregator in the ICLR paper (v4, proof of Theorem 3.4: "U is Schur-concave for
    tau <= 0, and Schur-convex for tau >= 0, hence it is maximized by the uniform ...", and
    the Figure 3(a) caption "tau >= 0 is Schur-convex; tau <= 0 is Schur-concave"). The
    manuscript may note this; it is not required.

12. **Minor, author notes (not in the manuscript).** `REVIEW-NOTES.md` misnames several
    journals (Fu-Wang-Shi as "J. Inequal. Appl.", Gerber 1981 as "Insurance Math. Econom.",
    Witkowski as "Aequationes Math.", Perla et al. as "Adv. Inequal. Appl.") and abbreviates
    the arXiv v4 hash as "...0fe3e" (the correct tail, as in the manuscript, is "...bd40b3fe").
    `refs.bib` is right in every case; the notes should be reconciled so they do not mislead
    the owner.

No em-dashes anywhere in the PDF (0 occurrences; the 15 en-dashes are "Schur–Ostrowski" and
page ranges). The AI-disclosure footnote is present in `\thanks`. No undefined references
or citations; the only compile warning is one underfull hbox (badness 1158) at lines
544-545. No typos found beyond the items above.

## What the referee verified independently, and how

All re-derivations were done before reading `verify/` and before reading `REVIEW-NOTES.md`.
Tools: sympy 1.14 / mpmath 1.3 in the project venv, exact `fractions.Fraction`, Tectonic
0.17, `pdftotext`, `curl` against the Crossref REST API and arXiv.

### Symbolic identities (`ref_identities.py`, `ref_identities2.py`)
- Lemma 2.3(a)-(e): translation, scaling, `d/dx_i B = w_i(1 + tau(x_i - B))`, the `tau`
  derivative equals the softmax variance, and the equal-split formula (e). (e) was confirmed
  after `rewrite(exp)`; `simplify` alone left a residue, which is a sympy artefact.
- Pair identity (Lemma 3.2): `S^2 (d_1 F - d_2 F) = P + sum_{k>=3} e^{-u_k} psi(u_k)` checked
  symbolically for n = 3, 4, 5 with the printed `P` and `psi`.
- Factorization (Lemma 3.3): `N = 2 e^{-c} sinh z [m(1 - c + z coth z) + 2 e^{-c}(cosh z + z/sinh z)]`
  as an identity in (c, z, m); the lower bound `N > 2 e^{-c} sinh z g(c)` follows from
  `z coth z > 1` and `cosh z + z/sinh z > 2`, both re-proved (Lemma 2.4(i),(ii), the second
  via the series in Lemma 2.4(iv), whose coefficient `4k(k-1)/(3(2k+1)!)` was recomputed).
- Split formula (eq:split) and the two forms of `eta = -g(c)/(mc)`; the `z^2` coefficient of
  Remark 3.3; Lemma 3.5's sign bound; the n = 2 closed form `c + z tanh(tau z)`.
- Simplex: `(H - 2) Z` identity, `phi(K) - 2`, `rho''(s)` of `(s-2)e^s`, `f'`, and (eq:Hsplit)
  for n = 4; Lemma 4.4's `T` and the split of equal coordinates.
- Lambert forms: `c_n = 2 + W_0(4/((n-2)e^2))` and `d_n = 2 + W_0(2(n-1)/e^2)` agree with the
  defining equations to 1e-39 (numerically; the symbolic residue is again a sympy artefact).
- Lehmer transfer `L_p(e^{eps x}) = Z_tau / Z_{tau - eps}` and its `eps -> 0` limit; the
  reflection `B_{-tau}(x) = -B_tau(-x)` and (eq:reduction).
- Lemma 2.2: the T-transform combination check (which is how problem 1 was found) and
  the chain argument (finite sequence of T-transforms, strict inequality at each step
  unless the step is a permutation).

### Constants and crossover (`ref_roots.py`, mpmath at 60 digits)
- 32-step bisection of `(n-2)(c-2)e^c = 4` and `(d-2)e^d = 2(n-1)` agrees with the Lambert
  forms to 1e-60 for every n in `constants.tex`; `c_3 - d_3 = 0` exactly; all eleven
  printed enclosures contain the true values with the printed signs of `d_n - 2c_n`.
- `d_n - 2c_n` for 3 <= n <= 400: negative for n <= 57, positive for n >= 58, strictly
  increasing; the sign change is unique. Proposition 4.5's printed enclosures
  `d_57 in [4.0169248, 4.0169249]`, `2c_57 in [4.0194941, 4.0194942]`,
  `2c_58 in [4.0191493, 4.0191494]`, `d_58 in [4.0287691, 4.0287692]` contain the true
  values (`d_57 = 4.01692486...`, `2c_57 = 4.01949419...`, `2c_58 = 4.01914938...`,
  `d_58 = 4.02876916...`), so the two strict comparisons are certified.
- Introduction numerics (`c_3 ~ 2.3728564`, `c_4 ~ 2.2177151`, `c_128 ~ 2.004278`,
  `d_4 ~ 2.4949858`, `d_128 ~ 4.5868813`), `e^{3/5} = 1.8221 < 2`, and
  `8 log 2 = 5.5452 > 4.8 > 2c_3 = 4.7457` confirmed.

### Necessity and sufficiency by direct evaluation (`ref_violations.py`)
- Box, n = 3, 4, 8: the referee's own vertex-split construction and the manuscript's
  (eq:box-construction) at `L = c_n (1 + 1e-3)` produce interior pairs `x > y` (majorization
  and non-permutation checked) with `F(x) > F(y)`, and transfer by reflection to the box
  `[-1, 2]` for both signs of `tau`. At `L = c_n (1 - 1e-3)` and at `L = c_n` the sampled
  Schur-Ostrowski quantity is positive throughout and 0 of 2000 random T-transforms
  violate; bracketing the sign change of the split difference in `L` returns `c_n`.
- Simplex, `tau = +1`: at `K = d_n (1 +- 1e-3)` and at `K = d_n`, `H(vertex) > 2` above and
  `<= 2` at or below; violations found above, none in 2000 samples at or below.
- Simplex, `tau = -1`: same pattern at `K = 2 c_n (1 +- 1e-3)`.

### Rational counterexamples (`ref_counterex.py`, exact rationals)
All four witnesses of Proposition 5.1 recomputed with `Fraction`: majorization, the
non-permutation condition, the values `88/91 < 43/44`, `3/91 > 1/44`, `49/69 < 97/136`,
`17/296 > 1/18` and their differences match the manuscript exactly. The domains are
nonnegative and each pair violates exactly the row of Table 3 that is quoted.

### Verification suite and generated files
`verify/run_all.sh` with the venv interpreter: all four scripts pass; `identities.py`
(seed 20260925, 50 digits) and `violations.py` reproduce the referee's findings;
`roots.py` regenerates `constants.tex` byte-identically; the four SHA-256 halves in
`hashes.tex` match the scripts. The certificate logic in `roots.py` (degree-30 Taylor at
`y = x/8` with the geometric tail bound `y/32 < 1`, then the eighth power of both rational
bounds, `RuntimeError` if an enclosure
straddles zero, endpoint signs certified before bisection) was read afterwards and is
sound; the width claim of Section 6.1 (`U(y)^8 - P(y)^8 < 1e-29` on `[0, 8]`; the referee
measured 1.1e-30 at x = 8, where it is largest) holds, and `U(3/5)^8 = 1.82212 < 2`.

### Sources
- ICLR 2026 paper: arXiv v4 and v1 PDFs downloaded, hashed and read (details in
  problem 5). The softmax aggregator `Softmax_t(x) = sum_i e^{t x_i} x_i / sum_j e^{t x_j}`
  is `B_t` exactly; the paper's Definition 3.2 places Schur-monotonicity on `R^N`, and its
  Section 2 restricts efforts to `[0, 1]`, so the counterexamples on nonnegative inputs
  (and inside `[0, 1]^n` after scaling by `tau`) address the quoted claim on its own domain.
- Fu, Wang, Shi (2016), JNSA 9(6): the publisher PDF (via the DOI redirect) states Theorem
  1.4(II) exactly as quoted: "If p > 1/2, then for any a > 0, L_p(x) is
  Schur-geometrically convex with x in [((p-1)/p)^2 a, a]^n".
- Shi, Jiang, Jiang (2009), RGMIA 10(2), Theorem 3: Schur-geometric convexity of the Gini
  mean in (x, y) for r, s >= 0 (and concavity for r, s <= 0), as cited.
- Marshall, Olkin, Arnold: Lemma 2.B.1 (T-transform chain) and Theorem 3.A.4
  (Schur-Ostrowski) are the right citations; Definition and Proposition of Chapter 3
  on strict Schur-convexity match the manuscript's definition.
- Crossref: every DOI in `refs.bib` resolves and matches, except Perla et al. (see
  problem 8). Tinbergen URL returns 200; Gerber 1981 metadata matches.
- Compile: `tectonic` on a scratch copy exits 0, 17 pages, no undefined references, no
  em-dashes, disclosure footnote present.

### Prior-art search (six queries, as bounded)
Queries: Esscher premium + Schur; softmax-weighted mean + Schur-convex (top hit is the
lab's own PR #21); Gini means of n variables + Schur; exponential mean + Lambert W;
van Heerwaarden 1989 abstract; Boltzmann operator + Schur. No source states `c_n`, `d_n`,
the Lambert-W forms, or the crossover at n = 58. Li and Shi's "generalized exponent
mean" (J. Math. Inequal.) is a two-variable object and not the same as `B_tau`.

## Priority concerns, in order

1. van Heerwaarden, Kaas, Goovaerts (1989) must be read in full before the sentence in
   Section 7 about the Esscher literature is finalized (problem 6). The abstract's phrase
   "also for less variable risks" describes the same failure of ordering for the Esscher
   premium; whether they identified any range condition, and for which orderings, is the
   only open novelty question the referee found.
2. Wang and Zhang (2026) and Polson (2026) are cited but unread; the manuscript's claim that
   they do not contain the thresholds is at present an inference from their abstracts.
   Either read them or soften the sentence to "we found no statement of the thresholds
   in the abstracts or previews available to us".
3. The public-disclosure record (hraness/algal-lab PR #21, 2026-09-24) is the manuscript's
   priority claim; the repository location placeholder must be resolved for that record
   to be checkable.
4. Problem 1 is the only mathematical error; it is in a proof, not in a statement, and
   the fix is one line.

Nothing in this report requires new mathematics. The referee recommends acceptance after
the fixes above and a second look by the authors at problems 5 and 6.
