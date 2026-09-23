# Novelty ledger

Last audited 23 September 2026. This records claim scope and source coverage,
not a certificate that no equivalent result exists. Proofs are in the
[ordered-survival note](ordered-survival-discovery.md), the
[rank-selection and groups note](rank-selection-and-triples.md),
[all-horizon group proof](intact-groups-all-horizons.md),
[stochastic-order group theorem](stochastic-intact-groups.md),
[three-triple extension](block-separated-triples.md),
[CDF robustness](robust-stochastic-groups.md),
[two-threshold certificate](two-threshold-certificate.md),
[context reduction and ordered sharpness](rank-context-compression.md), and
[minimal rank contexts](minimal-rank-contexts.md).

| Claim | Status within this lab | Priority assessment |
|---|---|---|
| Exponential representation and pair-inclusion integrals | Used and reproduced | Established prior art; no novelty claim |
| Four-point chain for second-order successive-sampling inclusion | Proved at every fixed size | Exact chain not located; priority unresolved |
| General clock gap identity and reversed-hazard sufficient condition | Proved; stochastic order alone can fail the crossing-versus-nested comparison | Candidate extension; broader stochastic-order comparison needed |
| Adjacent/extreme optimal pairing once the chain is available | Proved | Standard exchange consequence |
| Consecutive equal groups stochastically maximize intact count at every survivor horizon | Proved for independent atomless clocks under ordinary stochastic order; arbitrary independent background vector allowed; atoms permitted with uniform or aligned ties | General assembly/supermodular sorting is established prior art; priority of the FOSD random-rank application unresolved |
| Cut-separated quartet comparison remains valid with nonnegative outside selection factors | Proved by a positive integral and conditional rank counting; gives the all-size grouping theorem by product factorization | Precise rank-cutoff implication not located; conditioning and telescoping are established methods |
| Three target triples need only between-group CDF order | Exact finite proof covers all 280 partitions, all Boolean selection states and all count tails, with arbitrary independent backgrounds | Scope extension; precise priority unresolved; nonnegative-cone certificates are an established technique |
| CDF perturbations bound the entire intact-count tail vector and grouping regret | Proved with sharp linear constants 1 for stability and 2 for transfer regret | Elementary stability argument; no separate novelty claim |
| Midpoint CDF projection supplies an approximation certificate when CDFs cross | Implemented using exact rational errors and fixed-order minimax radius | Projection is precisely the established Basic L∞ isotonic regression; no regression-algorithm novelty claim |
| Universal quartet inequalities reduce exactly to two background thresholds | Proved even with dependence within the quartet | Specific characterization not located; conditioning is standard and priority remains unresolved |
| Two backgrounds are necessary even under strict stochastic ordering and positive densities | Exact seven-bin examples and a general positive/negative/positive block construction | Stronger sharpness result; exact prior-art comparison remains open |
| Any reward supported on one focal cardinality reduces pathwise to two backgrounds | Proved without distributional assumptions; universal-expectation corollary permits dependent focal scores | Elementary rank-counting method; no priority claim for the general technique |
| Minimum deterministic context preserving any fixed set reward is the span of its feasible active ranks | Proved; exhaustive Boolean-reward comparison; harmonic consequences use lowest nonconstant degree | Exact formulation not located; rank trimming and harmonic algebra are established ingredients |
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
Full extracted text read. Section 4, equation (6), gives the general
second-order inclusion integral for independent order sampling; equation (7)
specializes it to exponential scores. This is representation precedent.

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
Further bounded searches of author, Melbourne/ABS and thesis routes did
not recover the original. Its accuracy-check identities remain unread;
they must not be assumed to be just the familiar fixed-sample-size identities.

**Matei (2005), Computational aspects of sample surveys.**
The [complete Neuchâtel dissertation](https://libra.unine.ch/server/api/core/bitstreams/93669154-3cd3-4ce4-8a12-48765e2e27f2/content)
was recovered. Sections 1.3.1 and 2.2, the Chapter 2 introduction and the
bibliography were inspected. Equation (2.2) expresses first inclusion using
an outside order statistic; equation (2.3), credited to Cao–West (1997),
recursively evaluates a nonidentical independent order statistic's CDF.
The thesis cites the forthcoming Ng–Donadio paper as another method but
does not reproduce its algorithm. Its coordinated-sample joint probability
concerns one unit on two occasions, rather than two units in one sample.
This is additional method precedent, not clearance of the unread original.

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
At a deterministic mission time, the four-component product specialization
gives the nonnegative CDF product `D`. The new positive integral establishes
an additional term needed for a cutoff chosen by the same scores' ranks.
The report's §3, Theorem 4 (printed page 10, checked visually), already gives
a stochastic comparison of functioning
module counts in its static series-assembly setting. Distributional rather
than merely mean optimality is therefore also established method precedent.

**El-Neweihi, Proschan and Sethuraman (1987), Optimal assembly of systems
using Schur functions and majorization.**
The [full 1986 report, ADA177151](https://archive.org/download/DTIC_ADA177151/DTIC_ADA177151.pdf)
was retrieved and §§2–4 read; the hypotheses and Theorem 4.1 on printed pages
12–13 were visually checked. Theorem 2.1 and Remark 2.2 give consecutive
series-system assembly and maximal expected working-system count. Section 3
extends this across deterministic mission times. Theorem 4.1 uses a monotone,
lattice-supermodular common reliability function, the same general exchange
principle used here. Our earlier outside-failure integral supplies an extra
step for the dependent **component-rank** cutoff under hazard order. The new
quartet integral and outside-factor lift supply that step under ordinary
stochastic order alone. Deterministic-time optimality does not by itself
justify evaluating at a cutoff chosen by the components' ranks. The inspected
statements do not directly supply either step. This is a specific hypothesis
comparison, not proof that no published result supplies it.

**Hwang and Rothblum (2006), A Polytope Approach to the Optimal Assembly
Problem.** [University full PDF](https://ir.lib.nycu.edu.tw/server/api/core/bitstreams/0c781947-b25a-4b0a-b436-814780b5c44d/content),
[DOI](https://doi.org/10.1007/s10898-005-3844-2).
Sections 1–2, Lemmas 4.1–4.2, Theorems 4.3–4.4 and 5.1, and §6 were
read; printed pages 388 and 394 were checked visually. Theorem 4.4 gives
monotone optimal assembly for series modules and prescribed part counts;
Theorem 5.1 allows size bounds. This is stronger general assembly precedent.
The reliability model explicitly assumes independent operative states and
uses product module and system probabilities in (1.2)–(1.3). Fixed-size
rank membership does not meet that assumption. Section 6's abstract extension
requires an asymmetric Schur-convex objective of module sums; a reduction of
the arbitrary-FOSD rank problem to that representation has not been supplied.
These observations rule out direct substitution, not every indirect reduction.

**D'Abadie and Proschan (1983), Stochastic Rearrangement Inequalities.**
The [full September 1983 FSU report M672 / AFOSR 83-167](https://archive.org/download/DTIC_ADA150573/DTIC_ADA150573.pdf)
was recovered. Definitions 3.1/3.3, Theorem 4.2, equation (4.4),
Theorems 4.29/5.1 and Example 5.2 were inspected, including rendered scans.
The report gives genuine stochastic-order rearrangement results and
preservation by rank transformations. Its relevant premises concern
conditional arrangement laws (AI, PSA or AP), stronger than marginal FOSD.
Our continuous three-bin laws `W=(2,4,9)/15`, `S=(1,5,9)/15` satisfy
`F_S≤F_W`, but conditional aligned order has probability `4/9<5/9`
when ordered observations lie in bins 1 and 2. Two independent copies,
conditioned in bins 0/1 and 1/2, give PSA mixed difference `−1/21`.
The [exact verifier](../research/spikes/stochastic/scope_witnesses.py)
checks both. These refute the natural conditional-kernel premises under
FOSD; they do not exclude every auxiliary AP representation. The assembly
example has two stockpiles and no common survivor-count cutoff. The report
was not assumed identical to the 1984 chapter or the unread 1987 final article.

**Marichal, Mathonet and Spizzichino (2015), On modular decompositions of
system signatures.** The [2014 arXiv v2 primary text](https://arxiv.org/html/1208.5658v2)
was inspected: equations (13), (16), (17), Definition 8, Theorems 9/12,
Examples 14–16 and §4.2. Our fixed-rank count tails are probability-signature
tails for threshold combinations of series modules; that representation is
established. Their general modular formula requires a factorization of
the relative-quality law `q(A)`. Independent FOSD does not imply it:
two-bin rows `(1,4),(2,3),(3,2),(4,1)` give, for partition `ab/cd`,
incompatible values `88/135` and `5/9` for the same occupancy coefficient
`c(1,1)`. The [verifier](../research/spikes/stochastic/scope_witnesses.py)
computes the complete subset law independently. Theorem 12 quantifies over
every semicoherent module choice; failure of its premise does not prevent
a special series-module occupancy representation. That representation
still needs an inequality comparing the different occupancy laws induced
by different partitions. The inspected theorems do not supply that comparison.
This is a scoped distinction, not literature-priority clearance.

**Stout (2018), Weighted L∞ isotonic regression.**
[Author-hosted paper](https://web.eecs.umich.edu/~qstout/pap/LinfinityIsoReg.pdf),
[DOI](https://doi.org/10.1016/j.jcss.2017.09.001).
Section 2.1.1 was read in indexed primary text; direct full-PDF retrieval
timed out. Its unweighted Basic formula is exactly the midpoint of a prefix
maximum and suffix minimum used in our [CDF approximation](robust-stochastic-groups.md).
It records earlier work on this regression. We credit the projection and
its minimax objective to prior art; this application combines it with a
separate rank-count stability proof.

**Li and You (2015), Permutation Monotone Functions of Random Vectors with
Applications in Financial and Actuarial Risk Management.**
[Official full PDF](https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/4261A1C17437AC957A015E36CAE29454/S0001867800007801a.pdf/permutation_monotone_functions_of_random_vectors_with_applications_in_financial_and_actuarial_risk_management.pdf),
[DOI](https://doi.org/10.1239/aap/1427814591).
Definition 2.2, Theorems 3.1–3.3, Corollaries 3.2 and 3.4, and relevant
appendices were inspected. Their density/tail permutation premises or
hazard-order specializations do not follow from a heterogeneous independent
FOSD chain. Our strict three-bin example has `f_a/f_b=1/10,9,20/19` across
its bins, violating likelihood-ratio order. At `t=3/2`, ordinary hazards
`h_a=18/49>2/39=h_b` and reversed hazards `r_c=2/39<18/49=r_d`
also violate the corresponding ordered hypotheses. The respective tail
density differences have the wrong sign. This excludes direct use of those
full-chain premises for the entire admitted class, not a specialized reduction
through other rearrangement machinery.

**Khaledi and Kochar (2000), Stochastic Comparisons and Dependence among
Concomitants of Order Statistics.**
[Author-hosted full paper](https://web.pdx.edu/~kochar/Papers/d_papers/jmva2000.pdf).
Theorems 3.1, 3.3 and 4.2 were inspected. They concern the second coordinates
of independent identically distributed bivariate observations, reordered by
their first coordinates. Label-specific inclusion indicators of heterogeneous
scores are different objects. Even with four identical continuous scores and
top-two selection, two distinct inclusion indicators have covariance `−1/12`;
the association conclusion for concomitants cannot be substituted here.

**Later stock-grouping comparisons (2017 and 2023).**
[Hazra, Finkelstein and Cha (2017)](https://doi.org/10.1016/j.jmva.2017.06.006),
§2 and Lemma 4, were read in indexed primary text; complete text and some
later formulas remained unavailable.
[Balakrishnan et al. (2023)](https://doi.org/10.3390/math11173718),
§3 and Theorems 1 and 4, were read in a public reproduction of the paper
with fragmented mathematical typography; its upload provenance was not
independently verified. These models vary how many components share a
randomly chosen stock, or the stock-selection probabilities. They change
the joint sampling law. The inspected formulas have no decision variable
for partitioning a fixed list of heterogeneous labels under common rank
selection. Equal group sizes give the same formula input for every such
partition. This is a model comparison, with the access limitations retained.

**Belzunce, Ortega, Pellerey and Ruiz (2005), On ranking and top choice orderings
for random utility models with dependent utilities.**
[Institutional preprint](https://cio.umh.es/files/2011/12/CIO_2005_15.pdf).
Definitions 2.2–2.8, Theorems 3.10, 3.12, 3.13, Corollary 3.14 and their
proofs were read. They give alternative/subset preferences and improving-rank
transposition comparisons through joint stochastic or likelihood-ratio
orders. In particular, the proof of Theorem 3.10, printed page 6, compares
individual top-`t` sets: `P_t(A∪{j})≥P_t(A∪{k})` for every common
`(t−1)`-subset `A`, under conditional joint stochastic order (3.8).
Independent FOSD satisfies that premise. This is stronger than marginal
top-size membership order and is explicitly credited here.
Theorem 3.12 identifies the relevant likelihood-ratio condition
with an arrangement-increasing (AI) joint density. The existing dependent
countermodel also meets that density premise: on each order cone of the unit
cube give density `24` times its order probability. Those probabilities pass
all 72 improving transpositions and all 24 improving same-size subset swaps
at top sizes one, two and three, but give an adjacent pair sum `3/11` below
the crossing sum `4/11`. The [exact verifier](../research/spikes/rank/verify.py)
constructs each top-size law from all 24 full rankings. Thus the broad AI premise
alone does not imply the target additive quartet comparison. This distinguishes the inspected result;
it does not exclude a stronger theorem using independence. The inspected
source is the 2005 preprint, not an assumed identical 2007 final version.

**Joe (2000; 2002), independent random-utility inequalities and orders.**
The [2000 publisher abstract](https://link.springer.com/article/10.1023/A:1010058117460)
describes inequalities proved through association, with equality conditions.
Its PDF route returns a subscription preview. The
[2002 DOI](https://doi.org/10.1016/S0165-4896(02)00018-5) and publisher routes
did not supply theorem text; the author-university bibliography lists the DOI
without a manuscript. Neither original was read in full. Belzunce's equations
(1.2)–(1.3) and Definition 2.2 restate a Joe implication from independent
FOSD order to ordered marginal top-size membership probabilities. An independent
categorical calculation confirms that the strict seven-bin example has those
ordered marginals while its second quartet gap is `−5/410758`. This refutes
deduction from that specific weaker conclusion. It does not clear unread
Joe theorems; the fixture also does not satisfy likelihood-ratio order.
The stronger subset-swap conclusion in Belzunce's proof is now checked
separately above; even that conclusion alone does not give the first quartet
gap. The dependent counterlaw does not rule out an implication from additional
independence assumptions. Inspection of the UBC technical-report archive
entries 154–213 (1995–2005) recovered neither original. No inference of
priority is drawn from that bounded search.

**Regenwetter, Marley and Joe (1998), Random Utility Threshold Models of
Subset Choice.**
[Author-uploaded full paper](https://www.researchgate.net/profile/A-A-J-Marley/publication/233046765_Random_Utility_Threshold_Models_of_Subset_Choice/links/58a8910092851cf0e3bfa7b3/Random-Utility-Threshold-Models-of-Subset-Choice.pdf),
[DOI](https://doi.org/10.1080/00049539808258794).
Theorem 1(ii), Theorem 2 and Appendix Examples 4–5 were read in the extracted
text. Some displays were missing and screenshot retrieval failed, so the
formula audit is incomplete. The top-size/random-threshold representation
uses a threshold that may depend on the utilities. Example 5 obstructs an
independent common-threshold representation. These are direct precedents;
neither is the same operation as retaining top ranks with two independent
outsiders. The inspected statements do not give the marginal-concatenation
construction that hides a violation from every one-background test.

**Cohen and Kaplan (2008), Tighter Estimation using Bottom-k Sketches.**
[Conference full paper](https://www.vldb.org/pvldb/vol1/1453884.pdf).
Section 5 and Appendix B, Lemma B.1, were inspected. They condition on
outside order statistics for single-item and pair inclusion, with a stated
subset-product extension. This is direct precedent for rank conditioning.
Their event is inclusion of a fixed subset; ours requires exactly a specified
number of focal labels and retains their identity. The two adjacent outside
boundaries follow by a short extension of that familiar idea. The inspected
lemma does not state the universal two-background equivalence or the ordered
zero/one-versus-two separation. Conditioning itself is not a novelty claim.

**Filmus and Mossel, Harmonicity and Invariance on Slices of the Boolean Cube.**
[Author full version, 21 December 2018](https://yuvalfilmus.cs.technion.ac.il/Papers/2slice.pdf).
Definitions 3.1–3.2, Theorem 3.6 and Lemma 3.7 were inspected. Zero row sums
of a homogeneous quadratic are precisely harmonicity; the quartet rewards
factor into disjoint coordinate differences. This is established algebra,
with earlier representation work credited to Dunkl. The new context notes
use it rather than claim a new harmonic representation. The inspected slice
statements do not themselves replace a background ranking population.

**Bairamov and Eryilmaz (2008), Joint Behaviour of Precedences and Exceedances
in Random Threshold Models.**
[Author-hosted full paper](https://dm.ieu.edu.tr/Ism/anzj.pdf),
[DOI](https://doi.org/10.1111/j.1467-842X.2008.00512.x).
Theorem 1 on printed pages 210–211 and §3 were inspected. They give a joint
count law relative to two random thresholds, including thresholds that are
order statistics of another sample. This is explicit two-threshold precedent.
The focal sample is independent and identically distributed; the formula
does not retain a nonidentical labeled top subset or construct a failure
hidden from every one-background test. Under identical focal laws the
quartet gaps vanish by symmetry. This is a hypothesis comparison, not a
claim that all random-threshold literature has been cleared.

**Kalmanson (1975), Edgeconvex Circuits and the Traveling Salesman Problem.**
[Full primary article](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/S0008414X00016291).
The four-point statements on printed pages 1000–1001 were inspected. The
sign-reversed quartet chain is the Supnick chain, credited there to Supnick
(1957); the original 1957 paper was not read. More concretely, rank-membership
indicators define a disagreement pseudometric
`d_ij=P(I_i≠I_j)=q_i+q_j−2q_ij`. Marginal terms cancel in quartet sums,
so our chain for `q` becomes the established Supnick chain for `d`. Its
matrix structure and exchange consequences are prior art; establishing that
a particular sampling law has that structure is the probability question.

**Ng, Barketau, Cheng and Kovalyov (2010), “Product Partition” and related
problems of scheduling and systems reliability: Computational complexity and
approximation.** [Publisher/DOI](https://doi.org/10.1016/j.ejor.2010.05.034),
[author-university record](https://research.polyu.edu.hk/en/publications/product-partition-and-related-problems-of-scheduling-and-systems-/).
Primary abstract and metadata read. It already gives strong hardness for
Product Partition variants and a series–parallel reliability-design problem.
Further bounded DOI, author-repository, bibliographic-API and exact-objective
searches did not retrieve full text; a university issue-contents PDF was not
the article. Following the official repository handle
[10397/29613](https://hdl.handle.net/10397/29613) returned a withdrawn-item
notice, not the paper. The actual reliability
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
explicitly assign the rearrangement method to prior art. Full Ng–Donadio,
Ng et al. and Joe comparisons remain outstanding. A particularly close
unread final version is [Chan, D'Abadie and Proschan (1987), Stochastic rearrangement
inequalities](https://doi.org/10.1016/0047-259X(87)90156-4): its abstract
explicitly includes ranking and optimal assembly, but full primary text was
not obtained. The inspected 1983 report closes the earlier precursor gap;
equivalence to the final text has not been established. There are also later versions/extensions of
the retrieved reports and a specialist review of the exact random-rank
representation and two-threshold characterization. These gaps qualify
priority claims; they do not invalidate the proofs or executable examples.

Two current candidates warrant the closest comparison. The uniform block
construction
preserves independent, CDF-ordered marginals while hiding any eligible
negative no-background gap from all zero/one-background tests, yet exposing
it with two backgrounds. None of the inspected rank-conditioning, harmonic,
AI-ranking or random-threshold theorems supplies that closure statement.
That is a specific non-subsumption assessment, not a certificate of absence
from the wider literature. The strict positive-density example removes
degenerate ordering as an explanation for the separation.

The all-size intact-group theorem now assumes only independent atomless
clocks in ordinary stochastic order. Its positive quartet integral remains
valid with a nonnegative function of the other selected labels, which is the
bridge to larger group exchanges. The inspected deterministic-time assembly
theorems do not directly supply this rank-cutoff bridge. Full comparison
against broader stochastic rearrangement and allocation results remains
necessary before describing this theorem as literature-first. The two
candidates are compatible: the hidden ordered violation concerns the second
quartet gap, whereas intact-group optimality uses the first.

Searches were bounded and exploratory across sampling, reversed-hazard order,
arrangement, component assignment, quadratic partition, rank-selection
four-point comparisons, and inclusion-matrix/Monge terminology. No
claim of exhaustive indexing, peer review, or author confirmation is made.
No authors were contacted and no paywall was bypassed.
