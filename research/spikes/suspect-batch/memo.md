# Claim-shape audit: the paywalled suspect queue

Run dir: `research/spikes/context/runs/suspect-batch/` (gitignored).
Exact arithmetic: `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy Rational; Sturm `Poly.count_roots` + exact rational witnesses).
Script: `certify_batch.py` → `certify_out.txt`. Audited 2026-09-25.
Method = the SMH2026 "conditional claim-shape" audit: verbatim abstracts +
what later citers transmit + certified counterexamples to the standard
n≥3 claim shapes.

## The shared certificate battery

| Cert | Claim shape refuted | Instance | Result |
|---|---|---|---|
| A | (p,λ),(p,γ)∈U₃, λ≻γ ⇒ hr ordered | p=(39/86,18/43,11/86) dec; λ=(4,6,9), γ=(4,7,8) | **FAILS** — num deg 9, Sturm 2 roots on (0,1]; d(1/2)>0, d(3/4)<0: hazards cross. α-independent (u=e^{−αt}); covers ordinary, PHR, α-mixture (∀α>0), and Weibull (u=e^{−t^k}) subfamilies |
| B | [p;λ]∈V₃, [q;γ]=[p;λ]M_T (single T) ⇒ hr ordered | T on cols (1,2), ω=13/20, third column frozen | **FAILS** — deg 83 numerator, Sturm 2 roots; the frozen column sits inside numerator AND denominator |
| C | rh-order claim shapes | r_α(t)=(1/t)·bracket(t^α), symbolic | identity **verified** ⇒ A/B refute rh claims too |
| D | multiple-outlier rh order under majorization | n=3, groups (2,1), equal weights, power-function CDFs | **1836 crossing pairs**; minimal λ_A=(1,1,2) vs λ_B=(1,1,3) — a *componentwise increase* — yet rh rates cross (signs +,−,− at u=1/4,1/2,9/10). Covers ordinary + α-CDF-mixture readings of δ-mixture |
| E | generalized-Lehmann hr order under U₃+majorization | h_GL(t)=Σpᵢθᵢt^{θᵢ−1}/Σpᵢ(1−t^{θᵢ}) (Fᵢ=t^{θᵢ} = GL/uniform subfamily) | **234 crossings**; first θ=(1,1,4)≻η=(1,2,3), p=(2/5,2/5,1/5) |

Baselines used (exponential, power-function/uniform-Lehmann, Weibull) are
the standard admissible examples of this literature — power functions are
DRHR and log-concave, so they satisfy the usual baseline-side hypotheses.

## Per-paper scoreboard

| Key | Verified identity | Abstract | Transmitted claim shape | Verdict | Minimal certificate |
|---|---|---|---|---|---|
| **BKZ2021** | Barmalzan–Kosari–Zhang, *On stochastic comparisons of finite α-mixture models*, SPL 173:109083 (Jun 2021), DOI 10.1016/j.spl.2021.109083; ~17–18 citers | verbatim (Sem. Scholar): "Sufficient conditions on the underlying distribution parameters and the mixing probabilities are established for the comparisons of different α-mixtures of survival or distribution functions with respect to the usual stochastic order and the (reversed) hazard rate order." | SKF2026 l.202: "obtained usual stochastic, hazard rate and reversed hazard rate orders between two finite α-mixture models… baseline G(.;θ)" | **conditional certified carrier** (hr+rh at n≥3) | CERT A (hr, all α>0); CERT B (matrix-change); CERT C (rh). st claims expected clean (additive lift) |
| **SBB2022** | Sattari–Barmalzan–Balakrishnan, *…with generalized Lehmann distributed components*, CSTM 51(22):7767–7782, online 3 Feb 2021, DOI 10.1080/03610926.2021.1880592; 8 citers | verbatim (OpenAlex): "…stochastic comparison results for two finite mixtures models with components having generalized Lehmann distribution." | GY2024 l.88 (verbatim): "usual stochastic order, hazard rate order and likelihood ratio order of finite mixture models with generalized Lehmann distributed components **through chain majorization**"; BHKKB2025, BKF2024, BKKA2024 concur | **conditional certified carrier** (hr at n≥3; lr inherits since lr⇒hr on shared hypotheses) | CERT E (GL-hr crossing; 234 instances); CERT B for the chain-majorization/matrix-change claims. st clean |
| **PKP2022** | Panja–Kundu–Pradhan, *On stochastic comparisons of finite mixture models*, Stoch. Models 38(2):190–213, online 20 Oct 2021, DOI 10.1080/15326349.2021.1987264; ~12–13 citers | verbatim (OpenAlex): "…stochastic comparison results for two finite mixture models where the corresponding random variables follow one of the parental families of distributions, namely, proportional odds, proportional hazards, and proportional reversed hazards." | GY2024 l.993 (verbatim): PKP's hr results are **two-component** ("we generalize some results of the hazard rate order of two-component mixture models into n(>2)…"); l.1137: PKP's n-component results are **star order and Lorenz order** | **probably clean-shape for the defect cone** (n=2 hr theorems are the true base case; n-component claims are star/Lorenz — a different order family outside this battery); st via additive lift legitimate | residual: any n≥3 hr/rh claim under majorization is refuted by CERT A/B; star/Lorenz claims not covered |
| **BBKP2024** | Bhakta–Balakrishnan–Kayal–Pradhan, *…with generalized Weibull distributed components*, Statistics 58(3):552–575, online 3 May 2024, DOI 10.1080/02331888.2024.2347343; 2 citers | verbatim (OpenAlex): "…usual stochastic order, hazard rate order, and likelihood ratio order… generalized Weibull… conditions are mainly based on the majorization order, weak supermajorization order, and weak submajorization order… heterogeneity in one (model) parameter, and then in two parameters (model parameter and mixing proportion)… generalized… to τ-mixture models." | abstract alone carries the matrix-change signature ("heterogeneity in two parameters" = the [p;λ]→[q;γ] lift) | **conditional certified carrier** (hr at n≥3 in the Weibull subfamily; lr inherits) | CERT A under u=e^{−t^k} (Weibull nests inside every standard "generalized Weibull"); CERT B for the two-parameter claims. st + unordered-majorization st claims clean |
| **BKB-SPL24** | Bhakta–Kayal–Balakrishnan, *Ordering results between two multiple-outlier finite δ-mixtures*, SPL 213:110193 (Oct 2024), DOI 10.1016/j.spl.2024.110193; 3 citers | verbatim (ScienceDirect/RePEc): "…sufficient conditions for comparing two multiple-outlier (M-O) finite δ-mixtures based on the usual stochastic order and reversed hazard rate order… general parametric family…" Keywords: *Majorization order* | SKB2026 [22]: "conditions ensuring usual stochastic and reversed hazard rate orderings for multiple-outlier FαMMs" | **conditional certified carrier** (rh at n=3 M-O) | CERT D: λ_A=(1,1,2) vs λ_B=(1,1,3), p=(1/3,1/3,1/3), groups (2,1), power-function CDFs — rh rates cross although the parameter increase is componentwise; 1836 such pairs found. st clean |
| **VAMSG2025** | = **VKF2025** (identity confirmed: same DOI 10.1080/02331888.2025.2502946, Statistics 59(5):1278–1300, Varghese–Ameen Mahmood–Sarkar–Ghosh–Majumder). "VAMSG" is the author-initial key; "VKF" the earlier task key | verbatim (OpenAlex): "…α-mixture… usual stochastic order, hazard rate order, and reverse hazard rate order… location-scale family" | SKF2026: Thm 3.4 "improved version of Theorem 3.1(ii) of Varghese et al." | **already audited, different defect** — scale-vector st claims fail iff αγ>1 (sharp boundary; ~2050/10,200 admissible violate above it); not the frozen-column lift | `vkf2025/certify_r1.py` (Lomax baseline, α=γ=2); not re-run |
| **SAF2023-CSTM** | Shojaee–Asadi–Finkelstein, *On the hazard rate of α-mixture of survival functions*, CSTM 53(11):4062–4084, DOI 10.1080/03610926.2023.2172586; ~8 citers | verbatim (Sem. Scholar): "…hazard rate of α-mixture in terms of hazard rates of mixed baseline distributions… additive or multiplicative models… an inverse problem… α-mixture hazard rate ordering for the ordered **mixing distributions** in the sense of likelihood ratio order… dispersive ordering… hazard rate tends to the strongest/weakest population as α→±∞." | SKB2026 ref-list only; SMH2026 cites it; no theorem-level transmission found | **clean-shape for the defect cone** — the ordering method is lr-ordered *mixing distributions* (the Navarro/Finkelstein–Esaulova component-wise technique), not parameter-matrix majorization; consistent with SAF2022's Rem 6.18 caution | none needed; st/dispersive claims outside this battery but carry no lift signature |

## Notes on the battery's coverage

- **CERT A's α-independence** (u=e^{−αt}) means one polynomial refutes the hr
  claim shape for *every* α>0 α-mixture, the ordinary mixture (α=1), PHR
  mixtures (s=F̄(t)), and Weibull subfamilies (u=e^{−t^k}) simultaneously;
  CERT C converts it to rh of CDF/α-mixtures verbatim.
- **CERT E was needed separately for SBB2022** because generalized-Lehmann
  components (F_i=F^{θᵢ}) put the parameters in the denominator's
  complement — the CERT A numerator does not cross under the GL expression
  (Sturm 1 root = endpoint; all probes positive), but a 234-hit exact
  search supplies clean crossings.
- **CERT D's minimal pair is stronger than needed**: a componentwise
  parameter increase that still produces crossing rh rates refutes the M-O
  rh claim in *both* directions and under every majorization variant these
  instances satisfy (weak-sub on the 3-vector and on the 2-vector of
  distinct parameters).
- Verdicts are "conditional" because all six texts are paywalled (T&F/
  Elsevier bot-walled; Unpaywall `is_oa:false` for every target; no
  preprints found). What is certified is the *standard claim shape* each
  abstract/citer transmits — upgrade to "certified carrier" requires the
  printed theorem statements.

## Retrieval log

- Crossref `api.crossref.org/works/<doi>` — all 6 DOIs resolved (titles,
  vol/issue/page, dates; no deposited abstracts).
- OpenAlex — abstracts for SBB2022, PKP2022, BBKP2024, VAMSG2025; BKZ2021
  and BKB-SPL24 carry none (Elsevier doesn't deposit); rate limit hit
  mid-session (shared-IP budget exhausted).
- Semantic Scholar — BKZ2021 and SAF2023-CSTM abstracts.
- ScienceDirect PII page + RePEc `ideas.repec.org/a/eee/stapro/…` —
  BKB-SPL24 abstract verbatim + keywords.
- SAF2023 Crossref reference deposit is unstructured/empty (30 refs, only
  2 parseable) — its cluster citations could not be enumerated this way.
- Citers grepped: `hf2018-deep/skf2026.txt`, `hf2018-deep/bkf2024.txt`,
  `shekari2026/shekari2026.txt`, `gy2024-skb2026/skb2026.txt`,
  `gy2024-skb2026/gy2024.txt`, `bkka2024/bkka2024.txt`,
  `bhb2022-own/bhkkb2025.txt`, `btdk-arxiv/paper.txt`,
  `mixture-claim-audit/SAF2022.txt`.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY certify_batch.py    # CERTS A–E; ~5 min (CERT D/E are exact searches)
