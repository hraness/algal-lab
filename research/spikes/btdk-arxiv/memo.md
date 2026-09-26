# Audit: BTDK arXiv:2412.10071 — multiple-outlier location-scale mixtures

Run dir: `research/spikes/context/runs/btdk-arxiv/` (gitignored).
Exact arithmetic: `.venv-math/bin/python` (sympy 1.14, mpmath 1.3).
Script: `audit_btdk.py`. PDF + TeX source in `./paper.pdf`, `./src/`.
Audited against the printed v1 PDF (26 pp, math.ST, submitted 13 Dec 2024).

## Citation

R. Bhakta, N. Torrado, S. Das, S. Kayal, "Ordering results between two
finite arithmetic mixture models with multiple-outlier location-scale
distributed components", **arXiv:2412.10071v1** (2024). No journal-ref
recorded on the arXiv page as of audit date. Kayal (NIT Rourkela) node of
the citation cone; cites `barmalzan2022orderings` (BKB2022) as motivation.

## Headline verdict

**Not a carrier of the certified T-transform-lift defect.** The model is a
*two-group* multiple-outlier location-scale mixture (n1 components ~
LS(F,σ1,λ1), n2 ~ LS(F,σ2,λ2)). There is no n-column parameter matrix, no
chain majorization, and no n=2 reduction anywhere in the paper. The hr/rh/lr
theorems compare *component counts* (n1,n2) vs (n1*,n2*) under the
cross-product condition Δ := n1n2* − n1*n2 ≥ 0 and are argued by **direct
cross-multiplication** of the two-group ratio of sums. The only
majorization lemma used (Lemma 2.1, Haidari et al. 2019 Thm 1(i)) is applied
in Thm 4.1 to the survival function — an *additive* functional, the
legitimate class.

**But the paper is defective by other mechanisms** — three theorems fail
outright on certified instances, two more are vacuous where stated:

| Printed | Claim | Status | Mechanism |
|---|---|---|---|
| Thm 4.1 | st-order, weak majorization of tied scale vectors | **vacuous + reversed direction** | hypothesis "F is IPRFR" is unsatisfiable on unbounded support; Lemma 2.1(i) pairs ≼_w with the wrong conclusion direction (fails n=1 check); n-vector hypothesis vs 2-vector derivative check mismatch when n1≠n2 |
| Cex 4.1/4.2 | st fails when σ-vectors differ | consistent (negative results) | — |
| Thm 4.2 | st-order, different counts, D_2+/E_2+ | **FALSE (certified)** | middle region σ2<x≤σ1 forces the opposite order whenever n2*>n2 — admissible under stated hypotheses |
| Thm 4.3 | hr-order, different counts | **D-case VALID; E-case FALSE (certified)** | E middle region requires Δ≤0, opposite of hypothesis; Pareto baseline (DPFR, support (1,∞)) certified |
| Thm 4.4 | rh-order, different counts | **D-case VALID; E-case vacuous** | IRFR unsatisfiable on unbounded support (r̃ nondec ⇒ ∫r̃=∞ ⇒ F≡0) |
| Thm 4.5 | lr-order, different counts | **D-case FALSE (certified); E-case same gap** | proof multiplies 1/(x−σ1)≥1/(x−σ2) by t1f′/f(t1)≥t2f′/f(t2) where tf′/f is **sign-indefinite** — invalid; counterexample certified in Q(√) |
| Thm 4.6 + Cor 4.1, 4.7, 4.8 | star / Lorenz / dispersive / right-spread | not fully audited; 4.6 argument reviewed informally and looks structurally sound (A·B sign-separated decomposition, not a product of two positive-side inequalities); 4.7 proof omitted entirely | different machinery (Saunders/Kochar one-parameter lemmas; no T-lift) |

## Certificates (exact)

All in `audit_btdk.py`; exact Fraction/sympy-algebraic arithmetic.

**Thm 4.2 (st), D-case** — symbolic identity on σ2<x≤σ1:
`Sf_{U*} − Sf_U = (n2*−n2)·r2·(Sf(t2)−1)`, so claimed `U_n ≤_st U_{n*}`
requires `n2* ≤ n2`. Admissible counterexample `n=(3,1)`, `n*=(1,4)`,
`r=(3/11,2/11)` (D_2+: r1≥r2 ✓, balance n1r1+n2r2=1=n1*r1+n2*r2 ✓,
n=4≤5=n*), σ=(2,1), λ=(2,1), Lomax Sf=(1+t)^{−2}:
at x=3/2, `Sf_U = 89/99 > 59/99 = Sf_{U*}` — **strict opposite order on the
whole middle region**. For D + strict n<n*, admissibility forces either
(n1*>n1, n2*<n2) [claim holds] or (n1*<n1, n2*>n2) [claim fails] — failure
is systematic, not sporadic. The n≥n* branch fails symmetrically.

**Thm 4.3 (hr)** — symbolic cross-multiplication verified:
`h_U − h_{U*} = Δ·r1r2·(f1S̄2/λ1 − f2S̄1/λ2)/(λ1λ2)` on x>σ1, and numerator
`−r1·Δ` on the D middle region — the D-case proof is **correct** (both
factors positive; (1/λ1)h(t1) ≤ (1/λ2)h(t2) under IFR since t1≤t2, λ1≥λ2).
E-case: middle region σ1<x≤σ2 has only group 1; `h_U − h_{U*}` numerator is
`+r2·Δ` — opposite of what `U_n ≥_hr` needs. Certified with Pareto
Sf(t)=t^{−2} on (1,∞) (t·h ≡ 2, DPFR boundary, unbounded support admissible
under Set-up 4.1): σ=(1,2), λ=(1,2), n=(3,2), n*=(2,3), r=(1/5,1/5), Δ=5:
at x=3, `h_U = 3/11 > 1/7 = h_{U*}` (violation); at x=6, `h_U=149/310 <
407/830 = h_{U*}` — the rate order flips across regions. NB: DPFR is
unsatisfiable on support exactly (0,∞) (t·h noninc ⇒ h≥c/t near 0 ⇒
F̄≡0), so the E-case lives entirely on left-endpoint>0 baselines.

**Thm 4.4 (rh)** — same symbolic reduction verified; D middle region gives
*equality* of r̃ and x>σ1 reduces to `(1/λ1)r̃(t1) ≥ (1/λ2)r̃(t2)`, valid via
the product of **positive** monotone factors (t·r̃ ≥ 0 always — this is the
structural reason hr/rh survive where lr fails). D-case **correct**.
E-case hypothesis IRFR (r̃ nondecreasing) is unsatisfiable on any unbounded
support: r̃(t0)>0 ⇒ ∫_{t0}^T r̃ ≥ c(T−t0) ⇒ F(T) → ∞ — vacuous.

**Thm 4.5 (lr), D-case** — IPLR baseline `f(t) ∝ t^{−1/2}(1+t)^{−1}`
(−tf′/f = 1/2 + t/(1+t) increasing ✓, unbounded support ✓).
σ=(2,1), λ=(2,1), n=(3,2), n*=(2,3), r=(1/5,1/5), Δ=5:
φ′ sign `(1/λ2)(f′/f)(t2) − (1/λ1)(f′/f)(t1)` is **positive** at all 59/59
grid points x ∈ (2,5) (e.g., 800/41 at x=81/40) ⇒ density ratio
R(x)=f_U/f_{U*} strictly decreasing there. Exact algebraic certificate:
`R(81/40) = (486 − 5√82)/319 ≈ 1.3816 > R(4) = 4 − 5√3/3 ≈ 1.1132`,
`a<b` but `R(a)>R(b)` ⇒ **U_n ≥_lr U_{n*} fails**. The E-case (DPLR) shares
the same invalid product-of-inequalities step (sign-indefinite tf′/f);
a certified E-instance needs a DPLR baseline on (a,∞) (e.g.
t^{−2}/ln t on (e,∞)) and interval-arithmetic sign bounds — gap noted,
not separately certified in this budget.

**Thm 4.1** — vacuity certified analytically: IPRFR (t·r̃ nondecreasing)
⇒ for t≥t0, r̃(t) ≥ t0 r̃(t0)/t ⇒ F(T)/F(t0) = exp(∫r̃) ≥ (T/t0)^c → ∞,
contradicting F≤1 — **no IPRFR distribution on unbounded support exists**;
Thm 4.1 (both parts) is vacuous under Set-up 4.1. Direction check with the
hypothesis relaxed: `λ=(2,1) ≼_w θ=(2,3/2)` on D_2+ (n1=n2=1, so n-vector
and 2-vector readings coincide) gives `S̄_U(3)=5/18 < 277/882=S̄_V(3)`, i.e.
`U <_st V` — opposite of the claimed `≥_st`: the printed Lemma 2.1(i)
(`≼_w` ⇒ φ(u)≥φ(v) for nonneg-increasing partials) is wrong already at n=1
(the consistent pairing is `≼^w`↔≥ or `≼_w`↔≤); part (ii) uses `≼^w` and
has the correct direction. Also flagged: hypothesis is stated on the tied
n-vectors but the proof checks only the 2-dimensional derivative condition;
for n1≠n2 the n-vector `≼_w` (λ1≤θ1 ∧ n1λ1+n2λ2≤n1θ1+n2θ2) is a different
relation than the 2-vector one.

## Relation to the cluster memo

This is the first audited suspect where the headline mechanism is **absent
and the counterexample set is different in kind**: no Φ(A)=Σψ(a1i,a2i)
reduction, no frozen columns inside a ratio of sums. Its defects are
(1) vacuous proportional-ageing hypotheses on unbounded support (IPRFR,
IRFR; DPFR only satisfiable off-0), (2) systematic middle-region direction
errors in the count-comparison theorems (the "it is easy to check" steps),
(3) a sign-indefinite product of monotone factors in the lr proof, and
(4) a misprinted/mispaired weak-majorization lemma. Notably **Thm 4.2 fails
at st-order** — the order class that was clean across the whole T-lift
cluster — because the defect here is upstream of any lifting question.

Status against `cluster-audit/memo.md` suspect queue: **audited — defective,
different mechanism family** (not the T-transform lift). The "inspired by
BKB2022" citation is motivational only; no BKB Lemma 2.4/2.5 invocation.

## Files

- `abs.html`, `paper.pdf`, `paper.txt`, `src/` (arXiv source)
- `audit_btdk.py` — all certificates above (runtime < 60 s)
