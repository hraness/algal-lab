# Audit memo: Varghese–Ahmad–Sarkar–Ghosh–Majumder (2025) — VKF2025

Run dir (gitignored): `research/spikes/context/runs/vkf2025/`.
Sibling audits: `research/spikes/mixture-audit/memo.md` (SKF2026/SAF2022),
`research/spikes/context/runs/bhb2022/memo.md` (BKB2022 T-transform lemmas).

## 1. Citation and retrieval

**[VKF2025]** Varghese, Akhila Anna; K., Ameen Mahmood; Sarkar, Soumyadeep;
Ghosh, Shyamal; Majumder, Priyanka. *On stochastic comparisons of α-mixture
models with location-scale family of distributions.* **Statistics** 59(5),
1278–1300 (published online 14 May 2025). DOI 10.1080/02331888.2025.2502946.

NOTE: the task brief's author guess ("Varghese, Kayal, Finkelstein") is wrong
— there is no Kayal or Finkelstein on it; the SKF reference list entry is
"Varghese, A. A., K, A. M., Sarkar, S., Ghosh, S. and Majumder, P. (2025).
On stochastic comparisons of α-mixture models with location-scale family of
distributions, Statistics. pp. 1–23." (SKF2026.txt l.1638).

**Retrieval status: CLOSED ACCESS — no full text obtained.** Attempts
(2026-09-25): T&F `doi/pdf`, `doi/epdf`, `doi/abs`, `doi/full` → 403
(bot wall); Unpaywall reports `is_oa:false`, zero OA locations; OpenAlex
`oa_status:closed`, no repository copy; Semantic Scholar `openAccessPdf`
CLOSED; arXiv API (title/abstract/author searches) — no preprint; Google
Scholar cluster 15662529887310497940 — only T&F + Ingenta + EBSCO copies;
EBSCO crawler page has metadata only (1.9 MB PDF gated); scholar.archive.org
and BASE behind Anubis challenges; fatcat.wiki unreachable; no IISER-TVM
institutional repository found (idr/dspace/eprints DNS all fail); the
author's LinkedIn share link resolves to the DOI. **The audit below therefore
runs on reconstructed statements** — the same method used for BKB2022.

## 2. Claims as cited by SKF2026 (reconstruction basis)

| Ref in SKF2026 | What SKF says |
|---|---|
| l.210 (intro) | VKF "considered finite α-mixture models comprising of location-scale families of distributions, and obtained some stochastic ordering results" (st, hr, rh per abstract) |
| l.727 (pre-Thm 3.4) | SKF Thm 3.4 "can be treated as an improved version of the result in Theorem 3.1(ii) of Varghese et al. (2025) since it holds for a wider range of the parameter α. The range of α includes non-positive values." |
| l.782 (Rem 3.4) | "When α ≥ γ₁, the result is similar to Theorem 3.1(i) of Varghese et al. (2025)." |
| l.958 (pre-Thm 3.6) | "The similar setup has been considered by Varghese et al. (2025) in their result, for example Theorem 3.10. However, their sufficient conditions do not match with the conditions proposed in the following result. Mainly, we have proved it when α is non-positive." |

Reconstructed claims (common scale-family frame: a location-scale family
contains the pure-scale subfamily μ≡0, so counterexamples on scale families
refute any VKF statement covering them):

- **R1** [VKF Thm 3.1(i)]: `t²g` increasing; `p ∈ ε⁺ₙ` (or `D⁺ₙ`);
  `θ, ξ ∈ D⁺ₙ` (or `ε⁺ₙ`); `θ ≺^w ξ`; **α ≥ γ** ⇒ `U ≥st V`.
- **R2** [VKF Thm 3.1(ii)]: same claim for **0 < α < γ** (SKF extended it to
  α ≤ 0 — that is SKF Thm 3.4, already refuted).
- **R3** [VKF Thm 3.10]: two-parameter heterogeneity (p vs q, θ vs ξ, scalar
  γ), **α > 0**. Weak-order direction on p not recoverable; both `p ≺_w q`
  and `p ≺^w q` tested.

## 3. Results

**R1 — EXACT COUNTEREXAMPLE (Sturm-certified).**
Instance (`certify_r1.py`, all hypotheses verified exactly):

    n = 2, Lomax baseline Ḡ = 1/(1+t)  (t²g = t²/(1+t)² strictly increasing)
    p = (4/5, 1/5)  ∈ D⁺        γ = 2,  α = 2  (α ≥ γ, αγ = 4 > 1)
    θ = (4, 7),  ξ = (1, 9)  ∈ ε⁺
    θ ≺^w ξ:  increasing partial sums  4 ≥ 1,  4+7 = 11 ≥ 1+9 = 10   ✓

    d(t) = inner_U − inner_V =
      −4t·(785t¹¹ + 27790t¹⁰ + 327620t⁹ − 40910t⁸ − 41847610t⁷
           − 511276910t⁶ − 3236661628t⁵ − 12444557762t⁴ − 29727405727t³
           − 42795153072t² − 34285682592t − 11970249984)
      / 5(t+1)⁴(t+4)⁴(t+7)⁴(t+9)⁴

Numerator has exactly **1 positive root, isolated in (12,13)**
(`Poly.intervals`); denominator strictly positive on t>0. Witnesses:
`d(12) = +19760252621/571952479518784 > 0`,
`d(15) = −10812822913/31261159604224 < 0`.
The claimed `U ≥st V` fails on an interval — mixtures are incomparable.

Counts (Fraction-exact grid, `audit_vkf_fast.py`, 20000 draws):

| cell | admissible | violations |
|---|---|---|
| α≥γ, αγ=1, all n∈{2,3,4}, both orientations, both baselines (Fraction-exact) | 3704 | **0** |
| α≥γ, αγ>1, Lomax | 14778 | **1830** |
| α≥γ, αγ>1, power2 | 7498 | **32** |
| α≥γ, fractional α, Lomax (mpmath 60-digit): αγ<1 / αγ=1 / αγ>1 | 3885 / 440 / 2465 | 0 / 0 / **97** |

Robustness to hypothesis direction (α≥γ, αγ>1, Lomax, n=3): `θ ≺_w ξ`
(submajorization): 6130/6419 violations — inner diff mostly ≤0, i.e. the
claimed direction fails wholesale under that convention. `θ ≻ ξ`
(majorization): 416/416 violations.

**R2 — refuted by inheritance.** The SKF-audit certificate for Thm 3.4
(`p=(1/3,2/3)`, `γ=3`, `α=2/3`, `θ=(3,1)`, `ξ=(7/2,1/2)`, Lomax;
`d(1)=305/3888>0`, `d(20)=−1579547560/2598836427243<0`, 1 root in (0,1))
satisfies `0 < α < γ` — the exact positive-α range SKF attributes to VKF
3.1(ii). Verified in `certify_r1.py` control section.

**R3 — fails.** Lomax, α>0, n=3, `θ ≺^w ξ`: 95/3391 violations.
(`p ≺_w q` and `p ≺^w q` coincide exactly for sorted equal-sum vectors —
both reduce to `p₁ ≥ q₁ ∧ pₙ ≤ qₙ` — so one count covers both readings.)
First witness: `p=(8/61,26/61,27/61)`, `q=(6/79,34/79,39/79)`, `γ=3`,
`α=4`, `θ=(6,5,4)`, `ξ=(8,3,1)` — d>0 through t≈3 then `d(5)<0` (sign
change). Whichever weak order VKF 3.10 asserts, the claim fails at α>0.

## 4. Mechanism and the αγ = 1 boundary

The proof step in this program is Schur-concavity of
`inner(θ) = Σᵢ pᵢ Ḡ(t/θᵢ)^{αγ}` via
`T14 = (θᵢ−θⱼ)[pᵢ Xᵢ − pⱼ Xⱼ]`,
`Xᵢ = Ḡ^{αγ−1}(t/θᵢ)·(t/θᵢ)²g(t/θᵢ)/θᵢ²`. For `θᵢ ≥ θⱼ`, `pᵢ ≤ pⱼ`:

- `(t/θᵢ)²g(t/θᵢ) ≤ (t/θⱼ)²g(t/θⱼ)`  (t²g increasing),
- `Ḡ^{αγ−1}(t/θᵢ) ⋛ Ḡ^{αγ−1}(t/θⱼ)` according to sign of `αγ−1`.

For `αγ > 1` the two factors of `X` compete and `pᵢXᵢ ≶ pⱼXⱼ` is genuinely
undetermined — the claimed sign does not follow. For `αγ ≤ 1` both factors
move the same way in `X` (both `≤`), but `pᵢXᵢ vs pⱼXⱼ` still involves the
weight competition — empirically it always lands the right way: **0/~10,200
violations at αγ ≤ 1 across both positive-α regimes** (α≥γ and 0<α<γ
sweeps combined) vs **~2,050 violations at αγ > 1**. The empirical boundary
in the positive-α program is **αγ = 1, not α = γ**. (Sharper than the
sibling memo's "violations on both sides of αγ ≤ 1" for SKF 3.4 — that
bucket appears to include α<0 sign-flip bookkeeping; at positive α I find
no violations with αγ ≤ 1. Worth a recheck in the SKF sweep.)

The T-transform / Lemma-2.5 machinery that sinks SKF Thms 3.8–3.12 is a
DIFFERENT failure (hr/rh claims, non-separable h̃). R1/R2/R3 are st-order
claims whose proofs need only Schur-concavity in θ — no separability issue.
The st-order bug (T14) is what VKF shares with SKF.

## 5. Verdict and caveats

- If VKF's Thm 3.1(i)/(ii) and Thm 3.10 are the claims SKF describes (the
  natural reading of Rem 3.4 and the pre-3.6 remark), **VKF fails in exactly
  the same place as SKF: the α ≥ γ side is NOT safe.** The counterexample
  is baseline-generic (Lomax suffices), n = 2 suffices, and it survives all
  four hypothesis-direction readings. The SKF-vs-VKF contrast the task hoped
  for does not exist at the st-order level: the bug is in the shared T14
  Schur-concavity step, which fails whenever αγ > 1, on both sides of
  α = γ.
- What could still save VKF's *actual* statements (unseen): a different
  weak-order convention on θ, a `γ` defined per-component rather than
  scalar, a baseline restriction stronger than "t²g increasing", or
  extra hypotheses coupling p to θ. Any such variant needs the paper text.
- hr/rh claims of VKF (the abstract asserts them): not audited — no
  statements recoverable from SKF's citations. If VKF uses the same
  h̃ ratio-of-sums + Lemma-2.5 lift for n ≥ 3, expect the same
  non-separability failure; that remains a conjecture, not a result.
- Obtain the paper (T&F Statistics 59(5):1278–1300) to convert the
  reconstruction into a verdict on VKF's own numbering.

Files: `audit_lib.py` (copied), `audit_vkf.py` (symbolic version),
`audit_vkf_fast.py` (Fraction-exact scan), `audit_vkf_frac.py`
(mpmath 60-digit fractional-α scan), `certify_r1.py` (Sturm certificate +
R2 control). Retrieval log in this memo's §1.
