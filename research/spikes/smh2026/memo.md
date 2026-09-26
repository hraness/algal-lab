# Audit memo: SMH2026 = Sahoo–Misra–Hazra (2026)

Run dir: `research/spikes/context/runs/smh2026/` (gitignored).
Exact arithmetic via `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy Rational; Sturm `Poly.count_roots` + exact rational witnesses).
Scripts: `certify_smh.py`, `sweep_smh.py`. Audited 2026-09-25.

## Citation (verified via Crossref + OpenAlex)

- **[SMH2026]** T. Sahoo, N. Misra, N. K. Hazra, *On stochastic
  comparisons of mixtures of distributions*, Statistics (2026), pp. 1–28,
  online 2026-04-28. DOI **10.1080/02331888.2026.2661806**.
  (Cluster-map "SMH2026" resolves to this; the alternative reading
  "Shahraki–Mohtashami–Haidari" has no matching record.)
- Authors: Tanmay Sahoo (IIT Palakkad; PhD 2023 IIT Jodhpur under Hazra —
  NOT the same person as SKF2026's Supriya Sahoo, NIT Rourkela);
  Neeraj Misra (IIT Kanpur); Nil Kamal Hazra (IIT Jodhpur) — **Hazra is
  the HF2018 coauthor**, i.e. an author of the probable origin paper.
- Abstract (verbatim, OpenAlex/T&F metadata): "we consider both α-mixture
  of survival functions and α-mixture of cumulative distribution functions.
  We study some stochastic comparison results for α-mixture of ordinary
  distributions. Subsequently, we study the ordering properties of the
  α-mixture of weighted distributions … The results derived in the paper
  generalize many results available in the literature."

## Retrieval status: **UNRETRIEVABLE**

Closed access everywhere checked: T&F (Cloudflare wall, 403), Unpaywall
`is_oa: false`, OpenAlex `oa_status: closed`, Semantic Scholar not indexed,
no arXiv preprint (Tanmay Sahoo has only unrelated 2307.02133, 2510.13174),
Strathprints (Hazra/Misra are not Strathclyde), no T&F figshare
supplementary, IIT Palakkad page lists only the DOI link, ShodhGanga
bot-walled (and the 2023 thesis predates the paper anyway). **0 citations**
(Google Scholar / Semantic Scholar) — no citing paper transmits its
theorem statements, so unlike HF2018/NT2020 there is not even a
transmitted verbatim statement to audit.

## Reference-list forensics (Crossref deposits all 46 refs)

SMH2026 cites, in the defect cone: **HF2018** (10.1007/s11749-018-0581-7,
probable origin of the frozen-column lift), **NT2020**
(10.1080/03610926.2020.1788082, certified carrier), **BKZ2021**
(10.1016/j.spl.2021.109083, suspect), **VAMSG2025**
(10.1080/02331888.2025.2502946, certified different-defect), **BBKP2024**
(10.1080/02331888.2024.2347343, suspect), **HKFN2017**
(10.1016/j.jmva.2017.06.006), Misra–Naqvi 2018 (10.1080/03610926.2018.1445859),
Finkelstein–Esaulova 2006. Model sources: AES2019 (α-mixture of SFs,
10.1017/jpr.2019.72), Shojaee–Momeni 2023 (α-mixture of CDFs,
10.1007/s41096-023-00169-2), SAF-Metrika 2021, SAF2023-CSTM,
B&K-Metrika 2025. Weighted-distribution classics: Rao 1965, Patil,
Gupta–Kirmani 1990, Nanda–Jain 1999, Misra–Gupta–Dhariyal 2008,
Albabtain et al. 2020.

**Notably absent**: BKB2022 and BHM2015 — if SMH2026 carries the defect,
it imports the lift **directly from HF2018** (consistent with Hazra's
authorship), not via the Lemmas-2.4/2.5 handle.

## Claim-shape certificates (all reconstructed — flagged)

The abstract promises ordering results for n-component α-mixtures of SFs
and of CDFs. The two canonical claim shapes of the cited machinery both
fail at n=3, and the certificates are **α-independent**:

For the SF-mixture `F̄_α=(ΣpᵢF̄ᵢ^α)^{1/α}` with exponential components,
`h_α(t)=Σpᵢλᵢu^{λᵢ}/Σpᵢu^{λᵢ}` with `u=e^{−αt}` — the same rational
function for every α>0, so ONE polynomial certificate refutes the hr
claim for all α>0 at once (α=1 = ordinary mixture). For the CDF-mixture
`F_α=(ΣpᵢFᵢ^α)^{1/α}` with power-function components `Fᵢ(t)=t^{λᵢ}` on
(0,1), `r_α(t)=(1/t)·Σpᵢλᵢx^{λᵢ}/Σpᵢx^{λᵢ}` with `x=t^α` — verified
symbolically (CERT C); the same bracket, positive factor `1/t`, so the
SAME sign change refutes rh claims for all α>0.

| Claim shape (source machinery) | Content | Status | Evidence |
|---|---|---|---|
| A: (p,λ),(p,γ)∈U_n, λ≻γ ⇒ hr ordered (NT Thm 4.2 / HF2018 pattern) | n=3 exp α-mixture | **EXACT COUNTEREXAMPLE, all α>0** | CERT A below |
| B: [p;λ]∈V_n, [q;γ]=[p;λ]M_T ⇒ hr ordered (frozen-column lift) | n=3, single T | **EXACT COUNTEREXAMPLE, all α>0** | CERT B below |
| rh analogs for CDF-mixture | n=3 power-function components | **EXACT COUNTEREXAMPLE, all α>0** | same brackets (CERT C) |
| st-order theorems | additive functional ΣpᵢF̄ᵢ^α under monotone outer power | expected clean | lift is legitimate there (whole-cluster pattern) |
| weighted-distribution section | conditional: identity weights recover ordinary mixture | **inherits counterexample** iff it claims n>2 hr/rh ordering under majorization | claim shape only |
| α<0 hr claims | u∈(1,∞) domain | not refuted by CERT A instance (d>0 at u=3/2,2,4) | would need a separate u>1 instance |
| paper's own examples | — | **not-checkable** (no text) | — |

### CERT A (claim shape A, n=3)

    p=(39/86,18/43,11/86) dec; λ=(4,6,9), γ=(4,7,8) inc
    (p,λ),(p,γ)∈U₃, λ≻γ  [all hypotheses verified exactly]
    d(u)=h_λ−h_γ: numerator deg 9, denominator root-free on (0,1),
    Sturm count 2 roots on (0,1]. Witnesses:
      d(1/2)=6271/156247>0   (violates claimed h_λ≤h_γ)
      d(3/4)=−17228781/103906915<0   d(7/8)<0
    ⇒ hazards cross once; ordering fails for EVERY α>0.

### CERT B (claim shape B, n=3, single T, the lift itself)

    p=(1/8,29/72,17/36), λ=(9,5,4) ∈V₃;  T on cols (1,2), ω=13/20
    ⇒ q=(2/9,11/36,17/36), γ=(38/5,32/5,4)   [T verified componentwise;
      third column frozen inside numerator AND denominator of the ratio]
    In w=u^{1/5}: numerator deg 83, Sturm count 2 on (0,1].
    Witnesses: D(1/2)>0, D(7/8)<0 ⇒ crossing; fails for EVERY α>0.

### Sweep counts (claim shape, n=3, 10-pt exact grid, 8000 draws each)

| Claim shape | Admissible | Violations | of which crossings |
|---|---|---|---|
| A: U₃ + λ≻γ ⇒ hr | 208 | **36** | 36 |
| B: V₃ single-T ⇒ hr (claimed direction) | 1926 | **1579** | 108 (1471 uniformly opposite) |
| B: W₃ single-T ⇒ hr | 1855 | **1333** | 1332 |

All counts are α-independent (u=e^{−αt}) and equally refute the rh
claims for the CDF-mixture (x=t^α bracket, CERT C).

## Verdict

**UNRETRIEVABLE → conditional certified carrier.** The paper could not be
read; no theorem statement is transmitted by any citing work (0 citations).
Its own examples are not-checkable. However:

- It is inside the defect cone by reference structure (cites HF2018 +
  NT2020, not BKB2022/BHM2015), coauthored by the origin author.
- IF it contains any n≥3 hazard-rate (resp. reversed-hazard-rate) ordering
  theorem for α-mixtures of SFs (resp. CDFs) under majorization hypotheses
  of shape A or B — the standard form in every cited sibling — that
  theorem is **false**, by the α-independent certificates above.
- Any st-ordering theorems are expected clean (legitimate additive lift).
- Verdict in scoreboard terms: mark **suspect — reconstructed claims
  certified false at shape; verbatim statements unverifiable**. Upgrade to
  certified carrier requires the text (interlibrary loan or author eprint).

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY certify_smh.py    # certificates A, B, C
    $PY sweep_smh.py      # admissible/violation counts at claim shape
