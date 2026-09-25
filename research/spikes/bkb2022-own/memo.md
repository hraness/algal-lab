# Audit memo: BKB2022's OWN theorems (Barmalzan–Kosari–Balakrishnan)

Run dir (gitignored): `research/spikes/context/runs/bhb2022-own/`.
Siblings: `runs/bhb2022/memo.md` (Lemma 2.4/2.5 verification — both TRUE),
`runs/shekari2026/memo.md` (same-author-cluster descendant, Thm 11 = lift of
the invalid step), `research/spikes/mixture-audit/memo.md` (SKF2026/SAF2022).

Exact arithmetic: `/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python`
(sympy Rational/Poly/Sturm; mpmath.iv outward-rounded interval certification).

## 1. What BKB2022 literally claims — sourcing status

**[BKB2022]** G. Barmalzan, S. Kosari, N. Balakrishnan, *Orderings of finite
mixture models with location-scale distributed components*, Probab. Eng. Inf.
Sci. **36**(2), 461–481 (2022), DOI 10.1017/S0269964820000467.

**No open copy exists.** Confirmed via OpenAlex (`is_oa:false`,
`has_fulltext:false`), Unpaywall (`oa_status:"closed"`, no repository copy),
Semantic Scholar (`openAccessPdf` empty), zbMATH record 7621890 (metadata only;
review text license-blocked), McMaster Experts (abstract only). No sci-hub or
pirate source was used or needed.

**Obtained verbatim (abstract, via Semantic Scholar API / McMaster /
Cambridge listing):**

> "In this paper, we consider finite mixture models with components having
> distributions from the location-scale family. We then discuss the usual
> stochastic order and the reversed hazard rate order of such finite mixture
> models under some majorization conditions on location, scale and mixing
> probabilities as model parameters."

Keywords: *multivariate chain majorization order, reversed hazard rate order,
usual stochastic order*. Note: the abstract names **st + rh only** (no hr).

**Reconstructed (not read) theorem map** — from two corroborating open-access
sources in the same author cluster:

- **Shekari–Pakdaman–Saadat Kia Barmalzan–Balakrishnan 2026** (J. Inequal.
  Appl. 2026:28, OA, local `shekari2026.txt`), whose distortion-family
  theorems recover BKB's as special cases, with explicit mappings:
  - Rem 9:  their **Thm 9** (n=2, rh, DDFM, `[γ;π]≫[γ*;π*]` on antiordered
    `A_2`) specialized to identity distortion + LS components **yields
    BKB2022 Thm 1** (and Bhakta-Kayal-Finkelstein Thm 8). So BKB Thm 1 is a
    **n=2 reversed-hazard ordering under 2×2 chain majorization**.
  - Rem 8:  their **Thm 8** (n=2, hr, DSFM) similarly yields **BKB2022
    Thm 5** — the n=2 rate-ordering companion (rh on the CDF side, since BKB
    covers rh not hr).
  - Rem 11: their **Thm 11** (arbitrary n, single T-transform
    `[γ*;π*]=[γ;π]T^{ij}_ω`, both in `A_n`, rate ordering) yields
    **BKB2022 Thm 2** — the flagship n≥3 claim.
- **Bhakta–Kayal–Finkelstein 2024** (MCAP 26(4):52, *Final Published Version*
  PDF legitimately downloaded from Strathprints record 91121 — saved as
  `bkf2024.pdf`/`bkf2024.txt`): the sibling LS-mixture paper whose Thms
  11/12/13 are the same T-transform ladder for the **st order** (n=2 single
  T, n-arbitrary single T, different-structure T-chain) — valid there because
  the SF `Σp_iF̄((x−σ)/λ_i)` is a *separable* column sum.

So the most charitable reconstruction of BKB2022's theorem suite:

| BKB (recon.) | shape | class | mechanism |
|---|---|---|---|
| Thm 1 | n=2, rh ordering, `[row;p]≫[row*;p*]` | antiordered `V_2` | Lemma 2.4 (2×2 iff) |
| Thm 2 | n arbitrary, rate ordering (rh per abstract; hr per Shekari's literal map), `[row*;p*]=[row;p]T^{ij}_ω` | `V_n`/`W_n` | "unchanged columns ⇒ n=2 applies" (invalid for ratios) |
| Thm 5 | n=2 rate ordering, chain majorization | `V_2`/`W_2` | Lemma 2.4 |
| st theorems | n arbitrary, T-transforms / vector majorization on `[λ;p]` or `[μ;p]` | — | separable sum — lift is VALID |

Plus corollaries chaining T-transforms (same-structure products collapse to a
single T; different-structure chains need intermediates in the class).

## 2. What is checkable vs assumed

- Lemmas 2.4/2.5: already verified TRUE (bhb2022 memo); the error is the
  *usage pattern*: feeding a **ratio of sums** into a lift proved only for
  **separable sums** (or equivalently "frozen columns" reasoning — the n−2
  untouched components stay inside numerator and denominator).
- The claim shape audited here: for ordinary LS mixtures with scale row
  `λ` (rates `ν_i=1/λ_i`), weights `p`, exponential baseline
  `F̄=e^{−t}` (s=e^{−t}∈(0,1)):
  `rh: r(s)=Σp_iν_i s^{ν_i}/(1−Σp_i s^{ν_i})`,
  `hr: h(s)=Σp_iν_i s^{ν_i}/Σp_i s^{ν_i}`.
  A single T-transform on one column pair of the 2×n matrix; both A and B
  required in the same class (V_n antiordered or W_n comonotone).
- **Convention S (paper-faithful):** parameter row = scales λ; T applied to
  λ, rates inverted afterwards. **Convention R:** parameter row = rates ν
  (BKB may parametrize either way; both conventions tested).
- Assumed but unverifiable: the exact baseline side-conditions BKB attach to
  their rate theorems, and the claimed direction (both refuted anyway by
  crossings), and whether the row is location or scale (see caveat §5).

## 3. Certified counterexamples (all exact)

n=3, exponential baseline, **integer rates** (tiny polynomials, full Sturm):

| case | order | class | A (ν;p) | B=AT_{1/2} | numerator | Sturm roots in (0,1) | witnesses (exact) |
|---|---|---|---|---|---|---|---|
| C1i | rh | V_3 | (1,15,3); (33/40,1/20,1/8) | (2,15,2); (19/40,1/20,19/40) | deg 18 | **3** | num(7/8)<0, num(1/16)>0 |
| C2i | rh | W_3 | (10,16,2); (9/40,27/40,1/10) | (13,13,2); (9/20,9/20,1/10) | deg 29 | **3** | num(11/16)<0, num(1/16)>0 |
| C3i | hr | V_3 | (13,15,11); (3/20,1/20,4/5) | (14,14,11); (1/10,1/10,4/5) | deg 29 | **2** | num(5/8)<0, num(1/16)>0 |
| C4i | hr | W_3 | (9,1,12); (17/40,1/20,21/40) | (5,5,12); (19/80,19/80,21/40) | deg 21 | **2** | num(1/16)<0, num(3/4)>0 |

(`certify_int.py` / `certify_int_out.txt`.) Every instance crosses — **both
directions of the claimed ordering fail**. Denominator positivity on (0,1) is
analytic (hr: positive sum; rh: `1−Σp_i s^{ν_i}>0` since `Σp_i=1`, `s^{ν}<1`).

n=3, exponential baseline, **scale row** `[λ;p]` (BKB/BKF convention), T on
scales, rates `ν=1/λ` — certified by outward-rounded interval evaluation
(`certify_iv.py` / `certify_iv_out.txt`):

| case | order | class | λ; p | λB; pB (ω) | certified crossing |
|---|---|---|---|---|---|
| C3 | rh | V_3 | (4/13,6/7,5/23); (13/40,9/40,9/20) | (141/182,71/182,5/23); (6/25,31/100,9/20) (ω=3/20) | d(15/128)∈[−1.569e−4]<0, d(2/128)∈[+5.91e−4]>0 |
| C4 | rh | W_3 | (1/10,1/4,4/15); (9/40,1/4,21/40) | (61/400,79/400,4/15); (187/800,193/800,21/40) (ω=13/20) | d(78/128)<0, d(2/128)>0 |
| C5 | hr | V_3 | (4,1/10,3/4); (3/40,1/2,17/40) | (73/80,1/10,307/80); (163/400,1/2,37/400) (ω=1/20) | d(2/128)<0, d(12/128)>0 |
| C6 | hr | W_3 | (5/6,1/2,2); (9/40,7/40,3/5) | (3/5,11/15,2); (19/100,21/100,3/5) (ω=3/10) | d(11/128)<0, d(2/128)>0 |

All four cross inside (0,1); memberships in V_3/W_3 verified exactly on the
scale rows.

**n=2 base cases also fail for the unconditional claim shape** (certified;
the 2×2 machinery is iff, so these instances simply fail its condition (ii)):

- rh, V_2→V_2: ν=(12/5,1/2), p=(1/4,3/4), ω=1/2 → νB=(29/20,29/20),
  pB=(1/2,1/2); L=20, deg-77 numerator, **Sturm: 3 roots in (0,1)**;
  exact witnesses num(63/64)<0, num(1/32)>0 (`certify_n2_out.txt`).
- rh, W_2→W_2: ν=(23,3/2), p=(5/8,3/8), ω=1/4 → νB=(55/8,141/8),
  pB=(7/16,9/16); interval-certified crossing d(96/128)<0, d(2/128)>0.

Baseline-side-condition caveat: if BKB's Thms 1/5 attach a hypothesis that
excludes the exponential baseline (e.g. on `f` or `t²f`), the n=2 instances
may lie outside the theorem's scope — the n≥3 failure is robust regardless
(the lift is invalid for *any* baseline).

Also from `scan_out.txt` (float scan, `search_bkb.py`): massive violation
rates under both conventions at n=2 **and** n=3, e.g. conv-S n=3:
rh V_3 crossing 657/861 admissible, rh W_3 676/965, hr V_3 813/885,
hr W_3 593/898; n=2 rates similar (V_2 rh 1993/3142 conv-S).

**st-order control** (`st_control_out.txt`): SF difference sign changes at
462/626 in W_3 (0/590 in V_3) — i.e., the *unconditional* st claim fails for
exponential baseline too. The separable lift is valid, so this only means
BKB's st theorems need their side conditions (BKF-style `t²f increasing`,
`tf decreasing`, etc.); those are structurally sound claims, not lift victims.

## 4. Verdict per theorem (fidelity-caveat flagged)

| BKB claim (recon.) | certified status | confidence in statement |
|---|---|---|
| Lemmas 2.4/2.5 | TRUE (prior audit, verbatim via SKF2026) | verbatim |
| st-order theorems | mechanism VALID (separable sums); conclusions need their (unknown) side conditions — not refuted here | medium: direction/conditions unreconstructed |
| **Thm 2 — n≥3 rate ordering under single T** | **FALSE for the natural claim shape: certified crossings in rh and hr, both classes, both parametrization conventions; expected proof step (frozen-column / separable lift) is invalid** | high on shape (Shekari Rem 11 pins it), medium on which order (rh per abstract; hr in Shekari's map) |
| Thms 1/5 — n=2 rate orderings | unconditional shape FAILS already at n=2 (certified, exp baseline); may be rescued by baseline side conditions I could not read | medium-high on shape; low on side conditions |
| corollaries/chains | inherit Thm 2's failure | medium |

**Headline:** the same invalid lift that sank SKF2026 Thm 3.8 and Shekari
Thm 11 is, by Shekari's own Remark 11, **the BKB2022 Thm 2 content** — and the
natural claim is certified false at n=3 (and at n=2 without side conditions).
The most defensible formulation: *for ordinary LS mixtures, neither
X ≤_rh Y nor X ≥_rh Y (nor either hr direction) follows from a single
T-transform on [scale;p] within V_n or W_n — the rates cross.*

## 5. Residual gaps (honest accounting)

- Verbatim hypotheses not obtained (paywalled). If BKB Thm 2 restricts to
  specific baselines satisfying a side condition, my exp/IE certificates need
  a matching baseline; the hr-form certificates double as **inverted-
  exponential-baseline rh** certificates (`t²r(t)=Σp_iλ_i s^{λ_i}/Σp_i
  s^{λ_i}`, s=e^{−1/t}, t²f increasing — BKF's own flagship condition), so
  two distinct baseline-condition families are already covered.
- Location-row `[μ;p]` T-theorems (if BKB has them): not separately
  certified — the mixture is piecewise in t over the ordered locations; same
  non-separable-ratio obstruction applies but a dedicated certificate would
  need region-by-region analysis.
- Whether BKB's claim direction or class pairing differs (e.g. theorem only
  for W_n): moot — certified crossings exist in both classes.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY search_int.py      # integer-rate admissible-instance search
    $PY certify_int.py     # Sturm-certified n=3 counterexamples (V_3,W_3; rh,hr)
    $PY certify_iv.py      # interval-certified scale-row counterexamples
    $PY search_bkb.py 6000 # float scan, both conventions, n=2,3
    $PY certify_n2.py      # n=2 probes (V_2 Sturm cert; W_2 Sturm slow -> see
                           #   interval cert in certify_iv_out.txt tail)

Files: `bkf2024.pdf/.txt` (Strathprints OA published version of the sibling
paper), `bhkkb2025.txt` (arXiv 2511.00791, Barmalzan's own follow-up citing
BKB2022), `scan_out.txt`, `search_int_out.txt`, `certify_int_out.txt`,
`certify_iv_out.txt`, `certify_n2_out.txt`, `st_control_out.txt`.
