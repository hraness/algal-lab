# Field audit protocol: exact re-verification of stochastic-comparison theorems

Status: frozen before any data collection, 2026-09-27. Changes after the
corpus freeze (step 2) are recorded as dated amendments below, never by editing
this text.

## Question

In the published literature on stochastic comparisons of heterogeneous
parametric models (mixtures, order statistics, coherent systems), how often is a
theorem false as stated, and how often does printed numerical evidence fail
exact re-evaluation?

The cluster audit (`../cluster-audit/`) found both at high rates, but in papers
chosen because they share one defective proof step. This study measures the
rate in a random sample, so the known cone is excluded from the primary
estimate and reported separately.

## Primary outcomes

- **P1.** Share of sampled eligible papers with at least one theorem refuted as
  stated, with a 95% Wilson interval.
- **P2.** Share of printed numerical examples (point values, sign claims,
  transform products, weight vectors) that fail exact re-evaluation, using the
  verdict classes of `../example-sweep/memo.md`.

Secondary: rates by proof technique (T-transform or chain-majorization lift on a
ratio functional versus everything else), venue and year, and the share of
claims the harness can check at all.

## 1. Population and frame

- Works whose title or abstract contains "stochastic comparison", "stochastic
  ordering" or "stochastic order", together with one of "majorization",
  "heterogeneous", "mixture", "order statistic", "coherent system", "series
  system" or "parallel system", published 2010-01-01 to 2026-09-27, as returned
  by Semantic Scholar and Crossref (OpenAlex too if its API is not throttled),
  deduplicated by DOI.
- Eligible: the paper states at least one theorem ordering two parametric
  distributions under a named order (usual stochastic, hazard rate, reversed
  hazard rate, likelihood ratio, dispersive, star, Lorenz, ageing orders), and
  its full text is legally retrievable (open access, arXiv, or author
  manuscript).
- The 31 papers of the known defect cone are removed from the frame and
  analysed as a separate stratum.

## 2. Freeze and sample

- Commit the eligible list (DOI, title, venue, year, text source) and its
  SHA-256 before testing any claim.
- Draw a simple random sample of 100 papers (all of them if fewer are eligible)
  with a seed derived from that hash, so the sample cannot be chosen by hand.

## 3. Claim extraction

- Two independent passes per paper, each producing structured claim records:
  family, parameters, every hypothesis, order, direction, quantifiers and
  domain, plus a verbatim quote with page and line.
- The second pass does not see the first. Disagreements are adjudicated against
  the text. Only agreed or adjudicated records are tested.
- A claim is checkable if its functional can be evaluated exactly for at least
  one family the harness supports (exponential and Weibull-type models by
  substitution, power-function, Pareto, proportional hazards and reversed
  hazards, generalized Lehmann, location-scale with those baselines, and
  mixtures and order statistics of these). Uncheckable claims are recorded,
  not tested.

## 4. Testing

- Generate admissible instances with exact rational parameters that satisfy
  every printed hypothesis, including majorization conditions checked exactly.
- Evaluate both sides of the claimed inequality exactly: rational functions
  after substitution, Sturm root counts for interval claims, and rational
  bisection with interval enclosures for quantile orders
  (`../shape-sweep/mixlib.py`).
- **Refuted as stated** requires an admissible instance and an exact sign
  certificate. A refutation that depends on one reading of an ambiguous
  hypothesis is reported as "refuted under reading R" and excluded from P1.
- A claim that survives is reported as "no counterexample in a bounded search
  of k instances", never as true.

## 5. Controls

- **C1, known true.** 20 standard theorems from Shaked and Shanthikumar (2007)
  and Marshall, Olkin and Arnold (2011) run through the same pipeline without
  labels. Any refutation stops the study until the cause is found.
- **C2, planted false.** 20 mutations of true theorems (direction flipped,
  hypothesis dropped, order swapped). The pilot must refute at least 90%.
- **C3, second implementation.** Every refutation is re-checked by a separately
  written evaluator and must agree.
- **C4, hypothesis fidelity.** Every refuting instance is re-checked against the
  printed hypotheses by the second extraction pass.
- **C5, extraction agreement.** Inter-pass agreement on claim structure is
  reported; the pilot needs at least 80% before scaling.

## 6. Pilot and stopping rules

- Pilot: 10 papers drawn at random from the frozen sample.
- Scale to the full sample only if C1 is clean, C2 reaches 90% and C5 reaches
  80%.
- Stop immediately on any C1 failure.
- If the pilot finds no refutations and no failed printed numbers, still finish
  the sample of 100 (a low rate is a result), but do not expand beyond it.

## 7. Analysis

- P1 and P2 with Wilson intervals; secondary splits are descriptive.
- No outcome, threshold or exclusion changes after the freeze except through
  dated amendments with reasons.

## 8. Ethics

- Every certified refutation goes to the corresponding author with its
  certificate, and a 30-day window, before any public release.
- Public reports give aggregate rates. Per-paper findings appear only with
  their certificates and after notification.
- Errors are reported as errors. No claims about intent.
- The unlisted drafts on hraness.com stay unlisted until notification is done.

## 9. Decisions that need Ben

- **D1.** The second extraction pass needs a separate agent or model session
  that has not seen the first pass.
- **D2.** Author notifications are emails and need explicit approval before
  sending.
- **D3.** Venue for the write-up.

## Deliverables

The frozen frame and sample, claim records, certificates, pipeline code, control
results, and a paper reporting P1 and P2.

## Amendments

None yet.
