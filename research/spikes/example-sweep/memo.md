# Example-sweep: exact verdicts on every printed numeric claim in the audit cone

Run dir: `research/spikes/context/runs/example-sweep/` (gitignored). 2026-09-26.
Exact arithmetic: `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(Fraction/sympy where algebraic; mpmath 50–60 dps with independent-identity
cross-checks otherwise). Script: `sweep.py`; re-runs of prior per-paper
verifiers: `mixture-claim-audit/verify_paper_cex.py`, `bkf2024/verify_cex.py`,
`bkka2024/verify_examples.py` (regenerated this run).

## Retrievable-text inventory

| Paper | Text | Printed-numeric evidence? |
|---|---|---|
| SKF2026 (ASMBI 42:e70089) | `hf2018-deep/skf2026.txt` | yes: 3 point-value claims + figure sign claims |
| BKF2024 (MCAP 26:52) | `hf2018-deep/bkf2024.txt` | yes: 10 printed values in Cex 1–5 + T-product in Cex 7 |
| SPBB2026 (JIA 2026:28, Shekari et al.) | `shekari2026/shekari2026.txt` | yes: 4 printed T-products + 1 hypothesis claim |
| SKB2026 (Mathematics 14:2557) | `gy2024-skb2026/skb2026.txt` | figure claims only (Ex 1–11) + MLE data tables (not checkable) |
| GY2024 (arXiv:2407.15638) | `gy2024-skb2026/gy2024_pdf.txt` | yes: 6 printed T-transform products |
| BKKA2024 (Mathematics 12:852) | `bkka2024/bkka2024.txt` | yes: 2 printed values in Cex 3.2 |
| BTDK (arXiv:2412.10071) | `btdk-arxiv/paper.txt` | yes: pdf coefficients, 2 majorization claims |
| BHKKB2025 (Sankhya B 87:573) | `bhb2022-own/bhkkb2025.txt` | yes: 1 product inequality + weight vector |
| SAF2022 (PEIS 36:1055) — control | `mixture-claim-audit/SAF2022.txt` | yes: 4 printed arithmetic claims |
| SMH2026, VKF2025, BGSK-2511.00791, BKB2022, HF2018, NT2020 | **not retrievable** (closed access / no text) | — |

## Master table — printed numeric claims

Verdicts: **verified** (exact match), **sign-wrong**, **wrong-value**
(magnitude wrong), **FP-noise** (claimed nonzero value at a point where the
difference is identically zero, or identity-level cancellation), **fabricated**
(claimed qualitative phenomenon — sign change — does not exist),
**misprint** (digit/entry wrong; intended claim reproduces).

### SKF2026 — α-mixtures, resilience-scaled (ASMBI 42:e70089)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 1 | Cex 3.5 | `Ḡ_U(10)−Ḡ_V(10) = −0.08887328` | **verified** (60-dps −0.0888732807576) |
| 2 | Cex 3.7 | `Ḡ_U(20)−Ḡ_V(20) = −0.08336543` ⇒ ordering fails | **sign-wrong**: exact `+0.06744747` — ordering holds; counterexample void |
| 3 | Cex 3.8 | `h_U(6)−h_V(6) = −1.110223e−16`, `h_U(7)−h_V(7) = +2.220446e−16` ⇒ sign change | **FP-noise**: `h_U ≡ h_V = 7/(2t)` identically (scalar γ, Pareto baseline); the two printed epsilons are float64 representation error, not a sign change |

Figure-claim tier (all re-verified): Ex 3.1/3.2/3.3 diff ≤0 ✓; Cex 3.1, 3.2,
3.3, 3.4 (hr), 3.6, 3.9, 3.11 sign changes ✓ (exact roots/Sturm);
Ex 3.4/3.5/3.6/3.7/3.8 sign claims ✓; Cex 3.10, 3.12 ratio non-monotone ✓.
(`verify_paper_cex.py` rerun; roots at u=1 are the generic t=0 SF coincidence.)

### BKF2024 — location-scale mixtures (MCAP 26:52)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 4 | Cex 1 | `K1(0.52) = −5.32907e−15`, `K1(0.55) = +2.84217e−14` ⇒ sign change | **FP-noise + fabricated**: only component 2 alive at both t ⇒ `K1 ≡ 0`; in the all-alive region sign is constantly + — no sign change exists |
| 5 | Cex 2 | `K2(0.903) = +2.66454e−14`, `K2(0.990) = −2.50111e−12` ⇒ sign change | **FP-noise + fabricated**: `K2 ≡ 0` at both printed points; every nonzero evaluation on (0.11,1] is + |
| 6 | Cex 3 | `K3(0.80) = +2.22045e−16`, `K3(0.77) = −2.22045e−16` ⇒ sign change | **FP-noise + fabricated**: for Pareto `F̄=t⁻¹`, `h_U = h_V = 1/(x−σ)` identically for *any* weights/scales — difference is exactly zero everywhere |
| 7 | Cex 4 | `K4(5) = +0.0028828`, `K4(50) = −3.44858e−6` ⇒ sign change | **wrong-value + sign-wrong**: exact `+0.0104159` and `+5.18685e−7`; `K4 ≥ 0` on all of (1,60) — no sign change |
| 8 | Cex 5 | `K5(2.2003) = −9.09495e−13`, `K5(2.2083) = +1.42109e−14` ⇒ sign change | **FP-noise + fabricated**: only component 3 alive ⇒ `K5 ≡ 0` at both; genuine region constantly − |
| 9 | Cex 7 | `[s;θ] = [r;λ]T_{0.3} = (0.62,0.38;0.54,0.46)` | product **verified** exactly; but the claimed SF sign change (Fig 6a) is **absent** on exact scan (all +) — fabricated conclusion |

Figure-claim tier: Ex 1 (st), Ex 2 (rh), Ex 4 (st), Ex 5 (hr) verified on exact
grids; Ex 3(i)/(ii) lr ratios and Cex 6 (lognormal) consistent numerically.

### SPBB2026 — distorted mixtures (JIA 2026:28)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 10 | Ex 1 | `(γ,π)T_{0.8} = (0.34,0.46;0.56,0.44)` | **verified** |
| 11 | Ex 1 | "`D(Ḡ;γ)` and `−D′(Ḡ;γ)` are decreasing and convex in `0<γ<1`" (θ=0.6) | **false**: `−D′` is *increasing* and *concave* in γ for small `u` (e.g. `u=e^{−2}`: 65/93 increasing steps; `u=0.05`: 76/93). Conclusion direction still holds on grid |
| 12 | Cex 1 | `(γ,π)T_{0.4} = (5.2,4.8;0.56,0.44)` | **verified** |
| 13 | Cex 2 | `(γ,π)T_{0.3} = (7.9,5.1;0.38,0.62)` | **verified** |
| 14 | Ex 2 | `(γ*,π*) = (γ,π)T_1T_2T_3 = (4.28,3.76,3.95;0.27,0.38,0.35)` | **wrong-value** (NEW): exact product is `(3.992,3.464,3.544;0.2848,0.4416,0.3736)`; no ordering/transposition of the printed T's reproduces the printed output. (Printed T₃ is a 3-cycle — doubly stochastic but not itself a T-transform.) |

### GY2024 — MPHR mixtures (arXiv:2407.15638)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 15 | Ex 1 | `(p,α)T_{0.4} = (0.48,0.52;0.36,0.34)` | **verified** |
| 16 | Ex 2 | `T_1=(1,0,0;0,.4,.6;0,.8,.2)`, `T_2=(1,0,0;0,.2,.8;0,.6,.4)`; `(q,β)=(p,α)T_1T_2 = (0.2,0.388,0.412;0.5,0.212,0.188)` | **misprint/malformed matrices**: printed T₁,T₂ are not doubly stochastic and their literal product gives `(0.2,0.272,0.528)`; under the intended pairwise T-transforms (w=0.4 then w=0.2 on coords 2,3) the printed `q,β` are **exact** |
| 17 | Ex 3 | printed `T_1,T_2,T_3`; `(q,β) = (0.4192,0.248,0.3328;0.4456,0.568,0.4904)` | matrices malformed (composite rows, not doubly stochastic); semantic sequence reproduces `q` **exactly**; `β_2` printed `0.568` vs exact `0.564` — digit **misprint** |
| 18 | Ex 4 | `(p,λ)T_{0.3} = (0.62,0.38;0.325,0.425)` | **verified** |
| 19 | Ex 5 | `(p,λ)T_1T_2 = (0.5,0.268,0.232;3,4.44,4.56)` | **verified** |
| 20 | Ex 6 | `(p,α)T_{0.9} = (0.34,0.66;0.66,0.34)` | **verified** |

### BKKA2024 — inverse-Kumaraswamy mixtures (Mathematics 12:852)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 21 | Cex 3.2 | `K1(10) = +0.00262105`, `K1(100) = −0.00408561` ⇒ sign change | **sign-wrong + wrong-value + fabricated**: `K1(x) = (1/10)u^{28/5}(u^{51/5}−1)`, `u=x/(1+x)`, is `<0 ∀x>0`; exact `K1(10)=−0.0364592`, `K1(100)=−0.0091282` |

All other BKKA2024 examples/counterexamples (Ex 3.1–3.7, Cex 3.1,3.3–3.5)
re-verified exactly this run (`verify_examples.py`); only Cex 3.2 fails.

### BTDK — arithmetic M-O mixtures (arXiv:2412.10071)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 22 | Cex 3.1 | `f_U(x) = (3/320)((x−4)/12)²I(x>4) + (21/640)((x−2)/8)²I(x>2)` | coefficients **verified** exactly |
| 23 | Cex 4.1 | `σ=(6,6,6,8,8) ≼w μ=(4,4,4,12,12)` | **verified** (weak submajorization, all 5 partial sums) |
| 24 | Cex 4.2 | `σ=(9,9,9,9,6,6,6) ≼w μ=(15,15,15,15,2,2,2)` | **verified** |
| | Cex 4.1/4.2 | "the cdfs intersect" (Fig 1) | **verified** at 60 dps (both cross) |

### BHKKB2025 — ELS outliers (Sankhya B 87:573)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 25 | Ex 5.5 | `n₁r₁n₂*s₂ = 0.56 ≥ 0.06 = n₂r₂n₁*s₁` | **verified** (14/25 vs 3/50) |
| 26 | Cex 5.7 | weights `n=(10,10),n*=(7,3), r=(.03,.04), s=(.01,.01)` | **invalid**: `Σnᵢrᵢ = 0.7`, `Σnᵢ*sᵢ = 0.1` — the printed weights do not sum to 1; not legitimate mixture weights (same defect as BGSK Cex 5.7) |

### SAF2022 — control paper (PEIS 36:1055)

| # | Item | Printed claim | Exact verdict |
|---|---|---|---|
| 27 | Ex 6.7 | `(α₁p₁,α₂p₂,α₃p₃) = (1.375,1.05,0.4)` | **verified** |
| 28 | Ex 6.10 | `(αp) = (0.24,0.15,0.06)` | **verified** |
| 29 | Ex 6.19 | `(αp) = (1.375,1.35)` | **verified** |
| 30 | Ex 6.16 | `λ̄ = (0.63,0.63,0.63)` | **verified** (19/30 = 0.6333…) |

Figure-claim tier: Cex 6.8, 6.20, 6.23, 6.24, 6.25 (all "ordering fails") and
Ex 6.19 — all verified exactly (Sturm) or at 60 dps this run.

## Headline numbers

Counting **each example/counterexample that makes a printed numeric or printed
matrix-product claim** (figure-only sign claims excluded — all verified anyway
except BKF2024 Cex 7 which is counted with its T-product):

| Bucket | Items | Refuted | Refuted % |
|---|---|---|---|
| Certified-defect carriers (SKF, BKF, SPBB, BKKA) | 14 | **11** | 79% |
| Suspect cone, not yet defect-certified (GY, SKB, BTDK, BHKKB) | 12 | **4** | 33% |
| Control (SAF2022) | 4 | 0 | 0% |
| **All** | **30** | **15** | **50%** |

Refuted = at least one printed numeric claim is sign-wrong, wrong-value,
FP-noise at an identically-zero point, a fabricated sign change, a malformed/
non-T "T-transform", or an invalid weight vector.

## Patterns

1. **FP noise presented as evidence** (BKF2024 Cex 1,2,3,5; SKF2026 Cex 3.8):
   values at machine-epsilon scale (±1e−16 … ±1e−12) printed as proof of sign
   changes at points where the difference is *identically zero* — either a
   single alive component, or a baseline whose mixture hazard is
   parameter-free (`1/(x−σ)`, `γ/(2t)`).
2. **Fabricated sign changes** (BKF2024 Cex 1–5, 7; BKKA2024 Cex 3.2): the
   claimed sign change does not exist anywhere; where the function is nonzero
   it keeps one sign.
3. **Sign-wrong point values** (SKF2026 Cex 3.7: −0.0834 vs +0.0674;
   BKKA2024 K1(10): +0.0026 vs −0.0365; BKF2024 K4(50): −3.4e−6 vs +5.2e−7).
4. **Wrong/malformed printed matrices and products** (GY2024 Ex 2, 3;
   SPBB2026 Ex 2): printed "T-transforms" that are not doubly stochastic, or
   products that match no ordering of the printed factors.
5. **Invalid printed weights** (BHKKB2025 Cex 5.7): mixture weights summing
   to 0.7 / 0.1.

## Caveats

- 60-dps evaluations corroborate exact identities (`h_U ≡ h_V`, `K ≡ 0`) — the
  zero results are proven by symbolic simplification / single-alive-component
  reductions in `bkf2024/bkf_lib.py` and `verify_paper_cex.py`, not by
  floating point.
- SKB2026 Examples 3–11 are figure-only claims (hr/rh diffs, lr ratios);
  spot-checks in the prior audit were consistent; the MLE tables (Sec. 5) are
  data-analysis outputs, not machine-checkable claims.
- SPBB2026 Example 1(i): the printed hypothesis sentence is false for `−D′`,
  but the example's ordering conclusion still holds numerically — hypothesis
  check wrong, conclusion accidentally right.
- BKF2024 Cex 6 (lognormal, lr non-monotone) was consistent with prior numeric
  work; no printed point values.
