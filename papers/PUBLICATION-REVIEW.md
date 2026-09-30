# Publication review, 28 September 2026

Reviewer: Codex agent `/root/papers`; source and copy review, with computational and PDF checks recorded below. This is an agent review, not human peer review. Author identity was already present in all five source files. Prior referee reports are retained as historical agent-review documents; this note supersedes their stale author-placeholder and unmerged-branch entries.

Owner: Benjamin Guo / Hraness. Evidence check date: 2026-09-28. Reassess: 2026-11-09, or earlier when a cited source or exclusion proof becomes available. No journal submission or acceptance is asserted.

## Softmax thresholds

Reader job: choose a temperature range preserving majorization on a box or fixed-total simplex. The original contribution is the dimension-dependent constants, strict boundary behavior and exact crossover; the generic non-monotonicity observation is credited to earlier Esscher work. The repository owns the proofs and executable rational certificates. Closest papers are Boltzmann purity (optimization of an allocation matrix), hazard mixtures (rates under parameter majorization), and the mixture audit (source-specific counterexamples). This paper owns a distinct domain/temperature classification and should remain separate.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. The partial literature search prevents a priority claim; this is explicit. Agent assistance is visibly disclosed. The ICLR venue claim was removed because the local source records did not consistently establish it; the versioned preprint is cited instead. No invented personal experience appears.

## Boltzmann purity

Reader job: determine when an optimal nested Boltzmann allocation is pure, and how temperature changes the optimal occupancy pattern. The repository owns the structural proofs and independent symbolic/numerical checks. Its closest overlap is the softmax paper's scalar mean; that paper does not classify allocation optima. The hazard paper and cluster audit concern a different probabilistic model. This manuscript has an independent theorem and reader task, so remains separate.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. Claims of first priority remain qualified; some related sources were unavailable. Numerical grid maxima are explicitly checks, not proofs. The AI disclosure now distinguishes script checks from formal proof verification.

## Hazard mixtures

Reader job: determine which hazard-order conclusions survive majorization and construct exact crossing examples. The manuscript owns equal-weight constructions, crossing analysis and small certified witnesses. The cluster audit uses one such mechanism across published statements; it does not replace this self-contained mathematical treatment. The softmax and purity papers share exponential weights but answer different questions. Retain the paper and use one companion reference for the audit.

Proof checking is described as mathematical and computational agent review, not formal certification or human review. Exact script provenance is retained.

## Mixture claim audit

Reader job: identify the precise hypothesis and algebraic step behind a claimed mixture-rate ordering before using it. Its contribution is a source-indexed collection of explicit rational counterexamples, a correct additive-lift argument, and distinguished source-access levels. The companion hazard paper owns the general equal-weight mechanism; the audit owns the cross-paper statement and script map. The softmax and purity papers concern different target models. Retain as an audit with calibrated attributions.

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. Unavailable original texts prevent direct attribution of reconstructed claims. This review removes suggestions of fabrication, institutional blame and an inferred original-proof defect. SPBB's parameter-monotonicity hypothesis forces a parameter-independent distortion family; it does not force D(u)=u. The PHR crossing witnesses omit that hypothesis and are explicitly not counterexamples to the literal theorem. The rational, Sturm, interval and numerical evidence classes are separated. Previously gitignored BKF and additive-lemma scripts are now portable manuscript supplements.

## Small-grid enumeration

Reader job: distinguish certified constructions and recorded refutations from candidate exact values in a finite extremal search. The repository owns coordinates, enumerator sources and solver/checker records. The other four manuscripts do not study integer-grid geometry. This paper's independent output is a corrected reproducibility and evidence audit, so it remains useful even without claiming an independently certified C(6).

Admission: utility 2, original evidence 2, factual confidence 1, host fit 2, voice integrity 1, maintenance 2 = 10/12. C(3)=8 and C(4)=11 rely on existing recorded independent LRAT checking; their full proof files were not rerun here. Fresh integer checks cover all four lower-bound constructions and both larger orbit inventories. C(5)=14 and C(6)=18 are candidate exact values supported by completed corrected single-implementation searches. Attempted independent runs were invalidated by implementation defects; no independent larger exclusion is claimed. The false fitted formula, priority claim, layer predicate, table-memory estimates, entrywise-selftest claim and node counts were corrected.

## Validation

Completed on 28 September 2026. Python checks used CPython 3.12.14, SymPy 1.14.0 and mpmath 1.3.0; the Boltzmann numerical checks used NumPy 2.5.3. `python` below denotes that interpreter. These checks corroborate the stated calculations; they are not machine-checked proofs of every theorem.

| Manuscript | Fresh validation | Result |
| --- | --- | --- |
| Softmax thresholds | `python verify/identities.py`, `python verify/roots.py`, `python verify/counterexamples.py`, `python verify/violations.py`, from the paper directory | All completed successfully; exact identities, root certificates and the stated boundary counterexamples passed. |
| Boltzmann purity | `python verify/identities.py`, `python verify/occupancy.py`, `python verify/negative_outer.py`, `python verify/additive_boundary.py`, from the paper directory | All completed successfully; the numerical scripts reported `FAILURES: none`. The separate historical brute-force program was not rerun. |
| Hazard mixtures | `python verify/verify_core.py`, `python verify/verify_general_mechanism.py`, `python verify/verify_strict_variant.py`, `python verify/verify_two_crossings.py`, `python verify/verify_reversed_hazard.py`, from the paper directory | 110 passed, 0 failed, across five programs. |
| Mixture claim audit | `python verify/bkf2024/sturm_cert.py` and `python verify/bhb2022/audit_bhb.py`, from the paper directory; review of the cited per-claim memos and retained certificates | The four whole-interval checks passed; additive identities, 731 admissible three-column instances, the nonseparability witness and the exact differential value 25/11 agreed. This does not claim a fresh rerun of every historical cluster search. |
| Small-grid enumeration | `python papers/no-five-exact/verify/check_small.py`, from repository root | All four configurations passed independent integer determinant checks; the two orbit inventories are 1,905 and 8,133. Completed production logs were counted and source hashes compared as recorded in `no-five-exact/REVIEW-NOTES.md`. No full upper-bound search was rerun by this reviewer. |

All five sources were copied with their bibliography and figure dependencies to a temporary build directory, built with `tectonic --only-cached --keep-logs main.tex`, and their PDFs rendered with Poppler. The final PDFs are installed beside their sources. Every page was visually inspected, including full-size checks of the audit's dense tables and the longest paper's final references. A stranded one-entry final page was removed from the Boltzmann paper; the audit's table spacing and bibliography pagination were corrected. No missing citations, undefined references or overfull boxes remain in the final build logs. A minor underfull box in the softmax bibliography has no visible layout defect.

| PDF | Pages | Agent disposition |
| --- | --- | --- |
| `softmax-thresholds/main.pdf` | 18 | Ready for publication as a research manuscript with the bounded novelty search stated. |
| `boltzmann-purity/main.pdf` | 24 | Ready for publication as a research manuscript with numerical and source-access limits stated. |
| `hazard-mixture/main.pdf` | 17 | Ready for publication as a research manuscript with computational checks and agent assistance disclosed. |
| `mixture-cluster-audit/main.pdf` | 12 | Ready for publication as a calibrated audit; unavailable originals remain a limit on attribution, not a hidden pending claim. |
| `no-five-exact/main.pdf` | 5 | Ready for publication as an evidence and reproducibility report; not as independent certification of C(5) or C(6). |

`git diff --check -- papers` passed. The integration owner owns the repository-wide final gate, independent integration review and publication delivery. No external submission, publication or human review was performed by this reviewer.

## Sparse weighted digits: update of 29 September 2026

Readers can construct integer sets with a small sumset and a large difference set, and reproduce a rigorous lower bound for the corresponding two-set exponent. The manuscript proves a general weighted-digit theorem, retains the simpler sparse-alphabet bound `theta > 1.1855`, and now gives a four-digit construction proving `theta > 1.18565`. The new weights are determined by the sum of the source digits; separate minimum-cost recurrences merge all colliding sums and differences. The accompanying certificate records both cost histograms and the exact integers in the strict inequality.

The theorem and exact certificate improve Zheng's stated lower bound. This is not an optimality or current-record claim; the literature comparison distinguishes the two-set exponent from the one-set ratio. Independent mathematical and source review was performed by a separate Codex agent. Agent assistance is disclosed; no human peer review or journal acceptance is asserted. The [28 September immutable release](https://github.com/hraness/algal-lab/releases/tag/sum-difference-bound-20260928) preserves the original manuscript and its verification files.

Fresh validation used CPython 3.14.6 and the standard library. Four control groups passed, including all endpoint pairs in 24 tiny block configurations, strict-inequality and malformed-input cases, and rejection of an altered full histogram before exponentiation. One complete certificate verification reconstructed both 129-entry histograms and their integer totals, then verified the exact comparison certifying `23713/20000 = 1.18565`. The original geometric verifier and its tests remain unchanged. These are finite certificate checks, not an optimality search.

From the repository root, the new checks are:

```sh
python3 -B -m unittest discover -s papers/sparse-sum-difference -p test_carry_verify.py -v
python3 -B papers/sparse-sum-difference/carry_verify.py
```

The revised source built with cached Tectonic 0.17.0 using `--only-cached --untrusted --keep-logs`; no warnings, undefined references or overfull or underfull boxes were reported. Poppler 26.08.0 metadata and text checks completed, all seven pages were rendered, and every page was visually inspected. The installed seven-page PDF has clear equations, complete code blocks and legible references. Disposition: ready for publication as a research manuscript with the stated literature and optimality limits. Repository-wide checks and verification of the published files are recorded with the release.

## Fivefold sumset counterexample: 29 September 2026

The three-page note gives integer sets with `|A-B|^5 > |A+B|^5 |5B|`. They are base-193 encodings of two nonnegative integer simplices in dimension 128, with coordinate sums at most 160 and 32. A 33-term binomial sum counts the difference set, and a second formula independently counts its positive and negative supports. The note credits the classical simplex construction in Gyarmati, Hennecart and Ruzsa's published 2007 paper. It addresses their stated fivefold inequality without asserting priority in the later literature.

A separate Codex agent reviewed the proof, both formulas, integer encoding, verification source and citation against the published paper; no issues were found. Agent assistance is disclosed in the manuscript. This review does not constitute human peer review or journal acceptance.

Fresh validation used CPython 3.14.6 and its standard library. Three control groups passed: four literal finite-set cases, input-limit rejection, and the fixed certificate. The verifier reproduced the three recorded integers using both formulas and confirmed the strict fifth-power inequality. From the repository root:

```sh
python3 -B -m unittest discover -s papers/fivefold-sumset -p 'test_verify.py' -v
python3 -B papers/fivefold-sumset/verify.py
```

The source built with cached Tectonic 0.17.0 using `--only-cached --untrusted --keep-logs`, without warnings or layout errors. Poppler 26.08.0 metadata and text checks passed. Every page was rendered and visually inspected; equations, code, citations and references are complete and legible. The PDF is ready for publication as a research note with its stated literature scope.

## Sumset literature follow-up: 29 September 2026

Glasscock's 2012 master's thesis, Lemma B.1, already contains the unequal-radius
count and negative-support proof used in the fivefold note. The revised note
credits that lemma and Hennecart, Robert and Yudin's 1999 simplex construction.
It presents the explicit parameters and strict integer comparison as its result.
The weighted-digit manuscript now identifies its sums of maximum products with
the max-convolution in Matolcsi, Ruzsa, Shakan and Zhelezov's analytic work.

The [literature comparison](sumset-literature.md) records the relevant theorems,
their hypotheses and their relation to both constructions. It includes the
entropy translation and distinguishes the 2026 mixed-alphabet and one-set
exponents. Several identified source texts remain unread, so priority and
current-record status remain unestablished.

A separate Codex agent checked the attribution changes against primary-source
statements and the original thesis pages. The revised PDFs contain three and
seven pages. Both built with cached, untrusted Tectonic without warnings,
undefined references or box errors; Poppler metadata and text checks passed.
Every revised page was visually inspected. The fivefold theorem and the program
with its introduction each stay on one page. The mathematical certificates and
verification programs are unchanged. The corrected PDFs and their exact sources
are released together, with fresh checks of the downloaded verification files.

## Fivefold finite companion proof: 29 September 2026

The note now includes a second construction with a complete finite proof. It
uses fixed-weight binary words in base 9 and proves the strict fivefold
comparison by type counting, generating polynomials, small rational
inequalities and the binomial theorem. Its dimension is 555,008; the original
dimension-128 simplex example remains the main result. The companion does not
claim a smaller construction or a fourfold result.

A separate Codex agent checked every counting bound, the rational comparisons,
the base-9 embedding and the methodological attributions. The proof credits
Lau and Nair's type-counting method and the max-convolution framework of
Matolcsi, Ruzsa, Shakan and Zhelezov. The earlier simplex attributions and the
limits on priority and current-status claims remain. This is mathematical
agent review, not human peer review or journal acceptance.

The four-page PDF built with cached Tectonic 0.17.0 using
`--only-cached --untrusted --keep-logs`, without warnings, unresolved references
or box errors. Poppler 26.08.0 metadata and text checks passed. All four pages
were rendered and visually inspected: the theorem statements, proof, code
block and references are complete and legible. The original certificate and
verification programs are unchanged. The note is ready for publication with
its stated literature scope; repository and downloaded-file checks accompany
the release.

## Sumset source-version review: 29 September 2026

The literature comparison now identifies the exact Zheng preprint and theorem,
uses Lau and Nair's current v3, and explains the later two-point
max-convolution theorem of Becker, Ivanisvili, Krachun and Madrid. Lau and
Nair's main equivalence theorem is unchanged; the comparison records the
incomplete extraction of the new appendix and the unread journal editions of
two other sources.

A separate Codex agent checked the literature changes against retained
primary texts, source-version audit records and later-paper bibliographies.
The review found no required corrections to this literature update. The PDFs
and verifiers are unchanged. The immutable
[v3 release](https://github.com/hraness/algal-lab/releases/tag/sum-difference-results-20260929-v3)
preserves that manuscript package. Priority and current-record status
remain unestablished.

## Fourfold inequality on three points: 29 September 2026

The new twelve-page manuscript proves a strict reflected max-convolution
inequality for every three-point integer support, arbitrary positive kernel
weights and every nonzero finitely supported nonnegative input. The proof
covers unequal gaps by classifying fourfold collisions, and progressions by
explicit scalar inequalities and potentials whose differences telescope.
Every weight case and the endpoint terms establishing strictness are included.
The general fourfold question remains unresolved here.

A separate Codex agent reviewed the complete proof, including the collision
list, scalar identities, all potential vertices, limiting weight cases and
the final exhaustive case split. The review found no mathematical defect;
two wording changes clarified the common support and simultaneous reflection.
The relevant primary-source citations were checked. This is mathematical
agent review, not human peer review or journal acceptance. Comparisons with
the identified weighted Prékopa–Leindler chapter and the later journal text
remain incomplete; no priority or optimality claim is made.

The source built with cached Tectonic 0.17.0 using
`--only-cached --untrusted --keep-logs`, without warnings, undefined references
or overfull or underfull boxes. Poppler 26.08.0 metadata and text checks passed.
Every page was rendered and visually inspected. The bibliography was tightened
to eliminate an isolated final-reference page; all twelve final pages contain
complete, legible text, equations and tables. The manuscript is ready for
publication with the stated scope. Repository and downloaded-file checks
accompany the release.

The shared literature comparison also records the checked AlphaEvolve survey
version, the distinct projection-entropy problem in Tao's later paper, and
the remaining source-version and access gaps. The two construction papers
and their verification programs are unchanged.

## Small-support reflected inequalities: 29 September 2026

The new 37-page manuscript proves the reflected fourfold max-convolution
inequality for arbitrary nonnegative kernels on at most four integers and
constant kernels on every five-point integer support. Both results allow
arbitrary nonzero finitely supported nonnegative inputs and arbitrary
nonzero nonnegative denominator weights. The inequality is strict for
positive four-point kernels and positive constant five-point kernels.

The four-point proof identifies a universal translated-covering constant
with an ordinary-autoconvolution optimization, classifies all five
pair-sum collision patterns, and proves their sharp unweighted constants.
The proper-parallelogram constant is `25/16`; the arithmetic-progression
constant is `3/2`. The stronger covering inequality fails on
`{0,2,7,8,11}` by `1/16` at the displayed feasible profile. This proves
the universal support-size cutoff for that covering inequality. The
five-point theorem establishes the reflected inequality on the same
support for constant kernels. General kernels on five points and the
unrestricted fourfold problem remain unresolved here.

Separate Codex agents reviewed the mathematical arguments and their LaTeX
transcription, including the covering identity, collision classifications,
coefficient comparisons, sharp constants, zero-weight cases and strictness.
The five-point Sidon argument uses Freiman's classical `3k−4` theorem;
its exact hypotheses were checked in the restatement on page 1 of
Bollobás, Leader and Tiba's arXiv:2204.09816v1. Freiman's original proofs
were not read. The manuscript discloses AI assistance and mathematical
agent review; no human peer review or journal acceptance is asserted.

The accompanying literature comparison incorporates the complete
Green–Matolcsi–Ruzsa–Shakan–Zhelezov preprint arXiv:2003.04077v1 and
the analytic companion arXiv:2003.04075v1. All five pages of the former
and the latter's definitions and decisive proof pages were checked on
the original PDFs. The comparison identifies the precise `p=q=2`
equivalence between their two-point statements. It also shows that the
indicator-tripling invariants alone do not determine the reflected
quotient for a fixed denominator profile. Whether the full prior
framework implies these small-support theorems remains unestablished.
Unread editions and chapters are listed in the literature comparison;
the paper makes no priority claim.

The source built with cached Tectonic 0.17.0 using
`--only-cached --untrusted --keep-logs`, without warnings, undefined
references or box errors. Poppler 26.08.0 metadata and text checks passed.
All 37 pages were rendered and individually inspected, including every
coefficient table and the references. The proofs require no search
program or numerical optimizer. The PDF is ready for publication with
the stated mathematical and literature scope. Repository checks and
verification of the released files accompany the release.

## Weighted-digit entropy attribution: 29 September 2026

The general weighted-digit formula in Theorem 1 follows from Lau and Nair's
typical-set theorem, a symmetric Gibbs coupling with equal marginals, and
the finite-set transfer of Gyarmati, Hennecart and Ruzsa. The revised source
states this attribution beside the theorem and gives the derivation in
Appendix A. The direct proof specifies the cost sublevel sets used in the
construction, and the four-digit certificate proves the same strict bound
`theta > 1.18565`.

The comparison uses Lau and Nair's *Information inequalities via ideas from
additive combinatorics*, arXiv:2312.11017v3, dated 5 February 2025,
Theorem 10 in Appendix C, and the GHR lemma on printed page 179 of the
published 2007 paper. Codex agent `/root` read the complete 21-page v3
preprint. Codex agent `/root/papers` independently reviewed the needed
type argument in Appendices B and C and inspected original PDF pages
15–21. That review established the typical-set limit despite two printed
issues: the reversed inequality sign in Lemma 9 and the unrestricted
interior-inclusion aside in Theorem 9. The case in which `Γ_n` consists of
`n`-types, used by Theorem 10, is valid; the manuscript also supplies its
direct type-class proof.

The positive implication was formulated by `/root` and independently
reviewed by `/root/papers`. The review checked the common marginal, both
entropy bounds, use of the same typical sets, zero marginal masses,
irrational probabilities, integer encoding, diameter control, the strict
GHR hypothesis, and the quantifier for every fixed `K>1`. It establishes
the general formula as a consequence of those prior results. Priority of
the particular numerical construction and the fivefold example remains
unestablished. The entropy application concerns finite integer supports;
it proves no unrestricted fourfold inequality and gives no general
non-implication result about the earlier weighted frameworks. The identified
journal edition of Lau–Nair remains unread.

The public text was drafted by Codex agent `/root/papers`, using the
canonical Hraness writing guides and `hraness-generation-style/v1`.
This is mathematical and editorial agent work; no human peer review or
journal acceptance is asserted. The earlier dated entries and immutable
releases preserve their original reading and validation scopes.

The public transcription passed independent mathematical review. The revised
nine-page PDF was rebuilt and every page visually inspected, with no
unresolved references or layout defects. The numerical verification programs
and certificates are unchanged. Repository checks and verification of the
released files accompany this update.

## Binary construction and maximal-coupling comparison: 29 September 2026

The binary companion construction is an explicit application of Lau and
Nair's typical-set theorem, arXiv:2312.11017v3, Theorem 10 in Appendix C,
with the stated marginal pair and elementary generating-polynomial bounds.
The attribution distinguishes this asymptotic implication from the paper's
finite exact-type proof in dimension 555,008. The same binary set appears
in the sum, difference and all five positions of the repeated sumset.
The finite theorem, proof, numerical parameters, programs and certificates
are unchanged.

Codex agent `/root/field_audit` formulated the concrete application and
`/root/papers` independently reviewed the marginal constraints, entropy
bounds, strict rational comparison, repeated-set construction and integer
encoding. The review found no required mathematical correction. Priority
of the particular marginals and fivefold example remains unestablished.

The literature comparison also covers Ken Lau, Chandra Nair and Zhaobang
Zhu's author-hosted manuscript, *A maximal-coupling information inequality
of sums on finite subsets of Abelian groups*. Agent `/root/field_audit`
read all seven pages and inspected every original page image; `/root`
independently reviewed the comparison and checked the decisive theorem
and proof passages. Theorem 5's fractional-partition bounds are valid.
Its direct fourfold substitutions upper-bound maximal sum entropy and
do not establish the reflected fourfold comparison. Review of the actual
conditional-Shearer argument and a direct finite-polytope argument
resolved two presentation issues without invalidating the main theorem.
The comparison is limited to the linked author-hosted text; a final
publisher edition was not reviewed.

This is mathematical and editorial AI-agent work. The attribution does
not establish priority or a general non-implication theorem about the
earlier frameworks. The earlier dated entries and immutable releases
preserve their original reading and validation scopes.

## Arbitrary kernel weights on a five-point support: 30 September 2026

The small-support manuscript now proves the reflected fourfold inequality
for arbitrary nonnegative kernel weights on `F={0,2,7,8,11}`, including
strictness when every kernel weight is positive and both inputs are nonzero.
This strengthens its earlier constant-kernel conclusion on that support.
The support is also the paper's counterexample to the stronger covering
bound, so the extension belongs in the same manuscript.

The proof combines a sharper allocation estimate with two coefficient
comparisons on each of the 120 orders of the kernel weights. All 240
rational certificates passed independent exact verification. The checker
reconstructs the sum fibers and polynomial coefficients, checks the
nonnegative mixtures, and requires both comparisons on every order.
The paper supplies the hand argument linking these comparisons to the
reflected inequality, including the remaining corner bound and strictness.
Independent mathematical agent review checked that argument and the
public transcription. The supplement runs with Python's standard library;
a numerical optimizer is not needed to verify the result.

The literature comparison includes the relevant proofs in Lau's July 2025
thesis. Its signed fourfold entropy inequality has a different direction
from the comparison needed here. Its arbitrary-Abelian-group typical-set
theorem also implies a broader maximal sum-triangle statement considered
during this research, so that argument is credited to prior machinery.
These comparisons establish neither priority for the five-point theorem
nor a general non-implication result. The unrestricted fourfold problem
remains unresolved in this work. The exact source versions and reading
scopes are recorded in the shared literature comparison.
