# Field audit pilot: interim results (4 of 10 papers)

Status 2026-09-27. Both extraction passes finished 4 pilot papers before the
agent quota ran out; the other 6 await extraction. Controls C1 and C2 pass for
both certificate types (`harness/controls_result.json`,
`harness/controls_closed_result.json`). Per amendment 3 these pilot papers are
the development set; they are retested with the frozen harness later, and P1 is
reported with and without them.

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

## Running tally (development set, not a rate)

- Papers with at least one theorem refuted as stated: 1 of 3 testable
  (arxiv:2601.07249).
- Papers with failed printed evidence: 1 of 3 with printed examples
  (arxiv:2103.00763, 2 of 3 counterexamples).
