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
  by the Semantic Scholar bulk search (which applies this boolean rule to title
  and abstract), re-checked locally against the same rule, and deduplicated by
  DOI. OpenAlex is used as a cross-check if its API is not throttled, and the
  overlap is reported.
- Eligible: the paper states at least one theorem ordering two parametric
  distributions under a named order (usual stochastic, hazard rate, reversed
  hazard rate, likelihood ratio, dispersive, star, Lorenz, ageing orders), and
  its full text is legally retrievable (open access, arXiv, or author
  manuscript).
- The 31 papers of the known defect cone are removed from the frame and
  analysed as a separate stratum.

## 2. Freeze and sample

- Commit the candidate frame (every work matching the query, before any
  eligibility screening) and its SHA-256.
- Order the frame by a random permutation seeded from that hash, so the order
  cannot be chosen by hand.
- Screen candidates in that order and take the first 100 eligible papers (all
  eligible papers if the frame runs out). This is a simple random sample of the
  eligible population without screening every candidate.
- Record every screening decision with its reason, and commit the screened list
  before testing any claim.

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

1. **2026-09-27, before the freeze.** Semantic Scholar withholds the abstracts
   of some publishers, so the local re-check of the frame rule cannot run on
   those records. They are kept and flagged `abstract_withheld` (310 of the 858
   candidates) instead of dropped, because dropping them would bias the frame
   against those publishers. Screening reads each paper anyway.
2. **2026-09-27, before extraction and testing.** Clarifications from the first
   screening pass:
   - Eligibility covers parametric and semiparametric families (a baseline
     distribution with explicit parameters, such as scale, proportional hazards
     or transmuted families). Papers whose ordering results concern only
     arbitrary distributions with no parameters, or stochastic processes, are
     ineligible.
   - Unnumbered stated results count as theorems.
   - Candidates whose open-access link is blocked by the publisher's bot
     protection are marked `retrieval_blocked`, not ineligible. They are retried
     through a browser session before the sample of 100 is frozen, and join it
     in screening order if they turn out to be eligible.
   - The pilot is the first 10 eligible papers in screening order among those
     whose text was retrieved. Retrieval failures are technical, so the pilot
     remains a random subset of the eligible population.
   - The known cone is removed mechanically: a candidate is excluded if its
     DOI or arXiv id appears in any prior audit memo (`prior_audit_ids.json`).
3. **2026-09-27, during the pilot, after reading the pilot extractions and
   before running any pilot claim through the harness.** Many pilot families
   (for example compounded linear failure rate, generalized modified Weibull,
   q-Weibull) are not rational functions of one shared variable, so the first
   harness would mark them uncheckable. The harness gains a second certificate
   type, applied to every claim whose survival function has a closed form:
   the order's defining expression is evaluated at rational points (near the
   left boundary, on a linear grid and on a geometric grid) with rigorous
   interval arithmetic, and a point where the enclosure lies strictly on the
   wrong side is a refutation. Controls C1 and C2 are extended to this
   certificate type before it is used. Because this change was prompted by a
   pilot paper, the pilot serves as the development set: the harness is frozen
   after the pilot, all sampled papers including the pilot are tested with the
   frozen harness, and P1 is reported both with and without the pilot papers.
4. **2026-09-27, before the sample of 100 is frozen.** Retrieval adds
   Unpaywall's open-access locations (queried once per DOI) to Semantic
   Scholar's link and arXiv, and every candidate without retrieved text is
   re-attempted, repository copies first. This widens "legally retrievable" to
   accepted and submitted manuscripts in repositories, and reduces the
   publisher-blocked downloads that would otherwise skew the sample by
   publisher. The version retrieved (published, accepted or submitted) is
   recorded per paper. A refutation found on a manuscript version is reported
   with that version, since the published text may differ. The pilot keeps its
   fixed membership.

## Amendment 5 (2026-09-27, post-freeze): duplicate works in the sample

Two pairs of sample entries are the same underlying paper in two versions
(arXiv preprint + published version):

- positions 335 (arxiv:1612.00571) and 479 (doi:10.1080/02331888.2020.1722670)
  — "Reliability study of series and parallel systems ... proportional odds"
- positions 59 (doi:10.2991/jsta.2018.17.3.8) and 244 (arxiv:1704.03656)
  — "f-majorization ... extreme order statistics"

The frozen 100-paper sample is unchanged (positions and hashes stand).
For every headline statistic each pair counts as ONE unit: the canonical
claim set is the union of both versions' adjudicated records, with the
published version's text preferred where they differ. Extraction across
both versions still counts toward pass-agreement evidence (it is a
within-sample robustness check, not two papers). This yields a headline
denominator of 98 distinct papers. Report rates both ways.
