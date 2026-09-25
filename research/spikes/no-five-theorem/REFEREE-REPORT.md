# Referee report: Round 27, no-five-on-a-sphere lower-bound lane (Memo A)

Memo reviewed: `memo.md` in this directory (586 lines), with `src/` and `data/`, on branch
`research/no-five-theorem`.
Referee: an independent adversarial check, 2026-09-25. I did not edit the memo, commit or push.
My scratch scripts are in `/tmp/referee/` (throwaway, not committed): `common.py`,
`family.py`, `ids.py`, `kplane.py`, `zplane_exact.py`, `randcop.py`.

## Verdict

**Major revision.** The Section 2 results can stand; Section 4 has to be rewritten.

- **Section 2 is correct.** This covers the determinant identities (Lemmas 1, 3, T and C),
  Lemma A, family `F(p; q, r)`, Lemmas O, O' and R, and Proposition D. I checked each one by
  hand, and machine-checked the identities and the family myself. Attribution to Dong–Xu is
  honest, though it could be sharper (problem 9).
- **Two claims in Section 4 are false.**
  - The "elementary consequence that drives everything else" (§4.1).
  - Lemma V, for `k ≥ 11`.
- **The headline negative conclusion of §4.4 is not supported and is probably wrong.** That
  conclusion says plain deletion "cannot yield `(1+ε)n` ... which the data contradict". The
  exact plane-count constant is about 0.0721, which is *below* the threshold 0.0819. So the
  deletion route is open, conditional on a lattice-point estimate for spheres.

These problems sit in the obstruction analysis, which §0 presents as a main deliverable. That
is why I ask for major revision rather than minor.

## Numbered problems

**1. (Major, false statement.) §4.1, the bold claim at lines 390–393, repeated in §0 (lines
29–30) and in the last bullet of §4.4 (lines 494–496).** The claim reads: "if
`S ⊂ [0,n)³` has `|S| ≥ (1+ε)n` and `p ≤ n` is any prime, then at least `εn − 1` points of `S`
share their residue class mod `p` with another point of `S`, so `Θ(εn⁴)` 5-subsets have
`det5 ≡ 0 (mod p)`."

This is false. Residue classes of points mod `p` live in `F_p³`, and there are `p³` of them,
not `p`. Counterexample: `n = 10`, `p = 7`, and any 11 points of `[0,7)³ ⊂ [0,10)³` are
pairwise distinct mod 7, so no residue is repeated. Pigeonhole forces repeats only when
`p³ < |S|`.

What is actually true, for `p ≥ 5`:
- Ball's theorem means every `(p+2)`-subset of `S` contains a 5-subset with
  `det5 ≡ 0 (mod p)`. Averaging gives at least `C(|S|,5)/C(p+2,5)` such 5-subsets. For
  `p ≈ n` this is only `≈ (1+ε)^5`, a constant.
- Equivalently, at least `|S| − p − 1` points have to be deleted before mod `p` certifies
  every 5-subset.
- The count `Θ(εn⁴)` does hold when `S` contains a near-complete arc on a normal rational
  curve. A point off the curve lies on `~p³/24` hyperplanes spanned by four curve points. But
  this is special to curve-based constructions.

*Fix:* replace the bold statement and its two repetitions with the true statements above, and
check every conclusion in §4.1–4.4 that cites it.

**2. (Major, unsupported and probably wrong conclusion.) §4.4 lines 461–477, Conjecture 3,
and the §0 obstruction bullet.**

*The threshold arithmetic is correct.* Proposition D and the threshold `κ < (4/5)⁴/5 = 0.0819`
check out.

*The input constants are not.*
- **`Z_plane`.** I computed the asymptotic constant
  `K = (1/120)·Σ_{primitive v up to sign} ∫ φ_v(s)^5 ds`, where `φ_v` is the density of `v·U`
  with `U` uniform on `[0,1]³`. I used the closed form of `φ_v` with Gauss–Legendre
  quadrature.
  - Partial sums: `0.0468` (`|v|_∞ ≤ 1`), `0.0648` (`≤ 5`), `0.0701` (`≤ 20`),
    `0.0711` (`≤ 40`).
  - A `β/A` tail fit gives **`K ≈ 0.0721`**.
  - Exact lattice-plane sums over normals `|v|_∞ ≤ n−1` give lower bounds
    `Z_plane(n)/n^{11} ≥ 0.0580, 0.0668, 0.0691` at `n = 10, 20, 30`, increasing towards K.
    These are exact up to a negligible overcount of collinear 5-sets; planes with larger
    normals are omitted.
  - The same code reproduces the census coplanar totals exactly at `n = 3, 4` (2274, 109680).
  - The memo's heuristic "0.07–0.09" brackets this value. Its "measured 0.045" is about 35%
    low:
    - `random_census` uses 3 seeds, and the distribution is heavy-tailed. My 20 seeds at
      `N = 20`, `m = 40` gave coplanar mean 36.0 with standard deviation 29.1, implying 0.073.
    - The classifier files coplanar 5-sets that contain a collinear triple or a concyclic
      quadruple under other columns.
- **`Z_sphere`.** The "measured 0.14, growing" is not supported.
  - The memo's own `sphere5/N` ratios are 4.6, 5.7, 4.9, 4.3 for `N = 20, 30, 40, 60`: they
    *fall* after `N = 30`.
  - The sibling upper-bound memo's exact Monte Carlo (`n ≤ 128`) gives
    `Z_sphere/n^{11} ≈ n·E(n)/120 = 0.27, 0.23, 0.19, 0.175, 0.135, 0.084` for
    `n = 16, 32, 48, 64, 96, 128`, which is clearly decreasing.
  - The standard heuristic is that spheres with bounded-denominator centres number
    `≈ n⁵` and carry `≈ n` points each, which gives `n^{10+o(1)}`.
  - Conjecture 3 (`Z_sphere = Θ(n^{11})`) is therefore disfavoured by the available data.

*Consequence.* With `B = [0,n)³`, Proposition D gives
`C(n) ≥ ((4/5)(5K)^{-1/4} − o(1)) n ≈ 1.032 n`, provided that:
- (a) `Z_sphere(n) = o(n^{11})`, or even just `≤ 0.0098 n^{11}` for large `n`, which is the
  margin `0.0819 − 0.0721`; and
- (b) there is a rigorous version of `Z_plane(n) ≤ (K + o(1)) n^{11}`: a Riemann sum per
  direction plus an explicit tail bound over normals.

This would beat the known `n − o(n)`. It is **conditional, not a theorem**, and I do not claim
it as one. But it reverses the memo's "the data contradict".

Suk–White's exponent `3/4` for `d = 3` is exactly what this deletion computation gives with a
crude `Z_sphere ≤ n^{12+o(1)}`. That fits the picture that the sphere count is the only
bottleneck.

*Fix:* rewrite §4.4 and the §0 bullet. State the exact open lemma, (a) plus (b), and report
K ≈ 0.0721 with its method. Demote or reverse Conjecture 3 in light of the `n ≤ 128` data.
Remove "cannot yield (1+ε)n ... which the data contradict". For the technique, cite
Ghosal–Goenka arXiv:2609.20447 (weighted random sampling plus careful deletion, in 2D).

**3. (Moderate, false lemma; its conclusion survives.) Lemma V (§2.5) is false for `k ≥ 11`.**
The class-size step only works when a class of `j(k)+1` elements fits inside one 5-subset,
that is `j(k) ≤ 4`, that is `k ≤ 10`.

Counterexample: `k = 11` and `T = {0, …, p²−1} ⊂ Z/p^k`. Every pair has valuation ≤ 1, so
every 5-subset has valuation sum ≤ 10 = k−1. Yet `|T| = p² > 5p = p·j(11)`.

*Fix:* state the lemma for `2 ≤ k ≤ 10`, and add the general pigeonhole bound. If
`|T| > 4p^j`, then five elements share a class mod `p^j` and have valuation sum ≥ 10j. So a
V-certified set satisfies `|T| ≤ 4p^{⌈k/10⌉} = 4N^{⌈k/10⌉/k} ≤ 4N^{1/2}` for every `k ≥ 2`. The
"loses a square root" conclusion in §2.5 and §4.2 survives with constant 4. Correct lines 211–212
and 407 accordingly.

**4. (Minor.) Ball's theorem is quoted for every prime `p` (§0, §4.1). It needs `p ≥ 5`**, the
MDS condition `k = 5 ≤ q`. In `PG(4,2)` and `PG(4,3)` the maximum arc has 6 points.

**5. (Minor, unproved claim.) §4.2, lines 410–411: "Two different primes `p, q` ... need
`|S| ≤ min(p,q)+1` (Lemma V's argument mod `pq`, or Ball for each prime)."** Certifying a
5-subset mod `pq` needs only *one* of the two primes, so Ball applied to each prime separately
proves nothing. Lemma V concerns a single p-adic curve.
*Fix:* remove the claim, or prove it.

**6. (Minor, label.) §4.2, "Two curves mod the same `p` ... one of which is rational on
average, so `Θ(p⁴)`"** is a heuristic. Label it as one.

**7. (Minor, incomplete proofs.) The "Fibre lemma (proved)" paragraph in §4.3.**
- The inequality `≤ 4 − m_x` is fine.
- **"This is exactly the family of 2.3"**: only one direction is shown. Family 2.3 has profile
  `(1,3,3)`, but the converse (every such curve is of this form) is not proved. Say "includes".
- **The `U = 1` argument handles only a nonzero leading vector with `p ≡ 1 (mod 4)`.** Here is
  a complete version. Let `A = Y+iZ` and `B = Y−iZ`; then `deg A + deg B ≤ 4`. The degree
  pairs `(4,0)`, `(3,≤1)` and `(2,2)` each put too many of `1, t, A, B` into a space of too
  small a dimension, which gives a linear dependence. For `p ≡ 3 (mod 4)`, anisotropy forces
  `deg Y, deg Z ≤ 2`, and dependence follows the same way.
- **"Impossible for any Lemma-A curve" is asserted but not proved for general `U`.** Here is a
  short proof. Profile `(1,1,1)` means `X = G_x ℓ_x` and `U = G_x μ_x` with `G_x` cubic and
  `ℓ_x, μ_x` linear, and similarly for `y` and `z`.
  - If two of the `μ` coincide, say `μ_x = μ_y`, then `X`, `Y` and `U` all lie in the
    2-dimensional space `G·{linear}`, so they are dependent.
  - Otherwise each `x²`, `y²`, `z²` has a double pole at its own point of `P¹`, while the
    other two squares are regular there. So `W/U` has three distinct double poles, which
    forces `deg U ≥ 6`, a contradiction.

**8. (Minor, definitions.) The decomposition `Z = Z_plane + Z_sphere` in §4.4 and Conjecture 3
defines `Z_sphere` as "sphere with no four coplanar".** That leaves out non-coplanar degenerate
5-sets that contain four concyclic points.
*Fix:* define `Z_sphere` as "degenerate and not coplanar". Separately, the "proved" bound
`Z_plane ≥ 3n·C(n²,5)` double-counts 5-subsets on axis-parallel lines, each of which lies in
two axis planes. Subtract `3n²·C(n,5)`; the asymptotics do not change.

**9. (Minor, attribution precision.)** The memo credits Dong–Xu for the curve mechanism in §0
and §2.3 and does not claim it as new. I checked the paper: Theorem 4 is in Section 2 and
assumes `p ≡ 1 (mod 4)`, the identity `Σ f_i² = gh` and linear independence, and the curve
`(f_i/h)` is used in Section 3. Two sharpenings are needed:
- **Lemma A is Dong–Xu's Section 3 argument in determinant form.** Their argument is that a
  plane or sphere meets the curve in the zeros of a nonzero polynomial of degree `≤ d+1` in the
  span. Credit it at Lemma A itself, not only in §2.3.
- **Family F is an instance of the *mechanism*, not literally of their Theorem 4.** Theorem 4
  has degree profile `(3,3,3,2,4)` and assumes `p > (d+1)! = 24`. F has `U = t` of degree 1 and
  works for every `p ≡ 1 (mod 4)`. Their `n − o(n)` for all `n` also uses a random translation
  with `p` slightly above `n`, whereas F gives only `C(p) ≥ p − 1` at primes `p ≡ 1 (mod 4)`.

Replace "an explicit instance of their theorem in `d = 3`" with "an instance of their
mechanism".

**10. (Minor, vacuous check.) "`p = 5 ... zeros=0`" (§2.3 and the §5 table) is vacuous:**
`|S| = 4`, so there are no 5-subsets (`data/family133_default.txt` shows `subsets=0`). Say
"verified for 8 primes `13 ≤ p ≤ 73`; `p = 5` has no 5-subsets".

**11. (Minor, documentation error.) §1 and §6 say that
`printf '0 0 0\n1 0 0\n0 1 0\n0 0 1\n1 1 1\n' | ./zero5` prints `zeros=1 subsets=6`.**
I compiled `src/zero5.c` and ran it: it prints `zeros=1 subsets=1`. It prints `subsets=6` only
with a sixth point added. Also, `zero5.c` does not bound-check its `X[8192]` input buffer. That
is harmless at the sizes used, but worth a guard.

**12. (Minor, data citation.) §4.4, lines 480–482: "at `N = 60`, `m = 120`, the 322 zero subsets
... and 34 deletions kill all zeros".** This mixes two different sets:
- `random_spheres.txt` at `N = 60`, `m = 120` has 322 zeros;
- the 34 deletions come from the `greedy_delete.txt` run at `n = 62`, `m = 124`, which has 665
  zeros.

Separately, the §3.6 table omits the `n = 58` random row that is in the data (474 zeros,
survivor 83 = 1.431n). Including it does not change the stated range.

**13. (Minor, labels.) Some statements in §4.1 and §3.5 should be marked heuristic or
interpretive.**
- The single-prime bound "`≈ min(p, n³/p²)`" uses the facts that near-complete arcs lie on a
  normal rational curve (known only for large arcs) and Weil equidistribution. It is a
  heuristic for general arcs.
- "There is no hidden identity behind these zeros" (§3.5) is an interpretation, not a
  finding.

## What I verified independently, and how

**Exact determinant checker.** I wrote my own fraction-free Bareiss 5×5 determinant on the
lifted rows, in Python integers. I did not use the memo's code.

**Family F, exact checks** (`/tmp/referee/family.py`).
- Default `q = t²`, `r = t² + 1`: all points are distinct, every exact determinant is nonzero,
  *no* 5-subset determinant is divisible by `p` (the mod-`p` arc property itself), and the
  fibres are `[1,3,3]`:

  | p | points | 5-subsets |
  |---|---|---|
  | 5 | 4 | 0 (vacuous) |
  | 13 | 12 | 792 |
  | 17 | 16 | 4368 |
  | 29 | 28 | 98280 |

- Seven random admissible `(q, r)` (with `q₂r₂r₀ ≠ 0`) at `p = 13, 17, 37`: no determinant
  divisible by `p`, and the maximum fibre is ≤ 3 in every case.
- By hand, the coefficient determinant is `±q₂² r₂ r₀/(2i)`, with the 2×2 block
  `[[q₂/2, r₀/2], [q₂/(2i), −r₀/(2i)]]`.

**Identities** (my own sympy script, `/tmp/referee/ids.py`). All print `True`: Lemma 1 with a
general translation `c`, Lemma 3, translation invariance, and Lemma C
(`V(t)(1+h₂)`).

**Proofs checked by hand.**
- Lemma 1: the Laplace sign `(−1)^{16}`, and the vanishing complementary minors.
- Lemma 3: `D₁ = 2|a|² a·u`, `D₂ = −2a·w`.
- Lemma T.
- Lemma C: bialternant exponents, and `h₂ = ½(Σtᵢ² + (Σtᵢ)²) ≥ 0`.
- Lemma A: distinctness of points needs `|T| ≥ 5`; this is a nit.
- Lemma O: the simple root, and the derivative by multilinearity.
- Lemma O':
  - `Q(L(P) + sτ_u) = s²|u|²`
  - `l` is not the tangent line
  - `deg π · deg C' = 3`, so `π` is birational
  - the `O(p)` exceptional pairs
  - each triple comes from at most 3 pairs.
- Lemma R.
- Proposition D, including `C(m,5)/C(b,5) ≤ (m/b)⁵`, the optimum `(4/5)(5κ)^{-1/4}`, the
  threshold 0.0819, and 0.81 at `κ = 0.19`.
- §3.1 counts `64p⁴` and `72p³`, and the six tetrahedron edge functionals in §4.3.

**Plane constant** (`/tmp/referee/kplane.py`, `zplane_exact.py`, `randcop.py`): see
problem 2.

**Literature.** I fetched Dong–Xu (arXiv 2506.18113, HTML full text), Suk–White
(2412.02866) and Ghosal–Goenka (2609.20447) from arXiv.

## What I could not check

- **Rigorous version of K ≈ 0.0721.** It is numerical: continuous approximation, quadrature,
  and a `β/A` tail extrapolation. The finite-`n` exact sums are lower bounds, up to an
  `O(n⁸ log n)` overcount of collinear 5-sets, which is negligible here.
- **Not recomputed:** the §3 numerics (the translate census at `p = 13`, shift tests, p-adic
  histograms, sphere loads, greedy-deletion survivors, `random_census`), apart from the
  spot-checks above. The greedy survivors are reported as measurements, not theorems, and the
  memo labels them that way correctly.
- **No attempt:** a proof of `Z_sphere(n) = o(n^{11})`.

## Overclaim audit (summary)

- The memo claims no new lower bound. That is correct and prominently stated.
- The numerical measurements are labelled "numerical, not proved" throughout. The exceptions
  are problems 2 and 13, where data-based inferences are presented as settled obstructions.
- Section headers call Lemma V and the §4.1 bold statement "proved" or "elementary", but both
  are false as stated (problems 1 and 3).
