# Shape sweep: dispersive (SB2022) + star/Lorenz (PKP2022) claim shapes

Run dir: `research/spikes/context/runs/shape-sweep/` (gitignored). Compiled
26 September 2026. Exact arithmetic: `.venv-math` (sympy 1.14 Rational/Sturm
+ mpmath 1.3 rigorous interval arithmetic). Nothing committed.

**Verdict: all three remaining open shapes REFUTED at claim shape.**
CERT G (dispersive order), CERT H (star order), CERT I (Lorenz order) below.

## Method (new machinery: certified quantile intervals)

Ordinary exp-mixture Fbar(t) = sum p_i e^{-lam_i t}. Common rate denominator
D, k_i = D*lam_i integers, s = e^{-t/D} in (0,1):

- SF: V(s) = sum p_i s^{k_i} — exact rational at rational s.
- u-quantile: V(s*) = 1-u; bisection in s gives a **certified rational
  interval** [lo,hi] (V increasing; endpoint signs are exact rational
  comparisons). 40–56 iters → width ≤ 2^-40.
- Density at quantile: f(t*) = (1/D)A(s*), A(s)=sum p_i k_i s^{k_i}
  increasing in s → f(t*) in [A(lo)/D, A(hi)/D], **exact rationals**.
  Dispersive-order checks need no transcendentals at all.
- t* = D(-ln s*): rigorous mpmath.iv enclosures of ln at the certified
  endpoints → rigorous intervals for star-order ratios and Lorenz ordinates.

Machinery sanity-checked against closed forms: Exp(2) at u=1/3 gives
density interval [4/3,4/3] (exact), t* enclosure bracketing -ln(2/3)/2,
Lorenz ordinate bracketing the exact value.

Characterizations used:
- X ≤disp Y iff f_X(F_X⁻¹(u)) ≥ f_Y(F_Y⁻¹(u)) for all u in (0,1)
  (equivalently hazard-at-quantile; (1-u) cancels).
- X ≤* Y iff F_X⁻¹(u)/F_X⁻¹(v) ≥ F_Y⁻¹(u)/F_Y⁻¹(v) for 0<u<v<1.
- X ≤L Y iff L_X(p) ≥ L_Y(p); L = M/E with
  M(p) = sum_i p_i(1-s*^{k_i})/lam_i − D(-ln s*)(1-p), E = sum p_i/lam_i.
- Both ⇒ st: we first verify SF ordering (Sturm/factorization) so the
  surviving disp/star direction is the only one tested as "the claim".

## CERT G — dispersive order (SB2022 claim shape): REFUTED

Flagship instance: p = (4/11, 4/11, 3/11), lam = (2,3,8), gam = (2,4,7).
Hypotheses: (p,lam),(p,gam) in U_3 ✓, lam ≻ gam ✓.

    Fbar_lam − Fbar_gam = s^3 (1-s)(4 - 3 s^4)/11 > 0 on (0,1)

so X_lam is **strictly st-larger** — the only possible disp direction is
X_gam ≤disp X_lam. At u = 19/20 (bisection iters 56, exact rationals):

    f_gam(F_gam⁻¹(19/20)) ∈ [0.11171218803189009, 0.11171218803189009]
    f_lam(F_lam⁻¹(19/20)) ∈ [0.11237181334585682, 0.11237181334585683]
    certified: upper < lower  →  X_gam ≰disp X_lam   (violations u=19/20, 39/40)

Further certificates:
- **CERT-A instance** (p=(39/86,18/43,11/86), lam=(4,6,9), gam=(4,7,8)):
  Fbar_lam−Fbar_gam = s^6(1-s)(36-11 s^2)/86 > 0 (the "2 roots" reported by
  Sturm are the endpoint roots s=0,1); gam≤disp lam fails at every probed
  u ≥ 39/40 (exact bounds, e.g. u=199/200: 0.0205028243632 < 0.0208681386954).
- **CERT-B instance** (V_3 single T-transform): SF diff factors as
  w^25(w-1)(9w^19+…+9w^13 −7w^12−…−7w^7 −29w^6−…−29)/72 > 0 on (0,1);
  q;gam≤disp p;lam fails at u = 199/200, 397/400 (exact bounds).
- **n=4 equal weights**: lam=(2,5,9,14) ≻ gam=(3,6,8,13): gam≤disp lam
  fails at u=19/20, 39/40.
- **Equal-weights n=3**: lam=(3,4,11)≻gam=(3,6,9): fails at u=31/32;
  lam=(2,3,8)≻gam=(2,4,7): fails at u=31/32.
- Search sweep (240 admissible n=3 instances, lam≻gam integer triples,
  decreasing/equal weights): the st-compatible direction gam≤disp lam
  violated on 21/240 instances, always at top-tail u (≥ 9/10).

Mechanism: disp is a nonseparable quantile functional; failure is a deep-tail
effect — the st-larger mixture carries fatter density at extreme quantiles.
Covers SB2022's "dispersive order under majorization" claims at claim shape
(abstract verbatim lists disp among the orders compared under majorization).

## CERT H — star order (PKP2022 n-component shape): REFUTED

Flagship instance: **equal weights** p=(1/3,1/3,1/3), lam=(3,4,11),
gam=(3,6,9) — lam≻gam; equal weights satisfy every standard hypothesis
(U_n trivially). SF diff = w^4(w-1)^2(w+1)(w^4+w^3+w^2+w+1)/3 > 0 → only
gam≤*lam possible. At (u,v) = (13/16, 15/16), bisection 56 + iv-ln:

    T_gam(u)/T_gam(v) ∈ [0.53627319895821573, 0.53627319895821579]
    T_lam(u)/T_lam(v) ∈ [0.54142683876602883, 0.54142683876602889]
    certified: upper < lower  →  X_gam ≰* X_lam
    (also violated at (7/8,15/16); same signature on lam=(2,3,8),gam=(2,4,7))

CERT-A instance: star order fails in **both** directions (incomparable —
73 violations of lam≤*gam, 180 of gam≤*lam on the 24ths grid), so both
claim directions are refuted on U_3+maj hypotheses. CERT-B: 115 + 138.
Search sweep: 30/240 U_3-admissible instances violate gam≤*lam.
Failure is again a top-tail effect (violating pairs concentrate at v=15/16).

## CERT I — Lorenz order (PKP2022 n-component shape): REFUTED

Same flagship (equal weights, lam=(3,4,11)≻gam=(3,6,9)) at p=15/16:

    L_gam(15/16) ∈ [0.71758353389054611, 0.71758353389054612]
    L_lam(15/16) ∈ [0.72220531338182401, 0.72220531338182403]
    certified: L_gam < L_lam  →  X_gam ≰L X_lam

Richer Lorenz picture (both directions probed):
- Equal weights: Lorenz curves **cross** — on (3,4,11)/(3,6,9),
  lam≤L gam fails at 28/31 interior grid points while gam≤L lam fails only
  near p ≥ 29/32. Either claimed direction is refuted somewhere.
- **CERT-A (U_3 weights)**: ordering runs *opposite* to the
  heterogeneity⇒inequality direction: lam≤L gam holds on all 47 probed
  48ths while gam≤L lam fails at all 47. Same on CERT-B (23 violations of
  the heterogeneity⇒inequality direction, 0 of the other).
- 29/240 U_3-search instances violate gam≤L lam.

## Cone map update (which papers carry each shape)

- **SB2022** (Metrika 86:499): hr/rh halves already certified (CERT A/C);
  the **dispersive-order claims are now certified at claim shape by CERT G**.
  SB2022 moves from "conditional carrier + open disp shape" to fully
  certified-carrier status at claim shape.
- **PKP2022**: was clean-rated. Its n-component star/Lorenz ordering claims
  under majorization are refuted **at claim shape** by CERT H/I —
  the flagship refutations need only equal weights + majorization, the
  weakest standard hypothesis. Caveat: paywalled; if the theorems carry
  extra structure beyond maj/(chain-)majorization (e.g. restricted rate
  domains or a specific claim direction on PHR components), the text must
  be checked — but every standard admissible shape tested fails.
- **BHosp2022** (star/disp between a homogeneous exp and a *mixture*):
  different claim shape (scalar-vs-mixture heterogeneity, not two mixtures
  under majorization) — unaffected by these certificates.
- Transmission watch: any cone paper claiming disp/star/Lorenz ordering of
  exp-mixtures under majorization now has certified counterexamples.
  Dispersive⇒star⇒Lorenz means CERT G instances are also candidates for H/I,
  but the refutations here are independently certified anyway.

## Reproduce

    PY=/Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
    $PY attack.py          # full battery: CERT-A/B instances + 240-instance sweep
    $PY certify_GHI.py     # flagship exact/interval certificates (CERT G,H,I)

Files: `mixlib.py` (ExpMix + certified quantile bisection + disp/star/Lorenz
scans), `attack.py` (sweep), `certify_GHI.py` (flagship certs).

## Caveats / boundary

- "Claim-shape" certification: hypotheses satisfied are stated per instance
  (U_3+maj, V_3+single-T, equal-weights+maj); the papers' exact quantifiers
  are unverified (paywalled). Equal-weights instances are admissible under
  every hypothesis variant in this literature family.
- Violations are concentrated in the extreme tail (u ≳ 0.9). Claims with a
  bounded-quantile restriction would need finer analysis; none such are
  standard.
- Dispersive certificates are exact rational comparisons; star/Lorenz use
  rigorous mpmath.iv enclosures anchored on exact rational bisection
  (intervals ~1e-60 wide; margins ~5e-3 to 5e-1 — decisively separated).
- Lorenz direction asymmetry is real and worth noting in the cone narrative:
  under U_3 antiordered weights the *more* heterogeneous mixture is
  Lorenz-smaller (more equal); under equal weights the curves cross.
