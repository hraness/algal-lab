# Claim-shape audit: NT2022 (Nadeb–Torabi, CSTM)

Run dir: `research/spikes/context/runs/nt2022-shape/` (gitignored).
Exact arithmetic: `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy Rational; Sturm `Poly.count_roots` + exact rational witnesses).
Script: `certify_nt_shape.py` → `certify_out.txt`. Audited 25 September 2026.
This is the same paper audited as "NT2020" in `hf2018-nt2020/memo.md` — the
two keys differ only in online-year (2020) vs print-year (2022) convention.

## 1. Identity (verified via Crossref + OpenAlex + Semantic Scholar)

**[NT2022]** H. Nadeb, H. Torabi, *New results on stochastic comparisons of
finite mixtures for some families of distributions*, Communications in
Statistics – Theory and Methods **51**(10):3104–3119 (print 19 May 2022;
**online 9 July 2020**). DOI `10.1080/03610926.2020.1788082`.
OpenAlex `W3041433414`; SS citation count 24; Crossref is-referenced-by 20.

**Verbatim abstract** (OpenAlex inverted index; SS agrees):

> "The classical finite mixture model is an effective tool to describe the
> lifetimes of the items existing in a random sample which are selected from
> some heterogeneous populations. This paper carries out stochastic
> comparisons between two classical finite mixture models in the sense of the
> usual stochastic order, when the subpopulations follow a wide class of
> distributions including the scale model, the proportional hazard rate model
> and the proportional reversed hazard rate model. Next, we consider the
> hazard rate and dispersive orders when the subpopulations follow the
> proportional hazard rate model and also the reversed hazard rate order in
> the case that the subpopulations follow the proportional reversed hazard
> rate model. Finally, the likelihood ratio order between two finite
> mixtures is characterized when the subpopulations belong to the
> transmuted-G model."

The abstract carries the cluster signature (st + hr + rh + disp + lr under
majorization) but gives **no n-scope** — the rate-order sections' arity is
only recoverable through citers.

## 2. Retrieval status — still fully closed

Unpaywall `is_oa:false`, no `oa_locations`; OpenAlex `is_oa:false`,
`any_repository_has_fulltext:false` (locations: publisher + RePEc metadata
only); zbMATH record exists (MSC 60E15) but the review text is
license-blocked; CORE query returns nothing usable; no arXiv/institutional
preprint. Confirms the `hf2018-nt2020` memo's retrieval log — every claim
below is audited **at transmitted claim shape**.

## 3. Claim-shape transmission map (what citers attribute to NT2022)

| NT theorem | Transmitted by | As | Order | n-scope of witness |
|---|---|---|---|---|
| Thm 3.1, 3.2, Rem 3.2 | SPBB2026 Rem 7 | particular cases of SPBB **Thm 5** (hr, π ≽^m π*, (γ,π)∈A_n) and **Thm 6** (rh, same shape), under `D(u;γ)=u` + GP components | hr/rh under *vector* majorization of mixing proportions | SPBB's Thms 5/6 are stated **general n** — but "particular case" is satisfied by an n=2 source as well: **ambiguous** |
| Thm 3.2 | SAF2022 Rem 6.6 | "Theorem 6.5 extends the result of Theorem 3.2 ... that compares two finite ordinary mixtures with respect to parameter λ" | **st** under λ ≻^w γ, (p,λ),(p,γ)∈U_n | SAF's version is general n (additive target — legitimate lift); NT's arity unstated |
| Thm 4.2 | SAF2022 Cor 6.21 | "extends the result of Theorem 4.2 ... which compares two finite ordinary mixtures with respect to parameter λ" — SAF's extension is stated for **W₂/U₂** | hr under λ ≽^m γ, PHR family | **n=2** |
| §4 (open problem) | SAF2022 Rem 6.18, verbatim | "Theorem 6.17 is proved for n = 2. We have not yet been able to prove whether the result holds for n > 2 or not ... (see also Section 4 of Hazra and Finkelstein (2018) and Nadeb and Torabi (2020), where the authors make the similar statement for ordinary mixtures when n > 2)" | n>2 hr left **open** | NT itself declares the general-n case unproved |
| Thm 4.5 | SPBB2026 Rem 9 | "when `D(u;γ)=u^γ` and each component follows PRHR model, Theorem 4.5 of Nadeb and Torabi becomes a particular case of Theorem 9" — SPBB Thm 9 is `M₂`/`N₂`, `A₂`, 2×2 chain majorization | rh under matrix change, PRHR model | **n=2** (SPBB's whole §4 matrix-change block is n=2 only — its Lemma 7 = BHM2015 Thm 2 is printed as a 2-column criterion) |
| whole paper | GY2024 l.92 | "Nadeb and Torabi (2022) derived usual stochastic order, hazard rate order, reverse hazard rate order, likelihood ratio order and dispersive order of the finite mixture **in the sense of vector majorization**" | all | method = **vector** majorization, not multivariate chain majorization |
| — | BKKA2024 l.84 | "By utilizing the majorization idea, Nadeb and Torabi (2022) ... usual stochastic order, hazard rate order, and reversed hazard rate order" | st+hr+rh | unstated |
| — | BKF2024 l.107 | "Nadeb and Torabi (2022) compared two FMMs using usual stochastic order when the subpopulations follow a general class of distributions" | **st only** | — |
| — | BTDK l.75 | "explored comparisons for FMMs within the framework of the usual stochastic order, considering subpopulations that follow the PHR, PRH model, or the scale models" | **st only** | — |

**Reading.** Two citer traditions conflict only superficially. SAF2022 — the
careful, historically-clean paper — reads NT Thm 3.2 as a st-order λ-result
and NT Thm 4.2 as an n=2 hr result, and quotes NT §4 as leaving n>2 **open**.
SPBB2026 — a certified-defective paper — files NT's §3 theorems under its own
general-n π-majorization hr/rh theorems. If NT's §3 results are genuinely
st-order (as SAF transmits), SPBB's Rem-7 mapping is loose citation, not a
theorem-level witness to a general-n rate claim.

## 4. Certificates applied

Script `certify_nt_shape.py`; model F̄_i = e^{−λᵢt} (PHR baseline read
`s=F̄(t)`; the same polynomial covers ordinary, PHR, every α>0 α-mixture, and
Weibull-subfamily readings per `suspect-batch`).

| Cert | Shape | Result |
|---|---|---|
| **A** (rerun = `hf2018-nt2020` Certificate 1) | (p,λ),(p,γ)∈U₃, λ≽ᵐγ ⇒ hr ordered — the **open question NT itself poses** | **FAILS at n=3**: p=(39/86,18/43,11/86), λ=(4,6,9), γ=(4,7,8); num deg 9, Sturm 2 roots (0,1]; d(1/2)=+6271/156247, d(3/4)=−17228781/103906915. The question NT left open resolves **negatively** — consistent with, and identical to, the prior audit |
| **P** (new, π-side) | λ fixed, (λ,π),(λ,π*)∈A_n (antiordered), π≽ᵐπ* ⇒ hr ordered — the SPBB Thm 5/6 shape to which NT §3 was mapped | **n=2 clean**: 100 admissible, 0 crossings, single consistent direction (d<0 for all 40 non-tied ordered pairs). **n=3 FAILS**: 4263 admissible, **35 certified crossing pairs**. First certificate: λ=(1,2,3), π=(1/2,3/8,1/8), π*=(1/2,1/4,1/4) [π≽ᵐπ* exact; both A₃]; numerator deg 3, **1 interior root** (endpoint factors stripped); d(1/4)=+8/407, d(1/2)=−4/253, d(9/10)=−4140/39803 — hazards cross |
| **B** (frozen-column T-transform) | — | **not triggered**: no general-n matrix-change hr/rh claim is transmitted for NT2022; its only transmitted matrix-change theorem (Thm 4.5) arrives at n=2 via SPBB Thm 9 |
| **C** (rh duality) | — | applies verbatim to any rh shape above (r̃ = h̃/x, identical sign); no separate run needed |

Bug note: the first run's naïve `count_roots(0,1)` counted the endpoint root
u=0 (t→∞) and reported "80 crossings" at n=2; stripping u- and (u−1)-factors
before the Sturm count gives the true **0**. The endpoint root is benign —
the numerators of these brackets always vanish at u=0.

## 5. Verdict

**Probably clean-shape for the defect cone** — same family as SAF2022:

- Every rate-order theorem transmitted at theorem level arrives at **n=2**
  (Thm 4.2 via SAF Cor 6.21/W₂; Thm 4.5 via SPBB Thm 9/M₂). The n=2 hr and
  π-majorization shapes are consistent on samples (140 admissible / 0
  violations previously; 100/0 with consistent direction here).
- SAF2022's verbatim Rem 6.18 testifies NT §4 **declares n>2 open** — NT did
  not claim the general-n rate ordering. That open problem is now certified
  negative (CERT A).
- Its st results target the additive functional ΣpᵢF̄ᵢ — the majorization
  lift is legitimate there (2916 admissible / 0 violations previously).
- Per GY2024, NT's machinery is **vector** majorization — no evidence NT
  uses the frozen-column T-transform lift on ratios at all.

**Residual (flagged, not decidable without the text):** if SPBB Rem 7's
mapping is faithful and NT Thms 3.1/3.2 are *general-n* hr/rh claims under
π-majorization, NT2022 is a **conditional certified carrier** of the
vector-majorization defect — refuted by CERT P above. Under that reading the
verdict flips and the chronology below changes accordingly.

## 6. Provenance — does second-misuse move from BKB2022 to NT2022?

NT2022's reference list (25 Crossref-deposited refs, DOIs resolved):
**HF2018 is ref 9** (DOI 10.1007/s11749-018-0581-7) — confirmed citation of
the defect origin. **Absent**: BHM2015 (10.1109/TR.2014.2354192), BKB2022
(10.1017/S0269964820000467), HKFN2017. The remaining refs are the older
component-wise mixture literature (Finkelstein 2006 CSTM, ASZ2017 ORL,
Navarro ×3, Belzunce, Bartoszewicz, Kochar, Balakrishnan-ScandActJ, Nadeb ×2)
plus books. So NT2022 descends from HF2018 alone — and is *not* downstream
of BKB2022's Lemmas 2.4/2.5 handle.

Chronology: NT2022 online **9 Jul 2020** vs BKB2022 online **Sep 2020** —
NT is earlier, as the cluster map flagged. But the second-misuse question
turns on whether NT's hr theorems use the lift at general n, and the citer
record says they do not:

**Second-misuse stays with BKB2022** — conditional on the paywalled text.
NT2022 looks like the other prudent contemporary (with SAF2022): it inherited
HF2018's machinery, proved the n=2 cases, and stated n>2 as open — the open
problem whose negative answer this project has now certified twice. If the
unretrieved §3 turns out to contain general-n π-majorization hr/rh claims
(the hostile reading of SPBB Rem 7), NT2022 becomes a conditional carrier
via CERT P and *does* predate BKB2022 — the single document that would
settle it is the NT2022 text itself.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY certify_nt_shape.py    # CERT A rerun + CERT P (n=2 control, n=3 search) ~40s
    # identity/provenance payloads: crossref.json, openalex.json, ss.json (this dir)
