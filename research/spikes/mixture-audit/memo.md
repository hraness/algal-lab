# Audit memo: stochastic-ordering claims in SAF2022 and SKF2026

Committed copy: `research/spikes/mixture-audit/` — audit and certificate scripts
are alongside this memo. The source PDFs/text dumps and per-claim audit logs
remain in the gitignored `research/spikes/context/runs/mixture-claim-audit/`.

**Scope.** Exhaustive check of every finite-testable stochastic-ordering claim
in:

- **[SAF2022]** Shojaee, Asadi, Finkelstein, *Stochastic properties of
  generalized finite α-mixtures* (accepted manuscript, Strathprints 79140;
  published: J. Appl. Probab. 60(3):913–935, 2023). Local copy `SAF2022.pdf`,
  text `SAF2022.txt`. Numbering below is the accepted-manuscript numbering
  (published numbering differs: AM Thm 6.5/6.9/6.17 = publ. Thm 6.1/6.2/6.3).
- **[SKF2026]** Sahoo, Kayal, Finkelstein, *Stochastic ordering results between
  two finite α-mixture models with resilience-scaled components* (accepted
  manuscript, Strathprints 96227; appear in Probab. Eng. Inform. Sci. 2026).
  Local copy `SKF2026.pdf`, text `SKF2026.txt`.

Existing manuscript under audit: `papers/hazard-mixture/main.tex` already
refutes SKF Thms 3.8 (V_n/α≥0 half), 3.11, 3.12, Cor 3.3, and resolves SAF
Rem 6.18's open question / Thm 6.3 n>2. This memo audits **all remaining
checkable claims** in both papers.

## Method

Exact rational arithmetic throughout (`sympy`, Rational parameters).
For each claim we generate admissible rational parameter instances (all
hypothesis predicates — majorization, weak sub/supermajorization, p-larger,
V_n/W_n membership, U_n membership — checked exactly), reduce the claimed
difference to a polynomial or rational function in a substituted variable
(u = e^{−t/L} for exponential baselines; t itself for Lomax/Pareto/power-law
baselines), and screen signs on a rational grid. Sign changes are certified
by Sturm root counts (`Poly.count_roots`) and isolating intervals
(`Poly.intervals`), giving exact rational witnesses.

The testable quantities reduce, for both models, to comparisons of

- inner sums `Σ p_i s^{a_i}` (stochastic order),
- weighted-average ratios `Σ p_i γ_i s^{b_i}/Σ p_i s^{b_i}` (hazard and,
  under the paper's own displayed formula, reversed-hazard order),
- their t-derivatives (ageing, DFR/IFR/DFRA/IFRA closure),
- density ratios (lr order — not claimed by either paper; only checked where
  the papers themselves assert counterexamples).

Negative-α exponents are handled by multiplying through by a common power of
s, which preserves signs on (0,1). Fractional-power instances (Compound
Rayleigh, single-point figure values) are evaluated at 60-digit precision
(mpmath) and marked `numerical` — all exact certificates use SymPy Sturm
counts, not floating point.

Files: `audit_lib.py` (helpers + hypothesis predicates),
`audit_skf_st.py` (SKF Thms 3.1–3.6 / Cor 3.1),
`audit_skf_hr.py` (SKF Thms 3.7–3.12 / Cors 3.2–3.3, hr+rh),
`audit_saf.py` (SAF Thms 3.1, 3.5, 4.1, 5.1, 5.2, 6.5, 6.9, 6.13, 6.14, 6.17),
`verify_paper_cex.py` (exact checks of the papers' own examples and claimed
counterexamples), `certify_thm34.py`, `certify_whalf.py` (counterexample
certificates).

Grid used: s ∈ {1/16, 1/8, 1/4, 2/5, 1/2, 3/4, 7/8, 15/16} plus claim-specific
grids; every reported "holds" is bounded-search confirmation, not a proof.

## Results — SKF2026

| Claim (AM numbering) | Status | Evidence |
|---|---|---|
| Thm 3.1(i) st, γ ≺^w δ, p∈ε⁺/D⁺, α≥0 | holds-on-samples | 1087 admissible, 0 violations |
| Thm 3.1(ii) st, γ ≺_w δ, α<0 | holds-on-samples | 1036 admissible, 0 violations |
| Thm 3.2(i)–(iv) st, p vs q | holds-on-samples | 2964 admissible across 4 parts; only exact-zero ties flagged, no genuine violations |
| Thm 3.3(i)–(iii) st, p≺q & γ vs δ | holds-on-samples | 391 / 419 / 391 admissible, 0 violations |
| **Thm 3.4 st, θ ≺^w ξ, α < γ** | **EXACT COUNTEREXAMPLE (α>0 branch)** | certified below; 5/548 grid violations, α<0 branch 589/0 clean |
| Thm 3.5 st, θ ≽^p ξ | holds-on-samples | 549 + 583 admissible, 0 violations (both α signs) |
| Thm 3.6 st, θ≺^w ξ ∧ p≺_w q, α≤0 | holds-on-samples | 430 admissible, 0 violations |
| Cor 3.1 (ξ constant vector) | holds-on-samples | 1115 admissible, 0 violations |
| Thm 3.7 (n=2) hr, all four quarters | holds-on-samples | 4×800 admissible, 0 violations |
| Thm 3.8 V_n/α≥0 hr | **EXACT COUNTEREXAMPLE** (previously refuted) | see manuscript |
| **Thm 3.8 W_n/α≤0 hr** | **EXACT COUNTEREXAMPLE (new)** | certified below; 322/1274 (n=3), 481/1226 (n=4) violations |
| Thm 3.9 (mixed T-structures, hr) | **EXACT COUNTEREXAMPLE** (inherits 3.8 failures; a single T is a special case) | both halves |
| Thm 3.10 (n=2) rh | refuted (literal model) / holds-on-samples (displayed-formula reading) | literal-model reading: 2279/2500 violations; formula-reading: 1738 (V_2,α≥0) + 1740 (W_2,α≤0) admissible, 0 violations |
| Thm 3.11 V_n/α≥0 rh | **EXACT COUNTEREXAMPLE** (previously refuted) | manuscript |
| **Thm 3.11 W_n/α≤0 rh** | **EXACT COUNTEREXAMPLE (new)** | same certificate as 3.8 W-half (identical h̃ comparison); 616/2500 violations |
| Thm 3.12 (n-component rh analog) | **EXACT COUNTEREXAMPLE** | inherits 3.8/3.11 failures |
| Cor 3.2 (same-structure products, hr) | refuted | inherits |
| Cor 3.3 (n-component products, rh) | refuted | inherits |
| lr order | no positive claim (paper disclaims via counterexamples) | their Cex 3.10, 3.12 verified numerically |

### New exact counterexample 1 — Theorem 3.4 fails for α > 0

Theorem 3.4 claims: if `t²g(t)` is increasing on t>0, `α < γ` (scalar γ),
`p ∈ ε⁺` (increasing), `θ, ξ ∈ D⁺` (decreasing), and `θ ≺^w ξ` (θ's increasing
partial sums ≥ ξ's), then `U_n(p,γ,θ) ≥st V_n(p,γ,ξ)`.

Counterexample (n = 2; Lomax baseline `Ḡ(t) = 1/(1+t)`, `g = 1/(1+t)²`,
`t²g(t) = t²/(1+t)²` strictly increasing on t>0 — verified symbolically):

    p = (1/3, 2/3)        (increasing, in ε⁺)
    γ = 3,  α = 2/3       (α < γ; αγ = 2)
    θ = (3, 1),  ξ = (7/2, 1/2)   (both decreasing, in D⁺)
    θ ≺^w ξ:  increasing partial sums 1 ≥ 1/2, 1+3 = 4 ≥ 1/2+7/2 = 4  ✓

Since α > 0, `sign(S_U − S_V) = sign(inner_U − inner_V)` with

    d(t) = Σ_i p_i [ (θ_i/(θ_i+t))² − (ξ_i/(ξ_i+t))² ]
         = (−28t⁶ + 4t⁵ + 1053t⁴ + 3664t³ + 4565t² + 1722t) /
           (48t⁸ + 768t⁷ + 5064t⁶ + 17760t⁵ + 35763t⁴
            + 41880t³ + 27786t² + 9576t + 1323)

Denominator factors as `3(t+1)²(t+3)²(2t+1)²(2t+7)²` — no positive roots.
Numerator has exactly 2 positive roots, one isolated in (7,8); exact
witnesses:

    d(1)  = 305/3888                > 0
    d(20) = −1579547560/2598836427243 < 0

so the claimed ordering fails on a whole t-interval (the two mixtures are in
fact stochastically incomparable). Script: `certify_thm34.py`.

A 3-component instance is also certified there: p = (25/86, 27/86, 17/43),
γ = 6 (α = 5/6 so αγ = 5), θ = (8,8,5), ξ = (9,8,4) — numerator has 1 root
in (0,∞) and the difference changes sign.

Violations occur in both the `αγ ≤ 1` regime (44/797 sampled) and `αγ > 1`
(127/681) — no monotone repair via an αγ-threshold. The proof's key
Schur-concavity step (eq. 3.7, T14 ≤ 0) combines factors whose signs compete:
`Ḡ^{αγ−1}(t/θ)` and `(t/θ)²g(t/θ)/θ²` move in opposite directions for
θ_i > θ_j depending on `αγ−1`; the stated sign does not follow from the
hypotheses.

### New exact counterexample 2 — Theorem 3.8's second half (W_n, α ≤ 0)

Theorem 3.8 claims for `n ≥ 3`: `[p;γ] ∈ V_n` (or `∈ W_n`) and `α ≥ 0`
(or `≤ 0`) with `[q;δ] = [p;γ]M_T` (T-transform) imply `U ≥hr V`
(`U ≤hr V`). The manuscript already refutes the `(V_n, α≥0)` half; the
`(W_n, α≤0)` half is also false (n = 3, single T-transform):

    p  = (17/44, 5/11, 7/44), γ = (7, 9, 2)      — comonotone, in W_3
    T-transform on coordinates (1,3), ω = 17/20:
    q  = (31/88, 5/11, 17/88), δ = (25/4, 9, 11/4)
    α = −2, exponential baseline (θ scalar)

With y = Ḡ^α ∈ (1,∞), `h_U(t) = h(t/θ)/θ · h̃_{p,γ}(y)` where
`h̃_{p,γ}(y) = Σ p_i γ_i y^{γ_i}/Σ p_i y^{γ_i}`. The claimed `U ≤hr V`
requires `h̃_{p,γ} − h̃_{q,δ} ≥ 0` on the whole range. In s = e^{−t}
(w = s^{1/2} clears halves):

    numerator of h_U − h_V in w: 1 interior root in (0,1)
    h̃ diff at s = 1/4:  −161379121858494821/28929682881644134876 < 0
    h̃ diff at s = 7/8:  > 0  (exact rational witness in certify_whalf.py)

so `h_U − h_V` changes sign on (0,∞): the hazard rates cross; the ordering
fails. Script: `certify_whalf.py`. The same instance refutes Theorem 3.11's
W-half under the paper's displayed r_U formula (same h̃ comparison on
G^α ∈ (1,∞)) and consequently Thm 3.12/Cor 3.3 for the W-side.

Both halves of 3.8/3.11 therefore fail, in both readings — the failure is
the n ≥ 3 lift (Lemma 2.5 applied componentwise), consistent with the
manuscript's mechanism.

### Invalid "counterexamples" printed in SKF2026

- **Counterexample 3.7** claims `Ḡ_U(20) − Ḡ_V(20) = −0.08336543` for
  p=(0.05,0.3,0.65), q=(0.7,0.26,0.4), γ=2, θ=(5,3.5,2), ξ=(5,3,1.5),
  α=−0.3 (Pareto Ḡ=(1/t)^{1/2}). Exact evaluation gives **+0.0674**, not
  −0.0834: the ordering claimed by Theorem 3.6 actually *holds* on this
  instance — the purported counterexample is invalid.
- **Counterexample 3.8** claims `h_U − h_V` changes sign citing values
  −1.11e−16 and +2.22e−16 at t = 6,7. Symbolically,
  `h_U(t) = γ/(2t) = h_V(t)` identically for scalar γ and Pareto hazard
  h(t/θ_i)/θ_i = 1/(2t) — the reported values are floating-point noise; the
  claimed sign change does not exist.

(All other SKF counterexamples — 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.9, 3.10,
3.11, 3.12 — verified exactly or at 60-digit precision as claimed;
Cex 3.5's printed value −0.08887328 reproduces to all printed digits.)

## Results — SAF2022

| Claim (AM numbering) | Status | Evidence |
|---|---|---|
| Thm 3.1: hr bounds F_1 ≤hr F ≤hr / F ≤hr F_n | holds-on-samples | 1016 + 984 admissible, 0 violations |
| Thm 3.5(a): DFR (α>0) / IFR (α<0) closure | holds-on-samples | 1500 + 1500 exact derivative sign tests |
| Thm 3.5(b): DFRA (α>0) / IFRA (α<0) closure | holds-on-samples | 300 + 300 Weibull checks (numerical) |
| Lemma 3.3: ηᾱ concave (α>0) / convex (α<0) | holds-on-samples | 3000+3000 random Jensen checks (60-digit) |
| Thm 4.1(a): lim r(t,ᾱ) = α₁r₁/ᾱ | holds-on-samples | exact limit evaluations consistent |
| **Thm 4.1(b): "→0 iff cond. (16)"** | **EXACT COUNTEREXAMPLE (boundary)** | at α₁λ₁ = α₂λ₂, r(t,ᾱ) ≡ (α₁/ᾱ)r₁(t) for ALL t (proof below) yet cond. (16) fails — "only if" is false on the boundary; interior holds |
| Thm 5.1: componentwise ≤st ⇒ mixture ≤st | holds-on-samples | 558 admissible, 0 violations (one-line proof anyway) |
| Thm 5.2: hr-order under (i)–(iv) | holds-on-samples | α>0: 460 admissible, 0 viol.; α<0: 5741 admissible, 0 viol. |
| Thm 6.5 (publ. 6.1): st order, λ ≻^w γ | holds-on-samples | 229 (n=3) + 383 (n=4) admissible, 0 violations |
| Thm 6.9 (publ. 6.2): st order, α≤0 or 0<α<1 | holds-on-samples | 598 + 341 admissible, 0 violations |
| Cor 6.12 (PH family) | holds-on-samples | covered by Thm 6.5 domain |
| Cor 6.13 (accelerated life) | holds-on-samples | 573 admissible (uniform baseline), 0 violations |
| Cor 6.14 (prop. reversed hazard) | holds-on-samples | 774 admissible, 0 violations |
| Rem 6.15 bounds (i),(ii) | holds-on-samples | verified on their Example 6.16 params exactly |
| Thm 6.17 (publ. 6.3): hr order n=2, λ ≻ γ | holds-on-samples | 1030 (α>0) + 505 (α<0) admissible, 0 violations |
| Rem 6.18 open question (n>2) | resolved | manuscript n-component counterexample |
| Cor 6.21 (PH consequence of 6.17) | holds-on-samples | follows 6.17 |

Note on Thm 5.2 audit subtleties: for α_i<0, condition (i) requires
`(α_i/ᾱ)r_{Fi}` increasing in i — equivalently `α_i·a_i` *decreasing* since
ᾱ<0 — and the hazard formula needs its `1/ᾱ` prefactor to keep signs right.
Both were required for a correct test; with them, the α<0 branch holds on
5741 admissible instances.

### Minor errata in SAF2022 (not theorem failures)

- **Example 3.6**: the printed hazard formula
  `r(t,ᾱ) = (1/2.9)(1.12e^{−1.6t}+0.6e^{−2t})/(e^{−1.6t}+e^{−2t})` omits the
  `p_i` weights in the denominator. Correct value at t=0 is 86/145 ≈ 0.593
  (printed form gives 43/145 ≈ 0.297). The bound conclusion (r < r₁ = 0.8)
  is unaffected.
- **Counterexample 6.11** uses Compound Rayleigh `Ḡ(t|λ) = (λ/(λ+t²))^a`
  (not `(λ/(λ+t))^a`); with the correct baseline its claimed sign change
  verifies numerically.
- **Thm 4.1(b)**'s biconditional fails exactly on the boundary
  `α₁λ₁ = α₂λ₂`: then `Σp_iF̄_i^{α_i} = e^{−α₁λ₁∫r}` identically, so
  `r(t,ᾱ) ≡ (α₁/ᾱ)r₁(t)` → the difference is identically 0 while
  `r(t)e^{−(α₂λ₂−α₁λ₁)∫r} = r(t) → ∞`. A strict-inequality hypothesis
  `α₁ < (λ₂/λ₁)α₂` repairs it.

### SAF2022's own counterexamples — all verified

Cex 6.8, 6.11 (with t² baseline), 6.20, 6.24 exact Sturm-verified;
Cex 6.23 (different outer exponents — genuinely algebraic) and 6.25
(lr-ratio non-monotonicity) verified at 60-digit precision.
Example 6.7, 6.10, 6.16(i)/(ii), 6.19 all verify as claimed.

## Repair assessment

- **SKF Thm 3.4**: no repair via `αγ ≤ 1` (failures on both sides of the
  threshold). The proof needs inner(θ) Schur-concave; for scale families
  `Ḡ(t/θ) = H(t/θ)` the counterexample shows this fails generically.
  Possible salvage: restrict to `α < 0` only (clean on 589 samples; the
  negative-α proof segment may be right since the Ḡ-power factor ordering
  flips), or add a condition tying p to θ (e.g., `p ∝ θ^{−αγ}` rescaling).
- **SKF Thm 3.8/3.9/3.11/3.12, Cors 3.2–3.3**: not repairable by a
  distributional-class restriction — the failure is in the T-transform /
  Schur-lift step, independent of baseline family (exponential suffices).
  What survives: the n=2 statements (Thms 3.7, 3.10 under the
  displayed-formula reading) hold on 3200+3000 admissible instances, and the
  manuscript's correct analogs.
- **SAF Thm 4.1(b)**: replace `≤` by strict `<` in hypothesis `α₁ ≤ cα₂`,
  or add `α₁λ₁ < α₂λ₂` explicitly.
- **SAF Thm 5.2** α<0 branch: pending; if the corrected-direction run still
  fails, the branch needs `α_i a_i` decreasing (i.e., `(α_i/ᾱ)r_i` inc) to be
  stated explicitly — currently ambiguous.

## Adjacent papers worth auditing next

1. **Barmalzan, Haidari, Balakrishnan (2022)** — supplies Lemmas 2.4/2.5
   (the T-transform lift that is the failure point of Thms 3.8–3.12);
   its n≥3 lemmas deserve the same exact search.
2. **Nadeb & Torabi (2020)** (ORL) — SAF Thm 6.5's ordinary-mixture
   precursor; finite-testable.
3. **Varghese, Kayal, Finkelstein (2025)** — cited in SKF Rem 3.4 as the
   α ≥ γ₁ analog; sibling paper in the same program.
4. **Hazra & Finkelstein (2018)** — ordinary-mixture majorization results
   SAF cites for the n>2 open question.

## Source/paper limitations

- Numbering above is accepted-manuscript; the published versions renumber
  Section 6 claims (SAF) — map via Strathprints records 79140/96227.
- SKF Example 3.7 prints `[p;γ] ∈ W_2` for (0.6,0.4)/(4,5), but under their
  own Definition the pair is in V_2 ((0.2)(−1) = −0.2 ≤ 0) — the example
  actually sits in the V-branch; conclusion unaffected.
- Figure-axis text extracted by pdftotext is unreliable; all figure-based
  claims were re-derived from stated parameter values.
- SKF Cex 3.10's caption/params refer to "the same setup as Example 3.7
  except α" — α = −3 applied; ratio non-monotone verified numerically.
- Some printed definitions have reversed inequality signs vs. the
  convention actually used in proofs (Def 2.2(iv) p-larger prints `≤`
  products where `≥` is needed for consistency with their examples) —
  we followed the example-consistent reading.

## Reproduce

    cd .../mixture-claim-audit
    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY certify_thm34.py        # SKF Thm 3.4 counterexample certificate
    $PY certify_whalf.py        # SKF Thm 3.8 W_n/alpha<=0 counterexample
    $PY verify_paper_cex.py     # papers' own examples/counterexamples
    $PY audit_skf_st.py         # SKF Thms 3.1-3.6 stochastic order
    $PY audit_skf_hr.py         # SKF Thms 3.7-3.12 hazard/rev-hazard
    $PY audit_saf.py all        # SAF2022 claims

Runtime: all searches are niced and bounded; the heaviest single audit
(Thm 3.8 n=4) is minutes on this machine.
