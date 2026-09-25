# Audit memo: T-transform lift defects in GY2024 and SKB2026

Run dir (gitignored): `research/spikes/context/runs/gy2024-skb2026/`.
Exact arithmetic: `sympy`/Fraction; sign-change certificates by Sturm root
counts (`Poly.count_roots`) plus exact rational witnesses. Grid screening uses
exact `Fraction` evaluation of closed-form kernels — every kernel below is a
rational function of `y` (a monotone reparametrization of `t`), so a sign
change on `(0,1)` is a genuine crossing of the compared rates, for *every*
baseline SF simultaneously.

## Targets and retrieval

- **[GY2024]** L. Guo, R. Yan, *Orderings of the finite mixture with modified
  proportional hazard rate model*, arXiv:2407.15638v2 [math.ST], 23 Jul 2024.
  Retrieved 2026-09-25 via `arxiv.org/html/2407.15638v2` (HTML; math preserved
  via alttext) and `arxiv.org/pdf/2407.15638v2` → pdftotext. Files
  `gy2024_full.html`, `gy2024.txt`, `gy2024.pdf`, `gy2024_pdf.txt`.
- **[SKB2026]** S. Sahoo, S. Kayal, N. Balakrishnan, *Ordering Results Between
  Two Finite α-Mixture Models with Components Following Modified Proportional
  Hazard Rate Model*, Mathematics 14(14):2557, 2026. DOI 10.3390/math14142557.
  Open access. `mdpi.com` 403s scripted fetch; full PDF obtained 2026-09-25
  from `mdpi-res.com/.../mathematics-14-02557-v2.pdf` → `skb2026.pdf/.txt`.

## The defect pattern (restated)

BKB2022 Lemmas 2.4/2.5 (=BHM2015 Thm 2; here GY Lemma 1/2 and SKB Lemma 3/4,
cited from `[27]=BKB2022`) justify the n-component chain-majorization
comparison only for **additive** column functionals `Φ_n(A)=Σ_i Φ(a_1i,a_2i)`.
Mixture hazard and reversed-hazard rates are **ratios of sums**; "freezing"
n−2 columns inside numerator and denominator is invalid. Both papers carry
the defect; GY2024 additionally *asserts* its n×n hr theorem with no proof.

## Models (exact kernels)

GY2024: ordinary mixture `F̄_C = Σ_i p_i α_i y/(1−ᾱ_i y)`, `y = F̄^λ ∈(0,1)`,
`ᾱ=1−α`.  Hazard `r_C = λh(x)·C(y)`,
`C(y) = [Σ p_iα_i (1−ᾱ_i y)^{-2}]/[Σ p_iα_i (1−ᾱ_i y)^{-1}]` — **ratio of sums**.

SKB2026: α-mixture `Ḡ_W = [Σp_i K_i^α]^{1/α}`, `K_i = θ_i y/(1−θ̄_i y)`,
`y = Ḡ^β` (common `β`).  Hazard `h_W = βh(t)·A(y)`,
`A(y) = [Σp_iθ_i^α(1−θ̄_i y)^{-α-1}]/[Σp_iθ_i^α(1−θ̄_i y)^{-α}]`;
reversed hazard `r_W = βyh(t)/(1−y)·B(y)`,
`B(y) = [Σp_iθ_i(1−θ̄_i y)^{-α-1}]/[Σp_i(1−θ̄_i y)^{-α}]`.
MPRHR dual (`u = G^ξ`): `h_Ẇ = ξu r_b/(1−u)·B(u)`, `r_Ẇ = ξr_b·A(u)`.
Therefore **Thm 8 ≡ Thm 23** (A-kernel, α<0) and **Thm 11 ≡ Thm 20**,
**Thm 9 ≡ Thm 24**, **Thm 12 ≡ Thm 21** (B-kernel, α>0) — one certificate
serves each pair.

## GY2024 — theorem table

| Claim | Order / hypotheses | Proof supplied? | Verdict |
|---|---|---|---|
| Thm 1 | st, n=2, `(p,α)∈K_2` (i) / `∈L_2`+extra (ii), chain `≫` | yes (Lemma 1 on additive SF) | holds-on-samples; Ex 1 verified exactly |
| Thm 2 | st, n×n, single T | "G_n=ΣH additive → Lemma 2" — **legitimate lift** | holds-on-samples (n=3:1500, n=4:477, 0 viol.) |
| Cor 1 | st chains, same structure | Thm 2 | holds-on-samples; Ex 2 params reproduce exactly |
| Cor 2 | st chains, diff. structure, intermediates ∈K_n | Thm 2 | holds-on-samples; Ex 3 verified (typo: printed β₂=0.568 vs exact 0.564) |
| Thm 3 | st, n=2, `(p,λ)∈K_2`/`L_2` | yes | holds (800/0); Ex 4 verified |
| Thm 4 | st, n×n `(p,λ)` | additive lift | holds-on-samples (600/0, integer-λ) |
| Cors 3–4 | st chains `(p,λ)` | Thm 4 | holds-on-samples |
| Thm 5 | **hr**, n=2, `p₁α₁=p₂α₂`, `(p,α)∈K_2` | yes (Lemma 1 on the ratio — admissible for n=2) | holds-on-samples (800/0); Ex 6 verified |
| **Thm 6** | **hr, n×n, `p_iα_i=c ∀i`, `(p,α)∈K_n`, single T** | **NONE** — "Similarly … we can get the result" | **EXACT COUNTEREXAMPLE** (certified) |
| **Cor 5** | hr chains, same structure | none (from Thm 6) | refuted by Thm 6 certificate (single T is a chain) |
| **Cor 6** | hr chains, diff. structure, intermediates ∈K_n | none | **EXACT COUNTEREXAMPLE** (2-step certified) |
| Thm 7, Cor 7 | star / Lorenz, weak supermaj, two-group block α | Saunders-type quantile argument (Lemma 3), not the lift | not-checkable (needs F⁻¹; hypothesis on baseline shape) |

Note: under `p_iα_i=c`, `(p,α)∈K_n` is automatic (`p` decreases in `α`);
`Σp=1` forces `c=(Σ1/α_i)^{-1}`. The hypothesis class is nonempty and rich.

## SKB2026 — theorem table

`Dn`=antiordered vector pairs (audit's V_n-predicate); `εn`=comonotone;
`V_n`/`W_n` = 2×n matrix classes.

| Claim | Order / hypotheses | Lift step | Verdict |
|---|---|---|---|
| Thm 1(i)/(ii) | st (SF side), vector maj `p⪯^w q`/`⪯_w`, `εn`/`Dn` pair conditions | none — direct Schur on `Ḡ_W` | holds-on-samples (800/0) |
| Thm 2 | st, `β⪯^w δ`, `α≥1`, `0<θ<1` | none | holds-on-samples (via Thm 3 runs) |
| Thm 3 | st, combined `p` and `β` | none | holds-on-samples (800/0) |
| Thms 4–6 | st, CDF-side analogs | none | holds-on-samples (same machinery; spot-checked) |
| Thm 7 | **hr, n=2**, `[p;θ]≫[q;γ]`, `∈V_2`, `α≤0` | none — Lemma 3 on ratio (n=2 OK) | holds-on-samples (700/0); Ex 6 verified exactly |
| **Thm 8** | **hr, n, single T, `∈V_n`, `α≤0`** | **"Let Φ_n(θ)=h_{Wn}(t). It follows from Theorem 7 that Φ_2 satisfies Lemma 3. Hence, by applying Lemma 4, the desired result follows."** — Lemma 4 requires `Φ_n=ΣΦ(c_1i,c_2i)`; `h_{Wn}` is a ratio | **EXACT COUNTEREXAMPLE** (certified) |
| **Cor 1** | hr, same-structure chains | from Thm 8 | refuted (single-T instance) |
| **Thm 9** | hr, diff. structures, intermediates ∈V_n | "proof follows directly from Theorem 3.4 of [28]=HF2018" | **EXACT COUNTEREXAMPLE** (2-step, intermediates ∈V_3 certified) |
| Thm 10 | rh, n=2, `∈V_2`, `α≥0` | none — direct | holds-on-samples (700/0); Ex 8 verified |
| **Thm 11** | **rh, n, single T, `α≥0`** | "proof similar to Theorem 8" → broken lift | **EXACT COUNTEREXAMPLE** (certified) |
| **Cor 2** | rh chains | Thm 11 | refuted |
| **Thm 12** | rh, diff. structures | HF2018 Thm 3.4 | **EXACT COUNTEREXAMPLE** (2-step certified) |
| Thms 13–18 | MPRHR st (SF/CDF), vector maj | none | holds-on-samples (structural analogs of 1–6) |
| Thm 19, 22 | MPRHR hr/rh, n=2 | "similar to Thm 7/10" | holds-on-samples (700/0); Ex 10 verified |
| **Thm 20, Cor 3, Thm 21** | MPRHR hr n, single-T / chains / diff-struct, `α≥0` | "similar to Thm 8" / HF2018 3.4 | **EXACT COUNTEREXAMPLE** (kernel-identical to Thm 11 / Thm 12 certificates) |
| **Thm 23, Cor 4, Thm 24** | MPRHR rh n, `α≤0` | same lift | **EXACT COUNTEREXAMPLE** (kernel-identical to Thm 8 / Thm 9 certificates) |
| lr / rhr / rrhr non-extensibility | negative claims | — | consistent (their own Ex 7/9/11 non-monotone ratios plausible; spot-verified numerically where checkable) |

## Certificates (all Sturm-verified; denominators nonvanishing on (0,1))

**GY Thm 6 / Cor 5** — n=3, single T on coords (1,3) ω=3/4:
`p=(16/37,9/37,12/37)`, `α=(1/2,8/9,2/3)` (all `p_iα_i=8/37`, K_3 automatic);
`q=(15/37,9/37,13/37)`, `β=(13/24,8/9,5/8)`.
`r_V−r_W` numerator `=−6623y⁷+217404y⁶−…` (deg 7), **2 roots in (0,1)**;
`d(1/16)=−26382968577328/697805944384200125<0`,
`d(1/5)=1056692120/7414054947243>0` → hazards cross: `V ≱_hr W`.
Search counts: n=3 **1189/2500** admissible violate; n=4 **766/1500**.

**GY Cor 6** — two-step diff.-structure chain, intermediates ∈K_3:
`p=(6/13,4/13,3/13)`, `α=(1/2,3/4,1)`; T1 on (2,3) ω=3/10, T2 on (1,2)
ω=2/5 → `q=(219/650,123/325,37/130)`, `β=(151/200,67/100,33/40)`.
Numerator deg 9, **2 roots in (0,1)**; `d(1/100)<0`, `d(1/4)=+93985749125399489/18016492177225703385>0`.
885/1500 two-step admissible violate.

**SKB Thm 8 / Cor 1 / Thm 23 / Cor 4** — n=3, α=−4, single T on (2,3) ω=9/10:
`p=(7/16,1/4,5/16)`, `θ=(9/4,9,3)` ∈V_3;
`q=(7/16,41/160,49/160)`, `γ=(9/4,42/5,18/5)`.
`h_W−h_V` numerator `425849759289y⁷+…−611874189y` (deg 7), **2 roots in (0,1)**;
`d(1/100)=−353619533609100/43666123426941601543<0`,
`d(1/4)=175665260436/20936322432487>0` → `W ≰_hr V`.
327/3000 (n=3), 125/1500 (n=4) violate.

**SKB Thm 11 / Cor 2 / Thm 20 / Cor 3** — n=3, α=1, single T on (1,2) ω=3/10:
`p=(3/11,13/44,19/44)`, `θ=(5,3/2,1/4)` ∈V_3;
`q=(127/440,123/440,19/44)`, `γ=(51/20,79/20,1/4)`.
`r_W−r_V` numerator deg 7, **2 roots in (0,1)**;
`d(1/2)=−600799/39081240<0`, `d(3/5)=99643695690/444714850077511>0`
→ `W ≰_rh V` (and `Ẇ ≱_hr Ṽ` fails identically).
566/3000 (n=3), 355/1500 (n=4) violate.

**SKB Thm 9 / Thm 24** — two-step diff.-structure chain, intermediates ∈V_3,
α=−2: `p=(5/17,2/17,10/17)`, `θ=(1/3,7,1/4)`;
T1(1,3,ω=19/20), T2(1,2,ω=11/20) → `p2=(303/1360,277/1360,39/68)`,
`θ2=(15989/4800,6397/1600,61/240)`. Numerator deg 3, **2 roots in (0,1)**;
`d(1/100)<0`, `d(1/8)>0`, `d(1/16)<0`. 1/1500 admissible violate (the
V_n-intermediate constraint is restrictive but non-vacuous).

**SKB Thm 12 / Thm 21** — two-step, α=2:
`p=(3/34,7/17,1/2)`, `θ=(9,5/4,1)`;
T1(2,3,ω=19/20), T2(1,2,ω=9/20) → `p2=(3653/13600,3207/13600,337/680)`,
`θ2=(7569/1600,8811/1600,81/80)`. Numerator deg 13, **2 roots in (0,1)**;
`d(1/2)<0`, `d(3/4)>0`. 1/1500 violate.

## Papers' own examples — verification

GY2024: Ex 1, 2 (T-transform products reproduce printed `q,β` to all digits;
SF order direction confirmed), Ex 3 (`q` exact; printed `β_2=0.568` vs exact
`0.564` — typo, conclusion unaffected), Ex 4, 6 (hr n=2 claim) all verified
exactly on `(0,1)` grid.
SKB2026: Ex 6 (Thm 7, α=−1): `h_W−h_V>0` everywhere — verified exactly.
Ex 8 (Thm 10, α=5): `r_W−r_V<0` — verified exactly. Ex 10 (Thm 19, α=20):
`h_Ẇ−h_Ṽ<0` — verified exactly. Necessity examples 1–3: claimed sign changes
verified at 50-digit precision (Ex 2 requires the natural reading θ=1000 on
both mixtures; Ex 3's display implies baseline `Ḡ=e^{−(2t)³}`, under which
the hr sign change verifies).

## Verdicts

- **GY2024 — DEFECT CARRIER.** Thm 6 + Cors 5, 6 are false (Sturm-certified,
  ~40–50% of admissible single-T instances violate). The functional is a
  ratio of sums; no additive `G_n=ΣH` representation exists, and indeed the
  paper supplies **no proof** for Thm 6 — the lift is invoked implicitly by
  "Similarly … we can get the result". All st-order claims (additive lift)
  and the n=2 hr theorem hold on samples.
- **SKB2026 — DEFECT CARRIER, most explicit instance yet.** Thm 8's proof
  states verbatim `Φ_n(θ)=h_{Wn}(t)` followed by "applying Lemma 4" — the
  additive-only lift applied directly to a ratio of sums. Thms 8, 9, 11, 12,
  20, 21, 23, 24 and Cors 1–4 all false (certified; kernel duality covers the
  MPRHR half). The different-structure theorems are routed through
  "Theorem 3.4 of [28]" = **HF2018** — a direct citation of the conjectured
  origin node. n=2 base cases and all vector-majorization st claims hold on
  samples.
- Cluster count: certified defect carriers now **SKF2026, SPBB2026,
  BKB2022-Thm2, GY2024, SKB2026** (GY2024 the only non-Kayal-orbit carrier —
  the lift misuse is not confined to the NIT-Rourkela group; HF2018's role as
  the upstream source is strengthened by SKB2026's explicit "Thm 3.4 of [28]"
  delegations).

## Files

`audit_mphr.py` (kernels + hypothesis predicates + Sturm helpers),
`fast_eval.py` (Fraction evaluators), `attack_fast.py`, `attack_chains.py`
(searches), `certify.py`, `certify_chains.py` (certificates),
`verify_examples.py`, `check_st.py` (controls). Nothing committed; dir is
gitignored (`runs/` rule in `.gitignore:2`).
