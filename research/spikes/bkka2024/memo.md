# Audit: BKKA2024 — Bhakta, Kundu, Kayal, Alizadeh

"Stochastic orderings between two finite mixtures with inverted-Kumaraswamy
distributed components", *Mathematics* 12(6):852 (2024). OA at MDPI;
arXiv:2311.17568v2 (text audited from the arXiv PDF, `bkka2024.pdf` /
`bkka2024.txt`). Run dir: `research/spikes/context/runs/bkka2024/`.
Exact arithmetic: `/.venv-math/bin/python` (sympy 1.14, Fraction/Rational
throughout). Nothing committed.

## Model and notation

IK(α,β): F(x) = (1−(1+x)^{−α})^β, F̄ = 1−F. Mixture over columns
i=1..n with weights p_i. Audit substitution **y = 1/(1+x) ∈ (0,1)**
(decreasing in x): F_R(y) = Σ p_i (1−y^{α_i})^{β_i},
f_R(y) = Σ p_i α_iβ_i y^{α_i+1}(1−y^{α_i})^{β_i−1}; integer parameters make
everything polynomial → Sturm-exact. For the common-α theorems,
**g = 1−(1+x)^{−α} ∈ (0,1)** (increasing in x); rational β = k/L is
polynomialized by g = z^L.

L_n = {(ϱ,τ) rows : (ϱ_i−ϱ_j)(τ_i−τ_j) ≤ 0 ∀i,j} — antiordered rows.
Lemma 2.1 is the n=2 chain-majorization criterion (MOA/BHM-type):
Υ: R⁴₊→R preserves P≫Q on L_2 iff permutation-invariant and
Σᵢ(p_{ik}−p_{ij})[Υ_{ik}−Υ_{ij}] ≥ 0.

## Where the lift is (verbatim)

All chain-majorization theorems are **st-order claims on the additive SF**
Σp_i η(x;α_i,β_i) — the lift is *legitimate* here (frozen columns enter a
sum, not a ratio). The n≥3 reduction is outsourced, not proved in-text:

- **Thm 3.5 (n≥3 st, (p,α)∈L_n)**: "The proof of this theorem is similar to
  that of Theorem 4.2 of Bhakta et al. (2023). Thus, it is omitted."
  [Bhakta et al. 2023 = Bhakta–Majumder–Kayal–Balakrishnan, *Metrika* —
  =BMKB2024 in the cluster map.]
- **Thm 3.6** (k T-transforms, different structures, intermediates stay in
  L_n): "similar to that of the proof of Theorem 4.3 of Bhakta et al.
  (2023)".
- **Thm 3.8 (n≥3 st, (p,β)∈L_n)**: "The proof is similar to that of Theorem
  3.5, and thus it is omitted." Cor 3.2/3.3 and Thm 3.9 are the
  same/different-structure chain variants.
- Thm 3.3 cites "Lemma 2.4 of Bhakta et al. (2023)" for Schur-convexity of
  ψ(α)=Σp_i η_i — again additive, legitimate.

Spot check on generated admissible n=3 T-chains (`verify_examples.py` /
inline): Thm 3.5 instance (p=(.5,.3,.2), α=(1,2,4), T_{3/10} on cols 1,3,
β=1/2) — difference ≥0 at 39/39 exact algebraic evaluations; Thm 3.8
instance (p same, β=(1,3,6), same T, α=2) — ≤0 at 39/39. Holds on samples,
consistent with the additive-functional analysis.

## The carrier: Thm 3.10 (R−rh "ageing faster") — certified FALSE

**Statement.** R(X_{α,β};p) ≤_{R−rh} R(X_{α,β*};p*) — i.e.
r̃_R(x)/r̃_R*(x) non-increasing in x — "provided
max_{i≠j}|β_i−β_j| ≤ min_{i≠j}|β*_i−β*_j|". Note p,p* unconstrained and
not even in the hypothesis.

**Proof defect (certified).** The proof expands the derivative sign into a
quadruple sum (A15)–(A16) whose kernel is displayed as
  ∆_{i,j,k,l}(x) = {α(β_i−1)u −(α+1)} − {α(β*_k−1)u −(α+1)}
                 + αβ*_l u − αβ_j u,  u = (1+x)^{−α}/(1−(1+x)^{−α}) > 0.
Symbolically ∆ = **αu[(β_i−β_j)+(β*_l−β*_k)]**. The asserted "∆ ≤ 0 for all
i,j,k,l under the assumptions" is impossible: its max over quadruples is
range(β)+range(β*) > 0 whenever either vector is non-constant — the correct
sufficient condition would be range(β) ≤ −range(β*), i.e. the printed
max|·| ≤ min|·| hypothesis is exactly the wrong orientation for termwise
control. On the paper's own Example 3.6 parameters
(β=(.1,.2,.3), β*=(.5,1,2)): quadruple (i,j,k,l)=(3,1,1,3) gives
∆ = 17αu/10 > 0 (`certify_thm310.py`, symbolic). Same
frozen-columns-inside-a-ratio signature as the cluster defect, in a
max-vs-min costume: the summand couples the frozen indices i,j (β side)
and k,l (β* side) inside one signed kernel.

**Theorem fails.** r̃_R/r̃_R* = E_w[β]/E_w*[β*] with w_i ∝ p_i g^{β_i},
w*_j ∝ p*_j g^{β*_j}: d/dg log-ratio = [CV_w²(β) − CV_w*²(β*)]/g — the
boundary layer near g→0 is governed by the *smallest* spectral gap, and the
hypothesis pushes it the wrong way. Certificates:

- **Paper's Example 3.6 itself** (α=2, p=(.1,.3,.6), p*=(.2,.3,.5),
  β=(.1,.2,.3), β*=(.5,1,2); hypothesis .2 ≤ .5 holds). With g = z¹⁰ the
  ratio R(z) is rational; Sturm: numerator of R′ has **exactly 1 root in
  (0,1)**, no denominator roots; R′ > 0 at z ∈ {1/10, 1/4, 1/2} and < 0 at
  {3/4, 9/10, 19/20} — the ratio increases on a boundary layer.
  Exact witnesses: R(1/20) = 10775110255583/51200032000015 <
  R(1/10) = 35600534000000089/136004080000001360. The plotted Figure 5(b)
  shows a decreasing ratio because the increase lives at x ≲ 0.03 —
  invisible in their x∈(0,20) window.
- **Integer instance** β=(1,2,3), β*=(5,10,15), p=p*=(1/3,1/3,1/3)
  (range 2 ≤ min-gap 5): R(g) = (3g¹⁰−g⁹−g⁸+2g⁷−g⁶+2g⁵+g⁴−2g³+g²+g+1)
  /(15g¹⁰+10g⁵+5); dR/dg numerator degree 18, **exactly 1 root in (0,1)**;
  R increasing on g∈(0,g₀), g₀∈(2/5,3/5) ↔ x∈(0.29,0.58) for α=2 —
  macroscopic. R(1/20)=0.21045 < R(1/10)=0.22162 < R(1/5)=0.24508 <
  R(2/5)=0.28932 exact.
- n=2 already fails: β=(2,3), β*=(1,5), uniform weights — R′>0 on
  (0,g₀) with the crossing g₀∈(1/4,1/2); and β=(1,2), β*=(1,6),
  p=(3/4,1/4), p*=(1/4,3/4) — R′>0 on (0,g₀), g₀∈(1/10,1/4).
  So the failure is not even a lift-size artifact: the termwise bound is
  simply unsound. Both ratio directions fail on Example 3.6 (R nonmonotone
  ⇒ 1/R nonmonotone).

Also noted: numerically the printed quadruple-sum ξ does not equal the true
derivative up to a positive factor either (ratios 0.0087 vs 0.0234 at
x=2, x=3/2) — the intermediate algebra is additionally loose, though the
sign assertion is the operative (and false) step.

## The other non-additive theorems are TRUE (proofs repairable)

**Thm 3.11 (rh)**: R ≤rh R* provided max α* ≤ min α and
max{α_iβ_i} ≤ min{α*_jβ*_j}. The double-sum bracket (A19) is
  a_i b_i v^{−(a_i+1)}(1−v^{−a*_j}) − a*_j b*_j v^{−(a*_j+1)}(1−v^{−a_i}),
and the ratio of the positive parts factors as
  (a_i b_i)/(a*_j b*_j) · v^{a*_j−a_i} · (1−v^{−a*_j})/(1−v^{−a_i}),
a product of three factors each in (0,1] under the hypotheses → bracket
≤ 0 termwise → ξ ≤ 0. Theorem **true**; the hypotheses were chosen exactly
to make the bound work (they imply max β ≤ min β* as well). Scan: 0
violations over 180 admissible (a_i,a*_j,b_i,b*_j,v) tuples.

**Thm 3.12 (lr)**: R ≥lr R* provided max α ≤ min α* and
min{α_iβ_i} ≥ max{α*_jβ*_j}. Normalizing the (A21) bracket by
g_i g*_j > 0 gives
  B/(g_i g*_j) = (P−A)φ(A) + (C−Q)φ(C) + (C−A),
with A=α_i, C=α*_j, P=α_iβ_i ≥ Q=α*_jβ*_j, A ≤ C,
φ(t) = 1/(v^t−1) decreasing. Cases: if Q ≥ C or P ≥ A all terms ≥ 0
directly; the hard case P < A gives
  B/(g_i g*_j) ≥ (C−A)(1+φ(C)) − A(φ(A)−φ(C)) = ψ(C)−ψ(A) ≥ 0
since ψ(t) = t/(1−v^{−t}) is strictly increasing
(ψ′ ∝ 1−(1+u)e^{−u} > 0). Termwise bound **valid**: theorem true.
Scans: 0 violations over 151 + 258 adversarial tuples including
b_i→0, b*_j→0, C→A⁺, v→1⁺ boundary regimes.

## Verdicts on all results

| Claim | Type | Verdict |
|---|---|---|
| Thm 3.1 (st, p*≼_w p, (α,p),(α,p*)∈L_n) | additive | holds; Ex 3.1 verified (L_3 + ≼_w checked exactly; S̄(p*)−S̄(p) ≤0 on grid) |
| Cor 3.1 | additive | holds (≼ ⇒ ≼_w) |
| Thm 3.2 (st, (β,p)∈L_n) | additive | holds; Ex 3.2 verified |
| Thm 3.3 (st, α*≼_w α, β<1) | additive Schur | holds; Ex 3.3 verified |
| Thm 3.4 (n=2 st, (p,α)∈L_2, β<1) | additive base | holds; Ex 3.4 verified |
| Thm 3.5 (n≥3 st, L_n, β<1) | additive lift via BMKB Thm 4.2 | lift legitimate; holds on generated T-chain (39/39) |
| Cor 3.2, Thm 3.6 | additive lift | legitimate |
| Thm 3.7 (n=2 st, (p,β)∈L_2) | additive base | holds; Ex 3.5 verified |
| Thm 3.8 (n≥3 st, (p,β)∈L_n) | additive lift via Thm 3.5 | legitimate; holds on generated T-chain (39/39) |
| Cor 3.3, Thm 3.9 | additive lift | legitimate |
| **Thm 3.10 (R−rh, max-gap ≤ min-gap)** | **ratio of sums** | **FALSE — certified on Ex 3.6 itself + all tested admissible instances; proof's ∆_{ijkl}≤0 bound impossible under stated hypothesis** |
| Thm 3.11 (rh, max α* ≤ min α, max αβ ≤ min α*β*) | ratio, termwise | **TRUE** — analytic 3-factor proof; Ex 3.7 verified (d/dy[F*/F] ≤ 0, no interior sign changes; only endpoint roots y=0,1) |
| Thm 3.12 (lr, max α ≤ min α*, min αβ ≥ max α*β*) | ratio, termwise | **TRUE** — termwise bound provable via ψ(t)=t/(1−v^{−t}) monotonicity; Ex 3.8 verified on grid |

| Counterexample | Intent | Audit |
|---|---|---|
| Cex 3.1 ((α,p)∉L_3) | st fails | verified: hypotheses checked false exactly; crossing between y=7/12,3/5 |
| **Cex 3.2 ((β,p)∉L_3)** | st fails via sign change | **Printed numerics FALSE**: K1(x) = F̄(p*)−F̄(p) ≡ (1/10)·u^{28/5}(u^{51/5}−1) < 0 for ALL x>0 (u=x/(1+x)); claimed K1(10)=+0.00262105 — exact value −0.036459. The order does fail, but strictly in the opposite direction; no sign change exists |
| Cex 3.3 (α*⋠_w α) | st fails | verified: crossing at y∈(53/60,9/10) |
| Cex 3.4 (β=100∉(0,1)) | st fails | verified: crossing at y∈(1/5,13/60) |
| Cex 3.5 ((p,β)∉L_2) | st fails | verified (α=1): crossing at y∈(7/60,2/15) |
| Cex 3.6 (max α* ≰ min α) | rh fails | verified: d/dy[F*/F] sign change between y=1/12 and 1/10 |
| Cex 3.7 (max α ≰ min α*) | lr fails | verified: two sign changes at y∈(31/60,8/15), (7/10,43/60) |

Lemmas 3.1–3.3 (one-parameter monotonicity/convexity of η, ζ, κ) check out
analytically.

## Cluster fit

BKKA2024 is a **certified carrier, of the ratio-of-sums family but not via
the T-transform lift**: its chain-majorization theorems are all additive
st-order claims where the lift is legitimate, while the false claim
(Thm 3.10) is a separable max-gap/min-gap condition on the reversed-hazard
*ratio* — same frozen-columns-in-numerator-and-denominator phenomenon in
the quadruple-sum kernel ∆_{i,j,k,l}. Its rh (3.11) and lr (3.12) theorems
escape by using hypotheses strong enough to make the termwise bound
actually hold. The n≥3 lift proofs are outsourced to BMKB2023 (Metrika)
Thms 4.2/4.3 — flag that paper's hr/rh claims as the next audit target
(BKKA only inherits its *additive* uses). Lineage: Bhakta–Kayal avalanche;
Lemma 2.1 is the MOA/BHM2015/BKB2022-style n=2 criterion.

## Files

- `bkka2024.pdf`, `bkka2024.txt` — source (arXiv:2311.17568v2)
- `ik_lib.py` — exact IK-mixture library (F, f, r̃ in y/g/z; L_n,
  majorization, T-transform generators; Sturm wrapper)
- `certify_thm310.py` — ∆ symbolic certificate + Sturm/witness results
- `certify_thm311_312.py` — bracket scans + example certs (heavy Sturm
  steps on Cex 3.6/Ex 3.8 superseded by grid-exact witnesses)
- `verify_examples.py` — all Examples 3.1–3.8 + Counterexamples 3.1–3.7
