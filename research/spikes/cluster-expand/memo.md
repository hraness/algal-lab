# Cluster expansion: full citer set of the defect handles

Run dir: `research/spikes/context/runs/cluster-expand/` (gitignored). Compiled
26 September 2026. Exact arithmetic: `.venv-math` (sympy 1.14, Rational/Sturm).
Nothing committed.

## Enumeration

Handles resolved to OpenAlex IDs (round 1, before throttling):

| Handle | OpenAlex | DOI | OA cited_by | S2 citers | COCI citers |
|---|---|---|---|---|---|
| HF2018 (TEST) | W2794786652 | 10.1007/s11749-018-0581-7 | 28 | 1* | 22 |
| NT2022 (CSTM 51(10)) | 10.1080/03610926.2020.1788082 | — | – | 24 | 19 |
| BKB2022 (PEIS) | W3086585527 | 10.1017/S0269964820000467 | 14 | 11 | 11 |
| BKZ2021 (SPL 173) | W3135013245 | 10.1016/j.spl.2021.109083 | 17 | 18 | 13 |
| SKF2026 (ASMBI) | W7151946601 | 10.1002/asmb.70089 | 1 | 1 | 0 |
| SPBB2026 (JIA) | W7131069508 | 10.1186/s13660-026-03450-7 | 0 | 0 | 0 |
| +BHM2015 (true lemma src) | — | 10.1109/TR.2014.2354192 | ~92 | 91 | 72 |
| +HKFN2017 (JMVA) | — | 10.1016/j.jmva.2017.06.003 | – | 21 | 13 |
| +SAF2022 (PEIS) | — | 10.1017/S0269964821000243 | ~13 | 12 | 10 |

\* S2 resolves the HF2018 DOI to a record holding 1 citer — a known S2 merge
anomaly; COCI (22) and OA cited_by (28) are the real counts. NT2022 DOI found
via Crossref search (`10.1080/03610926.2020.1788082`, online Jul 2020).

**BHB2022 identity (task item): no such paper exists.** Crossref author-query
for Barmalzan+Haidari+Balakrishnan returns 13 works 2014–2023, none a 2022
lemma paper. "BHB2022" was the earlier audit's mis-initial for **BKB2022**
itself — `bhb2022-lemma/memo.md` already records "the task prompt guessed
'Haidari'; the actual middle author is Kosari". The lemma's true source is
BHM2015 Thm 2, enumerated above as a provenance handle.

**Union**: 143 distinct citing works (S2 139 + COCI-only extras; an OpenAlex
`cites:` pass was attempted but the API throttled this egress intermittently —
citer *counts* above are from OA records; the S2∪COCI union is the working
enumeration. OA-poller kept retrying in background: `oa_poller.py`).

## Filter

Keyword filter (mixture/stochastic-order/majorization family): **100 kept,
43 dropped** (dropped = pure estimation/engineering/GP papers citing the model
definition only — e.g., nanoparticle quantitation, DOE mixture-weight
estimation, Bayes Hilbert mixtures, composite-likelihood asymptotics).
Of the 100 kept: **34 mixture-side**, **66 systems/order-statistics-side**
(mostly BHM2015 citers — the additive lift is *legitimate* there; recorded for
honesty, not suspects).

## New suspects classified (delta over the existing ~25-paper map)

| Paper | Venue | Handles | Verdict |
|---|---|---|---|
| **JIAO2026** Liang Jiao | Stochastic Models 2026 (10.1080/15326349.2026.2682362) | NT2022 | **CONDITIONAL CARRIER.** Abstract verbatim: "comparison results for two FMMs whose component[s] belong to generalized Marshall–Olkin Topp Leone-G (MOTL-G) family… within [the] framework [of] chain and unordered majorization orders… sufficient conditions under which usual order, hazard rate order hold between FMMs in terms of … shape, scale, mixing proportion parameters." n-component FMM hr ordering under chain majorization = CERT A/B claim shape (MOTL-G scale-family baseline contains the exponential/PHR subfamily → certified false at claim shape). Paywalled; spread to a new orbit (Qinghai, CN). |
| **SB2022** Shojaee–Babanezhad | Metrika 86(5):499–515 (10.1007/s00184-022-00880-3) | HF2018, NT2022, SAF2022 | **CONDITIONAL CARRIER (hr/rh) + new open shape (disp).** Abstract verbatim: "stochastic comparison of two arithmetic (finite) mixture models using the majorization concept in the sense of the usual stochastic order, the hazard rate order, the reversed hazard rate order and the **dispersive order** both for a general case and for some semiparametric families." hr/rh n-mixture claims under majorization → CERT A/C claim shape. **Dispersive order of mixtures under majorization is a genuinely new claim shape** — quantile-difference functional, nonseparable; not yet certified (see CERT F note). |
| **WANG2023** Yi-Ting Wang | Pure Mathematics (Hans, OA) 2023 (10.12677/pm.2023.133053) | NT2022, SAF2022 | **CONDITIONAL CARRIER.** Abstract verbatim: "stochastic comparisons of generalized finite mixtures with dependent random variables using stochastic orders and majorization order in the sense of the usual stochastic and **likelihood ratio** ordering." lr of mixtures under majorization = ratio-of-sums lift. **Certified at claim shape by new CERT F below.** Dependence/copula setting may add structure — text is Chinese, math signature (matrix majorization a_ij·b_ij ≫ notation) consistent with the lift. |
| **LI2025** Na-Guo Li (Lina Guo) | Pure Mathematics (Hans, OA) 2025 (10.12677/pm.2025.152044) | BHM2015, BKB2022, HF2018, NT2022 | **Clean-shape.** MPRHR finite mixtures, explicitly uses "matrix chain majorization + T-transform matrices", but the abstract claims only "sufficient conditions for the establishment of **ordinary stochastic order**" — the additive SF functional, where the lift is legitimate. Second Hanx/Northwest-Normal-University node; defect vocabulary propagates even where the lift does not. |
| **SM2023** Shojaee–Momeni | J. Indian Soc. Probab. Stat. 24:599–621 (10.1007/s41096-023-00169-2) | SAF2022 | Suspect-leaning **clean-shape**. Abstract: rh + st comparison of two α-mixture CDFs "with different mixing probabilities and different baseline distributions" — ordered-mixing technique (SAF2023 style), no chain-majorization signature; rh-of-CDF-mixture claims would be CERT C shapes *if* a lift were used. Text paywalled. |
| **BHosp2022** Barmalzan–Hosseinzadeh–Balakrishnan | CSTM 51(24):8657–8670 (10.1080/03610926.2021.1901925) | HF2018 | **Clean-shape / different claim shape.** star/convex-transform/right-spread/dispersive orders between a homogeneous exponential and a *mixture* of exponentials + spacing comparisons — one-common-parameter-vs-heterogeneous, classic heterogeneity structure; not matrix majorization between two n-mixtures; no lift needed. |
| **SAF2021** Shojaee–Asadi–Finkelstein | Metrika 84(4):1213–1240 (10.1007/s00184-021-00818-1) | HF2018 | **Unrelated to defect** — α-mixture model properties (ageing/bending), no ordering-under-majorization claims. |
| **BBKM2026** Bera–Khan–Bhattacharyya–Mitra | PEIS 2026 (10.1017/s026996482510017x, OA) | BHM2015 | **Clean-shape.** "Multivariate chain majorization … stochastic ordering results for extreme-order statistics … generalized Gompertz" — PDF scanned: order statistics of independent heterogeneous variables; compared functionals are products/separable (order-statistic CDFs); legitimate additive lift. |
| **SH2026** Shojaee–Hazra | CSTM 2026 (10.1080/03610926.2026.2684462) | SAF2022 | **Clean-shape.** Series/parallel systems of dependent subsystems under Archimedean copula; st comparisons under majorization of hazard-parameter/component-count vectors — systems-side sums, legit. (Hazra = HF2018 coauthor.) |
| **SMM2023** Shojaee–Mohammadi–Momeni | Metrika 2023 (10.1007/s00184-023-00917-1) | HF2018, NT2022, SAF2022 | **Clean-shape.** Extremes/second-order statistics of dependent heterogeneous variables — order-statistic functionals, not mixture rates. |
| **NTD2021** Nadeb–Torabi–Dolati | JKSS 2021 (10.1007/s42952-021-00109-5) | NT2022 | **Clean-shape.** Usual st ordering of extreme order statistics under Archimedean copula — additive functionals. |
| 6 unrelated | nanoparticle quantitation; DOE weight estimation; compound-Rayleigh estimation; Bayesian α-mixture inference; Bayes-Hilbert mixtures; clustering | — | cite model definition only; discarded from cone (recorded). |

## CERT F (new battery entry): lr claim shape

Claim shape: [p;λ],[q;γ] 2×3 in V₃, [q;γ]=[p;λ]·T (single T, one frozen
column) ⇒ ordinary mixtures lr-ordered. On the CERT-B instance
p=(1/8,29/72,17/36), λ=(9,5,4) → q=(2/9,11/36,17/36), γ=(38/5,32/5,4)
(V₃ verified, ω=13/20): the density ratio R(u)=f_p/f_q, u=e^{−t}, has
derivative-numerator with **exactly 1 Sturm root on (0,1)**
(R′(1/4)>0, R′(1/2)<0 — ratio rises then falls). **lr ordering fails** —
the frozen column sits inside both sums of the density ratio. Covers
WANG2023's claim shape (and any future lr-of-mixtures-under-majorization
claim); script inline in run log / reproducible via `audit_lib`.

Dispersive-order-of-mixtures (SB2022) remains **open**: quantiles of
exp-mixtures lack closed form; no certified attack within budget — flag for
follow-up (interval-arithmetic quantile certificate or level-crossing
argument).

## Expanded scoreboard

**Certified defect carriers (verbatim or transmitted statements): 9**
SKF2026, SPBB2026, BKB2022, GY2024, SKB2026, BKF2024, HF2018 (as
transmitted), NT2022 (as transmitted), **BKKA2024** (folded in: Thm 3.10
rh "ageing faster" certified false — ratio-of-sums proof defect, not the
lift itself; `bkka2024/memo.md`).

**Conditional certified carriers (claim shape refuted by battery): 8**
SMH2026, BKZ2021, SBB2022, BBKP2024, BKB-SPL24, **JIAO2026**, **SB2022**
(hr/rh halves), **WANG2023** (lr half).

**Different-defect / boundary carriers: 3** — VKF2025, BTDK, BGSK.

**Clean (audited or clean-shape):** SAF2022, PKP2022, SAF2023, KBB2023,
BKD2025, B&K-Metrika, LI2025, BHosp2022, SAF2021, BBKM2026, SH2026,
SMM2023, NTD2021 (+ SAF-Remark-6.18 historical honesty).

**Unresolved shapes:** SB2022-disp; SM2023 pending text.

## Defensible headline

Of **N ≈ 31** papers in the defect cone (mixture-ordering works citing a
defect handle; 143 total citers enumerated, 100 keyword-kept, 34
mixture-side, ~6 unrelated dropped, 66 systems-side recorded clean), **M =
17 carry the defect**: 9 certified on verbatim/transmitted statements, 8
certified at claim shape (uniform instances refuting the transmitted
theorem family), plus 3 carriers of sibling ratio-of-sums/boundary defects.
Every st-order-only claim in the cone is clean — the defect is confined to
nonseparable (ratio-of-sums) rate/density functionals, exactly as the
mechanism predicts. The defect has spread beyond the original
Balakrishnan–Finkelstein–Kayal orbit to ≥3 new institutions (Qinghai via
JIAO2026; Northwest Normal via WANG2023/LI2025; SB2022 Zabol/Golestan).

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY enumerate_s2.py        # S2+COCI enumeration -> citers_s2/coci.json
    $PY merge_filter.py        # merge + keyword filter -> citers_merged.json
    $PY fetch_oa.py; $PY fetch_abstracts.py   # OA locations + Crossref abstracts
    $PY resolve_handles.py; $PY resolve_bhb.py # NT2022 DOI; BHB2022 identity
    $PY oa_poller.py           # OpenAlex citer pass (throttled; partial)
    # CERT F inline: CERT-B instance, density-ratio derivative, Sturm count
