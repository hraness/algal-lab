# Audit memo: Barmalzan–Kosari–Balakrishnan (2022) T-transform lemmas

Run dir (gitignored): `research/spikes/context/runs/bhb2022/`.
Sibling audit: `research/spikes/mixture-audit/memo.md`.

## The paper

**[BKB2022]** G. Barmalzan, S. Kosari, N. Balakrishnan, *Orderings of finite
mixture models with location-scale distributed components*, Probability in
the Engineering and Informational Sciences **36**(2), 461–481 (April 2022).
DOI: 10.1017/S0269964820000467. Published online 14 Sep 2020.
(SKF2026 cites it as "Barmalzan et al. (2022)" — reference list confirmed.
NOTE: the task prompt guessed "Haidari"; the actual middle author is Kosari.)

No open-access full text found (Cambridge paywall; no arXiv/Strathprints AM;
Semantic Scholar `openAccessPdf` empty). Lemma statements below are verbatim
from SKF2026 §2 (the citing paper, local `SKF2026.txt`), corroborated by an
independent open-access rendering: Shekari, Pakdaman, Saadat Kia Barmalzan &
Balakrishnan, J. Inequal. Appl. 2026:28, whose Lemma 7 states the same iff
condition and attributes it to **Theorem 2 of Balakrishnan, Haidari &
Masoumifard (2015), IEEE Trans. Reliab. 64(1), 333–348** — the 2×2 lemma
predates BKB2022 (BKB restate it).

## Lemma statements as used by SKF2026 (verbatim)

**Lemma 2.4 (Barmalzan et al. (2022))**: "A differentiable function
Ψ : R⁴₊ → R₊ satisfies
    Ψ(A) ≥ Ψ(B) for all A, B such that A ∈ V₂ (W₂), A ≫ B        (2.1)
if and only if
  (i)  Ψ(A) = Ψ(AΠ) for all permutation matrices Π, and for all A ∈ V₂ (W₂);
  (ii) Σ_{i=1}^{2} (a_{ik} − a_{ij}) [Ψ_{ik}(A) − Ψ_{ij}(A)] ≥ 0 for all
       j, k = 1, 2, and for all A ∈ V₂ (W₂), where Ψ_{ij} = ∂Ψ/∂a_{ij}."

**Lemma 2.5 (Barmalzan et al. (2022))**: "Let Ψ : R²₊ → R₊ be a
differentiable function, and define Ψ_n : R^{2n}₊ → R₊ by
Ψ_n(A) = Σ_{i=1}^{n} Ψ(a_{1i}, a_{2i}). If Ψ₂ satisfies condition (2.1),
then it follows that Ψ_n(A) ≥ Ψ_n(B), where A ∈ V_n (W_n) and B = AT."

## Verdict (headline)

**Both lemmas are true; the failure is SKF's application.** Lemma 2.5 only
lifts *separable sums* Ψ_n(A) = ΣᵢΨ(a_{1i},a_{2i}); SKF feed it
h̃_{p,γ}(y) = Σpᵢγᵢy^{γᵢ}/Σpᵢy^{γᵢ}, a ratio of sums. The BKB lemma chain
is sound — the T-transform error lives in SKF Thm 3.8's proof, full stop.

## Are the lemmas true? — verification detail

**Lemma 2.4 — TRUE.** Proof skeleton verified symbolically
(`audit_bhb.py` [A]). Along the T-path A(ω) = A·(ωI + (1−ω)Π₁₂):

- d/dω Ψ(A(ω)) = Σᵢ(a_{i1}−a_{i2})(Ψ_{i1}−Ψ_{i2})|_{A(ω)} — exact identity;
- a_{i1}(ω) − a_{i2}(ω) = (2ω−1)(a_{i1} − a_{i2}), so the column-gap product
  picks up (2ω−1)² ≥ 0: **V₂ and W₂ are closed under the T-path**;
- hence condition (ii) at A(ω) forces sign dΨ/dω = sign(2ω−1): Ψ(A(ω)) is
  unimodal with min at ω = 1/2, so Ψ(A) ≥ Ψ(A(ω)) for all ω ∈ [0,1];
  necessity follows from ω → 1. (Standard result — MOA Ch.5 lineage.)

**Lemma 2.5 — TRUE.** For separable Ψ_n, a T on columns j,k leaves the other
columns untouched:
    Ψ_n(A) − Ψ_n(AT^{jk}) = Ψ₂(A^{jk}) − Ψ₂(A^{jk}T₂),
verified symbolically ([B]); A ∈ V_n(W_n) ⟹ every column pair ∈ V₂(W₂),
checked on 731 rational instances. The hypothesis "Ψ₂ satisfies (2.1)" is
exactly what is needed.

Sanity sweep, separable Ψ (sweep_bhb.py [1], exact Fraction arithmetic,
3000 draws): Ψ(a,b)=a·b has pair-sum 2(a_{12}−a_{11})(a_{22}−a_{21}), which
is ≤0 on V₂ and ≥0 on W₂ — predicted Ψ_n(A) ≤ Ψ_n(AT) on V_n and
Ψ_n(A) ≥ Ψ_n(AT) on W_n. Result: **0/698 V₃ and 0/736 W₃ violations of the
predicted directions** (per-class recount after fixing a class-mixing artifact
in the first pass). Ψ=a²+b² (pair-sum 2Σᵢ(a_{i2}−a_{i1})² ≥ 0 identically):
**0/1044** violations of Ψ_n(A) ≥ Ψ_n(AT) across both classes.

## The misuse, pinpointed

SKF Thm 3.8 proof (SKF2026.txt l.1244–1246) sets Ψ_n([γ p]) := h_{U_n}(t)
and invokes Lemma 2.5. But:

**(a) h̃ is not separable — exact certificate ([C]).** With the T acting on
columns (1,3) of a 2×3 matrix, h̃(A) − h̃(AT) changes when the *untouched*
column 2 changes (col₂ = (2,1/4) vs (9,3/8) give different values at y = 3).
A separable Ψ_n would give a column-2-free difference. So Lemma 2.5 cannot
be invoked; and Thm 3.7's genuine n = 2 verification does not lift.

**(b) The necessary differential condition also fails ([D2]).** For a
general differentiable Ψ_n on R^{2n}, T-monotonicity on W_n in the claimed
direction requires (ω→1 limit) the n-column analogue of Lemma 2.4(ii):
    M_{jk}(A) := Σᵢ (a_{ik} − a_{ij})(Ψ_{ik} − Ψ_{ij}) ≤ 0 on W_n.
For Ψ_n = h̃ at the certificate instance, columns (1,3), y = Ḡ^α, z = y^{1/4}:
    M₁₃ numerator = −5(2720z⁴⁸ ln z − 260z⁴⁸ − 289z⁴⁰ − 3920z²⁸ ln z
                       − 140z²⁸ − 4760z²⁰ ln z − 240z²⁰ + 49),
    denominator (20z²⁸ + 17z²⁰ + 7)² > 0,
    **M₁₃(y=1) = 25/11 > 0** (exact — ln z vanishes at z=1; positive on a
    neighbourhood by continuity; numerically turns negative by y=2).
The very condition that would justify the lift fails already at the boundary.

**(c) Certified counterexample (re-derived independently; matches the sibling
audit).** A = [γ;p], γ = (7,9,2), p = (17/44, 5/11, 7/44) ∈ W₃ (exact);
T on columns (1,3), ω = 17/20 gives δ = (25/4, 9, 11/4), q = (31/88, 5/11,
17/88). With z = y^{1/4} > 1:
    d = h̃_A − h̃_B has numerator
      −5440z⁴⁵ + 6820z⁴² + 1581z³⁴ + 8500z²⁸ − 7840z²⁵ + 4913z²⁰
        − 3689z¹⁴ − 357,
    denominator 4(40z²⁵ + 31z¹⁴ + 17)(20z²⁸ + 17z²⁰ + 7) > 0 on z > 0.
    Sturm: exactly **1 root in z ∈ (1,∞)**, isolated in (1,2).
    Exact rational witnesses: num(1) = +4488 (d(1) = 51/176 > 0),
      num(5/4) = −753373969813394640678526829880437/19342813113834066795298816
      < 0.
So h̃_A > h̃_B on (1, ρ), ρ ≈ 2.4 — contradicting the claimed U ≤_hr V; the
hazard rates cross.

**Sweep counts** (sweep_bhb.py [2], exact dict-polynomial arithmetic,
n = 3, 4000 draws): V₃ half (claim h̃_A ≥ h̃_B on y ∈ (0,1)): **583/779
violating**; W₃ half (claim h̃_A ≤ h̃_B on y > 1): **541/773 violating**.

## Other checkable BKB claims — the deeper result

BKB2022's own theorems concern *ordinary* location-scale mixtures under
multivariate chain majorization on (params; p) — a keyword of the paper.
Two distinct situations:

- **Usual stochastic order**: F̄(t) = ΣpᵢF̄(t;μᵢ,σᵢ) IS separable in
  columns → Lemma 2.5 applies legitimately; those theorems are structurally
  sound.
- **Hazard / reversed-hazard rates**: h = ΣpᵢhᵢḠᵢ/ΣpᵢḠᵢ and
  r = Σpᵢfᵢ/ΣpᵢF̄ᵢ are ratios of sums — NOT separable. Any n≥3 claim proved
  via the lift has the same gap, and the conclusions are in fact false:

**Sweep (sweep_bhb.py [3]/[4], exact, ordinary exponential mixtures,
single T-transform on [λ;p], n = 3, 6000 draws each):**

| claim shape | <0 seen | >0 seen |
|---|---|---|
| rh, V₃ | 46/1172 | 1136/1172 |
| rh, W₃ | 417/1139 | 1103/1139 |
| hr, V₃ | 831/1159 | 359/1159 |
| hr, W₃ | 875/1098 | 459/1098 |

BOTH directions violated in BOTH classes — the rate functions cross; no
consistent ordering exists under the claim shape.

**Certified ordinary-mixture rh counterexample** (Sturm-verified):
λ = (5/3, 2, 16), p = (1/15, 2/5, 8/15) ∈ W₃ (comonotone); T on columns
(1,2), ω = 4/5 gives lB = (26/15, 29/15, 16), pB = (2/15, 1/3, 8/15).
In s = e^{−t} with s = u¹⁵ (u ∈ (0,1)):
    numerator of r_A − r_B is an integer polynomial of degree 270; Sturm
    isolation gives roots in (−1,0), (0,1/2), (1/2,1), plus a 25-fold root
    at u=0 and a 2-fold root at u=1 — i.e., **2 interior roots in (0,1)**;
    witnesses: diff(1/16) > 0, diff(1/4) > 0, diff(1/2) < 0, diff(3/4) < 0
    (a genuine sign change between u = 1/4 and u = 1/2, certified).
So r_A > r_B for large t and r_A < r_B for small t — the rates cross, and
any one-direction rh ordering claim on W₃ fails.

**Corroborating exposure in the same author cluster.** Shekari, Pakdaman,
Saadat Kia Barmalzan & Balakrishnan (J. Inequal. Appl. 2026:28, open access)
state the same n-component claim for distorted mixtures (their Thm 11, Cor 2,
Thm 12) with the explicit shortcut proof "columns k ≠ i,j are unchanged,
so the n = 2 theorem applies" — which is invalid for the same reason (the
frozen columns remain inside the ratio). Their Remark 11 identifies
**Theorem 2 of BKB2022** as the LS-model special case of their Thm 11 — i.e.,
BKB2022's own n ≥ 3 T-transform ordering theorems are very plausibly proved
by the same invalid lift and, per the table above, their natural claim shape
has exact counterexamples. This shifts the likely epicentre of the error
from SKF's application to the BKB/BHM lemma *usage pattern* itself: the
lemmas are fine; the field's habit of feeding ratio-of-sums rate functions
into the separable-sum lift is not. Caveat: without the BKB2022 full text
I cannot certify their exact theorem hypotheses; if their rh/hr theorems
carry extra side conditions (e.g., on the mixing weights alone), that mapping
needs revisiting — the st-order theorems are unaffected.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY audit_bhb.py    # symbolic lemma checks + counterexample certificates
    $PY sweep_bhb.py    # bounded sweeps, dict-polynomial exact arithmetic
