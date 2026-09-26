# Citation map: the broken-lift cluster

Run dir: `research/spikes/context/runs/cluster-map/` (gitignored). Compiled from
Crossref "cited by" blocks (Cambridge/Wiley/ScienceDirect pages), Semantic Scholar
citation counts, scite.ai, MaRDI/zbMATH records, and arXiv. A scripted OpenAlex
`works?filter=cites:W…` pass remains as a completeness check — DOIs below resolve
directly via `openalex.org/works/doi:<doi>`.

## The defect (one line)

BKB2022 Lemmas 2.4/2.5 (= BHM2015 Thm 2) justify φ(A)≤φ(B) under (multivariate)
chain majorization for **additive** φ(A)=Σ_i ψ(a_1i,a_2i). The n-component lift is
then silently applied to a **ratio of sums** (mixture hazard/reversed-hazard rate)
by "freezing" the n−2 untouched columns and invoking the n=2 theorem — invalid,
since the frozen columns sit inside both numerator and denominator of the ratio.
Certified defect carriers so far: SKF2026 (Thms 3.8–3.12, Cors 3.2–3.3), SPBB2026
(Thm 11, Cor 2, Thm 12 — plus a second, vacuity defect), BKB2022 Thm 2 itself
(LS counterexample, shekari-audit Finding 5). The n=2 base lemmas are TRUE.

## Anchor records (verified)

| Key | Authors | Title | Venue | DOI / ID | OA? | Cites (SS count) |
|---|---|---|---|---|---|---|
| BHM2015 | Balakrishnan, Haidari, Masoumifard | Stochastic comparisons of series and parallel systems with generalized exponential components | IEEE Trans. Reliab. 64(1):333–348, 2015 | 10.1109/TR.2014.2354192 (NOT ...2336691) | paywalled | ~92 |
| HF2018 | Hazra, Finkelstein | On stochastic comparisons of finite mixtures for some semiparametric families of distributions | TEST 27(4):988–1006, 2018 | 10.1007/s11749-018-0581-7 | paywalled (Strathprints AM likely exists) | ~26 |
| BKB2022 | Barmalzan, Kosari, Balakrishnan | Orderings of finite mixture models with location-scale distributed components | PEIS 36(2):461–481, 2022 (online Sep 2020) | 10.1017/S0269964820000467 | paywalled | ~15–20 |
| SAF2022 | Shojaee, Asadi, Finkelstein | Stochastic properties of generalized finite α-mixtures | PEIS 36(4):1055–1079, 2022 | 10.1017/S0269964821000243 | Strathprints 79140 | ~11–13 |
| SKF2026 | Sahoo, Kayal, Finkelstein | Stochastic ordering results between two finite α-mixture models with resilience-scaled components | ASMBI 42(2):e70089, 2026 | 10.1002/asmb.70089 | Strathprints 96227 | 1 (self-cite SKB2026) |
| SPBB2026 | Shekari, Pakdaman, Saadat Kia Barmalzan, Balakrishnan | Stochastic comparisons of finite mixture models derived from distorted distributions: vector and multivariate chain majorization | J. Inequal. Appl. 2026:28 | 10.1186/s13660-026-03450-7 | OA (CC BY-NC-ND) | 0 |

## The citation subgraph

### Layer 0 — background machinery (clean)
- Marshall–Olkin–Arnold (1979/2011): chain majorization ⇔ T-transform chains;
  additive-φ comparison is genuinely Schur-theoretic. VALID.
- Systems lineage (lift is legitimately additive there — series-system hazard is
  Σ h_i, a sum, not a ratio): Dykstra–Kochar–Rojo 1997 (JSPI 65(2):203–211);
  Khaledi–Kochar 2000; Joo–Mi 2010; Zhao–Balakrishnan 2011; → BHM2015 Thm 2
  (the 2×n iff criterion everyone cites; VALID as stated); HKFN2017 = Hazra,
  Kuiti, Finkelstein, Nanda, JMVA 160:31–41 (max order statistics, LS family).
- Older mixture-ordering work by DIFFERENT (component-wise ordering) techniques —
  not in the defect cone: Finkelstein–Esaulova 2006 (CSTM 35(11)); Navarro–
  Hernández 2008; Navarro et al. 2013; Navarro 2016; Amini-Seresht & Zhang 2017
  (ORL 45(5):475–480, ordered baselines); Navarro & del Águila 2017.
- Model sources: AES2019 (Asadi–Ebrahimi–Soofi, JAP 56(4):1151–1167 — the
  α-mixture definition); BBH2017 (Balakrishnan–Barmalzan–Haidari, JKSS
  47(1):127–138 — the MPHR/MPRHR model).

### Layer 1 — candidate first misuse (backward edge of the cluster)
- **HF2018 (TEST)** — first paper importing *multivariate chain majorization*
  into mixture-model hr/rh comparisons (PH/AL/PRH families). SPBB2026 Rem 11
  claims its defective Thm 11 "recovers HF2018 Thms 3.6/3.10"; SKF2026 defers
  Thm 3.9/3.12 proofs to "HF2018 Thm 3.4". If HF2018's proofs contain the
  frozen-column lift, the error dates to 2018 and everything below inherits it.
  MUST READ — not yet retrieved (paywalled; check Strathprints for Finkelstein's AM).

### Layer 2 — early propagation (2020–2022)
| Paper | Venue | online | Anchors cited | hr/rh claims via lift? | Status |
|---|---|---|---|---|---|
| Nadeb–Torabi | Comm. Statist. Theory Methods 51(10):3104–3119 | Jul 2020 | HF2018 | hr + disp for PHR model | suspect — check proof method |
| **BKB2022** (anchor) | PEIS 36(2) | Sep 2020 | BHM2015 (Lem 2.4/2.5 ← Thm 2) | rh order, matrix change | **DEFECTIVE (certified)** |
| Barmalzan–Kosari–Zhang | Statist. Probab. Lett. 173:109083 | Mar 2021 | AES2019, ASZ2017, NT2022 | α-mixture st + hr/rh | suspect — check |
| Sattari–Barmalzan–Balakrishnan | CSTM (10.1080/03610926.2021.1880592) | Feb 2021 | ASZ2017, BHM2015, HF2018 | gen. Lehmann mixtures "through chain majorization" | suspect |
| Panja–Kundu–Pradhan | Stochastic Models 38(2):190–213 | Oct 2021 | BKB2022, HF2018, ASZ2017 | prop. odds/PH/PRH mixtures, multivariate majorization | suspect |
| **SAF2022** (anchor) | PEIS 36(4) | Jul 2021 | HF2018, NT2022, AES2019 | hr n=2 only; **n>2 left as open problem (Rem 6.18)** | **CLEAN (audited)** |
| Kayal–Bhakta–Balakrishnan | Stochastic Models 39(2):363–382 | 2022 | BHM2015, BKB2022, BKZ2021 | **st order only** | probably clean |

### Layer 3 — the avalanche (2023–2026), mostly NIT-Rourkela (Kayal) + Balakrishnan/Finkelstein orbit
| Paper | Venue/ID | Anchors cited | Orders claimed | Status |
|---|---|---|---|---|
| Shojaee–Asadi–Finkelstein 2023 | CSTM 53(11):4062–4084 | SAF2022 | hazard-rate shape of α-mixtures | check (n>2 hr claims?) |
| Bhakta–Majumder–Kayal–Balakrishnan | Metrika 87(6):681–712, 2024 | BKB2022, KBB2023 | "hr + rh when a **matrix** of parameters changes" | **prime suspect** |
| Bhakta–Kayal–Finkelstein | Methodol. Comput. Appl. Probab. 26(4), 2024 | HF2018, NT2022, BKZ2021, BKB2022, SBB2022, KBB2023 | LS family: st + hr + rh + lr, two-parameter heterogeneity | **prime suspect (direct BKB2022 descendant)** |
| Bhakta–Kayal–Balakrishnan | SPL 213:110193, 2024 | BKB2022, BMKB2024 | multiple-outlier δ-mixtures: st + **rh** | suspect |
| Bhakta–Balakrishnan–Kayal–Pradhan | Statistics 58(3):552, 2024 | PKP2022, KBB2023, BKB2022 | gen-Weibull: st + **hr** + lr, 2-param heterogeneity | suspect |
| Bhakta–Kundu–Kayal–Alizadeh | Mathematics 12(6):852, 2024 (OA) + arXiv:2311.17568 | Navarro, ASZ2017, HF2018, BKZ2021, BKB2022, NT2022, PKP2022, KBB2023 | inv-Kumaraswamy: st + **rh (ageing-faster)** + lr | suspect |
| Bhakta–Kundu–Kayal | Sankhya B 87(2):573–603, 2025 | BKZ2021, BKF2024 | ELS components: **st only** per abstract | probably clean |
| Bhakta–Kayal | Metrika (10.1007/s00184-025-00996-2; RePEc lists 88(6):1523–1539 Aug 2025 AND 89(2):143–159 Feb 2026 — same DOI, likely one paper) | BKB2022, BKZ2021, KBB2023, BMKB2024 | α-mixture, general components: **st only** | probably clean |
| Guo–Yan | arXiv:2407.15638v2 (Jul 2024; OA) | HF2018, SBB2022, Navarro–Hernández | MPHR mixtures: st + **hr under chain majorization**, explicit "different settings of T-transform" | **prime suspect; open access — checkable today** |
| Varghese–Ameen Mahmood–Sarkar–Ghosh–Majumder | Statistics 59(5):1278–1300, 2025 | SAF2023, BKF2024, KBB2023, BMKB2024, BKZ2021 | α-mixture LS: st + hr + rh | suspect (IISER-TVM: spread beyond original orbit) |
| Bhakta–Torrado–Das–Kayal | arXiv:2412.10071 (Dec 2024) | HF2018 … cluster | arithmetic M-O mixtures, LS | suspect |
| **SKF2026** (anchor) | ASMBI 42(2):e70089 | BKB2022 (Lem 2.4/2.5), HF2018 (Thm 3.4), SAF2022, AES2019 | st + hr + rh, all order types | **CERTIFIED DEFECTIVE** |
| **SPBB2026** (anchor) | JIA 2026:28 | BHM2015 (Thm 2 = Lemma 7), BKB2022, HF2018 (Rem 11), Guo–Yan, +Shekari order-stats papers | distorted mixtures: st + hr + rh + disp | **CERTIFIED DEFECTIVE + vacuous hypotheses** |
| Sahoo–Kayal–Balakrishnan | Mathematics 14(14):2557, 2026 (OA) | SKF2026 [25], BKB-cluster [24] | MPHR α-mixtures, "vector and chain majorization" | **prime suspect (most recent)** |
| Sahoo–Misra–Hazra | Statistics (10.1080/02331888.2026.2661806, Apr 2026) | SAF2023, B&K-Metrika | α-mixtures of SFs/DFs + weighted dists | check (Hazra = HF2018 coauthor) |
| Bhakta–Gupta–Saadat Kia–Kayal | arXiv:2511.00791 (Nov 2025) | full cluster genealogy | ELS single/M-O mixtures: st + rh + lr | suspect |

### Peripheral citers — different methods, out of the defect cone
- Simone 2022 (TEST 31(3):828–855, discretized-beta ordinal mixtures — cites BKB2022 in review only);
- Albabtain et al. 2020 (Weibull mixtures via weight functions); Bansal–Gupta 2019
  (copula multivariate mixtures); Shekari–Pakdaman–Barmalzan–Balakrishnan 2025
  (JIA, order statistics — separable functionals, lift legit).

## Backward provenance of the lift

MOA chain majorization (T-transforms, 1979) → systems-side matrix-comparison
criteria (DKR1997 → Khaledi–Kochar → Joo–Mi → Zhao–Balakrishnan → **BHM2015 Thm 2**,
the canonical 2×n criterion, valid because system functionals are sums/products)
→ HKFN2017 (JMVA, LS max order statistics) → **imported to mixtures by HF2018**
(first multivariate-chain-majorization mixture paper) → **BKB2022** restates it as
Lemmas 2.4/2.5 (the citation handle everyone uses) → BKZ2021, SBB2022, NT2022,
PKP2022 → Bhakta/Kayal avalanche 2023–2026 → SKF2026, SPBB2026, SKB2026.

## Propagation history (one paragraph)

The lemma itself is fine — it is the standard T-transform criterion for additive
Schur functionals, proved for systems (series/parallel lifetimes, where the
compared quantities are sums or products) by BHM2015 (Thm 2, IEEE TR 2015), which
itself descends from the exponential-systems majorization line of Dykstra–Kochar–
Rojo (1997). The defect is born at the boundary between systems and mixtures:
a mixture hazard rate is a ratio of sums, not a sum, so the frozen-column lift is
invalid — and the ordering is not merely unproved but false. The first plausible
misuse is Hazra–Finkelstein (TEST 2018), whose chain-majorization hr/rh theorems
for semiparametric mixtures (Thms 3.4/3.6/3.10) are the named source for SKF2026's
deferred proofs and for SPBB2026's claimed recoveries — confirmation requires
reading the paywalled paper. BKB2022 (online Sep 2020; certified false by the
shekari audit's LS counterexample) then canonized the misuse, supplying the
"Lemmas 2.4/2.5" handle that Nadeb–Torabi (Jul 2020 online — possibly earlier than
BKB!), Barmalzan–Kosari–Zhang (SPL 2021), Sattari–Barmalzan–Balakrishnan (2021),
Panja–Kundu–Pradhan (2021) and the entire Bhakta–Kayal cluster (≥8 papers,
2023–2026) propagated across baseline families — LS, general, δ-, α-, MPHR,
ELS, distorted — with Finkelstein and Balakrishnan on both sides of the citation
edges. SAF2022 is the notable non-carrier: it posed the n>2 hazard-ordering as an
open problem rather than claiming it — and the answer turned out to be negative.

## Prioritized audit queue (highest value first)

1. **HF2018 Thm 3.4/3.6/3.10** (TEST; paywalled — try Strathprints AM, else
   interlibrary). Decides whether the defect is born 2018; its theorems are the
   upstream source SKF/SPBB appeal to. Baseline exp/PHR instance check is cheap
   once the statement is in hand (reuse `mixture-audit/audit_lib.py`).
2. **BKF2024** (Methodol. Comput. Appl. Probab. 26(4)) — same LS model as
   BKB2022 + Finkelstein coauthor; its two-parameter hr/rh theorems are the most
   likely verbatim carriers.
3. **BKZ2021** (SPL 173:109083) — the α-mixture bridge by the BKB authors.
4. **Guo–Yan 2024** (arXiv:2407.15638, OA HTML) — checkable today; hr claims
   under explicit T-transform settings for MPHR mixtures.
5. **Sahoo–Kayal–Balakrishnan 2026** (Mathematics 14:2557, OA) — newest node;
   cites SKF2026; MPHR α-mixture chain-majorization theorems.
6. **Nadeb–Torabi 2022** (CSTM) — online Jul 2020, *earlier* than BKB2022's
   online date: if its PHR-model hr theorems use the lift, it may outrank BKB2022
   as second-misuse (after HF2018).
7. **BMKB2024** (Metrika 87:681–712, Bhakta–**Majumder**–Kayal–
   Balakrishnan) — **RESOLVED: probable clean / lift-disciplined**.
   Citers transmit n≥3 claims only in the additive st domain; its rate
   theorems recover as n=2 via SPBB Thm 8. Not the lift's entry point
   (postdates all of Layer 2); a consolidation node. Majumder is the
   authorial bridge to VKF2025. Residual: if its paywalled rh
   matrix-change theorems are stated at general n, CERT B/C apply.
8. **Varghese et al. 2025** (Statistics) — demonstrates spread to a second
   institution (IISER-TVM); hr+rh for α-mixture LS.
9. Second tier: SBB2022, PKP2022, BKB2024-SPL, BBKP2024, BKKA2024, SMH2026,
   BTDK-2412.10071, BGSK-2511.00791, SAF2023-CSTM.
10. Expected-clean control set (verify st-only): KBB2023, BKD2025-Sankhya,
    B&K-Metrika, ASZ2017, Navarro line.

## Notes / gaps

- Citation counts (Semantic Scholar, retrieved ~Oct 2026): BHM2015 ~92 (mostly
  systems papers — that literature is fine, the additive lift is *legitimate*
  there); HF2018 ~26; BKB2022 ~15–20; BKZ2021 ~17; SAF2022 ~11–13; SKF2026 1;
  SPBB2026 0; SKB2026 0.
- Every "suspect" shares the signature: st/hr/rh ordering claims for n-component
  mixtures under chain/matrix majorization via "a matrix of parameters changes to
  another" phrasing. The n=2 instances are the control (correct); audit = check
  whether proofs invoke the 2-column lemma with n−2 frozen columns.
- Authorship pattern: Kayal (NIT Rourkela) is the hub node of the 2023–2026
  avalanche (students Bhakta, Sahoo, coauthors Alizadeh, Majumder, Pradhan, Das,
  Torrado, Gupta); Saadat Kia = Ghobad Barmalzan (same person, alternate name);
  Balakrishnan and Finkelstein recur as senior coauthors on BOTH the lemma source
  and its misuses — good for the story's "referee network" angle.
- Corrections to earlier records: BHM2015's DOI is 10.1109/TR.2014.2354192 (not
  ...2336691); SAF2022 is PEIS 36(4):1055–1079 (not JAP 60(3) — that was a
  conflation); SKF2026's version of record is ASMBI 42(2):e70089.
