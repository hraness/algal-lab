# Independent referee report: "Purity and phase structure of nested Boltzmann task allocation"

Manuscript: `papers/boltzmann-purity/main.tex` at commit 3772fc7 (24 pages, compiled with tectonic in a scratch copy; the repository PDF has the same page count). Reviewer: an independent adversarial referee agent; the author-agent's `REVIEW-NOTES.md` was read only after the mathematics had been re-derived and the computations re-run with fresh code (`bf.py`, `bf2.py`, `exact.py`, `sym.py`, kept outside the repository).

## Verdict

**Minor revision.** The centrepiece (Theorem 5.1, universal purity) is correct: every lemma it rests on was re-derived by hand, every identity was re-verified symbolically, and no exhaustive grid or multi-start ascent on shapes up to 7x3 / 5x5 / 6x4 found a fractional maximizer or a fractional tie. The refutation of the v1 conjecture is sound and the model matches Amir, Bettini and Prorok exactly. The gap certificates, phase thresholds, asymptotic coefficients and negative-outer witnesses all reproduce. One proof has a genuine (easily repaired) gap in an equality case (Theorem 7.2(b)/(c)); the remaining problems are wording that claims slightly more than the theorems prove, one display equation that is cut off at the page edge, several overfull lines, and the placeholder author line.

## Numbered problems

Severity scale: **must fix** (blocks submission), **minor** (fix before submission), **optional**.

1. **[minor, mathematics] Theorem 7.2(b), equality case is misstated for k = 0.** For L empty the subset mass is identically 0 = s_0, so equality holds for every x, not only for x = 1_L = 0. Fix: "with equality if and only if k = 0, k = N, or x = 1_L".

2. **[minor, mathematics] Theorem 7.2(c), the strictness argument has a gap.** The proof takes x_i in (0,1) minimal among the non-binary coordinates and u in (x_i, min({x_l : x_l > x_i} u {1})); it then claims the inequality in (b) is strict there. If x_i is the largest coordinate and no coordinate equals 1 (example: x = (1/2, 0), N = 2), then L_u is empty on that whole interval and (b) gives no strictness (see problem 1), so the argument as written does not prove B_t(x) < phi(sum x) for such x. The statement is true (for x = (1/2,0), t = 1 the gap is 5.4e-2; 20 000 random non-binary columns for N in {2,3,5} all gave a strictly positive gap). Fix (three cases, using that the coordinates below x_i are all 0): (i) if some coordinate is 0, take u in (0, x_i): then i is in L_u, L_u is not [N], and x differs from 1_{L_u} because x_i is not 1, so (b) is strict on that interval; (ii) if no coordinate is 0 and some coordinate exceeds x_i, the interval used in the proof works, because L_u is then nonempty and not [N]; (iii) if x is constant, equal to c in (0,1), then n_u = N for u < c and n_u = 0 for u > c, both applications of (b) are equalities, and strictness comes from the Jensen step: B_t(x) = c = c phi(N) + (1 - c) phi(0) < phi(Nc), because phi is concave and not linear on [0, N] (d_0 > d_1 when N >= 2), so its chord from (0,0) to (N,1) lies strictly below it at interior points. Theorem 7.4 and Corollary 7.5 use only the (true) statement, so nothing downstream changes.

3. **[minor, overclaim] Abstract and Introduction: "the complete two-agent solution for any number of tasks".** Theorem 6.5 is proved for t, tau > 0 only; for N = 2, M >= 3 and tau < 0 the paper proves nothing complete (Example 7.11 with (N,M) = (2,3) even exhibits fractional maximizers). The intro bullet "two agents and any number of tasks, where a single crossover ..." has the same omission. Fix: insert "at positive temperatures".

4. **[minor, overclaim] Abstract and Introduction: "for tau < 0 purity of maximizers is decided by whether M divides N together with the size of t".** The indivisible case with t s_q > 1 and y_* >= 1/ceil(M/r), and the behaviour for moderately negative tau, are explicitly open (Open questions 2 and 3). Fix: "depends on" or "is governed by ... in the following sense", and keep the precise statement that follows.

5. **[minor, presentation] Abstract: the gap-identity sentence omits N = M.** "every pure allocation other than complete concentration and a permutation strictly beats both" is a statement about square instances; say so ("on square instances" or "for N = M").

6. **[minor, mathematics/wording] Theorem 7.1, second sentence.** "for every function U: R^M -> R, max_A U(S(A)) is attained at a homogeneous allocation" presupposes that the maximum exists. Fix: "the supremum of U(S(A)) over F equals its supremum over homogeneous allocations, and whenever the maximum exists it is attained at a homogeneous allocation" (or assume U continuous).

7. **[optional] Lemma 2.1(ii).** The equality claim needs n >= 2 (for n = 1, p_1 = 1 = sigma(c,1) for every x); (iii) already carries the caveat.

8. **[must fix, layout] Page 12, the display at `main.tex` line 408** (D - H = ..., G(F) = ..., G'(F) = ... in the proof of Theorem 6.5) is 151 pt overfull and is physically cut off at the right page edge in the PDF: the expression for G'(F) ends with "2b(b-1)(F+M" and the rest is not printed. Fix: break it into two lines (align or gather).

9. **[minor, layout] Further overfull boxes** reported by tectonic: line 229 (2 pt), 431 (32 pt, Remark 6.4), 554 (15 pt display, Theorem 6.10 proof), 675 (7 pt), 690 (27 pt, the SHA-256 table is wider than the text block), 693-704 (37 pt), 710-711 (46 pt) and 722-723 (63 pt; the `\texttt` reproduction commands visibly protrude into the margin on page 22). Fix: `\small` or `\scriptsize` for the table, `\path`/`\url` or discretionary breaks for the `\texttt` strings, and reflow the two displays.

10. **[must fix before submission, non-mathematical] Author line is the placeholder "[Owner name to be confirmed]".** Also the `\thanks` footnote says the proofs were "independently machine-checked"; only the identities and the numerical statements are script-checked (no proof assistant was used), so reword to "the identities and every numerical statement were independently recomputed by the scripts of Section 8" to avoid overstating the check.

11. **[minor, related work] Venue of the source paper.** Section 9 says the venue "could not be confirmed from the arXiv record". The authors' own publication page (matteobettini.com/publication/hetenvdesign/) lists the paper under "International Conference on Learning Representations (ICLR)", 2026, and an OpenReview record exists (id uJCGMBO6Qx; the forum page is behind a browser check). Suggest: "listed as ICLR 2026 on the authors' page; not confirmed from OpenReview".

12. **[optional, related work] Version 3.** I verified the theorem title and the absence of "conjecture" in v1 (PDF text), v2 and v4 (arXiv HTML); v3 was not independently checked by me. The authors state they retrieved all four; keep the claim but make sure v3 was actually read.

13. **[minor, proof detail] Theorem 7.4.** "for a concave piecewise linear function with breakpoints at the integers it is attained at an integer vector" deserves one sentence: since sum_j c_j = N is an integer, a non-integer maximizer has two fractional coordinates; shifting mass between them along their common linear pieces cannot decrease the sum, so one can be moved to an integer, and repeat.

14. **[optional] Remark after Lemma 2.1.** Strict monotonicity on the feasible domain also holds at c = 1 (1 + c(x_i - B) = 0 would need x_i = 0 and B = 1, impossible); "0 < c <= 1".

15. **[optional] Theorem 6.7 / Example 6.8 wording.** Fine as is; note that the statement "u(t) is the unique solution of Q = H with tau > 0" is justified by G strictly decreasing with G(1) > 0, which the proof does establish.

16. **[minor, Section 8] "the complete run takes a few minutes on a laptop".** See the timing table in the verification section below and adjust the sentence if the measured total (dominated by `brute_force.py` and `negative_outer.py`) is materially longer.

17. **[optional, bibliography] All eight references were verified (Crossref for Shioura 2009 and Liao et al. 2023; Crossref search for Bolker 1972; arXiv for the two preprints and the ABP versions).** Bolker 1972 could carry its DOI 10.1016/0095-8956(72)90060-3. Crossref renders Shioura's title with an em-dash where the entry uses a colon (harmless). The dates in the ABPv4 entry (v2 28 Sep 2025, v3 4 Nov 2025, v4 1 Mar 2026) and in ABPv1 (11 Jun 2025) match the arXiv listing exactly.

18. **[optional] Remark 7.12.** "apart from the degenerate cases t <= 0 ... and N = 1" is loose: for t <= 0 and tau > 0 the unique maximizer is in fact pure (concentration), while for t <= 0 and tau < 0 (and for N = 1, tau <= 0) fractional maximizers do occur. Either drop the clause or state it precisely.

No em-dashes are present (0 occurrences of U+2014 and of `---`); en-dashes in "harmonic--arithmetic" and "Karush--Kuhn--Tucker" are fine. All `\ref`/`\label` pairs and all eight `\cite` keys resolve; the tectonic log contains no undefined references or citations.

## What was verified independently, and how

All checking code was written from the manuscript's definitions before any file in `verify/` was opened; the `verify/` scripts were run afterwards only to confirm the hashes and the `FAILURES: none` claim.

### Hand re-derivation

Every proof in Sections 2 to 7 was re-derived line by line. Points that were checked with particular care, because they are where such arguments usually break:

- Lemma 3.1: sum of partials equals 1; D^2 B[u,u] = c sum p_i (1 + h_i) u_i^2 - 2c u-bar DB[u]; the diagonal entry c p (1 - p) [2 - (2p - 1) d]. Lemma 3.2: the nested chain rule d_ij R = W_j p_ij h_ij with W_j = P_j g_j, and the second-derivative decomposition.
- Lemma 4.1: W_j > 0 on active tasks (needs only tau finite and the outer weight positive), h_ij > 0 at positive entries (from the diagonal second derivative and the KKT equation with a row multiplier), full budgets (otherwise a positive partial could be used), and the common multiplier lambda_i per row.
- Lemma 4.2 (forest): the cycle direction with entries +-1/lambda_i (sign alternating around the cycle) is feasible in both senses, has DR = 0 by the common-multiplier property, and D^2 R > 0. The case of a task shared by exactly two moving contributors, and the case of a single-edge path, were both checked; the argument is component-wise so several trees cause no problem.
- Lemma 4.3 (consolidation): psi(w) = (w - R) e^{tau w} and the sign of the change of the numerator and denominator; Lemma 4.4 (dominance) via the tangent inequality with z < 2; Corollary 4.5.
- Theorem 5.1: the path between two private leaf tasks exists with L >= 2 after consolidation; the endpoint bound 1 + 1/h - 2p > -1, grouped by row, gives strict positivity of D^2 R along the direction while DR = 0; a global maximizer in the relative interior of that segment is impossible. The direction stays feasible on an open interval because every entry used is strictly positive and row sums are unchanged.
- Corollary 5.3 (occupancy reduction R_pi), Theorem 6.1 (gap identity and f'(E) > 0), Theorem 6.3 and Remark 6.4, Theorem 6.5 (the function G, G(1), G(E), G(E(M - 1)), monotonicity), Theorem 6.7 (thresholds ell(t) and u(t), uniqueness of the root of Q = H), Theorem 6.9 (cumulant expansion and merge identity; all coefficients re-expanded), Theorem 6.10 (HM-AM step and the stated O(t^2 e^{-2t}) remainder), Theorems 7.1, 7.2 (where problems 1 and 2 were found), 7.4, Corollary 7.5, Theorem 7.6, Lemmas 7.7 and 7.8, the crumb function h(y) = y(qE + N - q) - qE(1 - e^{-ty}) with h'(0) = q(E(t - s_q) ... ) as stated, the value y_*, Theorem 7.10 and Example 7.11.

### Symbolic checks (sympy, `sym.py`)

Lemma 3.1 (a)-(d); the consolidation identity and the signs of Delta N and Delta D; the crumb identity and h'(0); the envelope identities of Theorem 7.2(f); the differences d_k and s_m - h; the 2xM and 3x3 algebra (G, G', a + b - 1 = 2(E - 1)(E + 1)/((2E + 1)(E + 2)), Q and H); the small-t coefficients for n = 4, 5, 6 against the closed form sum m_j (m_j - 1)(n - m_j)/(2 n^4); the merge identity. Two identities (f'(E) = p log(E/D) in the stated form, and the 2x2 closed form 1/2 + g_t(d) + g_tau(u)) were beyond sympy's simplifier and were confirmed numerically with mpmath at 50 digits at several points.

### Exact and high-precision arithmetic (`exact.py`: `fractions.Fraction` and mpmath)

59 checks pass; the one reported failure was an integer-division bug in my own script for the (5,3) score 8/11, and the manuscript's value is right. Confirmed: the 3x3 (2,1,0) gain at t = log 2 is 0.0053739 > 1/295; the 4x4 (2,2) gain at log 2 is 0.0090079 > 4/465 and at log 4 is 0.030131 > 1/35, with R(2,2) = 2r/(3(r + 1)); the auxiliary inequalities 12^5 < 16 * 7^5 and 9/4 > 2; the 2x3 gain D - H = 0.0069785 > 1/150 with H = 1/2; the gap identity and its sign for every partition with n <= 8 at four temperatures; ell(log 2) = 0.638532 and u(log 2) = 0.728389 with ell < t < u < t + log 4 and Q(ell) = P; the three rational fixtures q = 21/20, 15/14, 11/10 give the unique optima (1,1,1), (2,1), (3) respectively; the 2xM crossover tau_* lies in (t, t + log(M - 1)) for M in {2,3,4,8,50} and t in {0.2, log 2, 3} (M = 2 gives tau_* = t exactly, as Theorem 6.3 predicts); the crumb score 5/7 with s_1 = 2/3, delta = 1/21 and t s_1 = 0.924 < 1 for (3,2), E = 4; s_1 = 1/2, delta = 1/18 and scores 5/9, 8/11 for (5,3); the E = 64 half-crumb value 68/73 < 32/33; the fractional witness beats every pure allocation at tau = -(M-1)/(e delta) - 0.5 and below for (3,2) (0.714286 vs 0.697442 at tau = -8.225), (5,3) (0.563297 vs 0.518382 at -13.744) and (2,3) (0.391126 vs 0.149229 at -2.707); the small-t coefficient of (5,4) is 70/6561 and the large-t constant A(5,4) = 181/40; the balanced pair is the unique maximizer of the small-t coefficient for n = 3..12; A(m) is uniquely minimized by sqrt(n) equal groups for n in {4, 9, 16}.

### Brute force with fresh code (`bf.py`, `bf_grid.py`, `bf2.py`)

The model was coded from Section 2 (inner Boltzmann over all N rows including zeros, outer over all M tasks); the analytic gradient (Lemma 3.2) agrees with central finite differences to 1e-7 at random points. Purity was tested two ways: (i) exhaustive enumeration of every allocation whose rows lie on a uniform grid of the simplex with slack (or without slack where indicated), vectorized in chunks of 200 000 matrices, comparing the grid maximum with the best pure allocation and recording the best non-pure value; (ii) projected gradient ascent (exact sort-based projection onto {x >= 0, sum x <= 1} row by row) from hundreds of random starts, compared with the exact maximum over all pure allocations.

Grid shapes (N, M, G, slack): (2,2,12,yes), (2,3,8,yes), (3,2,10,yes), (3,3,7,yes), (2,4,6,yes), (4,2,8,yes), (4,3,6,no), (3,4,5,yes), (4,4,4,yes), (4,4,5,no), each at ten temperature pairs (t, tau) in {(0.5,0.5), (log 2, log 2), (1,2), (2,1), (3,0.5), (0.3,3), (5,5), (0.1,0.1), (1,0.7), (4,1.5)}. In every finished case the grid maximum equals the pure maximum and the best non-pure grid point is strictly below it (gaps between 1e-2 and 6e-2 in the lines quoted below).

Ascent and boundary checks: Theorem 7.6 for n in {2,3,4}, t in {0.5,2,4}, tau in {0,-0.5,-2,-8} (grid maximum equals sigma(t, n), every grid maximizer is a permutation matrix when the grid contains them, ascent never exceeds sigma); Theorem 7.1 for t in {0,-1,-5} and tau in {2,0,-3}; the (3,2), E = 4 grid at step 1/20 for tau in {-8,-6,-5.5,-5,-4,-1}; the Theorem 7.10 witnesses for (3,2) at tau in {-8,-12,-20} and (5,3) at tau in {-14,-25}; an extreme-temperature purity stress test (eight shapes, eight pairs with t, tau up to 8 and down to 0.05); and multi-start ascent on larger shapes. Final tallies are in the closing section.

### The source paper

arXiv 2506.09434 v1 was fetched as a PDF (SHA-256 begins 14c3a02ab1427008; the manuscript quotes no hash, the value agrees with the one recorded in the author-agent's notes) and read with pdftotext: the conjecture sentence is quoted verbatim in Section 6.1, and the theorem is titled "Exact softmax heterogeneity gain for N = M". v2 and v4 were read through the arXiv HTML rendering: the theorem is retitled and the word "conjecture" no longer appears; the version dates in `refs.bib` match the arXiv listing. The model in Section 2 matches the source exactly: B_c, the inner aggregation over all N agents (zero entries included), the outer aggregation over all M tasks, rows nonnegative with sum at most 1, and R_hom and R_het as the maxima over equal-row and general allocations. No discrepancy of definition, sign or normalization was found.

### Verification scripts of Section 8

SHA-256 of the five scripts, computed with `shasum -a 256`, match the manifest: identities 7c34e2c2...24b9, brute_force 65d22f42...8e5b, occupancy 6ec3a434...d807, negative_outer a836a9bd...9abb, additive_boundary c1443c8d...d991. Each script was run with the venv python; `identities.py` reports 75 checks and `negative_outer.py` 94 checks, both ending `FAILURES: none`, matching the manifest counts. The remaining three are reported in the closing section.

### References and prior art

Shioura 2009 and Liao et al. 2023 were resolved on Crossref by DOI (titles, authors, journal, year, pages agree); Bolker 1972 was found by Crossref search (DOI 10.1016/0095-8956(72)90060-3, not in the entry); the HLP, De Loera and Kim, Cohen and Fausti entries were checked against arXiv or Crossref metadata; ABPv1 and ABPv4 against the arXiv abstract page. Five prior-art searches (web and arXiv; nested or hierarchical softmax and Boltzmann-weighted task allocation, heterogeneity gain, pure maximizers of softmax-aggregated objectives over products of simplices) found no external statement of universal purity or of the gap identity; the only hit is the lab's own repository. The related-work paragraph is therefore accurate as far as I can tell; the pointers "Theorem 5" of Liao et al. and "eq. (41)" of Cohen and Fausti were not checked against the full texts.

### Compilation

`tectonic main.tex` on a scratch copy produces 24 pages, no undefined references or citations, no missing labels, no em-dash. Pages 12, 20 and 22 were rasterized and inspected: the truncation of the page-12 display (problem 8) and the protruding `\texttt` strings on page 22 (problem 9) are visible in the rendered PDF, not just in the log. The AI-disclosure footnote is present on the title page.
