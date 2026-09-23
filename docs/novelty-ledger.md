# Novelty ledger

Last audited 23 September 2026. This records claim scope and source coverage,
not a certificate that no equivalent result exists. Proofs are in the
[ordered-survival note](ordered-survival-discovery.md) and the
[rank-selection and groups note](rank-selection-and-triples.md),
[all-horizon group proof](intact-groups-all-horizons.md), and
[two-threshold certificate](two-threshold-certificate.md).

| Claim | Status within this lab | Priority assessment |
|---|---|---|
| Exponential representation and pair-inclusion integrals | Used and reproduced | Established prior art; no novelty claim |
| Four-point chain for second-order successive-sampling inclusion | Proved at every fixed size | Exact chain not located; priority unresolved |
| General clock gap identity and reversed-hazard sufficient condition | Proved; weaker assumptions have exact counterexamples | Candidate extension; broader stochastic-order comparison needed |
| Adjacent/extreme optimal pairing once the chain is available | Proved | Standard exchange consequence |
| Consecutive equal groups maximize intact count at every survivor horizon | Proved using a positive outside-failure integral; ordinary-hazard extension | General assembly/supermodular sorting is established prior art; priority of the random-rank application unresolved |
| Universal quartet inequalities reduce exactly to two background thresholds | Proved; two backgrounds are necessary in general | Specific characterization not located; conditioning is standard and priority remains unresolved |
| Exact histogram certificate in linear rational-arithmetic work | Implemented and independently checked, including rational counterexample witnesses | Specific certificate not located; quadratic minimization is standard |
| Universal quartet outside both ordinary- and reversed-hazard orders | Exact five-bin example | Demonstrates that the sufficient hazard assumptions are unnecessary; no separate priority claim |
| Strong NP-completeness of majority triples after two successive failures, with nearly equal rates | Proved with finite error and rounded threshold | Candidate restriction; generic reliability hardness is known |
| Quadratic near-uniform regret bound | Proved | Elementary range/variance consequence |
| Small-model advantage or token-efficient theorem origination | Not established | Previous Qwen pilot is negative; investigator costs are separate |

## Primary sources and actual reading depth

**Kochar and Korwar (2001), On Random Sampling Without Replacement from a Finite
Population.** [Official full PDF](https://www.ism.ac.jp/editsec/aism/pdf/053_3_0631.pdf),
[DOI](https://doi.org/10.1023/A:1014693702392). The 16-page scan was obtained,
rendered and OCRed; theorem pages 633–634 and references were checked visually.
Theorem 2.1 compares equal-size unordered samples differing in one unit.
Corollary 2.2 compares second-order inclusions sharing an endpoint. Theorem 2.2
gives an ordered-sample arrangement comparison. These are close precedents.
The public verifier supplies a dependent countermodel proving that endpoint
and rank-transposition monotonicity alone do not imply the four-point law.
This does not exclude a stronger independence-based prior theorem or another
property specific to successive sampling.

**Rudys (2012), Inclusion probabilities for successive sampling.**
[Full six-page workshop paper](https://www.statistikuasociacija.lv/workshop2012/papers/W2012_CP_RUDYS_TOMAS.pdf).
Full extracted text read. Equation 7 supplies second-order order-sampling
inclusion integrals. This is representation precedent.

**Rosén (1998), On inclusion probabilities for order sampling, R&D Report
1998:2.** [Official Statistics Sweden full report](https://www.scb.se/contentassets/14f5e346f4814dd0acd52d10b23286c6/rnd-report-1998-02-green.pdf).
The definition and roadmap, theorem statements and surrounding explanations
in §§2–4, and §5's exact-formula discussion were read. The extracted text
omits several displayed equations, so this was not a full visual formula
audit. The inspected results concern first-order approximation errors,
asymptotic relative inclusion probabilities, and first-order exact formulas.
No quartet comparison was identified in those sections. This is the 1998
report; equivalence to later published versions was not assumed.

**Ng and Donadio (2006), Computing inclusion probabilities for order sampling.**
[Publisher/DOI](https://doi.org/10.1016/j.jspi.2005.03.010).
Abstract and accessible preview read; full paper unread. It treats computation
of first- and second-order inclusion probabilities under order sampling. A full
comparison with its formulas and identities remains outstanding. Its
[OpenAlex record](https://openalex.org/W2048491060) was also checked for public
copies and supplied no open PDF; that metadata is not proof that none exists.

**Boland, Proschan and Tong (1989), Optimal arrangement of components via
pairwise rearrangements.**
[Publisher/DOI](https://doi.org/10.1002/1520-6750(198912)36:6%3C807::AID-NAV3220360606%3E3.0.CO;2-I).
The [full 1987 technical-report precursor, ADA187633](https://archive.org/download/DTIC_ADA187633/DTIC_ADA187633.pdf)
was retrieved and its text read; Definition 2 and Theorem 1/proof on printed
pages 3–4 were checked against rendered scans. Theorem 1 characterizes a
uniformly beneficial component swap through node criticality for a fixed
coherent structure with **independent binary component states**. This is
established method precedent. Nondegenerate fixed-size rank-membership
indicators do not meet that independence assumption: their sum is constant,
whereas independent nondegenerate Bernoulli indicators have positive total
variance. Thus direct substitution is invalid. An indirect reduction or
later extension is still possible. The published 1989 version was not assumed
identical to the report.

**Derman, Lieberman and Ross (1972), On optimal assembly of systems.**
The [full 1971 Stanford report, AD0737618](https://archive.org/download/DTIC_AD0737618/DTIC_AD0737618.pdf)
was retrieved. Theorem 1, its proof and priority footnote, and Theorem 2's
assembly application were read; Theorem 1 and the footnote on printed page 4
were checked against the rendered scan. It maximizes the sum of a common joint-CDF
reliability function by aligned component ranks. The footnote identifies its
assignment inequality as a rediscovery of a special case of Lorentz's work.
This explicitly rules out novelty for the general CDF assembly principle.

**El-Neweihi, Proschan and Sethuraman (1987), Optimal assembly of systems
using Schur functions and majorization.**
The [full 1986 report, ADA177151](https://archive.org/download/DTIC_ADA177151/DTIC_ADA177151.pdf)
was retrieved and §§2–4 read; the hypotheses and Theorem 4.1 on printed pages
12–13 were visually checked. Theorem 2.1 and Remark 2.2 give consecutive
series-system assembly and maximal expected working-system count. Section 3
extends this across deterministic mission times. Theorem 4.1 uses a monotone,
lattice-supermodular common reliability function, the same general exchange
principle used here. Our positive outside-failure integral supplies an extra
step for the dependent **component-rank** cutoff; deterministic-time
optimality alone does not justify evaluating at that cutoff. The inspected
statements do not directly supply that step. This is a specific hypothesis
comparison, not proof that no published result supplies it.

**Belzunce, Ortega, Pellerey and Ruiz (2005), On ranking and top choice orderings
for random utility models with dependent utilities.**
[Institutional preprint](https://cio.umh.es/files/2011/12/CIO_2005_15.pdf).
The extracted introduction, definitions and theorem 3.10/proof were inspected.
They concern alternative preference and ranking comparisons under stochastic
orders. They reinforce the need to compare against general random-utility
theory, not only graph or failure terminology. This audit does not establish
a reduction of the four-point chain from those results.

**Ng, Barketau, Cheng and Kovalyov (2010), “Product Partition” and related
problems of scheduling and systems reliability: Computational complexity and
approximation.** [Publisher/DOI](https://doi.org/10.1016/j.ejor.2010.05.034),
[author-university record](https://research.polyu.edu.hk/en/publications/product-partition-and-related-problems-of-scheduling-and-systems-/).
Primary abstract and metadata read. It already gives strong hardness for
Product Partition variants and a series–parallel reliability-design problem.
Further bounded DOI, author-repository, bibliographic-API and exact-objective
searches did not retrieve full text; a university issue-contents PDF was not
the article. The actual reliability
model has therefore not been compared theorem by theorem. Its abstract cannot
justify claiming either direct subsumption or a proved distinction from every
restriction in the majority-triple result.

**Garey and Johnson (1975), Complexity Results for Multiprocessor Scheduling
under Resource Constraints.** [Primary record/DOI](https://doi.org/10.1137/0204035).
Metadata and abstract checked; full paper not retrieved. Restricted strong
3-PARTITION is the standard source problem used by the reduction. Neither that
problem nor the quadratic balanced-partition mechanism is claimed as new.

## What would change the assessment

A matching prior theorem would downgrade the relevant claim to an independent
derivation or application. An exact reduction from a broader published theorem
would do the same, even if its wording and application domain differ. The
full-report comparisons above close several earlier abstract-only gaps and
explicitly assign the rearrangement method to prior art. Full Ng–Donadio and
Ng et al. comparisons remain outstanding, as do later versions/extensions of
the retrieved reports and a specialist review of the exact random-rank
representation and two-threshold characterization. These gaps qualify
priority claims; they do not invalidate the proofs or executable examples.

Searches were bounded and exploratory across sampling, reversed-hazard order,
arrangement, component assignment, quadratic partition, rank-selection
four-point comparisons, and inclusion-matrix/Monge terminology. No
claim of exhaustive indexing, peer review, or author confirmation is made.
No authors were contacted and no paywall was bypassed.
