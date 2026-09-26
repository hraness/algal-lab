# Cluster audit: the broken T-transform lift across the mixture-ordering literature

Synthesis of the exact-arithmetic audits in `research/spikes/` (run dirs
under `research/spikes/context/runs/`). Compiled 25 September 2026.

## The defect in one paragraph

Chain majorization of a 2×n parameter matrix is equivalent to a chain of
T-transforms; for **additive** functionals Φ(A)=Σᵢψ(a₁ᵢ,a₂ᵢ) a standard
lemma (Marshall–Olkin–Arnold; proved for systems in Balakrishnan–Haidari–
Masoumifard 2015, Thm 2; restated as BKB2022 Lemmas 2.4–2.5) reduces the
n-component comparison to the n=2 criterion. Mixture hazard and
reversed-hazard rates are **ratios of sums**
h(t)=Σᵢpᵢgᵢ(t)/ΣᵢpᵢGᵢ(t)-shaped kernels — the frozen columns sit inside
*both* numerator and denominator — so the lift does not apply. The audited
papers apply it anyway. The lemma is true; the use is false; the resulting
orderings are not merely unproved but fail on certified instances.

## Scoreboard (as of 25 September 2026)

| Paper | Venue | Certified | Mechanism |
|---|---|---|---|
| **SKF2026** Sahoo–Kayal–Finkelstein | ASMBI 42(2):e70089 | Thms 3.4, 3.8 (both halves), 3.9, 3.10 (literal), 3.11 (both), 3.12; Cors 3.2, 3.3; **2 printed counterexamples invalid** | lift on α-mixture hr/rh |
| **SPBB2026** Shekari et al. | J. Inequal. Appl. 2026:28 (OA) | Thm 11 (Sturm 2 roots), Cor 2, Thm 12, Cor 3; **all hr/rh theorems also vacuous** — hypothesis `-D'(u;γ)` monotone in γ cannot hold for any γ-dependent family (∫D′=1) | lift + unsatisfiable hypotheses |
| **BKB2022** Barmalzan–Kosari–Balakrishnan | PEIS 36(2):461–481 | Thm 2 (n≥3 rate ordering): crossings certified in both directions, both V/W classes, both conventions; n=2 Thms 1/5 also fail at the unconditional claim shape | the canonized misuse |
| **GY2024** Guo & Yan | arXiv:2407.15638v2 | Thm 6 / Cor 5 (48% violation at n=3), Cor 6 (2-step chain); Thm 6 has **no proof** ("Similarly… we can get the result") | lift on MPHR hr |
| **SKB2026** Sahoo–Kayal–Balakrishnan | Mathematics 14:2557 (OA) | Thms 8, 9, 11, 12 + MPRHR duals 20/21/23/24 + Cors 1–4; lift stated verbatim | lift on MPHR α-mixture |
| **BKF2024** Bhakta–Kayal–Finkelstein | MCAP 26(4):52 | Thms 2 (printed glyph), 3, 4 (whole cell), 5 (missing hypothesis), 6, 8; **Lemma 1 printed wrong direction**; printed Cex 1,2,3,5 are FP noise at identically-zero points, Cex 4 contradicted | hr/rh claims; st theorems clean |
| **VKF2025** Varghese–Ameen Mahmood et al. | Statistics 59(5) | Scale-vector st claims fail **iff αγ>1** (sharp boundary: 0/~10,200 admissible below, ~2050 above); a different defect — T14 Schur-concavity on the wrong side | boundary violation |
| **HF2018** Hazra & Finkelstein | TEST 27(4) | transmitted Thm 3.4 (via SKF2026) fails at n=3 already for **ordinary** mixtures (certified); probable **origin** of the defect | lift on ordinary mixtures |
| **NT2020** Nadeb & Torabi | CSTM 51(10) | transmitted Thm 4.2 fails at n=3; NT Thm 3.2 holds-on-samples | same lift |

**Controls (clean)**: every n=2 base theorem across all audited papers;
all st-order theorems (the mixture SF is a separable sum — the lift is
legitimate there); SAF2022 — audited clean *and* historically clean: its
Remark 6.18 posed n>2 hazard ordering as an open problem, answered
negatively by the certified exponential-mixture counterexample
(`hf2018-nt2020/certify_nt42_n3.py`).

**Not yet read (paywalled, statements reconstructed or unrecoverable)**:
HF2018, NT2020, BKB2022, VKF2025 — claims against them are audited "as
transmitted" or "at claim shape"; each memo marks exactly which. For
HF2018 the statement-level attribution is now pinned by two OA witnesses:
SKF2026's AAM quotes verbatim "The proof follows from Theorem 3.4 of
Hazra and Finkelstein (2018)", and SPBB2026's theorem-number map places
the n-component T-chain hr claim at HF §3 — so the defect originates in
2018 at statement level (verbatim proof text unretrieved).

**Audited, different defect family**: BTDK arXiv:2412.10071 (Bhakta–
Torrado–Das–Kayal, multiple-outlier two-group mixtures — no chain
majorization at all). Certified: Thm 4.2 st fails (the cluster's first
broken st claim), Thm 4.3-E hr, Thm 4.5-D lr; vacuity cases (4.1
satisfiable only under reversed direction; 4.4-E impossible); clean:
4.3-D, 4.4-D, plus the additive-lift st lemmas used legitimately.

**Audited, not a carrier, different defect**: BGSK arXiv:2511.00791
(Bhakta–Gupta–Saadat Kia–Kayal, general exponentiated location-scale
mixtures — vector majorization only, applied to the additive CDF
legitimately). Certified false anyway: Thm 4.2 (lr — the term-wise sign
step `(1/λ₁)f'/f ≤ (1/λ₂)f'/f` fails when `f'/f<0`), Thm 4.3 (R−rh AFO —
Sturm: exactly 1 root on (2,∞), and the printed Def 2.2 contradicts the
proof's direction, so the claim fails under both readings). All 7
examples + 9 printed counterexamples verify.

**Conditional certified carrier**: SMH2026 (Sahoo–Misra–Hazra, Statistics
2026, DOI 10.1080/02331888.2026.2661806 — text unretrievable, zero
citers). The abstract's n-component α-mixture hr/rh claims are refuted by
certificates uniform in α>0 (n=3: 36/208 on the HF-pattern claim,
1579/1926 on the lift claim). Hazra — HF2018 coauthor and probable defect
origin — is a coauthor: the lineage persists at the source.

## Suspect queue — resolved (`suspect-batch/`)

The ~12-paper queue is now fully classified (all verdicts conditional at
claim-shape level where texts are paywalled):

- **Conditional certified carriers (4 more)**: BKZ2021 (SPL 173:109083 —
  the BKB authors' own α-mixture bridge), SBB2022 (CSTM — generalized
  Lehmann, CERT E needed a dedicated certificate), BBKP2024 (Statistics
  — gen-Weibull), BKB-SPL24 (SPL — multiple-outlier δ-mixtures; the rh
  claim fails even under a *componentwise parameter increase*, 1836
  crossing pairs).
- **Clean-shape**: PKP2022 (n-component results are star/Lorenz orders —
  a different order family; its hr theorems are genuinely n=2), SAF2023
  (orders by lr-ordered *mixing distributions* — a different technique).
- **Identity fold**: VAMSG2025 = VKF2025.
- **Elsewhere in this file**: BKF2024 (certified verbatim), BKKA2024
  (under audit), SMH2026 (conditional), BTDK/BGSK (different families).

Certificate battery (CERT A–E, `suspect-batch/certify_batch.py`): a
single polynomial in u=e^{−αt} refutes the standard n≥3 hr claim for
every α-mixture, ordinary mixture, PHR mixture, and Weibull subfamily at
once; the rh duality converts it verbatim.


## Printed-evidence sweep (`example-sweep/`)

Of the 30 example/counterexample items carrying printed numeric evidence
across the nine retrievable cone texts, **15 are machine-refuted** — 11/14
(79%) on the four certified carriers, 4/12 on unaudited suspects, 0/4 on the
SAF2022 control. Verdict classes: verified / sign-wrong / wrong-value /
FP-noise (claimed nonzero at identically-zero points) / fabricated (claimed
phenomenon does not exist) / misprint. New hits beyond the per-paper memos:
SPBB2026 Example 2's printed T-product is wrong (and its T₃ is a 3-cycle,
not a T-transform); Example 1's hypothesis sentence is false; GY2024's
printed T-matrices are not doubly stochastic (intended transforms reproduce
the result); BHKKB2025 Cex 5.7's mixture weights do not normalize.

## Provenance

MOA (1979) → systems-side valid uses (series hazards are sums) → BHM2015
Thm 2 → HKFN2017 → **HF2018 (probable first misuse)** → BKB2022
(canonical citation handle, certified false for its own Thm 2) →
NT2020/BKZ2021/SBB2022/PKP2022 (2020–2021) → Bhakta–Kayal avalanche →
SKF2026, SPBB2026, SKB2026 (still propagating: SKB2026 cites SKF2026).

## Audit method (reproducible)

Admissible instances are generated exactly (rational weights/scales;
hypothesis predicates — V_n/W_n, T-transform factorization, weak
majorization — checked componentwise); ordering differences are evaluated
at rational points; sign changes are certified by exact rational witnesses
plus Sturm root counts on the polynomial numerator (interval-arithmetic
certificates where degree exceeds Sturm budget). `holds-on-samples` is
reported with admissible counts and is never called a proof.

Spike dirs: `mixture-audit/` (SKF, SAF), `shekari-audit/` (SPBB),
`bkb2022-own/` (BKB), `hf2018-nt2020/` (transmitted), `vkf2025/`,
`gy-skb-audit/` (GY, SKB); BHM2015/BKB lemma verification and the
non-separability certificate are in `context/runs/bhb2022/`.

## What this is not

- Not a claim that every listed suspect is false — suspects are named
  from claim shape alone until audited.
- Not a claim about st-order or systems literature — those uses of the
  same lemma are legitimate (the functional is additive there).
- Counterexamples to "transmitted" statements refute the statement as
  cited; whether the paywalled source stated it in that form is recorded
  per memo.
