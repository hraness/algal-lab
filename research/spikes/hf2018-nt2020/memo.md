# Audit memo: Hazra–Finkelstein (2018) and Nadeb–Torabi (2020)

Run dir: `research/spikes/context/runs/hf2018-nt2020/` (gitignored).
Exact arithmetic via `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy Rational; sign changes certified by `Poly.count_roots` Sturm counts +
exact rational witnesses). Scripts: `audit_hf_nt.py`, `audit_hf_nt2.py`,
`certify_nt42_n3.py`, `certify_hf_T_n3.py`.

## Citations (verified via Crossref/publisher records, 2025-09-25)

- **[HF2018]** N. K. Hazra, M. Finkelstein, *On stochastic comparisons of
  finite mixtures for some semiparametric families of distributions*,
  TEST 27(4):988–1006 (2018). DOI 10.1007/s11749-018-0581-7.
  (Task brief guessed J. Appl. Probab./Metrika — actual journal is TEST.)
- **[NT2020]** H. Nadeb, H. Torabi, *New results on stochastic comparisons
  of finite mixtures for some families of distributions*, Communications in
  Statistics – Theory and Methods 51(10):3104–3119 (2022; online 2020).
  DOI 10.1080/03610926.2020.1788082.
  (Task brief said Operations Research Letters — actual journal is
  Comm. Statist. Theory Methods; SAF2022 ref [23] agrees.)

## Retrieval status

Both papers are **closed access**: no OA copy on Unpaywall, OpenAlex,
Semantic Scholar, arXiv, Strathprints (title search: no matches), CORE,
or the authors' institutional pages (UFS DSpace is JS-only; the Yazd URL
that looked promising serves Torabi's CV, not the paper). This matches
`papers/hazard-mixture/main.tex` ("Sources not retrieved"), which already
recorded that these two texts were inaccessible.

**Consequence.** Claims below are *reconstructed* from the citing papers:
SAF2022 Rem 6.6 ("Theorem 6.5 extends Theorem 3.2 in Nadeb and Torabi
(2020)"), SAF2022 Cor 6.21 ("extends Theorem 4.2 in Nadeb and Torabi
(2020)"), SAF2022 Rem 6.18 (both papers leave the n>2 hr question open),
and SKF2026 Thms 3.9/3.12 ("proof follows from Theorem 3.4 of Hazra and
Finkelstein (2018)"). The ordinary-mixture (αᵢ=1) specializations tested
are the weakest form of each transmitted claim: a counterexample to the
specialization refutes any consistent reading; "holds-on-samples" does not
verify the original wording. The papers' own printed examples could not be
checked (no text) — flagged `not-checkable` below.

## Models tested

Ordinary finite mixtures F̄(t) = Σ pᵢ F̄(t|λᵢ):

- PH family F̄(t|λ) = F̄(t)^λ, exponential F̄ = e^{−t} (s = e^{−t} ∈ (0,1)):
  survival Σpᵢ s^{λᵢ}; hazard shape h̃(u) = Σpᵢλᵢu^{λᵢ}/Σpᵢu^{λᵢ}.
- PRH family: reversed-hazard shape r̃(x) = h̃(x)/x — sign identical to the
  h̃ comparison, so hr certificates refute rh claims simultaneously.
- T-transform on columns (i,j) of the 2×n matrix [p;λ], weight ω, applied
  to both rows. V_n = antiordered rows, W_n = comonotone rows.

## Claims table

| Claim (transmitted via) | Content tested | Status | Evidence |
|---|---|---|---|
| NT Thm 3.2 (SAF Rem 6.6) | st: p dec, λ,γ inc, (p,λ),(p,γ)∈U_n, λ ≻^w γ ⇒ Σpᵢs^{λᵢ} ≥ Σpᵢs^{γᵢ}; n≤4, exp baseline | holds-on-samples | 2916 admissible, 0 violations |
| NT Thm 4.2 (SAF Cor 6.21), n=2 | hr: U₂ conds + λ ≻^m γ ⇒ h̃_λ ≤ h̃_γ | holds-on-samples | 140 admissible, 0 violations |
| **NT/HF open question n>2** (SAF Rem 6.18; HF §4; NT §4) | same claim at n=3,4 | **EXACT COUNTEREXAMPLE** | certified below; 30/123 (n=3), 24/106 (n=4) violations; hazards cross |
| HF Thm 3.4 pattern (SKF Thms 3.8/3.9 cite it) | hr: [p;λ]∈V_n, [q;γ]=[p;λ]M_T ⇒ h̃_p ≤ h̃_q on (0,1) | **EXACT COUNTEREXAMPLE for n≥3** | certified below; n=2: 2264 admissible, 0 crossings (consistent w/ proved 2×2 case); n=3: 49/935 crossings; n=4: 23/325 |
| W_n single-T hr (α>0 domain) | either fixed direction | fails even at n=2 | 1535/2224 crossings at n=2 — no monotone direction exists; consistent with SKF pairing W only with α≤0 (different domain y>1, untested here) |
| rh analog for PRH (V_n) | r̃_p ≤ r̃_q | **EXACT COUNTEREXAMPLE n≥3** | identical sign computation (r̃ = h̃/x, x>0) — same certificate |
| NT further claims (scale-family st with different weights; disp order; lr characterization for transmuted-G) | — | not-checkable | text inaccessible; not transmitted verbatim |
| Papers' own printed examples/counterexamples | — | not-checkable | text inaccessible |

## Certificate 1 — n>2 hr open question resolves negatively (ordinary mixtures)

Claim pattern (NT Thm 4.2 extended to n>2; SAF Cor 6.21 direction):
(p,λ),(p,γ)∈U_n, λ ≻^m γ ⇒ h_{p,λ} ≤ h_{p,γ} for PH mixtures.

    p   = (39/86, 18/43, 11/86)   (decreasing)
    λ   = (4, 6, 9),  γ = (4, 7, 8)   (increasing)
    λ ≻ γ: 4 ≤ 4, 4+6=10 ≤ 4+7=11, 19 = 19         [verified exactly]
    (p,λ),(p,γ) ∈ U_3 (p dec vs λ,γ inc)           [verified exactly]

d(s) = h_λ − h_γ, s = e^{−t}: numerator degree 9, denominator root-free on
(0,1); Sturm count: exactly **1 interior root** (double root at 0, one root
>1, one <0). Exact rational witnesses:

    d(1/2)  = 6271/156247 > 0       (violates the claimed direction)
    d(3/4)  = −17228781/103906915 < 0
    d(1)    = −25/86 < 0            (t=0: weighted means 471/86 vs 496/86)

→ hazards cross once; the mixtures are hr-incomparable. Both HF2018 §4 and
NT2020 §4 state the n>2 case as open (per SAF Rem 6.18) — the answer is no,
already for ordinary exponential mixtures, no α-mixture needed.
Script: `certify_nt42_n3.py`.

## Certificate 2 — single T-transform hr claim fails at n=3

Claim pattern (HF2018 T-transform machinery → SKF Thm 3.8/3.9 via "HF
Thm 3.4"): [p;λ]∈V_n, [q;γ]=[p;λ]M_T ⇒ h̃_p ≤ h̃_q on (0,1).

    p = (1/8, 29/72, 17/36),  λ = (9, 5, 4)        ∈ V_3 (antiordered)
    T on cols (1,2), ω = 13/20:
    q = (2/9, 11/36, 17/36),  γ = (38/5, 32/5, 4)   [T verified componentwise]

In w = u^{1/5}: numerator degree 83, Sturm count **1 root in (0,1)** (root
0 mult. 45, one root in (1,2)). Witnesses:

    D(1/2)  = +2.78e37/5.22e39 > 0   (exact value in certificate)
    D(7/8)  < 0
    D(9/10) < 0

→ hazard rates cross; the claimed ordering fails on a whole u-interval.
Script: `certify_hf_T_n3.py`.

Same findings: n=3 V-class single-T: 49/935 admissible crossing; n=4:
23/325. n=2 V-class: 2264 admissible, ZERO crossings — the 2×2 result is
correct; the failure is specifically the n≥3 T-transform lift, i.e. the same
bug pattern as SKF (Lemmas 2.4/2.5 misapplied to a non-additive ratio).

## Reading of the cluster bug

- If HF2018 Thm 3.4 indeed asserts the n-component T-chain hr ordering for
  ordinary mixtures (as SKF's deferral implies), the bug is **upstream in
  HF2018**, not introduced by SKF's α-mixture lift: the α=1 specialization
  already fails (Certificate 2).
- If HF Thm 3.4 is only an additive-function chain-majorization lemma
  (correct as stated), then SKF's mistake is applying it to the hazard-rate
  *ratio*, which is not additive. Either way the transmitted n-component
  claim is false.
- The same certificate refutes the rh (PRH) analog, since r̃ = h̃/x has
  identical sign.

## Repair suggestions

- n=2 statements are fine (0 violations in all four tested quarters worth
  of the ordinary-mixture specialization).
- For n≥3 the T-transform claims need a genuinely additive target (e.g.,
  order the *sum* φ(pᵢ,λᵢ) quantities) or replacement hypotheses:
  comonotone rearrangement conditions strong enough to make h̃
  Schur-monotone, e.g. restrict to chains preserving U_n plus equal
  weighted means (counterexample 1 shows unequal E_p[λ] at t=0 is part of
  the failure — but sign changes occur even away from t=0, so equalizing
  means alone is not a repair).
- NT-3.2-type st results (weak supermajorization + U_n + dec-convex F̄)
  are robust: 0 violations on 2916 samples; the boundary case needs
  λ ≠ γ strictness only to avoid ties.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY certify_nt42_n3.py     # open-question counterexample certificate
    $PY certify_hf_T_n3.py     # T-transform n=3 certificate
    $PY audit_hf_nt.py nt32    # NT-3.2 specialization sweep
    $PY audit_hf_nt.py nt42    # n=2 vs n=3,4 majorization sweep
    $PY audit_hf_nt2.py        # raw sign patterns, V/W, n=2..4
