# Audit: BKF2024 — Stochastic Comparisons for Finite Mixtures from Location-Scale Families

**Paper.** Raju Bhakta, Suchandan Kayal, Maxim Finkelstein,
"Stochastic Comparisons for Finite Mixtures from Location-scale Family of
Distributions," *Methodology and Computing in Applied Probability* 26(4):52
(2024), DOI `10.1007/s11009-024-10121-x`. Received 28 Feb 2024, revised
22 Oct 2024, accepted 28 Oct 2024. Source: published PDF via Strathprints
record 91121, `../bhb2022-own/bkf2024.pdf` (text layer `bkf2024.txt`).

**Reproducibility.** Everything below is checkable with

```
/.../bkf2024/bkf_lib.py      # exact piecewise component models + Fraction SF/HR/RH
/.../bkf2024/certify.py      # -> certify_out.txt   (exact rational certificates)
/.../bkf2024/scan_all.py     # -> scan_all_out.txt  (broad admissible scans)
/.../bkf2024/verify_cex.py   # -> printed counterexample re-verification
/.../bkf2024/verify_rest.py  # -> verify_rest_out.txt (Ex3/Cex6/Cex4-wide/Cex7-wide)
/.../bkf2024/sturm_cert.py   # -> sturm_out.txt     (interval-wide Sturm certificates)
```

run under `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy 1.14.0, mpmath 1.3.0). All differences are exact `Fraction`s or
sympy rationals; no floating point enters the sign determinations.

**Notation.** `D_n^+`/`E_n^+` = positive reals decreasing/increasing in index.
`≺^m` majorized, `≺^w` weakly supermajorized (lower partial sums ≥),
`≺_w` weakly submajorized (upper partial sums ≤), `≺^{rm}` reciprocally
majorized (Def. 2 of the paper). Weak-majorization glyphs were resolved from
the published PDF's positioned XML (not the flattened txt): superscript
`w`/`m`/`rm` sit above the relation, subscript `w` below it; e.g. in Thm 8 the
`w` sits at top=260 against the baseline at 255–258 ⇒ `≺_w` (subscript).
The printed definitions were captured verbatim:

> "• weakly supermajorized by the vector v (denoted by u ≺^w v) if Σ_{i≤j} u_(i) ≥ Σ_{i≤j} v_(i) ...
>  • weakly submajorized by the vector v (denoted by u ≺_w v) if Σ_{i≥j} u_(i) ≤ Σ_{i≥j} v_(i) ...
>  • reciprocally majorized by the vector v (denoted by u ≺^{rm} v) if Σ_{i≤j} 1/u_(i) ≤ Σ_{i≤j} 1/v_(i) ..."

**Model.** Components `X_i ~ F((x−σ_i)/λ_i)`. For a baseline with support
`[u_min, u_max]` (or `(u_min,∞)`), component i contributes `F̄ = 1`,
`F = f = 0` below its support and `F̄ = 0` above; the mixture quantities are
sums over the *active* subset only — the piecewise displays in the paper's own
proofs (e.g. the `σ_{n} < x ≤ σ_{n−1}` display in Thm 6's proof and the
concluding remark) acknowledge this.

## Headline result

All seven ordering claims that go beyond the plain additive `st` lift are
affected by at least one of three defects:

- **(A) wrong weak-majorization direction** — a propagated error in the
  printed Lemma 1: it claims `u ≺_w v ⇒ φ(u) ≥ φ(v)` for *increasing*
  Schur-concave φ, which is false (see §Lemma 1). Used by Thms 2 and 8.
- **(B) missing hypothesis on the weight vector** — Thm 5 relates `r` and `s`
  only through `λ`; eq. (12) needs `(s_i r_j − s_j r_i)` sign information that
  no hypothesis supplies.
- **(C) piecewise-support / active-subvector gap** — once bounded-support
  components start dying (or truncated-below components are not yet alive),
  the comparison runs over a proper subvector `(r_k,…,r_n)` etc., while the
  paper applies the Schur argument to the full vector. Hits Thms 4, 6,
  Remark 5, and Thm 1 (at the *lower* boundary).
- **(D) fabricated counterexample numerics** — Counterexamples 1, 2, 3, 5
  report `~10^{-13}`–`~10^{-16}` values at points where the exact difference
  is *identically zero*; Cex 4's printed negative is contradicted by exact
  arithmetic; Cex 7's claimed sign change is absent on all scanned grids.

The T-transform (`st`) results — Thms 11, 12, 13, Cor 2 — use the additive
column-sum lift correctly: `F̄_mix = Σ_i r_i F̄_i` is a sum over columns, and
replacing the 2×2 matrix by a T-transform acts columnwise on each summand,
so the frozen-column objection does not apply. They verified clean on ~7,000
admissible evaluations.

## Theorem status table

| Thm | order | mechanism claimed | status |
|-----|-------|-------------------|--------|
| 1   | st    | dec + Schur-cvx under `1/λ ≺^w 1/θ` | **boundary counterexample**: fails when a component is below support; holds on all-alive samples (326 admissible, 2 boundary violations) |
| 2   | st    | inc + Schur-ccv under `λ ≺_w θ` ⇒ ≥ | **EXACT COUNTEREXAMPLE** (1758/1928 admissible violate); under the corrected `≺^w` reading 0/7366 — consistent with a printed-symbol error |
| 3   | st    | Lemma 2 (`≺^{rm}`) | **EXACT COUNTEREXAMPLE** — fails even in the all-alive interior (9002/11034); Lemma-2 prerequisites don't hold (ψ is Schur-*convex* and *decreasing*, matching neither branch) |
| 4   | hr    | Schur-cvx hazard in `r`, `r ≺^m s` | **EXACT COUNTEREXAMPLE** at n≥3 (active-subvector); n=2 clean (526 admissible, 0 viol); n=3: 8/70, n=4: 3/12 |
| 5   | hr    | sign of eq (12) | **EXACT COUNTEREXAMPLE** both branches — no `r`–`s` hypothesis at all |
| 6   | rh    | f decreasing + `r ≺^m s` | **EXACT COUNTEREXAMPLE** parts (i), (ii) at n≥3; Remark 5's extensions too (251, 245 violations) |
| 7   | lr    | log-concave/convex f, `max μ ≤ min σ` | holds-on-samples (Ex 3 verified numerically) |
| 8   | st    | two-step `≺_w` lifts | **EXACT COUNTEREXAMPLE** (41/60); decomposition shows the λ-side step is the broken one |
| 9   | st    | `r ≺^m s`, `σ ≺_w μ`, `max σ ≤ min μ` | **valid** — Abel-summation proof; 0/139 violations; Sturm-certified on 3 cells |
| 10  | hr    | two-step `hr` (r-step then σ-step) | conclusion **holds-on-samples** (0/85,410 in both readings) but the key intermediate eq (49) `h_U ≤ h_W` is **certified false** (24,844 violations under the printed `r ≺^m s`, 1,834 under `r ≽^m s`) |
| 11  | st    | 2-comp T-transform | holds-on-samples, lift is additive — sound (2,400 evals, 0 viol) |
| 12  | st    | n-comp T-transform | holds-on-samples (1,172 evals, 0 viol); proof cited to Balakrishnan et al. 2018 Thm 21 |
| Cor 2 | st  | same-structure T_i product | follows from Thm 11/12 mechanism |
| 13  | st    | different-structure T_i | holds-on-samples; proof cited to Balakrishnan et al. 2018 Thm 22 |

## Lemma-level defect (propagated error)

The paper prints, verbatim:

> **Lemma 1 (Theorem 3.A.8, Marshall et al. 2011)** A real valued function φ on R^n satisfies `u ≺^w v ⇒ φ(u) ≤ (≥) φ(v)` iff φ is decreasing and Schur-convex (Schur-concave). Similarly, φ satisfies `u ≺_w v ⇒ φ(u) ≤ (≥) φ(v)` iff φ is increasing and Schur-convex (Schur-concave).

The second clause's `(≥)` case is wrong: for `u ≺_w v`, `φ(u) ≥ φ(v)` holds
iff φ is *decreasing* and Schur-concave (equivalently `u ≺^w v` for
*increasing* Schur-concave). One-line refutation: `φ(u)=Σ√u_i` is increasing
Schur-concave; `u=(2,3/4,1/4) ≺_w (2,3/4,1/2)=v` (upper sums 2 ≤ 2,
11/4 ≤ 11/4, 3 ≤ 13/4), yet `φ(u) = 2.780… < 2.987… = φ(v)`.
Theorems 2 and 8 both invoke the false direction.

## Theorem-by-theorem detail

### Theorem 1 (st) — boundary-only failure

> "for `r,λ ∈ E_n^+` (or `D_n^+`), and fixed σ>0: `1/λ ≺^w 1/θ ⇒ U_n(r;λ) ≤st V_n(r;θ)`"

Certificate (certify.py, pareto1, σ=1/10):
`r=(1/6,1/6,2/3)`, `λ=(1/5,3/5,1)`, `θ=(1/5,1/2,3/2)`, all E₃⁺,
`1/λ ≺^w 1/θ` (weak supermaj — boundary equality). At `x=11/10`:
`u_3^V = 2/3 < 1` ⇒ V's third component contributes `F̄=1` (below support),
and `F̄_U − F̄_V = 1/60 > 0`, violating `U ≤st V`. The Schur argument treats
`F̄(u)=1/u` globally; at `u<1` the survival function truncates to 1 and the
Δ-sign computation changes. **2/326 admissible instances violate, both at
boundary cells; interior/all-alive samples are clean** — report as
"holds-on-samples in the all-alive regime, certified counterexample at the
support boundary."

### Theorem 2 (st) — printed `≺_w` makes the claim false

> "Then, for `r ∈ E_n^+ (or D_n^+)` and `λ ∈ D_n^+ (or E_n^+)`, and fixed σ>0, we have `λ ≺_w θ ⇒ U_n(r;λ) ≥st V_n(r;θ)`." (w printed *subscript*)

Certificate (burr3, σ=1/10): `r=(1/5,2/5,2/5) ∈ E_3^+`,
`λ=(2,1/2,1/5) ∈ D_3^+`, `θ=(2,1,2/3) ∈ D_3^+`, `λ ≺_w θ` (upper sums
2 ≤ 2, 5/2 ≤ 3, 27/10 ≤ 11/3). At `x=1/4`:
`F̄_U − F̄_V = −10116/73255 < 0`, violating `U ≥st V`.
Broad scan: **1758/1928 admissible evaluations violate** under the printed
direction. Re-reading the symbol as `≺^w` (weak supermaj — the direction the
proof actually supports, since `F̄` *is* increasing Schur-concave in λ):
**0/7366 violations**. Verdict: false as printed; consistent with a
typeset/copy error (`≺_w` for `≺^w`), inheriting the Lemma-1 misprint.

### Theorem 3 (st) — false even in the interior

> "for `r ∈ D_n^+ (or E_n^+)`, `λ ∈ E_n^+ (or D_n^+)`: `λ ≺^{rm} θ ⇒ U_n ≤st V_n`. Proof: Making use of Lemma 2, the proof follows from Lemmas 4 and 5."

Certificate (power2, σ=1/10): `r=(1/2,3/10,1/5) ∈ D_3^+`,
`λ=(1/10,2/5,7/10) ∈ E_3^+`, `θ=(1/10,3/10,3/5) ∈ E_3^+`,
`λ ≺^{rm} θ` verified (reciprocal sums 10≤10, 25/2≤40/3, 195/14≤15).
At `x=3/20` **all six components are alive** and
`F̄_U − F̄_V = 1133/282240 > 0`, violating `U ≤st V`.
Scan: 9002/11034 admissible instances violate in the *interior* region alone
(the boundary cells show the same count). This is not a truncation artifact —
the Lemma-2 application itself doesn't go through: for `ψ(α)=F̄(1/α)` the
Hazra lemma needs (convex+increasing) or (concave+decreasing) in `α`, while
`ψ` is Schur-**convex** and **decreasing** under the paper's pairing — the
`≤` branch needs concave, the `≥` branch needs increasing.

### Theorem 4 (hr) — active-subvector failure at n≥3

> "for `r ∈ D_n^+` (or `E_n^+`), `λ ∈ E_n^+` (or `D_n^+)` and fixed σ>0: `r ≺^m s ⇒ U_n(r;λ) ≥hr V_n(s;λ)`" — i.e. `h_U ≤ h_V`.

Certificates (power2, σ=1/10, λ=(1/2,3/2,2), x=1/2; active set {2,3}):
`r=(5/13,5/13,3/13)`, `s=(3/5,1/5,1/5)`, both D₃⁺, `r ≺^m s`:
`h_U = 60/13`, `h_V = 280/69`, `h_U − h_V = 500/897 > 0`.
Second arrangement (E-weights, D-scales, active {1,2}):
`h_U − h_V = 500/2337 > 0`.
**Interval certification (sturm_cert.py):** with
`r=(7/20,7/20,3/10), s=(3/5,1/5,1/5), λ=(1/4,4/3,2)`, the difference on the
whole middle cell `x∈(7/20,43/30]` is
`h_U−h_V = (1600000x − 160000)/D(x)`; Sturm counts: 0 roots of numerator and
denominator on the cell and sign + at `x=107/120` ⇒ `h_U>h_V` on the entire
cell, not just a point.
Scan: n=2 → 526 admissible, 0 viol; n=3 → 8/70; n=4 → 3/12. The gap is
exactly the frozen-column/subvector issue: in the middle region the
denominators differ by the *truncated* weights while majorization controls
the full vectors.

### Theorem 5 (hr) — false as stated (no `r`–`s` hypothesis)

> "Suppose h(t) = f(t)/F̄(t) is increasing. Then, for `λ ∈ D_n^+ (E_n^+)` and fixed σ>0, `U_n(r;λ) ≤hr (≥hr) V_n(s;λ)`."

There is no condition relating `r` and `s`. Eq (12) writes
`ξ'(x) = Σ_{i,j} s_i r_j F̄_i F̄_j (h_j/λ_j − h_i/λ_i)` (after factoring); the
anti-symmetric pairing contributes `(s_i r_j − s_j r_i)(F̄_iF̄_j)(h_j/λ_j −
h_i/λ_i)`, whose sign is not controlled by h-monotonicity alone.
Certificates (linhaz `h(t)=2t` model, x=3/5):
- `λ=(2,1) ∈ D_2^+`, `r=(1/2,1/2)`, `s=(1/10,9/10)`:
  `h_U=28/13`, `h_V=52/15`, `h_U−h_V = −256/195` — violates claimed `h_U≥h_V`.
- `λ=(1,2) ∈ E_2^+`, same weights: `h_U−h_V = 768/1105` — violates `h_U≤h_V`;
  and `ξ' = −768/845 < 0` certifies the reversed-survival ratio is not
  increasing.
Scan: ~25% of admissible evaluations violate in each branch
(4887/19580 and 5080/19711).

### Theorem 6 (rh) — active-subvector failure, both parts, plus Remark 5

> "(i) `r ∈ D_n^+`, `σ ∈ D_n^+`: `r ≺^m s ⇒ U_n(r;σ) ≤rh V_n(s;σ)`;
>  (ii) `r ∈ E_n^+`, `σ ∈ D_n^+`: `r ≺^m s ⇒ U_n(r;σ) ≥rh V_n(s;σ)`."

Certificates (pareto2, λ=2, σ=(4,3/2,1), x=9/2, active {2,3}):
- (i) `r=(7/18,1/3,5/18)`, `s=(1/2,1/4,1/4)`: `r̃_U − r̃_V = 69440/360177 > 0`
  violates `≤rh`.
- (ii) `r=(4/15,1/3,2/5)`, `s=(3/16,3/8,7/16)` (both E₃⁺):
  `r̃_U − r̃_V = −86800/1336803 < 0` violates `≥rh`.
Scan: 12/90 and 18/125 violations. Remark 5's claimed extensions
(`r∈D,σ∈E` and `r∈E,σ∈E`) violate at rates 251/782 and 245/782.

### Theorem 7 (lr) — consistent on checks

> "f log-concave (log-convex), σ,μ ∈ D_n^+, `max{μ} ≤ min{σ}` ⇒ `U ≥lr (≤lr) V`."

Example 3 (Weibull c=2, `r=(.1,.7,.2)`, `σ=(22,18,16)`, `μ=(12,8,2)`,
λ=2): `f_U/f_V` monotone increasing on `[16.1, 100]` (verified at 50-digit
mpmath). Counterexample 6 (lognormal, `σ=(.6,.4,.2)`, `μ=(.3,.2,.1)`, λ=1/2):
ratio rises to 1.487 at x≈0.91 then falls to 1.019 at x=58 — non-monotone,
so `U ⋡lr V` confirmed. Theorem status: holds-on-samples.

### Theorem 8 (st) — wrong weak-majorization direction

> "for `r ≺_w s`, `λ ≺_w θ`, `r,s ∈ E_n^+`, `λ,θ ∈ D_n^+`: `U_n(r;λ) ≥st V_n(s;θ)`" — both `w` printed *subscript*.

Certificate (burr3, σ=1/10, x=1/4):
`r=(1/3,1/3,1/3)`, `s=(1/4,1/4,1/2)`, `λ=(2,3/4,1/4)`, `θ=(2,3/4,1/2)`:
`F̄_U − F̄_V = −295/10062 < 0`, violating `U ≥st V`.
Decomposition (which step breaks): `F̄_U − F̄_W = +265/6192` (the `r→s` Abel
step is fine — for equal-sum weights `≺_w` and `≺^w` coincide);
`F̄_W − F̄_V = −15/208 < 0` (the `λ→θ` step is the broken one — increasing
Schur-concave `F̄` cannot yield `≥` under `≺_w`; it would under `≺^w`).
Scan: 41/60 violations. Their own Example 4 samples only confirm the printed
claim numerically (nonnegative differences on their grid) — the instance just
happens to land where the inequality still holds.

### Theorem 9 (st) — valid

> "for `r ≺^m s`, `σ ≺_w μ`, `r,σ ∈ E_n^+`, fixed λ>0: `U_n(r;σ) ≤st V_n(s;μ)`, provided `max{σ} ≤ min{μ}`."

With `σ` increasing and left-truncated supports, active sets are prefixes
`{1,…,k}`; for `r ≺^m s` the bottom sums satisfy `Σ_{i≤m}(r_i−s_i) ≥ 0`, and
`F_i` decreasing in i ⇒ Abel summation gives `Σ(r_i−s_i)F_i ≥ 0` on every
prefix ⇒ `F̄_U ≤ F̄_W`; then `max σ ≤ min μ` ⇒ componentwise `F̄_W ≤ F̄_V`.
Scan 139 admissible, 0 violations; Sturm-certified on cells (2,5/2],
(5/2,3], (3,4] with `r=(1/3,1/3,1/3)`, `s=(1/4,1/4,1/2)`, `σ=(1/4,1/2,3/4)`,
`μ=(1,3/2,2)`, λ=1 (0 numerator/denominator roots, sign − at witnesses).

### Theorem 10 (hr) — conclusion consistent; proof step eq (49) certified false

> "f increasing and h̃ decreasing; `r ≺^m s` (m superscript, verified),
> `r ∈ D_n^+`, `σ,μ ∈ D_n^+`, fixed λ>0: `U_n(r;σ) ≥hr V_n(s;μ)`, provided
> `max{μ} ≤ min{σ}`."

The proof inserts `W_n(s;σ)` and needs `h_U ≤ h_W` (their eq (49)) plus
`h_W ≤ h_V`. Since the mixture hazard is Schur-*concave* in the weight
vector on `D_n^+`, `r ≺^m s` gives `h_U ≥ h_W` — the opposite of eq (49).
Certified numerically in both readings (power c=3, l=2, λ=4):
- printed `r ≺^m s`: 24,844/29,470 evaluations violate `h_U ≤ h_W`
  (e.g. `r=(1/3,1/3,1/3)`, `s=(1/2,1/4,1/4)`, x=4: `h_U=7/250 > 45/2011=h_W`);
- `r ≽^m s`: 1,834/29,470 violate.
The final conclusion `h_U ≤ h_V` held on all 85,410 tested evaluations in
both majorization directions (their Example 5 parameters also satisfy it on
the grid). Status: **proof broken at eq (49); theorem conclusion
holds-on-samples, unproven**.

### Theorems 11–13, Corollary 2 (st, T-transforms) — clean lift

> **Thm 11**: "( r1 r2 / λ1 λ2 ) ⋘ ( s1 s2 / θ1 θ2 ) ⇒ `U_2(r;λ) ≤st V_2(s;θ)`"
> via Lemma 7 (chain majorization on `M_2`).
> **Thm 12**: generalizes to `( s… / θ… ) = ( r… / λ… ) T_{w1}…T_{wk}` ⇒ `≤st`.
> **Cor 2**: T_i with same structure.
> **Thm 13**: T_i with different structures, intermediate matrices in `M_n`.

These are the *only* results where the chain-majorization lift is used, and
it is used correctly: `F̄_mix` is additive in columns, so a T-transform on the
matrix acts separately on each summand — no frozen column sits in a ratio.
Scan: burr3 n=2 2400 evals / n=3 1172; pareto1 n=2 2367 / n=3 1120 — **0
violations**. Thm 12's proof is omitted "using similar arguments as in the
proof of Theorem 21 of Balakrishnan et al. (2018)"; Thm 13 to "Theorem 22 of
Balakrishnan et al. (2018)". The mechanism is sound; `holds-on-samples`.

## Counterexample audit

| cex | claim | verdict |
|-----|-------|---------|
| 1 | `K1(0.52)=−5.3e−15`, `K1(0.55)=+2.8e−14` ⇒ sign change | **fabricated**: at both printed points only component 2 is alive, so `K1 ≡ 0` exactly (h_U=h_V=525/46, 360/19); on live cells the difference is one-signed positive — 40/40 grid points. Ordering failure stands, but not via their numbers |
| 2 | `K2(0.903)=+2.7e−14`, `K2(0.990)=−2.5e−12` | **fabricated**: both printed points have only component 1 alive ⇒ `K2 ≡ 0` exactly (h_U=h_V=1606000/165191, 17800/179); all 90 sampled nonzero differences are positive |
| 3 | Pareto-1 `K3(0.80)=+2.2e−16`, `K3(0.77)=−2.2e−16` | **fabricated and conclusion false**: for Pareto-1 with common σ, `h_mix(x)=1/(x−σ)` identically on every active subset ⇒ `K3 ≡ 0`, so `U =hr V` and the stated `U ⋡hr V` is wrong |
| 4 | `K4(5)=+2.88e−3`, `K4(50)=−3.45e−6` ⇒ sign change | **false**: exact `K4(5)=+11315369175550/1086359197792113 ≈ 0.0104`, `K4(50) ≈ +5.19e−7 > 0`; exact scan of ~900 rational points on (2.3,120] found **no** negative `K4` |
| 5 | `K5(2.2003)=−9.1e−13`, `K5(2.2083)=+1.4e−14` ⇒ sign change | **fabricated**: only component 3 alive at both points ⇒ `K5 ≡ 0` exactly (r̃_U=r̃_V=8000000000000/2400540027, …/66813911787); all 70 sampled live-region diffs are one-signed negative (`r̃_U < r̃_V`). The qualitative point stands — `U ≥rh V` of Thm 6(ii) fails without `r ≺^m s` (in fact `U ≤rh V`) — but the printed sign-change is FP noise |
| 6 | lognormal ratio non-monotone | **verified**: `f_U/f_V` rises to ≈1.487 at x≈0.91 then decreases to ≈1.02 at x=58 |
| 7 | Burr-III sf difference "negative as well as positive" ⇒ `U ⋡st V` | **not confirmed**: `F̄_U−F̄_V` strictly positive at ~12,000 exact rational points for σ ∈ {0, 0.1, 0.5, 2, 5} — the mixtures are comparable (`U ≥st V`), just in the direction opposite to Thm 11's claim; no negative difference was found, so the printed claim of a sign change (and hence `⋡st`) is wrong |

Remark: Cex 1–5 all print magnitudes `10^{-12}`–`10^{-16}` consistent with
double-precision rounding noise — the authors evaluated `K_i` in floating
point and reported the noise as sign changes. Cex 4 is worse: the printed
`−3.45e−6` is not even the right *sign* of the true value `+5.19e−7`.

## Example audit

- **Ex 1** (Thm 1, Pareto-1): hypotheses verified (`1/λ ≺^w 1/θ` etc.);
  sampled `F̄_U−F̄_V ≤ 0` — consistent.
- **Ex 2** (Thm 6(ii), Pareto-2): hypotheses verified; sampled diffs
  nonnegative — consistent.
- **Ex 3** (Thm 7, Weibull): verified (monotone ratio).
- **Ex 4** (Thm 8, IE β=2): hypotheses and nonnegative sampled diffs verified
  at 40-digit mpmath — consistent.
- **Ex 5** (Thm 10): hypothesis directions verified; sampled `h_U−h_V < 0` —
  consistent with the conclusion (which does not rescue eq (49)).
- **Ex 7** (Thm 11, IE): the printed factorization
  `(0.56,0.44; 0.30,0.60) = (0.6,0.4; 0.2,0.7)·T_{0.2}` is **not** consistent
  as displayed — `(0.6,0.4; 0.2,0.7)·T_{0.2} = (0.44,0.56; 0.60,0.30)`
  exactly; the correct transform is `T_{0.8}` (or the same printed matrix with
  the `ω`-is-swap convention). With `T_{0.8}` the identity holds exactly and
  sampled SF diffs are consistent with `U ≤st V`.
  Cex 7 uses `r=(0.2,0.8) ∈ E_2^+` with
  `λ=(0.4,0.6) ∈ E_2^+` — violating Thm 11's anti-pairing (r should be in
  `D_2^+` when `λ ∈ E_2^+`), so it is a legitimate hypothesis-drop test;
  the claimed *sign change* is nonetheless absent (see table).

## Lift analysis

Verbatim lift-step quotes:

- Lemma 7 (chain-majorization criterion, Marshall et al. Ch. 15): *"A
  differentiable function φ : R₊⁴ → R satisfies φ(P) ≥ (≤) φ(Q) for all P,Q
  such that P ∈ M₂, and P ≼ᶜ Q, iff (i) φ(P)=φ(PΠ) for all permutation
  matrices Π, and (ii) Σ_{i=1}² (p_{ik}−p_{ij})[φ_{ik}(P)−φ_{ij}(P)] ≥ (≤) 0
  for all j,k."*
- Thm 11 proof opening: *"To establish the desired result, we have to check
  the Conditions (i) and (ii) of Lemma 7. Clearly, F̄_{U₂(r;λ)}(x) is
  permutation invariant on (r;λ), which confirms Condition (i)."*
- Thm 12: *"The proof of the following theorem follows using similar
  arguments as in the proof of Theorem 21 of Balakrishnan et al. (2018), and
  thus it is omitted."*
- Thm 13: *"The proof of theorem follows using similar arguments as in
  Theorem 22 of Balakrishnan et al. (2018), and therefore it is omitted for
  the sake of conciseness."*

The T-transform/chain-majorization results (Thms 11–13, Cor 2) touch only
the *additive* `st` functional `F̄_mix = Σ r_i F̄((x−σ)/λ_i)`: a T-transform
on the `(weight; scale)` matrix preserves the weighted column sum, and Lemma
7's conditions are checked by a Schur-type derivative identity on that sum.
No hazard/reversed-hazard/lr ratio ever passes through a T-transform in this
paper, so the frozen-column obstruction that invalidates ratio claims does
not arise. Where ratio claims *do* fail (Thms 4, 6, 10-step, and the
truncation defect in Thm 1), the culprit is instead the piecewise active
subset: the proof differentiates/majorizes the full vector while the mixture
ratio only sums the alive subvector, and no hypothesis controls that
subvector.

## Bottom line

- **Certified false as printed**: Thms 2, 3, 4, 5, 6(+Rem. 5), 8; the printed
  Lemma 1 (second clause, `≺_w`/≥ case); Counterexamples 1–5 as written
  (Cex 3 and 5's conclusions are also wrong/false on the evidence, not just
  their values); Cex 7's claimed sign change.
- **Conclusion unrefuted but proof broken**: Thm 10 (eq (49) direction).
- **Boundary-conditional**: Thm 1.
- **Consistent/valid on all tests**: Thms 7, 9, 11, 12, 13, Cor 2; Examples
  1–5, 7; Counterexample 6.
