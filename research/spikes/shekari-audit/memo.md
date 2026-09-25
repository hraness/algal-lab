# Audit memo: Shekari–Pakdaman–Saadat Kia Barmalzan–Balakrishnan (2026)

Run dir (gitignored): `research/spikes/context/runs/shekari2026/`.
Sibling audits: `research/spikes/context/runs/bhb2022/memo.md` (the T-transform
lift lemmas) and `research/spikes/mixture-audit/memo.md` (SKF2026/SAF2022).

## The paper

**[SPBB2026]** M. Shekari, Z. Pakdaman, G. Saadat Kia Barmalzan,
N. Balakrishnan, *Stochastic comparisons of finite mixture models derived from
distorted distributions: results based on vector and multivariate chain
majorization approaches*, **Journal of Inequalities and Applications 2026,
article 28**. DOI: 10.1186/s13660-026-03450-7. Published 23 Feb 2026, open
access (CC BY-NC-ND). Retrieved 2026-09-25. Full text: `shekari2026.txt`
(SpringerLink HTML rendering; the PDF endpoint is bot-challenged).

**Model.** DSFM mixture: SF $\bar F_{P_n}(t)=\sum_i\pi_i D(\bar G(t);\gamma_i)$,
density $g(t)\sum_i\pi_i D'(\bar G;\gamma_i)$ where
$D'(u;\gamma)=\partial_u D(u;\gamma)$. Hazard rate (their eq. (3)):
$h_{P_n}(t) = g(t)\,\frac{\sum_i\pi_iD'(\bar G(t);\gamma_i)}
{\sum_i\pi_iD(\bar G(t);\gamma_i)}$ — a **ratio of n-term sums**.

**Classes.** $\mathcal A_n$: $2\times n$ matrices $(x;y)$, $x_i>0$,
$0<y_j<1$, $(x_i-x_j)(y_i-y_j)\le 0$ (antiordered); $\mathcal B_n$: $\ge0$
(comonotone). In the theorems the matrix is $[\gamma;\pi]$ ($\gamma$ top row).
**Lemma 7** = the $2\times2$ iff criterion for $\varphi(A)\le\varphi(B)$ under
$A\gg B$ on $\mathcal A_2/\mathcal B_2$, attributed to **Theorem 2 of
Balakrishnan, Haidari & Masoumifard (2015), IEEE Trans. Reliab. 64(1)** —
the same lemma BKB2022 restate as Lemmas 2.4/2.5 and SKF2026 misuse. The lemma
itself is TRUE (verified in the BHB memo).

## Claimed results (verbatim essentials)

- **Thm 1–4** (st order, vector majorization): $\gamma\succeq^p\gamma^*$ or
  $\gamma\succeq^{rm}\gamma^*$ with $(\gamma,\pi),(\gamma^*,\pi)\in\mathcal A_n$
  (or $\mathcal B_n$) ⇒ $M_n\ge_{st}N_n$ / $P_n\le_{st}Q_n$, provided
  $D(G;e^\eta)$ monotone+convex/concave in $\eta$. Proof: Schur-concavity of the
  *separable* sum $\Lambda_1(\gamma)=\sum_i\pi_iD(G;\gamma_i)$ — legitimate.
- **Thm 5** (n arbitrary, hr, $\pi\succeq^m\pi^*$, $\gamma$ common): claims
  Schur-concavity of $J_1(\pi)=h_{P_n}(t)$ — direct differential argument, no
  T-lift — provided $D$ and $-D'$ both decreasing/increasing in $\gamma$.
- **Cor 1** (same, $\gamma\succeq^m\gamma^*$).
- **Thm 6–7** (rh analogs for DDFM).
- **Thm 8** (n=2, hr): $[\gamma;\pi]\gg[\gamma^*;\pi^*]$, both $\in\mathcal A_2$
  ⇒ (i) $P_2\ge_{hr}Q_2$ if $D(\bar G;\gamma)$ and $-D'(\bar G;\gamma)$ both
  *decreasing and convex* in $\gamma$; (ii) $P_2\le_{hr}Q_2$ if both
  *increasing and concave*. Proof via Lemma 7 — correct use (n=2, no frozen
  columns).
- **Thm 9** (n=2, rh, DDFM). **Thm 10** (n=2, disp: Thm 8(ii) + DHR +
  Bartoszewicz).
- **Thm 11** (n arbitrary, hr, single T): $[\gamma^*;\pi^*]=[\gamma;\pi]
  T^{i,j}_\omega$, both in $\mathcal A_n$ ⇒ (i) $P_n\ge_{hr}Q_n$ /
  (ii) $P_n\le_{hr}Q_n$ under the same D-conditions.
- **Cor 2** (n, product of same-structure T's). **Thm 12** (n, different-
  structure T-chain, all intermediates $\in\mathcal A_n$).
- **Cor 3** (n, st, row majorization under "conditions of Part (ii) of Cor 2").
- Remark 11: Thm 11 claimed to recover **BKB2022 Thm 2** (LS model, identity
  distortion), HF2018 Thms 3.6/3.10 (AL/PHR models), Guo–Yan Thms 2/4 (MPHR).

## Finding 1 — the invalid lift, verbatim

Thm 11 proof (`shekari2026.txt` l.1170–1174):

> "We observe that $P_n$ and $Q_n$ have the same distribution and same hazard
> rate function (i.e., $\pi_k=\pi_k^*$ and $\gamma_k=\gamma_k^*$) for all
> $k\neq i,j$ as the T-transform matrix $T^{i,j}_\omega=\omega I_n+(1-\omega)
> \Pi^{i,j}$ … Therefore, applying Theorem 8, the desired result follows
> immediately."

Identical gap to SKF2026 Thm 3.8 / BKB2022 Thm 2: the $n-2$ frozen components
stay inside both sums of the ratio $h_{P_n}=g\,L_1/L_2$; the sign of the
n-component hazard difference is not controlled by the 2-component comparison.
Thm 12 chains single-T steps through intermediates ("which gives
$R^{(k-1)}_n\le_{st}Q_n$" — their eq. line also has an st/hr typo) each via
Thm 11/Cor 2, so it inherits the gap; Cor 2 is a same-structure chain, same
step.

## Finding 2 — the γ-conditions are unsatisfiable on the whole support

Every hr/rh claim (Thms 5, Cor 1, 6–12, Cor 2, and Cor 3 via "Part (ii) of
Cor 2") requires $-D'(u;\gamma)=-\partial_uD$ to be monotone in $\gamma$ at
**every** $u=\bar G(t)\in(0,1)$. But $\int_0^1 D'(u;\gamma)\,du
=D(1;\gamma)-D(0;\gamma)=1$ for all $\gamma$: two distinct densities on $(0,1)$
cannot be pointwise ordered, so $-D'$ is monotone in $\gamma$ for all $u$ only
if $D$ is $\gamma$-free ($D=u$). Exact verification (`audit_shekari.py` [A]):

- **PHR** $D=u^\gamma$: $\partial_\gamma(-D')=-u^{\gamma-1}(1+\gamma\ln u)$;
  decreasing iff $\gamma|\ln u|\le1$ — fails for $u<e^{-1/\gamma}$; takes both
  signs in $\gamma$ at $u=1/2$ and is positive throughout at $u=e^{-3}$.
- **The paper's own Example 1(i)** $D=\theta u^\gamma/(1-(1-\theta)u^\gamma)$,
  $\theta=3/5$: claimed "−D′ decreasing and convex in $0<\gamma<1$". At
  $u=e^{-2}$ (i.e. $x\approx3.5$, inside their plotted range),
  $\partial_\gamma(-D')$ = −0.2495 at $\gamma=0.3$ but +0.4458, +0.7738 at
  $\gamma=0.4,0.5$ — non-monotone on the instance's own γ-range. **The
  example's hypothesis check is wrong**; at $u=e^{-3}$ the sign is positive
  throughout (−D′ *increasing* — opposite of claimed).

So as stated, the antecedents of Thms 8–12/11/12/Cor 2–3 hold only for the
trivial distortion; every conclusion is conditional on an empty hypothesis
class. Under that strict reading no counterexample exists (vacuous truth) —
but see Finding 4 for why the operative content still fails.

## Finding 3 — sweep: the claimed ordering fails on admissible instances

Under the PHR specialization $D(u;\gamma)=u^\gamma$ (the flagship family;
Remark 11(II) claims it recovers HF2018 Thm 3.10),
$h_{P_n}(t)=h_{\bar G}(t)\cdot\tilde h_{\pi,\gamma}(u)$, $u=\bar G(t)$, with
$\tilde h_{\pi,\gamma}(u)=\sum\pi_i\gamma_iu^{\gamma_i}/\sum\pi_iu^{\gamma_i}$
— the identical non-separable ratio as in the SKF audit. Part (i) claim:
$\tilde h_A\le\tilde h_B$ on $(0,1)$.

`sweep_int.py` (exact Fraction arithmetic, $u=v^L$ parametrization, 20000
draws, single T-transform, both matrices verified in $\mathcal A_n$):

| class | admissible | violating part-(i) claim | violating part-(ii) |
|---|---|---|---|
| $n=2$ (Thm 8 analog) | 6133 | **0** | 6133 (sign always −; part-(ii) conditions don't apply to PHR anyway) |
| $n=3$ | 5008 | **1725 (34%)** | 4221 |
| $n=4$ | 4106 | **2109 (51%)** | 3069 |

The $n=2$ cleanliness is the control: the base theorem works; the lift to
$n\ge3$ is what fails. Thm 5 spot-check (π-majorization version, PHR, n=3):
**2450/15704 admissible violated** — the vector-majorization hr claim fails
too (same vacuous −D′ condition; its Schur-sign step is only locally valid).

## Finding 4 — certified counterexample (Thm 11(i), PHR)

`certify_thm11.py`, all hypotheses verified exactly:

$$A=[\gamma;\pi]=\begin{pmatrix}2&4&3\\7/12&1/12&1/3\end{pmatrix}\in\mathcal A_3,
\quad B=A\,T^{2,3}_{3/10}=
\begin{pmatrix}2&33/10&37/10\\7/12&31/120&19/120\end{pmatrix}\in\mathcal A_3.$$

In $z=u^{1/10}$ the difference $d=\tilde h_A-\tilde h_B$ is rational,
numerator degree 37, denominator with no root in $(0,1)$:

- **Sturm: numerator has exactly 2 roots in $z\in(0,1)$** — a genuine sign
  change, not a grid artifact.
- Exact witnesses: $d(1/2)=+\frac{108762382147}{224621531888650}>0$;
  $d(15/16)=-\frac{3806332781036595055593927248477537911494140625}
  {120047874401815205058723168369647882297774115826}<0$.

So $\tilde h_A>\tilde h_B$ on most of $(0,1)$ and crosses below near $u=1$:
**$P_3\ge_{hr}Q_3$ fails**, contradicting Thm 11(i). The same instance refutes
Cor 2 (one-factor same-structure chain) and embeds in Thm 12 ($k=2$ with
$T_2$=identity $\omega=1$, intermediates stay in $\mathcal A_3$).

Caveat recorded honestly: since the −D′ condition cannot hold on all of
$(0,1)$, no *fully* admissible instance exists; violations concentrate where
the condition fails (`sweep_targeted.py`: 0/24599 violations were witnessed at
grid points inside the region $u\ge e^{-1/\gamma_{\max}}$ where the PHR
γ-conditions hold — grid reaches $z=31/32$, $u=z^L$; treat as
suggestive, not exhaustive).

## Finding 5 — the LS specialization (Remark 11(I)(i)) fails too

If Remark 11 is right that Thm 11 recovers BKB2022 Thm 2 for LS components,
ordinary exponential-scale mixtures must obey the ordering. They don't
(`sweep_ls.py`, `certify_ls.py`): $\gamma=(1/7,1/2,1/2)$,
$\pi=(1/3,1/3,1/3)\in\mathcal A_3$, single T on columns (1,3), $\omega=3/20$,
$\gamma^*=(25/56,1/2,11/56)$; rates $\lambda=1/\gamma=(7,2,2)$,
$\lambda^*=(56/25,2,56/11)$. In $z=s^{1/275}$ ($s=e^{-t}$), numerator degree
3325, denominator all-positive-coefficients:
$d(z)<0$ at $z=999/1000$ ($s\approx0.76$) and $d(z)>0$ at $z=1999/2000$
($s\approx0.87$) — an exact rational-witness sign change; the hazard rates
cross. (Full Sturm count on the degree-3325 numerator was not run in-budget;
the two exact opposite-sign evaluations plus denominator positivity already
certify a root.) 9/382 admissible LS instances violate — consistent with the
BHB memo's conclusion that BKB2022's Thm-2-type claims are false for $n\ge3$.

## Classification

| Claim | Status | Evidence |
|---|---|---|
| Lemma 7 (= BHM2015 Thm 2) | true (external) | BHB memo verification |
| Thm 1–4 (st, vector majorization) | not checked | separable-sum Schur arguments; different mechanism |
| Thm 5, Cor 1, Thm 6, 7 (hr/rh vector maj.) | vacuous hypotheses; effective content fails | unsatisfiable $-D'$ monotonicity (Finding 2); Thm 5(i): 2450/15704 PHR violations |
| Thm 8, 9, 10 ($n=2$, hr/rh/disp) | holds-on-samples, vacuous hypotheses | 0/6133 PHR violations; $-D'$ condition never globally satisfiable; Example 1 hypothesis check shown false |
| **Thm 11 (n, single T)** | **vacuous as stated; EXACT COUNTEREXAMPLE to its effective content; proof invalid** | frozen-column lift quoted; certified PHR sign change; 1725/5008 (n=3), 2109/4106 (n=4) violations |
| Cor 2 (same-structure chain) | fails with Thm 11 | one-factor chains are single T's |
| Thm 12 (different-structure chain) | fails with Thm 11 | each step invokes Thm 11 |
| Cor 3 (st row-maj under Cor-2(ii) conds) | not resolved | sampler too thin (1 admissible/40k); conditions inherit vacuity |
| Example 1 hypothesis verification | **false as stated** | $-D'$ non-monotone on [0.3,0.5] at $u=e^{-2}$ (exact) |

## Verdict

The paper's headline n-component results (Thm 11, Cor 2, Thm 12, and Cor 3 via
them) **fall the same way as SKF2026/BKB2022**: the lift of the $n=2$ theorem
to arbitrary $n$ via "unchanged columns" is invalid for a ratio of sums, and
the claimed ordering fails on a large fraction of structurally admissible
instances (certified sign changes). This paper adds a second, independent
defect: the γ-monotonicity hypotheses on $-D'$ are unsatisfiable for any
nontrivial distortion family ($\int_0^1D'\,du=1$), making the theorems
vacuous as literally stated and their own Example 1 mis-verified. The $n=2$
base theorems (8–10) and the separable-sum st theorems (1–4) are unaffected
by the lift issue; the former hold on samples, the latter not audited
(different mechanism). Net: same failure mode, certified — the n≥3 chain-
majorization ordering claims for distorted mixtures do not hold.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY audit_shekari.py A     # gamma-condition viability + Example-1 check
    $PY sweep_int.py 20000     # Thm 11 PHR sweep (n=2,3,4)
    $PY sweep_targeted.py 30000  # in-condition-region probe
    $PY certify_thm11.py       # Sturm certificate, Thm 11(i)
    $PY sweep_ls.py 30000      # LS specialization sweep
    $PY certify_ls.py          # LS sign-change witnesses
    $PY sweep_cor3.py          # Cor 3 + Thm 5 sweeps

Files: `audit_shekari.py`, `sweep_int.py`, `sweep_targeted.py`,
`certify_thm11.py`, `sweep_ls.py`, `certify_ls.py`, `sweep_cor3.py`,
`shekari2026.txt` (full text).
