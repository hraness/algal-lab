# Review notes: "Purity and phase structure of nested Boltzmann task allocation"

Manuscript: `papers/boltzmann-purity/main.tex` (+ `refs.bib`), built with `tectonic main.tex` (tectonic 0.17.0), 24 pages before the referee revision, 25 pages after it.
Delivered PDF: `boltzmann-allocation-purity.pdf` in the owner's delivery folder for 2026-09-25 (outside the repository).
Verification scripts: `papers/boltzmann-purity/verify/*.py`, outputs in `verify/results/`; all five end with `FAILURES: none` (75 + 192 + 140 + 94 + 38 checks).

## Dependency map

```
Lemma 2.1 (elementary: scaling, dB/dc = Var >= 0, monotonicity in c)
  -> Lemma 3.1 (derivative identities, Hessian, sum of partials = 1)
  -> Lemma 3.2 (nested chain rule: dR = W p h, second derivative decomposition)
     -> Lemma 4.1 (maximum-point signs: W_j > 0 on active tasks, h_ij > 0 at positive entries, full budgets, common row multiplier)
        -> Lemma 4.2 (forest structure of the support)          -> Theorem 5.1 (universal purity, t,tau > 0)
        -> Lemma 4.3 (private-task consolidation)  -> Cor 4.5 (separation) -> Corollary 5.3 (occupancy reduction)
        -> Lemma 4.4 (dominance)                                   |
                                                                    v
  Theorem 6.1 (gap identity, matched temperatures, refutation of v1 conjecture) <- Cor 5.3 + f'(E) > 0
  Theorem 6.3 (2x2 exact)                <- Cor 5.3
  Theorem 6.5 (2xM crossover)            <- Cor 5.3 + G-function analysis
  Theorem 6.7 (3x3 phase table)          <- Cor 5.3 + Theorem 6.1 (for ell < t < u)
  Theorem 6.9 (small matched t)          <- Cor 5.3 + cumulant expansion + merge identity
  Theorem 6.10 (large matched t)         <- Cor 5.3 + HM-AM inequality
  Theorem 7.1 (score set at t <= 0)      <- Lemma 2.1 only
  Theorem 7.2 (concave envelope, tau = 0)<- layer-cake + Jensen (self-contained)
  Theorem 7.4 (tau = 0 rectangular optimum) <- Theorem 7.2
  Cor 7.5 (divisible case, all tau <= 0) <- Theorem 7.4 + Lemma 2.1
  Theorem 7.6 (square, tau <= 0)         <- Cor 7.5
  Lemma 7.8 (bounds for tau <= 0), Lemma 7.9 (pure bottleneck ceiling)
  Theorem 7.10 (indivisible case: fractional maximizers) <- Lemmas 7.8, 7.9 + crumb function
```
(Numbers refer to the order in the PDF; labels in the source are `lem:elementary`, `lem:derivatives`, `lem:nested`, `lem:signs`, `lem:forest`, `lem:private`, `lem:dominance`, `cor:separation`, `thm:purity`, `cor:occupancy`, `thm:gap`, `thm:twotwo`, `thm:twoM`, `thm:threethree`, `thm:smallt`, `thm:larget`, `thm:scoreset`, `thm:envelope`, `thm:rect`, `cor:divisible`, `thm:square`, `lem:negouter`, `lem:ceiling`, `thm:indivisible`.)

## Claim-by-claim table

| Claim | Where proved | How re-verified | Status |
|---|---|---|---|
| Derivative identities, Hessian of B_c, sum of partials = 1 | Lemma 3.1 | sympy (`identities.py`) | verified |
| Nested chain rule dR = W p h and second-derivative decomposition | Lemma 3.2 | sympy | verified |
| Maximum-point signs, full budgets, common multiplier | Lemma 4.1 | line-by-line rederivation; brute-force maxima satisfy them | verified |
| Forest structure, consolidation, dominance, separation | Lemmas 4.2-4.4, Cor 4.5 | rederived; consolidation identity in sympy | verified |
| Universal purity for t, tau > 0 | Theorem 5.1 | rederived; exhaustive grids for 8 shapes x 9 temperature pairs + 40-start ascent (`brute_force.py`) | verified |
| Occupancy reduction R_pi | Cor 5.3 | sympy + numeric | verified |
| Gap identity and strict gain for n >= 3 at t = tau | Theorem 6.1 | sympy identity; mpmath for n = 3..8; Fraction certificates 1/295, 4/465, 1/35 | verified |
| Refutation of v1 exactness conjecture | Section 6.1 | v1 PDF quoted (SHA-256 14c3a02a...fa82); v2-v4 fetched | verified |
| 2x2: R_het = sigma(max{t,tau,0},2), closed form | Theorem 6.3, Remark 6.4 | sympy (tanh identity), grids for all sign patterns | verified |
| 2xM: max{H,D}, crossover t < tau_* < t + log(M-1), counts M(M-1)/M^2/M | Theorem 6.5 | sympy for G, G', G(1), G(E), G(E(M-1)); bisection for M in {2,3,4,8,50}; grid counts | verified |
| 2x3 example 1/150 | Example 6.6 | Fraction | verified |
| 3x3 phase table, ell(t) < t < u(t) < t + log 4, counts 6/24/18/21/3, 18 maximizers at matched t | Theorem 6.7, Example 6.8 | sympy; bisection for 7 values of t; rational fixtures; grid counts | verified |
| Small-t expansion, coefficient formula, balanced pair optimal | Theorem 6.9 | sympy power-sum form, merge identity; numeric convergence; exhaustive search n <= 12 | verified |
| Large-t expansion, A(m) >= 2 sqrt(n) - 2 | Theorem 6.10, Example 6.11 | sympy; numeric convergence; exhaustive n in {4,9,16} | verified (remainder stated as O(t^2 e^{-2t}), weaker than the notes' O(t e^{-2t})) |
| Score set at t <= 0 | Theorem 7.1 | grids with t <= 0, both signs of tau | verified |
| Concave envelope (a)-(f) | Theorem 7.2 | `additive_boundary.py` (random columns, price formula, gap constant) | verified |
| tau = 0 rectangular optimum, balanced pure maximizers, N = 1 exception | Theorem 7.4 | grids for 8 shapes | verified |
| Divisible case for all tau <= 0; square case = permutation matrices | Cor 7.5, Thm 7.6 | grids | verified |
| Bounds for tau <= 0, (M-1)/(e|tau|) | Lemma 7.8 | 20000 random vectors | verified |
| Indivisible case: fractional maximizers for tau < -(M-1)/(e delta) | Theorem 7.10 | rederived; witnesses in Fraction; crossover scan | verified |
| Witness numbers 5/7, 1/21, 5/9, 1/18, 68/73 | Example 7.11 | Fraction | verified |
| Crossover for (3,2), E = 4 between tau = -6 and -5 | Example 7.11 | grid step 1/20 (numerical observation only, stated as such) | numerical |

## Discrepancies found during re-verification

1. Threshold in the indivisible theorem: the notes state tau < -2(M-1)/(e delta); the argument gives the sharper tau < -(M-1)/(e delta). The manuscript uses the sharper bound (for (3,2), E = 4: -21/e instead of -42/e). Both are valid.
2. Large-t remainder: proved as O(t^2 e^{-2t}) (the cross term of two first-order terms); the notes' O(t e^{-2t}) was not re-derived and is not claimed.
3. Numerical value u(log 2): a draft of Example 6.5 carried 0.9036; the bisection gives 0.72839. Corrected.
4. In the notes' 3x3 analysis the numerator of a + b - 1 was recorded in a form that sympy could not confirm at first; the correct form 2(E-1)(E+1)/((2E+1)(E+2)) was verified and is used.
5. Two sympy checks needed manual rewriting (tanh identity via exp rewrite; f'(E) via forced log expansion); these were tool limitations, not mathematical errors.
6. The gradient-ascent restarts initially "failed" because non-global KKT points (matrices with an empty row) trap the ascent at large temperatures; this is consistent with the theory (full budgets are proved only at maximum points) and the check criterion was rewritten to test exactly what the theorem states. Documented in Section 8.
7. `mp.findroot` failed on the threshold equations; replaced by plain bisection.

## Results deliberately left out (and why)

- Sufficient regions t <= 2, tau >= t/4 and the kappa_N conditions of the earlier purity notes: superseded by the universal theorem.
- Feasible-reward certificate, support bounds K <= 2N-1 and E <= 3N-2, all-agent-star Lambert-W exclusion, two-agent trace argument: superseded or not needed once purity is universal.
- Flow reduction with weights and capacities, the certified solver internals (Megiddo/Dinkelbach parametric search, dynamic programming, interval arithmetic): software artifacts rather than theorems; the paper needs only the occupancy reduction.
- Schur-threshold notes and Proposition C (reduction in the negative-outer notes): not re-verified line by line in this pass.
- The "ICLR 2026" venue attribution of the source paper: could not be confirmed (arXiv record lists no venue; OpenReview unreachable).
- References that were only found by search but not retrieved (Lim-McCann 2022, Gross 1956) and works verified but not needed (Megiddo 1979, Dinkelbach 1967, Fox 1966, AHO 2003, Starr 1969, Hsu et al. 2013, AMO 1993, Bhatia-Davis 2000) are not cited.

## Blockers and caveats

- The author line is a placeholder `[Owner name to be confirmed]` with an AI-assistance footnote.
- Publisher pages (ScienceDirect, Taylor and Francis, INFORMS, World Scientific), OpenReview, DBLP and Google Books were blocked or rate limited; Crossref, arXiv, Open Library and Semantic Scholar answered intermittently. All eight cited references were verified by a successful fetch (arXiv, Crossref or Open Library); v2 and v3 of the source were read only through the arXiv HTML rendering summarized by the fetch tool.
- Open questions listed at the end of Section 9 (Section 9 is the related-work section; Section 8 is the verification section) are stated as open; nothing there is claimed.
- No result depends on repository code; the verification scripts are independent.

## Suggested venue

Primary: Operations Research Letters (short, complete proofs, OR audience) or Mathematics of Operations Research if extended with the open questions resolved. Alternative: Autonomous Agents and Multi-Agent Systems for the multi-agent audience. arXiv: math.OC, cross-list cs.MA.

## Revision response (after `REFEREE-REPORT.md`)

The independent referee report (verdict: minor revision) is committed unchanged as `REFEREE-REPORT.md`. Every item was addressed; numbers below are the referee's.

1. Theorem 7.2(b), k = 0: statement now reads "with equality if and only if k = 0, k = N or x = 1_L"; the proof treats k = 0 and k = N separately and argues strictness of both monotonicities for 1 <= k <= N-1.
2. Theorem 7.2(c), strictness gap: the converse is now proved by the referee's three cases. With c = x_i minimal among coordinates in (0,1) (so all smaller coordinates are 0): (i) some coordinate is 0, use u in (0,c); (ii) no coordinate is 0 and some exceeds c, use u in (c,c'); in both, 1 <= n_u <= N-1 and x differs from 1_{L_u}, so (b) is strict on an interval; (iii) x = c1 is constant, then B_t(x) = c and strictness comes from the Jensen step, since phi is concave, not linear on [0,N] (d_0 > d_{N-1}), and a concave function meeting its chord at an interior point equals the chord. Statement unchanged; Theorem 7.4 and Corollary 7.5 unaffected.
3. "at positive temperatures" added to the two-agent, M-task claim in the abstract and in the introduction bullet.
4. Abstract: "is decided by ... together with" replaced by "depends on whether M divides N and on the size of t", followed by the precise divisible and indivisible statements. Introduction: "depends on divisibility in the following sense", plus a sentence that the case t s_q > 1 and moderately negative tau remain open. The novelty paragraph now says "negative-outer divisibility results (Corollary 7.5 and Theorem 7.10)" instead of "dichotomy"; "Why this matters" says "negative-temperature results".
5. Abstract: the gap-identity sentence now begins "On square instances (N = M)".
6. Theorem 7.1: now "the supremum of U(S(A)) over F equals its supremum over homogeneous allocations, and whenever the maximum exists it is attained at a homogeneous allocation"; the proof notes that U o S takes the same set of values on both sets and that B_tau is continuous. The proof now cites Lemma 2.1(i) directly.
7. (optional, done) Lemma 2.1(ii): "(for n >= 2; if n = 1 then p_1 = 1 = sigma(c,1) for every x)".
8. (must fix, done) Theorem 6.5 proof display split into a two-line `gather*`; the G'(F) expression is printed in full (checked in the PDF text).
9. Overfull boxes: all removed (the final log has no Overfull or Underfull warnings). Consolidation display (Lemma 4.3), the s_k/d_k display (7.2 preamble) and the S_j display (Theorem 7.10 proof) split into two lines; Theorem 6.7 first sentence rephrased ("R_het is the largest of P, Q(tau) and H(tau)"); SHA-256 column set in `\scriptsize` monospace; the brute-force shape list written as a sentence; reproduction commands moved to a `quote` block; the repository path uses `\path`.
10. Author line kept as a clearly marked placeholder, "[Placeholder: author name to be confirmed]". The footnote now says the manuscript and proofs were prepared with AI research agents, "The identities and every numerical statement were independently recomputed by the scripts of Section 8; no proof assistant was used." The AI-assistance disclosure is kept. The Organization paragraph says "computational verification" instead of "machine verification".
11. Venue: Section 9 now says the arXiv record lists no venue and an author's publication page lists the paper under ICLR 2026, not confirmed from OpenReview. (Re-checked: matteobettini.com/publication/hetenvdesign/ contains "International Conference on Learning Representations (ICLR)".)
12. (optional, done) v3 re-read through arXiv HTML during this revision: Theorem 3.4 is titled "Softmax heterogeneity gain for N=M", the statement matches the quoted text, and the word "conjecture" does not occur. Section 9 now says Theorem 3.4 and its surrounding text were read in each version.
13. Theorem 7.4: added the argument that a maximizer of sum_j phi(c_j) with sum N can be moved to an integer vector (two fractional coordinates, linear pieces, move mass in a non-decreasing direction until one becomes integer, repeat).
14. (optional, done) Remark after Lemma 2.1: strict monotonicity on the feasible domain now stated for |c| <= 1 with the one-line reason (equality needs {x_i, B_c(x)} = {0,1}, impossible).
15. (optional, done) Theorem 6.7 proof now says explicitly that G is strictly decreasing with G(1) > 0, so it has exactly one root in (1, infinity), which lies in (1, 4E).
16. Timing sentence replaced by the measured timing; see "Verification rerun" below.
17. (optional, done) Bolker 1972 entry now carries DOI 10.1016/0095-8956(72)90060-3 (the `plain` style does not print DOIs, as for the other entries).
18. (optional, done) Remark 7.12 rewritten precisely: for t > 0 and N >= 2, fractional maximizers can occur only for tau < 0 and M not dividing N; for t <= 0 and M >= 2 the maximizers are exactly the M concentration allocations if tau > 0, while the uniform homogeneous (fractional) allocation is a maximizer if tau <= 0; for N = 1 and M >= 2 the maximizers are the unit rows (tau > 0), all full-budget rows (tau = 0), and the uniform row alone (tau < 0).

### Errors found in the author's own re-read (Sections 1 to 7)

Sections 1 to 5 were re-read line by line after the previous compaction; every derivation (Lemmas 2.1, 3.1, 3.2, 4.1 to 4.4, Corollary 4.5, Theorem 5.1, Corollary 5.3) was re-derived by hand and no mathematical error was found. Two factual errors were found in Section 6.1 and corrected:

- The paragraph "Refutation of the exactness conjecture" said the conjecture sentence of v1 *follows* Theorem 3.4. In the v1 PDF (SHA-256 14c3a02a...fa82, re-fetched) it *precedes* the theorem, as Section 9 correctly said. Now "the text immediately preceding it".
- The same paragraph said branch (iii) of the lower bound "is recovered in Theorem 7.6 and Remark 7.7"; those concern the tau <= 0 branch. It now justifies branch (iii) directly (a permutation matrix has reward sigma(t,N), and R_hom = sigma(tau,N) for tau >= 0) and attributes the tau <= 0 branch to Theorem 7.6 and Remark 7.7.

### Verification rerun (item 16)

All five scripts were rerun with the Python 3.12 venv on the unchanged scripts (SHA-256 values match the manifest in Section 8): identities 75, occupancy 140, negative_outer 94, additive_boundary 38 and brute_force 192 checks, all PASS, each ending `FAILURES: none`. Every output, including `results/brute_force.json`, is byte-identical to the committed results. The host was heavily loaded (load average 52 to 80 on 18 logical CPUs): total wall-clock 1866 s (31 min), total CPU (user + sys) 322.6 s (about 5.4 min), dominated by `additive_boundary.py` (116.5 s CPU) and `negative_outer.py` (100.1 s CPU), not by the brute-force grids (44.6 s CPU). Section 8 now states the CPU time, the wall-clock time and the load. Per-script timings are in `verify/results/timing.txt`, which replaces `occupancy.time` (that file recorded a local absolute interpreter path).

### Compilation

`tectonic main.tex`: 25 pages, no undefined references or citations, no Overfull or Underfull box warnings, no em-dash (U+2014) and no `---` in `main.tex`; the AI-assistance disclosure is kept in the title footnote.
