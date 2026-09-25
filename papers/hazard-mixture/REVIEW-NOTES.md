# Review notes: hazard-mixture counterexample manuscript

Date: 25 September 2026. Branch `paper/hazard-mixture`, directory `papers/hazard-mixture/`.

Artefacts: `main.tex`, `refs.bib`, `main.pdf` (12 pages, compiled with tectonic 0.17.0),
`verify/verify_core.py`, `verify/verify_general_mechanism.py`, `verify/verify_strict_variant.py`,
`verify/verify_two_crossings.py`, `verify/run_all.sh`; the revision adds
`verify/verify_reversed_hazard.py` and brings `main.pdf` to 15 pages (see "Revision response"). Delivery copy:
`/Users/bg/Documents/algal-lab-delivery-20260925/hazard-mixture-counterexample.pdf`.

Source of the claims: `docs/hazard-mixture-counterexample.md` (repository note, audit date
23 September 2026) and `docs/novelty-ledger.md`, row "Majorization does not order
exponential-mixture hazards in dimensions above two". The repository verifier
`research/spikes/stochastic/hazard_mixtures.py` was read but neither imported nor run; every
statement was re-derived with fresh scripts under `verify/` using
`/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python` (SymPy 1.14.0, Python 3.12.14).

Check identifiers below refer to the `PASS` lines printed by the scripts.

## 1. Claim-by-claim table: repository note

| # | Claim in the repository note | Where proved in the manuscript | How re-verified | Status |
|---|---|---|---|---|
| N1 | Equal weights, rates (1,3,5) majorize (1,4,4); increasing prefix sums (1,4,9) vs (1,5,9) | Theorem 3.1(a), with gamma = lambda T, T = (I + Pi_23)/2 | verify_core A1, A2, A3 (exact partial sums of decreasing rearrangements, both directions) | Verified |
| N2 | h_lambda(log 2) = 11/7, h_gamma(log 2) = 8/5, difference -1/35; h_lambda(log 4) = 103/91, h_gamma(log 4) = 12/11, difference 41/1001 | Theorem 3.1(d); formulas (2) and (3) | verify_core A4, A5, A6 at q = 1/2 and q = 1/4 (exact rationals) | Verified |
| N3 | Neither direction of the hazard rate order holds | Theorem 3.1, final sentence | Follows from N2; sign pattern verify_core A15 | Verified |
| N4 | S_lambda - S_gamma = q^3 (1-q)^2 / 3 > 0 for t > 0 (usual stochastic order holds) | Theorem 3.1(e) | verify_core A7 (polynomial identity), D1 (positivity on (0,1)) | Verified |
| N5 | Padded family m = n-2 >= 1: majorization persists; h_lambda - 1 = (2q^2+4q^4)/(m+q^2+q^4), h_gamma - 1 = 6q^3/(m+2q^3); hazard difference formula (1) of the note | Section 4, equation (6) = Theorem 4.1(a) | verify_core B1 (identity symbolic in m), B9 (direct-definition agreement and majorization for m = 1..64) | Verified |
| N6 | B_m(q) = m(1-2q) - q^3 - q^4 has derivative -2m - 3q^2 - 4q^3 < 0; B_m(1/4) = m/2 - 5/256 > 0, B_m(1/2) = -3/16 < 0; exactly one root q_* in (1/4, 1/2); crossing time in (log 2, log 4); difference negative before and positive after | Theorem 4.1(b), (c) | verify_core B3, B4, B5, B6, B9 (one root and localisation for m = 1..64), A9 to A12 for m = 1 | Verified. Note: for 0 < m < 5/128 one has B_m(1/4) < 0, so the root lies in (0, 1/4]; the manuscript states 0 < q_* < 1/2 for all m > 0 and the (1/4, 1/2) localisation only for m >= 1, which is what the note uses (m integer) |
| N7 | S_lambda - S_gamma = q^3 (1-q)^2 / n for the padded family | Theorem 4.1(e), with n = m + 2 | verify_core B2 (symbolic in m), D1 | Verified |
| N8 | m = 0 is the two-component pair (3,5) vs (4,4), bracket strictly negative, no crossing | Remark 4.2 | verify_core C1, C2, C3 | Verified |
| N9 | General mechanism: R = S_X/S_Y = 1 + (1-w)(cosh(dt)-1)/(w e^{ct} + 1 - w) > 1; (log(R-1))' = d coth(dt/2) - c w e^{ct}/(w e^{ct}+1-w); first term decreases from infinity to d, second increases to c > d; exactly one zero; h_X - h_Y = -(log R)' changes sign from negative to positive exactly once; stochastic dominance throughout | Theorem 5.1(a), (b) and its proof | verify_general_mechanism 1, 1', 2, 3, 4a to 4d (identities, derivatives and limits, symbolic in a, b, c, d, w) | Verified |
| N10 | With w = 0: h_X = b - d tanh(dt) <= b = h_Y | Theorem 5.1(c) | verify_general_mechanism 5, 5' | Verified |
| N11 | Antiordering of the three weights and rates needs w >= 1/3; the padded family has effective slow weight w = m/(m+2) | Corollary 5.2 | verify_general_mechanism 6a to 6f (specialisation (a,b,d) = (1,4,1), F = -2B_m(q)/((1-q)(m+2q^3)), w = 1/3 iff m = 1) | Verified |
| N12 | Specialisation of the 2022 hypotheses (Theorem 6.3, page 1073): baseline hazard r(t given lambda) = lambda linear (increasing, concave), survival e^{-lambda t} decreasing, alpha_i = 1, p_i = 1/n, antiordering with equality, majorization; the paper uses this baseline in Example 6.4; Remark 6.3 (page 1075) leaves n > 2 open | Section 7.1, Statement 7.1 and the paragraph after it | Read in the Cambridge Core version of record (SHA-256 6750bb3e...); Example 6.4 text confirmed ("Let F(t given lambda) = e^{-lambda t}"); page numbers confirmed | Verified by reading; the reduction is elementary |
| N13 | 2026 accepted manuscript: model (1.3), class V_n on page 6, Theorem 3.8 on page 20; with baseline e^{-t}, alpha = theta = 1, p = q = (1/3,1/3,1/3), T = (I + P_23)/2 one has [p; lambda] T = [p; gamma], the matrix lies in V_3, the conclusion U_3 >=_hr V_3 means h_lambda <= h_gamma, contradicted by 41/1001 > 0 | Section 7.2, Statement 7.2 (verbatim quotation) and instance (1) | Read in the Strathprints accepted manuscript (SHA-256 67efbc37...); the identities (1,3,5) T = (1,4,4) and pT = p for uniform p are one-line hand computations; membership in V_3 (antiordering with equality) checked by hand | Verified against the accepted manuscript only; the version of record was not retrieved |
| N14 | The proof of Theorem 3.8 invokes Lemma 2.5, which concerns a sum of functions of individual columns, while the mixture hazard is a ratio of sums with a shared denominator | Section 7.2, paragraph "Where the published argument stops" | Read Lemma 2.5 (page 6) and the proof on page 20 of the accepted manuscript | Diagnosis only; it is a reading of the published proof, not a theorem, and the counterexamples do not depend on it |
| N15 | Strict variant, common weights p = (2/5, 1/3, 4/15), lambda = (2,6,10), gamma = (2,7,9): weights strictly decreasing, rates strictly increasing, lambda majorizes gamma, difference at log 2 equals 248/4455 > 0, difference at log(4/3) negative | Proposition 6.1(a), (b) | verify_strict_variant 1 to 5 | Verified |
| N16 | Strict variant, transformed weights: T = (3/4) I + (1/4) P_23, pT = (2/5, 19/60, 17/60), lambda T = gamma, strict antiordering; h_{p,lambda}(log 2) = 898/405, h_{pT,gamma}(log 2) = 6829/3165, difference 1019/17091 > 0, negative at log(4/3) | Proposition 6.1(a), (c) | verify_strict_variant 6 to 10 | Verified |
| N17 | The repository verifier `research/spikes/stochastic/hazard_mixtures.py` reproduces the checks; rational grids for 3 <= n <= 32 are implementation checks only | Not used in the manuscript (Section 9 relies on the fresh scripts) | Not run, by instruction | Not re-verified; the manuscript does not depend on it |
| N18 | Priority: whether the observation or an equivalent correction already appeared elsewhere is unresolved | Section 8, "Literature search" | Eight web searches plus targeted retrievals on 25 September 2026, nothing found | Still unresolved; bounded search only |

## 2. Claim-by-claim table: statements that are new in the manuscript

| # | Manuscript statement | Proof | Machine check | Status |
|---|---|---|---|---|
| M1 | Lemma 2.2: h_{p,v} real-analytic, h(0) = mean, h'(0) = -variance, strictly decreasing, tail h - v_min ~ (W_2/W_1)(u - v_min) e^{-(u - v_min) t} | Hand proof in Section 2 (h' = -Var under the tilted weights, Proschan's argument; tail by cancelling e^{-v_min t}) | verify_core A16, A17, A18, D2 (instances); verify_two_crossings 8 to 10 (instances) | Proved; standard material |
| M2 | Lemma 2.3: convex sums and strict Schur-convexity of sum of squares via chains of T-transforms (Marshall, Olkin and Arnold, Lemma 2.B.1) | Hand proof in Section 2 relying on the cited lemma | none needed | Proved, relies on a textbook lemma |
| M3 | Theorem 3.1(c): the crossing time t_* = -log q_* with q_* in (1/4, 1/2), numerical values q_* = 0.439087115146..., t_* = 0.823057445625... | Hand proof (monotone B_1, sign change) | verify_core A10 (Sturm count), A12, A14 (interval isolation to 10^{-12}) | Proved; digits machine-certified |
| M4 | Remark after Theorem 3.1: B_1 is irreducible over Q, so q_* is algebraic of degree four | Not proved by hand | verify_core A15b (SymPy `is_irreducible`) | Machine-certified only (rational-root test plus an irreducibility routine); a hand proof would use the reduction of 1 - 2q - q^3 - q^4 modulo a small prime |
| M5 | Theorem 4.1(c): for m >= 1, 1/2 - 3/(16m) < q_*(m) < 1/2, hence log 2 < t_*(m) < log 2 + 3/(8m-3) < log 4; explicit differences -3/((16m+5)(4m+1)) at log 2 and 3(128m-5)/((256m+17)(32m+1)) at log 4 | Hand proof (evaluate B_m at the two endpoints; -log(1-x) <= x/(1-x)) | verify_core B7 (endpoint identity symbolic in m), B4, B5; instances in B9 | Proved |
| M6 | Theorem 4.1(d): q_*(m) strictly increasing in m, t_*(m) decreasing to log 2 | Hand proof (B_{m'}(q) - B_m(q) = (m'-m)(1-2q) > 0 on (0,1/2) and monotonicity of B_m) | verify_core B9 (isolating intervals for m = 1..64 are consistent) | Proved |
| M7 | Theorem 4.1 applies to all real m > 0 (not only integers); the note only used integers | Hand proof, same argument | verify_core B1 to B8 symbolic in m | Proved |
| M8 | Theorem 5.1: full trichotomy for the three-parameter family; crossing iff w in (0,1) and a < b - d; hazard order h_X < h_Y when w = 0 or a >= b - d; the crossing time solves d coth(dt/2) = c w e^{ct}/(w e^{ct} + 1 - w) | Hand proof in Section 5 using the identities of N9 and the limit comparison c versus d | verify_general_mechanism 1 to 5' (identities, derivatives, limits) | Proved. The boundary case a = b - d (c = d) is proved by hand: the decreasing term stays above d = c while the increasing term stays below c, so F > 0 |
| M9 | Remark 5.3: (1,1,7) versus (1,4,4) is the boundary case; the hazard order holds with an explicit formula | Hand remark plus the factorisation | verify_core E1, E2 (exact factored form 6 q^3 (q-1)(q^3+2)(q^2+q+1)/((2q^3+1)(q^6+2))) | Proved |
| M10 | Theorem 5.4: crossing criterion (A: smaller mean, or equal means and larger variance; B: equal minimal rate and smaller second distinct rate) forces h_{p,lambda} < h_{p,gamma} near 0 and > near infinity | Hand proof from Lemma 2.2(a), (c) | none beyond the lemma instances | Proved |
| M11 | Corollary 5.5: uniform weights, lambda majorizes gamma, not a rearrangement, common minimal rate with common multiplicity, lambda_(k+1) < gamma_(k+1) implies a crossing | Hand proof (Lemma 2.3(b) gives the variance inequality; Theorem 5.4) | none needed | Proved |
| M12 | Proposition 6.1(d): the strict-variant hazard differences have exactly one sign change each, at t about 0.380362 (common weights) and 0.367980 (transformed weights) | At least one sign change is proved by hand (values in N15, N16; Theorem 5.4 applied with different weight vectors gives the pattern near 0 and infinity); "exactly one" is not hand-proved | verify_strict_variant 11 and 12 for both cases (Sturm count on (0,1), endpoint exclusion to 10^{-30}, isolating intervals) | Exactly-one count is machine-certified only |
| M13 | Proposition 6.1(e): S_{p,lambda} - S_{p,gamma} = q^6 (1-q)(5 - 4q^3)/15 > 0 | Hand computation | verify_strict_variant 13 | Proved |
| M14 | Proposition 6.2: gamma' = (41/40, 159/40, 4) = lambda T_1 T_2 with T_2 = (119/120) I + (1/120) Pi_12; h_lambda < h_gamma' near 0 and near infinity, > at t_1 = 40 log(500/483); exactly two sign changes at t about 1.043788 and 1.885779; S_lambda > S_gamma' | (a) to (c) by hand plus one exact rational evaluation (a finite computation, script check 5); the count "exactly two" is not hand-proved | verify_two_crossings 1 to 10 (degree-275 numerator, VCA isolation, denominator has no root in (0,1)) | At least two crossings proved (given the exact value at t_1); exactly two is machine-certified only |
| M15 | Statement 7.1 (the n-component extension asked in Remark 6.3) is false for every n >= 3 with equality in the antiordering, and also with strict inequalities (Proposition 6.1(b)) | Reduction in Section 7.1 plus Theorems 3.1, 4.1 and Proposition 6.1 | as above | Proved |
| M16 | Statement 7.2 (Theorem 3.8 of the accepted manuscript) is contradicted by instances (1) n = 3 uniform, (2) every n >= 3 uniform, (3) n = 3 strictly antiordered; Corollary 3.2 (k = 1 case) by the same instances; Theorem 3.9 (two T-transforms with different structures, intermediate matrix in V_3) by instance (4) | Reduction in Section 7.2 plus the cited results | as above | Proved against the accepted manuscript; instance (4) relies on the exact rational value at t_1 (script check 5), not on the crossing count |
| M17 | Proposition 7.3 (what survives): for uniform weights and lambda majorizing gamma (not a rearrangement) S_lambda > S_gamma everywhere, h_lambda < h_gamma on a neighbourhood of 0, limits lambda_(1) <= gamma_(1), both hazards decreasing, and the two-component hazard order | Hand proof (Lemma 2.3(a) with the strictly convex e^{-tx}; Lemma 2.2; the cosh computation for n = 2) | instances in verify_core A7, D1, D2, C2 | Proved |

## 3. Discrepancies between the repository note and the re-verification

None of the note's mathematical statements failed re-verification. Differences are of scope and
precision only:

1. The note checked the strict variant at two points (log 2 and log(4/3)) only. The manuscript
   adds the exact number of crossings (one in each case) and the survival difference; the count
   is machine-certified, see M12.
2. The note's every-dimension statement uses integer m = n - 2 >= 1; the manuscript proves the
   family for every real m > 0 and adds explicit values, bounds and monotonicity (M5 to M7).
   For 0 < m < 5/128 the root is not in (1/4, 1/2); this does not affect the note, which has
   m >= 1.
3. The note's mechanism section proves the crossing for a < b - d; the manuscript adds the
   converse (M8), so the mechanism is a characterisation for that family.
4. The note's Sahoo et al. discussion covers Theorem 3.8 only; the manuscript also records
   that Corollary 3.2 and Theorem 3.9 of the accepted manuscript are false as stated (M16),
   the latter through a new example with distinct minimal rates and two crossings (M14).
5. The note says the 2026 theorem's proof "invokes Lemma 2.5"; the accepted manuscript's
   proof text invokes Lemma 2.4 for the two-column case and Lemma 2.5 for the extension. The
   manuscript reports this precisely (Section 7.2).
6. Bibliographic correction made during the work: the MDPI Mathematics 14(14):2557 article is
   Sahoo, Kayal and Balakrishnan (2026), not a published version of Guo and Yan
   (arXiv:2407.15638); the novelty ledger's description of the "July 2026 modified
   proportional hazard paper" should be read with this in mind. Guo and Yan's hazard-rate
   theorems vary tilt parameters and are not touched by our examples.
7. The note cites the Wiley publication date (8 April 2026) for Sahoo et al.; the manuscript
   cites the Crossref record (volume 42, issue 2, e70089) and states that the version of
   record was not retrieved and that Crossref lists no correction as of 25 September 2026.

## 4. Submission blockers and open items

1. Author block. `\author{[Owner name to be confirmed]}` must be replaced; affiliation, e-mail,
   ORCID and any funding statement are missing. The AI-assistance disclosure is a `\thanks`
   footnote on the title page; the chosen venue may require its own wording or a separate
   declaration.
2. Version of record of Sahoo, Kayal and Finkelstein (2026). Only the accepted author
   manuscript (Strathprints 96227, 26 pages, SHA-256 67efbc37...) was read; the Wiley version
   (doi:10.1002/asmb.70089, volume 42, issue 2, e70089) was not retrieved. Theorem numbers,
   wording or hypotheses may differ there. Section 7.2 and the `note` field of the bib entry
   say so explicitly. Someone with access should check Theorem 3.8, Corollary 3.2 and
   Theorem 3.9 in the version of record before submission and update the section.
3. Two cited papers were not read: Hazra and Finkelstein (2018, TEST) and Nadeb and Torabi
   (2022, Communications in Statistics). The accepted manuscript's proof of its Theorem 3.9
   cites Theorem 3.4 of Hazra and Finkelstein; if that theorem is an n-component hazard-rate
   statement for ordinary mixtures under chain majorization it may be affected by the same
   examples. The manuscript makes no claim about it; this should be checked.
4. Machine-certified counts. Three statements are certified by exact computation rather than
   by a hand proof and are labelled as such in the manuscript: irreducibility of B_1 (M4),
   "exactly one" crossing in Proposition 6.1(d) (M12), and "exactly two" crossings in
   Proposition 6.2(d) (M14). Everything the negative answers rest on (Theorems 3.1, 4.1, 5.1,
   5.4, Proposition 6.1(b), (c), Proposition 6.2(a) to (c)) is proved by hand, with the exact
   rational values also checked by the scripts. A referee may still ask for hand proofs of the
   counts; a Sturm-sequence argument by hand is feasible for the degree-13 and degree-17
   numerators of Proposition 6.1 but not realistic for the degree-275 numerator of
   Proposition 6.2, whose count is not needed for any conclusion.
5. Priority. The literature search (eight queries, 25 September 2026, recorded in Section 8)
   found no prior counterexample or correction, but it was bounded. Before submission: check
   the citing articles of Shojaee et al. (2022) and Sahoo et al. (2026) in Scopus or Google
   Scholar and the arXiv listings after 25 September 2026.
6. Courtesy. The manuscript contradicts three statements of a published paper. Consider
   informing the authors (and, if a comment format is chosen, the journal) at submission time.
   The manuscript's wording is factual and attributes the failure to a specific step of the
   proof (Lemma 2.5, additive form).
7. Length and format. 12 pages at 10pt with 0.9in margins and a compact bibliography; a
   journal class will change the count. Sections 8 and 9 (sources, reproducibility) can be
   shortened or moved to supplementary material if a venue requires it; the SHA-256 values
   should then move with them.
8. No blocker, for information: the repository verifier
   `research/spikes/stochastic/hazard_mixtures.py` is not referenced by the manuscript and was
   not run for it.

## 5. Suggested venue

Primary suggestion: Probability in the Engineering and Informational Sciences (Cambridge).
Remark 6.3 of Shojaee, Asadi and Finkelstein was posed there, the readership works on
stochastic orders of mixtures, and the result is a short, complete answer to a question the
journal published. A short-communication or note format fits the length.

Alternatives, in order:

1. Applied Stochastic Models in Business and Industry (Wiley), as a note or comment on Sahoo,
   Kayal and Finkelstein (2026), since three of its statements are contradicted; this route
   should only be taken after the version of record has been checked (item 2 above).
2. Statistics and Probability Letters (Elsevier), which publishes short notes on stochastic
   orders and counterexamples; the main content fits its page limits after moving Sections 8
   and 9 to supplementary material.

In every case post a preprint first on arXiv, primary math.PR with cross-list stat.ME, so the
negative answer is dated; the exact scripts can be attached as ancillary files.

## 6. Sources

Retrieved and read in full (scratchpad `sources/`):

- Shojaee, Asadi and Finkelstein (2022), Cambridge Core version of record, 25 pages,
  SHA-256 `6750bb3ec436b230b2caae9b38a3f801e847609988af0084176ec0c475e3256b`; Definition 6.1
  and the class U_n (page 1069), Theorem 6.3 (page 1073), Remark 6.3 and Example 6.4
  (page 1075) quoted in the manuscript.
- Sahoo, Kayal and Finkelstein (2026), accepted author manuscript, Strathprints record 96227,
  26 pages, SHA-256 `67efbc3770e16abdb2c4c2c6158323bf8e4966e9d8dd4dae6d0ac8efd6d1fe7c`;
  model (1.3) (page 3), Definition 2.1(ii), classes V_n and W_n and Lemmas 2.4, 2.5 (page 6),
  Theorems 3.7 to 3.9 and Corollary 3.2 (page 20). Theorem 3.8 is quoted verbatim.
- Guo and Yan (2024), arXiv:2407.15638v2, 32 pages,
  SHA-256 `26cbe4d4c562c0af4be0b852b694ec20e98c86dde01d40691d2295b2780bec0d`; read to confirm
  that its hazard-rate results concern tilt parameters and are not instances of our examples.

Not retrieved (bibliographic records verified through Crossref on 25 September 2026):

- Sahoo, Kayal and Finkelstein (2026), Wiley version of record (doi:10.1002/asmb.70089):
  access restricted. Crossref lists no correction or update for the DOI.
- Hazra and Finkelstein (2018), TEST 27(4):988-1006: full text not accessible.
- Nadeb and Torabi (2022), Communications in Statistics, Theory and Methods 51(10):3104-3119:
  full text not accessible.
- Sahoo, Kayal and Balakrishnan (2026), Mathematics 14(14):2557: Crossref record and abstract
  only (publisher page returned an error); cited as context.
- Bartoszewicz and Skolimowska (2006), PEIS 20(4):655-666: abstract only; cited as context.
- Asadi, Ebrahimi and Soofi (2019), Journal of Applied Probability 56(4):1151-1167: cited only
  as the origin of the alpha-mixture model, as both source papers attribute it.

The remaining entries (Marshall, Olkin and Arnold 2011; Shaked and Shanthikumar 2007;
Proschan 1963; Basu, Pollack and Roy 2006; Meurer et al. 2017 for SymPy) are standard
references whose Crossref records were verified; they are cited for the specific lemmas or
algorithms named in the text.

Web searches: eight queries on 25 September 2026, listed verbatim in a footnote of Section 8,
followed by targeted retrievals (Cambridge Core, Strathprints, Wiley, MDPI, arXiv including
arXiv:2511.00791). Nothing prior was found; the search was bounded.

## 7. Reproduction

```
cd papers/hazard-mixture/verify
PYTHON=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python ./run_all.sh
cd .. && /opt/homebrew/bin/tectonic main.tex
```

Scripts (SymPy 1.14.0, Python 3.12.14; exact arithmetic only, no repository imports):

| Script | Checks | Time | SHA-256 |
|---|---|---|---|
| `verify_core.py` | 42 | about 25 s | `4660ba2f26025e26f6a68fc8375a6bbb44306bd258d4cc5a203e653a28818b74` |
| `verify_general_mechanism.py` | 16 | about 70 s | `dd61c5493c737bc9baafc094684208e5e83448f4466d6211d70c119a8c4f7f68` |
| `verify_strict_variant.py` | 21 | about 6 s | `fe993d1b1df7d7d7fce6e77d57d3635ede71235b41862527e298b1a10c3055d3` |
| `verify_two_crossings.py` | 13 | about 25 s | `06b4eb6b6c8e02393c5a548911ee5c7b75798b3c1b963276f434cb865da1414c` |
| `verify_reversed_hazard.py` | 18 | about 5 s | `a25d901588f1efbc6a3b4431384b985221bcf775d414b8511a045152074f064d` |

(Table updated in the revision; the original four hashes and the count of 85 are superseded.)
All 110 checks pass; each script exits with status 0 only if every check passes. The hashes
above are the ones printed in Section 9 of the manuscript; if a script is edited, update both.

## 8. Revision response (referee report of 25 September 2026, `REFEREE-REPORT.md`)

Section numbers refer to the revised manuscript. The new Section 7.3 shifts "What survives"
to Section 7.4 (Proposition 7.3 keeps its number).

1. Author placeholder (blocking). Not resolved by the agents: the author block is kept as an
   explicit placeholder, now `[PLACEHOLDER: author name and affiliation to be inserted before
   submission]`. The AI-assistance `\thanks` footnote is kept and now says that it must be checked
   against the target journal's policy. The owner must fill this in before submission.
2. Root-isolation algorithm. Section 9 and the proof of Proposition 6.2 now name the
   Vincent-Akritas-Strzebonski continued-fraction method as implemented in SymPy's
   `Poly.intervals` and cite Akritas and Strzebonski (2005) (new `refs.bib` entry, DOI checked
   through Crossref; SymPy's `rootisolation.py` cites the same paper). The docstring of
   `verify_two_crossings.py` is corrected and its SHA-256 updated.
3. Degree 275. The proof of Proposition 6.2 now says that the directly formed numerator has
   degree 279 and that 275 is the degree after cancelling `(1+s+s^2)^2`. New check 3' in
   `verify_two_crossings.py` verifies 279, the common factor and 275.
4. Rounded digits. Theorem 3.1(c) now prints `t_* = 0.82305744562489...` and states that both
   decimals are truncated. The referee's suggested `0.8230574456249...` would also have been
   rounded, since the expansion is 0.82305744562489256... The Table 1 caption now says "rounded
   to six decimals".
5. Reversed hazard rates. New Section 7.3 "Scope, and the reversed hazard rate statements":
   (i) the reduction `h_U(t) = theta^{-1} h(t/theta) htilde(Gbar(t/theta)^alpha)` and the
   consequence that the failure of Theorem 3.8, Corollary 3.2 and Theorem 3.9 holds for every
   continuous baseline with positive hazard rate, every theta and every alpha > 0; (ii) an explicit
   statement that the W_n, alpha <= 0 half is not touched, with the alpha < 0 computation for
   instance (1); (iii) a verbatim quotation of SKF Theorem 3.11 (page 23) and descriptions of
   Corollary 3.3 and Theorem 3.12 (page 24), checked on 25 September 2026 against the Strathprints
   PDF (SHA-256 identical to the one in Section 8); (iv) reading (a), where the reversed hazard
   rate is the formula displayed in the proof: Theorem 3.11 and Corollary 3.3 fail at instances (1)
   to (3) and Theorem 3.12 at instance (4), for example `123/1001 > 0` at `t = log(4/3)`; the
   note that this formula belongs to the alpha-mixture of distribution functions, not to (1.3)
   (11/7 against 11/25); (v) reading (b), the reversed hazard rate of (1.3): Theorem 3.11 fails
   (`9/475 > 0` at `t = log 2`). A correction to the referee's "same distribution" remark: under
   reading (b) the same argument already applies to Theorems 3.7 and 3.10 at n = 2. For
   `(3,5)`, `(4,4)` it gives `17/59 > 4/15`, so under reading (b) Theorem 3.10 fails too, and a
   failure under that reading is not specific to n >= 3. The manuscript therefore treats (a) as
   the substantive reading and says so. The abstract and Introduction item (e) mention the
   strengthening, and Section 2 defines the reversed hazard rate order. Verified by
   `verify_reversed_hazard.py` (18 checks, including new check 4' for 123/1001).
6. Bibliography cross-reference. `\ref{sec:sources}` removed from the `note` field of
   `SahooKayalFinkelstein2026`; Section 7.2 now opens with an in-text pointer to Section 8.
7. SAF page numbers. Not re-checked: the version of record is paywalled and not available to
   the agents in this revision. Note an internal inconsistency to resolve with the PDF: Section 8
   of the manuscript places Definition 6.1 on page 1068, while Section 6 of these notes places
   Definition 6.1 and U_n on page 1069. The SKF page numbers were re-checked against the
   Strathprints PDF (statements up to Theorem 3.12 are now listed in Section 8).
8. Unread sources. A further search for an open copy of Hazra and Finkelstein (2018) found
   only the publisher's page. The cautious wording is kept and now covers Theorem 3.12, whose
   proof is also deferred to their Theorem 3.4. Nadeb and Torabi (2022) is still unread. Both
   remain open before submission.
9. Weak consistency check. Check 6' in `verify_two_crossings.py` is now the conjunction only
   (hash updated). The proof of Proposition 6.2 also gives the parity argument: signs
   `-, +, -` at three rational points and exactly two distinct roots imply two sign changes.
10. Irreducibility of B_1. The remark after Theorem 3.1 now contains the hand proof by reduction
    modulo 2 (plus Gauss's lemma). New check A15c in `verify_core.py` verifies each step.
11. Machine-only counts. Proposition 6.1(d) is now hand-checkable: explicit factorizations
    `q^4 P/(A C)` and `q^4 P~/(A C~)`, the substitution `q = 1/(1+x)`, the printed coefficient
    sequences of `Q` and `Q~` (one sign change each) and Descartes' rule (checks 14 to 18 in
    `verify_strict_variant.py`). The "(machine-certified)" label is removed there and kept for
    Proposition 6.2(d). Section 9 now says that Sturm and VAS counts are counts of distinct roots.
12. Neighbouring results. New paragraph in Section 8: Barmalzan, Kosari and Balakrishnan
    (2022), which the SKF manuscript names as the source of its Lemmas 2.4 and 2.5 (confirmed in its
    reference list), Bhakta, Kayal and Balakrishnan (2024), Guo and Yan (2024) and Sahoo, Kayal and
    Balakrishnan (2026) are named and declared outside the scope of the note. The paragraph says
    that we did not check whether they use a Lemma 2.5 step. The two new `refs.bib` entries were
    checked against Crossref (volume, issue, pages, DOI). "Where the published argument stops"
    now attributes Lemmas 2.4 and 2.5 to that paper and says that the lemma itself is not in question.
13. LaTeX. Recompiled with tectonic: no undefined references or citations, no overfull boxes,
    no em-dashes in source or PDF text, and the AI-disclosure footnote is present. The PDF is now
    15 pages.

Verify suite after the revision (`PYTHON=<python with sympy 1.14> ./verify/run_all.sh`): exit
status 0; 42 + 16 + 21 + 13 + 18 = 110 PASS lines. The runner uses `${PYTHON:-python3}` and
contains no local path.

Still open before submission: author block (item 1), SAF page numbers and the Definition 6.1
page discrepancy (item 7), Hazra and Finkelstein (2018) and Nadeb and Torabi (2022) (item 8),
the SKF version of record (Section 4 item 2), and informing the SKF authors (referee's
suggestion).
