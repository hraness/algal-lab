# Audit: BGSK2025 (arXiv:2511.00791) — ELS finite mixtures

**Citation.** R. Bhakta, K. Gupta, G. Saadat Kia (Barmalzan), S. Kayal,
"Stochastic comparisons of finite mixtures with general exponentiated
location-scale distributed components," arXiv:2511.00791v1 [math.ST],
2 Nov 2025. Text: `context/runs/bhb2022-own/bhkkb2025.txt` (= this paper;
ar5iv id confirmed in html). Audited 25 Sep 2026 in `context/runs/bgsk-arxiv/`.

**Model.** Component i: F_i(x) = F((x−σ_i)/λ_i)^{α_i}, x > σ_i + cλ_i (ELS
family, baseline F on (c,∞)). U_n(r,α,σ,λ): ordinary finite mixture,
CDF = Σ r_i F_i. Sec 4 = two-type "multiple-outlier" mixtures
(n_i of type i at weight r_i, n1r1+n2r2=1 vs n*_i, s_i).

## Lift usage: NONE — not a carrier of the BKB2022 defect

The paper never touches chain/matrix majorization. Its only majorization
tools are Lemmas 2.1/2.2 (Marshall–Olkin–Arnold Thm A.3-type
Schur-convexity criteria under **vector** majorization on D_n/E_n),
used exactly once (Thm 3.4) on the mixture CDF — an additive functional,
the legitimate use. Sec 4's two-type comparisons are settled by exact
cross-product algebra, not by any lift.

## Theorem table

| Claim | Order | Mechanism | Verdict |
|---|---|---|---|
| Prop 3.1 | — | pdf integrates to 1 | correct (trivial) |
| Thm 3.1 | st | case analysis, termwise F^{α_i}(u_i) ≥ F^{β_i}(v_i) | sound |
| Thm 3.2 | rh | double-sum, every (i,j) bracket ≥ 0 by separated max/min | sound (300 adm., 0 viol.) |
| Thm 3.3 | lr | double-sum bracket (β_j−α_i) ≥ 0 | sound (300 adm., 0 viol.) |
| Thm 3.4 | st | Schur-convexity of Σ s_i F^{α_i} — additive, legit | sound (592 adm., 0 viol.) |
| Thm 4.1 | rh | exact factorization (n1r1n2*s2 − n2r2n1*s1)·[…] ≤ 0 | sound (73+66 adm. both dirs, 0 viol.) |
| **Thm 4.2** | lr | ζ' ∝ (n1r1n2*s2 − n2r2n1*s1)φ', needs φ' ≤ 0 | **CERTIFIED FALSE** |
| **Thm 4.3** | R−rh | Λ' signed via sub-ineqs (a)(b)(c) | **CERTIFIED FALSE** + direction misprint |

## Certificate 1 — Theorem 4.2 is false

Instance (all hypotheses hold):
- Baseline Pareto: F(t) = 1−t^{−1}, t ≥ 1 (c=1). Then t·h̃(t) = 1/(t−1)
  is decreasing on t > 1, and t·f'/f(t) = −2 is (weakly) decreasing — both
  hypotheses met exactly.
- α = (1,2) ∈ E_2^+, α_i ≥ 1; σ = (0,1) ∈ E_2^+; λ = (1,1) ∈ E_2^+;
  X^(i) =_st Y^(i) (common parameters).
- n = (1,2), n* = (2,1); r = (1/2,1/4), s = (2/5,1/5): sums = 1 each;
  n1r1n2*s2 = 1/10 ≤ 2/5 = n2r2n1*s1 ✓ (the required direction).

Claim: ζ(x) = f_U/f_{U*} increasing for x > σ1+cλ1 = 1 (U ≥_lr U*).
Computed exactly:

    ζ'(x) = −15 x (x−4) (x−1)² / 4(3x³−8x²+6x−2)²

- num roots on (2,∞): x = 4 only (denominator: 0 roots on (2,∞), > 0).
- ζ' > 0 on (2,4), ζ' < 0 on (4,∞) — Sturm: 1 root in (2,4), the root at 4.
- Rational witnesses: ζ(4) = 455/344 > ζ(5) = 535/406.
- **ζ is non-monotone ⇒ U ≥_lr U* fails. Theorem 4.2 is false.**

Proof gap located: in (4.8) the bracket requires
  (1/λ1)(f'/f)(u1) ≤ (1/λ2)(f'/f)(u2),  u_i = (x−σ_i)/λ_i.
With f'/f < 0 and t·f'/f decreasing, u1·f'/f(u1) ≤ u2·f'/f(u2) < 0, i.e.
|u1 f'/f(u1)| ≥ |u2 f'/f(u2)|; dividing the left by the smaller (x−σ1)
cannot be signed — the printed proof asserts it anyway. For Pareto the
difference equals −2/(x−σ1) + 2/(x−σ2) > 0 whenever σ1 < σ2.

Note: their validating Example 5.6 does satisfy the conclusion (ξ' numerator
deg 24, exactly 1 (tangent) root on (16,∞), sign + both sides) — sufficient
conditions are only sufficient.

## Certificate 2 — Theorem 4.3 is false (both readings)

Instance: Lomax baseline F(t) = 1−(1+t)^{−1} = t/(1+t), t ≥ 0 (c=0, as
required); f'/f = −2/(1+t) increasing ✓; t·h̃(t) = 1/(1+t) decreasing ✓;
α = 1 ∈ (0,1]; σ = 2 ≥ μ = 0; λ = (1,5), θ = (1,1): min λ = 1 ≥ max θ = 1 ✓;
n = (2,3), n* = (3,2); r = (1/4,1/6), s = (1/6,1/4), both sum-normalized.

Claim (as proved and as "validated" by their Ex 5.7): Λ = h̃_U/h̃_V
decreasing on x > 2. Exactly:

    Λ'(x) = 2(x⁴ − 28x³ + 34x² − 12x + 21) / [(x−2)²(x−1)²(x+3)²]

- denominator > 0 on (2,∞); numerator has exactly 1 root on (2,∞)
  (Sturm: 1 root in (25,35), none in (30,40)); Λ' < 0 then Λ' > 0 past it.
- Rational witnesses violating decrease: Λ(20) = 3890/1311 < Λ(80) =
  253960/85241 (cross-multiplied: 331587490 < 332941560).
- **Theorem 4.3 false** under the paper's own claimed direction.

**Direction misprint (independent defect):** printed Def 2.2 says
X ≤_{R−rh} Y iff h̃_X/h̃_Y is **increasing**; Thm 4.3 states
U ≤_{R−rh} V but the proof and Ex 5.7 prove/observe Λ **decreasing**.
Under the printed definition the theorem's direction is backwards too
(Λ(3) = 7 > Λ(5) = 15/4 would refute "increasing" on the same instance).
Either the definition or the theorem label is wrong; in both readings the
claim fails.

The broken sub-inequality is (b): (1/λ_i)f'/f(u_i) ≤ (1/θ_j)f'/f(v_j)
with f'/f < 0 — same scale-vs-magnitude gap as Thm 4.2.

## Verification of the paper's Section 5 (all as printed claims)

| Item | Claim | Result |
|---|---|---|
| Ex 5.1 | st holds (Pareto k=5) | ✓ 0 violations, 73-pt exact grid; tail cert: F_U−F_V has 0 roots on (14,∞) |
| Cex 5.1 | st fails | ✓ 62 exact witness pts, first x = 121/4 |
| Cex 5.2 | rh fails | ✓ CDF ratio dips at x = 27 (exact) |
| Cex 5.3 | lr fails | ✓ pdf ratio dips at x = 33 (exact) |
| Ex 5.2 | rh holds | ✓ 0 dips, 115-pt grid (transcendental, 25-digit) |
| Cex 5.4 | rh fails | ✓ 519 dips from x = 8 |
| Ex 5.3 | lr holds | ✓ 0 dips x > 14 (exact) |
| Cex 5.5 | lr fails | ✓ 282 dips from x = 37/2 (exact) |
| Ex 5.4 | st holds | ✓ 0 violations, 195-pt grid (numeric) |
| Cex 5.6 | st fails | ✓ 575 witnesses from x = 25/2 (numeric) |
| Ex 5.5 | rh holds | ✓ 0 violations (numeric) |
| Cex 5.7 | rh fails | ✓ 535 witnesses from x = 265/8 — **but printed weights violate Assumption 4.1**: n·r = 7/10, n*·s = 1/10 ≠ 1 |
| Ex 5.6 | lr holds | ✓ ξ' ≥ 0, 1 tangent root (exact) — consistent despite Thm 4.2 false |
| Cex 5.8 | lr fails | ✓ 25 dips from x = 49/4 — **s-weights unnormalized**: n*·s = 1/10 ≠ 1 |
| Ex 5.7 | Λ decreasing | ✓ 0 increasing steps (numeric); f'/f-increasing hypothesis verified |
| Cex 5.9 | Λ nonmonotone | ✓ 34 increasing steps from x = 6 |

## Verdict

Not a frozen-column-lift carrier — should be reclassified in the suspect
queue. But the two multi-outlier rate theorems are **false as stated**:
Thm 4.2 (certified via Pareto instance, ζ non-monotone on (4,∞)) and
Thm 4.3 (certified via Lomax instance, Λ increases past x ≈ 30; plus an
independent definition-vs-theorem direction inconsistency). The shared
mechanism is a new defect shape, not the BKB2022 lift: a term-wise sign
assertion (1/λ)f'/f(u) ≤ (1/θ)f'/f(v) that is invalid when f'/f < 0 —
the scale denominators fight the magnitude ordering. The st theorems
(3.1, 3.4), the separated max/min rate theorems (3.2, 3.3), and the
exact-algebra rh theorem (4.1) are correct; the Schur-convexity lift in
Thm 3.4 is legitimately applied to the additive CDF.

Minor: Cex 5.7 and 5.8 print mixing weights that violate the paper's own
normalization n1r1 + n2r2 = 1 (sums 7/10, 1/10; 1/10) — conclusions
verify anyway since h̃ sees only relative proportions.

## Files / reproduction

- `audit_bgsk.py` — Thm 4.2 certificate, Thm 4.1 admissible scan, Thm 4.3 sweep
- `verify_examples.py`, `verify_ex_fast.py`, `verify_sec4.py` — Sec 5 checks
- Certificates: all rational (sympy 1.14, `.venv-math`), Sturm counts via
  `Poly.count_roots`; ζ'/Λ' numerators printed fully factored above.
