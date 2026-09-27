# Field audit pilot: interim results (8 of 10 papers)

Status 2026-09-27. Both extraction passes have finished 8 pilot papers; the
Frechet paper and the Remkan page-image re-extraction are in progress. Controls
C1 and C2 pass for both certificate types (`harness/controls_result.json`,
`harness/controls_closed_result.json`). Per amendment 3 these pilot papers are
the development set; they are retested with the frozen harness later, and P1 is
reported with and without them.

Harness changes during the pilot (all followed by a controls re-run): the
rational harness separates isolating intervals strictly; the closed-form grid is
scaled to the point where both survival functions fall below 1e-40, since a
fixed grid out to x = 30 left most points undecidable for fast-decaying models.

## Tally so far (development set, not a rate)

| paper | theorem-level result | printed evidence |
|---|---|---|
| arxiv:2601.07249 (CLFRD) | Theorem 3.2 (lr) and Remark 3.3 (rh) refuted | none printed |
| arxiv:2103.00763 (Poisson, geometric) | discrete, not checkable | 2 of 3 counterexamples fail |
| doi:10.7153/mia-2020-23-03 (claim amounts) | 16 theorems survive (independence only) | 7 of 7 reproduce |
| doi:10.52547/jsri.16.1.101 (GMW systems) | 13 theorem families survive (325 checks) | 5 of 5 reproduce |
| doi:10.1017/s0269964826100199 (q-Weibull) | 4 theorem families survive (80 checks) | 14 of 14 reproduce |
| arxiv:2407.18801 (second order statistics) | Remark 2 false; the ordering it licenses fails; Proposition 2 misstated | not checked |
| doi:10.37119/jpss2023.v21i1.637 (MWU) | Theorem (1) refuted in both parts, all three orders (directions reversed) | none printed |
| doi:10.1080/02331888.2025.2552185 (Kw-G random extremes) | Theorems 3.7 and 3.8 refuted | not yet checked |

Papers with at least one theorem refuted as stated, no ambiguity: 3 of the 7
with checkable theorems (CLFRD, MWU, Kw-G).

## doi:10.52547/jsri.16.1.101 (generalized modified Weibull systems)

Theorems 1, 2, 4, 7(i), 8, 9, 10, 11, 12, 15(i), 15(ii), 16(i), 16(ii): no
counterexample in 325 checks with independent components (the independence
copula meets every Archimedean condition used), g = 1, integer b; exact where
l = 0 is allowed, closed-form interval checks with l = 1/2 otherwise. Theorems
3, 5, 6, 7(ii), 13, 14, 17 untested. Printed Examples 1, 2(i), 2(ii), 3A, 3B
reproduce in the printed direction (`harness/pilot_gmw_examples_result.json`).
Pass A splits Example 3 into two records, pass B keeps one.

## doi:10.1017/s0269964826100199 (q-Weibull extremes)

Theorems 3.1(1), 3.1(2), 3.10(1), 3.10(2): no counterexample in 80 checks on
(0, D). All 14 printed example verdicts reproduce, including every "no order"
claim (both directions fail) and every printed interval end D. The passes agree
on all 40 records (labels differ only by figure references).

## arxiv:2407.18801 (second smallest order statistics, Archimedean copulas)

- Remark 2 says the scale, PHR and location models satisfy condition (ii) of
  Theorem 3.1 (a -> Fbar(x; e^a) decreasing and log-convex) and that (ii) is
  equivalent to a DFR baseline. False for two of the three models: under PHR
  the second derivative in a is e^a log Fbar(x) < 0 (exactly -1 at x = 1,
  a = 0), so (ii) never holds; under the scale model (ii) is equivalent to
  u h(u) decreasing, not DFR, and it fails for the paper's own example baseline
  EW(0.9, 0.9) (second derivative enclosed in [-0.0160005, -0.0160005] at
  u = 1/100).
- The ordering those models would inherit fails: with independence (a
  log-concave generator) and exponential rates theta = (11/4, 1/4, 3), which is
  p-larger than theta* = (1/2, 9/4, 2), S_X - S_Y is rigorously negative at
  t = 2, 4 ln 2, 4 and 8, so X_{2:3} >=st Y_{2:3} fails
  (`harness/pilot_2407_18801.py`, `harness/c3_2407.py`). The same instance
  transfers exactly to the PHR model with any baseline and to the scale model
  with any Weibull baseline, including DFR ones. Theorem 3.1 itself is not
  refuted, since these models violate its condition (ii); what fails is the
  paper's claim that the theorem covers them.
- Proposition 2 as printed places no condition on the location vectors while
  its proof assumes a common location; both passes flagged it independently.
  Recorded as a misstatement, not counted as a refutation.

## doi:10.37119/jpss2023.v21i1.637 (modified weighted uniform)

Theorem (1), read from the page image because the text layer drops subscripts:
(i) a1 < a2, l1 = l2 and (ii) a1 = a2, l2 > l1 each claim X <=lr Y, X <=hr Y
and X <=st Y. **Both parts are refuted in all three orders, and the reverse
orderings hold** (exact, `harness/pilot_mwu.py`): at a = (0, 1), l = 1,
S_X(1/4) = 3/4 > S_Y(1/4) = 9/16; at a = 1, l = (1, 2), S_X(1/4) = 9/16 >
S_Y(1/4) = 1/4. The proofs compute f_Y/f_X correctly and then call it
increasing when it is decreasing.

## doi:10.1080/02331888.2025.2552185 (Kumaraswamy-G random extremes)

Section 3.2 assumes independence and a common random sample size N. With
a = b = 1 the random minimum's survival is sum_m P(N = m) Gbar^{gamma_1 + ... +
gamma_m}, a mixture over partial sums in index order (`harness/pilot_kwg.py`,
exponential baseline, N uniform on {2, 3}):
- **Theorem 3.7 refuted** (sum gamma <= sum delta iff X_{1:N} >=hr Y_{1:N}):
  gamma = (2, 2, 1/2), delta = (1, 1, 3) meets the sum condition and the
  hazard order fails. It also fails under the stronger reading where the sum
  condition holds for every m that N can take: gamma = (1, 1, 1),
  delta = (1, 1, 18). The hazard rate order is not closed under mixtures over
  N, the same mechanism as the original cone's frozen-column lift.
- **Theorem 3.8 refuted** (delta majorized by gamma implies X_{1:N} >=hr
  Y_{1:N}): gamma = (3, 2, 1), delta = (2, 2, 2); even the usual order fails,
  S_X(1) = 0.00461 < S_Y(1) = 0.01040.
- Other theorems and the three printed counterexamples: not yet checked.

## Extraction agreement (C5, 4 papers)

Pass A and pass B found the same claims in 3 of 4 papers (7/7, 8/9, 23/23;
pass B added one table record). The fourth (Remkan) has 4 records in each pass
under different labels because the math glyphs are unreadable. Every matched
claim agrees on order and direction; hypothesis lists differ only in
granularity (pass A splits the distributional setup into its own item).

## arxiv:2601.07249 (compounded linear failure rate distribution)

- **Theorem 3.2 (lr): refuted as stated.** Claim: a1 <= a2, b1 <= b2,
  l1 <= l2 implies CLFRD(a1,b1,l1) >=lr CLFRD(a2,b2,l2). Instance
  a = (1,1), b = (1,2), l = (1,1) satisfies the conditions under either reading
  (joint or separate). The log-derivative of g_X/g_Y at 0+ is exactly -1
  (sympy limit), the harness encloses the lr expression at x = 1e-12 in
  [-3.99999999997, -3.99999999997], and an independent evaluator using the
  paper's printed density (`harness/c3_clfrd.py`) shows g_X/g_Y strictly
  decreasing near 0 with a rigorous interval enclosure (C3).
- **Remark 3.3, reversed hazard rate: refuted** (5 of 40 random admissible
  instances, all with equal a and l and b1 < b2; witness near 0).
- Remark 3.3, usual stochastic and hazard rate: no counterexample in 40
  instances each. Mean residual life, convex, concave and harmonic-average
  claims: not checkable by the harness.

## doi:10.7153/mia-2020-23-03 (largest claim amounts)

- Theorems 3.1 to 3.16: no counterexample in 290 exact checks under the
  independence copula (which meets every copula condition the theorems use),
  h(p) = p, and exponential or transmuted-exponential marginals
  (`harness/pilot_mia2020_result.json`). Dependent copulas are untested.
- Printed examples: all 7 reproduce. Examples 3.3, 3.5 and 3.6 exactly
  (Pareto marginals with AMH or FGM copulas are rational in 1/x); Examples 3.1,
  3.2, 3.4 and 3.7 on a 400-point grid at 50 digits. Example 3.3's printed p*
  misses its equal-sum majorization hypothesis by rounding
  (2.0479 x 2.0319 = 4.16112801 versus 2.02 x 2.06 = 4.1612): a misprint, not
  counted as a failure.

## arxiv:2103.00763 (Poisson and geometric extremes)

- Theorems 3.1 to 3.4: discrete families, outside the harness's checkable
  list; recorded, not tested.
- Printed counterexamples (standard discrete definitions, since the paper
  gives none):
  - 3.1 reproduces to 7 digits (-0.0232122 at r = 2, 0.0520158 at r = 5).
  - **3.2 fails:** printed values 0.0124328 (r = 6) and -0.00024431 (r = 16);
    computed 0.0160959 and +0.0027970. The hazard difference is positive for
    every r from 1 to 40, so the claimed sign change does not exist
    (wrong value, wrong sign, fabricated sign change).
  - **3.3 fails:** the printed vectors q = (0.99, 0.96, 0.57) and
    q* = (0.9, 0.78, 0.57) sum to 2.52 and 2.25, so the majorization hypothesis
    the counterexample is meant to satisfy does not hold; the printed values
    (-0.0010584 at u = 1, 0.00628996 at u = 4) do not reproduce, and the
    computed difference is positive for every u from 1 to 40.
  - A first scan of 3.2 at 50 digits showed a spurious sign change past r = 24;
    it came from cancellation in 1 - cdf for a Poisson mean of 0.1. The
    committed script sums the tails directly at 80 digits.

## doi:10.34198/ejms.14224.333347 (Remkan distribution)

Parameter symbols, formulas and order subscripts are unreadable in every text
rendering. Needs re-extraction from page images by both passes; not tested.

